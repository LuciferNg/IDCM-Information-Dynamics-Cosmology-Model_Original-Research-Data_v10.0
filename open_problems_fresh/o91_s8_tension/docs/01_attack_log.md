# O91 — S8 張力: 攻堅日誌

> **日期**: 2026-08-26
> **狀態**: 🔴 嘗試中 — 核心結構未鎖定
> **前置**: O76 (z 紅移) 🟢, O86 (Lagrangian) 🟢, O10 (峰振幅) 🟢

## 問題

S8 = σ₈ √(Ωₘ/0.3) — 結構增長幅度張力。
Planck CMB σ₈ ≈ 0.811 vs 弱透鏡 σ₈ ≈ 0.76-0.79 (2-3σ)。

## 攻堅嘗試

### 嘗試 1: K_Tree 投影因子 φ^(-2ℓ₈) (scripts/01) ❌

σ₈ = 0.086 (off by 10x) — 投影因子 φ^(-2·4.27) = 0.0163 太細。
問題: 將 CMB 峰歸一化 3ε 直接乘投影因子, 混淆咗 CMB 溫度功率譜同物質功率譜。

### 嘗試 2: Beat 頻譜方法 (scripts/02) ❌

Beat 譜直接歸一化到 Σγ=90 → σ₈ = 9.46 (off by 10x 相反方向)。
問題: top-hat 窗口 W₈(k) ≈ 1 對所有 beat modes (k << 1/R₈), 所以 σ₈² ≈ ΣΔ²(k)/k = 90。
但 beat 譜嘅 k 範圍 (0-0.033 Mpc⁻¹) 遠細過 8 h⁻¹ Mpc 嘅 k (0.57 Mpc⁻¹)。

## 關鍵洞察

### 尺度矛盾
- K_Chain 最小 beat 波長: λ_min = R_world/43 = 96 Mpc (Δn=43)
- 8 h⁻¹ Mpc = 11 Mpc << 96 Mpc
- **8 h⁻¹ Mpc 完全在 K_Chain 次格點尺度 (sub-grid)**
- 物質功率譜喺呢個尺度必須來自 K_Tree 層級投影

### K_Tree 投影嘅未解問題
- 每層 K_Tree 將尺度縮細 4 倍 (B=4)
- 每層投影效率係 φ⁻¹ 定係其他?
- 總功率是否守恆? (MERA isometry 條件)
- K_Tree 層 m 同 O76 嘅 ℓ = log₄(1+z) 係同一概念嗎?

### 需要回答嘅問題
1. **K_Chain 嘅 fundamental power spectrum 形狀係咩?** — 唔係 Σγₙ, 而係 Δ²(k) = f(k) × A²(k)
2. **K_Tree 點樣投影 power 到次格點尺度?** — 每層嘅 power transfer function
3. **CMB 峰振幅 P_m 同物質功率譜嘅關係?** — P_m = 3ε·F_m·φ^(-2(m-1)) 係 CMB 溫度, 唔係物質
4. **σ₈ 積分需要嘅 k 範圍** — 0.001 < k < 10 Mpc⁻¹, 但 K_Chain 只提供 0.0008-0.033 Mpc⁻¹

## 下一步方向

### 方向 A: 從 O76 z-redshift 框架推導物質功率譜
- O76 嘅 ℓ = log₄(1+z) 映射到 K_Tree 層
- 物質功率譜喺層 ℓ: P_ℓ = P₀ · (φ⁻¹)^{2ℓ} · (scale_factor)
- 需要推導 P₀ 同 CMB 歸一化嘅關係

### 方向 B: 用 BOSS DR12 ξ(s) 數據做實證歸一化
- 舊 sigma8_norm 腳本嘅 BOSS 數據整合係有用嘅
- 用 BOSS ξ(s) 測量值做 cross-check, 唔係直接作為 IDCM 預測
- 然後睇 IDCM 嘅 K_Chain 結構能否解釋 BOSS 同 Planck 嘅差異

### 方向 C: 用 O86 Lagrangian 推導 growth equation
- O86 完整 Lagrangian 包含 W-field 同 SM 嘅耦合
- 物質密度微擾 δ_m 嘅演化方程可以從 Lagrangian 推導
- 求解 growth factor D(z) 然後計算 σ₈(z)

### 方向 D: 直接從 K_Chain 推導 σ₈ 作爲 eigenvalue 問題
- σ₈ 係 K_Chain 某個 mode 嘅 eigenvalue
- 8 h⁻¹ Mpc 對應嘅 K_Chain mode n = R_world/(8/h) = 4129.94/11.02 = 374.7
- 但 n > 44, 需要用 K_Tree 嘅模態折疊

## 開放問題清單

| # | 問題 | 狀態 | 方向 |
|:-:|:-----|:----:|:----:|
| 1 | 8 h⁻¹ Mpc 對應嘅 K_Chain/K_Tree mode | 🔴 | A, D |
| 2 | K_Tree 每層嘅 power transfer function | 🔴 | A |
| 3 | CMB 峰振幅同物質功率譜嘅歸一化關係 | 🔴 | A, C |
| 4 | IDCM growth factor D(z) | 🔴 | C |
| 5 | O86 Lagrangian 嘅 density perturbation 方程 | 🔴 | C |
| 6 | 8 h⁻¹ Mpc top-hat window 積分 (數值) | 🔴 | B |
| 7 | BOSS DR12 ξ(s) 數據同 K_Chain 預測比較 | 🔴 | B |
| 8 | 弱透鏡 (KiDS/DES/ACT) 嘅 S8 測量方法 | 🟡 | 文獻 |