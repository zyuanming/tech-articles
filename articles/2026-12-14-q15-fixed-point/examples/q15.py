"""Q15 定点数模型：表示、乘法、舍入、溢出、滤波器。

只用标准库。所有数字由 build() 一次性算出，写进 results.json。

约定：Q15 = 16 位有符号整数，隐式除以 32768。真值范围 [-1, 1)。
"""

import json
import math

SCALE = 32768
FRAC_BITS = 15
FS = 48000


# ---------------------------------------------------------------- 随机数

class Rng:
    """xorshift32，种子先过一遍 LCG，避免低位退化。"""

    def __init__(self, seed):
        s = (1103515245 * seed + 12345) & 0x7FFFFFFF
        self.s = s or 0x9E3779B9

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s & 0xFFFFFFFF
        return self.s

    def rand(self):
        return self.next() / 4294967296.0

    def randrange16(self):
        # [-32768, 32767]
        return (self.next() >> 16) - 32768

    def choice(self, seq):
        return seq[self.next() % len(seq)]


# ---------------------------------------------------------------- 基本运算

def sat16(x):
    if x > 32767:
        return 32767
    if x < -32768:
        return -32768
    return x


def wrap16(x):
    return ((x + 32768) & 0xFFFF) - 32768


def to_q15(v):
    """浮点 -> Q15，四舍五入到最近（.5 向上）。"""
    return sat16(int(math.floor(v * SCALE + 0.5)))


def to_float(raw):
    return raw / SCALE


def mul_trunc(a, b):
    """直接右移：向下取整（对负数是朝 -inf），偏置为 -0.5 LSB。"""
    return (a * b) >> FRAC_BITS


def mul_round(a, b):
    """加半个 LSB 再右移：四舍五入（.5 朝 +inf），偏置接近 0。"""
    return (a * b + (1 << (FRAC_BITS - 1))) >> FRAC_BITS


def mul_rne(a, b):
    """四舍六入五取偶（banker's rounding），零偏置。"""
    p = a * b
    q = p >> FRAC_BITS
    r = p - (q << FRAC_BITS)
    half = 1 << (FRAC_BITS - 1)
    if r > half or (r == half and (q & 1)):
        q += 1
    return q


def mul_exact(a, b):
    return a * b / SCALE


MULS = {'trunc': mul_trunc, 'round': mul_round, 'rne': mul_rne}


def add_sat(a, b):
    return sat16(a + b)


def add_wrap(a, b):
    return wrap16(a + b)


# ---------------------------------------------------------------- 实验 1：表示

def representation():
    probes = [0.1, 0.2, 0.3, 1 / 3, 0.5, 0.7, 0.9, 0.999, -0.1, -0.5, -0.999]
    rows = []
    for v in probes:
        raw = to_q15(v)
        err = to_float(raw) - v
        rows.append({
            'value': v,
            'raw': raw,
            'decoded': to_float(raw),
            'err_lsb': err * SCALE,
            'err': err,
            'rel': (err / v) if v else 0.0,
        })
    # 1 LSB 折合多少 dBFS
    lsb_db = 20 * math.log10(1 / SCALE)
    return {'rows': rows, 'lsb_db': lsb_db, 'scale': SCALE,
            'headroom_db': 20 * math.log10(32767 / SCALE)}


# ---------------------------------------------------------------- 实验 2：乘法舍入

def mul_rounding(trials=20000, seed=7):
    rng = Rng(seed)
    out = {}
    for name, fn in MULS.items():
        errs = []
        exact_hits = 0
        for _ in range(trials):
            a = rng.randrange16()
            b = rng.randrange16()
            e = fn(a, b) - mul_exact(a, b)
            errs.append(e)
            if abs(e) < 1e-12:
                exact_hits += 1
        n = len(errs)
        mean = sum(errs) / n
        mx = max(abs(e) for e in errs)
        buckets = [0] * 22          # -1.1 .. 1.1，每格 0.1 LSB
        for e in errs:
            b = int((e + 1.1) * 10)
            if b < 0:
                b = 0
            if b > 21:
                b = 21
            buckets[b] += 1
        out[name] = {
            'mean_err_lsb': mean,
            'max_abs_err_lsb': mx,
            'exact_frac': exact_hits / n,
            'frac_le_half': sum(1 for e in errs if abs(e) <= 0.5) / n,
            'buckets': buckets,
        }

    # 累积：同一个乘法做 4096 次，看偏置怎么攒
    a, b = to_q15(0.1), to_q15(0.1)
    drift = {}
    for name, fn in MULS.items():
        s = 0
        for _ in range(4096):
            s += fn(a, b)
        drift[name] = {'sum_raw': s, 'sum_q15': to_float(s),
                       'true': 0.1 * 0.1 * 4096,
                       'err': to_float(s) - 0.1 * 0.1 * 4096}
    return {'stats': out, 'drift': drift, 'a_raw': a, 'b_raw': b,
            'product_exact': mul_exact(a, b)}


