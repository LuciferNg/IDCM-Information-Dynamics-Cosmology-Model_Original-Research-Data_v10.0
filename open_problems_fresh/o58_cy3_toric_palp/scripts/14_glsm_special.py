#!/usr/bin/env python3
"""
O58 script 14 — GLSM charges of the "special" divisors (7, 35) with
large negative self-intersections, and -44/-360/-232 structure.
Also: which divisors have K[i,i,j]=±44 (K_Chain N_d)?
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
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    glsm = cy.glsm_charge_matrix()  # (32, 37): 32 U(1) × 37 rays
    print(f"GLSM shape: {glsm.shape}")
    # rays → divisors: 37 rays, divisor basis = 32 (36 divisors total incl. extra)
    # print full charge vectors for ray 7 and ray 35 (if they exist as rays)
    for rid in [0, 7, 35]:
        if rid < glsm.shape[1]:
            row = glsm[:, rid]
            print(f"\nRay {rid} charges (32 U(1)):")
            print("  ", row.tolist())
            print(f"  sum={int(row.sum())}, col-0 (dominant U1)={row[0]}, col-2={row[2]}")

    # which divisor index in divisor_basis maps to ray 7 / 35?
    basis = cy.divisor_basis()  # 1-based
    print(f"\ndivisor_basis (1-based): {basis.tolist()}")
    print(f"len basis: {len(basis)}")

    # all K[i,i,j] with |v| in {44, 88, 90, 178, 232, 360}
    print("\n=== K[i,i,j] special values ===")
    targets = {44, 88, 90, 178, 232, 360}
    for i in range(36):
        for j in range(36):
            v = int(K[i,i,j])
            if abs(v) in targets:
                print(f"  K[{i},{i},{j}] = {v}")

    # negative self-intersections list
    print("\n=== Negative diagonal divisors ===")
    for i in range(36):
        v = int(K[i,i,i])
        if v < 0:
            print(f"  K[{i},{i},{i}] = {v}")

    with open("glsm_special_divisors.json", "w") as f:
        json.dump(dict(basis=basis.tolist()), f, indent=2)
    print("\nSaved data/glsm_special_divisors.json")

if __name__ == "__main__":
    main()
