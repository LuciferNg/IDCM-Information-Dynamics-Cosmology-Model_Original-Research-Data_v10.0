#!/usr/bin/env python3
"""O222 scripts/24 -- G5 machine: the rectangle criterion characterised (contract docs/16, g5-contract-v1).

No new semantics.  Everything comes from imported frozen objects:
  scripts/15 (the criterion feasible_chsh(mode='all4'), build_anti, order_list, simulate)
  scripts/12 (the machine run_pair / load_machine / load_a2)   scripts/21 (the frozen Hierholzer)

Cells
  P1  the exact criterion  c(a,a2) >= 2  versus the frozen brute-force enumeration, case by case --
      including an EXHAUSTIVE sweep over every pair set of size <= 5 on the first four settings
  P2  the necessary-condition ladder and the B3R2 corollary (injective prefix => not constructible)
  P3  the sufficient condition k >= 6 (from the anti perfect-matching lemma) and tightness of the bound
  P4  extremal: rz(3), rz(4), rz(5) by exhaustive search over 0-1 matrices, plus the KST upper bound
  P5  filter effect: raw rectangles versus filtered rectangles (k - c <= 4)
  P6  class-level prevalence: n = 4 exact (whole class), n = 5 exact if within the pre-registered caps
      else the frozen LCG sample, n = 62 the frozen LCG sample  -> verdict 🟡 whenever sampling is used

Usage:  /usr/bin/python3 scripts/24_g5_criterion.py
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
N = 62
RULES = 'g5-contract-v1'
CELLS = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')
LCG_A, LCG_C, LCG_M, LCG_SEED = 1103515245, 12345, 2 ** 31, 20260930
K_SAMPLE = 1000
L_BUDGET = min(21, N * (N - 1))        # frozen prefix rule: L = min(21, |E|)
# L_small = the pre-registered shorter prefix lengths for the degenerate small-n cases
L_SMALL = {4: 5, 5: 9}
NODE_CAP = 30000000
TIME_CAP = 600
P3_SCAN = 2000


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LCG(object):
    """hand-written LCG (the `random` module is banned by the contract's AST gate)."""
    def __init__(self, seed=LCG_SEED):
        self.x = seed

    def next(self):
        self.x = (LCG_A * self.x + LCG_C) % LCG_M
        return self.x

    def below(self, n):
        return self.next() % n


def isqrt_int(n):
    """integer square root (no math/sqrt: banned by the AST gate)."""
    if n < 0:
        raise ValueError
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def ai(x):
    """floor sqrt, as an integer."""
    return isqrt_int(x)


def cols_of(P):
    return sorted({b for (_a, b) in P})


def rows_of(P):
    return sorted({a for (a, _b) in P})


def crit_and_counts(P, anti):
    """returns (constructible_by_criterion, k_max, c_max, sum_k, sum_c, max_k_minus_c, argmax_pair)"""
    Pset = set(P)
    rows = rows_of(P)
    best_k = 0
    best_c = 0
    sk = 0
    sc = 0
    mkd = 0
    arg = None
    for ai_ in rows:
        for a2 in rows:
            if a2 <= ai_:
                continue
            shared = []
            for (x, q) in P:
                if x == ai_ and (a2, q) in Pset:
                    shared.append(q)
            if not shared:
                continue
            k = len(shared)
            c = 0
            for q in shared:
                if q == ai_ or q == a2:
                    continue
                if anti[ai_][q] or anti[a2][q]:
                    continue
                c += 1
            sk += k
            sc += c
            if k - c > mkd:
                mkd = k - c
            if k > best_k:
                best_k = k
                arg = (ai_, a2)
            if c > best_c:
                best_c = c
    return (best_c >= 2), best_k, best_c, sk, sc, mkd, arg


def brute(P, b3, M, den, ids, anti):
    v, arg, dom = b3.feasible_chsh(M, den, 'all4', set(P), anti, ids)
    return (v is not None), dom, arg


def walk_ok(edges):
    for i in range(len(edges) - 1):
        if edges[i][1] != edges[i + 1][0]:
            return False
    return True


def main():
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(200000)
    print('=' * 112)
    print('O222 scripts/24 -- G5: rectangle criterion characterised (rules %s)' % RULES)
    print('=' * 112, flush=True)
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g5m_b5')
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'g5m_b3')
    g4 = load(os.path.join(HERE, '21_g4_eulerian.py'), 'g5m_g4')
    C1f, C2f, ids, types, _d1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    anti = b3.build_anti(mm, U)
    den = 1
    for a in range(N):
        for b in range(N):
            d = F(C2f[a][b]).denominator
            g = den
            x, y = g, d
            while y:
                x, y = y, x % y
            den = den * d // x
    C2int = [[int(F(C2f[a][b]) * den) for b in range(N)] for a in range(N)]
    cells = {}
    budget = F(123, 2)

    # ---------------- the six known prefixes ----------------
    known = {}
    for oid in ('lex', 'diag', 'antidiag', 'block', 'stride'):
        p, _t, _b, _r = b3.simulate(b5, b3.order_list(oid), K, MUL, hx, budget, top=-1)
        known[oid] = set(p)
    out_adj = [sorted(j for j in range(N) if j != a) for a in range(N)]
    circuit = g4.hierholzer(N, out_adj, 0, first_edge=(0, 1))
    pcan, _t, _b, _r = b3.simulate(b5, circuit, K, MUL, hx, budget, top=-1)
    known['euler_canonical'] = set(pcan)
    rect = [(0, 2), (2, 1), (1, 3), (3, 0), (0, 3), (3, 1), (1, 2)]
    used = set(rect)
    cur = rect[-1][1]
    while len(rect) < len(pcan):
        for w in sorted(j for j in range(N) if j != cur):
            if (cur, w) not in used:
                rect.append((cur, w))
                used.add((cur, w))
                cur = w
                break
        else:
            break
    known['euler_rectangle'] = set(rect)

    # ---------------- P1: criterion vs brute force ----------------
    tests = []
    for k in sorted(known):
        tests.append((k, sorted(known[k])))
    # exhaustive: every pair set of size <= 5 on the first four settings (a 4x4 alphabet, loops included)
    alpha = list(range(4))
    small = [(a, b) for a in alpha for b in alpha]
    for s in range(0, 6):
        for comb in _combinations(small, s):
            tests.append(('synth4_%d_%d' % (s, len(tests)), list(comb)))
    p1_agree = 0
    p1_bad = []
    p1_constructible = 0
    for name, P in tests:
        if not P:
            crit = False
            bc = False
        else:
            crit = crit_and_counts(P, anti)[0]
            bc = brute(P, b3, C2int, den, ids, anti)[0]
        if crit == bc:
            p1_agree += 1
        elif len(p1_bad) < 8:
            p1_bad.append({'case': name, 'criterion': crit, 'brute': bc, 'P': [[ids[a], ids[b]] for a, b in P]})
        if bc:
            p1_constructible += 1
    p1_ok = not p1_bad
    cells['P1'] = {'verdict': '✅' if p1_ok else '🔴',
                   'value': {'cases': len(tests), 'agree': p1_agree, 'counterexamples': p1_bad,
                             'constructible_cases': p1_constructible,
                             'exhaustive_part': 'all pair sets of size <= 5 on 4 settings (loops included)',
                             'known_prefixes': sorted(known)},
                   'note': 'T1: constructible <=> exists a != a2 with c(a,a2) >= 2 ; tested case by case '
                           'against the frozen brute force'}

    # ---------------- P2: necessary conditions + B3R2 corollary ----------------
    p2_rows = []
    bad2 = []
    for name, P in tests:
        if not P:
            continue
        Pset = set(P)
        bc = brute(P, b3, C2int, den, ids, anti)[0]
        deg_out = {}
        deg_in = {}
        for (a, b) in Pset:
            deg_out[a] = deg_out.get(a, 0) + 1
            deg_in[b] = deg_in.get(b, 0) + 1
        mo = max(deg_out.values())
        mi = max(deg_in.values())
        checks = [len(Pset) >= 4, mo >= 2, mi >= 2]
        if bc and not all(checks):
            bad2.append({'case': name, 'sizes': [len(Pset), mo, mi]})
        if mo <= 1:
            if bc:
                bad2.append({'case': name, 'note': 'injective but constructible', 'P': P})
            p2_rows.append(name)
    cor = {}
    for f in ('diag', 'antidiag', 'stride'):
        P = sorted(known[f])
        deg_out = {}
        for (a, _b) in P:
            deg_out[a] = deg_out.get(a, 0) + 1
        cor[f] = {'max_deg_out': max(deg_out.values()), 'constructible': brute(P, b3, C2int, den, ids, anti)[0]}
    cor_ok = all(v['max_deg_out'] <= 1 and not v['constructible'] for v in cor.values())
    cells['P2'] = {'verdict': '✅' if (not bad2 and cor_ok) else '🔴',
                   'value': {'counterexamples': bad2, 'injective_prefixes_tested': p2_rows[:8],
                             'injective_count': len(p2_rows), 'b3r2_corollary': cor},
                   'note': 'T2: |P| >= 4, exists deg_out >= 2, exists deg_in >= 2 ; injective => not constructible '
                           '(B3R2 theorem becomes a corollary of the degree condition)'}

    # ---------------- P3: sufficient condition k >= 6 and tightness ----------------
    kc = []
    for name, P in tests:
        if not P:
            continue
        ok, bk, bc_, sk, sc, mkd, arg = crit_and_counts(P, anti)
        kc.append((bk, bc_, mkd))
    ge6 = [t for t in kc if t[0] >= 6]
    le1 = [t for t in kc if t[0] <= 1]
    maxkd = max([t[2] for t in kc] or [0])
    sat = all(t[1] >= 2 for t in ge6)
    tight = {}
    Pset_base = set()
    for kk in (2, 3, 4, 5):
        found_c = None
        found_n = None
        cand = _combinations([q for q in range(N)], kk)
        cnt = 0
        for Q in cand:
            cnt += 1
            if cnt > P3_SCAN:
                break
            P = [(0, q) for q in Q] + [(1, q) for q in Q]
            ok = crit_and_counts(P, anti)[0]
            if ok and found_c is None:
                found_c = list(Q)
            if (not ok) and found_n is None:
                found_n = list(Q)
            if found_c and found_n:
                break
        tight[kk] = {'constructible_instance': found_c, 'non_constructible_instance': found_n}
    # POSITIVE tests of the sufficient condition (the search set above contained no k >= 6 instance):
    ap = [next(b for b in range(N) if anti[a][b]) for a in range(N)]
    ge6_constructed = []
    for kk in (6, 8, 10, 12, 20):
        Q = list(range(2, 2 + kk))                       # avoids the self-exclusion columns {0,1}
        Pt = [(0, q) for q in Q] + [(1, q) for q in Q]
        ok_c = crit_and_counts(Pt, anti)[0]
        ok_b = brute(Pt, b3, C2int, den, ids, anti)[0]
        ge6_constructed.append({'k': kk, 'criterion': ok_c, 'frozen_brute_force': ok_b})
    # TIGHT instance of the inequality k - c <= 4: share 0, 1, anti(0), anti(1) plus two extra columns
    Qt = [0, 1, ap[0], ap[1], 30, 31]
    Pt = [(0, q) for q in Qt] + [(1, q) for q in Qt]
    tight_bound = {'Q': Qt, 'k': len(Qt), 'c': crit_and_counts(Pt, anti)[2],
                   'k_minus_c': 0, 'criterion': crit_and_counts(Pt, anti)[0],
                   'frozen_brute_force': brute(Pt, b3, C2int, den, ids, anti)[0]}
    tight_bound['k_minus_c'] = tight_bound['k'] - tight_bound['c']
    pos_ok = all(r2['criterion'] and r2['frozen_brute_force'] for r2 in ge6_constructed)
    cells['P3'] = {'verdict': '✅' if (sat and maxkd <= 4 and pos_ok and tight_bound['k_minus_c'] <= 4
                                      and tight_bound['criterion'] and tight_bound['frozen_brute_force']
                                      and all(tight[kk]['constructible_instance'] is not None
                                              and tight[kk]['non_constructible_instance'] is not None
                                              for kk in (2, 3, 4, 5)) and len(le1) > 0) else '🟡',
        'value': {'k_ge_6_instances_in_test_set': len(ge6), 'all_k_ge_6_constructible': sat,
                  'constructed_k_ge_6_positives': ge6_constructed, 'positive_tests_ok': pos_ok,
                  'tight_bound_instance': tight_bound,
                  'k_le_1_instances': len(le1), 'max_k_minus_c': maxkd, 'tightness': tight},
        'note': 'T3: with anti a perfect matching (31 pairs) c >= k - 4, so k >= 6 forces constructibility; '
                'k <= 1 forces non-constructibility; k = 2..5 must be decided case by case (bound is tight)'}

    # ---------------- P4: extremal rz(n) + KST ----------------
    def rz(n):
        masks = list(range(1 << n))
        best = [0]
        chosen = []
        order = sorted(masks, key=lambda mm2: -_pop(mm2))

        def rec(idx, total):
            nonlocal best
            if idx == n:
                if total > best[0]:
                    best[0] = total
                return
            remain = n - idx
            if total + remain * n <= best[0]:
                return
            for mm2 in order:
                if len(chosen) > 0 and _pop(mm2) > _pop(chosen[-1]):
                    continue
                if all(_pop(mm2 & c) <= 1 for c in chosen):
                    chosen.append(mm2)
                    rec(idx + 1, total + _pop(mm2))
                    chosen.pop()
        rec(0, 0)
        return best[0]

    rzs = {}
    for n in (3, 4, 5):
        rzs[n] = rz(n)
    sq = ai(4 * N - 3)
    root_ceil = sq if sq * sq == 4 * N - 3 else sq + 1
    kst = (N * (1 + root_ceil)) // 2
    cells['P4'] = {'verdict': '✅' if (L_BUDGET < kst and rzs[3] == 6 and rzs[4] >= 9 and rzs[5] >= rzs[4]) else '🟡',
                   'value': {'rz_3': rzs[3], 'rz_4': rzs[4], 'rz_5': rzs[5],
                             'kst_upper_bound_N62_ceil': kst, 'kst_sqrt_floor': sq, 'kst_root_ceil': root_ceil,
                             'kst_integer_form': '%d*(1+ceil(sqrt(%d)))/2 = %d' % (N, 4 * N - 3, kst),
                             'budget_edges': L_BUDGET, 'ratio_budget_over_bound': '%d/%d' % (L_BUDGET, kst)},
                   'note': 'T4: rz(n) exact for n = 3,4,5 by exhaustive 0-1 matrix search; the KST bound at N = 62 '
                           'is far above the budget => sparsity does NOT force non-constructibility'}

    # ---------------- P5: filter effect ----------------
    p5 = []
    for name in sorted(known):
        P = sorted(known[name])
        ok, bk, bc_, sk, sc, mkd, arg = crit_and_counts(P, anti)
        raw_rect = 0
        Pset = set(P)
        rows = rows_of(P)
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                sh = len([q for (x, q) in P if x == rows[i] and (rows[j], q) in Pset])
                if sh >= 2:
                    raw_rect += sh * (sh - 1) // 2
        p5.append({'prefix': name, 'edges': len(P), 'sum_k': sk, 'sum_c': sc, 'max_k_minus_c': mkd,
                   'raw_rectangles': raw_rect, 'filtered_max_c': bc_, 'constructible': ok})
    max_kd = max([r['max_k_minus_c'] for r in p5] or [0])
    cells['P5'] = {'verdict': '✅' if max_kd <= 4 else '🔴', 'value': p5,
                   'note': 'T5: k - c <= 4 (self-exclusion kills at most 2 columns, anti at most 2); '
                           'the raw count is reported next to the filtered one'}

    # ---------------- P6: class-level prevalence ----------------
    def enum_circuits(n, prefix_len, node_cap, time_cap):
        out_adj2 = [sorted(j for j in range(n) if j != v) for v in range(n)]
        total_edges = n * (n - 1)
        res = {'constructible': 0, 'circuits': 0, 'nodes': 0, 'capped': False}
        used = set()
        t0 = time.time()

        def dfs(v, depth, seq):
            res['nodes'] += 1
            if res['capped']:
                return
            if res['nodes'] > node_cap or (res['nodes'] % 100000 == 0 and time.time() - t0 > time_cap):
                res['capped'] = True
                return
            if depth == total_edges:
                if v == 0:
                    res['circuits'] += 1
                    if crit_and_counts(seq[:prefix_len] if prefix_len < total_edges else seq, anti)[0]:
                        res['constructible'] += 1
                return
            for w in out_adj2[v]:
                e = (v, w)
                if e in used:
                    continue
                if depth == 0 and e != (0, 1):
                    continue
                if depth == total_edges - 1 and w != 0:
                    continue
                used.add(e)
                seq.append(e)
                dfs(w, depth + 1, seq)
                seq.pop()
                used.remove(e)
                if res['capped']:
                    return
        dfs(0, 0, [])
        return res

    def sample_circuits(n, prefix_len, k_samples, seed):
        rng = LCG(seed)
        out_adj2 = [sorted(j for j in range(n) if j != v) for v in range(n)]
        total_edges = n * (n - 1)
        cons = 0
        circs = 0
        for _s in range(k_samples):
            rem = [list(x) for x in out_adj2]      # dynamic remaining out-edges (exact, no recomputation)
            stack = [0]
            vlist = []
            guard = 0
            while stack and guard < 100 * total_edges:
                guard += 1
                v = stack[-1]
                rv = rem[v]
                if rv:
                    kk = rng.below(len(rv))
                    w = rv.pop(kk)
                    stack.append(w)
                else:
                    vlist.append(stack.pop())
            vlist.reverse()          # Hierholzer gives the Euler tour as a VERTEX sequence
            seq = [(vlist[i], vlist[i + 1]) for i in range(len(vlist) - 1)]
            if len(seq) == total_edges and len(set(seq)) == total_edges and trail_closed(seq):
                k0 = seq.index((0, 1))          # canonical rotation = class convention (first edge (0,1))
                seq = seq[k0:] + seq[:k0]
                circs += 1
                if crit_and_counts(seq[:prefix_len], anti)[0]:
                    cons += 1
        return cons, circs

    n4 = enum_circuits(4, L_SMALL[4], NODE_CAP, TIME_CAP)
    n5 = enum_circuits(5, L_SMALL[5], NODE_CAP, TIME_CAP)
    n5s = None
    if n5['capped']:
        c5, t5 = sample_circuits(5, L_SMALL[5], K_SAMPLE, LCG_SEED)
        n5s = {'constructible': c5, 'circuits': t5, 'sampled': K_SAMPLE}
    c62, t62 = sample_circuits(N, L_BUDGET, K_SAMPLE, LCG_SEED)
    n62 = {'constructible': c62, 'circuits': t62, 'sampled': K_SAMPLE}
    n4_exact = (not n4['capped']) and n4['circuits'] == 256
    p6_verdict = '✅' if (n4_exact and n5s is None and n62['sampled'] == 0) else '🟡'
    cells['P6'] = {'verdict': p6_verdict,
                   'value': {'n4_exact': n4, 'n4_expected_circuits': 256, 'n4_exact_ok': n4_exact,
                             'n4_prefix_len': L_SMALL[4], 'n5_attempt': n5, 'n5_sampled': n5s,
                             'n5_prefix_len': L_SMALL[5], 'n62_sampled': n62, 'n62_prefix_len': L_BUDGET,
                             'lcg': {'a': LCG_A, 'c': LCG_C, 'm': LCG_M, 'seed': LCG_SEED, 'K': K_SAMPLE},
                             'caps': {'nodes': NODE_CAP, 'seconds': TIME_CAP}},
                   'note': 'class-level prevalence: n = 4 enumerated exactly (whole class, first edge (0,1)); '
                           'n = 5 / n = 62 are SAMPLES (LCG) -> this cell is honestly 🟡, never an exact value. '
                           'For n <= 5 the whole circuit fits inside the 21-edge budget, so the non-trivial '
                           'question uses the pre-registered shorter prefixes L_small'}

    out = {'rules_version': RULES, 'cells': cells, 'cell_order': list(CELLS)}
    with io.open(os.path.join(DATA, '24_g5_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for c in CELLS:
        v = cells[c]
        print('  %-3s %-2s %s' % (c, v['verdict'], json.dumps(v['value'], ensure_ascii=False)[:230]))
    cnt = {'✅': 0, '🟡': 0, '🔴': 0}
    for c in CELLS:
        cnt[cells[c]['verdict']] += 1
    print('-' * 112)
    print('G5: %d cells -> %d OK / %d PARTIAL / %d FAILED' % (len(CELLS), cnt['✅'], cnt['🟡'], cnt['🔴']))
    print('=' * 112)
    return 0


def trail_closed(edges):
    return all(edges[i][1] == edges[i + 1][0] for i in range(len(edges) - 1)) and edges[-1][1] == edges[0][0]


def _pop(x):
    c = 0
    while x:
        c += x & 1
        x >>= 1
    return c


def _combinations(xs, k):
    if k == 0:
        yield ()
        return
    n = len(xs)
    idx = list(range(k))
    while True:
        yield tuple(xs[i] for i in idx)
        i = k - 1
        while i >= 0 and idx[i] == n - k + i:
            i -= 1
        if i < 0:
            return
        idx[i] += 1
        for j in range(i + 1, k):
            idx[j] = idx[j - 1] + 1


if __name__ == '__main__':
    sys.exit(main())
