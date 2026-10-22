# O82 — docs/02: Renormalization Framework (R5a)

> **日期**: 2026-08-26
> **狀態**: 🟢 **已閉合** — 13/13 PASS
> **腳本**: scripts/03_renormalization.py

---

## 一、核心論證

IDCM 嘅 renormalization 框架與標準 QFT 有本質不同：

| 項目 | 標準 QFT | IDCM |
|:----|:---------|:-----|
| UV cutoff | Regulator (a→0) | 物理邊界 (88-site lattice) |
| UV 發散 | 有 (需要 renormalization) | 冇 (有限譜) |
| Continuum limit | 必要 | 唔存在 |
| RGE running | 有 (scale-dependent) | 冇 (參數係物理常數) |
| Renormalization | 必需 | 唔需要 (但可做 for completeness) |

## 二、天然 UV cutoff

**88-site 對偶鏈 = 物理 cutoff, 唔係 regulator:**

- 模式數: k = 1..44 (正頻率)
- 最高頻: ω₄₄ = 2 (Nyquist)
- 最短波長: λ_min = 2a = R_world/44 = 93.86 Mpc
- Lattice spacing: a = R_world/88 = 46.93 Mpc

**後果:**
- 冇 UV 發散: 所有 loop 積分變為有限和
- 冇需要 renormalization (finite QFT)
- 冇 continuum limit → 冇 RGE running

## 三、Counterterms (for completeness)

即使唔需要, 場論學家想睇:

```
L_bare = (1/2)(∂_μW_A)² − μ²|W_A|² + λ|W_A|⁴ + Σ_n κ·ω_n·W_A·φ_n²

L_ren = L_bare + δ_Z(∂_μW_A)² + δ_μ|W_A|² + δ_λ|W_A|⁴ + Σ_n δ_κ·ω_n·W_A·φ_n²

On-shell conditions:
  Σ_R(p² = ω_n²) = 0       (pole = physical mass)
  ∂Σ_R/∂p² |_{p²=ω_n²} = 0 (residue = 1)
```

## 四、Scheme Independence

**★★★ 核心論證: ΔE_n ∝ ω_n 係 renormalization scheme independent ★★★**

1. **耦合結構**: g_n = κ·ω_n (耦合 ∝ 模態頻率) — 結構性質, 唔係 loop 計算結果
2. **二階微擾**: ΔE_n = −g_n²/ω_n (教科書標準結果) — leading order exact
3. **Renormalization 只會**: 吸收數值因子到 κ_R, 唔改 ω_n 譜形

## 五、RGE

IDCM 係 finite QFT (有限譜):
- 冇 continuum limit → 冇必要做 RGE
- 參數 μ², λ, κ 係物理常數, 唔係 scale-dependent
- β_λ 同 β_κ 冇意義 (因為冇 running)

## 六、O88 關聯

O88 (46/46 PASS) 已驗證 anomaly-free:
- SU(12)³ anomaly = 0 (3×(12⊕12̄) 組合)
- Anomaly 係 topological — 即使 finite QFT 仍然有意義

## 七、誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| UV cutoff = 88-site lattice (物理) | 🟢 |
| 冇 UV 發散 (有限譜) | 🟢 |
| Counterterms 定義完整 | 🟢 |
| On-shell renormalization conditions | 🟢 |
| ΔE_n ∝ ω_n scheme independent | 🟢 |
| RGE: 冇 running (finite QFT) | 🟢 |
| O88 anomaly-free 關聯 | 🟢 |
| 場論學家可能會覺得 finite QFT 太特殊 | 🟡 |