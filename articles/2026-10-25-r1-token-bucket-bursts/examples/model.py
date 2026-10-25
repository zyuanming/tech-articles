"""Exact, serial, strict token bucket teaching model. CC0-1.0."""
from fractions import Fraction as F

INPUT = [('A','0','4'),('B','0','2'),('C','0','1'),
         ('D','0.5','2'),('E','1.5','3'),('F','2','1'),
         ('G','5','7'),('H','5','6'),('I','5.5','1')]
RATE, CAPACITY = F(2), F(6)

def police(events=INPUT, rate=RATE, capacity=CAPACITY, initial=None):
    rate, capacity = F(rate), F(capacity)
    credit = capacity if initial is None else F(initial)
    assert rate > 0 and capacity > 0 and 0 <= credit <= capacity
    previous = F(0)
    result=[]
    for name, arrival, cost in events:
        t, cost = F(arrival), F(cost)
        assert t >= previous and cost > 0
        elapsed = t-previous
        added = rate*elapsed
        before = min(capacity,credit+added)
        lost = max(F(0),credit+added-capacity)
        allowed = cost <= before
        after = before-cost if allowed else before
        result.append(dict(name=name,time=t,cost=cost,previous=previous,
                           old=credit,elapsed=elapsed,generated=added,
                           capped=lost,before=before,allowed=allowed,after=after))
        credit, previous = after,t
    return result

def shape(events=INPUT, rate=RATE, capacity=CAPACITY):
    """Offline FIFO eligibility, infinite waiting room, zero link service time.
    Oversize packets removed immediately, before FIFO; no time reservation.
    """
    credit, previous = capacity,F(0)
    result=[]
    for name,arrival,cost in events:
        arrival,cost = F(arrival),F(cost)
        if cost>capacity:
            result.append(dict(name=name,arrival=arrival,cost=cost,
                               status='oversize',departure=None,wait=None))
            continue
        head = max(arrival,previous)
        before = min(capacity,credit+rate*(head-previous))
        extra = max(F(0),(cost-before)/rate)
        departure = head+extra
        credit = min(capacity,before+rate*extra)-cost
        previous = departure
        result.append(dict(name=name,arrival=arrival,cost=cost,status='released',
                           head=head,before=before,extra=extra,
                           departure=departure,wait=departure-arrival,after=credit))
    return result

def encode(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value
