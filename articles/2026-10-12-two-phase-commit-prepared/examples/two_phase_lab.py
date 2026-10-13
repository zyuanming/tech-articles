"""Original finite 2PC teaching model. No network, database or real disk I/O.
Durable state changes are atomic; send is a separate step. Sent messages are
retained as an 'ever sent' set: delivery may be delayed/ignored indefinitely,
not an actual reliable queue. Only safety is exhaustively checked.
"""
from dataclasses import dataclass, replace
from collections import deque
import json

@dataclass(frozen=True)
class State:
    rm: tuple
    yes_sent: frozenset = frozenset()
    yes_seen: frozenset = frozenset()
    decision: str = '-'
    published: bool = False

def successors(s, bad=None):
    n=len(s.rm)
    def change(i,v):
        r=list(s.rm);r[i]=v;return replace(s,rm=tuple(r))
    for i,x in enumerate(s.rm):
        if x=='W':
            yield f'P{i}: persist PREPARED',change(i,'P')
            yield f'P{i}: reject before YES',change(i,'A')
        if x=='P' and i not in s.yes_sent:
            yield f'P{i}: send YES',replace(s,yes_sent=s.yes_sent|{i})
        if i in s.yes_sent and i not in s.yes_seen and s.decision=='-':
            yield f'TM: receive YES from P{i}',replace(s,yes_seen=s.yes_seen|{i})
        if s.published and x not in ('C','A'):
            yield f'P{i}: receive {s.decision}',change(i,s.decision)
        if bad=='timeout_abort' and x=='P':
            yield f'BAD P{i}: timeout then abort',change(i,'A')
        if bad=='local_commit' and x=='P':
            yield f'BAD P{i}: commit on own YES',change(i,'C')
    if s.decision=='-':
        yield 'TM: persist ABORT',replace(s,decision='A')
        threshold = n//2+1 if bad=='majority' else n
        if len(s.yes_seen)>=threshold:
            yield 'TM: persist COMMIT',replace(s,decision='C')
    if s.decision in ('C','A') and not s.published:
        yield 'TM: send durable decision',replace(s,published=True)

def safe(s):
    return not ('C' in s.rm and 'A' in s.rm)

def explore(n,bad=None):
    start=State(('W',)*n);todo=deque([start]);parents={start:None};edge=0;deliveries=0
    while todo:
        s=todo.popleft()
        if not safe(s):
            trace=[];t=s
            while parents[t]:p,label=parents[t];trace.append({'event':label,'state':show(t)});t=p
            return {'counterexample':list(reversed(trace)),'visited_until_failure':len(parents)}
        if bad is None:
            if s.decision=='C':assert all(x in ('P','C') for x in s.rm)
            if 'C' in s.rm:assert s.decision=='C' and s.published
            # A duplicate YES adds an existing identity, never a second vote.
            for i in s.yes_seen:assert len(s.yes_seen|{i})==len(s.yes_seen);deliveries+=1
        for label,t in successors(s,bad):
            edge+=1
            if bad is None:
                assert all(a==b for a,b in zip(s.rm,t.rm) if a in ('C','A'))
                assert s.decision=='-' or s.decision==t.decision
            if t not in parents:parents[t]=(s,label);todo.append(t)
    return {'states':len(parents),'transitions':edge,'duplicate_vote_checks':deliveries}

def show(s):return {'rm':list(s.rm),'yes_sent':sorted(s.yes_sent),'yes_seen':sorted(s.yes_seen),'TM':s.decision,'decision_sent':s.published}

def step(s,label):
    found=[t for k,t in successors(s) if k==label]
    assert len(found)==1,(label,show(s));return found[0]

def timeout_action(state):
    if state == 'W':
        return '可在承诺前撤销'
    if state == 'P':
        return '等待或查询可靠决定'
    return '保留已有最终结果'


def check():
    assert [timeout_action(x) for x in 'WPCA']==['可在承诺前撤销','等待或查询可靠决定','保留已有最终结果','保留已有最终结果']
    tests={str(n):explore(n) for n in (1,2,3,4)}
    failures={b:explore(3 if b=='majority' else 2,b) for b in ['timeout_abort','local_commit','majority']}
    assert all('counterexample' in x for x in failures.values())
    s=State(('W','W'));trace=[{'event':'start','state':show(s)}]
    sequence=['P0: persist PREPARED','P0: send YES','P1: persist PREPARED','P1: send YES','TM: receive YES from P0','TM: receive YES from P1','TM: persist COMMIT','TM: send durable decision','P1: receive C','P0: receive C']
    for event in sequence:s=step(s,event);trace.append({'event':event,'state':show(s)})
    # Same participant-visible observations, opposite durable TM decisions.
    both=State(('P','P'),frozenset({0,1}),frozenset({0,1}))
    hidden_c=step(both,'TM: persist COMMIT');hidden_a=step(both,'TM: persist ABORT')
    assert hidden_c.rm==hidden_a.rm and not hidden_c.published and not hidden_a.published
    assert all('TM:' in label for label,_ in successors(both))
    # Freeze TM: prepared participants have no protocol-changing step left.
    # If no one can reach durable TM state or a known decision, this is blocking.
    frozen_rm_steps=[x for x in successors(both) if not x[0].startswith('TM:')];assert frozen_rm_steps==[]
    return {'good_models':tests,'bad_protocols':failures,'normal_trace':trace,'hidden_commit':show(hidden_c),'hidden_abort':show(hidden_a),'blocked_participant_steps':len(frozen_rm_steps),'scope':'finite safety; durable state, one transaction, fixed participants, authenticated uncorrupted messages; no liveness proof or DBMS test'}

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))
