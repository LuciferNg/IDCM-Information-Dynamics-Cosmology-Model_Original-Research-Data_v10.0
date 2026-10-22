#!/usr/bin/env python3
"""scratch smoke test: verify the fixed brute_val against the explicit F/G split, and the
relaxation dominance condition, WITHOUT the expensive full pass."""
import sys

import numpy as np

SCR = ('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
       'open_problems_fresh/o224_amplitude_complex_phase_layer/scripts')
sys.path.insert(0, SCR)
import lib2i as L

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
KA = np.array(K, dtype=np.int32)
NMUL = np.array(MUL, dtype=np.int32)
hxa = np.array(hx, dtype=np.int32)

E4 = np.zeros((nax, nax, nax, nax), dtype=np.int32)
s2b = NMUL[:, hxa]
for a in range(nax):
    Aa = KA[:, a]
    s2 = s2b[:, a]
    for b in range(nax):
        s3 = NMUL[s2, hxa[b]]
        Wa = Aa * KA[s2, b]
        for c in range(nax):
            s4 = NMUL[s3, hxa[c]]
            W = Wa * KA[s3, c]
            E4[a, b, c, :] = W @ KA[s4, :]


def mermin_terms(nn):
    out = []
    for mask in range(1 << nn):
        eps = tuple((mask >> j) & 1 for j in range(nn))
        w = sum(eps)
        if w % 2 == 0:
            out.append((eps, 1 if (w // 2) % 2 == 0 else -1))
    return out


terms4 = mermin_terms(4)


def fg_vectors(a, ap, b, bp, c, cp):
    F = (E4[a, b, c, :] - E4[ap, bp, c, :] - E4[ap, b, cp, :] - E4[a, bp, cp, :])
    Gv = (E4[ap, bp, cp, :] - E4[ap, b, c, :] - E4[a, bp, c, :] - E4[a, b, cp, :])
    return F, Gv


def brute_val(a, ap, b, bp, c, cp):
    s = [a, ap, b, bp, c, cp]
    best = None
    for d in range(nax):
        for dp in range(nax):
            t = 0
            for e, coef in terms4:
                t += coef * int(E4[s[0 + e[0]], s[2 + e[1]], s[4 + e[2]],
                                   d if e[3] == 0 else dp])
            if best is None or abs(t) > abs(best):
                best = t
    return abs(best)


T4 = [(0, 1, 2, 3, 4, 5), (11, 22, 33, 44, 55, 60), (5, 5, 9, 9, 13, 13),
      (31, 30, 29, 28, 27, 26), (2, 4, 6, 8, 10, 12), (17, 19, 23, 29, 31, 37),
      (0, 61, 1, 60, 2, 59), (44, 44, 45, 45, 46, 46), (7, 8, 9, 10, 11, 12),
      (50, 51, 52, 53, 54, 55)]
ok = 0
for t in T4:
    F, Gv = fg_vectors(*t)
    ext = max(abs(int(F.max()) + int(Gv.max())), abs(int(F.min()) + int(Gv.min())))
    bv = brute_val(*t)
    print(t, 'split', ext, 'brute', bv, 'OK' if ext == bv else 'MISMATCH')
    ok += (ext == bv)
print('R7a-style agreement: %d/%d' % (ok, len(T4)))


def relaxed_pair(a, ap, b, bp):
    A1 = E4[a, b, :, :] - E4[ap, bp, :, :]
    B1 = E4[ap, b, :, :] + E4[a, bp, :, :]
    C1 = E4[ap, bp, :, :] - E4[a, b, :, :]
    D1 = E4[ap, b, :, :] + E4[a, bp, :, :]
    u1 = int((A1.max(axis=1) - D1.min(axis=1)).max())
    u2 = int((C1.max(axis=1) - B1.min(axis=1)).max())
    l1 = int((A1.min(axis=1) - D1.max(axis=1)).min())
    l2 = int((C1.min(axis=1) - B1.max(axis=1)).min())
    return u1 + u2, l1 + l2, (A1, B1, C1, D1)


for t in [(0, 1, 2, 3), (5, 5, 9, 9), (11, 22, 33, 44), (7, 8, 9, 10), (0, 0, 0, 0)]:
    u, l, (A1, B1, C1, D1) = relaxed_pair(*t)
    T = (A1[:, None, :, None] - B1[None, :, :, None]
         + C1[None, :, None, :] - D1[:, None, None, :])
    tmax, tmin = int(T.max()), int(T.min())
    print('relax', t, 'U', u, 'L', l, 'Tmax', tmax, 'Tmin', tmin,
          'dom', (u >= tmax and l <= tmin), 'exact==', max(abs(tmax), abs(tmin)))
