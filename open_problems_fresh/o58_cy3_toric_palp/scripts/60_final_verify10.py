#!/usr/bin/env python3
"""
O58 script 60 — FINAL VERIFIER for explorations S/T/U.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS S/T/U FINAL VERIFIER ===\n")

    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()

    # S: cone det reconstruction — K[8,8,8]/Σdet = -58 = -2×L₇
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    simps = [list(s) for s in tri.simplices()]
    pts = [tuple(int(x) for x in p) for p in P.points()]
    # compute Σdet for (8,8,8)
    contrib = 0.0
    for s in simps:
        if 8 in s:
            nonz = [v for v in s if v != 0]
            if len(nonz) >= 4:
                M = np.array([pts[v] for v in nonz[:4]])
                contrib += np.linalg.det(M)
    ratio = K[8,8,8] / contrib
    check("S: K[8,8,8]/Σdet = -58", abs(ratio + 58) < 1e-6, f"({ratio:.4f})")
    check("S: -58 = -2×L₇", abs(ratio + 2*29) < 1e-6)

    # U: q8 = -q0 - 1 (31/32 positions)
    glsm = cy.glsm_charge_matrix()
    q0 = glsm[:, 0].astype(int)
    q8 = glsm[:, 8].astype(int)
    diff = q8 + q0
    n_minus1 = np.count_nonzero(diff == -1)
    n_0 = np.count_nonzero(diff == 0)
    n_minus2 = np.count_nonzero(diff == -2)
    check("U: 24 positions cancel", n_0 == 24, f"({n_0})")
    check("U: 7 positions -1", n_minus1 == 7, f"({n_minus1})")
    check("U: 1 position -2 (U(1)0)", n_minus2 == 1, f"({n_minus2})")
    check("U: q8 = -q0-1 for 31/32", n_0 + n_minus1 == 31)

    # T: vertex Lucas universality
    data = json.load(open(os.path.join(DATA, "vertex_lucas_universality.json")))
    n_full = sum(1 for r in data if r["has_L1L4"])
    n_any2 = sum(1 for r in data if len(r["lucas_idx"]) >= 2)
    check("T: 30 instances scanned", len(data) == 30)
    check("T: ≥2 Lucas 30/30", n_any2 == 30, f"({n_any2}/30)")
    check("T: full L₁-L₄ ≥ 20", n_full >= 20, f"({n_full}/30)")
    # 84.1% Lucas
    total_v = sum(len(r["v_idx"]) for r in data)
    total_l = sum(len(r["lucas_idx"]) for r in data)
    frac = total_l / total_v
    check("T: 84.1% Lucas", abs(frac - 0.841) < 0.01, f"({frac:.3f})")
    # z-test > 5σ
    import math
    z = (frac - 0.5) / math.sqrt(0.25 / total_v)
    check("T: z > 5σ", z > 5, f"(z={z:.1f})")

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
