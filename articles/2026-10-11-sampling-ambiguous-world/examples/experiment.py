"""Original aliasing demonstration. Python 3, standard library only.
Run from an empty working directory. Creates low-volume synthetic WAV files.
This is analytic sampling, not an actual microphone/ADC measurement.
"""
from math import cos, pi
from pathlib import Path
import struct, wave

low = [cos(2*pi*1*n/8) for n in range(8)]
high = [cos(2*pi*7*n/8) for n in range(8)]
print('1 Hz:', [round(x, 6) for x in low])
print('7 Hz:', [round(x, 6) for x in high])
print('max error:', max(abs(a-b) for a,b in zip(low,high)))
assert max(abs(a-b) for a,b in zip(low,high)) < 1e-12

def tone(frequency, rate):
    result = []
    for n in range(rate):  # one second
        t = n/rate
        envelope = max(0, min(1, t/.01, (1-t)/.01))
        result.append(round(8191 * envelope * cos(2*pi*frequency*t)))
    return result

def write(name, rate, data):
    with wave.open(str(Path(name)), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(struct.pack('<' + 'h'*len(data), *data))

original = tone(7000, 48000)
alias = original[::6]
reference = tone(1000, 8000)
assert alias == reference
write('original-7khz-48k.wav', 48000, original)
write('aliased-7khz-8k.wav', 8000, alias)
write('reference-1khz-8k.wav', 8000, reference)
print('The two 8 kHz PCM arrays are exactly equal.')
