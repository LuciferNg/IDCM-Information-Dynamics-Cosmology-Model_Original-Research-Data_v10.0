#!/usr/bin/env python3
"""O224 scratch/measure_engines.py -- LOGGED measurement of the three round-5 engines on this box,
so that the numbers quoted in docs/06 section 7.2 are backed by an artefact instead of terminal
scrollback.  Read-only w.r.t. the project data (writes nothing; caller redirects stdout to a log).

M1 numpy per-group path of scripts/16 (fg_of_group + window_setup + 5x reduced_group) on declared groups.
M2 Numba JIT of scripts/18 in the production configuration (bmax = 62) over one pair per shard.
M3 CuPy GPU of scripts/17 (chunked, chunk = 128 outer groups), steady state after warmup.
"""
import importlib.util
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import lib2i as L                                                    # noqa: E402

SPEC16 = importlib.util.spec_from_file_location('w16', os.path.join(ROOT, 'scripts',
                                                                   '16_windows_global.py'))
cpu = importlib.util.module_from_spec(SPEC16)
SPEC16.loader.exec_module(cpu)

G_, idx, MUL, U, ids, types, hx, K = L.load_machine()
nax = len(ids)
KA = np.array(K, dtype=np.int32)
NMUL = np.array(MUL, dtype=np.int32)
hxa = np.array(hx, dtype=np.int32)
anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
partner = anti.argmax(axis=1).astype(np.int32)
adx = np.arange(nax)

t = time.time()
X = cpu.build_e4(nax, KA, NMUL, hxa)
print('E4 build: %.1f s, |E4|max = %d' % (time.time() - t, int(np.abs(X).max())))

# ---------------- M1: numpy per-group (scripts/16) ----------------
groups = [(0, 1, 2, 3), (0, 60, 0, 53), (0, 1, 8, 6), (5, 5, 9, 9), (31, 31, 31, 31),
          (0, 31, 1, 30), (13, 28, 22, 43), (11, 10, 9, 8), (44, 45, 46, 47), (3, 7, 11, 15),
          (17, 19, 23, 29), (0, 0, 0, 0), (60, 0, 53, 0), (0, 1, 7, 3), (2, 3, 4, 5),
          (0, 60, 32, 59), (7, 7, 7, 8), (22, 23, 24, 25)]
t = time.time()
ncalls = 0
for (a, ap, b, bp) in groups:
    fi = np.zeros(nax, bool)
    fi[[a, ap, b, bp]] = True
    F3, G3 = cpu.fg_of_group(X, a, ap, b, bp, nax)
    setup = cpu.window_setup(nax, a, ap, b, bp, adx, anti, fi)
    gate, masks, plane_cc = cpu.group_masks(nax, a, ap, b, bp, adx, anti, fi)
    for w in cpu.WINDOWS:
        if not gate[w]:
            continue
        cpu.reduced_group(F3, G3, w, setup, nax)
        ncalls += 1
dt = time.time() - t
print('M1 numpy per-group path (scripts/16): %d groups in %.1f s -> %.1f ms/group/'
      '(core) over %d window evaluations' % (len(groups), dt, dt / len(groups) * 1000, ncalls))

# ---------------- M2: Numba JIT (scripts/18), production config bmax = 62 ----------------
# Run through the script's own CLI: its @njit(cache=True) kernels pickle a reference to the defining
# module, so loading 18 via importlib under a fabricated module name breaks the cache reload
# (ModuleNotFoundError: No module named '<dynamic>').  The production runs use __main__ and are fine.
import subprocess                                                     # noqa: E402
t = time.time()
pr = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', '18_windows_global_jit.py'),
                     '--bench', '1'], capture_output=True, text=True)
dt = time.time() - t
for ln in pr.stdout.splitlines():
    if ln.startswith('  per group'):
        print('M2 Numba JIT (scripts/18, bmax = 62, 12 threads): %s  [wall %.1f s incl. E4 rebuild]'
              % (ln.strip(), dt))
        break
else:
    print('M2 FAILED rc=%d stderr tail=%s' % (pr.returncode, pr.stderr.strip()[-300:]))

# ---------------- M3: CuPy GPU (scripts/17) ----------------
try:
    import cupy as cp
    SPEC17 = importlib.util.spec_from_file_location('w17', os.path.join(ROOT, 'scripts',
                                                                       '17_windows_global_gpu.py'))
    gpu17 = importlib.util.module_from_spec(SPEC17)
    SPEC17.loader.exec_module(gpu17)
    chunk, _, _ = gpu17.make_gpu(None)
    dX = cp.asarray(X)
    danti = cp.asarray(anti)
    pool = cp.get_default_memory_pool()
    for B in (64, 128):
        pool.free_all_blocks()
        times = []
        for rep in range(6):
            gi = cp.asarray(np.arange(min(B, nax * nax), dtype=np.int64))
            b = gi.size
            t = time.time()
            chunk(dX, danti, 0, 1, gi, nax, b)
            cp.cuda.Stream.null.synchronize()
            dt = time.time() - t
            if rep >= 2:
                times.append(dt)
        med = float(np.median(times))
        print('M3 CuPy GPU (scripts/17), chunk B=%d: median %.1f ms/chunk -> %.3f ms/group -> '
              'full 62^8 estimate %.1f h (single stream)'
              % (B, med * 1000, med * 1000 / B, med / B * nax ** 4 / 3600))
        pool.free_all_blocks()
    free, total = cp.cuda.Device(0).mem_info          # cupy API: (free, total), NOT (used, total)
    print('GPU VRAM: %.2f GB free of %.2f GB total' % (free / 1e9, total / 1e9))
except Exception as exc:                                             # noqa: BLE001
    print('M3 GPU unavailable/failed: %s' % exc)

print('MEASUREMENT COMPLETE (no project data written)')
