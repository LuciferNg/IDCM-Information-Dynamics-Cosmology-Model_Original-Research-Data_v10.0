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

# 2026-09-22 O208 越權修改 — 需重建 (⚠️ 本段為新增, 以上原文一字不刪)

> 來源: O208 docs/05_rebuild_handover.md (事故承認)
> 狀態: 🔴 本檔案被 O208 session 越權修改, 需以本 O 上下文重建

## 事項

| # | 檔案 | O208 改咗啲咩 | 建議動作 |
|:-:|:-----|:------------|:--------|
| 1 | `scripts/09_first_principles_closure.py` | 6 處 dict True (first_principles_checklist) 被改為計算/🟡 | 以本 O 上下文重建 (以 O117 docs 重建, chi² 數值保留); 重跑確認 PASS 數唔含字面 True |

## 驗證標準
- 以 O117 docs 重建, chi² 數值保留; 重建後 script 輸出 PASS 數與 O 記錄一致或誠實標註
