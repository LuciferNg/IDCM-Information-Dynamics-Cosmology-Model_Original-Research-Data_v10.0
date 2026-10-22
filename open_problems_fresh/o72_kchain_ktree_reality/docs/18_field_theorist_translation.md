# O72 — docs/18: 場論學家友好翻譯 — IDCM 嘅 Lagrangian 語言

> **日期**: 2026-08-25
> **狀態**: 🟡 **初版 — 用場論學家識嘅語言重新表達 IDCM 核心**
> **目的**: 令「研究連續場論和 Lagrangian 的人」睇得明 IDCM 想證明咩
> **策略**: 由 O39 SSB 勢 (場論學家識嘅結構) 出發, 唔由數字閉合出發

---

## 0. 序言 (俾場論學家)

> 我哋有一個量子場論框架, 核心係一個複合標量場 W 喺
> 緊緻環 (S¹, 44-site lattice) 上嘅 SSB 凝聚。
> 佢冇暗能量、冇膨脹、冇暗物質粒子 — 呢啲全部係
> 同一結構嘅投影效應。以下係 Lagrangian 語言嘅描述。

---

## 1. 主 Lagrangian (O39, 已閉合)

### 1.1 場內容

```
φ_n(t): 44-site ring 上嘅實標量場, n = 1..44
W(t):   複合標量場 (W-field, 凝聚場) — 由 φ_n 嘅低能模式構成
```

### 1.2 自由部分 (K_Chain)

```
L_free = Σ_{n=1}^{44} [ (1/2)φ̇_n² − (1/2)(φ_{n+1}−φ_n)²/a² ]

譜: ω_k² = (4/a²)sin²(πk/44), k = 1..44
   → γ_k = 4sin²(πk/88) (對偶鏈)

物理: 緊緻 S¹ 上嘅 free massless scalar (tight-binding model)
  → 場論學家: 標準 lattice scalar field theory ✓
```

### 1.3 凝聚部分 (SSB, O39)

```
L_cond = (∂_μ W)†(∂^μ W) − V(W)
V(W) = −μ²|W|² + λ|W|⁴

μ² = Σγ_even − Σγ_odd = 90 − 88 = 2   (質量項, 奇偶分裂)
λ = 2/[3(N_d−dim_ℂ)] = 2/123          (四次耦合, 123 = L₁₀)

→ Mexican hat 勢 (標準 SSB!)
→ 真空: ⟨W⟩² = μ²/(2λ) = 123/2 = 61.5
→ V_min = −μ⁴/(4λ) = −123/2 = −61.5
→ 凝聚穩定: V''(⟨W⟩) = 8μ² > 0 ✓
```

### 1.4 真空能 ↔ 宇宙常數

```
V_min = −61.5 (O39: 凝聚負能)
V_Λ = F(γ) + 44 − F₈ − B = 283.0821 (O62: 全譜修正)

→ 場論學家: 「OK, 你有有效勢, 有 SSB, 有 vacuum energy.
   呢個我識。你嘅 283.0821 vs −61.5 嘅關係係咩?」
→ 待答: 283.0821 係「全譜」修正 (O62), −61.5 係「凝聚」部分
```

---

## 2. 粒子質量生成 (O54, 最大翻譯挑戰)

```
IDCM claim: m_e = M₀γ₁, m_μ = M₀γ₇·15.5, m_τ = M₀γ₂₀·37

場論學家: 「質量喺 QFT 係 Yukawa/Higgs 產生!
  你嘅 γ_k 係 ring 上嘅模式頻率, 點解等於粒子質量?」

IDCM 翻譯:
  γ_k 唔係「模式頻率」— 係「自能修正嘅動量依賴」
  → 粒子質量 = 自由場質量 + Σ(p) (自能)
  → IDCM: Σ(p) 由 K_Chain 模式結構決定
  → m_e = m_0 + Σ(pₑ), Σ 由 γ₁ 模主導
  → 冇 Higgs 粒子, 但有「幾何質量生成」
  → 場論學家: 「有趣, 但你要證明 Σ(p) 完整計算,
     唔係貼 γ_k 標籤」
  🔴 未完成: 冇完整 1-loop 自能計算
  🟡 有 O36 (質量生成 = 二階自能) 部分
```

---

## 3. Path integral / Correlator (Q4/Q5 缺口)

