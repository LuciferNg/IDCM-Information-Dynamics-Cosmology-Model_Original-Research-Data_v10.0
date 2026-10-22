#!/usr/bin/env python3
"""
O91/03: S8 張力 — 重新解釋: 距離-紅移關係效應
================================================
核心洞察: 弱透鏡 S8 測量依賴 angular diameter distance D_A(z)
IDCM (O76) 嘅 D_A(ℓ) = R_world(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ) 同 ΛCDM 唔同
→ 弱透鏡用 ΛCDM 距離去 infer σ₈, 但 IDCM 距離唔同 → inferred σ₈ 會偏

S8 = σ₈ √(Ωₘ/0.3)
弱透鏡測量: C_ℓ^γγ ∝ ∫ dz [W_γ(z)]² P(k=ℓ/χ(z), z)
其中 W_γ(z) = (3H₀²Ωₘ/2c²) × χ(z) × (1 - χ(z)/χ_s) / a(z)

如果 D_A(z) 唔同 → χ(z) 唔同 → lensing kernel 唔同 → inferred σ₈ 唔同

方法: 比較 IDCM 同 ΛCDM 嘅 D_A(z), 計算 lensing kernel 嘅差異,
     然後睇呢個差異能否解釋 S8 張力 (Planck 0.834 vs WL ~0.77)
"""
import math
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

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94       # Mpc
OMEGA_RING = 72.59      # (km/s)/Mpc
C_LIGHT = 299792.458    # km/s
H = OMEGA_RING / 100    # h = 0.7259
C_DELAY = -0.1697       # O76 群延遲修正

# IDCM Ωₘ (BBN 閉合)
OM_M = 0.3045

print("=" * 70)
print("  O91/03: S8 — 距離-紅移關係效應")
print("=" * 70)

# ============ 1. IDCM D_A(z) vs ΛCDM D_A(z) ============
print("\n--- 1. IDCM D_A(z) vs ΛCDM D_A(z) ---")

# IDCM angular diameter distance (O76)
def D_A_idcm(z):
    """IDCM angular diameter distance in Mpc"""
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# ΛCDM comoving distance (flat, Planck 2018)
def chi_lcdm(z, H0=67.4, Om=0.315, Ol=0.685):
    """ΛCDM comoving distance in Mpc"""
    # H(z) = H0 * sqrt(Om*(1+z)^3 + Ol)
    # χ(z) = c * ∫₀ᶻ dz'/H(z')
    n = 1000
    zs = np.linspace(0, z, n)
    dz = z / n
    integrand = 1.0 / np.sqrt(Om * (1 + zs)**3 + Ol)
    chi = C_LIGHT / H0 * np.trapezoid(integrand, zs)
    return chi

# IDCM: D_A = D_app (from O76)
# ΛCDM: D_A = χ/(1+z) (flat)

print(f"  {'z':>5} | {'IDCM D_A':>10} | {'ΛCDM D_A':>10} | {'ratio':>8} | {'IDCM χ':>10} | {'ΛCDM χ':>10} | {'χ ratio':>8}")
for z_vals in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]:
    idcm_da = D_A_idcm(z_vals)
    lcdm_da = chi_lcdm(z_vals) / (1 + z_vals)
    idcm_chi = idcm_da * (1 + z_vals)  # IDCM comoving distance = D_A × (1+z)
    lcdm_chi = chi_lcdm(z_vals)
    ratio = idcm_da / lcdm_da
    chi_ratio = idcm_chi / lcdm_chi
    print(f"  {z_vals:5.1f} | {idcm_da:10.1f} | {lcdm_da:10.1f} | {ratio:8.4f} | {idcm_chi:10.1f} | {lcdm_chi:10.1f} | {chi_ratio:8.4f}")

# ============ 2. Weak Lensing Kernel ============
print("\n\n--- 2. Weak Lensing Kernel 比較 ---")
# Weak lensing convergence power spectrum:
# C_ℓ^κκ = ∫₀^χ_s dχ W_γ(χ)² / χ² × P(ℓ/χ, z(χ))
# W_γ(χ) = (3H₀²Ωₘ/2c²) × χ × (1 - χ/χ_s) / a(z)
# 
# 對於固定 ℓ, 唔同 D_A(z) → 唔同 χ → 唔同 k = ℓ/χ → 唔同 P(k)
# 所以 S8 嘅 inferred value 會 shift

