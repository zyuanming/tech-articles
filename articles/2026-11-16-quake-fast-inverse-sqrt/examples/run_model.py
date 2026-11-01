"""Run the model and write results.json. Standard library only, MIT."""
import json
from pathlib import Path

import rsqrt as R

HERE = Path(__file__).resolve().parent


def main():
    out = R.build()
    out['meta'] = dict(
        title='0x5f3759df in float32 bits',
        note='每一步都做 float32 舍入；x87 的 80 位中间结果没有模拟。',
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')

    print('magic  %s = %d    sigma %.7f' %
          (out['magic'], out['magic_dec'], out['sigma_shipped']))
    print('公式反推 A*(127-sigma) = %d (%s)' %
          (out['magic_from_sigma'], out['magic_from_sigma_hex']))
    print('原版附近搜索     %s  Δ=%+d  err %.8f' %
          (out['sweep']['magic'], out['sweep']['delta'], out['sweep']['err']))
    print()
    print('%-18s %-11s %-11s %-12s' % ('常数', '0 次', '1 次', '2 次'))
    for r in out['table']:
        print('%-18s %.6f   %.8f   %.10f' %
              (r['name'], r['e0'], r['e1'], r['e2']))
    print()
    for r in out['max_err']:
        print('迭代 %d 次：最坏相对误差 %.3e' % (r['iters'], r['max_rel_err']))
    print()
    for e in out['examples']:
        print('x=%-10g bits=%s  y0=%.7f  y1=%.9f  y2=%.11f  1/√x=%.9f' %
              (e['x'], e['bits'], e['y0'], e['y1'], e['y2'], e['exact']))
    print()
    p = out['payload']
    print('每帧 %d 次归一化：快路径 %.1f ms，修开方 %.1f ms，差 %.1f 倍' %
          (p['normals'], p['ms_fast'], p['ms_slow'], p['ratio']))


if __name__ == '__main__':
    main()
