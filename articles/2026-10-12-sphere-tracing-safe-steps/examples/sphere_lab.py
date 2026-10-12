"""Original finite 2-D sphere-tracing lab. CC BY 4.0, zyuanming.
Python standard library only; this is not a production robust geometry kernel.
"""
import json, math, random, sys
from pathlib import Path


def circle_sdf(p, center=(5.0, 1.0), radius=2.0):
    return math.hypot(p[0]-center[0], p[1]-center[1])-radius


def box_sdf(p, center=(5.0, 0.0), half=(1.0, 1.0)):
    qx = abs(p[0]-center[0])-half[0]
    qy = abs(p[1]-center[1])-half[1]
    return math.hypot(max(qx, 0), max(qy, 0))+min(max(qx, qy), 0)


def march(sdf, origin=(0.0, 0.0), direction=(1.0, 0.0),
          factor=1.0, epsilon=1e-4, t_max=12.0, budget=256):
    """Exact-SDF contract. `factor` scales only the step, not the near test.
    A near result proves proximity to a surface, not a ray intersection.
    Every trace row is [sample index, t, exact signed distance].
    RANGE_CLEAR covers only [0, t_max], under exact arithmetic and the contract.
    """
    if not (0 < factor <= 1 and epsilon > 0 and t_max >= 0 and budget > 0):
        raise ValueError('invalid finite-range settings')
    if not math.isclose(math.hypot(*direction), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError('direction must have unit length')
    if not all(math.isfinite(x) for x in (*origin, *direction, factor, epsilon, t_max)):
        raise ValueError('finite inputs required')
    t, rows = 0.0, []
    for i in range(budget):
        p = (origin[0]+t*direction[0], origin[1]+t*direction[1])
        d = sdf(p)
        rows.append([i, t, d])
        if not math.isfinite(d):
            return {'status': 'INVALID_DISTANCE', 'trace': rows}
        if d < 0:
            return {'status': 'START_INSIDE' if i == 0 else 'OVERSHOOT', 'trace': rows}
        if d <= epsilon:
            return {'status': 'NEAR_SURFACE', 'trace': rows}
        step = factor*d
        if step > t_max-t:
            return {'status': 'RANGE_CLEAR', 'trace': rows}
        next_t = t+step
        if next_t == t:
            return {'status': 'STALLED', 'trace': rows}
        t = next_t
    return {'status': 'BUDGET', 'trace': rows}


def circle_roots(origin, direction, center=(5.0, 1.0), radius=2.0):
    """Independent reference: quadratic roots, not distance marching."""
    px, py = origin[0]-center[0], origin[1]-center[1]
    a = direction[0]**2+direction[1]**2
    b = 2*(px*direction[0]+py*direction[1])
    c = px*px+py*py-radius*radius
    disc = b*b-4*a*c
    if disc < 0:
        return []
    s = math.sqrt(disc)
    return sorted(t for t in ((-b-s)/(2*a), (-b+s)/(2*a)) if t >= 0)


def box_roots(origin, direction, center=(5.0, 0.0), half=(1.0, 1.0)):
    """Independent reference: intersection of coordinate slabs."""
    lo, hi = -math.inf, math.inf
    for o, v, c, h in zip(origin, direction, center, half):
        if v == 0:
            if not c-h <= o <= c+h:
                return []
        else:
            a, b = (c-h-o)/v, (c+h-o)/v
            lo, hi = max(lo, min(a, b)), min(hi, max(a, b))
    return sorted(t for t in (lo, hi) if t >= 0) if lo <= hi else []


def segment_distance(p, a, b):
    vx, vy = b[0]-a[0], b[1]-a[1]
    u = ((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)
    u = min(1, max(0, u))
    return math.hypot(p[0]-a[0]-u*vx, p[1]-a[1]-u*vy)


def run_tests():
    rng = random.Random(20261012)
    report = {'python': sys.version.split()[0], 'seed': 20261012,
              'epsilon': 1e-5, 't_max': 20, 'budget': 1024}
    # Independent geometric boundary reference for the box formula.
    corners = [(4,-1),(6,-1),(6,1),(4,1)]
    worst_box = 0.0
    for _ in range(10000):
        p = (rng.uniform(-2, 10), rng.uniform(-5, 5))
        boundary = min(segment_distance(p, corners[i], corners[(i+1)%4]) for i in range(4))
        sign = -1 if 4 < p[0] < 6 and -1 < p[1] < 1 else 1
        err = abs(box_sdf(p)-sign*boundary)
        worst_box = max(worst_box, err)
        assert err < 5e-14
    report['box_point_checks'] = {'count':10000, 'max_abs_error':worst_box}
    counts, segment_checks, near_without_root, ray_checks = {}, 0, 0, 0
    for sdf, roots_fn in [(circle_sdf, circle_roots), (box_sdf, box_roots)]:
        for factor in (1.0, .5):
            for _ in range(5000):
                o = (rng.uniform(-4,0),rng.uniform(-4,5))
                angle = rng.uniform(-.8,.8)
                v = (math.cos(angle),math.sin(angle))
                roots = roots_fn(o,v)
                first = roots[0] if roots else math.inf
                r = march(sdf,o,v,factor,1e-5,20,1024)
                counts[r['status']] = counts.get(r['status'],0)+1
                assert r['status'] in ('NEAR_SURFACE','RANGE_CLEAR','BUDGET')
                row = r['trace'][-1]
                for a,b in zip(r['trace'],r['trace'][1:]):
                    # An independent analytic root may be touched but not passed.
                    assert b[1] <= first+2e-10
                    assert b[1] >= a[1]
                    segment_checks += 1
                if r['status']=='RANGE_CLEAR':
                    assert first > 20-2e-10
                if r['status']=='NEAR_SURFACE':
                    assert 0 <= row[2] <= 1e-5
                    if first == math.inf:
                        near_without_root += 1
                ray_checks += 1
    report['random_rays'] = {'count':ray_checks,'statuses':counts,
                             'checked_advance_segments':segment_checks,
                             'near_without_analytic_root':near_without_root}
    main = march(circle_sdf)
    half = march(circle_sdf,factor=.5)
    assert main['status']==half['status']=='NEAR_SURFACE'
    report['main'] = main | {'analytic_first_t':5-math.sqrt(3)}
    report['half'] = {'samples':len(half['trace']),'t':half['trace'][-1][1],
                      'distance':half['trace'][-1][2]}
    grazing = {}
    for y in (1.0, 2.5, 2.99, 3.0, 3.00005, 3.001, 4.0):
        r = march(circle_sdf,origin=(0,y),epsilon=1e-4,budget=256)
        grazing[str(y)] = {'status':r['status'],'samples':len(r['trace']),
                          't':r['trace'][-1][1], 'distance':r['trace'][-1][2],
                          'analytic_roots':circle_roots((0,y),(1,0))}
    report['grazing'] = grazing
    assert grazing['3.00005']['status']=='NEAR_SURFACE'
    assert grazing['3.00005']['analytic_roots']==[]
    assert march(circle_sdf,origin=(5,1))['status']=='START_INSIDE'
    assert march(circle_sdf,budget=2)['status']=='BUDGET'
    assert march(circle_sdf,t_max=2)['status']=='RANGE_CLEAR'
    assert march(circle_sdf,origin=(3,1))['status']=='NEAR_SURFACE'
    assert march(lambda p:float('nan'))['status']=='INVALID_DISTANCE'
    assert march(lambda p:float('inf'))['status']=='INVALID_DISTANCE'
    for settings in ({'factor':0},{'factor':1.1},{'direction':(2,0)}, {'epsilon':0}):
        try: march(circle_sdf,**settings)
        except ValueError: pass
        else: raise AssertionError('input should be rejected')
    # Infinite-step example t_{k+1} = t_k + (1-t_k)/2.
    halvings = [1-2**(-k) for k in range(12)]
    report['halving_plane'] = halvings
    # Lower bound alone is not a proximity certificate.
    d = circle_sdf((0,0)); b = d*1e-6
    assert b < 1e-4 < d
    report['tiny_bound'] = {'actual_distance':d,'bound':b,'epsilon':1e-4}
    report['overestimate'] = {'first_step_3d':3*d,
         'next_signed_distance':circle_sdf((3*d,0)),
         'skipped_roots':circle_roots((0,0),(1,0)),
         'algebraic_f_at_origin':22}
    assert report['overestimate']['next_signed_distance']>0
    report['boundary_cases'] = ['inside_start', 'budget_2', 'range_2', 'on_surface', 'nan', 'infinity', 'zero_factor', 'factor_above_one', 'nonunit_direction', 'nonpositive_epsilon', 'near_without_root', 'overestimate_skips_roots', 'tiny_lower_bound']
    report['status'] = 'PASS'
    return report


if __name__ == '__main__':
    report = run_tests()
    s = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    if len(sys.argv)>1: Path(sys.argv[1]).write_text(s)
    print(s)
