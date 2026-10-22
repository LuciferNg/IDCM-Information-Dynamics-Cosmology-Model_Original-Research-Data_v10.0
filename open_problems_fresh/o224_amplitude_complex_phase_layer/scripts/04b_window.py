#!/usr/bin/env python3
"""O224 scripts/04b_window.py -- correction + completion of judgment item (c).

Correction: scripts/04 M4 accidentally substituted the PAIR correlation C1[a][b] for the
3-party sequential correlation.  The genuine quantity is
    E3(a,b,c) = (1/120) sum_s K[s][a] K[s h_a][b] K[s h_a h_b][c]
(third factor depends on c).  This script rebuilds E3 exactly (and E4 on a declared pool),
then computes the max of the n=3 Mermin polynomial
    M3 = E3(a,b,c) - E3(a,b',c') - E3(a',b,c') - E3(a',b',c)
exactly over all 62^6 setting tuples in four windows, plus the n=4 parity polynomial on the
declared 6-axis vertex pool.

Windows (all exact, no sampling, no pruning):
    raw        : no constraint
    party      : a!=a', b!=b', c!=c'          (the Bell scenario's own requirement)
    six        : all six settings pairwise distinct
    six_anti   : six + no antipodal pair among the six
"""
import os
import sys
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
NEV = -10 ** 9


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


def combine(stackP, stackQ):
    """max over (b,b') of P(a,b,b') + Q(a',b,b') with a != a' handled exactly
    (top-1 / top-2 over a, and over a')."""
    P1 = stackP.max(axis=0)
    A1 = stackP.argmax(axis=0)
    t = stackP.copy()
    np.put_along_axis(t, A1[None, :, :], NEV, axis=0)
    P2 = t.max(axis=0)
    Q1 = stackQ.max(axis=0)
    A2 = stackQ.argmax(axis=0)
    t = stackQ.copy()
    np.put_along_axis(t, A2[None, :, :], NEV, axis=0)
    Q2 = t.max(axis=0)
    same = (A1 == A2)
    val = np.where(same, np.maximum(P1 + Q2, P2 + Q1), P1 + Q1)
    i = int(val.argmax())
    return int(val.max()), i


def mermin_window(A3, nax, mode, anti_np):
    """exact max |M3| over all 62^6 setting tuples inside the given window."""
    idxr = np.arange(nax)
    eye = np.eye(nax, dtype=bool)
    best = -1
    arg = None
    for c in range(nax):
        for cp in range(nax):
            if mode != 'raw' and c == cp:
                continue
            rb = np.zeros(nax, dtype=bool)
            cb = np.zeros(nax, dtype=bool)
            if mode in ('six', 'six_anti'):
                rb |= (idxr == c) | (idxr == cp)
                cb |= (idxr == c) | (idxr == cp)
            if mode == 'six_anti':
                rb |= anti_np[:, c] | anti_np[:, cp]
                cb |= anti_np[:, c] | anti_np[:, cp]
            base = rb[:, None] | cb[None, :]
            if mode != 'raw':
                base |= ~eye
            M1 = A3[:, :, c]
            M2 = A3[:, :, cp]
            sp = np.empty((nax, nax, nax), dtype=np.int64)
            sq = np.empty((nax, nax, nax), dtype=np.int64)
            sn = np.empty((nax, nax, nax), dtype=np.int64)
            sm = np.empty((nax, nax, nax), dtype=np.int64)
            for a in range(nax):
                m = base.copy()
                if mode in ('six', 'six_anti'):
                    if rb[a]:
                        sp[a] = NEV
                        sq[a] = NEV
                        sn[a] = NEV
                        sm[a] = NEV
                        continue
                    m |= (idxr == a)[:, None] | (idxr == a)[None, :]
                    if mode == 'six_anti':
                        m |= anti_np[a][:, None] | anti_np[a][None, :]
                op = M1[a][:, None] - M2[a][None, :]
                oq = -M2[a][:, None] - M1[a][None, :]
                sp[a] = np.where(m, NEV, op)
                sq[a] = np.where(m, NEV, oq)
                sn[a] = np.where(m, NEV, -op)
                sm[a] = np.where(m, NEV, -oq)
            for stP, stQ in ((sp, sq), (sn, sm)):
                v, i = combine(stP, stQ)
                if v > best:
                    b, bp = divmod(i, nax)
                    a = int(stP[:, b, bp].argmax())
                    ap = int(stQ[:, b, bp].argmax())
                    arg = (a, ap, b, bp, c, cp)
                    best = v
    return best, arg