# ---------------------------------------------------------------- 实验 3：溢出

def overflow():
    rows = []
    for a_f, b_f in ((0.9, 0.5), (0.99, 0.9), (0.5, 0.6), (-0.9, -0.5),
                     (0.99, 0.99), (-0.99, -0.99)):
        a, b = to_q15(a_f), to_q15(b_f)
        s = a + b
        rows.append({
            'a': a_f, 'b': b_f, 'sum_true': a_f + b_f,
            'sat': to_float(add_sat(a, b)),
            'wrap': to_float(add_wrap(a, b)),
            'sat_raw': add_sat(a, b), 'wrap_raw': add_wrap(a, b),
        })

    # 乘法本身不会溢出：Q15 × Q15 落在 32 位里
    worst = -32768 * -32768
    return {'rows': rows, 'worst_product': worst,
            'product_bits': worst.bit_length(),
            'sat_max': to_float(32767), 'wrap_min': to_float(-32768)}


# ---------------------------------------------------------------- 实验 4：累加器宽度

def accumulator(trials=200, seed=11):
    rng = Rng(seed)
    n_terms = 256
    worst_sum = n_terms * 32768 * 32768          # 全是 (-1) × (-1)
    need_bits = worst_sum.bit_length()
    overflow32 = 0
    max_abs32 = 0
    max_abs64 = 0
    for _ in range(trials):
        acc32 = 0
        acc64 = 0
        for _ in range(n_terms):
            a = rng.choice([-32768, 32767]) if rng.rand() < 0.5 else rng.randrange16()
            b = rng.choice([-32768, 32767]) if rng.rand() < 0.5 else rng.randrange16()
            p = a * b
            acc64 += p
            acc32 = wrap32(acc32 + p)
            if abs(acc64) > 0x7FFFFFFF:
                overflow32 += 1
        max_abs32 = max(max_abs32, abs(acc32))
        max_abs64 = max(max_abs64, abs(acc64))
    return {'terms': n_terms, 'worst_sum': worst_sum, 'need_bits': need_bits,
            'int32_max': 0x7FFFFFFF, 'trials': trials,
            'overflow32_runs': overflow32,
            'max_abs_acc32': max_abs32, 'max_abs_acc64': max_abs64,
            'worst_ratio': worst_sum / 0x7FFFFFFF}


