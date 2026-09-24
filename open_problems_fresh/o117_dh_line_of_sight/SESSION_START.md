# O117 — SESSION END (2026-09-01)

## 完成進度

### 🟢 全部閉合 — O117 完滿解決

**3 個子問題全部解決**:

1. **主問題: DH 投影公式錯誤** 🟢
   - 才根原因: DM 和 DH 獨立投影，dD_app/dz 錯誤
   - 解決方案: DH(z) = R_H × (1 + δ_k0 + δ_gd) / (1+z)
   - DH/rd χ²: 59.1 → 7.41 (6 dof)

2. **C_DH 結構係數** 🟢
   - C_DH = C_DM × B/N_gen = C_DM × 4/3
   - 高精度掃描確認: 最優 C_DH = -0.2242, C_DM×4/3 = -0.2263, Δχ²=0.0002
   - 4/3 = B/N_gen = K_Tree 投影維度比

3. **3D 各向異性** 🟢
   - 不是問題 — DM/DH 獨立是徑向效應，非各向異性
   - AP 測試: χ²=4.65 (5 dof), χ²/dof=0.93
   - CMB 各向同性完全保留

### 腳本
- `scripts/01_dh_verification.py` — 基礎 DH 驗證 (v9.0 vs DESI DR2)
- `scripts/02_dh_group_delay.py` — 群延遲修正測試
- `scripts/03_cdh_structural.py` — C_DH 結構係數推導
- `scripts/04_anisotropy.py` — 3D 各向異性分析

### 開放問題
- O118: DM 高 z 殘差（LRG1 -3.05σ，Lyα +1.64σ）
- 所有其他 🔴 問題（見 README）

### 相關資源
- v9.0: `kchain_cosmic_web/anisotropic_xi/70_hz_rederivation.py`, `70e_operator_proof.py`
- O51: `scripts/86_cubic_correction.py` — 群延遲修正推導

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `RESULT.md:6,13` — DH 公式 + C_DM/C_DH (φ⁻³ = √5−2 已出現喺本檔)
- `docs/01_problem_record.md:6,11,23,31,33,51` — 根本原因 + 路線表
- `docs/02_first_principles_closure.md:9,25,26` — C_DM = −C_delay × 2φ⁻¹ × √5 = −0.169733
- `SESSION_START.md:10,31` — 完成進度 + 開放問題
- `scripts/01_dh_verification.py:63-69` — D_app / D_app_group_corrected 定義
- **C_DM 重推**: `C_DM = −C_delay × 2φ⁻¹ × √5 = −0.169733` 已證偽 → 用 O169 新身份 (C = −φ⁻³ 於 (ℓ−1/2) 形) 重新推導 DM 側係數
- **C_DH 重推**: `C_DH = C_DM × B/N_gen = −0.226311` 依賴 C_DM → 重推, 並獨立驗證 `B/N_gen = 4/3` 比例係咪仍然成立 (唔准假設)
- DH/rd χ² = 7.41/6 重算 (新 D_A 下); 舊 59.1 → 7.41 嘅改善幅度重驗
- ★核心結論 **D_H ≠ dD_A/dz** — O169 亦確認 (D_A 伸長修唔到 D_H 側) → **保留**, 只換引用嘅 D_A 公式

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。

---

## ⚠️ O170 證偽交回 (2026-09-24) — 待本 O 重驗

**修正點** (上游 O170 `docs/04_falsifications_open_items.md` §1 F2/F3):

- **F2 (❌ 作廢)**: 本 O 用錯 Lyα 誤差 — 用咗 **0.532**, 但該值實為 Lyα `D_M` 誤差;
  DESI DR2 Table 6 正解 Lyα `D_H/r_d` 誤差 = **0.101** (8.632 ± 0.098stat ± 0.026sys)
- **F3 (❌ 降級為巧合)**: 本 O Gaussian `δ_k0` (`σ_φ = ½·log₄φ = 0.17356`) 被判定無獨立結構依據
  (σ_φ 恰好 = 半個 φ 週期); 且深極限 `M(∞) = ln4 = 1.386 ≠ √2`
  (O170 由 `v_g(22) = 1/√2` 確立徑向深極限 `M = sec(π/4) = √2`)

