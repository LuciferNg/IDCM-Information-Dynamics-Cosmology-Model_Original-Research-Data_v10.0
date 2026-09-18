# O73 — docs/03: 新參數身份確立 + 攻堅報告 (H2-H7)

> **日期**: 2026-08-25
> **狀態**: 🟡 ω_ring 身份確立 + rename 完成; H2-H7 攻堅報告
> **指示**: 「執行O73，但新參數不能再叫哈伯常數」— IDCM 冇膨脹, 舊名係 ΛCDM 包袱

> **★ 後續修正 (2026-09-18 重驗)**: 本文 §2 (H2) 同 §3 (H3) 兩個 🔴 判決**已閉合** —
> ```
> §2 H2「R_world = 4129.94 冇結構分解」→ 由聲學尺鎖定 (O171 docs/29, 09-17):
>    R_world = r_d(obs) × 88×421/(420π) = 4129.99, dev 0.0011%
> §3 H3「CMB 67.36 未有結構解釋」→ 由 CMB 投影閉合 (本 O docs/05, 08-25 同日):
>    ω_cmb = ω_ring(1−π/44) = 67.407, dev 0.070%, z = 0.09σ (Planck)
> §4 H6「CMB 家族一致偏低 5-7% 未有結構」→ 同上 (投影閉合)
> ```
> 原文保留 (記錄當時認知); 最新狀態見 `docs/08` / `docs/14_open_problem_status.md`。

---

## 0. 核心交付: 新參數命名

```
🛑 停用 (ΛCDM 包袱):
   H₀ / 哈伯常數 / Hubble constant     → ω_ring
   R_H (Hubble radius)                 → R_world

✅ 新命名 (IDCM 語境):
   ω_ring = 72.59 (km/s)/Mpc  世界環角頻率 (world ring angular frequency)
   R_world = 4129.94 Mpc      世界環半徑 (world ring radius)
   T_ring = 84.63 Gyr         世界環周期 (world ring period, = 舊 T_sync)
   L_ring = 2πR_world = 25949.2 Mpc  世界環周長 (物理環)
   λ_sync = L_ring/88 = 294.88 Mpc   同步波長 (觀察者維度分割)

| 舊 (ΛCDM 包袱) | 新 (IDCM)          | 數值             |
|:---------------|:-------------------|:-----------------|
| H₀             | ω_ring             | 72.59 (km/s)/Mpc |
| R_H            | R_world            | 4129.94 Mpc      |
| T_sync         | T_ring             | 84.63 Gyr        |
| H₀ = c/R_H    | ω_ring = c/R_world | 恆等             |
```

---

## 1. ★★★ 身份修正: H₀ 係角頻率, 唔係頻率 (script 03, 6/6 PASS)

```
發現 O40 內部矛盾:
  src:      λ_n = R_H/n        → R_H 當「周長」(λ₁ = 4129.94 = 全環)
  O40:      T_sync = 2πR_H/c   → R_H 當「半徑」(周長 = 2πR_H = 25949)

驗證:
  c·T_sync = 25949.2 Mpc = 2πR_H (偏差 < 0.01%) ✅
  → T_sync 對應嘅環周長 = 2πR_world, 唔係 R_world
  → R_world 喺 T_sync 公式入面係「半徑」角色

  若 H₀ 係頻率 f:  T = 1/f = R_H/c = 13.47 Gyr ✗ (唔等於 T_sync)
  若 H₀ 係角頻率 ω: T = 2π/ω = 2πR_H/c = 84.63 Gyr ✅ (= T_sync)
  → H₀ = c/R_H 必須係「角頻率」!

  T_ring × ω_ring = 2π (精確, script 08 高精度確認) ✅
  → IDCM 一直叫「頻率」, 實際係角頻率 (差 2π)
  → 呢個 2π 混亂正正係「哈伯常數」命名遺毒:
    ΛCDM 嘅 H₀ 冇周期運動 → 冇 2π 問題
    IDCM 話「環頻率」→ 要面對角頻率 vs 頻率
```

**命名修正後嘅清晰圖像:**

```
世界環 (半徑 R_world = 4129.94 Mpc):
  ω_ring = c/R_world = 72.59 (km/s)/Mpc = 2.35e-18 rad/s (角頻率)
  T_ring = 2π/ω_ring = 84.63 Gyr (世界環周期, 冇熱寂 O39)
  f_ring = ω_ring/2π = 11.55 /Gyr (真正繞圈頻率)
  λ_sync = L_ring/88 = 294.88 Mpc (世界環 ÷ 觀察者維度 88)
```

---

## 2. H2 深搜: R_world 冇結構分解 (scripts 04, 08)

```
結構數除法 (44, 88, 90, 178, 264, 61.5, 123, 36, 98, 33, 22, 56, 32, 11, 121):
  全部無理數商 — 冇整數/半整數

φ 冪分解 (mpmath 60 位, B ∈ [-40,40]):
  冇整數/半整數 A 令 R_world = A·φ^B

γ 譜空間 (R_world × γ_n):
  n=26: 10586.96 ≈ 10587 (dev 1e-7, 但係統計噪音)
  n=32: 13668.96 ≈ 13669
  n=39: 15998.98 ≈ 15999
  n=41: 16331.00 ≈ 16331
  → 冇規律 (4/44 命中 ~9%, 純隨機) — 唔係結構

R_world/56 = 41×√(2φ) (dev 0.008%) — 有趣但 56 唔係主結構

🔴 H2 判決: R_world = 4129.94 冇結構分解
   → ω_ring 數值仍然係輸入 (身份已修正)
   → 「零參數」claim: 最少 1 個參數 (ω_ring)
```

