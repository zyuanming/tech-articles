"""Original MIT-licensed Pratt teaching parser, not CPython's parser.
Only ASCII integers/names, + - * / ** and grouping parentheses are supported.
No eval/exec, functions, attribute access, imports, or filesystem language features.
Running this file writes demonstration JSON and Graphviz source beside itself.
"""
from dataclasses import dataclass
from pathlib import Path
import ast,json,math,platform,random,re
HERE=Path(__file__).resolve().parent
# Strict loop condition: current right threshold < next token's left power.
# (left power, threshold used for the right argument)
BIND={'+':(10,10),'-':(10,10),'*':(20,20),'/':(20,20),'**':(30,29)}
PREFIX=25
TOKEN=re.compile(r'\s+|[0-9]+|[A-Za-z_][A-Za-z_0-9]*|\*\*|[+*/()\-]')
@dataclass(frozen=True)
class Token:
    text:str
    start:int
    end:int
    kind:str
class ParseError(ValueError):
    def __init__(self,message,position):super().__init__(message);self.position=position

def tokenize(source):
    if len(source)>3000:raise ParseError('input exceeds this example\'s 3000-character limit',3000)
    out=[];pos=0
    while pos<len(source):
        m=TOKEN.match(source,pos)
        if not m:raise ParseError('unsupported character',pos)
        text=m.group();start=pos;pos=m.end()
        if text.isspace():continue
        if text.isdigit():
            if len(text)>1 and text.startswith('0') and any(c!='0' for c in text):raise ParseError('leading zero integer is outside this grammar',start)
            kind='number'
        elif text[0].isalpha() or text[0]=='_':kind='name'
        else:kind='symbol'
        out.append(Token(text,start,pos,kind))
    out.append(Token('EOF',len(source),len(source),'end'));return out

def number(v):return {'kind':'number','value':v}
def unary(op,child):return {'kind':'unary','op':op,'child':child}
def binary(op,left,right):return {'kind':'binary','op':op,'left':left,'right':right}
def compact(node):
    k=node['kind']
    if k=='number':return str(node['value'])
    if k=='name':return node['name']
    if k=='unary':return f"({node['op']}{compact(node['child'])})"
    return f"({compact(node['left'])}{node['op']}{compact(node['right'])})"

class Parser:
    def __init__(self,source,*,trace=False,power_right=29):
        self.source=source;self.tokens=tokenize(source);self.pos=0;self.events=[];self.trace=trace;self.calls=0;self.max_depth=0;self.power_right=power_right
    def peek(self):return self.tokens[self.pos]
    def take(self):
        t=self.peek()
        if t.kind!='end':self.pos+=1
        return t
    def note(self,event,depth,rbp,left=None,**extra):
        if self.trace:self.events.append(dict(event=event,depth=depth,rbp=rbp,cursor=self.pos,next=self.peek().text,left=compact(left) if left else None,**extra))
    def prefix(self,t,depth,rbp):
        if t.kind=='number':return number(int(t.text))
        if t.kind=='name':return {'kind':'name','name':t.text}
        if t.text in ('+','-'):return unary(t.text,self.expression(PREFIX,depth+1))
        if t.text=='(':
            node=self.expression(0,depth+1)
            if self.peek().text!=')':raise ParseError('expected closing parenthesis',self.peek().start)
            self.take();return node
        raise ParseError('expected a number, name, prefix sign, or opening parenthesis',t.start)
    def infix(self,t,left,depth):
        right_threshold=self.power_right if t.text=='**' else BIND[t.text][1]
        return binary(t.text,left,self.expression(right_threshold,depth+1))
    def expression(self,rbp=0,depth=0):
        if depth>128:raise ParseError('this example limits nested parser tasks to depth 128',self.peek().start)
        self.calls+=1;self.max_depth=max(self.max_depth,depth);self.note('enter',depth,rbp)
        t=self.take();left=self.prefix(t,depth,rbp);self.note('prefix_ready',depth,rbp,left,consumed=t.text)
        while True:
            nxt=self.peek();lbp=BIND.get(nxt.text,(0,0))[0];go=rbp<lbp
            self.note('compare',depth,rbp,left,lbp=lbp,continue_loop=go)
            if not go:break
            op=self.take();self.note('take_infix',depth,rbp,left,consumed=op.text)
            left=self.infix(op,left,depth);self.note('combine',depth,rbp,left,operator=op.text)
        self.note('return',depth,rbp,left);return left
    def parse(self):
        node=self.expression()
        if self.peek().kind!='end':raise ParseError('unexpected remaining token',self.peek().start)
        return node

def evaluate(node,environment=None):
    """Small bounded demonstration evaluator. Parsing is a separate operation."""
    environment=environment or {};k=node['kind']
    if k=='number':value=node['value']
    elif k=='name':value=environment[node['name']]
    elif k=='unary':
        a=evaluate(node['child'],environment);value=a if node['op']=='+' else -a
    else:
        a=evaluate(node['left'],environment);b=evaluate(node['right'],environment);op=node['op']
        if op=='+':value=a+b
        elif op=='-':value=a-b
        elif op=='*':value=a*b
        elif op=='/':value=a/b
        else:
            if abs(b)>16:raise ValueError('demonstration exponent limit: absolute value at most 16')
            value=a**b
    if isinstance(value,complex) or abs(value)>10**12 or not math.isfinite(value):raise ValueError('demonstration numeric range exceeded')
    return value

