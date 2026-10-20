# O2 F7 前景診斷記錄 (2026-10-20)

## 狀態: ✅ F7 l=0° caveat 已拆 — 真延展 CMB 結構, 唔係點源/前景

## 背景

F7 熱斑候選 (0.2°, -37.9°), 353.1μK @ 0.5° 平滑, 三地圖 (SMICA/NILC/Commander)
0.06% 一致。之前唯一 caveat: **l=0.2° 銀心方向, 需排除前景/點源污染**。
本記錄 = 六重 model-free 診斷 (scripts/14 + 15), 全部通過。

## 診斷測試 (2026-10-20, SMICA R3.00 full 重下載 2.01GB 核實後)

| 測試 | 判据 | 結果 | 判決 |
|:-----|:-----|:-----|:----:|
| T1 三地圖 0.5° 重現 | SMICA/NILC/Commander ≈ 353μK, spread<1% | 353.0/353.1/353.2, spread 0.06% | ✅ |
| T2 多尺度掃描 | 點源 0.5°/3.0° ratio>5, 延展<5 | ratio=4.50 (353.0→235.4→78.5) | ✅ 延展 |
| T3 annulus 1-3° | peak-bg > 3×map std | bg=+24.2, peak-bg=+328.9 (3σ=252.2) | ✅ 顯著 peak |
| T4 A5 節點距離 | 唔喺節點上 (>3°), O5 預期 8-9° | 最近節點 #51 = 8.25° | ✅ 符號預期 |
| T5 銀道面 | \|b\|>20° | b=-37.9° | ✅ 高緯 |
| T6 徑向 FWHM | FWHM>beam(0.5°) = 延展 | FWHM≈1.5°, profile 單峰平滑衰減 | ✅ 延展 |

### T6 徑向 profile (0.5° 平滑, manual dot)
```
r=0.00°: +353.0 μK
r=0.25°: +311.4 μK
r=0.50°: +215.6 μK
r=0.75°: +127.3 μK
r=1.00°:  +87.1 μK
r=1.50°:  +60.3 μK
r=2.00°:  +43.1 μK
r=3.00°:  -14.7 μK
FWHM_est ≈ 1.50°  (beam = 0.5°)
```
單峰平滑衰減, 半功率寬 ~3×平滑 beam => **延展結構**, 點源會 FWHM≈0.5° 且
遠場急跌。T6 排除「暗源/緊湊銀心前景」假說。

## 技術注記 (可復現)

- angdist bug: `hp.rotator.angdist(vec(3,), pv(N,3))` 返回 garbage (max 120° 非 2°);
  T3 v3 早期版本因此不可信 → **全部重以手動 dot product** 計算:
  `degdist = degrees(arccos(clip(v1 @ v2.T)))` (min 0.0157°, max 2.0499° 精確)
- script 20 shadow bug 同源 (astropy units `u` 被 loop 變數覆蓋) — 已修
- SMICA = `/home/wsl/.hermes/cache/scratch/planck_smica/smica.fits` (sha256 前綴 60952c64)
- scripts: `14_f7_foreground_diagnosis.py` (T1-T6 集成), `15_f7_radial_profile.py` (T3+T6 manual dot, 修正版)

## 結論

**F7 (0.2°, -37.9°) @ 0.5° = 353.1μK 屬真延展 CMB 結構**:
1. 三獨立 CMB 分離演算法 0.06% 一致 (非 component-separation 假象)
2. 徑向 FWHM 1.5° >> smoothing beam —— 非點源
3. 離最近 A5 節點 8.25° —— 同 O5「熱點離節點 8-9°」觀測模式一致
4. 高銀緯 (-37.9°), 唔受銀河面 mask 影響

l=0° 銀心方向 caveat **解除**: 即使投影方向敏感, 延展 + 高緯 + 三方法一致
已排除緊湊前景源。F7 維持 🟡 候選 (非 🔴) 嘅理據而家由「得 0.06% 一致」
升級到「六重測試全過」; 但 F7 仍未到 F6 級確認 (仍需: 獨立 catalogue 對比 /
頻道殘餘圖分析), 所以 O2 狀態維持 partial。