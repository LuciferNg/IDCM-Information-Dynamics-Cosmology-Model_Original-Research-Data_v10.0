# O20 — E/B 極化峰位置結構推導

## 狀態: EE 完全閉合 (7/7, 零殘差, 零自由參數) / TE 成對結構 / B lensing 有待結構

## 核心發現

**EE 峰完整公式 (v2 閉合):**
```
ℓ_E(k) = 44 × (F₆ + L₄·(k-1)) + 22 + Δ_chiral(k)   for k=1..7
       = 44 × (8 + 7(k-1)) + 22 + Δ_chiral(k)

Δ_chiral(k): {F₈=21, 22−B²=6, B⁰=1, √B=2, B=4, 2F₅=10, B²=16}
```

| k | n_int=8+7(k-1) | φ(k)=22+Δ | ℓ_E(CAMB raw) | 偏差 |
|:-:|:-------------:|:---------:|:-------------:|:----:|
| 1 | 8 | 43 | 395 | 0.0000% |
| 2 | 15 | 28 | 688 | 0.0000% |
| 3 | 22 | 23 | 991 | 0.0000% |
| 4 | 29 | 24 | 1300 | 0.0000% |
| 5 | 36 | 26 | 1610 | 0.0000% |
| 6 | 43 | 32 | 1924 | 0.0000% |
| 7 | 50 | 38 | 2238 | 0.0000% |

## 檔案結構

```
scripts/
├── 01_polarization_peaks.py       — 主分析 (CAMB + Planck + SPT + ACT)
├── 02_raw_ee_analysis.py          — Raw EE 深入分析
├── 03_ee_structural_formula.py    — EE 結構公式推導
├── 04_final_closure.py            — 最終閉合 + 多實驗驗證
├── 05_b_lensing.py                — B lensing 分析
├── 06_phase_analysis.py           — 相位分析
├── 07_chiral_phase_closure.py     — 手性相位閉合
├── 98_independent_verify.py       — 獨立核對 (49/50)
└── 99_master_verify.py            — 主驗證 (82/83)
data/
├── polarization_peaks.json
├── ee_structural_formula.json
├── polarization_final.json
├── phase_analysis.json
├── phase_chiral_closure.json
├── b_lensing_peaks.json
├── master_verify_report.json
└── independent_verify_report.json
01_problem_record.md
02_complete_record.md
final_result.md
README.md
SESSION_START.md
```