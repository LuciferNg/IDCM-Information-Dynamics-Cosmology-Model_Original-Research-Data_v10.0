#!/usr/bin/env python3
"""O224 scripts/10_e5.py -- round 3 (part 2): the E5 layer over all 62^5 = 916,132,832 tuples.

ROUND-3 PRE-REGISTRATION (written BEFORE any number of this round is produced):

E1  the exact maximum of |E5| over ALL 62^5 setting tuples, together with the off-grid count over
    every one of the 916,132,832 numerators (integer arithmetic only; numpy is used as an integer
    accelerator on <=120-element vectors).  Test: every numerator divisible by 8 (the 1/15 grid
    holds for the 5-party object as well).
E2  the n = 5 triangle bound (16 terms x max|E5|) compared with the LHV bound of the n = 5
    Mermin polynomial (re-enumerated by all 4^5 = 1024 deterministic strategies).  The claim
    asserts only the arithmetic of the comparison; the n = 5 conclusion is labelled decisive or
    not according to what that comparison gives, and the triangle route is known from round 3
    part 1 to be a weak instrument (it failed at n = 4).

Exactness: E5(a,b,c,d,e) = (1/120) sum_s K[s][a] K[s h_a][b] K[s h_a h_b][c] K[s h_a h_b h_c][d]
K[s h_a h_b h_c h_d][e], computed by an exact integer accumulation over the 120 states.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')


def mermin_terms(n):
    out = []
    for mask in range(1 << n):
        eps = tuple((mask >> j) & 1 for j in range(n))
        w = sum(eps)
        if w % 2 == 0:
            out.append((eps, 1 if (w // 2) % 2 == 0 else -1))
    return out


def lhv_bound(n, terms):
    resp = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = 0
    for combo in range(4 ** n):
        c, fns = combo, []
        for _ in range(n):
            fns.append(resp[c % 4])
            c //= 4
        val = 0
        for eps, coef in terms:
            prod = 1
            for j in range(n):
                prod *= fns[j][eps[j]]
            val += coef * prod
        best = max(best, abs(val))
    return best


def main():
    R = L.Report('10_e5')
    print('=' * 108)
    print('O224 scripts/10 -- round 3 part 2: E5 over all 62^5 = 916,132,832 tuples')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    col = np.arange(nax, dtype=np.int32)
    s2b = NMUL[:, hxa]

    T = KA[NMUL[:, hxa], col[None, :]]               # T[s', e] = K[s' h_e][e]

    # exact-arithmetic cross-check of the accelerator on declared tuples
    def e5_exact(a, b, c, d, e):
        s2 = [MUL[s][hx[a]] for s in range(n)]
        s3 = [MUL[s2[s]][hx[b]] for s in range(n)]
        s4 = [MUL[s3[s]][hx[c]] for s in range(n)]
        s5 = [MUL[s4[s]][hx[d]] for s in range(n)]
        return sum(K[s][a] * K[s2[s]][b] * K[s3[s]][c] * K[s4[s]][d] * K[s5[s]][e]
                   for s in range(n))

    t0 = time.time()
    e5_absmax = 0
    e5_arg = None
    e5_off = 0
    e5_vals = set()
    probe = {"(0,1,0,1,0)": None}
    for a in range(nax):
        Aa = KA[:, a]
        s2 = s2b[:, a]
        for b in range(nax):
            s3 = NMUL[s2, hxa[b]]
            Wa = Aa * KA[s2, b]
            for c in range(nax):
                s4c = NMUL[s3, hxa[c]]
                W3 = Wa * KA[s3, c]
                for d in range(nax):
                    s4 = NMUL[s4c, hxa[d]]
                    W4 = W3 * KA[s4, d]
                    pos = W4 > 0
                    D4 = (np.bincount(s4[pos], minlength=n)
                          - np.bincount(s4[~pos], minlength=n))
                    V = D4 @ T                              # (62,) over e
                    if (a, b, c, d) == (0, 1, 0, 1):
                        probe["(0,1,0,1,0)"] = int(V[0])
                    mx = int(np.abs(V).max())
                    if mx > e5_absmax:
                        e5_absmax = mx
                        e5_arg = (a, b, c, d, int(np.argmax(np.abs(V))))
                    e5_off += int(np.count_nonzero(V % 8 != 0))
                    if len(e5_vals) < 400:
                        e5_vals.update(int(x) for x in np.unique(np.abs(V)).tolist())
    t_e5 = time.time() - t0
    probe_ok = probe["(0,1,0,1,0)"] == e5_exact(0, 1, 0, 1, 0)
    print('  E5 done in %.1f s ; max|E5| = %d/120 ; off-grid = %d'
          % (t_e5, e5_absmax, e5_off), flush=True)

    terms5 = mermin_terms(5)
    b5 = lhv_bound(5, terms5)
    bound5 = len(terms5) * e5_absmax
    R.claim('E1', 'E5 IN FULL: the exact maximum of |E5| over ALL 62^5 = 916,132,832 setting '
                  'tuples is computed (integer arithmetic only), and the off-grid count covers '
                  'every one of the 916,132,832 numerators, so the 1/15 grid is confirmed for the '
                  '5-party object as well. The numpy integer accelerator is validated against '
                  'exact Fraction/int arithmetic on a declared tuple',
            e5_off == 0 and probe_ok,
            'max|E5| = %d/120 = %.6f at %s ; off-grid numerators = %d / 916132832 ; accelerator '
            'probe (0,1,0,1,0) exact = %s ; max |E5| value set (|.| up to 400 values) = %s ; '
            'time = %.1f s'
            % (e5_absmax, e5_absmax / 120.0, tuple(ids[i] for i in (e5_arg or ())), e5_off,
               probe_ok, sorted(e5_vals)[:20], t_e5))

    decisive = bound5 < n * b5
    R.claim('E2', 'n = 5 TRIANGLE BOUND: 16 terms x max|E5| = %d/120 is compared with the LHV '
                  'bound of the n = 5 Mermin polynomial (4^5 = 1024 deterministic strategies). '
                  'The claim records the arithmetic and the resulting label; the n = 5 global '
                  'question is NOT claimed to be closed by this bound unless the comparison '
                  'allows it, and round 3 part 1 has already shown the triangle route to be a '
                  'weak instrument (it failed at n = 4 even though the exact n = 4 pool maxima '
                  'are far below the bound)' % bound5,
            True,
            'max|E5| = %d/120 ; 16*max|E5| = %d/120 = %.4f ; LHV bound (n=5) = %d ; decisive = %s'
            % (e5_absmax, bound5, bound5 / 120.0, b5, decisive))

    extra = {'E5': {'off_grid': e5_off, 'absmax_num': e5_absmax,
                    'argmax': tuple(ids[i] for i in (e5_arg or ())),
                    'abs_values_sample': sorted(e5_vals)[:40], 'seconds': t_e5},
             'n5': {'terms': len(terms5), 'triangle_bound_num': bound5, 'lhv_bound': b5,
                    'decisive': bool(decisive)},
             'verdicts': {'E1': 'E5 grid exact on all 916M numerators',
                          'E2': 'n = 5 ' + ('decisive' if decisive else
                                            'triangle bound insufficient (OPEN)')}}
    ok = R.finish(os.path.join(DATA, '10_e5.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
