"""Original standard-library nomogram geometry experiments (CC BY 4.0).
No physical measuring, circuit simulation, network access, or production claims.
"""
from fractions import Fraction as Q
from pathlib import Path
import math,random,json,argparse

def interpolate(y_left,y_right,t=Q(1,2)):
    return (1-t)*y_left+t*y_right

def determinant(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def add_coordinates(a,b):
    return (Q(0),Q(a)),(Q(1),Q(a+b,2)),(Q(2),Q(b))

def parallel_coordinates(r1,r2):
    if r1<=0 or r2<=0:raise ValueError('positive resistances only')
    result=Q(r1*r2,r1+r2)
    return ((Q(0),Q(1200,r1)),(Q(1),Q(600,result)),
            (Q(2),Q(1200,r2))),result

def make_paper(directory):
    """Three separate A4 SVG sheets; no externally loaded assets/fonts."""
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    for kind in ('addition','product','parallel'):
        out=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
             '<rect width="210" height="297" fill="white"/>',
             '<g fill="#173743" font-family="sans-serif">',
             f'<text x="15" y="22" font-size="7">Nomogram: {kind}</text>',
             '<text x="15" y="34" font-size="4">Original teaching chart. Join two known marks.</text>',
             '<text x="15" y="42" font-size="4">Use the specified ranges and units.</text>']
        if kind=='addition':
            vals=[list(range(11)),list(range(0,21,2)),list(range(11))]
            funcs=[lambda x:10*x,lambda x:5*x,lambda x:10*x]
            names=['a','c = a + b','b']
        elif kind=='product':
            vals=[[1,2,3,4,5,6,8,10],[1,2,3,5,10,12,20,30,50,100],[1,2,3,4,5,6,8,10]]
            funcs=[lambda x:100*math.log10(x),lambda x:50*math.log10(x),lambda x:100*math.log10(x)]
            names=['a > 0','c = a * b','b > 0']
        else:
            vals=[[10,12,15,20,30,50,100],[5,6,7.5,10,15,20,25,50],[10,12,15,20,30,50,100]]
            funcs=[lambda x:1200/x,lambda x:600/x,lambda x:1200/x]
            names=['R1 / ohm','Req / ohm','R2 / ohm']
        for x,values,fn,name in zip((30,105,180),vals,funcs,names):
            out.append(f'<text x="{x}" y="73" text-anchor="middle" font-size="4.2">{name}</text>')
            out.append(f'<path d="M {x} 88 V 240" fill="none" stroke="#173743" stroke-width="0.4"/>')
            for val in values:
                y=235-fn(val)
                out.append(f'<path d="M {x-2} {y:.8f} H {x+2}" stroke="#173743" stroke-width="0.3"/>')
                out.append(f'<text x="{x+3}" y="{y+1.3:.8f}" font-size="3.8">{val}</text>')
        out.extend(['<text x="15" y="265" font-size="4">Print the whole sheet together. Do not move one axis.</text>',
                    '<text x="15" y="273" font-size="4">Finite printed marks require interpolation; not exact arithmetic.</text>',
                    '<text x="15" y="281" font-size="3.5">zyuanming / tech-articles. CC BY 4.0.</text>','</g></svg>'])
        (directory/f'paper-{kind}.svg').write_text('\n'.join(out)+'\n')

def run_checks():
    addition=0
    for i in range(101):
        for j in range(101):
            a,b=Q(i,10),Q(j,10)
            pts=add_coordinates(a,b);assert determinant(*pts)==0
            assert interpolate(a,b)*2==a+b
            # Reverse reading, through middle and right, recovers the left.
            assert 2*pts[1][1]-b==a
            addition+=1
    reciprocal=0
    for r1 in range(10,101):
        for r2 in range(10,101):
            pts,r=parallel_coordinates(r1,r2)
            assert determinant(*pts)==0 and 0<r<min(r1,r2)
            assert Q(1,r)==Q(1,r1)+Q(1,r2)
            reciprocal+=1
    products=0;max_error=0
    for i in range(10,101):
        for j in range(10,101):
            a,b=i/10,j/10
            h=interpolate(100*math.log10(a),100*math.log10(b),.5)
            c=10**(h/50)
            max_error=max(max_error,abs(c-a*b)/abs(a*b));assert math.isclose(c,a*b,rel_tol=2e-15)
            products+=1
    # Off-centre axis reads a weighted value, not the sum with old labels.
    assert 2*interpolate(Q(2),Q(6),Q(1,3))==Q(20,3)
    # Arbitrary entire-chart affine transformations preserve collinearity.
    rng=random.Random(19251884);affine=0
    for _ in range(2000):
        aa,bb,cc,dd=[Q(rng.randrange(-9,10)) for _ in range(4)]
        if aa*dd-bb*cc==0:continue
        dx,dy=Q(rng.randrange(-10,11)),Q(rng.randrange(-10,11))
        pts=add_coordinates(Q(rng.randrange(11)),Q(rng.randrange(11)))
        mapped=[(aa*x+bb*y+dx,cc*x+dd*y+dy) for x,y in pts]
        assert determinant(*mapped)==0;affine+=1
    ratio_up=10**(.5/50);ratio_down=10**(-.5/50)
    assert math.isclose(12*ratio_up,12.279515907,rel_tol=1e-9)
    pts,eq=parallel_coordinates(30,60);assert eq==20
    return {'status':'PASS','addition_exact_pairs':addition,'parallel_exact_pairs':reciprocal,
            'product_float_pairs':products,'product_max_relative_error':max_error,
            'affine_nonsingular_cases':affine,'affine_trials':2000,'seed':19251884,
            'examples':{'sum_2_6':8,'reversed_11_minus_8':3,'product_2_6':12,
                        'parallel_30_60':str(eq),'parallel_heights_mm':[str(p[1]) for p in pts],
                        'wrong_center_at_one_third':str(Q(20,3)),
                        'center_error_only_half_mm_product_12':[12*ratio_down,12*ratio_up],
                        'half_mm_error_factors':[ratio_down,ratio_up]},
            'scope':'Ideal coordinates and finite code checks only; not physical ruler/circuit measurement.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--paper-dir');a=p.parse_args()
    result=run_checks()
    if a.paper_dir:make_paper(a.paper_dir)
    text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if a.out:Path(a.out).write_text(text)
    print(text)
