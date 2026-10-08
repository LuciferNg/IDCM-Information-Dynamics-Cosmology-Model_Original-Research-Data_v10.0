# O243 docs/04 — R3: 拓撲相變 No-Go 盲測 (譜 rigid / 冇 H(λ) / O7 事件分類)

> **日期**: 2026-10-08｜**script**: scripts/03_topological_no_go.py (**13/13 PASS**)
> **對應**: O243 問題記錄 §三 N3 / §四 R3
> **反駁對象**: Gemini G5/G6 — 「特徵譜線交叉重組 (Band Crossing) / winding number / 幾何相位改變, 全域連續且能量有限」

---

## 1. 拓撲相變需要乜 (機制前提)

Band crossing / spectral rearrangement 需要**哈密頓參數族 H(λ)**: 隨 λ 變化, 特徵值穿越簡併點, 拓撲不變量 (winding number / Chern / Berry phase) 改變。前提 = 有連續參數 λ 可以「扭動」譜。

## 2. 盲測結果 (13/13 PASS)

- **P3a1**: K_chain 譜 γ_n = 4sin²(πn/88), n=1..44: 全部 43 個 gap > 0 — **嚴格遞增、非簡併**
- **P3a2**: min gap = 5.095771e-3 > 0 — 冇內建簡併點
- **P3b1**: K_chain⊗K_tree 無參數 (N=88, B=4 全結構常數) — **冇 H(λ) 哈密頓族**
- **P3b2**: 譜 = 固定代數物件 (γ_n ∈ ℚ(ζ₈₈)⁺) — 冇時間演化推佢
- **P3c1**: ℓ-細化流 (O213) 係 observer 側投影: ℓ 唔出現喺 γ_n 公式 — 譜不變
- **P3c2**: 唯一「流」的不動點 = c (光速) — 係投影極限, 唔係 band crossing
- **P3d1**: V 只依賴 |W|: 相位滑移 π (O7) 保持 |W|=w0 不變 — **vacuum state 不變**
- **P3d2**: O7 ΔE=2|h_i| 係離散、局部、有限能量位元寫入 (H=-56) — 唔係全域真空相變
- **P3d3**: Goldstone m_θ=0 (O73): 相位方向係勢能 flat direction — 「相位轉變」零能量、非相變
- **P3e1**: 參數流形 0 維 (dof=1, O212): 冇閉迴路 — **Berry/幾何相位恆 0**
- **P3e2**: winding number 改變需要連續參數路徑 (0 維空間冇路徑) — 拓撲不變量恆定
- **P3f1**: O242: band crossing 唔係 A 類 (差分) 也唔係 B 類 (結構檢驗) — 無可觀測通道
- **P3f2**: NDT (O242 docs/04): 實體論 vs DTO 讀法實驗檯無差別 — 「拓撲相變」無判別力

## 3. 數學本質

拓撲相變喺 IDCM 嘅三個獨立 no-go:

1. **譜 rigid**: K_chain 是固定 88-site 離散 Laplacian, 特徵值 γ_n = 4sin²(πn/88) 非簡併, 冇 λ 參數 ⟹ 冇穿越可發生;
2. **冇演化「推手」**: 唯一嘅流係 ℓ-細化 (觀察者投影), 不動點=c, 佢唔鬱 γ_n; 冇 Hamiltonian 時間演化;
3. **O7 事件係資訊寫入, 唔係相變**: 相位滑移 π 沿 Goldstone flat direction (m_θ=0), |W|=w0 不變, ΔE=2|h_i| 離散有限; 用 O242 判準 — 唔係 A/B 類可觀測, NDT 令兩讀法無差別。

補充 (P3e1): Berry/幾何相位 ∮A·dλ 需要參數空間閉迴路; IDCM 參數流形 0 維 (唯一錨, 冇 dials) ⟹ 積分恆 0. **winding number 改變需要連續路徑, 0 維空間冇路徑** ⟹ 拓撲不變量係常數.

⟹ **N3 閉合: 拓撲相變 No-Go。** 保留嘅係 O7 類型**離散拓撲事件** (位元寫入) — 佢哋係結構內資訊處理, 唔係真空相變.