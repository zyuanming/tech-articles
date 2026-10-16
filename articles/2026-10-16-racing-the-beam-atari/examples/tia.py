"""A cycle-counting model of the Atari 2600 display path. Standard library only. MIT.

It is a *teaching* model, not a chip-accurate emulator:
  * the 6507 instruction set is limited to the opcodes the sample kernels use,
    but each one costs its documented number of machine cycles;
  * a scan line is 228 colour clocks = 76 machine cycles, as in the
    Stella Programmer's Guide;
  * one machine cycle is three colour clocks, so a write on machine cycle k
    lands the object at colour clock 3k + 5 (the 5-clock output delay is this
    model's chosen constant; the real chip's exact offset depends on where
    inside the cycle the write lands);
  * HMOVE applies HMPx (-8..+7 colour clocks) at the start of the line.
"""
from __future__ import annotations

COLOUR_CLOCKS = 228
CPU_CYCLES = 76
VISIBLE_START = 68
VISIBLE_WIDTH = 160
VISIBLE_LINES = 192

# TIA write addresses
W = {
    'VSYNC': 0x00, 'VBLANK': 0x01, 'WSYNC': 0x02, 'RSYNC': 0x03,
    'NUSIZ0': 0x04, 'NUSIZ1': 0x05, 'COLUP0': 0x06, 'COLUP1': 0x07,
    'COLUPF': 0x08, 'COLUBK': 0x09, 'CTRLPF': 0x0A, 'REFP0': 0x0B,
    'REFP1': 0x0C, 'PF0': 0x0D, 'PF1': 0x0E, 'PF2': 0x0F,
    'RESP0': 0x10, 'RESP1': 0x11, 'RESM0': 0x12, 'RESM1': 0x13, 'RESBL': 0x14,
    'AUDC0': 0x15, 'AUDC1': 0x16, 'AUDF0': 0x17, 'AUDF1': 0x18,
    'AUDV0': 0x19, 'AUDV1': 0x1A, 'GRP0': 0x1B, 'GRP1': 0x1C,
    'ENAM0': 0x1D, 'ENAM1': 0x1E, 'ENABL': 0x1F,
    'HMP0': 0x20, 'HMP1': 0x21, 'HMM0': 0x22, 'HMM1': 0x23, 'HMBL': 0x24,
    'VDELP0': 0x25, 'VDELP1': 0x26, 'VDELBL': 0x27,
    'RESMP0': 0x28, 'RESMP1': 0x29, 'HMOVE': 0x2A, 'HMCLR': 0x2B,
    'CXCLR': 0x2C,
}
R = {'CXM0P': 0x30, 'CXM1P': 0x31, 'CXP0FB': 0x32, 'CXP1FB': 0x33,
     'CXM0FB': 0x34, 'CXM1FB': 0x35, 'CXBLPF': 0x36, 'CXPPMM': 0x37,
     'SWCHA': 0x0280, 'SWCHB': 0x0282, 'INTIM': 0x0284}

OUT_DELAY = 5          # colour clocks from RESPx write to first pixel


