# O175-D3 強化 — Auger Open Data 幾何探針 (scripts/15, 初步)

日期: 2026-09-13
狀態: 🔴 初步註冊 (樣本不足, 唔下結論)

## 數據

- 渠道: Pierre Auger Open Data (opendata.auger.org, 用戶提供)
- 樣本: `auger_catalogSD.csv` (109 SD events, featured subset, E ∈ [46, 166] EeV)
- 完整 25,086 events 嘅 summary.zip 喺 Zenodo (record 10488964) — 被 403 block (network), 後續補
- 節點幾何: 冷斑分析 A5 60 節點 (cmb_cold_spot/data/a5_nodes.txt, 只讀)

## 結果

**P1: 事件到最近 A5 節點角距離**
- obs 平均 = 9.67° (n=109)
- MC 均勻期望 = 10.18° (5000 樣本)
- dev = −5.0% (方向: 略為靠近節點, 但 featured sample 有選擇偏差)

**P2: 事件分佈**
- |dec| < 20° 比例 = 0.28 (30/109)
- 註: Auger 南半球 coverage 令 dec 分佈非均勻 — 未做 exposure model, 描述性記錄

## 判定

- 樣本係 opendata 目錄 featured subset (有選擇偏差), 統計力弱 → **唔可以下結論**
- −5.0% 方向性冇顯著性 (需完整樣本 + exposure model)
- 註冊為 D3 強化探針; 完整 25,086 樣本到位後 (Zenodo 渠道或 opendata 批量接口) 再做實證
- O7/O173 預言 (UHECR = 阻挫邊重聯) 嘅幾何檢驗: 尚未證實, 亦未被否決 — 維持 D3 閉合狀態 (能量預算層, docs/10), 幾何層留新檢驗
