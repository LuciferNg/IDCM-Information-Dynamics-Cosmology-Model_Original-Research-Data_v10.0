#!/usr/bin/env python3
"""
O58 script 35 — C: 12³ block vs d_tensor non-linear mapping scan.
Scan ALL 27 consecutive 12×12×12 sub-blocks of true κ vs d_tensor_final.
Question: is there ANY block with strong correlation (linear OR non-linear)?
Also try rank-1 / sign / sparsity-pattern comparisons.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
DT = "/home/wsl/Projects/IDCM/IDCM-v10.0/data/d_tensor_final.npy"

def main():
    os.chdir(DATA)
    K = np.load("kappa_36d_true.npy")
    dt = np.load(DT)
    print(f"K nnz={np.count_nonzero(K)}, dt nnz={np.count_nonzero(dt)}, dt shape={dt.shape}")

    results = []
    # 27 blocks: b0,b1,b2 in {0,12,24}
    for b0 in [0, 12, 24]:
        for b1 in [0, 12, 24]:
            for b2 in [0, 12, 24]:
                sub = K[b0:b0+12, b1:b1+12, b2:b2+12]
                n = np.count_nonzero(sub)
                if n == 0:
                    continue
                flatK = sub.flatten()
                flatD = dt.flatten()
                mask = (np.abs(flatK) > 0) | (np.abs(flatD) > 0)
                corr = np.corrcoef(flatK[mask], flatD[mask])[0,1] if mask.sum() > 2 else 0
                # sign agreement
                sign_agree = np.mean(np.sign(flatK[mask]) == np.sign(flatD[mask])) if mask.sum() else 0
                # rank
                rk = np.linalg.matrix_rank(sub.reshape(12, -1))
                results.append(dict(block=(b0//12, b1//12, b2//12), nnz=int(n),
                                    corr=round(float(corr), 4), rank=int(rk),
                                    sign_agree=round(float(sign_agree), 3)))
                print(f"block ({b0//12},{b1//12},{b2//12}): nnz={n:3d} rank={rk:2d} corr={corr:+.4f} sign_agree={sign_agree:.2f}")
    # sort by |corr|
    results.sort(key=lambda r: -abs(r["corr"]))
    print("\nTop |corr| blocks:")
    for r in results[:5]:
        print(f"  {r['block']}: corr={r['corr']}")
    json.dump(results, open("block_vs_dtensor_scan.json", "w"), indent=2)
    print("\nSaved data/block_vs_dtensor_scan.json")

if __name__ == "__main__":
    main()