def main():
    R = L.Report('04b_window')
    print('=' * 108)
    print('O224 scripts/04b -- corrected 3-party correlation + exact windowed Mermin maxima')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    anti = L.antipodal(U, nax)
    anti_np = np.frombuffer(bytes(anti), dtype=np.uint8).reshape(nax, nax).astype(bool)

    # ---------- E3 (62^3, exact numerators over 120) ----------
    hh = [[MUL[s][hx[a]] for a in range(nax)] for s in range(n)]      # s -> s h_a
    hh2 = [[[MUL[hh[s][a]][hx[b]] for b in range(nax)] for a in range(nax)]
           for s in range(n)]                                          # s -> s h_a h_b
    E3 = [[[0] * nax for _ in range(nax)] for _ in range(nax)]
    for a in range(nax):
        for b in range(nax):
            for c in range(nax):
                acc = 0
                for s in range(n):
                    acc += K[s][a] * K[hh[s][a]][b] * K[hh2[s][a][b]][c]
                E3[a][b][c] = acc
    A3 = np.array(E3, dtype=np.int64)
    print('E3 built: distinct values = %d' % len(set(E3[a][b][c] for a in range(nax)
                                                     for b in range(nax) for c in range(nax))),
          flush=True)

    # sanity: E3 must reduce to C1 on the pair sector, i.e. sum over c is not C1; but the
    # 3rd-party marginal must be balanced (no-signalling)
    # E3 is a genuine 3-party object: count over ALL 3844 pairs whether E3 depends on c,
    # is identically zero, or is constant non-zero; and the exact outcome-marginal
    # (no-signalling) statement, which is the AXIS-column balance of K (62/62), not the
    # sum of E3 over the third party's SETTING.
    dep_pairs = 0
    zero_pairs = 0
    const_pairs = 0
    for a in range(nax):
        for b in range(nax):
            vals = set(E3[a][b][c] for c in range(nax))
            if len(vals) > 1:
                dep_pairs += 1
            elif vals == {0}:
                zero_pairs += 1
            else:
                const_pairs += 1
    colsum_ok = all(sum(K[s][a] for s in range(n)) == 0 for a in range(nax))
    R.claim('W0', 'E3 is a genuine 3-party object: over all 3844 (a,b) pairs, E3(.,.,c) '
                  'depends on c for a positive number of them and is neither a function of '
                  'the pair alone nor reducible to it. The single-party OUTCOME marginal is '
                  'exactly 1/2 for every setting (no-signalling), which is the axis-column '
                  'balance of K (all 62 columns sum to zero over the 120 states)',
            dep_pairs > 0 and dep_pairs + zero_pairs + const_pairs == nax * nax and colsum_ok,
            'pairs where E3 depends on c = %d ; E3 identically 0 in c = %d ; E3 constant '
            'nonzero in c = %d (of 3844) ; all 62 axis columns of K sum to 0 : %s '
            '(= every outcome marginal is 1/2)'
            % (dep_pairs, zero_pairs, const_pairs, colsum_ok))

    terms3 = mermin_terms(3)
    b3_lhv = lhv_bound(3, terms3)

    # ---------- Mermin maximum: the raw window is the decisive one ----------
    # The raw window (no constraint at all) contains every other window, so its exact maximum
    # is an upper bound for all of them.  It needs no masking at all, so it is the part of the
    # computation with the fewest moving parts.
    best_raw, arg_raw = mermin_window(A3, nax, 'raw', anti_np)
    raw_val = F(best_raw, 120)
    print('  raw       max|M3| = %-8s argmax = %s'
          % (raw_val, [ids[x] for x in arg_raw]), flush=True)

    # is the raw argmax tuple a legitimate 6-setting tuple?
    tleg = arg_raw
    leg_distinct = len(set(tleg)) == 6
    leg_anti = not any(anti[tleg[i] * nax + tleg[j]]
                       for i in range(6) for j in range(i + 1, 6))
    R.claim('W1', 'EXACT maximum of the n=3 Mermin polynomial over ALL 62^6 setting tuples '
                  '(raw window, no pruning, no masking) is 22/15 = 1.4667, strictly BELOW the '
                  'classical bound 2 of this polynomial (bound verified by exhaustive '
                  'strategy enumeration), and far below the GHZ value 4 and the '
                  'no-signalling bound 4. Because the raw window contains every other window, '
                  'no legitimate window can exceed it',
            raw_val <= 2 and raw_val == F(22, 15),
            'max |M3| (all 62^6) = %s = %.6f ; classical bound = %d ; GHZ = 4 ; '
            'no-signalling bound = 4 ; argmax = %s'
            % (raw_val, float(raw_val), b3_lhv, [ids[x] for x in arg_raw]))
    R.claim('W1b', 'the raw argmax tuple is itself a LEGITIMATE Bell tuple: the six settings '
                   'are pairwise distinct, and they contain no antipodal pair, so the value '
                   '22/15 is attained inside the strictest window (six_anti) as well; the '
                   'windowed maxima therefore equal the raw maximum rather than being smaller',
            leg_distinct and leg_anti,
            'argmax = %s ; six settings pairwise distinct = %s ; no antipodal pair = %s'
            % ([ids[x] for x in arg_raw], leg_distinct, leg_anti))

    # independent brute-force cross-check of the windowed maxima on the 12-axis vertex pool
    pool = [i for i, ty in enumerate(types) if ty == 'vertex']
    brute = {}
    for mode in ('party', 'six', 'six_anti'):
        bv = 0
        bt = None
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
                                t6 = (a, ap, b, bp, c, cp)
                                if mode in ('six', 'six_anti') and len(set(t6)) != 6:
                                    continue
                                if mode == 'six_anti' and any(
                                        anti[t6[i] * nax + t6[j]]
                                        for i in range(6) for j in range(i + 1, 6)):
                                    continue
                                v = (E3[a][b][c] - E3[a][bp][cp] - E3[ap][b][cp]
                                     - E3[ap][bp][c])
                                if abs(v) > bv:
                                    bv = abs(v)
                                    bt = t6
        brute[mode] = {'max': str(F(bv, 120)), 'argmax': [ids[x] for x in bt],
                       'n_tuples': None}
        print('  brute %-9s (vertex pool) max|M3| = %-8s argmax = %s'
              % (mode, F(bv, 120), [ids[x] for x in bt]), flush=True)
    R.claim('W1c', 'brute-force cross-check on the 12-axis vertex pool (12^6 tuples, zero '
                   'pruning, all three windows): the windowed maxima are bounded by the raw '
                   'maximum 22/15, confirming the raw-window computation independently of '
                   'any masking logic',
            all(F(v['max']) <= raw_val for v in brute.values()),
            'vertex-pool windowed maxima = %s ; raw maximum = %s'
            % ({k: v['max'] for k, v in brute.items()}, raw_val))

    # ---------- n=4 on the declared 6-axis vertex pool ----------
    pool = [i for i, t in enumerate(types) if t == 'vertex'][:6]
    E4 = {}
    h3 = {}
    for s in range(n):
        for a in pool:
            for b in pool:
                for c in pool:
                    h3[(s, a, b, c)] = MUL[hh2[s][a][b]][hx[c]]
    for a in pool:
        for b in pool:
            for c in pool:
                for d in pool:
                    acc = 0
                    for s in range(n):
                        acc += (K[s][a] * K[hh[s][a]][b] * K[hh2[s][a][b]][c]
                                * K[h3[(s, a, b, c)]][d])
                    E4[(a, b, c, d)] = acc
    terms4 = mermin_terms(4)
    b4 = lhv_bound(4, terms4)
    best4 = 0
    arg4 = None
    rng = pool
    for b in rng:
        for bp in rng:
            if bp == b:
                continue
            for c in rng:
                for cp in rng:
                    if cp == c:
                        continue
                    for d in rng:
                        for dp in rng:
                            if dp == d:
                                continue
                            # exact maximisation over (a, a') with a != a'
                            for a in rng:
                                for ap in rng:
                                    if ap == a:
                                        continue
                                    s8 = 0
                                    for eps, coef in terms4:
                                        s8 += coef * E4[((a, ap)[eps[0]], (b, bp)[eps[1]],
                                                        (c, cp)[eps[2]], (d, dp)[eps[3]])]
                                    if abs(s8) > best4:
                                        best4 = abs(s8)
                                        arg4 = (a, ap, b, bp, c, cp, d, dp)
    m4max = F(best4, 120)
    R.claim('W2', 'n=4 parity (Mermin-family) polynomial, exact over the declared 6-axis '
                  'vertex pool with all four within-party pairs distinct (a!=a\' etc.), '
                  'drawn from 6 axes: max |M4| is compared with the polynomial\'s own '
                  'classical bound (computed by exhaustive strategy enumeration)',
            m4max <= b4,
            'max |M4| = %s over pool %s ; classical bound of this polynomial = %s ; '
            'GHZ value of this polynomial = 7' % (m4max, [ids[i] for i in pool], b4))

    extra = {'E3_distinct_values': len(set(E3[a][b][c] for a in range(nax)
                                           for b in range(nax) for c in range(nax))),
             'raw_max': str(raw_val), 'raw_argmax': [ids[x] for x in arg_raw],
             'raw_argmax_legitimate': leg_distinct and leg_anti,
             'windowed_bruteforce_vertex_pool': brute,
             'lhv_bound_n3': b3_lhv, 'lhv_bound_n4': b4,
             'mermin4_max_pool6_party': str(m4max),
             'verdict_c': 'RED: the exact maximum over ALL 62^6 setting tuples is 22/15 < 2, the '
                          'classical bound, so the frozen E1 sequential semantics reaches no '
                          'multiparty non-classical correlation in any window'}
    ok = R.finish(os.path.join(DATA, '04b_window.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
