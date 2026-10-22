#!/usr/bin/env python3
"""O228 scripts/17 -- R8: critical sub-machine certificate for k_min = 7.

Contract: docs/11_r8_contract.md  (o228-r8-critical-submachine-v1)  -- FROZEN.

Motivation: k_min is monotone under row subsets: R0 subset of rows => k_min(R0) <= k_min(all).
So k_min(R0) = 7 for ANY row subset R0 already yields k_min(all) >= 7 (and <= 7 by the R2 construction).
The hope was that a SMALL R0 admits a short certificate (integral packing >= 7 or exact LP >= 7).

NOTE (recorded, not relaxed): by R6 the FULL family has nu = IP = LP* = 5, and both the integral packing
and the covering LP are MONOTONE in the requirement family (a subfamily is easier to cover, so its packing
and LP values are <= the full one).  Hence P4-3's hoped certificates are a priori <= 5 for every R0, and
P4-3 must fail: no sub-machine can be certified by packing or LP.  The contract is kept as written; the
failure is recorded and the correction (a no-go theorem) carries the -c tag.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/17_r8_critical_submachine.py
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
BUDGET = 2000000          # per cover search
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
    print('O228 scripts/17 -- R8: critical sub-machine for k_min(edge) = 7  (short certificate hunt)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')
    MACH, _ = s09.build_machines(s04)
    edge = [mm for mm in MACH if mm.name == 'M_edge'][0]
    m, N, pairs = edge.m, edge.N, edge.pairs
    NP = len(pairs)
    pindex = {p: b for b, p in enumerate(pairs)}
    pcol = [0] * NP                     # pair -> bitmask over the 62 columns
    cand = [[] for _ in range(NP)]       # pair -> list of columns separating it
    for a in range(N):
        mk = 0
        for b, (i, j) in enumerate(pairs):
            if edge.cols[a][i] != edge.cols[a][j]:
                mk |= (1 << b)
                cand[b].append(a)
        while mk:
            b = (mk & -mk).bit_length() - 1
            mk &= mk - 1
            pcol[b] |= (1 << a)

    def cover6(rows_sub):
        """Decide whether 6 columns separate all rows in rows_sub (i.e. cover its induced pair family)."""
        R = sorted(rows_sub)
        reqpairs = [pindex[(R[i], R[j])] for i in range(len(R)) for j in range(i + 1, len(R))]
        unc0 = 0
        for b in reqpairs:
            unc0 |= (1 << b)
        nodes = [0]
        cmask = [0] * N
        for a in range(N):
            mk = 0
            for b in reqpairs:
                if (pcol[b] >> a) & 1:
                    mk |= (1 << b)
            cmask[a] = mk

        def rec(unc, chosen, depth):
            nodes[0] += 1
            if unc == 0:
                return chosen
            if depth == K or nodes[0] > BUDGET:
                return None
            bb, ob = None, None
            u = unc
            while u:
                b = (u & -u).bit_length() - 1
                u &= u - 1
                opts = [a for a in cand[b] if not (chosen >> a) & 1]
                if not opts:
                    return None
                if ob is None or len(opts) < len(ob):
                    bb, ob = b, opts
                    if len(opts) == 1:
                        break
            for a in ob:
                r = rec(unc & ~cmask[a], chosen | (1 << a), depth + 1)
                if r is not None:
                    return r
                if nodes[0] > BUDGET:
                    return None
            return None

        sol = rec(unc0, 0, 0)
        if sol is not None:
            return 'cover', [a for a in range(N) if (sol >> a) & 1], nodes[0], len(reqpairs)
        return ('no_cover_complete' if nodes[0] <= BUDGET else 'budget_exceeded'), None, nodes[0], len(reqpairs)

    # ---------------- sanity: the full machine must be infeasible for k = 6 (R2's F_6 = 0)
    st, colsol, nodes_full, np_full = cover6(range(m))
    out['full_machine'] = {'status': st, 'nodes': nodes_full, 'n_pairs': np_full}
    print('full machine: %s (nodes %d, pairs %d)' % (st, nodes_full, np_full), flush=True)

    # ---------------- peel: remove rows while infeasibility survives
    R = list(range(m))
    traj = []
    changed = True
    while changed:
        changed = False
        for r in list(R):
            if len(R) <= 3:
                break
            cand_rows = [x for x in R if x != r]
            st2, cs, nd, npq = cover6(cand_rows)
            traj.append({'removed': r, 'kept': len(cand_rows), 'status': st2, 'nodes': nd})
            if st2 == 'no_cover_complete':       # infeasibility survives -> drop r permanently
                R = cand_rows
                changed = True
    out['peel'] = {'final_rows': R, 'n_final_rows': len(R), 'trajectory_len': len(traj),
                   'budget_exceeded_steps': sum(1 for t in traj if t['status'] == 'budget_exceeded'),
                   'trajectory': traj}
    print('peel: |R0| = %d rows %s ; steps %d ; budget-exceeded steps %d'
          % (len(R), R, len(traj), out['peel']['budget_exceeded_steps']), flush=True)

    # ---------------- the final critical sub-machine
    stR, csR, ndR, npR = cover6(R)
    m0 = len(R) * (len(R) - 1) // 2
    print('final R0: status %s (nodes %d, pairs %d)' % (stR, ndR, npR), flush=True)
    assert m0 == npR

    # removal-minimality: every single removal must restore feasibility (or hit the budget)
    removal = []
    for r in R:
        st2, cs2, nd2, _ = cover6([x for x in R if x != r])
        removal.append({'removed': r, 'status': st2, 'nodes': nd2,
                        'cover': cs2})
    out['removal_minimal'] = removal
    minimal_ok = all(x['status'] == 'cover' for x in removal)
    print('removal-minimal: %s  (%d/%d removals give a 6-cover)'
          % (minimal_ok, sum(1 for x in removal if x['status'] == 'cover'), len(removal)), flush=True)

    # ---------------- certificate catalogue for R0
    Rp = [pindex[(R[i], R[j])] for i in range(len(R)) for j in range(i + 1, len(R))]
    # greedy integral packing (multi-restart)
    rng = random.Random(SEED)
    bestp = []
    for t in range(200):
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
    print('R0 catalogue: greedy packing %d ; exact LP %s ; arrangement cap(6) = 32 >= %d'
          % (len(bestp), lpval, len(R)), flush=True)
    out['catalogue'] = {'n_pairs': len(Rp), 'greedy_packing': len(bestp),
                        'greedy_packing_pairs': bestp, 'exact_LP': None if lpval is None else str(lpval),
                        'exhaustive_certificate_nodes': ndR, 'arrangement_cap6': 32}
    out['full_machine_duals'] = {'nu_greedy_full': 5, 'LP_full': '5', 'IP_full': 5,
                                 'note': 'R5/R6: nu = 5 and IP <= LP* = 5, hence IP = 5 exactly'}

    # ---------------- claims
    claim('P4-1', 'A row subset R0 with k_min(R0) = 7 and |R0| <= 16 exists  [BLIND]',
          True and stR == 'no_cover_complete' and len(R) <= 16,
          '|R0| = %d (predicted <= 16) ; status %s' % (len(R), stR))
    claim('P4-2', 'peeling stops at a REMOVAL-MINIMAL R0: removing any single row restores a 6-cover  [BLIND]',
          bool(minimal_ok) and stR == 'no_cover_complete',
          '%d/%d single removals give a 6-cover ; budget-exceeded in peel = %d'
          % (sum(1 for x in removal if x['status'] == 'cover'), len(removal),
             out['peel']['budget_exceeded_steps']))
    claim('P4-3', 'the final R0 admits a SHORT certificate of the packing or LP type (packing >= 7 or LP >= 7)  '
                  '[BLIND]', bool(len(bestp) >= 7 or (lpval is not None and lpval >= 7)),
          'greedy packing = %d ; exact LP = %s -- both <= 5 as the monotonicity no-go predicts'
          % (len(bestp), lpval))
    claim('P4-4', 'the arrangement counting bound alone cannot certify: cap(6) = 32 >= |R0|', 32 >= len(R),
          'cap(6) = 32 ; |R0| = %d' % len(R))
    claim('P4-5', 'RECORD: the critical sub-machine is a strictly smaller certificate instance than the full '
                  'machine: |R0| rows / %d pairs vs %d rows / %d pairs; the exhaustive certificate costs %d '
                  'nodes (budget %d)' % (len(R), len(Rp), m, NP, ndR, BUDGET),
          stR == 'no_cover_complete' and len(Rp) < NP,
          '|R0| = %d rows, %d pairs, exhaustive nodes %d ; full machine %d rows / %d pairs (nodes %d)'
          % (len(R), len(Rp), ndR, m, NP, nodes_full))
    claim('P4-6', 'MONOTONICITY NO-GO: for EVERY row subset the induced pair family is a subfamily of the full '
                  'one, and both the integral packing nu and the covering LP are monotone under requirement '
                  'families; R6 gives nu(full) = IP(full) = LP*(full) = 5, hence nu(R0) <= 5 and LP*(R0) <= 5 '
                  'for every sub-machine. No sub-machine can be certified by packing, LP or any weighted '
                  'counting argument -- the certificate for k_min = 7 must be integral/exhaustive',
          bool(len(bestp) <= 5 and lpval is not None and lpval <= 5),
          'greedy packing = %d, LP = %s (both <= 5) while 7 is needed' % (len(bestp), lpval))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '17_r8_critical_submachine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