def python_tree(source):
    """Read CPython AST without executing any input."""
    names={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/',ast.Pow:'**',ast.UAdd:'+',ast.USub:'-'}
    def conv(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return number(n.value)
        if isinstance(n,ast.Name):return {'kind':'name','name':n.id}
        if isinstance(n,ast.UnaryOp):return unary(names[type(n.op)],conv(n.operand))
        if isinstance(n,ast.BinOp):return binary(names[type(n.op)],conv(n.left),conv(n.right))
        raise ValueError(type(n).__name__)
    return conv(ast.parse(source,mode='eval').body)

def dot_tree(tree):
    lines=['digraph AST {','graph [bgcolor="white",nodesep="0.5",ranksep="0.7"];','node [shape=circle,fontname="DejaVu Sans",fontsize=28,style=filled,fillcolor="#e8f0ec",color="#244650"];','edge [color="#64867c",arrowsize=0.7];'];next_id=0
    def visit(n):
        nonlocal next_id
        i=next_id;next_id+=1;k=n['kind'];label=str(n['value']) if k=='number' else n['name'] if k=='name' else n['op'];lines.append(f'n{i} [label="{label}"];')
        children=[] if k in ('number','name') else [n['child']] if k=='unary' else [n['left'],n['right']]
        for child in children:j=visit(child);lines.append(f'n{i} -> n{j};')
        return i
    visit(tree);lines.append('}');return '\n'.join(lines)+'\n'

def tests():
    examples=['2+3*4','(2+3)*4','8-3-1','8-(3-1)','2**3**2','(2**3)**2','-2**2','(-2)**2','2**-3','2*-3','12+damage*4','3/-2','--2','1+2/3*4-5']
    for s in examples:assert Parser(s).parse()==python_tree(s),s
    rng=random.Random(314159);ops=['+','-','*','/','**']
    def expression(depth):
        if depth<=0 or rng.random()<.3:return rng.choice(['0','1','2','3','7','damage','bonus'])
        choice=rng.randrange(4)
        if choice==0:return '('+expression(depth-1)+')'
        if choice==1:return rng.choice(['+','-'])+expression(depth-1)
        return expression(depth-1)+rng.choice(ops)+expression(depth-1)
    cases=5000
    for _ in range(cases):
        s=expression(4);assert Parser(s).parse()==python_tree(s),s
    invalid=['','2+','(2+3','2+*3','2 3','2(3+4)','2 @ 3','3//2',')2(','01']
    for s in invalid:
        try:Parser(s).parse()
        except ParseError:pass
        else:raise AssertionError(s)
    for s in ['-2**2','(-2)**2','2**-3','2+3*4','(2+3)*4','8-3-1','8-(3-1)']:
        target={'-2**2':-4,'(-2)**2':4,'2**-3':.125,'2+3*4':14,'(2+3)*4':20,'8-3-1':4,'8-(3-1)':6}[s];assert evaluate(Parser(s).parse())==target
    assert compact(Parser('2**3**2').parse())=='(2**(3**2))'
    assert compact(Parser('2**3**2',power_right=30).parse())=='((2**3)**2)'
    n=Parser('8/0').parse();assert n==python_tree('8/0')
    try:evaluate(n)
    except ZeroDivisionError:pass
    else:raise AssertionError('division by zero')
    return {'curated_ast_cases':len(examples),'random_ast_cases':cases,'random_seed':314159,'invalid_cases':len(invalid),'compared_with':'CPython ast.parse 3.12; structure only; CPython parser is not this Pratt implementation','division_by_zero_parse_succeeds_evaluation_fails':True}

def run():
    out={'python':platform.python_version(),'binding':BIND,'prefix_threshold':PREFIX,'strict_loop':'rbp < lbp','tests':tests(),'cases':{},'errors':[]}
    for source in ['2+3*4','(2+3)*4','8-3-1','8-(3-1)','2**3**2','(2**3)**2','-2**2','(-2)**2','2**-3','2*-3','12+damage*4','8/0']:
        p=Parser(source,trace=True);tree=p.parse()
        try:value=evaluate(tree,{'damage':3})
        except (ValueError,ZeroDivisionError) as e:value={'error':type(e).__name__}
        out['cases'][source]={'tokens':[t.__dict__ for t in p.tokens],'tree':tree,'parenthesized':compact(tree),'value':value,'trace':p.events,'calls':p.calls,'max_depth':p.max_depth,'consumed_tokens':p.pos,'python_ast_equal':tree==python_tree(source)}
    for source in ['2+','(2+3','2+*3','2 3','2(3+4)','2 @ 3']:
        try:Parser(source).parse()
        except ParseError as e:out['errors'].append({'source':source,'position':e.position,'message':str(e)})
    out['mutated_power']={'source':'2**3**2','right_threshold':30,'tree':compact(Parser('2**3**2',power_right=30).parse()),'normal_tree':out['cases']['2**3**2']['parenthesized']}
    (HERE/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    for name,source in [('normal','2+3*4'),('grouped','(2+3)*4')]:
        tree=out['cases'][source]['tree'];(HERE/(name+'-ast.dot')).write_text(dot_tree(tree))
    (HERE/'cpython-ast.txt').write_text(ast.dump(ast.parse('2+3*4',mode='eval'),indent=2)+'\n')
    print(json.dumps({'tests':out['tests'],'cases':{s:{k:v for k,v in c.items() if k in ('parenthesized','value','calls','max_depth','consumed_tokens','python_ast_equal')} for s,c in out['cases'].items()},'errors':out['errors']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
