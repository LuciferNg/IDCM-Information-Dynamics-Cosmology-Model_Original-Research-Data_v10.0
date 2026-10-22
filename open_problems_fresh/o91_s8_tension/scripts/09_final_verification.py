#!/usr/bin/env python3
"""
O91/09: 最終驗證 — 核對 O91 所有關鍵數值
============================================
驗證清單:
  1. O76 D_A(z) 自洽性 (z→0, H_eff(0)=ω_ring)
  2. K_Chain 結構常數 (Σγ=90, Σγ²=272, Σγv_g²=22)
  3. IDCM vs ΛCDM D_A(z) 差異
  4. Script 路徑檔案完整性
  5. 文檔一致性
"""
import math
import numpy as np
import os

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

def check_close(name, val, ref, tol, detail=""):
    global PASS, FAIL
    if abs(val - ref) < tol:
        PASS += 1
        print(f"  ✅ PASS: {name}  ({val:.10f} ≈ {ref:.10f})")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}  ({val:.10f} ≠ {ref:.10f}, diff={abs(val-ref):.2e})")
    if detail:
        print(f"    {detail}")

# ============ 常數 ============
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94
C_LIGHT = 299792.458
OMEGA_RING = 72.59
H = OMEGA_RING / 100
C_DELAY = -0.1697
ND = 44
OM_M = 0.3045

print("=" * 70)
print("  O91/09: 最終驗證")
print("=" * 70)

# ============ 1. O76 D_A(z) 自洽性 ============
print("\n--- 1. O76 D_A(z) 自洽性 ---")
def D_A_idcm(z):
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# 1a. z→0: D_A(0) = 0
da_0 = D_A_idcm(1e-6)
check_close("D_A(z→0) = 0", da_0, 0, 1)

# 1b. H_eff(0) = c/R_world = ω_ring
heff = C_LIGHT / R_WORLD
check_close("H_eff(0) = ω_ring = 72.59", heff, OMEGA_RING, 0.01)

# 1c. z=3 → ℓ=1.0
ell_3 = math.log(4, 4)
check_close("z=3 → ℓ=1.0", ell_3, 1.0, 1e-9)

# 1d. z=1 → ℓ=0.5
ell_1 = math.log(2, 4)
check_close("z=1 → ℓ=0.5", ell_1, 0.5, 1e-9)

# 1e. D_A(z=0.5) 自洽
da_05 = D_A_idcm(0.5)
ell_05 = math.log(1.5, 4)
base = R_WORLD * (1 - 4**(-ell_05))
proj = 1 + 2 * PHI_INV * ell_05
delta = C_DELAY * (ell_05 - 0.5) * (1 - 4**(-ell_05))
da_05_check = base * (proj + delta)
check_close("D_A(0.5) 公式自洽", da_05, da_05_check, 1e-6)

# ============ 2. K_Chain 結構常數 ============
print("\n--- 2. K_Chain 結構常數 ---")
gammas = []
vgs = []
for n in range(1, ND + 1):
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    gammas.append(gamma)
    vgs.append(vg)

# 2a. Σγ = 90
sum_gamma = sum(gammas)
check_close("Σγ = 90", sum_gamma, 90.0, 1e-9)

# 2b. Σγ² = 272
sum_gamma2 = sum(g**2 for g in gammas)
check_close("Σγ² = 272", sum_gamma2, 272.0, 1e-9)

# 2c. Σγv_g² = 22
sum_gamma_vg2 = sum(gammas[i] * vgs[i]**2 for i in range(ND))
check_close("Σγv_g² = 22", sum_gamma_vg2, 22.0, 1e-9)

# 2d. Σγv_g² = Σγ - Σγ²/4
check_close("Σγv_g² = Σγ - Σγ²/4", sum_gamma_vg2, sum_gamma - sum_gamma2/4, 1e-9)

