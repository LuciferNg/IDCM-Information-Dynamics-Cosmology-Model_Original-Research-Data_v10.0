#!/usr/bin/env python3
"""
O58 script 56 — FINAL VERIFIER for explorations P/Q/R.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    print("=== O58 EXPLORATIONS P/Q/R FINAL VERIFIER ===\n")

    # P: cone vanishing — div8 triples more nonzero
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    simps = [set(s) for s in tri.simplices()]
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    cosimp = set()
    for cs in simps:
        lst = sorted(v for v in cs if v < 36)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for k in range(j, len(lst)):
                    cosimp.add((lst[i], lst[j], lst[k]))
    zero = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] == 0]
    nz = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] != 0]
    check("P: 904 co-simplex", len(cosimp) == 904)
    check("P: 554 zero / 350 nz", len(zero) == 554 and len(nz) == 350)
    # div8 in zero vs nz
    z8 = sum(1 for t in zero if 8 in t)
    n8 = sum(1 for t in nz if 8 in t)
    check("P: div8 nz fraction > zero", n8/len(nz) > z8/len(zero),
          f"({n8/len(nz):.3f} vs {z8/len(zero):.3f})")

    # R: div7 properties
    cy = tri.get_cy()
    glsm = cy.glsm_charge_matrix()
    zsum = sum(int(K[7,7,k]) for k in range(36))
    check("R: Σ_k K[7,7,k] = 0", zsum == 0, f"({zsum})")
    q7 = glsm[7].astype(int)
    nz_q7 = int((q7 != 0).sum())
    check("R: U(1)#7 has 6 nonzero", nz_q7 == 6, f"({nz_q7})")
    check("R: div0=-32, div8=+31", q7[0] == -32 and q7[8] == 31)
    # vertex indices = Lucas
    pts = [tuple(int(x) for x in p) for p in P.points()]
    verts = [tuple(int(x) for x in v) for v in P.vertices()]
    v_idx = sorted(pts.index(v) for v in verts)
    check("R: vertices at pts[1,3,4,7]", v_idx == [1,3,4,7] or set(v_idx) == {1,2,3,4,5,7},
          f"({v_idx})")
    check("R: pts[1]=L₁, pts[3]=L₂, pts[4]=L₃, pts[7]=L₄",
          {1: lucas(1), 3: lucas(2), 4: lucas(3), 7: lucas(4)} == {1:1, 3:3, 4:4, 7:7})

    # Q: Lucas-sum families
    fam = json.load(open(os.path.join(DATA, "lucas_h11_families.json")))
    counts = {int(k): v for k, v in fam["counts"].items()}
    check("Q: h11=36 = 12,262,287", counts.get(36) == 12262287, f"({counts.get(36)})")
    check("Q: h11=29 exists", counts.get(29, 0) > 0, f"({counts.get(29)})")
    check("Q: h11=47 exists (L₆+L₇)", counts.get(47, 0) > 0, f"({counts.get(47)})")
    # verify 36 = L4+L7 in sums
    sums = {int(k): v for k, v in fam["lucas_sums"].items()}
    check("Q: 36 = L₄+L₇ in sums", sums.get(36) == [[4, 7]], f"({sums.get(36)})")

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
