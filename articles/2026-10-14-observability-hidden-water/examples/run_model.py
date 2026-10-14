#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exact rational discrete tank teaching model; not a physical tank experiment."""
from fractions import Fraction as F
from pathlib import Path
import argparse,csv,json,platform
DRAIN=F(1,5);G=F(1,10)

def value(v):
    return {'fraction':str(v),'litres':float(v)}

def advance(x,g=G,u=(F(0),F(0))):
    # All outflows and transfer use the volume at the start of the same step.
    transfer=g*(x[0]-x[1])
    return (x[0]-DRAIN*x[0]-transfer+u[0],x[1]-DRAIN*x[1]+transfer+u[1])

def trajectory(initial,g=G,steps=8,u=(F(0),F(0))):
    x=tuple(map(F,initial));rows=[]
    for n in range(steps+1):
        assert all(F(0)<=v<=10 for v in x)
        rows.append({'time_s':n,'left':value(x[0]),'right':value(x[1]),'sum':value(sum(x)),'difference':value(x[0]-x[1])})
        x=advance(x,g,u)
    return rows

def matrix_product_row(c,a):
    return [sum(c[k]*a[k][j] for k in range(2)) for j in range(2)]

def observation(c,g):
    a=[[F(4,5)-g,g],[g,F(4,5)-g]]
    rows=[c,matrix_product_row(c,a)]
    det=rows[0][0]*rows[1][1]-rows[0][1]*rows[1][0]
    return {'rows':[[str(x)for x in row]for row in rows],'determinant':str(det),'rank':2 if det else 1}

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    pairs={'A':(8,2),'B':(2,8),'C':(5,5)}
    traces={name:trajectory(x)for name,x in pairs.items()}
    for n in range(9):
        total=F(10)*F(4,5)**n;diff=F(6)*F(3,5)**n
        for row in [traces[k][n] for k in traces]:assert F(row['sum']['fraction'])==total
        assert F(traces['A'][n]['difference']['fraction'])==diff
        assert F(traces['B'][n]['difference']['fraction'])==-diff
        assert F(traces['C'][n]['difference']['fraction'])==0
        assert diff>0
    first=advance((F(8),F(2)))
    assert first==(F(29,5),F(11,5))
    first_account={'initial_litres':[8,2],'drain_left':value(F(8)*DRAIN),'drain_right':value(F(2)*DRAIN),'transfer_left_to_right':value(G*(8-2)),'after_left':value(first[0]),'after_right':value(first[1])}
    u=(F(3,10),F(1,10))
    input_traces={name:trajectory(x,u=u)for name,x in pairs.items()}
    for n in range(9):
        sums=[F(input_traces[name][n]['sum']['fraction'])for name in pairs];assert len(set(sums))==1
        if n:assert sums[0]==F(4,5)*F(input_traces['A'][n-1]['sum']['fraction'])+sum(u)
    recovery=[]
    for name,(left,right) in pairs.items():
        y0=F(left);y1=advance((F(left),F(right)))[0];estimate=(y1-F(7,10)*y0)/G
        assert estimate==right
        recovery.append(dict(case=name,observer_inputs=dict(y0= value(y0),y1=value(y1),known_diagonal='7/10',known_coupling='1/10',old_sum_measurement_used=False),recovered_right=value(estimate),truth_right_litres=right))
    noise=[]
    for g in [F(1,10),F(1,100)]:
        a=F(4,5)-g;y0=F(8);y1=advance((F(8),F(2)),g)[0];e0=F(1,50);e1=-F(1,50);m0=y0+e0;m1=y1+e1;estimate=(m1-a*m0)/g
        err=(e1-a*e0)/g;assert estimate-F(2)==err
        alt_y1=advance((F(8),F(3)),g)[0];assert alt_y1-y1==g
        noise.append(dict(coupling=str(g),diagonal=str(a),true_left0=value(y0),true_left1=value(y1),error0=value(e0),error1=value(e1),measured_left0=value(m0),measured_left1=value(m1),inferred_right=value(estimate),inference_error=value(err),truth_right_litres=2,new_comparison=dict(initial_states=[[8,2],[8,3]],second_readings=[value(y1),value(alt_y1)],separation=value(alt_y1-y1)),scope='One deterministic bounded error example; not random sensor measurements or a filter; negative inferred volume is not physical water'))
    assert F(noise[0]['inferred_right']['fraction'])==F(83,50)
    assert F(noise[1]['inferred_right']['fraction'])==-F(79,50)
    matrices={}
    for gs in ['1/10','1/100','0']:
        g=F(gs);matrices[gs]=dict(sum=observation([F(1),F(1)],g),left=observation([F(1),F(0)],g))
        assert matrices[gs]['sum']['rank']==1
        assert matrices[gs]['left']['rank']==(1 if g==0 else 2)
    result=dict(identity='Exact rational computation of an explicitly chosen discrete model, not physical experimental data',units=dict(volume='litre',sample_period_seconds=1,initial_capacity_each_litres=10),rule=dict(drain_per_step='1/5 of each initial step volume',coupling_per_step='1/10 of initial step left-right difference',update_matrix=[['7/10','1/10'],['1/10','7/10']],all_rates_evaluated_at_step_start=True),first_step_account=first_account,zero_input_trajectories=traces,known_input_demo=dict(add_at_each_step_end_litres=['3/10','1/10'],same_sequence_in_all_compared_experiments=True,trajectories=input_traces),left_sensor_recovery=recovery,observation_matrices=matrices,noise_examples=noise)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'trajectories.csv').open('w',newline='')as f:
        w=csv.writer(f);w.writerow(['input_case','state_case','time_s','left_litres','right_litres','sum_litres','difference_litres'])
        for inp,ts in [('zero',traces),('known_0.3_0.1',input_traces)]:
            for k,rows in ts.items():
                for row in rows:w.writerow([inp,k,row['time_s'],*[format(row[q]['litres'],'.8f')for q in ['left','right','sum','difference']]])
    text='\n'.join(['Exact-rational discrete tank model; no physical experiment',f'Python {platform.python_version()}',f'A first step: {first[0]} L, {first[1]} L','A/B/C sum traces: identical exactly at all 9 recorded instants','All 9 finite-step A-B differences: nonzero','Known-input paired outputs: identical exactly','Left-sensor recovery A/B/C: exact','Two-step sum observation rank: 1','Two-step left observation rank: 2 for g=0.1 and 0.01; 1 for g=0',f'Noise sample, g=0.1: inferred right {float(F(noise[0]["inferred_right"]["fraction"])):.2f} L',f'Noise sample, g=0.01: inferred right {float(F(noise[1]["inferred_right"]["fraction"])):.2f} L','All rational assertions: PASS'])+'\n'
    (out/'stdout.txt').write_text(text);print(text,end='')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();run(args.output.resolve())
