#!/usr/bin/env python3
"""
O58 script 20 — Deep dive into divisor 7 (-232 = -8×L₇) and divisor 35 (-360).
Questions:
  1. Which polytope point / ray does intersection index 7 map to?
  2. GLSM charges of that ray (dominant U(1), anomaly)
  3. Is divisor 7 a blow-up divisor? (interior lattice point?)
  4. -232 = -8×29: is 8 = 2³ = B×2? Is 29 = L₇ the ONLY Lucas here?
  5. Relation to 3×12 block structure (O53): which block does div 7/35 sit in?
"""
import os, json, numpy as np, math
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    # 1. points: index 7 (divisor 7, 1-based 8?) vs 0-based
    pts = P.points()
    print(f"total points: {len(pts)}")
    print(f"point 7 (0-based): {list(pts[7])}")
    print(f"point 35 (0-based): {list(pts[35])}")
    print(f"point 36 (0-based): {list(pts[36])}")

    # are they vertices? interior?
    verts = P.vertices()
    print(f"vertices count: {len(verts)}")
    for idx in [7, 35, 36]:
        is_v = any(list(pts[idx]) == list(v) for v in verts)
        print(f"  point {idx}: vertex={is_v}")

    # 2. GLSM charges of ray 7 & 35
    glsm = cy.glsm_charge_matrix()  # (32, 37)
    print(f"\nGLSM: {glsm.shape}")
    for rid in [7, 35]:
        if rid < glsm.shape[1]:
            q = glsm[:, rid]
            print(f"ray {rid}: sum={int(q.sum())}, q[0]={q[0]}, q[2]={q[2]}, "
                  f"nonzero count={(q!=0).sum()}")

    # 3. block membership: divisor 7, 35 in which 12-block?
    print(f"\nblock of divisor 7: {7//12} (0-based), divisor 35: {35//12}")

    # 4. -232 = -8×29 structure: all K[i,i,j] that are multiples of 8
    mult8 = []
    for i in range(36):
        for j in range(36):
            v = int(K[i,i,j])
            if v != 0 and v % 8 == 0:
                mult8.append((i, j, v))
    print(f"\nK[i,i,j] divisible by 8: {len(mult8)} entries")
    for i, j, v in sorted(mult8, key=lambda x: -abs(x[2]))[:20]:
        print(f"  K[{i},{i},{j}] = {v} (=8×{v//8})")

    # 5. div 7/35 rows: all their triple intersections with structure
    r7 = [(j, int(K[7,7,j])) for j in range(36) if K[7,7,j]!=0]
    r735 = [(j, int(K[7,35,j])) for j in range(36) if K[7,35,j]!=0]
    print(f"\nK[7,7,:]: {r7}")
    print(f"K[7,35,:]: {r735}")

    # 6. Volume at φ-tip for div 7 vs others — hierarchy
    basis = cy.divisor_basis()
    t32 = np.array([math.pow((1+math.sqrt(5))/2, 35-i) for i in range(32)])
    t32 /= t32.max()
    t36 = np.zeros(36)
    for idx, bidx in enumerate(basis):
        t36[bidx-1] = t32[idx]
    V = 0.5 * np.einsum('ijk,j,k->i', K, t36, t36)
    order = np.argsort(-V)
    print("\nTop 10 divisors by volume @ φ-tip:")
    for idx in order[:10]:
        print(f"  div {idx}: V={V[idx]:.4f}, diag={int(K[idx,idx,idx])}")

    def clean(x):
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating,)):
            return float(x)
        if isinstance(x, list):
            return [clean(i) for i in x]
        return x

    json.dump(dict(pt7=clean(list(pts[7])), pt35=clean(list(pts[35])),
                    glsm7=clean(glsm[:,7].tolist()) if 7 < glsm.shape[1] else None,
                    glsm35=clean(glsm[:,35].tolist()) if 35 < glsm.shape[1] else None,
                    mult8=[[int(i), int(j), int(v)] for i, j, v in mult8]),
              open("div7_35_identity.json", "w"))

if __name__ == "__main__":
    main()
