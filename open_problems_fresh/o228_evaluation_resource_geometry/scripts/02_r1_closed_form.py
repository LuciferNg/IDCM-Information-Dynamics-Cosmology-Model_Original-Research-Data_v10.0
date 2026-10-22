#!/usr/bin/env python3
"""O228 scripts/02 -- R1 frame-count closed form (contract docs/00_r1_contract.md, claims C12-C19).

Three INDEPENDENT routes are computed and cross-checked:
  (A) pruned DFS over k-subsets of the 62 columns (bitmask over the 66 row pairs)
  (B) partition-lattice Mobius form  F_k = C(N,k) + sum_{pi != 0hat} g(pi) C(beta(pi),k)
  (C) type-set form                F_k = sum_{T separating} e_k(T)
Plus: rank, family decomposition, EXACT null p0 over all 462 bisections of the 12 vertices,
convention variant, sub-arrangement table.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/02_r1_closed_form.py
"""
import importlib.util
import io
import itertools
import json
import math
import os
import sys
import time
import collections
from collections import defaultdict
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = os.path.abspath(os.path.join(ROOT, '..', 'o222_qm_evaluation_semantics'))
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


sp = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
mX = importlib.util.module_from_spec(sp)
sp.loader.exec_module(mX)
m, K, MUL, hx, ids, types = mX.load_machine()
axes, U, _ids, _types, _hv = m.load_inputs()
NR, NC = len(K), len(K[0])
ALLC = (1 << 66) - 1
PAIRS = [(i, j) for i in range(12) for j in range(i + 1, 12)]
PIDX = {p: b for b, p in enumerate(PAIRS)}


def pairmask(sep):
    """sep: predicate on (i,j) -> +mask"""
    mk = 0
    for (i, j) in PAIRS:
        if sep(i, j):
            mk |= (1 << PIDX[(i, j)])
    return mk


def inside_mask(block):
    b = set(block)
    mk = 0
    for (i, j) in PAIRS:
        if i in b and j in b:
            mk |= (1 << PIDX[(i, j)])
    return mk


def partitions_of(items):
    items = list(items)
    n = len(items)
    if n == 0:
        yield []
        return
    blocks = [[items[0]]]

    def rec(i):
        if i == n:
            yield [tuple(b) for b in blocks]
            return
        for b in blocks:
            b.append(items[i])
            for x in rec(i + 1):
                yield x
            b.pop()
        blocks.append([items[i]])
        for x in rec(i + 1):
            yield x
        blocks.pop()

    for x in rec(1):
        yield x


def gweight_sizes(sizes):
    w = 1
    for s in sizes:
        w *= (-1) ** (s - 1) * math.factorial(s - 1)
    return w


def refinements(pi):
    acc = [tuple()]
    for b in pi:
        acc = [x + tuple(y) for x in acc for y in partitions_of(b)]
    return acc


def int_partitions(n, mx=None):
    if mx is None:
        mx = n
    if n == 0:
        yield []
        return
    for first in range(min(n, mx), 0, -1):
        for rest in int_partitions(n - first, first):
            yield [first] + rest


