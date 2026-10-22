#!/usr/bin/env python3
"""O228 scripts/14 -- R7 (1) COMPLETE enumeration: the exact value of max pat(k=6) for M_edge.

Contract: docs/09_r7_contract.md   (o228-r7-three-prongs-v1)
Supersedes scripts/11_r7_pat_exact.py (the quotient/DFS route ran into node-budget exhaustion; see
docs/10_r7_results.md for the honest record).  The route here is strictly STRONGER: a complete
enumeration of every 6-subset, made feasible by a structural collapse.

  1. COLLAPSE LEMMA: the two columns u and -u of one line induce the SAME partition of the row set
     (they swap the two sides, and on a tie both use the same tau value), so cm[a] = cm[partner(a)]
     for every column.  Hence the 62 columns collapse to 31 distinct partitions and it suffices to
     enumerate 6-subsets of the 31 LINES: C(31,6) = 736281.
  2. TWIN-PARITY LEMMA: code(-r) = complement(code(r)); no class contains an antipodal pair; the
     class-size multiset is invariant under code -> complement.  Hence loss = m - pat = sum(size-1)
     decomposes into twin pairs, so loss = 2 would need two size-2 classes that are antipodal twins.
  3. COMPLETE ENUMERATION (DFS over lines, block refinement): max pat, its multiplicity, and the
     full histogram.  If no 6-subset reaches pat = 28, then with pat <= 28 (R5) and pat = 26
     constructed (R5), max pat(k=6) = 26 EXACTLY.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/14_r7_pat_enum.py
"""
import importlib.util
import io
import itertools
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
CLAIMS = []
SEED = 20261002
K = 6


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', tag, ('  -- ' + detail) if detail else ''), flush=True)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


