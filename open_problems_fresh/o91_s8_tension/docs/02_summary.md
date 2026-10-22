# O91 — S8 張力: 攻堅總結

> **日期**: 2026-08-26
> **狀態**: 🔴 **未閉合 — 核心問題未解決**
> **嘗試腳本**: scripts/01-04

## 嘗試總結

### 01: K_Tree 投影因子 ❌
σ₈ = 0.086 — 投影因子 φ^(-2·4.27) = 0.016 太細。
問題: 混淆 CMB 溫度歸一化同物質功率譜歸一化。

### 02: Beat 頻譜 ❌
σ₈ = 9.46 (beat 層直接) / 0.085 (K_Tree 投影) — 混亂。
問題: 8 h⁻¹ Mpc 完全在 K_Chain 次格點尺度 (λ_min_beat = 96 Mpc >> 11 Mpc)。

### 03: 距離-紅移效應 🟡
IDCM D_A(z) 同 ΛCDM 差異巨大 (z=0.5: +45%, z=1.0: +96%)。
Lensing kernel shift 1.5%, k-shift 39% (粗略)。
問題: 完整 3×2pt 分析先能量化真正效應。

### 04: CMB 峰歸一化 ❌
σ₈ ≈ 0.0000 — ΔT/T = 8e-8 太細, 乘 growth φ^{5.05} ≈ 11 都唔夠。
問題: Sachs-Wolfe 唔係正確嘅轉換 (CMB 溫度波動 ≠ 物質密度波動)。

## 根本困難

| 問題 | 狀態 |
|:-----|:----:|
| 8 h⁻¹ Mpc 在 K_Chain sub-grid scale | 🔴 |
| K_Tree 每層嘅 power transfer function 未明 | 🔴 |
| CMB 溫度 → 物質功率譜嘅轉換未嚴格推導 | 🔴 |
| K_Tree MERA isometry 條件同 power conservation | 🔴 |
| 需要完整嘅 growth equation (O86 Lagrangian) | 🔴 |

## 建議下一步

### 方向 C: 從 O86 Lagrangian 推導 growth equation
O86 完整 Lagrangian 已閉合 (34/34 PASS)。可以從中推導物質密度微擾 δ_m 嘅演化方程，求解 growth factor D(z)，然後計算 σ₈(z)。

### 方向 E: 用 BOSS DR12 ξ(s) 數據做實證校準
舊 sigma8_norm 腳本有 BOSS DR12 嘅 ξ(s) 數據。可以用呢個數據做實證 σ₈ 測量，然後比較 IDCM 嘅 K_Chain 結構同 BOSS 數據嘅吻合度。

### 方向 F: 文獻研究 — 弱透鏡 S8 測量方法
了解 KiDS-1000、DES Y3、ACT DR6 嘅具體分析流程，睇 IDCM 嘅距離-紅移關係 (O76) 會點樣影響 inferred S8。