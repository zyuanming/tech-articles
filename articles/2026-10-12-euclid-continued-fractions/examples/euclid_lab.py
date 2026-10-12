"""Original integer/rational experiments, Python standard library only."""
from fractions import Fraction
from math import gcd
import json
import platform


def euclid(a, b):
    if type(a) is not int or type(b) is not int:
        raise TypeError('integer inputs required')
    a, b = abs(a), abs(b)
    trace = []
    while b:
        q, r = divmod(a, b)
        trace.append([a, b, q, r])
        a, b = b, r
    return a, trace


def extended(a, b):
    aa, bb = a, b
    old_r, r = abs(a), abs(b)
    old_x, x, old_y, y = 1, 0, 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r-q*r
        old_x, x = x, old_x-q*x
        old_y, y = y, old_y-q*y
    sx = old_x if aa >= 0 else -old_x
    sy = old_y if bb >= 0 else -old_y
    return old_r, sx, sy


def from_cf(qs):
    v = Fraction(qs[-1])
    for q in reversed(qs[:-1]):
        v = q + 1/v
    return v


def divisors(a,b):
    return {d for d in range(1, max(abs(a),abs(b))+1) if a%d==b%d==0}


def main():
    g, trace = euclid(1071,462)
    assert trace==[[1071,462,2,147],[462,147,3,21],[147,21,7,0]]
    assert g==21 and extended(1071,462)==(21,-3,7)
    integer_cases = 0
    for a in range(-150,151):
        for b in range(-150,151):
            found, rows = euclid(a,b)
            gg,x,y = extended(a,b)
            assert found==gg==gcd(a,b) and a*x+b*y==gg
            for A,B,q,r in rows:
                assert A==q*B+r and 0<=r<B
            integer_cases+=1
    invariant_cases=0
    for a in range(1,81):
        for b in range(1,81):
            _, rows=euclid(a,b)
            for A,B,q,r in rows:
                assert divisors(A,B)==divisors(B,r)
                invariant_cases+=1
    rational_cases=0
    for a in range(1,101):
        for b in range(1,101):
            qs=[row[2] for row in euclid(a,b)[1]]
            assert from_cf(qs)==Fraction(a,b)
            rational_cases+=1
    target=Fraction(1071,462)
    # For each q, the nearest integer numerator is floor(target*q) or the next.
    near=[]
    for q in range(1,11):
        floor=(target*q).__floor__()
        candidates=[(abs(Fraction(p,q)-target),Fraction(p,q),p,q) for p in [floor,floor+1]]
        best=min(candidates)
        near.append({'q':q,'p':best[2],'fraction':str(best[1]),'error':str(best[0])})
    best_error=min(Fraction(row['error']) for row in near)
    assert best_error==Fraction(1,66)
    assert {row['fraction'] for row in near if Fraction(row['error'])==best_error}=={'7/3'}
    fibres=[]
    a,b=2,1
    for _ in range(15):
        fibres.append({'a':a,'b':b,'divisions_including_final_zero':len(euclid(a,b)[1])})
        a,b=a+b,a
    assert fibres[-1]=={'a':1597,'b':987,'divisions_including_final_zero':15}
    assert len(euclid(10**12,1)[1])==1
    # Integer-only demonstration: gcd(1000,1000)=1000 but gcd(1000,1001)=1.
    assert euclid(1000,1000)[0]==1000 and euclid(1000,1001)[0]==1
    rejected_float=False
    try: euclid(1.071,.462)
    except TypeError: rejected_float=True
    assert rejected_float
    print(json.dumps({'python':platform.python_version(),'gcd':g,'trace':trace,'bezout':extended(1071,462),
      'integer_pairs_checked':integer_cases,'divisor_set_step_checks':invariant_cases,
      'rational_cf_roundtrips':rational_cases,'continued_fraction':[2,3,7],
      'convergents':[str(from_cf([2,3,7][:n])) for n in range(1,4)],
      'denominator_cap_10':near,'error_7_over_3':'1/66','error_23_over_10':str(abs(Fraction(23,10)-target)),
      'fibonacci_pairs':fibres,'trillion_and_one_divisions':1,'tile_count':51*22,
      'float_rejected':rejected_float,'exercise_gcd_252_105':euclid(252,105)[0]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
