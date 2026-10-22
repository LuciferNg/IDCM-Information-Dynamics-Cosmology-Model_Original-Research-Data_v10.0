# O155 docs/02 — R2: P_B/P_I projector 精確定義 (scripts/04, 16/16 PASS)

> **日期**: 2026-09-07
> **問題**: P_B/P_I 嘅精確定義 (33-dim 空間), Tr(P_B)=1, Tr(P_I)=32 嘅算子證明。
> 反幻覺鐵律: 1/33 必須由算子 trace 定義, 唔可以當「level 數倒數」就收檔。

## §1 Projector 定義 (ℋ₃₃)

```
ℋ₃₃ = span{|1⟩, ..., |33⟩}       33-dim level Hilbert space
P_B = |33⟩⟨33|                   邊界 projector (最外層 level 33)
P_I = Σ_{k=1}^{32} |k⟩⟨k| = I₃₃ − P_B    內部 projector
```

代數性質 (C1):
```
P_B² = P_B,  P_I² = P_I              (冪等)
P_B·P_I = P_I·P_B = 0                (正交)
P_B + P_I = I₃₃                      (resolution of identity)
Tr(P_B) = 1,  Tr(P_I) = 32
```

## §2 ★ 1/33 = 零模機率 (算子推導, 唔係假設)

**推導**: 33-site free (Neumann) level-chain Laplacian 嘅零模 ψ₀ (唯一, 平移對稱強制):

```
L_neu·ψ₀ = 0,  ψ₀ = (1/√33)·(1,1,...,1)ᵀ   (uniform, ‖ψ₀‖=1)
⟨ψ₀|P_B|ψ₀⟩ = |ψ₀(33)|² = 1/33   ← 邊界 site 機率
⟨ψ₀|P_I|ψ₀⟩ = 32/33              ← 內部機率
```

即: **1/33 係零模喺邊界 site 嘅機率密度** — 由 uniform 零模歸一化推導,
唔係「level 數倒數」假設。同一結果亦可寫成維度歸一化 trace 比:

```
Tr(P_B)/Tr(I₃₃) = 1/33,  Tr(P_I)/Tr(I₃₃) = 32/33
```

## §3 Height operator: Tr(ĥ) = K_tree·F_proj ★

```
ĥ = diag(1, 2, ..., 33)         level index operator
Tr(ĥ) = 1+2+...+33 = 561 = 33·17 = K_tree·F_proj
mean level = 561/33 = 17 = F_proj = L₆−1 = Tr(T̂⁶)−1
```

**Median split** (S5 嘅 level-structure 推導):
```
levels 1..16 (< 17):  16 個 = B²
levels 17..33 (≥ 17): 17 個 = F_proj
→ K_tree = 16 + 17 = B² + F_proj      (median 17 = F_proj 強制)
```
之前 S5 (K_tree = B²+F_proj) 係 O138/O143 身份; 呢度係由 level 階梯 1..33 嘅
中位數 17 = F_proj **重新推導** — 兩者一致。

## §4 唯一性 (1/n 家族)

θ₁₂ = atan(β)+atan(1/n): n=33 Δ=0.0070° 係最細, n=32 Δ=0.0472° (6.7×)。
1/33 喺 1/n 家族唯一 (C6) — 與 docs/09 §15.3 一致。

## §5 Verdict

| 項目 | 狀態 |
|:-----|:----:|
| P_B/P_I resolution of identity, Tr = 1/32 | 🟢 算子定義 |
| **1/33 = ⟨ψ₀|P_B|ψ₀⟩ 零模機率 (推導)** | 🟢 反幻覺鐵律達成 |
| 1/33 = Tr(P_B)/Tr(I₃₃) trace 比 | 🟢 等價 |
| Tr(ĥ) = K_tree·F_proj, mean = F_proj | 🟢 精確 |
| K_tree = B²+F_proj median split | 🟢 由 level 階梯推導 |
| 1/n 唯一性 (6.7×) | 🟢 |
| 零模 ψ₀ 係物理相關態 (ground-state 選擇) | 🟡 結構假設 |
