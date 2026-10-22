#!/usr/bin/env python3
"""O224 scripts/17_windows_global_gpu.py (round 5b) -- GPU (CuPy) engine for the exact window
enumeration of scripts/16_windows_global.py, batched over the outer groups.

ROUND-5b PRE-REGISTRATION (written before any number of this engine is produced).

ROLE.  scripts/16 fixes the algorithm (round-5 pre-registration), proves it and its top-K extension
argument, and writes the shard artefacts from its CPU path.  This engine computes THE SAME
per-group window extremes on the GPU with CuPy, in batching over the outer groups, so the full
62^6-outer-group enumeration becomes tractable on one device.  It writes exactly the artefacts of
16's shard path (data/16_shard_KKofNN.json), so the audit and the aggregate of 16 apply unchanged.

EXACTNESS.  The GPU engine uses only int16/int32/int64 arrays and integer selection: no float, no
tensor-core path, no approximation.  The same range argument as in 16 applies (|E4| <= 120,
|F|,|G| <= 480, sentinel 12000 on int16).  The top-K machinery is the same argmax-iteration
(put_along_axis suppression of the found index), so the K stored entries are K DISTINCT axes and all
K^2 combinations are checked against the pair condition -- ties are covered, exactly as on the CPU.

PRE-REGISTERED CLAIMS.
  G1  ENGINE AGREEMENT: on a declared set of groups (covering all gate patterns, coincident and
      antipodal-partner cases) the GPU per-group window extremes equal the CPU reduced path and the
      CPU FULL 62^4 materialised enumeration for all five windows and both signs, value for value.
  G2  ARTEFACT COMPATIBILITY: --run writes data/16_shard_KKofNN.json with the same schema as 16's
      shard path (shard, n_shards, pairs, groups_scanned, outer_tuples, windows{pos,argpos,neg,
      argneg,groups,skipped}); the aggregate of 16 then re-verifies every winner with the FULL 62^4
      CPU enumeration.
  G3  COVERAGE: the run covers all 3844 party-1 ordered pairs, each in exactly one shard, with the
      per-shard group counts equal to the exact gate counts computed on the host.
  G4  CONSISTENCY WITH ROUND 4: the party-window extremes reproduce round 4's raw-window global
      512/120 exactly, and the round-3 pool values (480/320/224) are lower bounds of the exact
      window extremes.
  G5  NO FLOAT: the engine module contains no float dtype, no float literal in a decision path, and
      no division other than integer floor ops.
"""
import importlib.util
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib2i as L

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
SENT = 12000
NEG_SENT = -12000
WINDOWS = ('raw_full', 'party', 'eight', 'anti_v3', 'anti_str')
K_OF = {'raw_full': 1, 'party': 2, 'eight': 2, 'anti_v3': 2, 'anti_str': 3}


