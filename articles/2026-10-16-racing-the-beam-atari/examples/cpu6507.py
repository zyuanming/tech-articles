"""A small 6507 interpreter: only the opcodes the sample kernels need, but
each one burns its documented machine-cycle cost, because on this machine the
cycle count *is* the picture. MIT."""
from __future__ import annotations

CYCLES = {
    0xA9: 2, 0xA2: 2, 0xA0: 2,            # LDA/LDX/LDY #imm
    0x85: 3, 0x86: 3, 0x84: 3,            # STA/STX/STY zp
    0x8D: 4, 0x8E: 4, 0x8C: 4,            # STA/STX/STY abs
    0x95: 4, 0x94: 4,                     # STA zp,X / STY zp,X
    0xB9: 4, 0xBD: 4,                     # LDA abs,Y / abs,X
    0x99: 5,                              # STA abs,Y
    0xA5: 3, 0xB5: 4,                     # LDA zp / zp,X
    0xE8: 2, 0xC8: 2, 0xCA: 2, 0x88: 2,   # INX INY DEX DEY
    0xC0: 2, 0xE0: 2, 0xC9: 2,            # CPY # CPX # CMP #
    0xD0: 2, 0xF0: 2,                     # BNE BEQ (+1 when taken, +1 page)
    0x4C: 3, 0x20: 6, 0x60: 6,            # JMP abs, JSR, RTS
    0xEA: 2,                              # NOP
    0x18: 2, 0x38: 2,                     # CLC SEC
    0x69: 2, 0xE9: 2,                     # ADC # SBC #
    0x29: 2, 0x09: 2, 0x49: 2,            # AND # ORA # EOR #
    0x0A: 2, 0x4A: 2,                     # ASL A, LSR A
    0xAA: 2, 0xA8: 2, 0x8A: 2, 0x98: 2,   # TAX TAY TXA TYA
    0xE6: 5, 0xC6: 5,                     # INC zp DEC zp
    0x24: 3, 0x10: 2, 0x30: 2,            # BIT zp, BPL, BMI
    0x90: 2, 0xB0: 2,                     # BCC BCS
    0xA0 + 0x100: 2,
}
BRANCH = {0xD0, 0xF0, 0x10, 0x30, 0x90, 0xB0}
IMPLIED = {0xE8, 0xC8, 0xCA, 0x88, 0xEA, 0x18, 0x38, 0x0A, 0x4A, 0xAA, 0xA8, 0x8A, 0x98}


