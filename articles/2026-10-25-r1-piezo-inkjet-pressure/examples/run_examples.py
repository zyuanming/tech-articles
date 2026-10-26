"""Deterministic pedagogical calculations; not a printhead simulation.
Code and generated numeric data: CC0-1.0.
"""
from pathlib import Path
import json
import math
P = dict(radius_m=15e-6, nozzle_length_m=50e-6,
         density=1000.0, viscosity=0.004,
         surface_tension=0.030, chamber_m3=1e-9,
         compliance_m3_pa=1e-18, stroke_m3=30e-15,
         voltage_v=30.0, mean_wall_m=30e-9,
         active_area_m2=1e-6, acoustic_length_m=0.010,
         sound_speed_m_s=1000.0, drive_pa=20000.0,
         duration_s=20e-6)
r=P['radius_m']; l=P['nozzle_length_m']
rho=P['density']; mu=P['viscosity']; sigma=P['surface_tension']
A=math.pi*r*r
R=8*mu*l/(math.pi*r**4)
M=rho*l/A
pc=2*sigma/r
tau=M/R
qinf=(P['drive_pa']-pc)/R
T=P['duration_s']
def at(t):
 q=qinf*(-math.expm1(-t/tau))
 v=qinf*(t-tau*(-math.expm1(-t/tau)))
 return dict(t_us=t*1e6, q_pl_us=q*1e9,
             u_m_s=q/A, volume_pl=v*1e15)
end=at(T)
d=(6*end['volume_pl']*1e-15/math.pi)**(1/3)
u=end['u_m_s']; D=2*r
scales=dict(Re=rho*u*D/mu, We=rho*u*u*D/sigma,
            Oh=mu/math.sqrt(rho*sigma*D),
            capillary_time_us=math.sqrt(rho*r**3/sigma)*1e6,
            equivalent_diameter_um=d*1e6)
# A deliberately separate linear timing illustration, not a wave solver.
roundtrip=2*P['acoustic_length_m']/P['sound_speed_m_s']*1e6
def pulse(t,center,amp):
 return amp*max(0.0,1.0-abs(t-center)/4.0)
wave=[]
for i in range(561):
 t=-4+i*0.1
 a=pulse(t,0,-10)
 b=pulse(t,roundtrip,8)
 wave.append(dict(t_us=t, initial=a, reflected=b,
                  compression_matched=pulse(t,roundtrip,10),
                  compression_late=pulse(t,roundtrip+12,10),
                  matched=a+b+pulse(t,roundtrip,10),
                  late=a+b+pulse(t,roundtrip+12,10)))
# Numerical quadrature independently checks the closed-form volume.
N=20000; dt=T/N
volnum=dt*(at(0)['q_pl_us']/1e9/2+
           sum(at(i*dt)['q_pl_us']/1e9 for i in range(1,N))+
           at(T)['q_pl_us']/1e9/2)
assert abs(volnum-end['volume_pl']*1e-15)<1e-21
assert abs(scales['Oh']-math.sqrt(scales['We'])/scales['Re'])<1e-12
assert math.isclose(P['stroke_m3'],P['mean_wall_m']*P['active_area_m2'])
# A single illustrative explicit-Euler first step, starting at rest.
dtstep=1e-6
firstq=dtstep*(P['drive_pa']-pc)/M
visc=[]
for ratio in [0.25,1,4]:
 m=mu*ratio; rr=8*m*l/(math.pi*r**4); tt=M/rr
 qi=(P['drive_pa']-pc)/rr
 qe=qi*(-math.expm1(-T/tt))
 ve=qi*(T-tt*(-math.expm1(-T/tt)))
 visc.append(dict(mu_mpa_s=m*1000,q_pl_us=qe*1e9,
                  volume_pl=ve*1e15,Oh=m/math.sqrt(rho*sigma*D)))
caps=[]
for deg in [120,60]:
 theta=math.radians(deg); f=math.tan(theta/2)
 a=(6*end['volume_pl']*1e-15/(math.pi*f*(3+f*f)))**(1/3)
 h=a*f; radius=a/math.sin(theta)
 assert math.isclose(math.pi*h*(3*a*a+h*h)/6,end['volume_pl']*1e-15)
 caps.append(dict(angle_deg=deg,base_radius_um=a*1e6,
                  height_um=h*1e6,sphere_radius_um=radius*1e6))
voltage=[dict(t_us=t,voltage_v=v) for t,v in
         [(0,0),(5,P['voltage_v']),(25,P['voltage_v']),(30,0),(40,0)]]
res=dict(identity='设定参数的教学计算；不是设备实测或自由表面模拟',
         parameters=P, spherical_caps=caps, voltage=voltage, area_um2=A*1e12, resistance=R,
         inertance=M, capillary_pa=pc, tau_us=tau*1e6,
         closed_pressure_pa=P['stroke_m3']/P['compliance_m3_pa'],
         equivalent_bulk_pa=P['chamber_m3']/P['compliance_m3_pa'],
         volume_fraction=P['stroke_m3']/P['chamber_m3'],
         q_inf_pl_us=qinf*1e9,
         first_step=dict(dt_us=dtstep*1e6,q_pl_us=firstq*1e9,
                         u_m_s=firstq/A,exact=at(dtstep)),
         table=[at(t*1e-6) for t in [0,1,5,10,20]],
         curve=[at(i*T/400) for i in range(401)],
         end=end,scales=scales,viscosity_comparison=visc,
         acoustic=dict(roundtrip_us=roundtrip,one_way_us=roundtrip/2,
                       reflected_ratio=-0.8,wave=wave,
                       matched_peak=max(z['matched'] for z in wave),
                       late_peak=max(z['late'] for z in wave)),
         pressure_budget=dict(capillary_kpa=pc/1000,
                              viscous_kpa=R*end['q_pl_us']/1e12,
                              inertia_kpa=(P['drive_pa']-pc-R*end['q_pl_us']/1e9)/1000),
         checks=dict(volume_quadrature_error_m3=abs(volnum-end['volume_pl']*1e-15),
                     deterministic=True,free_surface=False))
Path(__file__).with_name('results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:res[k] for k in ['area_um2','resistance','inertance','capillary_pa','tau_us','end','scales','pressure_budget']},indent=2))
