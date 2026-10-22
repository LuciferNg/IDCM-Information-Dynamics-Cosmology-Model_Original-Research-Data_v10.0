#!/usr/bin/env python3
"""
O58 script 64 — FINAL VERIFIER for explorations V/W/X.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS V/W/X FINAL VERIFIER ===\n")

    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]

    # X: GLSM correspondence — col d ↔ pts[d]
    glsm = cy.glsm_charge_matrix()
    q0 = glsm[:, 0].astype(int)
    q8 = glsm[:, 8].astype(int)
    check("X: glsm shape (32,37)", glsm.shape == (32, 37))
    check("X: col0 sum=-742", q0.sum() == -742, f"({q0.sum()})")
    check("X: col8 sum=+733", q8.sum() == 733, f"({q8.sum()})")
    check("X: pts[8] = e₁+e₂", pts[8] == (1, 1, 0, 0))
    check("X: pts[1]+pts[47]=pts[8]", tuple(np.array(pts[1]) + np.array(pts[47])) == pts[8])
    # e1-e4 at Lucas positions {1,3,7,47}
    e_positions = [i for i, p in enumerate(pts) if p in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]]
    check("X: unit vectors at Lucas positions", set(e_positions) == {1, 3, 7, 47}, f"({e_positions})")

    # V: K[8,8,8] = -L₇ × Σ 1/|det| over star of 8
    dets = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets[tuple(sorted(nonz))] = np.linalg.det(M)
    total_abs = sum(abs(v) for v in dets.values())
    check("V: Σ|det| = 200", abs(total_abs - 200) < 1e-6, f"({total_abs:.4f})")
    # sum 1/|det| over cones containing 8
    s_inv = 0.0
    for s in simps:
        if 8 in s:
            nonz = tuple(sorted(v for v in s if v != 0))
            d = dets.get(nonz, 0)
            if d != 0:
                s_inv += 1/abs(d)
    check("V: Σ1/|det| (star 8) = 8", abs(s_inv - 8) < 1e-6, f"({s_inv:.4f})")
    check("V: K[8,8,8] = -L₇×8", K[8,8,8] == -29 * s_inv, f"({K[8,8,8]} vs {-29*s_inv})")

    # W: corrected fraction 61.6% (mostly from normalization indices 1,2,3)
    data = json.load(open(os.path.join(DATA, "vertex_lucas_universality.json")))
    from collections import Counter
    idx_counter = Counter()
    for r in data:
        for i in r["v_idx"]:
            idx_counter[i] += 1
    total_v = sum(idx_counter.values())
    lucas_set = {1, 2, 3, 4, 7, 11, 18}
    total_l = sum(v for i, v in idx_counter.items() if i in lucas_set)
    frac = total_l / total_v
    check("W: Lucas fraction ~61.6%", abs(frac - 0.616) < 0.02, f"({frac:.3f})")
    check("W: NOT 84.1% (old bug)", abs(frac - 0.841) > 0.1, f"({frac:.3f})")
    # excluding normalization indices 1,2,3 → no Lucas tendency
    excl = total_v - idx_counter[1] - idx_counter[2] - idx_counter[3]
    lucas_excl = total_l - idx_counter[1] - idx_counter[2] - idx_counter[3]
    frac_excl = lucas_excl / excl
    check("W: excl 1,2,3 → ~37% (no tendency)", frac_excl < 0.5, f"({frac_excl:.3f})")
    check("W: index 1,2,3 in all", all(1 in r["v_idx"] and 2 in r["v_idx"] and 3 in r["v_idx"] for r in data))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
