"""A small, readable Raft simulator. MIT.

This is a teaching model, not a production implementation: it covers terms,
elections, log replication, the commit rule, membership and network
partitions, and it deliberately leaves out persistence, snapshots, batching
and pipelining. Every number the article quotes comes from running it.
"""
from __future__ import annotations
import random
from collections import deque

FOLLOWER, CANDIDATE, LEADER = 'follower', 'candidate', 'leader'
NAMES = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
DEFAULT_NAMES = NAMES[:5]


class Entry:
    """One log entry: which term produced it, and what the client asked for."""

    __slots__ = ('term', 'command')

    def __init__(self, term: int, command):
        self.term = term
        self.command = command

    def __repr__(self):
        return 'T%d:%s' % (self.term, self.command)

    def __eq__(self, other):
        return (isinstance(other, Entry) and self.term == other.term
                and self.command == other.command)


class Message:
    __slots__ = ('kind', 'src', 'dst', 'term', 'payload', 'dropped')

    def __init__(self, kind, src, dst, term, payload=None):
        self.kind, self.src, self.dst = kind, src, dst
        self.term, self.payload = term, payload
        self.dropped = False


class Node:
    def __init__(self, name, cluster, *, election_timeout, heartbeat=8.0):
        self.name = name
        self.cluster = cluster
        self.term = 0
        self.voted_for = None
        self.state = FOLLOWER
        self.leader = None
        self.log = []                 # Entry list, index 0 is the first entry
        self.commit_index = 0         # number of committed entries
        self.applied = []             # commands applied to the state machine
        self.next_index = {}          # leader only, per peer
        self.match_index = {}         # leader only, per peer
        self.election_timeout = election_timeout
        self.heartbeat = heartbeat
        self.timer = 0.0
        self.votes = set()
        self.messages_sent = 0
        self.messages_received = 0
        self.elections_started = 0

    # ------------------------------------------------------------- log helpers
    @property
    def last_index(self):
        return len(self.log)

    @property
    def last_term(self):
        return self.log[-1].term if self.log else 0

    def term_at(self, index):
        """Term of the entry at 1-based `index`; 0 means "the empty prefix"."""
        return self.log[index - 1].term if 1 <= index <= len(self.log) else 0

    def is_up_to_date(self, last_index, last_term):
        """Raft's election restriction, expressed as a comparison."""
        if last_term != self.last_term:
            return last_term > self.last_term
        return last_index >= self.last_index

    # ---------------------------------------------------------------- lifecycle
    def become_follower(self, term):
        if term > self.term:
            self.term = term
            self.voted_for = None
        self.state = FOLLOWER
        self.leader = None
        self.votes = set()

    def become_candidate(self):
        self.state = CANDIDATE
        self.term += 1
        self.voted_for = self.name
        self.votes = {self.name}
        self.leader = None
        self.elections_started += 1
        self.reset_timer()

    def become_leader(self):
        self.state = LEADER
        self.leader = self.name
        nxt = self.last_index + 1
        self.next_index = {n: nxt for n in self.cluster.peers(self.name)}
        # The leader counts itself: its own log is by definition fully matched.
        self.match_index = {n: 0 for n in self.cluster.peers(self.name)}
        self.match_index[self.name] = self.last_index

    def reset_timer(self):
        self.timer = 0.0

    # ------------------------------------------------------------------ driving
    def tick(self, dt):
        """Advance local time. The timer means two different things depending on
        the state: for a leader it counts down to the next heartbeat, for
        everyone else it counts up to an election."""
        self.timer += dt
        if self.state == LEADER:
            if self.timer < self.heartbeat:
                return False
            self.timer = 0.0
            self.heartbeat_all()
            return False
        return self.timer >= self.election_timeout

    def send(self, kind, dst, payload=None):
        self.messages_sent += 1
        self.cluster.deliver(Message(kind, self.name, dst, self.term, payload))

    # ------------------------------------------------------------- RPC handlers
    def handle(self, msg):
        self.messages_received += 1
        if msg.term > self.term:
            # Any message from a higher term makes us a follower immediately.
            self.become_follower(msg.term)
            self.reset_timer()
        if msg.kind == 'request_vote':
            return self.on_request_vote(msg)
        if msg.kind == 'request_vote_reply':
            return self.on_request_vote_reply(msg)
        if msg.kind == 'append':
            return self.on_append(msg)
        if msg.kind == 'append_reply':
            return self.on_append_reply(msg)
        raise ValueError('unknown message %r' % msg.kind)

    def on_request_vote(self, msg):
        last_index, last_term = msg.payload['last_index'], msg.payload['last_term']
        granted = (msg.term >= self.term
                   and (self.voted_for in (None, msg.src))
                   and self.is_up_to_date(last_index, last_term))
        if granted:
            self.voted_for = msg.src
            self.reset_timer()
        self.send('request_vote_reply', msg.src,
                  {'granted': granted, 'term': self.term})

    def on_request_vote_reply(self, msg):
        if self.state != CANDIDATE or msg.term != self.term:
            return
        if msg.payload['granted']:
            self.votes.add(msg.src)
            if len(self.votes) >= self.cluster.majority:
                self.become_leader()

    def on_append(self, msg):
        p = msg.payload
        if msg.term < self.term:
            self.send('append_reply', msg.src,
                      {'success': False, 'term': self.term, 'match': 0})
            return
        # A valid leader for this term exists: do not run an election.
        self.leader = msg.src
        self.reset_timer()
        prev_index, prev_term = p['prev_index'], p['prev_term']
        if prev_index > self.last_index or self.term_at(prev_index) != prev_term:
            self.send('append_reply', msg.src,
                      {'success': False, 'term': self.term, 'match': 0,
                       'conflict': self.conflict_hint(prev_index, prev_term)})
            return
        # Everything up to prev_index agrees. Append what is genuinely new and
        # truncate any suffix that disagrees with the leader.
        entries = p['entries']
        for offset, entry in enumerate(entries):
            index = prev_index + offset + 1
            if index <= self.last_index:
                if self.log[index - 1].term != entry.term:
                    del self.log[index - 1:]
                    self.log.append(entry)
                    break
                # Same term at the same index: the entries are identical, keep it.
            else:
                self.log.append(entry)
        if p['leader_commit'] > self.commit_index:
            self.commit_index = min(p['leader_commit'], self.last_index)
            self.apply()
        # Report only how far the logs are *verified* to agree: prev_index plus
        # the entries just accepted. Reporting this node's whole log length
        # would let the leader believe a peer holds entries it never received
        # -- see `reply_rule='whole_log'`, which reproduces exactly that bug.
        if getattr(self.cluster, 'reply_rule', 'verified') == 'whole_log':
            match = self.last_index
        else:
            match = prev_index + len(entries)
        self.send('append_reply', msg.src,
                  {'success': True, 'term': self.term, 'match': match})

    def conflict_hint(self, prev_index, prev_term):
        """Raft's fast backup: instead of stepping back one entry at a time,
        jump to the first index of the conflicting term."""
        if prev_index > self.last_index:
            return {'next': self.last_index + 1}
        conflict_term = self.term_at(prev_index)
        i = prev_index
        while i > 1 and self.term_at(i - 1) == conflict_term:
            i -= 1
        return {'next': i}

    def on_append_reply(self, msg):
        if self.state != LEADER or msg.term != self.term:
            return
        p = msg.payload
        if p['success']:
            self.match_index[msg.src] = p['match']
            self.next_index[msg.src] = p['match'] + 1
            self.advance_commit()
        else:
            hint = p.get('conflict')
            self.next_index[msg.src] = (hint['next'] if hint
                                        else max(1, self.next_index[msg.src] - 1))
            self.replicate_to(msg.src)

    # ------------------------------------------------------------------- leader
    def peer_state(self, peer):
        """A leader may only discover a peer after the partition that hid it
        heals, so nextIndex/matchIndex are filled in lazily."""
        self.next_index.setdefault(peer, self.last_index + 1)
        self.match_index.setdefault(peer, 0)
        return self.next_index[peer]

    def replicate_to(self, peer):
        nxt = self.peer_state(peer)
        prev_index = nxt - 1
        prev_term = self.term_at(prev_index)
        entries = self.log[prev_index:]
        self.send('append', peer, {'prev_index': prev_index, 'prev_term': prev_term,
                                   'entries': list(entries),
                                   'leader_commit': self.commit_index})

    def broadcast(self):
        for peer in self.cluster.peers(self.name):
            self.replicate_to(peer)

    def heartbeat_all(self):
        for peer in self.cluster.peers(self.name):
            self.send('append', peer, {'prev_index': self.last_index,
                                       'prev_term': self.last_term, 'entries': [],
                                       'leader_commit': self.commit_index})

    def advance_commit(self):
        """Raft's commit rule: only entries of the *current* term may commit,
        and only once a majority has stored them.

        `match_index` includes the leader itself, so the majority-th largest
        value is exactly "the highest index a majority has stored".
        """
        matches = sorted(self.match_index.values(), reverse=True)
        n = matches[self.cluster.majority - 1]
        rule = getattr(self.cluster, 'commit_rule', 'raft')
        if n > self.commit_index and (rule == 'any' or self.term_at(n) == self.term):
            self.commit_index = n
            self.apply()

    def apply(self):
        while len(self.applied) < self.commit_index:
            self.applied.append(self.log[len(self.applied)].command)

    def client_append(self, command):
        """A client request, accepted only by a leader."""
        if self.state != LEADER:
            return None
        self.log.append(Entry(self.term, command))
        self.match_index[self.name] = self.last_index
        self.broadcast()
        self.advance_commit()
        return self.last_index