**問題** (本 O 受影響點):

- `scripts/01_dh_verification.py:90` — Lyα DH σ `0.532` → 應為 `0.101`
- `scripts/02_dh_group_delay.py:33` — 同上
- `scripts/08_T5_exact.py` / `scripts/09_first_principles_closure.py` — 同上 (共用 DESI 陣列)
- **全部 DH/rd χ² 需重算**: σ_Lyα 修正後 χ² 由 **7.41/6 → 29.50/6** (Lyα 變 **−4.76σ** 離群)
  > 註: 早前初算寫 29.22/6（只換 Lyα 一項）；以**全部 6 個 tracer** 嘅 Table 6 誤差重算 = **29.50/6**（見 `docs/03`、`scripts/10`）
- **C_DM / C_DH 重推** (O169 亦已要求, 見上段) — `C_DM = −C_delay × 2φ⁻¹ × √5` 身份已證偽
- `docs/01_problem_record.md` / `docs/02_first_principles_closure.md` / `RESULT.md` 數值同步
- 內部不一致: DM/rd χ² 於 `docs/01` 記 12.81 (用 C_DM), 於 `docs/02` 記 9.65 (用 C_DH) — 需統一

**根因** (Lyα 誤差): v9.0 covariance 矩陣 rows `[11,12]` 排序為 `[D_H, D_M]`, 但 data list 排序為 `[D_M, D_H]`
→ Lyα `D_H` 取錯 `D_M` 變異數:
  `cov[11,11] = 1.02136194e-02` → σ = **0.101** (真 Lyα `D_H`)
  `cov[12,12] = 2.82685779e-01` → σ = **0.532** (真 Lyα `D_M`)

**不受影響** (保留):

- ★核心結論 **`D_H ≠ dD_A/dz`** — DM 與 DH 係獨立投影 (O169 亦確認) → **保留**
- 其餘 5 個 tracer 嘅 DM 誤差逐字正確 (0.167/0.177/0.152/0.318/0.531) ✓
- 其餘 5 個 tracer 嘅 DH 誤差偏差 ≤ 4.15% (LRG3+ELG 最大) — 需以 Table 6 值替換

**狀態**: [~] 部分已執行 (2026-09-24)
> 只加註, 未改本 O 結論檔; 重驗後由本 O 自行寫入。

### 已執行 (2026-09-24)

- [x] **Lyα σ 修正 + 全 DH/rd χ² 重算** — `scripts/10_desi_table6_recompute.py` (7/7 PASS) + `docs/03_desi_table6_error_correction.md`
  - O117 誤差集複現 7.41/6 ✅ → Table 6 誤差重算 **29.50/6** (χ²/dof = 4.92)
  - Lyα pull −0.90σ → **−4.76σ**; 其餘 5 tracer σ_DH 偏差 ≤4.15%
  - 診斷: 自由掃描 C 最優仍係 9.76/6 → 正確誤差下公式無法擬合
  - DM/rd 側複現 12.81 (C_DM) / 9.65 (C_DH) ✅ 誤差集無誤
  - `README.md:54` 已同步 🟢 → 🟡

### 未執行

- [ ] **C_DM / C_DH 重推** — `C_DM = −C_delay × 2φ⁻¹ × √5 = −0.169733` 身份已由 O169 證偽 (新身份 `C = 1 − 2φ⁻¹ = −(√5−2) = −0.23606798` EXACT)；`C_DH = C_DM × 4/3` 連帶需重推 (4/3 比例不許假設)
- [ ] **Lyα −4.76σ 離群性質裁決** — 公式失效 / 高階相位相干 (O118) / Lyα 觀測系統，三選一
- [ ] `docs/01_problem_record.md`、`docs/02_first_principles_closure.md`、`RESULT.md` 內引用 7.41 之陳述 → 以 docs/03 為準
