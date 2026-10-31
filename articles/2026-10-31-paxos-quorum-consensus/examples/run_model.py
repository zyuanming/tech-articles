#!/usr/bin/env python3
"""Run the Paxos scenarios the article quotes and write results.json.

Standard library only. The prose and every figure read this file.
"""
from __future__ import annotations

import json
from pathlib import Path

import paxos

HERE = Path(__file__).resolve().parent


def trace_rows(sim):
    rows = []
    for e in sim.trace:
        if e["kind"] == "send":
            rows.append(dict(t=e["t"], src=e["src"], dst=e["dst"], dir="send",
                             kind=e["msg"]["kind"], ballot=e["msg"]["ballot"],
                             value=e["msg"].get("value"),
                             carried=e["msg"].get("accepted")))
        else:
            rows.append(dict(t=e["t"], src=e["src"], dst=e["dst"], dir="recv",
                             kind=e["msg"]["kind"], ballot=e["msg"]["ballot"],
                             value=e["msg"].get("value"),
                             note=e.get("note"), state=e.get("state")))
    return rows


def final_state(sim):
    return [a.state() for a in sim.acceptors.values()]


def firsts(sim, kind):
    """The time of the first message of a kind, and where it went."""
    hits = [e for e in sim.trace if e["kind"] == "send" and e["msg"]["kind"] == kind]
    return [dict(t=e["t"], src=e["src"], dst=e["dst"], ballot=e["msg"]["ballot"],
                 value=e["msg"].get("value")) for e in hits]


def main() -> None:
    out = {}

    happy = paxos.scenario((("P1", "X", 1),), seed=1)
    out["happy"] = dict(trace=trace_rows(happy), state=final_state(happy),
                        log=happy.proposers[0].log,
                        proposers=[dict(name=p.name, phase=p.phase, ballot=p.ballot,
                                        chosen=p.chosen, log=p.log)
                                   for p in happy.proposers])

    race = paxos.scenario((("P1", "X", 1), ("P2", "Y", 2)), seed=5, starts=(0, 12))
    out["race"] = dict(trace=trace_rows(race), state=final_state(race),
                       proposers=[dict(name=p.name, phase=p.phase, ballot=p.ballot,
                                       chosen=p.chosen, log=p.log)
                                  for p in race.proposers])

    naive = paxos.scenario((("P1", "X", 1), ("P2", "Y", 2)), seed=5, starts=(0, 12),
                           honour=False)
    out["naive"] = dict(trace=trace_rows(naive), state=final_state(naive),
                        proposers=[dict(name=p.name, phase=p.phase, ballot=p.ballot,
                                        chosen=p.chosen, log=p.log)
                                   for p in naive.proposers])

    # How many ballots it takes to settle when k proposers race.
    contention = []
    for k in range(1, 7):
        ballots, settled = [], 0
        for seed in range(60):
            racers = tuple((f"P{i + 1}", "XYZWUV"[i], i + 1) for i in range(k))
            starts = tuple(i // 2 for i in range(k))
            sim = paxos.scenario(racers, seed=seed, starts=starts, retries=8,
                                 latency=(1, 4))
            ballots.append(max(p.ballot for p in sim.proposers))
            settled += 1 if any(p.chosen for p in sim.proposers) else 0
        ballots.sort()
        contention.append(dict(k=k, runs=len(ballots), settled=settled,
                               mean=round(sum(ballots) / len(ballots), 3),
                               p50=ballots[len(ballots) // 2],
                               max=ballots[-1],
                               values=sorted({p.chosen for p in sim.proposers
                                              if p.chosen})))
    out["contention"] = contention

    # How many failures a quorum system of N acceptors tolerates.
    out["tolerance"] = [dict(n=n, quorum=n // 2 + 1, tolerated=n - (n // 2 + 1))
                        for n in range(1, 10)]

    (HERE / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("happy path :", happy.proposers[0].chosen, "|", happy.proposers[0].log)
    print("race       :", [p.chosen for p in race.proposers],
          "|", race.proposers[1].log)
    print("naive      :", [p.chosen for p in naive.proposers],
          "|", naive.proposers[1].log)
    for row in contention:
        print(f"contention k={row['k']}: mean ballots {row['mean']}, "
              f"max {row['max']}, settled {row['settled']}/{row['runs']}, "
              f"values {row['values']}")
    print("tolerance  :", [(r["n"], r["quorum"], r["tolerated"]) for r in out["tolerance"]])


if __name__ == "__main__":
    main()
