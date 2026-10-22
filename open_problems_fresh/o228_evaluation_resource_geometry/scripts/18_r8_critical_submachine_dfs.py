#!/usr/bin/env python3
"""O228 scripts/18 -- R8 (route 2): critical sub-machine, decided by the pruned column-side DFS.

Route history: scripts/17 used a pair-side most-constrained DFS (as in R7); for INFEASIBLE instances the
branching factor explodes and every call hit the 2M budget, so the peel could not decide anything (log kept).
This script uses scripts/04's `Machine.fk_dfs_k`, i.e. the suffix-union pruned DFS over COLUMN subsets, the
same algorithm that re-verified F_5 = F_6 = 0 in R5 within seconds.

Decisions:
  k_min(R0) >= 7   <=>   F_6(R0) = 0   (no 6-subset of the 62 columns separates all rows of R0)
Hence the peel is a sequence of exact, cheap F_6 computations, and the final certificate is:
  (a) F_6(R0) = 0 (pruned DFS, exact)  +  (b) an explicit 6-column cover for every single-row removal
      => k_min(R0) = 7 exactly and R0 is removal-minimal.

Contract: docs/11_r8_contract.md (o228-r8-critical-submachine-v1), FROZEN -- including P4-3, which the
monotonicity argument (R6: nu = IP = LP* = 5 for the full family, both monotone under subfamilies) already
falsifies a priori; it is kept and recorded as FAIL with the no-go as its -c correction.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/18_r8_critical_submachine_dfs.py
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
    print('O228 scripts/18 -- R8 route 2: critical sub-machine via the pruned column-side DFS (F_6)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
    MACH, _ = s09.build_machines(s04)
    edge = [mm for mm in MACH if mm.name == 'M_edge'][0]
    m, N, pairs = edge.m, edge.N, edge.pairs
    NP = len(pairs)
    pindex = {p: b for b, p in enumerate(pairs)}
    pcol = [0] * NP
    for a in range(N):
        for b, (i, j) in enumerate(pairs):
            if edge.cols[a][i] != edge.cols[a][j]:
                pcol[b] |= (1 << a)

    def sub_machine(R):
        mm = s04.Machine('sub_%d' % len(R), [edge.rows[i] for i in R], edge.cols)
        mm.census()
        return mm

    def F6(R):
        """exact pruned-DFS count of 6-column subsets separating all rows of R (0 <=> k_min(R) >= 7)"""
        t = time.time()
        v = sub_machine(R).fk_dfs_k(K)
        return v, time.time() - t

    f6_full, t_full = F6(range(m))
    out['full_machine'] = {'F_6': f6_full, 'seconds': round(t_full, 2), 'rows': m, 'pairs': NP}
    print('full machine: F_6 = %d  (%.2f s)  -- 0 confirms no 6-subset separates all %d rows' %
          (f6_full, t_full, m), flush=True)

    # ---------------- peel: ddmin (delta-debugging) then single removals, F_6 cheap on small subsets
    R = list(range(m))
    traj = []

    def try_keep(cand_rows, tag):
        v, dt = F6(cand_rows)
        traj.append({'tag': tag, 'n_rows_kept': len(cand_rows), 'F_6': v, 'seconds': round(dt, 2)})
        return v == 0

    n = 2
    while len(R) >= 2:
        chunk = (len(R) + n - 1) // n
        reduced = False
        for i in range(0, len(R), chunk):
            cand_rows = R[:i] + R[i + chunk:]
            if not cand_rows:
                continue
            if try_keep(cand_rows, 'ddmin n=%d' % n):
                R = cand_rows
                n = max(n - 1, 2)
                reduced = True
                break
        if not reduced:
            if n >= len(R):
                break
            n = min(2 * n, len(R))
    changed = True
    while changed:
        changed = False
        for r in list(R):
            cand_rows = [x for x in R if x != r]
            if not cand_rows:
                continue
            if try_keep(cand_rows, 'single removal %d' % r):
                R = cand_rows
                changed = True
    out['peel'] = {'final_rows': R, 'n_final_rows': len(R), 'steps': len(traj),
                   'seconds': round(sum(t['seconds'] for t in traj), 1), 'trajectory': traj}
    print('peel: |R0| = %d  R0 = %s  (steps %d, %.1f s)' % (len(R), R, len(traj), out['peel']['seconds']),
          flush=True)

    f6_R0, t_R0 = F6(R)
    n_pairs_R0 = len(R) * (len(R) - 1) // 2
    print('R0: F_6 = %d (%.2f s) ; pairs %d' % (f6_R0, t_R0, n_pairs_R0), flush=True)

    # ---------------- removal-minimality with EXPLICIT covers (feasibility witnesses)
    def explicit_cover(rows_sub):
        """greedy + fallback exhaustive search for 6 columns separating rows_sub; returns a column list or None"""
        Rp = [pindex[(rows_sub[i], rows_sub[j])] for i in range(len(rows_sub))
              for j in range(i + 1, len(rows_sub))]
        ALLP = 0
        for b in Rp:
            ALLP |= (1 << b)
        cm = []
        for a in range(N):
            mk = 0
            for b in Rp:
                if (pcol[b] >> a) & 1:
                    mk |= (1 << b)
            cm.append(mk)
        found = [None]

        def rec(unc, chosen, depth):
            if found[0] is not None:
                return
            if unc == 0:
                found[0] = [a for a in range(N) if (chosen >> a) & 1]
                return
            if depth == K:
                return
            bb, ob = None, None
            u = unc
            while u:
                b = (u & -u).bit_length() - 1
                u &= u - 1
                opts = [a for a in range(N) if (cm[a] >> b) & 1 and not (chosen >> a) & 1]
                if not opts:
                    return
                if ob is None or len(opts) < len(ob):
                    bb, ob = b, opts
                    if len(opts) == 1:
                        break
            for a in ob:
                rec(unc & ~cm[a], chosen | (1 << a), depth + 1)

        rec(ALLP, 0, 0)
        return found[0]

    removal = []
    for r in R:
        cov = explicit_cover([x for x in R if x != r])
        f6v, _ = F6([x for x in R if x != r])
        removal.append({'removed': r, 'F_6_after_removal': f6v, 'explicit_6_cover': cov})
    out['removal_minimality'] = removal
    minimal_ok = all(x['explicit_6_cover'] is not None and x['F_6_after_removal'] > 0 for x in removal)
    print('removal-minimal: %s (%d/%d removals give an explicit 6-cover)'
          % (minimal_ok, sum(1 for x in removal if x['explicit_6_cover'] is not None), len(removal)), flush=True)

    # ---------------- catalogue: packing / LP / counting bounds for R0
    Rp = [pindex[(R[i], R[j])] for i in range(len(R)) for j in range(i + 1, len(R))]
    rng = random.Random(SEED)
    bestp = []
    for t in range(300):
        pool = list(Rp)
        if t:
            rng.shuffle(pool)
        sel, used = [], 0
        for b in pool:
            if pcol[b] & used == 0:
                sel.append(b)
                used |= pcol[b]
        if len(sel) > len(bestp):
            bestp = list(sel)
    Ares = [[a for a in range(N) if (pcol[b] >> a) & 1] for b in Rp]
    lp = s10.solve_packing_lp(Ares, len(Rp), N)
    lpval = lp.get('opt')
    out['catalogue'] = {'n_pairs': len(Rp), 'greedy_packing': len(bestp), 'greedy_packing_pairs': bestp,
                        'exact_LP': None if lpval is None else str(lpval),
                        'arrangement_cap6': 32, 'F_6_certificate_seconds': round(t_R0, 2),
                        'full_machine_reference': {'rows': m, 'pairs': NP, 'F_6': f6_full,
                                                   'F_6_seconds': round(t_full, 2)},
                        'nu_full': 5, 'IP_full': 5, 'LP_full': '5'}
    print('R0 catalogue: greedy packing %d ; exact LP %s ; cap(6) = 32 ; F_6 certificate %.2f s (full: %.2f s)'
          % (len(bestp), lpval, t_R0, t_full), flush=True)

    # ---------------- claims (contract order)
    claim('P4-1', 'a row subset R0 with k_min(R0) = 7 and |R0| <= 16 exists  [BLIND]',
          f6_R0 == 0 and len(R) <= 16, '|R0| = %d (predicted <= 16), F_6(R0) = %d' % (len(R), f6_R0))
    claim('P4-2', 'peeling stops at a REMOVAL-MINIMAL R0 (every single removal restores a 6-cover)  [BLIND]',
          bool(minimal_ok) and f6_R0 == 0,
          '%d/%d removals give an EXPLICIT 6-cover ; peel steps %d' %
          (sum(1 for x in removal if x['explicit_6_cover'] is not None), len(removal), len(traj)))
    claim('P4-3', 'the final R0 admits a SHORT certificate of the packing or LP type (packing >= 7 or LP >= 7) '
                  '[BLIND]  -- pre-registered; a priori false by monotonicity, see P4-6',
          bool(len(bestp) >= 7 or (lpval is not None and lpval >= 7)),
          'greedy packing = %d, exact LP = %s (need 7); both <= 5 as the monotonicity no-go predicts'
          % (len(bestp), lpval))
    claim('P4-4', 'the arrangement counting bound alone cannot certify R0: cap(6) = 32 >= |R0|',
          32 >= len(R), 'cap(6) = 32 ; |R0| = %d' % len(R))
    claim('P4-5', 'RECORD: the critical sub-machine is a strictly smaller and FASTER certificate instance: '
                  '%d rows / %d pairs / F_6 certificate %.2f s, versus the full machine %d rows / %d pairs / '
                  '%.2f s' % (len(R), len(Rp), t_R0, m, NP, t_full),
          f6_R0 == 0 and len(Rp) < NP and t_R0 < t_full,
          '%d rows, %d pairs, %.2f s  vs  %d rows, %d pairs, %.2f s'
          % (len(R), len(Rp), t_R0, m, NP, t_full))
    claim('P4-6', 'MONOTONICITY NO-GO (the -c for P4-3): the induced pair family of any R0 is a subfamily of '
                  'the full one, and both the integral packing nu and the covering LP are monotone under '
                  'requirement families; R6 gives nu(full) = IP(full) = LP*(full) = 5, so nu(R0) <= 5 and '
                  'LP*(R0) <= 5 for EVERY sub-machine. No sub-machine can be certified by packing, LP or any '
                  'weighted counting argument; the certificate for k_min = 7 must be integral (exhaustive)',
          bool(len(bestp) <= 5 and lpval is not None and lpval <= 5),
          'greedy packing = %d, LP = %s while 7 is required' % (len(bestp), lpval))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '18_r8_critical_submachine_dfs.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
