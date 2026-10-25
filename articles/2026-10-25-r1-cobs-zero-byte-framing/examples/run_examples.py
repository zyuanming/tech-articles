"""Compute all quantities used by the article. CC0-1.0."""
from pathlib import Path
from itertools import product
import json, random, sys
from model import encode, decode, Receiver, formula, hexbytes
ROOT=Path(__file__).resolve().parent

def run():
    payload=bytes.fromhex('11 22 00 33 00 00 44 00')
    encoded, enc_trace=encode(payload,record=True)
    decoded, dec_trace=decode(encoded,record=True)
    assert encoded == bytes.fromhex('03 11 22 02 33 01 02 44 01')
    assert decoded == payload
    frame=encoded+b'\0'
    tiny=[]
    for p in [b'',b'\0',b'\0\0',bytes.fromhex('11'),bytes.fromhex('FF')]:
        e,_=encode(p)
        tiny.append(dict(input=list(p),encoded=list(e),wire=list(e+b'\0'),
                         codes=[x['start'] for x in decode(e,True)[1]]))
    boundaries=[]
    for n in [253,254,255,508]:
        p=bytes([0x55])*n
        a,_=encode(p);b,_=encode(p,True)
        boundaries.append(dict(n=n,plain=len(a),compact=len(b),
            plain_codes=[x['code'] for x in decode(a,True)[1]],
            compact_codes=[x['code'] for x in decode(b,True)[1]],
            plain_blocks=[x['count'] for x in decode(a,True)[1]],
            compact_blocks=[x['count'] for x in decode(b,True)[1]]))
    p=bytes([0x55])*254+b'\0'
    e,_=encode(p)
    after_full_zero=dict(n=len(p),encoded_length=len(e),
                        codes=[x['code'] for x in decode(e,True)[1]],
                        blocks=[x['count'] for x in decode(e,True)[1]])
    small_count=0
    for n in range(8):
        for values in product([0,1,255],repeat=n):
            p=bytes(values)
            for compact in [False,True]:
                e,_=encode(p,compact)
                assert 0 not in e and decode(e)[0]==p
                assert len(e)==formula(p,compact)
            small_count+=1
    rng=random.Random(2026102518)
    for trial in range(1200):
        n=rng.randrange(0,2200)
        p=bytes(rng.randrange(256) for _ in range(n))
        for compact in [False,True]:
            e,_=encode(p,compact)
            assert decode(e)[0]==p and 0 not in e
            assert len(e)==formula(p,compact)
            upper=n+1+n//254 if not compact else n+max(1,(n+253)//254)
            assert len(e)<=upper
    for n in range(1025):
        for p in [bytes(n),bytes([85])*n]:
            for compact in [False,True]:
                e,_=encode(p,compact)
                assert len(e)==formula(p,compact) and decode(e)[0]==p
    split_count=0
    for mask in range(1<<(len(frame)-1)):
        r=Receiver();start=0
        for i in range(1,len(frame)):
            if mask & (1<<(i-1)):
                r.feed(frame[start:i]);start=i
        r.feed(frame[start:])
        assert r.packets==[list(payload)] and not r.buffer
        split_count+=1
    stream=frame+encode(b'')[0]+b'\0'
    sizes=[2,3,1,5,1]
    r=Receiver();chunks=[];pos=0
    for size in sizes:
        chunks.append(r.feed(stream[pos:pos+size]));pos+=size
    assert pos==len(stream) and r.packets==[list(payload),[]]
    errors=[]
    changed=bytearray(encoded);changed[1]^=1
    badcode=bytearray(encoded);badcode[0]=0x0B
    for name,data in [('data_flip',bytes(changed)),('bad_code',bytes(badcode)),('zero_inside',b'\x02\0')]:
        try:
            d,t=decode(data,True);errors.append(dict(name=name,input=list(data),accepted=True,output=list(d),codes=[x['start'] for x in t]))
        except ValueError as exc:errors.append(dict(name=name,input=list(data),accepted=False,error=str(exc),codes=[0]))
    lost_delimiter=encoded+encode(b'')[0]+b'\0'+encode(bytes([0x66]))[0]+b'\0'
    r=Receiver();lost=r.feed(lost_delimiter)
    lost['first_codes']=[x['start'] for x in decode(lost_delimiter.split(b'\0')[0],True)[1]]
    assert lost['packets'][-1]==[0x66]
    r=Receiver(maximum=4);overflow=r.feed(b'\x55'*6+b'\0'+encode(b'\x66')[0]+b'\0')
    assert overflow['packets']==[[0x66]] and overflow['errors']==['frame too long']
    r=Receiver(synchronized=False);sync=r.feed(frame[4:]+encode(b'\x66')[0]+b'\0')
    assert sync['packets']==[[0x66]]
    budget=[]
    for n in [0,8,254,255,508,1000,1500]:
        budget.append(dict(n=n,plain_upper=n+1+n//254,
                           compact_upper=n+max(1,(n+253)//254)))
    result=dict(payload=list(payload),encoded=list(encoded),frame=list(frame),
        input_groups=[list(x) for x in payload.split(b'\0')],enc_trace=enc_trace,
        dec_trace=dec_trace,tiny=tiny,boundaries=boundaries,after_full_zero=after_full_zero,
        chunks=chunks,stream=list(stream),errors=errors,lost_delimiter=lost,
        overflow=overflow,sync=sync,budget=budget,
        checks=dict(exhaustive_payloads=small_count,random_payloads=1200,
        random_seed=2026102518,boundary_lengths=1025,all_frame_partitions=split_count))
    return result

if __name__=='__main__':
    r=run();(ROOT/'results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'environment.json').write_text(json.dumps(dict(python=sys.version.split()[0]),indent=2)+'\n')
    print('input:',hexbytes(r['payload']))
    print('encoded:',hexbytes(r['encoded']))
    print('checks:',r['checks'])
