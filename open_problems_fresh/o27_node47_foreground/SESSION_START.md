# SESSION_START — O27 節點 47 前景污染分析

> 交接日期: 2026-08-17
> 來源: O5 延伸 #1 (O5_OPEN_ISSUES.md)

## 問題
節點 47 (l=313.47°, b=-8.58°) 係 3.0° 第二冷 (-135.7 μK)，但接近銀河面 — 前景污染風險。

## 已確認
- 3.0° SMICA: -135.7 μK (排名 2/60)
- 5.0° SMICA (O2): -123.4 μK
- 距離大冷斑 90.5°、gp10 77.6° — 唔近任何已知結構

## 未做
- [ ] 前景 mask 檢查 (Planck 53%/70% mask)
- [ ] 三地圖一致性 (SMICA/NILC/Commander @ node47)
- [ ] 多頻譜檢查 (100/143/217/353 GHz)
- [ ] 多尺度穩定性 (0.5°-10°)
- [ ] 對徑反查 (133.47°, +8.58°)

## 資源
- O3 cache: `/tmp/cache_o3/SMICA_*.fits`, `NILC_*.fits`, `Commander_*.fits`
- O5 smooth cache: `../o5_catalog_compare/data/smooth_cache/`
- a5_nodes: `../cmb_cold_spot/data/a5_nodes.txt`

## 判定
🟢 三地圖一致 + 平譜 → 真實冷結構
🔴 分歧/光譜上升 → 前景污染
