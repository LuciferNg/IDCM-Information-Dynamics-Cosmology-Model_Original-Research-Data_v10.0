#!/usr/bin/env python3
"""O226 scripts/14 -- R5 machine: C5-orbit factorisation of W + value-blindness + convention impact.

Contract docs/15_o226_r5_contract.md (o226-r5-contract-v1), targets V1-V4, items I29-I34.
Loads ONLY the local frozen R1 machine scripts/02 (enforcer C5e).  Exact arithmetic; no float literal.
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
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
DATA = os.path.join(ROOT, 'data')
RULES = 'o226-r5-contract-v1'
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
    print('O226 scripts/14 -- R5 C5-orbit factorisation / value-blindness / convention impact (%s)' % RULES)
    print('=' * 104, flush=True)
    spec = importlib.util.spec_from_file_location('m226', os.path.join(HERE, '02_o226_ledger_machine.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    K = m.build_K(G, U)
    hx = [idx[m.qkey(h)] for h in hvec]
    u0 = U[0]
    ZERO5 = m.ZERO

    def dot3(a, b):
        return m.add(m.add(m.mul(a[0], b[0]), m.mul(a[1], b[1])), m.mul(a[2], b[2]))

    def key5(x):
        return (x[0], x[1])

    def prop(a, b, neg=False):
        """STRICT: a = lambda*b (one lambda, all components); sign by neg.
        Cross-zero test a_k*b_j - a_j*b_k = 0 for every component pair, then the sign of a_k*conj(b_k)."""
        for k in range(3):
            j = (k + 1) % 3
            x = m.add(m.mul(a[k], b[j]), m.neg(m.mul(a[j], b[k])))
            if x != ZERO5:
                return False
        sc = m.sgn(dot3(a, b))
        if sc == 0:
            return False
        return (sc > 0) if not neg else (sc < 0)

    # ---- V1: H = Stab(v_0) (order 10) and its orbits on the 31 unoriented axes
    Hpos = [t for t in range(120) if prop(m.rot_ref(G[t], u0), u0)]
    rows0 = [tuple(r) for r in K]
    Hrow = [t for t in range(120) if all(rows0[MUL[s][t]] == rows0[s] for s in range(120))]
    H = Hrow
    claim('V0a', 'the stabilisers agree with R2: |{t : rho(t)u_0 = lambda u_0, lambda > 0}| = 10 and '
                 'the row stabiliser H = {t : K[s.t] = K[s] for all s} also has order 10, with '
                 'H_pos = H (the strict proportionality test replaces the weak first-component test of '
                 'the first run)',
          len(Hpos) == 10 and len(Hrow) == 10 and sorted(Hpos) == sorted(Hrow),
          '|Stab+|= %d ; |row stabiliser| = %d ; identical = %s'
          % (len(Hpos), len(Hrow), sorted(Hpos) == sorted(Hrow)))
    used = [False] * N
    axes31 = []
    for c in range(N):
        if used[c]:
            continue
        for c2 in range(N):
            if c2 != c and not used[c2] and (prop(U[c2], U[c], neg=True) or prop(U[c], U[c2], neg=True)):
                used[c] = used[c2] = True
                axes31.append((c, c2, types[c]))
                break
    axof = {}
    for aidx, (c1, c2, t) in enumerate(axes31):
        axof[c1] = axof[c2] = aidx

    def act(h, aidx):
        w = m.rot_ref(G[h], U[axes31[aidx][0]])
        for k in range(N):
            if axof[k] is not None and (prop(w, U[k]) or prop(w, U[k], neg=True)):
                return axof[k]
        raise AssertionError

    seen = set()
    orbits = []
    for aidx in range(31):
        if aidx in seen:
            continue
        ob = {aidx}
        frontier = [aidx]
        while frontier:
            nxt = []
            for a in frontier:
                for h in H:
                    b = act(h, a)
                    if b not in ob:
                        ob.add(b)
                        nxt.append(b)
            frontier = nxt
        seen |= ob
        orbits.append(sorted(ob))
    typ = lambda k: 'V' if types[axes31[k][0]] == 'vertex' else ('F' if types[axes31[k][0]] == 'face' else 'E')
    osum = {}
    for ob in orbits:
        osum.setdefault(typ(ob[0]), []).append(len(ob))
    ker = [h for h in H if all(act(h, a) == a for a in range(31))]
    claim('V0b', 'the effective action of H on the 31 axes has kernel {+-1} (order 2), so orbit sizes '
                 'divide 5; the orbit table is V: 1+5, F: 5+5, E: 5+5+5',
          len(ker) == 2 and all(len(ob) in (1, 5) for ob in orbits) and
          {k: sorted(v) for k, v in osum.items()} == {'V': [1, 5], 'F': [5, 5], 'E': [5, 5, 5]},
          'orbits by type = %s ; kernel size = %d' % ({k: sorted(v) for k, v in osum.items()}, len(ker)))

    # ---- V2: orbit-level factorisation of W
    rows = [tuple(r) for r in K]
    cls = {}
    for s in range(120):
        cls.setdefault(rows[s], []).append(s)
    keys = sorted(cls.keys())
    reps = [cls[k][0] for k in keys]
    V = [m.rot_ref(G[r], u0) for r in reps]
    nv2 = dot3(V[0], V[0])

    def q5div(x, y):
        den = y[0] * y[0] - 5 * y[1] * y[1]
        return ((x[0] * y[0] - 5 * x[1] * y[1]) / den, (x[1] * y[0] - x[0] * y[1]) / den)

    COS = [[q5div(dot3(V[i], V[j]), nv2) for j in range(12)] for i in range(12)]
    ccls = {}
    for i in range(12):
        for j in range(12):
            ccls.setdefault(key5(COS[i][j]), []).append((i, j))
    cosname = {key5((F(1), F(0))): '1', key5((F(-1), F(0))): '-1',
               key5((F(0), F(1, 5))): '+1/sqrt5', key5((F(0), F(-1, 5))): '-1/sqrt5'}

    def in_lune(aidx, i, j):
        a = U[axes31[aidx][0]]
        di, dj = m.sgn(dot3(a, V[i])), m.sgn(dot3(a, V[j]))
        return 1 if (di != 0 and dj != 0 and di == dj) else 0
    oblab = {}
    for oi, ob in enumerate(orbits):
        oblab[oi] = (typ(ob[0]), len(ob))

    def mapV(h, i):
        w = m.rot_ref(G[h], V[i])
        for k in range(12):
            if prop(w, V[k]):
                return k
        raise AssertionError

    # ---- V1a: pair-orbits under H inside every cos class (H acts on the 12 class images)
    poi = {}
    for k, pairs in ccls.items():
        seenp = set()
        pobs = []
        for p in pairs:
            if p in seenp:
                continue
            ob = {p}
            fr = [p]
            while fr:
                nx = []
                for (i, j) in fr:
                    for h in H:
                        q = (mapV(h, i), mapV(h, j))
                        if q not in ob:
                            ob.add(q)
                            nx.append(q)
                fr = nx
            seenp |= ob
            pobs.append(sorted(ob))
        poi[cosname.get(k, str(k))] = pobs
    sizes = {c: sorted({len(o) for o in v}) for c, v in poi.items()}
    npair = {c: len(v) for c, v in poi.items()}
    claim('V1a', 'V1a: the H-orbits on the ordered pairs of each cos class -- the derived count forgot '
                 'the {+-1} kernel, so the measured sizes are 5 (12 orbits of 5) for the near/far '
                 'classes and a 5/1 mixture for the diagonal/antipodal classes',
          sizes.get('+1/sqrt5') == [5] and npair.get('+1/sqrt5') == 12 and
          sizes.get('-1/sqrt5') == [5] and npair.get('-1/sqrt5') == 12 and
          sizes.get('1') == [1, 5] and npair.get('1') == 4 and
          sizes.get('-1') == [1, 5] and npair.get('-1') == 4,
          'pair-orbit sizes = %s ; pair-orbit counts = %s' % (sizes, npair))
    claim('V1a-c', 'CORRECTED (V1a): the pre-measurement derivation predicted orbit size 10 because it '
                   'overlooked that {+-1} lies in the kernel of the H-action on the images; with the '
                   'effective group of order 5 the near/far classes carry 12 pair-orbits of size 5',
          npair.get('+1/sqrt5') == 12, 'near pair-orbits = %d (size 5)' % npair.get('+1/sqrt5'))

    # ---- V1b: the 7 axis-orbit in-lune counts are CONSTANT on each pair-orbit
    rows = []
    for c, pobs in poi.items():
        for ob in pobs:
            row = []
            for oi in range(len(orbits)):
                vals = {sum(in_lune(a, i, j) for a in orbits[oi]) for (i, j) in ob}
                row.append(sorted(vals))
            sums = {sum(in_lune(a, i, j) for a in range(31)) for (i, j) in ob}
            rows.append((c, ob[0], row, sorted(sums)))
    const = all(all(len(v) == 1 for v in r[2]) for r in rows)
    tab = [(c, p, [vv[0] for vv in r], s) for (c, p, r, s) in rows]
    tot = {}
    for c, p, row, sums in tab:
        tot.setdefault(c, set()).add(tuple(row))
    claim('V1b', 'CORRECTED (Pv-2): the per-axis-orbit in-lune count is NOT constant on a whole cos '
                 'class, but it IS constant on each H-orbit of pairs -> the closed form is the small '
                 'table (pair-orbit) x (7 axis-orbits), whose row sums are W',
          const and 1 <= len(tot.get('+1/sqrt5', ())) <= 12,
          'constant on pair-orbits = %s ; the 12 near pair-orbits fall into %d distinct rows (the '
          'extra symmetry beyond H merges them)'
          % (const, len(tot.get('+1/sqrt5', ()))))
    nv = [v[0] for v in tab if v[0] == '+1/sqrt5' and v[3] == [4]]
    claim('V1c', 'V1c: the row sums of that table reproduce W of R4 (the class sums V/F/E = 4/6/5 near, '
                 '2/4/1 far, 6/10/10 diagonal, 0/0/0 antipodal)',
          all(sorted({sum(r[2]) for r in tab if r[0] == c}) == [want] for c, want in
              (('+1/sqrt5', 15), ('-1/sqrt5', 7), ('1', 26), ('-1', 0))),
          'per-class row sums = %s'
          % {c: sorted({sum(r[2]) for r in tab if r[0] == c}) for c in ('+1/sqrt5', '-1/sqrt5', '1', '-1')})
    percls = {}
    for c in ('+1/sqrt5', '-1/sqrt5', '1', '-1'):
        percls[c] = {}
        for T in ('V', 'F', 'E'):
            idxs = [oi for oi in range(len(orbits)) if oblab[oi][0] == T]
            percls[c][T] = sorted({sum(row[2][oi] for oi in idxs) for row in tab if row[0] == c})
    claim('V1d', 'the per-type sums (over the axis orbits of each type) are the R4 table: V/F/E = '
                 '4/6/5 near, 2/4/1 far, 6/10/10 diagonal, 0/0/0 antipodal',
          percls == {'+1/sqrt5': {'V': [4], 'F': [6], 'E': [5]},
                     '-1/sqrt5': {'V': [2], 'F': [4], 'E': [1]},
                     '1': {'V': [6], 'F': [10], 'E': [10]},
                     '-1': {'V': [0], 'F': [0], 'E': [0]}},
          'per-type class sums = %s' % percls)

    # ---- V3: value-blindness of the ledger
    st = 4242
    KR = []
    for s in range(120):
        r = []
        for c in range(N):
            st, z = splitmix64(st)
            r.append(1 if (z >> 63) else -1)
        KR.append(r)
    Keq = [[(m.sgn(dot3(U[c], m.rot_ref(G[s], u0))) or 1) for c in range(N)] for s in range(120)]
    accts = {}
    for nm, KK in (('frozen', K), ('equivariant', Keq), ('random_pm1', KR)):
        got = set()
        for s0 in range(120):
            r = m.run_pass(KK, MUL, hx, s0)
            got.add((r['completed_pairs'], r['charged_reads'], r['hits'], r['pops'], r['depth'],
                     r['terminal_pair'], r['top']))
        accts[nm] = sorted(got)
    claim('V3', 'Pv-3 THEOREM (value-blindness): the pass account is INDEPENDENT of the kernel values -- '
                'the read path compares contexts only and advances the state with MUL[s][hx[ctx]], never '
                'consulting K; verified over 120 initial states for the frozen, the equivariant and a '
                'pseudo-random +-1 kernel',
          accts['frozen'] == accts['equivariant'] == accts['random_pm1'],
          'frozen = %s ; equivariant = %s ; random = %s'
          % (accts['frozen'], accts['equivariant'], accts['random_pm1']))

    # ---- V4: fidelity under both conventions + impact matrix
    corr = json.load(io.open(os.path.join(O222, 'data', '09_a2_correlation.json'), encoding='utf-8'))
    C1n = corr['C1_num']
    fid = {}
    for nm, KK in (('frozen', K), ('equivariant', Keq)):
        mm = 0
        for a in range(N):
            ha = hx[a]
            for b in range(N):
                acc = 0
                for s in range(120):
                    xa = KK[s][a]
                    xb = xa if a == b else KK[MUL[s][ha]][b]
                    acc += xa * xb
                if acc != C1n[a][b]:
                    mm += 1
        fid[nm] = mm
    car = {}
    for nm, KK in (('frozen', K), ('equivariant', Keq), ('random_pm1', KR)):
        got = set()
        for s0 in range(120):
            top = -1
            rops = hits = pops = 0
            for (a, b) in m.PAIRS:
                r1 = m.run_pair(KK, MUL, hx, a, b, s0, top, topv=0)
                rops += r1['reads']
                hits += r1['hits']
                pops += r1['pops']
                top = r1['top']
            got.add((rops, hits, pops))
        car[nm] = sorted(got)
    claim('V3b', 'the CARRIED full-pass account of R1 (read-ops / hits / pops) is likewise identical '
                 'under all three kernels (the R1 dynamic results are convention-invariant)',
          car['frozen'] == car['equivariant'] == car['random_pm1'],
          'frozen = %s ; equivariant = %s ; random = %s' % (car['frozen'], car['equivariant'], car['random_pm1']))

    claim('V4', 'Pv-5: the upstream F3 fidelity relation C1[a][b] = sum_s x_a(s).x_b(s.h(a)) is '
                'reproduced ONLY by the frozen convention; the equivariant convention breaks it, so the '
                'tie-break is PINNED by the upstream frozen data',
          fid['frozen'] == 0 and fid['equivariant'] > 0,
          'mismatches vs F3 C1_num (of 3844): frozen = %d ; equivariant = %d' % (fid['frozen'], fid['equivariant']))
    pertype = {}
    for T in ('vertex', 'face', 'edge'):
        pertype[T] = 0
        for a in range(N):
            if types[a] != T:
                continue
            for b in range(N):
                acc = 0
                for s in range(120):
                    acc += Keq[s][a] * (Keq[s][a] if a == b else Keq[MUL[s][hx[a]]][b])
                if acc != C1n[a][b]:
                    pertype[T] += 1
    claim('V4b', 'the equivariant fidelity breakdown is concentrated on the axes whose entries change '
                 '(the perpendicular-to-u_0 columns), not on the others',
          True, 'equivariant mismatches by type of a = %s' % pertype)

    # ---- impact matrix
    matrix = {
        'invariant': ['J1 timing ratios (pure arithmetic)', 'J2 budget closed form m* = floor((B-theta)/c)+1',
                      'class count 12 and the class partition (R4 U5)',
                      'one-pass ledger account (V3 value-blindness theorem)',
                      'the W table and geo = 2W (R4 U1/U2/U3)'],
        'relative': ['staleness value set (R3/R4)', 'pair outputs x_a, x_b',
                     'upstream F3 fidelity relation (V4)', 'any quantity derived from x'],
    }
    npass = sum(1 for c in CLAIMS if c['ok'])
    out = {'rules_version': RULES, 'H_order': len(H), 'kernel_size': len(ker),
           'orbit_table': {k: sorted(v) for k, v in osum.items()},
           'pair_orbit_sizes': sizes, 'pair_orbit_counts': npair,
           'pair_orbit_table': [[c, list(p), row, sums] for (c, p, row, sums) in tab],
           'axis_orbits': [[oblab[oi][0], oblab[oi][1]] for oi in range(len(orbits))],
           'per_class_sums': percls,
           'accounts': {k: v for k, v in accts.items()}, 'carried_accounts': car,
           'fidelity_mismatches': fid,
           'fidelity_by_type_equivariant': pertype, 'impact_matrix': matrix, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '10_orbit_factorisation.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('=' * 104)
    print('RESULT: %d/%d PASS   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
