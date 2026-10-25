"""Synchronous oral-message model, original educational code. CC0-1.0."""
from collections import Counter
ATTACK, RETREAT = '进', '退'

def majority(values):
    counts = Counter(values)
    for value, count in counts.items():
        if count * 2 > len(values):
            return value
    return RETREAT

def simulate(nodes, depth, faulty=(), command=ATTACK, strategy=None):
    """One scheduled slot per path/recipient; missing is None then RETREAT.
    Assumes fixed nodes, reliable authenticated direct channels, common rounds.
    No signatures, socket traffic, or real-time performance measurement.
    A faulty sender controls only its own outgoing slots. Invalid values default.
    """
    events, reductions = [], []
    faulty = set(faulty)
    def om(group, leader, value, m, prefix):
        path = prefix + (leader,)
        assert len(path) == len(set(path))
        others = [x for x in group if x != leader]
        received = {}
        for target in others:
            raw = strategy(path, target, value) if leader in faulty else value
            delivered = raw if raw in (ATTACK, RETREAT) else RETREAT
            received[target] = delivered
            events.append(dict(path=list(path), sender=leader, target=target,
                               round=len(path), raw=raw, value=delivered))
        if m == 0:
            return received
        child = {j: om(others, j, received[j], m-1, path) for j in others}
        result = {}
        for target in others:
            vector = [received[j] if j == target else child[j][target] for j in others]
            result[target] = majority(vector)
            reductions.append(dict(path=list(path), target=target, depth=m,
                                   columns=others, vector=vector, value=result[target]))
        return result
    result = om(list(nodes), nodes[0], command, depth, ())
    events.sort(key=lambda e:(e['round'],e['path'],e['target']))
    loyal = {k:v for k,v in result.items() if k not in faulty}
    return dict(nodes=list(nodes), m=depth, faulty=sorted(faulty), command=command,
                result=result, loyal=loyal, events=events, reductions=reductions,
                slots=len(events), sent=sum(e['raw'] is not None for e in events),
                rounds=max(e['round'] for e in events),
                agreement=len(set(loyal.values()))<=1,
                validity=all(v==command for v in loyal.values()) if nodes[0] not in faulty else None)
