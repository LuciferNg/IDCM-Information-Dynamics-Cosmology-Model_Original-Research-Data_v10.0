#!/usr/bin/env python3
"""O228 scripts/22 -- R11: complete enumeration and structure of the minimum separating frames.

Contract: docs/17_r11_contract.md   (o228-r11-opt-frame-census-v1)

A "frame" of size k = a set of k columns separating all pairs.  R2 counted F_7(M_edge) = 8584 by a pruned DFS
and R10 exhibited one explicitly; R11 enumerates them ALL and profiles the object:

  * per-column appearance counts        (resource-utilisation profile)
  * the union of all optimal frames     (are some columns never optimal?)
  * pairwise intersection distribution  (are two optimal frames ever disjoint?)
  * per-frame inclusion-minimality      (F_6 = 0  =>  every 7-frame is minimal)
  * type spectrum                       (frames grouped by R1's distinct column vectors)

Indexing discipline (R10 lesson 23): S[p] = the set of COLUMNS separating pair p;  CP[a] = the set of PAIRS
covered by column a.  Distinct names, and len(CP) == N asserted.

Usage: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u scripts/22_r11_opt_frame_census.py
"""
import importlib.util
import io
import itertools
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
NODE_CAP = 3000000000
WALL = 1500.0


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
    print('O228 scripts/22 -- R11: census of minimum separating frames (M_edge, k = 7)')
    print('=' * 112, flush=True)

    s04 = load(os.path.join(HERE, '04_r2_general_machine.py'), 's04')
    s09 = load(os.path.join(HERE, '09_r5_kmin_law.py'), 's09')
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
    ALLP = (1 << NP) - 1
    print('machine %s: N=%d columns, m=%d rows, %d pairs; candidate counts vary, all pairs coverable'
          % (edge.name, N, edge.m, NP), flush=True)

    # ---------------- (1) exhaustive enumeration of all TARGET-column frames
    suf = [0] * (N + 1)
    for i in range(N - 1, -1, -1):
        suf[i] = suf[i + 1] | CP[i]
    covers = []
    nodes = [0]
    aborted = [False]
    t = time.time()

    def rec(start, depth, mk, chosen):
        if aborted[0]:
            return
        nodes[0] += 1
        if nodes[0] > NODE_CAP or (time.time() - t) > WALL:
            aborted[0] = True
            print('   ... ABORT at %d nodes, %d frames, %.0f s' % (nodes[0], len(covers), time.time() - t),
                  flush=True)
            return
        if depth == TARGET:
            if mk == ALLP:
                covers.append(tuple(chosen))
            return
        need = TARGET - depth
        for j in range(start, N - need + 1):
            if (mk | CP[j] | suf[j + 1]) != ALLP:
                continue                      # j plus the remaining columns cannot finish the cover
            rec(j + 1, depth + 1, mk | CP[j], chosen + [j])
            if aborted[0]:
                return
        if nodes[0] % 2000000 < N + 1:
            print('   ... enumeration %d nodes, %d frames, %.0f s'
                  % (nodes[0], len(covers), time.time() - t), flush=True)

    rec(0, 0, 0, [])
    complete = not aborted[0]
    dt = time.time() - t
    print('enumeration: %d frames, %d nodes, %.1f s, complete=%s' % (len(covers), nodes[0], dt, complete),
          flush=True)
    out['enumeration'] = {'frames': len(covers), 'nodes': nodes[0], 'seconds': round(dt, 2),
                          'complete': complete, 'node_cap': NODE_CAP, 'wall': WALL}

    claim('P10-1', 'the complete enumeration reproduces F_7 = 8584 (cross-check against the R2 DFS count) '
                   '[not blind: value known from R2]', len(covers) == 8584 and complete,
          '%d frames found (complete=%s); R2 reported F_7 = 8584' % (len(covers), complete))

    masks = [sum(1 << a for a in cov) for cov in covers]

    # ---------------- (2) per-column appearance counts and union
    deg = [0] * N
    for mk in masks:
        d = mk
        while d:
            b = (d & -d).bit_length() - 1
            d &= d - 1
            deg[b] += 1
    union = 0
    for mk in masks:
        union |= mk
    never = [a for a in range(N) if deg[a] == 0]
    forced = [a for a in range(N) if deg[a] == len(covers)]
    out['degrees'] = {'min': min(deg), 'max': max(deg), 'distinct_values': sorted(set(deg)),
                      'hist': {str(v): deg.count(v) for v in sorted(set(deg))},
                      'never_in_any_frame': never, 'in_every_frame': forced,
                      'union_size': bin(union).count('1')}
    print('degrees: min=%d max=%d distinct=%s ; never-in-any-frame=%d ; in-every-frame=%d ; |union|=%d'
          % (min(deg), max(deg), sorted(set(deg)), len(never), len(forced), bin(union).count('1')),
          flush=True)
    claim('P10-2', 'no column is forced: every column is absent from at least one optimal frame  [BLIND]',
          len(forced) == 0, 'columns present in all %d frames: %d' % (len(covers), len(forced)))
    claim('P10-3', 'the union of all optimal frames is strictly smaller than 62: at least one column never '
                   'occurs in an optimal frame  [BLIND]', len(never) > 0,
          'never-occurring columns: %d %s' % (len(never), never[:8]))

    # ---------------- (3) per-frame inclusion-minimality (measured, not inferred)
    nonmin = 0
    for mk in masks:
        for a in range(N):
            if (mk >> a) & 1:
                rest = mk & ~(1 << a)
                cov = 0
                d = rest
                while d:
                    b = (d & -d).bit_length() - 1
                    d &= d - 1
                    cov |= CP[b]
                if cov == ALLP:
                    nonmin += 1
                    break
    out['minimality'] = {'non_minimal_frames': nonmin}
    print('inclusion-minimality: %d non-minimal frames out of %d' % (nonmin, len(covers)), flush=True)
    claim('P10-4', 'every 7-frame is inclusion-minimal (removing any one of its columns breaks it) '
                   '[not blind: follows from F_6 = 0]', nonmin == 0, '%d non-minimal frames' % nonmin)

    claim('P10-5', 'the per-column appearance-count distribution is non-uniform: at least 3 distinct values '
                   '[BLIND]', len(set(deg)) >= 3, 'distinct count values = %s' % sorted(set(deg)))

    # ---------------- (4) pairwise intersections
    hist = {}
    disjoint = 0
    t2 = time.time()
    for i in range(len(masks)):
        mi = masks[i]
        for j in range(i + 1, len(masks)):
            k = (mi & masks[j]).bit_count()
            hist[k] = hist.get(k, 0) + 1
            if k == 0:
                disjoint += 1
    out['pairwise'] = {'hist': {str(k): hist[k] for k in sorted(hist)}, 'disjoint_pairs': disjoint,
                       'pairs_examined': len(masks) * (len(masks) - 1) // 2,
                       'seconds': round(time.time() - t2, 1)}
    print('pairwise: %d pairs in %.1f s ; disjoint pairs = %d ; intersection hist = %s'
          % (len(masks) * (len(masks) - 1) // 2, time.time() - t2, disjoint,
             {k: hist[k] for k in sorted(hist)}), flush=True)

    # ---------------- (5) type spectrum (R1's distinct column vectors)
    vecs = {}
    ct = []
    for a in range(N):
        v = tuple(edge.cols[a])
        if v not in vecs:
            vecs[v] = len(vecs)
        ct.append(vecs[v])
    spectral = {}
    for cov in covers:
        key = tuple(sorted(ct[a] for a in cov))
        spectral[key] = spectral.get(key, 0) + 1
    out['type_spectrum'] = {'n_distinct_column_vectors': len(vecs),
                            'n_distinct_frame_types': len(spectral),
                            'top': sorted(((k, v) for k, v in spectral.items()), key=lambda t: -t[1])[:10]}
    print('type spectrum: %d distinct column vectors, %d distinct frame types' % (len(vecs), len(spectral)),
          flush=True)
    claim('P10-6', 'RECORD: type spectrum of the optimal frames (frame multisets of R1 column-vector types)',
          True, '%d distinct frame types over %d distinct column vectors' % (len(spectral), len(vecs)))

    out['claims'] = CLAIMS
    out['elapsed_s'] = time.time() - t0
    with io.open(os.path.join(DATA, '22_r11_opt_frame_census.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  (%d FAIL)   elapsed %.1f s' % (npass, len(CLAIMS), len(CLAIMS) - npass,
                                                              out['elapsed_s']))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
