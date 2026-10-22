# SESSION_START — O21 節點 9 極端 anomaly

> **開始**: 2026-08-17
> **來源**: O3 衍生問題 O3-1

## 任務

分析節點 9 (-106.99 μK, 全場第二冷但熱色著色) 係咪真實 anomaly。

## 交接點 (從 O3)

- 節點 9: T=-106.99 μK @ 4.17° SMICA, 色=熱 (hop=1), b=-31.2°
- 已有: 60 節點溫度 (o3_node_temperatures/data/node_temps.txt)
- 已有: 三地圖多尺度 cache (/tmp/cache_o3/, 30 個檔案)
- 方法參考: scripts/18_node45_region.py (區域分析)

## 第一步

三地圖 × 多尺度節點 9 溫度 → 附近區域結構 → 極端值 bootstrap
