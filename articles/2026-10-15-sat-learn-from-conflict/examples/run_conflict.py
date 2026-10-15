"""Original six-variable conflict lesson, not an industrial/full CDCL solver."""
from pathlib import Path
import argparse,csv,itertools,json,platform
NAMES={1:'p',2:'z',3:'x',4:'u',5:'v',6:'w'}
CLAUSES={'C1':(-3,4),'C2':(-3,5),'C3':(-1,-4,-5),'C4':(2,6)}
def canon(c):return tuple(sorted(set(c),key=lambda x:(abs(x),x)))
def littext(lit):return ('¬' if lit<0 else '')+NAMES[abs(lit)]
def value(lit,state):return None if abs(lit) not in state else state[abs(lit)]==(lit>0)
def satisfied(c,state):return any(value(l,state) is True for l in c)
def resolve(c,d,pivot):
    assert (pivot in c and -pivot in d) or (-pivot in c and pivot in d)
    out=canon([x for x in c if abs(x)!=abs(pivot)]+[x for x in d if abs(x)!=abs(pivot)])
    assert not any(-x in out for x in out)
    return out
class Lesson:
    def __init__(self,order):self.clauses=dict(CLAUSES);self.order=list(order);self.state={};self.trail=[];self.events=[];self.level=0
    def put(self,lit,reason=None):
        assert abs(lit) not in self.state
        antecedents=[] if reason is None else [-x for x in self.clauses[reason] if abs(x)!=abs(lit)]
        assert all(value(x,self.state) for x in antecedents)
        row=dict(literal=lit,text=littext(lit),level=self.level,reason=reason,antecedents=antecedents)
        self.state[abs(lit)]=lit>0;self.trail.append(row);self.events.append(dict(kind='decision' if reason is None else 'propagation',**row))
    def propagate(self):
        while True:
            changed=False
            for cid in self.order:
                clause=self.clauses[cid]
                if satisfied(clause,self.state):continue
                remaining=[x for x in clause if value(x,self.state) is None]
                if not remaining:self.events.append(dict(kind='conflict',clause=cid,literals=list(clause),level=self.level));return cid
                if len(remaining)==1:self.put(remaining[0],cid);changed=True
            if not changed:return None
    def decide(self,lit):self.level+=1;self.put(lit);return self.propagate()
    def analyze(self,conflict):
        learned=canon(self.clauses[conflict]);steps=[]
        levels={abs(r['literal']):r['level'] for r in self.trail}
        while sum(levels[abs(l)]==self.level for l in learned)>1:
            chosen=next(r for r in reversed(self.trail) if r['level']==self.level and any(abs(l)==abs(r['literal']) for l in learned))
            assert chosen['reason'] is not None
            reason=self.clauses[chosen['reason']];new=resolve(learned,reason,chosen['literal']);steps.append(dict(before=list(learned),reason=chosen['reason'],reason_clause=list(reason),pivot=chosen['literal'],after=list(new)));learned=new
        current=[l for l in learned if levels[abs(l)]==self.level];assert len(current)==1
        target=max([levels[abs(l)] for l in learned if l!=current[0]],default=0)
        return learned,steps,target,current[0]
    def backjump(self,target,learned):
        erased=[r for r in self.trail if r['level']>target];self.trail=[r for r in self.trail if r['level']<=target];self.state={abs(r['literal']):r['literal']>0 for r in self.trail};self.level=target;self.clauses['C5']=learned;self.order.append('C5');self.events.append(dict(kind='backjump',target=target,erased=erased,learned=list(learned)));assert self.propagate() is None

def run(order=('C1','C2','C3','C4')):
    s=Lesson(order);assert s.decide(1) is None;assert s.decide(2) is None;conflict=s.decide(3);assert conflict is not None
    before=list(s.trail);learned,steps,target,asserted=s.analyze(conflict);assert learned==(-1,-3) and target==1 and asserted==-3
    s.backjump(target,learned);assert s.state=={1:True,3:False};return dict(order=list(order),trail_before=before,conflict=conflict,learned=list(learned),resolution=steps,backjump_level=target,asserted_literal=asserted,trail_after=s.trail,events=s.events)

def main(out):
    out.mkdir(parents=True,exist_ok=False);main=run();states=[dict(zip(range(1,7),bits)) for bits in itertools.product([False,True],repeat=6)];truth=[];models=[];proof_checks=0
    for idx,s in enumerate(states):
        original=all(satisfied(c,s) for c in CLAUSES.values());learned=satisfied(main['learned'],s);after=original and learned
        assert original==after
        if original:models.append({NAMES[v]:int(s[v]) for v in range(1,7)})
        truth.append(dict(index=idx,**{NAMES[v]:int(s[v]) for v in range(1,7)},original=int(original),learned=int(learned),augmented=int(after)))
        for st in main['resolution']:
            if satisfied(st['before'],s) and satisfied(st['reason_clause'],s):assert satisfied(st['after'],s)
            proof_checks+=1
    assert len(models)==24 and sum(not r['learned']for r in truth)==16
    projected=[]
    for p,x in itertools.product([0,1],repeat=2):projected.append(dict(p=p,x=x,models=sum(r['original'] for r in truth if r['p']==p and r['x']==x)))
    order_checks=[]
    for order in itertools.permutations(CLAUSES):
        r=run(order);order_checks.append(dict(order=list(order),conflict=r['conflict'],learned=r['learned'],backjump=r['backjump_level']))
    witness=dict(p=1,z=1,x=0,u=0,v=0,w=0);assert witness in models
    result=dict(model='Six Boolean variables, fixed chosen decisions; deterministic scan propagation; explicit resolution; no external solver',python=platform.python_version(),variables=NAMES,clauses={k:list(v) for k,v in CLAUSES.items()},main=main,truth_rows=len(truth),models_before=len(models),models_after=len(models),models=models,projected=projected,learned_false_assignments=16,learned_clause_entailment_checks=64,resolution_implication_checks=proof_checks,clause_order_checks=order_checks,witness=witness)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'truth-table.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(truth[0]));w.writeheader();w.writerows(truth)
    summary=f"DECISIONS p=1@1, z=1@2, x=1@3; conflict={main['conflict']}\nLEARNED (not p OR not x); BACKJUMP 3 -> 1; ASSERT x=0@1\nFULL ASSIGNMENTS 64; MODELS 24 -> 24; learned rejects16 (all already illegal)\nPROOF: 128 resolution implication checks; 24 clause-order variants learn same clause\nWITNESS {json.dumps(witness,sort_keys=True)}\n"
    (out/'stdout.txt').write_text(summary);print(summary,end='')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)
