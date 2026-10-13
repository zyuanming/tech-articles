"""Original MIT-licensed, frictionless instantaneous 2D impulse teaching model.
Not Box2D-Lite. No collision detection or time integration is implemented here.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import math,random,json,copy,platform
HERE=Path(__file__).resolve().parent

def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def scale(s,a):return (s*a[0],s*a[1])
@dataclass
class Body:
    mass:float
    inertia:float
    position:tuple
    velocity:tuple
    omega:float=0.
    @property
    def inv_mass(self):return 0. if math.isinf(self.mass) else 1/self.mass
    @property
    def inv_inertia(self):return 0. if math.isinf(self.inertia) else 1/self.inertia

def at_contact(body,point):
    r=sub(point,body.position)
    return add(body.velocity,(-body.omega*r[1],body.omega*r[0]))
def kinetic(body):
    return 0. if math.isinf(body.mass) else .5*body.mass*dot(body.velocity,body.velocity)+.5*body.inertia*body.omega**2
def totals(a,b):
    p=(0.,0.);ang=0.;energy=0.
    for body in [a,b]:
        if math.isinf(body.mass):continue
        momentum=scale(body.mass,body.velocity);p=add(p,momentum)
        ang+=cross(body.position,momentum)+body.inertia*body.omega;energy+=kinetic(body)
    return {'momentum':p,'angular_momentum_origin':ang,'kinetic':energy}
def resolve(a,b,point,normal,e):
    """Normal from A toward B, common world-space contact, separating => no impulse."""
    assert abs(dot(normal,normal)-1)<1e-10 and 0<=e<=1
    a,b=copy.deepcopy(a),copy.deepcopy(b)
    ra=sub(point,a.position);rb=sub(point,b.position)
    vn=dot(sub(at_contact(b,point),at_contact(a,point)),normal)
    K=a.inv_mass+b.inv_mass+cross(ra,normal)**2*a.inv_inertia+cross(rb,normal)**2*b.inv_inertia
    assert K>0
    j=-(1+e)*vn/K if vn<0 else 0.
    impulse=scale(j,normal)
    a.velocity=sub(a.velocity,scale(a.inv_mass,impulse));a.omega-=a.inv_inertia*cross(ra,impulse)
    b.velocity=add(b.velocity,scale(b.inv_mass,impulse));b.omega+=b.inv_inertia*cross(rb,impulse)
    after=dot(sub(at_contact(b,point),at_contact(a,point)),normal)
    return a,b,{'vn_before':vn,'vn_after':after,'K':K,'j':j,'e':e}

def stacked_iterations(rounds=8):
    # Two 1kg point-mass vertical degrees of freedom. Ground is fixed.
    # A stripped-down algebra example, not a rigid-box engine run.
    v=[-1.,-1.];l=[0.,0.];trace=[{'round':0,'v':v.copy(),'lambda':l.copy()}]
    for iteration in range(rounds):
        old=l[0];l[0]=max(0.,old-v[0]);v[0]+=l[0]-old
        relative=v[1]-v[0];old=l[1];l[1]=max(0.,old-relative/2);j=l[1]-old;v[0]-=j;v[1]+=j
        trace.append({'round':iteration+1,'v':v.copy(),'lambda':l.copy()})
    return trace

def run():
    cases=[]
    for e in [0,.5,1]:
        a=Body(2,1,(-1,0),(3,0));b=Body(1,1,(1,0),(0,0));aa,bb,result=resolve(a,b,(0,0),(1,0),e)
        cases.append(dict(result,before=totals(a,b),after=totals(aa,bb),vA=aa.velocity,vB=bb.velocity))
    ground=Body(math.inf,math.inf,(0,0),(0,0));box=Body(2,4/3,(0,1),(0,-3));aa,bb,corner=resolve(ground,box,(1,0),(0,1),0)
    corner.update(velocity=bb.velocity,omega=bb.omega,contact_velocity=at_contact(bb,(1,0)))
    assert abs(corner['j']-2.4)<1e-12 and abs(bb.velocity[1]+1.8)<1e-12 and abs(bb.omega-1.8)<1e-12
    a=Body(2,1,(-1,0),(-1,0));b=Body(1,1,(1,0),(2,0));_,_,separating=resolve(a,b,(0,0),(1,0),.5);assert separating['j']==0
    rng=random.Random(20261013);max_momentum=max_angular=max_restitution=max_energy=0.
    for _ in range(4000):
        theta=rng.uniform(-math.pi,math.pi);n=(math.cos(theta),math.sin(theta));point=(rng.uniform(-2,2),rng.uniform(-2,2))
        a=Body(rng.uniform(.2,5),rng.uniform(.1,5),(-1,rng.uniform(-1,1)),(rng.uniform(-4,4),rng.uniform(-4,4)),rng.uniform(-2,2))
        b=Body(rng.uniform(.2,5),rng.uniform(.1,5),(1,rng.uniform(-1,1)),(rng.uniform(-4,4),rng.uniform(-4,4)),rng.uniform(-2,2))
        rel=dot(sub(at_contact(b,point),at_contact(a,point)),n)
        b.velocity=sub(b.velocity,scale(rel+rng.uniform(.01,5),n))
        e=rng.random();aa,bb,result=resolve(a,b,point,n,e);before=totals(a,b);after=totals(aa,bb)
        max_momentum=max(max_momentum,*map(abs,sub(before['momentum'],after['momentum'])))
        max_angular=max(max_angular,abs(before['angular_momentum_origin']-after['angular_momentum_origin']))
        max_restitution=max(max_restitution,abs(result['vn_after']+e*result['vn_before']))
        expected=before['kinetic']-.5*(1-e*e)*result['vn_before']**2/result['K']
        max_energy=max(max_energy,abs(after['kinetic']-expected));assert after['kinetic']<=before['kinetic']+1e-9
    assert max(max_momentum,max_angular,max_restitution,max_energy)<1e-9
    trace=stacked_iterations()
    for t in trace:assert abs(t['v'][0]+2**(-t['round']))<1e-12 and t['v'][0]==t['v'][1]
    # Accumulated correction: undo 0.2 of a previous 1.0, not clamp correction to zero.
    old=1.;delta=-.2;new=max(0.,old+delta);assert abs((new-old)+.2)<1e-12
    out={'python':platform.python_version(),'one_dimensional':cases,'corner_on_narrow_post':corner,'separating':separating,'two_mass_contact_iterations':trace,'accumulated_clamp':{'old':old,'proposed_delta':delta,'new':new,'applied_delta':new-old},'tests':{'random_cases':4000,'seed':20261013,'max_linear_momentum_error':max_momentum,'max_angular_momentum_error':max_angular,'max_restitution_error':max_restitution,'max_energy_formula_error':max_energy,'tolerance':1e-9}}
    (HERE/'analytic-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
