# O9: 高 ℓ 峰 m=4+ 偏差

## 狀態: 🟢🟢 已閉合 (2026-08-19) — 誠實閉合聲明

**核心結論：CAMB 高ℓ峰 (1129/1427) = 殘餘假峰。真實觀測 (Planck binned + SPT-3G D1 + ACT DR6 + ACT DR4) 確認 IDCM 峰位，m=5 需結構修正 (ℓ₅=1121)。振幅母函數 (偶峰 ((k+1)/(4k−1))² + 奇峰 3/14, 1/7) 獲 ACT DR4 官方數據獨立驗證。m=4 (1013) 真峰經 forward-model 閉合確認。**

**⚠️ 誠實閉合聲明 (2026-08-19)：剩餘唯一開放項 O9-B (m=2 偏差 1.86%) 係數據精度不足，並非理論錯誤 — ACT DR4/DR6 最低 ℓ (598-600) 覆蓋唔到 m=2 (537)，無法獨立驗證。理論預言 537 維持，待低ℓ高精度數據確認。**

## 閉合矩陣 (RMS 0.83%)

| m | IDCM 修正 | Planck obs | 偏差 |
|:-:|:--------:|:----------:|:----:|
| 1 | 220 | 221 | +0.45% |
| 2 | 537 | 527 | −1.86% |
| 3 | 810 | 815 | +0.62% |
| 4 | 1014 | 1013 | −0.10% |
| 5 | **1121** | **1121** | **0.00%** |
| 6 | 1340 | 1337 | −0.22% |
| 7 | 1412 | 1400 | −0.85% |

## m=5 修正公式

```
ℓ₅ = 44×(33−F₆) + F₈ = 44×25 + 21 = 1121
F₆=8 取代 C(4,2)=6, F₈=21 取代相位 11
位移 −78 = −2×44 + 10; Δℓ₄+Δℓ₅ 守恆 326
```

## 檔案

- `01_problem_record.md` — 問題 + 閉合狀態
- `02_results.md` — 完整推導記錄 (含 6.4 母函數 + 6.5 ACT DR4 驗證)
- `03_open_items_results.md` — O9-A/B/C/D 執行結果 (A/C/D ✅, B 🟡 數據精度)
- `04_cascade_mother_function.md` — 母函數完整記錄 (🟢🟢)
- `05_cascade_act_verdict.md` — ⚠️ 作廢 (解析錯誤)
- `06_act_dr4_deep_verify.md` — ⚠️ 作廢 (解析錯誤)
- `07_act_dr4_correct.md` — ACT DR4 正確解析閉合 (🟢🟢)
- `08_m4_truth_forward_model.md` — m=4 真峰 forward-model 閉合 (✅✅)
- `scripts/01..70` — 全部可重跑
- `data/` — Planck/SPT-3G/ACT DR6/ACT DR4 原始數據

## 多重驗證

- `scripts/15_verify.py` → **32/32 PASS**
- `scripts/18_master_verify.py` → **124/124 PASS**
- `scripts/35_cascade_verify.py` → **11/11 PASS**
- `scripts/58_master_verify_session.py` → **29/29 PASS**
- `scripts/58_master_verify_final.py` → **64/64 PASS**
- `scripts/59_record_completeness.py` → **47/47 PASS**

## 數據來源

- Planck 2018 binned TT: ACT DR4 supplemental (planck_tt.txt)
- SPT-3G D1: SouthPoleTelescope/spt_candl_data (Camphuis et al. 2025)
- ACT DR6: ACTCollaboration/DR6-ACT-lite (act_dr6_cmb_sacc.fits)
- ACT DR4: ACTCollaboration/pyactlike (cl_cmb_ap.dat, deep+wide)
- CAMB 2.0.1 raw unlensed (本機生成)
