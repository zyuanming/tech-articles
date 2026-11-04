#!/usr/bin/env python3
"""线性探测一文的原创教学插图。MIT。

带数字的图全部读 results.json；格子里的键、探测次数都从账本原样取，
不在画图时另算一遍。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import ImageFont

from figkit import (Fig, PALETTE, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER,
                    RED, GRAY, LIGHT, PALE, GREEN, CREAM, TINT_T, TINT_B,
                    TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

MONO_PATH = '/System/Library/Fonts/Menlo.ttc'
_MONO = {}
VIOLET = '#5b4b8a'
PALETTE.update({VIOLET})


def mono(fig, xy, s, size=38, color=INK, anchor='la'):
    if size not in _MONO:
        _MONO[size] = ImageFont.truetype(MONO_PATH, size, index=0)
    f = _MONO[size]
    bb = fig.d.textbbox(xy, s, font=f, anchor=anchor)
    fig.d.text(xy, s, font=f, fill=color, anchor=anchor)
    fig.labels.append(dict(s=s, size=size, bold=False, bbox=bb, inside=None,
                           anchor=anchor, allow_overlap=False, tag=None,
                           skip_audit=False))
    fig.min_px = min(fig.min_px, size)
    return bb


def new(n, title, sub=None):
    fig = Fig(900)
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=40, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, size, 974, color=color) * size * 1.35) + 16


def bullets(fig, y, items, accent=TEAL, size=40):
    for text in items:
        fig.circle(76, y + 20, 14, fill=accent, outline=accent)
        y += int(fig.wrap((114, y), text, size, 900, color=INK) * size * 1.35) + 24
    return y


def table(fig, y, cols, rows, size=38, row_h=70, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 14, 1014, y + row_h - 16, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            if not text:
                continue
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1020, 'cell out of band: %r' % (text,)
            fig.text((x, y + 2), text, size, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y + 14


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def legend(fig, y, items, x0=52, step=300):
    x = x0
    for color, text in items:
        fig.rect(x, y + 4, x + 30, y + 34, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 52


def card(fig, name, x0, y0, x1, y1, head, lines, accent, size=40, head_size=42):
    fig.box(name, x0, y0, x1, y1, fill=WHITE, outline=accent)
    fig.text((x0 + 24, y0 + 18), head, head_size, bold=True, color=accent,
             inside=name)
    y = y0 + 24 + head_size * 1.85
    for ln in lines:
        y += int(fig.wrap((x0 + 24, y), ln, size, (x1 - x0) - 48, color=INK,
                          inside=name) * size * 1.35) + 6
    return y


def axes(fig, x0, y0, x1, y1, xr, yr, xticks, yticks, xlabel, ylabel,
         fx=None, fy=None):
    """一根 x 轴一根 y 轴；返回 (fx, fy) 两个数据到像素的函数。"""
    def px(v):
        return x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)

    def py(v):
        return y1 - (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)

    for t in yticks:
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for t in xticks:
        fig.text((px(t), y1 + 14), str(t), 38, color=INK_SOFT, anchor='ma')
    for t in yticks:
        fig.text((x0 - 16, py(t) - 22), str(t), 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 66), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 54), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


# ---------------------------------------------------------------- 图 01

TINTS = [TINT_T, TINT_B, TINT_A, TINT_R, TINT_G, PALE]
SOLID = [TEAL, BLUE, AMBER, RED, GREEN, VIOLET]


def cl_color(cid):
    return WHITE if cid == 0 else TINTS[cid % len(TINTS)]


def fig01():
    t = R['toy']
    m = t['m']
    fig, y = new(1, '七个槽位，五个键，一个五连',
                 '取 m = 7，键除以 7 取余当起点。插入 1、8、15、2、9，'
                 ' 每一步都把「该去哪儿」和「实际去了哪儿」拉开一点。')
    cw, ch = 84, 84
    x0 = 210
    top = y + 20
    for j in range(m):
        fig.text((x0 + j * cw + cw / 2, top - 40), str(j), 38, color=GRAY,
                 anchor='ma')
    for i, st in enumerate(t['steps']):
        yy = top + i * (ch + 52)
        fig.text((44, yy + 18), '插 %d' % st['key'], 38, color=INK)
        fig.text((44, yy + 60), '起点 %d' % st['home'], 38, color=GRAY)
        for j, v in enumerate(st['slot']):
            filled = v not in (-1, -2)
            probed = st['home'] <= j < st['home'] + st['probe']
            fig.rect(x0 + j * cw + 4, yy, x0 + j * cw + cw - 4, yy + ch,
                     fill=(TINT_A if probed else WHITE) if filled else WHITE,
                     outline=AMBER if probed else LIGHT, width=3)
            if filled:
                fig.text((x0 + j * cw + cw / 2, yy + 24), str(v), 40,
                         bold=True, color=INK, anchor='ma')
        fig.text((x0 + m * cw + 24, yy + 24), '探测 %d 次' % st['probe'], 38,
                 color=AMBER)
    # 删除那一行
    yy = top + len(t['steps']) * (ch + 52)
    fig.text((44, yy + 18), '删掉 8', 38, color=RED)
    fig.text((44, yy + 60), '留个墓碑', 38, color=GRAY)
    for j, v in enumerate(t['after_delete']):
        fig.rect(x0 + j * cw + 4, yy, x0 + j * cw + cw - 4, yy + ch,
                 fill=TINT_R if v == -2 else WHITE, outline=LIGHT, width=3)
        if v == -2:
            fig.text((x0 + j * cw + cw / 2, yy + 24), '墓', 40, bold=True,
                     color=RED, anchor='ma')
        elif v >= 0:
            fig.text((x0 + j * cw + cw / 2, yy + 24), str(v), 40, bold=True,
                     color=INK, anchor='ma')
    fig.text((x0 + m * cw + 24, yy + 24), '查 15：3 次', 38, color=RED)
    y2 = yy + ch + 40
    y2 = note(fig, y2, '五个键挤成了一条长 5 的簇。查 22（起点 1）要走 6 次才撞到空槽；'
                       'Knuth 的公式给这个装载率（5/7）算出平均 6.6 次。')
    save(fig, '01-toy.png', '手算例子：m=7 的表在五步插入与一次删除后的形态')


def grid_panel(fig, g, y, title):
    m = g['m']
    per = 32
    cw = 29
    x0 = 44
    fig.text((x0, y), title, 40, bold=True, color=INK)
    for r in range(2):
        for j in range(per):
            idx = r * per + j
            cid = g['ids'][idx]
            xx = x0 + j * cw
            fig.rect(xx, y + 56 + r * cw, xx + cw - 2, y + 56 + r * cw + cw - 2,
                     fill=cl_color(cid), outline=WHITE, width=2)
    return y + 56 + 2 * cw


def fig02():
    fig, y = new(2, '簇会连成一片', 'm = 64 的表，同样的键，两种装载率。'
                                   ' 颜色相同的相邻格子属于同一条簇，白色是空槽。')
    y = grid_panel(fig, R['grid'][0], y + 10,
                   '装载 32/64：最长簇 %d' % R['grid'][0]['longest'])
    y = grid_panel(fig, R['grid'][1], y + 50,
                   '装载 57/64：最长簇 %d' % R['grid'][1]['longest'])
    legend(fig, y + 30, [(TINT_T, '簇'), (WHITE, '空槽')], step=260)
    y2 = note(fig, y + 96,
              '右边那张图里，四分之一个表是一条连着的簇。这不是画得夸张：'
              '簇一旦成形，后面落在这条簇上的键只能往更长里接，'
              '越长的簇越容易接上下一个，这叫主聚集。')
    save(fig, '02-clusters.png', '主聚集：同一张表在两个装载率下的簇长')


def fig03():
    c = R['curve']
    fig, y = new(3, '实测曲线压在 Knuth 的公式上',
                 'm = 4099，键由 splitmix64 生成。成功探测是查表里已有的键，'
                 ' 失败探测是查一个不存在的键。纵轴取对数。')
    x0, x1 = 190, 970
    ytop, ybot = y + 60, y + 470

    def fx(a):
        return x0 + a * (x1 - x0)

    def fy(v):
        t = (math.log10(max(v, 1.0))) / 3.0
        return ybot - max(0.0, min(t, 1.0)) * (ybot - ytop)

    for e in (0, 1, 2, 3):
        yy = fy(10 ** e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        fig.text((x0 - 16, yy - 22), str(10 ** e), 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    fig.line((x0, ytop), (x0, ybot), color=INK, width=3)
    fig.text((x0, ybot + 16), '0', 38, color=INK_SOFT, anchor='ma')
    fig.text((fx(0.5), ybot + 16), '0.5', 38, color=INK_SOFT, anchor='ma')
    fig.text((fx(1.0), ybot + 16), '1.0', 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 70), '装载率 α', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 56), '平均探测次数', 38, color=INK_SOFT)

    series = [(('fail', RED, '实测：失败', 5), ('fail_knuth', RED, None, 3)),
              (('succ', BLUE, '实测：成功', 5), ('succ_knuth', BLUE, None, 3))]
    for (k1, col, lab, w), (k2, _c, _l, w2) in series:
        pts = [(fx(r['alpha']), fy(r[k1])) for r in c]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=w)
        for p in pts:
            fig.circle(p[0], p[1], 6, fill=col, outline=col)
        pk = [(fx(r['alpha']), fy(r[k2])) for r in c]
        for a, b in zip(pk, pk[1:]):
            fig.line(a, b, color=col, width=w2, dash=10)
    legend(fig, ybot + 132, [(RED, '失败（粗=实测，虚=公式）'),
                             (BLUE, '成功（粗=实测，虚=公式）')], step=490)
    r90 = min(c, key=lambda r: abs(r['alpha'] - 0.9))
    r95 = min(c, key=lambda r: abs(r['alpha'] - 0.95))
    y2 = note(fig, ybot + 214,
              'α = 0.90 时失败探测实测 {:.1f} 次、公式 {:.1f} 次；α = 0.95 时实测 {:.0f}、'
              '公式 {:.0f}。越接近 1，公式对初始条件越敏感，4000 个槽撑不起这个精度——'
              '后文会单独算一次这件事。'.format(
                  r90['fail'], r90['fail_knuth'], r95['fail'], r95['fail_knuth']))
    save(fig, '03-curve.png', '装载率与平均探测次数：实测与 Knuth 公式')


def fig04():
    d = R['dist']
    fig, y = new(5, '同一条簇，两种探测',
                 '装载率 0.9。横轴是查一个已存在的键需要探测几次（最后一格是 10 次及以上），'
                 '纵轴是落在这一档的键有多少个（总数 3689）。')
    x0, x1 = 200, 960
    ytop, ybot = y + 60, y + 400
    top = max(v for _, v in d['linear']['hist'])
    bw = 34

    def fy(v):
        return ybot - v / top * (ybot - ytop)

    for j in range(1, 11):
        xx = x0 + (j - 1) * 74
        for k, (name, col) in enumerate((('linear', TEAL), ('double', VIOLET))):
            hh = dict(d[name]['hist'])
            if j < 10:
                hv = hh.get(j, 0)
            else:  # 最后一格是「10 次及以上」，不然长尾在图上消失
                hv = sum(v for kk, v in hh.items() if kk >= 10)
            fig.rect(xx + k * (bw + 4), fy(hv), xx + k * (bw + 4) + bw, ybot,
                     fill=col, outline=None)
        fig.text((xx + bw + 4, ybot + 16), str(j) if j < 10 else '10+', 38,
                 color=INK_SOFT, anchor='ma')
    fig.text((x0 - 20, ytop - 56), '键的数量', 38, color=INK_SOFT)
    fig.text((x1, ybot + 70), '探测次数', 38, color=INK_SOFT, anchor='ra')
    legend(fig, ybot + 104, [(TEAL, '线性探测'), (VIOLET, '双散列')], step=300)
    y2 = note(fig, ybot + 186,
              '线性探测的平均探测 {:.2f} 次、最长 {} 次；双散列 {:.2f} 次、最长 {} 次。'
              '平均值差不多，尾巴差七倍——查表变慢的体感来自尾巴，不是平均。'.format(
                  d['linear']['mean_succ'], d['linear']['max_succ'],
                  d['double']['mean_succ'], d['double']['max_succ']))
    save(fig, '05-hist.png', '探测长度分布：线性探测与双散列')


def fig05():
    c = R['curve']
    fig, y = new(6, '簇长随装载率涨得比探测次数快',
                 '同样的 m = 4099，最长的一条簇有多长。α = 0.9 时一条簇已经四百格。')
    x0, x1 = 190, 970
    ytop, ybot = y + 60, y + 420
    px, py = axes(fig, x0, ytop, x1, ybot, (0, 1), (0, 2000),
                  [0, 0.5, 0.9, 1], [0, 500, 1000, 1500, 2000],
                  '装载率 α', '最长簇的格数')
    pts = [(px(r['alpha']), py(min(r['max_cluster'], 2000))) for r in c]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=TEAL, width=5)
    for p in pts:
        fig.circle(p[0], p[1], 7, fill=TEAL, outline=TEAL)
    r = c[-4]
    fig.text((px(r['alpha']) - 20, py(r['max_cluster']) - 80),
             'α = %.2f：%d 格' % (r['alpha'], r['max_cluster']), 38, color=INK,
             anchor='ra')
    y2 = note(fig, ybot + 150,
              'α 从 0.9 到 0.97，平均探测次数只涨了不到四倍，最长簇从 407 涨到 1925。'
              '聚集是自加速的：簇越长，接住下一个键的面积越大。')
    save(fig, '06-cluster.png', '最长簇的长度随装载率上升')


def fig06():
    g = R['grow']
    fig, y = new(8, '两种策略，两种尾部',
                 'm = 65537，插到 88% 满。纵轴对数，看的是最长的那一次探测。')
    x0, x1 = 200, 960
    ytop, ybot = y + 60, y + 400

    def fx(a):
        return x0 + (a - 0.25) / 0.7 * (x1 - x0)

    def fy(v):
        return ybot - (math.log10(max(v, 1)) - 0.5) / 2.5 * (ybot - ytop)

    for e in (1, 10, 100):
        yy = fy(e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        fig.text((x0 - 16, yy - 22), str(e), 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    fig.line((x0, ytop), (x0, ybot), color=INK, width=3)
    for a in (0.3, 0.5, 0.7, 0.88):
        fig.text((fx(a), ybot + 16), '%.2f' % a, 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 70), '装载率', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 56), '最长探测次数', 38, color=INK_SOFT)
    for key, col, lab in (('lin_max_probe', RED, '线性探测'),
                          ('rh_max_probe', TEAL, 'Robin Hood')):
        pts = [(fx(r['alpha']), fy(r[key])) for r in g]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=5)
        for p in pts:
            fig.circle(p[0], p[1], 7, fill=col, outline=col)
    legend(fig, ybot + 104, [(RED, '线性探测'), (TEAL, 'Robin Hood')], step=320)
    last = g[-1]
    y2 = note(fig, ybot + 186,
              '插到 {:.0f}% 满时，线性探测的最长探测是 {} 次，Robin Hood 是 {} 次。'
              '平均值几乎一样（{:.2f} 对 {:.2f}），差的全在尾部。'.format(
                  last['alpha'] * 100, last['lin_max_probe'], last['rh_max_probe'],
                  last['lin_mean'], last['rh_mean']))
    save(fig, '08-tail.png', '最长探测次数：线性探测与 Robin Hood')


def fig07():
    rd = R['rhdemo']
    fig, y = new(7, '谁更冤，谁先坐',
                 'm = 11 的表，依次插 8、9、19、30。槽里写键，下面对应的绿色数字是'
                 ' 它离自己起点还有多远。')
    cw = 56
    x0 = 60
    for step, st in enumerate(rd['trace']):
        yy = y + 20 + step * 150
        fig.text((x0, yy - 4), '插 %d（起点 %d）' % (st['key'], st['home']), 38,
                 color=INK)
        cells = {i: (k, dd) for i, k, dd in st['items']}
        for j in range(rd['m']):
            xx = x0 + 330 + j * cw
            occ = j in cells
            fig.rect(xx, yy + 34, xx + cw - 6, yy + 110,
                     fill=TINT_T if occ else WHITE, outline=LIGHT, width=3)
            if occ:
                fig.text((xx + cw / 2 - 3, yy + 44), str(cells[j][0]), 38,
                         bold=True, color=INK, anchor='ma')
                fig.text((xx + cw / 2 - 3, yy + 132), str(cells[j][1]), 38,
                         color=TEAL, anchor='ma')
        fig.text((x0 + 330 - 12, yy + 44), '槽', 38, color=GRAY, anchor='ra')
    y2 = note(fig, y + 20 + 4 * 150 + 20,
              '插 19 时，槽 9 里的 9 刚到自己起点（d=0），而 19 已经跑了 1 格：'
              '让 19 坐下，9 往后挪。插 30 同样把 9 挤到槽 0。'
              '结果是所有人的探测距离都被压在最长的那个附近。')
    save(fig, '07-robinhood.png', 'Robin Hood 的让位规则：四次插入')


def fig08():
    t = R['tomb']
    fig, y = new(9, '删掉的键还在收费',
                 'm = 4099。插到 85% 满（3484 个），删掉 1200 个，'
                 ' 再查不存在的键。三组是三次独立实验。')
    x0, x1 = 210, 960
    ytop, ybot = y + 90, y + 420
    top = 30.0

    def fy(v):
        return ybot - v / top * (ybot - ytop)

    for tk in (0, 10, 20, 30):
        yy = fy(tk)
        fig.line((x0, yy), (x1, yy), color=PALE, width=2)
        fig.text((x0 - 16, yy - 22), str(tk), 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    fig.line((x0, ytop), (x0, ybot), color=INK, width=3)
    fig.text((44, ytop - 56), '失败探测次数', 38, color=INK_SOFT)
    groups = ['第一次', '第二次', '第三次']
    for gi, r in enumerate(t):
        gx = x0 + 30 + gi * 250
        fig.text((gx + 80, ybot + 16), groups[gi], 38, color=INK_SOFT,
                 anchor='ma')
        bars = [(r['fail_before'], RED), (r['fail_after'], AMBER),
                (r['fail_fresh'], TEAL)]
        for k, (v, col) in enumerate(bars):
            xx = gx + k * 54
            fig.rect(xx, fy(min(v, top)), xx + 46, ybot, fill=col, outline=None)
    fig.text((x0 + 30, ytop - 8), '前两根几乎一样高：墓碑没收走代价', 40,
             color=RED)
    legend(fig, ybot + 70, [(RED, '删除前'), (AMBER, '删除后'),
                            (TEAL, '同规模重建')], step=300)
    y2 = note(fig, ybot + 152,
              '三次实验：删除前 {:.1f} / {:.1f} / {:.1f} 次，删除后 {:.1f} / {:.1f} / {:.1f} 次，'
              '同一批活着的 {:.0f} 个键重建后只要 {:.1f} / {:.1f} / {:.1f} 次。'.format(
                  t[0]['fail_before'], t[1]['fail_before'], t[2]['fail_before'],
                  t[0]['fail_after'], t[1]['fail_after'], t[2]['fail_after'],
                  t[0]['succ_before'] and t[0]['occ'],
                  t[0]['fail_fresh'], t[1]['fail_fresh'], t[2]['fail_fresh']))
    save(fig, '09-tomb.png', '墓碑对失败探测的影响：三次独立实验')


def fig09():
    f = R['formula']
    fig, y = new(4, '三种策略的探测次数',
                 '公式来自各自的经典分析：线性探测是 Knuth 1963 的结论，'
                 ' 链地址与双散列是教科书公式。格子里是「成功 / 失败」。')
    rows = [[('α', INK, True), ('线性探测', RED, True),
             ('链地址', TEAL, True), ('双散列', BLUE, True)]]
    for r in f:
        rows.append([('%.2f' % r['alpha'], INK_SOFT, False),
                     ('%.1f / %.1f' % (r['lin'], r['lin_fail']), INK, False),
                     ('%.2f / %.2f' % (r['chain'], r['chain_fail']), INK, False),
                     ('%.2f / 不适用' % r['dbl'], INK, False)])
    cols = [(54, 'la'), (180, 'la'), (500, 'la'), (760, 'la')]
    y2 = table(fig, y + 10, cols, rows, row_h=84)
    y3 = note(fig, y2 + 20,
              '链地址的失败代价正好是 α：顺着链走完，表里没有空槽可撞。'
              '线性探测的失败代价是它的平方量级——这就是查不存在的键比查存在的键'
              '难受得多的原因。双散列的失败探测没有闭式，教科书给的上界与 1/(1−α) 同级。')
    save(fig, '04-formula.png', '三种探测策略在不同装载率下的探测次数')


def fig10():
    fig, y = new(10, '为什么现代实现一次比 16 个',
                 'SwissTable 的做法：每个槽配一个字节的控制字，'
                 ' 几十个槽的控制字挤在几条缓存行里。')
    x0, ytop = 60, y + 30
    cw = 52
    h2 = [0x2c, 0x91, 0x07, 0x55, 0x6b, 0xab, 0x3e, 0x18,
          0x2c, 0x74, 0xc3, 0x5f, 0x0d, 0x8e, 0x27, 0xb1]
    for j, b in enumerate(h2):
        xx = x0 + j * cw
        hit = b == 0x2c
        fig.rect(xx, ytop, xx + cw - 6, ytop + 76,
                 fill=TINT_T if hit else WHITE, outline=TEAL if hit else LIGHT,
                 width=4 if hit else 3)
        fig.text((xx + cw / 2 - 3, ytop + 18), '%02x' % b, 38,
                 color=TEAL if hit else INK_SOFT, anchor='ma')
    fig.text((x0, ytop - 44), '16 个控制字节 = 16 字节', 38, color=INK_SOFT)
    n = fig.wrap((x0, ytop + 100),
                 '要查的键的指纹是 2c：一条比较指令把 16 个里像的两个挑出来，'
                 '再逐个比真键。空槽和删过的槽各有一个不与指纹撞的专用值，这里没画。',
                 38, 974, color=INK)
    y2 = note(fig, ytop + 100 + n * 54 + 20,
              '这不是「线性探测更快」。这是把「沿着一条簇一格一格走」换成'
              '「一次看 16 格谁像」。线性探测的簇长规律仍然在，'
              '只是不再决定每次比较要花多少条指令。')
    save(fig, '10-swiss.png', 'SwissTable 的控制字节与批量比较（结构示意）')


def fig11():
    fig, y = new(11, '几种语言里的哈希表', '都叫「哈希表」，底层差得很远。')
    rows = [[('实现', INK, True), ('冲突处理', INK, True)],
            [('Python dict', TEAL, True), ('开放寻址 + 扰动探测', INK, False)],
            [('Rust HashMap', TEAL, True), ('SwissTable（分组控制字）', INK, False)],
            [('Go map', TEAL, True), ('分组桶 + tophash', INK, False)],
            [('C++ unordered_map', TEAL, True), ('链地址', INK, False)]]
    cols = [(54, 'la'), (486, 'la')]
    y2 = table(fig, y + 10, cols, rows, row_h=100)
    y3 = note(fig, y2 + 20,
              'Python 3.6 的紧凑布局、Rust 1.36 换 hashbrown、Go 1.24 换 Swiss Table，'
              '三次改动的方向一致：让「一次比较能覆盖的槽」变多，让探测落在同一条缓存行里。'
              '大 O 没变，常数变了。')
    save(fig, '11-impl.png', '四种哈希表的冲突处理方式')


def fig12():
    fig, y = new(12, '三句话')
    items = [('单条探测很便宜，簇很贵',
              ['线性探测的下一次探测就在隔壁，几乎不要钱。'
               '贵的是簇变长之后「每一步都不中」的连乘。']),
             ('决定代价的是失败查找',
              ['查一个不存在的键必须走完整条簇。α = 0.95 时失败探测 200 次，'
               '成功查找只要 10 次。']),
             ('装到七成就该扩容了',
              ['线性探测在 α = 0.7 时失败探测约 6 次，α = 0.9 时 50 次。'
               '表翻倍很便宜，簇变长很贵。'])]
    for i, (head, lines) in enumerate(items):
        yy = y + 20 + i * 230
        fig.rect(48, yy, 1014, yy + 206, fill=WHITE, outline=LIGHT, width=3,
                 radius=18)
        fig.text((78, yy + 24), head, 42, bold=True, color=TEAL)
        fig.wrap((78, yy + 96), ''.join(lines), 40, 908, color=INK)
    save(fig, '12-takeaways.png', '全文三句话')


def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 64), '下一个槽', 100, bold=True)
    fig.text((70, 182), '就在隔壁', 100, bold=True)
    fig.text((74, 308), '线性探测：便宜的一步，昂贵的簇尾', 44, color=INK_SOFT)
    mono(fig, (74, 400), 'm = 4099，α = 0.9', 52, color=TEAL)
    fig.text((74, 500), '成功查找：平均 5.6 次', 42, color=INK)
    fig.text((74, 570), '失败查找：平均 56 次', 42, color=INK)
    fig.text((74, 660), '最长的一条簇：407 格', 86, bold=True, color=RED)
    fig.text((74, 800), '同一个表，双散列最长 49 次', 40, color=TEAL)
    fig.text((74, 946), '2027-02-15 · 原创 · CC BY 4.0', 40, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig03, fig09, fig04, fig05, fig07, fig06, fig08,
               fig10, fig11, fig12):
        print(fn.__name__)
        fn()
    META.sort(key=lambda r: r['path'])
    meta = HERE / 'figure-metadata.json'
    meta.write_text(json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    print('wrote', meta, len(META), 'figures')
    cover()


if __name__ == '__main__':
    main()
