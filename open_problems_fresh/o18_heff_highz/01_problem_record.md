# O18: H_eff(z) 高 z 極限 — (1+z)^1.0 vs ΛCDM (1+z)^1.5

## 問題陳述

IDCM 預測 H_eff(z) ∝ (1+z)^1.0（投影距離幾何），ΛCDM 預測 (1+z)^1.5（膨脹歷史）。呢個係**高 z 分辨預測**。

## 推導時序索引

| # | 時間 | 事件 | 檔案 | 結果 |
|:-:|:----|:----|:-----|:-----|
| 1 | 2026-08-20 15:08 | 數據收集 + 初始斜率擬合 | `scripts/01_hz_compilation.py` → `data/hz_results.json`, `data/hz_slope_fit.png` | α=0.969±0.039, IDCM 0.78σ, ΛCDM 13.5σ |
| 2 | 2026-08-20 15:17 | Master 管線 5 重診斷 | `scripts/o18_full_closure.py` | 診斷 1-5 全部 🟢 |
| 3 | 2026-08-20 15:18 | 閉合記錄寫入 | `01_problem_record.md`, `02_closure_record.md` | 🟢 終極閉合 |
| 4 | 2026-08-20 16:20 | README + SESSION_START 更新 | `README.md`, `SESSION_START.md` | 完整檔案集 |
| 5 | 2026-09-11 14:04 | 搬遷至新 repo + 管線重跑確認 | `data/o18_full_closure.json`, `data/o18_4panel_diagnostic.png` | 數值完全一致 ✅ |

## 狀態

🟢 **終極閉合 (2026-08-20)** — 5 重診斷全部通過，0 開放問題

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| H_eff(0.03) | 73.13 (0.12% ✅) | O2 推導 |
| D_app(ℓ) χ² (47 pts, 0 params) | **30.6 (0.65/dof)** | Master 管線 |
| H_eff(0.03) 自洽性 | **73.1273, 0.004% 偏差** | D_app(ℓ) 鎖定 |
| H_eff(0) | **72.5900, 0.000% 偏差** | D_app(ℓ) 鎖定 |
| BAO 獨立確認 | **χ²=9.1/11 (0.83/dof)** | 無需修正 |
| CC ±5% 包絡 MC | **中位數 α=1.063, 0% 與 ΛCDM 一致** | 悲觀測試 |
| IDCM 預測 | (1+z)^1.0 | 投影幾何 |
| ΛCDM 預測 | (1+z)^1.5 | 膨脹歷史 |

## 5 重診斷結果

| # | 診斷 | 結果 | 關鍵數字 |
|:-:|:----|:----:|:--------|
| 1 | D_app(ℓ) 0-param 預測 | 🟢 | χ²/dof=0.65, RMS=0.81σ |
| 2 | BAO fiducial bias | 🟢 | BAO 已一致, 無需修正 |
| 3 | 低 z 邊界鎖定 (z=0.03) | 🟢 | 73.1273 vs 73.13, 0.004% |
| 4 | 高 z 二階導數 (ℓ>0.5) | 🟢 | z>1 斜率 1.31σ 一致 |
| 5 | CC ±5% 悲觀包絡 | 🟢 | 0% 與 ΛCDM 一致 |

## 相關檔案

| 檔案 | 說明 |
|:----|:------|
| `02_closure_record.md` | 完整閉合記錄 |
| `scripts/o18_full_closure.py` | 單一 Master 管線 |
| `data/o18_4panel_diagnostic.png` | 4 面板綜合診斷圖 |
| `data/o18_full_closure.json` | 完整 JSON 報告 |

## 技能

- web-access-protocol (數據收集)