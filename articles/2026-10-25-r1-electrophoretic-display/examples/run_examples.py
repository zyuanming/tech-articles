"""Deterministic teaching calculations, not an EPD calibration. CC0-1.0."""
from pathlib import Path
import json
P={'gap_m':30e-6,'voltage_v':15,'mobility_m2_v_s':2e-10,'pulse_s':.12,'refresh_energy_j':.012,'sleep_power_w':.00002,'observation_s':3600}
field=P['voltage_v']/P['gap_m'];speed=P['mobility_m2_v_s']*field;cross=P['gap_m']/speed
# p is one representative positive black particle's height/gap, NOT gray level.
def advance(p,v,t,mobility=P['mobility_m2_v_s']):
 return min(1,max(0,p+mobility*v*t/P['gap_m']**2))
V=P['voltage_v']; pulse=P['pulse_s']; initial_states=[.1,.6]
history=[{'start':p,'end':advance(p,V,pulse)} for p in initial_states]
reset=[{'start':p,'erased':advance(p,-V,cross),'written':advance(advance(p,-V,cross),V,pulse)} for p in initial_states]
trace=[]
trace_steps=42  # sampling resolution, not a physical parameter
for initial in initial_states:
 row=[]
 for i in range(trace_steps+1):
  t=i*(cross+pulse)/trace_steps
  p=advance(initial,-V,t) if t<=cross else advance(advance(initial,-V,cross),V,t-cross)
  row.append({'t_s':t,'p':p})
 trace.append({'initial':initial,'points':row})
zero=[.2,advance(.2,V,cross)];zero.append(advance(zero[-1],-V,cross))
energy=[]
for count in [1,60,3600]:
 update=count*P['refresh_energy_j'];sleep=P['sleep_power_w']*P['observation_s']
 energy.append({'updates':count,'update_j':update,'sleep_j':sleep,'total_j':update+sleep})
dither=[{'black_count':n,'total':16,'black_fraction':n/16,'cells':[int(i<n) for i in range(16)]} for n in [0,4,8,12,16]]
# Illustrative reset-to-white + write-to-black timing, not a commercial LUT.
lut=[]
for old in ['W','B']:
 for new in ['W','B']:
  segments=[[-V,cross],[V,cross]] if new=='B' else [[-V,cross]]
  state=0 if old=='W' else 1
  for v,t in segments:state=advance(state,v,t)
  assert abs(state-(0 if new=='W' else 1))<1e-10
  lut.append({'old':old,'new':new,'segments':segments,'final_state':state})
result={'parameters':P,'field_v_m':field,'speed_um_s':speed*1e6,'crossing_s':cross,'pulse_displacement_um':speed*P['pulse_s']*1e6,'history':history,'reset':reset,'reset_trace':trace,'zero_volt_seconds':{'states':zero,'integral_v_s':V*cross-V*cross},'energy':energy,'dither':dither,'mobility_comparison':[{'mobility':m,'crossing_s':P['gap_m']**2/(m*V)} for m in [P['mobility_m2_v_s'],P['mobility_m2_v_s']/2]],'transitions':lut}
assert abs(field-500000)<1e-8 and abs(cross-.3)<1e-10
assert all(abs(x['written']-.4)<1e-10 for x in reset)
assert abs(history[0]['end']-.5)<1e-10 and history[1]['end']==1
assert zero[-1]==0
out=Path(__file__).with_name('results.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Teaching calculations passed; results.json written.')
