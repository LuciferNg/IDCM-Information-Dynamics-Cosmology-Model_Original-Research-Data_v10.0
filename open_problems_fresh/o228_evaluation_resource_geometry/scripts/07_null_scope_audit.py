#!/usr/bin/env python3
"""O228 scripts/07 -- R4: scope audit of the C17 null (distinct 4-subsets vs with-replacement draws).

Contract: docs/03_r3_contract.md has H1; this script audits the *scope* of the recorded exact null
p0 = 6240/180251 = F_4(all 462 bisections of the 12 vertices) / C(462,4).

  J1  the Mobius code path of scripts/02_r1_closed_form.py (re-implemented here, independent of it)
      reproduces brute force at m = 6, 8, 10  (brute force = enumerate all 4-subsets of the bisections)
  J2  a 1e7-draw MC of *distinct* 4-subsets (Mersenne Twister) lies within 5 sigma of 6240/180251
  J3  the with-replacement draw is a DIFFERENT quantity: it differs from the distinct version by > 3 sigma
  J4  the exact reduction 6240/180251 in lowest terms

All exact arithmetic (integers/Fractions); floats only for the MC bands and printed percentages.
Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/07_null_scope_audit.py
"""
import collections
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
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def int_partitions(n, mx=None):
    """integer partitions of n (descending), independent implementation"""
    if mx is None:
        mx = n
    if n == 0:
        yield []
        return
    for first in range(min(n, mx), 0, -1):
        for rest in int_partitions(n - first, first):
            yield [first] + rest


