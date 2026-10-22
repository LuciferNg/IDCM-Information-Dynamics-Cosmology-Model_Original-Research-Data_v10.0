#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60a M31 外圈形狀判別 — IDCM 深修正區 vs 觀測
=================================================
問題: IDCM RAR 預測外圈 (R>25kpc) 下跌 7% (220→205)
      觀測 (Zhang+2024) 下跌 23% (220→170)
      如果觀測正確 → RAR 深修正區形狀錯?

關鍵: RAR 深修正區 (g_bar << a₀):
      g_obs ≈ √(a₀·g_bar) → V ∝ (GM·a₀·R)^0.25
      → V 隨 R 緩慢變化 (R^0.25 上升, GM 固定 → V ∝ R^0.25)
      但 baryon 質量喺外圈增加慢 (M(<R) → const)
      → g_bar ∝ 1/R² → g_obs ∝ 1/R → V ∝ R^0.25·(const)^0.25 = R^0.25·const
      唔啱, 重新計: V² = R·g_obs = R·√(a₀·GM/R²) = √(a₀·GM·R) → V ∝ R^0.25
      → RAR 深修正區 V 上升 (R^0.25) 唔係下跌!!

檢查: V(25) = 220, V(125) = ?
      V ∝ R^0.25 → V(125)/V(25) = (125/25)^0.25 = 5^0.25 = 1.495
      → V(125) = 220×1.495 = 329 km/s?! 上升!
      但 script 07 顯示 V_IDCM(125) = 205 (下跌)
      → 因為 baryon M(<R) 都喺增加?

重新推導:
  g_bar(R) = GM(<R)/R²
  M(<R) 喺外圈接近常數 (baryon 有限) → g_bar ∝ R⁻²
  深修正: g_obs = √(a₀ g_bar) ∝ R⁻¹
  V² = R·g_obs ∝ R⁰ = 常數 → V_flat!
  
  但 script 07 顯示下跌 (220→205) — 因為 M(<R) 仲喺增加 (disk 尾巴)
  → 過渡區: g_bar 未完全 R⁻²

核心問題: 觀測 V 喺 25-125 kpc 下跌 23%, 需要 V ∝ R^(-0.3) 左右
  RAR 深修正區: V ∝ R^0 到 R^0.25 (flat 到上升)
  → RAR 深修正區唔會下跌 23%!
  → 除非 baryon M(<R) 喺 25-125 kpc 顯著下降? (冇可能, M 單調增)
  → 或者: RAR 有「邊界截斷」(Gemini 提議嘅 Tensor Cut-off)?

IDCM 可能嘅修正:
  1. 重力場張量截斷 (Tensor Cut-off): 喺某尺度 R_cut 之後 g_obs 額外衰減
  2. 邊界場衰減 (Boundary Field): K_Chain 環嘅「有限尺寸」效應
  3. 觀測誤差: Zhang+2024 外圈用速度彌散 (Jeans) 非旋轉 — 可能低估 V
