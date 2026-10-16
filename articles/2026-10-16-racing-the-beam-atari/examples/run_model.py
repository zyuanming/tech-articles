#!/usr/bin/env python3
"""Experiments for the Atari 2600 article. Standard library only. MIT.

Everything here is produced by the teaching model in this directory; nothing
is a capture from real hardware or an emulator.
"""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image

from kernel import (CAL, place, scene_tables, program, render, ROWS)
from tia import VISIBLE_START, VISIBLE_WIDTH

OUT = Path(__file__).resolve().parent
PALETTE = {
    0: (0x10, 0x14, 0x10),      # background
    2: (0xC4, 0x8A, 0x3C),      # playfield
    3: (0x3C, 0xC8, 0x5A),      # player 0
    4: (0xE0, 0x50, 0x50),      # player 1
}


def to_image(lines, scale=3):
    im = Image.new('RGB', (VISIBLE_WIDTH, len(lines)))
    px = im.load()
    for y, row in enumerate(lines):
        for x, v in enumerate(row):
            px[x, y] = PALETTE[v]
    return im.resize((VISIBLE_WIDTH * scale, len(lines) * scale), Image.NEAREST)


def main():
    result = {}
    result['frame_timing'] = dict(
        scanlines=262, colour_clocks_per_line=228, machine_cycles_per_line=76,
        vsync_lines=3, vblank_lines=37, picture_lines=192, overscan_lines=30,
        horizontal_blank_clocks=68, visible_clocks=160)

    # 1. calibration: what one delay-loop step does to the sprite
    result['position_steps'] = [dict(loop_iterations=n, pixel=p)
                                for n, p in sorted(CAL.items())]

    # 2. a real frame of a Pong-like scene
    tables = scene_tables(p0_top=84, p1_top=74, ball_row=60, ball_col=96)
    flat = (tables['pf0'] + tables['pf1'] + tables['pf2']
            + tables['p0'] + tables['p1'] + tables['bl'])
    fr = render(program(24, 128, 96, 0xF800), flat)
    to_image(fr.lines).save(OUT / 'frame-pong.png')
    result['pong'] = dict(
        player0_pixel=fr.tia.pos['P0'] - VISIBLE_START,
        player1_pixel=fr.tia.pos['P1'] - VISIBLE_START,
        ball_pixel=fr.tia.pos['BL'] - VISIBLE_START,
        cycles_per_visible_line=fr.cycle_use[41],
        lines_captured=len(fr.lines))

    # 3. a second scene: the same kernel, objects moved
    tables2 = scene_tables(p0_top=40, p1_top=130, ball_row=100, ball_col=44)
    flat2 = (tables2['pf0'] + tables2['pf1'] + tables2['pf2']
             + tables2['p0'] + tables2['p1'] + tables2['bl'])
    fr2 = render(program(72, 150, 44, 0xF800), flat2)
    to_image(fr2.lines).save(OUT / 'frame-pong-moved.png')
    result['pong_moved'] = dict(
        player0_pixel=fr2.tia.pos['P0'] - VISIBLE_START,
        player1_pixel=fr2.tia.pos['P1'] - VISIBLE_START,
        ball_pixel=fr2.tia.pos['BL'] - VISIBLE_START)

    # 4. overrun: what happens when the kernel does not finish in time
    fr3 = render(program(24, 128, 96, 0xF800, faulty=True), flat)
    to_image(fr3.lines).save(OUT / 'frame-overrun.png')
    late = []
    for i, ev in enumerate(fr3.events):
        for clock, name, _ in ev:
            if name in ('PF0', 'PF1', 'PF2', 'GRP0', 'GRP1', 'ENABL') and clock > 68:
                late.append(dict(line=i, register=name, colour_clock=clock))
    result['overrun'] = dict(
        cycles_per_visible_line=fr3.cycle_use[41],
        writes_after_beam=len(late),
        first_late_writes=late[:6],
        picture_differing_lines=sum(
            1 for a, b in zip(fr.lines, fr3.lines) if a != b))

    # 5. collisions: the chip reports overlaps without any software help
    tcol = scene_tables(84, 74, 84, 24)
    flatc = (tcol['pf0'] + tcol['pf1'] + tcol['pf2']
             + tcol['p0'] + tcol['p1'] + tcol['bl'])
    frc = render(program(24, 128, 24, 0xF800), flatc)
    result['collisions'] = dict(
        registers={k: v for k, v in frc.tia.collisions.items() if v},
        pairs=[list(p) for p, (reg, bit) in frc.tia.COLLISION_BITS.items()
               if frc.tia.collisions[reg] & (1 << bit)],
        ball_pixel=frc.tia.pos['BL'] - VISIBLE_START,
        player0_pixel=frc.tia.pos['P0'] - VISIBLE_START)

    # 6. flicker: four things drawn with only two player sprites
    def flicker_tables(parity):
        pf0, pf1, pf2, p0, p1, bl = [], [], [], [], [], []
        for r in range(ROWS):
            pf0.append(0x10 if 4 <= r < ROWS - 4 else 0xF0)
            pf1.append(0x00 if 4 <= r < ROWS - 4 else 0xFF)
            pf2.append(0x00 if 4 <= r < ROWS - 4 else 0xFF)
            a = 0xFF if 60 <= r < 76 else 0x00
            b = 0xFF if 110 <= r < 126 else 0x00
            p0.append(a if parity == 0 else b)
            p1.append(b if parity == 0 else a)
            bl.append(1 if 150 <= r < 158 else 0)
        return (pf0 + pf1 + pf2 + p0 + p1 + bl)

    frA = render(program(60, 200, 130, 0xF800), flicker_tables(0))
    frB = render(program(60, 200, 130, 0xF800), flicker_tables(1))
    to_image(frA.lines).save(OUT / 'frame-flicker-a.png')
    to_image(frB.lines).save(OUT / 'frame-flicker-b.png')
    merged = []
    for ra, rb in zip(frA.lines, frB.lines):
        merged.append([a if a else b for a, b in zip(ra, rb)])
    to_image(merged).save(OUT / 'frame-flicker-both.png')
    result['flicker'] = dict(
        frame_a_rows=sum(1 for r in frA.lines if any(v == 3 for v in r)),
        frame_b_rows=sum(1 for r in frB.lines if any(v == 3 for v in r)),
        merged_rows=sum(1 for r in merged if any(v == 3 for v in r)),
        note='两帧各自只画两个物体；人眼把交替的两帧合成四个')

    # 7. how much of a line the kernel actually uses
    budget = []
    for label, used in (('播放场+两个玩家+球', 52),):
        budget.append(dict(kernel=label, cycles=used, spare=76 - used))
    result['kernel_budget'] = budget

    (OUT / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
