#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original periodic staggered-grid teaching solver, not Stam's original code.

Only NumPy is required. Run with --out a NEW directory; no network access.
Index arrays as [row_y, column_x], with y increasing upward in diagrams.
u[j,i] is at (i*h,(j+.5)*h); v[j,i] at ((i+.5)*h,j*h).
dye[j,i] is at ((i+.5)*h,(j+.5)*h). Domain length is 1.
"""
from pathlib import Path
import argparse, hashlib, json, platform
import numpy as np


def sample(a, x, y, ox, oy):
    """Bilinear, periodic point sampling. Offsets are in grid-cell units."""
    n = a.shape[0]
    gx, gy = x*n-ox, y*n-oy
    i0, j0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    tx, ty = gx-i0, gy-j0
    return ((1-ty)*((1-tx)*a[j0 % n, i0 % n] + tx*a[j0 % n, (i0+1) % n])
            + ty*((1-tx)*a[(j0+1) % n, i0 % n] + tx*a[(j0+1) % n, (i0+1) % n]))


def locations(n, ox, oy):
    j, i = np.indices((n, n))
    return (i+ox)/n, (j+oy)/n


def advect(a, u, v, dt, ox, oy):
    x, y = locations(len(a), ox, oy)
    # One Euler backtrace, not an exact characteristic and not the 1999 RK2 tracer.
    bx = x-dt*sample(u, x, y, 0, .5)
    by = y-dt*sample(v, x, y, .5, 0)
    return sample(a, bx, by, ox, oy)


def divergence(u, v):
    n = len(u)
    return n*(np.roll(u, -1, axis=1)-u + np.roll(v, -1, axis=0)-v)


def gradient(q):
    n = len(q)
    return n*(q-np.roll(q, 1, axis=1)), n*(q-np.roll(q, 1, axis=0))


def project(u, v):
    """Solve D G q = D w; remove Gq. q includes dt/rho, is not Pa."""
    n = len(u)
    div = divergence(u, v)
    k = np.arange(n)
    ev = 2*n*n*(np.cos(2*np.pi*k/n)-1)
    lap = ev[:, None]+ev[None, :]
    lap[0, 0] = 1  # zero mode is handled separately below
    qhat = np.fft.fft2(div)/lap
    qhat[0, 0] = 0  # choose mean(q)=0; mean divergence is zero on this domain
    q = np.fft.ifft2(qhat).real
    gx, gy = gradient(q)
    return u-gx, v-gy, q


def diffuse(a, alpha, dt):
    """Backward Euler solve (I-alpha*dt*L)a_new=a_old, periodic grid."""
    n = len(a)
    k = np.arange(n)
    ev = 2*n*n*(np.cos(2*np.pi*k/n)-1)
    lap = ev[:, None]+ev[None, :]
    return np.fft.ifft2(np.fft.fft2(a)/(1-alpha*dt*lap)).real


def initial(n):
    x, y = locations(n, 0, 0)
    psi = np.zeros_like(x)
    for cx, cy, strength, width in [(.35, .48, .035, .095), (.65, .52, .035, .095),
                                     (.5, .20, -.018, .09)]:
        dx = (x-cx+.5) % 1-.5
        dy = (y-cy+.5) % 1-.5
        psi += strength*np.exp(-(dx*dx+dy*dy)/(2*width*width))
    u = n*(np.roll(psi, -1, axis=0)-psi)
    v = -n*(np.roll(psi, -1, axis=1)-psi)
    x, y = locations(n, .5, .5)
    dye = np.exp(-((y-.48)/.035)**2)*np.exp(-((x-.5)/.35)**8)
    return u, v, dye


def stats(u, v, dye):
    d = divergence(u, v)
    return dict(dye_min=float(dye.min()), dye_max=float(dye.max()),
                dye_sum=float(dye.sum()), divergence_rms=float(np.sqrt(np.mean(d*d))),
                divergence_max=float(abs(d).max()), velocity_energy=float(.5*np.mean(u*u+v*v)))


def run(n=64, dt=.04, steps=120, nu=0., diffusivity=0.):
    u, v, dye = initial(n)
    frames = [(u.copy(), v.copy(), dye.copy())]
    rows = [dict(step=0, time=0., **stats(u, v, dye))]
    first = {}
    for s in range(1, steps+1):
        # Forces can be added here. Main run uses only its specified initial velocity.
        if nu:
            u, v = diffuse(u, nu, dt), diffuse(v, nu, dt)
        u, v, _ = project(u, v)
        au, av = advect(u, u, v, dt, 0, .5), advect(v, u, v, dt, .5, 0)
        u, v, q = project(au, av)
        if s == 1:
            first = dict(u_before=au, v_before=av, u_after=u.copy(), v_after=v.copy(), q=q,
                         div_before=divergence(au, av), div_after=divergence(u, v))
        if diffusivity:
            dye = diffuse(dye, diffusivity, dt)
        dye = advect(dye, u, v, dt, .5, .5)
        rows.append(dict(step=s, time=s*dt, **stats(u, v, dye)))
        if s % 10 == 0:
            frames.append((u.copy(), v.copy(), dye.copy()))
    return np.array(frames), rows, first


def small_examples():
    # Four-cell box A B / C D. Oriented edges A->B, C->D, A->C, B->D.
    B = np.array([[1,0,1,0], [-1,0,0,1], [0,1,-1,0], [0,-1,0,-1]], dtype=float)
    w = np.array([3., 1., 0., 0.])
    q = np.linalg.lstsq(-B@B.T, B@w, rcond=None)[0]
    q -= q[0]  # choose q_A=0 for hand calculation
    # Gradient along A->B is q_B-q_A, consistent with the periodic solver.
    correction = -B.T@q
    fixed = w-correction
    assert np.allclose(fixed, [0.5,-0.5,-0.5,0.5])
    assert np.allclose(B@fixed, 0)
    # A nonuniform flow counterexample: bounded interpolation does not preserve sum.
    old = np.array([0., 0., 1., 0.])
    departures = np.array([0., 1., 1.5, 2.])
    i = np.floor(departures).astype(int); t = departures-i
    new = (1-t)*old[i % 4]+t*old[(i+1) % 4]
    # Constant-translation ring: fixed total displacement, different numbers of samples.
    n = 64; x = np.arange(n)
    original = ((x >= 20)&(x < 36)).astype(float)
    shifts = {}
    for step_size, count in [(1.,16),(.5,32),(.25,64)]:
        a = original.copy()
        for _ in range(count):
            p = x-step_size; i=np.floor(p).astype(int); t=p-i
            a=(1-t)*a[i % n]+t*a[(i+1) % n]
        shifts[str(step_size)] = dict(count=count, values=a.tolist(), max=float(a.max()),
                                      l1_error=float(np.mean(abs(a-np.roll(original,16)))))
    a = np.zeros(12); a[3:6] = 1
    explicit=[a.copy()]; sl=[a.copy()]
    for _ in range(3):
        explicit.append(explicit[-1]-1.5*(explicit[-1]-np.roll(explicit[-1],1)))
        sl.append(.5*np.roll(sl[-1],1)+.5*np.roll(sl[-1],2))
    return dict(bilinear=dict(corners=[0,4,8,12], point=[.5,.75], horizontal=[2,10], result=8),
                four_cells=dict(incidence=B.tolist(), before=w.tolist(), net_before=(B@w).tolist(),
                                potential=q.tolist(), correction=correction.tolist(),
                                after=fixed.tolist(), net_after=(B@fixed).tolist()),
                nonconservative=dict(before=old.tolist(), departure=departures.tolist(), after=new.tolist()),
                translation=dict(original=original.tolist(), exact=np.roll(original,16).tolist(), variants=shifts),
                cfl=dict(courant=1.5, explicit=np.array(explicit).tolist(), semi_lagrangian=np.array(sl).tolist()),
                implicit_two_cells=dict(old=[0,12], a=1, new=[4,8]))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
    out=Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('Refusing to overwrite a nonempty output directory')
    out.mkdir(parents=True,exist_ok=True)
    frames,rows,first=run()
    np.savez_compressed(out/'frames.npz',frames=frames,**first)
    tests={}
    # Deterministic random projection, checked for divergence, energy, idempotence.
    rng=np.random.default_rng(20261014); a=rng.normal(size=(32,32));b=rng.normal(size=(32,32))
    u,v,q=project(a,b); uu,vv,_=project(u,v)
    tests['projection_max_divergence']=float(abs(divergence(u,v)).max())
    tests['projection_idempotence_max']=float(max(abs(uu-u).max(),abs(vv-v).max()))
    tests['energy_before']=float(np.sum(a*a+b*b));tests['energy_after']=float(np.sum(u*u+v*v))
    tests['constant_advected_max_error']=float(abs(advect(np.ones((32,32)),a,b,2.3,.5,.5)-1).max())
    # Backtrace bounds on arbitrary velocities and a very large timestep.
    dye=rng.random((32,32));r=advect(dye,a,b,10.,.5,.5)
    tests['sample_range_with_large_dt']=[float(r.min()),float(r.max())]
    assert tests['projection_max_divergence']<1e-10
    assert tests['projection_idempotence_max']<1e-12
    assert tests['energy_after']<=tests['energy_before']+1e-10
    assert tests['constant_advected_max_error']<1e-14
    assert r.min()>=dye.min()-1e-14 and r.max()<=dye.max()+1e-14
    assert max(x['divergence_max'] for x in rows)<1e-10
    assert min(x['dye_min'] for x in rows)>=-1e-14 and max(x['dye_max'] for x in rows)<=1+1e-14
    results=dict(model='Original periodic 2D MAC teaching implementation; not a 1999 code reproduction',
                 environment=dict(python=platform.python_version(),numpy=np.__version__),
                 config=dict(n=64,domain_length=1,dt=.04,steps=120,nu=0,dye_diffusivity=0,seed=20261014,
                             boundaries='periodic on both axes',backtrace='one Euler step',
                             interpolation='bilinear convex weights',projection='compatible discrete FFT Poisson'),
                 stats=rows, tests=tests, small=small_examples(),
                 first_step=dict(div_before_rms=float(np.sqrt(np.mean(first['div_before']**2))),
                                 div_after_rms=float(np.sqrt(np.mean(first['div_after']**2)))))
    (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    (out/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                              for p in [out/'frames.npz',out/'results.json']},indent=2)+'\n')
    print(json.dumps(dict(status='PASS',first=rows[0],last=rows[-1],first_step=results['first_step'],tests=tests),indent=2))


if __name__=='__main__':main()
