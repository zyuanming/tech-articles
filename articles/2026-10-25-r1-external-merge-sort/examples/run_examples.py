"""Actually run file experiments and export reproducible numbers. CC0-1.0."""
from pathlib import Path
import tempfile,random,json,hashlib,platform,math
from itertools import product
from external_sort import *
ROOT=Path(__file__).resolve().parent

def run(keys,chunk=6,block=2,fan=3,trace=False):
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);src=p/'input.bin';write_input(src,keys)
        result,data=external_sort(src,p/'runs',chunk,block,fan,trace)
        got=read_records(result);expected=sorted((k,i) for i,k in enumerate(keys));assert got==expected
        data.update(output=got,input_bytes=src.stat().st_size,output_bytes=result.stat().st_size,output_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
        return data

def main():
    data=run(KEYS,trace=True);data['keys']=KEYS
    data['config']=dict(record_bytes=RECORD.size,block_records=2,chunk_records=6,fan_in=3,data_buffer_blocks=4)
    data['python']=platform.python_version()
    assert [x['run_count'] for x in data['phases']]==[4,2,1]
    assert all(x['read_blocks']==x['write_blocks']==12 for x in data['phases'])
    data['total_blocks']=sum(x['read_blocks']+x['write_blocks'] for x in data['phases'])
    data['logical_bytes']=sum(x['read_bytes']+x['write_bytes'] for x in data['phases'])
    data['fan_comparison']=[]
    for fan in [2,3,4]:
        x=run(KEYS,fan=fan);data['fan_comparison'].append(dict(fan=fan,buffer_blocks=fan+1,passes=len(x['phases'])-1,blocks=sum(z['read_blocks']+z['write_blocks'] for z in x['phases']),counts=[z['run_count'] for z in x['phases']]))
    checked=0
    for n in range(6):
        for keys in product(range(3),repeat=n):run(list(keys),chunk=2,block=2,fan=2);checked+=1
    rng=random.Random(20261025)
    for n in range(1,82):run([rng.randrange(7) for _ in range(n)],chunk=5,block=3,fan=3);checked+=1
    large_rng=random.Random(20261025)
    bigkeys=[large_rng.randrange(1000) for _ in range(10000)]
    large=run(bigkeys,chunk=256,block=32,fan=8)
    data['large']={k:v for k,v in large.items() if k not in ['output','initial','merges']};data['large'].update(n=len(bigkeys),chunk=256,block=32,fan=8,seed=20261025)
    data['checks']=dict(file_cases=checked,large_cases=1)
    data['partial']=run([5,1,4,0,3],chunk=3,block=2,fan=2,trace=True)
    data['stable']=[list(x) for x in data['output'] if x[0] in [2,3,4,5,9]]
    data['concat_boundary']=[data['initial'][0]['sorted'][-1][0],data['initial'][1]['sorted'][0][0]]
    (ROOT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'phases':data['phases'],'blocks':data['total_blocks'],'bytes':data['logical_bytes'],'large':data['large'],'checks':data['checks']},ensure_ascii=False))
if __name__=='__main__':main()
