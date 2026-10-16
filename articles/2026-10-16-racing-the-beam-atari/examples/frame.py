"""Run a kernel for one NTSC frame and collect the 192 visible lines."""
from __future__ import annotations
from tia import TIA, CPU_CYCLES, VISIBLE_LINES
from cpu6507 import CPU


class Frame:
    def __init__(self, rom, trace=False):
        self.tia = TIA()
        self.tia.clock = 0
        self.cpu = CPU(rom, self.tia)
        self.lines = []
        self.events = []            # per scan line: (colour clock, reg, value)
        self.cycle_use = []
        self.trace = trace

    def run(self, visible_start_line=40):
        line_no = 0
        while line_no < 262 and len(self.lines) < VISIBLE_LINES:
            self.tia.clock = 0
            self.cpu.line_cycles = 0
            self.tia.record = []
            used = 0
            while used < CPU_CYCLES:
                before = self.cpu.cycles
                self.cpu.step()
                used += self.cpu.cycles - before
                if self.cpu.halted:
                    break
            self.cpu.halted = False
            ev = list(self.tia.record)
            self.tia.record = None
            self.events.append(ev)
            self.cycle_use.append(used)
            if line_no >= visible_start_line:
                self.lines.append(self.tia.line(ev))
            else:
                self.tia.apply_all(ev)
            line_no += 1
        return self.lines
