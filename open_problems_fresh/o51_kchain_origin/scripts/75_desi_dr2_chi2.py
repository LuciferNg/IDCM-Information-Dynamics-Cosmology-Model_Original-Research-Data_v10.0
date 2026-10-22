#!/usr/bin/env python3
"""
O51/75: DESI DR2 完整 χ² — IDCM D_app vs ΛCDM
===============================================================
DESI DR2 BAO (arXiv:2503.14738):
  7 tracers: BGS, LRG1, LRG2, LRG3+ELG, ELG2, QSO, Lyα
  D_M/rd, D_H/rd, D_V/rd (Table 1)

IDCM: D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)
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
rd_idcm = math.pi * R_H / 88
rd_corrected = rd_idcm * 420/421  # 421 = F₁₄+N_d

print("=" * 62)
print("DESI DR2 BAO — IDCM χ² 完整檢驗")
print("=" * 62)
print(f"rd_idcm = {rd_idcm:.4f} Mpc, rd_corrected = {rd_corrected:.4f} Mpc")

# ============ 2. IDCM 預言 ============
def D_app_idcm(z):
    ell = math.log(1 + z, 4)
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

def DH_idcm(z):
    dz = 1e-6
    return (D_app_idcm(z+dz) - D_app_idcm(z-dz)) / (2*dz)

def DV_idcm(z):
    dm = D_app_idcm(z)
    dh = DH_idcm(z)
    return (z * dm**2 * dh)**(1/3)

# ============ 3. DESI DR2 數據 ============
# D_M/rd 樣本
dm_samples = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]

# D_V/rd 樣本 (BGS 只有 D_V)
dv_samples = [
    ('BGS', 0.295, 7.942, 0.075),
    ('QSO', 1.484, 26.055, 0.398),
]

# 用兩種 rd 分別計算
for rd_label, rd_val in [("rd_idcm (147.44)", rd_idcm), ("rd_corrected (147.09)", rd_corrected)]:
    print(f"\n{'=' * 62}")
    print(f"IDCM with {rd_label}")
    print(f"{'=' * 62}")
    
    print(f"\nD_M/rd:")
    chi2_dm = 0
    for name, z, dm_obs, dm_err in dm_samples:
        dm_idcm = D_app_idcm(z) / rd_val
        sigma = (dm_idcm - dm_obs) / dm_err
        chi2_dm += sigma**2
        dev = (dm_idcm/dm_obs - 1)*100
        print(f"  {name:<12} z={z:.3f}: IDCM={dm_idcm:.3f}, DESI={dm_obs:.3f}±{dm_err:.3f}, dev={dev:+.2f}%, σ={sigma:+.2f}")
    
    print(f"\nD_V/rd:")
    chi2_dv = 0
    for name, z, dv_obs, dv_err in dv_samples:
        dv_idcm = DV_idcm(z) / rd_val
        sigma = (dv_idcm - dv_obs) / dv_err
        chi2_dv += sigma**2
        dev = (dv_idcm/dv_obs - 1)*100
        print(f"  {name:<12} z={z:.3f}: IDCM={dv_idcm:.3f}, DESI={dv_obs:.3f}±{dv_err:.3f}, dev={dev:+.2f}%, σ={sigma:+.2f}")
    
    chi2_total = chi2_dm + chi2_dv
    dof = len(dm_samples) + len(dv_samples)
    print(f"\n  χ²/dm = {chi2_dm:.2f} ({len(dm_samples)} dof), χ²/dv = {chi2_dv:.2f} ({len(dv_samples)} dof)")
    print(f"  χ²/总 = {chi2_total:.2f} ({dof} dof)")
    print(f"  χ²/dof = {chi2_total/dof:.2f}")
    
    if rd_label == "rd_corrected (147.09)":
        check("IDCM DR2 χ²/dof < 3", chi2_total/dof < 3, f"{chi2_total/dof:.2f}")

# ============ 4. DR1 vs DR2 比較 ============
print(f"\n{'=' * 62}")
print("DR1 vs DR2 對比")
print(f"{'=' * 62}")
print(f"{'樣本':<12} {'DR1 D_M':<12} {'DR2 D_M':<12} {'Δ':<8}")
print("-" * 44)
for name, z, dm_dr2, dm_err in dm_samples:
    # DR1 值 (from scripts/64)
    dm_dr1_map = {'LRG1': 13.62, 'LRG2': 16.85, 'LRG3+ELG': 21.71, 'ELG2': 27.79, 'Lyα': 39.71}
    if name in dm_dr1_map:
        dm_dr1 = dm_dr1_map[name]
        diff = (dm_dr2 - dm_dr1) / dm_dr1 * 100
        sig = diff / (dm_err / dm_dr2 * 100) if dm_err > 0 else 0
        print(f"{name:<12} {dm_dr1:<12.3f} {dm_dr2:<12.3f} {diff:+.2f}% ({sig:.1f}σ)")

# ============ 5. 總結 ============
print(f"\n{'=' * 62}")
print(f"DESI DR2 χ² 檢驗: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'rd_corrected': round(rd_corrected, 4),
    'chi2_idcm': round(chi2_total, 2),
    'dof': dof,
    'chi2_per_dof': round(chi2_total/dof, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/75_desi_dr2_chi2.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/75_desi_dr2_chi2.json")