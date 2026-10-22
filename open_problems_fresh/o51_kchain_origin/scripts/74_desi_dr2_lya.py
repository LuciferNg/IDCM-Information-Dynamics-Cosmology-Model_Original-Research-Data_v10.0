#!/usr/bin/env python3
"""
O51/74: DESI DR2 Lyα BAO — IDCM vs ΛCDM 對比
===============================================================
DESI DR2 Lyα forest BAO (arXiv:2607.27410):
  DM/rd = 39.32 ± 0.33 (z=2.33)
  DH/rd = 8.600 ± 0.066 (z=2.33)
  rd = 147.09 Mpc (fiducial)

IDCM:
  D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)
  rd_idcm = λ_sync/2 = 147.439 Mpc
  r_drag_corrected = 147.439 × 420/421 = 147.088 Mpc (vs Planck 147.090, 0.0012%)
"""
import json, math

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

# ============ 1. 結構參數 ============
R_H = 4129.94
phi = (1 + math.sqrt(5)) / 2
L_7, F_7, N_d = 29, 13, 44
rd_idcm = math.pi * R_H / 88
rd_corrected = rd_idcm * 420/421  # 角化修正

print("=" * 62)
print("DESI DR2 Lyα BAO — IDCM 對比")
print("=" * 62)

# ============ 2. IDCM 預言 ============
def D_app_idcm(z):
    ell = math.log(1 + z, 4)
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

z_lya = 2.330
# 用兩種 rd 分別計算
for rd_label, rd_val in [("rd_idcm (無修正)", rd_idcm), ("rd_corrected (421)", rd_corrected)]:
    print(f"\n--- IDCM D_M/rd ({rd_label}) ---")
    D_app = D_app_idcm(z_lya)
    dm_rd = D_app / rd_val
    print(f"z = {z_lya}, D_app = {D_app:.2f} Mpc")
    print(f"rd = {rd_val:.4f} Mpc")
    print(f"DM/rd = {dm_rd:.4f}")
    print(f"DESI DM/rd = 39.32 ± 0.33")
    dev = abs(dm_rd - 39.32) / 39.32 * 100
    sigma = abs(dm_rd - 39.32) / 0.33
    print(f"dev = {dev:.2f}%, σ = {sigma:.2f}")

# ============ 3. D_H 對比 ============
print("\n--- IDCM D_H/rd ---")
# D_H = c/H_eff(z) = dD_app/dz
dz = 1e-6
DH_app = (D_app_idcm(z_lya+dz) - D_app_idcm(z_lya-dz)) / (2*dz)
for rd_label, rd_val in [("rd_idcm", rd_idcm), ("rd_corrected", rd_corrected)]:
    dh_rd = DH_app / rd_val
    print(f"\n{rd_label}: DH/rd = {dh_rd:.4f}")
    print(f"DESI DH/rd = 8.600 ± 0.066")
    dev = abs(dh_rd - 8.600) / 8.600 * 100
    sigma = abs(dh_rd - 8.600) / 0.066
    print(f"dev = {dev:.2f}%, σ = {sigma:.2f}")

# ============ 4. 總結 ============
print(f"\n{'=' * 62}")

# 用 rd_corrected 做最終
D_app = D_app_idcm(z_lya)
dm_rd_c = D_app / rd_corrected
dh_rd_c = DH_app / rd_corrected
check("IDCM DM/rd ≈ DESI (3σ)", abs(dm_rd_c - 39.32) < 3*0.33, f"{dm_rd_c:.4f} vs 39.32±0.33")
check("IDCM DH/rd ≈ DESI (3σ)", abs(dh_rd_c - 8.600) < 3*0.066, f"{dh_rd_c:.4f} vs 8.600±0.066")

result = {
    'z_lya': z_lya,
    'D_app': round(D_app, 2),
    'rd_corrected': round(rd_corrected, 4),
    'dm_rd_idcm': round(D_app / rd_idcm, 4),
    'dm_rd_corrected': round(dm_rd_c, 4),
    'dm_rd_desi': 39.32,
    'dm_rd_err': 0.33,
    'dh_rd_idcm': round(DH_app / rd_idcm, 4),
    'dh_rd_corrected': round(dh_rd_c, 4),
    'dh_rd_desi': 8.600,
    'dh_rd_err': 0.066,
    'pass': PASS,
    'fail': FAIL
}

with open('data/74_desi_dr2_lya.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/74_desi_dr2_lya.json")