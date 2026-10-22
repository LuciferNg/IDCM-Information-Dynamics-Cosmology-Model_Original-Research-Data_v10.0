#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 本星系群 IDCM 自洽性 — 非膨脹框架下的結構檢驗
====================================================
核心問題: IDCM 冇膨脹冇 Big Bang。本星系群 (Local Group) 係咪同 IDCM 自洽?

檢驗面:
1. 本星系群質量 vs O32 M_d 階梯 (d=3: 4.53e12)
2. M31 RAR (已做: R<20kpc PASS)
3. 本星系群二體運動 (M31-MW) — 非膨脹框架
4. 衛星系平面 (VPOS) — K_Chain 投影預測?
5. 本星系群嘅「合併歷史」 vs IDCM 無年齡

關鍵 insight (2026-08-24):
IDCM 嘅結構 = K_Chain 44-site 1D 環投影到 3D
→ 大尺度: λ_sync 諧波 (BAO, 宇宙網)
→ 星系尺度: a₀ = cH₀/2π (RAR, 旋轉曲線) ✅ O32
→ 本星系群尺度: ???

本星系群作為「結構單元」:
- 半徑 ~1.5 Mpc, 質量 ~2.5e12
- K_Tree: level 1 = 4.03 Mpc (星系群), level 0 = 1033 Mpc (超星系團複合體)
- 本星系群 = level 1 嘅子結構 (0.37 × 4.03 Mpc)
"""
import numpy as np

phi = (1 + 5**0.5) / 2
G = 4.3009e-6
c = 299792.458
R_H = 4129.94
a0 = 1.1225e-10
kpc_to_m = 3.085677581e19

print("=" * 72)
print("O60: 本星系群 IDCM 自洽性 — 非膨脹框架")
print("=" * 72)

# 1. 本星系群質量階梯
M0 = 1.187e18
print(f"""
[1] 本星系群質量階梯:
    IDCM: d=3 → 4.53e12 M☉, d=4 → 7.08e10 M☉
    觀測: 本星系群總 ~2.5e12, M31 ~1.2e12, MW ~1.0e12
    → 本星系群 (2.5e12) = 0.55 × d=3 (4.53e12)
    → M31+MW (2.2e12) = 0.49 × d=3
    → 單一 M31 (1.2e12) = 0.26 × d=3
    → 本星系群作為「雙核」系統, 質量只有 d=3 嘅一半
    → 可能: 本星系群係 d=3 嘅「失敗者」(未完全合併成單一團)?
""")

# 2. 關鍵: M31-MW 二體運動 (Timing argument) 喺非膨脹框架
print(f"[2] M31-MW 二體運動 (Timing argument 非膨脹重詮釋):")
D = 780  # kpc
v_rel = 110  # km/s 靠近
M_tot = 2.2e12  # M☉
# 牛頓二體: v² = GM(2/r - 1/a)
v_esc = np.sqrt(2 * G * M_tot / D)  # km/s (escape velocity at 780 kpc)
print(f"    M31-MW: D = {D} kpc, v_rel = {v_rel} km/s (靠近)")
print(f"    M_tot = {M_tot:.1e} M☉")
print(f"    v_esc(780kpc) = √(2GM/D) = {v_esc:.0f} km/s")
print(f"    v_rel/v_esc = {v_rel/v_esc:.2f}")
print(f"    → v_rel < v_esc: 綁定系統 ✅")
# 軌道週期 (圓軌道近似): T = 2π√(a³/GM)
# GM = 4.3e-6 kpc·(km/s)²/M☉ × M[M☉]; √(kpc³/GM) = √(kpc³/(kpc·km²/s²)) = kpc·s/km
# 1 kpc = 3.0857e16 km → T[s] = 2π√(D³/GM) × 3.0857e16
T_orbit_s = 2 * np.pi * np.sqrt(D**3 / (G * M_tot)) * 3.0857e16
T_orbit_Gyr = T_orbit_s / 3.15576e16
print(f"    軌道週期 T = 2π√(D³/GM) = {T_orbit_Gyr:.1f} Gyr")
print(f"    τ = 13.47 Gyr, T_orbit/τ = {T_orbit_Gyr/13.47:.2f}")
print(f"    T_sync = 84.63 Gyr, T_orbit/T_sync = {T_orbit_Gyr/84.63:.3f}")
print(f"    → M31-MW 軌道週期 43.5 Gyr ≈ 0.51 T_sync")
print(f"    → 冇膨脹: 二體系統自然演化 (非 Hubble 流)")
print(f"    ⚠️ ΛCDM: M31-MW 自 Big Bang 起互相靠近 (無膨脹時 v 較大)")
print(f"    IDCM: 冇起始, 軌道週期 43.5 Gyr 只係週期性運動")

# 3. 零速度面 (zero-velocity surface)
print(f"[3] 零速度面 (IDCM 非膨脹 vs ΛCDM):")
R_zv = 1.05  # Mpc 觀測
# ΛCDM: R_zv = (GM/H0²)^(1/3)
# GM 轉 m³/s²: 4.3e-6 kpc·(km/s)²/M☉ × M × (3.0857e19 m/kpc × 1e6 m²/km²)
M_lg = 2.5e12
GM_m3s2 = G * M_lg * 3.0857e19 * 1e6
H0_s = 72.59 / 3.0857e19
R_zv_m = (GM_m3s2 / H0_s**2)**(1/3)
print(f"    觀測零速度面 R_zv ≈ 1.05 Mpc (Karachentsev 2009)")
print(f"    ΛCDM 預測 R_zv = (GM/H0²)^(1/3) = {R_zv_m/3.0857e22:.2f} Mpc (M=2.5e12)")
print(f"    IDCM: R_H = 4129.94 Mpc = 4.13 Gpc 環周長")
print(f"    本星系群零速度面 1.05 Mpc = R_H/3933 = R_H/(44×89.4)")
print(f"    ⚠️ 冇明顯結構閉合 — 需更多工作")

# 4. 衛星系平面 (VPOS) — K_Chain 投影預測?
print(f"""
[4] 衛星系平面 (VPOS) — IDCM 潛在預測:
    觀測: MW 衛星 11/11 喺同一極化平面 (VPOS)
          M31 衛星都有平面 (~15 個)
          Leo I proper motion (2023) 增強軌道相干性
    ΛCDM: 張力 (仍辯論中, TNG50 提議「早期形成」)
    IDCM: K_Chain 1D 環 → 3D 投影
          → 1D 結構投影會產生「平面」?
          → 44-site 環嘅 44 個模式 → 投影對稱性?
          → A₅ 冷斑節點 (60 節點) 已經有 3D 結構
    ⚠️ 未推導 — 需要知道 1D→3D 投影嘅數學 (O57 部分)
    🔴 開放問題: 衛星系平面係咪 K_Chain 投影嘅自然結果?
