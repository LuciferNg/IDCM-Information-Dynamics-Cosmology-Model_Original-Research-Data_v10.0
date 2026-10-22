#!/usr/bin/env python3
"""
O93/01: 路線 A — dD_A/dz 直接比較 CC H(z)
============================================
IDCM H_eff(z) = c / (d/dz [D_A(z) · (1+z)])

比較 IDCM vs ΛCDM H(z) 同 CC H(z) 數據點。
"""
import math
import numpy as np
import sys
sys.path.insert(0, '../data')
from cc_hz_data import *

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94       # Mpc
C_LIGHT = 299792.458    # km/s
OMEGA_RING = 72.59      # km/s/Mpc
C_DELAY = -0.1697       # O76 群延遲修正

# IDCM Ωₘ (BBN 閉合)
OM_M = 0.3045

# ΛCDM (Planck 2018)
H0_LCDM = 67.4
OM_M_LCDM = 0.315
OM_L_LCDM = 0.685

# SH0ES
H0_SH0ES = 73.04
H0_SH0ES_ERR = 1.04

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

# ============ IDCM D_A(z) ============
def D_A_idcm(z):
    """IDCM angular diameter distance (Mpc), O76"""
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# ============ IDCM H_eff(z) 數值微分 ============
def H_idcm(z, eps=1e-6):
    """
    IDCM effective H(z) = c / (d/dz [D_A(z) · (1+z)])
    數值微分 (central difference)
    """
    chi = lambda zz: D_A_idcm(zz) * (1 + zz)
    dchi_dz = (chi(z + eps) - chi(z - eps)) / (2 * eps)
    return C_LIGHT / dchi_dz

# ============ ΛCDM H(z) ============
def H_lcdm(z):
    """ΛCDM H(z) = H₀√(Ωₘ(1+z)³ + Ω_Λ)"""
    return H0_LCDM * math.sqrt(OM_M_LCDM * (1 + z)**3 + OM_L_LCDM)

# ============ IDCM H(z) 解析近似 (從 D_A 分析) ============
def H_idcm_analytic(z):
    """
    IDCM H(z) 解析近似 — 從 D_A 公式直接推導
    D_A(ℓ) = R(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ), ℓ=log₄(1+z)
    
    H(z) = c / (d/dz [D_A·(1+z)])
    
    解析推導:
    χ = D_A·(1+z) = R(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ)(1+z)
    dχ/dz = (dχ/dℓ)(dℓ/dz)
    dℓ/dz = 1/((1+z)ln4)
    """
    ell = math.log(1 + z, 4)
    
    # 部件
    A = 1 - 4**(-ell)
    B = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    
    # dA/dℓ = ln(4) · 4^{-ℓ}
    dA_dell = math.log(4) * 4**(-ell)
    
    # dB/dℓ = 2φ⁻¹
    dB_dell = 2 * PHI_INV
    
    # dδ/dℓ = C_DELAY[(1-4^{-ℓ}) + (ℓ-0.5)·ln4·4^{-ℓ}]
    ddelta_dell = C_DELAY * ((1 - 4**(-ell)) + (ell - 0.5) * math.log(4) * 4**(-ell))
    
    # χ = R · A · (B + delta) · (1+z)
    chi = R_WORLD * A * (B + delta) * (1 + z)
    
    # dχ/dℓ = R[(dA/dℓ)(B+δ) + A(dB/dℓ + dδ/dℓ)](1+z)
    dchi_dell = R_WORLD * (dA_dell * (B + delta) + A * (dB_dell + ddelta_dell)) * (1 + z)
    
    # dχ/dz = dχ/dℓ · dℓ/dz + χ/(1+z)  (因為 (1+z) 因子)
    dchi_dz = dchi_dell / ((1 + z) * math.log(4)) + chi / (1 + z)
    
    return C_LIGHT / dchi_dz

print("=" * 70)
print("  O93/01: 路線 A — dD_A/dz 直接比較 CC H(z)")
print("=" * 70)

