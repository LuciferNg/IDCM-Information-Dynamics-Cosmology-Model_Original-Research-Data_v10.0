# SESSION_START — O29 mean-nearest p=0.072 分解

> **交接日期**: 2026-09-11 (遷移至 IDCM-v10.0--It-From-Beat 後更新)
> **來源**: O5 延伸 #3 (O5_OPEN_ISSUES.md)
> **主體狀態**: ✅ 已閉合 (2026-08-21) — 🔴 冇第二結構
> **後續狀態**: 🔴 熱斑幾何歸屬開放 (O5 遺留)

## 主體結論 (已閉合, 唔使重做)

**🔴 p=0.072 殘餘信號 = 大冷斑家族 (6 斑) 尾巴, 冇第二結構 (node9/node47) 貢獻:**
- 冷斑族 = lit#1 + SMICA-c2 + sub-spots A-D (6 斑全部最近 node 0, 只係 O5 只減咗 lit#1)
- 完整移除冷斑族 → p=0.385 (1000-rot + 10,000-rot 雙重確認, 純噪聲)
- node9 排除: 相關斑 (c3,c11) 距離 10-12° 比隨機更遠 (+2.66°, P=0.79), 移除反而更顯著 (p=0.042)
- node47 零貢獻: 冇任何斑喺 23° 內 (最近 SMICA-h10 @ 23.18°)
- Bootstrap: 僅 22% draws p<0.05 — 信號脆弱, 單一族圖像
- 驗證: 47/47 verifier PASS + 獨立重算 (fresh seed 777, 10k-rot) 一致 (scripts/04_verify.py, 05_independent_recheck.py)

## 🔴 剩餘開放問題 (接手重點)

| # | 問題 | 狀態 | 說明 |
|:--:|:-----|:----:|:-----|
| 1 | **熱斑幾何歸屬 (F₆/F₇)** | ✅ 已閉合 (2026-09-11) | 14 SMICA 熱斑對節點 (z=-0.10)、三角形中心 (z=+0.92)、阻挫邊中點 (z=+1.74) 全部同緯度修正隨機冇分別 — 🔴 冇歸屬, 熱斑位置完全隨機。scripts/06_hotspot_attribution.py + data/hotspot_attribution.json |
| 2 | **相位機制假說** | 🟡 已移交 O143 | 點解係「特定節點」而唔係「全部節點」有異常? 異常 ∝ cos θ_i, 大部分 θ_i≈π/2 正交 — 見 o143/ |
| 3 | 冷斑族移除後殘餘 (29 斑) | ✅ 已答 | p=0.385 純噪聲, 冇需再跟 |

## 資源

- 目錄數據: `../o5_catalog_compare/data/match_results.json` (35 斑, 含 O2 F₆/F₇)
- 節點座標: `../cmb_cold_spot/data/a5_nodes.txt` (**ICRS! 要轉 Galactic lonlat 先採樣 — frame 鐵律**)
- O5 顯著性: `../o5_catalog_compare/scripts/04_significance.py`
- SMICA 平滑 cache: `../o5_catalog_compare/data/smooth_cache/` (0.5-10°)
- O21 (node9): `../o21_node9_anomaly/`
- O27 (node47 前景): `../o27_node47_foreground/`

## 已知陷阱 (必須遵守)

1. **Frame inversion trap**: SMICA 地圖 + R3 mask 都係 Galactic frame; a5_nodes.txt 係 ICRS。必須 `SkyCoord(icrs).galactic` → `hp.ang2pix(nside, l, b, lonlat=True)`, 否則靜默返回錯誤像素
2. **RNG stream 順序**: O5 嘅 04_significance.py 用 seed 20260817, subset 順序 all/lit/smica-cold/smica-hot 先、all-minus-coldspot 最後 — 唔同順序得出 p=0.052 vs 0.072
3. **match_results node 編號**: 舊版 index 冷斑=node 57, 新版 a5_nodes.txt 冷斑=node 0 — 以 a5_nodes.txt 0-based index 為準
4. 執行 Python 用 `/usr/bin/python3` (numpy 2.4.6 + healpy + astropy)

## 下一步建議 (熱斑幾何歸屬)

1. **重新檢驗 F₆/F₇**: 用新版 a5_nodes.txt 重算最近節點距離 (確認 9.03°/8.25° 冇 frame bug)
2. **多尺度檢查**: F₆/F₇ 喺 0.5°-10° 平滑下位置有冇漂移? 有冇對應更細尺度嘅節點?
3. **幾何歸屬候選**: 熱斑會唔會對應阻挫邊/三角形中心 (而非節點)? 用 O26 嘅 20 三角形 + 32 阻挫邊幾何測試
4. **對照 O24**: 極端節點冷色匹配 (8/10) 有冇熱斑對應? O24 記錄喺 `../o24_extreme_side_asym/`
