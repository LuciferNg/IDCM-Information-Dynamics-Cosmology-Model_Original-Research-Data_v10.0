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

## ⚠️ O169 修正交回 (2026-09-15) — 本 O 專屬 session 必須重新驗證 / 重新推導

> **上游 O**: `../o169_da_spectral_first_principles/` (commit 41b5485; docs/01–04 + final_result.md)
> **性質**: 上游結構修正 — 本 O 下列結論**依賴已證偽嘅伸長定律**, 需就地重驗或重推。
> **鐵律**: 唔准用自由參數 tune 返舊結論; 唔准引入新常數補齊; 若新結構出唔到 → **誠實標 🔴**。
> **本節只加註** — 本 O 原有結論 (01_problem_record.md / docs/ / final_result.md) 未經改動,
> 重驗後嘅新結論由本 O session 自行寫入, 並更新本節狀態。

### ① 上游修正內容

```
【已證偽】E(ℓ) = 1 + 2φ⁻¹ℓ              2φ⁻¹ = 1.2360679
          DESI DR2 D_M × 6 排除 4.88σ (自由擬合 a = 0.994278 ± 0.04951, b = 1.12157 ± 0.02458, ρ = −0.9575)

【新零參數】E(ℓ) = ⟨γ⟩_odd/2 · ℓ + 1/⟨v_g⟩_{1..22} = 1·ℓ + 1.11911398
          χ²(D_M × 6) = 2.4528/5,  6/6 |σ| ≤ 1.0     (舊 27.16 / 舊+δ 13.09)
          a = ⟨γ⟩_odd/2 = μ²/2 = Σγ_odd/N_d = 1      (Σγ_odd = 44 = N_d, EXACT)
          b: 窗口 K = 22 = N_d/2 = Z₂ 自對偶模 (掃 K = 1..43, 唯一 ≤1σ)

【δ 新身份】δ(ℓ) = −φ⁻³(ℓ − 1/2),   C = 1 − 2φ⁻¹ = −(√5−2) = −0.23606798  (EXACT)
          ⚠️ 舊 C = −0.1697 係 (ℓ−0.5)(1−4^{−ℓ}) 形狀嘅係數 — 定義唔同, 唔可直接比數值
             (C_old/C_new = 0.7189); 舊形嘅 (1−4^{−ℓ}) 因子係多餘

【φ 影子】E(ℓ) = ℓ + √5/2  (δ 零點精確喺 ℓ = 1/2, E(1/2) = φ) — 同譜讀法簡併 0.097%, 觀測不可分辨

【殘餘】LRG1 −3.05σ → −1.00σ ; Lyα +1.64σ → +0.05σ ; BGS(D_V) −2.15σ → +1.45σ
```

### ② 本 O 受影響檔案 (grep 定位)

- `RESULT.md:6,13` — DH 公式 + C_DM/C_DH (φ⁻³ = √5−2 已出現喺本檔)
- `docs/01_problem_record.md:6,11,23,31,33,51` — 根本原因 + 路線表
- `docs/02_first_principles_closure.md:9,25,26` — C_DM = −C_delay × 2φ⁻¹ × √5 = −0.169733
- `SESSION_START.md:10,31` — 完成進度 + 開放問題
- `scripts/01_dh_verification.py:63-69` — D_app / D_app_group_corrected 定義

### ③ 交回任務 (本 O 專屬 session 執行)

1. [ ] **C_DM 重推**: `C_DM = −C_delay × 2φ⁻¹ × √5 = −0.169733` 已證偽 → 用 O169 新身份 (C = −φ⁻³ 於 (ℓ−1/2) 形) 重新推導 DM 側係數
2. [ ] **C_DH 重推**: `C_DH = C_DM × B/N_gen = −0.226311` 依賴 C_DM → 重推, 並獨立驗證 `B/N_gen = 4/3` 比例係咪仍然成立 (唔准假設)
3. [ ] DH/rd χ² = 7.41/6 重算 (新 D_A 下); 舊 59.1 → 7.41 嘅改善幅度重驗
4. [ ] ★核心結論 **D_H ≠ dD_A/dz** — O169 亦確認 (D_A 伸長修唔到 D_H 側) → **保留**, 只換引用嘅 D_A 公式
5. [ ] 同 O170 (相位深度徑向映射) 劃清界線: 徑向本徵映射留 O170, 本 O 專注 partial trace 算符

### ④ 唔受影響 (核對過, 免重做)

- ★ D_H ≠ dD_A/dz (DM/DH 兩個獨立投影) — O169 側面確認, 保留
- 3D 各向異性分析: AP test χ² = 4.65 (5 dof), χ²/dof = 0.93; 徑向效應非各向異性
- CMB 各向同性保留

### ⑤ 參考

- `../o169_da_spectral_first_principles/docs/01_elongation_falsification.md` — 證偽全表 (七 tracer)
- `../o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md` — 譜閉合 + 恆等式 11/11 + C = −φ⁻³
- `../o169_da_spectral_first_principles/docs/03_window_selection.md` — K = 22 Z₂ 窗口唯一性
- `../o169_da_spectral_first_principles/docs/04_open_ledger.md` — 誠實帳簿 + 跨 O 影響
