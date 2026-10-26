"""Sagnac teaching calculations; code and computed JSON CC0-1.0."""
from pathlib import Path
from decimal import Decimal, localcontext
import json, math
ROOT=Path(__file__).resolve().parent
c=299792458; R=.1; omega=1.; wavelength=1550e-9; turns=1000
A=math.pi*R*R; L=2*math.pi*R; beta=R*omega/c
single=4*A*omega/c**2; phase=2*math.pi*c/wavelength*single
D={'parameters':dict(c_m_s=c,radius_m=R,omega_rad_s=omega,wavelength_m=wavelength,turns=turns,index=1.5),
 'area_m2':A,'circumference_m':L,'beta':beta,'relative_coordinate_correction':beta**2/(1-beta**2),
 'time_zero_s':L/c,'single_delay_s':single,'single_phase_rad':phase,
 'coil_area_m2':turns*A,'coil_length_m':turns*L,'coil_delay_s':turns*single,'coil_phase_rad':turns*phase,
 'coil_transit_s':1.5*turns*L/c,'optical_period_s':wavelength/c}
# High precision verifies cancellation; ordinary doubles lose tiny differences.
medium=[]
with localcontext() as ctx:
 ctx.prec=70
 C=Decimal(c); V=Decimal(str(R))*Decimal(str(omega)); LL=Decimal(str(L))
 D['proper_vs_coordinate_relative_difference']=str(1-(1-(V/C)**2).sqrt())
 for n in (Decimal(1),Decimal('1.5'),Decimal(2)):
  u=C/n; wp=(u+V)/(1+u*V/C**2); wm=(-u+V)/(1-u*V/C**2)
  tp=LL/(wp-V); tm=LL/(V-wm); delta=tp-tm
  exact=2*LL*V/(C*C-V*V)
  assert abs(delta-exact)<Decimal('1e-65')
  medium.append({'index':float(n),'time_plus_s':str(tp),'time_minus_s':str(tm),'delay_s':str(delta),'proper_delay_s':str(delta*(1-(V/C)**2).sqrt())})
D['medium']=medium
D['tilts']=[{'degrees':t,'projection':math.cos(math.radians(t)),'phase_rad':turns*phase*math.cos(math.radians(t))} for t in (0,60,90,120,180)]
D['winding_cases']=[{'forward':f,'reverse':r,'effective_turns':f-r,'phase_rad':(f-r)*phase} for f,r in [(1000,0),(500,500),(750,250)]]
D['detector']=[{'omega':o,'phase':turns*phase*o/omega,'bright':(1+math.cos(turns*phase*o/omega))/2,'biased':(1-math.sin(turns*phase*o/omega))/2} for o in [-1,-.1,0,.1,1]]
D['curves']=[{'phase':x*math.pi/150,'bright':(1+math.cos(x*math.pi/150))/2,'biased':(1-math.sin(x*math.pi/150))/2} for x in range(-150,151)]
# Visible space-time example: x = lab arc length / L, q = ct / L, beta = .2.
b=.2;qp=1/(1-b);qm=1/(1+b)
D['visible']={'beta':b,'q_plus':qp,'q_minus':qm,'receiver_plus':b*qp,'receiver_minus':b*qm,'path_plus':qp,'path_minus':qm}
D['area_shapes']=[{'name':'正方形','width':.2,'height':.2},{'name':'扁长方形','width':.35,'height':.05}]
for z in D['area_shapes']:z.update(area=z['width']*z['height'],perimeter=2*(z['width']+z['height']))
D['bias']={'bias_deg_s':.01,'points':[{'t_s':t,'error_deg':.01*t} for t in range(0,61)]}
D['rlg']={'side_m':3.6,'wavelength_m':632.8e-9,'earth_omega_rad_s':7.292115e-5,'tilt_degrees':45.}
z=D['rlg'];z['area_m2']=z['side_m']**2;z['perimeter_m']=4*z['side_m'];z['frequency_hz']=4*z['area_m2']*z['earth_omega_rad_s']*math.cos(math.radians(z['tilt_degrees']))/(z['wavelength_m']*z['perimeter_m'])
# Invariant checks, zero/flip tests, units are stated in each field.
assert math.isclose(D['coil_phase_rad'],8*math.pi*turns*A*omega/(wavelength*c))
assert math.isclose(D['detector'][0]['bright'],D['detector'][-1]['bright'])
assert math.isclose(D['tilts'][1]['phase_rad'],D['coil_phase_rad']/2)
assert D['winding_cases'][1]['phase_rad']==0
assert math.isclose(D['area_shapes'][0]['perimeter'],D['area_shapes'][1]['perimeter'])
D['checks']=['70-digit relativistic velocity addition for n=1,1.5,2','phase formula equivalence','even cosine ambiguity','cos60 projection','opposite turns cancel','equal perimeter unequal area']
(ROOT/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:D[k] for k in ['single_delay_s','single_phase_rad','coil_phase_rad','coil_delay_s','coil_transit_s','optical_period_s']},indent=2));print('checks: PASS')
