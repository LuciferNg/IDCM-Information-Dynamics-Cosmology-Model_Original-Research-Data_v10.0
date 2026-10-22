# SESSION_START — O52 60 節點系統性微冷/微熱檢驗

> **交接日期**: 2026-09-11 (遷移至 IDCM-v10.0--It-From-Beat 後更新; ΔE=0 最後裁決同日完成)
> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #4)
> **原編號**: O30（舊系列）→ 新系列 O52
> **主體狀態**: ✅ 已閉合 (2026-08-21) — 🔴 否定「全部 60 節點有異常」
> **後續狀態**: ✅ **完全閉合 (2026-09-11)** — ΔE=0 判死 (docs/02_deltaE0_verdict_20260911.md); 相位機制 → O143 (進行中)

## 主體結論 (已閉合, 唔使重做)

**🔴 60 節點冇系統性微冷/微熱** — 只有 node0/node9 係真異常:
- 全部 8 尺度 60 節點 mean |z|<0.4σ; 高緯 31 |z|<0.6σ; unmasked 45 |z|<0.4σ
- 堆疊 radial profile 全部 7 annulus |z|<0.6 (最內圈 0-2° z=-0.21)
- 剔除 node0/node9 後剩餘 58 節點反而微正 (+2.8 μK, z=+0.46)
- 冷/熱 = 29/31, 2σ = 4/2 (node0/node9 驅動)
- 驗證: 54/54 verifier PASS + 獨立重算一致 (scripts/03_verify.py, 04_independent_recheck.py)

## 🟡 剩餘開放問題 (全部已處理 2026-09-11)

| # | 問題 | 狀態 | 最新結果 |
|:--:|:-----|:----:|:---------|
| 1 | **ΔE=0 12節點抑制 — 跨地圖驗證** | 🔴 判死 (2026-09-11) | 多頻譜最後裁決: 4.17° 抑制只存在於組件分離地圖 (SMICA/NILC/Commander p=0.036-0.055); HFI 100/143/217 GHz 方向相反 (p≥0.99); 高緯子集 0/6 地圖達 p<0.05 (最好 100 GHz p=0.057)。→ 組件分離/前景假象, 唔係真實效應。scripts/06_deltaE0_verdict.py + docs/02 |
| 2 | **相位機制假說 — 點解係特定節點？** | 🟡 已移交 O143 | 4 步算子化框架: Step 1 (𝒫) 🟢, Step 2 (T_pipe) 🟢, Step 3/4 (θ_i^ind) 🟡 — 見 o143/ |
| 3 | **熱節點系統性 (O24 相關)** | 🟡 已部分處理 | O52 已顯示冇整體熱系統性; node53 熱異常 (+112 μK) 已獨立確認 |

## 資源

- 節點座標: `../cmb_cold_spot/data/a5_nodes.txt` (**ICRS! 要轉 Galactic lonlat 先採樣 — frame 鐵律**)
- SMICA 平滑 cache: `../o5_catalog_compare/data/smooth_cache/` (0.5-10°)
- 大尺度平滑 cache: `../o25_scale_spectrum/data/smooth_cache_large/`
- R3 mask: `../o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits`
- Raw SMICA IQU 2048: `../o26_node57_region/data/smica_iqu_2048.fits`
- O27 前景方法: `../o27_node47_foreground/scripts/03_foreground_mask.py`
- O143 (相位機制): `../o143_*/`

## 已知陷阱 (必須遵守)

1. **Frame inversion trap**: SMICA 地圖 + R3 mask 都係 Galactic frame; a5_nodes.txt 係 ICRS。必須 `SkyCoord(icrs).galactic` → `hp.ang2pix(nside, l, b, lonlat=True)`, 否則靜默返回錯誤像素 (本項目已中招一次)
2. **RNG stream 順序**: MC 檢驗 p 值有 ±0.02 變異, 結論要以 10k rotations + 多 seed 確認
3. 執行 Python 用 `/usr/bin/python3` (numpy 2.4.6 + healpy + astropy)

## 下一步建議 (2026-09-11 已全部完成)

1. ✅ **ΔE=0 判定收窄 (已完成)**: 用 HFI 143/217 GHz (加 100 GHz) 多頻譜做最後裁決 → 🔴 判死
   (抑制只存在於組件分離地圖, 多頻譜冇重現, 高緯 0/6 達 p<0.05)。scripts/06 + docs/02。
2. ✅ **O52 完全閉合**: ΔE=0 確認係組件分離/前景假象 → 本文件狀態已更新為 ✅。
3. ✅ **相位機制**: 詳細推導喺 O143 進行, O52 唔重做。
4. 🟡 (可選) Planck PR4 複查: 高緯 4 節點 {10,22,25,32} @4.17° ratio ~0.38-0.43 喺 4 幅地圖
   一致但 n=4 統計無力 (p≥0.057) — 留做 PR4 弱候選, 唔影響 O52 閉合。
