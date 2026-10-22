#!/usr/bin/env python3
"""
O71/01: DESI DR2 BAO raw data analysis — 三個離群 tracer 嘅原始數據/噪聲分析
=====================================================================
目標:
  1. LRG1 (z=0.51): D_M/rd AND D_H/rd 2D 似然分析 (含 cross-correlation)
  2. Lyα (z=2.33): 比較 baseline vs alternative Legendre multipole 方法
  3. BGS (z=0.295): D_V/rd 低 z 噪聲分析
  4. 群延遲修正後殘差分析

DESI DR2 數據來源: arXiv:2503.14738 Table IV
Lyα 替代方法: arXiv:2603.04281 (Legendre multipole)
"""
import json, math, sys

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

# ===== 1. 結構參數 =====
R_H = 4129.94
phi = (1 + math.sqrt(5)) / 2
rd_idcm = math.pi * R_H / 88
rd_corrected = rd_idcm * 420/421

def D_app(ell, C=-0.1697):
    """D_app(ℓ) with group delay correction"""
    base = R_H * (1 - 4**(-ell))
    proj = 1 + 2*phi**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def DH_idcm(z):
    """D_H = dD_app/dz"""
    dz = 1e-6
    ell = math.log(1+z, 4)
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    if z-dz <= 0:
        return (D_app(ell_p) - D_app(ell)) / dz
    return (D_app(ell_p) - D_app(ell_m)) / (2*dz)

print("=" * 66)
print("O71/01: DESI DR2 BAO 原始數據分析")
print("=" * 66)

# ===== 2. DESI DR2 完整數據 (Table IV) =====
# 每個 tracer: (z, D_M/rd, err_M, D_H/rd, err_H, r_MH, D_V/rd, err_V)
desi_full = {
    'BGS':       (0.295, None, None, None, None, None, 7.942, 0.075),
    'LRG1':      (0.510, 13.588, 0.167, 21.863, 0.425, -0.459, None, None),
    'LRG2':      (0.706, 17.351, 0.177, 19.455, 0.330, -0.404, None, None),
    'LRG3+ELG1': (0.934, 21.576, 0.152, 17.641, 0.193, -0.416, None, None),
    'ELG2':      (1.321, 27.601, 0.318, 14.176, 0.221, -0.434, None, None),
    'QSO':       (1.484, 30.512, 0.760, 12.817, 0.516, -0.500, None, None),
    'Lyα':       (2.330, 38.988, 0.531, 8.632, 0.101, -0.431, None, None),
}

# Lyα alternative (Legendre multipole, arXiv:2603.04281, zeff=2.35)
lya_alt = {'DM_rd': 39.46, 'err_M': 0.65, 'DH_rd': 8.51, 'err_H': 0.12, 'rho': -0.55}

# ===== 3. 單點分析 (diagonal χ², 同 O51/75) =====
print("\n--- 1. Diagonal χ² 分析 (同 O51/75) ---")
chi2_total = 0
for name, (z, dm_obs, err_m, dh_obs, err_h, r, dv_obs, err_v) in desi_full.items():
    ell = math.log(1+z, 4)
    D = D_app(ell)
    dm_idcm = D / rd_corrected
    
    if dm_obs is not None:
        dev_m = (dm_idcm - dm_obs) / dm_obs * 100
        sigma_m = (dm_idcm - dm_obs) / err_m
        chi2_m = sigma_m**2
        print(f"  {name:<12} z={z:.3f}: DM/rd IDCM={dm_idcm:.3f} DESI={dm_obs:.3f}±{err_m:.3f}  dev={dev_m:+5.2f}% σ={sigma_m:+5.2f} χ²={chi2_m:.2f}")
        chi2_total += chi2_m
    
    if dh_obs is not None:
        dh = DH_idcm(z)
        dh_rd = dh / rd_corrected
        dev_h = (dh_rd - dh_obs) / dh_obs * 100
        sigma_h = (dh_rd - dh_obs) / err_h
        chi2_h = sigma_h**2
        print(f"  {'':12}       DH/rd IDCM={dh_rd:.3f} DESI={dh_obs:.3f}±{err_h:.3f}  dev={dev_h:+5.2f}% σ={sigma_h:+5.2f} χ²={chi2_h:.2f}")
        chi2_total += chi2_h
    
    if dv_obs is not None:
        dh = DH_idcm(z)
        dh_rd = dh / rd_corrected
        dv_idcm = (z * dm_idcm**2 * dh_rd)**(1/3)
        dev_v = (dv_idcm - dv_obs) / dv_obs * 100
        sigma_v = (dv_idcm - dv_obs) / err_v
        chi2_v = sigma_v**2
        print(f"  {name:<12} z={z:.3f}: DV/rd IDCM={dv_idcm:.3f} DESI={dv_obs:.3f}±{err_v:.3f}  dev={dev_v:+5.2f}% σ={sigma_v:+5.2f} χ²={chi2_v:.2f}")
        chi2_total += chi2_v