---

## 3. H3 深攻: CMB 67.36 未有結構解釋 (scripts 05, 09)

```
CMB H₀ 唔係直接量度! 係 θ* (聲學視界角) + 模型反推:
  ΛCDM: θ* = r_s/D_A(z*), fit H₀
  → CMB 量到嘅「67.36」係 ΛCDM 模型嘅投影

IDCM r_s = λ_sync/2 = 147.44 Mpc (dev 0.24% vs Planck 147.09)
  → 聲學視界 = 世界環半波長 (但 λ_sync 有 H₀ 依賴 → re-label)

θ* 預言需要 D_A(z*) = 3.4210×R_world — 冇明顯結構
  3.4210 唔係 φ 冪/π/√ 組合 (script 09 掃描)

67.36/72.59 = 0.9280, δ = 7.20%
  「命中」全部係人為 fit (1/13.88, 6.34, 0.849 唔係結構數)
  → 零參數絕對主義: 唔可以過度 fit!

🔴 H3 判決: CMB 67.36 未有 IDCM 結構解釋
   → 保留為開放問題 (候選: CMB 反推嘅模型依賴)
```

---

## 4. H6: H₀ 張力完整地圖 (script 06)

| 方法 | 值 | σ | 偏差 vs ω_ring | 類型 |
|:-----|:---|:--|:--------------|:-----|
| CMB Planck 2018 | 67.36 | 0.54 | -7.20% | CMB 聲學 |
| CMB ACT DR6 2024 | 68.3 | 0.8 | -5.91% | CMB 聲學 |
| CMB SPT-3G 2024 | 68.8 | 0.8 | -5.22% | CMB 聲學 |
| TRGB (SH0ES 2024) | 69.85 | 0.97 | -3.77% | 恆星投影 |
| JAGB | 72.4 | 2.0 | -0.26% | 恆星投影 |
| GW170817 | 70.0 | 7.0 | -3.57% | 引力波 |
| 強透鏡 TDCOSMO | 67.4 | 3.6 | -7.15% | 透鏡 |
| 強透鏡 H0LiCOW | 73.3 | 1.8 | +0.98% | 透鏡 |
| Cepheid SH0ES | 73.04 | 1.04 | +0.62% | 恆星投影 |
| Miras | 73.3 | 2.6 | +0.98% | 恆星投影 |
| Maser MCP 2024 | 73.9 | 3.0 | +1.80% | 幾何 |
| 星系團 | 74.0 | 2.0 | +1.94% | 星系團 |

```
兩大陣營:
  CMB 家族 (67.4-68.8): 一致低 5-7% ← 「真張力」
  距離階梯 (72.4-74.0): ≈ ω_ring ± 2% ← O11 已解釋 (κφ⁻¹ 家族)
  強透鏡內部分歧 (TDCOSMO 67.4 vs H0LiCOW 73.3) = 模型依賴, 唔係物理

🔴 CMB 一致偏低 5-7% 未有 κφ⁻¹/44 系結構候選
```

---

## 5. src rename 執行記錄

```
src/kchain_wave_params.py:
  R_H = 4129.94 → R_world = 4129.94 (主名) + R_H alias (deprecated)
  H0 = 72.59    → omega_ring = 72.59 (主名) + H0 alias (deprecated)

src/ 其餘 10 個檔案 (各自定義 R_H):
  beat_frequencies, cy3_overlap, dijk_intersection, exhaustive_match,
  geometric_suppression, orbifold_projection, projection_operator,
  residual_analysis, selection_rules, structural_match
  → 全部 R_H → R_world (+alias), H0 → omega_ring (+alias)

驗證: 11/11 modules import OK, 全部 py_compile 通過
   (selection_rules.py indent 修正 1 處)
```

---

## 6. 誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| 新參數命名 (ω_ring/R_world) | 🟢 完成 |
| 身份修正 (角頻率, 2π 確認) | 🟢 script 03/08 6+4 PASS |
| src rename (11 檔案) | 🟢 11/11 import OK |
| R_world 結構分解 (H2) | 🔴 冇 — 係輸入 |
| CMB 67.36 解釋 (H3) | 🔴 未有 — 開放 |
| 張力完整地圖 (H6) | 🟡 12 方法, CMB 家族未解釋 |
| ω_ring 預言 (H7) | 🟡 O11 P1-P3 (ngVLA 2028+) |
| 「零參數」claim | 🔴 最少 1 參數 (ω_ring 數值) |

---

## 7. 關鍵結論

```
1. H₀ 嘅真實身份 = 世界環角頻率 ω_ring (唔係膨脹率!)
   - T_ring × ω_ring = 2π 精確閉合 ✅
   - ΛCDM 將佢誤讀做膨脹率 — IDCM 還原做角頻率

2. 新參數命名: ω_ring / R_world / T_ring (哈伯常數 徹底停用)

3. R_world = 4129.94 冇結構分解 → 係幾何輸入
   - 「零參數」claim: 最少 1 個參數 (ω_ring 數值)

4. CMB 67.36 未有 IDCM 結構解釋 (H3 開放)
   - CMB 家族一致低 5-7% 係「真張力」
   - 候選機制: 聲學視界反推嘅模型依賴
```
