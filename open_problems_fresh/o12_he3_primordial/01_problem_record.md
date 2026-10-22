# O12: ³He/H primordial 觀測現狀（原 P5）

## 問題陳述

IDCM 預測 primordial ³He/H = D/H × φ⁻² = 9.76×10⁻⁶ (D/H = 2.555×10⁻⁵ 已閉合)。ΛCDM 標準預測 ~1.04×10⁻⁵。

**需要:** 2026 年為止 ³He/H 最好觀測約束 (DLA 吸收線、HII 區、Planetary Nebula)。

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| IDCM 預測 | 9.76×10⁻⁶ = D/H×φ⁻² | bbn 07 |
| ΛCDM 預測 | ~1.04×10⁻⁵ | 標準 |
| **觀測上限 (Cooke 2022)** | **(1.09±0.18)×10⁻⁵** | ApJ, arXiv:2203.11256 |
| S209 外銀河系量度 | (1.10±0.28)×10⁻⁵ | Balser & Bania 2018 |
| D/H | 2.555×10⁻⁵ | 已閉合 ✅ |

## 驗證路徑

| # | 路徑 | 方法 | 狀態 |
|:-:|:----|:-----|:----:|
| 1 | 文獻搜索 | 2026 最新 ³He/H 約束 (web) | ✅ |
| 2 | DLA 方法 | 高紅移 DLA ³He 測量 | 🟡 冇成功案例 |
| 3 | 分辨力 | IDCM 9.76e-6 vs ΛCDM 1.04e-5 vs 觀測 | ✅ 🟡 分辨唔到 |
| 4 | 結論 | 邊個模型被支持? | 🟡 兩者都兼容 |

## 分辨力結論 (2026-08-20)

**🟡 觀測分辨唔到 IDCM vs ΛCDM:**
- 模型差距 6.16% (9.76e-6 vs 1.04e-5)
- 觀測誤差 16.5% (Cooke limit 1σ) / 25.5% (S209 1σ)
- 需要 <3.1% 誤差先可以 2σ 分辨
- IDCM 同 ΛCDM 都喺 Cooke 2022 limit 1σ 內 ✅
- ³He/⁴He 名義張力: IDCM 4.9σ (vs SM, 未計系統誤差; 組合誤差法 ~2.5σ 真實) — 最弱測試
- Johnson 2025: 需 ~4 個新量度先達 30% 精度 → 2030s 末有望分辨

## 相關檔案

```
02_results.md          — 完整結果記錄
scripts/01_resolution_analysis.py — 分辨力分析
main_problems/p1_bbn/06_complete_record.md
```

## 推導時序索引 (2026-08-20)

| 步驟 | 時間 | 內容 | 文件/script | 狀態 |
|:-:|:-----|:-----|:-----------|:----:|
| S0 | 08-16 21:33 | SESSION_START 建立 (³He/H 任務定義) | SESSION_START.md | ✅ 原版未改 |
| S1 | 08-20 01:50 | 文獻搜索: Cooke 2022 / Johnson 2025 / Balser & Bania 2018 | scripts/01_resolution_analysis.py | ✅ |
| S2 | 08-20 01:50 | 分辨力分析 (模型差距 6.16%, Cooke 1σ 16.5%, S209 1σ 25.5%) | scripts/01_resolution_analysis.py → 02_results.md | ✅ |
| S3 | 08-20 01:51 | 01_problem_record 更新 (觀測約束 + 分辨力結論) | 01_problem_record.md | ✅ |
| S4 | 08-20 01:54 | 02_results.md 建立 (完整結果 + Sources) | 02_results.md | ✅ |
| S5 | 08-20 01:54 | README.md O12 加入活躍清單 | ../README.md | ✅ |
| S6 | 08-20 01:58 | 獨立驗證 re-derivation (02_verifier.py 14/14 PASS) | scripts/02_verifier.py | ✅ |
| S7 | 08-20 01:58 | 03_verification_record.md 建立 | 03_verification_record.md | ✅ |
| S8 | 08-20 02:00 | 修正 1: 系統張力 2.6σ → 2.5σ (組合誤差法) | 02_results / 01 / README | ✅ |
| S9 | 08-20 02:01 | 修正 2: Cooke σ 0.7σ→0.63σ, 0.3σ→0.28σ | 02_results.md | ✅ |
| S10 | 08-20 02:01 | 03_verification_record 最終驗證總結 | 03_verification_record.md | ✅ |
| S11 | 08-20 02:10 | 文檔交叉核對 23/23 PASS (只讀, 未修改文檔) | scripts/03_doc_crosscheck.py | ✅ |
| S12 | 08-20 02:15 | final_result.md 建立 (RESULT_TEMPLATE 格式) | final_result.md | ✅ |

**時序完整性:** SESSION_START (08-16) → 本 session 01→02→03 順序建立, 冇回溯污染。所有修正 (S8, S9) 記錄於 03_verification_record.md「發現同修正」, 冇改寫歷史。

## 技能

- web-access-protocol (核心) ✅ 已用
- grounded-citations (輔助) ✅ 已用 (ledger 5 文獻)
