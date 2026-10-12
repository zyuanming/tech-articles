"""Original educational model. Python standard library, no hardware or network.

Time is in seconds; speed y and command u are normalized. Plant: y'=-y+u.
Controller u(t)=k*(1-y(t-delay)); past history y(t)=0 for t<=0.
Delay is ONLY in the measurement path. Target steps from 0 to 1 at t=0.
The numerical solver uses RK4 with piecewise linear past interpolation.
A separate 70-digit finite method-of-steps expression checks selected points.
"""
from decimal import Decimal, localcontext
import cmath
import json
import math


def loop_response(omega, delay, k=2.0):
    return k * cmath.exp(-1j * omega * delay) / (1 + 1j * omega)


def phase_margin(delay, k=2.0):
    if k <= 1:
        raise ValueError('This helper assumes k>1, one unity-gain crossing.')
    wc = math.sqrt(k*k - 1)
    return wc, 180 - math.degrees(math.atan(wc) + wc*delay)


def simulate(delay, k=2.0, end=40.0, h=0.002):
    if delay < 0 or h <= 0 or end < 0 or (delay and delay < h):
        raise ValueError('Require delay=0 or delay>=h; h>0, end>=0.')
    count = round(end/h)
    if not math.isclose(count*h, end, abs_tol=1e-12):
        raise ValueError('End time must be a multiple of h.')
    ys = [0.0]
    def past(t):
        if t <= 0:
            return 0.0
        x = t/h
        i = math.floor(x)
        if i >= len(ys)-1:
            return ys[-1]
        q = x-i
        return (1-q)*ys[i]+q*ys[i+1]
    def slope(t, y):
        delayed = y if delay == 0 else past(t-delay)
        return -y + k*(1-delayed)
    for n in range(count):
        t, y = n*h, ys[-1]
        a = slope(t,y)
        b = slope(t+h/2,y+h*a/2)
        c = slope(t+h/2,y+h*b/2)
        d = slope(t+h,y+h*c)
        ys.append(y+h*(a+2*b+2*c+d)/6)
    return ys


def steps_oracle(t, delay, k=2):
    """Independent finite inverse-transform solution, Decimal arithmetic.
    y(t)=k*sum_n (-k)^n*[1-exp(-a)*sum_{j=0}^n a^j/j!], a=t-n*delay>=0.
    For t<delay this reduces to k*(1-exp(-t)).
    Not used to generate the solver, and not a finite-delay approximation.
    """
    with localcontext() as context:
        context.prec=70
        t, delay, k = map(lambda x: Decimal(str(x)), (t, delay, k))
        if delay == 0:
            return float(k/(1+k)*(1-(-(1+k)*t).exp()))
        if delay < 0 or t < 0:
            raise ValueError('Nonnegative time and delay required.')
        answer=Decimal(0)
        for n in range(int(t/delay)+1):
            a=t-n*delay
            term=Decimal(1); polynomial=term
            for j in range(1,n+1):
                term *= a/j
                polynomial += term
            answer += k*(-k)**n*(1-(-a).exp()*polynomial)
        return float(answer)


def verify():
    wc=math.sqrt(3)
    critical=2*math.pi/(3*wc)
    assert abs(loop_response(wc,critical)+1)<1e-14
    frequency_checks=0
    max_magnitude_error=0
    for wi in range(1,1002):
        w=wi/100
        for D in [0,.2,.8,1.6,3]:
            actual=loop_response(w,D)
            expected=2/math.sqrt(1+w*w)
            err=abs(abs(actual)-expected)
            max_magnitude_error=max(max_magnitude_error,err)
            assert err<1e-14
            frequency_checks+=1
    # Verify the proposed steady sine directly in the differential equation.
    sine_checks=0
    for w in [.25,1,math.sqrt(3),4]:
        for i in range(1001):
            t=i/100
            y=(math.sin(w*t)-w*math.cos(w*t))/(1+w*w)
            dy=(w*math.cos(w*t)+w*w*math.sin(w*t))/(1+w*w)
            assert abs(dy+y-math.sin(w*t))<1e-14
            sine_checks+=1
    records=[]
    for D,k in [(0,2),(.8,2),(1.6,2),(1.6,1.2)]:
        coarse=simulate(D,k,h=.002)
        fine=simulate(D,k,h=.001)
        points=[i/4 for i in range(161)]
        err_coarse=max(abs(coarse[round(t/.002)]-steps_oracle(t,D,k)) for t in points)
        err_fine=max(abs(fine[round(t/.001)]-steps_oracle(t,D,k)) for t in points)
        assert err_fine<1e-4
        assert err_fine<=err_coarse+1e-12
        records.append({'delay_seconds':D,'k':k,'points':len(points),'h_coarse':.002,'h_fine':.001,'max_error_coarse':err_coarse,'max_error_fine':err_fine,'sample_values':{str(t):fine[round(t/.001)] for t in [0,1,2,4,8,16,24,32,40]},'last_10s_min':min(fine[30000:]),'last_10s_max':max(fine[30000:]),'phase_margin_degrees':phase_margin(D,k)[1]})
    return {'status':'PASS','model':"y'=-y+k*(1-y(t-D)), zero past, target=1 at t=0",'frequency_response_checks':frequency_checks,'maximum_magnitude_error':max_magnitude_error,'steady_sine_ode_checks':sine_checks,'critical_delay_seconds':critical,'crossing_omega_rad_per_second':wc,'critical_oscillation_period_seconds':2*math.pi/wc,'trajectory_oracle_checks':sum(r['points'] for r in records),'trajectories':records}


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