class Cluster:
    def __init__(self, names=DEFAULT_NAMES, *, seed=1, election_min=15.0,
                 election_max=30.0, heartbeat=8.0, latency=1.0):
        self.names = list(names)
        self.rng = random.Random(seed)
        self.nodes = {n: Node(n, self,
                              election_timeout=self.rng.uniform(election_min,
                                                                election_max),
                              heartbeat=heartbeat)
                      for n in self.names}
        self.election_min, self.election_max = election_min, election_max
        self.heartbeat = heartbeat
        self.latency = latency
        self.queue = deque()
        self.time = 0.0
        self.events = []          # (time, description) for the article's timeline
        self.delivered = 0
        self.dropped = 0
        self.history = []         # (time, per-node state summary)

    # ------------------------------------------------------------------ topology
    @property
    def majority(self):
        return len(self.names) // 2 + 1

    def peers(self, name):
        return [n for n in self.names if n != name and self.reachable(name, n)]

    def reachable(self, a, b):
        return not self.partitions or self.group_of(a) == self.group_of(b)

    def group_of(self, name):
        for i, group in enumerate(self.partitions):
            if name in group:
                return i
        return -1

    partitions = None             # None means "fully connected"

    def set_partitions(self, *groups):
        self.partitions = [set(g) for g in groups] if groups else None

    def heal(self):
        self.partitions = None

    def reset_timers(self):
        for node in self.nodes.values():
            node.reset_timer()

    # -------------------------------------------------------------------- events
    def deliver(self, msg):
        if not self.reachable(msg.src, msg.dst):
            msg.dropped = True
            self.dropped += 1
            return
        self.queue.append((self.time + self.latency, msg))

    def step(self, dt=0.5):
        """Advance simulated time by dt, delivering messages and ticking nodes."""
        self.time += dt
        # 1. deliver everything whose arrival time has come
        while self.queue and self.queue[0][0] <= self.time:
            _, msg = self.queue.popleft()
            self.delivered += 1
            self.nodes[msg.dst].handle(msg)
        # 2. leaders send heartbeats, followers may time out
        for name in self.names:
            node = self.nodes[name]
            if node.tick(dt):
                node.become_candidate()
                self.events.append((self.time, '%s 发起选举，任期 %d'
                                    % (name, node.term)))
                for peer in self.peers(name):
                    node.send('request_vote', peer,
                              {'last_index': node.last_index,
                               'last_term': node.last_term})
        self.history.append((self.time, self.snapshot()))

    def run(self, seconds, dt=0.5):
        for _ in range(int(round(seconds / dt))):
            self.step(dt)
        return self

    # ------------------------------------------------------------------- queries
    def leaders(self):
        return [n for n in self.names if self.nodes[n].state == LEADER]

    def leader(self):
        leaders = self.leaders()
        return self.nodes[leaders[0]] if len(leaders) == 1 else None

    def snapshot(self):
        return {n: (self.nodes[n].state, self.nodes[n].term,
                    self.nodes[n].commit_index, len(self.nodes[n].log))
                for n in self.names}

    def describe(self):
        parts = []
        for n in self.names:
            node = self.nodes[n]
            parts.append('%s:%s T%d log=%d commit=%d'
                         % (n, node.state[0].upper(), node.term, len(node.log),
                            node.commit_index))
        return '  '.join(parts)

    def logs(self):
        return {n: [repr(e) for e in self.nodes[n].log] for n in self.names}