```
現有: γ_k 譜 (dispersion) — 場論學家識
缺:   ⟨φ(x)φ(y)⟩ correlator — 未定義

橋 (CMB):
  C_ℓ = ⟨a_ℓm a*_ℓm⟩ = ∫d²Ω₁d²Ω₂ Y*_ℓm(Ω₁)Y_ℓm(Ω₂)⟨δT(Ω₁)δT(Ω₂)⟩
  IDCM: ⟨δT(Ω₁)δT(Ω₂)⟩ 由 γ_k 譜 + K_Tree 階梯決定
  → cmb_cl/ 有 C_ℓ 閉合 (ℓ_m = 44(M−C(9−m,2))+frac), 但未由
    Lagrangian 推導
  🔴 未完成: correlator 未定義, C_ℓ 係「拼湊」唔係推導
```

---

## 4. 對稱群 (Q6 缺口)

```
現有: S¹ (ring translation), Z₂ (奇偶), SU(12) (O59)
問題: SU(12) 係 global 定 gauge? 冇 gauge boson 定義

SM 連結 (O54/O56/O59):
  SU(12) ⊃ SU(3)×SU(2)×U(1)?
  → 未有完整 breaking chain
  → 場論學家: 「你要 show 12 → 3×2×1 嘅 breaking,
     同埋 gauge boson 質量 (Higgs 機制)」

🔴 未完成: gauge 結構未建立
🟡 有 CKM/PMNS 閉合 (O54), 但係「結構」唔係「gauge 推導」
```

---

## 5. 同 GR 嘅 coupling (Q10 致命缺口)

```
IDCM claim: 冇膨脹, 冇暗能量, 冇暗物質

場論學家: 「你嘅 spacetime 係咩? FLRW 係 approximation?
  你嘅 metric 喺邊?」

IDCM 翻譯 (O73):
  H₀ 唔係膨脹率 — 係世界環角頻率 ω_ring = c/R_world
  z 紅移 — 未翻譯 (最難缺口!)
  FLRW 度規 — 只係「環幾何」嘅投影?

🔴 致命: 冇 IDCM × GR coupling
🔴 致命: z 紅移未有場論翻譯
🟡 O73: CMB 67.36 = ω_ring×(1−π/44) — 投影閉合 (但機制 O74)
```

---

## 6. 場論學家會點睇 (誠實總結)

```
認得嘅 (🟢):
  ✓ Lattice scalar field (tight-binding)
  ✓ SSB 勢 V(W) = −μ²|W|²+λ|W|⁴ (Mexican hat)
  ✓ 真空能計算 (Σγ/2 = 45)
  ✓ Sine-Gordon 框架 (soliton)

質疑嘅 (🔴):
  ✗ 點解 44 site? 點解 R_world 半徑?
  ✗ 質量 = 模式頻率 (冇完整自能計算)
  ✗ 冇 path integral / correlator
  ✗ SU(12) 冇 gauge 結構
  ✗ 冇 SM × IDCM × GR 耦合 Lagrangian
  ✗ z 紅移冇翻譯
  ✗ 1496 複合模式冇物理

結論:
  → IDCM 唔係「冇 Lagrangian」— 有 O39 SSB 核心!
  → 但「數字閉合 → 物理」嘅橋未建好
  → 場論學家會話: 「你有一個有意思嘅 toy model,
     但未係完整物理 — 除非你推導出 C_ℓ, 質量譜,
     z(z) 由同一個 Lagrangian」
```

---

## 7. 行動清單 (令場論學家開始認同)

```
1. ★ 完整 1-loop 自能計算: 質量譜 (O54) 由 L_free+L_cond 推導
   → 唔係貼 γ_k, 係算 Σ(p)
2. ★ 定義 correlator: ⟨φφ⟩ ↔ C_ℓ (CMB) — 由 Lagrangian 推導
3. SU(12) → SM breaking chain (gauge boson 質量)
4. z 紅移翻譯 (最難) — 冇膨脹點出 redshift
5. V_Λ 統一: −61.5 (凝聚) + 283.0821 (全譜) 同一個框架
6. 1496 模式物理 (或者放棄佢)
```

## 8. 記錄

- O39 docs/01 — SSB 勢完整推導 (110/110 PASS)
- O62 — V_Λ = 283.0821
- O54 — SM 質量閉合
- O36 — 質量生成 = 二階自能
- 本文件 — 場論學家友好翻譯初版
