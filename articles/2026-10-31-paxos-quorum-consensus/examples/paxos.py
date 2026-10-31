#!/usr/bin/env python3
"""A small, deterministic Paxos simulator. Standard library only.

Every number the article quotes about a run — which acceptors promised, which
values came back in phase 1b, which ballot won — is produced by this file.
Messages sit in a seeded event queue, so they can arrive out of order and
overtake each other; an acceptor keeps its promise and its accepted value the
way a real one keeps them on disk.

`honour_promises=False` builds the flawed proposer used in one figure: it is
the same code with the phase-1b choice removed. It exists to show what the
rule prevents, and is never used to claim that Paxos is safe.
"""
from __future__ import annotations

import heapq
import random


class Acceptor:
    def __init__(self, name: str):
        self.name = name
        self.promised: int | None = None
        self.accepted: tuple[int, str] | None = None

    def state(self) -> dict:
        return {
            "acceptor": self.name,
            "promised": self.promised,
            "accepted_ballot": self.accepted[0] if self.accepted else None,
            "accepted_value": self.accepted[1] if self.accepted else None,
        }

    def receive(self, msg: dict):
        ballot = msg["ballot"]
        if msg["kind"] == "prepare":
            if self.promised is None or ballot > self.promised:
                self.promised = ballot
                return {"kind": "promise", "ballot": ballot,
                        "accepted": self.accepted}, "promised"
            return {"kind": "reject", "ballot": ballot,
                    "promised": self.promised}, "rejected"
        if msg["kind"] == "accept":
            if self.promised is None or ballot >= self.promised:
                self.promised = ballot
                self.accepted = (ballot, msg["value"])
                return {"kind": "accepted", "ballot": ballot,
                        "value": msg["value"]}, "accepted"
            return {"kind": "reject", "ballot": ballot,
                    "promised": self.promised}, "rejected"
        raise ValueError("unknown message " + msg["kind"])


class Proposer:
    """Ballot-numbered proposer, driven entirely by arriving messages."""

    def __init__(self, name: str, value: str, sim: "Sim", *, ballot: int = 1,
                 honour: bool = True, retries: int = 0, backoff=(0, 0),
                 rng: random.Random | None = None):
        self.name = name
        self.value = value
        self.sim = sim
        self.ballot = ballot
        self.honour = honour
        self.retries = retries
        self.backoff = backoff
        self.rng = rng or random.Random(0)
        self.phase = "idle"
        self.promises: list[dict] = []
        self.accepted: list[dict] = []
        self.chosen: str | None = None
        self.log: list[str] = []
        self.majority = sim.majority

    # -- outbound -------------------------------------------------------
    def start(self, delay: int = 0) -> None:
        self.phase = "phase1"
        self.promises.clear()
        self.sim.after(delay, lambda: self.sim.broadcast(
            self.name, {"kind": "prepare", "ballot": self.ballot}))

    def retry(self) -> None:
        self.ballot += 1
        self.log.append(f"{self.name} raises its ballot to {self.ballot}")
        self.start(self.rng.randint(*self.backoff))

    # -- inbound --------------------------------------------------------
    def receive(self, msg: dict) -> None:
        kind = msg["kind"]
        if kind in ("promise", "reject") and self.phase == "phase1":
            if msg["ballot"] != self.ballot:
                return
            self.promises.append(msg)
            if not self.reached(self.promises, kind):
                return
            ok = [m for m in self.promises if m["kind"] == "promise"]
            if len(ok) < self.majority:
                if self.retries:
                    self.retries -= 1
                    self.retry()
                else:
                    self.phase = "failed"
                    self.log.append("phase 1 refused by a majority")
                return
            self.choose_value(ok)
            self.phase = "phase2"
            self.sim.broadcast(self.name, {"kind": "accept",
                                           "ballot": self.ballot,
                                           "value": self.value})
        elif kind in ("accepted", "reject") and self.phase == "phase2":
            if msg["ballot"] != self.ballot:
                return
            self.accepted.append(msg)
            if self.reached(self.accepted, "accepted"):
                ok = [m for m in self.accepted if m["kind"] == "accepted"]
                if len(ok) >= self.majority:
                    self.chosen = self.value
                    self.phase = "done"
                    self.log.append(f"chosen: {self.value} at ballot {self.ballot}")
                elif self.retries:
                    self.retries -= 1
                    self.retry()

    def reached(self, replies: list[dict], kind: str) -> bool:
        """True once no further reply can change the outcome of this phase."""
        yes = sum(1 for m in replies if m["kind"] == kind)
        return yes >= self.majority or len(replies) >= len(self.sim.acceptors)

    def choose_value(self, promises: list[dict]) -> None:
        known = [p["accepted"] for p in promises if p.get("accepted")]
        if self.honour and known:
            ballot, value = max(known, key=lambda pair: pair[0])
            self.log.append(f"phase 1b carried value {value} from ballot {ballot}; "
                            f"adopting it instead of {self.value}")
            self.value = value
        elif known:
            self.log.append(f"phase 1b carried {known}; ignoring it")


