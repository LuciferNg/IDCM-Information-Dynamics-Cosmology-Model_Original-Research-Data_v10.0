# O118 — SESSION START

> **Session**: 2026-08-29 (新建立)
> **狀態**: 🔴 未開始
> **來源**: O1-O114 審計後發現不屬於任何現有 O 系列 — 宇宙學結構缺口
> **v10.0 位置**: IDCM-v10.0--It-From-Beat/open_problems_fresh/o118_desi_highz_residuals/

## 問題

見 `01_problem_record.md`

## 前置驗證：v9.0 相關推導

**v9.0 有大量 SYNC 轉折點和阻抗分析，可能包含局部阻抗修正的線索。**

### 1. `sync_bump_analysis/` 系列

| 文件 | 內容 | 驗證問題 |
|:-----|:------|:---------|
| `02_math_verification.md` | z_c = 0.6 = F₄/F₅ 結構推導 | 是否與 v10.0 一致？ |
| `03_sync_dip_to_bump_evolution.md` | SYNC 轉折演化 | 物理機制是否仍然有效？ |
| `references/flrw-idcm-tension-analysis.md` | FLRW vs IDCM 張力分析 | 是否包含阻抗修正的線索？ |

### 2. `kchain_cosmic_web/` 阻抗相關腳本

- `05_impedance_reflection.py` — 阻抗反射模型
- `06_boss_xi_impedance.py` — BOSS ξ(s) 阻抗驗證
- `12_xi_model_impedance.py` — 阻抗模型改進
- `anisotropic_xi/` 系列中的 DESI 比較腳本

### 3. 驗證問題

- v9.0 的阻抗模型是否基於 v_g(n) = cos(πn/88) 的正確框架？
- 在 v10.0 中，群延遲修正已將 χ² 從 42.23 降到 18.09，殘餘主要在 LRG1 (z=0.51)。v9.0 的阻抗模型能否解釋這個殘餘？
- 立方項修正已在 v10.0 中被測試並失敗 — v9.0 是否有其他非多項式修正形式？

## 攻擊路線（建議）

1. 先驗證 v9.0 阻抗模型在 v10.0 框架中的有效性
2. 重點放在 LRG1 (z=0.51, ℓ=0.30) 的局部修正
3. 測試 SYNC 轉折點附近的模式激活阻抗不匹配
4. 使用模式激活框架 (z_n = (γ_n/γ₂)×z_c − 1)

## 前置

- O76 (z紅移翻譯) 🟢
- O51 (群延遲修正) 🟢
- O73 (ω_ring) 🟢
- v9.0: `sync_bump_analysis/`, `kchain_cosmic_web/05-12` 阻抗系列

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

- `docs/01_problem_record.md:10` — 「群延遲修正 (C = −0.16973, 0.02%) 將 DESI DR2 χ² 從 42.23 降到 18.09, 但 χ²/dof = 2」

### ③ 交回任務 (本 O 專屬 session 執行)

1. [ ] 用新 δ 形重算 χ² (舊 42.23 → 18.09 嘅改善幅度需重驗)
2. [ ] 高 z 殘差結論 (LRG1/Lyα) 更新 → 可能可直接閉合

### ④ 唔受影響 (核對過, 免重做)

- 高 z 殘差分析框架

### ⑤ 參考

- `../o169_da_spectral_first_principles/docs/01_elongation_falsification.md` — 證偽全表 (七 tracer)
- `../o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md` — 譜閉合 + 恆等式 11/11 + C = −φ⁻³
- `../o169_da_spectral_first_principles/docs/03_window_selection.md` — K = 22 Z₂ 窗口唯一性
- `../o169_da_spectral_first_principles/docs/04_open_ledger.md` — 誠實帳簿 + 跨 O 影響
