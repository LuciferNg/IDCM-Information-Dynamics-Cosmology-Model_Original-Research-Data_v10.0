#!/usr/bin/env python3
"""
O51/64: DESI DR1 完整 χ² 檢驗 — IDCM D_app vs ΛCDM
===============================================================
完整 7 樣本 DESI DR1 BAO + 誤差棒統計檢驗:
  IDCM: D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ), ℓ=log₄(1+z)
  ΛCDM: D_M(z) = c/H0 ∫ dz'/E(z') (rd 用 Planck 147.09)
  
對比項目:
  1. D_M/rd 直接對比 (rd 消掉, 冇 h 依賴)
  2. χ² 統計 (IDCM vs ΛCDM)
  3. 殘差結構分析
"""
import json, math, sys
import numpy as np

# ============ 1. 結構參數 ============
R_H = 4129.94  # Mpc (IDCM 權威)
c = 299792.458  # km/s
H0_idcm = 72.59
phi = (1 + math.sqrt(5)) / 2
lambda_sync = 2 * math.pi * R_H / 88
rd_idcm = lambda_sync / 2
rd_planck = 147.09  # Mpc

print("=" * 66)
print("IDCM vs ΛCDM: DESI DR1 BAO 完整 χ² 檢驗")
print("=" * 66)
print(f"IDCM rd = λ_sync/2 = {rd_idcm:.3f} Mpc")
print(f"ΛCDM rd = {rd_planck:.2f} Mpc (Planck 2018)")

# ============ 2. DESI DR1 完整數據 ============
# Table 1: (sample, z_eff, DM/rd, err, DH/rd, err, DV/rd, err)
desi = [
    ('BGS',    0.295, None, None, None, None, 7.93, 0.15),
    ('LRG1',   0.510, 13.62, 0.25, 20.98, 0.61, None, None),
    ('LRG2',   0.706, 16.85, 0.32, 20.08, 0.60, None, None),
    ('LRG3+ELG', 0.930, 21.71, 0.28, 17.88, 0.35, None, None),
    ('ELG2',   1.317, 27.79, 0.69, 13.82, 0.42, None, None),
    ('QSO',    1.491, None, None, None, None, 26.07, 0.67),
    ('LyA',    2.330, 39.71, 0.94, 8.52, 0.17, None, None),
]

# ============ 3. IDCM 模型 ============
def D_app_idcm(z):
    """IDCM 非膨脹角距離 (PARADIGM BREAK 公式)"""
    ell = math.log(1 + z, 4)  # K_Tree level
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

def DH_idcm(z):
    """IDCM 視線距離元素: D_app/dℓ × dℓ/dz"""
    ell = math.log(1+z, 4)
    dapp = D_app_idcm(z)
    # D_app/dz = (dD_app/dℓ)(dℓ/dz) = [R_H/44 × 44·ln4/4^ℓ × (1+2φ⁻¹ℓ) + ...] × 1/((1+z)ln4)
    term1 = (44/4**ell) * math.log(4) * (1 + 2*phi**(-1)*ell) / 44
    term2 = (44 - 44/4**ell) * 2*phi**(-1) / 44
    dD_dl = R_H * (term1 + term2)
    dD_dz = dD_dl / ((1+z) * math.log(4))
    return dD_dz  # Mpc per dz

def DH_idcm_simple(z):
    """IDCM DH = dD_app/dz (D_H = c/H_eff, 冇 (1+z) 因子!)
    ⚠️ 之前錯加 (1+z) → QSO 爆 -40%"""
    dz = 1e-6
    return (D_app_idcm(z+dz) - D_app_idcm(z-dz)) / (2*dz)

# ============ 4. 對比計算 ============
print("\n" + "=" * 66)
print("D_M/rd 對比 (rd 固定, 冇 h 依賴)")
print("=" * 66)

print(f"{'Sample':<12}{'z':>7}{'DESI D_M/rd':>14}{'IDCM D_M/rd':>14}{'dev%':>8}{'σ':>6}")
chi2_idcm = 0
chi2_lcdm = 0
n_dm = 0
rows = []

for name, z, dm_rd, dm_err, dh_rd, dh_err, dv_rd, dv_err in desi:
    if dm_rd is not None:
        # IDCM: D_M/rd = D_app(z)/rd_idcm
        dm_idcm_ratio = D_app_idcm(z) / rd_idcm
        dev = (dm_rd - dm_idcm_ratio) / dm_rd * 100
        sigma = (dm_rd - dm_idcm_ratio) / dm_err
        chi2_idcm += sigma**2
        n_dm += 1
        rows.append((name, z, dm_rd, dm_idcm_ratio, dev, sigma))
        print(f"{name:<12}{z:>7.3f}{dm_rd:>14.2f}{dm_idcm_ratio:>14.2f}{dev:>7.1f}%{sigma:>6.2f}")

