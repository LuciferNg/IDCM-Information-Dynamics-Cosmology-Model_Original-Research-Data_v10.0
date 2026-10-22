#!/usr/bin/env python3
"""
O58 script 25 — Option 2: WHY pts[8]→L₇=29 but pts[36]→N_d+1=45?
Z₂ mirror pair (1,1,0,0) ↔ (-1,-1,0,0). Investigate:
  1. Which blocks do pts[8] (K idx 7) and pts[36] (K idx 35) sit in?
     pts[8]: K[7,...] → block 0 (0-11)
     pts[36]: K[35,...] → block 2 (24-35)
  2. Full K[i,i,:] rows for both — the intersection structure
  3. -K/8 = 29 vs 45: 45 = 29 + 16? 16 = 4² = B²? 29 = L₇, 45 = L₇+F₈? F₈=21 → 29+21=50≠45
     45-29 = 16 = B² = 4²  ← KEY!
  4. GLSM charges of rays pts[8], pts[36]
  5. Volume at φ-tip: pts[8] huge positive (13.5), pts[36] huge negative (-21.8)
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

    print("=== Option 2: 29 vs 45 asymmetry ===")
    print(f"45 - 29 = {45-29} = 16 = B² = 4²  ← KEY structural difference")
    print(f"L₇ = 29 (Lucas), N_d+1 = 45")
    print(f"45 = 29 + 16 = L₇ + B²")
    print(f"45 = 44 + 1 = N_d + 1")

    # 1. Block membership
    print(f"\npts[8] → K idx 7 → block {7//12}")
    print(f"pts[36] → K idx 35 → block {35//12}")

    # 2. Full K[7,7,:] and K[35,35,:] rows
    print(f"\nK[7,7,:]  (pts[8]):  {[(j, int(K[7,7,j])) for j in range(36) if K[7,7,j]!=0]}")
    print(f"K[35,35,:] (pts[36]): {[(j, int(K[35,35,j])) for j in range(36) if K[35,35,j]!=0]}")

    # cross: K[7,35,:]
    print(f"\nK[7,35,:]: {[(j, int(K[7,35,j])) for j in range(36) if K[7,35,j]!=0]}")

    # 3. row sums (linear functional L_i = Σ_j K[i,i,j])
    s7 = sum(int(K[7,7,j]) for j in range(36))
    s35 = sum(int(K[35,35,j]) for j in range(36))
    print(f"\nΣ_j K[7,7,j] = {s7}")
    print(f"Σ_j K[35,35,j] = {s35}")
    print(f"Σ_j K[0,0,j] = {sum(int(K[0,0,j]) for j in range(36))}")

    # 4. GLSM charges of the rays
    glsm = cy.glsm_charge_matrix()
    for pid in [8, 36]:
        if pid < glsm.shape[1]:
            q = glsm[:, pid]
            print(f"\nray {pid} (pts[{pid}]): sum={int(q.sum())}, q[0]={q[0]}, q[2]={q[2]}")

    # 5. Volumes
    basis = cy.divisor_basis()
    t32 = np.array([PHI ** (35 - i) for i in range(32)])
    t32 /= t32.max()
    t36 = np.zeros(36)
    for idx, bidx in enumerate(basis):
        t36[bidx-1] = t32[idx]
    V = 0.5 * np.einsum('ijk,j,k->i', K, t36, t36)
    print(f"\nV[7] = {V[7]:.4f}, V[35] = {V[35]:.4f}")

    # 6. all -K/8 values for negative diag divisors
    print("\n=== negative diag divisors: -K/8 ===")
    L = [2, 1]
    for n in range(2, 16):
        L.append(L[-1] + L[-2])
    for i in range(36):
        v = int(K[i,i,i])
        if v < 0:
            q = -v / 8
            print(f"  K[{i},{i},{i}] = {v}  -K/8 = {q:.2f}")

    json.dump(dict(K7_row=[[j, int(K[7,7,j])] for j in range(36) if K[7,7,j]!=0],
                   K35_row=[[j, int(K[35,35,j])] for j in range(36) if K[35,35,j]!=0],
                   sum7=s7, sum35=s35,
                   V7=float(V[7]), V35=float(V[35])),
              open("option2_asymmetry.json", "w"))

if __name__ == "__main__":
    main()
