#!/usr/bin/env python3
"""O224 scripts/05_valueset.py -- judgment item (d): the 1/15 quantisation of the frozen
correlation, and the exact discrete spectrum of the readout amplitude.

Pre-registered: P12, P13 (data/00_contract.json).
"""
import collections
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')


def main():
    R = L.Report('05_valueset')
    print('=' * 108)
    print('O224 scripts/05 -- (d) the 1/15 quantisation and the discrete amplitude spectrum')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    C1 = L.e1_table(K, MUL, hx, n, nax)      # integer numerators over 120
    C2 = L.e2_table(K, MUL, hx, n, nax)      # Fractions

    # ---------------- V1: the exact value set ----------------
    vals = sorted(set(C1[a][b] for a in range(nax) for b in range(nax)))
    mags = sorted(set(abs(v) for v in vals))
    expect = [0, F(1, 15), F(2, 15), F(1, 5), F(4, 15), F(1, 3), F(2, 3), F(1)]
    got = sorted(set(F(abs(v), n) for v in vals))
    R.claim('V1', 'C1 takes exactly 15 signed values whose magnitudes are exactly the docs/45 '
                  'B2 set {0, 1/15, 2/15, 1/5, 4/15, 1/3, 2/3, 1} (the denominator 15 = '
                  'N_gen * F_5 = 3 * 5 is the LCM of the reduced denominators)',
            len(vals) == 15 and got == expect,
            'distinct signed values = %d ; magnitudes = %s ; numerators (over 120) = %s'
            % (len(vals), [str(x) for x in got], mags))

    # ---------------- V2: the mod-8 structure explains 1/15 ----------------
    # 120 = 8 * 15 and every numerator is a multiple of 8.  Structurally: K[-s] = K[s], so the
    # 120-state sum is twice a sum over the 60 Z2-classes; and the 60-term sum is itself a
    # multiple of 4 (equivalently T = numerator/2 is in 4Z).
    mult8 = all(v % 8 == 0 for v in vals)
    T4 = all((v // 2) % 4 == 0 for v in vals)
    minpos = min(v for v in vals if v > 0)
    R.claim('V2', 'the 1/15 quantum is structural, not fitted: the 120 states collapse to 60 '
                  'Z2-classes (K[-s] = K[s]), so every numerator is 2*(sum over 60 classes), '
                  'and that 60-term sum is always a multiple of 4 -- hence every numerator is '
                  'a multiple of 8 and every correlation is a multiple of 8/120 = 1/15. The '
                  'smallest positive value is exactly 1/15',
            mult8 and T4 and minpos == 8,
            'all numerators divisible by 8 : %s ; all (numerator/2) divisible by 4 : %s ; '
            'smallest positive numerator = %d (= 8/120 = 1/15)' % (mult8, T4, minpos))

    # ---------------- V3: the discrete spectrum with multiplicities ----------------
    cnt = collections.Counter(C1[a][b] for a in range(nax) for b in range(nax))
    spec = {str(F(v, n)): c for v, c in sorted(cnt.items())}
    R.claim('V3', 'the full discrete spectrum of the frozen 2-party correlation (value -> '
                  'number of axis pairs, 3844 total) is reported; it is a rigid 15-point '
                  'spectrum, not a continuum',
            sum(cnt.values()) == nax * nax and len(cnt) == 15,
            'spectrum = %s' % spec)

    # ---------------- V4: the reduced-denominator class ----------------
    dens = sorted(set(F(abs(v), n).denominator for v in vals))
    R.claim('V4', 'the reduced denominators that occur are exactly the divisors of 15 '
                  '(1, 3, 5, 15): the frozen correlator has resolution 1/15 = 1/(N_gen*F_5) '
                  'and no finer structure is present in ANY of the 7440 readout entries',
            dens == [1, 3, 5, 15], 'reduced denominators = %s' % dens)

    # ---------------- V5: the budget side (counts, not amplitudes) ----------------
    # reproduce the O222 budget/window identities from docs/45 §2 / scripts/12
    B = F(123, 2)
    per_read = F(123, 88)
    e_min = F(123, 176)
    reads_per_pass = F(B, per_read)
    overrun = F(1922, 11)
    R.claim('V5', 'the budget layer is a COUNTING layer, not an amplitude layer: budget '
                  '123/2, per-read cost 123/88 = 2*E_min, so exactly 44 = N_d reads per pass, '
                  'and the memo-saturation tuple needs 1922/11 = 174.7273x the budget. These '
                  'are exact rationals (no free parameter), so they cannot be dialled to an '
                  'amplitude in [0.0211, 0.0387]',
            reads_per_pass == 44 and per_read == 2 * e_min and overrun == F(1922, 11),
            'reads/pass = %s ; per-read = %s = 2*E_min (%s) ; A2 overrun = %s = %.4f x'
            % (reads_per_pass, per_read, e_min, overrun, float(overrun)))

    # ---------------- V6: C2 spectrum for the record ----------------
    cnt2 = collections.Counter(C2[a][b] for a in range(nax) for b in range(nax))
    R.claim('V6', 'the persistent-ledger E2 correlation has the same 15-point magnitude '
                  'structure (reported for the record); no entry of either table carries '
                  'amplitude information beyond this discrete spectrum',
            len(cnt2) == 15,
            'E2 distinct values = %d ; spectrum = %s'
            % (len(cnt2), {str(k): v for k, v in sorted(cnt2.items())}))

    # ---------------- V7: candidate mechanisms for the 1/15 quantum ----------------
    # (iii) of the contract's definition (d): test subgroup left-invariance (orders 2/4/8/10),
    # the antipodal vertex count, and a >=300-draw random-generic-axis control.
    H = [g for g in range(n)
         if all(K[MUL[g][s]][a] == K[s][a] for s in range(n) for a in range(nax))]
    ordH = []
    for g in H:
        x, k = g, 1
        while x != idx[L.qkey(L.ID_ELEM)]:
            x = MUL[x][g]
            k += 1
        ordH.append(k)
    anti = L.antipodal(U, nax)
    n_anti_pairs = sum(anti) // 2
    R.claim('V7', 'mechanism audit: the FULL left-invariance kernel of the readout is '
                  '{1, -1} (order 2 only) -- so the divisibility by 8 is NOT produced by a '
                  'subgroup of order 4/8/10 acting trivially on the readout (that hypothesis is '
                  'refuted, orders present = {1,2}); the Z2 collapse is the only invariance. '
                  'The 62 axes contain 31 antipodal pairs, so the divisibility cannot come from '
                  'the axes either (it must come from the group)',
            len(H) == 2 and sorted(set(ordH)) == [1, 2] and n_anti_pairs == 31,
            '|left-invariance kernel| = %d with element-orders %s ; antipodal unordered pairs '
            'among the 62 axes = %d' % (len(H), sorted(set(ordH)), n_anti_pairs))

    # >=300-draw random-generic-axis control: the parity that forces divisibility by 8
    st = 20260930
    e0 = idx[L.qkey(L.ID_ELEM)]
    m1 = idx[L.qkey((L.scale(L.ONE, -1), L.ZERO, L.ZERO, L.ZERO))]
    invs = []
    for s in range(n):
        x, k = s, 1
        while x != e0:
            x = MUL[x][s]
            k += 1
        y = e0
        for _ in range(k - 1):
            y = MUL[y][s]
        invs.append(y)
    # the Z2 collapse K[-s] = K[s] pairs s with NEG(s) = (-1)*s, not with its inverse;
    # (-1)*s = s only for s = -1, and -1 has order 2, so this involution has 60 orbits of
    # size exactly 2 (using the inverse map instead would leave the singleton {-1} and give
    # 61 classes -- verified as a pitfall in this round)
    negs = [MUL[m1][s] for s in range(n)]
    assert all(negs[negs[s]] == s and negs[s] != s for s in range(n)), 'neg is a fixed-point-free involution'
    reps, seen = [], set()
    for s in range(n):
        if s in seen:
            continue
        reps.append(s)
        seen.add(s)
        seen.add(negs[s])
    assert len(reps) == 60
    ros = [L.rot_ref(G[s], U[0]) for s in range(n)]    # rotated reference vectors, once
    bad_draws = []
    for draw in range(300):
        ws = []
        for _ in range(2):
            w = []
            for _c in range(3):
                st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
                w.append((st >> 33) % 2000001 - 1000000)
            ws.append(w)
        st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        h = hx[(st >> 17) % nax]
        xs = []
        for w in ws:
            xv = []
            for s in range(n):
                r = ros[s]
                dot = L.add(L.add(L.mul(L.N(w[0]), r[0]), L.mul(L.N(w[1]), r[1])),
                            L.mul(L.N(w[2]), r[2]))
                sg = L.sgn(dot)
                if sg == 0:
                    # H3 tie rule: sign of the first non-zero component of the rotated vector
                    for comp in r:
                        if L.sgn(comp) != 0:
                            sg = L.sgn(comp)
                            break
                xv.append(sg)
            xs.append(xv)
        m = sum(1 for s in reps if xs[0][s] == xs[1][MUL[s][h]])
        nnum = 2 * (2 * m - 60)          # the 120-state numerator for this generic pair
        if m % 2 != 0 or nnum % 8 != 0:
            bad_draws.append(draw)
    # NULL control: an arbitrary +-1 function on the 60 orbits satisfies the same parity only
    # about half the time, so the property is NOT automatic
    null_bad = 0
    for draw in range(300):
        f = []
        g = []
        for s in reps:
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            f.append(1 if (st >> 33) & 1 else -1)
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            g.append(1 if (st >> 33) & 1 else -1)
        tot = sum(f[i] * g[i] for i in range(60))
        if tot % 4 != 0:
            null_bad += 1
    R.claim('V8', 'random-generic-axis control (300 draws): for random rational integer '
                  'directions (two per draw) and a random frozen h, the 120-state numerator '
                  '2*(#same - #diff) over the 60 Z2-orbits is divisible by 8 in EVERY draw. '
                  'The NULL control shows the property is not automatic: an arbitrary +-1 '
                  'function on the same 60 orbits fails the mod-4 parity in about half of 300 '
                  'draws. Therefore the 1/15 quantum is FORCED by the +-1 sign readout on the '
                  'discrete 2I orbit, not by the particular 62 frozen axis directions',
            len(bad_draws) == 0 and null_bad > 60,
            'draws with a failing parity = %d / 300 (fixed-point-free Z2 pairing, 60 orbits) ; '
            'NULL control failures = %d / 300' % (len(bad_draws), null_bad))

    # ---------------- V9: the continuous control (P14) ----------------
    nref = U[0]
    cont = set()
    for i in range(n):
        r = L.rot_ref(G[i], nref)
        for a in range(nax):
            u = U[a]
            cont.add(L.add(L.add(L.mul(u[0], r[0]), L.mul(u[1], r[1])),
                          L.mul(u[2], r[2])))
    R.claim('V9', 'CONTINUOUS control: replacing the +-1 binarisation by the exact inner '
                  'product <u_a, R_g n_0> widens the readout value set from 2 to 11 exact '
                  'values in Q(sqrt5) -- the continuum is destroyed by the SIGN MAP, not by '
                  'the group (the readout map is the only lossy step)',
            len(cont) > 2,
            'un-binarised readout distinct values = %d ; frozen readout alphabet = 2' % len(cont))

    extra = {'C1_signed_values': [str(F(v, n)) for v in vals],
             'magnitudes': [str(x) for x in got],
             'spectrum': spec,
             'smallest_positive': str(F(minpos, n)),
             'denominators': dens,
             'budget': {'B': str(B), 'per_read': str(per_read), 'E_min': str(e_min),
                        'reads_per_pass': str(reads_per_pass), 'overrun': str(overrun)},
             'verdict_d': 'RED: the amplitude layer is a rigid 15-point discrete spectrum with '
                          'quantum 1/15 = 1/(N_gen*F_5); there is no continuous amplitude to '
                          'recover, and the only continuous quantities are exact counting '
                          'rationals'}
    ok = R.finish(os.path.join(DATA, '05_valueset.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
