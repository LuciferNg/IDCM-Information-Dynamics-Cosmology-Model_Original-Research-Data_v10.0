"""Round-4 probe (scratch): (1) time the vectorised (d,d') separable inner solve; (2) check the
exact window semantics of round 3's eight_anti (whether it forbids an antipodal (d,d') pair);
(3) check the cost of the 4-D coupled variant; (4) verify the vectorised F/G against the frozen
round-3 fg_vectors and against direct 8-term enumeration.
No decision is taken here; nothing is written outside scratch.
"""
import os
import sys
import time

import numpy as np

SCR = ('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/'
       'o224_amplitude_complex_phase_layer/scripts')
sys.path.insert(0, SCR)
import lib2i as L

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
KA = np.array(K, np.int32)
NMUL = np.array(MUL, np.int32)
hxa = np.array(hx, np.int32)
anti = np.array(L.antipodal(U, nax), np.int32).reshape(nax, nax).astype(bool)
print('machine: n =', n, 'nax =', nax, 'vertex axes =', sum(1 for t in types if t == 'vertex'))

t0 = time.time()
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
            W = Wa * KA[s3, c]
            E4[a, b, c, :] = W @ KA[s4, :]
print('E4 build = %.1f s ; max|E4| = %d' % (time.time() - t0, int(np.abs(E4).max())))


def fg_frozen(a, ap, b, bp, c, cp):
    """round-3 fg_vectors (frozen reference)"""
    F = (E4[a, b, c, :] - E4[ap, bp, c, :] - E4[ap, b, cp, :] - E4[a, bp, cp, :])
    Gv = (E4[ap, bp, cp, :] - E4[ap, b, c, :] - E4[a, bp, c, :] - E4[a, b, cp, :])
    return F, Gv


def fg_vec(a, ap, b, bp):
    """vectorised over (c,c',d): returns F,G of shape (62,62,62)"""
    Tab, Tapbp, Tapb, Tabp = E4[a, b], E4[ap, bp], E4[ap, b], E4[a, bp]
    F = (Tab[:, None, :] - Tapbp[:, None, :] - Tapb[None, :, :] - Tabp[None, :, :])
    Gv = (Tapbp[None, :, :] - Tapb[:, None, :] - Tabp[:, None, :] - Tab[None, :, :])
    return F, Gv


t0 = time.time()
bad = 0
for (a, ap, b, bp) in [(0, 1, 2, 3), (5, 5, 9, 9), (11, 22, 33, 44), (61, 60, 59, 58)]:
    F, Gv = fg_vec(a, ap, b, bp)
    for c in (0, 7, 61):
        for cp in (0, 3, 60):
            f0, g0 = fg_frozen(a, ap, b, bp, c, cp)
            if not (np.array_equal(F[c, cp, :], f0) and np.array_equal(Gv[c, cp, :], g0)):
                bad += 1
print('vectorised vs frozen fg mismatch = %d ; 4 tuples time = %.2f s'
      % (bad, time.time() - t0))

# raw separable max over (c,c',d,d') for a few tuples
for (a, ap, b, bp) in [(0, 0, 0, 0), (0, 1, 2, 3), (5, 5, 9, 9)]:
    F, Gv = fg_vec(a, ap, b, bp)
    pos = int((F.max(2) + Gv.max(2)).max())
    neg = int((F.min(2) + Gv.min(2)).min())
    print('raw separable (a,ap,b,bp)=%s -> pos %d, neg %d, |M4|max = %d/120'
          % ((a, ap, b, bp), pos, neg, max(pos, -neg)))


