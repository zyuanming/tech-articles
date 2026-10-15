#!/usr/bin/env python3
"""Real loopback UDP sockets with explicit application fault injection. MIT.
One process, six sockets, one probe per independent case. No full SWIM or pcap.
"""
import argparse,csv,heapq,itertools,json,platform,selectors,socket,time
from pathlib import Path

def run(case):
    sel=selectors.DefaultSelector();socks={};logs=[];q=[];counter=itertools.count();acked=False;ack_ms=None
    for n in 'ABCDEF':
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind(('127.0.0.1',0));s.setblocking(False);sel.register(s,selectors.EVENT_READ,n);socks[n]=s
    start=time.perf_counter_ns()
    def elapsed():return (time.perf_counter_ns()-start)/1_000_000
    def log(event,src='',dst='',kind='',note=''):
        logs.append(dict(case=case,t_ms=round(elapsed(),6),event=event,src=src,dst=dst,kind=kind,note=note))
    def later(ms,fn,*args):heapq.heappush(q,(elapsed()+ms,next(counter),fn,args))
    def send(src,dst,kind,relay=''):
        p=dict(src=src,dst=dst,kind=kind,seq='A:1',relay=relay)
        raw=json.dumps(p,separators=(',',':')).encode();count=socks[src].sendto(raw,socks[dst].getsockname());assert count==len(raw)
        log('SEND',src,dst,kind,f'bytes={len(raw)}; seq=A:1')
    def process(p):
        nonlocal acked,ack_ms
        s,d,k=p['src'],p['dst'],p['kind'];log('PROCESS',s,d,k)
        if (case=='indirect' and {s,d}=={'A','B'}) or (case=='silent' and d=='B'):
            log('APP_DROP',s,d,k,'application ignores received datagram');return
        if k=='PING_REQ':send(d,'B','PING','A')
        elif k=='PING':send(d,s,'ACK',p['relay'])
        elif k=='ACK' and p['relay'] and d!='A':send(d,'A','ACK_RELAY')
        elif k in ('ACK','ACK_RELAY') and d=='A' and not acked:
            acked=True;ack_ms=elapsed();log('PROBE_OK','A','B',k)
    def indirect():
        if not acked:
            log('DIRECT_TIMEOUT','A','B')
            send('A','C','PING_REQ','A');send('A','D','PING_REQ','A')
    send('A','B','PING');later(100,indirect)
    while elapsed()<300:
        now=elapsed()
        while q and q[0][0]<=now:
            _,_,fn,args=heapq.heappop(q);fn(*args);now=elapsed()
        remain=300-elapsed()
        if remain<=0:break
        timeout=min(remain,max(0,q[0][0]-elapsed()) if q else remain)/1000
        for key,_ in sel.select(timeout):
            while True:
                try:raw,address=key.fileobj.recvfrom(4096)
                except BlockingIOError:break
                p=json.loads(raw);assert p['dst']==key.data and p['seq']=='A:1'
                log('SOCKET_RECEIVE',p['src'],p['dst'],p['kind'],f'bytes={len(raw)}')
                # Deliberate local scheduling delay; NOT measured network latency.
                later(20,process,p)
    log('DEADLINE','A','B',note='ack received' if acked else 'no ack; eligible to suspect')
    for s in socks.values():sel.unregister(s);s.close()
    sel.close()
    sent=sum(x['event']=='SEND' for x in logs);received=sum(x['event']=='SOCKET_RECEIVE' for x in logs);drops=sum(x['event']=='APP_DROP' for x in logs)
    assert sent==received
    assert sent=={'healthy':2,'indirect':9,'silent':5}[case]
    assert drops=={'healthy':0,'indirect':1,'silent':3}[case]
    assert acked==(case!='silent')
    assert ack_ms is None or 0<ack_ms<300
    return logs,dict(case=case,ack_received=acked,ack_ms=ack_ms,udp_sent=sent,udp_received=received,application_drops=drops,deadline_ms=logs[-1]['t_ms'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    rows=[];summaries=[]
    for case in ('healthy','indirect','silent'):
        r,s=run(case);rows.extend(r);summaries.append(s)
    result=dict(identity='one actual local run: six real loopback UDP sockets in one process; no packet capture; application log',python=platform.python_version(),clock='time.perf_counter_ns; elapsed monotonic milliseconds',processing_delay_ms=20,direct_timeout_ms=100,deadline_ms=300,randomness='none; OS scheduling and timing nondeterministic',cases=summaries)
    with (a.output/'udp-events.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (a.output/'udp-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    out='UDP assertions passed.\n'+json.dumps(summaries,indent=2)+'\n';(a.output/'udp-stdout.txt').write_text(out);print(out,end='')
if __name__=='__main__':main()
