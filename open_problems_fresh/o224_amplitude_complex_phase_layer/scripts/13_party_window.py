#!/usr/bin/env python3
"""O224 scripts/13_party_window.py (round 4, addendum) -- the legitimate-window consequence of the
exact global closure.

ROUND-4 ADDENDUM PRE-REGISTRATION (written BEFORE any number of this addendum is produced).

Round 4 (scripts/12) closed the raw-window question exactly: max M4 = 512/120 over all 62^8 setting
tuples (the round-3 interval [480, 768]/120 collapsed to a single number).  The round-4 achieved
configuration is (V00, E28, V00, E21, E11, F10, F01, F16).  This addendum tests, as its own
pre-registered claims, the consequences for the LEGITIMATE window:

P1  MEMBERSHIP: the round-4 achieving configured 8-tuple satisfies the party-window constraints
    exactly, i.e. the four within-pair settings are pairwise distinct (a != a', b != b', c != c',
    d != d'), checked with exact integer comparisons on the recorded axis indices.  If it does, the
    configuration is a legitimate Bell configuration, not merely a raw one.
P2  ATTAINMENT BY BRUTE FORCE (independent path): for the achieving party-1/pair-2 quadruple the
    full 4-D enumeration over (c,c',d,d') WITH the party constraints must reproduce 512 exactly
    (and its negative counterpart -512 at the recorded minimising tuple), so the party-window
    global maximum and minimum are attained values rather than extrapolations.
P3  THE BOUND COMPARISON: the LHV bound of the 8-term n = 4 Mermin polynomial is recomputed by
    enumerating all 4^4 = 256 deterministic strategies, and compared with 512/120.  Because the
    party window is a subset of the raw window and both attain 512, the party-window global maximum
    equals the raw global maximum exactly: the chained inequality
        LHV bound (480/120)  <  512/120  =  party-window global  <=  raw-window global  =  512/120
    is therefore an equality sandwich, and it says that the frozen machine violates the n = 4
    Mermin inequality inside the physically legitimate (within-pair-distinctness) window by exactly
    32/120.  The statement is recorded as it is.
P4  BRACKETS FOR THE STRICTER WINDOWS: the eight and eight_anti windows are subsets of the party
    window, so their global maxima are trapped between the round-3 pool values (320, 224) and 512;
    equality is NOT claimed for them (the round-4 achiever is not eight-distinct), and the exact
    global values of those two windows are recorded as NOT computed in this round.
P5  GRID: 512 is divisible by 8 (the 1/15 grid).

Exact arithmetic only; numpy as an integer accelerator; zero new parameters; writes only inside
this O directory.
"""
import io
import json
import os
import sys

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


def build_e4(nax, KA, NMUL, hxa):
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
    return E4


