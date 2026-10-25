"""Original teaching implementation. CC0-1.0. Not production serial firmware."""
def encode(data, compact=False, record=False):
    out = bytearray([0])
    pointer, count = 0, 1
    trace = []
    completed_codes = []
    for index, value in enumerate(data):
        if record:
            before = dict(pointer=pointer, count=count, out=list(out))
        if value == 0:
            out[pointer] = count
            completed_codes.append(pointer)
            pointer = len(out)
            out.append(0)
            count = 1
            action = 'zero'
        else:
            out.append(value)
            count += 1
            action = 'copy'
            if count == 255:
                out[pointer] = count
                completed_codes.append(pointer)
                pointer = len(out)
                out.append(0)
                count = 1
                action = 'full'
        if record:
            trace.append(dict(index=index, value=value, action=action,
                              before=before, pointer=pointer,
                              count=count, out=list(out),
                              completed_codes=list(completed_codes)))
    out[pointer] = count
    # Only omit the unused code after a final FULL block.
    if compact and data and action == 'full':
        out.pop()
    return bytes(out), trace


def decode(encoded, record=False):
    if not encoded:
        raise ValueError('empty encoded frame')
    if 0 in encoded:
        raise ValueError('zero inside encoded frame')
    out, trace = bytearray(), []
    i = 0
    while i < len(encoded):
        start = i
        code = encoded[i]
        end = i + code
        if end > len(encoded):
            raise ValueError('code exceeds frame')
        copied = encoded[i+1:end]
        out.extend(copied)
        add_zero = code < 255 and end < len(encoded)
        if add_zero:
            out.append(0)
        if record:
            trace.append(dict(start=start, code=code, count=code-1,
                              next=end, copied=list(copied),
                              add_zero=add_zero, out=list(out)))
        i = end
    return bytes(out), trace


class Receiver:
    """Delimiter scanner. Empty segments ignored; overflow drops until zero."""
    def __init__(self, maximum=2048, synchronized=True):
        self.buffer = bytearray()
        self.drop = not synchronized
        self.maximum = maximum
        self.packets = []
        self.errors = []

    def feed(self, chunk):
        emitted = []
        for b in chunk:
            if b == 0:
                if self.drop:
                    self.drop = False
                elif self.buffer:
                    try:
                        payload, _ = decode(self.buffer)
                        emitted.append(list(payload))
                        self.packets.append(list(payload))
                    except ValueError as exc:
                        self.errors.append(str(exc))
                self.buffer.clear()
            elif not self.drop:
                if len(self.buffer) >= self.maximum:
                    self.errors.append('frame too long')
                    self.buffer.clear()
                    self.drop = True
                else:
                    self.buffer.append(b)
        return dict(chunk=list(chunk), buffer=list(self.buffer),
                    drop=self.drop, emitted=emitted,
                    packets=list(self.packets), errors=list(self.errors))


def hexbytes(data):
    return ' '.join(f'{b:02X}' for b in data)


def formula(data, compact=False):
    runs = [len(x) for x in data.split(b'\0')]
    q = sum(r // 254 for r in runs)
    saving = int(compact and runs[-1] > 0 and runs[-1] % 254 == 0)
    return len(data) + 1 + q - saving
