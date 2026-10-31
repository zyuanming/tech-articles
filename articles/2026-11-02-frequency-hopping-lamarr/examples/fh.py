"""A frequency-hopping link and the jammers that chase it. MIT.

This is a model, not a measurement of real radio. It answers one question with
numbers: when the transmitter changes channel `H` times a second and the jammer
has `P` watts to spend, how much of the link survives?

The physics is one line: a jammer that covers a fraction `f` of the band with
total power `P_J` puts `P_J / (f * N)` into each channel; the signal puts `P_S`
into the one channel it is using. A hop dies when J/S exceeds 10 dB.

No third-party imports.
"""
from __future__ import annotations

import math

CHANNELS = 88          # the patent's number: one per piano key
HOPS = 4000            # hops per run
JSR_LIMIT = 10.0       # 10 dB: a hop is lost when J/S goes above this


class Rand:
    """Linear congruential generator. Reproducible without the `random` module."""

    def __init__(self, seed: int = 1942):
        self.x = seed & 0x7FFFFFFF

    def next(self) -> float:
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x / 0x7FFFFFFF


def lfsr_channels(n: int = HOPS, channels: int = CHANNELS,
                  taps=(16, 14, 13, 11), seed: int = 0xACE1) -> list:
    """A 16-bit LFSR reduced modulo `channels` to pick a hop channel.

    Not a generator you would ship; it is here because the 1941 patent drove the
    hops from a paper strip, and a shift register is the cheapest stand-in.
    """
    state = seed
    mask = (1 << 16) - 1
    out = []
    while len(out) < n:
        bit = 0
        for t in taps:
            bit ^= (state >> (t - 1)) & 1
        state = ((state << 1) | bit) & mask
        # fold the register before taking a byte: consecutive LFSR states are
        # correlated, and 88 shares a factor with 2^16
        v = (state ^ (state >> 6) ^ (state >> 11)) & 0xFF
        if v < channels:             # rejection sampling keeps it uniform
            out.append(v)
    return out


def fixed_channel(n: int = HOPS) -> list:
    return [0] * n


def jsr(jsr_total: float, coverage: float, channels: int = CHANNELS) -> float:
    """Jammer power inside one channel, relative to the signal.

    The same total jammer power spread over `coverage * channels` channels is
    weaker in each of them.
    """
    return jsr_total / (coverage * channels)


def lost(jsr_total: float, coverage: float, channels: int = CHANNELS) -> bool:
    return jsr(jsr_total, coverage, channels) > JSR_LIMIT


# --- jammer geometries -------------------------------------------------------
# Each returns a list of bools: was the hop's channel inside the jammer's slice
# at that instant, i.e. did the jammer radiate into the channel we used?

def park(seq: list, coverage: float, channels: int = CHANNELS) -> list:
    blocked = set(range(int(round(coverage * channels))))
    return [ch in blocked for ch in seq]


def full_band(seq: list) -> list:
    return [True] * len(seq)


def sweep(seq: list, width: int = 2, channels: int = CHANNELS) -> list:
    out = []
    pos = 0
    blocked = set()
    for i, ch in enumerate(seq):
        if i % width == 0:
            blocked = {(pos + k) % channels for k in range(width)}
            pos = (pos + width) % channels
        out.append(ch in blocked)
    return out


def follower(seq: list, delay: float, hop_rate: float, tol: float = 0.5,
             jitter: float = 0.5, seed: int = 7) -> list:
    """A jammer that hears the hop and retunes to it.

    It only needs to cover part of the hop to kill a packet: with a rate-1/2
    code, losing more than `tol` of the hop costs the packet. `jitter` is the
    spread in reaction time around `delay` (uniform ±50% by default).
    """
    rnd = Rand(seed)
    hop_len = 1.0 / hop_rate
    out = []
    for _ in seq:
        d = delay * (1.0 - jitter + 2 * jitter * rnd.next())
        out.append(d <= tol * hop_len)
    return out


def sync_mask(seq: list, offset: float) -> list:
    shift = int(round(offset))
    return [seq[i - shift] == seq[i] if i >= shift else False for i in range(len(seq))]


