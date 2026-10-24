"""Harmless finite artifact model. Does NOT compile machine code or implement a self-hosting compiler.
All artifacts are inert dictionaries; a visible marker is the only deviation. CC BY 4.0.
"""
from pathlib import Path
import json,hashlib,platform
APP={'kind':'application','text':'HELLO'}
SRC={'kind':'compiler-source','specified_marker':False}
def build(source,tool):
 if source['kind']=='compiler-source':
  return {'kind':'compiler','marker':source['specified_marker'] or tool['marker']}
 return {'kind':'output','text':source['text']+('*' if tool['marker'] else '')}
clean={'kind':'compiler','marker':False};marked={'kind':'compiler','marker':True}
chain=[];tool=marked
for gen in range(4):
 chain.append({'generation':gen,'tool':tool.copy(),'source':SRC.copy(),'output':build(APP,tool)['text']})
 tool=build(SRC,tool)
assert all(x['output']=='HELLO*' for x in chain)
assert build(APP,clean)['text']=='HELLO'
assert build(SRC,marked)==marked
intermediate=build(SRC,clean);reference=build(SRC,intermediate)
assert reference==clean and reference!=marked
D={'application':APP,'compiler_source':SRC,'normal':build(APP,clean),'marked':build(APP,marked),'generations':chain,'reference':reference,'candidate':marked,'repeatable':build(SRC,marked)==build(SRC,marked),'matches_source':reference==marked,'source_sha256':hashlib.sha256(json.dumps(SRC,sort_keys=True).encode()).hexdigest(),'python':platform.python_version()}
Path(__file__).with_name('results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');print('Trust model: 4 generations, repeatability and independent-reference distinction passed')
