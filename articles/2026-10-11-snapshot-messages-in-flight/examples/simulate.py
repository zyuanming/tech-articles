"""Original teaching model: one FIFO snapshot, two processes, no network or recovery."""
from collections import deque


def run(message_before_start=False):
    live = {'P': 5, 'Q': 3}
    channels = [('P', 'Q'), ('Q', 'P')]
    queues = {c: deque() for c in channels}
    saved, channel_log, closed = {}, {c: [] for c in channels}, set()

    def record(p):
        assert p not in saved
        saved[p] = live[p]
        # Marker is enqueued before any later application send on each output.
        for c in channels:
            if c[0] == p:
                queues[c].append(('marker', 0))

    def invariant():
        transit = sum(n for q in queues.values() for kind, n in q if kind == 'data')
        assert sum(live.values()) + transit == 8

    def send(channel, amount):
        sender, _ = channel
        assert 0 <= amount <= live[sender]
        live[sender] -= amount
        queues[channel].append(('data', amount))
        invariant()

    def deliver(channel):
        _, receiver = channel
        kind, amount = queues[channel].popleft()
        if kind == 'marker':
            if receiver not in saved:
                record(receiver)
            closed.add(channel)
        else:
            if receiver in saved and channel not in closed:
                channel_log[channel].append(amount)
            live[receiver] += amount
        invariant()

    send(('Q', 'P'), 2)
    if message_before_start:
        deliver(('Q', 'P'))
    record('P')
    deliver(('P', 'Q'))
    if not message_before_start:
        deliver(('Q', 'P'))
    deliver(('Q', 'P'))
    assert closed == set(channels)
    assert all(not q for q in queues.values())
    total = sum(saved.values()) + sum(sum(v) for v in channel_log.values())
    assert total == 8
    print('live =', live)
    print('saved =', saved)
    print('channels =', channel_log)
    print('snapshot_total =', total)
    return saved, channel_log


if __name__ == '__main__':
    assert run() == ({'P': 5, 'Q': 1}, {('P', 'Q'): [], ('Q', 'P'): [2]})
    print('\nVariant: message arrives before the snapshot starts')
    assert run(True) == ({'P': 7, 'Q': 1}, {('P', 'Q'): [], ('Q', 'P'): []})
