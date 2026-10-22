#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 M31 RAR 嚴格檢驗 — 誤差傳播 + 形狀比較
============================================
問題: v3 用 Zhang+2024 best-fit baryon 參數 (M_b, M_d), 冇考慮誤差
      M_b = 10^(10.57±0.17), M_d = 10^(10.86±0.20), q/a/b 都有誤差
      外部 halo 誤差太大 (σ~40) 導致 χ² 細 — 需要形狀檢驗

方法:
1. baryon 參數 Monte Carlo (誤差傳播)
2. 形狀比較: 觀測 V_c 喺 R>25kpc 下跌 (220→170), IDCM RAR 預測?
   → 呢個係關鍵: RAR 喺深修正區嘅形狀 (declining vs flat)
3. 對比: NFW halo 模型 (Zhang+2024) vs IDCM RAR
"""
import numpy as np

G = 4.3009e-6
a0 = 1.1225e-10
kpc_to_m = 3.085677581e19

# Zhang+2024 參數 (含誤差)
M_b = 10**10.57; M_b_lo = 10**(10.57-0.17); M_b_hi = 10**(10.57+0.17)
M_d = 10**10.86; M_d_lo = 10**(10.86-0.20); M_d_hi = 10**(10.86+0.20)
q = 0.84; q_lo = 0.84-0.46; q_hi = 0.84+0.46
a_mn = 5.77; a_lo = 5.77-2.14; a_hi = 5.77+2.14
b_mn = 0.55; b_lo = 0.55-1.83; b_hi = 0.55+1.83

def V_idcm(R, Mb, Md, qq, aa, bb):
    vb2 = G * Mb * R / (R + qq)**2
    s = aa + bb
    vd2 = G * Md * R**2 / (R**2 + s**2)**1.5
    v2 = vb2 + vd2
    gbar = v2 / R * 1e6 / kpc_to_m
    gobs = gbar * (1 + np.sqrt(1 + 4*a0/gbar)) / 2
    return np.sqrt(gobs * R * kpc_to_m) / 1e3

# 觀測
obs = [
    (1.86, 223.8, 10.72), (3.19, 226.79, 7.96), (4.23, 213.74, 8.17),
    (5.32, 212.54, 7.55), (6.27, 221.94, 7.2), (7.2, 223.3, 8.49),
    (8.2, 225.97, 9.28), (9.14, 226.63, 9.07), (9.93, 223.45, 10.29),
    (10.62, 221.25, 10.24), (11.25, 221.17, 11.16), (11.83, 213.58, 9.75),
    (12.48, 215.04, 12.67), (13.37, 215.12, 12.82), (14.29, 217.92, 13.52),
    (15.2, 215.97, 13.09), (16.08, 223.22, 13.07), (17.21, 213.32, 13.44),
    (18.31, 213.85, 15.37), (19.38, 199.73, 15.19),
    (20.41, 220.27, 37.18), (24.12, 219.28, 36.73), (28.63, 222.84, 38.16),
    (34.28, 210.33, 38.76), (39.56, 221.84, 36.68), (46.21, 185.33, 38.68),
    (52.08, 182.05, 38.15), (67.26, 202.02, 40.67), (98.74, 192.59, 42.23),
    (123.56, 168.53, 41.34),
]

print("=" * 72)
print("M31 RAR 嚴格檢驗 — Monte Carlo 誤差傳播")
print("=" * 72)

# MC: 參數擾動 (log-normal / uniform)
rng = np.random.default_rng(42)
N = 2000
Mb_mc = 10**rng.normal(10.57, 0.17, N)
Md_mc = 10**rng.normal(10.86, 0.20, N)
q_mc = rng.uniform(q_lo, q_hi, N)
a_mc = rng.uniform(a_lo, a_hi, N)
b_mc = rng.uniform(b_lo, b_hi, N)

Rs = np.array([o[0] for o in obs])
Vobs = np.array([o[1] for o in obs])
Ver = np.array([o[2] for o in obs])

# 每個 R 嘅 V_idcm MC 分佈
print("\nR<20 kpc (精確區域) — IDCM 預測 vs 觀測:")
print(f"{'R':>7} {'V_IDCM_med':>11} {'±':>2} {'V_obs':>7} {'Δ/σ':>6}")
chi2_disk = 0
for i, (R, vc, err) in enumerate(obs):
    if R > 20: continue
    Vs = np.array([V_idcm(R, Mb_mc[j], Md_mc[j], q_mc[j], a_mc[j], b_mc[j]) for j in range(N)])
    med = np.median(Vs)
    lo, hi = np.percentile(Vs, [16, 84])
    # 總誤差 (觀測 + 模型)
    sigma = np.sqrt(err**2 + ((hi-lo)/2)**2)
    dsig = (med - vc) / sigma
    chi2_disk += dsig**2
    print(f"{R:7.2f} {med:8.1f}±{(hi-lo)/2:5.1f} {vc:7.1f} {dsig:+6.2f}")

nd = sum(1 for o in obs if o[0] <= 20)
print(f"\nR≤20 kpc: χ² = {chi2_disk:.1f} / {nd} = {chi2_disk/nd:.2f}")

# 形狀檢驗: 外部下跌
print(f"\n形狀檢驗 (R>25 kpc, halo 主導):")
print(f"  觀測: V(25)≈219 → V(125)≈168 (下跌 51 km/s = 23%)")
V25 = np.array([V_idcm(25, Mb_mc[j], Md_mc[j], q_mc[j], a_mc[j], b_mc[j]) for j in range(N)])
V125 = np.array([V_idcm(125, Mb_mc[j], Md_mc[j], q_mc[j], a_mc[j], b_mc[j]) for j in range(N)])
print(f"  IDCM: V(25) = {np.median(V25):.1f} → V(125) = {np.median(V125):.1f} (下跌 {np.median(V25)-np.median(V125):.1f} km/s = {(np.median(V25)-np.median(V125))/np.median(V25)*100:.0f}%)")
print(f"  ⚠️ IDCM 預測下跌 {np.median(V25)-np.median(V125):.0f} km/s vs 觀測 51 km/s")
print(f"  → RAR 嘅深修正區形狀: g_obs ≈ √(a₀·g_bar) → V ∝ R^0.25·(GM)^0.25")
print(f"  → baryon 下跌 (1/R²) 被 √ 修正緩和 → V 緩慢下跌")
print(f"  → 觀測 23% 下跌 vs IDCM {abs(np.median(V25)-np.median(V125))/np.median(V25)*100:.0f}% 下跌 — 需要比較")

# 直接比較斜率
print(f"\n斜率比較 (R=25→125 kpc):")
obs_slope = (168.53 - 219.28) / (123.56 - 24.12) * 100  # km/s per 100 kpc
idcm_slope = (np.median(V125) - np.median(V25)) / (123.56 - 24.12) * 100
print(f"  觀測: {obs_slope:.1f} km/s/100kpc (負 = 下跌)")
print(f"  IDCM: {idcm_slope:.1f} km/s/100kpc")
print(f"  ⚠️ 關鍵區別: IDCM RAR 深修正區形狀 vs 觀測")

# 定量: 觀測外圈 vs IDCM 預測嘅 σ
print(f"\nR>40 kpc (深修正區, 誤差大):")
chi2_halo = 0
n_halo = 0
for R, vc, err in obs:
    if R <= 40: continue
    Vs = np.array([V_idcm(R, Mb_mc[j], Md_mc[j], q_mc[j], a_mc[j], b_mc[j]) for j in range(N)])
    med = np.median(Vs)
    lo, hi = np.percentile(Vs, [16, 84])
    sigma = np.sqrt(err**2 + ((hi-lo)/2)**2)
    dsig = (med - vc) / sigma
    chi2_halo += dsig**2
    n_halo += 1
    print(f"  R={R:7.2f}: V_IDCM={med:6.1f}±{(hi-lo)/2:4.1f} vs obs {vc:6.1f}±{err:4.1f} → Δ={dsig:+.2f}σ")
print(f"χ²(R>40) = {chi2_halo:.1f} / {n_halo} = {chi2_halo/n_halo:.2f}")

print(f"""
總結:
  R≤20 kpc: χ²/dof = {chi2_disk/nd:.2f} (含 baryon 誤差) — 內部區域 IDCM 成立?
  R>40 kpc: χ²/dof = {chi2_halo/n_halo:.2f} (誤差大, 統計力弱)
  形狀: 觀測外圈下跌 23%, IDCM RAR 下跌 {abs(np.median(V25)-np.median(V125))/np.median(V25)*100:.0f}%
  → 關鍵判別: 外圈形狀 (RAR 深修正區 vs NFW halo)
  → 目前誤差太大, 未能定論 — 但 R≤20 kpc 冇明顯違反!
""")
