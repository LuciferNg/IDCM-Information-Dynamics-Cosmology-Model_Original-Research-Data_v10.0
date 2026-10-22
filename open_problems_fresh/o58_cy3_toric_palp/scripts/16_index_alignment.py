#!/usr/bin/env python3
"""
O58 script 16 — Index alignment: CYTools intersection_numbers() divisor
indices vs polytope points vs GLSM rays. The -360 divisor (index 35) and
-232 divisor (index 7) need correct geometric identification.
"""
import os, json, numpy as np
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

    pts = P.points()
    print(f"total points: {len(pts)}")
    # CYTools convention: points()[0] = origin, [1:] = rays + interior
    # Find which points are VERTICES (extremal)
    verts = P.vertices()
    print(f"vertices: {len(verts)}")
    # rays = boundary points excluding origin (per skill: 37 rays = 32 coord + 5 non-coord)
    # but P.points() may list 48 points: origin + 37 rays + 10 interior?

    # divisor basis maps to which points? cy.divisor_basis() = 32 indices (1-based)
    basis = cy.divisor_basis()
    print(f"divisor_basis (1-based): {basis.tolist()}")

    # The 36 intersection indices = prime toric divisors
    pd = cy.prime_toric_divisors()
    print(f"prime_toric_divisors count: {len(pd) if hasattr(pd, '__len__') else 'n/a'}")

    # GLSM rays: 37 rays = 37 columns
    glsm = cy.glsm_charge_matrix()
    print(f"GLSM: {glsm.shape} (32 U1 × 37 rays)")

    # Point index → divisor index mapping:
    # intersection_numbers keys are 1-based divisor indices 1..36
    # Which point does divisor 35 correspond to? The last prime divisor.
    # Check: point indices vs divisor indices. divisors 1..36 ↔ points 1..36?
    for didx in [1, 7, 35, 36]:
        if didx < len(pts):
            print(f"divisor index {didx} → point {list(pts[didx])}")

    # ray index in GLSM (0-based) vs point index (0-based): GLSM column i ↔ point i+1?
    # skill says 37 rays: rays 0,3,4,7,8 non-coordinate
    print("\nNon-coordinate ray check (GLSM columns 0,3,4,7,8):")
    for c in [0, 3, 4, 7, 8]:
        col = glsm[:, c]
        if c < len(pts):
            print(f"  GLSM col {c} (point {list(pts[c])}): sum={int(col.sum())}")

    # The -360 divisor: find its point
    # intersection index 35 (0-based) = divisor 36 (1-based) → point 36?
    print(f"\npoint 36 (1-based divisor 36): {list(pts[36])}")
    print(f"point 7 (1-based divisor 7): {list(pts[7])}")

    # volumes: compute divisor volumes at uniform t to see which divisors are 'special'
    import numpy as np
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    # divisor volumes V_i = 1/2 Σ_jk K[i,j,k] t_j t_k at t = 1/36
    t = np.ones(36) / 36
    V = 0.5 * np.einsum('ijk,j,k->i', K, t, t)
    print("\nDivisor volumes at uniform t (top 8):")
    order = np.argsort(-V)
    for idx in order[:8]:
        print(f"  divisor {idx} (1-based {idx+1}): V={V[idx]:.4f}")

    print("\nSaved alignment notes to data/index_alignment.json")
    json.dump(dict(basis=basis.tolist(),
                   pts_7=list(pts[7]), pts_35=list(pts[35]), pts_36=list(pts[36]),
                   divisor_volumes=[float(v) for v in V]), open("index_alignment.json", "w"))

if __name__ == "__main__":
    main()
