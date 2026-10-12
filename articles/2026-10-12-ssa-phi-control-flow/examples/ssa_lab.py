"""Original small SSA interpreter and checker, CC BY 4.0.
Integer teaching IR, not LLVM. No pointers, exceptions, poison, overflow or I/O.
A block's phi inputs are selected by predecessor and committed simultaneously.
"""
from copy import deepcopy
from itertools import product
import argparse,json,random


def block(ops=(), term=('ret',0), phis=()):
    return {'phis':list(phis),'ops':list(ops),'term':term}


def successors(b):
    t=b['term'];return list(t[2:4]) if t[0]=='br' else [t[1]] if t[0]=='jmp' else []


def graph(program):
    blocks=program['blocks'];pred={b:set() for b in blocks}
    for name,b in blocks.items():
        for dst in successors(b):
            if dst not in blocks:raise ValueError('unknown successor')
            pred[dst].add(name)
    seen=set();stack=[program['entry']]
    while stack:
        n=stack.pop()
        if n not in seen:seen.add(n);stack.extend(successors(blocks[n]))
    if seen!=set(blocks):raise ValueError('this teaching checker rejects unreachable blocks')
    if pred[program['entry']]:raise ValueError('entry must have no predecessor')
    dom={b:({b} if b==program['entry'] else set(blocks)) for b in blocks}
    changed=True
    while changed:
        changed=False
        for b in blocks:
            if b==program['entry']:continue
            new={b}|set.intersection(*(dom[p] for p in pred[b]))
            if new!=dom[b]:dom[b]=new;changed=True
    return pred,dom


def validate(program):
    blocks=program['blocks'];entry=program['entry'];pred,dom=graph(program)
    defs={}
    def define(name,loc):
        if not isinstance(name,str) or name in defs:raise ValueError('duplicate or invalid definition: '+str(name))
        defs[name]=loc
    for name in program['params']:define(name,(entry,-2))
    for b,body in blocks.items():
        for dest,ins in body['phis']:
            if set(ins)!=pred[b]:raise ValueError('phi predecessor mismatch')
            define(dest,(b,-1))
        for i,(op,dest,args) in enumerate(body['ops']):
            if op not in ('copy','add','mul','lt'):raise ValueError('unknown operation')
            if len(args)!=(1 if op=='copy' else 2):raise ValueError('arity')
            define(dest,(b,i))
    def use(operand,b,index):
        if not isinstance(operand,str):
            if not isinstance(operand,int):raise ValueError('noninteger literal')
            return
        if operand not in defs:raise ValueError('undefined name '+operand)
        db,di=defs[operand]
        if db not in dom[b] or (db==b and di>=index):raise ValueError('definition does not dominate use: '+operand)
    for b,body in blocks.items():
        for _,ins in body['phis']:
            for p,value in ins.items():use(value,p,len(blocks[p]['ops']))
        for i,(_,_,args) in enumerate(body['ops']):
            for arg in args:use(arg,b,i)
        t=body['term']
        if t[0] in ('ret','br'):use(t[1],b,len(body['ops']))
        elif t[0]!='jmp':raise ValueError('unknown terminator')
    return {'predecessors':pred,'dominators':dom,'definitions':defs}


def evaluate(op,args):
    if op=='copy':return args[0]
    if op=='add':return args[0]+args[1]
    if op=='mul':return args[0]*args[1]
    if op=='lt':return int(args[0]<args[1])
    raise ValueError(op)


