# O101 — 問題記錄: 1+11 譜物理意義

> **日期**: 2026-08-28
> **狀態**: 🔴 **已註冊 — 待攻堅 (O110 缺口 #2)**
> **前置**: O59 (SU(12) 結構), O96 (SU(12) origin), O85 (SU(12)→SM breaking)
> **定位**: SU(12) fundamental 12 = 1 ⊕ 11 嘅物理意義

## 一、問題

SU(12) fundamental 12 = B×N_gen = 4×3 已閉合 (O59 41/41)，但 12 喺 Cartan subalgebra 下嘅 **1+11 分解**嘅物理意義未推導:

```
12 = 1 ⊕ 11
  ↑    ↑    ↑
fund  Cartan 其餘 11 維
      單態
```

## 二、已知結構

| 量 | 值 | 來源 |
|:---|:--:|:-----|
| 12 = L₅+1 | 11+1 | O59 |
| SU(12) rank | 11 | 12-1 |
| 12 = B×N_gen | 4×3 | O59, O96 |
| 66 = Λ²(12) | (6,6)⊕(10,3̄)=36+30 | O59 |
| 1+11 | 🔴 未推導 | O101 |
| SU(12)→SM | 4-step chain, 18/18 | O85 |

## 三、攻擊路線

### 路線 A: 群論 — 12 = 1 ⊕ 11 下 SU(12)

**問題**: 12 嘅 1+11 係 Cartan 分解定係 SU(12) → SU(11)×U(1) 分支?

a) **Cartan 分解**: 12 個 weight vectors, 1 個零權重 + 11 個非零權重
   - 1 = U(1) 方向 (overall phase)
   - 11 = 11 個 Cartan generator 方向
   - 物理: 1 = Higgs? 11 = gauge bosons?

b) **SU(12)→SU(11)×U(1) 分支**: 12 → 1_q ⊕ 11_q'
   - 1 = SU(11) 單態 (可能 right-handed neutrino / Higgs)
   - 11 = SU(11) fundamental
   - 但 SU(12)→SU(11) 唔係 O85 嘅 breaking chain

### 路線 B: 12 = B×N_gen = 4×3 分解

```
12 = 4 × 3
  ↑     ↑
  B   N_gen (K_Tree 分支因子)
```

12 嘅 1+11 可能係:
- 1 = B=4 嘅某個投影? 或 Cartan 方向?
- 11 = 3×3+2? 唔乾淨

### 路線 C: 66 = Λ²(12) fermion 對應 (O109 橋接)

66 = (6,6)⊕(10,3̄) = 36+30
- 6 = ? 6 = L₄? 6 = F₅? 6 = Σγ_odd/Σγ_even? 唔係
- 10 = F₅? 10 = L₅-1? 10 = B²+...?
- 3̄ = 3 = N_gen (世代)

66 之下嘅 1+11 分解: Λ²(1⊕11) = Λ²(1) ⊕ 1⊗11 ⊕ Λ²(11)
= 0 ⊕ 11 ⊕ Λ²(11)
= 11 ⊕ Λ²(11)

Λ²(11) = 55 = C(11,2). So 66 = 11 ⊕ 55 = 11 ⊕ C(11,2).

呢個分解下:
- 11 = 1⊗11 (fundamental 嘅 1 同 11 嘅反對稱積)
- 55 = Λ²(11) (11 嘅反對稱平方)

物理意義:
- 11 = SU(12) 嘅 Cartan generators? 或 gauge bosons?
- 55 = 剩餘 55 個 generators of SU(12)? No, SU(12) has 143 generators.

Actually, for the adjoint representation 143:
143 = 12²-1 = 143 = 11 (Cartan) + 132 (roots)
And 132 = 2×66 = 2×Λ²(12)?
No, 132 = 2×66 = 2×Λ²(12) = 2×C(12,2) = 2×66 = 132. Yes!
So the adjoint 143 = 11 ⊕ 2×66 = 11 ⊕ 132.

This means: 66 = Λ²(12) is HALF of the roots. This is the key!
- 66 = positive roots (or negative roots)
- 11 = Cartan generators
- 143 = 11 + 66 + 66 (Cartan + positive roots + negative roots)

So 1+11 in the fundamental 12 is related to the Cartan decomposition of the adjoint:
- 1 (in fundamental) ↔ 11 (Cartan generators in adjoint)? No, different representations.

Let me be more precise:

Under the Cartan subalgebra U(1)¹¹:
- 12 → 1₀ ⊕ 11_{weights} (one zero-weight and 11 non-zero weights of the fundamental)
- 143 → 11₀ ⊕ 66_{positive roots} ⊕ 66_{negative roots}

The 1 in 12 = 1⊕11 is the "zero-weight" direction. In the context of SU(12)→SM breaking, this zero-weight direction could correspond to the U(1) that gets a VEV (the Higgs direction).

The 11 in 12 = 1⊕11 are the 11 non-zero weights. These correspond to the 11 Cartan directions of SU(12).

## 四、攻擊腳本

scripts/01_analyze_1plus11.py:
1. 群論: SU(12) Cartan decomposition
2. 12 = 1⊕11 下 66 = Λ²(12) 分解
3. 與 O85 breaking chain 對接
4. 物理意義分配 (Higgs? Cartan? VL?)

## 五、狀態

| 項 | 狀態 |
|:---|:----:|
| SU(12) Cartan 分解 | 🔴 |
| 12 = 1⊕11 群論結構 | 🔴 |
| 66 = Λ²(12) 下 1+11 | 🔴 |
| 與 O85 breaking 對接 | 🔴 |
| 1 = Higgs? 物理意義 | 🔴 |
| 11 = Cartan gauge bosons? | 🔴 |