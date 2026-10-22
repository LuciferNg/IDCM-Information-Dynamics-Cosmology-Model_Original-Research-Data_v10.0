# O25: Node9 大尺度冷區 — 文獻對照 (物理來源評估)

> **日期**: 2026-08-21
> **方法**: arXiv 文獻搜尋 (browser, arxiv.org/search)
> **狀態**: 文獻對照完成 — 物理來源 🟡 部分評估

---

## Node9 數據回顧 (O25 尺度譜)

- **位置**: Galactic (l=214.92°, b=−31.16°), ICRS (RA=75.268°, Dec=−15.212°) ✅ (已核對 a5_nodes.txt idx 9; 早期寫 144.22°/−2.67° 係 node8 座標, 已修正)
- **細尺度**: 4.17° 時 T=−107.0 μK (rank 3/60) — 第二冷結構
- **大尺度**: 10° 時 T=−90.3 μK (**rank 1/60**), 三地圖一致 (SMICA −90.34 / NILC −90.51 / Commander −87.77)
- **區域**: 10° 半徑 mean=−72.0 μK (**z=−2.56σ**), 15° −50.8 (z=−2.32σ), 20° −35.1 (z=−1.89σ)
- **衰減**: 慢衰減 τ₂≈33° (= K_tree 尺度 33)
- **同冷斑距離**: 26.16° — 獨立結構, 唔係冷斑一部分

---

## 文獻脈絡

### 1. 大尺度峰研究 (最直接相關) — arXiv:1701.08552
**"Local properties of the large-scale peaks of the CMB temperature"** (Marcos-Caballero, Martínez-González, Vielva 2017, JCAP 05:023)

- 研究 Planck CMB **最大結構 + 最突出峰**, 指出全部集中喺**南銀河半球**
- 冷斑 anomaly = **中心大曲率**
- 峰嘅振幅 + 一階/二階導數之後, 其餘場同標準模型一致
- **⭐ 支持我哋嘅發現**: node9 (b=−31°) 喺南銀河半球, 係大尺度冷區一部分 — 同文獻嘅「南半球大尺度峰」圖像一致

### 2. 冷斑 supervoid 解釋 (主流) — arXiv:1406.3622, 2112.07699, 1511.09008
- Szapudi et al. 2014: 冷斑 = supervoid 嘅 shadow (Eridanus supervoid)
- Kovács et al. 2021 (DES): Eridanus supervoid 同冷斑嘅 lensing 研究
- Kovács & García-Bellido 2015: Cold Spot, Eridanus Supervoid, Great Walls

### 3. 反 supervoid 解釋 — arXiv:1704.03814, 2211.16139
- Mackenzie et al. 2017: **Evidence against a supervoid causing the CMB Cold Spot** — 冇搵到對應 supervoid
- Owusu et al. 2023: **ruling out a supervoid interpretation** (lensing 排除)

### 4. 多空洞模型 — arXiv:1512.02694
- Naidoo et al. 2016: 多空洞 ISW+RS 可以產生冷斑-like profile (但解釋唔到熱環)

### 5. Masking 詛咒 — arXiv:1405.1844
- Rassat et al. 2014: **masking 效應主導**, 冷斑喺好多地圖唔顯著 (LGMCA 全天地圖)
- 提醒: 大尺度冷區要小心 masking/前景殘餘

---

## Node9 物理來源評估

### 候選解釋

| 候選 | 支持 | 反對 | 狀態 |
|:---|:---|:---|:---:|
| **CMB 本徵大尺度峰** | 1701.08552 南半球大尺度峰; 三地圖一致 (2.6% spread) | 需要排除 masking/前景 | 🟡 最可能 |
| **ISW + supervoid** | 南半球有 Eridanus supervoid 家族; 多空洞可解釋 | node9 距離冷斑 26°, 冇文獻直接對應; supervoid 解釋有爭議 (1704.03814, 2211.16139) | 🟡 部分 |
| **前景殘餘** | node9 b=−31° 遠離銀河盤 (|b|>20°) | 三地圖一致 (SMICA/NILC/Commander 獨立分離法) — 前景殘餘會唔同 | 🔴 唔似 |
| **IDCM 結構** | τ₂≈33° = K_tree 尺度; 節點網絡 hop-1 冷斑鄰居 | 需要 IDCM 預言對照 | 🟡 待推導 |

### 關鍵判別測試 (可以做)

1. **lensing 檢驗**: node9 區域有冇 supervoid? (對照 DES/星系目錄) — 需要外部數據
2. **SMHW 尺度分析**: node9 喺 R8/R10/R15 尺度嘅 SMHW 係咪顯著? — 用本地地圖可做
3. **隨機對照**: 60 節點網絡內 node9 大尺度 rank 1/60 嘅全局顯著性 — 已做 (區域 z=−2.56σ 但單點 z=0.06σ)
4. **LGMCA 交叉**: 用 Rassat 嘅 LGMCA 全天地圖確認 (無 masking 效應) — 需要下載

---

## 結論

**🟡 Node9 大尺度冷區最可能係 CMB 本徵大尺度結構** (南銀河半球大尺度峰家族一部分, 見 1701.08552), 而非前景殘餘 (三地圖一致)。

**但注意**: 單點 z=0.06σ (隨機 60 點最冷 bootstrap) — 單點極端性本身唔顯著! 只有**區域平均** (10°-20° 半徑) 先顯著 (z=−2.56σ 至 −1.89σ)。呢個係「大尺度低溫區」嘅 signature, 唔係「單點冷斑」。

**同 IDCM 嘅關聯**: τ₂≈33° = K_tree 尺度 — 如果 IDCM 預言大尺度結構有 33° 特徵尺度, node9 區域係觀測支持。**但需要獨立推導, 唔可以當已確認。**

---

## 文獻清單

| arXiv ID | 標題 | 關聯 |
|:---|:---|:---|
| 1701.08552 | Local properties of the large-scale peaks of the CMB temperature | ⭐ 南半球大尺度峰 |
| 1406.3622 | The Cold Spot: the Shadow of a Supervoid | supervoid 解釋 |
| 2112.07699 | The DES view of the Eridanus supervoid and the CMB Cold Spot | DES lensing |
| 1511.09008 | Cosmic troublemakers: Cold Spot, Eridanus Supervoid, Great Walls | supervoid 家族 |
| 1512.02694 | Could multiple voids explain the CMB Cold Spot anomaly? | 多空洞模型 |
| 1704.03814 | Evidence against a supervoid causing the CMB Cold Spot | 反 supervoid |
| 2211.16139 | The CMB cold spot under the lens: ruling out a supervoid interpretation | 反 supervoid (2023) |
| 1405.1844 | Planck CMB Anomalies: Curse of Masking | masking 警告 |
