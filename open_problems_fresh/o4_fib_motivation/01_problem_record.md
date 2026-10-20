# O4: Fibonacci 等級模型物理動機 — 點解 F₃/F₄/F₅ ladder?

> **狀態**: 🔴🔴 **核心觀測推導統計上唔成立 (2026-08-17 深夜發現)** — 數學閉合 ✅ + 觀測未證實 ❌
> **致命發現**: `06_fatal_finding.md` — 節點級 BIC constant-mean (33.5) 贏 φ^-d (34.8); ANOVA 層間唔顯著; Spearman 距離相關唔顯著
> **數學閉合仍有效**: λ₂ = φ⁻², ω₂ = φ⁻¹, A₅ 特徵標 χ₃(5A)=φ (群論/圖論事實, 不受影響)

## 問題陳述

SMICA 驗證發現: 節點振幅唔係 uniform (全部 F₅), 而係近似 Fibonacci ladder (F₃/F₄/F₅ by BFS 距離)。6level 模型 χ²=1.31 最佳。但**點解係 Fibonacci? 點解 F₃=2, F₄=3, F₅=5? 點解按 BFS 距離? 點解 3 級?** — 未有物理推導。

## ⚠️ 致命發現 (2026-08-17 深夜, 獨立節點級統計)

**「Fibonacci 等級 = 距離衰減」喺節點級統計上唔成立:**

| 測試 | 結果 | 結論 |
|:-----|:-----|:-----|
| BIC constant-mean vs φ^-d | **33.5 vs 34.8** | constant 贏! 距離模型冇優勢 |
| ANOVA 層間差異 | p=0.071-0.112 | 唔顯著 |
| Spearman 距離相關 | p=0.085-0.158 | 唔顯著 |
| λ₂ 模投影 | 0.08-0.10 (期望 0.129) | 唔顯著 |
| 05_synthesis BIC | 遺漏 constant-mean 模型 | 「continuous 勝出」係錯 |

**問題根源**: 4.17° 平滑 (26° 節點間距 vs 平滑半徑) 製造虛假距離梯度 + 層均擬合掩蓋層內巨大 variance + d=0/d=1 小樣本。

## 核心答案 (數學閉合, 仍然有效)

| 問題 | 答案 | 閉合精度 |
|:-----|:-----|:---------|
| 點解 Fibonacci? | **A₅ 群論內建 φ**: 5-fold 旋轉幾何綁定 φ (cos72°=(φ-1)/2, χ₃(5A)=φ) | 精確 |
| 點解按 BFS 距離? | **A₅ Cayley 圖譜 λ₂ = φ⁻²** → 波主模 ω₂ = √λ₂ = φ⁻¹ | 8e-16 |
| 點解 3 級? | ε³ 截斷 = 2+1 = data+inversion | 結構閉合 |
| 冷斑閉合 | **A = 5ε⁵/8 × T_cmb = 150 μK = F₅**; RMS = ε⁵/8 × T_cmb = 30 μK | 0.1% |
| 冷斑觀測 | -134.2 μK @ SMICA 4.17°, rank 1/60 | 11.8% (振幅) |

**關鍵數值 (獨立重算確認, 見 o4_renew/G01):**
- λ₂ = 0.381966011250 = φ⁻² (偏差 8.33e-16, 多重度 3)
- ω₂ = √λ₂ = 0.618033988750 = φ⁻¹ (偏差 6.66e-16)
- 冷斑 (node 0): -134.2 μK @ SMICA 4.17° 平滑, rank 1/60 (最極端)
- A = 5ε⁵/8 × T_cmb = 150.00 μK = F₅ (RMS = ε⁵/8 × T_cmb = 30.00 μK)

⚠️ 但「呢啲數學結構係咪控制節點觀測溫度」**未有統計支持** (見致命發現)

## 統計判決 (修正後)

**節點級完整 BIC (含 constant-mean):**

| 模型 | χ² | BIC |
|:-----|:---:|:---:|
| **constant-mean (k=1)** | **29.4** | **33.5** ← 最優 |
| φ^-d 自由A (A*=115) | 30.7 | 34.8 |
| φ^-d A=150 固定 | 33.5 | 37.6 |
| 3lv | 51.4 | 63.7 |

→ **節點振幅同 BFS 距離冇統計上顯著關係**

## 五個候選機制判決 (修正後)

| # | 機制 | 判決 |
|:-:|:-----|:----:|
| 1 | BFS 距離衰減 A(d)=F₅·φ^(-d) | 🔴 **統計唔成立** (constant 贏) |
| 2 | 干涉級數 (word length) | 🔴 冇獨立支持 |
| 3 | K_Chain γ_n 組合 | 🔴 否定 |
| 4 | 拓撲位錯 k(i) | 🟡 輔助 (唔受影響) |
| 5 | ε³ 截斷 | 🟡 結構上有效 (3=2+1) 但觀測連接未證實 |

## 驗證 (數學部分)

- 最終雙重驗證: **21/21 通過** (`scripts/12_final_verify.py`) — 全部係數學/結構性質
- Vertex-transitive: 60/60 節點 BFS profile 一樣
- 旋轉不變: 20 次隨機旋轉 λ₂ std = 0
- 對照組: 隨機 60 點圖 λ₂ ≈ 0 (λ₂=φ⁻² 係 A₅ 結構性稀有)
- **完整測試 (無 timeout)**: 14/14 PASS (`run_all_full.sh`, v3)
- **⚠️ 無幻覺交叉驗證 20/20 只驗數學宣稱, 冇驗「距離衰減」統計宣稱**

