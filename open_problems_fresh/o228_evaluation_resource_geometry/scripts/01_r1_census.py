#!/usr/bin/env python3
"""O228 scripts/01 -- R1 resource-geometry census (contract docs/00_r1_contract.md).

Frozen input: K := o222/scripts/12_b5_budget.py::load_machine()   (read-only; sha pinned in the contract)
Claims C1-C11 (pre-registered BEFORE this script ran; register O228/R1 notes).
Outputs: data/01_r1_census.json ; stdout log.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/01_r1_census.py
"""
import importlib.util
import io
import json
import os
import sys
import collections

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


# ---------------------------------------------------------------- frozen machine
sp = importlib.util.spec_from_file_location('mX', os.path.join(O222, 'scripts', '12_b5_budget.py'))
mX = importlib.util.module_from_spec(sp)
sp.loader.exec_module(mX)
m, K, MUL, hx, ids, types = mX.load_machine()
axes, U, _ids, _types, _hv = m.load_inputs()
NR, NC = len(K), len(K[0])
G, idx, MULg = m.build_group()


def main():
    out = {}
    print('=' * 108)
    print('O228 scripts/01 -- R1 resource-geometry census   (rules o228-r1-resource-geometry-v1)')
    print('=' * 108, flush=True)

    # ---------------- C1
    valset = sorted({v for r in K for v in r})
    claim('C1', 'K is 120 x 62 with value set {-1,+1}',
          (NR, NC) == (120, 62) and valset == [-1, 1], 'shape = %dx%d ; values = %s' % (NR, NC, valset))
    out['n_rows'], out['n_cols'] = NR, NC

    # ---------------- C2  distinct rows
    rows = [tuple(K[i][a] for a in range(NC)) for i in range(NR)]
    first = {}
    for i, r in enumerate(rows):
        first.setdefault(r, i)
    reps = sorted(first, key=lambda r: first[r])
    mult = collections.Counter(rows)
    claim('C2', 'distinct rows = 12 and every multiplicity = 10',
          len(reps) == 12 and set(mult.values()) == {10},
          'distinct = %d ; multiplicities = %s' % (len(reps), sorted(mult.values())))
    out['n_distinct_rows'] = len(reps)
    R = 12
    # row directions (vertices of the icosahedron), exact in Q(sqrt5)^3
    V = [m.rot_ref(G[first[r]], U[0]) for r in reps]
    D = m.add(m.add(m.mul(V[0][0], V[0][0]), m.mul(V[0][1], V[0][1])), m.mul(V[0][2], V[0][2]))
    assert all(m.add(m.add(m.mul(v[0], v[0]), m.mul(v[1], v[1])), m.mul(v[2], v[2])) == D for v in V)


    def dot(x, y):
        return m.add(m.add(m.mul(x[0], y[0]), m.mul(x[1], y[1])), m.mul(x[2], y[2]))


    # icosahedron graph on the 12 vertices: adjacent <=> cos = +1/sqrt5 (exact)
    adj = [set() for _ in range(R)]
    for i in range(R):
        for j in range(R):
            if i == j:
                continue
            d = dot(V[i], V[j])
            if m.sgn(d) > 0:
                t = m.sub(m.mul(m.mul(d, d), (5, 0)), m.mul(D, D))   # 5 d^2 - D^2
                if m.is_zero(t):
                    adj[i].add(j)
    deg = sorted({len(a) for a in adj})
    claim('C2b', 'the 12 row directions are the icosahedron vertices (exact): every degree = 5',
          deg == [5], 'degrees = %s ; edge count = %d' % (deg, sum(len(a) for a in adj) // 2))
    out['icosahedron_degrees'] = deg
    closed = [frozenset([i]) | adj[i] for i in range(R)]

    # ---------------- C3  known upstream values
    ALLP = frozenset((i, j) for i in range(R) for j in range(i + 1, R))
    assert len(ALLP) == 66


    def fibre(col):
        d = collections.defaultdict(list)
        for j, r in enumerate(reps):
            d[r[col]].append(j)
        return tuple(sorted(tuple(sorted(v)) for v in d.values()))


    fp = [fibre(a) for a in range(NC)]
    cover = {a: frozenset(p for p in ALLP if reps[p[0]][a] != reps[p[1]][a]) for a in range(NC)}
    import itertools

    def brute(k, cols):
        cols = list(cols)
        n = 0
        for combo in itertools.combinations(cols, k):
            s = 0
            for c in combo:
                s |= cover_mask[c]
            if s == ALLMASK:
                n += 1
        return n


    cover_mask = {}
    for a in range(NC):
        mk = 0
        for bi, p in enumerate(sorted(ALLP)):
            if p in cover[a]:
                mk |= (1 << bi)
        cover_mask[a] = mk
    ALLMASK = (1 << 66) - 1
    F = {}
    for k in range(1, 5):
        F[k] = brute(k, range(NC))
    import math
    C624 = math.comb(62, 4)
    claim('C3', 'F_1 = F_2 = F_3 = 0, F_4 = 12645, C(62,4) = 557845 (upstream values reproduced)',
          F[1] == 0 and F[2] == 0 and F[3] == 0 and F[4] == 12645 and C624 == 557845,
          'F_1..F_4 = %s ; C(62,4) = %d ; rate = %s' %
          ([F[k] for k in (1, 2, 3, 4)], C624, '%s/%s' % (F[4], C624)))
    out['F_known'] = {str(k): F[k] for k in F}
    out['C62_4'] = C624

    # ---------------- C4  lines
    negmap = {}
    for a in range(NC):
        key = tuple(((-c[0]), (-c[1])) for c in U[a])
        for b in range(NC):
            if tuple(U[b]) == key:
                negmap[a] = b
    lines = sorted({tuple(sorted((a, negmap[a]))) for a in negmap if a in negmap})
    ltypes = collections.Counter(types[l[0]] for l in lines)
    claim('C4', 'the 62 columns form 31 unoriented axes (6 vertex / 10 face / 15 edge), each column having its negative in the set',
          len(lines) == 31 and ltypes == collections.Counter({'vertex': 6, 'face': 10, 'edge': 15}) and len(negmap) == 62,
          'lines = %d ; families = %s ; columns with a negative partner = %d' % (len(lines), dict(ltypes), len(negmap)))
    out['n_lines'] = len(lines)
    out['line_families'] = dict(ltypes)

    # ---------------- C5 / C6  fibre partitions
    shape = sorted({tuple(sorted(len(b) for b in p)) for p in fp})
    groups = collections.defaultdict(list)
    for a in range(NC):
        groups[fp[a]].append(a)
    hist = collections.Counter(len(v) for v in groups.values())
    claim('C5', 'every column fibre partition is a bisection (6,6); distinct partitions = 16',
          shape == [(6, 6)] and len(groups) == 16,
          'shapes = %s ; distinct = %d' % (shape, len(groups)))
    claim('C6', 'multiplicity histogram = {3:10, 5:5, 7:1} (sum = 62)',
          hist == collections.Counter({3: 10, 5: 5, 7: 1}),
          'histogram = %s ; sum = %d' % (dict(sorted(hist.items())), sum(k * v for k, v in hist.items())))
    out['n_types'] = len(groups)
    out['mult_histogram'] = {str(k): v for k, v in sorted(hist.items())}

    # ---------------- C7  split-line theorem
    split, unsplit = [], []
    for (a, b) in lines:
        (split if fp[a] != fp[b] else unsplit).append((a, b))
    split_fams = sorted({types[a] for (a, b) in split})
    unsplit_fams = collections.Counter(types[a] for (a, b) in unsplit)
    claim('C7', 'split lines (the two columns of a line give DIFFERENT fibre partitions) <=> edge lines; '
                'the 16 non-split lines are the 6 vertex + 10 face ones',
          len(split) == 15 and split_fams == ['edge'] and unsplit_fams == collections.Counter({'vertex': 6, 'face': 10}),
          'split = %d (%s) ; non-split = %d (%s)' % (len(split), split_fams, len(unsplit), dict(unsplit_fams)))
    out['split_lines'] = len(split)
    out['unsplit_families'] = dict(unsplit_fams)

    # ---------------- C8  zeros
    def zeros(col):
        return [i for i in range(R) if m.is_zero(dot(U[col], V[i]))]


    zstat = collections.Counter()
    ztot = 0
    for a in range(NC):
        z = zeros(a)
        ztot += len(z)
        zstat[(types[a], len(z))] += 1
    claim('C8', 'zero law: every edge column is perpendicular to exactly 4 rows, vertex/face columns to none; '
                'total zeros = 120 = 12 x 10',
          dict(zstat) == {('edge', 4): 30, ('face', 0): 20, ('vertex', 0): 12} and ztot == 120,
          'zeros by (family,#rows) = %s ; total = %d' % (dict(sorted(zstat.items())), ztot))
    out['zero_stats'] = {('%s,%d' % k): v for k, v in sorted(zstat.items())}

    # ---------------- C9  bijection 16 bisections <-> 16 non-edge lines
    lid = {}
    for li, (a, b) in enumerate(lines):
        lid[a] = li
        lid[b] = li
    nonedge_line_side = {}
    for (a, b) in unsplit:
        nonedge_line_side[lid[a]] = frozenset(tuple(sorted(s)) for s in fp[a])
    bij = len({s for s in nonedge_line_side.values()}) == 16
    sameFamOK = True
    for (a, b) in unsplit:
        if fp[a] != fp[b]:
            sameFamOK = False
    claim('C9', 'bijection: the 16 distinct bisections <-> the 16 non-edge lines; each vertex line and each face line '
                'contributes its two columns to the SAME bisection',
          bij and sameFamOK and len(nonedge_line_side) == 16,
          'non-edge lines = %d ; distinct bisections from them = %d ; +-coherence = %s'
          % (len(nonedge_line_side), len({s for s in nonedge_line_side.values()}), sameFamOK))

    # type keyed by family composition
    typefam = {}
    for p, cols in groups.items():
        typefam[p] = frozenset(types[c] for c in cols)
    vtypes = [p for p in groups if typefam[p] == frozenset({'vertex', 'edge'})]
    ftypes = [p for p in groups if typefam[p] == frozenset({'face', 'edge'})]
    # ---------------- C10  edge column allocation
    alloc = collections.Counter()
    for p in vtypes:
        alloc['V-type edge columns'] += sum(1 for c in groups[p] if types[c] == 'edge')
    for p in ftypes:
        alloc['F-type edge columns'] += sum(1 for c in groups[p] if types[c] == 'edge')
    vcounts = sorted(sum(1 for c in groups[p] if types[c] == 'edge') for p in vtypes)
    fcounts = sorted(sum(1 for c in groups[p] if types[c] == 'edge') for p in ftypes)
    claim('C10', 'edge columns allocate 20 to the V-type bisections (5 + 3+3+3+3+3) and 10 to the F-type ones (1 each)',
          alloc['V-type edge columns'] == 20 and alloc['F-type edge columns'] == 10 and vcounts == [3, 3, 3, 3, 3, 5]
          and fcounts == [1] * 10,
          'V-type edge counts = %s ; F-type edge counts = %s' % (vcounts, fcounts))
    out['edge_allocation'] = {'V-type': vcounts, 'F-type': fcounts}

    # ---------------- C11  V-type bisections = closed neighbourhoods
    def setof(p):
        return [set(b) for b in p]


    ok11 = 0
    for p in vtypes:
        sides = setof(p)
        if any(frozenset(s) == closed[i] or frozenset(s) == frozenset(set(range(R)) - closed[i])
               for s in sides for i in range(R)):
            ok11 += 1
    claim('C11', 'the 6 V-type bisections are the closed neighbourhoods N[v] of the icosahedron graph (with their complements)',
          ok11 == 6, 'V-type bisections matching a closed neighbourhood (or its complement): %d/6' % ok11)
    out['Vtype_closed_nbhd'] = ok11

    # informational: F-type side structure -- how many graph triangles (= faces) does each side contain?
    def triangles_in(s):
        return [frozenset(t) for t in itertools.combinations(sorted(s), 3)
                if all(b in adj[a] for a, b in itertools.combinations(t, 2))]

    tri_counts = []
    for p in ftypes:
        sides = setof(p)
        tri_counts.append(sorted(len(triangles_in(s)) for s in sides))
    out['Ftype_triangle_counts_per_side'] = tri_counts
    out['Ftype_all_have_one_triangle_each'] = all(t == [1, 1] for t in tri_counts)

    # ---------------- other outputs
    out['types'] = {'count': len(groups),
                    'multiset': sorted((len(v), [ids[c] for c in v]) for v in groups.values()),
                    'blocks': [[list(b) for b in p] for p in sorted(groups)]}
    out['row_reps_order'] = 'first-occurrence order of distinct K rows (index i in K)'
    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '01_r1_census.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 108)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 108)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
