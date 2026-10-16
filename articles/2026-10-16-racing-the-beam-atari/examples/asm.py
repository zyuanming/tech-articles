"""A very small 6507 assembler for the sample kernels. MIT.

Supports exactly the mnemonics the kernels use. Operand forms:
    ('LDA', '#$3F')  immediate        ('STA', '$1B')   zero page
    ('LDA', 'row')   label            ('JMP', 'main')  label
"""
from __future__ import annotations
import re

OPS = {
    ('LDA', 'imm'): 0xA9, ('LDX', 'imm'): 0xA2, ('LDY', 'imm'): 0xA0,
    ('STA', 'zp'): 0x85, ('STX', 'zp'): 0x86, ('STY', 'zp'): 0x84,
    ('STA', 'abs'): 0x8D, ('STX', 'abs'): 0x8E, ('STY', 'abs'): 0x8C,
    ('STA', 'zpx'): 0x95, ('STY', 'zpx'): 0x94,
    ('LDA', 'zp'): 0xA5, ('LDA', 'zpx'): 0xB5,
    ('LDA', 'absy'): 0xB9, ('LDA', 'absx'): 0xBD,
    ('STA', 'absy'): 0x99,
    ('INX', 'imp'): 0xE8, ('INY', 'imp'): 0xC8,
    ('DEX', 'imp'): 0xCA, ('DEY', 'imp'): 0x88,
    ('CPX', 'imm'): 0xE0, ('CPY', 'imm'): 0xC0, ('CMP', 'imm'): 0xC9,
    ('BNE', 'rel'): 0xD0, ('BEQ', 'rel'): 0xF0,
    ('BPL', 'rel'): 0x10, ('BMI', 'rel'): 0x30,
    ('BCC', 'rel'): 0x90, ('BCS', 'rel'): 0xB0,
    ('JMP', 'abs'): 0x4C, ('JSR', 'abs'): 0x20, ('RTS', 'imp'): 0x60,
    ('NOP', 'imp'): 0xEA, ('CLC', 'imp'): 0x18, ('SEC', 'imp'): 0x38,
    ('ADC', 'imm'): 0x69, ('SBC', 'imm'): 0xE9,
    ('AND', 'imm'): 0x29, ('ORA', 'imm'): 0x09, ('EOR', 'imm'): 0x49,
    ('ASL', 'acc'): 0x0A, ('LSR', 'acc'): 0x4A,
    ('TAX', 'imp'): 0xAA, ('TAY', 'imp'): 0xA8,
    ('TXA', 'imp'): 0x8A, ('TYA', 'imp'): 0x98,
    ('INC', 'zp'): 0xE6, ('DEC', 'zp'): 0xC6,
    ('BIT', 'zp'): 0x24,
}
# documented machine cycles, branch-taken adds one
CYC = {
    'LDAimm': 2, 'LDXimm': 2, 'LDYimm': 2, 'STAzp': 3, 'STXzp': 3, 'STYzp': 3,
    'STAabs': 4, 'STXabs': 4, 'STYabs': 4, 'STAzpx': 4, 'STYzpx': 4,
    'LDAzp': 3, 'LDAzpx': 4, 'LDAabsy': 4, 'LDAabsx': 4, 'STAabsy': 5,
    'imp': 2, 'CPXimm': 2, 'CPYimm': 2, 'CMPimm': 2, 'rel': 2, 'JMPabs': 3,
    'JSRabs': 6, 'ADCimm': 2, 'SBCimm': 2, 'ANDimm': 2, 'ORAimm': 2,
    'EORimm': 2, 'acc': 2, 'zp': 5,
}


def _mode(op, operand):
    if operand.endswith(',Y') or operand.endswith(',y'):
        return 'absy'
    if operand.endswith(',X') or operand.endswith(',x'):
        return 'absx'
    if operand.startswith('#'):
        return 'imm'
    if operand == '':
        return 'acc' if op in ('ASL', 'LSR') else 'imp'
    if op in ('BNE', 'BEQ', 'BPL', 'BMI', 'BCC', 'BCS'):
        return 'rel'
    if op in ('JMP', 'JSR'):
        return 'abs'
    if re.fullmatch(r'\$[0-9A-Fa-f]{2}', operand):
        return 'zpx' if op in ('STA', 'STY', 'LDA') and False else \
               ('zp' if int(operand[1:], 16) < 0x100 and op in
                ('STA', 'STX', 'STY', 'LDA', 'INC', 'DEC', 'BIT') else 'abs')
    if re.fullmatch(r'\$[0-9A-Fa-f]{4}', operand):
        return 'abs'
    return 'abs'


def _value(op, operand, mode, labels, pc):
    if mode in ('absx', 'absy'):
        operand = operand[:-2]
    if mode == 'imm':
        return int(operand[1:].lstrip('$'), 16) if operand[1] == '$' else int(operand[1:])
    if mode == 'imp' or mode == 'acc':
        return None
    if operand.startswith('$'):
        return int(operand[1:], 16)
    if operand in labels:
        v = labels[operand]
        if mode == 'rel':
            d = v - (pc + 2)
            assert -128 <= d <= 127, f'branch out of range to {operand}'
            return d & 0xFF
        return v
    return int(operand)


def assemble(program):
    """program: list of (label_or_None, mnemonic, operand_string)."""
    labels, pc, sizes = {}, 0xF000, []
    for label, op, operand in program:
        if label:
            labels[label] = pc
        if op is None:
            continue
        mode = _mode(op, operand)
        size = 1 if mode in ('imp', 'acc') else (2 if mode in ('imm', 'zp', 'rel', 'zpx') else 3)
        sizes.append(size)
        pc += size
    rom, pc, i = [0] * 4096, 0xF000, 0
    cycles = []
    for label, op, operand in program:
        if op is None:
            continue
        mode = _mode(op, operand)
        code = OPS[(op, mode)]
        v = _value(op, operand, mode, labels, pc)
        if mode in ('imp', 'acc'):
            rom[pc - 0xF000] = code
            cycles.append((pc, CYC['acc' if mode == 'acc' else 'imp'], op, operand))
            pc += 1
        elif mode in ('imm', 'zp', 'rel', 'zpx'):
            rom[pc - 0xF000] = code
            rom[pc - 0xF000 + 1] = v & 0xFF
            key = op + mode
            cycles.append((pc, CYC.get(key, 2), op, operand))
            pc += 2
        else:
            rom[pc - 0xF000] = code
            rom[pc - 0xF000 + 1] = v & 0xFF
            rom[pc - 0xF000 + 2] = (v >> 8) & 0xFF
            cycles.append((pc, CYC.get(op + 'abs', 4), op, operand))
            pc += 3
        i += 1
    return rom, labels, cycles
