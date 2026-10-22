# O100 — C_ℓ → P_3D(k) 逆投影算符 (Inverse Projection Operator ℳ)

> **創建日期**: 2026-08-28 (O100 攻堅 session)
> **狀態**: 🔴 → 🟡 **攻堅中 (三步執行中)**
> **來源**: O99-v2.0 docs/12 缺口本源 (σ_8 首推缺位)
> **前置**: O83 (C_ℓ correlator 🟢 58/58), O76 (z 紅移 🟢), O86 (SM×IDCM×GR 🟢 34/34), O99 (光本體論 🟡, σ_8 🔴)
> **優先度**: ★★★ (O72 延伸)

## 問題 (The Gap)

IDCM 固有量係 **角度功率譜 C_ℓ** (O83 beat system, 線譜 δ_{ℓ,ℓ_n}),
冇 **3D 物質功率譜 P_3D(k)**。σ_8 需要 ∫ P(k) dk — 未閉合。
真正缺口唔係 sub-grid 算力 (8 h⁻¹Mpc 喺網格外),
而係「ID 成個 framework 冇 P_3D(k) 呢個量」。

→ O100 任務: 建立逆投影算符 **ℳ: C_ℓ → P_3D(k)**,
零自由參數, 三步:

## 攻擊路線 (三步)

| 步 | 名稱 | 內容 | 產出 |
|:--:|:-----|:-----|:-----|
| **1** | 品圓 Harmonic↔ℓ↔k | 建立環世界 ℓ↔k 諧和對應: C_ℓ 峰 ℓ_m ↔ 3D 波數 k_m, 鎖定投影距離 χ* | scripts/01 |
| **2** | O83 母函→逆 Abel→3D | 由母函數振幅 A_m + 絕對歸一化 (D₁=5750μK²) + δT↔δ 轉換 (Poisson+SW 結構化) → P_3D(k) 線譜 | scripts/02 |
| **3** | BOSS DR12 P(k) 正則 | 線譜→平滑 P(k), top-hat σ_8 積分, 對照 BOSS σ8(z_eff)=0.783 / 目標 0.81±0.05 | scripts/03 |

## 可證偽預言

> **若 ℳ 成立, 用 IDCM 首推 P(k) 積分 σ_8 閉合至 0.81±0.05** (對照 BOSS 0.783)。

## 關鍵結構事實 (攻堅前置發現)

1. **R_world = c/H₀ = 4129.64 Mpc** → k_H ≡ H₀/c = 1/R_world (恆等, 非近似!)
2. **λ_sync = 2πR_world/88 = 294.88 Mpc**, BAO = λ_sync/2 = 147.44 Mpc ≈ r_drag (O51 ✅)
3. **C_ℓ 峰公式**: ℓ_m = 44×(M−C(9−m,2)) + frac, m=1..4,6,7; m=5: ℓ₅=1121
4. **母函數**: A_{2k}/A₁ = ((k+1)/(4k−1))² (偶), A₃=4/9, A₅=3/14, A₇=1/7 (奇), 極限 1/16
5. **若 χ* = R_world**: k_m = ℓ_m/R_world → **k/k_H = ℓ_m 完全結構化** (multipole = sub-horizon ratio)
6. **BOSS wiggle 峰**: k_n ≈ n·Δk, Δk = 2π/λ_sync·h = 0.0144 h/Mpc (O51 v2 ✅ 11 峰)

## 檔案結構

```
o100_cl_to_pk/
├── 01_problem_record.md   ← 本文件
├── SESSION_START.md
├── docs/
│   ├── 01_harmonic_correspondence.md   (步1)
│   ├── 02_inverse_abel_operator.md     (步2)
│   └── 03_sigma8_verdict.md            (步3)
├── scripts/
│   ├── 01_harmonic_ell_k.py
│   ├── 02_inverse_abel_pk.py
│   └── 03_sigma8_boss.py
└── data/                   ← script 輸出
```

## 誠實底線

- 若三步結果 σ_8^ID ∈ [0.76, 0.86] → 🟢 閉合
- 若 σ_8^ID 同量級 (0.3–1.5) 但 >2σ 偏差 → 🟡 半閉合, 標記具體缺口
- 若 σ_8^ID 完全脫靶 (<0.1) → 🔴 轉換有錯, 逐項追蹤 (transfer 係數 / SW 歸一化 / 窗函數)