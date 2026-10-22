#!/usr/bin/env python3
"""O228 scripts/10 -- R6: exact rational LP certificate for the set-cover relaxation of k_min.

Contract: docs/07_r6_contract.md   (o228-r6-lp-certificate-v1)

  primal (covering)   min sum_a x_a   s.t.  sum_a A[p][a] x_a >= 1  for every row pair p
  dual   (packing)    max sum_p y_p   s.t.  sum_p A[p][a] y_p <= 1  for every column a

Solved exactly with Fractions and Bland's anti-cycling rule (no floating point anywhere).  The
simplex multipliers of the packing LP give the covering solution, so BOTH optimality certificates
(primal x*, dual y* with equal objective) come out of one run.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/10_r6_lp_certificate.py
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
PIVOT_BUDGET = 20000


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', tag, ('  -- ' + detail) if detail else ''), flush=True)


def load(path, name):
    spc = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spc)
    spc.loader.exec_module(mod)
    return mod


def sep_matrix(mm):
    """A[p] = list of columns separating row pair p ; also the per-column pair masks"""
    A = [[] for _ in range(len(mm.pairs))]
    cm = []
    for a in range(mm.N):
        mk = 0
        for b, (i, j) in enumerate(mm.pairs):
            if mm.cols[a][i] != mm.cols[a][j]:
                mk |= (1 << b)
                A[b].append(a)
        cm.append(mk)
    return A, cm


def solve_packing_lp(A, npairs, ncols, budget=PIVOT_BUDGET):
    """exact simplex (max sum y  s.t.  A^T y <= 1, y >= 0).  Returns dict with everything needed."""
    n_rows = ncols
    n_y = npairs
    n_cols = n_y + n_rows
    T = [[F(0)] * (n_cols + 1) for _ in range(n_rows)]
    for p in range(n_y):
        for a in A[p]:
            T[a][p] = F(1)
    for a in range(n_rows):
        T[a][n_y + a] = F(1)
        T[a][n_cols] = F(1)
    cost = [F(1)] * n_y + [F(0)] * n_rows          # maximise: c = 1 on y, 0 on slacks
    basis = [n_y + a for a in range(n_rows)]       # start: all slacks basic, y = 0 (feasible)
    pivots = 0
    status = 'optimal'
    while True:
        cB = [cost[b] for b in basis]
        # reduced costs rc_j = c_j - sum_r cB[r] * T[r][j]   (only rows with cB != 0 contribute)
        hot = [r for r in range(n_rows) if cB[r] != 0]
        entering = -1
        for j in range(n_cols):
            s = cost[j]
            for r in hot:
                s -= T[r][j]
            if s > 0:
                entering = j
                break
        if entering < 0:
            break
        leaving, best = -1, None
        for r in range(n_rows):
            tr = T[r][entering]
            if tr > 0:
                ratio = T[r][n_cols] / tr
                if best is None or ratio < best or (ratio == best and basis[r] < basis[leaving]):
                    best, leaving = ratio, r
        if leaving < 0:
            return {'status': 'unbounded', 'pivots': pivots}
        piv = T[leaving][entering]
        T[leaving] = [v / piv for v in T[leaving]]
        for r in range(n_rows):
            if r != leaving and T[r][entering] != 0:
                f = T[r][entering]
                T[r] = [v - f * w for v, w in zip(T[r], T[leaving])]
        basis[leaving] = entering
        pivots += 1
        if pivots > budget:
            return {'status': 'pivot-budget-exceeded', 'pivots': pivots}
    cB = [cost[b] for b in basis]
    obj = sum((cB[r] * T[r][n_cols] for r in range(n_rows)), F(0))
    y = [F(0)] * n_y
    for r in range(n_rows):
        if basis[r] < n_y:
            y[basis[r]] = T[r][n_cols]
    # simplex multipliers = dual values = the covering solution x (slack columns hold B^{-1})
    x = [F(0)] * n_rows
    for a in range(n_rows):
        s = F(0)
        for r in range(n_rows):
            if cB[r] != 0:
                s += T[r][n_y + a]
        x[a] = s
    return {'status': status, 'pivots': pivots, 'opt': obj, 'x': x, 'y': y, 'basis': basis[:]}


def verify_certificate(A, npairs, ncols, res):
    """exact checks: primal feasible, dual feasible, objectives equal"""
    x, y = res['x'], res['y']
    primal_ok = all(v >= 0 for v in x)
    cover_ok = True
    for p in range(npairs):
        s = sum((x[a] for a in A[p]), F(0))
        if s < 1:
            cover_ok = False
            break
    dual_ok = all(v >= 0 for v in y)
    pack_ok = True
    for a in range(ncols):
        s = sum((y[p] for p in range(npairs) if a in A[p]), F(0))
        if s > 1:
            pack_ok = False
            break
    sx = sum(x, F(0))
    sy = sum(y, F(0))
    return {'primal_nonneg': primal_ok, 'primal_covers': cover_ok, 'dual_nonneg': dual_ok,
            'dual_packs': pack_ok, 'sum_x': sx, 'sum_y': sy,
            'objectives_equal': sx == sy == res['opt']}


def main():
    t0 = time.time()
    out = {'claims': None}
    print('=' * 112)
    print('O228 scripts/10 -- R6: exact rational LP certificate (set-cover relaxation of k_min)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    MACH, _ = s09.build_machines(s04)
    R2 = json.load(io.open(os.path.join(DATA, '04_r2_general_machine.json'), encoding='utf-8'))
    R5 = json.load(io.open(os.path.join(DATA, '09_r5_kmin_law.json'), encoding='utf-8'))
    kmin = {n: int(R2['k_min_final'][n]) for n in R2['k_min_final']}
    nu = {n: R5['packing'][n]['nu'] for n in R5['packing']}

    out['machines'] = {}
    l1_ok, l2_ok = True, True
    for mm in MACH:
        A, cm = sep_matrix(mm)
        npairs, ncols = len(mm.pairs), mm.N
        res = solve_packing_lp(A, npairs, ncols)
        cert = verify_certificate(A, npairs, ncols, res) if res.get('opt') is not None else None
        lam = [len(A[p]) for p in range(npairs)]
        lam_min, lam_max = min(lam), max(lam)
        support = [a for a in range(ncols) if res['x'][a] > 0]
        tight = [p for p in range(npairs) if sum((res['x'][a] for a in A[p]), F(0)) == 1]
        rec = {'n_pairs': npairs, 'n_cols': ncols, 'status': res['status'], 'pivots': res['pivots'],
               'LP': str(res['opt']), 'LP_float': float(res['opt']), 'nu': nu[mm.name], 'k_min': kmin[mm.name],
               'lambda_min': lam_min, 'lambda_max': lam_max, 'uniform_bound': str(F(ncols, lam_min)),
               'support_size': len(support), 'support': support, 'n_tight_pairs': len(tight),
               'tight_pairs_sample': tight[:12], 'certificate': cert}
        out['machines'][mm.name] = rec
        print('  %-7s LP* = %-12s (%.6f)  nu=%-2d k_min=%-2d  lambda_min=%-2d  support=%-3d tight=%-4d pivots=%d'
              % (mm.name, rec['LP'], rec['LP_float'], rec['nu'], rec['k_min'], lam_min, len(support),
                 len(tight), res['pivots']), flush=True)
        if not (F(rec['nu']) <= res['opt'] <= F(rec['k_min'])):
            l1_ok = False
        if not (cert['primal_nonneg'] and cert['primal_covers'] and cert['dual_nonneg'] and cert['dual_packs']
                and cert['objectives_equal']):
            l2_ok = False

    claim('L1-1', 'weak duality sandwich holds on all six machines: nu (integral packing, R5) <= LP* <= k_min',
          l1_ok, ' ; '.join('%s: nu=%d <= LP*=%s <= k_min=%d' % (n, out['machines'][n]['nu'],
                                                               out['machines'][n]['LP'], out['machines'][n]['k_min'])
                            for n in out['machines']))
    claim('L2-1', 'exact certificate pair for every machine: x* >= 0 covers every pair, y* >= 0 packs every '
                  'column, and sum x* = sum y* = LP* -- so LP* is optimal BY ARITHMETIC, not by trusting the '
                  'simplex', l2_ok,
          ' ; '.join('%s: sum_x=%s sum_y=%s opt=%s' % (n, out['machines'][n]['certificate']['sum_x'],
                                                      out['machines'][n]['certificate']['sum_y'],
                                                      out['machines'][n]['LP']) for n in out['machines']))

    e = out['machines']['M_edge']
    lp_edge = F(e['LP'])
    claim('L3-1', 'BLIND PREDICTION: LP*(M_edge) < 7, i.e. the set-cover LP relaxation does NOT reach the '
                  'integral optimum -- the LP route cannot certify k_min(M_edge) = 7',
          lp_edge < 7, 'LP*(M_edge) = %s = %.6f ; k_min = %d' % (e['LP'], e['LP_float'], e['k_min']))
    claim('L3-2', 'COROLLARY (registered either way): since LP* <= k_min = 7 always, LP*(M_edge) = 7 would have '
                  'been a certificate; the measured value settles whether the LP route lives or dies',
          lp_edge <= 7, 'LP* = %s ; gap to k_min = %s' % (e['LP'], F(e['k_min']) - lp_edge))
    claim('L4-1', 'BLIND PREDICTION: the hardest row pair of M_edge is separated by lambda_min in [8, 12] columns',
          8 <= e['lambda_min'] <= 12, 'lambda_min = %d (max = %d) ; uniform bound 62/lambda_min = %s = %.4f'
          % (e['lambda_min'], e['lambda_max'], e['uniform_bound'], float(F(62, e['lambda_min']))))
    claim('L5-1', 'BLIND PREDICTION: the primal optimum spreads over MORE than k_min columns '
                  '(|support(x*)| > k_min) -- no 7-column certificate hides in the fractional optimum',
          e['support_size'] > e['k_min'], 'support = %d columns vs k_min = %d' % (e['support_size'], e['k_min']))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '10_r6_lp_certificate.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
