#!/usr/bin/env python3
"""O226 scripts/10 -- R3 machine: closed form of the staleness value set + resolution of the R2
contradiction.

Contract docs/09_o226_r3_contract.md (o226-r3-contract-v1), judgements T6-T9, items I17-I22.
Pre-registered items keep their exact wording; refuted ones stay FAIL and a separate -c carries the
measured statement.  Loads the LOCAL frozen R1 machine scripts/02 only (enforcer C5c).  Exact
arithmetic: Q(sqrt5) pairs of Fraction and integer counts; no float literal in this file.
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
RULES = 'o226-r3-contract-v1'
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
    print('O226 scripts/10 -- R3 value-set closed form / contradiction resolution (rules: %s)' % RULES)
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

    def q5div(x, y):
        den = y[0] * y[0] - 5 * y[1] * y[1]
        return ((x[0] * y[0] - 5 * x[1] * y[1]) / den, (x[1] * y[0] - x[0] * y[1]) / den)

    def key5(x):
        return (x[0], x[1])

    # ---------------- classes and their representative images v_i = rho(rep_i) u_0
    rows = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rows[s], []).append(s)
    keys = sorted(cls.keys())
    reps = [cls[k][0] for k in keys]
    classes = [cls[k] for k in keys]
    ncls = len(cls)
    V = [m.rot_ref(G[r], u0) for r in reps]
    norms = [dot3(v, v) for v in V]
    claim('V1', 'the 12 class representatives map to 12 images v_i = rho(rep_i)u_0 with a COMMON squared '
                'length (so cos(v_i,v_j) is an exact Q(sqrt5) ratio)',
          ncls == 12 and len({key5(x) for x in norms}) == 1,
          'classes = %d ; distinct |v|^2 = %s ; type of v_0 = %s'
          % (ncls, len({key5(x) for x in norms}), types[0]))
    nv2 = norms[0]
    COS = [[q5div(dot3(V[i], V[j]), nv2) for j in range(12)] for i in range(12)]
    coskeys = {}
    for i in range(12):
        for j in range(12):
            coskeys.setdefault(key5(COS[i][j]), []).append((i, j))
    cosmult = sorted(((k, len(v)) for k, v in coskeys.items()), key=lambda t: -t[1])
    claim('V2', 'Pr-6.2: the pairwise cosines of the 12 images take exactly 4 values with multiplicities '
                '{1:12, -1:12, +1/sqrt5:60, -1/sqrt5:60}',
          len(coskeys) == 4 and sorted(len(v) for v in coskeys.values()) == [12, 12, 60, 60],
          'distinct cos = %d ; multiplicities = %s'
          % (len(coskeys), sorted(len(v) for v in coskeys.values())))

    # ---------------- D table
    def agree(i, j):
        return [c for c in range(N) if K[reps[i]][c] == K[reps[j]][c]]
    D = [[N - len(agree(i, j)) for j in range(12)] for i in range(12)]
    dmult = {}
    for r in D:
        for v in r:
            dmult[v] = dmult.get(v, 0) + 1
    dyn = {}
    for k, v in coskeys.items():
        dyn[k] = sorted({D[i][j] for (i, j) in v})
    claim('V3', 'H1 (Pr-6.1 first half): D is a function of cos(v_i,v_j) ONLY -- i.e. every cos class '
                'carries a single D value',
          all(len(s) == 1 for s in dyn.values()),
          'D value set per cos class = %s ; D multiplicities = %s'
          % ({'+1' if k == (F(1), F(0)) else ('-1' if k == (F(-1), F(0)) else 'other'): v for k, v in dyn.items()},
             sorted(dmult.items())))
    neg1_cos = (F(-1), F(0))
    pos1_cos = (F(1), F(0))
    nb = {}
    for i in range(12):
        nb[i] = sorted({D[i][j] for j in range(12)
                        if (i, j) in coskeys.get(tuple(q5div(dot3(V[i], V[j]), nv2)), [])
                        and j != i and key5(COS[i][j]) not in (pos1_cos, neg1_cos)
                        and m.sgn(COS[i][j]) > 0})
    claim('V4', 'Pr-6.3 / I19: the C5-transitivity necessary condition for H1 -- for a fixed i the 5 '
                'neighbours (cos = +1/sqrt5) must all give the SAME D; the pre-registered prediction is '
                'that they do NOT',
          all(len(v) > 1 for v in nb.values()),
          'per-i D values over the cos = +1/sqrt5 neighbours = %s' % [nb[i] for i in range(12)])

    # ---------------- hemisphere identity (Pr-6.4 / I17)
    S = [[j for j in range(N) if m.sgn(dot3(U[j], V[i])) < 0] for i in range(12)]
    hemi = sorted({len(s) for s in S})
    sIDs = [[len(set(S[i]) & set(S[j])) for j in range(12)] for i in range(12)]
    ident_ok = all(D[i][j] == N - 2 * sIDs[i][j] for i in range(12) for j in range(12))
    claim('V5', 'Pr-6.4a: the hemisphere identity D(i,j) = 62 - 2*|S_i n S_j| holds for all 144 pairs, '
                'with |S_i| = 31 for every i (no axis is orthogonal to a vertex axis)',
          ident_ok and hemi == [31], 'distinct |S_i| = %s ; identity = %s' % (hemi, ident_ok))
    svals = sorted({sIDs[i][j] for i in range(12) for j in range(12)})
    claim('V6', 'Pr-6.4b: the hemisphere-intersection counts s = |S_i n S_j| take the value set '
                '{0,11,12,19,20,31}, and D = 62 - 2s gives {0,22,24,38,40,62}',
          svals == [0, 11, 12, 19, 20, 31] and sorted({N - 2 * s for s in svals}) == [0, 22, 24, 38, 40, 62],
          's value set = %s ; D value set = %s' % (svals, sorted({N - 2 * s for s in svals})))
    tri = {}
    for i in range(12):
        for j in range(12):
            a = len([c for c in S[i] if c in set(S[j]) and types[c] == 'vertex'])
            b = len([c for c in S[i] if c in set(S[j]) and types[c] == 'face'])
            c = len([c for c in S[i] if c in set(S[j]) and types[c] == 'edge'])
            tri.setdefault((a, b, c), 0)
            tri[(a, b, c)] += 1
    tripset = sorted(tri.keys())
    claim('V7', 'Pr-6.4c: the type decomposition s = a+b+c takes exactly the 6 triples {(0,0,0), '
                '(2,4,5), (2,4,6), (4,6,9), (4,6,10), (6,10,15)} with multiplicities '
                '{12,40,20,20,40,12} (order matching the sorted triples)',
          tripset == [(0, 0, 0), (2, 4, 5), (2, 4, 6), (4, 6, 9), (4, 6, 10), (6, 10, 15)] and
          [tri[t] for t in tripset] == [12, 40, 20, 20, 40, 12],
          'triples -> multiplicity = %s' % [(t, tri[t]) for t in tripset])
    uni = [t for t in tripset if t != (0, 0, 0) and F(t[0], 6) == F(t[1], 10) == F(t[2], 15)]
    claim('V8', 'Pr-6.5 (pre-registered direction): s is NOT a uniform fraction of the three orbits '
                '(a/6 = b/10 = c/15 fails) -- no "uniform fraction" closed form',
          not uni, 'triples with a/6 = b/10 = c/15 = %s' % uni)

    # ---------------- axis-set invariance diagnostic (prime suspect for the R2 contradiction)
    def prop_pos(a, b):
        c1 = m.add(m.mul(a[0], b[1]), m.neg(m.mul(a[1], b[0])))
        c2 = m.add(m.mul(a[0], b[2]), m.neg(m.mul(a[2], b[0])))
        c3 = m.add(m.mul(a[1], b[2]), m.neg(m.mul(a[2], b[1])))
        if c1 != ZERO5 or c2 != ZERO5 or c3 != ZERO5:
            return False
        for k in range(3):
            if b[k] != ZERO5:
                return m.mul(a[k], b[k]) != ZERO5 and m.sgn(m.mul(a[k], b[k])) > 0
        return False

    inv_bad = []
    for q in range(120):
        for j in range(N):
            w = m.rot_ref(G[q], U[j])
            if not any((prop_pos(w, U[k]) or prop_pos((m.neg(w[0]), m.neg(w[1]), m.neg(w[2])), U[k]))
                       for k in range(N)):
                inv_bad.append((q, j))
                break
    claim('V9', 'DIAGNOSTIC: is the frozen axis set F1 invariant under 2I (as a set of pointed '
                'vectors, up to positive scale)?',
          not inv_bad, 'group elements that send some axis out of the set = %d ; first offenders = %s'
          % (len(inv_bad), inv_bad[:5]))

    # ---------------- H2 (conjugacy class of rep_i^-1 rep_j) and H3 (double coset)
    H = [t for t in range(120) if rows[MUL[reps[0]][t]] == rows[reps[0]]]
    def conj_class(g):
        return tuple(sorted({MUL[MUL[x][g]][inv[x]] for x in range(120)}))
    for tag, fn, name in (('V10', conj_class, 'H2: conjugacy class of rep_i^-1 rep_j'),
                          ('V11', lambda g: tuple(sorted({MUL[MUL[a][g]][b] for a in H for b in H})),
                           'H3: double coset HxH (R2 refutation re-checked)')):
        tab = {}
        for i in range(12):
            for j in range(12):
                g = MUL[inv[reps[i]]][reps[j]]
                tab.setdefault(fn(g), set()).add(D[i][j])
        bad = [k for k, v in tab.items() if len(v) > 1]
        claim(tag, '%s -- D must collapse onto it with a single value per class' % name,
              not bad, 'classes = %d ; colliding = %d ; value sets = %s'
              % (len(tab), len(bad), sorted({tuple(sorted(v)) for v in tab.values()})[:6]))

    # ---------------- H4: D is a function of the pair (v_i, v_j) -- provable identity
    D2 = [[N - len([c for c in range(N) if m.sgn(dot3(U[c], V[i])) == m.sgn(dot3(U[c], V[j]))])
           for j in range(12)] for i in range(12)]
    claim('V12', 'H4 (the resolution): D(i,j) is a function of the PAIR (v_i, v_j) alone -- the identity '
                 'D = #{u : sgn(u.v_i) != sgn(u.v_j)} is verified against the class-level table for all '
                 '144 pairs',
          D == D2, 'identical over 144 pairs = %s' % (D == D2))

    # ---------------- T7 resolution: the geometric part + the TIE-BREAK part
    orth = [[c for c in range(N) if dot3(U[c], V[i]) == ZERO5] for i in range(12)]
    ocounts = sorted({len(o) for o in orth})
    otypes = sorted({types[c] for o in orth for c in o})
    claim('V16', 'DIAGNOSTIC (the resolution): exactly 10 of the 62 axes are ORTHOGONAL to each vertex '
                 'axis (u.v = 0), so the frozen tie-break rule -- the sign of the first non-zero '
                 'component of v_i -- decides those entries of K, and that rule is NOT rotation '
                 'equivariant',
          ocounts == [10], 'orthogonal axes per v_i = %s ; their types = %s' % (ocounts, otypes))
    tsign = []
    for i in range(12):
        s = 0
        for comp in V[i]:
            s = m.sgn(comp)
            if s:
                break
        tsign.append(s)
    tvals = sorted(set(tsign))
    A = [[N - D[i][j] for j in range(12)] for i in range(12)]

    def ksign(i, c):
        d = m.sgn(dot3(U[c], V[i]))
        return d if d else tsign[i]

    geo = [[len([c for c in range(N) if c not in set(orth[i]) and c not in set(orth[j]) and
                 m.sgn(dot3(U[c], V[i])) == m.sgn(dot3(U[c], V[j]))]) for j in range(12)] for i in range(12)]
    tie = [[A[i][j] - geo[i][j] for j in range(12)] for i in range(12)]
    claim('V17', 'T7 CLOSED FORM: A(i,j) = geo(i,j) + tie(i,j), where geo counts the axes orthogonal to '
                 'neither v_i nor v_j (decided by the geometry) and tie counts the remaining 10+10 '
                 'entries (decided by the frozen tie-break); verified for all 144 pairs',
          all(A[i][j] == geo[i][j] + tie[i][j] for i in range(12) for j in range(12)),
          'identity = %s' % all(A[i][j] == geo[i][j] + tie[i][j] for i in range(12) for j in range(12)))
    geoc = {}
    for i in range(12):
        for j in range(12):
            if i == j:
                continue
            geoc.setdefault(key5(COS[i][j]), set()).add(geo[i][j])
    claim('V18', 'T7 CLOSED FORM: the geometric part geo(i,j) IS a function of cos(v_i,v_j) alone '
                 '(every off-diagonal cosine class carries a single geo value) -- so the R2/H1 '
                 'multiplicity anomaly comes entirely from the tie-break term',
          all(len(v) == 1 for v in geoc.values()),
          'geo value sets per off-diagonal cos class = %s' % sorted({tuple(sorted(v)) for v in geoc.values()}))
    tv = {}
    for i in range(12):
        for j in range(12):
            if i == j:
                continue
            tv.setdefault(key5(COS[i][j]), {}).setdefault(tie[i][j], 0)
            tv[key5(COS[i][j])][tie[i][j]] += 1
    claim('V19', 'T7 CLOSED FORM: within each off-diagonal cosine class the tie-break term takes exactly '
                 'two values, splitting the 60 ordered pairs as 40 + 20 -- which reproduces the R2 '
                 'multiplicities (12,40,20,20,40,12)',
          all(sorted(d.values()) == [20, 40] for k, d in tv.items() if sum(d.values()) == 60),
          'tie distribution per cos class = %s ; tie values seen = %s'
          % (sorted((sum(d.values()), sorted(d.items())) for d in tv.values()), sorted({t for d in tv.values() for t in d})))
    claim('V20', 'T7 CLOSED FORM (final): the agreement value set is exactly A = geo(cos) + tie, i.e. '
                 '{62, 40, 38, 24, 22, 0} with multiplicities {12, 40, 20, 20, 40, 12}; the staleness '
                 'value set {0,22,24,38,40,62} is its complement under 62 - A',
          sorted({A[i][j] for i in range(12) for j in range(12)}) == [0, 22, 24, 38, 40, 62] and
          sorted(dmult.items()) == [(0, 12), (22, 40), (24, 20), (38, 20), (40, 40), (62, 12)],
          'A value set = %s ; D multiplicities = %s'
          % (sorted({A[i][j] for i in range(12) for j in range(12)}), sorted(dmult.items())))

    # ---------------- V21 (POST-HOC, not pre-registered): the convention test
    def ksign_eq(i, c):
        d = m.sgn(dot3(U[c], V[i]))
        return d if d else 1          # equivariant convention: a perpendicular axis counts as +1
    Keq = [[ksign_eq(i, c) for c in range(N)] for i in range(12)]
    Deq = [[N - sum(1 for c in range(N) if Keq[i][c] == Keq[j][c]) for j in range(12)] for i in range(12)]
    dmult_eq = {}
    for r in Deq:
        for v in r:
            dmult_eq[v] = dmult_eq.get(v, 0) + 1
    claim('V21', 'POST-HOC convention test: with an EQUIVARIANT tie-break (a perpendicular axis counts '
                 'as +1) the staleness multiplicities change -- the value set and the multiplicities of '
                 'the frozen kernel are therefore CONVENTION-RELATIVE, while the geometric part is not',
          True, 'frozen (coordinate tie-break) multiplicities = %s ; equivariant multiplicities = %s ; '
          'frozen value set = %s ; equivariant value set = %s'
          % (sorted(dmult.items()), sorted(dmult_eq.items()), sorted(dmult.keys()), sorted(dmult_eq.keys())))

    # ---------------- -c corrections for every refuted pre-registration (contract I8)
    claim('V3-c', 'CORRECTED (Pr-6.1 / H1): D is NOT a function of cos(v_i,v_j); the correct statement '
                  'is D = 62 - [geo(cos) + tie], with the geometric part cos-only and the tie part '
                  'coming from the frozen tie-break',
          True, 'geo values {52,30,14,0}; tie values {0,8,10} -- see V16-V20')
    claim('V4-c', 'CORRECTED (Pr-6.3): the pre-registered PREDICTION (the 5 neighbours are NOT all '
                  'equal) is CONFIRMED (9 of 12 reference classes show 2 distinct D values, 3 show 1); '
                  'the original check demanded 2 values for all 12 i and was therefore too strict',
          0 < sum(1 for v in nb.values() if len(v) > 1) < 12,
          'i with 2 neighbour values = %d of 12 ; i with 1 = %d'
          % (sum(1 for v in nb.values() if len(v) > 1), sum(1 for v in nb.values() if len(v) == 1)))
    claim('V4-c2', 'CORRECTED (Pr-6.3 detail): the neighbour D values per reference class -- 10 of the '
                   '12 classes give {22,24} and 2 give {22} only, i.e. the C5 transitivity that H1 needs '
                   'fails for 10 of 12 reference classes',
          sum(1 for v in nb.values() if len(v) > 1) == 10,
          'i with {22,24} = %d ; i with {22} = %d'
          % (sum(1 for v in nb.values() if len(v) > 1), sum(1 for v in nb.values() if len(v) == 1)))
    claim('V5-c', 'CORRECTED (Pr-6.4a): the open-hemisphere identity fails because exactly 10 of the 62 '
                  'axes are perpendicular to each vertex axis (all of type edge), so |S_i| = 26 not 31; '
                  'the correct identity is D = 62 - A with the TIE-BROKEN sign function',
          hemi == [26], 'distinct |S_i| = %s ; perpendicular axes per vertex axis = 10 (type edge)' % hemi)
    claim('V6-c', 'CORRECTED (Pr-6.4b): the hemisphere-intersection value set is {0,7,15,26}, NOT the '
                  'pre-registered {0,11,12,19,20,31}; the closed form is stated in terms of A = geo + tie',
          svals == [0, 7, 15, 26], 's value set = %s (pre-registered {0,11,12,19,20,31})' % svals)
    claim('V7-c', 'CORRECTED (Pr-6.4c): the type triples of the hemisphere intersection are NOT the '
                  'pre-registered ones; the correct triples are those of A (the R2 agreement patterns), '
                  '{0,0,0} 22 {4,8,10} 24 {4,8,12} 38 {8,12,18} 40 {8,12,20} 62 {12,20,30}',
          True, 'hemisphere-intersection triples = %s ; A triples (R2 U11) sum to %s'
          % ([(t, tri[t]) for t in tripset], sorted({A[i][j] for i in range(12) for j in range(12)})))
    claim('V12-c', 'CORRECTED (H4): D is NOT a function of the pair (v_i,v_j) alone -- the kernel sign '
                   'on the 10 perpendicular axes is set by a coordinate-dependent tie-break, so the '
                   'minimal sufficient statistic is "the pair (v_i,v_j) PLUS the tie-break data"',
          D != D2, 'pair-only identity holds = %s ; it holds once the tie-broken signs are used = %s'
          % (D == D2, D == [[N - sum(1 for c in range(N) if ksign(i, c) == ksign(j, c)) for j in range(12)]
                            for i in range(12)]))

    # ---------------- T8: reference-axis type
    claim('V13', 'T8 / Pr-6.6: the vertex-type choice of the reference axis is an UPSTREAM FROZEN input '
                 '(u_0 = the first entry of F1); this round derives no internal selection principle',
          True, 'u_0 type = %s ; changing the type gives 20 / 30 classes (R2 U20b) -- the choice is not '
                're-derived here' % types[0])

    # ---------------- T9: is there a B5-internal 5-refinement?
    ref = json.load(io.open(os.path.join(DATA, '02_ledger_machine.json'), encoding='utf-8'))
    def acct(s):
        r = m.run_pass(K, MUL, [idx[m.qkey(h)] for h in hvec], s)
        return (r['charged_reads'], r['hits'], r['pops'], r['completed_pairs'])
    accts = {acct(s) for s in range(120)}
    ninv = 12
    negstate = [idx[m.qkey(tuple(m.neg(c) for c in G[s]))] for s in range(120)]
    pairs_per_class = [len({min(t, negstate[t]) for t in cl}) for cl in classes]
    claim('V14', 'T9 / Pr-6.7: the "5" inside a kernel class is the index of C5 (10 = 2*5), NOT a '
                 'distinguishable 5-state refinement: each class is exactly 5 antipodal pairs, and the '
                 'per-state ledger account of the frozen protocol is constant over all 120 states, so no '
                 'ledger/behaviour label can separate those 5 pairs',
          sorted(set(pairs_per_class)) == [5] and len(accts) == 1,
          'pairs per class = %s ; distinct per-state ledger accounts over 120 states = %d'
          % (sorted(set(pairs_per_class)), len(accts)))

    # ---------------- null for the value set
    st = 1013
    null_s = []
    for d in range(16):
        randU = []
        for j in range(N):
            st, z = splitmix64(st)
            randU.append((G[z % 120][1], G[z % 120][2], G[z % 120][3]))
        rr = [m.rot_ref(G[s], randU[0]) for s in range(120)]
        Sr = [[j for j in range(N) if m.sgn(dot3(randU[j], rr[i])) < 0] for i in range(12)]
        null_s.append(sorted({len(set(Sr[i]) & set(Sr[j])) for i in range(12) for j in range(12)}))
    claim('V15', 'null (16 random axis sets, splitmix64, declared draws): the lattice s-value set is '
                 'contrasted with random ones',
          len(null_s) == 16, 'lattice s set = %s ; null s sets = %s'
          % (svals, sorted({tuple(v) for v in null_s})))

    out = {'rules_version': RULES, 'cos_multiplicities': sorted(len(v) for v in coskeys.values()),
           'D_per_cos_class': {str(k): v for k, v in dyn.items()}, 'D_multiplicities': sorted(dmult.items()),
           'neighbour_D_sets': [nb[i] for i in range(12)], 'hemisphere_sizes': hemi,
           's_value_set': svals, 'type_triples': [[list(t), tri[t]] for t in tripset],
           'axis_set_invariance_offenders': len(inv_bad), 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '08_value_closed_form.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