# ============ 1. 低 z 極限: H(0) = ω_ring = c/R_world = 72.59 ============
print("\n--- 1. 低 z 極限: H(0) 一致性 ---")
z0 = 1e-6
h0_idcm = H_idcm(z0)
h0_analytic = H_idcm_analytic(z0)

check("IDCM H(0) = ω_ring = 72.59",
      abs(h0_idcm - OMEGA_RING) < 0.1,
      f"H_idcm(0) = {h0_idcm:.4f}, ω_ring = {OMEGA_RING:.4f}")

check("IDCM 解析 H(0) = ω_ring",
      abs(h0_analytic - OMEGA_RING) < 0.1,
      f"H_analytic(0) = {h0_analytic:.4f}")

check("IDCM H(0) 接近 SH0ES H₀",
      abs(h0_idcm - H0_SH0ES) < 2 * H0_SH0ES_ERR,
      f"H_idcm(0) = {h0_idcm:.2f}, SH0ES = {H0_SH0ES:.2f} ± {H0_SH0ES_ERR:.2f}")

check("ΛCDM H(0) = 67.4",
      abs(H_lcdm(0) - H0_LCDM) < 0.1,
      f"H_lcdm(0) = {H_lcdm(0):.4f}")

# ============ 2. 全範圍比較: IDCM vs ΛCDM vs CC ============
print("\n\n--- 2. CC H(z) 比較: IDCM vs ΛCDM ---")
print(f"  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_IDCM':>8} | {'H_LCDM':>8} | {'O-C_IDCM':>8} | {'O-C_LCDM':>8}")

# 用合併編纂 (去除低質量點)
z_vals = CC_COMBINED[0]
h_obs = CC_COMBINED[1]
h_err = CC_COMBINED[2]

chi2_idcm = 0.0
chi2_lcdm = 0.0
n_pts = 0

for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    
    h_id = H_idcm(z)
    h_lc = H_lcdm(z)
    
    oc_idcm = h_ob - h_id
    oc_lcdm = h_ob - h_lc
    
    chi2_idcm += (oc_idcm / he)**2
    chi2_lcdm += (oc_lcdm / he)**2
    n_pts += 1
    
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_id:8.1f} | {h_lc:8.1f} | {oc_idcm:+8.1f} | {oc_lcdm:+8.1f}")

# ============ 3. χ² 統計 ============
print(f"\n\n--- 3. χ² 統計 (N={n_pts}) ---")
dof_idcm = n_pts - 0  # IDCM: 零參數 (H(z) 從結構推導)
dof_lcdm = n_pts - 0  # ΛCDM: 也係零參數 (Planck 2018 fixed)

print(f"  IDCM: χ² = {chi2_idcm:.2f}, χ²/dof = {chi2_idcm/dof_idcm:.4f}  (0 params)")
print(f"  ΛCDM: χ² = {chi2_lcdm:.2f}, χ²/dof = {chi2_lcdm/dof_lcdm:.4f}  (0 params, Planck)")
print(f"  Δχ² = χ²_lcdm - χ²_idcm = {chi2_lcdm - chi2_idcm:+.2f}")
print(f"  {'✅ IDCM 優於 ΛCDM' if chi2_idcm < chi2_lcdm else '❌ ΛCDM 優於 IDCM'}")

# ============ 4. 紅移分段分析 ============
print(f"\n\n--- 4. 紅移分段 χ² ---")

# 低 z (z < 0.5, SH0ES 區域)
mask_low = z_vals < 0.5
chi2_low_idcm = np.sum(((h_obs[mask_low] - np.array([H_idcm(z) for z in z_vals[mask_low]])) / h_err[mask_low])**2)
chi2_low_lcdm = np.sum(((h_obs[mask_low] - np.array([H_lcdm(z) for z in z_vals[mask_low]])) / h_err[mask_low])**2)
n_low = np.sum(mask_low)

