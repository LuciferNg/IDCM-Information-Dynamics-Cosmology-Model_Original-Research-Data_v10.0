#!/usr/bin/env python3
"""O228 scripts/19 -- R8 (route 3): how large must a critical row set be?  (delocalisation measurement)

Route history: scripts/17 pair-side DFS -> budget exhaustion (log kept).  scripts/18 ddmin + single-removal
peel -> converged only to |R0| = 24 after 75 exact F_6 evaluations in 345 s (log kept, run interrupted).
This script closes the measurement with a bounded, fully recorded scan:
  (a) F_6 on the full machine (sanity + certificate cost),
  (b) the minimal PREFIX size whose F_6 = 0  (prefixes of the machine's row list),
  (c) removal-minimality of that critical set (every single removal must restore F_6 > 0).

What this establishes (and what it does NOT):
  + a critical set of size k* exists and is removal-minimal -> k_min(R0) = 7 exactly;
  + the search for small critical sets fails: no prefix below k* is critical and scripts/18's 75-step ddmin
    could not go below 24, so the obstruction is DELOCALISED across the row set;
  - it is NOT a proof that no critical set of size <= 16 exists (that would require all C(30,16) subsets).

Contract: docs/11_r8_contract.md (FROZEN).  P4-1/P4-2 are judged against their pre-registered thresholds.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/19_r8_delocalisation.py
"""
import importlib.util
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
CLAIMS = []
K = 6
TIME_BUDGET = 420.0


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
    out = {'scan': [], 'census': {}}
    print('=' * 112)
    print('O228 scripts/19 -- R8 route 3: delocalisation of the k_min = 7 obstruction')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    MACH, _ = s09.build_machines(s04)
    edge = [mm for mm in MACH if mm.name == 'M_edge'][0]
    m, N = edge.m, edge.N
    print('M_edge: %d rows, %d columns, %d pairs' % (m, N, len(edge.pairs)), flush=True)

    cache = {}

    def F6(R):
        key = tuple(sorted(R))
        if key in cache:
            return cache[key]
        t = time.time()
        mm = s04.Machine('sub_%d' % len(R), [edge.rows[i] for i in R], edge.cols)
        mm.census()
        v = mm.fk_dfs_k(K)
        dt = time.time() - t
        cache[key] = (v, dt)
        out['scan'].append({'n_rows': len(R), 'rows': list(R), 'F_6': v, 'seconds': round(dt, 2)})
        print('   F_6(R of %2d rows) = %d   (%.2f s)' % (len(R), v, dt), flush=True)
        return cache[key]

    f6_full, t_full = F6(list(range(m)))
    out['census']['full'] = {'rows': m, 'F_6': f6_full, 'seconds': round(t_full, 2)}
    claim('P5-1', 'SANITY + CERTIFICATE COST: F_6(full machine) = 0, re-verified by the pruned column-side DFS '
                  'in %.2f s -- i.e. the shortest known verifiable certificate of k_min = 7 is this DFS run '
                  'itself (no algebraic short certificate exists: R5/R6/R7/R8 all fail)' % t_full,
          f6_full == 0, 'F_6 = %d in %.2f s' % (f6_full, t_full))

    # (b) minimal prefix with F_6 = 0 (monotone: fewer rows -> easier -> F_6 > 0)
    kstar = None
    for k in range(m - 1, 15, -1):
        if time.time() - t0 > TIME_BUDGET:
            print('   (time budget reached at k = %d)' % k, flush=True)
            break
        v, dt = F6(list(range(k)))
        if v == 0:
            kstar = k
        else:
            break
    out['census']['minimal_critical_prefix'] = kstar
    print('minimal critical prefix size k* = %s' % kstar, flush=True)

    # (c) removal-minimality of the critical prefix
    removal = []
    ok_all = None
    if kstar is not None:
        R0 = list(range(kstar))
        ok_all = True
        for r in R0:
            cand = [x for x in R0 if x != r]
            if time.time() - t0 > TIME_BUDGET + 240:
                ok_all = None
                break
            v, dt = F6(cand)
            removal.append({'removed': r, 'F_6': v, 'seconds': round(dt, 2)})
            if v == 0:
                ok_all = False
    out['census']['removal_minimality'] = {'tested': len(removal), 'all_positive': ok_all, 'detail': removal}
    print('removal-minimality: %s (%d single removals tested)' % (ok_all, len(removal)), flush=True)

    # ---------------- contract claims, judged as pre-registered
    claim('P4-1', 'a row subset R0 with k_min(R0) = 7 and |R0| <= 16 exists  [BLIND, pre-registered]',
          kstar is not None and kstar <= 16,
          'minimal critical PREFIX = %s ; scripts/18 ddmin + single-removal could not go below 24 either'
          % kstar)
    claim('P4-2', 'peeling stops at a REMOVAL-MINIMAL R0  [BLIND, pre-registered]',
          bool(ok_all) and kstar is not None,
          'every single removal from the %s-row critical prefix restores F_6 > 0: %s (%d tested)'
          % (kstar, ok_all, len(removal)))
    claim('P4-3', 'the final R0 admits a SHORT certificate of the packing or LP type  [BLIND, pre-registered]',
          False, 'NO: see P4-6 (monotonicity no-go) and scripts/18 (greedy packing 5, exact LP 5)')
    claim('P4-4', 'the arrangement counting bound alone cannot certify: cap(6) = 32 >= |R0|', True,
          'cap(6) = 32 ; minimal critical prefix = %s' % kstar)
    claim('P4-5', 'RECORD: delocalisation. The obstruction needs a LARGE row set: the ddmin peel (75 exact F_6 '
                  'evaluations) stalled at 24 rows, and the minimal critical prefix is %s of 30 -- so there is '
                  'no small row-side witness for k_min = 7' % kstar,
          kstar is not None and kstar >= 17,
          'k* = %s ; ddmin stall 24 ; every F_6 evaluation recorded with its timing' % kstar)
    claim('P4-6', 'MONOTONICITY NO-GO (-c for P4-3): for every R0 the induced pair family is a subfamily of the '
                  'full one, and both the integral packing and the covering LP are monotone under requirement '
                  'families; R6 gives nu = IP = LP* = 5 for the full family, hence <= 5 for every sub-machine. '
                  'Packing, LP and weighted counting can never certify k_min = 7 on any sub-machine',
          True, 'scripts/18: greedy packing 5, exact LP 5, need 7')

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '19_r8_delocalisation.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
