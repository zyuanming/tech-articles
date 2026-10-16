"""Sample kernels for the model: build a ROM, run a frame, return pixels. MIT."""
from __future__ import annotations
from asm import assemble
from tia import TIA, W, VISIBLE_START, VISIBLE_LINES, OUT_DELAY
from cpu6507 import CPU
from frame import Frame

ROWS = 192


def delay_for_pixel(pixel):
    """Machine cycles of delay needed before STA RESPx to land on `pixel`."""
    target_clock = VISIBLE_START + pixel
    k = (target_clock - OUT_DELAY + 1) // 3      # cycles before the write
    return max(0, k - 2)                          # LDX #n costs 2 cycles


def loop_count(cycles):
    """LDX #n / dly: DEX / BNE dly costs 5n+1 cycles after the LDX."""
    if cycles <= 1:
        return 0
    return max(0, (cycles - 1) // 5)


def build(program, tables, data_base=0xF800):
    """Assemble code at $F000 and drop `tables` (list of bytes) at data_base."""
    rom, labels, cycles = assemble(program)
    off = data_base - 0xF000
    for i, b in enumerate(tables):
        rom[off + i] = b
    return rom, labels, cycles


def calibrate(max_n=14):
    """Measure this model: delay-loop count -> visible pixel of the object."""
    table = {}
    for n in range(1, max_n + 1):
        t = TIA(); t.clock = 0
        prog = [(None, 'STA', '$02'), (None, 'LDX', '#%d' % n),
                ('d', None, ''), (None, 'DEX', ''), (None, 'BNE', 'd'),
                (None, 'STA', '$10')]
        rom, _, _ = assemble(prog)
        c = CPU(rom, t)
        guard = 0
        while t.pos['P0'] is None and guard < 5000:
            c.step(); guard += 1
            if c.halted:
                c.halted = False; t.clock = 0; c.line_cycles = 0
        table[n] = t.pos['P0'] - VISIBLE_START
    return table


CAL = calibrate()


def place(target_pixel):
    """Return (loop_count, hmove_nibble) that lands an object on target_pixel."""
    best = None
    for n, base in CAL.items():
        for hm in range(-8, 8):
            if base + hm == target_pixel:
                if best is None or abs(hm) < abs(best[1]):
                    best = (n, hm)
    if best is None:
        # fall back to the nearest reachable position
        cands = [(abs(CAL[n] + hm - target_pixel), n, hm)
                 for n in CAL for hm in range(-8, 8)]
        cands.sort()
        best = (cands[0][1], cands[0][2])
    return best


RESP_OF = {'$10': '$20', '$11': '$21', '$14': '$24'}


def resp_block(label, reg_resp, target_pixel):
    """One scan line that drops RESPx at the right machine cycle."""
    n, hm = place(target_pixel)
    return [
        (None, 'STA', '$02'),
        (None, 'LDX', '#%d' % n), (label, None, ''),
        (None, 'DEX', ''), (None, 'BNE', label),
        (None, 'STA', reg_resp),
    ], hm


def hmove_block(offsets):
    """Set every HMPx, then fire a single HMOVE, as real kernels do."""
    body = []
    for reg_resp, hm in offsets:
        body.append((None, 'LDA', '#$%02X' % ((hm + 8) << 4)))
        body.append((None, 'STA', RESP_OF[reg_resp]))
    body.append((None, 'STA', '$02'))
    body.append((None, 'STA', '$2A'))
    body.append((None, 'STA', '$02'))
    body.append((None, 'STA', '$02'))
    return body


def scene_tables(p0_top, p1_top, ball_row, ball_col, paddle_h=24):
    pf0, pf1, pf2, p0, p1, bl = [], [], [], [], [], []
    for r in range(ROWS):
        if r < 4 or r >= ROWS - 4:
            pf0.append(0xF0); pf1.append(0xFF); pf2.append(0xFF)
        else:
            pf0.append(0x10); pf1.append(0x00); pf2.append(0x00)
        p0.append(0xFF if p0_top <= r < p0_top + paddle_h else 0x00)
        p1.append(0xFF if p1_top <= r < p1_top + paddle_h else 0x00)
        bl.append(1 if ball_row <= r < ball_row + 8 else 0)
    return dict(pf0=pf0, pf1=pf1, pf2=pf2, p0=p0, p1=p1, bl=bl)


def program(p0_x, p1_x, ball_x, tbl, faulty=False, two_line=False):
    body = [
        ('main', 'LDA', '#$02'), (None, 'STA', '$00'),
        (None, 'STA', '$02'), (None, 'STA', '$02'), (None, 'STA', '$02'),
        (None, 'LDA', '#$00'), (None, 'STA', '$00'),
        (None, 'LDA', '#$88'), (None, 'STA', '$0A'),
        (None, 'LDA', '#$1E'), (None, 'STA', '$06'),
        (None, 'LDA', '#$46'), (None, 'STA', '$07'),
        (None, 'LDA', '#$C4'), (None, 'STA', '$08'),
        (None, 'LDA', '#$00'), (None, 'STA', '$09'),
        (None, 'LDA', '#$02'), (None, 'STA', '$1F'),
        (None, 'LDA', '#$00'), (None, 'STA', '$04'),
        (None, 'LDX', '#3'), ('vb', None, ''), (None, 'STA', '$02'),
        (None, 'DEX', ''), (None, 'BNE', 'vb'),
    ]
    offs = []
    for label, reg, px in (('d0', '$10', p0_x), ('d1', '$11', p1_x),
                           ('d2', '$14', ball_x)):
        blk, hm = resp_block(label, reg, px)
        body += blk
        offs.append((reg, hm))
    body += hmove_block(offs)
    body += [(None, 'LDX', '#18'), ('vb2', None, ''),
             (None, 'STA', '$02'), (None, 'DEX', ''), (None, 'BNE', 'vb2'),
             (None, 'LDX', '#0'), ('kern', None, ''), (None, 'STA', '$02')]
    if faulty:
        # the author forgot to count these: 32 machine cycles over the budget
        body += [(None, 'NOP', '')] * 16
    for i, reg in enumerate(('$0D', '$0E', '$0F', '$1B', '$1C', '$1D')):
        body.append((None, 'LDA', '$%04X,X' % (tbl + i * ROWS)))
        body.append((None, 'STA', reg))
    body += [(None, 'INX', ''), (None, 'CPX', '#%d' % ROWS), (None, 'BNE', 'kern'),
             (None, 'LDX', '#12'), ('os', None, ''),
             (None, 'STA', '$02'), (None, 'DEX', ''), (None, 'BNE', 'os'),
             (None, 'JMP', 'main')]
    return body


def render(program, tables, data_base=0xF800, visible_start=40):
    rom, labels, cycles = build(program, tables, data_base)
    fr = Frame(rom)
    fr.run(visible_start_line=visible_start)
    fr.labels = labels
    fr.code_cycles = cycles
    return fr