def terms(nterm):
    out = []
    for mask in range(1 << nterm):
        eps = tuple((mask >> j) & 1 for j in range(nterm))
        w = sum(eps)
        if w % 2 == 0:
            out.append((eps, 1 if (w // 2) % 2 == 0 else -1))
    return out


T4 = terms(4)


def brute8(a, ap, b, bp, c, cp, d, dp):
    """direct 8-term enumeration with the frozen s-index rule (exact python ints)"""
    s = [a, ap, b, bp, c, cp]
    t = 0
    for e, coef in T4:
        t += coef * int(E4[s[0 + e[0]], s[2 + e[1]], s[4 + e[2]], d if e[3] == 0 else dp])
    return t


# exhaustive (d,d') check that the separable extremes are right, on the worst raw tuple
for (a, ap, b, bp) in [(0, 0, 0, 0), (0, 1, 2, 3)]:
    F, Gv = fg_vec(a, ap, b, bp)
    pos = int((F.max(2) + Gv.max(2)).max())
    neg = int((F.min(2) + Gv.min(2)).min())
    bf = -10 ** 9
    arg = None
    for c in range(nax):
        for cp in range(nax):
            for d in range(nax):
                for dp in range(nax):
                    t = brute8(a, ap, b, bp, c, cp, d, dp)
                    if abs(t) > bf:
                        bf, arg = abs(t), (c, cp, d, dp)
    print('brute 4-D |M4|max = %d (arg %s) ; separable = %d ; equal = %s'
          % (bf, arg, max(pos, -neg), bf == max(pos, -neg)))

# --- window semantics of round 3's eight_anti: can (d,d') be antipodal? ---
i4 = np.arange(nax)
avail = np.ones(nax, bool)


def window_value_v3(a, ap, b, bp, c, cp):
    """exact copy of round-3 window_max('eight_anti') logic for one 6-tuple: returns (pos, neg, argd)"""
    F, Gv = fg_frozen(a, ap, b, bp, c, cp)
    six = (a, ap, b, bp, c, cp)
    B0 = np.ones(nax, bool)
    for s in six:
        B0[s] = False
    for s in six:
        B0 = B0 & ~anti[s]
    A0 = B0.copy()
    NEG = -10 ** 9
    f = np.where(A0, F, NEG)
    g = np.where(B0, Gv, NEG)
    fn = np.where(A0, F, -NEG)
    gn = np.where(B0, Gv, -NEG)
    hi = [int(i) for i in np.argsort(g)[::-1] if B0[i]][:2]
    lo = [int(i) for i in np.argsort(gn) if B0[i]][:2]
    pos = neg = None
    arg = None
    for d in range(nax):
        if not A0[d]:
            continue
        v = int(f[d]) + int(g[hi[1]]) if d == hi[0] else int(f[d]) + int(g[hi[0]])
        if pos is None or v > pos:
            pos, arg = v, (d, hi[1] if d == hi[0] else hi[0])
        vn = int(fn[d]) + int(gn[lo[1]]) if d == lo[0] else int(fn[d]) + int(gn[lo[0]])
        if neg is None or vn < neg:
            neg = vn
    return pos, neg, arg


def is_antipodal_pair(x, y):
    return bool(anti[x, y])


print()
print('--- v3 eight_anti semantics probe (is an antipodal (d,d\') pair ever used?) ---')
cnt_anti_pair = 0
found = []
pool = [i for i, t in enumerate(types) if t == 'vertex']
for a in pool:
    for ap in pool:
        if ap == a:
            continue
        for b in pool:
            for bp in pool:
                if bp == b:
                    continue
                for c in pool:
                    for cp in pool:
                        if cp == c:
                            continue
                        six = (a, ap, b, bp, c, cp)
                        if len(set(six)) != 6:
                            continue
                        if any(anti[six[i], six[j]] for i in range(6) for j in range(i + 1, 6)):
                            continue
                        pos, neg, arg = window_value_v3(a, ap, b, bp, c, cp)
                        if arg and is_antipodal_pair(arg[0], arg[1]):
                            cnt_anti_pair += 1
                            if len(found) < 3:
                                found.append((six, arg, pos))
print('v3 eight_anti: cases whose realising (d,d\') is antipodal = %d ; examples = %s'
      % (cnt_anti_pair, found))

# --- strict version: all eight pairwise distinct and NO antipodal pair among all eight ---
t0 = time.time()


def window_value_strict(a, ap, b, bp):
    """vectorised over (c,c') with the 4-D coupled (d,d') step.  Returns (pos, neg, arg)."""
    F, Gv = fg_vec(a, ap, b, bp)            # (c,cp,d)
    sixset = {a, ap, b, bp}
    # excluded axes for d: the four outer + c + c'   (built per (c,cp))
    pos = None
    neg = None
    arg = None
    for c in range(nax):
        Fc = F[c]                            # (cp,d)
        Gc = Gv[c]                           # (cp,d)
        for cp in range(nax):
            if cp == c or cp in sixset or c in sixset:
                continue
            ex = sixset | {c, cp}
            okd = np.ones(nax, bool)
            for s in ex:
                okd[s] = False
                okd = okd & ~anti[s]
            f = np.where(okd, Fc[cp], -10 ** 9).astype(np.int32)
            g = np.where(okd, Gc[cp], -10 ** 9).astype(np.int32)
            # pair mask: full pairwise non-antipodal including (d,d')
            Tp = (f[:, None] + g[None, :])
            mask = ~anti
            Tp = np.where(mask, Tp, -10 ** 9)
            v = int(Tp.max())
            if pos is None or v > pos:
                dd = np.unravel_index(int(np.argmax(Tp)), Tp.shape)
                pos, arg = v, (c, cp, int(dd[0]), int(dd[1]))
            Tn = np.where(mask, (f[:, None] + g[None, :]), 10 ** 9)
            vn = int(Tn.min())
            if neg is None or vn < neg:
                neg = vn
    return pos, neg, arg


t0 = time.time()
for (a, ap, b, bp) in [(0, 1, 2, 3), (5, 7, 9, 11)]:
    p, q, ar = window_value_strict(a, ap, b, bp)
    print('strict eight_anti (a,ap,b,bp)=%s -> pos %d neg %d arg %s ; %.1f s'
          % ((a, ap, b, bp), p, q, ar, time.time() - t0))
    t0 = time.time()
print('done')
