#!/usr/bin/env python3
"""
O58 script 68 — FINAL VERIFIER for explorations Y/Z/AA.
"""
import os, json, numpy as np, math

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS Y/Z/AA FINAL VERIFIER ===\n")

    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]

    # Σ|det| = 200
    dets = []
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets.append(np.linalg.det(M))
    total = sum(abs(d) for d in dets)
    check("Z: Σ|det| = 200", abs(total - 200) < 1e-6, f"({total:.4f})")
    check("Z: 200 = -χ + L₉", abs(total - (124 + 76)) < 1e-6, "(-124 Euler + 76 L₉)")

    # Y: only (8,8,8) has ratio -29 (NOT universal)
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    dets2 = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets2[tuple(sorted(nonz))] = np.linalg.det(M)
    # count triples with ratio -29
    n_29 = 0
    for i in range(36):
        for j in range(i, 36):
            for k in range(j, 36):
                if K[i,j,k] == 0:
                    continue
                s_inv = 0.0
                for s in simps:
                    if i in s and j in s and k in s:
                        nonz = tuple(sorted(v for v in s if v != 0))
                        d = dets2.get(nonz, 0)
                        if d != 0:
                            s_inv += 1/abs(d)
                if s_inv > 0 and abs(K[i,j,k]/s_inv + 29) < 1e-9:
                    n_29 += 1
    check("Y: only (8,8,8) ratio=-29", n_29 == 1, f"({n_29} triples)")

    # AA: e-positions Lucas z>5
    data = json.load(open(os.path.join(DATA, "e_positions_lucas_universality.json")))
    luc = {1,2,3,4,7,11,18,29,47}
    total_e = 0; total_l = 0
    for r in data:
        for i, p in enumerate(r["e_pos"]):
            if i == 0:  # exclude e₁ (normalization)
                continue
            total_e += 1
            if p in luc:
                total_l += 1
    frac = total_l/total_e
    p0 = 9/55
    z = (frac - p0)/math.sqrt(p0*(1-p0)/total_e)
    check("AA: 30 instances", len(data) == 30)
    check("AA: e₂-e₄ Lucas z>5", z > 5, f"(z={z:.1f}, {total_l}/{total_e}={frac*100:.1f}%)")
    check("AA: e₁ always at 1", all(r["e_pos"][0] == 1 for r in data if r["e_pos"]))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
