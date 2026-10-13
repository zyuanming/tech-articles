"""Original finite fencing lab. Pure local state, no services, timers or disk I/O."""
from dataclasses import dataclass
from itertools import product, permutations
import json

@dataclass
class Resource:
    epoch: int = 0
    value: int = 100

    def activate(self, token):
        # Entire method is one atomic, durable resource operation in this model.
        if token < self.epoch:
            return False
        self.epoch = token
        return True

    def read(self, token):
        if token != self.epoch:
            return None
        return self.value

    def write(self, token, value):
        # Check AND effect share one atomic, durable operation.
        if token != self.epoch:
            return False
        self.value = value
        return True


def schedules(progress):
    if all(x == 3 for x in progress):
        yield ()
        return
    for i, x in enumerate(progress):
        if x < 3:
            new = list(progress); new[i] += 1
            for rest in schedules(tuple(new)):
                yield ((i, x),) + rest


def run_schedule(order, deltas):
    r = Resource(); snapshots = [None] * len(deltas)
    successes = []; events = []
    for i, stage in order:
        token = i + 1
        old_epoch = r.epoch
        if stage == 0:
            ok = r.activate(token); event = 'activate'
        elif stage == 1:
            snapshots[i] = r.read(token)
            ok = snapshots[i] is not None; event = 'read'
        else:
            ok = snapshots[i] is not None and r.write(token, snapshots[i] + deltas[i])
            if ok: successes.append(i)
            event = 'write'
        assert r.epoch >= old_epoch
        if ok and event == 'write': assert token == r.epoch
        assert r.value == 100 + sum(deltas[j] for j in successes)
        events.append({'worker':chr(65+i),'event':event,'token':token,'accepted':ok,'epoch':r.epoch,'value':r.value})
    return events


def main_trace():
    r=Resource(); trace=[]
    def row(event, ok=None):trace.append({'event':event,'epoch':r.epoch,'value':r.value,'accepted':ok})
    row('初始');row('A登记41',r.activate(41));old=r.read(41);row('A读100，准备加10')
    row('A暂停，租约在服务端到期');row('B登记42',r.activate(42));new=r.read(42);row('B读100，准备加20')
    row('B写120',r.write(42,new+20));row('A迟到写110',r.write(41,old+10))
    assert r.value==120 and trace[-1]['accepted'] is False
    return trace


def boundary_examples():
    # A new grant alone does not update resource state.
    r=Resource();r.activate(41);assert r.write(41,110)
    before_activate=r.value
    # Durably retaining the fence on resource restart preserves rejection.
    r.activate(42);r.write(42,120)
    good_restart=Resource(r.epoch,r.value);assert not good_restart.write(41,110)
    # Forgetting the fence, followed by delayed old activation, permits old writer.
    bad_restart=Resource(0,r.value);assert bad_restart.activate(41);assert bad_restart.write(41,110)
    # Reusing a token for distinct owners makes them indistinguishable.
    reused=Resource(7,100);assert reused.write(7,120);assert reused.write(7,110)
    # A read done before the new fence is installed can already be stale.
    bad_read=Resource(41,100);b_snapshot=bad_read.value
    assert bad_read.write(41,110);bad_read.activate(42);assert bad_read.write(42,b_snapshot+20)
    assert bad_read.value==120 # Should be130 if both accepted increments were preserved.
    # Separate checking and writing permits a write past a newer fence.
    split=Resource(41,100);old_check=(split.epoch==41)
    split.activate(42);split.write(42,120)
    if old_check:split.value=110
    assert split.epoch==42 and split.value==110
    # Same-epoch writes need their own ordering / retry semantics.
    same=Resource(42,100);same.write(42,120);same.write(42,110)
    assert same.value==110
    # Atomic request-id dedup is additional state, not supplied by a fence.
    value=100;seen=set()
    for req,delta in [('r1',10),('r1',10)]:
        if req not in seen:seen.add(req);value+=delta
    assert value==110
    return {'before_new_activation_old_write_accepted':before_activate,'durable_restart_value':good_restart.value,'forgotten_fence_value':bad_restart.value,'reused_token_value':reused.value,'read_before_activate_lost_increment':bad_read.value,'non_atomic_check_effect_value':split.value,'same_epoch_reordered_value':same.value,'extra_request_id_dedup_value':value}


def check():
    counts={};total_steps=0
    for n in (1,2,3):
        orders=list(schedules((0,)*n));checks=0
        # All signs and zero; linear score only, no real payment/inventory system.
        for ds in product((-2,0,3),repeat=n):
            for order in orders:run_schedule(order,ds);checks+=1;total_steps+=3*n
        counts[str(n)]={'schedules':len(orders),'delta_vectors':3**n,'runs':checks}
    # Enumerate arbitrary repeated / backwards activation requests.
    activation_count=0
    for tokens in product(range(1,5),repeat=6):
        r=Resource()
        for t in tokens:
            old=r.epoch;ok=r.activate(t)
            assert ok==(t>=old);assert r.epoch==max(old,t)
        activation_count+=1
    return {'interleavings':counts,'total_atomic_steps':total_steps,'activation_sequences_length6':activation_count,'main_trace':main_trace(),'boundaries':boundary_examples(),'scope':'finite original atomic/durable single-resource model; trusted unique increasing grants; no lock implementation, real clock, filesystem, consensus or production test'}

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))
