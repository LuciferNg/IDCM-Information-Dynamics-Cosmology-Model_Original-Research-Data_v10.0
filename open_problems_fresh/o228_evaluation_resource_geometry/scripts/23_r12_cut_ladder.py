#!/usr/bin/env python3
"""O228 scripts/23 -- R12: support-set cutting planes, raising the covering LP above 5.

Contract: docs/19_r12_contract.md   (o228-r12-support-cuts-v1)

Direction (fixed in the contract): adding a cut in PACKING space is a constraint and only lowers the bound
(useless for the covering lower bound); adding a cut in COVER space is an extra dual VARIABLE and can raise
it.  A 0/1-coefficient cut "sum_{a in A0} x_a >= 1" is exactly a virtual pair whose candidate set is A0, so
scripts/10's exact rational simplex solves the cut-augmented problem unchanged.

Validity oracle (exhaustive, small): the cut is valid for every integral cover iff NO cover is contained in
A0^c.  With the construction A0^c = S \\ {a} (S = the current LP support, |S| = 10) this is a 2^9 check.

Indexing discipline: S[p] = columns separating pair p, CP[a] = pairs covered by column a.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/23_r12_cut_ladder.py
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
CLAIMS = []
MAX_CUTS = 8
WALL = 240.0


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
    print('O228 scripts/23 -- R12: support-set cutting planes for the covering LP (M_edge)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
    MACH, _ = s09.build_machines(s04)
    edge = [mm for mm in MACH if mm.name == 'M_edge'][0]
    N, NP = edge.N, len(edge.pairs)
    S = []
    for p in range(NP):
        s = 0
        for a in range(N):
            if edge.cols[a][edge.pairs[p][0]] != edge.cols[a][edge.pairs[p][1]]:
                s |= (1 << a)
        S.append(s)
    CP = [0] * N
    for a in range(N):
        m = 0
        for p in range(NP):
            if (S[p] >> a) & 1:
                m |= (1 << p)
        CP[a] = m
    assert len(CP) == N
    ALL = (1 << N) - 1
    ALLP = (1 << NP) - 1

    # rows for the LP: one per pair (57 columns absent is impossible: every pair has 225 candidates)
    rows = [[a for a in range(N) if (S[p] >> a) & 1] for p in range(NP)]
    cuts = []                    # list of dicts describing the added cuts

    def solve(rows, ncols):
        lp = s10.solve_packing_lp(rows, len(rows), ncols)
        return lp

    def cover_inside(cols_subset):
        """is there a COVER (subset of cols_subset) separating all pairs?  exhaustive over subsets."""
        cl = list(cols_subset)
        if len(cl) > 22:
            return None
        for r in range(1, len(cl) + 1):
            for comb in __import__('itertools').combinations(cl, r):
                mk = 0
                for a in comb:
                    mk |= CP[a]
                if mk == ALLP:
                    return comb
        return False

    ladder = []
    t = time.time()
    lp = solve(rows, N)
    print('root LP = %s (support %d columns)'
          % (lp['opt'], sum(1 for v in lp['x'] if v > 0)), flush=True)
    ladder.append({'step': 0, 'value': str(lp['opt']), 'cuts': 0})
    valid_first = False
    bit_first = False
    for step in range(1, MAX_CUTS + 1):
        if (time.time() - t) > WALL:
            print('wall reached', flush=True)
            break
        xs = lp['x']
        supp = [a for a in range(N) if xs[a] > 0]
        best = None
        for a in supp:
            if xs[a] >= 1:
                continue
            Ac = [b for b in supp if b != a]                  # A0^c candidate = current support minus a
            if len(Ac) > 20:
                continue
            res = cover_inside(Ac)
            if res is None:
                continue
            if res is False:                                  # valid cut: no cover inside A0^c
                A0 = [b for b in range(N) if b not in Ac]     # complement of Ac
                viol = sum(xs[b] for b in A0)
                best = (a, Ac, A0, viol)
                break
        if best is None:
            print('no valid cutting candidate found at step %d' % step, flush=True)
            break
        a, Ac, A0, viol = best
        rows = rows + [[b for b in A0]]
        cuts.append({'step': step, 'pivot_support_column': a, 'A0_size': len(A0),
                     'A0_columns': A0, 'Ac_size': len(Ac), 'Ac_columns': Ac,
                     'violation_at_previous_point': str(viol)})
        if step == 1:
            valid_first = True
            bit_first = viol < 1
        lp = solve(rows, N)
        print('step %d: cut on column %d, A0 size %d, previous-point mass %s -> new LP = %s'
              % (step, a, len(A0), viol, lp['opt']), flush=True)
        ladder.append({'step': step, 'value': str(lp['opt']), 'cuts': step})

    out['ladder'] = ladder
    out['cuts'] = cuts
    final = F(ladder[-1]['value'])
    print('final LP bound = %s after %d cuts' % (final, len(cuts)), flush=True)

    claim('P11-1', 'at least one candidate cut is VALID (no cover inside A0^c) and BITES the current LP point '
                   '[BLIND]', valid_first and bit_first,
          'first cut: valid=%s, mass at previous point < 1: %s' % (valid_first, bit_first))
    claim('P11-2', 'the cut ladder reaches >= 6 within <= 8 cuts  [BLIND]', final >= 6,
          'final = %s after %d cuts (ladder %s)'
          % (final, len(cuts), [l['value'] for l in ladder]))
    claim('P11-3', 'the cut ladder reaches exactly 7 within <= 8 cuts (=> a SHORT certificate for k_min = 7) '
                   '[BLIND]', final == 7, 'final = %s after %d cuts' % (final, len(cuts)))

    # P11-4: exhaustive validity re-check of every added cut
    bad = []
    for c in cuts:
        res = cover_inside(c['Ac_columns'])
        if res is not False:
            bad.append((c['step'], res))
    claim('P11-4', 'every added cut is re-verified exhaustively: no cover lies inside its A0^c (0 '
                   'counterexamples)  [not blind: same oracle as construction]', len(bad) == 0,
          '%d cuts checked, %d failures' % (len(cuts), len(bad)))

    claim('P11-5', 'RECORD: certificate size. The cut certificate is %d cuts, each an explicit column set A0 '
                   'plus a 2^%d exhaustive check; the only previously known lower-bound certificate is a '
                   '19,352,397-node pruned DFS' % (len(cuts), len(cuts[0]['Ac_columns']) if cuts else 0),
          True, '%d cuts, ladder %s' % (len(cuts), [l['value'] for l in ladder]))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '23_r12_cut_ladder.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
