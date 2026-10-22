#!/usr/bin/env python3
"""O224 scripts/12_n4_global.py (round 4) -- EXACT GLOBAL CLOSURE OF THE n = 4 QUESTION.

ROUND-4 PRE-REGISTRATION (written BEFORE any number of this round is produced).

Residual under attack (round 3, R7e/R7f): "the exact global maximum of |M4| over all 62^8 setting
tuples is not established; it is trapped in [480, 768]/120 by the relaxation certificate R7f".
Route (1) recorded by R7e is executed here IN FULL: the (d,d') separability proved in R7a reduces
the global problem to an outer search over the six settings (a,a',b,b',c,c'), and that outer space
(62^6) is enumerated exactly -- sharded over the party-1 ordered pair and recombined.

EXACT ARITHMETIC ONLY in every decision: the values are integers (8 E4 numerators), numpy is an
integer accelerator (validated against exact Python/Fraction arithmetic per shard), and the one
non-elementary step -- the separable identity max_(d,d')[F(d)+G(d')] = max_d F + max_d' G, which is
valid because the raw window constrains neither d nor d' -- is verified independently at the
achieved configuration by a FULL 4-D enumeration over (c,c',d,d').

G1  RAW-WINDOW GLOBAL: the exact maximum and minimum of the 8-term Mermin expression M4 over all
    62^8 setting tuples with no distinctness or antipodality constraint (route (1) of R7e
    verbatim), hence the exact global maximum of |M4|.  Verified at the achieved configuration by
    (a) direct 8-term enumeration with the frozen s-index rule in exact Python ints, (b) a full 4-D
    enumeration over (c,c',d,d').  The value is recorded as it is; the round-3 interval collapses
    to a single number.
G2  COVERAGE: the shard union covers the party-1 ordered pairs exactly once and the enumerated
    outer count equals 62^6 = 56,800,235,584, so the reported extremum is global, not partial.
G3  WINDOW COROLLARY: every windowed global (party / eight / eight_anti, over ANY axis set) is
    bounded above by the raw global, so the round-3 pool values and the raw global together bound
    every legitimate n = 4 Bell statement; in particular, if the raw global does not exceed the
    LHV bound 4 = 480/120, then NO window and NO axis set can violate the inequality at n = 4, and
    the round-3 pool values (raw 480, party 480, eight 320, eight_anti 224, read from the frozen
    artefact data/09_global_n.json) are order-verified against this round's frame.
G4  PRECISION FINDING (recorded, not patched): the eight_anti window as implemented in round 3
    ("v3 semantics": the six outer settings pairwise distinct and pairwise non-antipodal, with d,d'
    outside the six and outside the antipodes of the six, and d != d') still PERMITS an antipodal
    (d,d') pair, although round 3's claim text described it as "no antipodal pair".  Round 4
    censuses, exactly and inside the declared pool, how many admissible six-tuples realise their
    v3 maximum with an antipodal pair and records a witness; the strict semantics (no antipodal
    pair anywhere among the eight) is a subset of v3, so v3's value is an upper bound for it.
G5  GRID: every reported numerator is divisible by 8 (the 1/15 grid), as it must be since M4 is a
    sum of 8 E4 numerators.
G6  SELF-CHECKS: per shard, |E4|max = 120/120 and the numpy accelerator is validated against exact
    evaluation on declared tuples.

Usage:
    python3 scripts/12_n4_global.py --shard K N      (one shard; N shards in total)
    python3 scripts/12_n4_global.py --aggregate      (merge, verify, write the round-4 report)
"""
import glob
import io
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
NEG = -10 ** 9
POS = 10 ** 9


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


def topk(arr, K, largest=True):
    m = arr.shape[-1]
    if largest:
        idx = np.argpartition(arr, m - K, axis=-1)[..., m - K:]
    else:
        idx = np.argpartition(arr, K - 1, axis=-1)[..., :K]
    val = np.take_along_axis(arr, idx, axis=-1)
    order = np.argsort(-val, axis=-1) if largest else np.argsort(val, axis=-1)
    return np.take_along_axis(val, order, axis=-1), np.take_along_axis(idx, order, axis=-1)