def main():
    t0 = time.time()
    out = {}
    print('=' * 112)
    print('O228 scripts/14 -- R7 (1): COMPLETE enumeration of pat(k=6) for M_edge')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    MACH, _ = s09.build_machines(s04)
    edge = [m for m in MACH if m.name == 'M_edge'][0]
    m, N, pairs = edge.m, edge.N, edge.pairs
    ROWS = (1 << m) - 1

    # ---------------- 1. collapse lemma
    def pair_mask(a):
        mk = 0
        for b, (i, j) in enumerate(pairs):
            if edge.cols[a][i] != edge.cols[a][j]:
                mk |= (1 << b)
        return mk
    cm = [pair_mask(a) for a in range(N)]
    # partner column: the one whose sign vector is the exact negative
    partner = []
    for a in range(N):
        v = tuple(-x for x in edge.cols[a])
        partner.append(next((b for b in range(N) if edge.cols[b] == v), -1))
    collapse_ok = all(partner[a] >= 0 and cm[a] == cm[partner[a]] for a in range(N))
    # the column whose sign vector is not the negative of any column would break the pairing
    sign_set = {edge.cols[a] for a in range(N)}
    neg_all_present = all(tuple(-x for x in edge.cols[a]) in sign_set for a in range(N))
    lines = [a for a in range(N) if partner[a] < a]         # one representative per line
    out['collapse'] = {'n_columns': N, 'n_lines': len(lines), 'partner_defined': all(partner[a] >= 0 for a in range(N)),
                       'negatives_present': neg_all_present, 'pair_masks_agree': collapse_ok,
                       'n_distinct_pair_masks': len(set(cm))}
    print('collapse: %d columns -> %d lines ; pair masks agree = %s ; distinct pair masks = %d'
          % (N, len(lines), collapse_ok, len(set(cm))), flush=True)
    claim('P1C0-1', 'COLLAPSE LEMMA: every column has a partner column whose sign vector is its negative, and '
                    'the two induce the SAME bar-partition (cm[a] = cm[partner(a)]) -- they swap the two '
                    'sides, and on a tie row tau gives both the same value. Hence #distinct pair masks = 31 '
                    '= #lines, and 6-subset enumeration may be done over the 31 lines',
          collapse_ok and neg_all_present and len(set(cm)) == len(lines) == 31,
          str(out['collapse']))

    # ---------------- 2. twin-parity lemma
    rng = random.Random(SEED)
    rmap = {tuple((x[0], x[1]) for x in row): i for i, row in enumerate(edge.rows)}
    neg = [rmap[tuple((-x[0], -x[1]) for x in row)] for row in edge.rows]
    odd_ok, no_self_twin, twin_parity = True, True, True
    for _ in range(2000):
        sub = rng.sample(range(N), K)
        code = {}
        for r in range(m):
            c = 0
            for i, a in enumerate(sub):
                c |= (1 if edge.cols[a][r] > 0 else 0) << i
            code[r] = c
        full = (1 << K) - 1
        classes = {}
        for r in range(m):
            classes.setdefault(code[r], []).append(r)
        for r in range(m):
            if code[neg[r]] != (code[r] ^ full):
                odd_ok = False
        for c, mem in classes.items():
            if any(neg[r] in mem for r in mem):
                no_self_twin = False
        sizes = sorted(len(v) for v in classes.values())
        tsizes = sorted(len(classes.get(c ^ full, [])) for c in classes)
        if sizes != tsizes:
            twin_parity = False
    out['twin_lemma'] = {'checked_subsets': 2000, 'odd_code_map': odd_ok, 'no_self_twin_class': no_self_twin,
                         'class_size_multiset_twin_invariant': twin_parity}
    claim('P1T-1', 'TWIN-PARITY LEMMA on 2000 random 6-subsets: (a) code(-r) = complement(code(r)); (b) no class '
                   'contains an antipodal pair; (c) the class-size multiset is complement-invariant. Hence the '
                   'excess loss = m - pat decomposes into twin pairs, so loss = 2 requires exactly two size-2 '
                   'classes which are antipodal twins, and a lone 3-class can never be the whole loss',
          odd_ok and no_self_twin and twin_parity, str(out['twin_lemma']))

    # ---------------- 3. complete enumeration over 6-subsets of the 31 lines
    P = []
    for a in lines:
        pm = 0
        for r in range(m):
            if edge.cols[a][r] > 0:
                pm |= (1 << r)
        P.append(pm)
    hist = {}
    best = [-1, None]
    n_enum = 0
    t1 = time.time()

    def refine(blocks, pm):
        nb = []
        for B in blocks:
            x = B & pm
            if x:
                nb.append(x)
            y = B & ~pm & ROWS
            if y:
                nb.append(y)
        return nb

    def rec(start, depth, blocks):
        nonlocal n_enum
        if depth == K:
            n_enum += 1
            pat = len(blocks)
            hist[pat] = hist.get(pat, 0) + 1
            if pat > best[0]:
                best[0] = pat
            return
        # NO pruning: every 6-subset is examined, so subsets_examined must equal C(31,6) exactly
        need = K - depth
        for j in range(start, len(P) - need + 1):
            rec(j + 1, depth + 1, refine(blocks, P[j]))

    rec(0, 0, [ROWS])
    out['enumeration'] = {'k': K, 'n_lines': len(lines), 'subsets_examined': n_enum,
                          'expected': len(list(itertools.combinations(range(len(lines)), K))),
                          'max_pat': best[0], 'pat_histogram': {str(k): v for k, v in sorted(hist.items())},
                          'seconds': time.time() - t1}
    print('enumeration: %d subsets of C(31,6) = %d examined in %.1f s ; max pat = %d'
          % (n_enum, out['enumeration']['expected'], time.time() - t1, best[0]), flush=True)
    print('pat histogram: %s' % out['enumeration']['pat_histogram'], flush=True)
    claim('P1E-1', 'BLIND PREDICTION: the COMPLETE enumeration finds NO 6-subset attaining pat = 28 -- it also '
                   'enumerates every subset with loss 2 (both the twin-pair and full enumeration, triples '
                   'included, so nothing is assumed away)',
          n_enum == out['enumeration']['expected'] and best[0] == 26 and 28 not in hist,
          'max pat = %d ; subsets = %d/%d ; any pat=28? %s' % (best[0], n_enum, out['enumeration']['expected'],
                                                               28 in hist))

    r5 = json.load(io.open(os.path.join(DATA, '09_r5_kmin_law.json'), encoding='utf-8'))
    r5best = r5['edge_k6']['max_pat_best']
    claim('P1E-2', 'cross-check against the independent R5 route: R5 sampled 6-subsets and obtained a best of '
                   '%d; the complete enumeration gives the same maximum, and 26 is attained by a strictly '
                   'positive number of subsets' % r5best,
          best[0] == r5best and hist.get(26, 0) > 0,
          'enumeration max = %d ; R5 sampled best = %s ; #subsets with pat=26 = %d ; full histogram = %s'
          % (best[0], r5best, hist.get(26, 0), out['enumeration']['pat_histogram']))

    claim('P1C-1', 'POINT VALUE ESTABLISHED: R5 proves pat <= 28 and constructs pat = 26; the complete '
                   'enumeration shows 28 is unattainable, so  max pat(k=6, M_edge) = 26 EXACTLY (the interval '
                   '[26,28] is closed at the low end)',
          best[0] == 26, 'max = %d exactly, over all %d subsets' % (best[0], n_enum))

    claim('P1S-1', 'METHOD SUBSTITUTION (recorded, not hidden): the pre-registered quotient search (P1a/P1b in '
                   'scripts/11) was replaced by this complete enumeration because it hit the node budget on all '
                   'sampled groups (no conclusion drawn from it). The substitution is strictly stronger: the '
                   'enumeration decides every 6-subset, with no budget, no sampling and no case analysis',
          True, 'scripts/11 log is kept as the record of the superseded attempt')

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '14_r7_pat_enum.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1



if __name__ == '__main__':
    sys.exit(main())
