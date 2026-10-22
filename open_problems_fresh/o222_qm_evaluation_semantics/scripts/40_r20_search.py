#!/usr/bin/env python3
"""O222 R20 -- M3 DISCOVERY script (NOT frozen, NOT authoritative).

Purpose: propose CANDIDATE rank-r sign realizations of the frozen 120x62 sign matrix K,
following the protocol frozen in docs/27_r20_contract.md 3(M3):

    f(U,V) = sum_{i,j} exp(-K_ij * (U V^T)_ij)
    Adam, lr = 0.01, steps = 4000, restarts = 200 per r, init N(0, 1/r)
    seeds: numpy.random.default_rng(20260930 + 1000*r + k), k = 0..199
    r in 5, 4, 3, 2
    accept candidate if min_{i,j} K_ij*(UV^T)_ij >= 1e-3
    candidate -> integers on the 1e-4 grid:  w -> round(w*10^4)

Float arithmetic NEVER decides anything: it only SELECTS candidates worth exact verification.
The verdict is produced by scripts/41_r20_closure.py with exact Fraction arithmetic
(7440 signs must all be strictly nonzero and equal to K).

Usage:
    /usr/bin/python3 scripts/40_r20_search.py            # full frozen protocol
    /usr/bin/python3 scripts/40_r20_search.py --quick    # smoke test (few restarts/steps)
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

RS = (5, 4, 3, 2)
LR = 0.01
STEPS = 4000
RESTARTS = 200
SEED0 = 20260930
ACCEPT = 1e-3
SCALE = 10 ** 4


def load_K():
    """Load the frozen 120x62 +-1 sign matrix via the pinned loader (scripts/12)."""
    import importlib.util
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location("b5_pin", os.path.join(HERE, "12_b5_budget.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _mm, K, MUL, hx, _ids, _types = m.load_machine()
    return K


def run_r(Knp, r, restarts, steps, log):
    m, n = Knp.shape
    best = (None, -1.0, -1.0)  # (obj, min_margin, seed)
    accepted = []
    for k in range(restarts):
        rng = np.random.default_rng(SEED0 + 1000 * r + k)
        U = rng.normal(0.0, r ** -0.5, size=(m, r))
        V = rng.normal(0.0, r ** -0.5, size=(n, r))
        mU = np.zeros_like(U); mV = np.zeros_like(V)
        vU = np.zeros_like(U); vV = np.zeros_like(V)
        b1, b2, eps = 0.9, 0.999, 1e-8
        for t in range(1, steps + 1):
            P = U @ V.T                      # (m,n)
            S = Knp * P
            E = np.exp(-S)
            obj = float(E.sum())
            # d f / d S = -exp(-S) ;  d f / d P = -K * exp(-S)
            G = -Knp * E
            gU = G @ V
            gV = G.T @ U
            mU = b1 * mU + (1 - b1) * gU; vU = b2 * vU + (1 - b2) * gU * gU
            mV = b1 * mV + (1 - b1) * gV; vV = b2 * vV + (1 - b2) * gV * gV
            U = U - LR * (mU / (1 - b1 ** t)) / (np.sqrt(vU / (1 - b2 ** t)) + eps)
            V = V - LR * (mV / (1 - b1 ** t)) / (np.sqrt(vV / (1 - b2 ** t)) + eps)
        P = U @ V.T
        S = Knp * P
        minm = float(S.min())
        obj = float(np.exp(-S).sum())
        if best[0] is None or obj < best[0]:
            best = (obj, minm, k)
        elif minm > best[1]:
            best = (min(best[0], obj), minm, k)
        if minm >= ACCEPT:
            Ui = np.rint(U * SCALE).astype(np.int64)
            Vi = np.rint(V * SCALE).astype(np.int64)
            accepted.append({"r": r, "seed": k, "den": SCALE,
                             "float_min_margin": repr(minm), "float_obj": repr(obj),
                             "U": Ui.tolist(), "V": Vi.tolist()})
            log("  r=%d seed=%d ACCEPTED (float min margin %.6g)" % (r, k, minm))
        if (k + 1) % 50 == 0:
            log("  r=%d restart %d/%d  best obj %.6g  best min margin %.6g" % (r, k + 1, restarts, best[0], best[1]))
    return best, accepted


def main():
    quick = "--quick" in sys.argv
    out_path = os.path.join(DATA, "40_candidates.json")
    log_path = os.path.join(ROOT, "logs", "40_r20_search.out")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    fh = open(log_path, "w", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        fh.write(msg + "\n")
        fh.flush()

    K = load_K()
    Knp = np.array(K, dtype=np.float64)
    log("=" * 100)
    log("O222 R20 M3 discovery -- sign realizations of the frozen %dx%d matrix K" % Knp.shape)
    log("protocol: Adam lr=%.2f steps=%d restarts=%d init N(0,1/r) seeds rng(%d+1000r+k) accept min margin >= %.0e"
        % (LR, STEPS, RESTARTS, SEED0, ACCEPT))
    log("quick mode: %s" % quick)
    log("=" * 100)
    all_accepted = []
    summary = {}
    t0 = time.time()
    for r in RS:
        restarts = 6 if quick else RESTARTS
        steps = 300 if quick else STEPS
        log("-- r = %d : %d restarts x %d steps" % (r, restarts, steps))
        best, acc = run_r(Knp, r, restarts, steps, log)
        summary[str(r)] = {"best_obj": best[0], "best_min_margin": best[1], "best_seed": best[2],
                           "accepted": len(acc), "restarts": restarts, "steps": steps}
        all_accepted.extend(acc)
        log("   ==> r=%d accepted=%d  best obj %.6g  best min margin %.6g  (elapsed %.1f s)"
            % (r, len(acc), best[0], best[1], time.time() - t0))
    payload = {"protocol": {"objective": "sum exp(-K_ij (U V^T)_ij)", "lr": LR, "steps": STEPS,
                            "restarts": RESTARTS, "init": "N(0,1/r)", "seed0": SEED0, "accept_min_margin": ACCEPT,
                            "grid": SCALE, "quick": quick},
               "K_shape": list(Knp.shape), "summary": summary, "candidates": all_accepted,
               "elapsed_s": round(time.time() - t0, 2)}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    log("wrote %s  (%d candidates total, %.1f s)" % (out_path, len(all_accepted), time.time() - t0))
    fh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
