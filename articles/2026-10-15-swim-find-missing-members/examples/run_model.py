#!/usr/bin/env python3
"""Original, bounded SWIM teaching model. MIT. Not a production SWIM implementation."""
from __future__ import annotations
import argparse,csv,heapq,itertools,json,math,random
from pathlib import Path
from fractions import Fraction
NODES='ABCDEF'

def merge(old,new):
    """Paper section 4.2; confirmed is terminal for this membership identity."""
    oi,os=old; ni,ns=new
    if os=='confirmed': return old
    if ns=='confirmed': return new
    if ni>oi or (ni==oi and ns=='suspect' and os=='alive'): return new
    return old

class Model:
    def __init__(self,case):
        self.case=case;self.t=0;self.q=[];self.counter=itertools.count();self.packet=0
        self.logs=[];self.states={n:(0,'alive') for n in NODES};self.pending={};self.own_b=0
    def log(self,event,src='',dst='',kind='',seq='',note=''):
        self.logs.append(dict(case=self.case,t_ms=self.t,event=event,src=src,dst=dst,kind=kind,seq=seq,note=note))
    def at(self,t,fn,*args):heapq.heappush(self.q,(t,next(self.counter),fn,args))
    def learn(self,node,rec):
        if node=='B' and rec[1]=='suspect' and rec[0]>=self.own_b:
            self.own_b=rec[0]+1;self.states[node]=(self.own_b,'alive');self.log('REFUTE',node,note=f'B alive {self.own_b}');return
        old=self.states[node];new=merge(old,rec)
        if new!=old:
            self.states[node]=new;self.log('STATE',node,note=f'B {new[1]} {new[0]}')
            if new[1]=='suspect':self.at(self.t+600,self.expire,node,new[0])
        elif rec!=old:self.log('IGNORE',node,note=f'incoming {rec}; keep {old}')
    def expire(self,node,inc):
        if self.states[node]==(inc,'suspect'):self.learn(node,(inc,'confirmed'))
        else:self.log('TIMER_CANCELLED',node,note=f'old suspicion {inc}')
    def send(self,src,dst,kind,seq,requester='',target='',updates=True):
        self.packet+=1
        p=dict(id=self.packet,src=src,dst=dst,kind=kind,seq=seq,requester=requester,target=target,update=self.states[src] if updates else None)
        self.log('SEND',src,dst,kind,seq,f'packet={self.packet}; B={p["update"]}')
        self.at(self.t+20,self.receive,p)
    def receive(self,p):
        s,d,k,q=p['src'],p['dst'],p['kind'],p['seq']
        if (self.case=='indirect' and {s,d}=={'A','B'}) or (d=='B' and (self.case=='dead' or (self.case=='pause' and self.t<350))):
            self.log('DROP',s,d,k,q,f'packet={p["id"]}; injected fault');return
        self.log('RECEIVE',s,d,k,q,f'packet={p["id"]}')
        if p['update'] is not None:self.learn(d,tuple(p['update']))
        if k=='PING_REQ':self.send(d,p['target'],'PING',q,requester=p['requester'])
        elif k=='PING':self.send(d,s,'ACK',q,requester=p['requester'])
        elif k=='ACK':
            if p['requester'] and d!=p['requester']:self.send(d,p['requester'],'ACK_RELAY',q)
            elif q in self.pending and self.pending[q]['src']==d:
                if not self.pending[q]['ok']:
                    self.pending[q]['ok']=True;self.pending[q]['ack_ms']=self.t;self.log('PROBE_OK',d,self.pending[q]['target'],k,q)
        elif k=='ACK_RELAY' and q in self.pending and self.pending[q]['src']==d:
            if not self.pending[q]['ok']:
                self.pending[q]['ok']=True;self.pending[q]['ack_ms']=self.t;self.log('PROBE_OK',d,self.pending[q]['target'],k,q)
    def probe(self,src,target,helpers=()):
        q=f'{src}:{len(self.pending)+1}';self.pending[q]=dict(src=src,target=target,ok=False,start_ms=self.t)
        self.send(src,target,'PING',q);self.at(self.t+100,self.indirect,q,helpers);self.at(self.t+300,self.deadline,q)
    def indirect(self,q,helpers):
        p=self.pending[q]
        if not p['ok']:
            self.log('DIRECT_TIMEOUT',p['src'],p['target'],seq=q)
            for h in helpers:self.send(p['src'],h,'PING_REQ',q,requester=p['src'],target=p['target'])
    def deadline(self,q):
        p=self.pending[q]
        if not p['ok']:
            self.log('PROBE_TIMEOUT',p['src'],p['target'],seq=q)
            # This small model has membership state only for target B.
            assert p['target']=='B'
            self.learn(p['src'],(self.states[p['src']][0],'suspect'))
    def run(self):
        self.at(0,self.probe,'A','B',('C','D'))
        if self.case in ('pause','dead'):
            self.at(400,self.probe,'A','C')
            self.at(440,self.probe,'C','B',('D','E'))
            self.at(500,self.probe,'C','A')
        if self.case=='pause':self.at(560,self.learn,'A',(0,'suspect'))
        while self.q:
            self.t,_,fn,args=heapq.heappop(self.q);fn(*args)
        return self

