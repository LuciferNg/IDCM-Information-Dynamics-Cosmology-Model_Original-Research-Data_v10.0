# O123 — 中微子 δ_CP 從 CY₃ 投影

## 狀態: 🟡 結構派生候選（π 分支 🟢、深度 n 🟡、1e-8 唯一性 🟢；底層推導 🔴 剩一項）

## 結論
`SESSION_START.md` 指定路線（CY₃ 投影 / Z₅ twisted sector）經兩個獨立 no-go 否證；
上游 4 個互相矛盾候選（222.5°/72°/144°/230°）全部結構否證；
δ_PMNS 唯一存活機制 = tree 扇區實比 arctan，結構候選 = **π + atan(β) = 211.717474°**（🟡）。

## 關鍵公式
- 統一相位公式: `δ_sector = arg(Z_canon) + atan(|Z_canon|)`
  - chain: Z = ω₂₁/ω₉ = +2.2889 → δ_CKM = 66.399960°（J > 0，1e-9）
  - tree: Z = −φ⁻¹（tree 唯一負物件）→ δ_PMNS = 211.717474°（J < 0）
- Sector-Chirality 定理: `sign(J_PMNS) = −sign(J_CKM)` — J_PMNS ≈ −0.0177 vs NuFIT 6.1 ≈ −0.0178 ✓
- 有限深度表示: `π + atan(F₅/F₆) = 212.005383°`（理論窗 211.72°±0.15°，有界 0.29°）
- 唯一性: tree-池 924 式只有 β 一個獨立值（3 個代數別名），最近競爭者間距 0.05°
- no-go: `uniform Z₅ twist ⇒ J ≡ 0`（P4）；`δ_230 coverage = 100%`（115 witness）
- 真身份（保留 🟢）: `46 = Σγ(k≡0 mod 4, k=4..88) = 46.000000`

## 盲測對比（凍結窗口 data/00）
- NuFIT 6.1 NO δ = 212°：pull −0.01σ；PDG 2025 217.8°：pull −0.20σ
- J_CP 統計帶無法分開 βⁿ（半寬 0.0285 > 族跨度 0.0189）— 誠實 FAIL

## 密度基準
- N_search = 570（tree-比家族式數；B(a) 全池 = 2751；唯一性池 = 924）
- N_mc = 500，seed = 7
- d_obs = 0.2825°（|211.7175 − 212|）；d_med = 0.3898°；q_obs = 72.5% → 🟡
- 唯一性掃描: tol 1e-8，mult = 1（代數別名除外），最近獨立競爭值 dev = 1.01e-3

> ⚠️ O208 規則: 數值貼合不顯著（q_obs = 72.5%）；價值在形式定理 + 否證 + 唯一性。

## 剩餘 🔴（唯一）
1. 統一相位公式 δ = arg(Z) + atan|Z| 嘅底層推導（由 U_PMNS 構造，唔係 pattern 歸納；
   接 ckm_reconstruction texture 算子）。
2. 跨域映射（δ_CP ↔ 宏觀 β，交 O26-G1/O43-C）

## 依賴
O54 → O59 → O53 → O123；ckm_reconstruction T7/T9 → O123

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `6d5148ea2e60c0be` | 2026-10-24 | partial | SESSIONSTART.md 指定路線（CY₃ 投影 / Z₅ twisted sector）經兩個獨立 no-go 否證； 上游 4 個互相矛盾候選（222.5°/72°/144°/230°）全部結構否證； δPMNS 唯一存活機制 … | open_problems_fresh/o123_neutrino_delta_cp/final_result.md | — |
<!-- conclusion-history:end -->
