#!/usr/bin/env python3
"""
O53: 12 維 d_tensor 嘅 Z₃ 結構驗證
====================================
問題: d_tensor_final (12³) 嘅「12 維」係咪真係 Z₃ 結構?
     定係 WDVV 優化嘅偶然結果?

驗證:
  1. d_tensor_final 有冇 Z₃ 對稱性 (orbit 結構)?
  2. 12 個維度嘅「物理」係咪有 Z₃ 分組?
  3. 用原生 12D 構建 (derive_dijk_12d_native) 對比
  4. Z₃ 相位結構 (ω 本徵值)
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "src"))

phi = (1 + math.sqrt(5)) / 2
omega = np.exp(2j * np.pi / 3)

print("=" * 70)
print("O53: 12 維 d_tensor Z₃ 結構驗證")
print("=" * 70)

d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
print(f"d_tensor_final shape: {d12.shape}")

# --- [1] Z₃ 對稱性檢查 ---
print("\n[1] Z₃ 對稱性 (索引移位):")
# 如果 d 有 Z₃ 結構, d[i,j,k] 應該喺 i→i+4 移位下近似不變 (12/3=4)
# 或者有特定 orbit 結構
err_shift = 0
n_shift = 0
for i in range(12):
    for j in range(12):
        for k in range(12):
            i4, j4, k4 = (i+4) % 12, (j+4) % 12, (k+4) % 12
            err_shift += abs(d12[i,j,k] - d12[i4,j4,k4])
            n_shift += 1
mean_err = err_shift / n_shift
print(f"    4-shift 平均誤差: {mean_err:.4f}")
print(f"    d 嘅整體規模: {np.abs(d12).mean():.4f}")
print(f"    → {'✅ 有 Z₃ 結構 (移位不變)' if mean_err < np.abs(d12).mean() * 0.1 else '❌ 冇明顯 Z₃'}")

# --- [2] 12 維度嘅 Z₃ 分組 ---
print("\n[2] 12 維度 Z₃ orbit 結構:")
# 原生構建用 3 bands × 4 orbits
# 檢查維度 0,4,8 (同一 orbit?) 有冇相似性
for group_name, idxs in [("orbit0 (0,4,8)", [0,4,8]), ("orbit1 (1,5,9)", [1,5,9]),
                          ("orbit2 (2,6,10)", [2,6,10]), ("orbit3 (3,7,11)", [3,7,11])]:
    # 比較 d[i,:,:] 嘅行
    rows = [d12[i].flatten() for i in idxs]
    cors = []
    for a in range(3):
        for b in range(a+1, 3):
            ma = (rows[a] != 0) & (rows[b] != 0)
            if ma.sum() > 3:
                cors.append(np.corrcoef(rows[a][ma], rows[b][ma])[0, 1])
    if cors:
        print(f"    {group_name}: 行 corr mean={np.mean(cors):.4f}")

# --- [3] Z₃ 本徵值 ---
print("\n[3] Z₃ 作用本徵值 (應該有 ω, ω² 結構):")
# 構建 Z₃ 移位矩陣 (4-shift)
S = np.zeros((12, 12), dtype=complex)
for i in range(12):
    S[(i+4) % 12, i] = 1
evals_S = np.linalg.eigvals(S)
print(f"    移位矩陣本徵值: {np.unique(np.round(evals_S, 10))}")
# 對 12×12 Yukawa 做 Z₃ 分析
v = np.array([phi ** (-k/12) for k in range(12)])
Y = np.einsum('ijk,k->ij', d12, v)
Y_sym = (Y + Y.T) / 2
# 檢查 Y 有冇 Z₃ 協變性: S Y S^{-1} ≈ Y?
SY = S @ Y_sym @ S.T.conj()
err_z3 = np.abs(SY - Y_sym).max()
print(f"    S Y S⁻¹ 誤差: {err_z3:.4e}")
print(f"    → {'✅ Z₃ 協變' if err_z3 < 1e-6 else '🟡 唔完全協變'}")

# --- [4] 原生 12D 構建對比 ---
print("\n[4] 原生 12D 構建 (derive_dijk_12d_native):")
from derive_dijk_12d_native import build_native_12d_tensor
d_native, orbits = build_native_12d_tensor()
print(f"    native d shape: {d_native.shape}")
print(f"    orbit modes: {orbits}")
# 對比 native 同 final
corr = np.corrcoef(d_native.flatten(), d12.flatten())[0, 1]
print(f"    native vs final corr: {corr:.4f}")
print(f"    → {'✅ 相關 (同源)' if corr > 0.5 else '❌ 唔相關 (唔同結構)'}")

# --- [5] Z₃ 唔變量檢查 ---
print("\n[5] d_tensor 嘅 Z₃ 唔變量:")
# 如果 d 係 Z₃ 唔變 (invariant), 則 d[i,j,k] 只依賴 orbit 結構
# 檢查: d[i,j,k] = d[i+4,j+4,k+4] 應該精確成立 (如果 invariant)
max_diff = 0
for i in range(12):
    for j in range(12):
        for k in range(12):
            diff = abs(d12[i,j,k] - d12[(i+4)%12,(j+4)%12,(k+4)%12])
            if diff > max_diff:
                max_diff = diff
print(f"    最大 4-shift 差異: {max_diff:.6f}")
print(f"    → {'✅ Z₃ 精確不變' if max_diff < 1e-10 else f'🟡 有偏差 ({max_diff:.4f})'}")

print("\n" + "=" * 70)
print("【結論】")
print("=" * 70)