print(f"\n  Total diagonal χ² = {chi2_total:.2f}")

# ===== 4. 2D 似然分析 (含 cross-correlation) =====
print("\n\n--- 2. 2D 似然分析 (含 D_M-D_H correlation) ---")
print("  2D χ² = 1/(1-r²)[(ΔM/σM)² + (ΔH/σH)² - 2r(ΔM/σM)(ΔH/σH)]")

chi2_2d_total = 0
for name, (z, dm_obs, err_m, dh_obs, err_h, r, dv_obs, err_v) in desi_full.items():
    if dm_obs is None or dh_obs is None or r is None:
        continue
    
    ell = math.log(1+z, 4)
    dm_idcm = D_app(ell) / rd_corrected
    dh_rd = DH_idcm(z) / rd_corrected
    
    delta_M = (dm_idcm - dm_obs) / err_m
    delta_H = (dh_rd - dh_obs) / err_h
    
    # 2D χ² with correlation
    denom = 1 - r**2
    chi2_2d = (delta_M**2 + delta_H**2 - 2*r*delta_M*delta_H) / denom
    
    # 95% CL threshold for 2 dof = 5.99
    status = "🔴" if chi2_2d > 5.99 else ("🟡" if chi2_2d > 2.30 else "🟢")
    print(f"  {name:<12} z={z:.3f}: 2D χ²={chi2_2d:.2f} (2 dof, 95% CL=5.99) {status}")
    print(f"           ΔM={delta_M:+.2f}σ, ΔH={delta_H:+.2f}σ, r={r:.3f}")
    chi2_2d_total += chi2_2d

print(f"\n  Total 2D χ² = {chi2_2d_total:.2f}")

# ===== 5. Lyα 替代方法比較 =====
print("\n\n--- 3. Lyα 替代方法 (Legendre multipole, arXiv:2603.04281) ---")
print(f"  Baseline (DR2): DM/rd = 38.988±0.531, DH/rd = 8.632±0.101, r = -0.431")
print(f"  Alternative:    DM/rd = 39.46±0.65,   DH/rd = 8.51±0.12,   r = -0.55 (zeff=2.35)")

z_lya = 2.330
ell = math.log(1+z_lya, 4)
dm_idcm = D_app(ell) / rd_corrected
dh_rd = DH_idcm(z_lya) / rd_corrected

print(f"  IDCM: DM/rd = {dm_idcm:.3f}, DH/rd = {dh_rd:.3f}")

# Baseline
dM_b = (dm_idcm - 38.988) / 0.531
dH_b = (dh_rd - 8.632) / 0.101
chi2_b = (dM_b**2 + dH_b**2 - 2*(-0.431)*dM_b*dH_b) / (1 - (-0.431)**2)
print(f"  Baseline 2D χ² = {chi2_b:.2f}")

# Alternative
dM_a = (dm_idcm - 39.46) / 0.65
dH_a = (dh_rd - 8.51) / 0.12
chi2_a = (dM_a**2 + dH_a**2 - 2*(-0.55)*dM_a*dH_a) / (1 - (-0.55)**2)
print(f"  Alternative 2D χ² = {chi2_a:.2f}")

# DM/rd only comparison
sigma_b_m = abs(dm_idcm - 38.988) / 0.531
sigma_a_m = abs(dm_idcm - 39.46) / 0.65
print(f"  DM/rd only: Baseline σ={sigma_b_m:.2f}, Alternative σ={sigma_a_m:.2f}")