# ------------------------------------------------------------------ invariants
def check_safety(cluster):
    """Check Raft's four safety properties on the cluster's current state.

    An empty list means "no violation was observed in this schedule" — it is
    never a proof. The properties are the ones Raft actually promises; in
    particular a node stuck in a minority partition is *allowed* to hold a
    conflicting, uncommitted entry at some index, so the committed-entry check
    only compares nodes that both committed that index.
    """
    problems = []
    nodes = [cluster.nodes[n] for n in cluster.names]

    # 1. Election safety: at most one leader per term, at any moment.
    by_term = {}
    for node in nodes:
        if node.state == LEADER:
            by_term.setdefault(node.term, []).append(node.name)
    for term, leaders in sorted(by_term.items()):
        if len(leaders) > 1:
            problems.append('同一任期 %d 有两个领导：%s' % (term, leaders))

    # 2. Log matching: same index and term implies the same prefix.
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            for k in range(1, min(a.last_index, b.last_index) + 1):
                if a.term_at(k) == b.term_at(k):
                    if ([repr(e) for e in a.log[:k]]
                            != [repr(e) for e in b.log[:k]]):
                        problems.append('%s 与 %s 在第 %d 项同任期却前缀不同'
                                        % (a.name, b.name, k))
                        break

    # 3. Committed entries agree wherever two nodes both committed them.
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            for k in range(1, min(a.commit_index, b.commit_index) + 1):
                if (a.term_at(k) != b.term_at(k)
                        or a.log[k - 1].command != b.log[k - 1].command):
                    problems.append('%s 与 %s 都提交了第 %d 项，内容却不同'
                                    % (a.name, b.name, k))

    # 4. State machines agree on the prefix they have both applied.
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            n = min(a.commit_index, b.commit_index)
            if a.applied[:n] != b.applied[:n]:
                problems.append('%s 与 %s 已应用的序列不同' % (a.name, b.name))
    return problems


