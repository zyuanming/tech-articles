#!/usr/bin/env python3
"""Run the shared-wire model and write results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import net

HERE = Path(__file__).resolve().parent


def main() -> int:
    out = net.measure()
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('throughput ceiling : ALOHA %.1f%%  slotted %.1f%%'
          % (100 * out['ceiling']['aloha'], 100 * out['ceiling']['slotted']))
    print('backoff (stations -> mean collisions):')
    for row in out['backoff']:
        print('   %2d  %5.2f' % (row['stations'], row['mean']))
    print('efficiency with 32 stations: ALOHA %.1f%%  CSMA/CD %.1f%%'
          % (100 * out['levers'][0]['efficiency'],
             100 * out['levers'][1]['efficiency']))
    print('speed -> span for a 64-byte frame:',
          ', '.join('%gM:%gm' % (r['mbps'], r['span_m']) for r in out['speeds']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
