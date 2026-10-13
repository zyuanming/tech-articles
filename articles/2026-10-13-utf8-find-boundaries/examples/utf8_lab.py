"""UTF-8 educational model and exhaustive, reproducible tests. Python 3.10+.
The strict parser below handles complete byte strings, not untrusted streaming
protocols. Production software should normally use maintained codec libraries.
"""
from pathlib import Path
import codecs, json, sys, unicodedata
SAMPLE = 'A中𠮷B'

def encode_scalar(n):
    if not 0 <= n <= 0x10FFFF or 0xD800 <= n <= 0xDFFF:
        raise ValueError('not a Unicode scalar value')
    if n < 0x80: return bytes([n])
    if n < 0x800: return bytes([0xC0 | n >> 6, 0x80 | n & 63])
    if n < 0x10000: return bytes([0xE0 | n >> 12, 0x80 | n >> 6 & 63, 0x80 | n & 63])
    return bytes([0xF0 | n >> 18, 0x80 | n >> 12 & 63, 0x80 | n >> 6 & 63, 0x80 | n & 63])

def decode_strict(data):
    values=[];i=0
    while i < len(data):
        b=data[i]
        if b < 0x80: width=1;n=b;minimum=0
        elif 0xC2 <= b <= 0xDF: width=2;n=b&31;minimum=0x80
        elif 0xE0 <= b <= 0xEF: width=3;n=b&15;minimum=0x800
        elif 0xF0 <= b <= 0xF4: width=4;n=b&7;minimum=0x10000
        else: raise ValueError('invalid first byte')
        if i+width > len(data): raise ValueError('incomplete sequence')
        for tail in data[i+1:i+width]:
            if tail & 0xC0 != 0x80: raise ValueError('invalid continuation')
            n=(n<<6)|(tail&63)
        if n<minimum or n>0x10FFFF or 0xD800<=n<=0xDFFF:
            raise ValueError('overlong or not a scalar value')
        values.append(n);i+=width
    return values

def next_boundary_of_valid_utf8(data, offset):
    """Only for a suffix of a known valid UTF-8 byte sequence; NOT a validator."""
    if not 0 <= offset <= len(data): raise ValueError('offset out of range')
    while offset<len(data) and data[offset]&0xC0==0x80:
        offset+=1
    return offset

def accepted(data, reference=False):
    try:
        if reference: data.decode('utf-8','strict')
        else: decode_strict(data)
        return True
    except (ValueError,UnicodeDecodeError):return False

def run():
    widths={i:0 for i in range(1,5)}
    for cp in range(0x110000):
        if 0xD800<=cp<=0xDFFF:continue
        b=encode_scalar(cp)
        assert b==chr(cp).encode('utf-8')
        assert decode_strict(b)==[cp]
        assert all(0x80<=t<=0xBF for t in b[1:])
        assert all(t>=0x80 for t in b) if cp>=0x80 else b==bytes([cp])
        widths[len(b)]+=1
    short={}
    for length in [1,2]:
        valid=0
        for n in range(256**length):
            b=n.to_bytes(length,'big');ours=accepted(b)
            assert ours==accepted(b,True),(b.hex(),ours)
            valid+=ours
        short[str(length)]={'strings':256**length,'valid':valid}
    sample=SAMPLE.encode();assert sample.hex(' ').upper()=='41 E4 B8 AD F0 A0 AE B7 42'
    cut_results=[]
    for offset in range(len(sample)+1):
        nxt=next_boundary_of_valid_utf8(sample,offset)
        assert nxt-offset<=3
        suffix=sample[nxt:].decode('utf-8')
        cut_results.append({'cut':offset,'next':nxt,'skipped':nxt-offset,'remaining':suffix})
    # All possible partitions between the sample's nine bytes, not merely two chunks.
    partitions=0
    for mask in range(1<<(len(sample)-1)):
        edges=[0]+[i for i in range(1,len(sample)) if mask>>(i-1)&1]+[len(sample)]
        dec=codecs.getincrementaldecoder('utf-8')('strict')
        parts=[dec.decode(sample[a:b],final=False) for a,b in zip(edges,edges[1:])]
        parts.append(dec.decode(b'',final=True));assert ''.join(parts)==SAMPLE
        partitions+=1
    invalid={
      'C0 AF':'overlong slash','E0 80 AF':'overlong slash in three bytes',
      'ED A0 80':'surrogate U+D800','F4 90 80 80':'above U+10FFFF',
      '80':'lone continuation','E4 B8':'truncated',
      'E4 41 AD':'wrong continuation','F5 80 80 80':'invalid lead',
      'FF':'invalid lead','C1 BF':'invalid lead'}
    for x in invalid:assert not accepted(bytes.fromhex(x)) and not accepted(bytes.fromhex(x),True)
    prefixes=[b'A', bytes.fromhex('E4'),bytes.fromhex('B8'),bytes.fromhex('AD')]
    dec=codecs.getincrementaldecoder('utf-8')('strict');stream=[]
    for chunk in prefixes:
        text=dec.decode(chunk,final=False);stream.append({'bytes':chunk.hex(' ').upper(),'emitted':text,'pending':dec.getstate()[0].hex(' ').upper()})
    assert ''.join(x['emitted'] for x in stream)=='A中'
    assert bytes.fromhex('E4 41 AD').decode('utf-8','replace')=='�A�'
    assert bytes.fromhex('C3 A9').decode('latin-1')=='Ã©'
    assert '文'.encode().hex(' ').upper()=='E6 96 87'
    dec=codecs.getincrementaldecoder('utf-8')('strict')
    assert dec.decode(bytes.fromhex('E4 B8'),final=False)==''
    try: dec.decode(b'',final=True)
    except UnicodeDecodeError: pass
    else: raise AssertionError('incomplete final sequence must fail')
    assert unicodedata.normalize('NFC','e\u0301')=='é'
    assert len('é'.encode())==2 and len('e\u0301'.encode())==3
    result=dict(python=sys.version.split()[0],unicode_database=unicodedata.unidata_version,
        sample=SAMPLE,bytes=sample.hex(' ').upper(),scalar_values_tested=sum(widths.values()),
        length_counts=widths,short_strings=short,all_partitions_tested=partitions,
        cut_results=cut_results,stream=stream,invalid_cases=invalid,
        code_points=[{'char':c,'point':f'U+{ord(c):04X}','decimal':ord(c),'bytes':c.encode().hex(' ').upper()} for c in SAMPLE])
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cut_results','invalid_cases','stream','code_points']},ensure_ascii=False,indent=2))
    print('All assertions passed.')
    return result

if __name__=='__main__':run()
