"""In-memory authority model; NOT a Python sandbox or filesystem security tool.
The broker and caller identity are assumed trusted. Calls are sequential.
who is supplied by the test driver to stand for trusted caller context; this
model does NOT authenticate it. An untrusted client allowed to choose who can
impersonate another principal. Real systems must derive it from protected context.
Original code MIT.
"""
from pathlib import Path
from dataclasses import dataclass
import json
@dataclass(frozen=True)
class Entry:
 target:str
 rights:frozenset
class Broker:
 def __init__(self):
  self.objects={'photo':'pixels','output':'','stats':'0','bill':'paid'};self.tables={};self.gates={}
 def grant(self,who,slot,target,rights):
  assert target in self.objects
  self.tables.setdefault(who,{})[slot]=Entry(target,frozenset(rights))
 def use(self,who,slot,op,data=''):
  e=self.tables.get(who,{}).get(slot)
  if e is None or op not in e.rights:raise PermissionError('not held or right missing')
  if op=='read':return self.objects[e.target]
  if op=='write':self.objects[e.target]=data;return True
  raise PermissionError('unsupported operation')
 def derive(self,who,slot,dest,newslot,rights):
  e=self.tables[who][slot];r=frozenset(rights)
  if not r<=e.rights:raise PermissionError('cannot widen')
  self.grant(dest,newslot,e.target,r)
 def proxy(self,name,who,slot):self.gates[name]=[True,who,slot]
 def via_proxy(self,name,op,data=''):
  live,who,slot=self.gates[name]
  if not live:raise PermissionError('revoked')
  return self.use(who,slot,op,data)
def attempt(fn):
 try:fn();return '允许'
 except PermissionError:return '拒绝'
def main():
 b=Broker();b.grant('convert',3,'photo',{'read'});b.grant('convert',4,'output',{'write'});b.grant('meter',3,'stats',{'write'})
 tests=[['读照片',attempt(lambda:b.use('convert',3,'read'))],['改照片',attempt(lambda:b.use('convert',3,'write','x'))],['写输出',attempt(lambda:b.use('convert',4,'write','thumbnail'))],['猜账本槽',attempt(lambda:b.use('convert',9,'write','oops'))],['增加权利',attempt(lambda:b.derive('convert',3,'helper',3,{'read','write'}))]]
 assert tests==[['读照片','允许'],['改照片','拒绝'],['写输出','允许'],['猜账本槽','拒绝'],['增加权利','拒绝']]
 assert b.objects['bill']=='paid'
 b.derive('convert',4,'copy',6,{'write'});b.proxy('gate','convert',4)
 before=attempt(lambda:b.via_proxy('gate','write','before'));b.gates['gate'][0]=False
 after=attempt(lambda:b.via_proxy('gate','write','after'));direct=attempt(lambda:b.use('copy',6,'write','direct'))
 assert (before,after,direct)==('允许','拒绝','允许')
 d={'tests':tests,'slots':[['转换器',3,'照片','读'],['转换器',4,'输出','写'],['计量器',3,'统计','写']],'revoke':[['撤销前经门',before],['撤销后经门',after],['已给直达权',direct]],'bill':b.objects['bill']}
 Path(__file__).with_name('results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False))
if __name__=='__main__':main()