def two_leaders_now(cluster):
    """The one property that must hold at every instant, not just at the end."""
    by_term = {}
    for name in cluster.names:
        node = cluster.nodes[name]
        if node.state == LEADER:
            by_term.setdefault(node.term, []).append(name)
    return [(t, names) for t, names in by_term.items() if len(names) > 1]


def random_schedule(seed, *, seconds=180.0, n=5, crash_prob=0.02,
                    partition_prob=0.01, command_prob=0.05, commands=10,
                    commit_rule='raft', reply_rule='verified'):
    """Drive a cluster through a random schedule of crashes and partitions,
    then check the invariants.

    `commit_rule='any'` deliberately drops Raft's "current term only" rule, so
    the checker has something real to catch. Empty `problems` means "no
    violation showed up in this schedule", never "proved safe".
    """
    rng = random.Random(seed)
    cluster = Cluster(list(NAMES[:n]), seed=seed, election_min=15.0,
                      election_max=30.0)
    cluster.commit_rule = commit_rule
    cluster.reply_rule = reply_rule
    cluster.instant_violations = []
    alive = set(cluster.names)
    next_command = 0
    crashes = partitions = restarts = 0
    for _ in range(int(seconds / 0.5)):
        if rng.random() < crash_prob and len(alive) > cluster.majority:
            victim = rng.choice(sorted(alive))
            alive.discard(victim)
            crashes += 1
        if rng.random() < crash_prob and len(alive) < n:
            back = rng.choice([x for x in cluster.names if x not in alive])
            alive.add(back)
            cluster.nodes[back].become_follower(cluster.nodes[back].term)
            cluster.nodes[back].reset_timer()
            restarts += 1
        if rng.random() < partition_prob:
            if cluster.partitions:
                cluster.heal()
            else:
                order = sorted(cluster.names)
                rng.shuffle(order)
                cut = rng.randint(1, n - 1)
                cluster.set_partitions(order[:cut], order[cut:])
                partitions += 1
        if next_command < commands and rng.random() < command_prob:
            leader = next((cluster.nodes[x] for x in sorted(alive)
                           if cluster.nodes[x].state == LEADER), None)
            if leader is not None:
                leader.client_append('cmd%d' % next_command)
                next_command += 1
        for name in sorted(cluster.names):
            node = cluster.nodes[name]
            if name not in alive:
                continue
            if node.tick(0.5):
                node.become_candidate()
                for peer in cluster.peers(name):
                    node.send('request_vote', peer,
                              {'last_index': node.last_index,
                               'last_term': node.last_term})
        while cluster.queue and cluster.queue[0][0] <= cluster.time + 0.5:
            _, msg = cluster.queue.popleft()
            if not cluster.reachable(msg.src, msg.dst) or msg.dst not in alive:
                continue
            cluster.delivered += 1
            cluster.nodes[msg.dst].handle(msg)
        cluster.instant_violations.extend(two_leaders_now(cluster))
        cluster.time += 0.5
    problems = check_safety(cluster) + [
        '同一任期 %d 同时有两个领导：%s' % (t, names)
        for t, names in cluster.instant_violations]
    committed = max(cluster.nodes[x].commit_index for x in cluster.names)
    return dict(seed=seed, problems=problems, crashes=crashes,
                partitions=partitions, restarts=restarts,
                commands_sent=next_command, committed=committed,
                commit_rule=commit_rule,
                states={x: cluster.nodes[x].state for x in cluster.names})


