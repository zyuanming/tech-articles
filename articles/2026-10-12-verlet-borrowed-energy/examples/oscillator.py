"""Original teaching experiment: 1D undamped spring, no engine or device test.
Python standard library only. Run: python oscillator.py
Units: x metres, v metres/second, mass kg, k N/metre, h seconds.
"""
import json
import math
import random
from fractions import Fraction


def step(method, x, v, h, omega=1.0):
    a = -omega * omega * x
    if method == 'explicit':
        return x + h*v, v + h*a  # both right-hand sides use old state
    if method == 'semi':
        v = v + h*a
        return x + h*v, v
    if method == 'verlet':
        half = v + 0.5*h*a
        x = x + h*half
        return x, half - 0.5*h*omega*omega*x
    raise ValueError(method)


def trajectory(method, h, steps, x=1.0, v=0.0, omega=1.0):
    states = [(0.0, x, v, (v*v + omega*omega*x*x)/2)]
    for n in range(steps):
        x, v = step(method, x, v, h, omega)
        states.append(((n+1)*h, x, v, (v*v + omega*omega*x*x)/2))
    return states


def main():
    # Fraction arithmetic checks the explicit-Euler amplification identity exactly.
    exact_cases = 0
    for x in range(-5, 6):
        for v in range(-5, 6):
            for h in [Fraction(1,10), Fraction(1,5), Fraction(1,2), Fraction(3,2)]:
                xx, vv = Fraction(x), Fraction(v)
                xn, vn = step('explicit', xx, vv, h, Fraction(1))
                assert xn*xn+vn*vn == (1+h*h)*(xx*xx+vv*vv)
                exact_cases += 1
    # Independent scalar position recurrence versus velocity-Verlet positions.
    rng = random.Random(1967)
    recurrence_cases = 0
    reverse_error = 0.0
    for _ in range(200):
        x, v = rng.uniform(-2,2), rng.uniform(-2,2)
        omega = rng.uniform(0.2,2)
        h = rng.uniform(0.01,0.5)/omega
        old = x - h*v - 0.5*h*h*omega*omega*x
        now = x
        for n in range(50):
            nxt = 2*now-old-h*h*omega*omega*now
            x, v = step('verlet', x, v, h, omega)
            assert abs(x-nxt) < 2e-10
            old, now = now, nxt
            recurrence_cases += 1
        start = (x,v)
        x1,v1 = step('verlet',x,v,h,omega)
        x2,v2 = step('verlet',x1,v1,-h,omega)
        reverse_error=max(reverse_error,abs(x2-start[0]),abs(v2-start[1]))
    assert reverse_error < 1e-12
    output={'parameters':{'mass':1,'k':1,'omega':1,'h':0.2,'steps':500,'x0':1,'v0':0},
            'first_step':{},'long_run':{},'checks':{'rational_euler_identity':exact_cases,'position_recurrence_comparisons':recurrence_cases,'one_step_reverse_max_error':reverse_error}}
    for method in ['explicit','semi','verlet']:
        states=trajectory(method,.2,500)
        ratios=[row[3]/states[0][3] for row in states]
        output['first_step'][method]=states[1]
        output['long_run'][method]={'last':states[-1],'energy_ratio_min':min(ratios),'energy_ratio_max':max(ratios)}
        if method=='explicit':
            assert math.isclose(ratios[-1],1.04**500,rel_tol=3e-14)
        elif method=='semi':
            invariant=[(v*v+x*x-.2*x*v)/2 for t,x,v,e in states]
            assert max(invariant)-min(invariant)<1e-12
        else:
            invariant=[(v*v+(1-.2**2/4)*x*x)/2 for t,x,v,e in states]
            assert max(invariant)-min(invariant)<1e-12
    boundary=trajectory('verlet',2,30,x=1,v=.1)
    over=trajectory('verlet',2.2,30,x=1,v=.1)
    output['boundary_h2']={'initial':boundary[0],'last':boundary[-1]}
    output['over_boundary_h2_2']={'initial':over[0],'last':over[-1]}
    output['phase_example_h1_t30']={'numerical':trajectory('verlet',1,30)[-1],'exact_x':math.cos(30),'exact_v':-math.sin(30),'numerical_period_seconds':6,'exact_period_seconds':2*math.pi}
    # Equal time T=20; reducing h delays explicit-Euler drift, not unconditional stability.
    output['explicit_equal_time_20']={str(h):trajectory('explicit',h,round(20/h))[-1][3]/.5 for h in [.4,.2,.1,.05]}
    print(json.dumps(output,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
