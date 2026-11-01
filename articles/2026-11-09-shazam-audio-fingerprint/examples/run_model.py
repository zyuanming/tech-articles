#!/usr/bin/env python3
"""Run every measurement the Shazam article quotes, write results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import shazam as S

HERE = Path(__file__).resolve().parent
SEEDS = (11, 23, 37)
FAN = 6


def grid(spec, cols, rows, fmax_bin=S.BINS):
    """Max-pool a spectrogram to a coarse grid of integers (dB, rounded)."""
    nf, nb = len(spec), min(fmax_bin, len(spec[0]))
    out = []
    for r in range(rows):
        lo = int(r * nb / rows)
        hi = max(lo + 1, int((r + 1) * nb / rows))
        line = []
        for c in range(cols):
            a = int(c * nf / cols)
            b = max(a + 1, int((c + 1) * nf / cols))
            v = max(spec[t][f] for t in range(a, b) for f in range(lo, hi))
            line.append(round(v))
        out.append(line)
    return out


def main() -> int:
    songs = []
    for seed in SEEDS:
        sig, notes = S.song(seed)
        songs.append(dict(seed=seed, sig=sig, notes=notes))

    db = S.Database()
    per_song = []
    for i, s in enumerate(songs):
        spec = S.spectrogram(s['sig'])
        peaks = S.pick_peaks(spec)
        pairs = S.hashes(peaks, fan=FAN)
        db.add(i, pairs)
        s['spec'] = spec
        s['peaks'] = peaks
        per_song.append(dict(
            seed=s['seed'], seconds=len(s['sig']) / S.SR, notes=len(s['notes']),
            frames=len(spec), bins=S.BINS, freq_step=round(S.SR / S.FRAME, 3),
            frames_per_second=round(S.FPS, 2),
            peaks=len(peaks), peaks_per_second=round(len(peaks) / 8.0, 2),
            hashes=len(pairs), unique_hashes=len({k for k, _t in pairs}),
        ))

    # --- identification, clean and noisy
    snr_rows = []
    for snr in (30, 20, 10, 5, 0, -5, -10, -15, -20):
        r = S.identify(db, songs[1]['sig'], snr)
        other = max([v for (s, _o), v in r['tally'].items() if s != r['song']] or [0])
        snr_rows.append(dict(snr=snr, song=r['song'], votes=r['votes'],
                             runner_up=other, peaks=r['peaks'],
                             hashes=r['hashes'], correct=r['song'] == 1,
                             confident=r['song'] == 1 and r['votes'] >= 10
                             and r['votes'] >= 2 * other))

    # --- the offset histogram, for the query that succeeds
    clean = S.identify(db, songs[1]['sig'], 30)
    tally = clean['tally']
    offsets = {}
    for (song_id, shift), n in tally.items():
        if song_id == 1 and 0 <= shift <= 160:
            offsets[shift] = n
    hist_correct = [offsets.get(i, 0) for i in range(161)]
    # the same query measured against one wrong song only
    wrong = {i: n for (s, i), n in tally.items() if s == 2 and 0 <= i <= 160}
    hist_wrong = [wrong.get(i, 0) for i in range(161)]

    # --- robustness to speed: a turntable that runs 1% fast, same music
    speed_rows = []
    for factor in (1.0, 1.005, 1.01, 1.02, 1.05):
        r = S.identify(db, songs[1]['sig'], 30, factor=factor)
        speed_rows.append(dict(factor=factor, song=r['song'], votes=r['votes'],
                               hashes=r['hashes'], correct=r['song'] == 1,
                               confident=r['votes'] >= 10))

    # --- why not compare waveforms: correlation needs a sample-exact lag
    clip = songs[1]['sig'][94 * S.HOP:94 * S.HOP + 94 * S.HOP]
    lag = 94 * S.HOP
    corr_rows = []
    for label, sig in (('原速', clip),
                       ('10 dB 噪声', S.noise(clip, 10)),
                       ('慢了 1%（转速差）', S.stretch(clip, 1.01)),
                       ('快了 1%', S.stretch(clip, 0.99))):
        best = max(S.correlation(S.noise(clip, 30) if label == '原速' else sig,
                                 songs[1]['sig'], lg)
                   for lg in range(lag - 40, lag + 41))
        corr_rows.append(dict(label=label, peak=round(best, 4)))

    # --- how long does the query have to be
    length_rows = []
    for frames in (16, 31, 47, 63, 94, 125, 157):
        r = S.identify(db, songs[1]['sig'], 30, clip_frames=frames)
        other = max([v for (s2, _o), v in r['tally'].items() if s2 != r['song']] or [0])
        length_rows.append(dict(frames=frames,
                                seconds=round(frames * S.HOP / S.SR, 2),
                                peaks=r['peaks'], hashes=r['hashes'],
                                votes=r['votes'], runner_up=other,
                                confident=r['song'] == 1 and r['votes'] >= 10
                                and r['votes'] >= 2 * other))

    # --- how many hashes a big library would hold (same density)
    library_rows = []
    for dur in (60, 240, 300, 3600):
        n = round(per_song[0]['hashes'] * dur / 8.0)
        library_rows.append(dict(seconds=dur, hashes=n))

    out = dict(
        audio=dict(sample_rate=S.SR, frame=S.FRAME, hop=S.HOP, bins=S.BINS,
                   freq_step=round(S.SR / S.FRAME, 3),
                   frames_per_second=round(S.FPS, 2),
                   note_seconds=S.NOTE, clip_frames=94,
                   clip_seconds=round(94 * S.HOP / S.SR, 3),
                   offset_frames=94),
        fan_out=FAN,
        peak_max=140,
        songs=per_song,
        database=dict(entries=len(db.table),
                      pairs=sum(len(v) for v in db.table.values())),
        identification=snr_rows,
        histogram=dict(correct=hist_correct, wrong=hist_wrong,
                       best_offset=max(range(161), key=lambda i: hist_correct[i]),
                       wrong_total=sum(hist_wrong), wrong_max=max(hist_wrong)),
        speed=speed_rows,
        clip_length=length_rows,
        correlation=corr_rows,
        library=library_rows,
        panels=dict(song=grid(songs[1]['spec'], 150, 56),
                    query=grid(S.spectrogram(S.noise(
                        songs[1]['sig'][94 * S.HOP:94 * S.HOP + 94 * S.HOP], 30)),
                        70, 56),
                    clean=songs[1]['peaks'],
                    song_id=1, seed=songs[1]['seed']),
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('songs', [s['peaks'] for s in per_song], 'db', out['database'])
    print('snr', [(r['snr'], r['votes'], r['runner_up'], r['correct']) for r in snr_rows])
    print('speed', [(r['factor'], r['votes'], r['correct']) for r in speed_rows])
    print('length', [(r['seconds'], r['votes'], r['runner_up'], r['confident']) for r in length_rows])
    print('corr', corr_rows)
    print('best offset', out['histogram']['best_offset'],
          'votes', hist_correct[out['histogram']['best_offset']])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
