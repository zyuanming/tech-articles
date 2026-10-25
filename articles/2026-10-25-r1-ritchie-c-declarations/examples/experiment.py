#!/usr/bin/env python3
# Original code: CC0-1.0.
"""Run with --out outside this source directory for independent checks."""
import argparse
import json
import os
import platform
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CASES = {
    'wrong_row': 'int main(void) {\n  int a[3]={10,20,30};\n  int (*row)[3]=a;\n  return (*row)[1];\n}\n',
    'call_integer_pointer': 'int main(void) {\n  int a=20; int *p=&a;\n  return p(1);\n}\n',
    'function_returns_array': 'int bad(void)[3];\n',
    'array_of_functions': 'int bad[3](void);\n',
    'const_pointer_reassign': 'typedef int *IntPtr;\nint main(void) {\n  int a[3]={10,20,30};\n  const IntPtr p=a;\n  p=a+1;\n  return *p;\n}\n',
    'const_pointee_write': 'int main(void) {\n  int a[3]={10,20,30};\n  const int *p=a;\n  *p=11;\n  return *p;\n}\n',
}

def run(args, cwd):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       env={**os.environ, 'LC_ALL': 'C'})
    return {'command': args, 'returncode': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'main.c').write_bytes((HERE / 'main.c').read_bytes())
    flags = ['-std=c11', '-Wall', '-Wextra', '-pedantic-errors',
             '-fdiagnostics-color=never']
    compile_result = run(['gcc', *flags, 'main.c', '-o', 'demo'], out)
    assert compile_result['returncode'] == 0, compile_result
    result = run(['./demo'], out)
    assert result['returncode'] == 0
    values = json.loads(result['stdout'])
    assert values['row_second'] == values['reader_value'] == 20
    assert values['array_bytes'] == values['sample_count']*values['int_bytes']
    assert values['param_bytes'] == values['pointer_bytes']
    assert values['grid_param_row_bytes'] == values['row_bytes']
    assert values['links_values'] == [values['samples'][i]
                                      for i in values['links_indices']]
    negatives = {}
    for name, source in CASES.items():
        (out / (name+'.c')).write_text(source)
        r = run(['gcc', *flags, '-Werror', '-fsyntax-only', name+'.c'], out)
        assert r['returncode'] != 0, (name, r)
        negatives[name] = {'source': source, **r}
    version = run(['gcc', '--version'], out)['stdout'].splitlines()[0]
    data = {'license': 'CC0-1.0', 'environment': {
        'compiler': version, 'system': platform.system(),
        'machine': platform.machine(), 'standard': 'C11',
        'flags': flags}, 'values': values, 'compile': compile_result,
        'execution': result, 'negative_cases': negatives}
    (out / 'results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'compiler': version, 'values': values,
                      'rejected': list(negatives)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
