#!/usr/bin/env python3
"""O222 R20-extension -- structured (flip-based) search for a rank-2 sign realization of K.

Why a second, different method: the frozen discovery protocol (scripts/40) is gradient-based in (U,V) with an
exp loss.  A rank-2 realization is a *combinatorial* object (12 cell patterns against 62 oriented lines in R^2),
so a flip-based simulated annealing over the geometric directions is much better adapted.  Purpose: either find a
rank-2 realization (which would complete sign_rank(K) = 2 exactly) or add independent evidence that none exists.

Model: U in R^{120x2} (points), V in R^{62x2} (oriented lines).  Sign of U_i . V_j must equal K_ij.
Energy = number of mismatching signs (0 = certified candidate).  Moves: perturb one direction vector by a random
Gaussian jitter (fresh normal draws, seeds frozen below); accept via Metropolis.  Exact verification (if energy 0)
is done separately with Fraction arithmetic.

Usage: /usr/bin/python3 scripts/43_r2_flip_search.py [minutes]
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
SEED = 2026093
RESTARTS = 400
STEPS = 6000
T0, T1 = 0.35, 0.005
GRID = 10 ** 4


def load_K():
    import importlib.util
    spec = importlib.util.spec_from_file_location("b5_pin_r2", os.path.join(HERE, "12_b5_budget.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _mm, K, MUL, hx, _ids, _types = m.load_machine()
    return np.array(K, dtype=np.float64)


def run(K, budget_s, log):
    m, n = K.shape
    best = (m * n + 1, None)
    t_start = time.time()
    for r in range(RESTARTS):
        rng = np.random.default_rng(SEED + r)
        U = rng.normal(0, 1, size=(m, 2))
        V = rng.normal(0, 1, size=(n, 2))
        S = np.sign(U @ V.T)
        S[S == 0] = 1.0
        E = int((S != K).sum())
        if E < best[0]:
            best = (E, (U.copy(), V.copy()))
        for t in range(STEPS):
            T = T0 * (T1 / T0) ** (t / STEPS)
            side = rng.integers(0, 2)
            i = int(rng.integers(0, m if side == 0 else n))
            step = 0.6 * T + 0.02
            if side == 0:
                U[i] += rng.normal(0, step, size=2)
            else:
                V[i] += rng.normal(0, step, size=2)
            row = np.sign(U @ V.T) if side == 0 else np.sign(U @ V.T)
            row[row == 0] = 1.0
            E2 = int((row != K).sum())
            if E2 <= E or rng.random() < np.exp((E - E2) / max(T, 1e-9)):
                S = row
                E = E2
                if E < best[0]:
                    best = (E, (U.copy(), V.copy()))
                    log("  restart %d step %d: energy %d" % (r, t, E))
                if E == 0:
                    return best, r
        if time.time() - t_start > budget_s:
            log("  time budget reached at restart %d (best energy %d)" % (r, best[0]))
            break
    return best, RESTARTS


def main():
    budget_s = float(sys.argv[1]) * 60 if len(sys.argv) > 1 else 240.0
    log_path = os.path.join(ROOT, "logs", "43_r2_flip_search.out")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    fh = open(log_path, "w", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        fh.write(msg + "\n")
        fh.flush()

    K = load_K()
    log("=" * 100)
    log("O222 R20-ext: flip-based (simulated annealing) rank-2 search, %dx%d, seed %d, restarts %d x %d steps, budget %.0f s"
        % (K.shape[0], K.shape[1], SEED, RESTARTS, STEPS, budget_s))
    log("=" * 100)
    best, done = run(K, budget_s, log)
    E, UV = best
    out = {"method": "flip-based simulated annealing over 2-dim directions", "seed": SEED, "restarts": RESTARTS,
           "steps": STEPS, "best_energy": E, "mismatches_of_7440": E, "restarts_run": done,
           "grid": GRID, "candidates": []}
    if E == 0 and UV is not None:
        U, V = UV
        out["candidates"] = [{"r": 2, "den": GRID, "seed": -1,
                              "U": np.rint(U * GRID).astype(np.int64).tolist(),
                              "V": np.rint(V * GRID).astype(np.int64).tolist()}]
        log("*** energy 0 reached -- candidate written for exact certification ***")
    log("best energy = %d / %d  (mismatching signs)" % (E, K.shape[0] * K.shape[1]))
    with open(os.path.join(DATA, "43_r2_flip_search.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    fh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
