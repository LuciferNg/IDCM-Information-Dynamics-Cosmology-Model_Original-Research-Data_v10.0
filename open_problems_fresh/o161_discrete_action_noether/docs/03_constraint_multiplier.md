# O161 docs/03 — 約束乘子重構: mass-as-multiplier (T3)

> **日期**: 2026-09-08 · **腳本**: scripts/03_constraint_multiplier.py (25/25 PASS) · **狀態**: 🟢
> **目標**: 將 sector-locking 寫成約束, μ² 做 Lagrange multiplier —
> 將 O159 譜身份重寫為變分語言 (形式統一, 唔係新物理)。

## 1. 約束 + 乘子

```
C[Φ] := Σ_even|Φ_k|² − Σ_odd|Φ_k|² − Δ
S' = S + λ·C = Σ_k(γ_k+μ²)|Φ_k|² + λ(Σ_even|Φ_k|² − Σ_odd|Φ_k|² − Δ)
```

- canonical state (|Φ_k|²=1): Σ_even = Σ_odd = 44 ⟹ C = 0
- vacuum: C = 0 ⟹ **Δ = 0** (兩狀態都滿足約束 — 約束非空)
- ∂S'/∂λ = C ⟹ stationary ⟹ 約束強制 (標準 Lagrange 力學, 鞍點結構)

## 2. EOM + 扇區隙: λ = 1, μ² = 2λ = 2

```
δS'/δΦ*_k = (γ_k + μ² + λ·s_k)Φ_k = 0,   s_k = +1 (even) / −1 (odd)
扇區隙 2λ = (μ²+λ) − (μ²−λ)
要求 2λ = E−O = 2  ⟹  λ = 1
μ² = 2λ = 2
```

**★★ 四重身份**: μ² = E−O = γ₄₄ = BC-cost = **2λ** — O159 三路 + 乘子路。
EOM 只有平凡解 (有效質量 {even 3, odd 1} 全正 — 一致, 冇 tachyon)。

## 3. ★ 物理內容: 質量 = sector-locking 價格

跨扇區移動 δ 單位 occupation (odd → even) 嘅能量成本:

```
ΔS' = (μ²+λ)δ − (μ²−λ)δ = 2λδ = 2δ
δ = 1:    成本 = 2 = μ²      (一個單位唔平衡 = 一個質量量子)
δ = N_d:  成本 = 2N_d = 88 = Σγ_odd  (全轉移 = 觀察者扇區能量)
鎖定態: λ·C = 0 (約束態上乘子項零能量)
```

**mass-as-multiplier 嘅物理陳述**: 質量 = 扇區鎖定約束力嘅常數 —
打破 sector balance 一個單位嘅代價就係 μ²。唔係新物理, 係新語言。

## 4. Mean-preserving split + 誠實 off-shell 差異

- mean(μ²±λ) = μ² = 2 (扇區對稱 split 唔郁譜平均)
- λ = 1 = μ²/2 (兩扇區平分約束力)
- **傳播子**: G'(even) = 1/(γ+3) < G = 1/(γ+2) < G'(odd) = 1/(γ+1) ∀k —
  split 括住 O159 傳播子; mean(G') > mean(G) (Jensen 凸性)。
  ⚠️ **off-shell 內容唔等於 O159** — 乘子重構嘅波動層係新結構
  (扇區-dependent 質量); 形式統一嘅範圍 = on-shell/譜內容, 唔包括傳播子。

## 5. 判決 (R3)

- ✅ λ = 1 由 2λ = E−O = 2 重現 μ² = 2 (冇新參數 — λ 由譜身份唯一定)
- ✅ Δ = 0 由 occupation balance 定 (canonical/vacuum 一致)
- ✅ μ² 四重身份閉合: 譜身份 (E−O) / 自對偶 (γ₄₄) / 邊界 (BC-cost) / 乘子 (2λ)
- ✅ **非平凡內容 = 有**: mass-as-multiplier 提供「質量 = 扇區鎖定價格」嘅
  操作讀法 (轉移成本 2λδ = μ²δ), 同變分語言統一 — 但唔係新物理
- 🟡 剩: 乘子 reformulation 嘅 off-shell (傳播子 split {1,3}) 有冇物理對應 —
  目前評「形式統一工具」, 唔宣稱新預測; 「扇區鎖定」嘅本體論歸屬 (詮釋層)