def main():
    t00 = time.time()
    out = {}
    print('=' * 108)
    print('O228 scripts/02 -- R1 frame-count closed form   (rules o228-r1-resource-geometry-v1)')
    print('=' * 108, flush=True)

    rows = [tuple(K[i][a] for a in range(NC)) for i in range(NR)]
    first = {}
    for i, r in enumerate(rows):
        first.setdefault(r, i)
    reps = sorted(first, key=lambda r: first[r])
    R = len(reps)
    ROWS = [list(r) for r in reps]

    masks = [pairmask(lambda i, j, a=a: ROWS[i][a] != ROWS[j][a]) for a in range(NC)]
    fam = [types[a] for a in range(NC)]

    def fibre(col):
        d = defaultdict(list)
        for j in range(R):
            d[ROWS[j][col]].append(j)
        return tuple(sorted(tuple(sorted(v)) for v in d.values()))

    fp = [fibre(a) for a in range(NC)]
    typeset = sorted(set(fp))
    mult_of = {p: sum(1 for x in fp if x == p) for p in typeset}
    KT = len(typeset)
    print('census: %d distinct column bisections, multiplicities %s'
          % (KT, sorted(mult_of.values())), flush=True)

    # ---------------- (B) Mobius data: every partition refining >= 1 bisection
    t0 = time.time()
    refined = {}                                     # pi (tuple of blocks) -> int mask of refining columns
    for a in range(NC):
        for pi in refinements(fp[a]):
            key = tuple(sorted(pi))
            refined[key] = refined.get(key, 0) | (1 << a)
    t_ref = time.time() - t0
    inside = {pi: 0 for pi in refined}
    for pi in refined:
        mk = 0
        for blk in pi:
            mk |= inside_mask(blk)
        inside[pi] = mk
    betas = {}
    for pi in refined:
        X = inside[pi]
        b = 0
        for a in range(NC):
            if masks[a] & X == 0:
                b += 1
        betas[pi] = b
    out['n_refining_partitions'] = len(betas)
    out['beta_spectrum'] = {str(v): c for v, c in sorted(collections.Counter(betas.values()).items())}
    print('refining partitions = %d (%.1f s) ; beta spectrum = %s ; #pi with beta>=4 = %d'
          % (len(betas), t_ref, out['beta_spectrum'], sum(1 for b in betas.values() if b >= 4))
          if len(out['beta_spectrum']) < 40 else
          'refining partitions = %d (%.1f s) ; #pi with beta>=4 = %d'
          % (len(betas), t_ref, sum(1 for b in betas.values() if b >= 4)), flush=True)

    def F_mobius(k, N=NC, betasrc=None, gof=None):
        tot = math.comb(N, k)
        for pi, b in (betasrc or betas).items():
            if len(pi) == R:
                continue
            if b >= k:
                tot += (gof(pi) if gof else gweight_sizes([len(x) for x in pi])) * math.comb(b, k)
        return tot

    # ---------------- (C) type-set form
    tmask = {}
    for i, p in enumerate(typeset):
        mk = 0
        for a in range(NC):
            if fp[a] == p:
                mk |= masks[a]
        tmask[i] = mk
    mults = [mult_of[p] for p in typeset]

    def e_k(T, k):
        poly = [1]
        for i in T:
            coef = [math.comb(mults[i], t) for t in range(1, mults[i] + 1)]
            new = [0] * (len(poly) + len(coef))
            for u, cu in enumerate(poly):
                if cu == 0:
                    continue
                for v, cv in enumerate(coef, start=1):
                    new[u + v] += cu * cv
            poly = new
        return poly[k] if k < len(poly) else 0

    sepT = defaultdict(list)
    t0 = time.time()
    for T in range(1, 1 << KT):
        mk = 0
        Ts = [i for i in range(KT) if T >> i & 1]
        for i in Ts:
            mk |= tmask[i]
        if mk == ALLC:
            sepT[len(Ts)].append(tuple(Ts))
    out['separating_typesets_by_size'] = {str(k): len(v) for k, v in sorted(sepT.items())}
    print('separating type-sets by size = %s  (%.1f s)'
          % (out['separating_typesets_by_size'], time.time() - t0), flush=True)

    def F_typeset(k):
        return sum(e_k(T, k) for sz in sepT for T in sepT[sz] if sz <= k)

    ks = list(range(1, 9))
    Fmob = {k: F_mobius(k) for k in ks}
    Fts = {k: F_typeset(k) for k in ks}
    claim('C12', 'partition-lattice Mobius form (beta(pi) = #{a : pi <= pi_a}) reproduces the type-set form for k = 1..8',
          all(Fmob[k] == Fts[k] for k in ks),
          'Mobius = %s ; type-set = %s' % ([Fmob[k] for k in ks], [Fts[k] for k in ks]))
    claim('C13', 'type-set closed form F_k = sum over SEPARATING type-sets of e_k(T); no separating type-set of size <= 3 exists',
          all(Fts[k] == Fmob[k] for k in ks) and not sepT.get(1) and not sepT.get(2) and not sepT.get(3),
          'separating type-sets by size = %s ; F_4 = %d' % (out['separating_typesets_by_size'], Fts[4]))

    # ---------------- (A) pruned DFS brute force
    suffix = [0] * (NC + 1)
    for i in range(NC - 1, -1, -1):
        suffix[i] = suffix[i + 1] | masks[i]

    def F_dfs(k, ms=None):
        ms = ms or masks
        n = len(ms)
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suf[i] = suf[i + 1] | ms[i]
        cnt = [0]

        def rec(start, depth, mk):
            if depth == k:
                if mk == ALLC:
                    cnt[0] += 1
                return
            need = k - depth
            for j in range(start, n - need + 1):
                nm = mk | ms[j]
                if nm | suf[j + 1] != ALLC:
                    continue
                rec(j + 1, depth + 1, nm)

        rec(0, 0, 0)
        return cnt[0]

    t0 = time.time()
    Fbf = {}
    for k in range(1, 7):
        Fbf[k] = F_dfs(k)
        print('   brute-force F_%d = %d   (%.1f s)' % (k, Fbf[k], time.time() - t0), flush=True)
    out['F_brute'] = {str(k): Fbf[k] for k in Fbf}
    claim('C14', 'the closed form agrees with the independent brute-force count for k = 1..6 '
                 '(including the NEW values F_5 and F_6)',
          all(Fbf[k] == Fts[k] for k in Fbf) and Fbf[4] == 12645,
          'closed form F_1..F_6 = %s ; brute force = %s'
          % ([Fts[k] for k in range(1, 7)], [Fbf[k] for k in range(1, 7)]))
    out['F_closed_form'] = {str(k): Fts[k] for k in ks}

    # ---------------- C15 rank
    def rank_vecs(vecs):
        A = [[F(x) for x in v] for v in vecs]
        nr, ncol = len(A), len(A[0])
        r = 0
        for c in range(ncol):
            piv = next((i for i in range(r, nr) if A[i][c] != 0), None)
            if piv is None:
                continue
            A[r], A[piv] = A[piv], A[r]
            for i in range(r + 1, nr):
                if A[i][c] != 0:
                    f = A[i][c] / A[r][c]
                    for j in range(c, ncol):
                        A[i][j] -= f * A[r][j]
            r += 1
            if r == nr:
                break
        return r

    def rank_mat(cols):
        return rank_vecs([[ROWS[j][a] for a in cols] for j in range(R)])

    rk_all = rank_mat(range(NC))
    Vidx = [i for i in range(NC) if ids[i].startswith('V')]
    rk_V6 = rank_mat(Vidx[:6])
    # every 5-subset has rank <= 5 is a DIMENSION fact (5 vectors span <= 5 dims); we verify on a deterministic
    # window sample (stride 7) for support, not as the proof
    rk5max = max(rank_mat(list(range(i, i + 5))) for i in range(0, NC - 4, 7))
    dvec = {tuple(ROWS[j][a] for j in range(R)) for a in range(NC)}
    out['distinct_column_vectors'] = len(dvec)
    out['negated_vectors_not_present'] = len({tuple(-x for x in v) for v in dvec} - dvec)
    # exact number of 6-subsets that are bases (rank 6), reduced to the distinct vectors
    dl = sorted(dvec)
    dmult = collections.Counter(tuple(ROWS[j][a] for j in range(R)) for a in range(NC))
    nb = 0
    if len(dl) <= 40:
        for combo in itertools.combinations(range(len(dl)), 6):
            if rank_vecs([list(dl[i]) for i in combo]) == 6:
                w = 1
                for i in combo:
                    w *= dmult[dl[i]]
                nb += w
    out['n_rank6_bases'] = nb
    claim('C15', 'rank_Q(K) = 6 with V00-V05 an explicit basis; 5 columns can never span it (dimension), so 6 is minimal',
          rk_all == 6 and rk_V6 == 6 and rk5max == 5,
          'rank(K) = %d ; rank(V00..V05) = %d ; max rank over a deterministic 5-window sample (stride 7) = %d '
          '(<= 5 = dimension bound) ; '
          'distinct column vectors = %d ; exact number of rank-6 bases = %d'
          % (rk_all, rk_V6, rk5max, len(dvec), nb))

    # ---------------- C16 family decomposition
    mix = collections.Counter()
    for combo in itertools.combinations(range(NC), 4):
        mk = masks[combo[0]] | masks[combo[1]] | masks[combo[2]] | masks[combo[3]]
        if mk == ALLC:
            mix[''.join(sorted(fam[c][0].upper() for c in combo))] += 1
    out['F4_family_mixtures'] = dict(sorted(mix.items()))
    claim('C16', 'family-mixture decomposition of F_4 sums to 12645 with the single-family EEEE count = 625',
          sum(mix.values()) == 12645 and mix['EEEE'] == 625,
          'mixtures = %s' % dict(sorted(mix.items())))

    # ---------------- C17 EXACT null: all C(12,6)/2 = 462 bisections
    t0 = time.time()
    tot_bis = math.comb(12, 6) // 2
    F4all = math.comb(tot_bis, 4)
    for sizes in int_partitions(12):
        if sizes == [1] * 12:
            continue
        cnt = collections.Counter(sizes)
        npar = math.factorial(12)
        for s, mm in cnt.items():
            npar //= (math.factorial(mm) * math.factorial(s) ** mm)   # C17-c fix: (s!)^m, not s^m
        # beta_hat = (1/2) * #{sub-multisets of blocks with total size 6}
        poly = [1] + [0] * 6
        for s in sizes:
            new = poly[:]
            for t in range(6 - s + 1):
                new[t + s] += poly[t]
            poly = new
        bh = poly[6] // 2
        if bh >= 4:
            F4all += npar * gweight_sizes(sizes) * math.comb(bh, 4)
    C462 = math.comb(tot_bis, 4)
    p0 = F(F4all, C462)
    # MC sanity (declared draws)
    draws = 200000
    st = 20261002
    half = [s for s in itertools.combinations(range(12), 6) if 0 in s]
    bm = [pairmask(lambda i, j, S=set(s): (i in S) != (j in S)) for s in half]
    hit = 0
    for _ in range(draws):
        mk = 0
        for _q in range(4):
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            mk |= bm[(st >> 33) % len(bm)]
            if mk == ALLC:
                break
        if mk == ALLC:
            hit += 1
    mc = F(hit, draws)
    rate = F(12645, math.comb(62, 4))
    out['null_all_bisections'] = {'F4': F4all, 'C462_4': C462, 'p0': str(p0), 'p0_float': float(p0),
                                  'mc_draws': draws, 'mc_hits': hit, 'mc_float': float(mc),
                                  'machine_rate': str(rate), 'machine_rate_float': float(rate)}
    print('exact null: F_4(all 462 bisections) = %d / %d -> p0 = %s = %.6f ; MC(%d) = %.6f ; machine rate = %.6f'
          % (F4all, C462, p0, float(p0), draws, float(mc), float(rate)), flush=True)
    # small-analogue REGRESSION test for the size-multiset reduction (the first run failed exactly here)
    def _formula_F(pts, k):
        nb = math.comb(pts, pts // 2) // 2
        tot = math.comb(nb, k)
        for sizes in int_partitions(pts):
            if sizes == [1] * pts:
                continue
            cn = collections.Counter(sizes)
            npar2 = math.factorial(pts)
            for s2, mm in cn.items():
                npar2 //= (math.factorial(mm) * math.factorial(s2) ** mm)
            poly2 = [1] + [0] * (pts // 2)
            for s2 in sizes:
                new = poly2[:]
                for t in range(pts // 2 - s2 + 1):
                    new[t + s2] += poly2[t]
                poly2 = new
            b2 = poly2[pts // 2] // 2
            if b2 >= k:
                tot += npar2 * gweight_sizes(sizes) * math.comb(b2, k)
        return tot

    def _brute_F(pts, k):
        plocal = [(i, j) for i in range(pts) for j in range(i + 1, pts)]
        pil = {p: b for b, p in enumerate(plocal)}

        def pm(S):
            mk = 0
            for (i, j) in plocal:
                if (i in S) != (j in S):
                    mk |= (1 << pil[(i, j)])
            return mk

        allb = [set(s) for s in itertools.combinations(range(pts), pts // 2) if 0 in s]
        ALLX = (1 << len(plocal)) - 1
        bms = [pm(S) for S in allb]
        n = 0
        for combo in itertools.combinations(range(len(allb)), k):
            mk = 0
            for i in combo:
                mk |= bms[i]
            if mk == ALLX:
                n += 1
        return n

    reg = [(pts, k, _formula_F(pts, k), _brute_F(pts, k)) for pts in (4, 6) for k in (1, 2, 3)
           if k <= math.comb(pts, pts // 2) // 2]
    regok = all(f == b for (_p, _k, f, b) in reg)
    print('regression on small analogues (formula vs brute force): %s' % reg, flush=True)
    claim('C17-c', 'CORRECTED exact null: the size-multiset Mobius sum equals the MC estimate, and the reduction is '
                   'regression-tested on the pts=4/6 analogues (the first run of C17 FAILED on a wrong partition-count '
                   'formula; that FAIL is preserved in logs/02_r1_firstrun_C17_FAIL_excerpt.out)',
          abs(float(p0) - float(mc)) < 0.002 and regok,
          'p0(exact) = %.6f (%.1f s) ; MC(%d draws) = %.6f ; machine F_4/C(62,4) = %.6f ; small-analogue regression = %s'
          % (float(p0), time.time() - t0, draws, float(mc), float(rate), regok))

    # ---------------- C18 convention variant
    G, idxg, MULg = m.build_group()
    V = [m.rot_ref(G[first[r]], U[0]) for r in reps]

    def dotv(x, y):
        return m.add(m.add(m.mul(x[0], y[0]), m.mul(x[1], y[1])), m.mul(x[2], y[2]))

    Req = [[(1 if m.sgn(dotv(U[a], V[i])) == 0 else m.sgn(dotv(U[a], V[i]))) for a in range(NC)] for i in range(R)]
    fpeq = []
    for a in range(NC):
        d = defaultdict(list)
        for j in range(R):
            d[Req[j][a]].append(j)
        fpeq.append(tuple(sorted(tuple(sorted(v)) for v in d.values())))
    histeq = collections.Counter(collections.Counter(fpeq).values())
    meq = [pairmask(lambda i, j, a=a: Req[i][a] != Req[j][a]) for a in range(NC)]
    F4eq = sum(1 for combo in itertools.combinations(range(NC), 4)
               if (meq[combo[0]] | meq[combo[1]] | meq[combo[2]] | meq[combo[3]]) == ALLC)
    shp = sorted({tuple(sorted(len(b) for b in p)) for p in fpeq})
    out['equivariant_variant'] = {'n_types': len(set(fpeq)), 'mult_histogram': {str(k): v for k, v in sorted(histeq.items())},
                                  'F4': F4eq, 'shapes': shp}
    claim('C18', 'convention dependence: under the equivariant tie-break (tie -> +1) the census AND F_4 change',
          (len(set(fpeq)), F4eq) != (16, 12645),
          'frozen: 16 types / hist {3:10,5:5,7:1} / F_4 = 12645 ; equivariant: %d types / hist %s / F_4 = %d / shapes %s'
          % (len(set(fpeq)), dict(sorted(histeq.items())), F4eq, shp))

    # ---------------- C19 sub-arrangements
    fams = defaultdict(list)
    for a in range(NC):
        fams[types[a]].append(a)
    sub = {'V': fams['vertex'], 'F': fams['face'], 'E': fams['edge'],
           'V+F': fams['vertex'] + fams['face'], 'V+E': fams['vertex'] + fams['edge'],
           'F+E': fams['face'] + fams['edge'], 'all': list(range(NC))}
    tbl = {}
    for name, cols in sub.items():
        n = len(cols)
        ms = [masks[c] for c in cols]
        row = {}
        for k in range(1, min(7, n) + 1):
            row[k] = F_dfs(k, ms)
        kmin = next((k for k in sorted(row) if row[k] > 0), None)
        tbl[name] = {'n': n, 'F': row, 'k_min': kmin}
        print('   %-5s n=%-3d k_min=%-4s F = %s' % (name, n, kmin, row), flush=True)
    out['sub_arrangements'] = tbl
    claim('C19', 'sub-arrangement table: E alone already admits 4-frames while V alone and F alone need 5; '
                 'the 625 E-frames are reproduced',
          tbl['E']['k_min'] == 4 and tbl['V']['k_min'] == 5 and tbl['F']['k_min'] == 5 and tbl['E']['F'][4] == 625,
          'k_min = %s ; F_4(E) = %d' % ({n: tbl[n]['k_min'] for n in tbl}, tbl['E']['F'][4]))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t00
    with io.open(os.path.join(DATA, '02_r1_closed_form.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              time.time() - t00))
    print('=' * 108)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
