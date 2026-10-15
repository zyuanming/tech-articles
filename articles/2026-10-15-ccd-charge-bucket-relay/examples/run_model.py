#!/usr/bin/env python3
"""Original educational CCD bookkeeping, not semiconductor/device simulation. MIT."""
from pathlib import Path
from fractions import Fraction
import csv, json, math
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'examples'; O=ROOT/'originals'
def dump(name, obj): (E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def csvout(name, rows):
 with (E/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def ideal_readout(original):
 image=[r[:] for r in original]; serial=[0]*len(image[0]); outputs=[]; events=[]
 total=sum(map(sum,image))
 def record(kind, value=None, source=None):
  mass=sum(map(sum,image))+sum(serial)+sum(outputs)
  assert mass==total
  events.append(dict(step=len(events),kind=kind,source=source,output_e=value,image_e=[r[:] for r in image],serial_e=serial[:],output_so_far_e=outputs[:],conserved_e=mass))
 record('initial')
 for row in reversed(range(len(image))):
  assert not any(serial)
  serial=image[-1][:]; image=[[0]*len(serial)]+image[:-1];record('parallel')
  for col in range(len(serial)):
   q=serial[0];outputs.append(q);serial=serial[1:]+[0];record('serial',q,[row,col])
 assert outputs==[v for r in reversed(original) for v in r]
 reconstructed=[[0]*len(serial) for _ in original]
 for ev in events:
  if ev['source'] is not None:
   r,c=ev['source'];reconstructed[r][c]=ev['output_e']
 assert reconstructed==original and not any(map(any,image)) and not any(serial)
 return events,reconstructed

def residual_register(eta, steps=16):
 """Each step transfers eta of each slot left; remainder stays. Fractional mean charge."""
 q=[Fraction(0),Fraction(0),Fraction(0),Fraction(1000),Fraction(0),Fraction(0)]
 rows=[];total_out=Fraction(0)
 for t in range(1,steps+1):
  out=eta*q[0];q=[(1-eta)*q[i]+(eta*q[i+1] if i+1<len(q) else 0) for i in range(len(q))]
  total_out+=out;assert total_out+sum(q)==1000
  rows.append(dict(tick=t,output_e=float(out),remaining_e=float(sum(q)),cumulative_output_e=float(total_out)))
 return rows

def main():
 E.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
 original=[[100*(4*r+c+1) for c in range(4)] for r in range(3)]
 events,reconstructed=ideal_readout(original);dump('readout-events.json',events)
 serial=[e for e in events if e['kind']=='serial']
 csvout('readout.csv',[dict(sample=k+1,event_step=e['step'],source_row=e['source'][0],source_col=e['source'][1],electrons=e['output_e']) for k,e in enumerate(serial)])
 # Exhaustively enumerate all binary 2x3 images to validate serialization and conservation.
 for bits in range(64):
  a=[[(bits>>(r*3+c))&1 for c in range(3)] for r in range(2)]
  ideal_readout(a)
 efficiency=[dict(transfers=n,eta_09999=0.9999**n,eta_099999=0.99999**n) for n in range(0,2049)]
 csvout('efficiency.csv',efficiency)
 perfect=residual_register(Fraction(1));delayed=residual_register(Fraction(9,10))
 csvout('trail.csv',[dict(tick=a['tick'],ideal_e=a['output_e'],delayed_e=b['output_e'],remaining_e=b['remaining_e'],cumulative_e=b['cumulative_output_e']) for a,b in zip(perfect,delayed)])
 assert delayed[3]['output_e']==656.1 and delayed[4]['output_e']==262.44
 # Toy directed overflow to immediately following row; not a physical blooming solver.
 before=[100,1500,100];capacity=1000;after=before[:]
 for r in range(len(after)-1):
  excess=max(0,after[r]-capacity);after[r]-=excess;after[r+1]+=excess
 assert sum(before)==sum(after) and after==[100,1000,600]
 phases=[dict(stage=k,active=a,packet_center_gate=c) for k,(a,c) in enumerate([
  ('A',0),('A+B',0.5),('B',1),('B+C',1.5),('C',2),('C+A',2.5),('A',3)])]
 # Last A denotes next spatial A; active-phase state is periodic, position advances.
 results=dict(identity='deterministic educational bookkeeping model; no physical measurement',
 units='electrons; fractional values in transfer model are mean charge, not split individual electrons',
 initial_e=original,total_e=7800,events=len(events),parallel_events=3,serial_events=12,
 outputs_e=[e['output_e'] for e in serial],reconstructed_e=reconstructed,
 binary_2x3_cases_checked=64,phase_sequence=phases,
 eta_after_2048={str(e):e**2048 for e in [0.9999,0.99999]},
 residual_model={'eta':0.9,'pulse_initial_slot_zero_based':3,'initial_e':1000,'ticks':16,'last_state':delayed[-1]},
 bloom={'input_e':before,'capacity_e':capacity,'output_e':after,'rule':'excess moves to next row; no drain'},
 adc_example={'signal_e':900,'gain_e_per_DN':2,'bias_DN':100,'code_DN':550},
 exposure_example={'photons_per_s':1000,'quantum_efficiency':0.5,'exposure_s':0.2,'expected_signal_e':100})
 dump('results.json',results)
 print('ideal readout:',results['outputs_e'])
 print('charge conserved across',len(events),'states:',results['total_e'],'e-')
 print('exhaustive binary 2x3 images:',64,'PASS')
 print('2048-step retained fractions:',results['eta_after_2048'])
 print('delayed pulse first nonzero bins:',[r['output_e'] for r in delayed[3:7]])
 print('overflow toy:',before,'->',after)
if __name__=='__main__':main()