class TIA:
    def __init__(self):
        self.reset()

    def reset(self):
        self.reg = {k: 0 for k in W}
        self.reg['COLUBK'] = 0
        self.pos = {n: None for n in ('P0', 'P1', 'M0', 'M1', 'BL')}
        self.hm = {n: 0 for n in ('P0', 'P1', 'M0', 'M1', 'BL')}
        self.collisions = {r: 0 for r in
                           ('CXM0P', 'CXM1P', 'CXP0FB', 'CXP1FB', 'CXM0FB',
                            'CXM1FB', 'CXBLPF', 'CXPPMM')}
        self.record = None       # list of (clock, name, value) when tracing

    def reg_addr(self, name):
        return W[name]

    # ---- CPU-side writes -------------------------------------------------
    IMMEDIATE = ('RES', 'HMP', 'HMM', 'HMBL', 'HMOVE', 'HMCLR', 'CXCLR')

    def write(self, addr, value):
        for name, a in W.items():
            if a == addr:
                value &= 0xFF
                if self.record is not None:
                    self.record.append((3 * self.clock, name, value))
                if name.startswith(self.IMMEDIATE):
                    self._apply(name, value)
                return True
        return False

    def _apply(self, name, value):
        """Apply one register write. Position registers act at once; graphics
        and colour registers are replayed as the beam reaches their clock."""
        self.reg[name] = value & 0xFF
        if name.startswith('RES'):
            who = {'RESP0': 'P0', 'RESP1': 'P1', 'RESM0': 'M0',
                   'RESM1': 'M1', 'RESBL': 'BL'}[name]
            self.pos[who] = 3 * self.clock + OUT_DELAY
        elif name.startswith('HMP') or name.startswith('HMM') or name == 'HMBL':
            who = {'HMP0': 'P0', 'HMP1': 'P1', 'HMM0': 'M0',
                   'HMM1': 'M1', 'HMBL': 'BL'}[name]
            self.hm[who] = ((value & 0xF0) >> 4) - 8
        elif name == 'HMOVE':
            for who in self.pos:
                if self.pos[who] is not None:
                    self.pos[who] += self.hm[who]
        elif name == 'HMCLR':
            for who in self.hm:
                self.hm[who] = 0
        elif name == 'CXCLR':
            self.collisions = {r: 0 for r in
                           ('CXM0P', 'CXM1P', 'CXP0FB', 'CXP1FB', 'CXM0FB',
                            'CXM1FB', 'CXBLPF', 'CXPPMM')}
        return True

    COLLISION_BITS = {
        ('M0', 'P1'): ('CXM0P', 7), ('M0', 'P0'): ('CXM0P', 6),
        ('M1', 'P0'): ('CXM1P', 7), ('M1', 'P1'): ('CXM1P', 6),
        ('P0', 'BL'): ('CXP0FB', 7), ('P0', 'PF'): ('CXP0FB', 6),
        ('P1', 'BL'): ('CXP1FB', 7), ('P1', 'PF'): ('CXP1FB', 6),
        ('M0', 'BL'): ('CXM0FB', 7), ('M0', 'PF'): ('CXM0FB', 6),
        ('M1', 'BL'): ('CXM1FB', 7), ('M1', 'PF'): ('CXM1FB', 6),
        ('BL', 'PF'): ('CXBLPF', 7),
        ('P0', 'P1'): ('CXPPMM', 7), ('M0', 'M1'): ('CXPPMM', 6),
    }

    def collisions_this_line(self):
        """Which of the 15 collision latches the beam would set on this line."""
        pf = self._playfield_bits()
        hit = set()
        for c in range(VISIBLE_WIDTH):
            clock = VISIBLE_START + c
            on = set()
            if pf[c]:
                on.add('PF')
            for who in ('P0', 'P1'):
                if self._object_pixel(who, clock, 8):
                    on.add(who)
            for who in ('M0', 'M1'):
                if self._object_pixel(who, clock, self._missile_width(who)):
                    on.add(who)
            if self._object_pixel('BL', clock, self._ball_width()):
                on.add('BL')
            for pair in self.COLLISION_BITS:
                if pair[0] in on and pair[1] in on:
                    hit.add(pair)
        return hit

    def apply_all(self, events):
        """Commit a scan line's writes without drawing it (blanked lines)."""
        for clock, name, value in events:
            if not name.startswith(self.IMMEDIATE):
                self._apply(name, value)

    # ---- pixel generation for one line ----------------------------------
    def line(self, events=()):
        """Return 160 palette indices for this line, replaying register writes
        as the beam reaches them (writes after clock 68 change the rest of the
        line, which is the whole point of racing the beam)."""
        events = sorted(events)
        px = [0] * VISIBLE_WIDTH          # 0 = background
        ei = 0
        for c in range(VISIBLE_WIDTH):
            clock = VISIBLE_START + c
            while ei < len(events) and events[ei][0] <= clock:
                nm = events[ei][1]
                if not nm.startswith(self.IMMEDIATE):
                    self._apply(nm, events[ei][2])
                ei += 1
            pf = self._playfield_bits()
            bit = pf[c]
            colour = None
            if bit:
                colour = 'PF'
            for who, col in (('P0', 'P0'), ('P1', 'P1')):
                if self._object_pixel(who, clock, 8):
                    colour = col
            for who, col in (('M0', 'P0'), ('M1', 'P1')):
                if self._object_pixel(who, clock, self._missile_width(who)):
                    colour = col
            if self._object_pixel('BL', clock, self._ball_width()):
                colour = 'PF'
            px[c] = {'PF': 2, 'P0': 3, 'P1': 4, None: 0}[colour]
        for pair in self.collisions_this_line():
            reg, bit = self.COLLISION_BITS[pair]
            self.collisions[reg] |= (1 << bit)
        return px

    def _playfield_bits(self):
        """160 booleans: 20 bits per half, each bit 4 clocks, mirrored or not."""
        bits = []
        pf0 = self.reg['PF0'] & 0xF0
        for i in range(4):                       # PF0 uses bits 4..7, reversed
            bits.append((pf0 >> (4 + i)) & 1)
        for i in range(8):
            bits.append((self.reg['PF1'] >> (7 - i)) & 1)
        for i in range(8):
            bits.append((self.reg['PF2'] >> (7 - i)) & 1)
        out = []
        for b in bits:
            out.extend([b] * 4)
        if self.reg['CTRLPF'] & 1:               # reflect
            out = out + out[::-1]
        else:
            out = out + out
        return out[:VISIBLE_WIDTH]

    def _missile_width(self, who):
        n = self.reg['NUSIZ0'] if who == 'M0' else self.reg['NUSIZ1']
        return [1, 2, 4, 8][(n >> 4) & 3]

    def _ball_width(self):
        return [1, 2, 4, 8][(self.reg['CTRLPF'] >> 4) & 3]

    def _object_pixel(self, who, clock, width):
        start = self.pos[who]
        if start is None:
            return False
        if who in ('M0', 'M1', 'BL'):
            en = {'M0': 'ENAM0', 'M1': 'ENAM1', 'BL': 'ENABL'}[who]
            if not (self.reg[en] & 2):
                return False
            return start <= clock < start + width
        g = self.reg['GRP0'] if who == 'P0' else self.reg['GRP1']
        refl = self.reg['REFP0' if who == 'P0' else 'REFP1'] & 8
        nusiz = self.reg['NUSIZ0' if who == 'P0' else 'NUSIZ1']
        copies, size = nusiz & 7, 1
        if copies == 5:
            size = 2
        elif copies == 7:
            size = 4
        span = 8 * size
        offsets = {
            0: [0], 1: [0, 16], 2: [0, 32], 3: [0, 16, 32],
            4: [0, 64], 5: [0], 6: [0, 32, 64], 7: [0],
        }[copies]
        for off in offsets:
            s = start + off
            if s <= clock < s + span:
                i = (clock - s) // size
                bit = (g >> (i if refl else 7 - i)) & 1
                if bit:
                    return True
        return False
