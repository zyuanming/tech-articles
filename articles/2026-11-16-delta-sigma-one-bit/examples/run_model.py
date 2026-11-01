#!/usr/bin/env python3
"""Run the model and write results.json. Standard library only."""
import json
from pathlib import Path

import dsigma as D

HERE = Path(__file__).resolve().parent


def main():
    R = D.build()
    (HERE / 'results.json').write_text(json.dumps(R, indent=1,
                                                 ensure_ascii=False) + '\n')
    print('theory  order1 %.1f dB  order2 %.1f dB' % (R['theory']['o1'],
                                                      R['theory']['o2']))
    print('sim     order1 %.1f dB  order2 %.1f dB' % (R['sim']['o1'],
                                                      R['sim']['o2']))
    for row in R['oversample']:
        print('  OSR %3d  sim %5.1f / %5.1f   theory %5.1f / %5.1f'
              % (row['osr'], row['sim1'], row['sim2'], row['th1'], row['th2']))


if __name__ == '__main__':
    main()