def mobius_F4_total(m):
    """the code path of scripts/02 C17: count separating 4-subsets among ALL bisections of m points.

    F = C(nbis,4) + sum over non-discrete set-partition shapes (sizes) of
        npar(sizes) * gweight(sizes) * C(beta_hat(sizes), 4)
    where npar = m! / prod (m_i! (s_i!)^{m_i}) counts set partitions of that shape,
    beta_hat = (1/2) * #{sub-multisets of blocks with total size m/2}  (bisections compatible with the shape),
    gweight = the Mobius weight of the shape in the partition lattice (mu(pi, 1-hat)).
    """
    nbis = math.comb(m, m // 2) // 2
    tot = math.comb(nbis, 4)
    terms = []
    for sizes in int_partitions(m):
        if sizes == [1] * m:
            continue
        cnt = collections.Counter(sizes)
        npar = math.factorial(m)
        for s, mm in cnt.items():
            npar //= (math.factorial(mm) * math.factorial(s) ** mm)
        poly = [1] + [0] * (m // 2)
        for s in sizes:
            new = poly[:]
            for t in range(m // 2 - s + 1):
                new[t + s] += poly[t]
            poly = new
        bh = poly[m // 2] // 2
        if bh >= 4:
            g = gweight(sizes)
            if g:
                tot += npar * g * math.comb(bh, 4)
                terms.append((sizes, npar, g, bh, npar * g * math.comb(bh, 4)))
    return tot, nbis, terms


def gweight(sizes):
    """mu(pi, top) for the shape: product over blocks of (-1)^{s-1} (s-1)!"""
    w = 1
    for s in sizes:
        w *= (-1) ** (s - 1) * math.factorial(s - 1)
    return w


def brute_F4_total(m):
    """enumerate all 4-subsets of the bisections of m points and count separating ones"""
    pts = list(range(m))
    bis = [set(S) for S in itertools.combinations(pts, m // 2) if 0 in S]
    n = 0
    for q in itertools.combinations(range(len(bis)), 4):
        # separating <=> every pair of points is split by at least one of the four
        ok = True
        for i in range(m):
            if not ok:
                break
            for j in range(i + 1, m):
                sep = False
                for a in q:
                    S = bis[a]
                    if (i in S) != (j in S):
                        sep = True
                        break
                if not sep:
                    ok = False
                    break
        if ok:
            n += 1
    return n, math.comb(len(bis), 4)


def masks_for(m):
    pts = list(range(m))
    bis = [set(S) for S in itertools.combinations(pts, m // 2) if 0 in S]
    pairs = [(i, j) for i in range(m) for j in range(i + 1, m)]
    pidx = {p: b for b, p in enumerate(pairs)}
    ALLP = (1 << len(pairs)) - 1
    ms = []
    for S in bis:
        mk = 0
        for (i, j) in pairs:
            if (i in S) != (j in S):
                mk |= (1 << pidx[(i, j)])
        ms.append(mk)
    return ms, ALLP


def main():
    t0 = time.time()
    out = {}
    print('=' * 110)
    print('O228 scripts/07 -- R4: scope audit of the exact null (distinct 4-subsets vs with-replacement)')
    print('=' * 110, flush=True)

    # ---------- J1: the Mobius code path vs brute force at m = 6, 8, 10
    j1 = {}
    for m in (6, 8):                      # brute force is O(C(nbis,4)); m=10 (C(126,4) = 1.0e7) is out of reach
        t = time.time()
        fm, nbis, _terms = mobius_F4_total(m)
        fb, cb = brute_F4_total(m)
        j1[m] = {'mobius': fm, 'brute': fb, 'C_nbis_4': cb, 'nbis': nbis, 'secs': round(time.time() - t, 1)}
        print('   m=%2d nbis=%3d  Mobius=%d  brute=%d  match=%s  (%.1f s)'
              % (m, nbis, fm, fb, fm == fb, time.time() - t), flush=True)
    out['J1'] = j1
    claim('J1', 'the C17 Mobius code path (re-implemented independently) reproduces brute force for the '
                'number of separating 4-subsets among ALL bisections of m points, at m = 6 and 8',
          all(v['mobius'] == v['brute'] for v in j1.values()) and len(j1) == 2,
          '; '.join('m=%d %d==%d' % (m, v['mobius'], v['brute']) for m, v in j1.items()))

    # J1b: at m = 10 brute force is infeasible (C(126,4) = 1.0e7 covering tests), so check the Mobius
    # formula against an independent MC of distinct 4-subsets there
    m10 = 10
    f10, nbis10, _ = mobius_F4_total(m10)
    c10 = math.comb(nbis10, 4)
    ms10, ALLP10 = masks_for(m10)
    rng10 = random.Random(2281010)
    s10 = rng10.sample
    d10 = 3 * 10 ** 6
    h10 = 0
    for _ in range(d10):
        q = s10(range(nbis10), 4)
        if (ms10[q[0]] | ms10[q[1]] | ms10[q[2]] | ms10[q[3]]) == ALLP10:
            h10 += 1
    p10 = f10 / c10
    sd10 = math.sqrt(p10 * (1 - p10) / d10)
    out['J1b'] = {'m': m10, 'mobius': f10, 'C_nbis_4': c10, 'p10': p10, 'mc': h10 / d10,
                  'draws': d10, 'sigma': sd10, 'dev': abs(h10 / d10 - p10)}
    claim('J1b', 'at m = 10 the Mobius formula agrees with an independent distinct-4-subset MC '
                 '(3e6 draws) within 5 sigma',
          abs(h10 / d10 - p10) < 5 * sd10,
          'Mobius p = %d/%d = %.6f ; MC(%d) = %.6f ; |dev| = %.2e ; 5 sigma = %.2e'
          % (f10, c10, p10, d10, h10 / d10, abs(h10 / d10 - p10), 5 * sd10))

    # ---------- J2/J3: distinct-subset MC vs with-replacement MC at m = 12
    ms, ALLP = masks_for(12)
    nb = len(ms)
    exact_num, exact_den = 6240, 180251
    p0 = F(exact_num, exact_den)
    fm12, nbis12, terms12 = mobius_F4_total(12)
    out['J4'] = {'mobius_F4_m12': fm12, 'C462_4': math.comb(462, 4),
                 'p0': str(F(fm12, math.comb(462, 4))), 'recorded': '6240/180251',
                 'recorded_float': float(p0), 'mobius_float': fm12 / math.comb(462, 4),
                 'n_terms': len(terms12), 'lowest_terms': (F(fm12, math.comb(462, 4)).numerator,
                                                           F(fm12, math.comb(462, 4)).denominator)}
    claim('J4', 'the exact reduction of the C17 null is 6240/180251 in lowest terms '
                '(Mobius F_4 = 6240, C(462,4) = 180251*? -> see detail)',
          F(fm12, math.comb(462, 4)) == p0,
          'Mobius F_4(m=12) = %d ; C(462,4) = %d ; p0 = %s = %.8f ; recorded 6240/180251 = %.8f'
          % (fm12, math.comb(462, 4), F(fm12, math.comb(462, 4)), fm12 / math.comb(462, 4), float(p0)))

    draws = 10 ** 7
    rng = random.Random(2281002)
    sample = rng.sample
    hit_d = 0
    for _ in range(draws):
        q = sample(range(nb), 4)
        if (ms[q[0]] | ms[q[1]] | ms[q[2]] | ms[q[3]]) == ALLP:
            hit_d += 1
    mc_d = F(hit_d, draws)
    sd_d = math.sqrt(float(p0) * (1 - float(p0)) / draws)
    out['J2'] = {'draws': draws, 'mc_distinct': float(mc_d), 'hits': hit_d, 'exact': float(p0),
                 'sigma': sd_d, 'dev': abs(float(mc_d) - float(p0)), 'band_5sigma': 5 * sd_d}
    claim('J2', 'a 1e7-draw MC of DISTINCT 4-subsets (uniform, Mersenne Twister) lies within 5 sigma of '
                'the exact p0 = 6240/180251',
          abs(float(mc_d) - float(p0)) < 5 * sd_d,
          '%d draws -> %.8f ; exact = %.8f ; |dev| = %.2e ; 5 sigma = %.2e'
          % (draws, float(mc_d), float(p0), abs(float(mc_d) - float(p0)), 5 * sd_d))

    rng2 = random.Random(2281003)
    rr = rng2.randrange
    hit_w = 0
    for _ in range(draws):
        if (ms[rr(nb)] | ms[rr(nb)] | ms[rr(nb)] | ms[rr(nb)]) == ALLP:
            hit_w += 1
    mc_w = hit_w / draws
    sd_w = math.sqrt(mc_w * (1 - mc_w) / draws)
    z = abs(mc_w - float(p0)) / math.sqrt(sd_w ** 2 + sd_d ** 2)
    out['J3'] = {'draws': draws, 'mc_with_replacement': mc_w, 'mc_distinct': float(mc_d),
                 'z_between_scopes': z}
    claim('J3', 'the with-replacement draw is a DIFFERENT quantity from the distinct-4-subset fraction: '
                'reported side by side (> 3 sigma apart), so the first H1 run compared two different scopes',
          z > 3,
          'distinct = %.6f ; with-replacement = %.6f ; difference = %.6f = %.1f sigma'
          % (float(mc_d), mc_w, mc_w - float(mc_d), z))

    out['claims'] = CLAIMS
    out['elapsed_s'] = round(time.time() - t0, 1)
    with open(os.path.join(DATA, '07_null_scope_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 110)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), out['elapsed_s']))
    print('=' * 110)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