class Sim:
    def __init__(self, acceptor_names=("A1", "A2", "A3", "A4", "A5"), *,
                 latency=(1, 3), seed: int = 0):
        self.acceptors = {name: Acceptor(name) for name in acceptor_names}
        self.proposers: list[Proposer] = []
        self.majority = len(acceptor_names) // 2 + 1
        self.latency = latency
        self.rng = random.Random(seed)
        self.clock = 0
        self.queue: list = []
        self.seq = 0
        self.trace: list[dict] = []

    # -- scheduling -----------------------------------------------------
    def after(self, delay: int, action) -> None:
        self.seq += 1
        heapq.heappush(self.queue, (self.clock + delay, self.seq, action))

    def send(self, src: str, dst: str, msg: dict) -> None:
        lo, hi = self.latency
        delay = self.rng.randint(lo, hi) if hi > lo else lo
        self.seq += 1
        entry = {"t": self.clock, "kind": "send", "src": src, "dst": dst,
                 "msg": dict(msg)}
        self.trace.append(entry)
        heapq.heappush(self.queue, (self.clock + delay, self.seq,
                                    lambda: self.deliver(src, dst, msg)))

    def broadcast(self, src: str, msg: dict) -> None:
        for name in self.acceptors:
            self.send(src, name, msg)

    def deliver(self, src: str, dst: str, msg: dict) -> None:
        node = self.acceptors.get(dst)
        if node is None:
            target = next(p for p in self.proposers if p.name == dst)
            self.trace.append({"t": self.clock, "kind": "recv", "src": src,
                               "dst": dst, "msg": dict(msg)})
            target.receive(msg)
            return
        reply, note = node.receive(msg)
        self.trace.append({"t": self.clock, "kind": "recv", "src": src,
                           "dst": dst, "msg": dict(msg), "note": note,
                           "state": node.state()})
        if reply:
            self.send(dst, src, reply)

    def run(self, limit=20000) -> None:
        while self.queue:
            t, _, action = heapq.heappop(self.queue)
            self.clock = t
            action()
            limit -= 1
            if limit <= 0:
                raise RuntimeError("simulation did not settle")


def scenario(proposers=(("P1", "X", 1),), *, acceptors=("A1", "A2", "A3", "A4", "A5"),
             seed=0, latency=(1, 3), honour=True, retries=0, backoff=(0, 0),
             starts=(0,)):
    """Build and run one scenario; return the simulation."""
    sim = Sim(acceptors, latency=latency, seed=seed)
    rng = random.Random(seed + 7)
    for index, (name, value, ballot) in enumerate(proposers):
        prop = Proposer(name, value, sim, ballot=ballot, honour=honour,
                        retries=retries, backoff=backoff, rng=rng)
        sim.proposers.append(prop)
        prop.start(starts[index] if index < len(starts) else 0)
    sim.run()
    return sim
