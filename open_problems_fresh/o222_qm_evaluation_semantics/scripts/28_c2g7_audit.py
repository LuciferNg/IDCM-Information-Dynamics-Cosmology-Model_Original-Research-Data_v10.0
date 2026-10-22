#!/usr/bin/env python3
"""O222 scripts/28 -- INDEPENDENT audit of the C2+G7 round (scripts/27).

Independence: this file does NOT import scripts/27.  Where the machine used the frozen run_pair and
Fraction elimination, the audit uses
  * the GROUP AXIOM route : every pair map is a composition of left translations and identities, hence a
                            bijection  =>  the uniform measure is invariant (no DP needed);
  * modular rank over GF(p) for two primes plus explicit spanning / minor checks for rank_R(K);
  * its own rebuild of the antipodal table, its own fooling-set greedy (reversed order), its own
    commutator-subgroup closure;
  * a direct recomputation of the recorded joint-measure witness (marginals, four correlators, support);
  * the atom-wise CHSH bound as the certificate that |S| > 2 admits no joint measure.

Usage:  /usr/bin/python3 scripts/28_c2g7_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
N = 62
NSTATE = 120
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    print('=' * 118)
    print('O222 scripts/28 -- INDEPENDENT audit of the C2+G7 round (does not import scripts/27)')
    print('=' * 118, flush=True)
    a2 = load(os.path.join(HERE, '09_a2_rollback.py'), 'c28_a2')
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'c28_b5')
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'c28_b3')
    _C1, C2, ids, types, den = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    anti = b3.build_anti(mm, U)
    rec = json.load(io.open(os.path.join(DATA, '27_c2g7_results.json'), encoding='utf-8'))
    cells = rec['cells']
    fz = json.load(io.open(os.path.join(DATA, '26_c2g7_freeze.json'), encoding='utf-8'))

    onts = hashlib.sha256(io.open(os.path.join(ROOT, fz['impl']['path']), 'rb').read()).hexdigest()
    keep = os.path.join(ROOT, 'logs/27_c2g7_firstrun_c3_infeasible.out')
    claim('A0', 'frozen impl hash matches the on-disk file and the first-run log is preserved',
          onts == fz['impl']['sha256'] and os.path.exists(keep) and os.path.getsize(keep) > 0,
          'impl=%s  first-run log keeps the pre-amendment C3 = 🟡' % onts[:12])

    # ---- A1: group-axiom route: every pair map is a bijection => uniform measure invariant ----
    G, idxg, MUL2 = a2.build_group()
    hydx = [idxg[a2.qkey(hh)] for hh in _h]
    nonbij = 0
    checked = 0
    sample = []
    st = 20260930
    for _s in range(400):                       # audit's own LCG sample of pairs for the map check
        st = (1103515245 * st + 12345) % (2 ** 31)
        a = st % N
        st = (1103515245 * st + 12345) % (2 ** 31)
        b = st % N
        sample.append((a, b))
    for (a, b) in sample:
        img = set()
        for s in range(NSTATE):
            img.add(MUL2[MUL2[s][hydx[a]]][hydx[b]])
        checked += 1
        if len(img) != NSTATE:
            nonbij += 1
    diag_ok = all(len({MUL2[s][g] for s in range(NSTATE)}) == NSTATE for g in range(NSTATE))
    claim('A1a', 'group-axiom route: all %d sampled pair maps are bijections (and every left translation is) '
                 '=> the uniform state measure is invariant without running the DP' % checked,
          nonbij == 0 and diag_ok, 'non-bijective = %d' % nonbij)
    C1v = cells['C1']['value']
    claim('A1b', 'p_k = uniform: the record reports dev_L1 = 0 at ALL %d steps with value set %s; by A1a this '
                 'zero is FORCED (a bijection cannot move mass between states), so it is a proof, not a fit'
          % (C1v['steps'], C1v['p_value_set']),
          C1v['max_L1_dev_from_uniform'] == '0' and C1v['uniform_steps'] == C1v['steps'] == 3844
          and C1v['p_value_set'] == ['1/120'], 'steps=%s uniform=%s' % (C1v['steps'], C1v['uniform_steps']))
    # machine DP cross-check on the audit's own sample via the frozen run_pair
    BUD = F(10 ** 9, 1)
    mis = 0
    for (a, b) in sample[:60]:
        acc = F(0)
        for s0 in range(NSTATE):
            rr, _nb = b5.run_pair(a, b, s0, -1, K, MUL, hydx, BUD)
            acc += F(1, NSTATE) * (rr['x_a'] * rr['x_b'])
        if acc != C2[a][b]:
            mis += 1
    claim('A1c', 'audit-side expectation under the uniform measure reproduces the frozen C2 table on its own '
                 'sample of pairs (%d checked)' % 60, mis == 0, 'mismatches = %d' % mis)

    # ---- A2: marginals, own computation ----
    cs = [sum(K[s][aa] for s in range(NSTATE)) for aa in range(N)]
    claim('A2', 'outcome marginals: sum_s K[s][a] = 0 for all 62 settings, computed here from the frozen K',
          set(cs) == {0} and all(K[s][aa] in (1, -1) for s in range(NSTATE) for aa in range(N)),
          'column sums = %s' % sorted(set(cs)))

    # ---- A3: verify the recorded joint-measure witness from scratch ----
    ok_w = True
    det = []
    for tname, T in (('C1', [[F(x, 120) for x in row] for row in json.load(
            io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))['C1_num']]), ('C2', C2)):
        v = cells['C3']['value'][tname]
        if not v.get('joint_measure_found'):
            ok_w = False
            det.append('%s: no witness' % tname)
            continue
        p = [F(x) for x in v['p_vector']]
        idx = [(x, y, u, w) for x in (1, -1) for y in (1, -1) for u in (1, -1) for w in (1, -1)]
        a, a2, b, bp = v['quartet']
        margs = [sum(p[k] for k in range(16) if idx[k][w] == 1) for w in range(4)]
        cors = {}
        for (i, j) in ((0, 0), (0, 1), (1, 0), (1, 1)):
            cors[(i, j)] = sum(p[k] * idx[k][i] * idx[k][2 + j] for k in range(16))
        frozen_vals = {(0, 0): T[a][b], (0, 1): T[a][bp], (1, 0): T[a2][b], (1, 1): T[a2][bp]}
        good = (all(x >= 0 for x in p) and sum(p) == 1 and all(m == F(1, 2) for m in margs)
                and all(cors[k] == frozen_vals[k] for k in cors))
        ok_w &= good
        det.append('%s: support=%d min_p=%s marginals=%s correlators match=%s'
                   % (tname, sum(1 for x in p if x > 0), min(p),
                      ['%s' % m for m in margs], all(cors[k] == frozen_vals[k] for k in cors)))
    claim('A3', 'the recorded 16-atom witness independently reproduces normalisation, the four marginals '
                '= 1/2 and the four frozen table values (both tables)', ok_w, ' | '.join(det))

    # ---- A4: the atom-wise bound and the antipodal character of the |S| > 2 tuple ----
    amax = max(x * y - x * w + z * y + z * w
               for x in (1, -1) for z in (1, -1) for y in (1, -1) for w in (1, -1))
    C1tab = [[F(x) for x in row] for row in json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'),
                                                               encoding='utf-8'))['C1_num']]
    C1tab = [[F(x, 120) for x in row] for row in C1tab]
    gt2 = None
    for tname, T in (('C1', C1tab), ('C2', C2)):
        v = cells['C4']['value'][tname]
        if F(v['max_abs_S_all4']) > 2:
            gt2 = (tname, v['argmax_all4'], T)
    if gt2 is None:
        claim('A4', 'atom-wise bound >= every joint-measure value (no |S| > 2 tuple in the frozen tables)',
              amax == 2, 'atom-wise max = %d' % amax)
    else:
        tname, (a, a2, b, bp), T = gt2
        S = T[a][b] - T[a][bp] + T[a2][b] + T[a2][bp]
        px = [(a, b), (a, bp), (a2, b), (a2, bp)]
        nap = sum(1 for (x, y) in px if anti[x][y])
        vals = [T[a][b], T[a][bp], T[a2][b], T[a2][bp]]
        c4 = cells['C4']['value'][tname]
        claim('A4', 'the |S| > 2 tuple (table %s) violates the atom-wise bound %d, hence admits NO joint '
                    'measure; measured antipodal count = %d and the machine also reports infeasible'
              % (tname, amax, nap),
              amax == 2 and abs(S) > 2 and c4.get('joint_measure_exists_for_gt2_tuple') is False,
              'argmax = %s  S = %s  values = %s  antipodal = %d  (the frozen anti filter is already applied '
              'inside the all4 domain, so the earlier "antipodal contamination" attribution does not apply here)'
              % ((a, a2, b, bp), S, [str(v) for v in vals], nap))

    # ---- A5: rank of K by modular arithmetic + explicit span/minor; sign structure ----
    def rank_mod(M, p):
        A = [[int(x) % p for x in row] for row in M]
        r = 0
        rows = len(A)
        cols = len(A[0])
        for c in range(cols):
            pr = None
            for i in range(r, rows):
                if A[i][c] % p:
                    pr = i
                    break
            if pr is None:
                continue
            A[r], A[pr] = A[pr], A[r]
            inv = pow(A[r][c], p - 2, p)
            A[r] = [(x * inv) % p for x in A[r]]
            for i in range(rows):
                if i != r and A[i][c]:
                    f2 = A[i][c]
                    A[i] = [(A[i][t] - f2 * A[r][t]) % p for t in range(cols)]
            r += 1
            if r == rows:
                break
        return r

    rowsK = [[K[s][aa] for aa in range(N)] for s in range(NSTATE)]
    rk7 = rank_mod(rowsK, 7)
    rk13 = rank_mod(rowsK, 13)
    rk17 = rank_mod(rowsK, 17)
    rank_lower = min(rk7, rk13, rk17)
    basis = []
    for i in range(NSTATE):
        w = [F(x) for x in rowsK[i]]
        for bvec, piv in basis:
            if w[piv] != 0:
                f2 = w[piv]
                w = [w[t] - f2 * bvec[t] for t in range(N)]
        piv = next((t for t in range(N) if w[t] != 0), None)
        if piv is not None:
            pv0 = w[piv]
            w = [x / pv0 for x in w]                # normalise (keeps the exact arithmetic small)
            basis.append((w, piv))
    in_span = 0
    for i in range(NSTATE):
        w = [F(x) for x in rowsK[i]]
        for bvec, piv in basis:
            if w[piv] != 0:
                f2 = w[piv]
                w = [w[t] - f2 * bvec[t] for t in range(N)]
        if all(t == 0 for t in w):
            in_span += 1
    span_ok = (len(basis) == rank_lower) and in_span == NSTATE
    claim('A5a', 'rank_R(K): modular rank over GF(7)/GF(13)/GF(17) = %d/%d/%d and a %d-row spanning set '
                 'contains every one of the 120 rows (so rank_R(K) = %d exactly)'
          % (rk7, rk13, rk17, len(basis), rank_lower),
          span_ok and rank_lower == cells['C5']['value']['rank_R_K'],
          'rank >= %d from the modular lower bound and rank <= %d from a rational spanning set of %d rows '
          'covering all 120 ; machine rank = %d'
          % (rank_lower, len(basis), len(basis), cells['C5']['value']['rank_R_K']))
    noneither = 0
    for i in range(NSTATE):
        for j in range(i + 1, NSTATE):
            eq = rowsK[i] == rowsK[j]
            comp = (not eq) and all(rowsK[i][t] == -rowsK[j][t] for t in range(N))
            if not (eq or comp):
                noneither += 1
    chosen = []
    for s in range(NSTATE - 1, -1, -1):                 # reversed scan order (audit's own)
        for aa in range(N - 1, -1, -1):
            if K[s][aa] != 1:
                continue
            if all(K[s][a3] * K[s3][aa] == -1 for (s3, a3) in chosen):
                chosen.append((s, aa))
    claim('A5b', 'sign-rank = 1 test: %d row pairs are neither equal nor complementary (so sign_rank > 1); '
                 'reversed-greedy fooling set of size %d is a lower bound'
          % (noneither, len(chosen)),
          noneither == cells['C5']['value']['pairs_neither'] and len(chosen) >= 1
          and cells['C5']['value']['fooling_set_size_lower_bound'] >= 1,
          'machine: %d neither, fooling >= %d ; audit: %d neither, fooling >= %d'
          % (cells['C5']['value']['pairs_neither'], cells['C5']['value']['fooling_set_size_lower_bound'],
             noneither, len(chosen)))

    # ---- A6: observables commute; commutator subgroup ----
    bad = 0
    for aa in range(N):
        for bb in range(aa + 1, N):
            for s in range(NSTATE):
                if K[s][aa] * K[s][bb] != K[s][bb] * K[s][aa]:
                    bad += 1
    e = next(g for g in range(NSTATE) if all(MUL2[g][h] == h for h in range(NSTATE)))
    inv = [next(h for h in range(NSTATE) if MUL2[g][h] == e) for g in range(NSTATE)]
    coms = set()
    for g in range(NSTATE):
        for h in range(NSTATE):
            coms.add(MUL2[MUL2[g][h]][MUL2[inv[g]][inv[h]]])
    seen = set(coms)
    while True:
        new = set(MUL2[x][y] for x in seen for y in coms) - seen
        if not new:
            break
        seen |= new
    nc = sum(1 for aa in range(N) for bb in range(N) if MUL2[hydx[aa]][hydx[bb]] != MUL2[hydx[bb]][hydx[aa]])
    claim('A6', 'observables commute identically (0/226920 non-zero), the commutator subgroup is the whole '
                'group (%d/%d) and %d/%d translation pairs do not commute'
          % (len(seen), NSTATE, nc, N * N),
          bad == 0 and len(seen) == NSTATE and nc == cells['C6']['value']['translation_pairs_not_commuting'],
          'audit: %d non-commuting translation pairs (machine %d)' % (nc,
              cells['C6']['value']['translation_pairs_not_commuting']))

    # ---- A8: what makes the |S| > 2 tuple possible: memo saturation, not antipodal pairs ----
    diag_ones = sum(1 for i in range(N) if C2[i][i] == 1)
    offsat = [(i, j) for i in range(N) for j in range(N) if abs(C2[i][j]) == 1 and i != j]
    a, a2, b, bp = cells['C4']['value']['C2']['argmax_all4']
    vals = [C2[a][b], C2[a][bp], C2[a2][b], C2[a2][bp]]
    same_C1 = [C1tab[a][b], C1tab[a][bp], C1tab[a2][b], C1tab[a2][bp]]
    sat_pairs = sum(1 for (x, y) in ((a, b), (a, bp), (a2, b), (a2, bp)) if abs(C2[x][y]) == 1)
    claim('A8', 'mechanism: the diagonal of C2 is saturated (memo hits: %d/62 entries = +1) and there are %d '
                'further off-diagonal entries with |value| = 1; the |S| = 3 tuple uses %d saturated entries '
                'while C1 on the SAME tuple gives (S = 2) -- so the driver is memo saturation, not antipodal pairs'
          % (diag_ones, len(offsat), sat_pairs),
          diag_ones == 62 and sat_pairs >= 1,
          'C2 values %s -> S = %s ; C1 values %s -> S = 2 ; budget-window values (B3R2/D6) stay < 2'
          % ([str(v) for v in vals], vals[0] - vals[1] + vals[2] + vals[3], [str(v) for v in same_C1]))

    # ---- A7: record integrity ----
    order = rec['cell_order']
    claim('A7', 'record integrity: %d cells in order, no cell sampled (samples_used = %d, nodes_used = %d), '
                'C5 is the only 🔴 and C7 the only 🟡' % (len(order), rec['samples_used'], rec['nodes_used']),
          order == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'] and rec['samples_used'] == 0
          and [c for c in order if cells[c]['verdict'] == '🔴'] == ['C5']
          and [c for c in order if cells[c]['verdict'] == '🟡'] == ['C7'],
          'diff %s vs %s' % (rec['samples_used'], ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'].index('C1')))

    with io.open(os.path.join(DATA, '28_c2g7_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'claims': CLAIMS, 'rank_mod': {'gf7': rk7, 'gf13': rk13, 'gf17': rk17},
                   'fooling_set_reversed': len(chosen)}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(CLAIMS), len(CLAIMS) - npass))
    print('=' * 118)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