def run(program,inputs,max_blocks=10000,trace=False):
    validate(program)
    if set(inputs)!=set(program['params']):raise ValueError('input names')
    env=dict(inputs);name=program['entry'];previous=None;events=[];arithmetic=0
    def val(x):return env[x] if isinstance(x,str) else x
    for _ in range(max_blocks):
        b=program['blocks'][name]
        # Read selected incoming values from OLD env before committing any phi.
        incoming={dest:val(options[previous]) for dest,options in b['phis']}
        env.update(incoming)
        event={'block':name,'predecessor':previous,'phi_values':dict(incoming)}
        for op,dest,args in b['ops']:
            env[dest]=evaluate(op,[val(x) for x in args])
            arithmetic+=op in ('add','mul','lt')
        if trace:event['environment']=dict(env);events.append(event)
        t=b['term']
        if t[0]=='ret':return {'value':val(t[1]),'trace':events,'arithmetic_operations':arithmetic}
        previous,name=name,(t[1] if t[0]=='jmp' else t[2] if val(t[1]) else t[3])
    raise RuntimeError('block budget exhausted; not a termination proof')


def diamond(left=3,right=1,extra=2):
    return {'params':['flag'],'entry':'entry','blocks':{
      'entry':block(term=('br','flag','left','right')),
      'left':block([('copy','x1',[left])],('jmp','join')),
      'right':block([('copy','x2',[right])],('jmp','join')),
      'join':block([('add','y1',['x3',extra])],('ret','y1'),[('x3',{'left':'x1','right':'x2'})])}}


def sum_loop():
    return {'params':['n'],'entry':'entry','blocks':{
      'entry':block([('copy','i0',[0]),('copy','s0',[0])],('jmp','head')),
      'head':block([('lt','more',['i1','n'])],('br','more','body','exit'),
                   [('i1',{'entry':'i0','body':'i2'}),('s1',{'entry':'s0','body':'s2'})]),
      'body':block([('add','s2',['s1','i1']),('add','i2',['i1',1])],('jmp','head')),
      'exit':block(term=('ret','s1'))}}


def swap_loop():
    return {'params':['n','a0','b0'],'entry':'entry','blocks':{
      'entry':block([('copy','i0',[0])],('jmp','head')),
      'head':block([('lt','more',['i1','n'])],('br','more','body','exit'),
          [('a1',{'entry':'a0','body':'b1'}),('b1',{'entry':'b0','body':'a1'}),('i1',{'entry':'i0','body':'i2'})]),
      'body':block([('add','i2',['i1',1])],('jmp','head')),
      'exit':block([('mul','t1',['a1',1000]),('add','answer',['t1','b1'])],('ret','answer'))}}


def constant_facts(program):
    """Conservative known-constant propagation: require ALL phi inputs known/equal.
    No executable-edge analysis, so this is not a complete SCCP implementation.
    """
    validate(program);known={};changed=True
    def get(v):return known.get(v) if isinstance(v,str) else v
    while changed:
        changed=False
        for b in program['blocks'].values():
            for dest,ins in b['phis']:
                vals=[get(v) for v in ins.values()]
                if vals and all(v is not None for v in vals) and len(set(vals))==1 and dest not in known:
                    known[dest]=vals[0];changed=True
            for op,dest,args in b['ops']:
                vals=[get(x) for x in args]
                if all(x is not None for x in vals) and dest not in known:
                    known[dest]=evaluate(op,vals);changed=True
    return known


def fold_constants(program):
    facts=constant_facts(program);out=deepcopy(program)
    def sub(x):return facts.get(x,x) if isinstance(x,str) else x
    for b in out['blocks'].values():
        # Preserve phi structure and predecessor edges; replace known operands.
        b['phis']=[(dest,{p:sub(v) for p,v in ins.items()}) for dest,ins in b['phis']]
        b['ops']=[('copy',dest,[facts[dest]]) if dest in facts else (op,dest,[sub(x) for x in args]) for op,dest,args in b['ops']]
        t=b['term']
        if t[0] in ('br','ret'):b['term']=(t[0],sub(t[1]),*t[2:])
    validate(out);return out,facts



def dominance_frontiers(program):
    """Direct definition for tiny teaching graphs, NOT the fast 1991 algorithm."""
    pred,dom=graph(program)
    return {x:{y for y in pred if any(x in dom[p] for p in pred[y]) and not (x!=y and x in dom[y])} for x in pred}


