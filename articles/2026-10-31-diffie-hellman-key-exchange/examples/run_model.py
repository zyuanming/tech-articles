#!/usr/bin/env python3
"""Run the Diffie–Hellman examples the article quotes. Standard library only."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import dh

HERE = Path(__file__).resolve().parent


def main() -> None:
    out = {}

    # The hand-computable example: p = 23, g = 5.
    out["table"] = [dict(k=k, value=v) for k, v in dh.pow_table(23, 5)]
    out["demo"] = dh.key_exchange(23, 5, 6, 15)

    # What an eavesdropper with a pocket calculator would have to do.
    out["brute"] = []
    for a in range(2, 8):
        found, steps = dh.brute_force(5, pow(5, a, 23), 23)
        out["brute"].append(dict(a=a, A=pow(5, a, 23), found=found, steps=steps))

    # The man in the middle: two separate secrets, neither party notices.
    out["mitm"] = dh.mitm(23, 5, 6, 9, 13, 15)

    # Growing primes, actually attacked, actually timed.
    out["cost"] = dh.measure()

    # The real group from RFC 3526.
    p, g = dh.MODP14, 2
    rng = random.Random(1976)
    a = rng.randrange(2, p - 2)
    b = rng.randrange(2, p - 2)
    real = dh.key_exchange(p, g, a, b)
    out["real"] = dict(
        p_digits=len(str(p)), p_bits=p.bit_length(), g=g,
        a_digits=len(str(a)), b_digits=len(str(b)),
        A_hex_digits=len(format(real["A"], "x")),
        shared_equal=real["s_alice"] == real["s_bob"],
        shared_hex=format(real["s_alice"], "x")[:32] + "…",
        p_hex_head=dh.MODP14_HEX[:96], p_hex_tail=dh.MODP14_HEX[-48:],
        p_hex_len=len(dh.MODP14_HEX),
    )

    # Arithmetic, not measurement: how big the square-root attack gets.
    est = []
    for bits in (16, 32, 64, 128, 1024, 2048):
        # In log10 so 2048-bit numbers stay representable.
        log10_steps = (bits / 2) * math.log10(2)
        log10_years = log10_steps - 9 - math.log10(3.15e7)
        est.append(dict(bits=bits, steps_exponent=round(bits / 2, 1),
                        log10_steps=round(log10_steps, 1),
                        steps="10^%.1f" % log10_steps,
                        log10_years=round(log10_years, 1),
                        years="10^%.1f" % log10_years))
    out["estimate"] = est

    # The property that makes the trick work, checked on small numbers.
    checks = []
    for (p_, g_, a_, b_) in ((23, 5, 6, 15), (23, 5, 2, 3), (101, 2, 7, 11),
                             (10007, 5, 1234, 4321)):
        left = pow(pow(g_, a_, p_), b_, p_)
        right = pow(pow(g_, b_, p_), a_, p_)
        checks.append(dict(p=p_, g=g_, a=a_, b=b_, left=left, right=right,
                           equal=left == right))
    out["commute"] = checks

    out["ecdh"] = dh.ecdh_demo()

    (HERE / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")

    d = out["demo"]
    print("demo  : p=%d g=%d a=%d b=%d -> A=%d B=%d shared=%d"
          % (d["p"], d["g"], d["a"], d["b"], d["A"], d["B"], d["s_alice"]))
    print("table :", [r["value"] for r in out["table"]][:11], "...")
    for row in out["cost"]:
        print("cost  : %2d bits, brute %9d steps / %7.3fs, bsgs %6d steps / %.5fs"
              % (row["bits"], row["brute_steps"], row["brute_seconds"],
                 row["bsgs_steps"], row["bsgs_seconds"]))
    print("real  : %d-bit p, %d digits, shared equal: %s"
          % (out["real"]["p_bits"], out["real"]["p_digits"], real["s_alice"] == real["s_bob"]))
    print("est   :", [(e["bits"], e["steps_exponent"]) for e in est])
    e = out["ecdh"]
    print("ecdh  : curve y^2=x^3+7 mod 17, %d affine points, g=%s -> A=%s B=%s s=%s equal=%s"
          % (len(e["points"]), e["g"], e["A"], e["B"], e["s1"], e["equal"]))


if __name__ == "__main__":
    main()