## 推導時序索引 (Derivation Timeline Index)

> 每條: 時序 → script → data 輸出 → 結果。時序由底向上 (最早→最新)。
> 完整核對: o4_renew/G01 (獨立重算) + G02 (文檔核對 39/39)。

| # | 時序 | 步驟 | Script | 輸出 | 結果 |
|:-:|:----:|:------|:-------|:-----|:-----|
| 1 | 08-17 03:46 | BFS 距離層 fit | 01_bfs_fit.py | bfs_fit.txt | ✅ 層分佈 |
| 2 | 08-17 03:55 | 群論字群 (word group) | 02_group_word.py | group_word.txt | ✅ 5 irrep 類 |
| 3 | 08-17 03:56 | K_Chain 關聯 | 03_kchain.py | kchain.txt | ✅ 否定 |
| 4 | 08-17 03:56 | 阻挫計算 | 04_frustration.py | frustration.txt | ✅ 32 |
| 5 | 08-17 03:59 | 綜合分析 (BIC) | 05_synthesis.py | synthesis.txt | ⚠️ 遺漏 constant |
| 6 | 08-17 04:01 | 機制 5 判決 | 06_mechanism5.py | mechanism5.txt | ✅ |
| 7 | 08-17 04:05 | 數學驗證 | 07_verify.py | verification.txt | ✅ 21/21 |
| 8 | 08-17 04:07 | 波衰減 | 08_wave_decay.py | wave_decay.txt | ✅ |
| 9 | 08-17 04:08 | 譜計算 | 09_spectrum.py | spectrum.txt | ✅ |
| 10 | 08-17 04:10 | 譜閉合 λ₂=φ⁻² | 10_spectrum_closure.py | spectrum_closure.txt | ✅ 8e-16 |
| 11 | 08-17 04:27 | vertex-transitive | 11_vertex_transitive.py | vertex_transitive.txt | ✅ 60/60 |
| 12 | 08-17 04:29 | 最終雙重驗證 | 12_final_verify.py | final_verification.txt | ✅ 21/21 |
| 13 | 08-17 10:27 | 開放問題量化 | 13_open_issues.py | open_issues.txt | ✅ |
| 14 | 08-17 12:07 | d=1 層分析 (修正版) | 14_d1_layer.py | d1_layer.txt | ✅ 0.344 |
| 15 | 08-17 12:31 | 無幻覺交叉驗證 | 15_claim_verification.py | claim_verification.txt | ✅ 20/20 數學 |
| 16 | 08-17 13:02 | 衰減率獨立檢查 | 16_decay_rate_check.py | decay_rate_check.txt | 🔴 唔穩定 |
| 17 | 08-17 13:07 | Laplacian 模態檢查 | 17_laplacian_mode_check.py | laplacian_mode_check.txt | 🔴 投影唔顯著 |
| 18 | 08-17 13:25 | 觀測結構掃描 | 18_obs_structure_scan.py | obs_structure_scan.txt | ✅ |
| 19 | 08-17 13:30 | 排除 node 0 控制 | 19_node0_control.py | node0_control.txt | 🔴 單點驅動 |
| 20 | 08-17 13:38 | 跨地圖獨立驗證 | 20_cross_map_structure.py | cross_map_structure.txt | 🔴 SMICA 特定 |
| 21 | 08-17 13:51 | 高緯 ΔE=0 跨地圖 | 21_highlat_deltaE0_cross.py | highlat_deltaE0_cross.txt | ✅ 釐清 |
| 22 | 08-17 12:31 | 完整測試 runner | run_all_full.sh | full_test_results.txt | ✅ 14/14 PASS |
| 23 | 09-09 09:06 | 推導鏈核對 (o4_renew) | G01 | G01_o4_derivation.txt | ✅ 全閉合 |
| 24 | 09-09 09:09 | 文檔核對 (o4_renew) | G02 | G02_o4_docs.txt | ✅ 39/39 |

### 推導鏈 (驗證後)

```
0,1 → 2 bits → 2+1=3 → ε³ 截斷
→ A₅ 5-fold 幾何綁定 φ: cos72°=(φ-1)/2, cos36°=φ/2
→ ε = φ⁻¹/4 = 0.1545084972
→ A₅ 特徵標: Σdim²=60, χ₃(5A)=φ, χ₃(5B)=1-φ, ⟨χ₃,χ₃⟩=1
→ A₅ Cayley 圖譜: λ₂ = φ⁻² = 0.381966011250 (8.33e-16, 多重度 3)
→ 波主模: ω₂ = √λ₂ = φ⁻¹ = 0.618033988750 (6.66e-16)
→ RMS = ε⁵/8 × T_cmb = 30.00 μK; A = 5ε⁵/8 × T_cmb = 150.00 μK = F₅
→ 冷斑觀測: -134.2 μK @ SMICA 4.17° (rank 1/60, 偏差 11.8%)
→ [斷裂] 每 hop 衰減 φ⁻¹ → A(d) = F₅·φ^(-d) ← BIC constant 33.5 贏 34.8, 觀測唔支持
```

## 檔案

```text
01_problem_record.md      # 本文件 (問題 + 狀態)
03_complete_record.md     # 完整閉合記錄 (數學部分)
04_open_issues.md         # 開放問題盤點
05_full_test_record.md    # 完整測試記錄
06_fatal_finding.md       # ← 致命發現 (最重要)
SESSION_START.md          # session 啟動文件
scripts/01-17             # 17 個分析腳本
run_all_full.sh           # 完整測試 runner
data/*.txt                # 18 個數據輸出
```
