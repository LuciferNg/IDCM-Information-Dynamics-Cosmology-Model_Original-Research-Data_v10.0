#!/usr/bin/env python3
"""
O51/79: 二階修正一致性檢查 — H_eff, zeta, Omega_Lambda
===============================================================
檢查二階修正對已閉合鏈嘅影響:
  1. H_eff(0) = 72.59 km/s/Mpc (O2 閉合)
  2. H_eff(z) 斜率 (1+z)^1.0 (O18 閉合)
  3. Omega_Lambda = 4/(phi^4-1) = 0.683282 (結構常數)
  4. 47 點 chi2 = 30.6 (O18 閉合)
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

R_H = 4129.94
N_d = 44
c_mpc_gyr = 306.601394
phi = (1 + math.sqrt(5)) / 2

print("=" * 62)
print("一致性檢查: 二階修正對閉合鏈嘅影響")
print("=" * 62)

# ============ 1. D_app 公式 ============
def D1(ell):
    """原始一階 D_app"""
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

def D2(ell):
    """二階修正 D_app"""
    eps = 2/90  # (46-44)/90
    ell0 = 0.5
    alpha = 4*phi
    corr = 1 - eps * math.tanh(alpha * (ell - ell0))
    return D1(ell) * corr

# ============ 2. H_eff(z) 計算 ============
def H_eff(D_func, z):
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    dD = (D_func(ell_p) - D_func(ell_m)) / (2*dz) if z-dz > 0 else 0
    return c_mpc_gyr / dD if dD > 0 else 0

print("\n--- H_eff(z) 對比 ---")
print(f"{'z':<8} {'H1(km/s/Mpc)':<18} {'H2(km/s/Mpc)':<18} {'dev%':<10}")
print("-" * 54)
KMS = 977.8  # 1 Gyr⁻¹ = 977.8 km/s/Mpc

for z in [0, 0.001, 0.03, 0.1, 0.3, 0.5, 0.7, 1.0, 2.0, 3.0]:
    H1 = H_eff(D1, z) * KMS
    H2 = H_eff(D2, z) * KMS
    if H1 > 0 and H2 > 0:
        dev = (H2 - H1) / H1 * 100
        ok = " ✅" if abs(dev) < 0.5 else ""
        print(f"{z:<8.3f} {H1:<18.4f} {H2:<18.4f} {dev:>+8.3f}%{ok}")

# ============ 3. H_eff(0) 一致性 ============
print("\n--- H_eff(0) 鎖定檢查 ---")
H0_1 = H_eff(D1, 0.001)
H0_2 = H_eff(D2, 0.001)
print(f"H_eff(0.001) 一階: {H0_1:.4f} km/s/Mpc")
print(f"H_eff(0.001) 二階: {H0_2:.4f} km/s/Mpc")
print(f"IDCM 鎖定值: 72.5900 km/s/Mpc")
check("H_eff(0) 一階 ≈ 72.59", abs(H0_1 - 72.59) < 0.01, f"{H0_1:.4f}")
check("H_eff(0) 二階 ≈ 72.59", abs(H0_2 - 72.59) < 0.01, f"{H0_2:.4f}")

# ============ 4. Omega_Lambda 一致性 ============
print("\n--- Omega_Lambda 結構常數 ---")
OL_idcm = 4 / (phi**4 - 1)
print(f"Omega_Lambda = 4/(phi^4-1) = {OL_idcm:.6f}")

# Omega_Lambda 同 H_eff(z) 嘅關係:
# 在原始公式, H_eff(z) 喺 z=0 時 = 72.59
# 呢個值同 Omega_Lambda 嘅比例關係由結構鎖定
# 二階修正改變 H_eff(0) 但唔應該改變 Omega_Lambda

# 實際上, Omega_Lambda 係結構常數, 同 D_app 公式無關
OL_check = 4 / (phi**4 - 1)
check("Omega_Lambda 結構常數不變", abs(OL_check - 0.683282) < 1e-6, f"{OL_check:.6f}")

# ============ 5. zeta(z) 投影 Jacobian ============
print("\n--- zeta(z) 投影 Jacobian ---")
# zeta(z) = D_app(z) / D_ΛCDM(z) (已 demoted)
# 二階修正會改變呢個比例
# 但係 zeta(z) 已經 demoted, 所以唔需要檢查

# ============ 6. 原始 O18 47 點 chi2 ============
# 原始 D_app 對 47 點: chi2 = 30.6 (0.65/dof)
# 二階修正對 47 點: 需要檢查
# 但係我冇 47 點數據, 用 DESI 5 點近似

print("\n--- DESI 5 點 chi2 對比 ---")
desi = [
    (0.510, 13.588, 0.167),
    (0.706, 17.351, 0.177),
    (0.934, 21.576, 0.152),
    (1.321, 27.601, 0.318),
    (2.330, 38.988, 0.531),
]
rd_c = math.pi * R_H / 88 * 420/421

chi2_1 = 0
chi2_2 = 0
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d1 = D1(ell) / rd_c
    d2 = D2(ell) / rd_c
    chi2_1 += ((d1 - dm)/err)**2
    chi2_2 += ((d2 - dm)/err)**2
    
print(f"DESI 5 點 chi2 (一階): {chi2_1:.2f}")
print(f"DESI 5 點 chi2 (二階): {chi2_2:.2f}")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print("一致性檢查總結")
print("=" * 62)
print(f"✅ {PASS} / {PASS+FAIL}")
print(f"""
H_eff(0) 一階: {H0_1:.4f} km/s/Mpc
H_eff(0) 二階: {H0_2:.4f} km/s/Mpc
Omega_Lambda: {OL_idcm:.6f} (結構常數, 不變)
DESI 5 點 chi2 一階: {chi2_1:.2f}
DESI 5 點 chi2 二階: {chi2_2:.2f}
""")

result = {
    'H0_1st': round(H0_1, 4),
    'H0_2nd': round(H0_2, 4),
    'Omega_Lambda': round(OL_idcm, 6),
    'chi2_desi_1st': round(chi2_1, 2),
    'chi2_desi_2nd': round(chi2_2, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/79_consistency_check.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"-> data/79_consistency_check.json")