def gossip(seed=2301,rounds=8):
    rng=random.Random(seed);known={'A'};snapshots=[dict(round=0,known='A',count=1)];contacts=[]
    for r in range(1,rounds+1):
        before=set(known);after=set(known)
        # All pings see start-of-round state; ack sees the just-received ping.
        for s in NODES:
            d=rng.choice([x for x in NODES if x!=s]);has=s in before or d in before
            contacts.append(dict(round=r,src=s,dst=d,ping_has_update=s in before,ack_has_update=has))
            if has:after.update((s,d))
        known=after;snapshots.append(dict(round=r,known=''.join(sorted(known)),count=len(known)))
    return snapshots,contacts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases={k:Model(k).run() for k in ('healthy','indirect','pause','dead')}
    assert cases['healthy'].pending['A:1']['ack_ms']==40
    assert cases['indirect'].pending['A:1']['ack_ms']==180
    assert cases['pause'].states['A']==(1,'alive')
    assert cases['dead'].states['A']==(0,'confirmed')
    assert [x['t_ms'] for x in cases['pause'].logs if x['event']=='STATE' and x['src']=='A']==[300,520]
    assert [x['t_ms'] for x in cases['dead'].logs if x['event']=='STATE' and x['src']=='A']==[300,900]
    assert merge((0,'suspect'),(0,'alive'))==(0,'suspect')
    assert merge((0,'suspect'),(1,'alive'))==(1,'alive')
    assert merge((1,'alive'),(0,'suspect'))==(1,'alive')
    assert merge((0,'confirmed'),(99,'alive'))==(0,'confirmed')
    ordering=[]
    for msgs in itertools.permutations([(0,'alive'),(0,'suspect'),(1,'alive')]):
        v=(0,'alive')
        for msg in msgs:v=merge(v,msg)
        assert v==(1,'alive');ordering.append(dict(messages=msgs,result=v))
    # Duplicate suspicion does not restart a running timer.
    z=Model('dead');z.at(300,z.learn,'A',(0,'suspect'));z.at(500,z.learn,'A',(0,'suspect'))
    while z.q:z.t,_,fn,ar=heapq.heappop(z.q);fn(*ar)
    assert [x['t_ms'] for x in z.logs if x['note']=='B confirmed 0']==[900]
    snaps,contacts=gossip()
    assert snaps[-1]['count']==6
    loads=[dict(n=n,all_to_all_heartbeats=n*(n-1),healthy_ping_ack=2*n) for n in (6,100,1000)]
    detection=[]
    for n in (6,10,100,1000):
        miss=Fraction(n-2,n-1)**(n-1);p=1-miss
        detection.append(dict(n=n,p_at_least_one_probe=float(p),expected_rounds=float(1/p),miss_three_rounds=float(miss**3)))
    out=dict(model='bounded pedagogical event model, not complete SWIM',time_unit='virtual milliseconds',one_way_ms=20,direct_timeout_ms=100,probe_deadline_ms=300,suspicion_ms=600,seed_gossip=2301,cases={k:dict(final_state_A_for_B=v.states['A'],first_probe=v.pending['A:1'],sent_packets=sum(x['event']=='SEND' for x in v.logs)) for k,v in cases.items()},gossip=snaps,loads=loads,detection=detection,merge_permutation_cases=6,duplicate_suspicion_keeps_deadline=True)
    (args.output/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    def csvout(name,rows):
        with (args.output/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    csvout('events.csv',[x for v in cases.values() for x in v.logs]);csvout('gossip-contacts.csv',contacts)
    (args.output/'merge-tests.json').write_text(json.dumps(ordering,indent=2)+'\n')
    s='All assertions passed.\n'+json.dumps(out['cases'],ensure_ascii=False,indent=2)+'\nGossip counts: '+','.join(str(x['count']) for x in snaps)+'\n'
    (args.output/'stdout.txt').write_text(s);print(s,end='')
if __name__=='__main__':main()
