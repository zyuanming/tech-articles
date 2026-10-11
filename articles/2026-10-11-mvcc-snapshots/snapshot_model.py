"""An intentionally small snapshot-isolation teaching model, not PostgreSQL.
It enumerates six-event schedules for two transactions updating different rows.
No SQL, locks, MVCC storage, SSI implementation, crash recovery or performance test.
"""
from itertools import combinations

def schedules():
    # Keep read -> decide/write -> commit inside each transaction.
    for a_positions in combinations(range(6), 3):
        a_events = iter(('A.read', 'A.write', 'A.commit'))
        b_events = iter(('B.read', 'B.write', 'B.commit'))
        yield [next(a_events) if i in a_positions else next(b_events)
               for i in range(6)]

def run(events):
    committed = {'A': 1, 'B': 1}
    snapshots, pending = {}, {'A': {}, 'B': {}}
    for event in events:
        who, step = event.split('.')
        if step == 'read':
            snapshots[who] = committed.copy()
        elif step == 'write':
            if sum(snapshots[who].values()) > 1:
                pending[who][who] = 0
        elif step == 'commit':
            committed.update(pending[who])
    return committed

if __name__ == '__main__':
    serial_a = ['A.read', 'A.write', 'A.commit',
                'B.read', 'B.write', 'B.commit']
    serial_b = ['B.read', 'B.write', 'B.commit',
                'A.read', 'A.write', 'A.commit']
    all_schedules = list(schedules())
    bad = [s for s in all_schedules if sum(run(s).values()) == 0]
    assert len(all_schedules) == 20
    assert len(bad) == 18
    assert run(serial_a) == {'A': 0, 'B': 1}
    assert run(serial_b) == {'A': 1, 'B': 0}
    print('A then B:', run(serial_a))
    print('B then A:', run(serial_b))
    print('Order-preserving schedules:', len(all_schedules))
    print('Schedules ending with zero on duty:', len(bad))
    print('Example:', ' -> '.join(bad[0]))
