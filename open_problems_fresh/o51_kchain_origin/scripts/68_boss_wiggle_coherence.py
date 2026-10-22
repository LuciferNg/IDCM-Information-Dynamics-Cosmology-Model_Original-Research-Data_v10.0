#!/usr/bin/env python3
"""
O51/68: BOSS DR12 wiggle P(k) — IDCM 振盪週期相干性檢驗
===============================================================
BOSS DR12 wiggle (P-P_smooth)/P_smooth, 82 點, k=0.0159-0.1451 h/Mpc

IDCM 預言: BAO 振盪週期 Δk = 2π/r_d, r_d = λ_sync/2 = 147.44 Mpc
  Δk = 2π/(147.44×0.6727) = 0.0634 h/Mpc
  k 範圍跨度 0.129 h/Mpc ≈ 2.0 個週期

檢驗:
  1. Fit wiggle(k) = A·sin(2πk/Δk_idcm + φ) — IDCM 固定週期
  2. R² 同相位一致性
  3. 對比: 自由週期 fit (ΛCDM 唔鎖週期)
  4. 相位穩定性: 前後半段相位差
"""
import json, math, sys
import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. 讀數據 ============
k_vals, P_vals, P_smooth, wiggle = [], [], [], []
with open('/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/sync_bump_analysis/boss_dr12_bao_wiggles.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 4:
            k_vals.append(float(parts[0]))
            P_vals.append(float(parts[1]))
            P_smooth.append(float(parts[2]))
            wiggle.append(float(parts[3]))

k = np.array(k_vals)
w = np.array(wiggle)
P = np.array(P_vals)
Ps = np.array(P_smooth)
print("=" * 62)
print("BOSS DR12 wiggle P(k) — IDCM 週期相干性")
print("=" * 62)
print(f"數據: {len(k)} 點, k = {k.min():.4f}-{k.max():.4f} h/Mpc")
print(f"跨度: {k.max()-k.min():.4f} h/Mpc")

# ============ 2. IDCM 預言 ============
R_H = 4129.94
h = 0.6727
rd_idcm = math.pi * R_H / 88  # λ_sync/2
dk_idcm = 2 * math.pi / (rd_idcm * h)
print(f"\nIDCM r_d = λ_sync/2 = {rd_idcm:.3f} Mpc")
print(f"IDCM Δk = 2π/(r_d·h) = {dk_idcm:.5f} h/Mpc")
print(f"k 跨度 / Δk = {(k.max()-k.min())/dk_idcm:.2f} 個週期")

# ============ 3. IDCM 固定週期 fit ============
print("\n--- IDCM 固定週期 fit: w(k) = A·sin(2πk/Δk + φ) ---")
# 線性化: w = A·sin(2πk/Δk)cosφ + A·cos(2πk/Δk)sinφ = c1·sin + c2·cos
sin_term = np.sin(2 * math.pi * k / dk_idcm)
cos_term = np.cos(2 * math.pi * k / dk_idcm)
# 最小二乘: w ≈ c1·sin + c2·cos
A_mat = np.column_stack([sin_term, cos_term])
coeff, res, rank, sv = np.linalg.lstsq(A_mat, w, rcond=None)
c1, c2 = coeff
A_fit = math.hypot(c1, c2)
phi_fit = math.atan2(c2, c1)
w_pred = A_mat @ coeff

ss_res = np.sum((w - w_pred)**2)
ss_tot = np.sum((w - np.mean(w))**2)
r2 = 1 - ss_res / ss_tot
n_dof = len(k) - 2
chi2 = ss_res / np.var(w, ddof=1) * (len(k)-1) / n_dof  # 近似

print(f"A = {A_fit:.4f}, φ = {phi_fit:.3f} rad")
print(f"R² = {r2:.4f}")
print(f"wiggle std = {w.std():.4f}, 殘差 std = {np.std(w - w_pred):.4f}")
print(f"解釋比例 = {1 - np.var(w-w_pred)/np.var(w):.1%}")

# 顯著性: F-test
var_explained = ss_tot - ss_res
var_resid = ss_res / (len(k) - 2)
F = (var_explained / 2) / var_resid
p_F = 1  # 用 scipy 先準確
print(f"F(2,{len(k)-2}) = {F:.2f}")

check("IDCM 固定週期解釋 > 20% 變異", 1 - np.var(w-w_pred)/np.var(w) > 0.2,
      f"解釋 {1 - np.var(w-w_pred)/np.var(w):.1%}")

# ============ 4. 對照: 自由週期 fit ============
print("\n--- 對照: 自由週期 fit (ΛCDM 唔鎖週期) ---")
from scipy.optimize import curve_fit

def sine_model(x, A, dk, phi):
    return A * np.sin(2 * math.pi * x / dk + phi)

try:
    popt, pcov = curve_fit(sine_model, k, w, p0=[0.05, dk_idcm, 0.0],
                           bounds=([0, 0.02, -10], [0.5, 0.15, 10]), maxfev=5000)
    A_free, dk_free, phi_free = popt
    w_free = sine_model(k, A_free, dk_free, phi_free)
    ss_res_free = np.sum((w - w_free)**2)
    r2_free = 1 - ss_res_free / ss_tot
    print(f"A = {A_free:.4f}, Δk = {dk_free:.5f} (IDCM: {dk_idcm:.5f}), φ = {phi_free:.3f}")
    print(f"R² = {r2_free:.4f}")
    dev_dk = abs(dk_free - dk_idcm) / dk_idcm * 100
    print(f"Δk 偏差: {dev_dk:.2f}%")
    check("自由 fit Δk ≈ IDCM Δk (10%)", dev_dk < 10, f"dev={dev_dk:.2f}%")
except Exception as e:
    print(f"自由 fit 失敗: {e}")
    check("自由 fit Δk ≈ IDCM Δk", False, "fit 失敗")

# ============ 5. 相位穩定性 (前後半段) ============
print("\n--- 相位穩定性: 前後半段 ---")
half = len(k) // 2
for label, idx in [("前半", slice(0, half)), ("後半", slice(half, None))]:
    kk = k[idx]
    ww = w[idx]
    A_m = np.column_stack([np.sin(2*math.pi*kk/dk_idcm), np.cos(2*math.pi*kk/dk_idcm)])
    cc, _, _, _ = np.linalg.lstsq(A_m, ww, rcond=None)
    ph = math.atan2(cc[1], cc[0])
    print(f"  {label} ({len(kk)} 點): φ = {ph:+.3f} rad")

# 相干性: 兩個半段相位差
A_m1 = np.column_stack([np.sin(2*math.pi*k[:half]/dk_idcm), np.cos(2*math.pi*k[:half]/dk_idcm)])
A_m2 = np.column_stack([np.sin(2*math.pi*k[half:]/dk_idcm), np.cos(2*math.pi*k[half:]/dk_idcm)])
c1_1, _, _, _ = np.linalg.lstsq(A_m1, w[:half], rcond=None)
c1_2, _, _, _ = np.linalg.lstsq(A_m2, w[half:], rcond=None)
phi1 = math.atan2(c1_1[1], c1_1[0])
phi2 = math.atan2(c1_2[1], c1_2[0])
dphi = abs((phi1 - phi2 + math.pi) % (2*math.pi) - math.pi)
print(f"前後半段相位差: {dphi:.3f} rad")
check("前後半段相位一致 (< 1 rad)", dphi < 1.0, f"Δφ={dphi:.3f}")

# ============ 6. 總結 ============
print(f"\n{'=' * 62}")
print(f"BOSS wiggle 週期檢驗: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'rd_idcm': round(rd_idcm, 4),
    'dk_idcm': round(dk_idcm, 5),
    'r2_fixed': round(float(r2), 4),
    'A_fixed': round(float(A_fit), 4),
    'phi_fixed': round(float(phi_fit), 3),
    'frac_explained': round(float(1 - np.var(w-w_pred)/np.var(w)), 4),
    'pass': PASS,
    'fail': FAIL
}

with open('data/68_boss_wiggle_coherence.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/68_boss_wiggle_coherence.json")