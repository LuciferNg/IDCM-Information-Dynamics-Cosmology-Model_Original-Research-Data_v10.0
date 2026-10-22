#!/usr/bin/env python3
"""O222 scripts/21 -- G4 machine: the read order derived from the frozen structure (contract docs/14, g4-contract-v1).

No new semantics.  Everything comes from imported frozen objects:
  scripts/12 (the machine: run_pair / load_machine / load_a2)  -- the ONLY source of costs and values,
  scripts/15 (B3R2: simulate / feasible_chsh / order_list / build_anti) -- the SAME statistic definitions.

Cells:
  P1  cost law over the whole table: 63 settings-of-top x 62 x 62 = 242,172 frozen machine runs
  P2  Hierholzer construction of an Eulerian circuit on the loop-free complete digraph (3782 edges)
  P3  optimality: (i) min cost from the P1 table, (ii) measured reads of the circuit, (iii) n=3 full
      permutation enumeration (6! = 720) testing "optimal <=> Eulerian"
  P4  non-uniqueness: BEST = t_w * prod(deg-1)! with exact big integers; brute-force EC and arborescence
      counts for n=3,4 to validate the formula's applicability
  P5  constructibility of the prefix: (a) the canonical circuit, (b) an explicit Eulerian circuit whose
      prefix contains a 2x2 rectangle (B3R2 criterion), with the residual-Eulerian argument verified
  P6  fairness: max_v |out - in| on the canonical prefix, and the same measure for the five B3R2 families

Usage:  /usr/bin/python3 scripts/21_g4_eulerian.py
"""
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
RULES = 'g4-contract-v1'
CELLS = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fact(n):
    r = 1
    for k in range(2, n + 1):
        r *= k
    return r


def law(t, a, b):
    return 3 - (1 if t == a else 0) - (1 if b == a else 0)


def hierholzer(n, out_adj, start, first_edge=None):
    """exact Hierholzer, canonical tie-break = smallest index; returns the edge sequence of a closed circuit."""
    ptr = dict((v, 0) for v in range(n))
    stack = [start]
    vseq = []
    while stack:
        v = stack[-1]
        if ptr[v] < len(out_adj[v]):
            w = out_adj[v][ptr[v]]
            ptr[v] += 1
            stack.append(w)
        else:
            vseq.append(stack.pop())
    vseq.reverse()
    edges = [(vseq[i], vseq[i + 1]) for i in range(len(vseq) - 1)]
    if first_edge is not None and edges:
        k = edges.index(first_edge)
        edges = edges[k:] + edges[:k]
    return edges


def trail_ok(edges):
    for i in range(len(edges) - 1):
        if edges[i][1] != edges[i + 1][0]:
            return False
    if edges and edges[-1][1] != edges[0][0]:
        return False
    return True


def eulerian_clock(n, include_loops):
    return [(a, b) for a in range(n) for b in range(n) if include_loops or a != b]


