"""CC BY 4.0. Execute only the supplied original toy program, no downloaded code."""
from pathlib import Path
import contextlib,io,json,subprocess,sys
from tiny_lit import parse,tangle,weave
base=Path(__file__).resolve().parent
parts,chunks=parse((base/'positive.lit').read_text());code=tangle(chunks)
(base/'generated.py').write_text(code);(base/'generated.html').write_text(weave(parts))
stdout=subprocess.check_output([sys.executable,str(base/'generated.py')],text=True)
assert stdout=='8\n'
namespace={}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,'generated.py','exec'),namespace)
tests=[]
for inputs,want in [([],0),([-5,-1],0),([3,-2,5,0],8),([1,2,3],6),([0],0)]:
    got=namespace['sum_positive'](inputs);assert got==want;tests.append(dict(input=inputs,expected=want,actual=got))
errors={}
for label,sample in [('missing',{'主程序':['<<不存在>>']}),('cycle',{'主程序':['<<A>>'],'A':['<<主程序>>']})]:
    try:tangle(sample)
    except ValueError as e:errors[label]=str(e)
    else:raise AssertionError(label)
# A prose explanation does not catch this edit by itself; the example test does.
broken=code.replace('total += value','total = value');ns={}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(broken,'broken-demo','exec'),ns)
wrong=ns['sum_positive']([3,-2,5,0]);assert wrong==5
trace=[];total=0
for value in [3,-2,5,0]:
    before=total
    if value>0:total+=value
    trace.append(dict(value=value,before=before,after=total))
d=dict(stdout=stdout,tests=tests,errors=errors,trace=trace,broken_result=wrong,presentation_order=list(chunks),expanded_lines=code.splitlines(),python_version=sys.version.split()[0])
(base/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('PASS: stdout=8; five cases; missing/cycle errors; faulty edit produces5')
