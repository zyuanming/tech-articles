"""Run the Z-order model and write results.json."""

import json
import time
from pathlib import Path

import zorder as Z

OUT = Path(__file__).resolve().parent / 'results.json'


def main():
    t0 = time.time()
    R = Z.build()
    # one extra sweep for the plot: square size versus run count
    sweep = []
    for side in (2, 4, 8, 16, 32, 64):
        sweep.append(dict(side=side,
                          morton=Z.rect_runs(256, 'morton', side, side, aligned=False),
                          hilbert=Z.rect_runs(256, 'hilbert', side, side, aligned=False),
                          row=Z.rect_runs(256, 'row', side, side, aligned=False)))
    R['sweep'] = sweep
    OUT.write_text(json.dumps(R, indent=1, ensure_ascii=False) + '\n')

    print('cells            %d' % len(R['cells']))
    print('bit layout       (%d,%d) -> %s' % (R['bit_layout']['x'], R['bit_layout']['y'],
                                              R['bit_layout']['code_bits']))
    for c in R['cost']:
        print('%-8s mean %.3f  p95 %.2f  longest %.1f  jumps>4 %d'
              % (c['order'], c['mean'], c['p95'], c['longest'], c['over_4']))
    print('jumps>1 in 8x8  %d' % R['jumps']['total'])
    for r in R['rects']:
        print('%dx%-3d aligned row %5.2f morton %5.2f hilbert %5.2f | free %5.2f %5.2f %5.2f'
              % (r['w'], r['h'], r['row'], r['morton'], r['hilbert'],
                 r['row_free'], r['morton_free'], r['hilbert_free']))
    for s in R['sectors']:
        print('%-8s %-6s lines %2d  span %d' % (s['order'], s['tile'], s['lines'], s['span']))
    for c in R['compression']:
        print('%-8s delta %.1f cells, %.2f bits' % (c['order'], c['mean_delta'], c['mean_bits']))
    for t in R['three_d']:
        print('3d %-6s aligned=%d runs %.2f' % (t['order'], t['aligned'], t['runs']))
    print('sweep')
    for s in sweep:
        print('  side %2d  row %5.2f morton %5.2f hilbert %5.2f'
              % (s['side'], s['row'], s['morton'], s['hilbert']))
    print('done in %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
