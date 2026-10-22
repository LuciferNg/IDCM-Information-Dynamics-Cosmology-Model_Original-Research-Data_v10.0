#!/usr/bin/env python3
"""
O58 script 17 — Identify divisors 7 & 35 (the -232 and -360 self-intersection
divisors) via: (a) φ-power tip divisor volumes, (b) GLSM dominant charge.
The goal: map K_Chain structure (N_d=44, B=4, L_7=29) onto real CY₃ divisors.
"""
import os, json, numpy as np, math
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PHI = (1 + math.sqrt(5)) / 2

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

    basis = cy.divisor_basis()  # 1-based 32 indices
    glsm = cy.glsm_charge_matrix()  # (32, 37)

    # φ-power t in divisor basis → 36D
    t32 = np.array([PHI ** (35 - i) for i in range(32)], dtype=float)
    t32 /= t32.max()
    t36 = np.zeros(36)
    for idx, bidx in enumerate(basis):
        t36[bidx - 1] = t32[idx]

    # divisor volumes V_i = 1/2 Σ_jk K[i,j,k] t_j t_k
    V = 0.5 * np.einsum('ijk,j,k->i', K, t36, t36)
    order = np.argsort(-V)
    print("Divisor volumes at φ-power tip (all 36):")
    for idx in order:
        print(f"  divisor {idx:2d}: V={V[idx]:10.4f}  diag K[i,i,i]={int(K[idx,idx,idx]):6d}")

    # GLSM dominant charge (col 0) per ray → map to divisors via basis
    print("\nGLSM dominant charge (col 0) for divisor-basis rays:")
    for idx, bidx in enumerate(basis):
        ray = bidx - 1  # 0-based ray
        if ray < glsm.shape[1]:
            q0 = int(glsm[0, ray])
            q2 = int(glsm[2, ray])
            if idx in (6, 34) or q0 != 0:  # divisor 7 (idx6), 35 (idx34)
                print(f"  basis[{idx}]→ray {ray}: q0={q0}, q2={q2}, V={V[bidx-1]:.4f}, diag={int(K[bidx-1,bidx-1,bidx-1])}")

    # focus: divisors 7 & 35
    print("\n=== FOCUS: divisors 7 & 35 ===")
    for didx in [7, 35]:
        print(f"divisor {didx}: V={V[didx]:.4f}, diag K={int(K[didx,didx,didx])}")
        # all K[didx,didx,j]
        row = [(j, int(K[didx,didx,j])) for j in range(36) if K[didx,didx,j] != 0]
        print(f"  K[{didx},{didx},:]: {row}")

    json.dump(dict(volumes=[float(v) for v in V],
                   diag=[int(K[i,i,i]) for i in range(36)]),
              open("divisor_identification.json", "w"))

if __name__ == "__main__":
    main()
