# h0_tension — SESSION START (O169 修正交回專用, 2026-09-15 建立)
> **本 O 定位**: 舊目錄 (無 O 編號) — H₀ 投影公式 (D_app) 嘅早期實作。

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `06_complete_record.md` — `H_eff(0.03) = 73.13` (舊伸長) → **`66.33`**; 「匹配 SH0ES 0.12%」→ **6.5σ 偏離** (`H₀_idcm = c/R_H = 72.59` 不變)
- `scripts/02_h0_projection.py:62-124,156,201-202` — D_app + dD/dz 導出
- `scripts/07_calibration_methods.py:29,112`
- `01_problem_record.md:14,88`, `03_first_results.md:28`, `06_complete_record.md:62-69`, `08_calibration_mechanism.md:64`
- dD/dz 導出 (line 201-202) 重推 (斜率 2φ⁻¹ → 1)

**狀態**: [x] 已重驗 (2026-09-23, O170 N4 獨立驗證 — scripts/21 5/5 PASS)
> ★ 重驗結果 = O170 N4 交收, 已處理: `H_eff(0.03) = 73.13 (舊伸長) → 新律 66.27`
> (O169 律 E = ℓ+1.11911398), 「SH0ES 匹配 0.12%」撤回 → 🔴 **N4 開放** (SH0ES 73.04 需新解釋;
> 候選: O167 低 z 斜率比 1−π/44 / 局部擾動)。`H₀_idcm = c/R_H = 72.59` 不變。
> 日期化更正註已落: 03_first_results / 01_problem_record / 06_complete_record /
> 08_calibration_mechanism / scripts/02 + 新檔 09_o170_n4_handoff.md。
> 其他開放項 (Maser 機制) 未掂。

★★ **2026-09-23 更新: N4 已解 — E(ℓ) 低 ℓ 形式已由 O169 推導 (scripts/22 + docs/16, 14/14 PASS)**:
```text
E(ℓ) = 1 + ℓ + (⟨sec⟩_{1..K(z)} − 1)·(1 − 4^{−mℓ}),   m ∈ {5,6,7} = {2N_gen−1, 2N_gen, 2N_gen+1}
  (1) E(0) = 1 EXACT ⟹ H_eff(0) = c/R = 72.59 EXACT (H₀_idcm 恢復, 舊線性律 64.88)
  (2) DESI χ² = 3.2–4.5 (Δχ² ≤ 2);  (3) SH0ES z=0.03: 0.96–1.36σ (舊 7.99σ)
  H_eff(0.03) = 70.96–71.67 (舊線性律 66.27, −9.3% → −1.3~2.9%)
  舊 linear 律 E = ℓ + 1.119… 只係 ℓ ≥ 0.3 高 ℓ 漸近 (E(0) = 1.119 ≠ 1 已修正)
狀態: [x] N4 已解 — 09_o170_n4_handoff.md §4 + 10_translation_layer_analysis.md §5/§6 嘅
      「E(ℓ) 低 ℓ 形式未推導」→ 已推導; 本 O 日期化註已更新 (見 09 檔 §5b 後續)。
```
