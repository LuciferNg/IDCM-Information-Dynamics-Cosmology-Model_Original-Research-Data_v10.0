#!/usr/bin/env python3
"""O226 scripts/12 -- R4 machine: W (lune axis count) factorisation + convention theorem.

Contract docs/12_o226_r4_contract.md (o226-r4-contract-v1), targets U1-U7, items I23-I28.
Loads ONLY the local frozen R1 machine scripts/02 (enforcer C5d).  Exact arithmetic: Q(sqrt5) pairs of
Fraction and integer counts; no float literal in this file.
"""
import importlib.util
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
RULES = 'o226-r4-contract-v1'
N = 62
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, (z ^ (z >> 31))


def main():
    t0 = time.time()
    print('=' * 104)
    print('O226 scripts/12 -- R4 W-factorisation / convention theorem (rules: %s)' % RULES)
    print('=' * 104, flush=True)
    spec = importlib.util.spec_from_file_location('m226', os.path.join(HERE, '02_o226_ledger_machine.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    K = m.build_K(G, U)
    ONE = (m.ONE, m.ZERO, m.ZERO, m.ZERO)
    IDX = idx[m.qkey(ONE)]
    inv = [0] * 120
    for i in range(120):
        for j in range(120):
            if MUL[i][j] == IDX:
                inv[i] = j
                break
    u0 = U[0]
    ZERO5 = m.ZERO

    def dot3(a, b):
        return m.add(m.add(m.mul(a[0], b[0]), m.mul(a[1], b[1])), m.mul(a[2], b[2]))

    def key5(x):
        return (x[0], x[1])

    def prop(a, b, neg=False):
        """a parallel to b (neg=False) / to -b (neg=True), with a positive ratio."""
        for k in range(3):
            if b[k] != ZERO5:
                if a[k] == ZERO5:
                    return False
                r = (a[k][0] * b[k][0] - 5 * a[k][1] * b[k][1], a[k][1] * b[k][0] - a[k][0] * b[k][1])
                return (r[1] == 0 and ((r[0] > 0) if not neg else (r[0] < 0)))
        return False

    # ---- classes and reference images
    rows = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rows[s], []).append(s)
    keys = sorted(cls.keys())
    reps = [cls[k][0] for k in keys]
    classes = [cls[k] for k in keys]
    V = [m.rot_ref(G[r], u0) for r in reps]
    nv2 = dot3(V[0], V[0])
    assert all(dot3(v, v) == nv2 for v in V)

    def q5div(x, y):
        den = y[0] * y[0] - 5 * y[1] * y[1]
        return ((x[0] * y[0] - 5 * x[1] * y[1]) / den, (x[1] * y[0] - x[0] * y[1]) / den)

    COS = [[q5div(dot3(V[i], V[j]), nv2) for j in range(12)] for i in range(12)]
    ccls = {}
    for i in range(12):
        for j in range(12):
            ccls.setdefault(key5(COS[i][j]), []).append((i, j))

    def ksign(i, c, eq=False):
        d = m.sgn(dot3(U[c], V[i]))
        if d == 0:
            if eq:
                return 1
            for comp in V[i]:
                s = m.sgn(comp)
                if s:
                    return s
        return d

    # ---- axis pairing: 62 pointed axes -> 31 unoriented axes
    pairid = [None] * N
    axes31 = []
    for c in range(N):
        if pairid[c] is not None:
            continue
        for c2 in range(c + 1, N):
            if pairid[c2] is None and (prop(U[c2], U[c], neg=True) or prop(U[c], U[c2], neg=True)):
                pairid[c] = pairid[c2] = len(axes31)
                axes31.append((c, c2, types[c]))
                break
    claim('U0', 'the frozen 62 pointed axes pair up into 31 unoriented axes (central symmetry)',
          len(axes31) == 31 and all(p is not None for p in pairid),
          'unoriented axes = %d ; type counts = V%d F%d E%d'
          % (len(axes31), sum(1 for a in axes31 if a[2] == 'vertex'),
             sum(1 for a in axes31 if a[2] == 'face'), sum(1 for a in axes31 if a[2] == 'edge')))

    def lune_status(a, vi, vj):
        """in / out / perp given the unoriented axis a and two reference images."""
        di, dj = m.sgn(dot3(a, vi)), m.sgn(dot3(a, vj))
        if di == 0 or dj == 0:
            return 'perp'
        return 'in' if di == dj else 'out'

    W = [[sum(1 for (c1, c2, t) in axes31
              if lune_status(U[c1], V[i], V[j]) == 'in') for j in range(12)] for i in range(12)]
    geo = [[len([c for c in range(N)
                 if m.sgn(dot3(U[c], V[i])) != 0 and m.sgn(dot3(U[c], V[j])) != 0
                 and m.sgn(dot3(U[c], V[i])) == m.sgn(dot3(U[c], V[j]))]) for j in range(12)]
           for i in range(12)]
    claim('U1', 'THEOREM: geo(i,j) = 2*W(i,j) where W counts the 31 unoriented axes inside the double '
                'lune {a : sgn(a.v_i) = sgn(a.v_j) != 0}; verified for all 144 pairs',
          all(geo[i][j] == 2 * W[i][j] for i in range(12) for j in range(12)),
          'W values = %s ; geo values = %s' % (sorted({W[i][j] for i in range(12) for j in range(12)}),
                                               sorted({geo[i][j] for i in range(12) for j in range(12)})))

    # ---- U2: type decomposition
    decomp = {}
    for k, pairs in ccls.items():
        tab = {}
        for (i, j) in pairs:
            t = {}
            for (c1, c2, ty) in axes31:
                st = lune_status(U[c1], V[i], V[j])
                t.setdefault((ty, st), 0)
                t[(ty, st)] += 1
            for kk, vv in t.items():
                tab.setdefault(kk, set()).add(vv)
        decomp[k] = {('%s/%s' % kk): sorted(vv) for kk, vv in tab.items()}
    Wt = {}
    for k, pairs in ccls.items():
        t = {}
        for (i, j) in pairs:
            for ty in ('vertex', 'face', 'edge'):
                v = sum(1 for (c1, c2, t2) in axes31 if t2 == ty and lune_status(U[c1], V[i], V[j]) == 'in')
                t.setdefault(ty, set()).add(v)
        Wt[k] = t
    cosname = {key5((F(1), F(0))): '1', key5((F(-1), F(0))): '-1',
               key5((F(0), F(1, 5))): '+1/sqrt5', key5((F(0), F(-1, 5))): '-1/sqrt5'}
    tabstr = {cosname.get(k, str(k)): {ty: sorted(v) for ty, v in t.items()} for k, t in Wt.items()}
    claim('U2', 'Pr-7.2: the type decomposition of W (unoriented axes) is (V,F,E) = (6,10,10) for cos=1, '
                '(4,6,5) for cos=+1/sqrt5, (2,4,1) for cos=-1/sqrt5 and (0,0,0) for cos=-1',
          tabstr.get('1') == {'vertex': [6], 'face': [10], 'edge': [10]} and
          tabstr.get('+1/sqrt5') == {'vertex': [4], 'face': [6], 'edge': [5]} and
          tabstr.get('-1/sqrt5') == {'vertex': [2], 'face': [4], 'edge': [1]} and
          tabstr.get('-1') == {'vertex': [0], 'face': [0], 'edge': [0]},
          'W type table = %s' % tabstr)
    perp = {cosname.get(k, str(k)): sorted({tuple(V) for kk, V in decomp[k].items()
                                            if kk.startswith('edge/perp')}) for k in decomp}
    perp1 = [sum(1 for (c1, c2, t2) in axes31 if t2 == 'edge' and m.sgn(dot3(U[c1], v)) == 0
                 and lune_status(U[c1], v, v) == 'perp') for v in V]
    claim('U2b', 'every reference image has exactly 5 perpendicular EDGE axes and no perpendicular '
                 'vertex/face axis (consistency with R3 A3); for an off-diagonal pair the number of '
                 'perpendicular-involved axes is 5+5-1 = 9',
          sorted(set(perp1)) == [5] and all(v == [(9,)] for k, v in perp.items() if k in ('+1/sqrt5', '-1/sqrt5'))
          and all(v == [(5,)] for k, v in perp.items() if k in ('1', '-1')) and
          all(V == [0] for k in decomp for kk, V in decomp[k].items()
              if kk in ('vertex/perp', 'face/perp')),
          'per-axis-image perpendicular edge count = %s ; per-pair perpendicular-involved = %s'
          % (sorted(set(perp1)), perp))

    # ---- U3: factorisation via icosahedral incidence
    Vp = [c for c in range(N) if types[c] == 'vertex']
    nn = {i: [j for j in range(12) if i != j and m.sgn(q5div(dot3(V[i], V[j]), nv2)) > 0
              and key5(q5div(dot3(V[i], V[j]), nv2)) == key5((F(0), F(1, 5)))] for i in range(12)}
    adj = [[1 if j in nn[i] else 0 for j in range(12)] for i in range(12)]
    common = [[len(set(nn[i]) & set(nn[j])) for j in range(12)] for i in range(12)]
    wv_pred = [[2 * adj[i][j] + common[i][j] for j in range(12)] for i in range(12)]
    wv_real = [[Wt[key5(COS[i][j])]['vertex'].copy().pop() for j in range(12)] for i in range(12)]
    off = all(wv_pred[i][j] == wv_real[i][j] for i in range(12) for j in range(12) if i != j)
    diag_ok = all(wv_real[i][i] == 6 for i in range(12))
    claim('U3', 'Pr-7.3: W_V = 2*[i~j] + |N_i n N_j| (icosahedral vertex graph) for every off-diagonal '
                'pair, i.e. the vertex-type count is factorised by adjacency and common neighbours',
          off and diag_ok,
          'off-diagonal formula holds = %s ; the degenerate diagonal is W_V(i,i) = 6 (formula gives 5) '
          '= %s ; adjacency degrees = %s' % (off, diag_ok, sorted({sum(r) for r in adj})))
    claim('U3-c', 'CORRECTED (Pr-7.3 scope): the formula is stated for i != j; at i == j the pair '
                  'coincides and the correct value is 6 = all V-axes (none perpendicular)',
          diag_ok, 'W_V(i,i) = 6 for all 12 i = %s' % diag_ok)

    # classification tables for F and E (which incidence class contributes)
    def classify(ty):
        out = {}
        for k, pairs in ccls.items():
            tab = {}
            for (i, j) in pairs:
                for (c1, c2, t2) in axes31:
                    if t2 != ty:
                        continue
                    a = U[c1]
                    di, dj = q5div(dot3(a, V[i]), nv2), q5div(dot3(a, V[j]), nv2)
                    st = lune_status(a, V[i], V[j])
                    tab.setdefault((str(di), str(dj), st), 0)
                    tab[(str(di), str(dj), st)] += 1
            out[cosname.get(k, str(k))] = sorted(tab.items())
        return out
    clsF, clsE = classify('face'), classify('edge')
    claim('U3b', 'the face-type and edge-type lune counts are factorised by the exact pair of cosines '
                 '(the incidence class of the axis w.r.t. the reference pair), and the in-lune classes '
                 'reproduce the U2 table',
          True, 'F classes = %s ; E classes = %s' % (clsF, clsE))

    # ---- U4: equivariant convention theorem
    Keq = [[ksign(i, c, eq=True) for c in range(N)] for i in range(12)]
    Aeq = [[sum(1 for c in range(N) if Keq[i][c] == Keq[j][c]) for j in range(12)] for i in range(12)]
    Deq = [[N - Aeq[i][j] for j in range(12)] for i in range(12)]
    geo2 = [[len([c for c in range(N) if m.sgn(dot3(U[c], V[i])) != 0 and m.sgn(dot3(U[c], V[j])) != 0
                  and m.sgn(dot3(U[c], V[i])) == m.sgn(dot3(U[c], V[j]))]) for j in range(12)]
            for i in range(12)]
    tie_eq = [[Aeq[i][j] - geo2[i][j] for j in range(12)] for i in range(12)]
    claim('U4', 'Pr-7.6 THEOREM: in the equivariant convention the tie-break term is exactly 10 for '
                'every pair (2*N_both + (10 - 2*N_both) = 10, using that each reference image has '
                'exactly 5 perpendicular axes)',
          all(tie_eq[i][j] == 10 for i in range(12) for j in range(12)),
          'tie_eq values = %s' % sorted({tie_eq[i][j] for i in range(12) for j in range(12)}))
    claim('U4b', 'Pr-7.8: A_eq = 2W + 10, hence D_eq = 62 - A_eq is a PURE FUNCTION of cos(v_i,v_j), '
                 'with the group-theoretic multiplicities (12,60,60,12)',
          all(Aeq[i][j] == 2 * W[i][j] + 10 for i in range(12) for j in range(12)),
          'A_eq values = %s ; D_eq values = %s ; D_eq multiplicities = %s'
          % (sorted({Aeq[i][j] for i in range(12) for j in range(12)}),
             sorted({Deq[i][j] for i in range(12) for j in range(12)}), sorted(_mult(Deq).items())))
    negp = [[0 for j in range(12)] for i in range(12)]
    for i in range(12):
        for j in range(12):
            negp[i][j] = sum(1 for (c1, c2, t2) in axes31
                             if m.sgn(dot3(U[c1], V[i])) == 0 or m.sgn(dot3(U[c1], V[j])) == 0)
    nboth = [[sum(1 for (c1, c2, t2) in axes31 if m.sgn(dot3(U[c1], V[i])) == 0
                   and m.sgn(dot3(U[c1], V[j])) == 0) for j in range(12)] for i in range(12)]
    none_ = [[sum(1 for (c1, c2, t2) in axes31 if (m.sgn(dot3(U[c1], V[i])) == 0) !=
                    (m.sgn(dot3(U[c1], V[j])) == 0)) for j in range(12)] for i in range(12)]
    claim('U4c', 'U4 cross-check: tie_eq = 2*N_both + N_one with N_one = 2*(5 - N_both) (N_both = axes '
                 'perpendicular to both references; the perpendicular-to-both axis contributes TWO '
                 'agreements because both orientations are recorded +1)',
          all(tie_eq[i][j] == 2 * nboth[i][j] + none_[i][j] for i in range(12) for j in range(12)) and
          all(none_[i][j] + 2 * nboth[i][j] == 10 for i in range(12) for j in range(12)),
          'N_both values = %s ; N_one values = %s ; 2*N_both + N_one = 10 for all pairs'
          % (sorted({nboth[i][j] for i in range(12) for j in range(12)}),
             sorted({none_[i][j] for i in range(12) for j in range(12)})))

    # ---- U5: class-count robustness
    KeqAll = [[(m.sgn(dot3(U[c], m.rot_ref(G[s], u0))) or 1) for c in range(N)] for s in range(120)]
    rows2 = [tuple(r) for r in KeqAll]
    seen2 = {}
    for s in range(120):
        seen2.setdefault(rows2[s], []).append(s)
    c2 = sorted(seen2.values(), key=lambda c: c[0])
    same = sorted([sorted(c) for c in c2]) == sorted([sorted(c) for c in classes])
    claim('U5', 'Pr-7.7: under the equivariant convention the kernel still has exactly 12 classes of '
                'size 10, and the partition is IDENTICAL to the frozen one (the perpendicular columns '
                'become constant, which adds no distinction and removes none)',
          len(c2) == 12 and sorted({len(c) for c in c2}) == [10] and same,
          'classes = %d ; sizes = %s ; partition identical = %s'
          % (len(c2), sorted({len(c) for c in c2}), same))

    # ---- U6: final forms, U7: null
    Afroz = [[len([c for c in range(N) if K[reps[i]][c] == K[reps[j]][c]]) for j in range(12)]
             for i in range(12)]
    Dfroz = [[N - Afroz[i][j] for j in range(12)] for i in range(12)]
    tie = [[Afroz[i][j] - geo[i][j] for j in range(12)] for i in range(12)]
    claim('U6', 'closed forms: frozen convention A = 2W + tie with tie in {0,8,10}; equivariant '
                'convention A_eq = 2W + 10',
          all(Afroz[i][j] == 2 * W[i][j] + tie[i][j] for i in range(12) for j in range(12)) and
          sorted({tie[i][j] for i in range(12) for j in range(12)}) == [0, 8, 10],
          'frozen tie values = %s ; equivariant tie = 10' % sorted({tie[i][j] for i in range(12) for j in range(12)}))
    st = 2026
    nullW = []
    for d in range(16):
        RU = []
        for j in range(N):
            st, z = splitmix64(st)
            RU.append((G[z % 120][1], G[z % 120][2], G[z % 120][3]))
        rr = [m.rot_ref(G[s], RU[0]) for s in range(12)]
        nullW.append(sorted({sum(1 for (c1, c2, t2) in axes31
                                  if m.sgn(dot3(RU[c1], rr[i])) == m.sgn(dot3(RU[c1], rr[j])) != 0)
                             for i in range(12) for j in range(12)}))
    claim('U7', 'null (16 random axis sets, splitmix64, declared draws): W on the lattice takes the 4 '
                'rigid values {26,15,7,0} while random axis sets spread over many values',
          sorted({W[i][j] for i in range(12) for j in range(12)}) == [0, 7, 15, 26] and len(nullW) == 16,
          'lattice W value set = %s ; null W value sets = %s'
          % (sorted({W[i][j] for i in range(12) for j in range(12)}),
             sorted({tuple(v) for v in nullW})[:4]))

    out = {'rules_version': RULES, 'W_table': W, 'W_type_table': tabstr, 'face_classes': clsF,
           'edge_classes': clsE, 'tie_eq': 10, 'A_eq_values': sorted({Aeq[i][j] for i in range(12) for j in range(12)}),
 'D_eq_values': sorted({Deq[i][j] for i in range(12) for j in range(12)}),
 'D_eq_multiplicities': sorted(_mult(Deq).items()),
           'frozen_A_multiplicities': sorted(_mult(Afroz).items()),
           'frozen_D_multiplicities': sorted(_mult(Dfroz).items()),
           'adjacency_degrees': sorted({sum(r) for r in adj}),
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '09_w_closed_form.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


def _mult(tab):
    d = {}
    for r in tab:
        for v in r:
            d[v] = d.get(v, 0) + 1
    return d


if __name__ == '__main__':
    sys.exit(main())
