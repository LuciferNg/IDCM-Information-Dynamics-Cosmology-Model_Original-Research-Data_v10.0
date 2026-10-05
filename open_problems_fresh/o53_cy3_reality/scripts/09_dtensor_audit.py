#!/usr/bin/env python3
"""
O53 Q2 延續: 已保存 d_tensor 嘅 rank 結構分析
================================================
檢查所有 data/d_tensor*.npy:
  - rank-1 可分離? 定係 WDVV 後有真正三體耦合?
  - 邊個 tensor 有真正 36 維結構?
  - eigenvalues_final 嘅來源驗證
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")

print("=" * 70)
print("O53 Q2: data/d_tensor*.npy rank 結構審計")
print("=" * 70)

files = sorted(f for f in os.listdir(DATA) if f.startswith("d_tensor") and f.endswith(".npy"))
print(f"\n發現 {len(files)} 個 d_tensor 檔案:")

for fn in files:
    path = os.path.join(DATA, fn)
    try:
        d = np.load(path)
        shape = d.shape
        size = d.size
        # 基本性質
        neg = np.sum(d < 0)
        pos = np.sum(d > 0)
        zero = np.sum(d == 0)
        
        # rank 分析 (flatten mode-0)
        if len(shape) == 3:
            D0 = d.reshape(shape[0], shape[1]*shape[2])
            r0 = np.linalg.matrix_rank(D0, tol=1e-10)
            # 全正? 
            all_pos = np.all(d >= 0) if size < 1e6 else np.all(d.flatten()[:10000] >= 0)
            # 可分離檢查 (抽樣)
            sep_err = None
            if shape[0] == shape[1] == shape[2] and shape[0] <= 40:
                try:
                    d_iii = np.array([d[i,i,i] for i in range(shape[0])])
                    a = np.cbrt(np.abs(d_iii))
                    errs = []
                    idx = np.random.default_rng(0).integers(0, shape[0], (200, 3))
                    for i, j, k in idx:
                        prod = a[i]*a[j]*a[k]
                        if prod > 0:
                            errs.append(abs(d[i,j,k]/prod - 1))
                    if errs:
                        sep_err = max(errs)
                except Exception:
                    pass
            print(f"\n  {fn}:")
            print(f"    shape={shape}, size={size}")
            print(f"    neg={neg}, pos={pos}, zero={zero}")
            print(f"    mode-0 flatten rank: {r0} / {shape[0]}")
            if sep_err is not None:
                print(f"    rank-1 可分離誤差: {sep_err:.2e} {'✅ rank-1' if sep_err < 1e-8 else '❌ 非 rank-1 (有三體耦合!)'}")
            # 對角線範圍
            d_diag = np.array([d[i,i,i] for i in range(min(shape[0], 12))])
            print(f"    d[i,i,i] 前 12: {np.array2string(d_diag, precision=3, suppress_small=True)}")
        else:
            print(f"\n  {fn}: shape={shape} (非 3-tensor)")
    except Exception as e:
        print(f"\n  {fn}: ❌ 載入失敗 {e}")

# eigenvalues
print("\n" + "=" * 70)
print("eigenvalues_final.npy:")
try:
    ev = np.load(os.path.join(DATA, "eigenvalues_final.npy"))
    print(f"  shape: {ev.shape}")
    print(f"  值: {ev}")
except Exception as e:
    print(f"  ❌ {e}")

print("=" * 70)
