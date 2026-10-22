#!/usr/bin/env python3
"""O228 scripts/11 -- R7 ①: the EXACT point value of max pat(k=6) for M_edge.

Contract: docs/09_r7_contract.md   (o228-r7-three-prongs-v1)

R5 proved  pat <= 28   (F_6 = 0  =>  pat <= 29 ; negation closure => pat even)
R5 constructed pat = 26   (two 36-degree triples)
This script settles the interval.

Reduction used (proved and verified here):
  * pattern map is ODD: code(-r) = complement(code(r))  =>  classes never contain an
    antipodal pair and every class has a twin class of the SAME size;
  * therefore loss = m - pat = sum(size-1) decomposes into twin pairs of contributions,
    so  loss = 2  <=>  exactly two classes of size 2 that are antipodal twins of each other;
  * equivalently: some 6-subset separates all row pairs EXCEPT the two twin pairs.
So: enumerate the 225 unordered {p, twin(p)} pair groups and ask whether 6 columns can cover
ALLC minus those two bits.  All fail  =>  loss >= 4  =>  pat <= 26  =>  max pat(k=6) = 26 exactly.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/11_r7_pat_exact.py
"""
import importlib.util
import io
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
CLAIMS = []
MT_SEED = 20261002
NODE_BUDGET = 3000000


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', tag, ('  -- ' + detail) if detail else ''), flush=True)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


def col_masks(mm):
    cm = []
    for a in range(mm.N):
        mk = 0
        for b, (i, j) in enumerate(mm.pairs):
            if mm.cols[a][i] != mm.cols[a][j]:
                mk |= (1 << b)
        cm.append(mk)
    return cm


def find_cover(cm, req, k, budget=NODE_BUDGET):
    """DFS: is there a k-subset of columns whose mask union covers `req`?  returns (found, nodes, hits)"""
    n = len(cm)
    suf = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suf[i] = suf[i + 1] | cm[i]
    res = []
    nodes = [0]

    def rec(start, depth, mk, acc):
        if res or nodes[0] > budget:
            return
        nodes[0] += 1
        if mk == req:
            res.append(acc[:])
            return
        if depth == k:
            return
        need = k - depth
        for j in range(start, n - need + 1):
            nm = mk | cm[j]
            if nm == req:
                res.append(acc + [j])
                return
            if (nm | suf[j + 1]) & req != req:
                continue
            acc.append(j)
            rec(j + 1, depth + 1, nm, acc)
            acc.pop()
            if res:
                return

    rec(0, 0, 0, [])
    return res[0] if res else None, nodes[0], nodes[0] > budget


