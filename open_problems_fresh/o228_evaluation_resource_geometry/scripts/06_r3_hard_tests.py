#!/usr/bin/env python3
"""O228 scripts/06 -- R3: the two remaining section-five hard tests.

Contract: docs/03_r3_contract.md  (o228-r3-hardtests-v1)
  H1  the null of R1 C17-c replayed at 1e7 draws, checked against the exact p0 within 5 sigma
  H2  structural rigidity: single column deletion / single line deletion / random line substitution on M_2I

Exact integers for every frame count; the only floating point is the MC band and printed percentages.
Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/06_r3_hard_tests.py
"""
import collections
import importlib.util
import io
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def fk4_of_cols(m, cols):
    """exact F_4 from a list of column sign-vectors, by the type-set form (fast for 62 columns)"""
    cls = {}
    for a, v in enumerate(cols):
        cls.setdefault(min(v, tuple(-x for x in v)), []).append(a)
    types = sorted(cls.keys())
    mults = [len(cls[t]) for t in types]
    pairs = [(i, j) for i in range(m) for j in range(i + 1, m)]
    ALLP = (1 << len(pairs)) - 1
    tpm = []
    for t in types:
        v = t
        mk = 0
        for b, (i, j) in enumerate(pairs):
            if v[i] != v[j]:
                mk |= (1 << b)
        tpm.append(mk)
    tot = 0
    for r in range(1, 5):
        for Ts in itertools.combinations(range(len(types)), r):
            mk = 0
            for i in Ts:
                mk |= tpm[i]
            if mk != ALLP:
                continue
            poly = [1]
            for i in Ts:
                coef = [math.comb(mults[i], t) for t in range(1, mults[i] + 1)]
                new = [0] * (len(poly) + len(coef))
                for u, cu in enumerate(poly):
                    if cu == 0:
                        continue
                    for v2, cv in enumerate(coef, start=1):
                        new[u + v2] += cu * cv
                poly = new
            tot += poly[4] if 4 < len(poly) else 0
    return tot


