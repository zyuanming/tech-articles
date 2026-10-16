"""Compare source-derived reading units with HTML; code whitespace is significant."""
from __future__ import annotations

import re
from html.parser import HTMLParser

from .blocks import parse_blocks


def plain_inline(text: str) -> str:
    # Source-based Markdown text extraction, independent of the HTML renderer.
    codes = []
    def protect(match):
        codes.append(match[1])
        return '\x00%d\x00' % (len(codes) - 1)
    text = re.sub(r'`([^`]+)`', protect, text)
    text = re.sub(r'\[([^\[\]]+)\]\((?:https?://|mailto:)[^)\s]+\)', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'~~([^~\n]+)~~', r'\1', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m[1])], text)


def normal(text):
    return ' '.join(text.split())


def code_hint(block):
    lang = block.get('lang', '')
    return (lang + ' · ' if lang else '') + '左右滑动查看代码'


class ReadingUnits(HTMLParser):
    """Reading units of the article, ignoring generated chrome.

    A subtree marked ``data-decoration`` is layout the compose stage added --
    a section number, an English eyebrow label, a table of contents, a
    signature block. None of it comes from the source article, so counting it
    as content would fail every article that has any design at all. Skipping it
    keeps the guarantee that matters: source text still has to appear, in
    order, unaltered.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.units = []
        self.current = None
        self.parts = []
        self.root = None
        self.stack = []
        self.decoration_depth = 0
        self.decoration_roots = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'data-decoration' in values:
            self.decoration_depth += 1
            self.decoration_roots.append(len(self.stack))
        if self.decoration_depth:
            if tag not in {'img', 'br', 'hr', 'meta'}:
                self.stack.append(tag)
            return
        style = values.get('style', '').replace(' ', '')
        if tag == 'img':
            self.units.append(('image', values.get('src', ''), values.get('alt', '')))
        if tag == 'hr':
            self.units.append(('hr', ''))
        if tag == 'br' and self.current:
            self.parts.append('\n')
        if tag in {'img', 'br', 'hr', 'meta'}:
            return
        if self.current is None:
            is_code = tag == 'code' and 'display:inline-block' in style
            # Existing quotes use a section with a left border and direct text.
            is_quote = tag == 'section' and 'border-left:3px' in style
            if tag in {'h1', 'h2', 'h3', 'p', 'li', 'th', 'td', 'figcaption'} or is_code or is_quote:
                self.current = 'code' if is_code else 'p' if is_quote else tag
                self.root = len(self.stack)
                self.parts = []
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack:
            return
        if self.stack[-1] != tag:
            return  # syntax errors are reported by the main HTML parser
        if self.decoration_roots and self.decoration_roots[-1] == len(self.stack) - 1:
            self.decoration_roots.pop()
            self.decoration_depth -= 1
            self.stack.pop()
            return
        if self.current and self.root == len(self.stack) - 1:
            text = ''.join(self.parts)
            self.units.append((self.current, text.replace('\xa0', ' ') if self.current == 'code' else normal(text)))
            self.current = None
        self.stack.pop()

    def handle_data(self, text):
        if 'head' in self.stack or self.decoration_depth:
            return
        if self.current:
            self.parts.append(text)
        elif text.strip():
            self.units.append(('unscoped_text', normal(text)))


def expected_units(markdown: str, figures: dict,
                   include_h1: bool = False) -> tuple[list, list]:
    """The reading units the source article promises, and the permitted gaps.

    Separated from ``check_content`` so a debugging tool can print the
    expectation beside what the renderer produced, instead of only being told
    that unit 47 differs.
    """
    expected = []
    differences = []
    for block in parse_blocks(markdown):
        kind = block['kind']
        if kind == 'h1' and not include_h1:
            differences.append('platform_title_omitted')
        elif kind in {'h1', 'h2', 'h3', 'p', 'quote'}:
            expected.append(('p' if kind == 'quote' else kind, normal(plain_inline(block['text']))))
        elif kind in {'ul', 'ol'}:
            expected.extend(('li', normal(plain_inline(item))) for item in block['items'])
        elif kind == 'table':
            expected.extend(('th', normal(plain_inline(cell))) for cell in block['header'])
            expected.extend(('td', normal(plain_inline(cell))) for row in block['rows'] for cell in row)
        elif kind == 'code':
            expected += [('p', code_hint(block)), ('code', block['text'].expandtabs(4))]
            differences.append('code_language_and_scroll_hint')
        elif kind == 'hr':
            expected.append(('hr', ''))
        elif kind == 'image':
            expected.append(('image', block['src'], block['alt']))
            if block['alt']:
                expected.append(('figcaption', normal(plain_inline(block['alt']))))
        elif kind == 'marker':
            figure = figures.get(block['id'])
            if figure:
                expected.append(('image', figure.get('output', ''), figure.get('alt', '')))
                if figure.get('caption'):
                    expected.append(('figcaption', normal(plain_inline(figure['caption']))))
                differences.append('approved_visual:' + block['id'])
    from src.visual.source_rights import source_endnotes
    notes = source_endnotes(figures)
    expected.extend(('p', normal(note)) for note in notes)
    if notes:
        differences.append('source_credits_endnotes')
    return expected, differences


def check_content(html: str, markdown: str, figures: dict, include_h1=False) -> dict:
    expected, differences = expected_units(markdown, figures, include_h1)
    parser = ReadingUnits()
    parser.feed(html)
    parser.close()
    mismatches = [i for i in range(max(len(expected), len(parser.units)))
                  if i >= len(expected) or i >= len(parser.units) or expected[i] != parser.units[i]]
    return {'status': 'FAIL' if mismatches else 'PASS',
            'expected_units': len(expected), 'actual_units': len(parser.units),
            'mismatched_units': mismatches, 'permitted_differences': list(dict.fromkeys(differences))}