def safety_sweep(seeds=200, *, commit_rule='raft', seconds=180.0,
                 reply_rule='verified'):
    """Run many random schedules and count how many broke an invariant."""
    bad = []
    totals = dict(crashes=0, partitions=0, restarts=0, commands=0)
    for seed in range(1, seeds + 1):
        r = random_schedule(seed, commit_rule=commit_rule, seconds=seconds,
                            reply_rule=reply_rule)
        for k in totals:
            totals[k] += r[k if k != 'commands' else 'commands_sent']
        if r['problems']:
            bad.append(dict(seed=seed, problems=r['problems'][:3]))
    return dict(seeds=seeds, commit_rule=commit_rule, seconds=seconds,
                violated=len(bad), clean=seeds - len(bad),
                examples=bad[:5], totals=totals)


def two_rule_comparison(seeds=200):
    """The same schedules under Raft's rule and under a naive one."""
    return dict(raft=safety_sweep(seeds, commit_rule='raft'),
                any=safety_sweep(seeds, commit_rule='any'))


def bug_hunt(seeds=400):
    """The same schedules with the matchIndex reply deliberately broken, to
    show that the checker does catch this one."""
    return dict(correct=safety_sweep(seeds),
                broken=safety_sweep(seeds, reply_rule='whole_log'))


# ------------------------------------------------------- scripted scenarios
def election_timeline(seed=5, seconds=70.0, dt=0.5):
    """A quiet cluster: one election, then heartbeats. Returns the trace."""
    cluster = Cluster(seed=seed)
    trace = []
    for _ in range(int(seconds / dt)):
        cluster.step(dt)
        trace.append((round(cluster.time, 1),
                      {n: cluster.nodes[n].state for n in cluster.names},
                      {n: cluster.nodes[n].term for n in cluster.names}))
    return cluster, trace


def fixed_timeout_split_vote(seconds=600.0, timeout=20.0, dt=0.5):
    """Every node uses the *same* timeout, so they keep colliding forever."""
    cluster = Cluster(seed=1)
    for node in cluster.nodes.values():
        node.election_timeout = timeout
    cluster.run(seconds, dt)
    terms = {n: cluster.nodes[n].term for n in cluster.names}
    return dict(seconds=seconds, timeout=timeout,
                elections={n: cluster.nodes[n].elections_started
                           for n in cluster.names},
                terms=terms, leaders=cluster.leaders(),
                max_term=max(terms.values()),
                still_no_leader=not cluster.leaders())


def randomized_timeout_election(seed=11, seconds=600.0, dt=0.5, runs=40):
    """The same cluster with randomized timeouts, measured over many seeds."""
    rows = []
    for s in range(1, runs + 1):
        cluster = Cluster(seed=s)
        t_leader = None
        for _ in range(int(seconds / dt)):
            cluster.step(dt)
            if t_leader is None and cluster.leaders():
                t_leader = round(cluster.time, 1)
        rows.append(dict(seed=s, first_leader_at=t_leader,
                         elections=sum(cluster.nodes[n].elections_started
                                       for n in cluster.names),
                         leader=cluster.leaders()[0] if cluster.leaders() else None))
    times = [r['first_leader_at'] for r in rows if r['first_leader_at']]
    return dict(rows=rows, runs=runs, worst=max(times), best=min(times),
                mean=round(sum(times) / len(times), 2),
                failed=[r['seed'] for r in rows if not r['first_leader_at']])


