#!/usr/bin/env python3
"""Original discrete teaching model. No hardware/sensor measurements. MIT."""
import math,json,csv,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def schmitt(x,previous,low,high):
    if not all(math.isfinite(v) for v in (x,low,high)):raise ValueError('finite values required')
    if not low<high:raise ValueError('low must be below high')
    if x>=high:return True
    if x<=low:return False
    return bool(previous)

def run(values,low=26,high=28,initial=False):
    state=initial;out=[]
    for x in values:
        state=schmitt(x,state,low,high);out.append(int(state))
    return out

def count_switches(states,initial=0):
    return sum(a!=b for a,b in zip([initial]+states,states))

def reference_voltage(vref,vout,rref,rf):
    # Input pin takes zero current; ideal fixed output voltage.
    return (vref/rref+vout/rf)/(1/rref+1/rf)

def data():
    hand=[25,27,28.2,27.8,28.1,27.9,27,26.1,25.9]
    rows=[];s=False
    for i in range(601):
        t=i/50
        x=25+.8*t if t<4 else 28+.18*math.sin(2*math.pi*3*(t-4)) if t<8 else 28-.6*(t-8)
        s=schmitt(x,s,26,28)
        rows.append({'t':t,'input':x,'one_threshold':int(x>=28),'hysteresis':int(s)})
    return hand,rows

def verify():
    n=0
    for low in [-2,0,26]:
      for width in [.25,1,2]:
       high=low+width
       for prior in [False,True]:
        for i in range(-10,21):
         x=low+width*i/10;z=schmitt(x,prior,low,high)
         assert z==(True if x>=high else False if x<=low else prior);n+=1
    rng=random.Random(20261013)
    for _ in range(5000):
      lo=rng.uniform(-100,100);hi=lo+rng.uniform(.01,20);x=rng.uniform(lo,hi)
      if lo<x<hi:
       assert not schmitt(x,False,lo,hi) and schmitt(x,True,lo,hi)
    for bad in [(float('nan'),0,1),(0,1,1),(0,2,1),(float('inf'),0,1)]:
      try:schmitt(bad[0],False,bad[1],bad[2])
      except ValueError:pass
      else:raise AssertionError('bad input accepted')
    assert reference_voltage(2.5,0,10000,40000)==2
    assert abs(reference_voltage(2.5,5,10000,40000)-3)<1e-12
    hand,rows=data();hs=run(hand);ss=[int(x>=28) for x in hand]
    assert hs==[0,0,1,1,1,1,1,1,0] and ss==[0,0,1,0,1,0,0,0,0]
    # A pulse crossing the upper boundary persists until lower crossed.
    assert run([25,29,27,27,25])==[0,1,1,1,0]
    # A full-scale bouncing switch crosses both boundaries repeatedly.
    assert run([0,3.3,0,3.3,0,3.3],1,2)==[0,1,0,1,0,1]
    return {'discrete_transition_cases':n,'random_memory_cases':5000,'seed':20261013,
      'hand_values':hand,'hand_single':ss,'hand_hysteresis':hs,'hand_single_switches':count_switches(ss),'hand_hysteresis_switches':count_switches(hs),
      'trace_samples':len(rows),'trace_single_switches':count_switches([r['one_threshold'] for r in rows]),'trace_hysteresis_switches':count_switches([r['hysteresis'] for r in rows]),
      'ideal_feedback_low_v':reference_voltage(2.5,0,10000,40000),'ideal_feedback_high_v':reference_voltage(2.5,5,10000,40000),'hardware_tested':False}

if __name__=='__main__':
    result=verify();(ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    hand,rows=data()
    with (ROOT/'trace.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(result,ensure_ascii=False,indent=2))
