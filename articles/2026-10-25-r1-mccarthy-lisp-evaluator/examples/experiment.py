"""Generate all examples and traces. CC0-1.0."""
import json
from pathlib import Path
from evaluator import Pair, Evaluator, LispError, parse, show, run

ROOT = Path(__file__).resolve().parent
RECURSIVE = '''((label first
 (lambda (x)
  (cond ((atom x) x)
        (t (first (car x))))))
 '((a b) c))'''
SIMPLE = "((lambda (x y) (cons (car x) y)) '(a b) '(c))"
DYNAMIC = "((lambda (x) (f)) 'inner)"

def graph(value):
    nodes = []
    def visit(v):
        ident = len(nodes)
        node = dict(id=ident, type='pair' if isinstance(v, Pair) else 'atom')
        nodes.append(node)
        if isinstance(v, Pair):
            node['car'] = visit(v.car)
            node['cdr'] = visit(v.cdr)
        else:
            node['value'] = v
        return ident
    return dict(root=visit(value), nodes=nodes)

def record(source, env=()):
    value, machine = run(source, env)
    return dict(source=source, result=show(value), steps=machine.steps,
                events=machine.events, calls=machine.calls)

def generate():
    cases = {
        'quoted': "'(car '(a b))", 'executed': "(car '(a b))",
        'simple': SIMPLE, 'recursive': RECURSIVE,
        'safe_cond': "(cond (t 'ok) (t (car 'a)))",
        'nil_atom': '(atom nil)', 'empty_eq': "(eq nil '())",
        'eq_same': "(eq 'a 'a)", 'eq_different': "(eq 'a 'b)",
        'car': "(car '(a b))", 'cdr': "(cdr '(a b))",
        'cons': "(cons 'a '(b))", 'pair': "(cons 'a 'b)",
        'list_atom': "(atom '(a b))",
        'non_nil_truth': "(cond ('anything 'yes))",
    }
    out = {key: record(src) for key, src in cases.items()}
    out['dynamic'] = record(DYNAMIC, (('f', parse('(lambda () x)')), ('x', 'outer')))
    assert out['simple']['result'] == '(a c)'
    assert out['recursive']['result'] == 'a'
    assert out['dynamic']['result'] == 'inner'
    assert out['safe_cond']['result'] == 'ok'
    assert not any(c['expr'] == "(car (quote a))" for c in out['safe_cond']['calls'])
    errors = {
        'eager_branch': "(cons 'ok (car 'a))",
        'missing_quote': '(car (a b))',
        'unbound': 'missing', 'car_nil': '(car nil)',
        'deep_eq': "(eq '(a) '(a))", 'arity': "(car 'a 'b)",
        'no_clause': "(cond (nil 'a))",
        'loop': "((label loop (lambda (x) (loop x))) 'a)",
        'escaped_lambda': "((lambda (f) (f)) ((lambda (x) '(lambda () x)) 'gone))",
    }
    out['errors'] = []
    for key, src in errors.items():
        try:
            run(src, limit=100)
            raise AssertionError('should fail: ' + key)
        except LispError as error:
            out['errors'].append(dict(name=key, source=src, error=str(error)))
    for key in ('a', '(a b)', '((a b) c)', '(a . b)', '()'):
        assert show(parse(show(parse(key)))) == show(parse(key))
    out['structure'] = graph(parse('(a b)'))
    out['nested_structure'] = graph(parse('((a b) c)'))
    out['recursive_frames'] = [c for c in out['recursive']['calls']
        if c['kind'] == 'apply' and c['expr'].startswith('(lambda')]
    assert [c['args'][0] for c in out['recursive_frames']] == ['((a b) c)', '(a b)', 'a']
    out['tests'] = dict(success_cases=len(cases)+1, error_cases=len(errors),
                        parse_roundtrips=5, evaluation_order='left-to-right',
                        step_limit_case=100)
    (ROOT/'results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(out['tests']))

if __name__ == '__main__':
    generate()