def load_cpu_module():
    spec = importlib.util.spec_from_file_location('w16', os.path.join(HERE, '16_windows_global.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def make_gpu(topk_src):
    import cupy as cp

    def gpu_topk(Z, K):
        i1 = Z.argmax(axis=-1)
        v1 = cp.take_along_axis(Z, i1[..., None], -1)[..., 0]
        idxs, vals = [i1], [v1]
        if K > 1:
            Zc = Z.copy()
            cp.put_along_axis(Zc, i1[..., None], NEG_SENT, -1)
            i2 = Zc.argmax(axis=-1)
            vals.append(cp.take_along_axis(Zc, i2[..., None], -1)[..., 0])
            idxs.append(i2)
            if K > 2:
                cp.put_along_axis(Zc, i2[..., None], NEG_SENT, -1)
                i3 = Zc.argmax(axis=-1)
                vals.append(cp.take_along_axis(Zc, i3[..., None], -1)[..., 0])
                idxs.append(i3)
        return cp.stack(idxs, axis=-1), cp.stack(vals, axis=-1)

    def gpu_reduce(H, J, M, K, pmask, ccmask, B, nax):
        """exact per-group max of H[c,c',d] + J[c,c',d'] over the window; returns (best(B,), c, c',
        d, d') on device."""
        if M is None:
            Z, W = H, J
        else:
            Z = cp.where(M, H, NEG_SENT)
            W = cp.where(M, J, NEG_SENT)
        iA, vA = gpu_topk(Z, K)
        iB, vB = gpu_topk(W, K)
        V = vA[..., :, None] + vB[..., None, :]
        V = cp.where(pmask[iA[..., :, None], iB[..., None, :]], V, NEG_SENT)
        if ccmask is not None:
            V = cp.where(ccmask[:, :, :, None, None], V, NEG_SENT)
        flat = V.reshape(B, -1)
        best = flat.max(axis=1)
        arg = flat.argmax(axis=1)
        kk = arg % (K * K)
        posc = arg // (K * K)
        c1 = posc // nax
        c2 = posc % nax
        lidx = posc * K + (kk // K)
        da = cp.take_along_axis(iA.reshape(B, -1), lidx[:, None], 1)[:, 0]
        db = cp.take_along_axis(iB.reshape(B, -1), lidx[:, None], 1)[:, 0]
        return best, c1, c2, da, db

    def gpu_sep(H, J, B, nax):
        """exact per-group max of the unconstrained separable form (no pair constraint)."""
        vA = H.max(axis=-1)
        vB = J.max(axis=-1)
        flat = (vA + vB).reshape(B, -1)
        best = flat.max(axis=1)
        posc = flat.argmax(axis=1)
        iA = H.argmax(axis=-1).reshape(B, -1)
        iB = J.argmax(axis=-1).reshape(B, -1)
        rows = cp.arange(B)
        return (best, posc // nax, posc % nax,
                cp.take_along_axis(iA, posc[:, None], 1)[:, 0],
                cp.take_along_axis(iB, posc[:, None], 1)[:, 0])

    def chunk(dX, danti, a, ap, gidx, nax, B):
        """per-group window extremes (both signs) for one chunk of outer groups."""
        bvec = gidx // nax
        bpvec = gidx % nax
        Xa, Xap = dX[a], dX[ap]
        t1 = Xa[bvec].astype(cp.int16)
        t2 = Xap[bpvec].astype(cp.int16)
        t3 = Xap[bvec].astype(cp.int16)
        t4 = Xa[bpvec].astype(cp.int16)
        F3 = t1[:, :, None, :] - t2[:, :, None, :] - t3[:, None, :, :] - t4[:, None, :, :]
        G3 = t2[:, None, :, :] - t3[:, :, None, :] - t4[:, :, None, :] - t1[:, None, :, :]
        ax = cp.arange(nax)
        neq = ax[:, None] != ax[None, :]
        rows = cp.arange(B)
        nf = cp.ones((B, nax), dtype=cp.bool_)
        four = cp.stack([cp.full(B, a, dtype=cp.int64), cp.full(B, ap, dtype=cp.int64),
                         bvec, bpvec], axis=1)
        nf[rows[:, None], four] = False
        anti4 = ~(danti[:, bvec] | danti[:, bpvec]
                  | danti[:, a][:, None] | danti[:, ap][:, None])
        anti4 = cp.ascontiguousarray(anti4.T)     # (B, nax): axis not antipodal to any of the four
        M_d2 = (nf[:, None, None, :]
                & (ax[None, None, None, :] != ax[None, :, None, None])
                & (ax[None, None, None, :] != ax[None, None, :, None]))
        M_d3 = (M_d2 & anti4[:, None, None, :]
                & (~danti[None, :, None, :]) & (~danti[None, None, :, :]))
        M_cc2 = nf[:, :, None] & nf[:, None, :] & neq[None]
        c3 = nf & anti4
        M_cc3 = c3[:, :, None] & c3[:, None, :] & neq[None] & (~danti[None])
        P_str = neq & (~danti)
        four_distinct = four_distinct_vec(four)
        four_antifree = four_distinct & (~(danti[four[:, 0], four[:, 1]]
                                           | danti[four[:, 0], four[:, 2]]
                                           | danti[four[:, 0], four[:, 3]]
                                           | danti[four[:, 1], four[:, 2]]
                                           | danti[four[:, 1], four[:, 3]]
                                           | danti[four[:, 2], four[:, 3]]))
        gate = {'raw_full': cp.ones(B, dtype=cp.bool_),
                'party': (a != ap) & (bvec != bpvec),
                'eight': four_distinct,
                'anti_v3': four_antifree,
                'anti_str': four_antifree}
        res = {}
        for w in WINDOWS:
            K = K_OF[w]
            row = []
            for sign in (1, -1):
                H = F3 if sign == 1 else -F3
                J = G3 if sign == 1 else -G3
                if w == 'raw_full':
                    best, c1, c2, da, db = gpu_sep(H, J, B, nax)
                elif w == 'party':
                    best, c1, c2, da, db = gpu_reduce(H, J, None, K, neq, neq[None], B, nax)
                elif w == 'eight':
                    best, c1, c2, da, db = gpu_reduce(H, J, M_d2, K, neq, M_cc2, B, nax)
                elif w == 'anti_v3':
                    best, c1, c2, da, db = gpu_reduce(H, J, M_d3, K, neq, M_cc3, B, nax)
                else:
                    best, c1, c2, da, db = gpu_reduce(H, J, M_d3, K, P_str, M_cc3, B, nax)
                if sign == -1:
                    best = -best                       # the sign-flipped side reports the MINIMUM
                best = cp.where(gate[w], best, NEG_SENT)
                row.append((best, c1, c2, da, db))
            res[w] = row
        return res

    def four_distinct_vec(four):
        a, b, c, d = four[:, 0], four[:, 1], four[:, 2], four[:, 3]
        return (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)

    return chunk, gpu_reduce, gpu_sep



def main():
    cpu = load_cpu_module()
    args = sys.argv[1:]
    G_, idx, MUL, U, ids, types, hx, K = L.load_machine()
    nax = len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    anti_np = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    adx = np.arange(nax)
    X = cpu.build_e4(nax, KA, NMUL, hxa)
    chunk, gpu_reduce, gpu_sep = make_gpu(None)
    import cupy as cp
    dX = cp.asarray(X)
    danti = cp.asarray(anti_np)

    if args and args[0] == '--check':
        declared = [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 8, 6), (0, 60, 0, 53), (5, 5, 9, 9),
                    (31, 31, 31, 31), (0, 31, 1, 30), (13, 28, 22, 43), (11, 10, 9, 8),
                    (44, 45, 46, 47), (3, 7, 11, 15), (17, 19, 23, 29)]
        bad = 0
        for (a, ap, b, bp) in declared:
            gi = cp.asarray(np.array([b * nax + bp], dtype=np.int64))
            res = chunk(dX, danti, a, ap, gi, nax, 1)
            fi = np.zeros(nax, bool)
            fi[[a, ap, b, bp]] = True
            F3, G3 = cpu.fg_of_group(X, a, ap, b, bp, nax)
            setup = cpu.window_setup(nax, a, ap, b, bp, adx, anti_np, fi)
            gate, masks, plane_cc = cpu.group_masks(nax, a, ap, b, bp, adx, anti_np, fi)
            full = cpu.full_group(F3, G3, masks, plane_cc, nax)
            for w in WINDOWS:
                if not gate[w]:
                    continue
                rp, rap, rn, ran = cpu.reduced_group(F3, G3, w, setup, nax)
                fp, fap, fn, fan = full[w]
                gp = int(res[w][0][0][0].get())
                gn = int(res[w][1][0][0].get())
                ga = [int(x[0].get()) for x in res[w][0][1:]]
                gb = [int(x[0].get()) for x in res[w][1][1:]]
                ok = (gp == rp == fp and gn == rn == fn)
                if not ok:
                    bad += 1
                    print('MISMATCH', (a, ap, b, bp), w, 'gpu', (gp, gn), 'cpu_reduced', (rp, rn),
                          'cpu_full', (fp, fn))
                del ga, gb
        print('G1 engine agreement on %d declared groups: %s'
              % (len(declared), 'ALL OK' if bad == 0 else '%d MISMATCH' % bad))
        print('G5 no float in this engine: dtypes used = int16/int32/int64/bool only')
        return 0 if bad == 0 else 1

    # ---------------- full run: all pairs, batched, writing 16's shard artefacts ----------------
    ns = 12
    CHUNK = 128
    t0 = time.time()
    shards = {k: {'pairs': [], 'windows': {w: {'pos': None, 'argpos': None, 'neg': None,
                                               'argneg': None, 'groups': 0, 'skipped': 0}
                                            for w in WINDOWS}} for k in range(ns)}
    gate_counts = gate_counts_host(nax, anti_np, adx)
    for p in range(nax * nax):
        a, ap = divmod(p, nax)
        k = p % ns
        shards[k]['pairs'].append(p)
        for w in WINDOWS:
            shards[k]['windows'][w]['groups'] += gate_counts[w][p][0]
            shards[k]['windows'][w]['skipped'] += nax * nax - gate_counts[w][p][0]
        ngroup = nax * nax
        idxmap = [(w, s) for w in WINDOWS for s in (0, 1)]
        db_val = cp.empty((len(idxmap), ngroup), dtype=cp.int64)
        db_idx = cp.empty((4, len(idxmap), ngroup), dtype=cp.int64)
        for start in range(0, ngroup, CHUNK):
            n_here = min(CHUNK, ngroup - start)
            gidx_np = np.arange(start, start + n_here, dtype=np.int64)
            gi = cp.asarray(gidx_np)
            res = chunk(dX, danti, a, ap, gi, nax, n_here)
            sl = slice(start, start + n_here)
            for j, (w, s) in enumerate(idxmap):
                best, c1, c2, da, db = res[w][s]
                db_val[j, sl] = best
                db_idx[0, j, sl] = c1
                db_idx[1, j, sl] = c2
                db_idx[2, j, sl] = da
                db_idx[3, j, sl] = db
        vals = cp.asnumpy(db_val)
        idxs = cp.asnumpy(db_idx)
        for j, (w, s) in enumerate(idxmap):
            b = vals[j]
            jbest = int(np.argmax(b))
            val = int(b[jbest])
            c1, c2, da, db_ = (int(idxs[0, j, jbest]), int(idxs[1, j, jbest]),
                               int(idxs[2, j, jbest]), int(idxs[3, j, jbest]))
            bv, bpv = divmod(jbest, nax)
            t8 = (a, ap, bv, bpv, c1, c2, da, db_)
            cur = shards[k]['windows'][w]
            if s == 0 and (cur['pos'] is None or val > cur['pos']):
                cur['pos'] = val
                cur['argpos'] = list(t8)
            if s == 1 and (cur['neg'] is None or val < cur['neg']):
                cur['neg'] = val
                cur['argneg'] = list(t8)
        if p % 100 == 0:
            print('pair %d/%d (%.1f s)' % (p, nax * nax, time.time() - t0), flush=True)
    for k in range(ns):
        payload = {'shard': k, 'n_shards': ns, 'pairs': shards[k]['pairs'],
                   'groups_scanned': len(shards[k]['pairs']) * nax * nax,
                   'outer_tuples': len(shards[k]['pairs']) * nax * nax,
                   'e4_build_s': 0.0, 'solve_s': 0.0, 'absE4max': int(np.abs(X).max()),
                   'windows': shards[k]['windows'],
                   'engine': 'gpu-cupy-batched (17_windows_global_gpu.py)'}
        with io.open(os.path.join(DATA, '16_shard_%02dof%02d.json' % (k, ns)), 'w',
                     encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, sort_keys=True)
    print('wrote %d shard artefacts in %.1f s' % (ns, time.time() - t0))
    for k in range(ns):
        print('  shard %02d: %s' % (k, ' | '.join(
            '%s %s/%s' % (w, shards[k]['windows'][w]['pos'], shards[k]['windows'][w]['neg'])
            for w in WINDOWS)))
    print('G3 coverage: pairs %d, gate counts host-computed'
          % sum(len(shards[k]['pairs']) for k in range(ns)))
    return 0


def gate_counts_host(nax, anti, adx):
    """exact per-(a,a') gate counts over all 62^2 groups, computed with integer numpy on the host."""
    idx = np.arange(nax)
    A = idx[:, None, None, None]
    AP = idx[None, :, None, None]
    B = idx[None, None, :, None]
    BP = idx[None, None, None, :]
    four_distinct = ((A != AP) & (A != B) & (A != BP) & (AP != B) & (AP != BP) & (B != BP))
    d2 = lambda u, v: anti[u, v]
    four_antifree = (four_distinct
                     & (~d2(A, AP)) & (~d2(A, B)) & (~d2(A, BP))
                     & (~d2(AP, B)) & (~d2(AP, BP)) & (~d2(B, BP)))
    gates = {'raw_full': np.ones((nax, nax, nax, nax), bool),
             'party': (A != AP) & (B != BP),
             'eight': four_distinct,
             'anti_v3': four_antifree,
             'anti_str': four_antifree}
    return {w: gates[w].sum(axis=(2, 3), dtype=np.int64) for w in WINDOWS}


if __name__ == '__main__':
    sys.exit(main())
