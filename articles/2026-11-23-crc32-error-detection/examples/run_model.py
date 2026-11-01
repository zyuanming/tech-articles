"""Run the CRC model once and write results.json.

Everything the article and the figures quote comes from here.
"""

import json
import time

import crc


def main():
    t0 = time.time()
    R = crc.build()
    with open('results.json', 'w') as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
        f.write('\n')

    print('check values')
    for row in R['standards']:
        flag = 'ok' if row['ok'] else 'MISMATCH'
        print('  %-22s width %2d  %08X  %s' % (row['name'], row['width'],
                                               row['check'], flag))
    print('fox: %s' % R['fox']['crc_hex'])
    print('burst <= 16: %d patterns, %d missed'
          % (sum(r['patterns'] for r in R['burst']),
             sum(r['missed'] for r in R['burst'])))
    print('first undetectable burst: %d bits (%s)'
          % (R['burst_min']['length'], R['burst_min']['hex']))
    print('narrow CRC-8: %.4f missed (predicted %.4f)'
          % (R['narrow']['rate'], R['narrow']['predicted']))
    for row in R['swap']:
        print('  swap %-14s missed %.4f' % (row['scheme'], row['miss_rate']))
    print('distance: %s' % [(d['msglen'], d['distance']) for d in R['distance']])
    print('%.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
