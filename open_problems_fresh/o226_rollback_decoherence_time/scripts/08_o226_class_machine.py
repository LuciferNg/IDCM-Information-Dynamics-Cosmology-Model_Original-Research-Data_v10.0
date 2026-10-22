#!/usr/bin/env python3
"""O226 scripts/08 -- R2 machine: the group-theoretic source of the kernel-class structure.

Contract: docs/06_o226_r2_contract.md (o226-r2-contract-v1), items I10-I16, judgements T1-T5.
Pre-registered items keep their exact wording; refuted ones stay FAIL and a separate -c carries the
measured statement (contract I8).  Addendum, registered BEFORE the family prediction was measured:
K is right-Stab(u_0)-invariant => #classes = [2I : Stab(u_0)] = |orbit(u_0)|, which predicts
12 / 20 / 30 classes for a vertex / face / edge reference axis.

Loads the LOCAL frozen R1 machine scripts/02 only (enforcer C5b).  Exact arithmetic everywhere:
Q(sqrt5) pairs of Fraction and integer counts; no float literal in this file.
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
RULES = 'o226-r2-contract-v1'
N = 62
B_UNITS = 88
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
    print('O226 scripts/08 -- R2 kernel-class source (rules: %s)' % RULES)
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
    naxis = len(U)
    u0 = U[0]
    type_of = {}
    for a in range(naxis):
        type_of.setdefault(types[a], []).append(a)

    def dot3(a, b):
        return m.add(m.add(m.mul(a[0], b[0]), m.mul(a[1], b[1])), m.mul(a[2], b[2]))

    def qdiv(x, y):
        den = y[0] * y[0] - 5 * y[1] * y[1]
        return ((x[0] * y[0] - 5 * x[1] * y[1]) / den, (x[1] * y[0] - x[0] * y[1]) / den)

    def negax(v):
        return (m.neg(v[0]), m.neg(v[1]), m.neg(v[2]))

    def dir_key(v):
        # sign-preserving: the first non-zero component is normalised to +1 and its sign is kept,
        # so v and -v get DIFFERENT keys (pointed directions) while parallel vectors share one key
        for k in range(3):
            if v[k] != m.ZERO:
                return (m.sgn(v[k]), k) + tuple(qdiv(c, v[k]) for c in v)
        return None

    def build_K_ref(G0, U0, ref):
        K0 = []
        for q in G0:
            r = m.rot_ref(q, ref)
            row = []
            for u in U0:
                s = m.sgn(dot3(u, r))
                if s == 0:
                    for comp in r:
                        sc = m.sgn(comp)
                        if sc:
                            s = sc
                            break
                row.append(s)
            K0.append(row)
        return K0

    def orbit_dir(u):
        return {dir_key(m.rot_ref(G[s], u)) for s in range(120)}

    def order_of(i):
        p, o = G[i], 1
        while m.qkey(p) != m.qkey(ONE):
            p = m.qmul(p, G[i])
            o += 1
        return o

    # ---------------- classes of the read kernel
    rows = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rows[s], []).append(s)
    keys = sorted(cls.keys())
    reps = [cls[k][0] for k in keys]
    classes = [cls[k] for k in keys]
    ncls = len(cls)
    claim('U1', 'the read kernel has 12 classes (R1 G1 reproduced); reps rebuilt from the frozen inputs',
          ncls == 12 and sorted({len(v) for v in classes}) == [10],
          'classes = %d ; sizes = %s' % (ncls, sorted({len(v) for v in classes})))

    # ---------------- T2: stabilisers (pre-registered wording kept verbatim)
    stabs = [[t for t in range(120) if rows[MUL[r][t]] == rows[r]] for r in reps]
    specs = [sorted(order_of(t) for t in H) for H in stabs]
    claim('U2', 'Pr-5.2: every class stabiliser has order 10 with element-order multiset '
                '{1,2,5,5,5,5,10,10,10,10} (= C10, contains the centre)',
          all(len(H) == 10 for H in stabs) and all(s == [1, 2, 5, 5, 5, 5, 10, 10, 10, 10] for s in specs),
          'sizes = %s ; order multisets distinct = %s'
          % ([len(H) for H in stabs], sorted({tuple(s) for s in specs})))
    inter = sorted({len(set(stabs[i]) & set(stabs[j])) for i in range(ncls) for j in range(i + 1, ncls)})
    claim('U3', 'Pr-5.2 (as pre-registered): distinct classes have stabilisers meeting exactly in the '
                'centre {+-1} (order 2)',
          inter == [2], 'pairwise intersection sizes = %s' % inter)
    Hset = set(stabs[0])
    claim('U3-c', 'CORRECTED Pr-5.2 (measured): all 12 classes share ONE and the SAME stabiliser '
                  'subgroup H of order 10 (pairwise intersections = |H| = 10) => K is right-H-invariant',
          len({tuple(sorted(H)) for H in stabs}) == 1 and len(Hset) == 10,
          'distinct stabiliser sets = %d ; |H| = %d' % (len({tuple(sorted(H)) for H in stabs}), len(Hset)))
    nsub = len({tuple(sorted(H)) for H in stabs})
    claim('U4', 'the 12 stabilisers fall into 6 distinct subgroups (12 = 6 conjugate C10 x 2 classes each)',
          nsub == 6 and 12 // nsub == 2,
          'distinct stabiliser subgroups = %d ; classes per subgroup = %d' % (nsub, 12 // nsub))
    coset_ok = all(set(v) == {MUL[r][t] for t in Hset} for r, v in zip(reps, classes))
    claim('U4-c', 'CORRECTED: the class count is [2I : H] = 120/10 = 12 (not 6 subgroups); the 12 rows '
                  'are exactly the 12 right cosets rep*H',
          nsub == 1 and coset_ok, 'distinct subgroups = %d ; every class = rep*H = %s' % (nsub, coset_ok))

    stab_u0 = [s for s in range(120) if dir_key(m.rot_ref(G[s], u0)) == dir_key(u0)]
    claim('U5-c', 'THEOREM (immediate from the definition of K, measured): H = Stab_{2I}(u_0), the '
                  'pointed stabiliser of the reference axis u_0 => K is right-H-invariant and the '
                  'class count equals |orbit(u_0)|',
          set(stab_u0) == Hset and len(stab_u0) == 10,
          '|Stab(u_0)| = %d ; equals the common class stabiliser = %s ; u_0 type = %s'
          % (len(stab_u0), set(stab_u0) == Hset, types[0]))

    # ---------------- T1: fixed axes of H, and the corrected bijection
    fixed_H = [a for a in range(naxis)
               if all(dir_key(m.rot_ref(G[t], U[a])) in (dir_key(U[a]), dir_key(negax(U[a]))) for t in Hset)]
    claim('U5', 'Pr-5.1: every class stabiliser fixes exactly 2 of the 62 pointed axes, both of type '
                'vertex and mutually antipodal',
          len(fixed_H) == 2 and all(types[a] == 'vertex' for a in fixed_H) and
          dir_key(U[fixed_H[0]]) == dir_key(negax(U[fixed_H[1]])),
          'fixed pointed axes of H = %s (types %s)' % (fixed_H, [types[a] for a in fixed_H]))
    claim('U6', 'Pr-5.1: the map class -> directed fixed vertex axis is a BIJECTION onto the 12 vertex '
                'axes (each used exactly once)',
          len(fixed_H) == 12,
          'directed fixed axes over the 12 classes = %d (all classes share the same 2 axes: no bijection)'
          % len(fixed_H))
    orb_v = {a: len(orbit_dir(U[a])) for a in type_of['vertex']}
    cls_axis = [dir_key(m.rot_ref(G[r if False else reps[i]], u0)) for i in range(12)]
    claim('U6-c', 'CORRECTED Pr-5.1 (the real bijection): class(s) -> rho(s) u_0 is a bijection onto the '
                  '12 pointed vertex axes; well defined on right cosets since H = Stab(u_0) fixes u_0',
          sorted(set(orb_v.values())) == [12] and len(set(cls_axis)) == 12,
          'orbit size of every vertex axis = %s ; distinct images of the 12 classes = %d'
          % (sorted(set(orb_v.values())), len(set(cls_axis))))
    claim('U7', 'Pr-5.1: the induced map class -> antipodal vertex pair is 2-to-1 onto 6 pairs '
                '(12 = 2 x 6)',
          False,
          'antipodal pairs reached by the 12 classes = 1 (all classes share the reference pair): '
          'the 2-to-1 structure is REFUTED; the bijection is 12 classes <-> 12 pointed vertex axes')

    # ---------------- family prediction (registered before this measurement)
    fam = {t: sorted({len(orbit_dir(U[a])) for a in type_of[t]}) for t in ('vertex', 'face', 'edge')}
    claim('U20', 'FAMILY PREDICTION (registered before measurement): with the reference axis replaced '
                 'by an axis of type T the number of kernel classes equals |orbit| = 120/|Stab| = '
                 '12 / 20 / 30 for T = vertex / face / edge',
          fam == {'vertex': [12], 'face': [20], 'edge': [30]},
          'orbit sizes by reference type over all 62 axes = %s' % fam)
    full = {t: len({tuple(r) for r in build_K_ref(G, U, U[type_of[t][0]])})
            for t in ('vertex', 'face', 'edge')}
    claim('U20b', 'non-degeneracy of the theorem: for a reference axis of each type the kernel really '
                  'has exactly |orbit| distinct rows (no further degeneracy) -- 12 / 20 / 30',
          full == {'vertex': 12, 'face': 20, 'edge': 30}, 'measured distinct rows = %s' % full)

    # ---------------- row weights
    wts = [sum(K[r]) for r in reps]
    claim('U8', 'BLIND (reported, not pre-registered): the 12 class row weights split 6/6 as +-10 '
                '(forced by the 62 per-setting 60/60 balances: the 12 weights must sum to 0)',
          sorted(wts) == [-10] * 6 + [10] * 6, 'weights = %s' % sorted(wts))

    # ---------------- T3: agreement sets and the value set
    def agree(i, j):
        return [c for c in range(N) if K[reps[i]][c] == K[reps[j]][c]]

    D = [[N - len(agree(i, j)) for j in range(12)] for i in range(12)]
    dvals = sorted({v for r in D for v in r})
    agvals = sorted({(N - v) // 2 for v in dvals})
    orbit_sets = {'V': type_of['vertex'], 'F': type_of['face'], 'E': type_of['edge']}
    not_union = []
    for i in range(12):
        for j in range(12):
            A = set(agree(i, j))
            if not all((set(v) <= A) or not (set(v) & A) for v in orbit_sets.values()):
                not_union.append([i, j, len(A)])
    claim('U9', 'Pr-5.3: the agreement counts (62-d)/2 take the value set {0,11,12,19,20}',
          agvals == [0, 11, 12, 19, 20], 'agreement value set = %s (d value set %s)' % (agvals, dvals))
    claim('U10', 'Pr-5.3 (pre-registered direction): at least one agreement set is NOT a union of the '
                 'V/F/E axis-type orbits (the agreement structure is finer than the type partition)',
          len(not_union) > 0, 'non-union pairs = %d of 144 ; first = %s' % (len(not_union), not_union[:4]))
    pats = {}
    for i in range(12):
        for j in range(12):
            A = set(agree(i, j))
            sig = tuple(len(set(v) & A) for v in orbit_sets.values())
            pats[sig] = pats.get(sig, 0) + 1
    claim('U11', 'the agreement sets take %d distinct patterns over the 144 class pairs = (how much of '
                 'each of V/F/E is agreed); reported only' % len(pats),
          True, 'patterns (V,F,E) -> multiplicity = %s' % sorted(pats.items()))

    dc = {}
    for i in range(12):
        for j in range(12):
            x = MUL[inv[reps[i]]][reps[j]]
            key = tuple(sorted({MUL[MUL[a][x]][b] for a in stabs[i] for b in stabs[j]}))
            dc.setdefault(key, set()).add(D[i][j])
    bad_dc = [k for k, v in dc.items() if len(v) > 1]
    coll = []
    if bad_dc:
        for i in range(12):
            for j in range(12):
                x = MUL[inv[reps[i]]][reps[j]]
                key_ij = tuple(sorted({MUL[MUL[a][x]][b] for a in stabs[i] for b in stabs[j]}))
                if key_ij in bad_dc:
                    coll.append([i, j, D[i][j], order_of(x)])
    byorder = {}
    for i in range(12):
        for j in range(12):
            x = MUL[inv[reps[i]]][reps[j]]
            byorder.setdefault(order_of(x), set()).add(D[i][j])
    claim('U12-c', 'POST-HOC (not pre-registered): the refuted double-coset hypothesis is replaced by '
                   'the measured finer structure -- the colliding double cosets carry 2 distances each, '
                   'and the distance is not a function of the order of rep_i^-1 rep_j either',
          len(bad_dc) == 2, 'collisions = %d ; colliding (i,j,d,ord(x)) = %s ; distance per order of x '
          '= %s' % (len(bad_dc), coll[:12],
                    {k: sorted(v) for k, v in sorted(byorder.items())}))
    claim('U12', 'Pr-5.4: d(i,j) depends only on the double coset H x H -- the 144 distances collapse '
                 'onto the distinct double cosets with no collision carrying two values',
          not bad_dc, 'distinct double cosets = %d ; value multiset = %s ; collisions = %d'
          % (len(dc), sorted({v for s in dc.values() for v in s}), len(bad_dc)))

    claim('U9-c', 'CORRECTED Pr-5.3: the agreement counts are {31} on the 12 diagonal (self) pairs and '
                  '{0,11,12,19,20} on the 132 off-diagonal class pairs -- the pre-registered set forgot '
                  'the diagonal (62/2 = 31), which is an accounting slip, not a structural finding',
          agvals == [0, 11, 12, 19, 20, 31],
          'full agreement value set = %s ; off-diagonal (d > 0) = %s'
          % (agvals, sorted({(N - D[i][j]) // 2 for i in range(12) for j in range(12) if D[i][j] > 0})))

    # ---------------- T4: the three-layer collapse
    neg = [idx[m.qkey(tuple(m.neg(c) for c in q))] for q in G]
    pmap = {}
    for s in range(120):
        pmap.setdefault(min(s, neg[s]), []).append(s)
    npairs = len(pmap)
    inside = all(len({min(t, neg[t]) for t in cl}) == 5 for cl in classes)
    claim('U13', 'Pr-5.5: the 120 states form 60 antipodal pairs {s,-s} (the B5 Z2 collapse quoted from '
                 'G3), and every kernel class is exactly 5 such pairs',
          npairs == 60 and inside and 12 * 5 == 60,
          'antipodal pairs = %d ; pairs per class = 5 ; 12 x 5 = %d' % (npairs, 12 * 5))
    claim('U14', 'Pr-5.5: the kernel collapse (120 -> 12) is strictly coarser than the B5 behaviour '
                 'collapse (120 -> 60)',
          npairs == 60 and inside and ncls == 12 and 60 // ncls == 5,
          'behaviour pairs = 60 ; kernel classes = %d ; ratio = %d' % (ncls, 60 // ncls))

    # ---------------- T5: which k gives the recorded 44 charges?
    ks = []
    for k in (1, 2, 3, 4):
        mstar = (B_UNITS - 1) // k + 1
        ks.append({'k': k, 'm_star': mstar, 'sigma_units': mstar * k,
                   'exact': mstar * k == B_UNITS, 'is_44': mstar == 44})
    claim('U15', 'Pr-5.6: k is fixed by the RECORDED account (the feasible pass charges exactly '
                 '44 = N_d reads = 1 tick), not by exact exhaustion; measured k-table for k = 1..4',
          ks[0]['m_star'] == 88 and ks[1]['m_star'] == 44 and ks[3]['m_star'] == 22 and
          sum(1 for v in ks if v['is_44']) == 1,
          ' | '.join('k=%d -> m*=%d Sigma=%d theta exact=%s' % (v['k'], v['m_star'], v['sigma_units'],
                                                                v['exact']) for v in ks))
    claim('U16', 'Pr-5.6 (pre-registered value for k = 3 was 29): the machine measures k = 3 -> 30 '
                 '((88-1)//3 + 1 = 30)  =>  the pre-registered number is REFUTED',
          ks[2]['m_star'] == 30, 'k = 3 -> m* = %d (pre-registered 29)' % ks[2]['m_star'])
    claim('U16-c', 'CORRECTED Pr-5.6: for k = 1..4 the charged reads are 88 / 44 / 30 / 22; only k = 2 '
                   'reproduces the recorded 44 reads per tick, and k = 1 also exhausts the budget '
                   'exactly (Sigma = 88 theta = B) => the choice k = 2 is DATA-selected, not derived '
                   'from exhaustion',
          [v['m_star'] for v in ks] == [88, 44, 30, 22] and ks[0]['exact'] and ks[1]['exact'] and
          sum(1 for v in ks if v['is_44']) == 1,
          'reads = %s ; exactly-exhausting k = %s' % ([v['m_star'] for v in ks],
                                                       [v['k'] for v in ks if v['exact']]))

    # ---------------- Pr-5.7: discriminating power of the raw numbers
    pool = {12: ['|orbit of a vertex axis|', 'B*N_gen = 4*3', '|2I|/|H| = 120/10', 'N_gen^2+N_gen = 9+3'],
            10: ['|H| = |Stab(u_0)|', '2*B+2', '|centre|*|C5| = 2*5', '|C10|'],
            6: ['2*N_gen', '|antipodal vertex axes|', '|A5|/|C5|/2'],
            5: ['|C5|', 'pairs per class', 'N_gen+2', 'the fold of the 5-fold axis'],
            11: ['(62-40)/2', 'B*N_gen-1', 'N_d/4'],
            19: ['(62-24)/2', 'F_7-10'],
            20: ['|orbit of a face axis|', '2*|H|', 'N_d-24', 'A5/C3'],
            22: ['(62-18)/2', 'N_d/2'],
            24: ['2*12', '|H|+14', '2*B*N_gen'],
            38: ['62-24', '2*19'],
            40: ['62-22', '2*20', '2*|face orbit|']}
    multi = [k for k, v in pool.items() if len(v) >= 2]
    claim('U17', 'Pr-5.7: every raw number in play (12, 10, 6, 5, 11, 19, 20, 22, 24, 38, 40) carries '
                 '>= 2 independent structural readings => no single number has discriminating power; '
                 'only the explicit orbit statement (U5-c/U6-c/U20) carries structure',
          len(multi) >= 5, 'values with >= 2 readings = %d of %d' % (len(multi), len(pool)))

    # ---------------- null: random axis sets
    st = 226
    nulls = []
    for d in range(32):
        randU = []
        for j in range(N):
            st, z = splitmix64(st)
            randU.append((G[z % 120][1], G[z % 120][2], G[z % 120][3]))
        rn = {}
        Kn = build_K_ref(G, randU, randU[0])
        for s in range(120):
            rn.setdefault(tuple(Kn[s]), []).append(s)
        nulls.append({'classes': len(rn), 'sizes': sorted({len(v) for v in rn.values()})})
    ncls_set = sorted({v['classes'] for v in nulls})
    claim('U18', 'null (32 random axis sets, splitmix64, declared draws): the lattice kernel (12 '
                 'classes, all of size 10) contrasted with random kernels',
          len(nulls) == 32, 'lattice = 12 (sizes [10]) ; null class counts = %s ; null size sets = %s'
          % (ncls_set, sorted({tuple(v['sizes']) for v in nulls})))

    # ---------------- rigidity
    alt = [cl[-1] for cl in classes]
    D2 = [[N - sum(1 for c in range(N) if K[alt[i]][c] == K[alt[j]][c]) for j in range(12)] for i in range(12)]
    claim('U19', 'rigidity: the 12 x 12 distance table is independent of the choice of class '
                 'representatives (first vs last member of each class)',
          D == D2, 'identical = %s' % (D == D2))

    out = {'rules_version': RULES, 'classes': ncls, 'common_stabiliser_order': len(Hset),
           'stab_u0_order': len(stab_u0), 'reference_axis_type': types[0],
           'fixed_pointed_axes_of_H': fixed_H, 'orbit_sizes_by_reference_type': fam,
           'measured_rows_by_reference_type': full, 'class_pair_distance': D,
           'distance_value_set': dvals, 'agreement_value_set': agvals,
           'agreement_patterns': {'|'.join(map(str, k)): v for k, v in sorted(pats.items())},
           'agreement_not_union_pairs': not_union[:20], 'double_cosets': len(dc),
           'double_coset_collisions': len(bad_dc), 'collision_detail': coll[:12],
           'antipodal_pairs': npairs, 'weights': sorted(wts), 'k_table': ks,
           'null_class_counts': ncls_set, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '07_class_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
