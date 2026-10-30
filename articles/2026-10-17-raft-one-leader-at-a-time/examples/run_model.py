#!/usr/bin/env python3
"""Run every Raft experiment the article quotes, and write results.json.

Standard library only. Everything here is deterministic given the seeds.
"""
from __future__ import annotations
import json
from pathlib import Path

import raft as R

HERE = Path(__file__).resolve().parent


def main() -> None:
    out = {}

    # ---- how big a cluster has to be
    out['majority'] = R.majority_table()

    # ---- a quiet cluster: one election, then heartbeats
    cluster, trace = R.election_timeline()
    out['timeline'] = R.timeline_rows()
    out['timeline']['states'] = [
        dict(t=t, states=states, terms=terms) for t, states, terms in trace
        if int(t * 10) % 20 == 0]

    # ---- randomized vs fixed timeouts
    out['fixed_timeout'] = R.fixed_timeout_split_vote()
    out['random_timeout'] = R.randomized_timeout_election()

    # ---- one client write, message by message
    out['round_trip'] = R.request_round_trip()
    out['latency'] = R.commit_latency()
    out['election_messages'] = R.round_trip_by_size()

    # ---- a leader dies
    out['crash'] = R.leader_crash_recovery()

    # ---- divergent tail repaired
    out['conflict'] = R.conflict_repair()

    # ---- a partition, and what the isolated old leader believes
    out['partition'] = R.partition_story()

    # ---- the commit rule, hand-built from the paper's Figure 8
    out['figure8'] = R.figure8()

    # ---- membership change
    out['membership'] = R.membership_change()

    # ---- randomized schedules against the invariants
    out['sweep'] = R.safety_sweep(400)
    out['sweep_harsh'] = R.safety_sweep(
        400, seconds=400.0)
    out['two_rules'] = R.two_rule_comparison(400)
    out['bug_hunt'] = R.bug_hunt(400)

    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')

    print('majority table:', out['majority'])
    print('fixed timeout: %d elections each, max term %d, leader=%s' % (
        out['fixed_timeout']['elections']['A'], out['fixed_timeout']['max_term'],
        out['fixed_timeout']['leaders']))
    print('random timeout: first leader in %.1f..%.1f s (mean %.2f) over %d runs'
          % (out['random_timeout']['best'], out['random_timeout']['worst'],
             out['random_timeout']['mean'], out['random_timeout']['runs']))
    print('round trip: committed after %s s with %d messages'
          % (out['round_trip']['committed_after'], out['round_trip']['messages']))
    print('latency by size:', [(r['n'], r['messages_per_write'])
                               for r in out['latency']])
    print('crash: %s -> %s in %s s, log preserved=%s' % (
        out['crash']['first_leader'], out['crash']['new_leader'],
        out['crash']['election_seconds'], out['crash']['log_preserved']))
    print('conflict: %s discarded %s, repaired=%s' % (
        out['conflict']['new_leader'], out['conflict']['discarded'],
        out['conflict']['repaired']))
    print('partition: old %s kept %d entries, orphans discarded %s' % (
        out['partition']['old_leader'], out['partition']['old_commit'],
        out['partition']['orphans_discarded']))
    print('figure 8: correct rule commits to %s, broken rule to %s, entry lost=%s'
          % (out['figure8']['correct_commit_index'],
             out['figure8']['broken_commit_index'],
             out['figure8']['committed_entry_lost']))
    print('membership: %s -> %d nodes, majority %d' % (
        out['membership']['before']['n'], out['membership']['final_n'],
        out['membership']['final_majority']))
    for key in ('sweep', 'sweep_harsh'):
        s = out[key]
        print('%s: %d of %d schedules broke an invariant (%s)'
              % (key, s['violated'], s['seeds'], s['totals']))
    print('two rules: raft=%d violations, naive=%d violations of %d'
          % (out['two_rules']['raft']['violated'],
             out['two_rules']['any']['violated'], out['two_rules']['raft']['seeds']))
    print('bug hunt: correct reply %d violations, whole-log reply %d violations'
          ' of %d schedules' % (out['bug_hunt']['correct']['violated'],
                                out['bug_hunt']['broken']['violated'],
                                out['bug_hunt']['correct']['seeds']))
    print('writes results.json')


if __name__ == '__main__':
    main()