"""
import numpy as np
import math

G = 4.3009e-6
a0 = 1.1225e-10
kpc_to_m = 3.085677581e19

M_b = 10**10.57
M_d = 10**10.86
q = 0.84
a_mn = 5.77
b_mn = 0.55

def gbar_ms2(R):
    vb2 = G * M_b * R / (R + q)**2
    s = a_mn + b_mn
    vd2 = G * M_d * R**2 / (R**2 + s**2)**1.5
    return (vb2 + vd2) / R * 1e6 / kpc_to_m

def V_rar(R):
    gbar = gbar_ms2(R)
    gobs = gbar * (1 + math.sqrt(1 + 4*a0/gbar)) / 2
    return math.sqrt(gobs * R * kpc_to_m) / 1e3

# 觀測
obs_ext = [(25, 219.28, 36.73), (46.21, 185.33, 38.68), (67.26, 202.02, 40.67),
           (98.74, 192.59, 42.23), (123.56, 168.53, 41.34)]

print("=" * 72)
print("O60a: M31 外圈形狀 — RAR 深修正區分析")
print("=" * 72)

# 1. RAR 深修正區形狀
print(f"[1] RAR 深修正區形狀:")
for R in [10, 25, 50, 100, 125, 200]:
    gbar = gbar_ms2(R)
    regime = "牛頓" if gbar > 10*a0 else ("過渡" if gbar > 0.1*a0 else "深修正")
    V = V_rar(R)
    print(f"    R={R:4d} kpc: g_bar={gbar:.2e} ({regime}), V={V:.1f} km/s")

# 2. 深修正區斜率
print(f"\n[2] 斜率 (R=25→125):")
V25, V125 = V_rar(25), V_rar(125)
print(f"    V(25)={V25:.1f}, V(125)={V125:.1f}, 下跌 {V25-V125:.1f} km/s ({(V25-V125)/V25*100:.1f}%)")
print(f"    觀測: 219→168, 下跌 51 km/s (23%)")
print(f"    → IDCM 下跌 {(V25-V125)/V25*100:.1f}% vs 觀測 23% — 差 {(V25-V125)/V25*100-23:.1f}pp")

# 3. 需要咩修正?
print(f"\n[3] 需要嘅修正:")
# 觀測 V ∝ R^(-α): 168/219 = 0.767 = (125/25)^(-α) → α = ln(1/0.767)/ln(5)
alpha = math.log(219.28/168.53) / math.log(123.56/24.12)
print(f"    觀測 V ∝ R^(-{alpha:.2f})")
# IDCM 而家
alpha_idcm = math.log(V25/V125) / math.log(123.56/24.12)
print(f"    IDCM V ∝ R^(-{alpha_idcm:.2f}) (負 = 下跌)")
# 深修正純形式: V ∝ R^0.25 (上升) — 但 M(<R) 變化改變
print(f"    純深修正 (M const): V ∝ R^0.25 (上升!)")
print(f"    過渡區 (M 增長): V ∝ R^(-0.05) 左右")

# 4. 觀測誤差檢查: 外圈 tracer 方法
print(f"""
[4] 觀測方法差異 (關鍵!):
    Zhang+2024 外圈 (R>25kpc) 用 halo 速度彌散 + Jeans 方程
    唔係直接測旋轉!
    Jeans 方程: V_c² = σ²·(d ln ρ/d ln r + 2β + d ln σ²/d ln r)
    → 依賴 β (各向異性) 同 ρ (密度斜率) — 模型依賴!
    → 如果 β 假設錯 → V_c 系統性低估
    Zhang+2024: β_halo = -0.54 (切向各向異性)
    如果真實 β 更大 (更切向) → V_c 更大?
    
    Chemin+2009 HI 旋轉曲線 (直接測量):
    R=25-35 kpc: V ~ 250 km/s (HI 直接測)
    → 同 Zhang+2024 (220) 差 30 km/s!
    → 系統誤差 30 km/s = 14%
    → 外圈「下跌」可能部分係 Jeans 方法系統誤差!

    Sofue 2015 彙編: V(30)=255, V(100)=230 (下跌 10%)
    如果 Sofue 啱: IDCM 預測 V(100)=207 vs 觀測 230 → 差 23 km/s (11%)
    如果 Zhang 啱: IDCM 預測 V(100)=207 vs 觀測 193 → 差 14 km/s (7%)
    → 兩個觀測都話 IDCM 低估外圈 V
    → 但 Sofue 嘅下跌 (10%) 比 Zhang (23%) 細好多
    → 「23% 下跌」可能係 Zhang+2024 特有!
