# O122 — Feynman 規則從 W-field 晶格推導

> **創建日期**: 2026-08-29
> **狀態**: 🟢 **已閉合** (2026-09-03) — v9.0 驗證失效 → 重建離散 Feynman 規則, 47/47 PASS
> **來源**: v9.0 項目審計 — `open_problems_fresh/p_fr_feynman_rules/`
> **前置**: O80 (W-field Lagrangian) 🟢, O82 (質量生成) 🟢, O37 (Lagrangian) 🟢
> **定位**: 從 v9.0 p_fr_feynman_rules 遷移 — W-field 晶格嘅完整 Feynman 規則推導

---

## 一、問題

從 v9.0 p_fr_feynman_rules 遷移 — W-field 晶格嘅完整 Feynman 規則推導

## 二、前置驗證判決 (docs/02)

**v9.0 推導在 v10.0 中失效 — 需要重建 (非遷移)。**

| 衝突 | v9.0 | v10.0 已閉合 |
|:-----|:-----|:-------------|
| 連續極限 | N_d→∞ 必要 | 冇 continuum limit (88-site 物理 cutoff, O82) |
| 標度 | m_H = 123.11 GeV, a = 1/M_GUT | M₀ = 27.9 MeV, a = R_world/88 = 46.93 Mpc |
| 耦合 | κ = 1/16 (φ⁴ 頂點) | κ² = M₀ (三線性), λ = 2/123 (W⁴) |
| 場結構 | 單一 scalar φ⁴ | W × 44 模式 (L_int = Σ_n κω_n W φ_n²) |
| 動量守恆 | 連續 δ⁴(Σp) | 離散模式對角 mod 44 |

## 三、閉合內容 (docs/03 + scripts/01-03)

### 新推導: 離散 Feynman 規則 (基於 O80 Lagrangian)

```
L_W = ½(∂_μW_A)² − μ²|W_A|² + λ|W_A|⁴ + Σ_n κ·ω_n·W_A·φ_n²
     μ² = 2,  λ = 2/123,  κ² = M₀ = 27.9009 MeV,  ω_n = 2sin(nπ/88)
```

| 元素 | 規則 | 來源 |
|:-----|:-----|:-----|
| φ_n 傳播子 | i/(ω²−ω_n²+iε) | O80 Script 5 |
| h 傳播子 | i/(p²−m_h²+iε), m_h = M₀/2 = 13.95 MeV | O37 |
| h-φ² 頂點 | −i·κ·ω_n (模式對角) | O80 |
| 1-loop 自能 | Σ_n = −κ²ω_n = −m_n | O82/O94 |
| 2→2 散射 | M(s) = g_n·g_m/(s−m_h²) = M₀·ω_n·ω_m/(4m_n²−m_h²) | 本推導 |
| Unitarity | 全域上界 max\|a₀\| = 0.00274 (4,44); kinematically-allowed 真正上限 0.00039 (4,4), 全部 ≪ 0.5 | 本推導 |
| 模式守恆 | h 只耦合 φ_n φ_n (模式對角) | 本推導 |

### 驗證結果

| Script | 內容 | 結果 |
|:-------|:-----|:----:|
| 01_preverification.py | v9.0 衝突確認 | 14/14 PASS |
| 02_feynman_rules.py | 離散規則數值驗證 | 24/24 PASS |
| 03_cross_validation.py | 閉合審計 + O82/O94/O144 對照 | 9/9 PASS |
| **合計** | | **47/47 PASS** ✅ |

### 交叉驗證一致
- m_e/m_μ/m_τ (O82): 0.16% / 0.13% / 0.34% ✅
- m_W/m_Z, m_H/m_W (O144 模式選擇): 0.15% / 0.11% ✅
- O94 finite part = 0 (冇 UV 發散) ✅

## 四、誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| 離散 Feynman 規則 (傳播子+頂點+自能+散射) | 🟢 閉合 |
| 2→2 tree-level unitarity | 🟢 閉合 (全域上界 0.00274, kinematically-allowed 0.00039) |
| SSB h³/h⁴ 頂點定量 | 🟢 微積分精確 (L2 制 V'''=24λ⟨W⟩, V''''=24λ); L3 制 λ_eff 需標度變換 🟡 |
| SM 費曼規則 (fermion/gauge) | 🔴 → O85/O144 |
| 散射截面 vs 實驗 | 🔴 冇 PDG 散射數據 |

## 五、檔案結構

```
o122_feynman_rules_wfield/
├── SESSION_START.md              ← 🟢 已閉合
├── docs/
│   ├── 01_problem_record.md      ← 🟢 本文件
│   ├── 02_preverification.md     ← 🟢 v9.0 前置驗證
│   ├── 03_derivation.md          ← 🟢 離散 Feynman 規則推導
│   └── 04_audit.md               ← 🟢 獨立審計記錄
├── scripts/
│   ├── 01_preverification.py     (14/14 PASS)
│   ├── 02_feynman_rules.py       (24/24 PASS)
│   └── 03_cross_validation.py    (9/9 PASS)
└── data/
```
