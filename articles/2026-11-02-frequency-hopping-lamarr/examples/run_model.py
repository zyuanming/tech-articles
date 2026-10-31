#!/usr/bin/env python3
"""Run every measurement the article quotes and write results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import fh

HERE = Path(__file__).resolve().parent


def main() -> None:
    data = fh.measure()
    (HERE / 'results.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    s = data['sequence']
    print('sequence: %d hops, %d/%d channels used, chi2 %.1f (df 87), '
          'same as previous %d' % (s['hops'], s['used'], data['channels'],
                                   s['chi2'], s['same_as_previous']))
    print('processing gain: %.2f dB' % data['gain'])

    print('\n%-22s %-16s %8s %10s %8s' % ('mode', 'jammer', 'cover', 'power', 'PER'))
    for r in data['compare']:
        print('%-22s %-16s %8s %9.0fx %8.3f'
              % (r['mode'], r['jammer'], r['coverage'], r['needed'], r['per']))

    print('\nreaction (share of hop, PER):',
          [(r['share_of_hop'], r['per']) for r in data['reaction']])
    print('hop rates (hops/s, hops inside a 2 ms reaction):',
          [(r['rate'], r['hops_in_reaction']) for r in data['rates']])
    print('sync (offset in hops, share aligned):',
          [(r['offset'], r['aligned']) for r in data['sync']])


if __name__ == '__main__':
    main()
