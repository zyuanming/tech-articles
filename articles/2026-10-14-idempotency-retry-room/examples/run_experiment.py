#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Actual local SQLite operations; no network, game service or payment API calls."""
from pathlib import Path
import argparse, concurrent.futures, json, os, sqlite3, subprocess, sys, threading

ACTOR, KEY, MODE = 'p7', 'K17', 'duo'
class KeyConflict(ValueError):
    pass

def connect(path):
    con = sqlite3.connect(path, timeout=10, isolation_level=None)
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA synchronous=FULL')
    return con

def initialize(path):
    con = connect(path)
    try:
        con.execute('PRAGMA journal_mode=DELETE')
        con.executescript('''
        CREATE TABLE rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            mode TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE receipts (
            actor TEXT NOT NULL,
            operation_key TEXT NOT NULL,
            parameters TEXT NOT NULL,
            http_status INTEGER NOT NULL,
            response_body TEXT NOT NULL,
            retained_since INTEGER NOT NULL,
            PRIMARY KEY(actor, operation_key)
        );
        CREATE TABLE naive_markers (
            actor TEXT NOT NULL,
            operation_key TEXT NOT NULL,
            PRIMARY KEY(actor, operation_key)
        );
        ''')
    finally:
        con.close()

def canonical_parameters(mode):
    if mode not in ('duo', 'squad'):
        raise ValueError('mode must be duo or squad')
    return json.dumps({'mode': mode}, sort_keys=True, separators=(',', ':'))

def insert_room(con, actor, mode):
    room_id = con.execute('INSERT INTO rooms(owner, mode) VALUES (?, ?)', (actor, mode)).lastrowid
    return {'room_id': f'R{room_id:03d}', 'mode': mode}

def create_with_key(path, actor, key, mode, *, now=0, crash_phase=None):
    """This table belongs only to create-room; actor is assumed already authenticated.
    Serializes all writers for pedagogy, not a high-throughput production design.
    replayed is experiment metadata, outside the saved simulated HTTP body.
    """
    if not actor or not key:
        raise ValueError('actor and key required')
    parameters = canonical_parameters(mode)
    con = connect(path)
    try:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT parameters, http_status, response_body FROM receipts WHERE actor=? AND operation_key=?', (actor, key)).fetchone()
        if row:
            if row[0] != parameters:
                raise KeyConflict('same actor/key, different parameters')
            con.commit()
            return {'status': row[1], 'body': json.loads(row[2]), 'replayed': True}
        body = insert_room(con, actor, mode)
        if crash_phase == 'before_commit':
            os._exit(86)  # Actual child-process termination; not a power-loss test.
        body_text = json.dumps(body, sort_keys=True, separators=(',', ':'))
        con.execute('INSERT INTO receipts VALUES (?, ?, ?, ?, ?, ?)', (actor, key, parameters, 201, body_text, now))
        con.commit()
        if crash_phase == 'after_commit':
            os._exit(87)  # Durable transaction already returned; response not returned.
        return {'status': 201, 'body': json.loads(body_text), 'replayed': False}
    except BaseException:
        if con.in_transaction:
            con.rollback()
        raise
    finally:
        con.close()

def unsafe_create(path):
    con = connect(path)
    try:
        con.execute('BEGIN IMMEDIATE')
        body = insert_room(con, ACTOR, MODE)
        con.commit()
        return body
    finally:
        con.close()

def snapshot(path):
    con = connect(path)
    try:
        return {'rooms': [dict(id=f'R{r[0]:03d}', owner=r[1], mode=r[2], active=bool(r[3])) for r in con.execute('SELECT id,owner,mode,active FROM rooms ORDER BY id')],
                'receipts': [dict(actor=r[0], key=r[1], parameters=json.loads(r[2]), status=r[3], response=json.loads(r[4]), retained_since=r[5]) for r in con.execute('SELECT * FROM receipts ORDER BY actor,operation_key')],
                'naive_markers': [list(r) for r in con.execute('SELECT * FROM naive_markers ORDER BY actor,operation_key')]}
    finally:
        con.close()

def child(path, phase):
    if phase in ('before_commit', 'after_commit'):
        create_with_key(path, ACTOR, KEY, MODE, crash_phase=phase)
    elif phase == 'effect_first':
        unsafe_create(path)
        os._exit(88)  # Resource committed, receipt never written.
    elif phase == 'marker_first':
        con = connect(path)
        con.execute('BEGIN IMMEDIATE')
        con.execute('INSERT INTO naive_markers VALUES (?,?)', (ACTOR,KEY))
        con.commit()
        os._exit(89)  # Marker committed, resource never created.
    else:
        raise ValueError(phase)