def leader_crash_recovery(seed=3):
    """Kill the leader mid-flight; a new one must appear without losing entries."""
    cluster = Cluster(seed=seed)
    cluster.run(40)
    first = cluster.leader()
    for i in range(3):
        first.client_append('x=%d' % i)
    cluster.run(10)
    committed_before = first.commit_index
    log_before = [repr(e) for e in first.log]
    # The leader disappears: nothing it sends is delivered any more.
    cluster.set_partitions([first.name],
                           [n for n in cluster.names if n != first.name])
    t0 = cluster.time
    new_leader = None
    for _ in range(int(200 / 0.5)):
        cluster.step(0.5)
        leaders = [n for n in cluster.leaders() if n != first.name]
        if leaders:
            new_leader = leaders[0]
            break
    elapsed = round(cluster.time - t0, 1)
    node = cluster.nodes[new_leader] if new_leader else None
    return dict(first_leader=first.name, new_leader=new_leader,
                election_seconds=elapsed,
                new_term=node.term if node else None,
                log_before=log_before,
                log_after=[repr(e) for e in node.log] if node else [],
                committed_before=committed_before,
                committed_after=node.commit_index if node else None,
                log_preserved=(node is not None
                               and [repr(e) for e in node.log][:len(log_before)]
                               == log_before))


def conflict_repair(seed=3):
    """A follower with an uncommitted tail that disagrees gets truncated.

    The divergence is produced by the simulator, not hand-edited: a leader
    replicates two entries to only one follower, dies, and a new leader with a
    shorter log wins the next election. Two values are hand-set, and only to
    make the interesting case happen: who times out first, and the length of
    the window in which the old leader can still reach its one follower.
    """
    cluster = Cluster(seed=seed)
    cluster.run(40)
    first = cluster.leader()
    first.client_append('e1')
    cluster.run(20)
    committed = first.commit_index
    pair = [first.name] + [n for n in cluster.names if n != first.name][:1]
    rest = [n for n in cluster.names if n not in pair]
    cluster.set_partitions(pair, rest)
    cluster.reset_timers()
    first.client_append('e2')
    first.client_append('e3')
    cluster.run(3)                 # just long enough for the old leader -> peer
    b_name = pair[1]
    b = cluster.nodes[b_name]
    orphan_log = [repr(e) for e in b.log]
    orphan_commit = first.commit_index
    b.election_timeout = 1e9       # the longest log must not win this time
    cluster.set_partitions([first.name],
                           [n for n in cluster.names if n != first.name])
    cluster.reset_timers()
    new_leader = None
    for _ in range(int(400 / 0.5)):
        cluster.step(0.5)
        leaders = [n for n in cluster.leaders() if n != first.name]
        if leaders:
            new_leader = leaders[0]
            break
    winner = cluster.nodes[new_leader]
    winner.client_append('e4')
    cluster.run(20)
    follower_before_repair = [repr(e) for e in b.log]
    b.election_timeout = 20.0
    cluster.run(120)
    return dict(first_leader=first.name, slow_follower=b_name,
                new_leader=new_leader, new_term=winner.term,
                committed_before=committed,
                orphan_log=orphan_log, orphan_commit=orphan_commit,
                winner_log=[repr(e) for e in winner.log],
                follower_before_repair=follower_before_repair,
                follower_after_repair=[repr(e) for e in b.log],
                repaired=b.log == winner.log,
                discarded=[e for e in orphan_log
                           if e not in [repr(x) for x in b.log]],
                final_commit=winner.commit_index)


def partition_story(seed=3):
    """Split the cluster; the old leader keeps believing it is the leader."""
    cluster = Cluster(seed=seed)
    cluster.run(40)
    old = cluster.leader()
    for i in range(2):
        old.client_append('before%d' % i)
    cluster.run(10)
    committed = old.commit_index
    cluster.set_partitions([old.name],
                           [n for n in cluster.names if n != old.name])
    t0 = cluster.time
    new_leader, at = None, None
    for _ in range(int(300 / 0.5)):
        cluster.step(0.5)
        side = [n for n in cluster.leaders() if n != old.name]
        if side and new_leader is None:
            new_leader, at = side[0], round(cluster.time - t0, 1)
        if new_leader and cluster.time - t0 > at + 40:
            break
    stale_writes = []
    if old.state == LEADER:
        for i in range(2):
            old.client_append('orphan%d' % i)
            stale_writes.append('orphan%d' % i)
    isolated = dict(old_state=old.state, old_term=old.term,
                    old_log=[repr(e) for e in old.log],
                    old_commit=old.commit_index,
                    new_leader=new_leader, elected_after=at,
                    new_term=cluster.nodes[new_leader].term if new_leader else None,
                    new_log=[repr(e) for e in cluster.nodes[new_leader].log]
                    if new_leader else [],
                    stale_writes=stale_writes)
    cluster.heal()
    cluster.run(200)
    final = cluster.leader()
    final_log = [e.command for e in final.log] if final else []
    return dict(old_leader=old.name, committed_before=committed, **isolated,
                healed_leader=final.name if final else None,
                healed_log=[repr(e) for e in final.log] if final else [],
                orphans_discarded=[w for w in stale_writes if w not in final_log],
                old_final_log=[repr(e) for e in old.log],
                old_final_commit=old.commit_index,
                old_stepped_down=old.state != LEADER)


