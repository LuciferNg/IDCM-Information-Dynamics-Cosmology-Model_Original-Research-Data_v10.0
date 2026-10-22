# O27 結果: 節點 47 前景污染分析 — 🔴 判定為前景污染

> **日期**: 2026-08-21
> **狀態**: ✅ 完成 + 已驗證 (82/82 PASS)
> **判定**: 🔴 **前景污染** (多頻譜 veto)
> **驗證**: `scripts/09_full_verification.py` — 82 PASS / 0 FAIL (2026-08-21)

## 結論

**節點 47 (l=313.47°, b=-8.58°) 嘅 -135.7 μK (3.0° SMICA) 係銀河面塵埃前景污染, 唔係真實 CMB 冷結構。**

SMICA 喺銀河面低估前景殘留, 產生虛假冷信號。多頻譜測試 (100/143/217/353 GHz) 提供決定性證據。

---

## 證據矩陣

| 測試 | 結果 | 判定 | 權重 |
|:---|:---|:---:|:---:|
| ① 多尺度穩定性 | 10 尺度 rank 1-2/60 | 🟢🟢 | 3 |
| ② 三地圖一致性 | spread 9.7-10.0% (Commander 系統偏冷) | 🟡 | 2 |
| ③ 前景 mask | R3 CMB common mask **遮住** node47 | 🔴 | 3 |
| ④ 對徑反查 | 對徑 +16.3 μK 唔冷 | 🟢 | 2 |
| ⑤ Commander 偏差 | 低緯系統偏冷 -2.7 μK (p=0.0004) | 🟢 | 1 |
| ⑥ 多頻譜 | 143 GHz 唔冷 + 217 GHz 急升 (217/143=20.8) | 🔴 | 5 |

**最終判決: 🔴 前景污染** — 多頻譜測試係一票否決 (veto)。

---

## 詳細數據

### ① 多尺度穩定性 (SMICA, 全部 rank top-2)

| 尺度 | 0.5° | 1.0° | 1.5° | 2.0° | 3.0° | 4.17° | 5.0° | 7.0° | 10.0° |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| T47 (μK) | -249.6 | -211.6 | -174.4 | -153.8 | -135.7 | -123.4 | -116.3 | -102.1 | -86.1 |
| rank | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 1 | 2 |

**表面睇好穩定** — 但係多頻譜顯示呢個「穩定」係前景殘留嘅平滑尺度穩定性, 唔係 CMB 結構。

### ② 三地圖一致性 (3.0°)

| map | T47 (μK) | T0 冷斑 (μK) |
|:---|---:|---:|
| SMICA | -135.7 | -145.0 |
| NILC | -132.9 | -145.0 |
| Commander | -146.7 | -144.0 |
| spread | 9.95% | 0.67% |

- SMICA↔NILC 差只有 2.1% 🟢 — 兩個方法一致
- Commander 特別冷 (-146.7) — 但係低緯節點系統性偏冷 (t=-3.75, **p=0.0004**)
- 即係 Commander 差異係**系統效應**唔係 node47 特有

### ③ 前景 mask — 🔴 關鍵紅旗

| mask | node47 狀態 | 60 節點 |
|:---|:---|:---|
| R3 CMB common (Int) | **🔴 遮住** | 45/60 保留 |
| R2 IQU common | 保留 | 45/60 保留 |
| GalPlane apo0 | 遮住 (銀河面) | 10/60 保留 |

- node47 0.5°-5° 盤喺 R3 mask **全部 0% 保留**
- 官方 Planck R3 CMB common mask 認為呢個位置有前景風險

### ④ 對徑反查 — 🟢 (真結構必要條件, 但唔充分)

- 對徑 (133.47°, +8.58°) 3.0° = **+16.3 μK** — 唔冷
- node47 週邊係大範圍冷區: ≤8° mean=-81.4 μK (冷斑 -59.2)
- 冇 mirror 對稱 — 符合真冷結構特徵, 但**唔足以推翻多頻譜**

### ⑤ Commander 系統偏差 — 已解釋

- 低緯 (|b|<20°) 節點 Commander-SMICA = -2.7±5.4 μK
- 高緯 = +0.8±1.4 μK
- t-test p=0.0004 — Commander 喺銀河面系統性偏冷 (組件分離方法嘅已知特性)

### ⑥ 多頻譜 — 🔴 決定性證據

**3.0° FWHM 平滑後單像素 (K_CMB 單位):**

