# O157 交接材料 — 已知驗證狀態快照 (O155 T31/T32 移交)

> 本檔為 O157 專屬 session 嘅起點材料, 全部數值已經 O155 scripts 驗證, 唔使重推。

## 核心錨點 (直接引用, 全部 PASS)

```
γ_k = 4sin²(kπ/176) (176-Laplacian, 88-site 對偶鏈)
Σγ_odd = 88 (觀察者), Σγ_even = 90 (世界), 178 = 2F₁₁, E−O = 2 = γ₄₄ = μ²
winding(88) = (a−b)/4 圈, 閉合 ⟺ a−b ≡ 0 (mod 4)
winding(55) = (a−b)/2 圈, 閉合 ⟺ d 偶
δ_CKM = atan(sin(21π/176)/sin(9π/176)) = 66.399960° — winding 3 = N_gen 圈
θ₂₃(55) = atan(sin(7π/55)/sin(6π/55)) = 49.1966° — 相鄰 modes, 最大混合
tan δ = 2.288905 ∉ Q (連分數 15 項唔終止) — 域不相容
自對偶錨: 88 鏈 k=44 (γ₄₄ = 2 = μ²); 55 塔中心 27.5 ∉ ℤ 冇錨
懲罰泛函 (建構): E = λ₁·frac(w)² + λ₂·(Δθ/σ)² — 正確分配 = 唯一零懲罰基態
```

## P1 候選路線 (能量泛函第一原理)

1. 譜泛函 E = ⟨φ|ĥ|φ⟩ — Π₄₄ 稅算子 (T18, ⟨φ₄₄|ĥ|φ₄₄⟩ = 2) 已存在
2. winding 項 frac(w)² ← 環拓撲 (T31) — 非整數 winding 嘅譜後果?
3. λ₁/λ₂ 比率由譜隙固定? (λ₁ ↔ B = 4, λ₂ ↔ μ² = 2?)
4. SES 分裂 (T17: 176 = 66⊕68⊕42) 做泛函嘅 sector 分解?

## P2 候選路線 (Dirichlet 場論)

1. 88-site 鏈 transfer matrix → 連續極限 → 邊界項 (Dirichlet/Neumann)
2. Dirichlet → odd sector (sin 型, φ(0)=0), Neumann → even sector (cos 型)
3. U(1) 生成元從 E−O = 2 構造 (2 實自由度 = 複場)
4. 實虛對互補 γ_k+γ_{88−k} = 4 = B 做 U(1) 不變量?
5. 對比: Tr(Dir)−Tr(Neu) = 2 = E−O (scripts/05 C3)

## 陷阱 (O155 教訓)

- 176-Laplacian 慣例 (γ_k = 4sin²(kπ/176)); 44-mode chain 慣例 (γ_n = 4sin²(nπ/88)) 唔好混
- 55 塔 ω 用 2sin(kπ/55) (N=55), 唔係 2N=110
- φ-trap: 360φ⁻² ≈ 137.5 唔可以當閉合
- 唯一性聲稱要對觀測 target 盲測, 唔好對自己定義嘅 target 宣稱
