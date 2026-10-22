#!/usr/bin/env python3
"""
O58 script 12 — K[0,0,0] = 4 = B? Exploration.
K[0,0,0] is the self-triple-intersection of divisor 0 (first divisor).
Questions:
  1. What is divisor 0 geometrically? (GLSM charge, ray)
  2. Is K[0,0,0]=4 universal across the 100 (36,98) instances?
  3. K[i,i,i] diagonal — any structure (B, N_d, φ-related)?
  4. Does the 3×12 block structure of O53 show up in the TRUE κ?
"""
import subprocess, os, json, sys, numpy as np, math
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PHI = (1 + math.sqrt(5)) / 2

def parse_poly_file(path):
    lines = open(path).read().splitlines()
    polies = []
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            coords = []
            ok = True
            j = i + 1
            for _ in range(n):
                if j >= len(lines):
                    ok = False
                    break
                cp = lines[j].split()
                if len(cp) != d:
                    ok = False
                    break
                try:
                    coords.append([int(x) for x in cp])
                except ValueError:
                    ok = False
                    break
                j += 1
            if ok:
                polies.append(coords)
                i = j
                continue
        i += 1
    return polies

def build_kappa(coords):
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v
    return K, cy

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()

    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    K, cy = build_kappa(canon)

    # 1. diagonal K[i,i,i]
    diag = [K[i,i,i] for i in range(36)]
    nnz_diag = [(i, v) for i, v in enumerate(diag) if v != 0]
    print(f"Diagonal K[i,i,i]: {len(nnz_diag)} non-zero")
    print("  values:", sorted(set(v for _, v in nnz_diag)))
    print("  first 12:", [(i, v) for i, v in nnz_diag[:12]])

    # 2. K[0,0,0] context — divisor 0 GLSM charge
    glsm = cy.glsm_charge_matrix()  # (32,37) per skill
    print(f"\nGLSM shape: {glsm.shape}")
    # divisor 0 charge (first ray)
    print("Ray 0 charge (first row of GLSM):", glsm[0] if glsm.shape[0] > 0 else "?")

    # 3. K[i,i,j] patterns
    Kii = np.zeros((36, 36))  # K[i,i,j]
    for i in range(36):
        for j in range(36):
            Kii[i, j] = K[i, i, j]
    row_sums = Kii.sum(axis=1)
    print(f"\nK[i,i,:] row sums: min={row_sums.min()}, max={row_sums.max()}")
    print("  K[0,0,:] row:", [(j, int(Kii[0,j])) for j in range(36) if Kii[0,j] != 0][:15])

    # 4. 3×12 block structure on TRUE κ (O53 used raw; re-verify)
    blocks = np.zeros((3, 3, 3))
    for b0 in range(3):
        for b1 in range(3):
            for b2 in range(3):
                sub = K[b0*12:(b0+1)*12, b1*12:(b1+1)*12, b2*12:(b2+1)*12]
                blocks[b0, b1, b2] = np.count_nonzero(sub)
    print(f"\n3×12 block nnz matrix:\n{blocks.astype(int)}")
    same = blocks[0,0,0] + blocks[1,1,1] + blocks[2,2,2]
    cross = blocks.sum() - same
    ratio = same / cross if cross else float('inf')
    print(f"same-block nnz: {same}, cross-block nnz: {cross}, ratio: {ratio:.3f}")

    # 5. Check K[0,0,0] across multiple instances (sampling 8)
    polies = parse_poly_file("all_36_98.poly")
    print("\nK[0,0,0] across instances:")
    k000_vals = []
    for idx in [0, 1, 2, 3, 10, 20, 50, 89]:
        try:
            Kk, _ = build_kappa(polies[idx])
            k000_vals.append((idx, int(Kk[0,0,0])))
        except Exception as e:
            k000_vals.append((idx, str(e)[:40]))
    for idx, v in k000_vals:
        print(f"  instance {idx}: K[0,0,0]={v}")
    # note: divisor indexing is instance-specific (no canonical meaning across polytopes)
    print("  ⚠️ NOTE: divisor 0 has NO canonical meaning across different polytope normal forms")

    results = dict(diag_nnz=len(nnz_diag), diag_values=sorted(set(v for _, v in nnz_diag)),
                   K000=float(K[0,0,0]), block_ratio=float(ratio),
                   k000_across=k000_vals)
    with open("k000_exploration.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nSaved data/k000_exploration.json")

if __name__ == "__main__":
    main()
