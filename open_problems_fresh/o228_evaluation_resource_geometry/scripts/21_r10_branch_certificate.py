#!/usr/bin/env python3
"""O228 scripts/21 -- R10 (fixed indexings): non-convex (B&B) certificate attempt for k_min(edge) = 7.

Contract: docs/15_r10_contract.md   (o228-r10-branch-certificate-v1)  -- FROZEN.

ROUTE HISTORY (kept honestly): the first version of this script confused the two indexings -- it used
S[a] (the set of columns separating PAIR a) as if it were the set of pairs covered by COLUMN a.  For M_edge
this silently produced a semantically meaningless tree (no crash, 62 <= 435) and for the smaller machines it
crashed with IndexError.  That log is kept: logs/21_r10_branch_certificate.out (route-history block).  This
version builds CP[a] = the pair-mask covered by column a explicitly and uses S[p] for pairs only.

Why no convex certificate can exist: any fractional / weighted / counting lower bound equals the value of
some feasible dual vector y >= 0, and restricting to a subfamily only relaxes the LP, so every such bound is
<= LP*(full) = 5 < 7 (R6).  Breaking 5 needs NON-CONVEX (integrality) information:

    root: cover = min sum x_a s.t. all pairs, LP = 5
    branch on the MOST CONSTRAINED pair p: for each candidate column a of p, the case "a in cover" gives
        child_a = (R \\ CP[a], C \\ {a}) with bound 1 + certified(child_a)
    certify a node iff EVERY branch is certified; node bound = min over branches
    leaf: LP >= target, or R is empty.
An explicit target-size cover (upper bound) then completes the certificate.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/21_r10_branch_certificate.py
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
TARGET = 7
NODE_BUDGET = 200000
DEPTH_CAP = 6


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
    print('O228 scripts/21 -- R10 (fixed indexings): B&B certificate attempt for k_min(edge) = 7')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
    s10 = load(os.path.join(HERE, '10_r6_lp_certificate.py'), 's10')

    def prep(mm):
        NP = len(mm.pairs)
        S = []
        for p in range(NP):
            s = 0
            for a in range(mm.N):
                if mm.cols[a][mm.pairs[p][0]] != mm.cols[a][mm.pairs[p][1]]:
                    s |= (1 << a)
            S.append(s)
        CP = [0] * mm.N
        for a in range(mm.N):
            m = 0
            for p in range(NP):
                if (S[p] >> a) & 1:
                    m |= (1 << p)
            CP[a] = m
        return NP, S, CP

    def lp(Rmask, Cmask, NP, S, N):
        cols = [a for a in range(N) if (Cmask >> a) & 1]
        rows = [p for p in range(NP) if (Rmask >> p) & 1]
        if not rows:
            return F(0), [], None
        A = []
        for p in rows:
            avail = [i for i, a in enumerate(cols) if (S[p] >> a) & 1]
            if not avail:
                return None, None, 'infeasible'
            A.append(avail)
        lpout = s10.solve_packing_lp(A, len(A), len(cols))
        return lpout['opt'], lpout['x'], None

    def prove(NP, S, CP, N, Rmask, Cmask, target, tree, state):
        """certified lower bound of the node, or None when it could not be certified within the budget"""
        state['nodes'] += 1
        state['maxdepth'] = max(state.get('maxdepth', 0), state['depth'])
        if state['nodes'] > NODE_BUDGET or (time.time() - state['t0']) > state['wall']:
            return None
        lb, x, flag = lp(Rmask, Cmask, NP, S, N)
        node = {'R': bin(Rmask).count('1'), 'C': bin(Cmask).count('1'), 'depth': state['depth'],
                'lb': None if lb is None else str(lb), 'status': flag or 'lp'}
        tree.append(node)
        if flag == 'infeasible':
            node['status'] = 'infeasible'
            return None
        if Rmask == 0:
            node['status'] = 'covered'
            return F(0)
        if lb >= target:
            node['status'] = 'leaf_bound'
            return lb
        if state['depth'] >= DEPTH_CAP:
            node['status'] = 'depth_cap'
            return None
        best_p, best_opts = None, None
        rm = Rmask
        while rm:
            p = (rm & -rm).bit_length() - 1
            rm &= rm - 1
            opts = [a for a in range(N) if ((S[p] >> a) & 1) and ((Cmask >> a) & 1)]
            if not opts:
                node['status'] = 'pair_uncoverable'
                return None
            if best_opts is None or len(opts) < len(best_opts):
                best_p, best_opts = p, opts
                if len(opts) == 1:
                    break
        node['branch_pair'] = best_p
        node['branch_options'] = best_opts
        state['depth'] += 1
        children, bounds = [], []
        for a in best_opts:
            child = {'case': 'pair %d covered by column %d' % (best_p, a), 'children': []}
            b = prove(NP, S, CP, N, Rmask & ~CP[a], Cmask & ~(1 << a), target, child['children'], state)
            child['own_bound'] = None if b is None else str(1 + b)
            children.append(child)
            bounds.append(None if b is None else 1 + b)
        state['depth'] -= 1
        node['children'] = children
        if any(b is None for b in bounds):
            node['status'] = 'uncertified_branch'         # cannot conclude: a branch is not yet closed
            state['open'] = state.get('open', 0) + 1
            state.setdefault('open_frac', []).append(
                sum(1 for b in bounds if b is None) / float(len(bounds)))
            state.setdefault('open_R', []).append(bin(Rmask).count('1'))
            return None
        bound = min(bounds)
        node['bound'] = str(bound)
        node['status'] = 'branch'
        # closed lemma: this whole subtree is now certified (measure of how FAR the proof got)
        state.setdefault('closed', []).append(bin(Rmask).count('1'))
        state.setdefault('closed_bounds', []).append(str(bound))
        if state['nodes'] % 5 == 0:
            print('   ... B&B %d nodes, depth %d, R=%d C=%d, %.0f s'
                  % (state['nodes'], state['depth'], bin(Rmask).count('1'), bin(Cmask).count('1'),
                     time.time() - state['t0']), flush=True)
        return bound

    def depth_of(tr):
        d = 0
        for n in tr:
            if n.get('children'):
                d = max(d, 1 + depth_of(n['children']))
        return d

    def reverify(tr, Rmask, Cmask, bad):
        for n in tr:
            lb, x, flag = lp(Rmask, Cmask, NP, S, edge.N)
            want = None if n['lb'] is None else F(n['lb'])
            if flag == 'infeasible':
                if n['status'] != 'infeasible':
                    bad.append(('status', n.get('lb'), flag))
            elif want is None or lb != want:
                bad.append(('value', n.get('lb'), None if lb is None else str(lb)))
            opts = n.get('branch_options')
            ch = n.get('children') or []
            if opts and ch and len(opts) == len(ch):
                for a, cc in zip(opts, ch):
                    reverify(cc['children'], Rmask & ~CP[a], Cmask & ~(1 << a), bad)

    MACH, _ = s09.build_machines(s04)
    edge = [mm for mm in MACH if mm.name == 'M_edge'][0]
    NP, S, CP = prep(edge)
    ALLR, ALLC = (1 << NP) - 1, (1 << edge.N) - 1

    # ---------------- (1) the B&B certificate attempt for M_edge
    tree, state = [], {'nodes': 0, 'depth': 0, 't0': time.time(), 'wall': 100.0}
    t = time.time()
    bound = prove(NP, S, CP, edge.N, ALLR, ALLC, TARGET, tree, state)
    dt = time.time() - t
    dep = depth_of(tree)
    out['edge_certificate'] = {'bound': None if bound is None else str(bound), 'nodes': state['nodes'],
                               'depth': dep // 2, 'depth_true': state.get('maxdepth', 0),
                               'closed_lemmas': len(state.get('closed', [])),
                               'closed_max_R': max(state.get('closed', [0]) or [0]),
                               'open_nodes': state.get('open', 0),
                               'open_max_R': max(state.get('open_R', [0]) or [0]),
                               'closed_R_hist': sorted(set(state.get('closed', [])))[:12],
                               'seconds': round(dt, 2), 'tree': tree}
    print('M_edge B&B: bound = %s ; nodes = %d ; depth = %d ; %.1f s' % (bound, state['nodes'], dep, dt),
          flush=True)
    claim('P8-1', 'an exact-rational B&B tree certifies k_min(M_edge) >= 7 with <= 40 nodes  [BLIND]',
          bound is not None and bound >= TARGET and state['nodes'] <= 40,
          'bound = %s ; nodes = %d (predicted <= 40)' % (bound, state['nodes']))
    claim('P8-2', 'the proof tree has depth <= 4 (nested branch levels)  [BLIND]',
          state.get('maxdepth', 0) <= 4, 'true depth = %d (DEPTH_CAP %d; raw tree levels = %d)'
          % (state.get('maxdepth', 0), DEPTH_CAP, dep))

    # ---------------- (2) independent re-verification of every recorded node's LP value
    bad = []
    reverify(tree, ALLR, ALLC, bad)
    out['reverify'] = {'mismatches': len(bad), 'examples': bad[:3]}
    print('re-verification of every node: %d mismatches' % len(bad), flush=True)
    claim('P8-3', 'every recorded node carries an exact Fraction LP value and re-solving each node from '
                  'scratch reproduces it (0 mismatches)  [BLIND]', len(bad) == 0,
          '%d mismatches over %d nodes' % (len(bad), state['nodes']))

    # ---------------- (3) explicit 7-column cover (upper bound)
    def find_cover(target_k, budget=4000000):
        cols = [CP[a] for a in range(edge.N)]
        n = len(cols)
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suf[i] = suf[i + 1] | cols[i]
        found, nodes = [None], [0]

        def rec(start, depth, mk, chosen):
            nodes[0] += 1
            if found[0] is not None or nodes[0] > budget:
                return
            if mk == ALLR:
                found[0] = list(chosen)
                return
            if depth == target_k:
                return
            need = target_k - depth
            for j in range(start, n - need + 1):
                nm = mk | cols[j]
                if nm | suf[j + 1] != ALLR:
                    continue
                rec(j + 1, depth + 1, nm, chosen + [j])
                if found[0] is not None:
                    return

        rec(0, 0, 0, [])
        return found[0], nodes[0]

    cov, cnodes = find_cover(TARGET)
    ok_cov = False
    if cov is not None:
        m2 = 0
        for a in cov:
            m2 |= CP[a]
        ok_cov = (m2 == ALLR) and len(cov) == TARGET
    out['explicit_cover'] = {'columns': cov, 'size': None if cov is None else len(cov),
                             'covers_all': ok_cov, 'nodes': cnodes}
    print('explicit %d-cover: %s (search nodes %d, covers all = %s)' % (TARGET, cov, cnodes, ok_cov),
          flush=True)
    claim('P8-4', 'an EXPLICIT 7-column cover re-verifies as separating all 435 pairs (upper bound); with a '
                  'certified tree (lower bound) this completes k_min = 7', ok_cov,
          'columns = %s ; all pairs covered = %s' % (cov, ok_cov))

    # ---------------- (4) same machinery on the six R2 machines
    R2K = {'M_2I': 4, 'M_face': 5, 'M_edge': 7, 'M_T': 2, 'M_O': 3, 'M_D4': 1}
    six = []
    for mm in MACH:
        NPx, Sx, CPx = prep(mm)
        tr, st = [], {'nodes': 0, 'depth': 0, 't0': time.time(), 'wall': 12.0}
        b = prove(NPx, Sx, CPx, mm.N, (1 << NPx) - 1, (1 << mm.N) - 1, R2K[mm.name], tr, st)
        six.append({'machine': mm.name, 'k_min': R2K[mm.name], 'bound': None if b is None else str(b),
                    'nodes': st['nodes'], 'depth': depth_of(tr)})
        print('  %-7s k_min=%d -> tree bound %s (%d nodes, depth %d)'
              % (mm.name, R2K[mm.name], b, st['nodes'], depth_of(tr)), flush=True)
    out['six_machines'] = six
    claim('P8-5', 'the same machinery reproduces k_min = {4,5,7,2,3,1} for the six R2 machines  [BLIND]',
          all(r['bound'] is not None and F(r['bound']) >= r['k_min'] for r in six),
          ' ; '.join('%s %s(%d nodes)' % (r['machine'], r['bound'], r['nodes']) for r in six))

    print('EXPLORATORY (not a pre-registered claim): closed lemmas = %d (largest residual R = %d), open '
          'nodes = %d (largest R = %d), max nested depth = %d'
          % (len(state.get('closed', [])), max(state.get('closed', [0]) or [0]), state.get('open', 0),
             max(state.get('open_R', [0]) or [0]), state.get('maxdepth', 0)), flush=True)
    out['exploratory'] = {'closed_lemmas': len(state.get('closed', [])),
                          'closed_max_R': max(state.get('closed', [0]) or [0]),
                          'open_nodes': state.get('open', 0),
                          'open_max_R': max(state.get('open_R', [0]) or [0]),
                          'maxdepth_true': state.get('maxdepth', 0),
                          'nodes_explored': state['nodes'],
                          'note': 'not a pre-registered claim: measured reach of the B&B class'}
    claim('P8-6', 'RECORD (measured): the M_edge B&B tree reached %d nodes / depth %d and did %s certify '
                  'k_min >= 7 inside the budget; every recorded node carries one exact rational LP value that '
                  'one re-solve reproduces. The R9 pruned DFS needs 19,352,397 node visits for the same '
                  'statement' % (state['nodes'], dep, 'NOT' if bound is None else ''),
          True, 'tree nodes = %d ; depth = %d ; certified = %s ; DFS nodes = 19,352,397'
          % (state['nodes'], dep, bound is not None))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '21_r10_branch_certificate.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
