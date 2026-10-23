# O234 — 質量公式檢驗方法反推: RG-invariant 質量比驗證協議 (FLAG/PDG 凍結觀測層)

## 狀態: 🟢 已閉合（方法論閉合，2026-10-07；35/35 獨立審計）

## 結論
檢驗方法建立完成並交付：質量公式 m_f = M₀·γ_n·C_f 在 ratio 層的可證偽內容被精確定界——只有一個純γ比（u/d）可檢驗且雙尺通過（MS +0.85σ / RGI +0.51σ），其餘 8 個比在 {C∈ℝ⁺} 模型類內結構上不可證偽；C-shape 被凍結層釘死（shape DOF=0）但只有後驗意義；8 條零自由參數預言已 pre-registered，等外部 lattice 量度（killer = P2 u/d，P1 ms/mu=42.89 已被指認為循環）。

## 關鍵公式
- m_f = M₀·γ_n·C_f（O120 by-construction ⟹ γ·C 回復恆等，0 檢驗力）
- γ_n = 4sin²(nπ/88)（A_γ: e1 u2 d3 s4 μ5 c7 τ9 b11 t13）；γ3/γ2 = **2.245223121**
- C-shape v2: u=1 d=0.958 s=10.777 c=41.585 b=79.645 | e=1 μ=8.356 τ=44.418（anchor 每扇區=1）
- redundancy 閉環: (b/c@3GeV)(c/s) = 53.436 vs M_RGI_b/M_RGI_s = 53.369（dev 0.13%, z=+0.08）
- 不可證偽性: 模型類 {m=M₀γC, C∈ℝ⁺} ⟹ P(mismatch)=0（C-dominated 比）

## 依賴
O120 → O233 → O136 → O137 → O234；handoff O234 → O209（混標度 watch）；P3/P4 → O235

## 密度基準
- N_search = 72（有序 γ 對枚舉）+ 結構池掃描（nominal, look-elsewhere 未校正）
- N_mc = 10⁶（scripts/02 枚舉密度 null 對照），seed = deterministic
- d_obs = 0.85σ（u/d 純γ MS 通道，唯一命中）
- 命中率 = 1.4%（1/72 nominal）→ 🟡（單一測試點，非 5σ 閉合；258 條目見 docs/02-04）

> ⚠️ O208 規則: 本 O 為方法論閉合（檢驗能力定界 + 預言 register），唔係常數匹配閉合——密度基準記錄判別力，唔係命中優於 5σ。

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `9560b37c3c8c592b` | 2026-10-24 | closed | 檢驗方法建立完成並交付：質量公式 mf = M₀·γn·Cf 在 ratio 層的可證偽內容被精確定界——只有一個純γ比（u/d）可檢驗且雙尺通過（MS +0.85σ / RGI +0.51σ），其餘 8 個比在 {C∈ℝ⁺} 模型類內結… | open_problems_fresh/o234_mass_ratio_reverse_validation/final_result.md | — |
<!-- conclusion-history:end -->
