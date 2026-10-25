"""CC0-1.0. Deterministic thin-element teaching model, lengths in mm."""
import json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent
N, F, R = 1.49, 200.0, 50.0

def slope(r, n=N):
    theta = math.atan(r / F)
    return math.atan2(math.sin(theta), n - math.cos(theta))

def bend(alpha, n=N):
    s = n * math.sin(alpha)
    return None if abs(s) > 1 else math.asin(s) - alpha

def reflect(i, n1, n2):
    t = math.asin(n1 * math.sin(i) / n2)
    rs = (n1*math.cos(i)-n2*math.cos(t))/(n1*math.cos(i)+n2*math.cos(t))
    rp = (n2*math.cos(i)-n1*math.cos(t))/(n2*math.cos(i)+n1*math.cos(t))
    return (rs*rs + rp*rp)/2

rows=[]
for r in [0, 10, 20, 30, 40, 50]:
    a=slope(r); d=bend(a)
    rows.append(dict(r=r, theta_deg=math.degrees(math.atan(r/F)), alpha_deg=math.degrees(a), beta_deg=math.degrees(math.asin(N*math.sin(a))), hit=r-F*math.tan(d), depth_per_mm=math.tan(a)))
assert max(abs(x['hit']) for x in rows)<1e-12
# An infinitesimally thin reference plane. Each annulus uses the slope
# of its midpoint, so each ray's focal-plane residual is r-r_mid.
pitches=[]
for p in [10.0,5.0,1.0]:
    zones=[]; samples=[]
    for j in range(round(R/p)):
        low=j*p; high=(j+1)*p; mid=(low+high)/2; a=slope(mid); d=bend(a)
        ray=[]
        for k in range(11):
            r=low+(high-low)*k/10
            hit=r-F*math.tan(d)
            ray.append({'r':r,'hit':hit}); samples.append(hit)
        zones.append(dict(low=low,high=high,mid=mid,alpha_deg=math.degrees(a),depth=p*math.tan(a),rays=ray))
    pitches.append(dict(pitch=p,zones=zones,max_abs_hit=max(abs(x) for x in samples),dead_fraction=0.05/p))
colors=[]
a=slope(40)
for label,n in [('低n假设',1.48),('设计值',1.49),('高n假设',1.50)]:
    d=bend(a,n); colors.append(dict(label=label,n=n,theta_deg=math.degrees(d),focus=40/math.tan(d),hit=40-F*math.tan(d)))
loss=[]
entry=reflect(0,1,N)
for r in [0,40,50]:
    a=slope(r); ex=reflect(a,N,1);loss.append(dict(r=r,entry_reflect=entry,exit_reflect=ex,two_surface_transmit=(1-entry)*(1-ex)))
# Paraxial finite-object illustration, a new stated use of same f.
u=1000.0; v=1/(1/F-1/u)
# Sphere radius (n-1)*f = 98 mm: different surface, same n and aperture.
sphere_radius=(N-1)*F
sphere=[]
for r in [10,30,50]:
    a=math.asin(r/sphere_radius); d=bend(a)
    sphere.append(dict(r=r,alpha_deg=math.degrees(a),focus=None if d is None else r/math.tan(d)))
# Lost path length delta z=1 mm: same angle does not imply same hit.
a=slope(40); d=bend(a)
translation_error=math.tan(d)*1.0
result=dict(conceptual_segments=[[{'r':j+k/20,'sag':(j+k/20)**2} for k in range(21)] for j in range(5)],model={'n':N,'f':F,'radius':R,'diameter':2*R,'dead_width':0.05,'sphere_radius':sphere_radius,'direction':'parallel rays +z, flat air-to-medium entry, tilted medium-to-air exit; all exit intersections at z=0','critical_angle_deg':math.degrees(math.asin(1/N)),'max_exit_deflection_deg':90-math.degrees(math.asin(1/N))},rays=rows,pitches=pitches,colors=colors,loss=loss,finite_object={'u':u,'v':v,'magnification':-v/u,'source_width':2,'paraxial_image_width':2*abs(v/u)},sphere=sphere,translation={'delta_z':1,'delta_hit':translation_error})
assert abs(v-250)<1e-9
assert abs(pitches[0]['max_abs_hit']-5)<1e-10
assert colors[0]['focus']>F>colors[-1]['focus']
assert all(0<x['two_surface_transmit']<1 for x in loss)
(ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['model','rays','colors','loss','finite_object','sphere','translation']},ensure_ascii=False,indent=2))
