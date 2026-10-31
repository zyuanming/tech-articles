#!/usr/bin/env python3
"""Measure what the article claims. Standard library only."""
from __future__ import annotations

import json
import math
from pathlib import Path

import glyph

HERE = Path(__file__).resolve().parent


def scaled(contours, px, dy=0.0, dx=0.0):
    return [[(x * px + dx, y * px + dy) for x, y in c] for c in contours]


def render(contours, px, ss):
    return glyph.coverage(scaled(contours, px), px, px, ss)


def max_err(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def main() -> None:
    out = {}

    o = glyph.flatten_all(glyph.outline_o(), 12)
    i = glyph.flatten_all(glyph.outline_i(), 12)

    # 1. Flattening a curve into straight lines.
    out["chord"] = [dict(steps=s, em=round(e, 7), at_12px=round(e * 12, 4))
                    for s, e in glyph.chord_error(glyph.outline_o()[0],
                                                  (1, 2, 4, 8, 16, 32))]

    # 2. Supersampling vs accuracy, measured against a 64x reference.
    aa = []
    for name, contours, px in (("O", o, 12), ("I", i, 11)):
        ref = render(contours, px, 64)
        for ss in (1, 2, 4, 8, 16):
            cov = render(contours, px, ss)
            aa.append(dict(glyph=name, px=px, ss=ss, samples=ss * ss,
                           max_err=round(max_err(cov, ref), 4),
                           levels=glyph.grey_levels(cov),
                           contrast=glyph.contrast(cov)))
    out["aa"] = aa

    # 3. The same stem, drawn at different pixel sizes.
    stem = []
    for px in (8, 9, 10, 11, 12, 16, 24, 48):
        cov = render(i, px, 16)
        row = glyph.stem_profile(cov, px // 2)
        ink = [v for v in row if v > 0.01]
        stem.append(dict(px=px, width_em=0.12, width_px=round(0.12 * px, 3),
                         columns=len(ink), ink_total=round(sum(row), 3),
                         lightest=round(min(ink), 3) if ink else 0,
                         levels=glyph.grey_levels(cov),
                         profile=[round(v, 3) for v in row]))
    out["stem"] = stem

    # 3b. How much does the same stem jump between neighbouring sizes?
    adj = []
    for px in range(8, 21):
        ink = sum(v for v in glyph.stem_profile(render(i, px, 16), px // 2) if v > 0.01)
        prev = adj[-1]['ink'] if adj else None
        adj.append(dict(px=px, ink=round(ink, 3),
                        jump_pct=None if prev is None
                        else round((ink - prev) / prev * 100, 1)))
    out["adjacent"] = adj

    # 4. Hinting: snap the outline to whole pixels and look again.
    hinted = []
    for px in (11, 12, 14):
        cov = render(i, px, 16)
        hcov = glyph.coverage(scaled(glyph.hint(i, px, px), px), px, px, 16)
        row = glyph.stem_profile(cov, px // 2)
        hrow = glyph.stem_profile(hcov, px // 2)
        hinted.append(dict(px=px,
                           before=dict(ink_total=round(sum(row), 3),
                                       lightest=round(min([v for v in row if v > 0.01]), 3),
                                       columns=len([v for v in row if v > 0.01])),
                           after=dict(ink_total=round(sum(hrow), 3),
                                      lightest=round(min([v for v in hrow if v > 0.01] or [0]), 3),
                                      columns=len([v for v in hrow if v > 0.01])),
                           before_profile=[round(v, 3) for v in row],
                           after_profile=[round(v, 3) for v in hrow]))
    out["hint"] = hinted

    # 5. Gamma: what a 50 % pixel actually looks like.
    out["gamma"] = [dict(coverage=c, linear=round(c, 4),
                         srgb=round(glyph.srgb_encode(c), 4),
                         as_percent=round(glyph.srgb_encode(c) * 100, 1))
                    for c in (0.1, 0.25, 0.5, 0.75, 0.9)]

    # 6. Distance field: store once, rebuild at any size.
    field = glyph.sdf(scaled(o, 12), 12, 12)
    direct = render(o, 48, 16)
    recon = glyph.sdf_reconstruct(field, 4, edge=0.75)
    recon_soft = glyph.sdf_reconstruct(field, 4, edge=1.5)
    out["sdf"] = dict(
        grid=12, factor=4,
        rms_tight=round(math.sqrt(sum((a - b) ** 2 for ra, rb in zip(recon, direct)
                                      for a, b in zip(ra, rb)) / (48 * 48)), 4),
        rms_soft=round(math.sqrt(sum((a - b) ** 2 for ra, rb in zip(recon_soft, direct)
                                     for a, b in zip(ra, rb)) / (48 * 48)), 4),
        bytes_tight=12 * 12, bytes_direct=48 * 48,
        levels_tight=glyph.grey_levels(recon),
    )

    # 7. A diagonal edge: how many grey levels does it get?
    diag = [[(0.15, 0.15), (0.95, 0.15), (0.15, 0.95)]]
    diag_px = 12
    d = []
    for ss in (1, 2, 4, 8):
        cov = glyph.coverage([[(x * diag_px, y * diag_px) for x, y in c] for c in diag],
                             diag_px, diag_px, ss)
        d.append(dict(ss=ss, samples=ss * ss, levels=glyph.grey_levels(cov)))
    out["diagonal"] = d

    (HERE / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")

    print("chord :", [(r["steps"], r["at_12px"]) for r in out["chord"]])
    for r in out["aa"]:
        print("aa    : %s %dpx ss=%2d err=%.4f levels=%d" %
              (r["glyph"], r["px"], r["ss"], r["max_err"], r["levels"]))
    for r in out["stem"]:
        print("stem  : %2dpx width=%.2f ink=%.2f lightest=%.2f" %
              (r["px"], r["width_px"], r["ink_total"], r["lightest"]))
    for r in out["hint"]:
        print("hint  : %dpx before %s after %s" %
              (r["px"], r["before"], r["after"]))
    print("adj   :", [(r["px"], r["jump_pct"]) for r in out["adjacent"]])
    print("gamma :", [(g["coverage"], g["as_percent"]) for g in out["gamma"]])
    print("sdf   :", out["sdf"])
    print("diag  :", [(r["ss"], r["levels"]) for r in out["diagonal"]])


if __name__ == "__main__":
    main()
