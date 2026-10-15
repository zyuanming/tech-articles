"""Original MIT-licensed measurements from logged Box2D-Lite CSV, not a solver."""
from pathlib import Path
import csv,json,math
HERE=Path(__file__).resolve().parent

def frame_data(path):
    out={}
    for row in csv.DictReader(path.open()):
        r={k:float(v) for k,v in row.items()};out.setdefault(int(r['frame']),[]).append(r)
    return out

def momentum(rows):return tuple(sum(r['mass']*r[k] for r in rows) for k in ['vx','vy'])
def inertia(r):return r['mass']*(r['width']**2+r['height']**2)/12

def angular(rows):return sum(r['mass']*(r['x']*r['vy']-r['y']*r['vx'])+inertia(r)*r['omega'] for r in rows)
def kinetic(rows):return sum(.5*r['mass']*(r['vx']**2+r['vy']**2)+.5*inertia(r)*r['omega']**2 for r in rows)

def run():
    out={}
    for p in sorted((HERE/'engine-output').glob('*.csv')):
        frames=frame_data(p);keys=sorted(frames);first,last=frames[keys[0]],frames[keys[-1]]
        d={'frames':len(frames),'dt':frames[1][0]['time'],'body_count':len(first),'max_penetration':max(r['max_penetration'] for f in frames.values() for r in f),'last':last}
        if p.stem in ['center','offset']:
            c=next(k for k in keys if frames[k][0]['contacts']>0);p0=momentum(first);l0=angular(first)
            d.update(first_reported_contact_frame=c,first_reported_contact_time=frames[c][0]['time'],after_first_step=frames[c],momentum_error=max(math.hypot(*(a-b for a,b in zip(momentum(rows),p0))) for rows in frames.values()),kinetic_first_last=[kinetic(first),kinetic(last)],max_angular_error=max(abs(angular(rows)-l0) for rows in frames.values()))
        out[p.stem]=d
    (HERE/'engine-output/summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in d.items() if k not in ['last','after_first_step']} for name,d in out.items()},indent=2))
if __name__=='__main__':run()
