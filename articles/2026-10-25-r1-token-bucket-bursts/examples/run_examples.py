"""Run deterministic exact examples and independent finite checks. CC0-1.0."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,platform
from model import INPUT,RATE,CAPACITY,police,shape,encode

def interval_check(rows, tk='time'):
    checked=0
    for i,a in enumerate(rows):
        for j in range(i,len(rows)):
            amount=sum((r['cost'] for r in rows[i:j+1]),F(0))
            bound=CAPACITY+RATE*(rows[j][tk]-a[tk])
            assert amount<=bound
            checked+=1
    return checked

def run():
    rows=police(); shaped=shape()
    assert ''.join(r['name'] for r in rows if r['allowed'])=='ABEFHI'
    assert [r['after'] for r in rows]==list(map(F,[2,0,0,1,0,0,6,0,0]))
    assert [r['departure'] for r in shaped]==[F(0),F(0),F('0.5'),F('1.5'),F(3),F('3.5'),None,F('6.5'),F(7)]
    count=interval_check([r for r in rows if r['allowed']])
    count+=interval_check([r for r in shaped if r['departure'] is not None],'departure')
    # Independent tick oracle: quarter-second ticks, integer half-credit units.
    # Exhaust every length-four size sequence, arrivals 0,.25,.5,.75 seconds.
    cases=0
    for costs in product(range(1,8),repeat=4):
        events=[(str(i),str(F(i,4)),str(c)) for i,c in enumerate(costs)]
        oracle=12; expected=[]
        for i,c in enumerate(costs):
            if i:oracle=min(12,oracle+1)
            ok=oracle>=2*c
            if ok:oracle-=2*c
            expected.append((ok,F(oracle,2)))
        got=police(events)
        assert [(r['allowed'],r['after']) for r in got]==expected
        cases+=1
    points=[F(i,4) for i in range(25)]
    idle=[dict(time=t,credit=min(CAPACITY,RATE*t),uncapped=RATE*t) for t in points]
    windows=[]
    for t in [F(1,2),F(1),F(3),F(10),F(60)]:
        windows.append(dict(duration=t,burst=CAPACITY,refill=RATE*t,
                            bound=CAPACITY+RATE*t,mean=RATE+CAPACITY/t))
    fw_events=[('a','0.99','1'),('b','0.99','1'),('c','1.01','1'),('d','1.01','1')]
    fw_tb=police(fw_events,rate=2,capacity=2)
    bins={}; accepted=[]
    for n,t,c in fw_events:
        window=int(F(t)); used=bins.get(window,0);ok=used+int(c)<=2
        if ok:bins[window]=used+int(c)
        accepted.append(ok)
    peak=F(8); duration=CAPACITY/(peak-RATE)
    peak_curve=[dict(time=t,credit=max(F(0),CAPACITY-(peak-RATE)*t)) for t in [F(i,8) for i in range(9)]]
    race_credit=F(1); race_cost=F(1)
    race_reads=[race_credit,race_credit]
    race_decisions=[q>=race_cost for q in race_reads]
    race_writes=[]
    for q,ok in zip(race_reads,race_decisions):
        if ok:race_credit=q-race_cost
        race_writes.append(race_credit)
    unsafe_count=sum(race_decisions)
    assert unsafe_count==2 and race_credit==0
    data=dict(python=platform.python_version(),parameters=dict(rate=RATE,capacity=CAPACITY,bytes_per_credit=1000,initial=CAPACITY),input=INPUT,
              policing=rows,shaping=shaped,idle=idle,windows=windows,
              peak=dict(rate=peak,duration=duration,amount=peak*duration,curve=peak_curve),
              fixed=dict(input=fw_events,window_allowed=accepted,token_rows=fw_tb,
                         gap=F(fw_events[2][1])-F(fw_events[0][1]),
                         window_count=sum(accepted),token_count=sum(r['allowed'] for r in fw_tb)),
              initial_comparison=dict(full=police([INPUT[0]]),empty=police([INPUT[0]],initial=0),empty_wait=F(INPUT[0][2])/RATE),
              race=dict(initial=F(1),cost=race_cost,reads=race_reads,decisions=race_decisions,writes=race_writes,final=race_credit,unsafe_allowed=unsafe_count,serial_allowed=sum(r['allowed'] for r in police([('X','0','1'),('Y','0','1')],capacity=1))),
              checks=dict(exhaustive_sequences=cases,intervals=count))
    return encode(data)
if __name__=='__main__':
    data=run();Path(__file__).with_name('results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data['checks'],ensure_ascii=False))