def main():
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(400000)      # EC(62) has ~5200 digits; the default cap is 4300
    print('=' * 112)
    print('O222 scripts/21 -- G4: read order derived from the frozen structure (rules %s)' % RULES)
    print('=' * 112, flush=True)
    b5 = load(os.path.join(HERE, '12_b5_budget.py'), 'g4b5')
    b3 = load(os.path.join(HERE, '15_b3r2_orderfair.py'), 'g4b3')
    C1f, C2f, ids, types, den1 = b5.load_a2()
    mm, K, MUL, hx, ids2, types2 = b5.load_machine()
    axis, U, _i4, _t4, _h4 = mm.load_inputs()
    corr = json.load(io.open(os.path.join(DATA, '09_a2_correlation.json'), encoding='utf-8'))
    budget = F(123, 2)
    cells = {}

    # ---------------- P1: the cost law over the WHOLE table ----------------
    total = 0
    match = 0
    exceptions = []
    seen = {}
    for t in (-1,) + tuple(range(N)):
        for a in range(N):
            for b in range(N):
                r, _rem = b5.run_pair(a, b, 0, t, K, MUL, hx, budget)
                got = r['misses']
                want = law(t, a, b)
                total += 1
                if got == want:
                    match += 1
                elif len(exceptions) < 40:
                    exceptions.append({'t': t, 'a': ids[a], 'b': ids[b], 'got': got, 'law': want})
                grad = got - want
                seen[grad] = seen.get(grad, 0) + 1
    p1_ok = match == total
    cells['P1'] = {'verdict': '✅' if p1_ok else '🟡' if match * 100 >= total * 99 else '🔴',
                   'value': {'cells': total, 'matches': match, 'exceptions': exceptions,
                             'gradient_histogram': dict((str(k), v) for k, v in sorted(seen.items())),
                             'degenerate_t_a_b': sum(1 for t in range(N) for x in range(N)
                                                     if t == x)},
                   'note': 'cost(e) = 3 - [t == a] - [b == a]; the t = a = b case consumes the seeded '
                           'ledger entry (pop eats the seed) -- reported, never patched'}

    # ---------------- P2: Hierholzer ----------------
    out_adj = [sorted(j for j in range(N) if j != a) for a in range(N)]
    circuit = hierholzer(N, out_adj, 0, first_edge=(0, 1))
    eset = set(circuit)
    wanted = set(eulerian_clock(N, False))
    p2_ok = (len(circuit) == N * (N - 1) and eset == wanted and len(eset) == len(circuit) and trail_ok(circuit))
    cells['P2'] = {'verdict': '✅' if p2_ok else '🔴',
                   'value': {'edges_in_circuit': len(circuit), 'distinct_edges': len(eset),
                             'expected': N * (N - 1), 'closed_and_connected': trail_ok(circuit),
                             'head_equals_tail_everywhere': all(circuit[i][1] == circuit[i + 1][0]
                                                                for i in range(len(circuit) - 1)),
                             'first_edges': [[ids[a], ids[b]] for a, b in circuit[:6]]},
                   'note': 'Hierholzer with the canonical tie-break (smallest index); rotated to start at (0,1)'}

    # ---------------- P3: optimality ----------------
    min_nondegenerate = min(law(t, a, b) for t in (-1,) + tuple(range(N))
                            for a in range(N) for b in range(N) if a != b)
    min_all = min(law(t, a, b) for t in (-1,) + tuple(range(N)) for a in range(N) for b in range(N))
    p3i = {'min_cost_loop_free_edges': min_nondegenerate, 'min_cost_all_pairs': min_all,
           'law_total_for_circuit': 3 + 2 * (len(circuit) - 1)}
    # (ii) measured reads on the frozen machine
    pref, trail, blocked_at, rem = b3.simulate(b5, circuit, K, MUL, hx, budget, top=-1)
    reads = sum(e['misses'] for e in trail)
    p3ii = {'feasible_prefix_edges': len(pref), 'reads': reads, 'budget': str(budget),
            'budget_left': str(rem), 'blocked_at': None if blocked_at is None else [ids[blocked_at[0]], ids[blocked_at[1]]],
            'reads_per_edge': [e['misses'] for e in trail]}
    # (iii) n = 3 full permutation enumeration
    n3 = 3
    pairs3 = eulerian_clock(n3, False)
    import itertools
    best3 = None
    minimisers = []
    perm_count = 0
    for perm in itertools.permutations(pairs3):
        perm_count += 1
        t = -1
        c = 0
        ok = True
        for (a, b) in perm:
            c += law(t, a, b)
            t = b
        if best3 is None or c < best3:
            best3 = c
            minimisers = [perm]
        elif c == best3:
            minimisers.append(perm)
    eul3 = [p for p in minimisers if trail_ok(list(p))]
    p3iii = {'permutations_enumerated': perm_count, 'min_total_cost': best3,
             'law_predicted_min': 3 + 2 * (len(pairs3) - 1),
             'minimiser_count': len(minimisers), 'minimisers_all_eulerian': len(eul3) == len(minimisers),
             'eulerian_minimisers': len(eul3)}
    p3_ok = (min_nondegenerate == 2 and min_all == 1 and reads == 3 + 2 * (len(pref) - 1)
             and best3 == 3 + 2 * (len(pairs3) - 1) and len(eul3) == len(minimisers))
    cells['P3'] = {'verdict': '✅' if p3_ok else '🟡' if min_nondegenerate == 2 else '🔴',
                   'value': {'i_min_cost': p3i, 'ii_measured': p3ii, 'iii_toy_n3': p3iii},
                   'note': 'every loop-free edge costs >= 2; the circuit measures exactly 2 per internal edge; '
                           'in the n=3 toy every cost-optimal order IS Eulerian (T2(iii) survives)'}

    # ---------------- P4: non-uniqueness (BEST) ----------------
    def arborescences(n):
        """brute force in-arborescences rooted at 0 (exact, small n only)."""
        cnt = 0
        verts = list(range(1, n))

        def rec(k, parent):
            nonlocal cnt
            if k == len(verts):
                for w in verts:
                    seen = set()
                    x = w
                    while x != 0:
                        if x in seen:
                            return
                        seen.add(x)
                        x = parent[x]
                cnt += 1
                return
            v = verts[k]
            for p in range(n):
                if p != v:
                    parent[v] = p
                    rec(k + 1, parent)
        rec(0, dict((v, 0) for v in verts))
        return cnt

    def brute_ec(n):
        """count Eulerian circuits starting at vertex 0 (edge sequences), exact DFS."""
        out_adj2 = [sorted(j for j in range(n) if j != v) for v in range(n)]
        used = set()
        total_edges = n * (n - 1)
        cnt = [0]

        def dfs(v, depth):
            if depth == total_edges:
                if v == 0:
                    cnt[0] += 1
                return
            for w in out_adj2[v]:
                e = (v, w)
                if e in used:
                    continue
                used.add(e)
                dfs(w, depth + 1)
                used.remove(e)
        dfs(0, 0)
        return cnt[0]

    best_rows = []
    for n in (3, 4):
        t_w = arborescences(n)
        best = t_w * fact(n - 2) ** n if n >= 2 else 1
        bf = brute_ec(n)
        # CONVENTION: BEST counts circuits with a fixed first edge; a DFS over edge sequences from w
        # revisits every circuit once per out-edge of w, i.e. outdeg(w) = n - 1 times.
        best_rows.append({'n': n, 'arborescences_bruteforce': t_w, 'n^(n-2)': n ** (n - 2),
                          'best_theorem_fixed_first_edge': best,
                          'best_times_outdeg_w': best * (n - 1),
                          'brute_force_edge_sequences_from_vertex0': bf,
                          'agree': bf == best * (n - 1) or bf == best,
                          'convention': 'sequences = BEST * outdeg(w)' if bf == best * (n - 1) else 'exact'})
    EC62 = N ** (N - 2) * fact(N - 2) ** N
    p4_ok = all(r['agree'] and r['arborescences_bruteforce'] == r['n^(n-2)']
                and r['convention'] == 'sequences = BEST * outdeg(w)' for r in best_rows)
    cells['P4'] = {'verdict': '✅' if p4_ok else '🔴',
                   'value': {'n3_n4_validation': best_rows,
                             'EC_62_formula': "62^60 * (60!)^62",
                             'EC_62_digits': len(str(EC62)),
                             'EC_62_head': str(EC62)[:24] + '...' + str(EC62)[-8:],
                             'EC_62_gt_1': EC62 > 1,
                             'unique_order': EC62 == 1},
                   'note': 'BEST validated on n=3,4 by brute force (arborescences AND circuits); '
                           'the structure forces the CLASS, not a unique order'}

    # ---------------- P5: constructibility ----------------
    den2 = 1
    for a in range(N):
        for b in range(N):
            d = F(C2f[a][b]).denominator
            g = den2
            x, y = g, d
            while y:
                x, y = y, x % y
            den2 = den2 * d // x
    C2int = [[int(F(C2f[a][b]) * den2) for b in range(N)] for a in range(N)]   # denominator COMPUTED, not assumed
    anti = b3.build_anti(mm, U)
    pref_set = set(pref)
    vA, bargA, domA = b3.feasible_chsh(C2int, den2, 'all4', pref_set, anti, ids)
    # (b) explicit Eulerian circuit whose prefix contains a rectangle (0,2),(0,3),(1,2),(1,3)
    rect_edges = [(0, 2), (2, 1), (1, 3), (3, 0), (0, 3), (3, 1), (1, 2)]
    # extend the trail to exactly len(pref) edges with a greedy but verified walk
    used_e = set(rect_edges)
    cur = rect_edges[-1][1]
    trail_b = list(rect_edges)
    while len(trail_b) < len(pref):
        for w in sorted(j for j in range(N) if j != cur):
            if (cur, w) not in used_e:
                trail_b.append((cur, w))
                used_e.add((cur, w))
                cur = w
                break
        else:
            break
    remainder = sorted(set(eulerian_clock(N, False)) - used_e)
    # the prefix is a trail s0 -> t0, so the residual admits an Eulerian PATH t0 -> s0 (not a circuit);
    # construct it by adding the virtual edge (s0, t0), which balances the residual exactly.
    s0, t0 = trail_b[0][0], trail_b[-1][1]
    indeg = dict((v, 0) for v in range(N))
    outdeg = dict((v, 0) for v in range(N))
    for (a, b) in remainder:
        outdeg[a] += 1
        indeg[b] += 1
    imbalance_ok = (outdeg[t0] - indeg[t0] == 1 and indeg[s0] - outdeg[s0] == 1
                    and all(outdeg[v] == indeg[v] for v in range(N) if v not in (s0, t0)))
    nonempty = all(outdeg[v] > 0 for v in range(N))
    aug = [sorted(w for (x, w) in remainder if x == v) for v in range(N)]
    aug[s0] = sorted(aug[s0] + [t0])
    circ = hierholzer(N, aug, s0)
    k = circ.index((s0, t0))
    comp = circ[k + 1:] + circ[:k]
    full = trail_b + comp
    ok_b = (imbalance_ok and nonempty and len(full) == N * (N - 1)
            and set(full) == set(eulerian_clock(N, False)) and trail_ok(full))
    pref_b = set(trail_b)
    vB, bargB, domB = b3.feasible_chsh(C2int, den2, 'all4', pref_b, anti, ids)
    cells['P5'] = {'verdict': '✅' if (vA is None and vB is not None and ok_b) else '🟡',
                   'value': {'a_canonical_prefix_edges': len(pref),
                             'a_constructible': vA is not None, 'a_all4': None if vA is None else str(vA),
                             'a_argmax': None if bargA is None else [ids[x] for x in bargA],
                             'b_prefix_edges': len(trail_b), 'b_rectangle_present': True,
                             'b_constructible': vB is not None, 'b_all4': None if vB is None else str(vB),
                             'b_argmax': None if bargB is None else [ids[x] for x in bargB],
                             'b_residual_imbalance_ok': imbalance_ok, 'b_residual_full_degree': nonempty,
                             'b_assembled_circuit_edges': len(full),
                             'b_assembled_is_full_eulerian_circuit': (len(full) == N * (N - 1)
                                                                     and set(full) == set(eulerian_clock(N, False))
                                                                     and trail_ok(full)),
                             'b_residual_ok': ok_b},
                   'note': 'canonical prefix is a TRAIL (each edge once) so its pair set is sparse; the '
                           'existence half shows a rectangle CAN sit inside an Eulerian prefix, so '
                           'constructibility is achievable inside the structurally forced class'}

    # ---------------- P6: fairness ----------------
    def fairness(prefset, label):
        outd = dict((v, 0) for v in range(N))
        ind = dict((v, 0) for v in range(N))
        for (a, b) in prefset:
            outd[a] += 1
            ind[b] += 1
        return {'family': label, 'edges': len(prefset),
                'max_abs_out_minus_in': max(abs(outd[v] - ind[v]) for v in range(N)),
                'unbalanced_vertices': sum(1 for v in range(N) if outd[v] != ind[v]),
                'max_out': max(outd.values()), 'max_in': max(ind.values())}
    rows = [fairness(pref_set, 'Eulerian-canonical')]
    for oid in ('lex', 'diag', 'antidiag', 'block', 'stride'):
        p2, _tr, _bl, _rm = b3.simulate(b5, b3.order_list(oid), K, MUL, hx, budget, top=-1)
        rows.append(fairness(set(p2), oid))
    worst = max(r['max_abs_out_minus_in'] for r in rows if r['family'] == 'Eulerian-canonical')
    cells['P6'] = {'verdict': '✅' if worst <= 1 else '🔴', 'value': rows,
                   'note': 'theorem: in any prefix of an Eulerian circuit each vertex has |out - in| <= 1; '
                           'the five human families are listed under the SAME definition'}

    out = {'rules_version': RULES, 'cells': cells, 'cell_order': list(CELLS),
           'eulerian_circuit_head': [[ids[a], ids[b]] for a, b in circuit[:12]]}
    with io.open(os.path.join(DATA, '21_g4_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for c in CELLS:
        print('  %-3s %-2s %s' % (c, cells[c]['verdict'], json.dumps(cells[c]['value'], ensure_ascii=False)[:220]))
    n = {'✅': 0, '🟡': 0, '🔴': 0}
    for c in CELLS:
        n[cells[c]['verdict']] += 1
    print('-' * 112)
    print('G4: %d cells -> %d OK / %d PARTIAL / %d FAILED' % (len(CELLS), n['✅'], n['🟡'], n['🔴']))
    print('=' * 112)
    return 0


if __name__ == '__main__':
    sys.exit(main())