# 簡單近似: S8 ∝ [∫ dz W_γ(z)² D_A(z) ]^{1/2} (忽略 P(k) 形狀)
# 因為 W_γ(z) ∝ χ(z) = D_A(z)(1+z)

def lensing_kernel_weight(z, z_s, H0, Om):
    """Lensing kernel weight (unnormalized)"""
    chi = D_A_idcm(z) * (1 + z)  # IDCM comoving distance
    chi_s = D_A_idcm(z_s) * (1 + z_s)
    if chi >= chi_s:
        return 0
    # W_γ ∝ χ × (1 - χ/χ_s) / a(z)
    a = 1.0 / (1 + z)
    return chi * (1 - chi/chi_s) / a

# Source redshift z_s (typical for KiDS-1000: z_med ≈ 0.7)
z_s = 0.7
zs_lens = np.linspace(0.001, z_s, 100)
dz = z_s / 100

# 計算 IDCM lensing kernel
idcm_kernel = np.array([lensing_kernel_weight(z, z_s, 0, 0) for z in zs_lens])

# ΛCDM lensing kernel
def lcdm_kernel_weight(z, z_s, H0, Om):
    chi = chi_lcdm(z, H0, Om)
    chi_s = chi_lcdm(z_s, H0, Om)
    if chi >= chi_s:
        return 0
    a = 1.0 / (1 + z)
    # W_γ ∝ χ × (1 - χ/χ_s) / a
    return chi * (1 - chi/chi_s) / a

lcdm_kernel = np.array([lcdm_kernel_weight(z, z_s, 67.4, 0.315) for z in zs_lens])

# Normalize
idcm_kernel /= np.trapezoid(idcm_kernel, zs_lens)
lcdm_kernel /= np.trapezoid(lcdm_kernel, zs_lens)

print(f"  Source redshift z_s = {z_s}")
print(f"  {'z':>5} | {'IDCM kernel':>12} | {'ΛCDM kernel':>12} | {'ratio':>8}")
for i in range(0, len(zs_lens), 10):
    z = zs_lens[i]
    print(f"  {z:5.3f} | {idcm_kernel[i]:12.6f} | {lcdm_kernel[i]:12.6f} | {idcm_kernel[i]/lcdm_kernel[i]:8.4f}")

# ============ 3. S8 Shift ============
print(f"\n\n--- 3. S8 Shift 估計 ---")
# 弱透鏡測量 S8 嘅 inferred value 同 lensing kernel 嘅積分成正比
# S8_obs ∝ [∫ W_γ(z)² P(k=ℓ/χ, z) dz]^{1/2}
# 如果 P(k) 相同但距離唔同, S8_obs 會 shift

# 粗略近似: shift factor = sqrt(∫ W_idcm² dz / ∫ W_lcdm² dz)
idcm_w2 = np.trapezoid(idcm_kernel**2, zs_lens)
lcdm_w2 = np.trapezoid(lcdm_kernel**2, zs_lens)
shift = math.sqrt(idcm_w2 / lcdm_w2)
print(f"  ∫ IDCM kernel² dz = {idcm_w2:.6f}")
print(f"  ∫ ΛCDM kernel² dz = {lcdm_w2:.6f}")
print(f"  S8 shift factor = √(IDCM/ΛCDM) = {shift:.4f}")

# 如果 ΛCDM 用 Planck 距離 infer S8 = 0.834
# 用 IDCM 距離 infer: S8_idcm = 0.834 × shift
S8_planck = 0.834
S8_idcm_inferred = S8_planck * shift
print(f"\n  Planck S8 (ΛCDM distance) = {S8_planck:.3f}")
print(f"  IDCM-inferred S8 = {S8_idcm_inferred:.3f}")
print(f"  KiDS-1000 S8 = 0.759 ± 0.017")
print(f"  DES Y3 S8 = 0.776 ± 0.017")
print(f"  ACT DR6 S8 = 0.788 ± 0.010")

