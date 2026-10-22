#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 星系合併 — 結構時鐘假說測試
==================================
Massari+2026 時間線: LKH 12.3 → GSE 10.5 → Sgr 6.0 → now
間隔: 1.8, 4.5, 6.0 Gyr

IDCM 時標工具:
- τ = 13.470 Gyr (渲染深度)
- T_sync = 84.635 Gyr (SYNC 週期)
- 模式頻率: ω_n = 2sin(πn/88), f_n = ω_n/(2π·T_scale)

問題: 合併間隔 1.8/4.5/6.0 Gyr 有冇結構? 邊個 K_Chain 模式提供「合併時鐘」?
"""
import numpy as np
from itertools import combinations

phi = (1 + 5**0.5) / 2
c = 299792.458
R_H = 4129.94
tau = R_H * 3.085677581e19 / c / 3.15576e7 / 1e9   # 13.470 Gyr
T_sync = 84.6349

print("=" * 72)
print("O60: 合併時鐘假說 — K_Chain 模式週期 vs 合併間隔")
print("=" * 72)

# K_Chain 模式週期 (以 τ 為單位尺度)
# ω_n = 2sin(πn/88) (無量綱), 週期 T_n = 2π/ω_n × τ? 
# 標準: T_sync 對應 n=2? 定 n=1?
# O32: ω₁ = (88c/R_H)·sin(π/88) → T₁ = 2π/ω₁
# T_sync = 84.635 Gyr 係 88 步週期 (θ_n = n·2π/88)
# 每步時間 = T_sync/88 = 0.9618 Gyr
step = T_sync / 88
print(f"\nK_Chain 時間步: T_sync/88 = {step:.4f} Gyr")
print(f"τ/step = {tau/step:.3f} (τ ≈ 14 步)")
print(f"τ = 13.470 Gyr ≈ 14.0 步 (14/88 週期)")

# 合併間隔喺步單位
for name, gap in [("LKH→GSE", 1.8), ("GSE→Sgr", 4.5), ("Sgr→now", 6.0)]:
    print(f"  {name}: {gap:.1f} Gyr = {gap/step:.2f} 步")

print(f"""
[1] 間隔 = 整數步?
    1.8/0.9618 = 1.87 步 (≈2 步, 偏差 6.3%)
    4.5/0.9618 = 4.68 步 (≈5 步, 偏差 6.4%)
    6.0/0.9618 = 6.24 步 (≈6 步, 偏差 3.9%)
    → 全部接近整數步! 1.87/4.68/6.24 → 2/5/6 步
    ⚠️ 但偏差 4-6% 大過年齡誤差 (0.26 Gyr = 0.27 步)
    → 唔算閉合 🟡
""")

# 模式週期表: 邊個模式嘅週期 ≈ 合併間隔?
print("[2] K_Chain 模式週期 (週期 = T_sync·2sin(π/88)/(2sin(πn/88))):")
periods = {}
for n in range(1, 45):
    T_n = T_sync * (2*np.sin(np.pi/88)) / (2*np.sin(np.pi*n/88))
    periods[n] = T_n
targets = {"LKH→GSE 1.8": 1.8, "GSE→Sgr 4.5": 4.5, "Sgr→now 6.0": 6.0, "t_iso-τ 1.0": 1.01}
for label, tgt in targets.items():
    best_n = min(periods, key=lambda n: abs(periods[n]-tgt)/tgt)
    print(f"  {label}: 最近模式 n={best_n}, T={periods[best_n]:.3f} Gyr, 偏差 {abs(periods[best_n]-tgt)/tgt*100:.1f}%")

# 反過來: 邊啲模式週期係「乾淨」?
print(f"\n[3] 關鍵模式週期:")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
    print(f"    n={n:2d}: T = {periods[n]:7.3f} Gyr  ({T_sync/periods[n]:5.2f}× 週期/T)")

# 合併時間點 (絕對) vs 模式週期
print(f"\n[4] 合併「發生時間」作為 K_Chain 相位:")
# ΛCDM: 宇宙年齡 13.8 Gyr。IDCM: τ = 13.47 Gyr 觀察窗。
# 合併時間 t_accr (Gyr ago) = 13.8 - (大爆炸後時間) 喺 ΛCDM
# IDCM 重新詮釋: 合併時間 = 相位 φ_i = t_accr/τ (觀察窗分數)
t_events = {"LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48}
print(f"    t/τ (觀察窗分數):")
for k, v in t_events.items():
    print(f"    {k:6s}: {v:.2f}/{tau:.2f} = {v/tau:.4f}  (≈ φ⁻ⁿ?)")
    # 搵 φ⁻ⁿ 近似
    best = min(range(1, 15), key=lambda n: abs(phi**-n - v/tau)/(v/tau))
    print(f"         最近 φ⁻{best} = {phi**-best:.4f} 偏差 {abs(phi**-best-v/tau)/(v/tau)*100:.1f}%")

# 反物質: 間隔 1.8 = L₆/10
print(f"""
[5] 間隔結構 (Lucas/Fibonacci):
    1.8 Gyr: 1.8×10 = 18 = L₆ ✅ (偏差 0%)
    4.5 Gyr: 4.5×2 = 9 = F₆+1? 或 4.5 = 9/2
    6.0 Gyr: 6.0 = 2×3 = 2F₄? 或 6 = L₃+2?
    序列 1.8, 4.5, 6.0: 1.8 = L₆/10, 4.5 = L₅/2.44?, 6.0 = ?
    比率: 4.5/1.8 = 2.5 = 5/2 = F₅/2 (Fibonacci!)
    6.0/4.5 = 4/3 = B/F₄ (K_Tree 分支比!)
    2.5 × 4/3 = 10/3 = 3.33 ≠ 6/1.8
    ⚠️ 3 個數字, 過度擬合風險高 — 需要更多合併事件