chi2_idcm_dof = chi2_idcm / n_dm
print(f"\nIDCM D_M: χ² = {chi2_idcm:.2f} / {n_dm} dof = {chi2_idcm_dof:.2f}/dof")

# ============ 5. D_V 對比 (BGS + QSO) ============
print("\n" + "=" * 66)
print("D_V/rd 對比")
print("=" * 66)

print(f"{'Sample':<12}{'z':>7}{'DESI D_V/rd':>14}{'IDCM D_V/rd':>14}{'dev%':>8}{'σ':>6}")
for name, z, dm_rd, dm_err, dh_rd, dh_err, dv_rd, dv_err in desi:
    if dv_rd is not None:
        # IDCM D_V = (z·D_M²·D_H)^(1/3)
        dm_idcm = D_app_idcm(z)
        # DH 用數值微分
        dh_idcm = DH_idcm_simple(z)
        dv_idcm = (z * dm_idcm**2 * dh_idcm)**(1/3)
        dv_idcm_ratio = dv_idcm / rd_idcm
        dev = (dv_rd - dv_idcm_ratio) / dv_rd * 100
        sigma = (dv_rd - dv_idcm_ratio) / dv_err
        chi2_idcm += sigma**2
        rows.append((name, z, dv_rd, dv_idcm_ratio, dev, sigma))
        print(f"{name:<12}{z:>7.3f}{dv_rd:>14.2f}{dv_idcm_ratio:>14.2f}{dev:>7.1f}%{sigma:>6.2f}")

total_pts = len(rows)
print(f"\nIDCM 全部: χ² = {chi2_idcm:.2f} / {total_pts} dof = {chi2_idcm/total_pts:.2f}/dof")

# ============ 6. ΛCDM 對比 ============
print("\n" + "=" * 66)
print("ΛCDM 對比 (Planck 2018: H0=67.36, Ωm=0.315)")
print("=" * 66)

H0_lcdm = 67.36
Om_lcdm = 0.315

def E_z(z):
    return math.sqrt(Om_lcdm*(1+z)**3 + (1-Om_lcdm))

def DM_lcdm(z):
    """ΛCDM 角距離 D_M = D_C (flat)"""
    N = 400
    integral = 0.0
    for i in range(N):
        integral += 1/E_z((i+0.5)*z/N)
    return c/H0_lcdm * integral * z/N

def DH_lcdm(z):
    return c/(H0_lcdm * E_z(z))

print(f"{'Sample':<12}{'z':>7}{'DESI D_M/rd':>14}{'ΛCDM D_M/rd':>14}{'dev%':>8}{'σ':>6}")
chi2_lcdm = 0
for name, z, dm_rd, dm_err, dh_rd, dh_err, dv_rd, dv_err in desi:
    if dm_rd is not None:
        dm_lcdm_ratio = DM_lcdm(z) / rd_planck
        dev = (dm_rd - dm_lcdm_ratio) / dm_rd * 100
        sigma = (dm_rd - dm_lcdm_ratio) / dm_err
        chi2_lcdm += sigma**2
        print(f"{name:<12}{z:>7.3f}{dm_rd:>14.2f}{dm_lcdm_ratio:>14.2f}{dev:>7.1f}%{sigma:>6.2f}")

print(f"\nΛCDM D_M: χ² = {chi2_lcdm:.2f} / {n_dm} dof = {chi2_lcdm/n_dm:.2f}/dof")

# ============ 7. 總結 ============
print("\n" + "=" * 66)
print(f"總結: IDCM χ²/dof = {chi2_idcm/total_pts:.2f} vs ΛCDM χ²/dof = {chi2_lcdm/n_dm:.2f}")
print("=" * 66)

result = {
    'rd_idcm': round(rd_idcm, 4),
    'rd_planck': rd_planck,
    'chi2_idcm': round(chi2_idcm, 3),
    'chi2_idcm_dof': round(chi2_idcm/total_pts, 3),
    'chi2_lcdm': round(chi2_lcdm, 3),
    'chi2_lcdm_dof': round(chi2_lcdm/n_dm, 3),
    'n_points': total_pts,
    'rows': [{'sample': r[0], 'z': r[1], 'obs': r[2], 'idcm': round(r[3],3), 'dev_pct': round(r[4],2), 'sigma': round(r[5],3)} for r in rows]
}

with open('data/64_bao_chi2.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/64_bao_chi2.json")