def main():
    R = L.Report('13_party_window')
    print('=' * 108)
    print('O224 scripts/13 (round-4 addendum) -- the legitimate-window consequence')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    pool = [i for i, ty in enumerate(types) if ty == 'vertex']
    terms4 = mermin_terms(4)
    b4 = lhv_bound(4, terms4)

    with io.open(os.path.join(DATA, '12_n4_global.json'), encoding='utf-8') as fh:
        r4 = json.load(fh)
    X4 = r4['raw_global']
    argmax4 = list(X4['max_argmax'])
    argmin4 = list(X4['min_argmax'])
    glob_max = int(X4['max_num'])
    glob_min = int(X4['min_num'])

    X = build_e4(nax, KA, NMUL, hxa)

    def brute8(t8):
        a, ap, b, bp, c, cp, d, dp = t8
        s = [a, ap, b, bp, c, cp]
        tot = 0
        for e, coef in terms4:
            tot += coef * int(X[s[0 + e[0]], s[2 + e[1]], s[4 + e[2]], d if e[3] == 0 else dp])
        return tot

    # ---------------- P1 membership ----------------
    pairs = [(argmax4[0], argmax4[1]), (argmax4[2], argmax4[3]), (argmax4[4], argmax4[5]),
             (argmax4[6], argmax4[7])]
    pair_ok = all(u != v for u, v in pairs)
    pairs_min = [(argmin4[0], argmin4[1]), (argmin4[2], argmin4[3]),
                 (argmin4[4], argmin4[5]), (argmin4[6], argmin4[7])]
    pair_ok_min = all(u != v for u, v in pairs_min)
    R.claim('P1', 'MEMBERSHIP IN THE LEGITIMATE WINDOW: the round-4 achieving configuration '
                  'satisfies the party-window constraints exactly (all four within-pair settings '
                  'pairwise distinct), so it is a legitimate Bell configuration rather than a merely '
                  'unconstrained one; the same holds for the minimising configuration',
            pair_ok and pair_ok_min,
            'max tuple %s -> within-pair pairs %s distinct = %s ; min tuple %s -> distinct = %s'
            % (X4['max_argmax_ids'], pairs, pair_ok, X4['min_argmax_ids'], pair_ok_min))

    # ---------------- P2 attainment by 4-D brute force WITH the party constraints ----------------
    def brute4d_party(a, ap, b, bp):
        i = np.arange(nax)
        A = X[a, b] - X[ap, bp]
        Rm = X[ap, b] + X[a, bp]
        U = X[ap, bp] - X[a, b]
        V = X[ap, b] + X[a, bp]
        T1 = A[:, None, :] - Rm[None, :, :]              # (c, c', d)
        T2 = U[None, :, :] - V[:, None, :]               # (c, c', d')
        T = T1[:, :, :, None] + T2[:, :, None, :]        # (c, c', d, d')
        ok = ((i[:, None] != i[None, :])[:, :, None, None]                    # c != c'
              & (i[None, None, :, None] != i[None, None, None, :]))           # d != d'
        big = np.where(ok, T, -10 ** 9)
        small = np.where(ok, T, 10 ** 9)
        return int(big.max()), int(small.min())

    p_max, p_min = brute4d_party(argmax4[0], argmax4[1], argmax4[2], argmax4[3])
    p_max2, p_min2 = brute4d_party(argmin4[0], argmin4[1], argmin4[2], argmin4[3])
    R.claim('P2', 'ATTAINMENT BY BRUTE FORCE WITH THE PARTY CONSTRAINTS: a full 4-D enumeration '
                  'over (c,c\',d,d\') restricted by the party constraints reproduces the value 512 '
                  'at the round-4 maximising quadruple and -512 at the minimising one, so the '
                  'party-window extremes are attained, not extrapolated',
            p_max == glob_max == 512 and p_min2 == glob_min == -512,
            'achieving quadruple %s -> party-constrained 4-D (max %d, min %d) ; minimising '
            'quadruple %s -> (max %d, min %d) ; exact 8-term value at the achiever = %d, at the '
            'minimiser = %d'
            % (tuple(ids[v] for v in argmax4[:4]), p_max, p_min,
               tuple(ids[v] for v in argmin4[:4]), p_max2, p_min2,
               brute8(argmax4), brute8(argmin4)))

    # ---------------- P3 the bound comparison ----------------
    R.claim('P3', 'THE VIOLATION IS EXACT AND CLOSED IN THE LEGITIMATE WINDOW: because the party '
                  'window is a subset of the raw window and both attain 512, the chained '
                  'inequality LHV bound < 512/120 = party global <= raw global = 512/120 collapses '
                  'to an equality at both ends: the frozen machine violates the n = 4 Mermin '
                  'inequality inside the physically legitimate (within-pair-distinctness) window by '
                  'exactly 512 - 480 = 32 units of 1/120, i.e. by 6.667%. The statement is '
                  'recorded as it is',
            glob_max == 512 and glob_min == -512 and n * b4 == 480 and pair_ok and pair_ok_min,
            'LHV bound = %d = %d/120 ; raw global max = %d/120 ; party-window global max = %d/120 '
            '(sandwiched) ; excess = %d/120 = %.4f%% of the bound ; raw global min = %d/120 ; '
            'party-window global min = %d/120 ; |M4|max = 512/120 = %.6f'
            % (n * b4, n * b4, glob_max, glob_max, glob_max - n * b4,
               100.0 * (glob_max - n * b4) / (n * b4), glob_min, glob_min, glob_max / 120.0))

    # ---------------- P4 brackets for the stricter windows ----------------
    r3_pool = r4['round3_cross']['pool_values']
    R.claim('P4', 'BRACKETS FOR THE STRICTER WINDOWS (not closed here, stated honestly): the eight '
                  'and eight_anti windows are subsets of the party window, so their global maxima '
                  'lie in [320, 512] and [224, 512] respectively (round-3 pool values as lower '
                  'bounds, this round\'s party/raw global as the upper bound); equality is NOT '
                  'claimed, because the round-4 achiever is not eight-distinct, and the exact '
                  'global values of those two windows are recorded as NOT computed',
            r3_pool['eight'] <= glob_max and r3_pool['eight_anti'] <= glob_max
            and r3_pool['raw'] == 480 and r3_pool['party'] == 480,
            'round-3 pool values = %s ; brackets: eight in [%d, %d], eight_anti in [%d, %d] ; '
            'achiever eight-distinct = %s'
            % (r3_pool, r3_pool['eight'], glob_max, r3_pool['eight_anti'], glob_max,
               len(set(argmax4)) == 8))

    # ---------------- P5 grid ----------------
    R.claim('P5', 'GRID: the reported numerators are divisible by 8 (the 1/15 grid)',
            glob_max % 8 == 0 and glob_min % 8 == 0,
            'max %d %% 8 = %d ; min %d %% 8 = %d' % (glob_max, glob_max % 8, glob_min, glob_min % 8))

    extra = {'lhv_bound_num': n * b4, 'lhv_bound': b4,
             'achiever': {'tuple': list(argmax4), 'ids': X4['max_argmax_ids'],
                          'value_num': glob_max, 'within_pair_distinct': bool(pair_ok),
                          'eight_distinct': bool(len(set(argmax4)) == 8)},
             'attainer_min': {'tuple': list(argmin4), 'ids': X4['min_argmax_ids'],
                              'value_num': glob_min, 'within_pair_distinct': bool(pair_ok_min)},
             'party_constrained_4d': {'at_achiever': [p_max, p_min], 'at_minimiser': [p_max2, p_min2]},
             'raw_global_from_round4': [glob_max, glob_min],
             'brackets': {'eight': [r3_pool['eight'], glob_max],
                          'eight_anti': [r3_pool['eight_anti'], glob_max],
                          'party': [glob_max, glob_max]},
             'verdicts': {'P3': 'the n = 4 Mermin inequality is violated by the frozen machine '
                                'inside the legitimate (within-pair-distinctness) window by exactly '
                                '32/120; gained by the exact round-4 raw global plus the exact '
                                'membership and attainment checks of P1/P2',
                          'P4': 'eight and eight_anti globals remain bracketed, not closed'}}
    ok = R.finish(os.path.join(DATA, '13_party_window.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