""")

# 檢查: LKH 質量 5e8 vs GSE 質量 5e8 — 相同質量, 時間差 1.8
print(f"[6] LKH vs GSE 質量相同 (5e8 M☉) 但時間差 1.8 Gyr:")
print(f"    → 質量階梯唔區分時間, 需要第二個結構變數")
print(f"    → 可能係「軌道能量」EJ (論文用 EJ + Jz + circularity)")
print(f"    → IDCM: EJ = Jacobi 能量 可能對應 K_Chain 模式 index")
print(f"    → 呢個係未來工作 🔴")

# 本星系群質量
print(f"""
[7] 本星系群 (Local Group) 質量階梯 vs O32 M_d:
    O32: M_d = M₀/64^d, M₀ = 1.187e18 M☉
    d=3: 4.53e12 (星系團), d=4: 7.08e10 (銀河系), d=5: 1.11e9 (矮)
    觀測 (McConnachie 2012; Karachentsev 2013):
      M31 總質量 ~1.2e12, MW ~1.0e12 (含 DM 暈)
      LMC ~2e10, SMC ~7e9, Fornax ~2e7, Sculptor ~3e7
      M31+MW+衛星 ~2.3e12 (本星系群總質量 ~2.5e12)
    IDCM 預測:
      本星系群作為 d=3 結構 → 4.53e12?
      觀測 2.5e12 → 比率 0.55 🟡
      但本星系群係「雙核」(M31+MW) 特殊結構
      單一 M31 = 1.2e12 vs d=4 7.08e10 → 比率 17× (唔啱!)
      單一 M31 用 DM 暈 vs O32 d=4 用「總質量」定義?
      ⚠️ 定義唔一致 (baryon vs total) — 需要小心
""")

# M31 旋轉曲線測試 (IDCM RAR 預測)
print(f"[8] M31 旋轉曲線 (IDCM RAR 可測試):")
print(f"    O32 RAR: g_obs = g_bar·(1+√(1+4a₀/g_bar))/2, a₀ = 1.122e-10 m/s²")
print(f"    M31: V_flat ~ 250 km/s, R ~ 30 kpc")
print(f"    g_bar(30kpc) = GM_bar/R², M_bar ~ 1e11 M☉")
M31_Mbar = 1e11  # M☉
R_kpc = 30.0
G = 4.3009e-6  # kpc·km²/s²/M☉
gbar = G * M31_Mbar / R_kpc**2 * 1e3  # m/s²? G 單位: kpc (km/s)²/M☉
# G = 4.3009e-6 kpc·(km/s)²/M☉ → g = GM/R² [km²/s²/kpc] = (km/s)²/kpc
# 1 kpc = 3.0857e16 km → g [m/s²] = GM/R² [km²/s²/kpc] / 3.0857e16 × 1e3
gbar_ms2 = (G * M31_Mbar / R_kpc**2) / 3.0857e16 * 1e3
a0 = 1.1225e-10
gobs = gbar_ms2 * (1 + np.sqrt(1 + 4*a0/gbar_ms2)) / 2
print(f"    g_bar(30kpc) = {gbar_ms2:.3e} m/s²")
print(f"    g_obs = {gobs:.3e} m/s² → V_obs = √(g_obs·R) = {np.sqrt(gobs*R_kpc*3.0857e19)*1e-3:.0f} km/s")
print(f"    vs M31 觀測 V_flat ~ 250-260 km/s")
print(f"    ⚠️ 粗略估計: M31 質量用 1e11 M☉ baryon, 需要完整旋轉曲線")
print(f"    → M31 RAR 測試係可行嘅 IDCM 中小尺度檢驗! 🟢")

print("=" * 72)
