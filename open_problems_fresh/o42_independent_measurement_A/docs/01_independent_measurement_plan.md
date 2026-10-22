# O42 — 冷斑 A 獨立量度方案

> 日期: 2026-08-20
> 狀態: 🟠 方案設計中
> 調律者: 三通道獨立量度方案

---

## 核心問題

A = 88×61/40 = 134.2 μK 係 O41 結構閉合（零自由參數），但係 post-diction（側推識別）。要將佢提升為可證偽預言，需要：
1. **獨立於 IDCM 理論參數**嘅天文觀測驗證
2. **精確分離 foreground** 同超空洞二次效應
3. **多通道交叉確認**（SMHW + ISW + 偏振）

---

## 通道 1: 高精度 CMB 全天頻譜剝離

### 方法
SMHW (Spherical Mexican Hat Wavelet) 小波變換 → 多尺度提取冷斑區域嘅平均溫度欠缺 A。

### 已有數據
- Planck SMICA 頻段圖 (30-857 GHz, 已用於 O5/O7)
- NILC/Commander 交叉驗證 (O3 已確認 18/18 讀數一致)
- Smooth cache 0.5°-10° 共 11 個尺度 (o5_catalog_compare/data/smooth_cache/)

### 零成本驗證
對 Planck SMICA 4.17° 平滑（對應冷斑結構尺度 R8 = 4.17°）：
- 抽節點 0 溫度: T = −134.19 μK（O5 已確認）
- 多尺度穩定性: 1°-10° 節點 0 全部 rank 1-3
- 跨-map: SMICA/NILC/Commander 一致

### 關鍵測量
A = 134.2 μK 喺冷斑中心區域 (209°, -57°) 嘅 10° 直徑範圍內平均欠缺。

---

## 通道 2: 視線方向超空洞 ISW 解耦

### 學術現狀
Eridanus Supervoid (z ≈ 0.16, 半徑 ≈ 80 Mpc, δ ≈ −20%) 已被 Pan-STARRS (Szapudi+2015) 確認為真實結構。

### 標準模型 (ΛCDM) 預言
暗能量 (DE) 令勢阱 Φ 隨時間演化 → 超空洞產生冷斑 ISW 貢獻 ΔT_ISW ≈ −10 至 −40 μK。

### IDCM 預言
**IDCM 冇暗能量、冇膨脹 → 勢阱靜態 → ISW = 0**
→ A_prim = A_total = 134.2 μK（冇嘢要扣）

### 參考文獻值
| 文獻 | 超空洞 ISW 貢獻 | 備註 |
|:-----|:---------------:|:-----|
| Granett+2008 | −11.3 ± 4.5 μK | Stacked voids, 非 specific |
| Szapudi+2015 | −20 ± 10 μK | Eridanus specific |
| Planck 2015 XXIII | < 10 μK (marginal) | Cold spot specific |
| Finelli+2016 (Planck) | ~10 μK | Supervoid 解釋有限 |

### 可證偽預言
| 預言 | IDCM | ΛCDM + supervoid |
|:-----|:----:|:----------------:|
| Eridanus ISW 貢獻 | 0 μK | −10~−40 μK |
| A_prim (原生 CMB) | 134.2 μK | 94-124 μK |
| DESI 2026+ 分辨 | ISW=0 | ISW≠0 |

### 時間表
- DESI 完整 5 年巡天 (2026): 量度超空洞 3D 密度 → ISW 預期
- Euclid (2027+): 寬場巡天交叉驗證
- 目前: Planck 2015 已傾向支持 ISW 貢獻小 (< 10 μK)，**間接支持 IDCM**

---

## 通道 3: CMB 偏振 (E-mode) + 引力透鏡勢場

### E-mode 偏振
- 冷斑係溫度異常，IDCM 未對偏振做過預言
- T-E 交叉相關可以檢驗冷斑係咪「相干幾何結構」
- 🟡 非核心預言通道

### 透鏡勢場重建
- CMB 四次矩 (Trispectrum) 重建 Φ
- 扣除前景引力透鏡扭曲 → 純淨 A
- 🟡 需要大量計算資源

### 誠實標記
IDCM 對偏振同透鏡**未有結構預言**。呢個通道可提供交叉驗證，但唔係 IDCM 可證偽性嘅核心。

---

## 零成本立即執行項目

### 1. SMHW 小波驗證 (預計 1-2 日)
用現有 Planck SMICA 數據做 SMHW 變換，喺尺度 R=5° 提取冷斑幅度 A，同 pixel 抽樣結果 (−134.19 μK) 比較。

### 2. 多頻段穩定性 (預計 1-2 日)
下載 Planck 30/44/70/100/143/217/353 GHz 單頻段圖，每個頻段獨立抽樣冷斑 A，檢查頻段一致性。

### 3. ISW 文獻整合 (預計 0.5 日)
系統性整理 Eridanus Supervoid ISW 文獻值，量化 IDCM (ISW=0) vs ΛCDM (ISW=−10~−40) 嘅分辨所需精度。

### 4. 徑向溫度剖面 (預計 0.5 日)
冷斑中心 0°-15° 徑向剖面，驗證 A₅ 節點網絡嘅溫度結構。

---

## 參考文獻
- Cruz et al. 2005 (astro-ph/0405341) — 冷斑發現
- Szapudi et al. 2015 (Nature) — Eridanus Supervoid
- Finelli et al. 2016 (Planck 2015 results XXIII) — ISW limits
- Granett, Neyrinck & Szapudi 2008 — Stacked ISW
- O5 cold spot catalogue (IDCM, 2026-08-17)
- O7 frustration distribution (IDCM, 2026-08-19)
- O41 observer budget (IDCM, 2026-08-20)