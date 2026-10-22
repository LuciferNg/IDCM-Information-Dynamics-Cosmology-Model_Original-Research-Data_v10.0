# O82 — docs/04: SM Higgs vs IDCM 質量生成比較 (R5c)

> **日期**: 2026-08-26
> **狀態**: 🟢 **已閉合** — 16/16 PASS
> **腳本**: scripts/05_higgs_comparison.py

---

## 一、機制對照

| 概念 | SM Higgs | IDCM W-field |
|:----|:---------|:-------------|
| 場類型 | Complex doublet | Real scalar (物理層) |
| 對稱性 | SU(2)_L × U(1)_Y | S¹ × Z₂ × U(1)_W (global) |
| SSB 參數 μ² | μ²_H > 0 (自由) | μ² = 2 = Σγ_even−Σγ_odd |
| 四次耦合 λ | λ_H (自由) | λ = 2/123 = 2/[3(N_d−dim_ℂ)] |
| VEV | v = 246 GeV | ⟨W⟩² = 61.5 (無量綱) |
| 尺度 | v/√2 = 174 GeV | a = M₀/√61.5 = 3.5578 MeV |
| 質量公式 | m_f = y_f·v/√2 | m_n = κ²·ω_n = M₀·sin(ratio) |
| 耦合參數 | y_f (自由, 3代) | κ² = M₀ (結構閉合) |
| Yukawa-like | y_f·ψ̄_L·H·ψ_R | g_n = κ·ω_n (耦合 ∝ 頻率) |
| 質量階層 | 任意 (y_f 自由) | 結構決定 (sin 比值 × φ 階梯) |
| Higgs 粒子 | m_H = 125 GeV | 冇 (凝聚場, 冇 propagation) |
| Unitarity | ~1.2 TeV 救場 | ~55.8 MeV 天然 cutoff |
| 截止 | 冇 (continuum) | 88-site lattice (物理) |

## 二、共同點

1. **Mexican hat 勢**: V(φ) = −μ²|φ|² + λ|φ|⁴ — 場論學家識
2. **SSB**: ⟨φ⟩ ≠ 0 → 質量生成
3. **質量 ∝ 耦合 × VEV**: 結構類似

## 三、關鍵差異

1. **冇 Higgs particle**: W 係凝聚場, 唔係 propagation scalar
2. **1-loop vs tree-level**: IDCM 質量 = 二階微擾自能, SM = tree-level Yukawa
3. **尺度不同**: M₀ = 27.9 MeV vs v = 246 GeV
4. **耦合結構**: g_n = κ·ω_n 係結構決定, y_f 係自由參數

## 四、等效性定理

喺低能極限 (ω_n ≪ m_W), IDCM 質量生成 = SM Higgs 質量生成:

| SM | IDCM | 對應 |
|:---|:-----|:-----|
| m_f = y_f·v/√2 | m_n = (g²/m_W²)·ω_n | 耦合²/重場質量² × 模態頻率 |
| y_f (free) | κ² = g²/m_W² (structural) | 有效耦合 |
| v/√2 (VEV) | ω_n (mode frequency) | 標度參數 |

**結論:** IDCM 質量生成 = SM Higgs 機制嘅推廣 (零自由參數版本)

## 五、IDCM 優勢

1. **零自由參數質量預言** (SM 需要 5+)
2. **質量階層自然解釋** (sin 比值 × φ 階梯)
3. **真空能計算** (SM 冇預言)
4. **天然 cutoff → 冇 hierarchy problem**

## 六、誠實差異

| 差異 | 嚴重性 | 處理 |
|:----|:------:|:-----|
| 冇 Higgs particle | 🔴 最大 | 天然 cutoff 避免 unitarity 問題 |
| 1-loop vs tree-level | 🟡 | 低能有效理論等效 |
| 尺度不同 (27.9 MeV vs 246 GeV) | 🔴 | O85 SU(12) → SM breaking |
| 耦合結構不同 | 🟢 | 優勢: 零自由參數 |