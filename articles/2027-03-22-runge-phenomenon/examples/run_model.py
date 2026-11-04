"""跑全部实验，写出 results.json。"""
import json
import math
import pathlib

import interp as I

HERE = pathlib.Path(__file__).resolve().parent
A = 25.0
LO, HI = -1.0, 1.0


def main():
    out = {'meta': {'function': 'f(x) = 1 / (1 + 25x^2)', 'a': A,
                    'interval': [LO, HI], 'float': 'float64（Python float）'}}

    f = I.runge

    # 1. 三个节点的手算例子
    nodes3 = I.equispaced(3, LO, HI)
    coef3 = I.monomial_fit(nodes3, f)
    x0 = 0.5
    out['hand'] = {
        'nodes': nodes3,
        'values': [f(x) for x in nodes3],
        'coef': coef3,
        'at': x0,
        'exact': f(x0),
        'interp': I.polyval(coef3, x0),
        'error': I.polyval(coef3, x0) - f(x0),
        'peak': I.polyval(coef3, 1.0),
    }

    # 1b. 那条抛物线在整个区间上的形状
    out['quad'] = {'rows': [{'x': x, 'f': f(x), 'p': I.polyval(coef3, x)}
                            for x in I.grid(LO, HI, 201)]}

    # 2. 11 个节点的两种插值，取稠密曲线
    n11 = 11
    out['curve'] = {}
    for name, nodes in (('equi', I.equispaced(n11, LO, HI)),
                        ('cheb', I.chebyshev(n11, LO, HI))):
        p = I.interpolant(nodes, f)
        rows = [{'x': x, 'f': f(x), 'p': p(x)}
                for x in I.grid(LO, HI, 401)]
        out['curve'][name] = {'nodes': nodes, 'values': [f(x) for x in nodes],
                              'rows': rows,
                              'sup': max(abs(r['f'] - r['p']) for r in rows)}

    # 3. 误差与 Lebesgue 常数随节点数的变化
    ns = list(range(2, 31))
    out['sweep'] = []
    for n in ns:
        row = {'n': n}
        for name, maker in (('equi', I.equispaced), ('cheb', I.chebyshev)):
            nodes = maker(n, LO, HI)
            err, at = I.sup_error(f, nodes, count=2001)
            lam, lam_at = I.lebesgue(nodes, count=2001)
            row[name] = {'error': err, 'at': at, 'lebesgue': lam,
                         'lebesgue_at': lam_at}
        out['sweep'].append(row)

    # 4. 节点位置与间距
    out['nodes'] = {}
    for name, maker in (('equi', I.equispaced), ('cheb', I.chebyshev)):
        nodes = maker(n11, LO, HI)
        out['nodes'][name] = {
            'nodes': nodes,
            'gaps': [nodes[i + 1] - nodes[i] for i in range(len(nodes) - 1)],
            'closest': min(nodes[i + 1] - nodes[i] for i in range(len(nodes) - 1)),
        }

    # 5. 基函数的振幅：每个 L_i 在区间上的最大绝对值
    out['basis'] = {}
    for name, maker in (('equi', I.equispaced), ('cheb', I.chebyshev)):
        nodes = maker(n11, LO, HI)
        xs = I.grid(LO, HI, 2001)
        peaks = [0.0] * n11
        for x in xs:
            for i, v in enumerate(I.basis_at(nodes, x)):
                if abs(v) > peaks[i]:
                    peaks[i] = abs(v)
        out['basis'][name] = {'nodes': nodes, 'peaks': peaks,
                              'worst': max(peaks),
                              'worst_i': peaks.index(max(peaks))}

    # 6. 误差热图：n × x
    out['heat'] = {}
    for name, maker in (('equi', I.equispaced), ('cheb', I.chebyshev)):
        rows = []
        for n in range(3, 26):
            nodes = maker(n, LO, HI)
            p = I.interpolant(nodes, f)
            rows.append({'n': n,
                         'err': [abs(f(x) - p(x)) for x in I.grid(LO, HI, 121)]})
        out['heat'][name] = {'xs': I.grid(LO, HI, 121), 'rows': rows}

    # 7. 收敛率由最近的极点决定：a 取 1 / 5 / 25
    out['rates'] = []
    for a in (1.0, 5.0, 25.0):
        rows = []
        for n in range(4, 31):
            nodes = I.chebyshev(n, LO, HI)
            err, at = I.sup_error(lambda x, a=a: I.runge(x, a), nodes,
                                  count=2001)
            rows.append({'n': n, 'error': err, 'at': at})
        ns_ = [r['n'] for r in rows if r['error'] > 1e-16]
        es_ = [r['error'] for r in rows if r['error'] > 1e-16]
        rho = math.sqrt(a)
        out['rates'].append({
            'a': a,
            'pole_imag': 1.0 / rho,
            'rho_theory': I.ellipse_rho(1.0 / rho),
            'rho_fit': I.fit_rho(ns_, es_),
            'rows': rows,
        })

    # 9. |x| 是折线，没有极点，换节点也救不回来
    rows = []
    for n in range(4, 31):
        nodes = I.chebyshev(n, LO, HI)
        err, at = I.sup_error(I.absx, nodes, count=2001)
        rows.append({'n': n, 'error': err, 'at': at})
    out['absx'] = {'rows': rows,
                   'ratio': I.fit_ratio([r['n'] for r in rows],
                                        [r['error'] for r in rows])}

    # 自检
    ok = True
    ok &= abs(out['hand']['values'][1] - 1.0) < 1e-15
    ok &= abs(out['hand']['coef'][2] + 25.0 / 26.0) < 1e-15
    ok &= out['curve']['cheb']['sup'] < out['curve']['equi']['sup']
    ok &= out['sweep'][-1]['equi']['error'] > out['sweep'][-1]['cheb']['error']
    lam = [r['equi']['lebesgue'] for r in out['sweep']]
    ok &= lam == sorted(lam)
    ok &= abs(I.ellipse_rho(0.2) - 1.21978) < 1e-4
    out['selfcheck'] = ok

    (HERE / 'results.json').write_text(json.dumps(out, indent=1))
    print('hand', out['hand']['interp'], out['hand']['error'],
          out['hand']['peak'])
    for row in out['sweep']:
        if row['n'] in (3, 5, 9, 11, 15, 21, 30):
            print('n=%2d  equi err %.3e lam %.3e | cheb err %.3e lam %.3f'
                  % (row['n'], row['equi']['error'], row['equi']['lebesgue'],
                     row['cheb']['error'], row['cheb']['lebesgue']))
    for r in out['rates']:
        print('a=%-4g pole %.3f  rho_theory %.4f  rho_fit %.4f'
              % (r['a'], r['pole_imag'], r['rho_theory'], r['rho_fit']))
    print('absx 每加一个节点乘 %.4f   n=30 err %.3e' % (out['absx']['ratio'],
                                                       out['absx']['rows'][-1]['error']))
    print('selfcheck', out['selfcheck'])


if __name__ == '__main__':
    main()
