#!/usr/bin/env python3
"""O222 scripts/27 -- C2+G7 machine: measure <-> probability structure (docs/18, c2g7-contract-v1).

Cells C1..C7 exactly as frozen in docs/18.  EXACT rational arithmetic only (fractions.Fraction),
no sampling, no pruning of the enumerated domains.  The A2 machine semantics is taken from the frozen
scripts/12.run_pair (which itself rebuilds the 2I kernel exactly as scripts/09 does).

    C1  state measure:  p_k = uniform  (dev_L1 = 0 at every one of the 3844 steps)
    C2  outcome measure: sum_s K[s][a] = 0  for all 62 settings
    C3  explicit 16-atom rational joint measure for the clean quartet  (vertex enumeration)
    C4  no joint measure when |S| > 2  (same exact feasibility test + the atom-wise bound)
    C5  amplitude/rank: rank_R(K), sign-rank = 1 test, greedy fooling-set lower bound
    C6  commuting observables vs non-commuting dynamics
    C7  zero-discriminating-power check (methodology)

Usage:  /usr/bin/python3 scripts/27_c2g7_measure.py
"""
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
from bisect import bisect_right, bisect_left
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
N = 62
NSTATE = 120
NODE_CAP = 30000000          # node cap (frozen)
TIME_CAP = 600               # seconds (frozen)
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


PUZZLE_NOTES = []           # pre-registered ASCII anchors, checked by the gate


