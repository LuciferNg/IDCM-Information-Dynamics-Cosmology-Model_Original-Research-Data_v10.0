# O12: ³He/H — 驗證記錄 (Verification Record)

## 驗證日期

2026-08-20 (session 內完整驗證)

## 驗證方法

**獨立 re-derivation:** 由文獻原始數字 + IDCM 基礎常數, 用全新 script (`scripts/02_verifier.py`) 重新推導所有結果 — 唔重用 `01_resolution_analysis.py`, 避免相同錯誤重複。

## 驗證項目 (14/14 PASS)

| # | 項目 | 計算值 | 期望值 | 狀態 |
|:-:|:-----|:-------|:-------|:----:|
| 1 | IDCM ³He/H = D/H×φ⁻² | 9.7592e-6 | 9.7592e-6 | ✅ |
| 2 | ΛCDM ³He/H | 1.04e-5 | 1.04e-5 | ✅ |
| 3 | 模型差距 % | 6.1612% | 6.1615% | ✅ |
| 4 | ³He/⁴He IDCM (Y_p 轉換) | 1.1736e-4 | 1.1736e-4 | ✅ |
| 5 | ³He/⁴He ΛCDM | 1.2799e-4 | 1.2799e-4 | ✅ |
| 6 | Cooke limit 誤差 % | 16.51% | 16.51% | ✅ |
| 7 | S209 誤差 % | 25.45% | 25.45% | ✅ |
| 8 | 需要 2σ 分辨誤差 | 3.08% | 3.08% | ✅ |
| 9 | IDCM vs Cooke limit σ | 0.63σ | 0.63σ | ✅ |
| 10 | ΛCDM vs Cooke limit σ | 0.28σ | 0.28σ | ✅ |
| 11 | IDCM vs S209 σ | 0.44σ | 0.44σ | ✅ |
| 12 | ΛCDM vs S209 σ | 0.21σ | 0.21σ | ✅ |
| 13 | IDCM vs SM 名義 σ | 4.9σ | 4.9σ | ✅ |
| 14 | 系統修正 σ (quadrature) | 2.46σ | 2.46σ | ✅ |

## 發現同修正

### 🔧 修正: 「~2.6σ」→「~2.5σ」(組合誤差法)

**問題:** 初始分析用「6.6% / (1.35% + 2.5%) = 1.71σ」(直接相加法) 同「~2.6σ」(粗略估計) 兩個值, 唔一致。

**獨立驗證發現:** 統計正確嘅組合誤差法 (quadrature) 係:

```
組合誤差 = √(SM_err² + sys_err²) = √(1.35² + 2.5²) = 2.84%
真實張力 = 6.6% / 2.84% = 2.46σ ≈ 2.5σ
```

**修正位置:**
- `02_results.md` line 46: 2.6σ → 2.5σ + 完整公式
- `01_problem_record.md` line 35: 2.6σ → 2.5σ
- `README.md` O12 行: 2.6σ → 2.5σ
- `scripts/02_verifier.py`: expected 2.6 → 2.46

**結論影響:** 無 — 2.5σ 同 2.6σ 都係「唔足以排除」, 🟡 狀態不變。

### 🔧 修正 2: 「0.7σ/0.3σ」→「0.63σ/0.28σ」(Cooke limit σ 精確值)

**問題:** 02_results.md 初始寫 IDCM vs Cooke limit = 0.7σ, ΛCDM = 0.3σ (四捨五入過度)。

**獨立驗證:** 精確計算 |9.7592e-6 − 1.09e-5| / 0.18e-5 = **0.6338σ**, |1.04e-5 − 1.09e-5| / 0.18e-5 = **0.2778σ**。

**修正位置:** `02_results.md` line 36 + line 50。

**結論影響:** 無 — 都係「1σ 內」, 🟡 狀態不變。

## 文獻數字來源確認

所有文獻數字直接摘自 Cooke 2022 全文 (browser console 提取), 非記憶:

| 數字 | 值 | 來源句 |
|:-----|:---|:-------|
| Orion ³He/⁴He | (1.77±0.13)×10⁻⁴ | "We measure a value 3He/4He = (1.77±0.13)×10⁻⁴" |
| SM (³He/⁴He)_p | (1.257±0.017)×10⁻⁴ | "assuming the Standard Model...(3He/4He)_p = (1.257±0.017)×10⁻⁴" |
| GCE fit | (1.043±0.089)×10⁻⁴ | "primordial helium isotope ratio is (3He/4He)_p = (1.043±0.089)×10⁻⁴" |
| Empirical limit | (³He/H)_p ≤ (1.09±0.18)×10⁻⁵ | "empirical limit on the primordial 3He abundance (3He/H)_p ≤ (1.09±0.18)×10⁻⁵" |
| S209 ³He/H | (1.10±0.28)×10⁻⁵ | "best available estimate...3He/H = (1.10±0.28)×10⁻⁵" |

## IDCM 基礎常數來源確認

| 常數 | 值 | 來源 |
|:-----|:---|:-----|
| D/H | 2.555×10⁻⁵ | bbn/06_complete_record.md T5 (閉合 1.12%) |
| Y_p | 0.2496 | bbn/06_complete_record.md T4 (閉合 1.77%) |
| φ⁻² | 0.3819660113 | (1+√5)/2 嘅平方倒數 |
| ³He/H 公式 | D/H × φ⁻² | bbn/scripts/07_he3_and_omegab.py 候選 |

## 一致性檢查

- [x] `01_resolution_analysis.py` 同 `02_verifier.py` 數值一致 (σ, %, 界限)
- [x] `02_results.md` 同 `01_problem_record.md` 數字一致
- [x] `README.md` O12 摘要同結果文檔一致
- [x] Citation ledger 5/5 文獻被引用, verify OK
- [x] 文獻數字全部有原文出處 (無幻覺)

## 最終狀態

**🟡 分辨唔到 — 兩模型 (IDCM 9.76e-6, ΛCDM 1.04e-5) 都 consistent with 觀測 (Cooke limit 1.09±0.18e-5)。**

*驗證: scripts/02_verifier.py*
*日期: 2026-08-20*

## 最終驗證總結 (2026-08-20 session 結束時)

| 檢查項 | 結果 |
|:-------|:----:|
| `01_resolution_analysis.py` 重跑 | ✅ exit 0 |
| `02_verifier.py` 獨立 re-derivation | ✅ 14/14 PASS |
| Citation ledger verify | ✅ 5/5 文獻被引用 |
| 文件數字一致性 (02_results ↔ 01_problem_record ↔ README) | ✅ |
| 修正 1 (2.6σ → 2.5σ) 已記錄 | ✅ |
| 修正 2 (0.7σ → 0.63σ, 0.3σ → 0.28σ) 已記錄 | ✅ |
| Memory 更新 (O12 🟡) | ✅ |

**本 session 所有推導、發現、計算、驗證已全部寫入記錄文檔:**
- `02_results.md` — 分辨力分析結果 (含全部文獻數字)
- `03_verification_record.md` — 獨立驗證 + 修正記錄 (本文件)
- `01_problem_record.md` — 問題狀態更新
- `README.md` — O12 加入活躍清單
- `scripts/01_resolution_analysis.py` + `scripts/02_verifier.py` — 可重跑驗證
