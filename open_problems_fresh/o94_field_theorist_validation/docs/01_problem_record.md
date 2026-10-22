# O94 — 場論學家驗證: 1-loop 完整有限部分 + 已發表數據驗證

> **創建日期**: 2026-08-27
> **狀態**: 🔴 **已註冊 — 待攻堅 (另一 session)**
> **來源**: O72 可疑點 #9 (「O82 R5 係結構驗證, 唔係實驗驗證」)
> **前置**: O82 (R1-R5 全部完成), O80 (W-field Lagrangian, 85/85), O86 (SM×IDCM×GR, 34/34), O54 (SM 質量閉合), O36 (二階自能機制, 44/44)
> **定位**: 用方案 A (完整 1-loop finite part 計算) + 方案 C (已發表 PDG 數據驗證) 填補 O82 R5 嘅「場論學家驗證」缺口 — 冇實驗室冇資助，只有計算機同已發表數據。
> **優先度**: ★★★

---

## 問題

O82 R5 完成咗場論學家翻譯框架 (Feynman 規則, 1-loop self-energy leading order, renormalization scheme, 10 問答, Higgs 比較)，但係：
- 方案 A 未做：完整 1-loop finite part 積分 (sympy analytic)
- 方案 C 未做：用已發表 PDG 數據直接驗證質量公式

場論學家會問：「你嘅 1-loop 計算有冇 finite correction? Ward identity 過唔過? 同 PDG 數據嘅偏差係幾多?」

## 攻擊路線

### 方案 A: 完整 1-loop finite part (★★★ 純計算, 零成本)

```
R1: 用 sympy 做 analytic 1-loop 積分 (in (1+1)D 或 dimensional regularization)
    Σ(p) = g² ∫ d²k/(2π)² D_W(k) D_φ(p−k)
    → 解析解 (finite part + log divergence)

R2: Leading order 驗證 (vs O82 scripts/01)
    Σ(p) → (g²/m_W²)·ω_n (同 O36 ΔE_n = −κ²·ω_n 一致)

R3: Finite correction 計算
    δm_n = Σ(pole) − m_n (leading order)
    → 如果 δm_n ≪ m_n → 1-loop 自能係 reliable

R4: Ward identity 檢查
    Gauge invariance of the self-energy
```

### 方案 C: 已發表數據驗證 (★★ 最快, 半日)

```
R5: 收集 PDG 質量數據
    m_e = 0.510998950 ± 0.000000015 MeV
    m_μ = 105.6583755 ± 0.0000023 MeV
    m_τ = 1776.86 ± 0.12 MeV

R6: 對照 O54 質量公式
    m_e = M₀γ₁ → dev?
    m_μ = M₀γ₇·15.5 → dev?
    m_τ = M₀γ₂₀·37 → dev?

R7: 統計分析
    χ²/dof, p-value
    → 如果 p > 0.05 → 質量公式同 PDG 數據一致
    → 證明 O82 翻譯唔係「結構驗證」亦係「實驗驗證」

R8: 撰寫 O94 closure record
    🟢 如果 A+C 全部 PASS
    → 可疑點 #9 填坑完成
    → O72 嘅 #9 缺口閉合
```

## 檔案結構

```
o94_field_theorist_validation/
├── docs/01_problem_record.md
├── SESSION_START.md
├── scripts/
│   ├── 01_finite_part.py      (R1-R3: 完整 1-loop finite part)
│   ├── 02_pdg_validation.py   (R5-R7: PDG 數據驗證)
│   └── 03_closure.py          (R8: 閉合記錄)
├── data/
│   └── pdg_masses.csv         (PDG 質量數據)
└── README.md
```

## 驗證標準

```
[1] ✅ 1-loop 解析積分完成 (sympy analytic)
[2] ✅ Leading order 同 O36 一致
[3] ✅ Finite correction δm_n ≪ m_n
[4] ✅ Ward identity 檢查通過
[5] ✅ PDG 質量對照 χ²/p-value
[6] ✅ 閉合判決: 🟢 如果 p > 0.05
```

## 狀態

```
🔴 已註冊 — 待攻堅 (另一 session)
```