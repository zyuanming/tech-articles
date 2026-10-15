"""Original educational rsync-like delta model, not the rsync program/protocol.
MIT. Standard library only. Fixed full blocks; partial basis tail always literal.
Strong digest SHA-256; unsigned-byte rolling sum, M=65536, no rsync checksum seed.
"""
from pathlib import Path
import hashlib,json,struct,random,platform,gzip
HERE=Path(__file__).resolve().parent;MOD=65536

def weak(block):
    a=sum(block)%MOD;b=sum((len(block)-i)*x for i,x in enumerate(block))%MOD
    return a,b

def roll(a,b,outgoing,incoming,size):
    a=(a-outgoing+incoming)%MOD;b=(b-size*outgoing+a)%MOD
    return a,b

def packweak(pair):return pair[0]+65536*pair[1]
def digest(b):return hashlib.sha256(b).hexdigest()

def signatures(basis,size):
    if not 1<=size<2**32:raise ValueError('bad block size')
    return [{'index':i//size,'weak':packweak(weak(basis[i:i+size])),'strong':digest(basis[i:i+size])} for i in range(0,len(basis)-size+1,size)]

def delta(target,signature,size):
    # Sender receives signatures, never the basis file.
    lookup={}
    for entry in signature:lookup.setdefault(entry['weak'],[]).append(entry)
    ops=[];literal=bytearray();offset=0;pair=None;stats={'windows':0,'rolling_updates':0,'weak_hits':0,'strong_checks':0,'strong_rejects':0,'copied_bytes':0,'literal_bytes':0};trace=[]
    def flush():
        if literal:ops.append({'op':'DATA','hex':bytes(literal).hex()});literal.clear()
    while offset+size<=len(target):
        if pair is None:pair=weak(target[offset:offset+size])
        stats['windows']+=1;key=packweak(pair);candidates=lookup.get(key,[]);found=None
        if candidates:
            stats['weak_hits']+=1;stats['strong_checks']+=1;strong=digest(target[offset:offset+size])
            found=next((x for x in candidates if x['strong']==strong),None)
            if found is None:stats['strong_rejects']+=1
        if len(trace)<24:trace.append({'offset':offset,'window_hex':target[offset:offset+size].hex(),'a':pair[0],'b':pair[1],'weak_hit':bool(candidates),'match_index':None if found is None else found['index']})
        if found is not None:
            flush();ops.append({'op':'COPY','index':found['index']});stats['copied_bytes']+=size;offset+=size;pair=None
        else:
            literal.append(target[offset]);stats['literal_bytes']+=1
            if offset+size<len(target):pair=roll(*pair,target[offset],target[offset+size],size);stats['rolling_updates']+=1
            offset+=1
    tail=target[offset:];literal.extend(tail);stats['literal_bytes']+=len(tail);flush()
    return {'target_length':len(target),'target_sha256':digest(target),'size':size,'ops':ops,'stats':stats,'trace':trace}

def reconstruct(basis,packet):
    out=bytearray();size=packet['size']
    for op in packet['ops']:
        if op['op']=='DATA':out.extend(bytes.fromhex(op['hex']))
        elif op['op']=='COPY':
            start=op['index']*size;block=basis[start:start+size]
            if len(block)!=size:raise ValueError('invalid block reference')
            out.extend(block)
        else:raise ValueError('unknown operation')
    out=bytes(out)
    if len(out)!=packet['target_length'] or digest(out)!=packet['target_sha256']:raise ValueError('reconstruction verification failed')
    return out

def signature_wire(signature,size):
    return b'SG1'+struct.pack('>II',size,len(signature))+b''.join(struct.pack('>II',s['index'],s['weak'])+bytes.fromhex(s['strong']) for s in signature)

def delta_wire(packet):
    # Exact illustrative wire format; not compatible with actual rsync.
    data=b'DL1'+struct.pack('>Q',packet['target_length'])+bytes.fromhex(packet['target_sha256'])+struct.pack('>I',len(packet['ops']))
    for op in packet['ops']:
        if op['op']=='COPY':data+=b'C'+struct.pack('>I',op['index'])
        else:
            b=bytes.fromhex(op['hex']);data+=b'D'+struct.pack('>I',len(b))+b
    return data

def case(name,basis,target,size,keep=False):
    signature=signatures(basis,size);packet=delta(target,signature,size);rebuilt=reconstruct(basis,packet);assert rebuilt==target
    sw=signature_wire(signature,size);dw=delta_wire(packet)
    out={'name':name,'basis_bytes':len(basis),'target_bytes':len(target),'block_size':size,'signature_blocks':len(signature),'signature_bytes':len(sw),'delta_bytes':len(dw),'two_way_bytes':len(sw)+len(dw),'reconstructed_exact':True,'basis_sha256':digest(basis),'target_sha256':digest(target),'stats':packet['stats'],'ops_count':len(packet['ops']),'trace':packet['trace']}
    if keep:
        out['signatures']=signature;out['ops']=packet['ops'];(HERE/f'{name}.signature.bin').write_bytes(sw);(HERE/f'{name}.delta.bin').write_bytes(dw)
    return out

def make_image():
    # Original deterministic RGB byte test pattern; an sRGB-like PPM variant.
    rng=random.Random(20261013);w,h=96,64;data=bytearray()
    for y in range(h):
        for x in range(w):
            if (x-70)**2+(y-18)**2<9**2:base=(232,192,91)
            elif y>46+int(7*__import__('math').sin(x/12)):base=(33+x,85+y,78+x//3)
            else:base=(25+y,44+y,93+x//2)
            data.extend(max(0,min(255,v+rng.randrange(-3,4))) for v in base)
    header=f'P6\n{w} {h}\n255\n'.encode();basis=header+data;target=basis[:3]+b'\n'+basis[3:]
    (HERE/'landscape-old.ppm').write_bytes(basis);(HERE/'landscape-new.ppm').write_bytes(target)
    return basis,target

def tests():
    rng=random.Random(1618033);checks=0
    for size in (1,2,4,8,31,256):
        b=bytes(rng.randrange(256) for _ in range(size+500));pair=weak(b[:size])
        for i in range(500):pair=roll(*pair,b[i],b[i+size],size);assert pair==weak(b[i+1:i+1+size]);checks+=1
    for _ in range(500):
        old=bytes(rng.randrange(256) for _ in range(rng.randrange(0,150)));pos=rng.randrange(len(old)+1);new=old[:pos]+bytes(rng.randrange(256) for _ in range(rng.randrange(0,20)))+old[pos:];size=rng.randrange(1,25);p=delta(new,signatures(old,size),size);assert reconstruct(old,p)==new
    # Exhaust small binary strings, including empty, full match and partial tails.
    from itertools import product
    strings=[bytes(x) for n in range(6) for x in product((0,1),repeat=n)];pairs=0
    for old in strings:
        for new in strings:
            for size in (1,2,4):assert reconstruct(old,delta(new,signatures(old,size),size))==new;pairs+=1
    assert weak(b'ABCD')==weak(b'B@DD')==(266,660);assert digest(b'ABCD')!=digest(b'B@DD')
    bad=delta(b'B@DD',signatures(b'ABCD',4),4);assert bad['stats']['strong_rejects']==1 and bad['stats']['copied_bytes']==0
    p=delta(b'AAAABBBB',signatures(b'AAAABBBB',4),4)
    try:reconstruct(b'ZAAABBBB',p)
    except ValueError:pass
    else:raise AssertionError('tampered basis not detected')
    return {'rolling_vs_full_recalculations':checks,'random_insert_cases':500,'exhaustive_binary_string_pairs_and_block_sizes':pairs,'weak_collision_rejected':True,'tampered_basis_rejected':True}

def run():
    basis,target=make_image();result={'python':platform.python_version(),'model':'unsigned rolling checksum plus SHA-256; full fixed blocks only; educational custom wire format, NOT rsync binary','seed_image':20261013,'tests':tests()}
    result['toy']=case('toy',b'AAAABBBBCCCCDDDD',b'XAAAABBBBCCCCDDDD',4,True)
    result['collision']=case('collision',b'ABCD',b'B@DD',4)
    result['image']=case('image',basis,target,256,True)
    result['block_sizes']=[case('image-size-'+str(s),basis,target,s) for s in [16,32,64,128,256,512,1024,2048]]
    result['reorder']=case('reorder',b'AAAABBBBCCCCDDDD',b'CCCCAAAADDDDBBBB',4,True)
    oldgz=gzip.compress(basis,mtime=0);newgz=gzip.compress(target,mtime=0)
    result['gzip']=case('gzip',oldgz,newgz,256);result['gzip']['gzip_note']='same compressor, only header newline changed in source; outcome specific to this input, not all compressed files'
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'tests':result['tests'],'image':{k:v for k,v in result['image'].items() if k not in ('trace','signatures','ops')},'blocks':[(r['block_size'],r['two_way_bytes'],r['stats']['literal_bytes']) for r in result['block_sizes']]},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