# 但 shift 通常好接近 1, 因為 lensing kernel 嘅形狀主要受 source redshift 決定
# 真正嘅效應來自 k = ℓ/χ 嘅 shift, 影響 P(k) 嘅採樣尺度

# ============ 4. k-shift 效應 ============
print(f"\n\n--- 4. k-shift 效應 (P(k) 採樣尺度) ---")
# 弱透鏡: C_ℓ ∝ P(k=ℓ/χ)
# 如果 IDCM 嘅 χ 同 ΛCDM 唔同 → k 唔同 → P(k) 唔同
# 尤其係喺 k ~ 0.5 Mpc⁻¹ (8 h⁻¹ Mpc), 功率譜斜率 ~ -2.5

# 典型弱透鏡 ℓ ~ 1000, z ~ 0.5
# ΛCDM: χ(0.5) ≈ 1300 Mpc, k = 1000/1300 = 0.77 Mpc⁻¹
# IDCM: χ(0.5) = D_A(0.5) × 1.5
ell_typ = 1000
z_typ = 0.5

chi_lcdm_typ = chi_lcdm(z_typ, 67.4, 0.315)
chi_idcm_typ = D_A_idcm(z_typ) * (1 + z_typ)
k_lcdm = ell_typ / chi_lcdm_typ
k_idcm = ell_typ / chi_idcm_typ

print(f"  ℓ = {ell_typ}, z = {z_typ}")
print(f"  ΛCDM χ = {chi_lcdm_typ:.0f} Mpc, k = {k_lcdm:.4f} Mpc⁻¹")
print(f"  IDCM χ = {chi_idcm_typ:.0f} Mpc, k = {k_idcm:.4f} Mpc⁻¹")
print(f"  k ratio = {k_idcm/k_lcdm:.4f}")

# 功率譜斜率 (近似): dlnΔ²/dlnk ≈ -2.5 at k ≈ 0.8 Mpc⁻¹ (ΛCDM)
# 所以 Δ²(k) ∝ k^{-2.5}
# ΔS8/S8 ≈ 0.5 × (-2.5) × Δk/k
slope = -2.5
dk_k = (k_idcm - k_lcdm) / k_lcdm
dS8_S8 = 0.5 * slope * dk_k
print(f"  功率譜斜率 dlnΔ²/dlnk ≈ {slope}")
print(f"  Δk/k = {dk_k:.4f}")
print(f"  ΔS8/S8 ≈ 0.5 × {slope} × {dk_k:.4f} = {dS8_S8:.4f}")

# ============ 5. 多個 ℓ 同 z 嘅累積效應 ============
print(f"\n\n--- 5. Multi-ℓ Multi-z 累積 ---")
# 真正嘅弱透鏡分析用多個 ℓ bin 同 source redshift bin
# 以下係粗略估計

# 典型 S8 測量嘅 ℓ 範圍: 100 < ℓ < 5000
# 典型 z 範圍: 0.1 < z < 1.5
# 計算每個 (ℓ, z) 嘅 k shift

ells = [100, 300, 1000, 2000]
zs = [0.2, 0.5, 0.8, 1.0]

print(f"  {'ℓ':>5} | {'z':>4} | {'k_ΛCDM':>10} | {'k_IDCM':>10} | {'ratio':>8} | {'ΔS8/S8':>8}")
for ell in ells:
    for z in zs:
        chi_l = chi_lcdm(z, 67.4, 0.315)
        chi_i = D_A_idcm(z) * (1 + z)
        k_l = ell / chi_l
        k_i = ell / chi_i
        ratio = k_i / k_l
        dk_k = ratio - 1
        dS8 = 0.5 * slope * dk_k
        print(f"  {ell:5d} | {z:4.1f} | {k_l:10.4f} | {k_i:10.4f} | {ratio:8.4f} | {dS8:8.4f}")

# ============ 6. 總結 ============
print(f"\n{'='*70}")
print(f"  總結: 距離-紅移關係喺 IDCM 同 ΛCDM 嘅差異")
print(f"  會影響弱透鏡 S8 測量嘅 inferred value")
print(f"  但需要完整嘅弱透鏡分析去量化呢個效應")
print(f"  目前只係粗略估計, 唔係嚴格推導")
print(f"{'='*70}")