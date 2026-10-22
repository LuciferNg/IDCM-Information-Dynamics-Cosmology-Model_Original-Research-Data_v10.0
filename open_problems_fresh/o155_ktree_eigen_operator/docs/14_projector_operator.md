# docs/14 — Item 1: P_CY₃ projector 算子化 (176→42, kernel = 134)

**日期**: 2026-09-07 · **Script**: 18 (20/20 PASS) · **狀態**: 🟢 算子構造閉合 / 🔴 mode 選擇規則開放

## 1. 自然分解 (T̂ 階梯三層)

```
176 = 66 ⊕ 68 ⊕ 42
    = 2K_tree ⊕ 2F₉ ⊕ 2F₈        (tree-pair ⊕ F₉-pair ⊕ F₈-pair)
```

| 扇區 | 值 | 身份 | 出處 |
|---|---|---|---|
| tree-pair | 66 | 2K_tree = Σλ_tree (Dirichlet trace) | R3 🟢 |
| F₉-pair | 68 | 2F₉ = B·F_proj = 2(K_tree+1) | R3 🟢 |
| F₈-pair | 42 | 2F₈ = N_d⁻ (觀察者) | T13 🟢 |

## 2. 層級: tree ⊕ home (docs/08 交叉)

```
N = K_tree + F₁₀ = 33 + 55              (chain = tree + home)
home-pair = 2F₁₀ = 110 = 68 ⊕ 42        (home = F₉-pair ⊕ F₈-pair)
2N = 2K_tree + 2F₁₀ = 66 + 110
```

## 3. ★ 幾何扇區 = tree-pair ⊕ F₉-pair = 134 = h¹¹+h²¹

```
V_geom = 66 + 68 = 134 = 4K_tree + 2    (T13)
V_obs  = 42
SES: 0 → 2F₈ → 2(F₈ ⊕ F₉ ⊕ K_tree) → 2(F₉ ⊕ K_tree) → 0   (分裂, T14)
```

## 4. 顯式 idempotent

P = F₈-summand 投影 (ℝ¹⁷⁶ 上嘅 block 形式): P² = P, rank 42, nullity 134,
tr P = 42, P 固定 Im(P), P 殺幾何扇區。全部精確驗證。

## 5. 自然性: F₈ = AP 終止項

- AP {6,11,16,21} 終止於 F₈ = 21 (R4: F₉ = K_tree+1 封頂)
- 觀察者 = AP 階梯最後一級 ×2 — 階梯嘅「最後 rung」
- F₈ + F₉ = F₁₀ (fib 身份 → home 完整)

## 6. 誠實 audit

- 🟢 分解/冪等/rank-nullity/SES: 全部精確
- 🔴 **mode 選擇規則**: F₈-pair (42 個 mode) ↔ 對偶鏈實際 mode 嘅映射未定
  (候選: 21 對 (k, 88−k)? γ 閾值? T̂ 權重?) — 需要 mode 級判準
- P 喺 ℝ¹⁷⁶ 嘅 block 形式自然 (三層 = T̂ 階梯), 但 physical mode 對應係下一步