def per(hit: list, jsr_total: float, coverage: float,
        synced: list | None = None) -> dict:
    """A hop is lost when the jammer radiates into it *and* is loud enough,
    or when the two sides are out of sync."""
    if synced is None:
        synced = [True] * len(hit)
    strong = jsr(jsr_total, coverage) > JSR_LIMIT
    lost_n = sum(1 for h, s in zip(hit, synced) if (h and strong) or not s)
    return dict(hops=len(hit), lost=lost_n, per=round(lost_n / len(hit), 4),
                good=len(hit) - lost_n, jsr=round(jsr(jsr_total, coverage), 2),
                strong=strong)


# --- the runs ----------------------------------------------------------------

def compare_modes(hop_rate: float = 1000.0) -> list:
    """Every jammer here is exactly loud enough to kill the hops it reaches.
    The two columns that matter: what it costs in power, and how many hops die.
    """
    hop = lfsr_channels()
    fix = fixed_channel()
    rows = []

    def row(mode, jammer, coverage, hit, note):
        rows.append(dict(mode=mode, jammer=jammer,
                         coverage=('1/88' if abs(coverage * CHANNELS - 1) < 1e-9
                                   else '%.2f' % coverage if coverage < 0.01
                                   else '%d/88' % round(coverage * CHANNELS)),
                         needed=power_needed(coverage),
                         per=round(sum(1 for h in hit if h) / len(hit), 4),
                         note=note))

    row('定频', '窄带瞄准', 1 / CHANNELS, park(fix, 1 / CHANNELS),
        '干扰者知道你的频点')
    row('定频', '全频带', 1.0, full_band(fix), '要压住 88 个频点')
    row('跳频', '挡住 20% 的频点', 0.2, park(hop, 0.2), '每跳有 1/5 的机会撞上')
    row('跳频', '扫频 2 个频点', 2 / CHANNELS, sweep(hop), '窄带快速扫过整个频段')
    row('跳频', '全频带', 1.0, full_band(hop), '功率摊到 88 个频点')
    row('跳频', '跟随（反应 0.2 ms）', 1 / CHANNELS,
        follower(hop, 0.0002, hop_rate), '追得上每一跳')
    row('跳频', '跟随（反应 2 ms）', 1 / CHANNELS,
        follower(hop, 0.002, hop_rate), '每跳 1 ms，追不上')
    return rows


def power_needed(coverage: float, channels: int = CHANNELS) -> float:
    """Total jammer power (relative to the signal) that breaks one hop."""
    return round(JSR_LIMIT * coverage * channels, 1)


def power_table() -> list:
    return [
        dict(case='定频，瞄准 1 个频点', coverage=1 / CHANNELS,
             needed=power_needed(1 / CHANNELS)),
        dict(case='跳频，挡住 10% 的频点', coverage=0.1,
             needed=power_needed(0.1)),
        dict(case='跳频，挡住 20% 的频点', coverage=0.2,
             needed=power_needed(0.2)),
        dict(case='跳频，挡住一半', coverage=0.5, needed=power_needed(0.5)),
        dict(case='跳频，全频带压制', coverage=1.0, needed=power_needed(1.0)),
    ]


def reaction_curve(delays=(0.00005, 0.0001, 0.0002, 0.0003, 0.0005, 0.0008,
                           0.001, 0.002, 0.005),
                   hop_rate: float = 1000.0) -> list:
    seq = lfsr_channels()
    rows = []
    for d in delays:
        rows.append(dict(delay=d, share_of_hop=round(d * hop_rate, 3),
                         per=per(follower(seq, d, hop_rate), 30.0,
                                1 / CHANNELS)['per']))
    return rows


def hop_rate_table(rates=(10, 50, 240, 500, 1000, 2000, 5000),
                   reaction: float = 0.002) -> list:
    """How many hops a 2 ms reaction time spans, at each hop rate. The
    ratio d/T is what the reaction curve above is plotted against."""
    rows = []
    for r in rates:
        share = reaction * r
        rows.append(dict(rate=r, hop_ms=round(1000 / r, 2),
                         hops_in_reaction=round(share, 2),
                         caught=share < 0.5))
    return rows


