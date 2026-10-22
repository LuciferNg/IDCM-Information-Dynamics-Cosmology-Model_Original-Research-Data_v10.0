#!/usr/bin/env python3
"""
O93/99: Verifier — 獨立驗證所有關鍵數值
========================================
"""
import math
import numpy as np
import sys, json
sys.path.insert(0, '../data')
from cc_hz_data import *

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94
C_LIGHT = 299792.458
OMEGA_RING = 72.59
C_DELAY = -0.1697
OM_M = 0.3045

# ΛCDM
H0_LCDM = 67.4
OM_M_LCDM = 0.315
OM_L_LCDM = 0.685

PASS = 0
FAIL = 0
WARN = 0

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

def warn(name, detail=""):
    global WARN
    WARN += 1
    print(f"  🟡 WARN: {name}")
    if detail:
        print(f"    {detail}")

# ============ IDCM functions ============
def D_A_idcm(z):
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def H_idcm_from_DA(z, eps=1e-6):
    chi = lambda zz: D_A_idcm(zz) * (1 + zz)
    dchi = (chi(z + eps) - chi(z - eps)) / (2 * eps)
    return C_LIGHT / dchi

def H_lcdm(z):
    return H0_LCDM * math.sqrt(OM_M_LCDM * (1+z)**3 + OM_L_LCDM)

def H_power(z, n=0.6):
    return OMEGA_RING * (1 + z)**n

# CC data
z_vals = CC_COMBINED[0]
h_obs = CC_COMBINED[1]
h_err = CC_COMBINED[2]

print("=" * 70)
print("  O93/99: Verifier — 獨立驗證")
print("=" * 70)

# ============ 1. 數據完整性 ============
print("\n--- 1. 數據完整性 ---")
check("CC 數據點數 ≥ 30", len(z_vals) >= 30, f"N={len(z_vals)}")
check("z 覆蓋範圍 0-2", z_vals.min() < 0.1 and z_vals.max() > 1.9,
      f"z=[{z_vals.min():.3f}, {z_vals.max():.3f}]")
check("H(z) 範圍合理", h_obs.min() > 50 and h_obs.max() < 250,
      f"H=[{h_obs.min():.0f}, {h_obs.max():.0f}]")
check("高質量子集 ≥ 20", CC_HIGH_QUALITY.shape[1] >= 20,
      f"N_hq={CC_HIGH_QUALITY.shape[1]}")

# ============ 2. H(0) 一致性 ============
print("\n\n--- 2. H(0) 一致性 ---")
h0_idcm = H_idcm_from_DA(1e-6)
h0_power = H_power(0)
check("H_idcm(0) = ω_ring = 72.59", abs(h0_idcm - OMEGA_RING) < 0.1,
      f"H_idcm(0)={h0_idcm:.4f}")
check("H_power(0) = ω_ring = 72.59", abs(h0_power - OMEGA_RING) < 0.1,
      f"H_power(0)={h0_power:.4f}")

# ============ 3. 路線 A: dD_A/dz ============
print("\n\n--- 3. 路線 A: dD_A/dz 直接比較 ---")
chi2_A = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_id = H_idcm_from_DA(z)
    chi2_A += ((h_ob - h_id) / he)**2
chi2_A_dof = chi2_A / len(z_vals)

check("路線 A 確認失敗 (χ²/dof > 10)", chi2_A_dof > 10,
      f"χ²/dof = {chi2_A_dof:.2f}")
warn("dD_A/dz 路線不適用於 IDCM",
     "D_A(z) 係投影距離, 唔係 FLRW 膨脹積分")

# ============ 4. 路線 B: K_Chain 結構 ============
print("\n\n--- 4. 路線 B: K_Chain 結構 ---")
# 最佳冪律
chi2_power = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_pow = H_power(z, 0.6)
    chi2_power += ((h_ob - h_pow) / he)**2

check("冪律 H(z)=H₀(1+z)^0.6 χ²/dof < 2", chi2_power/len(z_vals) < 2,
      f"χ²/dof = {chi2_power/len(z_vals):.4f}")

# 2/3 冪律
chi2_2_3 = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_pow = H_power(z, 2/3)
    chi2_2_3 += ((h_ob - h_pow) / he)**2

check("H(z)=H₀(1+z)^(2/3) 有理數指數", chi2_2_3/len(z_vals) < 3,
      f"χ²/dof = {chi2_2_3/len(z_vals):.4f}")

# ============ 5. 路線 C: ΛCDM 比較 ============
print("\n\n--- 5. 路線 C: ΛCDM 比較 ---")
chi2_lcdm = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_lc = H_lcdm(z)
    chi2_lcdm += ((h_ob - h_lc) / he)**2

check("ΛCDM χ²/dof < 1", chi2_lcdm/len(z_vals) < 1,
      f"χ²/dof = {chi2_lcdm/len(z_vals):.4f}")

# ============ 6. 結構常數驗證 ============
print("\n\n--- 6. 結構常數驗證 ---")
# K_Chain 結構常數
N = 88
GAMMA = 4 * np.sin(np.pi * np.arange(1, N+1, dtype=float) / N)**2
check("Σγ_world = 90", abs(np.sum(GAMMA[1::2]) - 90) < 0.1,
      f"Σγ_world = {np.sum(GAMMA[1::2]):.4f}")
check("Σγ_obs = 88", abs(np.sum(GAMMA[::2]) - 88) < 0.1,
      f"Σγ_obs = {np.sum(GAMMA[::2]):.4f}")
check("Σγ_total = 178", abs(np.sum(GAMMA) - 178) < 0.1,
      f"Σγ_total = {np.sum(GAMMA):.4f}")

# D_A(z) 結構
check("D_A(0) = 0", abs(D_A_idcm(1e-10)) < 0.01, f"D_A(0)={D_A_idcm(1e-10):.6f}")
check("D_A(∞) → R(1+2φ⁻¹ℓ)", D_A_idcm(10) > 4000, f"D_A(10)={D_A_idcm(10):.0f}")

# ============ 7. 總結 ============
print(f"\n{'='*70}")
print(f"  Verifier 總結")
print(f"  {'='*70}")
print(f"")
print(f"  PASS: {PASS}/{PASS+FAIL}")
print(f"  FAIL: {FAIL}/{PASS+FAIL}")
print(f"  WARN: {WARN}")
print(f"")
print(f"  🟢 路線 A 確認: dD_A/dz 不適用於 IDCM H(z)")
print(f"  🟡 路線 B: 最佳冪律 H(z)=H₀(1+z)^0.6, χ²/dof={chi2_power/len(z_vals):.2f}")
print(f"  🟢 路線 C: ΛCDM 匹配 CC H(z), χ²/dof={chi2_lcdm/len(z_vals):.2f}")
print(f"  🔴 開放: K_Chain 色散關係 → H(z) 結構推導")

# 儲存
results = {
    "verifier": "O93/99",
    "n_total": int(len(z_vals)),
    "n_hq": int(CC_HIGH_QUALITY.shape[1]),
    "chi2_route_A": float(f"{chi2_A_dof:.2f}"),
    "chi2_power_06": float(f"{chi2_power/len(z_vals):.4f}"),
    "chi2_2_3": float(f"{chi2_2_3/len(z_vals):.4f}"),
    "chi2_lcdm": float(f"{chi2_lcdm/len(z_vals):.4f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "warn": int(WARN),
    "status": "🟡"
}
with open("../data/99_verifier_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/99_verifier_results.json")