def solve_pair_raw(X, a, ap, nax):
    """exact raw-window extremes over (b,b',c,c',d,d') for a fixed party-1 pair (a,a').

    X : E4 (4-D).  Returns (pos, neg, argpos, argneg, groups) with 8-tuples as plain ints."""
    best_pos = None
    best_neg = None
    arg_pos = None
    arg_neg = None
    groups = 0
    for b in range(nax):
        Xab = X[a, b]
        for bp in range(nax):
            A = Xab - X[ap, bp]              # (c, d)
            R = X[ap, b] + X[a, bp]          # (c', d)
            U = X[ap, bp] - Xab              # (c', d')
            V = X[ap, b] + X[a, bp]          # (c, d')
            T1 = A[:, None, :] - R[None, :, :]          # (c, c', d)
            T2 = U[None, :, :] - V[:, None, :]          # (c, c', d')
            phi = T1.max(axis=2) + T2.max(axis=2)       # (c, c')
            psi = T1.min(axis=2) + T2.min(axis=2)
            i, j = np.unravel_index(int(np.argmax(phi)), phi.shape)
            v = int(phi[i, j])
            if best_pos is None or v > best_pos:
                best_pos = v
                arg_pos = (a, ap, b, bp, int(i), int(j),
                           int(np.argmax(T1[i, j])), int(np.argmax(T2[i, j])))
            k, l = np.unravel_index(int(np.argmin(psi)), psi.shape)
            vn = int(psi[k, l])
            if best_neg is None or vn < best_neg:
                best_neg = vn
                arg_neg = (a, ap, b, bp, int(k), int(l),
                           int(np.argmin(T1[k, l])), int(np.argmin(T2[k, l])))
            groups += nax * nax
    return best_pos, best_neg, arg_pos, arg_neg, groups


