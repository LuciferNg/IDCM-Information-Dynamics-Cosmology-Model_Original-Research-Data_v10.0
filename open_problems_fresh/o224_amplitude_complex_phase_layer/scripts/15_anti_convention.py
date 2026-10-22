#!/usr/bin/env python3
"""O224 scripts/15_anti_convention.py (round 4, addendum 3) -- discriminating test of the
tie-degeneracy hypothesis for the "antipodal-realised" counts.

BACKGROUND (why this script exists, stated before any number of this script is produced).

scripts/14 measured the rule-independent EXISTENCE count for the v3 eight_anti semantics: the
number of admissible six-tuples that admit ANY admissible antipodal (d,d') pair attaining their
exact v3 maximum.  Three other numbers exist in the record for what looked like the same thing:

  * 880  -- data/12_n4_global.json census_v3.antipodal_realised (round-4 census rule: top-2 x top-2
            via an argpartition-based topk helper, index-order tie break),
  * 392  -- scratch/probe_r4.py (probe rule: best d over all admissible axes, d' from the top-2 of
            G ordered by np.argsort(g)[::-1], whose reversal reverses the order of ties),
  * 1734 / 1794 -- scripts/14's own reconstructions of those two rules with an argsort(-g) tie order.

14's pre-registered claim Q3 predicted that 14's reconstructions would reproduce 880 and 392; it
FAILED (1734 / 1794), which is the phenomenon: the v3 maximum is heavily tie-degenerate, so "the
pair that realises it" is a SELECTION-RULE ARTEFACT while the existence question is not.

PRE-REGISTERED CLAIMS OF THIS SCRIPT.

T1  CONVENTION REPRODUCTION: re-running the recorded selection conventions verbatim reproduces the
    two recorded numbers exactly -- the probe convention (np.argsort(g)[::-1], first maximum in
    index order) gives 392, and the census convention (the argpartition-then-argsort(-value) topk
    of scripts/12) gives 880.  If either fails, the tie-degeneracy hypothesis is wrong.
T2  CONVENTION INVARIANCE OF THE EXISTENCE COUNT: recomputing the existence count with a different
    algorithm -- the full 62x62 outer sum f[d] + g[d'] with the diagonal and disallowed axes
    masked, taking the maximum, then testing every admissible antipodal ordered pair for equality
    -- reproduces scripts/14's 11318 exactly.  (Different algorithm, same quantity: this is the
    quantity that no tie convention can move.)
T3  RELATIONS: the census-rule count and the probe-rule count are both <= the existence count, the
    existence count is 24.5616% of the 46,080 domain, and the census-rule percentage recorded in
    docs/06 (1.910%) understates the incidence of the phenomenon by a factor of ~12.9.
T4  TIE-DEGENERACY WITNESSES: explicit six-tuples are printed for which the attaining set contains
    BOTH an antipodal and a non-antipodal pair, and the count of such "mixed" six-tuples is
    reported -- direct evidence for the mechanism, not merely an inference from the counts.

Exact integer arithmetic (common denominator 120); numpy as an integer accelerator; no new
parameters; writes only inside this O directory.
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
                E4[a, b, c, :] = (Wa * KA[s3, c]) @ KA[s4, :]
    return E4


def topk_census_style(arr, K):
    """verbatim re-implementation of scripts/12 topk(arr, K, largest=True)"""
    m = arr.shape[-1]
    idx = np.argpartition(arr, m - K, axis=-1)[..., m - K:]
    val = np.take_along_axis(arr, idx, axis=-1)
    order = np.argsort(-val, axis=-1)
    return np.take_along_axis(val, order, axis=-1), np.take_along_axis(idx, order, axis=-1)


def main():
    R = L.Report('15_anti_convention')
    print('=' * 108)
    print('O224 scripts/15 (round-4 addendum 3) -- discriminating test: tie conventions vs existence')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    pool = [i for i, ty in enumerate(types) if ty == 'vertex']
    na = len(pool)
    adx = np.arange(nax)
    negbig = -10 ** 9

    with io.open(os.path.join(DATA, '12_n4_global.json'), encoding='utf-8') as fh:
        cen4 = json.load(fh)['census_v3']
    with io.open(os.path.join(DATA, '14_census_exact.json'), encoding='utf-8') as fh:
        c14 = json.load(fh)
    n_exists14 = c14['existence_count']

    Xf = build_e4(nax, KA, NMUL, hxa)
    X = Xf[np.ix_(pool, pool, pool, np.arange(nax))]

    ed = [(x, y) for x in range(nax) for y in range(x + 1, nax) if anti[x, y]]
    ex = np.array([e[0] for e in ed], dtype=np.int64)
    ey = np.array([e[1] for e in ed], dtype=np.int64)

    domain = 0
    n_exists = 0
    n_census_conv = 0
    n_probe_conv = 0
    n_mixed = 0
    w_probe = w_census = w_mixed = None

    for a in pool:
        for ap in pool:
            for b in pool:
                for bp in pool:
                    four = (a, ap, b, bp)
                    if len(set(four)) != 4:
                        continue
                    if any(anti[four[i], four[j]] for i in range(4) for j in range(i + 1, 4)):
                        continue
                    Xab, Xapbp = X[a, b], X[ap, bp]
                    A = Xab - Xapbp
                    Rm = X[ap, b] + X[a, bp]
                    Ums = Xapbp - Xab
                    V = X[ap, b] + X[a, bp]
                    Fc = A[:, None, :] - Rm[None, :, :]
                    Gc = Ums[None, :, :] - V[:, None, :]
                    base = np.ones(nax, bool)
                    for s in four:
                        base &= (adx != s) & (~anti[s])
                    valid_c = np.array([x not in four for x in pool])
                    for ci in range(na):
                        if not valid_c[ci]:
                            continue
                        cx = pool[ci]
                        for cj in range(na):
                            if not valid_c[cj]:
                                continue
                            cy = pool[cj]
                            if cx == cy or anti[cx, cy]:
                                continue
                            if anti[cx, a] or anti[cx, ap] or anti[cx, b] or anti[cx, bp]:
                                continue
                            if anti[cy, a] or anti[cy, ap] or anti[cy, b] or anti[cy, bp]:
                                continue
                            allowed = base & (adx != cx) & (~anti[cx]) & (adx != cy) & (~anti[cy])
                            if int(allowed.sum()) < 2:
                                continue
                            domain += 1
                            f = np.where(allowed, Fc[ci, cj], negbig).astype(np.int64)
                            g = np.where(allowed, Gc[ci, cj], negbig).astype(np.int64)

                            # ---- T2 path: full 62x62 outer sum with diagonal + mask ----
                            M = f[:, None] + g[None, :]
                            mask = allowed[:, None] & allowed[None, :] & ~np.eye(nax, dtype=bool)
                            M = np.where(mask, M, negbig)
                            Vfull = int(M.max())
                            ok_edges = allowed[ex] & allowed[ey]
                            xe, ye = ex[ok_edges], ey[ok_edges]
                            anti_attr = ((f[xe] + g[ye] == Vfull) | (f[ye] + g[xe] == Vfull))
                            if anti_attr.any():
                                n_exists += 1
                            # ---- mixed-degeneracy witness (antipodal and non-antipodal attainers)
                            att = np.argwhere(M == Vfull)
                            has_anti = has_nonanti = False
                            d1 = d2 = -1
                            for (d1, d2) in att:
                                if anti[d1, d2]:
                                    has_anti = True
                                else:
                                    has_nonanti = True
                                if has_anti and has_nonanti:
                                    break
                            if has_anti and has_nonanti:
                                n_mixed += 1
                                if w_mixed is None:
                                    w_mixed = {'six': [a, ap, b, bp, cx, cy],
                                               'value': Vfull,
                                               'antipodal_example': [int(d1), int(d2)],
                                               'attainers': int(len(att))}

                            # ---- probe convention: np.argsort(g)[::-1], first max in index order
                            hi = [int(i) for i in np.argsort(g)[::-1] if allowed[i]][:2]
                            pos, arg = None, None
                            for d in range(nax):
                                if not allowed[d]:
                                    continue
                                dd = hi[1] if d == hi[0] else hi[0]
                                v = int(f[d]) + int(g[dd])
                                if pos is None or v > pos:
                                    pos, arg = v, (d, dd)
                            if arg is not None and pos == Vfull and anti[arg[0], arg[1]]:
                                n_probe_conv += 1
                                if w_probe is None:
                                    w_probe = {'six': [a, ap, b, bp, cx, cy], 'd_dp': list(arg),
                                               'value': pos}

                            # ---- census convention: argpartition topk on both sides ----
                            Fm = np.where(allowed, Fc[ci, cj], negbig).astype(np.int64)
                            Gm = np.where(allowed, Gc[ci, cj], negbig).astype(np.int64)
                            vF, iF = topk_census_style(Fm[None, :], 2)
                            vG, iG = topk_census_style(Gm[None, :], 2)
                            iF, iG = iF[0], iG[0]
                            cb, cp_ = None, None
                            for d1 in iF:
                                for d2 in iG:
                                    if d1 == d2:
                                        continue
                                    v = int(f[d1]) + int(g[d2])
                                    if cb is None or v > cb:
                                        cb, cp_ = v, (int(d1), int(d2))
                            if cp_ is not None and cb == Vfull and anti[cp_[0], cp_[1]]:
                                n_census_conv += 1
                                if w_census is None:
                                    w_census = {'six': [a, ap, b, bp, cx, cy], 'd_dp': list(cp_),
                                                'value': cb}

    R.claim('T1', 'CONVENTION REPRODUCTION: re-running the two recorded selection conventions '
                  'verbatim reproduces the two recorded numbers exactly -- probe convention = 392, '
                  'census convention = 880 -- which identifies the discrepancy as a tie-convention '
                  'artefact rather than a disagreement about the v3 semantics',
            n_probe_conv == 392 and n_census_conv == cen4['antipodal_realised'] == 880,
            'probe convention = %d (recorded 392) ; census convention = %d (recorded %s) ; '
            'domain = %d ; witnesses: probe %s / census %s'
            % (n_probe_conv, n_census_conv, cen4['antipodal_realised'], domain,
               json.dumps(w_probe, ensure_ascii=False), json.dumps(w_census, ensure_ascii=False)))

    R.claim('T2', 'CONVENTION INVARIANCE OF THE EXISTENCE COUNT: the full 62x62 outer-sum algorithm '
                  '(different from scripts/14\'s top-2-based maximum) reproduces the existence '
                  'count 11318 exactly, so the quantity reported by scripts/14 is not movable by any '
                  'tie convention',
            n_exists == n_exists14 == 11318,
            'this script (62x62 outer sum) = %d ; scripts/14 (top-2 based) = %d ; domain = %d'
            % (n_exists, n_exists14, domain))

    R.claim('T3', 'RELATIONS: the census-rule and probe-rule counts are both lower bounds on the '
                  'existence count, and the existence incidence is 24.5616% of the 46,080 domain, so '
                  'the 1.910% recorded in docs/06 (census rule) understates the phenomenon by a '
                  'factor of about 12.9',
            (n_census_conv <= n_exists and n_probe_conv <= n_exists and domain == 46080
             and n_exists * 10000 // domain == 2456),
            'existence = %d/%d = %.4f%% ; census rule = %d (%.4f%%) ; probe rule = %d (%.4f%%) ; '
            'ratio existence/census-rule = %.2f'
            % (n_exists, domain, 100.0 * n_exists / domain, n_census_conv,
               100.0 * n_census_conv / domain, n_probe_conv, 100.0 * n_probe_conv / domain,
               float(n_exists) / n_census_conv))

    R.claim('T4', 'TIE-DEGENERACY WITNESSES: six-tuples exist whose attaining set contains both an '
                  'antipodal and a non-antipodal pair, and the number of such mixed six-tuples is '
                  'reported -- direct evidence for the mechanism behind the convention-dependent '
                  'counts',
            n_mixed > 0 and w_mixed is not None,
            'mixed (both antipodal and non-antipodal attainers) six-tuples = %d ; witness = %s'
            % (n_mixed, json.dumps(w_mixed, ensure_ascii=False)))

    extra = {'domain': domain, 'existence_count': n_exists,
             'census_convention_count': n_census_conv, 'probe_convention_count': n_probe_conv,
             'mixed_count': n_mixed,
             'recorded': {'census_v3.antipodal_realised': cen4['antipodal_realised'],
                          'probe_r4.py': 392,
                          'scripts_14_Q3_reconstruction': {'census_rule': 1734, 'probe_rule': 1794}},
             'witnesses': {'probe_convention': w_probe, 'census_convention': w_census,
                           'mixed_attainment': w_mixed},
             'verdict': 'the "antipodal-realised" counts 392 / 880 / 1734 / 1794 are four tie '
                        'conventions of one degenerate maximum; the rule-independent existence '
                        'count is 11318 of 46080 = 24.5616%'}
    ok = R.finish(os.path.join(DATA, '15_anti_convention.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