# 中 z (0.5 ≤ z < 1.0, SYNC 過渡)
mask_mid = (z_vals >= 0.5) & (z_vals < 1.0)
chi2_mid_idcm = np.sum(((h_obs[mask_mid] - np.array([H_idcm(z) for z in z_vals[mask_mid]])) / h_err[mask_mid])**2)
chi2_mid_lcdm = np.sum(((h_obs[mask_mid] - np.array([H_lcdm(z) for z in z_vals[mask_mid]])) / h_err[mask_mid])**2)
n_mid = np.sum(mask_mid)

# 高 z (z ≥ 1.0)
mask_high = z_vals >= 1.0
chi2_high_idcm = np.sum(((h_obs[mask_high] - np.array([H_idcm(z) for z in z_vals[mask_high]])) / h_err[mask_high])**2)
chi2_high_lcdm = np.sum(((h_obs[mask_high] - np.array([H_lcdm(z) for z in z_vals[mask_high]])) / h_err[mask_high])**2)
n_high = np.sum(mask_high)

print(f"  {'z 範圍':>12} | {'N':>3} | {'IDCM χ²':>9} | {'ΛCDM χ²':>9} | {'Δχ²':>7} | {'winner':>8}")
print(f"  {'z<0.5':>12} | {n_low:3d} | {chi2_low_idcm:9.2f} | {chi2_low_lcdm:9.2f} | {chi2_low_lcdm - chi2_low_idcm:+7.2f} | {'IDCM' if chi2_low_idcm < chi2_low_lcdm else 'ΛCDM':>8}")
print(f"  {'0.5≤z<1.0':>12} | {n_mid:3d} | {chi2_mid_idcm:9.2f} | {chi2_mid_lcdm:9.2f} | {chi2_mid_lcdm - chi2_mid_idcm:+7.2f} | {'IDCM' if chi2_mid_idcm < chi2_mid_lcdm else 'ΛCDM':>8}")
print(f"  {'z≥1.0':>12} | {n_high:3d} | {chi2_high_idcm:9.2f} | {chi2_high_lcdm:9.2f} | {chi2_high_lcdm - chi2_high_idcm:+7.2f} | {'IDCM' if chi2_high_idcm < chi2_high_lcdm else 'ΛCDM':>8}")

# ============ 5. 高質量子集分析 ============
print(f"\n\n--- 5. 高質量子集 (σ_H < 20) ---")
z_hq = CC_HIGH_QUALITY[0]
h_hq = CC_HIGH_QUALITY[1]
e_hq = CC_HIGH_QUALITY[2]
n_hq = len(z_hq)

chi2_hq_idcm = np.sum(((h_hq - np.array([H_idcm(z) for z in z_hq])) / e_hq)**2)
chi2_hq_lcdm = np.sum(((h_hq - np.array([H_lcdm(z) for z in z_hq])) / e_hq)**2)

print(f"  N = {n_hq}")
print(f"  IDCM: χ² = {chi2_hq_idcm:.2f}, χ²/dof = {chi2_hq_idcm/n_hq:.4f}")
print(f"  ΛCDM: χ² = {chi2_hq_lcdm:.2f}, χ²/dof = {chi2_hq_lcdm/n_hq:.4f}")
print(f"  Δχ² = {chi2_hq_lcdm - chi2_hq_idcm:+.2f}")

# ============ 6. H(z) 曲線形狀比較 ============
print(f"\n\n--- 6. IDCM vs ΛCDM H(z) 形狀比較 ---")
print(f"  {'z':>5} | {'H_IDCM':>8} | {'H_LCDM':>8} | {'ratio':>8} | {'dH/dz_IDCM':>10} | {'dH/dz_LCDM':>10}")

zs_grid = np.linspace(0, 2.0, 21)
for z in zs_grid:
    h_id = H_idcm(z)
    h_lc = H_lcdm(z)
    
    # 數值 dH/dz
    eps = 1e-4
    dh_id = (H_idcm(z + eps) - H_idcm(z - eps)) / (2 * eps)
    dh_lc = (H_lcdm(z + eps) - H_lcdm(z - eps)) / (2 * eps)
    
    print(f"  {z:5.2f} | {h_id:8.1f} | {h_lc:8.1f} | {h_id/h_lc:8.4f} | {dh_id:10.1f} | {dh_lc:10.1f}")