def check_random_dominance():
    rng=random.Random(199110);count=0
    for _ in range(2000):
        n=rng.randint(2,10);names=['b'+str(i) for i in range(n)];blocks={}
        for i,name in enumerate(names):
            if i==n-1:blocks[name]=block(term=('ret',0));continue
            other=rng.randrange(1,n)
            term=('br','flag',names[i+1],names[other]) if other!=i+1 else ('jmp',names[i+1])
            blocks[name]=block(term=term)
        prog={'params':['flag'],'entry':names[0],'blocks':blocks};_,dom=graph(prog)
        for removed in names:
            reachable=set();stack=[] if removed==names[0] else [names[0]]
            while stack:
                x=stack.pop()
                if x==removed or x in reachable:continue
                reachable.add(x);stack.extend(successors(blocks[x]))
            for x in names:assert (removed in dom[x])==(x not in reachable)
        count+=1
    return count


def checks():
    random_graphs=check_random_dominance()
    assert dominance_frontiers(diamond())=={'entry':set(),'left':{'join'},'right':{'join'},'join':set()}
    assert dominance_frontiers(sum_loop())['head']=={'head'}
    comparisons=0
    for left,right,extra in product(range(-8,9),repeat=3):
        p=diamond(left,right,extra);f,_=fold_constants(p)
        for flag in (0,1):
            expected=(left if flag else right)+extra
            assert run(p,{'flag':flag})['value']==expected
            assert run(f,{'flag':flag})['value']==expected
            comparisons+=1
    sums=0
    for n in range(-10,301):
        assert run(sum_loop(),{'n':n})['value']==sum(range(n));sums+=1
    swaps=0
    for a,b,n in product(range(-4,5),range(-4,5),range(21)):
        x,y=a,b
        for _ in range(n):x,y=y,x
        assert run(swap_loop(),{'a0':a,'b0':b,'n':n})['value']==1000*x+y;swaps+=1
    p=diamond(7,7,2);f,facts=fold_constants(p)
    assert facts['x3']==7 and facts['y1']==9
    assert [run(p,{'flag':x})['arithmetic_operations'] for x in (0,1)]==[1,1]
    assert [run(f,{'flag':x})['arithmetic_operations'] for x in (0,1)]==[0,0]
    # Wrong ordinary use from only one branch is statically rejected.
    bad=diamond();bad['blocks']['join']['ops'][0]=('add','y1',['x1',2])
    rejected=[]
    for label,prog in [('non-dominating-use',bad)]:
        try:validate(prog)
        except ValueError as e:rejected.append({'case':label,'reason':str(e)})
        else:raise AssertionError(label)
    bad=diamond();bad['blocks']['right']['ops'][0]=('copy','x1',[1])
    try:validate(bad)
    except ValueError as e:rejected.append({'case':'duplicate-definition','reason':str(e)})
    else:raise AssertionError('duplicate')
    bad=diamond();bad['blocks']['join']['phis'][0][1].pop('right')
    try:validate(bad)
    except ValueError as e:rejected.append({'case':'missing-phi-edge','reason':str(e)})
    else:raise AssertionError('missing edge')
    return {'scope':'Original integer teaching IR, not LLVM execution or production compiler benchmark',
      'random_cfg_dominance_remove_vertex_checks':random_graphs,'random_seed':199110,
      'diamond_input_cases_original_and_folded':comparisons,'sum_loop_inputs':sums,'swap_loop_inputs':swaps,
      'invalid_programs_rejected':rejected,'sum_n4_trace':run(sum_loop(),{'n':4},trace=True),
      'swap_once_trace':run(swap_loop(),{'n':1,'a0':1,'b0':2},trace=True),
      'constant_facts_equal_branch':facts,'diamond_dominators':validate(diamond())['dominators']}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args()
    result=json.dumps(checks(),ensure_ascii=False,indent=2,default=lambda v:sorted(v) if isinstance(v,set) else str(v))+'\n'
    if args.output:
        with open(args.output,'w') as f:f.write(result)
    print(result,end='')