def sync_curve(offsets=(0, 1, 2, 3)) -> list:
    seq = lfsr_channels()
    rows = []
    for off in offsets:
        rows.append(dict(offset=off,
                         aligned=round(sum(sync_mask(seq, off)) / len(seq), 4)))
    return rows


def chi_square(seq: list, channels: int = CHANNELS) -> float:
    """Uniformity check: for 88 channels the expected value is 87."""
    counts = [0] * channels
    for ch in seq:
        counts[ch] += 1
    expected = len(seq) / channels
    return round(sum((c - expected) ** 2 / expected for c in counts), 1)


def sequence_stats(seq: list) -> dict:
    counts = {}
    for ch in seq:
        counts[ch] = counts.get(ch, 0) + 1
    vals = list(counts.values())
    mean = sum(vals) / len(vals)
    var = sum((c - mean) ** 2 for c in vals) / len(vals)
    return dict(hops=len(seq), used=len(counts), min=min(vals), max=max(vals),
                mean=round(mean, 2), std=round(math.sqrt(var), 2),
                same_as_previous=sum(1 for a, b in zip(seq, seq[1:]) if a == b),
                chi2=chi_square(seq))


def waterfall(seq: list, hops: int = 100) -> list:
    return [[i, ch] for i, ch in enumerate(seq)][:hops]


def gain_curve() -> list:
    return [[n, round(10 * math.log10(n), 2)] for n in (2, 4, 8, 16, 32, 64, 88, 128, 256)]


def strip_rows() -> list:
    """What the eight rows actually drive, per the patent's own description.

    Row H is the indicator lamp. Rows A-G close seven switches at the
    transmitter; the receiving station only has four condensers, D-G, so the
    A/B/C channels are transmitted but never received -- that is the
    deception channel the patent describes.
    """
    return [dict(row='A', role='发端电容 24a', rx='收端没有'),
            dict(row='B', role='发端电容 24b', rx='收端没有'),
            dict(row='C', role='发端电容 24c', rx='收端没有'),
            dict(row='D', role='发端电容 24d', rx='收端 24′d'),
            dict(row='E', role='发端电容 24e', rx='收端 24′e'),
            dict(row='F', role='发端电容 24f', rx='收端 24′f'),
            dict(row='G', role='发端电容 24g', rx='收端 24′g'),
            dict(row='H', role='指示灯开关 42', rx='指示灯 43')]


def channel_counts() -> list:
    """Processing gain for the channel counts that actually appear: the four
    the receiver can hear, the seven the transmitter can send, and the 88 the
    patent extrapolates to from a player-piano roll."""
    out = []
    for n, why in ((4, '收端能收到的频点数'),
                   (7, '发端能发出的频点数'),
                   (88, '专利从钢琴卷纸推到上限')):
        out.append(dict(channels=n, gain_db=round(10 * math.log10(n), 2),
                        needed=round(JSR_LIMIT * n, 1), why=why))
    return out


def power_curve() -> list:
    out = []
    for c in (1 / CHANNELS, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0):
        out.append(dict(coverage=round(c, 4), channels=round(c * CHANNELS, 1),
                        needed=power_needed(c)))
    return out


def measure() -> dict:
    seq = lfsr_channels()
    hop = seq
    parked = park(hop, 0.2)
    return dict(
        channels=CHANNELS,
        hops=HOPS,
        hop_rate=1000.0,
        jsr_limit=JSR_LIMIT,
        sequence=sequence_stats(seq),
        waterfall=waterfall(seq),
        waterfall_parked=[[i, ch, bool(j)] for (i, ch), j
                          in zip(waterfall(seq, 60), parked[:60])],
        compare=compare_modes(),
        power=power_table(),
        power_curve=power_curve(),
        reaction=reaction_curve(),
        rates=hop_rate_table(),
        sync=sync_curve(),
        gain=round(10 * math.log10(CHANNELS), 2),
        gain_curve=gain_curve(),
        strip=strip_rows(),
        channel_counts=channel_counts(),
    )