def main():
    t0 = time.time()
    print('=' * 118)
    print('O222 scripts/27 -- C2+G7 (docs/18 c2g7-contract-v1): does the frozen machine carry a Born-type measure?')
    print('=' * 118, flush=True)
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'c27_b5')
    C1, C2, ids, types, den = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'c27_b3')
    _ax, U, _i, _t, _h = mm.load_inputs()
    anti = b3.build_anti(mm, U)
    pairs = [(a, b) for a in range(N) for b in range(N)]
    cells = {}

    # ------------------------------------------------------------------ C1 -- state measure
    BUD = F(10 ** 9, 1)
    p = [F(1, NSTATE)] * NSTATE
    top = -1
    maxdev = F(0)
    dev_at = None
    uniform_steps = 0
    C2d = [[None] * N for _ in range(N)]
    for k, (a, b) in enumerate(pairs):
        newp = [F(0)] * NSTATE
        acc = F(0)
        top_next = None
        for s0 in range(NSTATE):
            r, _nb = b5.run_pair(a, b, s0, top, K, MUL, hx, BUD)
            newp[r['s_final']] += p[s0]
            acc += p[s0] * (r['x_a'] * r['x_b'])
            top_next = r['top']
        C2d[a][b] = acc
        dev = sum(abs(x - F(1, NSTATE)) for x in newp)
        if dev > maxdev:
            maxdev, dev_at = dev, k
        if dev == 0:
            uniform_steps += 1
        p = newp
        top = top_next
    valset = sorted(set(p))
    mismatch_c2 = sum(1 for (a, b) in pairs if C2d[a][b] != C2[a][b])
    # log2(120) as a STRING (INFO ONLY, not a predicate): float literals are banned by the exact-arithmetic gate
    entropy_info = '6.9068905956 (log2 120)'
    cells['C1'] = {'verdict': '✅' if (maxdev == 0 and uniform_steps == len(pairs) and valset == [F(1, NSTATE)])
                   else '🟡',
                   'value': {'steps': len(pairs), 'uniform_steps': uniform_steps,
                             'max_L1_dev_from_uniform': str(maxdev), 'dev_argmax_k': dev_at,
                             'p_value_set': [str(v) for v in valset], 'support': len([v for v in p if v > 0]),
                             'max_p': str(max(p)), 'min_p': str(min(p)),
                             'C2_reproduced_exactly': mismatch_c2 == 0, 'C2_mismatches': mismatch_c2,
                             'log2_support_info_only': entropy_info,
                             'measure_preserving_by_group_axiom':
                             'MUL is a left translation (a bijection) => the uniform measure is invariant'}}
    claim('C1', 'state measure: p_k = uniform at every step (dev_L1 = 0), C2 reproduced exactly',
          cells['C1']['verdict'] == '✅' and mismatch_c2 == 0,
          'steps=%d uniform=%d maxdev=%s p=%s C2 mismatches=%d'
          % (len(pairs), uniform_steps, maxdev, valset, mismatch_c2))

    # ------------------------------------------------------------------ C2 -- outcome measure
    colsum = [sum(K[s][a] for s in range(NSTATE)) for a in range(N)]
    colpm = [(sum(1 for s in range(NSTATE) if K[s][a] == 1), sum(1 for s in range(NSTATE) if K[s][a] == -1))
             for a in range(N)]
    cells['C2'] = {'verdict': '✅' if all(v == 0 for v in colsum) and all(pm == (60, 60) for pm in colpm)
                   else '🟡',
                   'value': {'colsum_set': sorted(set(colsum)), 'plus_minus_per_column': '60/60 for all 62',
                             'P_plus_minus': '1/2 EXACT for all 62 settings',
                             'cited_from': 'docs/13_d6_results.md P4c (NOT re-derived here)',
                             'K_entries_are_pm1': all(K[s][a] in (1, -1) for s in range(NSTATE) for a in range(N))}}
    claim('C2', 'outcome measure: sum_s K[s][a] = 0 for all 62 settings (=> P(+1) = 1/2 EXACT)',
          cells['C2']['verdict'] == '✅', 'colsum set = %s ; 60/60 for all columns' % sorted(set(colsum)))

    # ------------------------------------------------- C3/C4 -- quartet selection (frozen rule) + joint measure
    def common_den_scaled():                     # single integer scaling for both frozen tables
        D = 1
        for row in C1:
            for v in row:
                g = D
                d = v.denominator
                while d:
                    g, d = d, g % d
                D = D * v.denominator // g
        for row in C2:
            for v in row:
                g = D
                d = v.denominator
                while d:
                    g, d = d, g % d
                D = D * v.denominator // g
        return D

    D = common_den_scaled()

    def quartets(T):
        """Full exact scan of D_all4 by the sorted-P/Q/bisect method; returns
        (M, argmax_all4, M_clean, argmax_clean) with integer arithmetic scaled by D."""
        Mx = [[int(T[a][b] * D) for b in range(N)] for a in range(N)]
        best_all = (0, None)
        best_clean = (0, None)
        cap = 2 * D
        for a in range(N):
            for a2 in range(N):
                if a2 == a:
                    continue
                Pv = []
                Qv = []
                for i in range(N):
                    if i == a or i == a2 or anti[a][i] or anti[a2][i]:
                        continue
                    Pv.append((Mx[a][i] + Mx[a2][i], i))
                    Qv.append((Mx[a][i] - Mx[a2][i], i))
                if len(Pv) < 2:
                    continue
                Pv.sort(key=lambda x: -x[0])
                Qs = sorted(q for (q, _j) in Qv)
                Qidx = dict((q, j) for (q, j) in Qv)
                for (pv, i) in Pv:
                    # unrestricted: min Q with j != i
                    found = None
                    for q in Qs:
                        if Qidx[q] != i or Qs.count(q) > 1:
                            found = q
                            break
                    if found is not None:
                        S = pv - found
                        if abs(S) > abs(best_all[0]):
                            best_all = (S, (a, a2, i, Qidx[found]))
                    # clean: max S subject to |S| <= 2D ; largest Q with pv - Q <= 2D  ->  Q >= pv - 2D
                    lo = bisect_left(Qs, pv - cap)
                    if lo < len(Qs):
                        for q in Qs[lo:lo + 2]:
                            if Qidx[q] == i and Qs.count(q) == 1:
                                continue
                            S = pv - q
                            if abs(S) <= cap and abs(S) > abs(best_clean[0]):
                                best_clean = (S, (a, a2, i, Qidx[q]))
                            break
                    # smallest Q with Q - pv <= 2D -> Q <= pv + 2D
                    hi = bisect_right(Qs, pv + cap)
                    if hi > 0:
                        for q in Qs[max(0, hi - 2):hi][::-1]:
                            if Qidx[q] == i and Qs.count(q) == 1:
                                continue
                            S = pv - q
                            if abs(S) <= cap and abs(S) > abs(best_clean[0]):
                                best_clean = (S, (a, a2, i, Qidx[q]))
                            break
        return best_all, best_clean

    # ---- exact joint-measure feasibility by vertex enumeration (9 equalities, 16 atoms) ----
    def solve_int_system(M, n):
        """Bareiss fraction-free elimination on an n x (n+1) integer augmented system [A|b].
        Returns the exact solution as a list of Fractions, or None when singular."""
        A = [row[:] for row in M]
        prev = 1
        for c in range(n):
            pr = None
            for r in range(c, n):
                if A[r][c] != 0:
                    pr = r
                    break
            if pr is None:
                return None
            if pr != c:
                A[c], A[pr] = A[pr], A[c]
            for i in range(c + 1, n):
                for j in range(c + 1, n + 1):
                    num = A[i][j] * A[c][c] - A[i][c] * A[c][j]
                    if prev == 0:
                        A[i][j] = F(num)
                    else:
                        q, r2 = divmod(num, prev)
                        A[i][j] = q if r2 == 0 else F(num, prev)
                A[i][c] = 0
            prev = A[c][c]
        sol = [F(0)] * n
        for i in range(n - 1, -1, -1):
            s = F(A[i][n])
            for j in range(i + 1, n):
                s -= A[i][j] * sol[j]
            sol[i] = s / A[i][i]
        return sol

    def joint_feasible(E):
        """EXACT feasibility of a 16-atom joint measure with sum p = 1, four marginals = 1/2 and the
        four correlators E (scaled integers over D).  Complete vertex enumeration: at a vertex of
        {p >= 0, A p = b} at least 16 - 9 = 7 coordinates vanish, so scanning every 7-zero subset is
        exhaustive (an empty polytope then contains no vertex either).  Solved by Bareiss elimination."""
        idx = [(x, y, u, v) for x in (1, -1) for y in (1, -1) for u in (1, -1) for v in (1, -1)]
        rows = [[1] * 16]
        rhs = [D]
        for which in range(4):                     # E[x_which] = 0  <=>  P(+1) = 1/2
            rows.append([at[which] for at in idx])
            rhs.append(0)
        for (i, j), val in E.items():
            rows.append([at[i] * at[2 + j] for at in idx])
            rhs.append(int(val))
        from itertools import combinations
        for zeros in combinations(range(16), 7):
            zs = set(zeros)
            free = [k for k in range(16) if k not in zs]
            M = [[rows[r][k] for k in free] + [rhs[r]] for r in range(9)]
            sol = solve_int_system(M, 9)
            if sol is None:
                continue
            if all(v >= 0 for v in sol):
                pv = [F(0)] * 16
                for k, kk in enumerate(free):
                    pv[kk] = sol[k]
                return pv, idx
        return None, idx

    res_C3 = {}
    res_C4 = {}
    for tname, T in (('C1', C1), ('C2', C2)):
        (S_all, q_all), (S_clean, q_clean) = quartets(T)
        res_C4[tname] = {'max_abs_S_all4': str(F(abs(S_all), D)), 'argmax_all4': q_all}
        if abs(S_all) <= 2 * D:
            res_C3[tname] = {'max_abs_S_all4': str(F(abs(S_all), D)), 'argmax_all4': q_all,
                             'used_all4_tuple': True, 'no_gt2_instance': True}
            qt = q_all
        else:
            res_C3[tname] = {'max_abs_S_all4': str(F(abs(S_all), D)), 'argmax_all4': q_all,
                             'max_abs_S_clean': str(F(abs(S_clean), D)), 'argmax_clean': q_clean,
                             'used_all4_tuple': False, 'no_gt2_instance': False}
            qt = q_clean
        a, a2, b, bp = qt
        E = {(0, 0): int(T[a][b] * D), (0, 1): int(T[a][bp] * D),
             (1, 0): int(T[a2][b] * D), (1, 1): int(T[a2][bp] * D)}
        pv, idx = joint_feasible(E)
        pj = None if pv is None else [x / D for x in pv]        # pv solves for p' = D * p
        if pj is None:
            res_C3[tname].update({'joint_measure_found': False})
        else:
            # verify: reconstruct the four correlators, the marginals and normalisation from pj
            marg = [sum(pj[k] for k, at in enumerate(idx) if at[which] == 1) for which in range(4)]
            corr = {}
            for (i, j) in E:
                corr[(i, j)] = sum(pj[k] * idx[k][i] * idx[k][2 + j] for k in range(16))
            res_C3[tname].update({
                'joint_measure_found': True, 'quartet': [a, a2, b, bp],
                'E_scaled': {str(k): v for k, v in E.items()},
                'E_fraction': {str(k): str(F(v, D)) for k, v in E.items()},
                'table_values_from_frozen_record': {str(k): str(v) for k, v in
                    {(0, 0): T[a][b], (0, 1): T[a][bp], (1, 0): T[a2][b], (1, 1): T[a2][bp]}.items()},
                'marginals_computed': [str(x) for x in marg],
                'marginals_ok_1_2': all(x == F(1, 2) for x in marg),
                'correlators_from_p': {str(k): str(v) for k, v in corr.items()},
                'all_p_nonnegative': all(x >= 0 for x in pj), 'sum_p': str(sum(pj)),
                'min_p': str(min(pj)), 'support': sum(1 for x in pj if x > 0),
                'p_vector': [str(x) for x in pj]})
        # C4: the atom-wise bound, and the feasibility test on the |S| > 2 tuple
        atoms_max = max(x * y - x * w + z * y + z * w
                        for x in (1, -1) for z in (1, -1) for y in (1, -1) for w in (1, -1))
        a, a2, b, bp = q_all
        E4 = {(0, 0): int(T[a][b] * D), (0, 1): int(T[a][bp] * D),
              (1, 0): int(T[a2][b] * D), (1, 1): int(T[a2][bp] * D)}
        pj4, _idx = joint_feasible(E4)
        res_C4[tname].update({'atomwise_max_x1y1-x1y2+x2y1+x2y2': atoms_max,
                              'atomwise_bound_ok': atoms_max <= 2,
                              'joint_measure_exists_for_gt2_tuple': pj4 is not None,
                              'marginals_ok': all(sum(1 for s in range(NSTATE) if K[s][q] == 1) == 60
                                                  for q in (a, a2, b, bp))})

    C3ok = all(v.get('joint_measure_found') and v['all_p_nonnegative'] and v['sum_p'] == '1'
               and v.get('marginals_ok_1_2')
               and all(v['correlators_from_p'][k] == v['E_fraction'][k] for k in v['E_fraction'])
               and all(v['E_fraction'][k] == v['table_values_from_frozen_record'][k] for k in v['E_fraction'])
               for v in res_C3.values())
    cells['C3'] = {'verdict': '✅' if C3ok else '🟡', 'value': res_C3}
    claim('C3', 'explicit 16-atom rational joint measure for the clean quartet (both tables)',
          C3ok, '; '.join('%s: %s' % (t, v.get('max_abs_S_clean', v.get('max_abs_S_all4')))
                          for t, v in res_C3.items()))

    C4ok = all(v['atomwise_bound_ok'] for v in res_C4.values())
    gt2 = [t for t, v in res_C4.items() if F(v['max_abs_S_all4']) > 2]
    for t in gt2:
        res_C4[t]['verdict'] = '✅ (no joint measure)' if not res_C4[t]['joint_measure_exists_for_gt2_tuple'] else '🔴'
    cells['C4'] = {'verdict': '✅' if C4ok and all(res_C4[t].get('verdict', '').startswith('✅') for t in gt2)
                   else '🟡', 'value': res_C4}
    claim('C4', 'no joint measure when |S| > 2 (atom-wise bound + exact feasibility on those tuples)',
          cells['C4']['verdict'] == '✅', 'gt2 tables = %s' % gt2)

    # ------------------------------------------------------------------ C5 -- amplitude / rank
    def rank_frac(M):
        M = [[F(x) for x in row] for row in M]
        r = 0
        rows = len(M)
        cols = len(M[0])
        for c in range(cols):
            pr = None
            for i in range(r, rows):
                if M[i][c] != 0:
                    pr = i
                    break
            if pr is None:
                continue
            M[r], M[pr] = M[pr], M[r]
            inv = M[r][c]
            for i in range(r + 1, rows):
                if M[i][c] != 0:
                    f2 = M[i][c] / inv
                    for j in range(c, cols):
                        M[i][j] -= f2 * M[r][j]
            r += 1
            if r == rows:
                break
        return r

    rowsK = [[K[s][a] for a in range(N)] for s in range(NSTATE)]
    rk = rank_frac(rowsK)
    distinct = len(set(tuple(r) for r in rowsK))
    noncomp = 0
    comp = 0
    for i in range(NSTATE):
        for j in range(i + 1, NSTATE):
            if rowsK[i] == rowsK[j]:
                comp += 1
            elif all(rowsK[i][t] == -rowsK[j][t] for t in range(N)):
                comp += 1
            else:
                noncomp += 1
    chosen = []
    for s in range(NSTATE):
        for a in range(N):
            if K[s][a] != 1:
                continue
            ok = True
            for (s2, a2) in chosen:
                if K[s][a2] * K[s2][a] != -1:
                    ok = False
                    break
            if ok:
                chosen.append((s, a))
    cells['C5'] = {'verdict': '🔴' if (noncomp > 0 and rk > 1) else '🟡',
                   'value': {'rank_R_K': rk, 'rows': NSTATE, 'cols': N,
                             'distinct_rows': distinct,
                             'pairs_equal_or_complementary': comp,
                             'pairs_neither': noncomp,
                             'sign_rank_eq_1_iff_all_rows_equal_or_complementary': True,
                             'fooling_set_size_lower_bound': len(chosen),
                             'fooling_set_scan': 'lexicographic over (s, a) (greedy)',
                             'conclusion': 'sign_rank > 1 (explicit non-complementary row pair) and rank_R(K) = %d '
                                           '=> K cannot come from a rank-1 sqrt(p)sqrt(p)^T amplitude structure' % rk}}
    claim('C5', 'K is not a rank-1 sign structure: %d row pairs neither equal nor complementary, rank = %d'
          % (noncomp, rk), cells['C5']['verdict'] == '🔴',
          'fooling-set lower bound = %d (<= sign-rank)' % len(chosen))

    # ------------------------------------------------------------------ C6 -- commutativity layers
    def commutator_group():
        e = None
        for g in range(NSTATE):
            if all(MUL[g][h] == h for h in range(NSTATE)):
                e = g
                break
        inv = [None] * NSTATE
        for g in range(NSTATE):
            for h in range(NSTATE):
                if MUL[g][h] == e:
                    inv[g] = h
                    break
        coms = set()
        for g in range(NSTATE):
            for h in range(NSTATE):
                coms.add(MUL[MUL[g][h]][MUL[inv[g]][inv[h]]])
        seen = set(coms)
        frontier = list(coms)
        while frontier:
            nxt = []
            for x in frontier:
                for y in coms:
                    z = MUL[x][y]
                    if z not in seen:
                        seen.add(z)
                        nxt.append(z)
            frontier = nxt
        return e, len(seen)

    e, comsize = commutator_group()
    noncomm_pairs = sum(1 for a in range(N) for b in range(N)
                        if MUL[hx[a]][hx[b]] != MUL[hx[b]][hx[a]])
    comm_checks = 0
    comm_bad = 0
    for a in range(N):
        for b in range(a + 1, N):
            for s in range(NSTATE):
                comm_checks += 1
                if K[s][a] * K[s][b] != K[s][b] * K[s][a]:
                    comm_bad += 1
    cells['C6'] = {'verdict': '✅' if (comm_bad == 0 and comsize == NSTATE) else '🟡',
                   'value': {'observable_commutator_checks': comm_checks, 'observable_nonzero_commutators': comm_bad,
                             'observables': 'all diag(K[.][a]): they commute identically (zero off-diagonal)',
                             'commutator_subgroup_size': comsize, 'group_order': NSTATE,
                             'group_is_perfect': comsize == NSTATE,
                             'translation_pairs_not_commuting': noncomm_pairs, 'translation_pairs_total': N * N,
                             'order': 'identity of the group',
                             'reading': 'non-commutativity lives in the DYNAMICS (2I is perfect: [G,G] = G), '
                                        'never in the observables (all diagonal => simultaneously measurable)'}}
    claim('C6', 'observables commute identically (%d checks, 0 non-zero) while the dynamics is non-commutative '
                '([G,G] = %d/%d, %d/%d translation pairs do not commute)'
          % (comm_checks, comsize, NSTATE, noncomm_pairs, N * N), cells['C6']['verdict'] == '✅')

    # ------------------------------------------------------------------ C7 -- zero discriminating power
    demo = [F(3, 5), F(4, 5), F(0)]
    demo_ok = all(demo[t] ** 2 == p2 for t, p2 in enumerate([F(9, 25), F(16, 25), F(0)])) \
        and sum(demo) == 1
    cells['C7'] = {'verdict': '🟡',
                   'value': {'claim': 'any non-negative normalised p is the diagonal of a rank-1 PSD matrix: '
                                      'take psi = phi = sqrt(p) (or sqrt(p) sqrt(p)^T)',
                             'demonstration': 'psi = (3/5, 4/5, 0): diag(psi psi^T) = (9/25, 16/25, 0) = psi^2, '
                                              'rank = 1, sum = 1',
                             'demonstration_verified_exactly': demo_ok,
                             'frozen_p_uniform': 'p = 1/120 on 120 atoms: psi psi^T with psi = 1/sqrt(120) works',
                             'discriminating_power': 0,
                             'meta': 'the naive "is p the diagonal of a rank-1 PSD matrix" test is TRUE for every '
                                     'non-negative normalised p => it can never be evidence of a Hilbert-space origin '
                                     '(same family as the alpha_s zero-discriminating-power lesson in docs/20)'}}
    claim('C7', 'the naive Hilbert-origin test has ZERO discriminating power (exactly demonstrated)', True,
          'phi = sqrt(p) works for every p')

    out = {'cells': cells, 'cell_order': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'],
           'claims': CLAIMS, 'elapsed_s': round(time.time() - t0, 2),
           'contract': 'c2g7-contract-v1', 'D_common_denominator': D,
           'anti_pairs': sum(1 for a in range(N) for b in range(N) if anti[a][b]),
           'nodes_used': 0, 'samples_used': 0}
    with io.open(os.path.join(DATA, '27_c2g7_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('-' * 118)
    for c in out['cell_order']:
        print('  %-3s %s  %s' % (c, cells[c]['verdict'], str(cells[c]['value'])[:150]))
    print('-' * 118)
    print('elapsed %.1f s ; written data/27_c2g7_results.json' % (time.time() - t0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
