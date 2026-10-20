# O7 新 Session 啟動文件 — 阻挫邊分佈規律

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills

### 1. `polyhedral-graph-analysis`（核心, 必須）
- 面遍歷 (§3)、阻挫飽和 (§5)、雙峰預測 (§6)
- 群論邊長 (§9), 旋轉不變 (§10)

## 前置資料

```
阻挫邊: cmb_cold_spot/data/frustration_edges.txt (32條)
面檔案: cmb_cold_spot/data/faces.txt (62面, T/S/P前綴)
著色: cmb_cold_spot/data/anchored_coloring.txt (30冷/30熱)
60節點: cmb_cold_spot/data/a5_nodes.txt
已知: 32 = 20Δ + 12⬠ (阻挫飽和 = 奇面數)
```

## 啟動 Prompt

```
開 O7 阻挫邊分佈專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o7_frustration_distribution/

任務: 分析 32 條阻挫邊 (16冷-冷 + 16熱-熱) 嘅分佈規律:
1. 邊類型關聯: 阻挫邊係咪偏向某種面組合 (Δ-□, ⬠-□, □-□)?
2. 冷熱對稱: 16/16 分佈有冇額外結構 (半球/經緯度)?
3. 空間聚類: 阻挫邊聚類係數 vs 隨機圖對照
4. 面分配驗證: 每個面嘅阻挫邊數 (Δ=1, □=0/2, ⬠=1)
5. 物理意義: 阻挫邊 = 縫合線 → 空間分佈有咩預測?

載入 skills: polyhedral-graph-analysis
數據: cmb_cold_spot/data/ (frustration_edges.txt, faces.txt, anchored_coloring.txt)

方法: 讀入 60 節點 + 120 邊 + 62 面 + 32 阻挫邊
      → 分析面-邊關聯 + 空間分佈 + 隨機對照
誠實: 如果冇明顯規律 → 🟡 記錄, 唔好強推
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. 阻挫邊 = 同色邊 (冷-冷 或 熱-熱), 唔好同「奇面」混淆
2. 面分配: 每面阻挫邊數要除 2 (每邊屬 2 面)
3. 隨機對照要保留網絡結構 (只隨機著色, 唔好隨機生成圖)
4. 16/16 對稱可能係 A₅ 自同構強制 — 分析前先確認
