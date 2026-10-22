#!/usr/bin/env python3
"""O224 scripts/14_census_exact.py (round 4, addendum 2) -- the exact EXISTENCE census for the
v3 eight_anti precision finding, prompted by a discrepancy between two independent codes.

WHY THIS SCRIPT EXISTS (stated before any number of this script is produced).

The round-4 census (scripts/12, claim G4) counted 880 of the 46,080 admissible six-tuples as
"the v3 maximum is realised by an antipodal (d,d') pair".  The round-4 scratch probe
(scratch/probe_r4.py, a different selection rule: best d over all admissible axes, d' over the
top-2 of G) counted 392 over what is claimed here to be the SAME domain.  Both codes are
correct but they answer a SELECTION-RULE-dependent question, so neither number is the quantity
the finding needs.  The finding needs the EXISTENCE question:

    does the six-tuple admit ANY admissible antipodal pair (d,d') that ATTAINS the v3 maximum?

PRE-REGISTERED CLAIMS.

Q1  DOMAIN: the admissible-six-tuple domain (all six drawn from the 12 vertex axes, pairwise
    distinct, no antipodal pair among the six) has 46,080 elements, matching the round-4 census
    field census_v3.six_tuples exactly.
Q2  EXACT EXISTENCE COUNT: the number of six-tuples admitting an admissible antipodal (d,d')
    pair attaining the v3 maximum, computed exactly (max over d in A0 of F[d] + best G[d'] with
    d' != d, then an explicit search over the admissible antipodal pairs for equality with that
    maximum), is reported.  It must satisfy count >= max(880, 392): both the census-rule and the
    probe-rule instances are genuine attained maxima, hence certified lower bounds.
Q3  RULE DEPENDENCE: the census rule (top-2 of F x top-2 of G, index-order tie break) and the
    probe rule (all d x top-2 of G) are recomputed here and must reproduce 880 and 392
    respectively, demonstrating that the attribution "the realising pair is antipodal" is a
    selection-rule artefact and that the existence count is the only rule-independent quantity.
Q4  WITNESS: one six-tuple is kept for each of the three counts (existence, census rule, probe
    rule) so the three notions are separately checkable.

Exact arithmetic (integers, common denominator 120); numpy as an integer accelerator; no new
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
                W = Wa * KA[s3, c]
                E4[a, b, c, :] = W @ KA[s4, :]
    return E4


def main():
    R = L.Report('14_census_exact')
    print('=' * 108)
    print('O224 scripts/14 (round-4 addendum 2) -- exact existence census for eight_anti v3')
    print('=' * 108, flush=True)

    G, idx, MUL, U, ids, types, hx, K = L.load_machine()
    n, nax = len(G), len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    pool = [i for i, ty in enumerate(types) if ty == 'vertex']

    with io.open(os.path.join(DATA, '12_n4_global.json'), encoding='utf-8') as fh:
        r4 = json.load(fh)
    cen4 = r4['census_v3']

    Xf = build_e4(nax, KA, NMUL, hxa)
    X = Xf[np.ix_(pool, pool, pool, np.arange(nax))]     # first three parties = pool, d = all axes
    na = len(pool)
    adx = np.arange(nax)
    negbig = -10 ** 9
    # antipodal edges as arrays, for a vectorised existence test
    ed = [(x, y) for x in range(nax) for y in range(x + 1, nax) if anti[x, y]]
    ex = np.array([e[0] for e in ed], dtype=np.int64)
    ey = np.array([e[1] for e in ed], dtype=np.int64)
    print('antipodal edges = %d (axes = %d ; each axis has exactly one partner = %s)'
          % (len(ed), nax, len(ed) * 2 == nax), flush=True)

    valid_six = 0
    n_exists = 0
    n_census_rule = 0
    n_probe_rule = 0
    w_exists = w_census = w_probe = None

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
                    # F[c, c', d] and G[c, c', d'] over the whole 62-axis d range
                    Fc = (A[:, None, :] - Rm[None, :, :])[..., :]          # (c, c', d)
                    Gc = (Ums[None, :, :] - V[:, None, :])[..., :]         # (c, c', d')
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
                            if not allowed.any():
                                continue
                            six = (a, ap, b, bp, cx, cy)
                            f = np.where(allowed, Fc[ci, cj], negbig).astype(np.int64)
                            g = np.where(allowed, Gc[ci, cj], negbig).astype(np.int64)
                            # ---- exact maximum: max over d in A0 of F[d] + best G[d'] != d ----
                            order = [int(i) for i in np.argsort(-g) if allowed[i]]
                            if len(order) < 2:
                                continue
                            valid_six += 1
                            best = None
                            for d in range(nax):
                                if not allowed[d]:
                                    continue
                                dd = order[0] if order[0] != d else order[1]
                                v = int(f[d]) + int(g[dd])
                                if best is None or v > best:
                                    best = v
                            # ---- existence of an admissible antipodal pair attaining it ----
                            ok_edges = allowed[ex] & allowed[ey]
                            pair_hit = False
                            if ok_edges.any():
                                xe, ye = ex[ok_edges], ey[ok_edges]
                                hits = ((f[xe] + g[ye] == best) | (f[ye] + g[xe] == best))
                                if hits.any():
                                    pair_hit = True
                                    if w_exists is None:
                                        j = int(np.argmax(hits))
                                        w_exists = {'six': list(six),
                                                    'd_dp': [int(xe[j]), int(ye[j])],
                                                    'value': int(best)}
                            if pair_hit:
                                n_exists += 1
                            # ---- census rule: top-2 of F x top-2 of G, index-order tie break ----
                            iF = [int(i) for i in np.argsort(-f) if allowed[i]][:2]
                            iG = [int(i) for i in np.argsort(-g) if allowed[i]][:2]
                            cb, cp_ = None, None
                            for d1 in iF:
                                for d2 in iG:
                                    if d1 == d2:
                                        continue
                                    v = int(f[d1]) + int(g[d2])
                                    if cb is None or v > cb:
                                        cb, cp_ = v, (d1, d2)
                            if cp_ is not None and cb == best and anti[cp_[0], cp_[1]]:
                                n_census_rule += 1
                                if w_census is None:
                                    w_census = {'six': list(six), 'd_dp': list(cp_), 'value': int(cb)}
                            # ---- probe rule: best d over all A0 x top-2 of G ----
                            pg = None
                            for d1 in range(nax):
                                if not allowed[d1]:
                                    continue
                                d2 = iG[0] if iG[0] != d1 else iG[1]
                                v = int(f[d1]) + int(g[d2])
                                if pg is None or v > pg[0]:
                                    pg = (v, (d1, d2))
                            if pg is not None and pg[0] == best and anti[pg[1][0], pg[1][1]]:
                                n_probe_rule += 1
                                if w_probe is None:
                                    w_probe = {'six': list(six), 'd_dp': list(pg[1]),
                                               'value': int(pg[0])}

    R.claim('Q1', 'DOMAIN: the admissible-six-tuple domain (six pairwise distinct vertex axes, no '
                  'antipodal pair among the six) has 46,080 elements, matching the round-4 census '
                  'field census_v3.six_tuples exactly, so the three counts below are computed over '
                  'one and the same domain',
            valid_six == cen4['six_tuples'] == 46080,
            'this script = %d ; round-4 census = %s' % (valid_six, cen4['six_tuples']))

    R.claim('Q2', 'EXACT EXISTENCE COUNT: the number of admissible six-tuples that admit ANY '
                  'admissible antipodal (d,d\') pair attaining the exact v3 maximum (max over d in '
                  'A0 of F[d] + best G[d\'] with d\' != d, then an explicit equality search over all '
                  'admissible antipodal pairs) is reported; it must be at least max(880, 392) '
                  'because every census-rule and probe-rule instance is a certified attained '
                  'antipodal maximum',
            n_exists >= max(cen4['antipodal_realised'], 392) and n_exists <= valid_six,
            'exact existence count = %d of %d (%.4f%%) ; certified lower bounds: census rule = %d, '
            'probe rule = %d ; domain = %d'
            % (n_exists, valid_six, 100.0 * n_exists / valid_six, cen4['antipodal_realised'],
               n_probe_rule, valid_six))

    R.claim('Q3', 'RULE DEPENDENCE: the census rule (top-2 x top-2, index-order tie break) and the '
                  'probe rule (best d over A0, d\' over the top-2 of G) each reproduce their own '
                  'round-4 counts (880 and 392), which shows that "the realising pair is antipodal" '
                  'is selection-rule dependent: both are genuine sub-counts of the exact existence '
                  'count, and only the existence count is rule independent',
            n_census_rule == cen4['antipodal_realised'] == 880 and n_probe_rule == 392,
            'census rule = %d (round-4 field %s) ; probe rule = %d (scratch probe 392) ; exact '
            'existence = %d' % (n_census_rule, cen4['antipodal_realised'], n_probe_rule, n_exists))

    R.claim('Q4', 'WITNESSES: one witness six-tuple (with its antipodal pair and value) is kept for '
                  'each of the three counts, so the existence count, the census rule and the probe '
                  'rule are separately checkable',
            None not in (w_exists, w_census, w_probe),
            'existence witness = %s ; census-rule witness = %s ; probe-rule witness = %s'
            % (json.dumps(w_exists, ensure_ascii=False), json.dumps(w_census, ensure_ascii=False),
               json.dumps(w_probe, ensure_ascii=False)))

    extra = {'domain': valid_six,
             'existence_count': n_exists,
             'census_rule_count': n_census_rule,
             'probe_rule_count': n_probe_rule,
             'round4_census_field': cen4['antipodal_realised'],
             'witnesses': {'existence': w_exists, 'census_rule': w_census, 'probe_rule': w_probe},
             'verdict': 'the exact existence count is the rule-independent statement of the round-4 '
                        'eight_anti precision finding; the census rule 880 is a certified lower '
                        'bound and the probe rule 392 is a weaker sub-count (both reproduce here)'}
    ok = R.finish(os.path.join(DATA, '14_census_exact.json'), extra)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
