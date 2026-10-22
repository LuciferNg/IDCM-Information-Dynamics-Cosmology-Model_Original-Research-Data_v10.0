#!/usr/bin/env python3
"""scratch debug: why do the three antipodal-realisation counts differ (392 / 880 / 1734 / 1794 /
11318)?  Pin the rule and the F/G source for one concrete six-tuple."""
import io
import json
import os
import sys

import numpy as np

HERE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/scripts'
sys.path.insert(0, HERE)
import lib2i as L

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/data'

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
KA = np.array(K, np.int32)
NMUL = np.array(MUL, np.int32)
hxa = np.array(hx, np.int32)
anti = np.array(L.antipodal(U, nax), np.int32).reshape(nax, nax).astype(bool)
pool = [i for i, t in enumerate(types) if t == 'vertex']

E4 = np.zeros((nax, nax, nax, nax), np.int32)
s2b = NMUL[:, hxa]
for a in range(nax):
    Aa = KA[:, a]
    s2 = s2b[:, a]
    for b in range(nax):
        s3 = NMUL[s2, hxa[b]]
        Wa = Aa * KA[s2, b]
        for c in range(nax):
            s4 = NMUL[s3, hxa[c]]
            E4[a, b, c, :] = (Wa * KA[s3, c]) @ KA[s4, :]

X = E4  # full 62^4 frame; indices below are absolute axes

print('lib2i attributes:', [x for x in dir(L) if not x.startswith('_')])


def fg_abs(a, ap, b, bp, c, cp):
    """F(d) and G(d') over ALL 62 axes (A/R/U/V form, absolute indices)."""
    A = X[a, b, c] - X[ap, bp, c]          # (d,)
    Rm = X[ap, b, cp] + X[a, bp, cp]       # (d,)
    Ums = X[ap, bp, cp] - X[a, b, cp]      # (d',)
    V = X[ap, b, c] + X[a, bp, c]          # (d',)
    return A - Rm, Ums - V


def probe_style(six):
    a, ap, b, bp, c, cp = six
    F, Gv = fg_abs(a, ap, b, bp, c, cp)
    B0 = np.ones(nax, bool)
    for s in six:
        B0[s] = False
    for s in six:
        B0 = B0 & ~anti[s]
    A0 = B0.copy()
    NEG = -10 ** 9
    f = np.where(A0, F, NEG)
    g = np.where(B0, Gv, NEG)
    hi = [int(i) for i in np.argsort(g)[::-1] if B0[i]][:2]
    pos, arg = None, None
    for d in range(nax):
        if not A0[d]:
            continue
        v = int(f[d]) + int(g[hi[1]]) if d == hi[0] else int(f[d]) + int(g[hi[0]])
        if pos is None or v > pos:
            pos, arg = v, (d, hi[1] if d == hi[0] else hi[0])
    # exact max over A0 x A0 with d != d'
    best, barg = None, None
    for d in range(nax):
        if not A0[d]:
            continue
        for e in range(nax):
            if e == d or not A0[e]:
                continue
            v = int(F[d]) + int(Gv[e])
            if best is None or v > best:
                best, barg = v, (d, e)
    return pos, arg, best, barg, int(A0.sum()), hi


for six in [(0, 1, 7, 3, 2, 6), (0, 1, 8, 6, 2, 4), (0, 1, 2, 5, 7, 3), (0, 1, 2, 4, 8, 6)]:
    pos, arg, best, barg, nallowed, hi = probe_style(six)
    print()
    print('six =', six, 'allowed d count =', nallowed, 'G top2 =', hi)
    print('  probe-style pos =', pos, 'arg =', arg, 'antipodal(arg) =', bool(arg and anti[arg[0], arg[1]]))
    print('  exact best =', best, 'at', barg, 'antipodal =', bool(barg and anti[barg[0], barg[1]]))
    if arg:
        print('  probe pos == exact best ?', pos == best)
