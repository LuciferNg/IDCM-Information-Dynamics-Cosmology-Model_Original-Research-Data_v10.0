#!/usr/bin/env python3
"""
O53: tr(Y) = 66 精確閉合追蹤
==============================
問題: tr(Y) = Σ d_iik·v_k = 66.3554 (誤差 0.54%)
追蹤:
  1. v_k 選擇空間: φ^(-k/12) 係咪唯一令 tr=66 嘅?
  2. 有冇「結構 VEV」令 tr(Y) 精確 = 66?
  3. 0.54% 誤差有冇幾何來源 (例如 d_tensor 嘅 WDVV 殘差)?
  4. 66 = 3×22 嘅 22 有冇獨立閉合?
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: tr(Y) = 66 精確閉合追蹤")
print("=" * 70)

d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
d_iik = np.einsum('iik->i', d12)

# --- [1] 現狀 ---
print("\n[1] 現狀:")
v_phi = np.array([phi ** (-k/12) for k in range(12)])
tr_phi = np.sum(d_iik * v_phi)
print(f"    v_k = φ^(-k/12): tr(Y) = {tr_phi:.6f}, 誤差 = {abs(66-tr_phi)/66*100:.4f}%")

# --- [2] 系統掃描 v_k 參數化 ---
print("\n[2] v_k = φ^(-k/n) 掃描 (n = 步長參數):")
print(f"    {'n':>4} | {'tr(Y)':>12} | {'誤差%':>8} | {'狀態':>6}")
for n in range(6, 25):
    v = np.array([phi ** (-k/n) for k in range(12)])
    tr = np.sum(d_iik * v)
    err = abs(66 - tr) / 66 * 100
    status = "✅" if err < 0.1 else ("🟡" if err < 1 else "")
    print(f"    {n:4d} | {tr:12.4f} | {err:7.3f}% | {status}")

# --- [3] 最佳 v_k (least squares) ---
print("\n[3] 最接近 tr=66 嘅 v_k (fit):")
# min ||Σ d_iik v_k − 66||
# 單一自由度: v_k = φ^(-α k)
best_alpha = None
best_tr = None
best_err = 1e9
for alpha_100 in range(1, 1000):
    alpha = alpha_100 / 100
    v = np.array([phi ** (-alpha * k) for k in range(12)])
    tr = np.sum(d_iik * v)
    err = abs(66 - tr)
    if err < best_err:
        best_err = err
        best_tr = tr
        best_alpha = alpha
print(f"    最佳 α = {best_alpha:.3f} (k 指數步長)")
print(f"    tr(Y) = {best_tr:.6f}, 誤差 = {best_err:.6f} ({best_err/66*100:.4f}%)")
print(f"    α = 1/12 = {1/12:.4f}?  {'✅ 一致' if abs(best_alpha - 1/12) < 0.02 else '❌ 唔同'}")
print(f"    α = 1/12 嘅 tr = {tr_phi:.4f}")

# --- [4] 0.54% 誤差來源: WDVV 殘差? ---
print("\n[4] 誤差來源分析:")
print(f"    d_tensor_final 嘅 WDVV 殘差 (未收斂?):")
# 檢查 d_tensor 有冇 WDVV 殘差
D = d12
t = np.ones(12)
g = np.einsum('ijk,k->ij', D, t)
try:
    g_inv = np.linalg.inv(g)
    lhs = np.einsum('ijp,pq,qkl->ijkl', D, g_inv, D)
    rhs = np.einsum('ilp,pq,qjk->ijkl', D, g_inv, D)
    wdvv_res = np.sum((lhs - rhs)**2)
    print(f"    WDVV 殘差 (t=1): {wdvv_res:.4e}")
    print(f"    → {'✅ 已收斂' if wdvv_res < 1e-6 else '🟡 有殘差'}")
except Exception as e:
    print(f"    g 不可逆: {e}")

# --- [5] 22 = 2×11 閉合 ---
print("\n[5] 22 嘅結構身份:")
print(f"    22 = 2×11 = 2×L₅ (Lucas)")
print(f"    22 = 44/2 = Nd/2")
print(f"    22 = C(7,2)+1? {7*6//2+1}")
print(f"    22 = 12+10?  12 = Z₃, 10 = ?")
print(f"    22 = 33−11?  33 = M (K_Tree), 11 = L₅")

# 66 = 3×22 嘅 3 係咩?
print(f"\n    66 = 3×22:")
print(f"    3 = 代數 (SM 三代)")
print(f"    3 = Z₃ (orbifold)")
print(f"    3 = 12/4?  4 = B")
print(f"    3 = 33/11?  33 = M, 11 = L₅")

# --- [6] 精確閉合嘗試: 66 = tr(Y) 需要咩條件? ---
print("\n[6] tr(Y) = 66 嘅精確條件:")
print(f"    Σ_i d_iik·v_k = 66")
print(f"    d_iik 固定 (WDVV 解), v_k 可調")
print(f"    → 如果 v_k = φ^(-k/12) 係結構 VEV:")
print(f"      需要 Σ d_iik·φ^(-k/12) = 66 精確")
print(f"      而家 = {tr_phi:.4f}, 差 {66-tr_phi:+.4f}")

# 檢查: 66 係咪 d_iik 嘅「結構總和」?
print(f"\n    Σ_i d_iik = {np.sum(d_iik):.4f} (v=1)")
print(f"    Σ_i d_iik·φ^(-i/12) = {np.sum(d_iik * np.array([phi**(-i/12) for i in range(12)])):.4f}")
print(f"    66 係咪 d_iik 嘅某種加權和?")

# 66 同 d_iik 嘅直接關係
print(f"\n    66 / Σ d_iik = {66/np.sum(d_iik):.4f}")
print(f"    Σ d_iik × φ^(-1/4) = {np.sum(d_iik) * phi**(-1/4):.4f}")
print(f"    Σ d_iik × φ^(-1/3) = {np.sum(d_iik) * phi**(-1/3):.4f}")
print(f"    Σ d_iik × φ^(-1/2) = {np.sum(d_iik) * phi**(-1/2):.4f}")

print("\n" + "=" * 70)
print("【結論】")
print("=" * 70)
print(f"""
  tr(Y) = {tr_phi:.4f} (v=φ^(-k/12)), 誤差 0.54%
  {'🟡 0.54% 誤差可能係 WDVV 未完全收斂 / v_k 步長近似' if wdvv_res > 1e-6 else '🟡 誤差來源未明'}
  {'✅ α=1/12 係最接近 66 嘅結構步長' if abs(best_alpha - 1/12) < 0.02 else '❌ α≠1/12'}
""")
print("=" * 70)