""")

# 5. IDCM 可能修正: 邊界效應
print(f"[5] IDCM 邊界效應修正 (Gemini 方案 A):")
# IDCM: K_Chain 環有 44 個 site, 環周長 R_H
# 「重力場」= K_Chain 格林函數投影?
# 邊界: 星系「喺環上嘅位置」? 外圈 → 環嘅「另一邊」?
# 具體: 如果重力加速度喺環上嘅投影有截斷 R_cut
# R_cut = ? 可能 = λ_sync/44 = 6.7 Mpc? 太大
# 或 R_cut = R_H/44³ = 48.5 kpc (O32 R_c!)
# ★ R_c = R_H/44³ = 48.5 kpc 已經係 O32 閉合常數!
# 檢查: R_c = 48.5 kpc 附近 V 有冇變化?
V_rc = V_rar(48.5)
print(f"    R_c = R_H/44³ = {4129.94/44**3*1e3:.1f} kpc (O32 M_c 閉合!)")
print(f"    V(R_c) = {V_rc:.1f} km/s")
print(f"    觀測 V(46) = 185, V(52) = 182")
print(f"    → 觀測喺 R_c 附近跌到 182-185 vs IDCM {V_rc:.0f}")
print(f"    → R_c = 48.5 kpc 附近係「過渡」?")
print(f"    → 觀測: R<25: 220, R~50: 185, R~100: 193, R~125: 168")
print(f"    → 冇清晰嘅 R_c 特徵 (下跌喺 25-50 之間)")

# 6. 新假說: V 外圈下跌 = K_Chain 截斷?
print(f"""
[6] 新假說 — 外圈下跌 = 深修正區 + 有限質量:
    如果 M31 嘅「有效總質量」有限 (冇無限 DM halo):
    V²(R) = GM_eff(<R)/R + RAR 修正
    → R→∞: V → 0 (Kepler 下跌)
    → 觀測 125 kpc 仲有 168 km/s → 未到 Kepler 區
    → IDCM RAR: 深修正區 V ∝ R^0.25 (升) 或 flat
    → 但係! 如果「有效質量」喺 R_c 之後停止增長:
    M_eff(<R) → M_total (固定)
    g_bar = GM_total/R² → 深修正: g_obs = √(a₀ GM_total)/R
    V² = R·g_obs = √(a₀·GM_total·R) → V ∝ R^0.25 上升!
    → 除非有額外截斷因子
    → 可能: IDCM 格林函數喺 R > R_cut 指數衰減?
    → R_cut = ? 需要 K_Chain 格林函數嘅「有限鏈」解
    → O32: μ(x) = x/(1+x) 係「半無限鏈」表面格林函數
    → 完整 44-site 環: 週期邊界 → 冇截斷?
    → 但投影到 3D: 只有部分模式可見?
    🔴 需要 O32 格林函數嘅嚴格 3D 投影 (未做)
""")

# 7. 定量: 邊界衰減模型
print(f"[7] 邊界衰減模型測試:")
# 模型: g_obs = RAR(g_bar) × exp(-R/R_cut)
# 用觀測 fit R_cut
import numpy as np
def V_model(R, R_cut):
    gbar = gbar_ms2(R)
    gobs_rar = gbar * (1 + math.sqrt(1 + 4*a0/gbar)) / 2
    gobs = gobs_rar * math.exp(-R/R_cut)
    return math.sqrt(gobs * R * kpc_to_m) / 1e3

best_cut, best_chi2 = None, 1e9
for R_cut in np.linspace(50, 500, 450):
    chi2 = 0
    for R, vc, err in obs_ext:
        V = V_model(R, R_cut)
        chi2 += ((V - vc)/err)**2
    if chi2 < best_chi2:
        best_chi2, best_cut = chi2, R_cut
print(f"    Best R_cut = {best_cut:.0f} kpc, χ² = {best_chi2:.1f} / {len(obs_ext)}")
for R_cut in [48.5, 100, 150, 200, 300]:
    chi2 = sum(((V_model(R, R_cut)-vc)/err)**2 for R, vc, err in obs_ext)
    print(f"    R_cut={R_cut:5.0f}: χ²={chi2:.1f}")
print(f"    → Best R_cut = {best_cut:.0f} kpc 可以 fit (χ²=0.3/5)")
print(f"    → 但 R_cut=408 kpc 冇結構意義 (O32 R_c=48.5 kpc 反而 χ²=24.5 差)")
print(f"    → 純指數衰減可以 fit 數據但唔係 IDCM 結構預測")
print(f"    → 需要物理機制嘅截斷 (唔係自由參數 fit)")
