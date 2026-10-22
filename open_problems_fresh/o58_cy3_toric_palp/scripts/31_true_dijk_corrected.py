#!/usr/bin/env python3
"""
O58 script 31 — CORRECTED true d_ijk computation.
FIX: CYTools intersection_numbers() keys are 0-based (divisor d ↔ pts[d]).
The old script 08 did `i-1, j-1, k-1` (double-shift) → WRONG mapping.
Rebuild K[36³] directly from raw keys (no shift), recompute:
  nnz, rank, d_tensor correlation, kappa_36d_raw comparison.
"""
import subprocess, os, json, sys, numpy as np
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OLD_DATA = "/home/wsl/Projects/IDCM-Original/ICDM-v6.0--Information-Dynamics-Cosmology-Model/data/cy_search/data"

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()

    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    print("reflexive:", P.is_reflexive(), "h11,h21:", P.h11(), P.h21())
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    print("intersection dict entries:", len(inter))
    print("key range:", min(min(k) for k in inter), "-", max(max(k) for k in inter))

    # CORRECT: keys are 0-based divisor indices. divisor d ↔ pts[d].
    # K has 36 dims (h11=36); keys with index >= 36 would be beyond h11
    # (e.g. extra rays) — keep only < 36.
    K = np.zeros((36, 36, 36))
    skipped = 0
    for (i, j, k), v in inter.items():
        if i < 36 and j < 36 and k < 36:
            K[i, j, k] = v
        else:
            skipped += 1
    nnz = np.count_nonzero(K)
    print(f"dense 36³: {nnz} non-zero ({nnz/36**3*100:.2f}%), K[0,0,0]={K[0,0,0]}, skipped keys: {skipped}")
    print(f"diagonal K[d,d,d]: {[int(K[d,d,d]) for d in range(36) if K[d,d,d]!=0]}")

    # rank tests
    for mode in range(3):
        axes = [mode] + [m for m in range(3) if m != mode]
        M = K.transpose(axes).reshape(36, -1)
        print(f"  mode-{mode} flatten rank: {np.linalg.matrix_rank(M)}")

    # 12×12×12 sub-blocks
    print("\n12×12×12 sub-block nnz scan:")
    for b0 in range(0, 36, 12):
        for b1 in range(0, 36, 12):
            for b2 in range(0, 36, 12):
                sub = K[b0:b0+12, b1:b1+12, b2:b2+12]
                n = np.count_nonzero(sub)
                if n:
                    print(f"  block ({b0//12},{b1//12},{b2//12}): {n} nnz")

    # d_tensor correlation (CORRECT: use raw keys, first 12 divisors = K[0:12])
    dt_path = "/home/wsl/Projects/IDCM/IDCM-v10.0/data/d_tensor_final.npy"
    if os.path.exists(dt_path):
        dt = np.load(dt_path)
        print(f"\nd_tensor_final: shape={dt.shape}, rank={np.linalg.matrix_rank(dt.reshape(12,-1))}, nnz={np.count_nonzero(dt)}")
        K00 = K[0:12, 0:12, 0:12]
        print(f"K block (0,0,0) [divisors 0-11]: rank={np.linalg.matrix_rank(K00.reshape(12,-1))}, nnz={np.count_nonzero(K00)}")
        flatK = K00.flatten()
        flatD = dt.flatten()
        mask = (np.abs(flatK) > 0) | (np.abs(flatD) > 0)
        if mask.sum() > 2:
            corr = np.corrcoef(flatK[mask], flatD[mask])[0,1]
            print(f"K[0:12] vs d_tensor corr (nonzero mask): {corr:.4f}")

    # kappa_36d_raw re-audit (old file uses 1-based? check keys)
    raw_path = os.path.join(OLD_DATA, "kappa_36d_raw.json")
    if os.path.exists(raw_path):
        raw = json.load(open(raw_path))
        entries = raw.get("kappa", raw)
        print(f"\nkappa_36d_raw: {len(entries)} entries, sample keys: {list(entries)[:5]}")
        # build both interpretations
        Kraw0 = np.zeros((36,36,36))  # keys as-is (0-based)
        Kraw1 = np.zeros((36,36,36))  # keys-1 (1-based)
        for key, val in entries.items():
            parts = [int(x) for x in key.split(",")]
            if len(parts) == 3:
                i, j, k = parts
                if i < 36 and j < 36 and k < 36:
                    Kraw0[i,j,k] = val
                if i-1 >= 0 and j-1 >= 0 and k-1 >= 0:
                    Kraw1[i-1,j-1,k-1] = val
        nnz0, nnz1 = np.count_nonzero(Kraw0), np.count_nonzero(Kraw1)
        print(f"  as 0-based: nnz={nnz0}, matches true diag: {[d for d in range(36) if Kraw0[d,d,d]!=0]}")
        print(f"  as 1-based: nnz={nnz1}, matches true diag: {[d for d in range(36) if Kraw1[d,d,d]!=0]}")
        agree0 = np.sum((K != 0) & (Kraw0 != 0) & (K == Kraw0))
        agree1 = np.sum((K != 0) & (Kraw1 != 0) & (K == Kraw1))
        shared0 = np.sum((K != 0) & (Kraw0 != 0))
        shared1 = np.sum((K != 0) & (Kraw1 != 0))
        print(f"  as 0-based: shared={shared0}, identical={agree0}")
        print(f"  as 1-based: shared={shared1}, identical={agree1}")

    # save CORRECT kappa
    np.save("kappa_36d_true.npy", K)
    with open("true_kappa_summary.json", "w") as f:
        json.dump(dict(nnz=int(nnz), sparsity=round(nnz/36**3, 4),
                       K000=float(K[0,0,0]),
                       diag={int(d): int(K[d,d,d]) for d in range(36) if K[d,d,d]!=0}),
                  f, indent=2)
    print("\nSaved CORRECTED data/kappa_36d_true.npy + true_kappa_summary.json")

if __name__ == "__main__":
    main()
