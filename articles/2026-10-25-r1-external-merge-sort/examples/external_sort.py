"""Original binary-file external merge teaching implementation. CC0-1.0.
Counters measure nonempty application block transfers, never physical disk I/O.
"""
from pathlib import Path
import struct, heapq
RECORD=struct.Struct('<II')
KEYS=[17,4,9,1,12,4,8,3,15,2,11,6,14,5,10,0,7,13,9,2,16,5,18,3]

def write_input(path, keys):
    with Path(path).open('xb') as f:
        for pos,key in enumerate(keys):f.write(RECORD.pack(key,pos))

def read_records(path):
    data=Path(path).read_bytes()
    if len(data)%RECORD.size:raise ValueError('partial record')
    return list(RECORD.iter_unpack(data))

class Reader:
    def __init__(self,path,block,stats,events=None):
        self.file=Path(path).open('rb');self.name=Path(path).name
        self.block=block;self.stats=stats;self.events=events
        self.buffer=[];self.index=0;self.eof=False
    def next(self):
        if self.index==len(self.buffer):
            data=self.file.read(self.block*RECORD.size)
            if len(data)%RECORD.size:raise ValueError('partial record')
            if not data:self.eof=True;return None
            self.stats['read_blocks']+=1;self.stats['read_bytes']+=len(data)
            self.buffer=list(RECORD.iter_unpack(data));self.index=0
            if self.events is not None:self.events.append(dict(kind='read',file=self.name,records=self.buffer.copy()))
        result=self.buffer[self.index];self.index+=1;return result
    def close(self):self.file.close()

class Writer:
    def __init__(self,path,block,stats,events=None):
        self.file=Path(path).open('xb');self.name=Path(path).name
        self.block=block;self.stats=stats;self.events=events;self.buffer=[]
    def put(self,record):
        self.buffer.append(record)
        if len(self.buffer)==self.block:self.flush()
    def flush(self):
        if not self.buffer:return
        data=b''.join(RECORD.pack(*r) for r in self.buffer)
        self.file.write(data);self.stats['write_blocks']+=1;self.stats['write_bytes']+=len(data)
        if self.events is not None:self.events.append(dict(kind='write',file=self.name,records=self.buffer.copy()))
        self.buffer.clear()
    def close(self):self.flush();self.file.close()

def counts():return dict(read_blocks=0,write_blocks=0,read_bytes=0,write_bytes=0)

def merge_group(paths,out,block,stats,trace=False):
    events=[] if trace else None;readers=[];writer=None;steps=[];emitted=[]
    try:
        for p in paths:readers.append(Reader(p,block,stats,events))
        writer=Writer(out,block,stats,events);heap=[]
        for i,r in enumerate(readers):
            rec=r.next()
            if rec is not None:heapq.heappush(heap,(rec,i))
        while heap:
            if trace:before=[dict(run=i,record=list(rec)) for rec,i in heap]
            rec,i=heapq.heappop(heap);writer.put(rec)
            if trace:emitted.append(rec)
            nxt=readers[i].next()
            if nxt is not None:heapq.heappush(heap,(nxt,i))
            if trace:steps.append(dict(heap_before=before,chosen=list(rec),run=i,heap_after=[dict(run=j,record=list(v)) for v,j in heap],output_buffer=writer.buffer.copy(),remaining=[r.buffer[r.index:] for r in readers]))
        writer.close();writer=None
    finally:
        if writer is not None:writer.file.close()
        for r in readers:r.close()
    return dict(inputs=[Path(p).name for p in paths],output=Path(out).name,steps=steps,events=events,records=emitted) if trace else None

def external_sort(input_path,work_dir,chunk_records=6,block_records=2,fan_in=3,trace=False):
    if any(type(x) is not int for x in [chunk_records,block_records,fan_in]):raise ValueError('integer parameters required')
    if chunk_records<1 or block_records<1 or fan_in<2:raise ValueError('positive chunk/block and fan-in >=2 required')
    work=Path(work_dir);work.mkdir(parents=True,exist_ok=True)
    if any(work.iterdir()):raise ValueError('work directory must be empty')
    phases=[];stat=counts();runs=[];initial=[];reader=Reader(input_path,block_records,stat)
    try:
        while True:
            chunk=[]
            for _ in range(chunk_records):
                rec=reader.next()
                if rec is None:break
                chunk.append(rec)
            if not chunk:break
            original=chunk.copy() if trace else None;chunk.sort()
            path=work/f'p0-r{len(runs)}.bin';writer=Writer(path,block_records,stat)
            try:
                for rec in chunk:writer.put(rec)
            finally:writer.close()
            runs.append(path)
            if trace:initial.append(dict(file=path.name,input=original,sorted=chunk.copy(),bytes=path.stat().st_size))
    finally:reader.close()
    phases.append(dict(phase=0,run_count=len(runs),**stat))
    if not runs:
        final=work/'empty.bin';final.touch();return final,dict(phases=phases,initial=initial,merges=[])
    merges=[];level=0
    while len(runs)>1:
        level+=1;stat=counts();new=[]
        for start in range(0,len(runs),fan_in):
            out=work/f'p{level}-r{len(new)}.bin'
            detail=merge_group(runs[start:start+fan_in],out,block_records,stat,trace)
            if trace:detail['phase']=level;merges.append(detail)
            new.append(out)
        runs=new;phases.append(dict(phase=level,run_count=len(runs),**stat))
    return runs[0],dict(phases=phases,initial=initial,merges=merges)