def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/11 -- R7 (1): exact point value of max pat(k=6) for M_edge')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    MACH, _ = s09.build_machines(s04)
    edge = [m for m in MACH if m.name == 'M_edge'][0]
    m, N, pairs = edge.m, edge.N, edge.pairs
    cm = col_masks(edge)
    ALLC = (1 << len(pairs)) - 1
    bits = s09.type_bits(edge)

    # ---------------------------------------------------------------- row negation map
    rr = {tuple((x[0], x[1]) for x in row): i for i, row in enumerate(edge.rows)}
    neg = []
    for row in edge.rows:
        k2 = tuple((-x[0], -x[1]) for x in row)
        neg.append(rr.get(k2, -1))
    out['negation_map_complete'] = all(v >= 0 for v in neg)
    print('negation map: complete=%s' % out['negation_map_complete'], flush=True)

    # ---------------------------------------------------------------- T1: the odd-map / twin-parity lemma
    rng = random.Random(MT_SEED)
    odd_ok, no_self_twin, twin_parity = True, True, True
    checked = 0
    for _ in range(2000):
        sub = rng.sample(range(edge.N), 6)
        code = {}
        for r in range(m):
            c = 0
            for i, a in enumerate(sub):
                c |= (1 if edge.cols[a][r] > 0 else 0) << i
            code[r] = c
        full = (1 << 6) - 1
        for r in range(m):
            if neg[r] >= 0 and code[neg[r]] != (code[r] ^ full):
                odd_ok = False
        classes = {}
        for r in range(m):
            classes.setdefault(code[r], []).append(r)
        for c, mem in classes.items():
            if any(neg[r] in mem for r in mem):
                no_self_twin = False
        # class-size multiset must be twin-invariant: class of code c has twin code c^full
        sizes = sorted(len(v) for v in classes.values())
        tsizes = sorted(len(classes.get(c ^ full, [])) for c in classes)
        if sizes != tsizes:
            twin_parity = False
        checked += 1
    out['lemma'] = {'checked_subsets': checked, 'odd_code_map': odd_ok, 'no_self_twin_class': no_self_twin,
                    'class_size_multiset_twin_invariant': twin_parity}
    claim('P1T-1', 'twin-parity lemma on 2000 random 6-subsets: (a) code(-r) = complement(code(r)) [odd map], '
                   '(b) no class contains an antipodal pair [no self-twin], (c) the class-size multiset is '
                   'invariant under code -> complement [twin parity]. Consequence: loss = m - pat decomposes '
                   'into twin pairs of contributions, so loss = 2 requires exactly two size-2 classes that are '
                   'antipodal twins, and a single 3-class can NEVER be the whole loss',
          odd_ok and no_self_twin and twin_parity, str(out['lemma']))

    # ---------------------------------------------------------------- P1A: the 225 quotients
    def pair_index(i, j):
        if i > j:
            i, j = j, i
        return pairs.index((i, j))

    groups = []
    for b, (i, j) in enumerate(pairs):
        ni, nj = neg[i], neg[j]
        if ni < 0 or nj < 0:
            continue
        tb = pair_index(ni, nj)
        if tb < b:
            continue
        groups.append((b, tb))
    out['n_pair_groups'] = len(groups)
    print('pair groups up to twin symmetry: %d' % len(groups), flush=True)

    hits, budget_hit, nodes_tot = [], [], 0
    t1 = time.time()
    for idx, (b, tb) in enumerate(groups):
        ex = (1 << b) | (1 << tb)
        req = ALLC & ~ex
        sol, nodes, over = find_cover(cm, req, 6)
        nodes_tot += nodes
        if over:
            budget_hit.append([b, tb])
        if sol:
            hits.append({'pair_group': [b, tb], 'pairs': [list(pairs[b]), list(pairs[tb])],
                         'columns': sol})
        if (idx + 1) % 25 == 0:
            print('   ... %d/%d groups, hits=%d, budget-hits=%d, nodes=%d, %.1f s'
                  % (idx + 1, len(groups), len(hits), len(budget_hit), nodes_tot, time.time() - t1), flush=True)
    out['pair_group_search'] = {'groups': len(groups), 'hits': hits, 'budget_exhausted': budget_hit,
                                'nodes_total': nodes_tot, 'seconds': time.time() - t1}
    claim('P1A-1', 'BLIND PREDICTION (all fail): no {p, twin(p)} pair group admits a 6-column cover of '
                   'ALLC minus its two bits -- so no 6-subset can leave exactly one twin pair of rows '
                   'unseparated', len(hits) == 0 and len(budget_hit) == 0,
          'groups=%d hits=%d budget_exhausted=%d nodes=%d' % (len(groups), len(hits), len(budget_hit), nodes_tot))

    # ---------------------------------------------------------------- P1C: the point value
    r5 = json.load(io.open(os.path.join(DATA, '09_r5_kmin_law.json'), encoding='utf-8'))
    constructed = r5['edge_k6']['max_pat_best']
    exact_ok = (len(hits) == 0 and len(budget_hit) == 0 and constructed == 26)
    out['point_value'] = {'constructed': constructed, 'upper': 26 if exact_ok else None,
                          'interval_before': [26, 28]}
    claim('P1C-1', 'INTERVAL COLLAPSED: no 6-subset reaches pat = 28 (P1A-1 exhaustive over all 225 twin pair '
                   'groups, no budget exhausted) and pat is even with pat <= 28, hence pat <= 26; R5 already '
                   'constructs 26  =>  max pat(k=6) = 26 EXACTLY (not an interval)',
          exact_ok, 'constructed = %d ; upper = %s ; hits = %d' % (constructed, 26 if exact_ok else 'n/a', len(hits)))

    # ---------------------------------------------------------------- sanity: the triple case is impossible
    tri_tested, tri_hits = 0, 0
    for t in range(60):                      # 60 sampled triples, for illustration only
        trip = rng.sample(range(m), 3)
        ts = set(trip)
        if any(neg[r] in ts and r < neg[r] for r in trip):
            continue
        ex = 0
        for i in range(3):
            for j in range(i + 1, 3):
                ex |= 1 << pair_index(trip[i], trip[j])
                ni, nj = neg[trip[i]], neg[trip[j]]
                if ni >= 0 and nj >= 0:
                    ex |= 1 << pair_index(ni, nj)
        req = ALLC & ~ex
        sol, nodes, over = find_cover(cm, req, 6)
        tri_tested += 1
        if sol:
            tri_hits += 1
    out['triple_sample'] = {'tested': tri_tested, 'hits': tri_hits}
    claim('P1T-2', 'illustration of the lemma: on 60 sampled triple merges (the triple AND its antipodal twin '
                   'both merged, as twin parity forces) no 6-column cover exists either -- consistent with the '
                   'lemma excluding the single-3-class route to loss 2', tri_hits == 0 and tri_tested > 0,
          'tested=%d hits=%d' % (tri_tested, tri_hits))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '11_r7_pat_exact.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
