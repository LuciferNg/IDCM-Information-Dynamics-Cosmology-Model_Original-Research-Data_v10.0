# O188 docs/28 — R13 L2h：62-axis frame 嘅 rep-theoretic decomposition（elementwise 最後出路）

**日期**: 2026-10-10（Route L2 第十輪）
**腳本**: `scripts/28_l2h_rep_decomposition.py` — **7/7 PASS**（logs/28.txt）
**對象**: R12 verdict 指明「elementwise map remains open for a **rep-theoretic construction**」—— 今輪就係嗰個 construction，但喺正確層級（frame 級，唔係 per-axis 級）

---

## 〇、一句話

**elementwise spin-label（每條 axis 帶一個 j）唔成立，但「frame 係 spin-1 irrep V₁ 內嘅 2I-stable object」係新定理。** 62-axis frame = 三個 homogeneous spaces G/C₁₀、G/C₆、G/C₄ 嘅 union，全部位於 2I 嘅 3-dim irrep V₁ = ℝ³ —— 呢個先係 rep-theoretic 級別嘅正確對應，唔再係 geometric-symmetry 嘅 per-axis 嘗試。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| P1 | 2I G-action 喺 62 axes 上：**3 orbits**（V=12、F=20、E=30）= homogeneous spaces 120/10、120/6、120/4 | ✅ |
| P2 | Pointwise stabiliser 精確：12→{10}、20→{6}、30→{4}（2I lifts of C₅/C₃/C₂） | ✅ |
| P3 | **★ Frame closure theorem：每個 g∈2I 將每個 axis 送到 62-set 成員（|violations|=0）** —— frame 係 V₁ 內嘅 2I-STABLE SUBSET | ✅ |
| P4 | Burnside ⟨χ,χ⟩ per orbit = {12: 4, 20: 8, 30: 16}（exact rationals；transitivity ≥2 驗證；**4/8/16 = 2²/2³/2⁴ 記錄，冇結構 claim**） | ✅ |
| P5 | 2I irreps dims {1,2,2,3,3,4,4,5,6}：Σd² = 120 = |2I|（rep warehouse identity） | ✅ |
| P6 | V₁ weight space {−1,0,+1} = K-table alphabet —— **STRUCTURAL COINCIDENCE CANDIDATE**（zero 頻率語義唔同：K 嘅 0 係 exact-orthogonality accident、weights 係 generic eigenvalues；唔 claim） | ✅ |
| P7 | Verdict：elementwise spin-label **NOT established**（R12 negative stands）；frame 級對應升格 rep-theoretic + equivariant | ✅ |

## 二、結構意義

- **R12 嘅「rep-theoretic construction」兌現**：R12 否定 per-axis stabiliser→j；今輪喺**正確層級**建立對應 —— 唔係「axis a 帶 spin j」，而係「**成個 frame 係 spin-1 irrep 內嘅 equivariant object**」。
- **P3 係新定理**：62 axes 對 2I 嘅 spin-1 action 封閉（0 violation）—— frame 唔係任意點集，而係 V₁ 內嘅 G-stable subset。呢個係 rep-theoretic（唔係數值湊）：真群作用、精確 ℚ(√5)。
- **Cell types = coset spaces**：vertex axes ↔ G/C₁₀、face ↔ G/C₆、edge ↔ G/C₄（120/10=12、120/6=20、120/4=30）—— orbit 結構由 stabiliser 完全決定，跟 2I 嘅 subgroup lattice。
- **P4 嘅 4/8/16**：⟨χ,χ⟩ 數值 4、8、16 係「pair action 嘅 orbit 數」—— 誠實記錄為數據；冇 operator identity 將佢接到 IDCM 量，唔 claim。
- **P6 嘅 {−1,0,+1} = weight space**：K 表 entries 同 V₁ weight space 作為**有序集合**相同 —— 但 zero 嘅統計語義唔同（K 嘅 0 極少見係正交 accident；weight m=0 係 generic）→ structural coincidence candidate，唔 claim。

## 三、判決

- **L2h：完成** —— frame-級 rep-theoretic 對應（spin-1 irrep 內嘅 G-stable object）＋ 三個 homogeneous spaces
- **Elementwise spin-label 最終狀態**：**否定**（R12 per-axis 候選被面積譜 refute；R13 證明正確層級係 frame/equivariant，唔係 per-axis）—— 「唔 claim」由「結構性否定 + 指明正確層級」完整收斂
- 🔴 未閉合：無（此路線）；frame 內嘅 spin-label field（每 axis 帶一個 j 嘅 field-theoretic map）仍屬未來方向，但**唔係 O188 範圍內嘅必要對應**（範圍鐵律：純結構對應）

## 四、同前輪對比
- R12（L2g）：試 per-axis stabiliser→j —— 面積譜 refute（geometric-symmetry mismatch）
- **R13（L2h）：rep-theoretic construction 喺 frame 級成立** —— 62 axes = V₁ 內 2I-stable、三 homogeneous spaces；per-axis 嘅意圖由 frame-level equivariance 取代
- L2 最終終態：frame 級對應**完整**（threshold → cover → per-row 定理 → unoriented 表 → rep-theoretic equivariance）；per-axis spin-label 有結構根據嘅否定