| 位置 | SMICA | 100 GHz | 143 GHz | 217 GHz | 217/143 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **node47** | **-136.1** | -58.0 | **+18.3** | **+380.9** | **20.8** 🔴 |
| node0 冷斑 | -145.0 | -125.4 | **-111.9** | -40.1 | 0.36 🟢 |
| node9 第二冷 | -110.6 | -72.5 | -42.2 | +110.3 | -2.6 |
| 高緯隨機 A | +32.6 | +60.1 | +81.5 | +187.4 | 2.30 |
| 高緯隨機 B | +38.8 | +65.0 | +90.7 | +213.9 | 2.36 |

**判讀:**
- **真 CMB 冷結構** (node0 冷斑): 143 GHz = **-112 μK** — 所有頻率都冷, 217/143 = 0.36 (平譜)
- **node47**: 143 GHz = **+18 μK** (唔冷!!) + 217 GHz = **+381 μK** — 光譜急升, 217/143 = **20.8**
- 217 GHz 強烈上升 = **熱塵埃 (thermal dust) 特徵** (ν^β, β≈1.5-2 喺 K_CMB)
- SMICA 嘅 -136 μK 係 SMICA 喺銀河面**高估減去塵埃**嘅結果 — 組件分離殘留假象

---

## 對 IDCM 嘅意義

1. **node47 唔係 A₅ 網絡嘅第二冷結構** — 佢嘅「冷」係銀河面前景假象
2. **anchor-control 測試仍然有效**: O3 skill §2 用 node47 做「第二冷控制」嘅結論 (z=-0.92 冇 signal) 唔受影響 — 因為 node47 根本唔係真冷結構, 只會令控制更保守
3. **60-node 微冷系統學 (O52, 原 O30)** 必須考慮銀河面 15/60 節點嘅前景風險 — 建議 mask |b|<20° 或 R3 CMB mask 後重做
4. **教訓**: 任何 |b|<20° 節點嘅溫度異常必須做多頻譜檢查先可以宣稱物理意義

## 驗證記錄 (2026-08-21 close-out)

`scripts/09_full_verification.py` — **82 PASS / 0 FAIL** (5 層驗證):

| 層 | 內容 | 結果 |
|:---|:---|:---|
| ① 檔案存在 | 26 個 JSON/fits/doc/script 路徑 | ✅ 全部存在 |
| ② JSON 結構 | 6 個 JSON keys/counts 完整 | ✅ 全部正確 |
| ③ 直接 FITS 重算 | SMICA cache: T47/T0 多尺度、rank、對徑、三地圖 | ✅ 全部一致 (|Δ|<0.5 μK) |
| ④ 多頻譜獨立重算 | 143/217 GHz 從 fits 重平滑: node47 +18.3/+380.9, node0 -111.9/-40.1 | ✅ 全部一致 |
| ⑤ 文檔一致性 | NN_results.md 18 個關鍵數字 + spread/Commander 統計 | ✅ 全部命中 |

**關鍵重算確認**: node47 143 GHz = +18.5 μK (唔冷), 217/143 = 20.6 (dust 特徵); node0 143 GHz = -111.9 μK (冷), 217/143 = 0.36 (平譜) — 判定 🔴 前景污染 穩固。

**搬遷後重驗證 (2026-09-11)**: O27 搬遷至 IDCM-Original repo 後, scripts path 已修復 (O3C `/tmp/cache_o3` 已清, 三地圖重算改用 o5 smooth_cache 4.17 版)。重跑: `08_verify.py` 25/25 + `09_full_verification.py` 82/82 = **107/107 PASS**。低緯 C-S 4.17° = -2.3 (與 3.0° -2.7 同號) — Commander 偏冷系統效應穩健。判定不變。

---

## 檔案

```
scripts/
  01_node47_multiscale.py    多尺度穩定性 (SMICA 10 scales)
  02_crossmap_node47.py      三地圖一致性
  03_foreground_mask.py      前景 mask 檢查
  04_antipode_check.py       對徑反查 + 週邊環境
  05_commander_anomaly.py    Commander 系統偏差
  06_multifreq_node47.py     多頻譜 (3° 盤平均)
  06b_multifreq_smooth.py    多頻譜 (3° FWHM 平滑, 精確)
  07_synthesis.py            綜合判定 (多頻譜 veto)
  08_verify.py               檔案驗證 (25/25 PASS)
  09_full_verification.py    close-out 全面驗證 (82/82 PASS)
data/
  node47_multiscale.json
  crossmap_node47.json
  mask_node47.json
  antipode_node47.json
  commander_anomaly.json
  multifreq_node47.json
  multifreq_smooth_node47.json
  HFI_SkyMap_100/143/217/353_2048_R3.01_full.fits  (2GB × 4)
  COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits
  COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.01.fits
  HFI_Mask_GalPlane-apo0_2048_R2.00.fits
```