""")

# 5. 合併歷史 vs 無年齡
print(f"""
[5] 合併歷史 vs IDCM 無年齡:
    ΛCDM: LKH 12.3 Gyr ago → GSE 10.5 → Sgr 6.0 → now
    IDCM: 冇「ago」— 只有結構座標 ℓ = log₄(1+z)
    LKH z>4 → ℓ > 1.16
    GSE ~z2-3 → ℓ ~ 0.86-1.0
    Sgr ~z0.5 → ℓ ~ 0.29
    → 合併事件嘅「結構深度」: ℓ = 1.16, 0.86-1.0, 0.29
    → 呢啲係 K_Tree 層級 (level 1-2) 嘅結構事件
    → IDCM 框架: 合併 = 質量階梯 d=5 系統 (5e8) 被 d=4 系統 (MW) 吸收
    → 質量階梯預測「邊啲合併會發生」(質量等級), 唔預測「幾時」
    🔴 合併時鐘未推導 — 但可以預測: 合併質量比 = 階梯比 = 64×
    LKH/GSE/Sgr 質量 ~4-5e8 vs MW 當時質量?
    MW 當時 (ℓ=1.16) 質量 ~? (d=4 = 7e10 而家, 早期更細)
    比率 5e8/7e10 = 1/140 (而家) — 早期 MW 更細 → 比率更大
    論文: mass ratio > 0.2-0.3 (LKH 合併時) → MW 當時 ~2e9
    → 2e9 = d≈5.5 (介乎 d=5 1.1e9 同 d=4 7e10)
    → MW 當時 ~2e9 對應 K_Tree 半級
    ⚠️ 有結構意義但未閉合
""")

# 6. 全部整合
print(f"""
[6] 本星系群 IDCM 自洽性總結:

    ✅ M31 內部 RAR (R<20kpc): χ²/dof = 0.19, 零參數
    ✅ 本星系群係綁定系統 (v_rel < v_esc)
    🟡 本星系群質量 2.5e12 = 0.55 × d=3 (4.53e12) — 雙核特殊
    🟡 M31-MW 軌道週期 43.5 Gyr ≈ 0.51 T_sync — 半週期巧合 (待結構意義)
    🔴 零速度面冇結構閉合
    🔴 衛星系平面 (VPOS) 未推導
    🔴 合併時間順序冇機制 (合併時鐘)
    🟡 合併質量階梯一致 (LKH/GSE/Sgr ~5e8 ≈ d=5)

    核心判別 (未來可測):
    1. M31 外圈 (R>40 kpc) 旋轉曲線形狀: RAR 預測 7% 下跌 vs NFW 23%
       → JWST M31 恆星運動學可裁決
    2. 本星系群動力學: 非膨脹框架嘅二體演化 vs ΛCDM
       → GAIA NDR + 精確本動測量
    3. 衛星系平面: K_Chain 投影預測?
       → 需要 O57 (CY₃ 投影生成) 延伸
""")

print("=" * 72)