def figure8():
    """Raft's Figure 8, hand-built: why only current-term entries may commit.

    The states come straight from the paper's figure, not from a random run.
    """
    def make(name, term, log):
        node = Node(name, None, election_timeout=20.0)
        node.term = term
        node.log = [Entry(t, c) for t, c in log]
        node.commit_index = 1          # index 1 was committed back in term 1
        return node

    # (a) S1 leads term 4 and has replicated index 2 (term 2) to S2 only.
    #     S3, S4, S5 only have index 1 (term 1).
    base = [(1, 'a')]
    states_a = {'S1': (4, base + [(2, 'b')]), 'S2': (4, base + [(2, 'b')]),
                'S3': (2, base), 'S4': (2, base), 'S5': (2, base)}
    # (b) S1 dies. S5 wins term 5 and appends its own index 2.
    # (c) S5 dies. S1 restarts, wins term 6, and pushes index 2 (term 2) to S3,
    #     so index 2 now sits on a majority -- but it is from an old term.
    states_c = {'S1': (6, base + [(2, 'b')]), 'S2': (6, base + [(2, 'b')]),
                'S3': (6, base + [(2, 'b')]), 'S4': (2, base),
                'S5': (5, base + [(5, 'c')])}
    nodes = {n: make(n, t, log) for n, (t, log) in states_c.items()}

    def commit_rule(leader, current_term_only):
        """A cut-down advance_commit that can be told to skip the term check."""
        matches = [len(log) for n, (_, log) in states_c.items()]
        n = sorted(matches, reverse=True)[2]      # a majority of 5 is 3
        if n > leader.commit_index:
            if current_term_only and leader.term_at(n) != leader.term:
                return leader.commit_index, False
            leader.commit_index = n
            return n, True
        return leader.commit_index, False

    correct, correct_committed = commit_rule(nodes['S1'], True)
    broken, broken_committed = commit_rule(nodes['S1'], False)

    # (d) With index 2 "committed" under the broken rule, S1 dies again and S5
    #     wins term 7 (its last term is 5, higher than S3's 2). S5 then
    #     overwrites index 2 on S3: a committed entry disappears.
    s5, s3 = nodes['S5'], nodes['S3']
    s5.term = 7
    overwritten = [repr(e) for e in s3.log]
    s3.log = list(s5.log)          # an AppendEntries from S5 truncates and replaces
    lost = (broken_committed and 'T2:b' in overwritten
            and 'T2:b' not in [repr(e) for e in s3.log])
    return dict(
        states_a={n: dict(term=t, log=['T%d:%s' % e for e in log])
                  for n, (t, log) in states_a.items()},
        states_c={n: dict(term=t, log=['T%d:%s' % e for e in log])
                  for n, (t, log) in states_c.items()},
        correct_commit_index=correct, correct_committed=correct_committed,
        broken_commit_index=broken, broken_committed=broken_committed,
        s3_before=overwritten, s3_after=[repr(e) for e in s3.log],
        committed_entry_lost=lost,
        index2_term=nodes['S1'].term_at(2), leader_term=nodes['S1'].term)


