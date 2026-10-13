"""Exact-arithmetic teaching SAR ADC, not a hardware or production ADC model.
Convention: unipolar floor quantizer; input >= DAC retains the trial bit.
"""
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
import math,json,random,sys

def sar(vin, n=8, reference=F(256,100), offset=F(0)):
    if not isinstance(n,int) or n<1 or reference<=0:raise ValueError('configuration')
    if not isinstance(vin,(list,tuple)):vin=[F(vin)]*n
    if len(vin)!=n:raise ValueError('one input per comparison')
    code=0;steps=[];hi=2**n
    for j,bit in enumerate(range(n-1,-1,-1)):
        trial=code+2**bit;threshold=reference*trial/2**n
        keep=vin[j]+offset>=threshold
        if keep:code=trial
        else:hi=trial
        steps.append(dict(step=j+1,weight=2**bit,trial=trial,trial_bits=format(trial,f'0{n}b'),
            threshold=float(threshold),vin=float(vin[j]),keep=keep,code=code,
            low=float(reference*code/2**n),high=float(reference*hi/2**n)))
    return code,steps

def run():
    reference=F(256,100);v=F(1737,1000);code,steps=sar(v)
    assert code==173 and [s['keep'] for s in steps]==[True,False,True,False,True,True,False,True]
    assert [s['trial'] for s in steps]==[128,192,160,176,168,172,174,173]
    points=0
    for n in range(1,13):
        for k in range(2**n):
            for fraction in [F(0),F(1,2),F(999,1000)]:
                x=(k+fraction)*reference/2**n;r,trace=sar(x,n,reference)
                assert r==k and len(trace)==n
                assert F(r)*reference/2**n<=x<F(r+1)*reference/2**n
                for step in trace:assert step['low']<=float(x)<step['high']
                points+=1
        assert sar(F(-1),n,reference)[0]==0
        assert sar(reference,n,reference)[0]==2**n-1
        assert sar(reference+1,n,reference)[0]==2**n-1
    # Offset model adds 20 mV to the comparator input; no noise is added here.
    offset_code,_=sar(v,offset=F(2,100));assert offset_code==175
    assert sar(F('0.427'))[0]==42
    assert [sar(F(x))[0] for x in ['1.7299','1.7300','1.7301']]==[172,173,173]
    assert sar(v,n=9)[0]==347
    actual_reference=F(250,100);ref_code,_=sar(v,reference=actual_reference);assert ref_code==177
    moving=[F(12,10)+F(i,7) for i in range(8)]
    moving_code,moving_trace=sar(moving);held_code,_=sar(moving[0])
    rng=random.Random(20261013);hist=Counter()
    for _ in range(10000):
        # One noise value per held sample; this does not model noisy decisions inside a conversion.
        x=1.73+rng.gauss(0,.002);hist[min(255,max(0,math.floor(x/.01)))]+=1
    cap=[]
    for k in range(8):
        # 4C, 2C, C bit capacitors plus grounded dummy C: total=8C.
        bottoms=[reference if k&w else F(0) for w in [4,2,1]]+[F(0)]
        top=-v+sum(c*b for c,b in zip([4,2,1,1],bottoms))/8
        charge=sum(c*(top-b) for c,b in zip([4,2,1,1],bottoms))
        assert charge==-8*v
        cap.append({'bits':f'{k:03b}','vtop':float(top),'stored_top_charge_in_CV':float(charge)})
    max_center_error=max(abs((k+.5)*.01-float((F(k)+F(j,100))*F(1,100))) for k in range(256) for j in range(100))
    assert abs(max_center_error-.005)<1e-12
    result={'python':sys.version.split()[0],'model':'ideal floor-quantizer SAR; >= retains; clipping at endpoints',
      'reference_V':float(reference),'input_V':float(v),'bits':8,'code':code,'binary':f'{code:08b}',
      'interval_V':[1.73,1.74],'midpoint_estimate_V':1.735,'steps':steps,
      'exact_test_points':points,'widths_tested':[1,12],'all_assertions':'PASS',
      'offset_added_V':.02,'offset_code':offset_code,'actual_reference_V':2.5,'reference_error_code':ref_code,
      'nominal_midpoint_estimate_with_wrong_reference_V':round((ref_code+.5)*.01,6),
      'moving_inputs_V':[float(x) for x in moving],'moving_code':moving_code,'held_code':held_code,'moving_trace':moving_trace,
      'noise_model':{'seed':20261013,'samples':10000,'mean_V':1.73,'sigma_V':.002,'histogram':dict(sorted(hist.items()))},
      'capacitor_charge_checks':cap,'acquisition_error_fraction_after_5_tau':math.exp(-5),
      'half_lsb_fraction_8bit':1/512,'required_tau_for_full_scale_to_half_lsb_8bit':math.log(512)}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['steps','moving_trace','capacitor_charge_checks']},ensure_ascii=False,indent=2))
    return result
if __name__=='__main__':run()