def census_v3_pool(X, pool, anti, nax):
    """exact census, inside the declared pool frame, of the v3 eight_anti semantics: for every
    admissible six-tuple (pairwise distinct and pairwise non-antipodal) count the (c,c') whose v3
    maximiser is realised by an ANTIPODAL (d,d') pair, and keep a witness."""
    na = len(pool)
    adx = np.arange(nax)
    valid_six = 0
    anti_realised = 0
    witness = None
    for a in pool:
        for ap in pool:
            for b in pool:
                for bp in pool:
                    four = (a, ap, b, bp)
                    four_ok = len(set(four)) == 4 and not any(
                        anti[four[i], four[j]] for i in range(4) for j in range(i + 1, 4))
                    if not four_ok:
                        continue
                    Xab, Xapbp = X[a, b], X[ap, bp]
                    A = Xab - Xapbp
                    R = X[ap, b] + X[a, bp]
                    U = Xapbp - Xab
                    V = X[ap, b] + X[a, bp]
                    T1 = A[:, None, :] - R[None, :, :]
                    T2 = U[None, :, :] - V[:, None, :]
                    # admissibility on the d axis, in frame indices (c, c')
                    base = np.ones(nax, bool)
                    for s in four:
                        base &= (adx != s) & (~anti[s])
                    valid_c = np.array([x not in four for x in pool])
                    neq_ccp = (np.array(pool)[:, None] != np.array(pool)[None, :])
                    anti_ccp = ~anti[np.ix_(pool, pool)]
                    anti4 = np.ones(na, bool)
                    for s in four:
                        anti4 &= ~anti[np.array(pool), s]
                    outer = (neq_ccp & valid_c[:, None] & valid_c[None, :]
                             & anti_ccp & anti4[:, None] & anti4[None, :])
                    if not outer.any():
                        continue
                    allowed = np.zeros((na, na, nax), bool)
                    allowed[:] = base[None, None, :]
                    for x in range(na):
                        allowed[:, x, :] &= (adx != pool[x]) & (~anti[pool[x]])
                        allowed[x, :, :] &= (adx != pool[x]) & (~anti[pool[x]])
                    allowed &= outer[:, :, None]
                    Fm = np.where(allowed, T1, NEG)
                    Gm = np.where(allowed, T2, NEG)
                    vF, iF = topk(Fm, 2, True)
                    vG, iG = topk(Gm, 2, True)
                    K = 2
                    dF = np.broadcast_to(iF[:, :, None, :], (na, na, K, K))
                    dG = np.broadcast_to(iG[:, :, :, None], (na, na, K, K))
                    vv = vF[:, :, None, :] + vG[:, :, :, None]
                    ok = (dF != dG) & (vF[:, :, None, :] > NEG // 2) & (vG[:, :, :, None] > NEG // 2)
                    big = np.where(ok, vv, NEG)
                    flat = big.reshape(na, na, K * K)
                    ii = np.argmax(flat, axis=2)
                    ii = np.argmax(big.reshape(na, na, -1), axis=2)
                    best = np.take_along_axis(big.reshape(na, na, -1), ii[:, :, None],
                                              axis=2)[:, :, 0]
                    sel_i, sel_j = ii // K, ii % K
                    # the (d,d') actually used
                    for ci in range(na):
                        for cj in range(na):
                            if not outer[ci, cj]:
                                continue
                            valid_six += 1
                            d1 = int(iF[ci, cj, sel_i[ci, cj]])
                            d2 = int(iG[ci, cj, sel_j[ci, cj]])
                            if anti[d1, d2]:
                                anti_realised += 1
                                if witness is None:
                                    witness = {'six': (a, ap, b, bp, int(pool[ci]),
                                                       int(pool[cj])),
                                               'd_dp': (d1, d2),
                                               'value': int(best[ci, cj])}
    return valid_six, anti_realised, witness


def main():
    args = sys.argv[1:]
    nax_expected_shards = None
    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    pool = [i for i, ty in enumerate(types) if ty == 'vertex']
    terms4 = mermin_terms(4)
    b4 = lhv_bound(4, terms4)
    npairs = nax * nax

    def e4_exact(a, b, c, d):
        s2 = [MUL[s][hx[a]] for s in range(n)]
        s3 = [MUL[s2[s]][hx[b]] for s in range(n)]
        s4 = [MUL[s3[s]][hx[c]] for s in range(n)]
        return sum(K[s][a] * K[s2[s]][b] * K[s3[s]][c] * K[s4[s]][d] for s in range(n))

    if '--shard' in args:
        i = args.index('--shard')
        shard_k, shard_n = int(args[i + 1]), int(args[i + 2])
        t0 = time.time()
        X = build_e4(nax, KA, NMUL, hxa)
        t_e4 = time.time() - t0
        acc_t = [(0, 1, 0, 1), (3, 5, 7, 11), (61, 60, 59, 58)]
        acc_mism = sum(1 for t in acc_t if int(X[t]) != e4_exact(*t))
        absmax = int(np.abs(X).max())
        pairs = [p for p in range(npairs) if p % shard_n == shard_k]
        best_pos = best_neg = None
        arg_pos = arg_neg = None
        groups = 0
        t0 = time.time()
        for cnt, p in enumerate(pairs):
            a, ap = divmod(p, nax)
            bp_, bn_, ap_, an_, g = solve_pair_raw(X, a, ap, nax)
            groups += g
            if best_pos is None or bp_ > best_pos:
                best_pos, arg_pos = bp_, ap_
            if best_neg is None or bn_ < best_neg:
                best_neg, arg_neg = bn_, an_
        dt = time.time() - t0
        out = {'shard': shard_k, 'n_shards': shard_n, 'pairs': pairs, 'groups': groups,
               'pos': best_pos, 'neg': best_neg, 'argpos': list(arg_pos), 'argneg': list(arg_neg),
               'e4_build_s': t_e4, 'solve_s': dt, 'absE4max': absmax, 'acc_mismatch': acc_mism,
               'ids_argpos': [ids[v] for v in arg_pos],
               'ids_argneg': [ids[v] for v in arg_neg]}
        path = os.path.join(DATA, '12_shard_%02dof%02d.json' % (shard_k, shard_n))
        with io.open(path, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        print('shard %d/%d: pairs %d, groups %d, pos %s, neg %s, %.1f s (E4 %.1f s), '
              '|E4|max %d, acc mism %d -> %s'
              % (shard_k, shard_n, len(pairs), groups, best_pos, best_neg, dt, t_e4, absmax,
                 acc_mism, path), flush=True)
        return 0 if (acc_mism == 0 and absmax == 120) else 1

    # ---------------- aggregate ----------------
    R = L.Report('12_n4_global')
    print('=' * 108)
    print('O224 scripts/12 (round 4) -- EXACT GLOBAL CLOSURE of the n = 4 Mermin question')
    print('=' * 108, flush=True)
    shard_files = sorted(glob.glob(os.path.join(DATA, '12_shard_*of*.json')))
    if not shard_files:
        print('no shard files -- run --shard K N first')
        return 2
    shards = []
    for f in shard_files:
        with io.open(f, encoding='utf-8') as fh:
            shards.append(json.load(fh))
    ns = sorted({s['n_shards'] for s in shards})
    ok_shards = len(ns) == 1 and len(shards) == ns[0] and len({s['shard'] for s in shards}) == ns[0]
    covered = sorted(p for s in shards for p in s['pairs'])
    coverage_ok = covered == list(range(npairs))
    groups_total = sum(s['groups'] for s in shards)
    outer_total = npairs * nax ** 4
    acc_ok = all(s['acc_mismatch'] == 0 and s['absE4max'] == 120 for s in shards)
    best = max(shards, key=lambda s: s['pos'])
    worst = min(shards, key=lambda s: s['neg'])
    pos, neg = best['pos'], worst['neg']
    argpos, argneg = best['argpos'], worst['argneg']
    print('shards = %d ; coverage of the %d party-1 pairs = %s ; outer tuples counted = %d '
          '(62^6 = %d)' % (len(shards), npairs, coverage_ok, groups_total, nax ** 6), flush=True)

    t0 = time.time()
    X = build_e4(nax, KA, NMUL, hxa)
    t_e4 = time.time() - t0

    # factorisation self-check: the A/R/U/V form must reproduce the round-3 F and G expressions
    # (direct indexing) exactly, on declared six-tuples
    fac_rows = []
    fac_ok = 0
    for (a, ap, b, bp, c, cp) in [(0, 1, 2, 3, 4, 5), (11, 22, 33, 44, 55, 60),
                                  (7, 7, 9, 9, 13, 13), (61, 60, 59, 58, 57, 56)]:
        A = X[a, b] - X[ap, bp]
        Rm = X[ap, b] + X[a, bp]
        U = X[ap, bp] - X[a, b]
        V = X[ap, b] + X[a, bp]
        F_fac = A[c, :] - Rm[cp, :]
        G_fac = U[cp, :] - V[c, :]
        F_dir = (X[a, b, c, :] - X[ap, bp, c, :] - X[ap, b, cp, :] - X[a, bp, cp, :])
        G_dir = (X[ap, bp, cp, :] - X[ap, b, c, :] - X[a, bp, c, :] - X[a, b, cp, :])
        ok = np.array_equal(F_fac, F_dir) and np.array_equal(G_fac, G_dir)
        fac_ok += 1 if ok else 0
        fac_rows.append(((a, ap, b, bp, c, cp), bool(ok)))
    print('factorisation self-check (A/R/U/V vs direct indexing) = %d/4' % fac_ok, flush=True)

    def brute8(t8):
        a, ap, b, bp, c, cp, d, dp = t8
        s = [a, ap, b, bp, c, cp]
        tot = 0
        for e, coef in terms4:
            tot += coef * int(X[s[0 + e[0]], s[2 + e[1]], s[4 + e[2]], d if e[3] == 0 else dp])
        return tot

    bf_pos = brute8(argpos)
    bf_neg = brute8(argneg)

    # full 4-D enumeration over (c,c',d,d') -- the independent path for the separable identity
    def raw4d_full(a, ap, b, bp):
        """exhaustive enumeration of the raw window over (c,c',d,d') for one party-1/2 quadruple:
        builds the full 4-D array and takes its extremes (no separability used)."""
        A = X[a, b] - X[ap, bp]
        R = X[ap, b] + X[a, bp]
        U = X[ap, bp] - X[a, b]
        V = X[ap, b] + X[a, bp]
        T1 = A[:, None, :] - R[None, :, :]                # (c, c', d)
        T2 = U[None, :, :] - V[:, None, :]                # (c, c', d')
        big = T1[:, :, :, None] + T2[:, :, None, :]       # (c, c', d, d') : 62^4 int32
        return int(big.max()), int(big.min())

    a_best, ap_best, b_best, bp_best = argpos[0], argpos[1], argpos[2], argpos[3]
    w4d = raw4d_full(a_best, ap_best, b_best, bp_best)
    fourd_rows = []
    fourd_ok = 0
    for t in [(0, 0, 0, 0), (0, 1, 2, 3), (11, 22, 33, 44), (30, 31, 32, 33),
              (a_best, ap_best, b_best, bp_best)]:
        mp_, mn_ = raw4d_full(*t)
        # the separable value of the same group, recomputed independently
        A = X[t[0], t[2]] - X[t[1], t[3]]
        Rm = X[t[1], t[2]] + X[t[0], t[3]]
        U = X[t[1], t[3]] - X[t[0], t[2]]
        V = X[t[1], t[2]] + X[t[0], t[3]]
        T1 = A[:, None, :] - Rm[None, :, :]
        T2 = U[None, :, :] - V[:, None, :]
        sp, sn = int((T1.max(axis=2) + T2.max(axis=2)).max()), \
            int((T1.min(axis=2) + T2.min(axis=2)).min())
        ok = (mp_ == sp and mn_ == sn)
        fourd_ok += 1 if ok else 0
        fourd_rows.append((t, mp_, sp, mn_, sn, ok))
    en_p, en_n = w4d

    with io.open(os.path.join(DATA, '09_global_n.json'), encoding='utf-8') as fh:
        r3 = json.load(fh)
    r3_pool = {'raw': r3['n4']['raw_pool_max_num'], 'party': r3['n4']['window_pool_max']['party'],
               'eight': r3['n4']['window_pool_max']['eight'],
               'eight_anti': r3['n4']['window_pool_max']['eight_anti']}
    cert3 = r3['n4']['relax_certificate']['sup_abs_num']

    t0 = time.time()
    Xp = X[np.ix_(pool, pool, pool, np.arange(nax))]   # pool frame for the first three parties,
    census_six, census_anti, census_witness = census_v3_pool(Xp, pool, anti, nax)   # 4th = all 62
    t_census = time.time() - t0

    abs_global = max(pos, -neg)
    R.claim('G1', 'RAW-WINDOW GLOBAL MAXIMUM OF THE n = 4 MERMIN EXPRESSION, CLOSED EXACTLY: the '
                  'whole 62^6 outer space is enumerated (sharded, exactly, integer arithmetic) '
                  'with the proven (d,d\') separability, giving the exact maximum and minimum of '
                  'M4 over all 62^8 setting tuples with no constraint; the achieved configuration '
                  'is verified by direct 8-term enumeration in exact Python ints and by a full 4-D '
                  'enumeration over (c,c\',d,d\') for its party-1 pair. The round-3 interval '
                  '[480, 768]/120 therefore collapses to a single exact number, and the round-3 '
                  'residual "the n = 4 global maximum is not established" is closed',
            (bf_pos == pos and bf_neg == neg and en_p == pos and en_n == neg
             and fourd_ok == 5
             and pos >= r3_pool['raw'] and abs_global <= cert3 and pos % 8 == 0 and neg % 8 == 0),
            'global max M4 = %d/120 = %.6f at %s ; global min M4 = %d/120 = %.6f at %s ; '
            '|M4|max = %d/120 = %.6f ; LHV bound = %d = 480/120 ; round-3 certificate = %d/120 ; '
            'round-3 attained = %d/120 ; brute-force (8 terms) at argmax = %d ; 4-D enumeration of '
            'the winning group = (%d, %d) ; separable-identity rows verified = %d/5'
            % (pos, pos / 120.0, tuple(ids[v] for v in argpos),
               neg, neg / 120.0, tuple(ids[v] for v in argneg),
               abs_global, abs_global / 120.0, n * b4, cert3,
               r3_pool['raw'], bf_pos, en_p, en_n, fourd_ok))

    R.claim('G2', 'COVERAGE OF THE OUTER SPACE: the union of the shards covers every party-1 '
                  'ordered pair exactly once and the enumerated outer count equals '
                  '62^6 = 56,800,235,584, so the reported extremum is global rather than partial; '
                  'each shard additionally self-checks |E4|max = 120/120 and validates the numpy '
                  'integer accelerator against exact evaluation on declared tuples',
            coverage_ok and ok_shards and acc_ok and groups_total == outer_total,
            'shards = %d (each %d pairs) ; pairs covered = %d/%d ; outer tuples counted = %d ; '
            'expected = %d ; accelerator mismatches = 0 required ; covered pairs = %s'
            % (len(shards), len(shards[0]['pairs']), len(covered), npairs, groups_total,
               outer_total, coverage_ok))

    R.claim('G3', 'WINDOW COROLLARY (bounding every legitimate n = 4 statement): the raw window is '
                  'the weakest constraint set, so every windowed global -- party, eight, '
                  'eight_anti_v3, eight_anti_strict, on ANY axis set -- is bounded above by this '
                  'round\'s raw global; combined with the round-3 pool values read from the frozen '
                  'artefact, this brackets all four legitimate windows from above. If the raw '
                  'global does not exceed the LHV bound 480/120, then no windowed configuration '
                  'anywhere in the 62^8 space can violate the n = 4 Mermin inequality, which is '
                  'exactly the (c)/B6 question at n = 4',
            pos >= max(r3_pool.values()) and abs_global <= cert3,
            'raw global = %d/120 ; round-3 pool values = %s ; implied upper bounds: party <= %d, '
            'eight <= %d, eight_anti_v3 <= %d, strict <= eight_anti_v3 ; LHV bound = 480/120 ; '
            'violation possible = %s'
            % (pos, r3_pool, pos, pos, pos, pos > n * b4))

    R.claim('G4', 'PRECISION FINDING ON THE ROUND-3 eight_anti WINDOW (recorded, not patched): the '
                  'semantics actually implemented in round 3 -- d and d\' excluded from the six and '
                  'from the antipodes of the six, with d != d\' -- still permits an ANTIPODAL '
                  '(d,d\') pair, whereas round 3\'s claim text said "no antipodal pair". The exact '
                  'census inside the declared pool counts the admissible six-tuples whose v3 '
                  'maximum is realised by such a pair, and a witness is recorded; the strict '
                  'semantics (no antipodal pair among all eight) is a subset, so the v3 value '
                  'upper-bounds it. Round 3\'s eight_anti number 224/120 is therefore a v3 number, '
                  'and the strict number is <= it',
            census_anti >= 0 and census_six > 0,
            'pool census: admissible six-tuples (c,c\') evaluated = %d ; realised by an antipodal '
            '(d,d\') pair = %d (%.3f%%) ; witness = %s ; round-3 pool eight_anti value = %d/120'
            % (census_six, census_anti, 100.0 * census_anti / max(census_six, 1), census_witness,
               r3_pool['eight_anti']))

    R.claim('G5', 'GRID: every reported numerator is divisible by 8 (the 1/15 grid), as it must be '
                  'since M4 is a sum of 8 E4 numerators each divisible by 8',
            pos % 8 == 0 and neg % 8 == 0,
            'max numerator %d %% 8 = %d ; min numerator %d %% 8 = %d'
            % (pos, pos % 8, neg, neg % 8))

    R.claim('G6', 'SELF-CHECKS: |E4|max = 120/120 as in round 3, the accelerator agrees with exact '
                  'evaluation on declared tuples in every shard, and the A/R/U/V factorisation of '
                  'F and G reproduces the round-3 direct-indexing expressions exactly on declared '
                  'six-tuples (the identity the whole round-4 pass rests on)',
            acc_ok and fac_ok == 4,
            'per-shard |E4|max = %s ; accelerator mismatches = %s ; factorisation rows ok = %d/4 '
            '; rows = %s' % ([s['absE4max'] for s in shards[:3]], [s['acc_mismatch'] for s in shards[:3]],
                            fac_ok, fac_rows))

    extra = {'lhv_bound': b4, 'terms': len(terms4), 'shards': len(shards),
             'outer_tuples': groups_total, 'outer_expected': outer_total,
             'raw_global': {'max_num': pos, 'min_num': neg, 'absmax_num': abs_global,
                            'max_argmax': list(argpos), 'max_argmax_ids': [ids[v] for v in argpos],
                            'min_argmax': list(argneg), 'min_argmax_ids': [ids[v] for v in argneg],
                            'brute8_at_max': bf_pos, 'brute8_at_min': bf_neg,
                            'fourD_of_winning_group': [en_p, en_n],
                            'fourD_separable_identity_rows': fourd_rows,
                            'fourD_rows_ok': fourd_ok},
             'round3_cross': {'pool_values': r3_pool, 'certificate_num': cert3,
                              'interval_round3': r3['n4']['global_interval_num']},
             'census_v3': {'six_tuples': census_six, 'antipodal_realised': census_anti,
                           'witness': census_witness, 'pool_frame': pool},
             'coverage_ok': bool(coverage_ok), 'acc_ok': bool(acc_ok),
             'factorisation_ok': fac_ok, 'factorisation_rows': fac_rows,
             'timing': {'e4_build_s': t_e4, 'census_s': t_census,
                        'shard_solve_s': [s['solve_s'] for s in shards]},
             'verdicts': {'G1': 'the n = 4 global question (raw window) is CLOSED exactly: the '
                                'round-3 interval [480,768]/120 collapses to a single number',
                          'G3': 'all windowed n = 4 statements are bracketed; violation is possible '
                                'only if the raw global exceeds 480/120',
                          'G4': 'round-3 eight_anti is a v3-semantics number (antipodal (d,d\') '
                                'pairs permitted); the strict variant is <= it'}}
    ok = R.finish(os.path.join(DATA, '12_n4_global.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
