"""Original teaching model. CC BY 4.0. No mercury or hardware experiment.
Only Python standard library. Run: python delay_model.py
Times are microseconds. An 8-slot ideal ring is NOT the EDSAC hardware.
"""
from pathlib import Path
import json, math, sys
BITS = [1,0,1,1,0,0,1,0]
BIT_US = 2
PERIOD_US = len(BITS)*BIT_US

def next_start(request_us, phase_us, period_us=PERIOD_US):
    """Earliest start >= request, ideal zero control/setup delay."""
    return phase_us + max(0, math.ceil((request_us-phase_us)/period_us))*period_us

def simulate(cycles=3, replacement=None, feedback=True):
    ring=BITS[:]
    rows=[]
    for k in range(cycles*len(BITS)):
        bit=ring.pop(0)
        slot=k%len(BITS)
        sent=bit if feedback else 0
        if replacement is not None and len(BITS)<=k<len(BITS)+4:
            # At t=16..22 replace A; explicit example only.
            sent=replacement[slot]
        rows.append(dict(time_us=k*BIT_US, slot=slot, read=bit, sent=sent))
        ring.append(sent)
    return rows

def write_b():
    ring=BITS[:]; out=[]
    replacement=[0,1,0,1]
    for k in range(24):
        bit=ring.pop(0); slot=k%8
        sent=replacement[slot-4] if 4<=k<8 else bit
        out.append(dict(time_us=k*2,slot=slot,read=bit,sent=sent))
        ring.append(sent)
    return out

def run():
    trace=simulate(); lost=simulate(feedback=False); rewritten=write_b()
    assert [r['read'] for r in trace]==BITS*3
    assert [r['read'] for r in lost][8:]==[0]*16
    expected=[1,0,1,1,0,1,0,1]
    assert [r['read'] for r in rewritten][8:16]==expected
    cases=[]
    for req in [0,3,8,9,24]:
        s=next_start(req,8)
        cases.append(dict(request_us=req,word='B',start_us=s,wait_us=s-req,finish_us=s+8))
    for phase in range(0,16,2):
        for req10 in range(1000):
            req=req10/10; t=next_start(req,phase)
            assert t>=req and 0<=t-req<16+1e-10
            assert abs((t-phase)/16-round((t-phase)/16))<1e-10
    received=[0.82,0.08,0.71,0.65,0.12,0.06,0.76,0.11]
    recovered=[int(x>=0.5) for x in received]
    assert recovered==BITS
    corrupted=received[:]; corrupted[2]=0.31
    assert [int(x>=0.5) for x in corrupted]!=BITS
    d=dict(model='ideal 8-slot educational ring; not EDSAC emulator',python=sys.version.split()[0],units='microseconds',bits=BITS,bit_us=2,period_us=16,trace=trace,feedback_off=lost,write_b=rewritten,requests=cases,regeneration=dict(received=received,threshold=0.5,recovered=recovered,corrupted=corrupted),counts=dict(short_slot_positions=18,short_useful_bits=17,long_slot_positions=36,long_useful_bits=35,short_words_per_tank=32,long_words_per_tank=16,first_day_active_tanks=4,first_complete_battery_tanks=16,eventual_tanks=32),checks='8000 next-arrival cases plus feedback, write and threshold assertions passed')
    p=Path(__file__).with_name('results.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({k:d[k] for k in ['model','python','requests','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
