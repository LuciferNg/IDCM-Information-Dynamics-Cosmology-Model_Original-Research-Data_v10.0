# O48 / Q1.44 — Audit 最終收口：27/34/35 script 檢查 + 純 TT 疊圖

> **日期**: 2026-10-10
> **狀態**: ✅ Audit 全部 script 完成分類（docs/21+22+23+25 收口）
> **Script**: 27/34/35 檢查 + `fig_q1_peak_valley_overlay_pureTT.png`

## 1. 最後三隻 script 污染分類

| Script | 數據源 | 裁決 |
|:-------|:-------|:-----|
| **27** 峰+谷後驗 (+0.588) | `o9_high_ell_peaks/data/planck_tt.txt` = **純 TT** | ✅ **有效, 唔受污染** —— 重跑確認 +0.588 |
| **34** 參數掃描 | SPT/ACT 樣本外 + Plik 診斷行 | ✅ SPT/ACT 主判據有效 (0.5,50-60)；🔴 **Plik 診斷行 (0.3,50) +0.208 撤回**（613-rows 污染）→ 由 51 script 純 TT V¾ +0.629 取代 |
| **35** 疊圖 | Plik 613-rows | 🔴 已重畫純 TT 版（見下） |

## 2. 純 TT 疊圖（fig_q1_peak_valley_overlay_pureTT.png）

35 script 污染版疊圖 → 重畫: Planck 純 TT（每 ℓ max）+ SPT-3G + ACT DR4
三實驗 detrend residual 標準化 + IDCM 峰+谷 V¾ 模型 overlay。
Vision 驗證: 峰標記（紅虛線 221/527/815/1013/1121/1337/1409）同數據局部極值
對齊、谷線（藍點線 V¾ 450/743/1044/1337）對應凹陷、模型線形狀吻合。
純 TT V¾ corr = +0.607 全譜（同 51 script 一致）。

## 3. Q1 Audit 最終總帳（docs/21+22+23+25+26）

```
✅ 有效（唔受污染）: 27 (+0.588), 29 (ACT 2/2), 36 (SPT χ² 347.3),
                    峰位/峰高/谷位/谷深/兩層週期/V¾ 前驗/峰集止 1409
🔴 撤回（613-rows 污染）: 28 binning差異, 32 谷距297/谷偏0.220,
                          33 Plik 平排0.17, 43 Lorentz 全勝, 45/46b 右重,
                          37 k共存, 34 Plik 診斷行
修正值: 谷=[437,716,1040,1346], Plik V¾ +0.629, k=[10,11,9,7],
        谷距中心 303, 谷→後峰 0.280, G vs L 無分辨力
樣本外: PR3 +0.629 | PR4 NPIPE +0.425 | SPT +0.475 | ACT +0.272
```

## 4. 遺留（已知極限, 非污染）

- 峰形（形狀族 G/L、不對稱 γL/γR）喺現有公開數據無統計力
  （Plik 215 bins over-parameterized; SPT/ACT bins 疏; PR4 detset noise）——docs/25
- σ 算子身份（49.5 vs 50 vs 55）開放——唯一門路係 PR4 xfreq co-add + beam deconv
- 谷距 k 值（[10,11,9,7]）4 點唔夠閉合結構身份