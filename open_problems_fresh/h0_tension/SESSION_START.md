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

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。
