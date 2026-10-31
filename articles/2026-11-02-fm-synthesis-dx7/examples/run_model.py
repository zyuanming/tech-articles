#!/usr/bin/env python3
"""Run the FM measurements and write results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import fm

HERE = Path(__file__).resolve().parent


def main() -> int:
    out = fm.measure()
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('index -> partials (440 : 110):',
          ', '.join('%g:%d' % (r['index'], r['partials'])
                    for r in out['index_sweep']))
    print('highest sideband, as multiples of fm:',
          ', '.join('%g:%d' % (r['index'], r['reach'])
                    for r in out['index_sweep']))
    print('Carson vs measured (Hz, one-sided):')
    for r in out['bandwidth']:
        print('   fm %4.0f I %g  carson %6.1f  measured %6.1f'
              % (r['fm'], r['index'], r['carson'], r['measured']))
    print('ratios:', ', '.join('%s:%s' % (r['ratio'],
                                          'harmonic' if r['harmonic'] else 'inharmonic')
                               for r in out['ratios']))
    print('aliasing: highest sideband vs Nyquist (22050 Hz)')
    for r in out['aliasing']:
        extra = ''
        if r['beyond']:
            extra = '  folds to %.0f Hz, found %.0f Hz at %.1f dB' % (
                r['alias_hz'], r['found_hz'], r['found_db'])
        print('   fc %5.0f fm %5.0f  n<=%d  top %6.0f  %s%s'
              % (r['fc'], r['fm'], r['n_max'], r['top'],
                 'beyond' if r['beyond'] else 'ok', extra))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
