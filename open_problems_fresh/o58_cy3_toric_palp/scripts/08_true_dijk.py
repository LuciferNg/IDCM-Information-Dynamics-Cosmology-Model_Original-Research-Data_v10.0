#!/usr/bin/env python3
"""
O58 script 08 — REAL d_ijk from the canonical (36,98) polytope via CYTools.
Purpose: O50 upgrade — compare the true CY₃ triple intersection tensor
(36³ dense, from cy.intersection_numbers()) against:
  1. d_tensor_final.npy (12³ float, rank 12, WDVV-cleaned — the IDCM carrier)
  2. kappa_36d_raw.json (old, NOT trustworthy — re-audit)
Report: nnz counts, rank, sparsity, block structure, any 12×12×12 sub-block
that could map to d_tensor.
"""
import subprocess, os, json, sys, numpy as np
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
O53_DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data"
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

    # build dense 36³ via 6-permutation (keys are 1-based)
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        i0, j0, k0 = i - 1, j - 1, k - 1
        for a, b, c in permutations((i0, j0, k0)):
            K[a, b, c] = v
    nnz = np.count_nonzero(K)
    print(f"dense 36³: {nnz} non-zero ({nnz/36**3*100:.2f}%), K[0,0,0]={K[0,0,0]}")
    np.save("kappa_36d_true.npy", K)

    # rank tests (flatten modes)
    for mode in range(3):
        # mode-0 flatten: K[i,:,:] as rows; mode-1: K[:,j,:]; mode-2: K[:,:,k]
        axes = [mode] + [m for m in range(3) if m != mode]
        M = K.transpose(axes).reshape(36, -1)
        print(f"  mode-{mode} flatten rank: {np.linalg.matrix_rank(M)}")

    # 12×12×12 sub-blocks: all consecutive-block triples
    print("\n12×12×12 sub-block nnz scan (blocks 0-2, 3-5, ...):")
    for b0 in range(0, 36, 12):
        for b1 in range(0, 36, 12):
            for b2 in range(0, 36, 12):
                sub = K[b0:b0+12, b1:b1+12, b2:b2+12]
                n = np.count_nonzero(sub)
                if n:
                    print(f"  block ({b0//12},{b1//12},{b2//12}): {n} nnz")

    # load d_tensor_final.npy
    dt_path = "/home/wsl/Projects/IDCM/IDCM-v10.0/data/d_tensor_final.npy"
    if os.path.exists(dt_path):
        dt = np.load(dt_path)
        print(f"\nd_tensor_final: shape={dt.shape}, rank={np.linalg.matrix_rank(dt.reshape(12,-1))}, nnz={np.count_nonzero(dt)}")
        # compare with the (0,0,0) 12-block of K (first 12 divisors)
        K00 = K[0:12, 0:12, 0:12]
        print(f"K block (0,0,0): rank={np.linalg.matrix_rank(K00.reshape(12,-1))}, nnz={np.count_nonzero(K00)}")
        # correlation of flattened values
        if K00.size == dt.size:
            flatK = K00.flatten()
            flatD = dt.flatten()
            mask = (np.abs(flatK) > 0) | (np.abs(flatD) > 0)
            if mask.sum() > 2:
                corr = np.corrcoef(flatK[mask], flatD[mask])[0,1]
                print(f"K[0:12] vs d_tensor corr (nonzero mask): {corr:.4f}")
    else:
        print("\nd_tensor_final.npy NOT FOUND at", dt_path)

    # kappa_36d_raw re-audit
    raw_path = os.path.join(OLD_DATA, "kappa_36d_raw.json")
    if os.path.exists(raw_path):
        raw = json.load(open(raw_path))
        entries = raw.get("kappa", raw)
        Kraw = np.zeros((36, 36, 36))
        for key, val in entries.items():
            parts = [int(x) for x in key.split(",")]
            if len(parts) == 3:
                i, j, k = parts
                for a, b, c in permutations((i, j, k)):
                    Kraw[a, b, c] = val
        nnz_raw = np.count_nonzero(Kraw)
        # compare with true
        agree = np.sum((K != 0) & (Kraw != 0) & (K == Kraw))
        print(f"\nkappa_36d_raw: nnz={nnz_raw}, K[0,0,0]={Kraw[0,0,0]}")
        print(f"shared nnz entries with true: {np.sum((K!=0)&(Kraw!=0))}, identical values: {agree}")

    with open("true_kappa_summary.json", "w") as f:
        json.dump(dict(nnz=int(nnz), sparsity=round(nnz/36**3, 4),
                       K000=float(K[0,0,0])), f, indent=2)
    print("\nSaved data/kappa_36d_true.npy + true_kappa_summary.json")

if __name__ == "__main__":
    main()