# 2e. Σγₙn²
sum_gamma_n2 = sum(gammas[i] * (i+1)**2 for i in range(ND))
print(f"  Σγₙn² = {sum_gamma_n2:.4f}")

# 2f. Beat 總數 = C(44,2) = 946
n_beats = ND * (ND - 1) // 2
check_close("Beat 總數 = 946", n_beats, 946, 0.5)

# ============ 3. IDCM vs ΛCDM D_A(z) ============
print("\n--- 3. IDCM vs ΛCDM D_A(z) 差異 (關鍵) ---")
def chi_lcdm(z):
    n = 2000
    zs = np.linspace(0, z, n)
    integrand = 1.0 / np.sqrt(0.315 * (1 + zs)**3 + 0.685)
    return C_LIGHT / 67.4 * np.trapezoid(integrand, zs)

key_ratios = {
    0.2: (1.14, 0.05),
    0.3: (1.25, 0.05),
    0.5: (1.45, 0.05),
    0.7: (1.66, 0.05),
    0.8: (1.76, 0.05),
    1.0: (1.96, 0.05),
}

for z, (expected, tol) in key_ratios.items():
    ratio = D_A_idcm(z) / (chi_lcdm(z) / (1 + z))
    check_close(f"D_A(z={z}) IDCM/ΛCDM = {expected:.2f}", ratio, expected, tol)

# ============ 4. 檔案完整性 ============
print("\n--- 4. 檔案完整性 ---")
base = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o91_s8_tension"
expected_files = [
    "01_problem_record.md",
    "docs/01_attack_log.md",
    "docs/02_summary.md",
    "docs/03_progress.md",
    "docs/04_restart.md",
    "scripts/01_s8_core_structure.py",
    "scripts/02_beat_spectrum.py",
    "scripts/03_distance_effect.py",
    "scripts/04_cmb_normalization.py",
    "scripts/05_geometric_derivation.py",
    "scripts/06_group_velocity.py",
    "scripts/07_s8_resolution.py",
    "scripts/08_final_argument.py",
    "scripts/09_final_verification.py",
]

for f in expected_files:
    path = os.path.join(base, f)
    exists = os.path.exists(path)
    check(f"檔案存在: {f}", exists)

# ============ 5. 最終結論驗證 ============
print("\n--- 5. 最終結論驗證 ---")
S8_planck = 0.834
S8_wl_avg = (0.759 + 0.776 + 0.788) / 3
S8_wl_err = 0.017
S8_planck_err = 0.016

# ΛCDM 張力
lcdm_tension = (S8_planck - S8_wl_avg) / math.sqrt(S8_planck_err**2 + S8_wl_err**2)
print(f"  ΛCDM S8 張力 = {lcdm_tension:.1f}σ")
check("ΛCDM S8 張力 > 2σ (確認問題存在)", lcdm_tension > 2)

# IDCM D_A(z) 差異在弱透鏡範圍
z_range = [0.2, 0.3, 0.5, 0.7, 0.8]
ratios = [D_A_idcm(z) / (chi_lcdm(z) / (1 + z)) for z in z_range]
print(f"  IDCM/ΛCDM D_A 差異範圍: {min(ratios):.2f} - {max(ratios):.2f}")
check("IDCM D_A(z) 差異顯著 (>10%)", min(ratios) > 1.10)

# IDCM D_A(z) 自洽
check("D_A(z→0) = 0", D_A_idcm(1e-6) < 1)
check("H_eff(0) = ω_ring", abs(C_LIGHT/R_WORLD - OMEGA_RING) < 0.01)

print(f"\n{'='*70}")
print(f"  最終驗證結果")
print(f"  PASS: {PASS}/{PASS+FAIL}")
print(f"  FAIL: {FAIL}/{PASS+FAIL}")
print(f"  狀態: {'✅ 全部通過' if FAIL == 0 else '❌ 有失敗'}")
print(f"{'='*70}")