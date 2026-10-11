"""Original teaching simulation. Python 3 + NumPy. Writes four CSV snapshots.
No bird biology or collision-safety claim. Run: python simulate.py
Parameters match this article's 100-agent figures, not its 3-agent hand calculation.
"""
from pathlib import Path
import numpy as np

rng = np.random.default_rng(12)
p = rng.uniform(0, 10, (100, 2))
angle = rng.uniform(0, 2 * np.pi, 100)
v = np.column_stack((np.cos(angle), np.sin(angle))) * .6
SEPARATION = .65  # try 0, keeping the seed unchanged
ALIGNMENT = .65
COHESION = .22

def update(p, v):
    delta = p[:, None, :] - p[None, :, :]
    delta = (delta + 5) % 10 - 5
    d2 = (delta**2).sum(-1)
    near = (d2 < 2.2**2) & (d2 > 1e-10)
    count = np.maximum(near.sum(1), 1)[:, None]
    coh = -(delta * near[:, :, None]).sum(1) / count
    ali = (near @ v) / count - v
    ali[near.sum(1) == 0] = 0
    close = (d2 < .6**2) & (d2 > 1e-10)
    sep = (delta * close[:, :, None]
           / np.maximum(d2[:, :, None], .04)).sum(1)
    a = ALIGNMENT * ali + COHESION * coh + SEPARATION * sep
    length = np.linalg.norm(a, axis=1)
    a *= np.minimum(1, .7 / np.maximum(length, 1e-9))[:, None]
    nv = v + a * .1
    speed = np.linalg.norm(nv, axis=1)
    nv *= np.minimum(1, 1.2 / np.maximum(speed, 1e-9))[:, None]
    return (p + nv * .1) % 10, nv

if __name__ == '__main__':
    for step in range(181):
        if step in (0, 40, 100, 180):
            np.savetxt(Path(f'boids-{step}.csv'), np.column_stack((p, v)),
                       delimiter=',', header='x,y,vx,vy', comments='')
        p, v = update(p, v)
    print('Wrote snapshots for steps 0, 40, 100, 180; seed=12.')