def wrap32(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


# ---------------------------------------------------------------- 实验 5：系数精度

def coef_precision():
    rows = []
    for f in (0.1, 1, 5, 20, 100, 1000, 5000, 10000):
        a = 1 - math.exp(-2 * math.pi * f / FS)
        raw_f = a * SCALE
        raw = int(math.floor(raw_f + 0.5))
        aq = raw / SCALE
        f_real = -math.log(1 - aq) * FS / (2 * math.pi) if aq < 1 else float('inf')
        rows.append({'cutoff': f, 'a': a, 'a_raw': raw, 'a_q15': aq,
                     'cutoff_after': f_real,
                     'rel_err': (f_real - f) / f if aq > 0 else None})
    min_a = 1 / SCALE
    f_floor = -math.log(1 - min_a) * FS / (2 * math.pi)
    return {'rows': rows, 'min_a': min_a, 'f_floor': f_floor,
            'fs': FS, 'f_nyq': FS / 2}


# ---------------------------------------------------------------- 实验 6：极点半径

def pole_precision():
    rows = []
    for t60 in (0.001, 0.01, 0.1, 1.0, 5.0, 10.0, 20.0):
        r = math.exp(-6.907755278982137 / (t60 * FS))   # ln(1000) ≈ 6.9078
        b1 = -r * r
        raw = int(math.floor(b1 * SCALE + 0.5))
        rq = math.sqrt(-raw / SCALE) if raw < 0 else 1.0
        t60q = -6.907755278982137 / (math.log(rq) * FS) if rq < 1 else float('inf')
        rows.append({'t60': t60, 'r': r, 'b1_raw': raw, 'r_q15': rq,
                     't60_q15': t60q,
                     'rel_err': (t60q - t60) / t60 if rq < 1 else None,
                     'steps_per_lsb': abs(1 / (2 * r))})
    finite = [r['t60_q15'] for r in rows if r['t60_q15'] != float('inf')]
    return {'rows': rows, 'longest_finite_t60': max(finite),
            'b1_lsb': 1 / SCALE}


# ---------------------------------------------------------------- 实验 7：极限环

def limit_cycle():
    """单极点低通 y += a*(x-y)，输入激励后归零，看尾巴怎么停。"""

    def run(mul, a_q, n=4000, amp=0.5):
        y = to_q15(amp)
        trace = []
        for i in range(n):
            x = to_q15(amp) if i == 0 else 0
            d = add_sat(x, -y)
            p = mul(d, a_q)
            y = add_sat(y, p)
            trace.append(y)
        # 找到最后一次"绝对值明显不为零"的位置
        last = 0
        for i, v in enumerate(trace):
            if abs(v) > 1:
                last = i
        tail = trace[-200:]
        flips = sum(1 for i in range(2, len(tail))
                    if (tail[i] - tail[i - 1]) * (tail[i - 1] - tail[i - 2]) < 0)
        curve = [to_float(trace[i]) for i in range(0, 400, 2)]
        return {'final': trace[-1], 'last_over_1lsb': last,
                'tail_max': max(abs(v) for v in tail),
                'tail_flips': flips, 'curve': curve}

    a_f = 0.05
    a_q = to_q15(a_f)
    float_run = {'final': None}
    y = 0.5
    for i in range(4000):
        x = 0.5 if i == 0 else 0.0
        y = y + a_f * (x - y)
    float_run = {'final_raw': y, 'final_q15': y * SCALE}
    return {'a': a_f, 'a_q': a_q, 'deadband_lsb': 1.0 / a_f,
            'trunc': run(mul_trunc, a_q),
            'round': run(mul_round, a_q),
            'float_final_lsb': y * SCALE}


# ---------------------------------------------------------------- 实验 8：Q15 滤波 vs 浮点

def filter_snr():
    """一阶低通，同一条输入，Q15 与浮点比较。"""
    a_f = 0.02
    a_q = to_q15(a_f)
    n = 2000
    x = [0.5 * math.sin(2 * math.pi * 220 * i / FS) + 0.3 * math.sin(2 * math.pi * 3000 * i / FS) + 0.2 * math.sin(2 * math.pi * 9000 * i / FS) for i in range(n)]

    def run(mul, quantise_input):
        y = 0
        out = []
        for s in x:
            xs = to_q15(s) if quantise_input else s
            d = add_sat(xs, -y) if quantise_input else xs - to_float(y)
            p = mul(d, a_q)
            y = add_sat(y, p)
            out.append(to_float(y))
        return out

    fl = []
    y = 0.0
    for s in x:
        y = y + a_f * (s - y)
        fl.append(y)

    def err(q):
        return [q[i] - fl[i] for i in range(n)]

    def snr(e):
        s = sum(v * v for v in e) / len(e)
        p = sum(v * v for v in fl) / len(fl)
        return 10 * math.log10(p / s) if s > 0 else float('inf')

    res = {}
    waves = {}
    for name, mul in MULS.items():
        q = run(mul, True)
        e = err(q)
        res[name] = {'snr_db': snr(e),
                     'max_abs_err_lsb': max(abs(v) for v in e) * SCALE,
                     'rms_err_lsb': math.sqrt(sum(v * v for v in e) / n) * SCALE}
        step = n // 200
        waves[name] = [q[i] for i in range(0, n, step)]
    step = n // 200
    return {'a': a_f, 'a_q': a_q, 'n': n, 'runs': res,
            'float_wave': [fl[i] for i in range(0, n, step)],
            'input_wave': [x[i] for i in range(0, n, step)],
            'q15_waves': waves}


# ---------------------------------------------------------------- 实验 9：正弦表

def sin_table(size=1024):
    tab = [to_q15(math.sin(2 * math.pi * i / size)) for i in range(size)]
    max_err = 0.0
    arg = 0
    for i in range(size * 4):
        v = i / (size * 4) * 2 * math.pi
        # 最近点查表
        idx = int(round(v / (2 * math.pi) * size)) % size
        err = abs(to_float(tab[idx]) - math.sin(v)) * SCALE
        if err > max_err:
            max_err, arg = err, v
    # 线性插值
    max_err_lerp = 0.0
    for i in range(size * 4):
        v = i / (size * 4) * 2 * math.pi
        p = v / (2 * math.pi) * size
        i0 = int(math.floor(p)) % size
        fr = p - math.floor(p)
        i1 = (i0 + 1) % size
        val = to_float(tab[i0]) + (to_float(tab[i1]) - to_float(tab[i0])) * fr
        err = abs(val - math.sin(v)) * SCALE
        max_err_lerp = max(max_err_lerp, err)
    curve_n = 200
    curve_near, curve_lerp, curve_ref = [], [], []
    for i in range(curve_n):
        v = 2 * math.pi * i / curve_n
        ref = math.sin(v)
        idx = int(round(v / (2 * math.pi) * size)) % size
        p = v / (2 * math.pi) * size
        i0 = int(math.floor(p)) % size
        fr = p - math.floor(p)
        i1 = (i0 + 1) % size
        lerp = to_float(tab[i0]) + (to_float(tab[i1]) - to_float(tab[i0])) * fr
        curve_ref.append(ref)
        curve_near.append((to_float(tab[idx]) - ref) * SCALE)
        curve_lerp.append((lerp - ref) * SCALE)
    return {'size': size, 'table_bytes': size * 2,
            'max_err_lsb': max_err, 'at_radian': arg,
            'max_err_lerp_lsb': max_err_lerp,
            'phase_err_lsb': math.pi * SCALE / size,
            'phase_step': 2 * math.pi / size,
            'curve_near': curve_near, 'curve_lerp': curve_lerp}


# ---------------------------------------------------------------- 实验 9b：阶梯

def staircase(n=96, cycles=1.5):
    xs = [math.sin(2 * math.pi * cycles * i / n) for i in range(n)]
    q15 = [to_q15(v) for v in xs]
    q3 = [sat16(int(round(v * 8)) * 4096) for v in xs]   # 4 位有效（含符号）对照
    return {'n': n, 'input': xs, 'q15': [to_float(v) for v in q15],
            'q15_raw': q15, 'q3': [to_float(v) for v in q3],
            'q15_step': 1 / SCALE, 'q3_step': 1 / 8}


# ---------------------------------------------------------------- 实验 10：位宽与 SQNR

def sqnr_sweep():
    """量化正弦（满幅）的信噪比，理论 6.02N + 1.76。"""
    rows = []
    n = 4096
    for bits in (8, 10, 12, 14, 16, 20, 24):
        step = 2.0 / (1 << bits)
        err = []
        sig = []
        for i in range(n):
            v = math.sin(2 * math.pi * 7 * i / n)
            q = round(v / step) * step
            q = max(-1.0, min(1.0 - step, q))
            err.append(q - v)
            sig.append(v)
        ps = sum(v * v for v in sig) / n
        pe = sum(v * v for v in err) / n
        rows.append({'bits': bits, 'measured': 10 * math.log10(ps / pe),
                     'theory': 6.02 * bits + 1.76})
    return rows


# ---------------------------------------------------------------- 实验 11：字长扫描

def word_sweep(bits_list=(16, 20, 24, 28, 32)):
    """同一个低通，用不同字长的定点实现，跟浮点比 SNR。"""
    a_f = 0.02
    n = 2000
    x = [0.5 * math.sin(2 * math.pi * 220 * i / FS)
         + 0.3 * math.sin(2 * math.pi * 3000 * i / FS)
         + 0.2 * math.sin(2 * math.pi * 9000 * i / FS) for i in range(n)]
    fl = []
    y = 0.0
    for s in x:
        y = y + a_f * (s - y)
        fl.append(y)
    ps = sum(v * v for v in fl) / n

    rows = []
    for bits in bits_list:
        scale = 1 << (bits - 1)
        frac = bits - 1
        a_q = int(math.floor(a_f * scale + 0.5))
        lo, hi = -scale, scale - 1
        yq = 0
        err = []
        for i, s in enumerate(x):
            xq = max(lo, min(hi, int(math.floor(s * scale + 0.5))))
            d = max(lo, min(hi, xq - yq))
            p = (d * a_q + (1 << (frac - 1))) >> frac
            yq = max(lo, min(hi, yq + p))
            err.append(yq / scale - fl[i])
        pe = sum(v * v for v in err) / n
        rows.append({'bits': bits, 'a_q': a_q, 'snr_db': 10 * math.log10(ps / pe),
                     'max_err_lsb': max(abs(v) for v in err) * scale,
                     'floor_db': 6.02 * bits + 1.76})
    return rows


# ---------------------------------------------------------------- 汇总

def build():
    return {
        'config': {'fs': FS, 'frac_bits': FRAC_BITS, 'scale': SCALE},
        'representation': representation(),
        'mul': mul_rounding(),
        'overflow': overflow(),
        'accumulator': accumulator(),
        'coef': coef_precision(),
        'poles': pole_precision(),
        'limit_cycle': limit_cycle(),
        'filter': filter_snr(),
        'sin_table': sin_table(),
        'staircase': staircase(),
        'sqnr': sqnr_sweep(),
        'word_sweep': word_sweep(),
    }


if __name__ == '__main__':
    print(json.dumps(build(), indent=1, ensure_ascii=False))