def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/06 -- R3: section-five hard tests (10^7 null band + structural rigidity)')
    print('=' * 112, flush=True)

    sp = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
    mX = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mX)
    m, K, MUL, hx, ids, types = mX.load_machine()
    axes, U, ids_u, types_u, hvec = m.load_inputs()
    Gf, idx, MULg = m.build_group()

    # rows = the 12 distinct icosahedron vertices; cols = the 62 sign vectors (exactly as R1)
    KV = [m.rot_ref(q, U[0]) for q in Gf]
    rows, seen = [], set()
    for r in KV:
        key = tuple((x[0], x[1]) for x in r)
        if key not in seen:
            seen.add(key)
            rows.append(r)
    cols = []
    for a in range(62):
        u = U[a]
        col = []
        for r in rows:
            dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
            s = m.sgn(dot)
            if s == 0:
                for comp in r:
                    sc = m.sgn(comp)
                    if sc:
                        s = sc
                        break
            col.append(s)
        cols.append(tuple(col))
    F4_base = fk4_of_cols(12, cols)
    print('M_2I reference: m=12 N=62 F_4 = %d' % F4_base, flush=True)

    # ------------- H1: 1e7-draw MC band on the R1 null
    half = [s for s in itertools.combinations(range(12), 6) if 0 in s]
    pl = [(i, j) for i in range(12) for j in range(i + 1, 12)]
    pidx = {p: b for b, p in enumerate(pl)}
    ALLX = (1 << len(pl)) - 1
    bm = []
    for S in half:
        mk = 0
        for (i, j) in pl:
            if (i in S) != (j in S):
                mk |= (1 << pidx[(i, j)])
        bm.append(mk)
    draws = 10 ** 7
    # H1-c correction (TWO defects in the first run):
    #  (1) SCOPE: the recorded exact p0 = 6240/180251 is the fraction of *distinct* 4-subsets of the 462
    #      bisections (its denominator is C(462,4)); the first run drew WITH REPLACEMENT (462^4), a
    #      different quantity (~0.0341 vs 0.03462).  Corrected: sample 4 DISTINCT bisections uniformly.
    #  (2) the LCG-vs-Mersenne-Twister note: both RNGs agree (~0.0341 for the with-replacement scope), so
    #      the first-run failure was the scope mismatch, not RNG drift.  MT is kept anyway.
    rng_h1 = random.Random(20261002)
    smp = rng_h1.sample
    hit = 0
    nb = len(bm)
    for _ in range(draws):
        q = smp(range(nb), 4)
        if (bm[q[0]] | bm[q[1]] | bm[q[2]] | bm[q[3]]) == ALLX:
            hit += 1
    mc = hit / draws
    p0 = float(F(6240, 180251))
    sd = math.sqrt(p0 * (1 - p0) / draws)
    out['H1'] = {'draws': draws, 'mc': mc, 'exact_p0': p0, 'sigma': sd, 'band_5sigma': 5 * sd,
                 'dev': abs(mc - p0), 'secs': round(time.time() - t0, 1)}
    claim('H1', 'section-five (2): the null MC at 1e7 draws of DISTINCT 4-subsets (Mersenne Twister) lies '
                'within 5 sigma of the exact p0 = 6240/180251 (the exact value stays authoritative)',
          abs(mc - p0) < 5 * sd,
          '%d draws -> MC = %.6f ; exact = %.6f ; |dev| = %.2e ; 5 sigma = %.2e (%.0f s)'
          % (draws, mc, p0, abs(mc - p0), 5 * sd, time.time() - t0))

    # ------------- H2a/b/c: deletion + substitution rigidity
    del_col = {}
    for a in range(62):
        del_col[a] = fk4_of_cols(12, cols[:a] + cols[a + 1:])
    # H2b-c correction: pair the columns into the 31 GEOMETRIC lines by verifying U[2k+1] = -U[2k]
    # in the frozen Q(sqrt5) axis vectors (the sign-partner pairing used in the first run is invalid
    # for the edge lines, whose two columns are not exact negations because tau is not odd at ties)
    lines = []
    used_l = set()
    for a in range(62):
        if a in used_l:
            continue
        for b in range(62):
            if b == a or b in used_l:
                continue
            if all(m.add(U[a][j], U[b][j]) == (0, 0) for j in range(3)):
                lines.append((a, b))
                used_l.add(a)
                used_l.add(b)
                break
    assert len(lines) == 31, 'expected 31 +- lines, found %d' % len(lines)
    out['line_pairing'] = {'n_lines': len(lines), 'pair_rule': 'U[2k+1] = -U[2k] (exact)',
                           'first_pairs': lines[:3]}
    del_line = {}
    for (a, b) in lines:
        remain = [cols[i] for i in range(62) if i not in (a, b)]
        del_line[(a, b)] = fk4_of_cols(12, remain)
    fam = {}
    for (a, b) in lines:
        t = ids_u[a][0]
        fam.setdefault(t, []).append((a, b))
    del_col_hist = collections.Counter(del_col.values())
    del_line_hist = collections.Counter(del_line.values())
    fam_col = {t: sorted({del_col[a] for (a, b) in v for a in (a, b)}) for t, v in fam.items()}
    fam_line = {t: sorted({del_line[l] for l in v}) for t, v in fam.items()}
    out['H2_deletion'] = {'F4_base': F4_base, 'per_column': del_col_hist, 'per_line': del_line_hist,
                          'family_values_column': fam_col, 'family_values_line': fam_line,
                          'column_value_multiplicities': {str(v): c for v, c in
                                                          sorted(collections.Counter(del_col.values()).items())},
                          'column_family_mult': {t: len(v) * 2 for t, v in fam.items()}}
    claim('H2a', 'section-five (4): the 62 single-column deletions give exactly 3 distinct F_4 values with '
                 'multiplicities (12, 20, 30) (the V/F/E group orbits are transitive), each < 12645',
          len(del_col_hist) == 3 and all(v < F4_base for v in del_col_hist)
          and sorted(del_col_hist.values()) == [12, 20, 30],
          'values -> multiplicities = %s ; family values (per column) = %s'
          % (out['H2_deletion']['column_value_multiplicities'], fam_col))
    claim('H2b', 'section-five (4): the 31 single-line deletions give exactly 3 distinct F_4 values with '
                 'multiplicities (6, 10, 15), each < 12645',
          len(del_line_hist) == 3 and all(v < F4_base for v in del_line_hist)
          and sorted(del_line_hist.values()) == [6, 10, 15],
          'values -> multiplicities = %s ; family values (per line) = %s'
          % ({str(v): c for v, c in sorted(del_line_hist.items())}, fam_line))

    claim('H2a-c', 'CORRECTED (H2a failed): the deletion spectrum is finer than the V/F/E orbits - the '
                    'frozen tie rule tau is NOT 2I-equivariant (it reads the first non-zero component of the '
                    'row), so within V and within F the lines split further; every single deletion still '
                    'reduces F_4',
          all(v < F4_base for v in del_col_hist) and len(del_col_hist) >= 4 and len(fam_col['V']) == 2,
          'distinct values = %d ; values = %s ; per-family values = %s'
          % (len(del_col_hist), out['H2_deletion']['column_value_multiplicities'], fam_col))
    claim('H2b-c', 'CORRECTED (H2b failed): same for the 31 geometric lines (paired by U[2k+1] = -U[2k]); '
                    'every line deletion reduces F_4',
          all(v < F4_base for v in del_line_hist) and len(del_line_hist) >= 3,
          'distinct values = %d ; values = %s ; per-family values = %s'
          % (len(del_line_hist), {str(v): c for v, c in sorted(del_line_hist.items())}, fam_line))

    rng = random.Random(228228)
    changed = 0
    vals = []
    for _ in range(200):
        S = set(rng.choice(half))
        li = rng.randrange(31)
        a, b = lines[li]
        remaining = [cols[i] for i in range(62) if i not in (a, b)]
        v = tuple(1 if i in S else -1 for i in range(12))
        new_cols = remaining + [v, tuple(-x for x in v)]
        f = fk4_of_cols(12, new_cols)
        vals.append(f)
        if f != F4_base:
            changed += 1
    out['H2c'] = {'draws': 200, 'changed': changed, 'min': min(vals), 'max': max(vals),
                  'median': sorted(vals)[100], 'seed': 228228}
    claim('H2c', 'section-five (4): substituting one random bisection for one line (seed 228228, 200 draws, '
                 'Mersenne Twister) changes F_4 at least 190 times out of 200',
          changed >= 190,
          'changed = %d/200 ; F_4 range = [%d, %d] ; median = %d (base %d)'
          % (changed, min(vals), max(vals), sorted(vals)[100], F4_base))

    # ------------- verdict
    out['H2d_reference'] = {'R1_C18': 'equivariant tie rule -> 16 types / F_4 = 12645 -> 1000 (12.6x)'}
    verdict_ok = (len(del_col_hist) == 3 and len(del_line_hist) == 3 and changed >= 190)
    claim('H2v', 'section-five (4) VERDICT (pre-registered direction): the resource counts are NOT structurally '
                 'rigid - F_4 responds to every single deletion/line deletion and to ~all random substitutions, '
                 'and R1 C18 shows a 12.6x swing from the tie convention alone',
          verdict_ok,
          'deletion values = 3 distinct per family ; substitution changes = %d/200 ; convention swing = 12645 -> 1000'
          % changed)

    claim('H2v-c', 'CORRECTED VERDICT (H2v failed on its own pre-registered condition): the resource counts are '
                   'NOT structurally rigid - 62/62 single-column and 31/31 single-line deletions strictly reduce '
                   'F_4, the deletion spectrum splits into 4 (columns) / 7 (lines) classes instead of the V/F/E '
                   'orbits, 199/200 random line substitutions change F_4 (range 10987..17507), and the tie '
                   'convention alone swings it 12.6x (R1 C18)',
          all(v < F4_base for v in del_col_hist) and all(v < F4_base for v in del_line_hist)
          and len(del_col_hist) >= 4 and len(del_line_hist) >= 7 and changed >= 190,
          'column deletion values = %d classes (all < %d) ; line deletion values = %d classes (all < %d) ; '
          'substitutions changed = %d/200 ; convention = 12645 -> 1000'
          % (len(del_col_hist), F4_base, len(del_line_hist), F4_base, changed))

    out['claims'] = CLAIMS
    out['elapsed_s'] = round(time.time() - t0, 1)
    with io.open(os.path.join(DATA, '06_r3_hard_tests.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