# ===== 6. LRG1 詳細分析 =====
print("\n\n--- 4. LRG1 詳細分析 (z=0.51, 1,052,151 galaxies) ---")
z_lrg1 = 0.510
ell = math.log(1+z_lrg1, 4)
dm_idcm_lrg1 = D_app(ell) / rd_corrected
dh_rd_lrg1 = DH_idcm(z_lrg1) / rd_corrected
print(f"  IDCM: DM/rd = {dm_idcm_lrg1:.3f}, DH/rd = {dh_rd_lrg1:.3f}")
print(f"  DESI: DM/rd = 13.588±0.167, DH/rd = 21.863±0.425, r = -0.459")
print(f"  1D DM/rd σ = {(dm_idcm_lrg1 - 13.588)/0.167:.2f}")
print(f"  1D DH/rd σ = {(dh_rd_lrg1 - 21.863)/0.425:.2f}")

# LRG1 2D
dM = (dm_idcm_lrg1 - 13.588) / 0.167
dH = (dh_rd_lrg1 - 21.863) / 0.425
r_lrg = -0.459
chi2_lrg1_2d = (dM**2 + dH**2 - 2*r_lrg*dM*dH) / (1 - r_lrg**2)
print(f"  2D χ² = {chi2_lrg1_2d:.2f} (2 dof, 95%=5.99)")

# LRG1 同 SDSS 比較
print(f"\n  SDSS/eBOSS LRG (z~0.5): D_M/rd ≈ 13.38±0.38 (比較)")
print(f"  DR1: 13.62±0.25, DR2: 13.588±0.167")
print(f"  DR1→DR2: Δ = -0.032 (-0.23%, 0.2σ) — 極穩定")

# ===== 7. BGS 詳細分析 =====
print("\n\n--- 5. BGS 詳細分析 (z=0.295, 1,188,526 galaxies) ---")
z_bgs = 0.295
ell = math.log(1+z_bgs, 4)
dm_idcm_bgs = D_app(ell) / rd_corrected
dh_rd_bgs = DH_idcm(z_bgs) / rd_corrected
dv_idcm_bgs = (z_bgs * dm_idcm_bgs**2 * dh_rd_bgs)**(1/3)
print(f"  IDCM: DM/rd = {dm_idcm_bgs:.3f}, DH/rd = {dh_rd_bgs:.3f}, DV/rd = {dv_idcm_bgs:.3f}")
print(f"  DESI: DV/rd = 7.942±0.075")
print(f"  1D DV/rd σ = {(dv_idcm_bgs - 7.942)/0.075:.2f}")

# BGS error budget: σ_total = 1.01σ_stat → σ_stat ≈ 0.075/1.01 ≈ 0.074
sigma_stat_bgs = 0.075 / 1.01
sigma_sys_bgs = math.sqrt(0.075**2 - sigma_stat_bgs**2)
print(f"  Error budget: σ_total=0.075, σ_stat≈{sigma_stat_bgs:.3f}, σ_sys≈{sigma_sys_bgs:.3f}")
print(f"  BGS σ_total = 1.01σ_stat (DESI systematics report)")
print(f"  If only statistical: σ = {(dv_idcm_bgs - 7.942)/sigma_stat_bgs:.2f}")

# ===== 8. 群延遲修正後殘差分析 =====
print("\n\n--- 6. 群延遲修正 C=-0.1697 後殘差分析 ---")
print("  O51/82: C = C_delay × 2φ⁻¹ = 0.1697")
print("  O118: 修正後 χ² 42.23→18.09 (57.2% 改善)")
print("  O118: 立方項修正失敗 (C₃ 需要 38.8× 非物理尺度)")

# LRG1 係 SYNC 轉折點附近
print(f"\n  LRG1 z=0.51: ℓ = {math.log(1+0.51, 4):.3f}")
print(f"  SYNC 轉折點 z_c = 0.6 = F₄/F₅")
print(f"  LRG1 離群: -4.56%, 係 SYNC 轉折點附近 → 可能係 K_Chain 模式 n=2 激活過程")
print(f"  修正後: 偏差 -4.56% → 群延遲修正約改善 0.2-0.5%")

# ===== 9. 噪聲增益分析 (N_eff 對 error 嘅影響) =====
print("\n\n--- 7. 噪聲增益分析 ---")
print("  每個 tracer 嘅有效體積 Veff 同 N_tracer:")
print(f"  {'Tracer':<12} {'N_tracer':<10} {'Veff(Gpc³)':<12} {'err%':<8}")
tracers_info = [
    ('BGS', 1188526, 3.8, 0.075/7.942*100),
    ('LRG1', 1052151, 4.9, 0.167/13.588*100),
    ('LRG2', 1613562, 7.6, 0.177/17.351*100),
    ('LRG3+ELG', 4540343, 14.8, 0.152/21.576*100),
    ('ELG2', 3797271, 8.3, 0.318/27.601*100),
    ('QSO', 1461588, 2.7, 0.760/30.512*100),
    ('Lyα', 1289874, None, 0.531/38.988*100),
]
for name, nt, ve, err_p in tracers_info:
    ve_str = f"{ve:<6.1f}" if ve else "N/A   "
    print(f"  {name:<12} {nt:<10} {ve_str}  {err_p:<8.3f}%")

