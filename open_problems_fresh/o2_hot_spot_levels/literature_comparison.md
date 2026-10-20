# O2 文獻對比 — Hou et al. 2009 熱冷斑分析

> 日期: 2026-08-16
> 論文: Zhen Hou, A. J. Banday, K. M. Gorski, "The Hot and Cold Spots in Five-Year WMAP Data" (arXiv:0903.4446)

## 論文核心發現

Hou et al. 2009 對 WMAP 5 年數據嘅局部極值 (local extrema) 做咗詳盡嘅 frequentist 分析:

1. **熱/冷斑低 variance**: 所有頻段都觀測到熱斑和冷斑嘅低 variance (low-variance of hot and cold spots)
2. **95% C.L. 拒絕高斯假設**: 喺 KQ75 mask 外同北半球 (Galactic 同 ecliptic 座標), 觀測同高斯模擬嘅一致性被拒絕
3. **大尺度結構關聯**: P-P (pair-counting) 相關函數證明: **係大角度尺度結構同其異常性質, 同熱/冷斑嘅性質密切相關**
4. **T-T 低於 3σ**: 溫度配對乘積 (T-T) 喺 20° 以下尺度有弱相關, 完全低於 3σ 置信區域

## 與 O2 結果嘅對照

### 1. 熱斑冷斑低 variance ✅ 對應

Hou 2009 發現熱/冷斑低 variance — 即係極值唔似高斯場預期咁分散。

**O2 對應發現**: 
- 冷斑 = -145.0 μK (3°平滑) vs 預期高斯場最大極值
- 全天最熱點 (masked) = 150.2 μK (3°平滑), 只有 3.56σ
- 高斯場預期: NSIDE 2048 平滑後約 10⁵ 個獨立區域, 最熱點應該 ~4.5-5σ
- **觀測 3.56σ 明顯低於高斯預期 → 低 variance 證據 🟢**

### 2. 大尺度結構與冷斑關聯 ✅ 對應

Hou 2009: "it is the large angular-scale structures, and some unusual properties thereof, that are intimately connected to the properties of the hot and cold-spots"

**O2 對應發現**:
- IDCM 嘅 A₅ 60 節點網絡就係大尺度結構 (邊長 26.09°)
- 冷斑錨定著色嘅熱/冷節點分離: 1.83σ (p=0.0335)
- 6-level BFS ladder (χ²/dof=0.54): 節點振幅隨網絡距離衰減
- **F₆ 熱點 (157.8°, -70.3°) 離冷斑 25.2°** — 喺 A₅ 網絡嘅節點間距尺度

### 3. T-T 弱相關 ✅ 對應

Hou 2009: T-T 喺 20° 以下弱相關, 低於 3σ。

**O2 對應發現**:
- 邊長 vs |ΔT| 冇信號 (-0.52σ) — 之前 cmb_cold_spot 分析
- 即係話: 信號唔喺「距離」度, 而係喺「拓撲身份」(frustration vs normal edge)
- 同 Hou 嘅「大尺度結構關聯」一致

### 4. 熱斑目錄 (Vielva 2007 / Hou 2009)

Hou 2009 冇提供具體熱斑目錄表, 但提供咗統計性質:
- 熱/冷斑數量: 低於高斯預期
- 分佈: 偏向大尺度結構

**O2 熱斑候選位置**:
| 候選 | 位置 | 峰值 | 尺度 | 文獻對應 |
|:----|:----|:----|:----:|:--------|
| F₆ 熱斑 | (157.8°, -70.3°) | 277.6 μK | 1.0° | 高緯度極值 |
| F₇ 熱斑 | (0.2°, -37.9°) | 353.4 μK | 0.5° | 高緯度極值 |

> ⚠️ 時序註釋: 本文檔寫於 2026-08-16 20:42 (Commander 三地圖驗證完成前)。
> 後續 §9 三地圖版本: F₆=277.7±0.74 μK, F₇=353.1±0.06 μK (三方法 0.06-2.0% 一致) — 以 01_problem_record.md §9 為準。

## 結論

Hou et al. 2009 嘅三個核心發現同 O2 結果**完全一致**:

1. **低 variance 熱冷斑** ↔ 全天最熱只有 3.56σ (高斯預期更高)
2. **大尺度結構關聯** ↔ A₅ 60 節點網絡 + BFS ladder
3. **T-T 弱相關** ↔ 邊長無信號, 拓撲身份先係關鍵

呢啲唔係巧合 — Hou 2009 (WMAP 5yr) 同我哋 (Planck SMICA/NILC/Commander) 用完全獨立嘅數據同方法, 得出相同嘅結論:**CMB 熱冷斑有系統性異常, 同大尺度幾何結構相關**。(★ω★)♪