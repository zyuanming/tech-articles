"""Original finite WAL model: serialized transactions, atomic page writes,
valid durable log prefix, no media loss, all recovery finishes before service.
NOT a DBMS, ARIES implementation, disk/fsync test, or concurrent algorithm.
"""
from itertools import product
import json

INITIAL = {'A': 100, 'B': 40}
# UPDATE, transaction, page, before, after; COMMIT, transaction.
PROGRAM = [('U', 1, 'A', 100, 70), ('U', 1, 'B', 40, 70), ('C', 1),
           ('U', 2, 'A', 70, 80), ('U', 2, 'B', 70, 60), ('C', 2)]

def recover(disk, durable_log):
    """只用于正文的串行、全日志模型。"""
    result = dict(disk)
    winners = {r[1] for r in durable_log if r[0] == 'C'}
    # 顺序重做所有保留的修改
    for r in durable_log:
        if r[0] == 'U':
            result[r[2]] = r[4]
    # 逆序撤销没有持久提交的尾部
    for r in reversed(durable_log):
        if r[0] == 'U' and r[1] not in winners:
            result[r[2]] = r[3]
    return result

def recovery_writes(log):
    winners = {r[1] for r in log if r[0] == 'C'}
    return [(r[2],r[4]) for r in log if r[0]=='U'] + [(r[2],r[3]) for r in reversed(log) if r[0]=='U' and r[1] not in winners]

def expected(log, initial=INITIAL):
    # Separate commit oracle: publish each transaction's private write set only
    # on encountering its durable commit, never read original data-page state.
    state=dict(initial); pending={}
    for r in log:
        if r[0]=='U':pending.setdefault(r[1],{})[r[2]]=r[4]
        else:state.update(pending.pop(r[1],{}))
    return state

def explore(program=PROGRAM, initial=INITIAL):
    # Exact reachability, not all arbitrary impossible disk/log combinations.
    # State: issued count, durable log count, durable page A/B plus page LSNs.
    first=(0,0,initial['A'],initial['B'],0,0)
    todo=[first]; seen={first}; edges=0; recovery_cuts=0
    while todo:
        s=todo.pop(); i,k,a,b,pa,pb=s; disk={'A':a,'B':b};log=program[:k]
        assert recover(disk,log)==expected(log,initial)
        assert recover(recover(disk,log),log)==expected(log,initial)
        partial=dict(disk)
        for page,value in recovery_writes(log):
            partial[page]=value
            assert recover(partial,log)==expected(log,initial)
            recovery_cuts+=1
        # At most one transaction runs; the next starts only after the previous
        # commit is durable. A durable commit need not yet have been acknowledged.
        successors=[]
        if i<len(program) and (i==0 or program[i-1][0]!='C' or k>=i):
            successors.append((i+1,k,a,b,pa,pb))
        if k<i:successors.append((i,k+1,a,b,pa,pb))
        mem=dict(initial);last={'A':0,'B':0}
        for n,r in enumerate(program[:i],1):
            if r[0]=='U':mem[r[2]]=r[4];last[r[2]]=n
        if last['A']>pa and last['A']<=k:successors.append((i,k,mem['A'],b,last['A'],pb))
        if last['B']>pb and last['B']<=k:successors.append((i,k,a,mem['B'],pa,last['B']))
        for t in successors:
            edges+=1
            if t not in seen:seen.add(t);todo.append(t)
    return {'reachable_states':len(seen),'state_transitions':edges,'recovery_write_crash_cuts':recovery_cuts}

def check():
    counts=explore(); varied=0; states=0
    # Different initial values and two transfers, including zero and negative
    # toy values. Money/business constraints are outside this recovery model.
    for a,b,x,y in product(range(-2,3),repeat=4):
        init={'A':a,'B':b};p=[('U',1,'A',a,a-x),('U',1,'B',b,b+x),('C',1),('U',2,'A',a-x,a-x+y),('U',2,'B',b+x,b+x-y),('C',2)]
        z=explore(p,init);varied+=1;states+=z['reachable_states']
    main_disk={'A':80,'B':40};main_log=PROGRAM[:5]; trace=[];state=dict(main_disk)
    for page,value in recovery_writes(main_log):state[page]=value;trace.append(dict(state))
    assert trace==[{'A':70,'B':40},{'A':70,'B':70},{'A':80,'B':70},{'A':80,'B':60},{'A':80,'B':70},{'A':70,'B':70}]
    # Intentionally illegal durable images demonstrate the two required orders.
    missing_log = recover({'A':70,'B':40},[])  # data before its log: no old A
    lost_ack = recover(INITIAL,PROGRAM[:2])    # acknowledged before commit flush
    assert missing_log!={'A':100,'B':40}
    assert lost_ack!={'A':70,'B':70}
    # Chronological rather than reverse undo fails if one unfinished tx writes
    # the same page twice. Correct reverse undo restores 100.
    twice=[('U',1,'A',100,70),('U',1,'A',70,60)]
    assert recover({'A':60,'B':40},twice)==INITIAL
    wrong=dict(INITIAL)
    for r in twice:wrong[r[2]]=r[3]
    assert wrong['A']==70
    # No acknowledged client message is modelled. Durable commit means committed
    # even if the client did not receive a reply; absent reply is not an abort.
    return {'main':counts,'varied_programs':varied,'varied_reachable_states':states,'main_log':[list(r) for r in main_log],'main_disk':main_disk,'main_recovery_trace':trace,'main_final':state,'illegal_page_before_log':missing_log,'illegal_ack_before_commit':lost_ack,'wrong_forward_undo':wrong,'model':'serialized, atomic pages, valid durable prefix, retained full log, no readers during recovery'}

if __name__=='__main__': print(json.dumps(check(),ensure_ascii=False,indent=2))
