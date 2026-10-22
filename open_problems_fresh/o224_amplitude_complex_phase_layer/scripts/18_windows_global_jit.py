#!/usr/bin/env python3
"""O224 scripts/18_windows_global_jit.py (round 5c) -- Numba JIT multi-threaded engine for the exact
window enumeration of scripts/16_windows_global.py.

ROUND-5c PRE-REGISTRATION (written before any number of this engine is produced).

WHY.  scripts/16 fixes the algorithm and verifies it with the CPU numpy path (whose per-group cost is
bandwidth/call-bound), 17 is the same algorithm on the GPU (measured 2.87 ms/group on the GTX 1060,
i.e. 11.8 h single-stream -- slower than the 12-thread CPU).  This engine keeps the SAME exact
algorithm but executes the (c,c',d) scans in compiled scalar loops with Numba, parallelised over the
12 shards, so no intermediate 62^3 arrays are materialised at all.

EXACTNESS.  Integer only (int32 values, int64 bookkeeping); no float, no fastmath, no approximation.
Per group the scan keeps the top-3 of F over the admissible d-set and the top-3 of G over the same
set, then enumerates the 9 combinations against the pair constraints.  The top-3 bound is the same
extension argument as in 16 (at most 2 axes are unusable against a fixed partner: the partner itself
and its antipode), so no admissible candidate is missed; ties are irrelevant because every
combination of the stored indices is checked explicitly.

PRE-REGISTERED CLAIMS.
  J1  GROUP-LEVEL AGREEMENT: for a declared set of groups (all gate patterns, coincident and
      antipodal cases) the engine's per-group window extremes equal the numpy reduced path of 16 AND
      the numpy FULL 62^4 materialised enumeration, for all five windows and both signs.
  J2  ARTEFACT COMPATIBILITY: --run writes data/16_shard_KKofNN.json in 16's shard schema, so the
      aggregate of 16 re-verifies every winner by the FULL 62^4 CPU enumeration and by the direct
      8-term evaluation.
  J3  COVERAGE: all 3844 party-1 ordered pairs, each in exactly one shard; per-shard group counts
      equal the exact host-computed gate counts.
  J4  ROUND-4 CONSISTENCY: raw_full and party reproduce round 4's 512/120 exactly, and the round-3
      pool values (480/320/224) bound the exact window extremes from below.
  J5  DETERMINISM: re-running any shard reproduces its extremes value for value (the shard result is
      an order-independent max over its pairs).
  J6  ACCUMULATION AND PRESENCE: on a COMMON RESTRICTED outer domain (b,bp < 2) the per-shard
      accumulation of the kernel (pos = max, neg = min, presence flags, plus the per-window gate
      counters) equals the same aggregation computed from the numpy per-pair path of 16.
      (Restricting b,bp is a joint restriction of BOTH engines, not a relaxation; the unrestricted
      per-group semantics is J1.)

ENGINE MEASUREMENTS (this machine: Ryzen 5 5600X, 6C/12T; GTX 1060 3 GB).
  scripts/16 numpy CPU   : 21.5 ms per group per core  -> 12 processes ~5-7 h
  scripts/17 CuPy GPU    : 2.87 ms per group (measured steady state, chunk 128) -> 11.8 h one stream;
                           exact and verified (G1 ALL OK) but memory-bound on 3 GB and slower than
                           the CPU, so it is kept only as a third independent engine, not used.
  this engine  (Numba)   : 1.30 ms per group with 12 threads -> ~5.3 h for the full space.

CORRECTION (2026-10-01, written AFTER the production run; original text above kept verbatim).
The table above was pre-registered from partial terminal profiling.  Measured and logged in
scratch/measure_engines.py -> logs/18_engine_measure.out (two passes, identical timings):
  scripts/16 numpy CPU : 14.3-15.0 ms per group per core  -> 12 processes ~5.0 h
                         (NOT 21.5 ms / 5-7 h: that row was a sum of per-stage profiling estimates)
  scripts/18 Numba JIT : 1.280 ms per group (12 threads) -> ~5.3 h ; per core ~15.4 ms
                         (12-thread parallel efficiency ~94%)
  scripts/17 CuPy GPU  : 2.84-2.90 ms per group -> 11.7-11.9 h single stream.  Chunk 64 and chunk 128
                         are equally fast, so NEITHER the chunk size NOR the 3 GB VRAM is the binding
                         factor: the earlier "memory-bound on 3 GB / small chunks" attribution is
                         WITHDRAWN.  The card is indeed a GTX 1060 3GB (nvidia-smi 3072 MiB, torch
                         total_mem 3.22 GB), but VRAM is not the bottleneck; the workload's shape
                         (62-axis small reductions, several kernel launches per chunk, low arithmetic
                         intensity) is what makes the GPU 2.2x slower than the CPU engines.
Consequence: the two CPU engines are effectively EQUIVALENT (~5 h); this engine was chosen for
OPERATIONAL reasons (single process using all 12 threads, built-in per-range checkpoints writing the
same shard schema) rather than for a large speed margin.  No judging value is affected.
"""
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

