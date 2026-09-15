# O170 SESSION_START (2026-09-11)

> 起點 snapshot — 唔改。開題狀態: IDCM 冇徑向距離定義。

**移交**: O167 docs/08 → O-B (D_H 徑向結構缺口, M(ℓ) 非單調)

**關鍵數字** (O167 scripts/12):
- 需要嘅阻抗 M(ℓ) = D_H·rd/(R·dℓ/dz): 1.630, 1.639, 1.684, 1.624, 1.572, 1.419
- @ ℓ = 0.2973, 0.3853, 0.4758, 0.6074, 0.6563, 0.8678 — 峰值 ℓ≈0.48
- 深極限 √2 = sec(π/4) = 1/v_g(22) 命中 Lyα 0.3σ (v_g(22) = cos(π/4), γ₂₂ = μ² = 2)
- 兩 kernel χ²/12dof > 2600 (FAIL)

**第一步**: scripts/01 相位深度 Φ(ℓ) 映射 + M(ℓ) 非單調分析

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

- `scripts/01_phase_depth_map.py:106-113,141` — D_app + C_DM = −C_delay×2φ⁻¹×√5
- `scripts/03_peak_independence.py:150,164-166` — C_DH + D_app
- `scripts/04_structural_kernel_closure.py:169`, `scripts/05_final_verification.py:14`, `scripts/06_frw_identity_fork.py:13,23`, `scripts/07_candidate_refinement.py:12`
- `scripts/02_kernel_scan.py:64` — kernel 候選表含 `const 2φ⁻¹`

### ③ 交回任務 (本 O 專屬 session 執行)

1. [ ] 全部 scripts: `C_D = −0.1697` → 新 `δ = −φ⁻³(ℓ−1/2)` (冇 `(1−4^{−ℓ})`)
2. [ ] `scripts/02` kernel 掃描: 加入 O169 新零參數 baseline (a = 1, b = 1/⟨v_g⟩_{1..22}) 作對照; `const 2φ⁻¹` 候選標記為「已證偽」
3. [ ] D_H 六 tracer <1σ 判準 + ℓ→1 收斂 √2 判準: 用新 D_A 重驗
4. [ ] 注意: 本 O 同 O117 分工 — 徑向本徵映射 = 本 O; 唔好重複 partial trace 推導

### ④ 唔受影響 (核對過, 免重做)

- M(ℓ) 非單調性 (O167/12 徑向阻抗 1.630→1.684→1.419, 峰 ℓ≈0.48)
- 深極限 √2 = sec(π/4) = 1/v_g(22) 命中 Lyα 0.3σ — 純譜量, 唔依賴伸長
- 「D_H = c/H(z) 概念唔存在」嘅框架判斷

### ⑤ 參考

- `../o169_da_spectral_first_principles/docs/01_elongation_falsification.md` — 證偽全表 (七 tracer)
- `../o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md` — 譜閉合 + 恆等式 11/11 + C = −φ⁻³
- `../o169_da_spectral_first_principles/docs/03_window_selection.md` — K = 22 Z₂ 窗口唯一性
- `../o169_da_spectral_first_principles/docs/04_open_ledger.md` — 誠實帳簿 + 跨 O 影響