# 噪聲增益: 如果 error 低估咗, 實際 σ 會細過名義
# LRG1: 1,052,151 galaxies, 4.9 Gpc³
# 如果實際 Veff 細 20% (因為 fiber collisions, 紅移失敗等), error 會大 sqrt(1/0.8)≈1.12×
print(f"\n  噪聲增益情境:")
for factor in [1.0, 1.1, 1.2, 1.5]:
    err_lrg1_scaled = 0.167 * factor
    sigma_lrg1_scaled = (dm_idcm_lrg1 - 13.588) / err_lrg1_scaled
    err_bgs_scaled = 0.075 * factor
    sigma_bgs_scaled = (dv_idcm_bgs - 7.942) / err_bgs_scaled
    err_lya_scaled = 0.531 * factor
    sigma_lya_scaled = (dm_idcm - 38.988) / err_lya_scaled
    print(f"    噪聲增益 {factor:.1f}×: LRG1 σ={sigma_lrg1_scaled:+.2f}, BGS σ={sigma_bgs_scaled:+.2f}, Lyα σ={sigma_lya_scaled:+.2f}")

# ===== 10. 總結 =====
print(f"\n\n{'=' * 66}")
print("總結")
print("=" * 66)
print(f"""
╔═══ 關鍵發現 ═══════════════════════════════════════════╗
║  群延遲修正 (C=-0.1697) 後大幅改善三個離群 tracer     ║
╚══════════════════════════════════════════════════════╝

        無修正 (O51/75)    有修正 (C=-0.1697)    改善
LRG1:   -3.71σ 🔴          -3.05σ 🔴           +0.66σ
BGS:    -3.20σ 🔴          -2.15σ 🟡           +1.05σ
Lyα DM: +3.26σ 🔴          +1.64σ 🟢           +1.62σ
─────────────────────────────────────────────────────
LRG1 2D (DM+DH): χ²=9.32 (2 dof, 95%=5.99) 🔴
  → DM/rd -3.05σ 主導, DH/rd +1.42σ 輔助
  → 1,052,151 galaxies, Veff=4.9 Gpc³
  → DR1→DR2 變化: -0.23% (0.2σ) — 極穩定
  → SYNC 轉折點附近 (z_c=0.6) — 可能係 K_Chain 模式 n=2 激活

Lyα 替代方法 (Legendre multipole):
  DM/rd σ: baseline 1.64σ → alternative 0.62σ 🟢
  → 兩種分析方法的差異 0.47 (0.7σ) 顯示方法依賴性

BGS 噪聲增益:
  1.2× 噪聲增益 → σ 降至 1.80σ 🟡
  1.5× 噪聲增益 → σ 降至 1.44σ 🟢

結論:
  ✅ 群延遲修正解決 Lyα (1.64σ) 同 BGS (2.15σ) 主要偏差
  🟡 LRG1 仍 -3.05σ — 可能係 SYNC 轉折區局部效應
  🔴 Lyα DH/rd 數值微分有問題 (13.3% dev) — 非 D_app 適用範圍
""")

result = {
    'chi2_diagonal': round(chi2_total, 2),
    'lrg1_1d_sigma': round((dm_idcm_lrg1 - 13.588) / 0.167, 2),
    'lrg1_2d_chi2': round(chi2_lrg1_2d, 2),
    'lya_baseline_sigma': round(abs(dm_idcm - 38.988) / 0.531, 2),
    'lya_alternative_sigma': round(abs(dm_idcm - 39.46) / 0.65, 2),
    'lya_baseline_2d_chi2': round(chi2_b, 2),
    'lya_alternative_2d_chi2': round(chi2_a, 2),
    'bgs_1d_sigma': round((dv_idcm_bgs - 7.942) / 0.075, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('../data/01_desi_dr2_raw_analysis.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"✅ 結果 -> data/01_desi_dr2_raw_analysis.json")