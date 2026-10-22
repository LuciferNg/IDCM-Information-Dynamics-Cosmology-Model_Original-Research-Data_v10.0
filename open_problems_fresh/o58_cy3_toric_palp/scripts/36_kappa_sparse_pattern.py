#!/usr/bin/env python3
"""
O58 script 36 — F: κ sparse pattern — block structure + O53 3×12 correspondence.
True κ (350 nnz, corrected). Questions:
  1. Block distribution (3×12 blocks)
  2. Does the O53 3×12 structure (z=9.69σ) survive in CORRECTED κ?
  3. Diagonal / off-diagonal pattern
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    K = np.load("kappa_36d_true.npy")
    nnz_total = np.count_nonzero(K)
    print(f"True κ: {nnz_total} nnz / 36³ = {nnz_total/46656*100:.2f}%\n")

    # 1. 12×12×12 block distribution (3³=27 blocks)
    print("=== 12×12×12 block nnz matrix (rows b0, cols b1, each cell 3 blocks b2) ===")
    block_nnz = np.zeros((3,3,3), dtype=int)
    for b0 in range(3):
        for b1 in range(3):
            for b2 in range(3):
                sub = K[b0*12:(b0+1)*12, b1*12:(b1+1)*12, b2*12:(b2+1)*12]
                block_nnz[b0,b1,b2] = np.count_nonzero(sub)
    for b0 in range(3):
        row_str = []
        for b1 in range(3):
            row_str.append(f"b1={b1}:{list(block_nnz[b0,b1,:])}")
        print(f"  b0={b0}: {'  '.join(row_str)}")

    # 2. O53 3×12 structure: is there a 3-group × 12-block pattern?
    # O53 found 3×12 block structure with z=9.69σ. Test: group divisors 0-11,12-23,24-35
    print("\n=== 3-group × 3-group (12 each) nnz ===")
    g = np.zeros((3,3,3), dtype=int)
    for a in range(3):
        for b in range(3):
            for c in range(3):
                sub = K[a*12:(a+1)*12, b*12:(b+1)*12, c*12:(c+1)*12]
                g[a,b,c] = np.count_nonzero(sub)
    print(g)

    # 3. diagonal vs off-diagonal
    diag = sum(1 for d in range(36) if K[d,d,d] != 0)
    off = nnz_total - diag
    print(f"\ndiagonal entries: {diag}, off-diagonal: {off} ({off/nnz_total*100:.1f}%)")

    # 4. value distribution
    vals = K[K != 0]
    print(f"\nvalue distribution: min={int(vals.min())}, max={int(vals.max())}, "
          f"unique={len(np.unique(vals))}")
    from collections import Counter
    c = Counter(int(v) for v in vals)
    print("top values:", c.most_common(10))

    # 5. symmetric structure — how many distinct (i≤j≤k) entries?
    keys = set()
    for i in range(36):
        for j in range(36):
            for k in range(36):
                if K[i,j,k] != 0:
                    keys.add(tuple(sorted((i,j,k))))
    print(f"\ndistinct (i≤j≤k) entries: {len(keys)} (vs raw dict 361)")

    json.dump(dict(nnz=int(nnz_total), blocks=block_nnz.tolist(),
                   diag_entries=int(diag), off_diag=int(off)),
              open("kappa_sparse_pattern.json", "w"), indent=2)
    print("\nSaved data/kappa_sparse_pattern.json")

if __name__ == "__main__":
    main()
