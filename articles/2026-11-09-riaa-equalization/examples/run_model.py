"""跑 RIAA 模型，写出 results.json。只用标准库。"""

import json
import math
from pathlib import Path

import riaa as R

FREQS = [20, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]


def main():
    out = dict(
        constants=dict(T1=R.T1, T2=R.T2, T3=R.T3,
                       f1=round(R.hz(R.T1), 2), f2=round(R.hz(R.T2), 2),
                       f3=round(R.hz(R.T3), 2),
                       ref_hz=R.REF_HZ, v_ref_cm_s=R.V_REF * 100),
        curve=R.curve(FREQS),
        span=R.span(),
        headroom=R.bass_headroom(),
        playing=R.playing_time(),
        geometry=dict(r_out_mm=R.R_OUT * 1000, r_in_mm=R.R_IN * 1000, rpm=R.RPM,
                      guard=R.GUARD),
        speeds=R.speeds(),
        tracing=dict(
            outer=R.tracing(R.speeds()['outer']),
            mid=R.tracing(R.speeds()['mid']),
            inner=R.tracing(R.speeds()['inner']),
        ),
        noise=dict(full=R.noise_gain(), hf=R.noise_gain(1000.0, 20000.0),
                   by_octave=R.noise_by_octave()),
        tolerance=R.tolerance(),
        tolerance_curves=R.tolerance_curves(),
        tolerance_curves_tight=R.tolerance_curves(r_tol=0.001, c_tol=0.01),
        tolerance_tight=R.tolerance(r_tol=0.001, c_tol=0.01),
        warp=R.warp(),
        loudness=R.loudness_note(),
    )
    Path('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')

    c = out['constants']
    print('角点 %.1f / %.1f / %.1f Hz' % (c['f1'], c['f2'], c['f3']))
    print('曲线跨度 %+.1f dB（20 Hz）… %+.1f dB（20 kHz），共 %.1f dB'
          % (out['span']['at20'], out['span']['at20k'], out['span']['total']))
    for r in out['headroom']:
        print('  %6d Hz  有均衡 %7.1f µm  平坦 %8.1f µm  省 %4.1f dB'
              % (r['f'], r['with_riaa_um'], r['flat_um'], r['saved_db']))
    p = out['playing']
    print('沟槽间距 %.2f mm → %.1f 分钟；平坦 %.2f mm → %.1f 分钟'
          % (p['pitch_riaa_mm'], p['riaa']['minutes'],
             p['pitch_flat_mm'], p['flat']['minutes']))
    sp = out['speeds']
    print('线速度 外 %.3f / 中 %.3f / 内 %.3f m/s' % (sp['outer'], sp['mid'], sp['inner']))
    for k in ('outer', 'mid', 'inner'):
        print('  20 kHz 波长 %-5s %.1f µm' % (k, out['tracing'][k][-1]['lam_um']))
    print('白噪：全带 %+.1f dB，1–20 kHz %+.1f dB'
          % (out['noise']['full'], out['noise']['hf']))
    print('  各倍频程：', ' '.join('%d:%+.0f' % (o['f'], o['db'])
                                   for o in out['noise']['by_octave']))
    print('容差 1%%R/5%%C：最坏 %.2f dB，中位 %.2f dB；1%%/1%%：最坏 %.2f dB'
          % (out['tolerance']['worst_db'], out['tolerance']['p50_db'],
             out['tolerance_tight']['worst_db']))
    w = out['warp']
    print('33⅓ 转翘曲 %.2f Hz，输出 %+.1f dB' % (w['hz'], w['db']))
    print('5 cm/s：1 kHz 振幅 %.1f µm，50 Hz 振幅 %.1f µm'
          % (out['loudness']['amp_1k_um'], out['loudness']['amp_50_um']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
