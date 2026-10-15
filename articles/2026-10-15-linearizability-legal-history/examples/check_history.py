#!/usr/bin/env python3
"""Bounded, single-register teaching experiment. Python standard library only."""
import argparse, csv, itertools, json, platform, sys, threading, time
from pathlib import Path

def validate(ops):
    assert len({o['id'] for o in ops}) == len(ops)
    endpoints = []
    for o in ops:
        assert o['kind'] in ('write', 'read')
        assert isinstance(o['call'], int)
        endpoints.append(o['call'])
        if o['end'] is not None:
            assert o['end'] > o['call']
            endpoints.append(o['end'])
        if o['kind'] == 'write':
            assert o['value'] in (0, 1)
        if o['end'] is not None and o['kind'] == 'read':
            assert o['result'] in (0, 1)
    assert len(set(endpoints)) == len(endpoints), 'use unique event-order indices'

def complete_orders(ops):
    """Enumerate legal sequential witnesses for complete operations, initial value 0."""
    validate(ops)
    assert all(o['end'] is not None for o in ops)
    witnesses = []
    for order in itertools.permutations(ops):
        rank = {o['id']: i for i, o in enumerate(order)}
        if any(a['end'] < b['call'] and rank[a['id']] > rank[b['id']]
               for a in ops for b in ops):
            continue
        state = 0
        for o in order:
            if o['kind'] == 'write':
                state = o['value']
            elif o['result'] != state:
                break
        else:
            witnesses.append([o['id'] for o in order])
    return witnesses

def check(ops):
    """Complete any subset of pending writes at the tail, drop the remainder.
    Pending reads are deliberately outside this teaching checker's input contract.
    Precedence is checked on the extended history, including retained pending writes.
    """
    validate(ops)
    pending = [o for o in ops if o['end'] is None]
    assert all(o['kind'] == 'write' for o in pending)
    done = [o for o in ops if o['end'] is not None]
    tail = max([e for o in ops for e in (o['call'], o['end']) if e is not None] + [0])
    results = []
    for mask in itertools.product((False, True), repeat=len(pending)):
        retained = [dict(o, end=tail+i+1, result='ok')
                    for i, (o, keep) in enumerate(zip(pending, mask)) if keep]
        for w in complete_orders(done + retained):
            results.append({'order': w, 'included_pending': [o['id'] for o in retained]})
    return results

def op(name, kind, call, end, value=None, result=None):
    return dict(id=name, kind=kind, call=call, end=end, value=value, result=result)

def cases():
    return {
      'old_then_new': [op('W','write',1,6,1,'ok'),op('A','read',2,3,result=0),op('B','read',4,5,result=1)],
      'new_then_old': [op('W','write',1,6,1,'ok'),op('A','read',2,3,result=1),op('B','read',4,5,result=0)],
      'stale_after_write': [op('W','write',1,2,1,'ok'),op('A','read',3,4,result=0)],
      'call_sort_fails': [op('A','read',1,4,result=1),op('W','write',2,3,1,'ok')],
      'return_sort_fails': [op('W','write',1,4,1,'ok'),op('A','read',2,3,result=1)],
      'pending_needed': [op('W','write',1,None,1),op('A','read',2,3,result=1)],
      'pending_optional': [op('W','write',1,None,1),op('A','read',2,3,result=0)],
      'future_pending_cannot_help': [op('A','read',1,2,result=1),op('W','write',3,None,1)],
      'both_reads_overlap': [op('W','write',1,6,1,'ok'),op('A','read',2,5,result=1),op('B','read',3,4,result=0)],
    }

class Recorder:
    def __init__(self):
        self.rows = []
        self.lock = threading.Lock()
        self.start = time.perf_counter_ns()
    def event(self, ident, event, value):
        with self.lock:
            self.rows.append(dict(index=len(self.rows)+1, elapsed_ns=time.perf_counter_ns()-self.start,
                                  id=ident, event=event, value=value))