BIG = 1 << 20
WINDOWS = ('raw_full', 'party', 'eight', 'anti_v3', 'anti_str')


def build_kernels():
    from numba import njit, prange

    @njit(cache=True, fastmath=False)
    def group_scan(X, partner, a, ap, b, bp, bv, ba, bc):
        """per-group window extremes; bv (5,2) values, ba (5,2,8) args, bc (5,2) 0/1 presence."""
        nax = X.shape[0]
        AB = np.empty((nax, nax), np.int32)
        RB = np.empty((nax, nax), np.int32)
        UB = np.empty((nax, nax), np.int32)
        for c in range(nax):
            for d in range(nax):
                v1 = X[a, b, c, d]
                v2 = X[ap, bp, c, d]
                v3 = X[ap, b, c, d]
                v4 = X[a, bp, c, d]
                AB[c, d] = v1 - v2
                RB[c, d] = v3 + v4
                UB[c, d] = v2 - v1
        d8 = np.zeros(nax, np.bool_)
        d3 = np.zeros(nax, np.bool_)
        for x in range(nax):
            ok = (x != a) and (x != ap) and (x != b) and (x != bp)
            d8[x] = ok
            d3[x] = ok and (partner[x] != a) and (partner[x] != ap) and (partner[x] != b) \
                and (partner[x] != bp)
        four_distinct = (a != ap) and (a != b) and (a != bp) and (ap != b) and (ap != bp) and (b != bp)
        four_antifree = (four_distinct and (partner[a] != ap) and (partner[a] != b)
                         and (partner[a] != bp) and (partner[ap] != b) and (partner[ap] != bp)
                         and (partner[b] != bp))
        gate = np.zeros(5, np.bool_)
        gate[0] = True
        gate[1] = (a != ap) and (b != bp)
        gate[2] = four_distinct
        gate[3] = four_antifree
        gate[4] = four_antifree
        for wi in range(5):
            cslice = 0 if wi <= 1 else (2 if wi == 2 else 3)
            dslice = cslice
            excl_cc = (wi >= 2)
            pairmode = 0 if wi == 0 else (2 if wi == 4 else 1)
            use_anti = wi >= 3
            for si in range(2):
                bc[wi, si] = 0
                if not gate[wi]:
                    continue
                neg = (si == 1)
                best = -BIG
                bc_c = 0
                bc_cp = 0
                bc_d = 0
                bc_dp = 0
                for c in range(nax):
                    if cslice == 2 and (not d8[c]):
                        continue
                    if cslice == 3 and (not d3[c]):
                        continue
                    for cp in range(nax):
                        if cp == c and wi != 0:
                            continue
                        if cslice == 2 and (not d8[cp]):
                            continue
                        if cslice == 3:
                            if (not d3[cp]) or (partner[c] == cp):
                                continue
                        f1 = -BIG; f2 = -BIG; f3 = -BIG
                        g1 = -BIG; g2 = -BIG; g3 = -BIG
                        i1 = -1; i2 = -1; i3 = -1
                        j1 = -1; j2 = -1; j3 = -1
                        for d in range(nax):
                            if dslice == 2 and (not d8[d]):
                                continue
                            if dslice == 3 and (not d3[d]):
                                continue
                            if excl_cc and (d == c or d == cp):
                                continue
                            if use_anti and (partner[c] == d or partner[cp] == d):
                                continue
                            fd = AB[c, d] - RB[cp, d]
                            gd = UB[cp, d] - RB[c, d]
                            if neg:
                                fd = -fd
                                gd = -gd
                            if fd > f1:
                                f3 = f2; f2 = f1; f1 = fd
                                i3 = i2; i2 = i1; i1 = d
                            elif fd > f2:
                                f3 = f2; f2 = fd
                                i3 = i2; i2 = d
                            elif fd > f3:
                                f3 = fd; i3 = d
                            if gd > g1:
                                g3 = g2; g2 = g1; g1 = gd
                                j3 = j2; j2 = j1; j1 = d
                            elif gd > g2:
                                g3 = g2; g2 = gd
                                j3 = j2; j2 = d
                            elif gd > g3:
                                g3 = gd; j3 = d
                        for u in range(3):
                            fu = f1 if u == 0 else (f2 if u == 1 else f3)
                            iu = i1 if u == 0 else (i2 if u == 1 else i3)
                            if iu < 0 or fu <= -BIG // 2:
                                continue
                            for v in range(3):
                                gv = g1 if v == 0 else (g2 if v == 1 else g3)
                                jv = j1 if v == 0 else (j2 if v == 1 else j3)
                                if jv < 0 or gv <= -BIG // 2:
                                    continue
                                if pairmode == 1 and iu == jv:
                                    continue
                                if pairmode == 2 and (iu == jv or partner[iu] == jv):
                                    continue
                                val = fu + gv
                                if val > best:
                                    best = val
                                    bc_c = c
                                    bc_cp = cp
                                    bc_d = iu
                                    bc_dp = jv
                if best > -BIG // 2:
                    bc[wi, si] = 1
                    bv[wi, si] = (-best) if neg else best
                    ba[wi, si, 0] = a
                    ba[wi, si, 1] = ap
                    ba[wi, si, 2] = b
                    ba[wi, si, 3] = bp
                    ba[wi, si, 4] = bc_c
                    ba[wi, si, 5] = bc_cp
                    ba[wi, si, 6] = bc_d
                    ba[wi, si, 7] = bc_dp

    @njit(parallel=True, cache=True, fastmath=False)
    def run_shards(X, partner, nax, p0, p1, ns, bmax, outv, outa, outbc, outg):
        for k in prange(ns):
            gv = np.empty((5, 2), np.int64)
            ga = np.zeros((5, 2, 8), np.int64)
            gc = np.zeros((5, 2), np.int64)
            bv = np.zeros((5, 2), np.int64)
            for wi in range(5):
                bv[wi, 1] = BIG * 4
            ba = np.zeros((5, 2, 8), np.int64)
            pres = np.zeros((5, 2), np.int64)
            ng = np.zeros(5, np.int64)
            ns_sk = np.zeros(5, np.int64)
            for p in range(k + p0, p1, ns):
                a = p // nax
                ap = p % nax
                for b in range(bmax):
                    for bp in range(bmax):
                        group_scan(X, partner, a, ap, b, bp, gv, ga, gc)
                        for wi in range(5):
                            if gc[wi, 0] == 1:
                                ng[wi] += 1
                            else:
                                ns_sk[wi] += 1
                            for si in range(2):
                                if gc[wi, si] != 1:
                                    continue
                                val = gv[wi, si]
                                take = False
                                if pres[wi, si] == 0:
                                    take = True
                                elif si == 0 and val > bv[wi, si]:
                                    take = True
                                elif si == 1 and val < bv[wi, si]:
                                    take = True
                                if take:
                                    bv[wi, si] = val
                                    pres[wi, si] = 1
                                    for t in range(8):
                                        ba[wi, si, t] = ga[wi, si, t]
            for wi in range(5):
                for si in range(2):
                    outv[k, wi, si] = bv[wi, si]
                    for t in range(8):
                        outa[k, wi, si, t] = ba[wi, si, t]
                    outbc[k, wi, si] = pres[wi, si]
            for wi in range(5):
                outg[k, wi, 0] = ng[wi]
                outg[k, wi, 1] = ns_sk[wi]

    return group_scan, run_shards


