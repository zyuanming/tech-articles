"""Original two-stage orient2d lesson: outward intervals, then exact rationals.
Not a port of Shewchuk's adaptive expansion arithmetic or a CGAL benchmark.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import argparse,csv,io,json,math,random,sys

class Uncertain(Exception):
    pass

class Interval:
    def __init__(self, lo, hi=None):
        self.lo = float(lo)
        self.hi = self.lo if hi is None else float(hi)
        if not (math.isfinite(self.lo) and math.isfinite(self.hi)):
            raise Uncertain('nonfinite interval endpoint')
    @staticmethod
    def outward(lo, hi):
        if not (math.isfinite(lo) and math.isfinite(hi)):
            raise Uncertain('overflow or invalid interval arithmetic')
        return Interval(math.nextafter(lo, -math.inf),
                        math.nextafter(hi, math.inf))
    def __sub__(self, other):
        return self.outward(self.lo-other.hi, self.hi-other.lo)
    def __mul__(self, other):
        products = [a*b for a in (self.lo,self.hi)
                        for b in (other.lo,other.hi)]
        if not all(math.isfinite(p) for p in products):
            raise Uncertain('product overflow')
        return self.outward(min(products), max(products))


def sign(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    return (v > 0) - (v < 0)


def det(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def exact_det(a,b,c):
    return det(*[tuple(Fraction.from_float(x) for x in p) for p in (a,b,c)])


def interval_det(a,b,c):
    return det(*[tuple(Interval(x) for x in p) for p in (a,b,c)])


def orient(a,b,c):
    if not all(math.isfinite(x) for p in (a,b,c) for x in p):
        raise ValueError('Input coordinates must be finite binary64 values')
    enclosure=None
    try:
        iv=interval_det(a,b,c)
        enclosure=[iv.lo,iv.hi]
        if iv.lo > 0:
            return dict(sign=1,route='interval',enclosure=enclosure)
        if iv.hi < 0:
            return dict(sign=-1,route='interval',enclosure=enclosure)
    except Uncertain:
        pass
    return dict(sign=sign(exact_det(a,b,c)),route='exact',enclosure=enclosure)


def inspect(a,b,c):
    true=exact_det(a,b,c)
    result=orient(a,b,c)
    assert result['sign']==sign(true)
    if result['enclosure'] is not None:
        lo,hi=result['enclosure']
        assert Fraction.from_float(lo)<=true<=Fraction.from_float(hi)
    naive=det(a,b,c)
    return dict(points=[a,b,c],exact=str(true),naive=naive if math.isfinite(naive) else str(naive),
                naive_sign=sign(naive),**result)


def hull(points, predicate):
    # Monotone chain, deleting non-left turns; duplicate points removed.
    points=sorted(set(points))
    def half(seq):
        out=[]
        for p in seq:
            while len(out)>=2 and predicate(out[-2],out[-1],p)<=0:
                out.pop()
            out.append(p)
        return out
    if len(points)<2:return points
    return half(points)[:-1]+half(reversed(points))[:-1]


def run():
    assert sys.float_info.radix==2 and sys.float_info.mant_dig==53
    N=2**27
    A=(0.,0.);B=(float(N),float(N-1));C=(float(N+1),float(N))
    main=inspect(A,B,C)
    assert main['exact']=='1' and main['naive']==0 and main['sign']==1
    cyclic=[inspect(*ps) for ps in [(A,B,C),(B,C,A),(C,A,B)]]
    assert [x['naive'] for x in cyclic]==[0.,1.,1.]
    all_permutations=[inspect(*ps) for ps in permutations([A,B,C])]
    naive_hull=hull([A,B,C],lambda a,b,c:sign(det(a,b,c)))
    robust_hull=hull([A,B,C],lambda a,b,c:orient(a,b,c)['sign'])
    assert len(naive_hull)==2 and len(robust_hull)==3
    eps=1e-9
    small=[(0.,0.),(1.,0.),(1.,2.**-40)]
    scaled=[tuple(x*2**20 for x in p) for p in small]
    scales=[dict(scale=s,det=det(*ps),epsilon_sign=0 if abs(det(*ps))<eps else sign(det(*ps)),**orient(*ps)) for s,ps in [(1,small),(2**20,scaled)]]
    assert [r['epsilon_sign'] for r in scales]==[0,1]
    assert [r['sign'] for r in scales]==[1,1]
    grid=[];ulp=math.ulp(float(N))
    for j in range(-15,16):
        for i in range(-15,16):
            p=(C[0]+i*ulp,C[1]+j*ulp)
            r=inspect(A,B,p)
            grid.append(dict(ix=i,iy=j,exact_sign=r['sign'],naive_sign=r['naive_sign'],
                             route=r['route'],exact=r['exact'],naive=r['naive']))
    rng=random.Random(240014)
    ordinary=[inspect(*[tuple(rng.uniform(-100,100) for _ in range(2)) for _ in range(3)]) for _ in range(500)]
    extremes=[inspect((0.,0.),(1e-200,0.),(0.,1e-200)),
              inspect((0.,0.),(1e200,1e200),(1e200,2e200)),
              inspect((0.,0.),(1.,1.),(2.,2.)),
              inspect((0.,0.),(0.,0.),(2.,2.))]
    m=2**53
    original=((0,0),(m,m),(m+1,m))
    stored=[tuple(float(x) for x in p) for p in original]
    loss=dict(original_integer_det=str(det(*original)),stored_points=stored,
              stored_exact_det=str(exact_det(*stored)),same_B_C=stored[1]==stored[2])
    assert loss['original_integer_det']==str(-m) and loss['stored_exact_det']=='0'
    invalid_rejected=0
    for v in [float('nan'),float('inf'),float('-inf')]:
        try:orient((v,0.),B,C)
        except ValueError:invalid_rejected+=1
    assert invalid_rejected==3
    return dict(main=main,N=N,products=dict(left_exact=str(N*N),right_exact=str((N-1)*(N+1)),left_float=float(N)*N,right_float=float(N-1)*(N+1)),
                cyclic=cyclic,all_permutations=all_permutations,
                hull=dict(naive=naive_hull,robust=robust_hull),
                scale_example=scales,grid=grid,grid_ulp=ulp,
                ordinary_cases=ordinary,extreme_cases=extremes,input_rounding=loss,
                counts=dict(grid_total=len(grid),grid_naive_wrong=sum(r['naive_sign']!=r['exact_sign'] for r in grid),grid_exact=sum(r['route']=='exact' for r in grid),
                            ordinary_total=len(ordinary),ordinary_exact=sum(r['route']=='exact' for r in ordinary),
                            total_verified=1+len(cyclic)+len(all_permutations)+len(grid)+len(ordinary)+len(extremes),invalid_rejected=invalid_rejected),
                seed=240014)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    r=run();(args.output/'results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(r['grid'][0]));w.writeheader();w.writerows(r['grid']);(args.output/'grid.csv').write_text(out.getvalue())
    text='\n'.join(['Exact determinant 1; naive determinant 0',
                    'Cyclic naive determinants: 0, 1, 1',
                    'Convex hull vertices: naive 2, robust 3',
                    f"Grid: {r['counts']['grid_naive_wrong']}/961 naive errors; {r['counts']['grid_exact']}/961 exact fallbacks",
                    f"Ordinary: {r['counts']['ordinary_exact']}/500 exact fallbacks",
                    f"Verified {r['counts']['total_verified']} cases; invalid inputs rejected: 3"] )+'\n'
    (args.output/'stdout.txt').write_text(text);print(text,end='')
if __name__=='__main__':main()
