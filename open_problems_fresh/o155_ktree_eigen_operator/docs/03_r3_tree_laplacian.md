# O155 docs/03 — R3: 33-level tree Laplacian 算子證明 (scripts/05, 12/12 PASS)

> **日期**: 2026-09-07
> **問題**: 33-level tree Laplacian (λ_k = 4sin²(kπ/68)) Σλ = 66 = 2K_tree — 算子證明 + 同 2N_gen·L₅ 身份嘅關係

## §1 算子定義

**L_tree = 33-site chain 嘅 Dirichlet Laplacian** (兩端固定):

```
L_tree = tridiag(2, −1) 33×33      (diag 2, 上/下離對角 −1)
```

物理讀法: tree 有 33 個 levels = 33 條 links 喺 F₉ = 34 個節點之間 (docs/01:
K_tree = F₉−1 = 33); 兩端夾制 (Dirichlet) — 邊界之外冇 level。

## §2 譜 (全部 33 模態驗證)

```
λ_k = 4sin²(kπ/68) = 2 − 2cos(kπ/34),  k = 1..33
```

numpy eigh vs mpmath 公式: 33/33 模態一致 (tol 1e-10)。
λ₁ = 0.008532 (基態), λ₃₃ = 3.991468 (Nyquist 類模態, γ₄₄=4 對照)。

## §3 Σλ = 66 = 2K_tree = 2N_gen·L₅ (trace 證明)

```
Tr(L_tree) = 33 × 2 = 66        (diag 2 × 33 sites)
Σ_{k=1}^{33} λ_k = 66           (譜和 = trace)
66 = 2K_tree = 2N_gen·L₅ = 2·3·11
```

**一般身份** (C6, n=3..40 全部成立):
```
Σ_{k=1}^{n} 4sin²(kπ/(2(n+1))) = 2n
```
— Dirichlet chain 嘅 trace 身份係一般定理, n=33 時 = 66。

## §4 ★ Dirichlet vs Neumann: 邊界夾制代價 = E−O 奇偶隙

```
Tr(L_Neumann) = 64 = 2(K_tree−1)       (free chain, 端點 diag 1)
Tr(L_Dirichlet) − Tr(L_Neumann) = 66 − 64 = 2
2 = E−O = Σγ_even − Σγ_odd = 90 − 88   (88-site 對偶鏈奇偶隙, μ²)
```

**結構**: tree 兩端夾制令 Laplacian trace 增加 2 — 啱好等於 chain sector 嘅
世界−觀察者奇偶隙。tree 邊界修正 = chain 奇偶不對稱, 跨 sector 一致。
(⚠️ γ 用 176-Laplacian 慣例: γ_k = 4sin²(kπ/176), k=2..88 even → 90, k=1..87 odd → 88)

## §5 66 = dim Λ²(12) (O59 連接)

```
66 = C(12,2) = dim Λ²(12) = (6,6) ⊕ (10,3̄) = 36 + 30
```

Tree Laplacian trace = SU(12) 反對稱平方維度 — tree 譜和撞正 GUT 表示維度。

## §6 譜分母 68 = 2F₉ = B·F_proj

```
68 = 2·34 = 2F₉ = 2(K_tree+1)        (K_tree = F₉−1)
68 = B·F_proj = 4·17                  (分支 × 投影維)
```
Dirichlet chain 譜分母 2(n+1) 嘅 n=33 特例 = 2F₉ — tree 維度同 T̂⁹ (9=N_gen²) 嘅
連接 (docs/01 C5)。

## §7 Verdict

| 項目 | 狀態 |
|:-----|:----:|
| λ_k = 4sin²(kπ/68), k=1..33 (33/33) | 🟢 算子譜驗證 |
| Σλ = 66 = 2K_tree = 2N_gen·L₅ | 🟢 trace 證明 |
| 一般身份 Σ4sin²(kπ/(2(n+1))) = 2n | 🟢 定理 |
| **Dirichlet−Neumann = 2 = E−O (90−88)** | 🟢 跨 sector 一致 |
| 66 = dim Λ²(12) = 36+30 | 🟢 O59 一致 |
| 68 = 2F₉ = B·F_proj | 🟢 |
| 點解係 Dirichlet (兩端夾制) | 🟡 結構假設 (夾制 = tree 有界) |