def threaded_run(broken=False):
    """Actual local threads; Events impose a deliberate schedule, not random stress."""
    rec = Recorder()
    entered, permit_write, committed, permit_return = [threading.Event() for _ in range(4)]
    lock = threading.Lock()
    state = [0]
    errors = []
    def wait(e):
        if not e.wait(5):
            raise RuntimeError('bounded event wait timed out')
    def writer():
        try:
            rec.event('W','call',1)
            entered.set()
            wait(permit_write)
            with lock:
                state[0] = 1
            committed.set()
            wait(permit_return)
            rec.event('W','return','ok')
        except Exception as exc:
            errors.append(repr(exc))
    def read(name, stale=False):
        rec.event(name,'call','read')
        with lock:
            value = 0 if stale else state[0]
        rec.event(name,'return',value)
    thread = threading.Thread(target=writer, daemon=True)
    thread.start()
    try:
        wait(entered)
        if not broken:
            read('A')
        permit_write.set()
        wait(committed)
        if broken:
            read('A')
        read('B',stale=broken)
    finally:
        permit_write.set()
        permit_return.set()
        thread.join(6)
    if thread.is_alive() or errors:
        raise RuntimeError(errors or 'thread did not finish')
    ops = []
    for name in ('W','A','B'):
        a, b = [e for e in rec.rows if e['id']==name]
        ops.append(op(name,'write' if name=='W' else 'read',a['index'],b['index'],
                      1 if name=='W' else None,b['value']))
    return {'events': rec.rows, 'operations': ops, 'witnesses': check(ops)}

def independent_one_write(ops):
    """Second criterion only for one write(1), two 0/1 reads, initial 0.
    Add all real-time edges, plus read(0)->W and W->read(1).
    An acyclic graph is exactly a valid total-order extension for this case.
    """
    edges = {(a['id'],b['id']) for a in ops for b in ops if a['end'] < b['call']}
    for o in ops:
        if o['kind'] == 'read':
            edges.add((o['id'],'W') if o['result']==0 else ('W',o['id']))
    remaining = {o['id'] for o in ops}
    while remaining:
        roots = {x for x in remaining if not any(b==x and a in remaining for a,b in edges)}
        if not roots:
            return False
        remaining -= roots
    return True

def exhaust():
    counts = {'endpoint_orders':0,'histories':0,'linearizable':0,'not_linearizable':0,'crosscheck_disagreements':0}
    endpoints = ['Wc','We','Ac','Ae','Bc','Be']
    for seq in itertools.permutations(endpoints):
        pos = {e:i+1 for i,e in enumerate(seq)}
        if any(pos[n+'c']>pos[n+'e'] for n in ('W','A','B')):
            continue
        counts['endpoint_orders'] += 1
        for ra,rb in itertools.product((0,1),repeat=2):
            ops = [op('W','write',pos['Wc'],pos['We'],1,'ok'),op('A','read',pos['Ac'],pos['Ae'],result=ra),op('B','read',pos['Bc'],pos['Be'],result=rb)]
            result = bool(check(ops))
            counts['histories'] += 1
            counts['linearizable' if result else 'not_linearizable'] += 1
            counts['crosscheck_disagreements'] += result != independent_one_write(ops)
    return counts

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    args=p.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=False)
    histories=cases()
    expected={'old_then_new':True,'new_then_old':False,'stale_after_write':False,'call_sort_fails':True,'return_sort_fails':True,'pending_needed':True,'pending_optional':True,'future_pending_cannot_help':False,'both_reads_overlap':True}
    fixed={k:{'operations':v,'witnesses':check(v)} for k,v in histories.items()}
    assert all(bool(fixed[k]['witnesses'])==v for k,v in expected.items())
    live={'locked_register':threaded_run(False),'injected_stale_read':threaded_run(True)}
    assert bool(live['locked_register']['witnesses'])
    assert not live['injected_stale_read']['witnesses']
    counts=exhaust(); assert counts['histories']==360 and counts['crosscheck_disagreements']==0
    result={'python':platform.python_version(),'clock':'perf_counter_ns; event indices used for ordering',
            'scope':'one register initially 0; values 0/1; finite history; synthetic cases plus local controlled threads',
            'fixed_cases':fixed,'threaded_runs':live,'exhaustive':counts}
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for name,run in live.items():
        with (out/(name+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['index','elapsed_ns','id','event','value']);w.writeheader();w.writerows(run['events'])
    lines=[f'Python {platform.python_version()}', 'Controlled local threads (not network/service measurement):']
    for name,run in live.items():
        lines.append(f"{name}: {'PASS' if run['witnesses'] else 'FAIL'} witness={run['witnesses']}")
        lines.extend(f"  {e['index']} {e['id']} {e['event']} {e['value']} elapsed_ns={e['elapsed_ns']}" for e in run['events'])
    lines.append('Exhaustive '+json.dumps(counts,sort_keys=True))
    lines.extend(f"{k}: {'PASS' if v['witnesses'] else 'FAIL'}" for k,v in fixed.items())
    text='\n'.join(lines)+'\n'; (out/'stdout.txt').write_text(text); print(text,end='')
if __name__=='__main__':main()