class CPU:
    def __init__(self, rom, tia, ram=None):
        self.rom = list(rom)              # 4096 bytes, mapped at $F000
        self.tia = tia
        self.ram = list(ram or [0] * 128)
        self.a = self.x = self.y = 0
        self.sp = 0xFF
        self.pc = 0xF000
        self.cycles = 0
        self.line_cycles = 0
        self.flag_z = False
        self.flag_c = False
        self.flag_n = False
        self.halted = False

    # ---- memory ---------------------------------------------------------
    def read(self, addr):
        if addr < 0x80:
            return 0
        if addr < 0x100:
            return self.ram[addr - 0x80]
        if addr >= 0xF000:
            return self.rom[addr - 0xF000]
        return 0

    def write(self, addr, value, at_cycle=None):
        value &= 0xFF
        if at_cycle is not None:
            self.tia.clock = at_cycle
        if addr < 0x80:
            self.tia.write(addr, value)
            if addr == self.tia.reg_addr('WSYNC'):
                self.halted = True
        elif addr < 0x100:
            self.ram[addr - 0x80] = value

    # ---- execution ------------------------------------------------------
    def step(self):
        op = self.read(self.pc)
        if op not in CYCLES:
            raise NotImplementedError(f'opcode ${op:02X} at ${self.pc:04X}')
        n = CYCLES[op]
        imm = self.read((self.pc + 1) & 0xFFFF)
        if op in BRANCH:
            taken = ((op == 0xD0 and not self.flag_z) or
                     (op == 0xF0 and self.flag_z) or
                     (op == 0x10 and not self.flag_n) or
                     (op == 0x30 and self.flag_n) or
                     (op == 0x90 and not self.flag_c) or
                     (op == 0xB0 and self.flag_c))
            self.pc = (self.pc + 2) & 0xFFFF
            if taken:
                self.pc = (self.pc + _signed(imm)) & 0xFFFF
                n += 1
        elif op in (0x4C,):
            self.pc = imm | (self.read((self.pc + 2) & 0xFFFF) << 8)
        elif op == 0x20:
            lo, hi = imm, self.read((self.pc + 2) & 0xFFFF)
            ret = (self.pc + 2) & 0xFFFF
            self._push((ret >> 8) & 0xFF); self._push(ret & 0xFF)
            self.pc = lo | (hi << 8)
        elif op == 0x60:
            lo = self._pull(); hi = self._pull()
            self.pc = ((hi << 8) | lo) + 1
        elif op in (0x8D, 0x8E, 0x8C):
            addr = imm | (self.read((self.pc + 2) & 0xFFFF) << 8)
            self.write(addr, {0x8D: self.a, 0x8E: self.x, 0x8C: self.y}[op],
                       self.line_cycles + n - 1)
            self.pc = (self.pc + 3) & 0xFFFF
        elif op == 0x99:
            addr = (imm | (self.read((self.pc + 2) & 0xFFFF) << 8)) + self.y
            self.write(addr, self.a, self.line_cycles + n - 1)
            self.pc = (self.pc + 3) & 0xFFFF
        elif op in (0xB9, 0xBD):
            base = imm | (self.read((self.pc + 2) & 0xFFFF) << 8)
            self.a = self.read((base + (self.y if op == 0xB9 else self.x)) & 0xFFFF)
            self._nz(self.a); self.pc = (self.pc + 3) & 0xFFFF
        else:
            self.pc = (self.pc + (1 if op in IMPLIED else 2)) & 0xFFFF
            self._exec(op, imm, n)
        self.cycles += n
        self.line_cycles += n
        return n

    def _exec(self, op, imm, n=2):
        zaddr = None
        wclock = self.line_cycles + n - 1 if op in (0x85, 0x86, 0x84, 0x95, 0x94) else None
        if op in (0x85, 0x86, 0x84, 0xA5, 0xB5, 0x95, 0x94, 0xE6, 0xC6, 0x24):
            zaddr = imm
        if op == 0xA9:
            self.a = imm; self._nz(self.a)
        elif op == 0xA2:
            self.x = imm; self._nz(self.x)
        elif op == 0xA0:
            self.y = imm; self._nz(self.y)
        elif op == 0x85:
            self.write(zaddr, self.a, wclock)
        elif op == 0x86:
            self.write(zaddr, self.x, wclock)
        elif op == 0x84:
            self.write(zaddr, self.y, wclock)
        elif op == 0x95:
            self.write((zaddr + self.x) & 0xFF, self.a, wclock)
        elif op == 0x94:
            self.write((zaddr + self.x) & 0xFF, self.y, wclock)
        elif op == 0xA5:
            self.a = self.read(zaddr); self._nz(self.a)
        elif op == 0xB5:
            self.a = self.read((zaddr + self.x) & 0xFF); self._nz(self.a)
        elif op == 0xE6:
            v = (self.read(zaddr) + 1) & 0xFF; self.write(zaddr, v); self._nz(v)
        elif op == 0xC6:
            v = (self.read(zaddr) - 1) & 0xFF; self.write(zaddr, v); self._nz(v)
        elif op == 0x24:
            self.flag_z = (self.read(zaddr) & self.a) == 0
            self.flag_n = bool(self.read(zaddr) & 0x80)
        elif op == 0xE8:
            self.x = (self.x + 1) & 0xFF; self._nz(self.x)
        elif op == 0xC8:
            self.y = (self.y + 1) & 0xFF; self._nz(self.y)
        elif op == 0xCA:
            self.x = (self.x - 1) & 0xFF; self._nz(self.x)
        elif op == 0x88:
            self.y = (self.y - 1) & 0xFF; self._nz(self.y)
        elif op == 0xC0:
            self._cmp(self.y, imm)
        elif op == 0xE0:
            self._cmp(self.x, imm)
        elif op == 0xC9:
            self._cmp(self.a, imm)
        elif op == 0xEA:
            pass
        elif op == 0x18:
            self.flag_c = False
        elif op == 0x38:
            self.flag_c = True
        elif op == 0x69:
            self._adc(imm)
        elif op == 0xE9:
            self._adc(imm ^ 0xFF)
        elif op == 0x29:
            self.a &= imm; self._nz(self.a)
        elif op == 0x09:
            self.a |= imm; self._nz(self.a)
        elif op == 0x49:
            self.a ^= imm; self._nz(self.a)
        elif op == 0x0A:
            self.flag_c = bool(self.a & 0x80); self.a = (self.a << 1) & 0xFF; self._nz(self.a)
        elif op == 0x4A:
            self.flag_c = bool(self.a & 1); self.a >>= 1; self._nz(self.a)
        elif op == 0xAA:
            self.x = self.a; self._nz(self.x)
        elif op == 0xA8:
            self.y = self.a; self._nz(self.y)
        elif op == 0x8A:
            self.a = self.x; self._nz(self.a)
        elif op == 0x98:
            self.a = self.y; self._nz(self.a)
        else:
            raise NotImplementedError(f'opcode ${op:02X}')

    def _adc(self, v):
        t = self.a + v + (1 if self.flag_c else 0)
        self.flag_c = t > 0xFF
        self.a = t & 0xFF
        self._nz(self.a)

    def _cmp(self, reg, v):
        self.flag_c = reg >= v
        self._nz((reg - v) & 0xFF)

    def _nz(self, v):
        self.flag_z = (v & 0xFF) == 0
        self.flag_n = bool(v & 0x80)

    def _push(self, v):
        self.write(0x100 + self.sp, v); self.sp = (self.sp - 1) & 0xFF

    def _pull(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.read(0x100 + self.sp)


def _signed(b):
    return b - 256 if b > 127 else b