def membership_change(seed=3):
    """Adding one node at a time never needs two majorities to agree."""
    cluster = Cluster(seed=seed)
    cluster.run(40)
    lead = cluster.leader()
    for i in range(5):
        lead.client_append('k%d' % i)
    cluster.run(30)
    before = dict(n=len(cluster.names), majority=cluster.majority,
                  leader=cluster.leader().name if cluster.leader() else None,
                  entries=lead.commit_index)
    steps = []
    for new_name in ('F', 'G'):
        old_names = list(cluster.names)
        old_majority = len(old_names) // 2 + 1
        cluster.names.append(new_name)
        node = Node(new_name, cluster, election_timeout=20.0)
        cluster.nodes[new_name] = node
        leader = cluster.leader()
        if leader:
            leader.next_index[new_name] = 1
            leader.match_index[new_name] = 0
            leader.replicate_to(new_name)
        cluster.run(40)
        caught = node.last_index
        cluster.run(40)
        steps.append(dict(added=new_name, old_n=len(old_names),
                          new_n=len(cluster.names),
                          old_majority=old_majority,
                          new_majority=cluster.majority,
                          leader=cluster.leader().name if cluster.leader() else None,
                          caught_at=caught,
                          leader_log=leader.last_index if leader else 0,
                          caught_up=caught >= (leader.last_index if leader else 0)))
    return dict(before=before, steps=steps,
                final_n=len(cluster.names), final_majority=cluster.majority,
                final_leader=cluster.leader().name if cluster.leader() else None)


def request_round_trip(seed=3):
    """Follow one client write from the leader's log to the state machines."""
    cluster = Cluster(seed=seed)
    cluster.run(40)
    leader = cluster.leader()
    trace = []
    original_handle = Node.handle

    def spy(self, msg):
        original_handle(self, msg)
        trace.append(dict(t=round(cluster.time, 1), src=msg.src, dst=self.name,
                          kind=msg.kind, term=msg.term))

    Node.handle = spy
    t0 = cluster.time
    leader.client_append('x=1')
    committed_at = None
    for _ in range(int(40 / 0.5)):
        cluster.step(0.5)
        if committed_at is None and leader.commit_index >= 1:
            committed_at = round(cluster.time - t0, 1)
        if committed_at is not None and cluster.time - t0 > committed_at + 5:
            break
    Node.handle = original_handle
    return dict(leader=leader.name, term=leader.term, started=t0,
                committed_after=committed_at, trace=trace,
                messages=len(trace),
                applied={n: cluster.nodes[n].applied for n in cluster.names},
                commit_index=leader.commit_index)


def commit_latency(seed=3, sizes=(3, 5, 7), writes=20):
    """How long one client write takes to commit, as the cluster grows."""
    rows = []
    for n in sizes:
        cluster = Cluster(list(NAMES[:n]), seed=seed)
        cluster.run(40)
        leader = cluster.leader()
        latencies = []
        for i in range(writes):
            t0 = cluster.time
            leader.client_append('w%d' % i)
            for _ in range(int(40 / 0.5)):
                cluster.step(0.5)
                if leader.commit_index >= len(leader.log):
                    break
            latencies.append(round(cluster.time - t0, 1))
        rows.append(dict(n=n, majority=cluster.majority,
                         tolerated=(n - 1) // 2,
                         mean=round(sum(latencies) / len(latencies), 2),
                         worst=max(latencies),
                         messages_per_write=round(
                             sum(cluster.nodes[x].messages_sent
                                 for x in cluster.names) / writes, 1)))
    return rows


def majority_table(sizes=range(1, 8)):
    """Majority size, tolerated failures, and how many nodes can be isolated."""
    return [dict(n=n, majority=n // 2 + 1, tolerated=(n - 1) // 2,
                 isolated=n - (n // 2 + 1)) for n in sizes]


def round_trip_by_size(seed=3, sizes=(3, 5, 7)):
    """Message counts for one election, by cluster size."""
    rows = []
    for n in sizes:
        cluster = Cluster(list(NAMES[:n]), seed=seed)
        before = sum(cluster.nodes[x].messages_sent for x in cluster.names)
        cluster.run(60)
        after = sum(cluster.nodes[x].messages_sent for x in cluster.names)
        rows.append(dict(n=n, majority=cluster.majority,
                         messages=after - before,
                         leader=cluster.leaders()[0] if cluster.leaders() else None))
    return rows


def timeline_rows(seed=5, seconds=70.0):
    """A compact per-node timeline for the figure: when each node changed state."""
    cluster, trace = election_timeline(seed=seed, seconds=seconds)
    changes = []
    previous = {n: 'follower' for n in cluster.names}
    for t, states, terms in trace:
        for n in cluster.names:
            if states[n] != previous[n]:
                changes.append(dict(t=t, node=n, to=states[n], term=terms[n]))
                previous[n] = states[n]
    return dict(changes=changes, seconds=seconds,
                final={n: cluster.nodes[n].state for n in cluster.names},
                final_term={n: cluster.nodes[n].term for n in cluster.names})
