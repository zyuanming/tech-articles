#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile only the accompanying original examples; use installed GNU tools.
Run: python3 reproduce.py --out /path/to/new-output-directory
The output directory contains binaries, full command transcripts, and results.
No downloads, package installation, network operations, or system changes.
"""
import argparse, hashlib, json, os, platform, shutil, struct, subprocess
from pathlib import Path

SRC = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
if any(out.iterdir()):
    raise SystemExit('Choose an empty output directory; existing files are never removed.')
if platform.system() != 'Linux' or platform.machine() != 'x86_64':
    raise SystemExit('This exact executable experiment requires Linux x86_64.')
for name in ['as','gcc','ld','readelf','objdump']:
    if not shutil.which(name): raise SystemExit('Missing installed tool: '+name)
for name in ['start.s','answer.c','padding.s','caller.c']:
    shutil.copy2(SRC/name, out/name)
(out/'raw').mkdir()
env = dict(os.environ, LC_ALL='C', LANG='C', SOURCE_DATE_EPOCH='1791849600')
transcript=[]
def run(tag, cmd, expected=0):
    cp = subprocess.run(cmd, cwd=out, env=env, text=True, capture_output=True)
    record={'command':cmd,'exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
    transcript.append(record)
    (out/'raw'/f'{tag}.txt').write_text('$ '+' '.join(cmd)+'\n'+cp.stdout+cp.stderr+'\n[exit_code='+str(cp.returncode)+']\n')
    if expected is not None and cp.returncode != expected:
        raise RuntimeError(f'{tag}: expected {expected}, got {cp.returncode}: {cp.stderr}')
    return cp

versions={n:run('version-'+n,[n,'--version']).stdout.splitlines()[0] for n in ['as','gcc','ld','readelf','objdump']}
flags=['-c','-O1','-fno-pie','-fno-asynchronous-unwind-tables','-fno-stack-protector','-fcf-protection=none']
run('assemble-start',['as','--64','start.s','-o','start.o'])
run('compile-answer',['gcc',*flags,'answer.c','-o','answer.o'])
run('compile-caller',['gcc',*flags,'caller.c','-o','caller.o'])
run('assemble-padding',['as','--64','padding.s','-o','padding.o'])
base=['ld','-m','elf_x86_64','-static','-e','_start','--build-id=none']
configs={'normal':('0x401000',['start.o','answer.o']),
         'padded':('0x401000',['start.o','padding.o','answer.o']),
         'shifted':('0x501000',['start.o','answer.o']),
         'reversed':('0x401000',['answer.o','start.o'])}
for label,(address,objects) in configs.items():
    run('link-'+label,[*base,'-Ttext='+address,*objects,'-o',label])
    run('execute-'+label,['./'+label],42)
observed=run('observed-shell',['sh','-c','./normal; echo $?'])
assert observed.stdout == '42\n'
missing=run('link-missing',[*base,'-Ttext=0x401000','start.o','-o','missing'],None)
duplicate=run('link-duplicate',[*base,'-Ttext=0x401000','start.o','answer.o','answer.o','-o','duplicate'],None)
assert missing.returncode != 0 and 'undefined reference' in missing.stderr
assert duplicate.returncode != 0 and 'multiple definition' in duplicate.stderr
for f in ['start.o','answer.o','caller.o',*configs]:
    for opt,tag in [('-hW','header'),('-SW','sections'),('-sW','symbols'),('-rW','relocations'),('-lW','segments')]:
        run(f'{f}-{tag}',['readelf',opt,f])
    run(f'{f}-disassembly',['objdump','-drw',f])

# Parse ELF64 independently of readelf/objdump to check the actual bytes.
def elf(path):
    b=path.read_bytes()
    assert b[:6] == b'\x7fELF\x02\x01'
    h=struct.unpack_from('<HHIQQQIHHHHHH',b,16)
    typ,machine,_,entry,phoff,shoff,_,_,phentsize,phnum,shentsize,shnum,shstr=h
    assert machine == 62
    sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shentsize) for i in range(shnum)]
    strings=b[sections[shstr][4]:sections[shstr][4]+sections[shstr][5]]
    z=lambda data,i:data[i:data.index(b'\0',i)].decode()
    names={z(strings,s[0]):i for i,s in enumerate(sections)}
    textsec=sections[names['.text']]
    symsec=sections[names['.symtab']]; strsec=sections[symsec[6]]
    symstr=b[strsec[4]:strsec[4]+strsec[5]]
    syms={};ordered=[]
    for off in range(symsec[4],symsec[4]+symsec[5],symsec[9]):
        n,info,other,ndx,value,size=struct.unpack_from('<IBBHQQ',b,off)
        item={'name':z(symstr,n),'value':value,'size':size,'section_index':ndx,'binding':info>>4,'type':info&15}
        ordered.append(item);syms[item['name']]=item
    rel=[]
    if '.rela.text' in names:
        sec=sections[names['.rela.text']]
        for off in range(sec[4],sec[4]+sec[5],sec[9]):
            ro,ri,ra=struct.unpack_from('<QQq',b,off)
            rel.append({'offset':ro,'symbol_index':ri>>32,'type':ri&0xffffffff,'addend':ra,'symbol':ordered[ri>>32]['name']})
    ph=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*phentsize)[0] for i in range(phnum)]
    return {'bytes':b,'type':typ,'entry':entry,'text_address':textsec[3],'text_file_offset':textsec[4],
            'text_bytes':b[textsec[4]:textsec[4]+textsec[5]],'symbols':syms,'relocations':rel,
            'has_interp':3 in ph,'sections':list(names)}

obj=elf(out/'start.o'); ans=elf(out/'answer.o')
assert obj['type']==1 and len(obj['text_bytes'])==14 and len(ans['text_bytes'])==6
assert obj['text_bytes'][:5].hex(' ') == 'e8 00 00 00 00'
assert obj['relocations'] == [{'offset':1,'symbol_index':2,'type':4,'addend':-4,'symbol':'answer'}]
assert obj['symbols']['answer']['section_index']==0
assert obj['text_file_offset']==64
results={'platform':'Linux x86-64 / ELF64 little endian','versions':versions,
         'source_flags':flags,
         'input':{'start_text_hex':obj['text_bytes'].hex(' '),'start_text_size':len(obj['text_bytes']),
                  'answer_text_hex':ans['text_bytes'].hex(' '),'answer_text_size':len(ans['text_bytes']),
                  'text_file_offset':obj['text_file_offset'],'patch_file_offset':obj['text_file_offset']+1,
                  'relocations':obj['relocations'],'symbols_start':[obj['symbols'][k] for k in ['_start','answer']],
                  'symbols_answer':[ans['symbols']['answer']]},'builds':{},
         'errors':{'missing_exit':missing.returncode,'missing_stderr':missing.stderr,'duplicate_exit':duplicate.returncode,'duplicate_stderr':duplicate.stderr}}
for label in configs:
    e=elf(out/label); start=e['symbols']['_start']['value']; target=e['symbols']['answer']['value']
    offset=start-e['text_address']; call=e['text_bytes'][offset:offset+5]
    assert call[0]==0xe8
    disp=struct.unpack('<i',call[1:])[0];p=start+1;nextip=start+5
    assert nextip+disp == target and target-4-p == disp
    assert e['type']==2 and not e['has_interp'] and not e['relocations']
    assert '.plt' not in e['sections']
    results['builds'][label]={'start':start,'target':target,'P':p,'next_instruction':nextip,'addend':-4,
      'displacement':disp,'call_bytes':call.hex(' '),'text_size':len(e['text_bytes']),
      'text_file_offset':e['text_file_offset'],'patch_file_offset':e['text_file_offset']+offset+1,
      'has_interp':e['has_interp'],'has_plt':False,'remaining_text_relocations':0,'exit_code':42}
assert [results['builds'][k]['displacement'] for k in configs] == [9,25,9,-11]
results['tests']={'build_variants':4,'all_exit_42':True,'independent_ELF_byte_checks':True,'missing_and_duplicate_failures':True}
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
(out/'transcript.json').write_text(json.dumps(transcript,ensure_ascii=False,indent=2)+'\n')
(out/'binary-sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name in ['start.o','answer.o','caller.o','normal','padded','shifted','reversed']},indent=2)+'\n')
print('PASS: four linked programs return 42; displacements 9, 25, 9, -11; two expected link failures; ELF bytes independently verified.')
