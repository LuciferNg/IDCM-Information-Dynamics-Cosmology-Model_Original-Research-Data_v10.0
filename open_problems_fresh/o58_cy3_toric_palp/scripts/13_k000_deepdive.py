#!/usr/bin/env python3
"""
O58 script 13 — Deep dive: K[0,0,35] = -44 (=-N_d) and K[7,7,7] = -232.
Also: full K[0,0,:] row and K[i,i,i] diagonal analysis with K_Chain lens.
Q: does -44 (= -N_d) appear systematically? What about 232 = 2×116 = ? 
232 = 44+44+144? = 88+144? 144 = 12²? 
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

    print("=== K[0,0,:] full row ===")
    row0 = [(j, int(K[0,0,j])) for j in range(36) if K[0,0,j] != 0]
    for j, v in row0:
        print(f"  K[0,0,{j:2d}] = {v:5d}")

    print("\n=== K[7,:,:] row (divisor 7) ===")
    row7 = [(j, int(K[7,7,j])) for j in range(36) if K[7,7,j] != 0]
    for j, v in row7:
        print(f"  K[7,7,{j:2d}] = {v:6d}")

    print("\n=== Diagonal K[i,i,i] full ===")
    diag = [(i, int(K[i,i,i])) for i in range(36) if K[i,i,i] != 0]
    for i, v in diag:
        print(f"  K[{i:2d},{i:2d},{i:2d}] = {v:6d}")

    # sums
    print(f"\nΣ K[i,i,i] = {sum(v for _, v in diag)}")
    print(f"Σ |K[i,i,i]| = {sum(abs(v) for _, v in diag)}")

    # structure: -44 appears in K[0,0,35]; is 44 = N_d?
    # check all K[i,i,j] == ±44 or ±88 etc
    print("\n=== K[i,i,j] values ±44, ±88, ±90, ±124 search ===")
    targets = {44, 88, 90, 124, 178}
    hits = []
    for i in range(36):
        for j in range(36):
            v = int(K[i,i,j])
            if abs(v) in targets:
                hits.append((i, j, v))
    for h in hits[:30]:
        print(f"  K[{h[0]},{h[0]},{h[1]}] = {h[2]}")
    print(f"  total hits: {len(hits)}")

    # 232 factorization
    print("\n=== 232 analysis ===")
    print("  232 = 2³×29 = 8×29; 232 = 44+44+144; 232 = 88+144; 144=12²")
    print("  232 = Σγ(90)×2 + 52? no. 232 = 178+54? no.")
    print("  232 = 2×116; 116 = 2×58; 58 = 2×29")

    results = dict(row0=row0, row7=row7, diag=diag,
                   sum_diag=sum(v for _, v in diag),
                   sum_abs_diag=sum(abs(v) for _, v in diag),
                   target_hits=hits[:30])
    with open("k000_deepdive.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nSaved data/k000_deepdive.json")

if __name__ == "__main__":
    main()