def load_machine_arrays():
    G_, idx, MUL, U, ids, types, hx, K = L.load_machine()
    nax = len(ids)
    KA = np.array(K, dtype=np.int32)
    NMUL = np.array(MUL, dtype=np.int32)
    hxa = np.array(hx, dtype=np.int32)
    X = np.zeros((nax, nax, nax, nax), dtype=np.int32)
    s2b = NMUL[:, hxa]
    for a in range(nax):
        Aa = KA[:, a]
        s2 = s2b[:, a]
        for b in range(nax):
            s3 = NMUL[s2, hxa[b]]
            Wa = Aa * KA[s2, b]
            for c in range(nax):
                s4 = NMUL[s3, hxa[c]]
                X[a, b, c, :] = (Wa * KA[s3, c]) @ KA[s4, :]
    anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
    partner = anti.argmax(axis=1).astype(np.int32)
    return X, anti, partner, nax


def main():
    args = sys.argv[1:]
    mode = args[0] if args else '--run'
    t0 = time.time()
    X, anti, partner, nax = load_machine_arrays()
    print('E4 built %.1f s, |E4|max %d' % (time.time() - t0, int(np.abs(X).max())), flush=True)
    group_scan, run_shards = build_kernels()

    if mode == '--check':
        import importlib.util
        spec = importlib.util.spec_from_file_location('w16', os.path.join(HERE,
                                                                         '16_windows_global.py'))
        cpu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cpu)
        adx = np.arange(nax)
        rng = np.random.RandomState(20261001)
        declared = [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 8, 6), (0, 60, 0, 53), (5, 5, 9, 9),
                    (31, 31, 31, 31), (0, 31, 1, 30), (13, 28, 22, 43), (11, 10, 9, 8),
                    (44, 45, 46, 47), (3, 7, 11, 15), (17, 19, 23, 29), (0, 0, 0, 0),
                    (60, 0, 53, 0), (0, 1, 7, 3), (2, 3, 4, 5)]
        # deterministic extra groups: uniform, coincident-heavy and antipodal-partner patterns
        for i in range(60):
            declared.append(tuple(int(x) for x in rng.randint(0, nax, 4)))
        for i in range(30):
            base = int(rng.randint(0, nax, 1)[0])
            declared.append((base, base, int(rng.randint(0, nax, 1)[0]), base))
        for i in range(30):
            x = int(rng.randint(0, nax, 1)[0])
            declared.append((x, int(partner[x]), int(rng.randint(0, nax, 1)[0]), x))
        bad = 0
        bv = np.zeros((5, 2), np.int64)
        ba = np.zeros((5, 2, 8), np.int64)
        bc = np.zeros((5, 2), np.int64)
        for (a, ap, b, bp) in declared:
            group_scan(X, partner, a, ap, b, bp, bv, ba, bc)
            fi = np.zeros(nax, bool)
            fi[[a, ap, b, bp]] = True
            F3, G3 = cpu.fg_of_group(X, a, ap, b, bp, nax)
            setup = cpu.window_setup(nax, a, ap, b, bp, adx, anti, fi)
            gate, masks, plane_cc = cpu.group_masks(nax, a, ap, b, bp, adx, anti, fi)
            full = cpu.full_group(F3, G3, masks, plane_cc, nax)
            for wi, w in enumerate(WINDOWS):
                if not gate[w]:
                    if bc[wi, 0] == 1 or bc[wi, 1] == 1:
                        print('GATE MISMATCH', (a, ap, b, bp), w, 'jit produced a value')
                        bad += 1
                    continue
                rp, rap, rn, ran = cpu.reduced_group(F3, G3, w, setup, nax)
                fp, fap, fn, fan = full[w]
                jp = int(bv[wi, 0]) if bc[wi, 0] else None
                jn = int(bv[wi, 1]) if bc[wi, 1] else None
                ok = (jp == rp == fp and jn == rn == fn)
                if not ok:
                    print('MISMATCH', (a, ap, b, bp), w, 'jit', (jp, jn), 'numpy_reduced', (rp, rn),
                          'numpy_full', (fp, fn))
                    bad += 1
        print('J1 group-level agreement over %d declared groups (jit vs numpy-reduced vs '
              'numpy-full): %s' % (len(declared), 'ALL OK' if bad == 0 else '%d MISMATCH' % bad))
        return 0 if bad == 0 else 1

    if mode == '--bench':
        ns = 12
        per = int(args[1]) if len(args) > 1 else 4
        npairs = ns * per
        outv = np.full((ns, 5, 2), -BIG * 4, np.int64)
        outa = np.zeros((ns, 5, 2, 8), np.int64)
        outbc = np.zeros((ns, 5, 2), np.int64)
        outg = np.zeros((ns, 5, 2), np.int64)
        t = time.time()
        run_shards(X, partner, nax, 0, npairs, ns, nax, outv, outa, outbc, outg)
        dt = time.time() - t
        groups = npairs * nax * nax
        print('bench: %d shards x %d pairs = %d groups in %.1f s' % (ns, per, groups, dt))
        print('  per group %.3f ms ; full 3844-pair estimate %.1f min'
              % (dt / groups * 1000, dt / groups * (nax * nax) * nax * nax / 60))
        return 0

    if mode == '--check-range':
        import importlib.util
        spec = importlib.util.spec_from_file_location('w16', os.path.join(HERE,
                                                                         '16_windows_global.py'))
        cpu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cpu)
        adx = np.arange(nax)
        p0, p1 = int(args[1]), int(args[2])
        bmax = int(args[3]) if len(args) > 3 else 2
        ns = 12
        outv = np.zeros((ns, 5, 2), np.int64)
        outv[:, :, 1] = BIG * 4
        outa = np.zeros((ns, 5, 2, 8), np.int64)
        outbc = np.zeros((ns, 5, 2), np.int64)
        outg = np.zeros((ns, 5, 2), np.int64)
        t = time.time()
        run_shards(X, partner, nax, p0, p1, ns, bmax, outv, outa, outbc, outg)
        print('jit range [%d,%d) on the COMMON RESTRICTED domain b,bp < %d: %.1f s'
              % (p0, p1, bmax, time.time() - t))
        ref = {}
        for k in range(ns):
            ref[k] = {'pos': np.zeros(5, np.int64), 'neg': np.zeros(5, np.int64),
                      'has': np.zeros((5, 2), np.int64)}
            ref[k]['neg'][:] = BIG * 4
            for p in range(k + p0, p1, ns):
                a, ap = divmod(p, nax)
                for b in range(bmax):
                    for bp in range(bmax):
                        fi = np.zeros(nax, bool)
                        fi[[a, ap, b, bp]] = True
                        gate, masks, plane_cc = cpu.group_masks(nax, a, ap, b, bp, adx, anti, fi)
                        F3, G3 = cpu.fg_of_group(X, a, ap, b, bp, nax)
                        setup = cpu.window_setup(nax, a, ap, b, bp, adx, anti, fi)
                        for wi, w in enumerate(WINDOWS):
                            if not gate[w]:
                                continue
                            pos, argp, neg, argn = cpu.reduced_group(F3, G3, w, setup, nax)
                            for si, val in ((0, pos), (1, neg)):
                                if val is None:
                                    continue
                                if ref[k]['has'][wi, si] == 0:
                                    ref[k]['pos' if si == 0 else 'neg'][wi] = val
                                    ref[k]['has'][wi, si] = 1
                                elif si == 0 and val > ref[k]['pos'][wi]:
                                    ref[k]['pos'][wi] = val
                                elif si == 1 and val < ref[k]['neg'][wi]:
                                    ref[k]['neg'][wi] = val
        bad = 0
        for k in range(ns):
            for wi, w in enumerate(WINDOWS):
                for si in range(2):
                    jit_has = int(outbc[k, wi, si])
                    ref_has = int(ref[k]['has'][wi, si])
                    if jit_has != ref_has:
                        print('PRESENCE MISMATCH shard %d %s si=%d jit %d ref %d'
                              % (k, w, si, jit_has, ref_has))
                        bad += 1
                        continue
                    if not jit_has:
                        continue
                    refv = int(ref[k]['pos' if si == 0 else 'neg'][wi])
                    if int(outv[k, wi, si]) != refv:
                        print('VALUE MISMATCH shard %d %s si=%d jit %d numpy %d'
                              % (k, w, si, int(outv[k, wi, si]), refv))
                        bad += 1
        print('J6 accumulation+presence vs numpy per-pair path on [%d,%d) x (b,bp < %d): %s'
              % (p0, p1, bmax, 'ALL OK' if bad == 0 else '%d MISMATCH' % bad))
        return 0 if bad == 0 else 1

    if mode == '--run-range':
        p0, p1 = int(args[1]), int(args[2])
        ns = 12
        outv = np.full((ns, 5, 2), -BIG * 4, np.int64)
        outa = np.zeros((ns, 5, 2, 8), np.int64)
        outbc = np.zeros((ns, 5, 2), np.int64)
        outg = np.zeros((ns, 5, 2), np.int64)
        t = time.time()
        run_shards(X, partner, nax, p0, p1, ns, nax, outv, outa, outbc, outg)
        dt = time.time() - t
        scratch = os.path.join(ROOT, 'scratch')
        if not os.path.isdir(scratch):
            os.makedirs(scratch)
        tag = '%06d_%06d' % (p0, p1)
        np.savez(os.path.join(scratch, 'r5_part_%s.npz' % tag), outv=outv, outa=outa,
                 outbc=outbc, outg=outg, p0=p0, p1=p1)
        print('range [%d,%d): %.1f s (%.2f min); partial saved as r5_part_%s.npz'
              % (p0, p1, dt, dt / 60, tag), flush=True)
        for k in range(ns):
            print('  shard %02d partial: %s' % (k, ' | '.join(
                '%s %s/%s' % (WINDOWS[wi], outv[k, wi, 0], outv[k, wi, 1]) for wi in range(5))))
        return 0

    if mode == '--merge':
        scratch = os.path.join(ROOT, 'scratch')
        parts = sorted(f for f in os.listdir(scratch) if f.startswith('r5_part_')
                       and f.endswith('.npz'))
        if not parts:
            print('no partials found')
            return 1
        ns = 12
        bv = np.zeros((ns, 5, 2), np.int64)
        bv[:, :, 1] = BIG * 4
        ba = np.zeros((ns, 5, 2, 8), np.int64)
        bc = np.zeros((ns, 5, 2), np.int64)
        bg = np.zeros((ns, 5, 2), np.int64)
        covered = []
        for f in parts:
            z = np.load(os.path.join(scratch, f))
            covered.append((int(z['p0']), int(z['p1'])))
            v, a, c, g = z['outv'], z['outa'], z['outbc'], z['outg']
            for k in range(ns):
                for wi in range(5):
                    for si in range(2):
                        if c[k, wi, si] != 1:
                            continue
                        val = v[k, wi, si]
                        take = (bc[k, wi, si] == 0)
                        if not take:
                            if si == 0 and val > bv[k, wi, si]:
                                take = True
                            elif si == 1 and val < bv[k, wi, si]:
                                take = True
                        if take:
                            bv[k, wi, si] = val
                            for t in range(8):
                                ba[k, wi, si, t] = a[k, wi, si, t]
                            bc[k, wi, si] = 1
            bg += g
        npairs = nax * nax
        summary = []
        for k in range(ns):
            pairs = [p for p in range(npairs) if p % ns == k]
            windows = {}
            for wi, w in enumerate(WINDOWS):
                okp = int(bc[k, wi, 0]) == 1
                okn = int(bc[k, wi, 1]) == 1
                windows[w] = {'pos': int(bv[k, wi, 0]) if okp else None,
                              'argpos': [int(x) for x in ba[k, wi, 0]] if okp else None,
                              'neg': int(bv[k, wi, 1]) if okn else None,
                              'argneg': [int(x) for x in ba[k, wi, 1]] if okn else None,
                              'groups': int(bg[k, wi, 0]), 'skipped': int(bg[k, wi, 1])}
            payload = {'shard': k, 'n_shards': ns, 'pairs': pairs,
                       'groups_scanned': len(pairs) * nax * nax,
                       'outer_tuples': len(pairs) * nax ** 4, 'e4_build_s': 0.0,
                       'solve_s': 0.0, 'absE4max': int(np.abs(X).max()), 'windows': windows,
                       'engine': 'numba-jit-parallel (18_windows_global_jit.py)',
                       'partials': ['%s' % p for p in sorted(
                           os.path.basename(x) for x in parts)], 'ranges': covered}
            with io.open(os.path.join(DATA, '16_shard_%02dof%02d.json' % (k, ns)), 'w',
                         encoding='utf-8') as fh:
                json.dump(payload, fh, ensure_ascii=False, sort_keys=True)
            summary.append((k, {w: (windows[w]['pos'], windows[w]['neg']) for w in WINDOWS}))
        print('merged %d partials, wrote %d shard artefacts' % (len(parts), ns))
        for k, wv in summary:
            print('  shard %02d: %s' % (k, ' | '.join(
                '%s %s/%s' % (w, wv[w][0], wv[w][1]) for w in WINDOWS)))
        return 0

    # ---------------- --run ----------------
    ns = 12
    npairs = nax * nax
    outv = np.full((ns, 5, 2), -BIG * 4, np.int64)
    outa = np.zeros((ns, 5, 2, 8), np.int64)
    outbc = np.zeros((ns, 5, 2), np.int64)
    outg = np.zeros((ns, 5, 2), np.int64)
    t1 = time.time()
    run_shards(X, partner, nax, 0, npairs, ns, nax, outv, outa, outbc, outg)
    print('run_shards done: %.1f s (%.1f min)' % (time.time() - t1, (time.time() - t1) / 60),
          flush=True)
    for k in range(ns):
        pairs = [p for p in range(npairs) if p % ns == k]
        windows = {}
        for wi, w in enumerate(WINDOWS):
            gp, gs = int(outg[k, wi, 0]), int(outg[k, wi, 1])
            okp = int(outbc[k, wi, 0]) == 1
            okn = int(outbc[k, wi, 1]) == 1
            windows[w] = {'pos': int(outv[k, wi, 0]) if okp else None,
                          'argpos': [int(x) for x in outa[k, wi, 0]] if okp else None,
                          'neg': int(outv[k, wi, 1]) if okn else None,
                          'argneg': [int(x) for x in outa[k, wi, 1]] if okn else None,
                          'groups': gp, 'skipped': gs}
        payload = {'shard': k, 'n_shards': ns, 'pairs': pairs,
                   'groups_scanned': len(pairs) * nax * nax, 'outer_tuples': len(pairs) * nax * nax,
                   'e4_build_s': 0.0, 'solve_s': 0.0, 'absE4max': int(np.abs(X).max()),
                   'windows': windows, 'engine': 'numba-jit-parallel (18_windows_global_jit.py)'}
        with io.open(os.path.join(DATA, '16_shard_%02dof%02d.json' % (k, ns)), 'w',
                     encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, sort_keys=True)
    print('wrote %d shard artefacts' % ns)
    for k in range(ns):
        print('  shard %02d: %s' % (k, ' | '.join(
            '%s %s/%s' % (w, windows[w]['pos'], windows[w]['neg']) for w in WINDOWS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