def run(out):
    out.mkdir(parents=True, exist_ok=False)
    def db(name):
        p = out/(name+'.sqlite3'); initialize(p); return p
    results = {}
    p = db('unsafe_response_ignored')
    first = unsafe_create(p)  # Deliberately discard at the simulated client.
    retry = unsafe_create(p)
    results['unsafe_response_ignored'] = dict(first_server_result=first, retry=retry, final=snapshot(p))

    p = db('safe_response_ignored')
    first = create_with_key(p, ACTOR, KEY, MODE)
    retry = create_with_key(p, ACTOR, KEY, MODE)
    assert first['body'] == retry['body'] and not first['replayed'] and retry['replayed']
    results['safe_response_ignored'] = dict(first_server_result=first, retry=retry, final=snapshot(p))

    p = db('new_intent_same_parameters')
    first = create_with_key(p, ACTOR, KEY, MODE)
    second = create_with_key(p, ACTOR, 'K18', MODE)
    results['new_intent_same_parameters'] = dict(first=first, second=second, final=snapshot(p))

    p = db('same_key_different_parameters')
    first = create_with_key(p, ACTOR, KEY, MODE)
    try:
        create_with_key(p, ACTOR, KEY, 'squad')
        raise AssertionError('conflict not detected')
    except KeyConflict as e:
        conflict = str(e)
    results['same_key_different_parameters'] = dict(first=first, rejected=conflict, final=snapshot(p))

    p = db('same_key_different_actor')
    a = create_with_key(p, ACTOR, KEY, MODE)
    b = create_with_key(p, 'p8', KEY, MODE)
    results['same_key_different_actor'] = dict(first=a, second=b, final=snapshot(p))

    for phase, expected_code in [('before_commit',86), ('after_commit',87), ('effect_first',88), ('marker_first',89)]:
        p = db(phase)
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(p), phase], capture_output=True, text=True)
        assert process.returncode == expected_code, (process.returncode,process.stderr)
        before_retry = snapshot(p)
        if phase == 'marker_first':
            # The broken algorithm trusts a bare marker and skips the missing work.
            con = connect(p)
            seen = con.execute('SELECT 1 FROM naive_markers WHERE actor=? AND operation_key=?',(ACTOR,KEY)).fetchone()
            con.close()
            retry = {'skipped_because_seen': bool(seen), 'room_id': None}
        else:
            retry = create_with_key(p, ACTOR, KEY, MODE)
        results[phase] = dict(child_exit_code=process.returncode, before_retry=before_retry, retry=retry, final=snapshot(p))

    p = db('concurrent_same_key')
    barrier = threading.Barrier(2)
    def worker():
        barrier.wait(timeout=10)
        return create_with_key(p, ACTOR, KEY, MODE)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        calls = [pool.submit(worker) for _ in range(2)]
        outcomes = sorted((x.result(timeout=15) for x in calls),key=lambda r:r['replayed'])
    assert [x['replayed'] for x in outcomes] == [False,True]
    assert outcomes[0]['body']==outcomes[1]['body']
    results['concurrent_same_key'] = dict(outcomes_sorted_by_replayed=outcomes, winner_thread='not asserted; scheduling is nondeterministic', final=snapshot(p))

    p = db('receipt_expired')
    first = create_with_key(p, ACTOR, KEY, MODE, now=0)
    con = connect(p)
    con.execute('BEGIN IMMEDIATE')
    # Clock ticks are teaching units. Remove exactly the receipt aged 11 >= 10.
    removed = con.execute('DELETE FROM receipts WHERE retained_since <= ?', (11-10,)).rowcount
    con.commit(); con.close()
    forgotten = snapshot(p)
    late = create_with_key(p, ACTOR, KEY, MODE, now=11)
    results['receipt_expired'] = dict(retention_ticks=10, retry_tick=11, first=first, removed_receipts=removed, after_purge=forgotten, late_retry=late, final=snapshot(p))

    p = db('resource_lifecycle')
    first = create_with_key(p, ACTOR, KEY, MODE)
    con = connect(p);con.execute('UPDATE rooms SET active=0 WHERE id=1');con.close()
    retry = create_with_key(p, ACTOR, KEY, MODE)
    results['resource_lifecycle'] = dict(first=first, retry=retry, final=snapshot(p), meaning='Original creation result replayed; does not assert room is still open')

    # Expected counts are independent, hand-derived assertions on actual rows.
    expected_rooms={'unsafe_response_ignored':2,'safe_response_ignored':1,'new_intent_same_parameters':2,'same_key_different_parameters':1,'same_key_different_actor':2,'before_commit':1,'after_commit':1,'effect_first':2,'marker_first':0,'concurrent_same_key':1,'receipt_expired':2,'resource_lifecycle':1}
    for name,count in expected_rooms.items():
        assert len(results[name]['final']['rooms']) == count,(name,count)
    assert len(results['before_commit']['before_retry']['rooms']) == 0
    assert len(results['before_commit']['before_retry']['receipts']) == 0
    assert len(results['after_commit']['before_retry']['rooms']) == 1
    assert len(results['after_commit']['before_retry']['receipts']) == 1
    result=dict(identity='Actual Python sqlite3 experiment; replies deliberately ignored locally; no real network packet-loss or power-failure test',cases=results)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    environment=dict(python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,journal_mode='DELETE',synchronous='FULL',connection_timeout_seconds=10,concurrency='two threads, separate SQLite connections, common barrier; all writers serialized by BEGIN IMMEDIATE',child_crashes='os._exit at four explicit points; not OS/power/device failures')
    (out/'environment.json').write_text(json.dumps(environment,ensure_ascii=False,indent=2)+'\n')
    lines=['SQLite local experiment — no network service',f'Python {environment["python"]}; SQLite {environment["sqlite"]}']
    for name in expected_rooms:
        state=results[name]['final'];lines.append(f'{name}: rooms={len(state["rooms"])} receipts={len(state["receipts"])} markers={len(state["naive_markers"])}')
    lines.append('All asserted outcomes: PASS')
    transcript='\n'.join(lines)+'\n'
    (out/'stdout.txt').write_text(transcript)
    print(transcript,end='')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--child',nargs=2,metavar=('DATABASE','PHASE'))
    args=parser.parse_args()
    if args.child: child(Path(args.child[0]),args.child[1])
    elif args.output: run(args.output.resolve())
    else: parser.error('--output must name a new directory')
