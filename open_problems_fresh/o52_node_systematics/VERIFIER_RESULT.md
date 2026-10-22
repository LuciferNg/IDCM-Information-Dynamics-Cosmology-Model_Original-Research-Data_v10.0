# O52 Verifier Result — File Simulation Verification

> **日期**: 2026-08-21
> **方法**: `scripts/03_verify.py` — 直接讀取 saved JSON 數據檔案, 獨立驗證 NN_results.md 所有數字
> **結果**: **54/54 PASS** ✅

## 驗證層

| 層 | 檢查數 | 通過 |
|:---|:---:|:---:|
| 1. 檔案存在 (7 個) | 7 | 7/7 |
| 2. 多尺度系統性 (8 尺度 × z/mean/counts) | 33 | 33/33 |
| 3. 堆疊 profile (annulus 值 + z + p) | 9 | 9/9 |
| 4. Doc 結構 (關鍵宣稱) | 5 | 5/5 |
| **總計** | **54** | **54/54** |

## 關鍵驗證點

- ✅ R3 mask 45/60 unmasked (frame-corrected, 同 O27 一致)
- ✅ 全部 8 尺度 60-node z_vs_sky 同 z_vs_ctrl |z|<0.5
- ✅ 高緯度子集 n=31, z_hl 全部 |z|<0.6
- ✅ 3.0° node_mean=-1.522, z=-0.27 (剔除 node0/9 後 +2.832, z=+0.46)
- ✅ 堆疊最內圈 0-2°: obs=-1.286, z=-0.21, p=0.411 (🔴 純噪聲)
- ✅ 全部 7 annulus |z|<0.6

## 幻覺檢查

所有 NN_results.md 數字均從 saved JSON 直接重讀並對比 (z ±0.05, μK ±0.1, counts exact)。**冇幻覺**。

## Frame Bug 記錄

初版 script 用 ICRS theta/phi 採樣 SMICA (Galactic frame) — frame inversion trap, 得出 R3 mask 48/60 (錯)。修正為 Galactic lonlat 後 45/60 (同 O27 一致)。**任何新 sampling script 必須先 frame check。**
