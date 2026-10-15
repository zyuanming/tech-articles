"""Original deterministic system-identification simulation; no physical measurements."""
from pathlib import Path
import argparse,json,csv,math,random,platform
A=.8;B=.4;SIGMA=.03;DT=1

def simulate(u,a=A,b=B,seed=None,y0=0.0,sigma=SIGMA,saturate=False):
    rng=random.Random(seed);y=[y0];w=[]
    for uk in u:
        wk=rng.gauss(0,sigma) if seed is not None else 0.0
        w.append(wk);y.append(a*y[-1]+b*(min(1,max(0,uk)) if saturate else uk)+wk)
    return y,w

def fit(u,y):
    yy=math.fsum(v*v for v in y[:-1]);uu=math.fsum(v*v for v in u);yu=math.fsum(x*v for x,v in zip(y[:-1],u))
    yz=math.fsum(x*z for x,z in zip(y[:-1],y[1:]));uz=math.fsum(v*z for v,z in zip(u,y[1:]));det=yy*uu-yu*yu
    if det<=1e-12*max(1,yy*uu):return dict(identifiable=False,determinant=det)
    a=(yz*uu-yu*uz)/det;b=(yy*uz-yu*yz)/det
    return dict(identifiable=True,a=a,b=b,determinant=det,normal_sums=dict(yy=yy,uu=uu,yu=yu,yz=yz,uz=uz),static_c=uz/uu)

def rmse(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b))/len(a))
def lagcorr(xs,lag):
    mean=math.fsum(xs)/len(xs);d=[x-mean for x in xs];den=math.fsum(x*x for x in d)
    return math.fsum(d[k]*d[k-lag] for k in range(lag,len(d)))/den

def assess(u,y,fit_result):
    a,b,c=(fit_result[k] for k in ('a','b','static_c'))
    pred=[a*yk+b*uk for yk,uk in zip(y[:-1],u)];free,_=simulate(u,a,b,y0=y[0]);static=[c*x for x in u]
    res=[z-p for z,p in zip(y[1:],pred)];sr=[z-p for z,p in zip(y[1:],static)]
    return dict(one_step=pred,free_run=free,static=static,residuals=res,static_residuals=sr,one_step_rmse=rmse(y[1:],pred),free_run_rmse=rmse(y[1:],free[1:]),static_rmse=rmse(y[1:],static),residual_lag1=lagcorr(res,1),static_residual_lag1=lagcorr(sr,1),residual_autocorrelation=[lagcorr(res,k) for k in range(1,9)],static_residual_autocorrelation=[lagcorr(sr,k) for k in range(1,9)])

def main(out):
    out.mkdir(parents=True,exist_ok=False);rng=random.Random(2700)
    train_u=[float(rng.randrange(2)) for _ in range(24) for _dummy in [0]]
    train_u=[v for v in train_u for _ in range(5)]
    val_u=([0.0]*8+[1.0]*8+[.5]*8+[0.0]*8+[1.0]*8)*2
    ty,tw=simulate(train_u,seed=2701);vy,vw=simulate(val_u,seed=2702);f=fit(train_u,ty);t=assess(train_u,ty,f);v=assess(val_u,vy,f)
    noiseless,_=simulate([1.0]*8);exact=fit([1.0]*8,noiseless);assert abs(exact['a']-A)<1e-12 and abs(exact['b']-B)<1e-12
    steady_u=[1.0]*20;steady_y=[2.0]*21;ambiguous=fit(steady_u,steady_y);assert not ambiguous['identifiable']
    candidates=[dict(a=a,b=2*(1-a),cooling=simulate([0.0]*8,a,2*(1-a),y0=2)[0]) for a in [.5,.8,.9]]
    for row in candidates:assert abs(row['a']*2+row['b']-2)<1e-15
    repeats=[]
    for seed in range(27100,27200):
        y,_=simulate(train_u,seed=seed);p=fit(train_u,y);assert p['identifiable'];repeats.append(dict(seed=seed,a=p['a'],b=p['b']))
    spread={}
    for key in ['a','b']:
        vals=[r[key] for r in repeats];mean=math.fsum(vals)/len(vals);sd=math.sqrt(math.fsum((x-mean)**2 for x in vals)/(len(vals)-1));spread[key]=dict(mean=mean,sd=sd,min=min(vals),max=max(vals))
    sat_u=[2.0]*20;sat,_=simulate(sat_u,saturate=True);linear,_=simulate(sat_u)
    # Normal-equation orthogonality and an independent grid minimum check.
    tr=t['residuals'];orth=[math.fsum(x*e for x,e in zip(ty[:-1],tr)),math.fsum(x*e for x,e in zip(train_u,tr))]
    assert max(map(abs,orth))<1e-11
    loss=lambda a,b:math.fsum((z-a*y-b*u)**2 for y,u,z in zip(ty[:-1],train_u,ty[1:]))
    best=loss(f['a'],f['b']);checks=0
    for da in [-.1,-.02,0,.02,.1]:
        for db in [-.1,-.02,0,.02,.1]:assert loss(f['a']+da,f['b']+db)>=best-1e-12;checks+=1
    result=dict(model='y[k+1]=0.8*y[k]+0.4*u[k]+w[k]; dt=1s; y temperature deviation in degC; u normalized power; synthetic data only',python=platform.python_version(),true_a=A,true_b=B,sigma_degC=SIGMA,train=dict(seed_input=2700,seed_noise=2701,u=train_u,y=ty,w=tw),validation=dict(seed_noise=2702,u=val_u,y=vy,w=vw),fit=f,train_metrics=t,validation_metrics=v,noiseless=dict(u=[1.0]*8,y=noiseless,fit=exact),steady=dict(u=steady_u,y=steady_y,fit=ambiguous,candidates=candidates),repeats=repeats,spread=spread,extrapolation=dict(u=sat_u,saturated_y=sat,linear_y=linear),checks=dict(normal_equation_residuals=orth,nearby_grid_minimum_checks=checks))
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'observations.csv').open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(['dataset','k','time_s','u_k','y_k_degC','y_next_degC','w_k_degC'])
        for name,u,y,w in [('train',train_u,ty,tw),('validation',val_u,vy,vw)]:
            for k,(uk,yk,yn,wk) in enumerate(zip(u,y[:-1],y[1:],w)):writer.writerow([name,k,k,uk,yk,yn,wk])
    summary=f"Synthetic only; dt=1s; train=120 transitions; validation=80 transitions\nTRUE a={A}, b={B}; FIT a={f['a']:.9f}, b={f['b']:.9f}\nTRAIN one-step RMSE={t['one_step_rmse']:.9f} degC\nVALIDATION one-step={v['one_step_rmse']:.9f}, free-run={v['free_run_rmse']:.9f}, static={v['static_rmse']:.9f} degC\nVALIDATION residual lag1: dynamic={v['residual_lag1']:.9f}, static={v['static_residual_lag1']:.9f}\nSTEADY determinant={ambiguous['determinant']}; 100 noise-repeat estimates; 25 grid checks\n"
    (out/'stdout.txt').write_text(summary);print(summary,end='')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);main(p.parse_args().output)