# ============ 7. H(z) 關鍵紅移值 ============
print(f"\n\n--- 7. 關鍵紅移 H(z) 值 ---")
key_zs = [0.0, 0.03, 0.1, 0.2, 0.5, 0.7, 1.0, 1.5, 2.0]
print(f"  {'z':>5} | {'H_IDCM':>8} | {'H_LCDM':>8} | {'ratio':>8} | {'CC obs':>8} | {'CC σ':>6}")

for z in key_zs:
    h_id = H_idcm(z)
    h_lc = H_lcdm(z)
    
    # Find nearest CC data point
    idx = np.argmin(np.abs(z_vals - z))
    z_near = z_vals[idx]
    h_near = h_obs[idx]
    e_near = h_err[idx]
    
    if abs(z_near - z) < 0.05:
        print(f"  {z:5.2f} | {h_id:8.1f} | {h_lc:8.1f} | {h_id/h_lc:8.4f} | {h_near:8.1f} | {e_near:6.1f}")
    else:
        print(f"  {z:5.2f} | {h_id:8.1f} | {h_lc:8.1f} | {h_id/h_lc:8.4f} |  —    |  —   ")

# ============ 8. 總結 ============
print(f"\n{'='*70}")
print(f"  總結: 路線 A — dD_A/dz 直接比較")
print(f"  {'='*70}")
print(f"")
print(f"  全樣本 (N={n_pts}):")
print(f"    IDCM: χ² = {chi2_idcm:.2f}, χ²/dof = {chi2_idcm/n_pts:.4f}")
print(f"    ΛCDM: χ² = {chi2_lcdm:.2f}, χ²/dof = {chi2_lcdm/n_pts:.4f}")
print(f"    Δχ² = {chi2_lcdm - chi2_idcm:+.2f}")
print(f"")
print(f"  高質量 (N={n_hq}):")
print(f"    IDCM: χ² = {chi2_hq_idcm:.2f}, χ²/dof = {chi2_hq_idcm/n_hq:.4f}")
print(f"    ΛCDM: χ² = {chi2_hq_lcdm:.2f}, χ²/dof = {chi2_hq_lcdm/n_hq:.4f}")
print(f"    Δχ² = {chi2_hq_lcdm - chi2_hq_idcm:+.2f}")

# ============ 驗證 ============
print(f"\n\n--- 驗證 ---")
# H(0) = ω_ring
check("H_idcm(0) = c/R_world = 72.59",
      abs(h0_idcm - OMEGA_RING) < 0.1)

# H(z) monotonic (positive)
zs_test = np.linspace(0, 2, 100)
hs_test = np.array([H_idcm(z) for z in zs_test])
check("H(z) 單調增長 (z>0)", np.all(np.diff(hs_test) > 0))

# H(z) 正定
check("H(z) > 0 所有 z", np.all(hs_test > 0))

# 低 z 匹配 SH0ES
check("z=0.03 H ≈ SH0ES",
      abs(H_idcm(0.03) - H0_SH0ES) < 2 * H0_SH0ES_ERR,
      f"H_idcm(0.03) = {H_idcm(0.03):.2f}")

print(f"\n  PASS: {PASS}/{PASS+FAIL}")
print(f"  FAIL: {FAIL}/{PASS+FAIL}")

# Save results
import json
results = {
    "route": "A",
    "n_total": int(n_pts),
    "n_high_quality": int(n_hq),
    "chi2_idcm_total": float(f"{chi2_idcm:.2f}"),
    "chi2_lcdm_total": float(f"{chi2_lcdm:.2f}"),
    "chi2_idcm_highq": float(f"{chi2_hq_idcm:.2f}"),
    "chi2_lcdm_highq": float(f"{chi2_hq_lcdm:.2f}"),
    "delta_chi2": float(f"{chi2_lcdm - chi2_idcm:.2f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟢" if FAIL == 0 else "🟡"
}
with open("../data/01_route_a_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/01_route_a_results.json")