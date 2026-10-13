# Original teaching data reader. MIT license: ../licenses/Example-Code-MIT.txt
from pathlib import Path
import struct,collections,json

def parse(path):
 b=Path(path).read_bytes();magic,n,d=struct.unpack_from('<4sii',b);assert magic in (b'PWAD',b'IWAD');l={}
 for i in range(n):
  o,z,k=struct.unpack_from('<ii8s',b,d+16*i);assert 0<=o<=len(b) and 0<=z<=len(b)-o;l[k.rstrip(b'\0').decode()]=b[o:o+z]
 def records(name,fmt):
  assert len(l[name])%struct.calcsize(fmt)==0;return list(struct.iter_unpack(fmt,l[name]))
 return {'vertices':records('VERTEXES','<2h'),'lines':records('LINEDEFS','<7H'),'segs':records('SEGS','<6H'),'subsectors':records('SSECTORS','<2H'),'nodes':records('NODES','<12h2H'),'sectors':records('SECTORS','<2h8s8shhh'),'things':records('THINGS','<5h')}

def summarize(m):
 nodes=m['nodes'];root=len(nodes)-1;seen_n=set();seen_s=set()
 def walk(ref):
  if ref&0x8000:
   ss=ref&0x7fff;assert ss<len(m['subsectors']);assert ss not in seen_s;seen_s.add(ss);return (0,1)
  assert ref<len(nodes) and ref not in seen_n;seen_n.add(ref);a=walk(nodes[ref][-2]);b=walk(nodes[ref][-1]);return(1+a[0]+b[0],a[1]+b[1])
 counts=walk(root);assert counts==(len(nodes),len(m['subsectors']))
 for count,first in m['subsectors']:assert first+count<=len(m['segs'])
 assert sum(x[0] for x in m['subsectors'])==len(m['segs'])
 def count(ref):
  if ref&32768:return 0,1
  a=count(nodes[ref][-2]);b=count(nodes[ref][-1]);return 1+a[0]+b[0],a[1]+b[1]
 v=m['vertices'];line=539;segs=[(i,s) for i,s in enumerate(m['segs']) if s[3]==line and s[4]==0]
 pair=m['lines'][line][:2]
 return {'counts':{k:len(val) for k,val in m.items()},'root_index':root,'root':nodes[root],'root_child_descendants':[count(c) for c in nodes[root][-2:]],'player_starts':[x for x in m['things'] if x[3]==1],'real_split_example':{'linedef':line,'side':0,'from':v[pair[0]],'to':v[pair[1]],'segs':[{'index':i,'from':v[s[0]],'to':v[s[1]]} for i,s in segs]},'all_nodes_and_subsectors_reachable_exactly_once':True}
if __name__=='__main__':
 path=Path(__file__).with_name('freedoom-map01.wad')
 print(json.dumps(summarize(parse(path)),ensure_ascii=False,indent=2))
