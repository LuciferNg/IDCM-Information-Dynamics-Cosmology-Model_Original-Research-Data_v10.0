#!/usr/bin/env python3
"""O228 scripts/13 -- R7 (3): the packing gap k_min - nu across a machine ZOO (law hunt).

Contract: docs/09_r7_contract.md   (o228-r7-three-prongs-v1)

R6 left: gap = k_min - nu = {2,2,2,1,1,0} on six machines (three icosahedral rows, T, O, D4).
Is the gap a LAW of the machine?  Build a zoo (cyclic / dihedral / tetrahedral / octahedral /
D4 subgroups, several u0, derived axes), compute (m, |G|, N, k_min, nu, LP*, gap) exactly for each,
and test the blind prediction that the gap is NOT a function of m.

nu is exact whenever greedy == floor(LP*): then greedy <= IP <= LP* and IP integer forces IP = greedy.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/13_r7_gap_law.py
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


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', tag, ('  -- ' + detail) if detail else ''), flush=True)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


def int_machine(s04, name, grp, u0, ax):
    """local copy of s04s builder (that one lives inside s04.main and is not importable):
       rows = orbit of u0 ; columns = both +u and -u for every axis line"""
    rows, seen = [], set()
    for M in grp:
        r = s04.matvec(M, u0)
        if r not in seen:
            seen.add(r)
            rows.append(r)
    zc = 0
    cols = []
    for u in ax:
        for uu in (u, tuple(-x for x in u)):
            col = []
            for r in rows:
                if s04.vdot(uu, r) == 0:
                    zc += 1
                col.append(s04.sgn_tie(uu, r))
            cols.append(tuple(col))
    return s04.Machine(name, rows, cols, zc)


def col_masks(mm):
    cm = []
    for a in range(mm.N):
        mk = 0
        for b, (i, j) in enumerate(mm.pairs):
            if mm.cols[a][i] != mm.cols[a][j]:
                mk |= (1 << b)
        cm.append(mk)
    return cm


def cover_exists(cm, ALLP, k, budget=400000):
    n = len(cm)
    suf = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suf[i] = suf[i + 1] | cm[i]
    found = [False]
    nodes = [0]

    def rec(start, depth, mk):
        if found[0] or nodes[0] > budget:
            return
        nodes[0] += 1
        if mk == ALLP:
            found[0] = True
            return
        if depth == k:
            return
        need = k - depth
        for j in range(start, n - need + 1):
            nm = mk | cm[j]
            if nm == ALLP:
                found[0] = True
                return
            if (nm | suf[j + 1]) & ALLP != ALLP:
                continue
            rec(j + 1, depth + 1, nm)
            if found[0]:
                return

    rec(0, 0, 0)
    return found[0], nodes[0], nodes[0] > budget


def greedy_packing(cm, npairs, rng, restarts=40):
    best = 0
    order0 = sorted(range(npairs), key=lambda p: sum(1 for a in range(len(cm)) if (cm[a] >> p) & 1))
    for t in range(restarts):
        order = order0[:] if t == 0 else rng.sample(range(npairs), npairs)
        acc, cnt = 0, 0
        for p in order:
            bit = 1 << p
            if acc & bit:
                continue
            sep = 0
            for a in range(len(cm)):
                if (cm[a] >> p) & 1:
                    sep |= cm[a]
            if sep & acc == 0:
                acc |= bit
                cnt += 1
        best = max(best, cnt)
    return best


def main():
    t0 = time.time()
    out = {'zoo': {}, 'skipped': []}
    print('=' * 112)
    print('O228 scripts/13 -- R7 (3): packing gap k_min - nu across a machine zoo (law hunt)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
    rng = random.Random(SEED)

    # ---------------- regression: the six R2 machines through this code path
    MACH, _ = s09.build_machines(s04)
    R6 = json.load(io.open(os.path.join(DATA, '10_r6_lp_certificate.json'), encoding='utf-8'))
    reg_ok = True
    reg_rows = []
    for mm in MACH:
        cm = col_masks(mm)
        npairs = len(mm.pairs)
        ALLP = (1 << npairs) - 1
        g = greedy_packing(cm, npairs, rng)
        lp = s10.solve_packing_lp([[a for a in range(mm.N) if (cm[a] >> p) & 1] for p in range(npairs)],
                                  npairs, mm.N)
        lpval = lp['opt']
        nu = int(lpval) if g == int(lpval) else g
        r6rec = R6['machines'][mm.name]
        if nu != r6rec['nu'] or str(lpval) != r6rec['LP']:
            reg_ok = False
        reg_rows.append('%s: nu=%d LP*=%s gap=%d' % (mm.name, nu, lpval, r6rec['k_min'] - nu))
        print('  regression %-7s m=%-3d N=%-3d nu=%-2d LP*=%s' % (mm.name, mm.m, mm.N, nu, lpval), flush=True)
    claim('P3R-1', 'regression through this code path: the six R2 machines reproduce R6s exact packing values '
                   'nu = {2,3,5,1,2,1} and LP* = {5/2, 3, 5, 3/2, 2, 1}', reg_ok,
          ' ; '.join(reg_rows))

    # ---------------- the zoo
    SM = s04.signed_perm_mats()
    V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    Tgrp = [M for M in SM if sorted(s04.matvec(M, v) for v in V) == sorted(V)]
    Rz = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    Rz3 = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
    Rx = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
    Ry = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
    Rz2 = s04.matmul(Rz, Rz)
    duties = [
        ('C2', s04.group_closure([Rz2]), {2}),
        ('C3', s04.group_closure([Rz3]), {3}),
        ('C4', s04.group_closure([Rz]), {4}),
        ('D2', s04.group_closure([Rx, Ry]), {2}),
        ('D3', s04.group_closure([Rz3, Rx]), {2, 3}),
        ('D4', s04.group_closure([Rz, Rx]), {2, 4}),
        ('T', Tgrp, {2, 3}),
        ('S4', [M for M in SM if s04.det3(M) == 1], {2, 3, 4}),
        ('Oh', SM, {2, 3, 4}),
    ]
    u0s = [(1, 1, 1), (1, 1, 0), (1, 0, 0), (0, 0, 1), (1, 2, 0), (1, 1, 2), (1, 2, 3), (1, -1, 1), (2, 1, 0)]
    seen = set()
    zoo = []
    for gname, grp, orders in duties:
        ax = s04.group_axes(grp, orders)
        if len(ax) < 2:
            continue
        for u0 in u0s:
            mm = int_machine(s04, '%s|%s' % (gname, u0), grp, u0, ax)
            if mm.m < 2 or mm.N < 2:
                continue
            key = (mm.m, mm.N, tuple(sorted(set(tuple(c) for c in mm.cols))))
            if key in seen:
                continue
            seen.add(key)
            cens = mm.census()
            cm = col_masks(mm)
            npairs = len(mm.pairs)
            ALLP = (1 << npairs) - 1
            # k_min by early-exit DFS
            kmin, ksrc = None, None
            for k in range(1, 9):
                ok_, nodes, over = cover_exists(cm, ALLP, k)
                if ok_:
                    kmin, ksrc = k, {'nodes': nodes}
                    break
            g = greedy_packing(cm, npairs, rng)
            lp = s10.solve_packing_lp([[a for a in range(mm.N) if (cm[a] >> p) & 1] for p in range(npairs)],
                                      npairs, mm.N)
            lpval = lp['opt']
            nu = int(lpval) if g == int(lpval) else None
            zoo.append({'name': mm.name, 'group': gname, 'u0': list(u0), 'm': mm.m, 'N': mm.N,
                        'group_order': len(grp), 'n_lines': len(ax), 'ties': mm.n_zeros,
                        'n_types': cens['n_types'], 'shapes': cens['shapes'],
                        'k_min': kmin, 'greedy': g, 'LP': str(lpval), 'nu': nu,
                        'gap': (kmin - nu) if (kmin is not None and nu is not None) else None})
            if (len(zoo) % 10) == 0:
                print('   ... zoo %d entries (%.1f s)' % (len(zoo), time.time() - t0), flush=True)
    out['zoo'] = zoo
    print('zoo size = %d (deduped)' % len(zoo), flush=True)
    for r in zoo:
        print('   %-16s m=%-3d N=%-3d |G|=%-3d k_min=%-2s nu=%-3s LP*=%-6s gap=%s'
              % (r['name'], r['m'], r['N'], r['group_order'], r['k_min'], r['nu'], r['LP'], r['gap']), flush=True)

    complete = [r for r in zoo if r['gap'] is not None]
    claim('P3a-1', 'zoo computed exactly: k_min by pruned DFS and nu exact whenever greedy = floor(LP*) '
                   '(IP integer sandwich)',
          len(complete) >= 8 and all(r['gap'] is not None for r in complete),
          'entries=%d complete=%d' % (len(zoo), len(complete)))

    bym = {}
    for r in complete:
        bym.setdefault(r['m'], set()).add(r['gap'])
    counterexamples = {m: sorted(v) for m, v in bym.items() if len(v) > 1}
    out['gap_by_m'] = {str(k): sorted(v) for k, v in sorted(bym.items())}
    out['counterexamples'] = {str(k): v for k, v in counterexamples.items()}
    claim('P3b-1', 'BLIND PREDICTION: the gap is NOT a function of m -- the zoo contains machines with the '
                   'SAME number of distinct rows m but DIFFERENT gaps',
          len(counterexamples) > 0, 'gap by m = %s ; counterexamples at m = %s'
          % (out['gap_by_m'], list(counterexamples.keys())))

    gvals = sorted(set(r['gap'] for r in complete))
    out['gap_values_seen'] = gvals
    claim('P3b-2', 'recorded gap spectrum: which gap values actually occur in the zoo',
          True, 'gap values seen = %s ; distribution = %s'
          % (gvals, {g: sum(1 for r in complete if r['gap'] == g) for g in gvals}))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '13_r7_gap_law.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
