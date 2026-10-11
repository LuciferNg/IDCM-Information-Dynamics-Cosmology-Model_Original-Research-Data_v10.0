# O64 文檔 01 — 一期：9 費米子質量階層 — sector-dependent 幾何分析

> **日期**: 2026-08-31
> **狀態**: 🟡 **結構分析完成 — 核心瓶頸已標記**
> **腳本**: scripts/01–04
> **前置**: O57 docs/13 (Kähler trade-off), O61 (A_ij 3×12 block), O57 docs/14 (Q_ij 3 clusters)

---

## 一、問題回顧

SM 9 費米子質量階層 10⁸（e:μ:τ = 1:207:3477, u:c:t = 1:477:133077, d:s:b = 1:20:1548）需要 sector-dependent 幾何：3 type 各自 curve 子集，Yukawa 矩陣結構。

O57 docs/13 證明 Kähler trade-off 定律：**單一全局 Kähler 參數做唔到「9 個有限 + 階層 1e8」**。O61 發現 κ_ijk 有內稟 3×12 block 結構，係 sector-dependent 幾何嘅 CY₃ 實現。

**本輪目標**: 用 O61 嘅 3×12 block Yukawa 矩陣，推導 9 費米子質量。

---

## 二、已確認結構

### 2.1 66 態 = 3×(12+10) = 3×22

```
66 態 = 36 K (Kähler moduli) + 30 C (CPX)
      = 3 × 12 K + 3 × 10 C
      = 3 × 22 per type/generation
```

- W_K (36×36) 有 3×12 block 結構：diag/off = 4.24 ✅
- 每個 block 嘅 12 K 態完美對應 12 Kähler moduli (overlap >0.99)
- 30 C 態正交於 K 態，冇直接 block 結構

### 2.2 Q_ij 3 clusters ↔ 3 types

Q_ij (185×32) 有 3 clusters [81, 70, 34]（O57 docs/14）:
- 81 = 22 (type 0) + 59 (extra divisors)
- 70 = 22 (type 1) + 48 (extra divisors)
- 34 = 22 (type 2) + 12 (extra divisors)
- 59+48+12 = 119 = 185−66 ✅

**→ 3 clusters 對應 3 types (up/down/lepton)**

### 2.3 κ_ijk 3×12 block 結構

| 類別 | 非零數 | 比例 | mean|κ| |
|:-----|:------:|:----:|:------:|
| 完全對角 (g=g=g) | 432 | 32.2% | **12.99** |
| 兩維對角 | 807 | 60.2% | 2.10 |
| 完全混合 | 102 | 7.6% | — |

- 92.4% 非零項至少有兩個 index 喺同一 block
- 內/間耦合比 = 6.41
- **diag/off = 40.99 同參數無關** → block 結構係 κ 幾何內稟

### 2.4 純 κ_ggg Yukawa 本徵值

用 φ^(35-i) Kähler 參數（只限 κ_ggg 部分）:

| Block | pos | top3 本徵值 | top3 ratio |
|:-----:|:---:|:-----------:|:----------:|
| 0 (idx 0-11) | 9/12 | 5.53e9, 2.97e8, 1.67e8 | 33.2:1.8:1 |
| 1 (idx 12-23) | 7/12 | 1.21e5, 8.40e4, 5.75e4 | 2.1:1.5:1 |
| 2 (idx 24-35) | 10/12 | 1.63e3, 9.84e2, 3.60e2 | 4.5:2.7:1 |

**Between-block scale 自然出現**:
- Block 0/Block 1 top ≈ 46000
- Block 1/Block 2 top ≈ 75
- 來自不同 block 嘅 κ 非零密度差異（292:86:54）

---

## 三、核心瓶頸

### 3.1 Within-block hierarchy 太淺

SM 需要：

| Type | 最輕:中間:最重 | 階層幅度 |
|:-----|:-------------:|:--------:|
| up | 1:477:133077 | 10⁵ |
| down | 1:20:1548 | 10³ |
| lepton | 1:207:3483 | 10³ |

但 12×12 Yukawa block 嘅 top3 ratio 係 **33:1.8:1** — 無論用 φ^(35-i)、φ^(-i)、2^(-i) 定 γ_n 做 Kähler 參數，呢個 ratio 都係由 κ_ggg 結構固定，**唔受 Kähler 參數影響**（α 掃描證實 ratio 只由 κ_ggg 決定）。

### 3.2 γ_n 譜本身唔夠動態範圍

γ_n 譜範圍: 0.0051 (n=1) 到 4.0 (n=44)
γ_n max ratio: γ_44/γ_1 = **785**
SM up-type 需要: **133077** — 差 170 倍 ❌

γ_n² 就夠: max ratio = 616169 > 133077 ✅

### 3.3 γ_n 同 Yukawa 本徵值嘅關係未建立

γ_n 係 K_Chain 離散化頻率，Yukawa 本徵值係 CY₃ 交集數結構。兩者嘅聯繫係通過 **66 態投影（P̂ matrix）**，但呢個聯繫嘅具體機制未推導。

---

## 四、質量模型候選

### 4.1 γ_n² 模型（最準確嘅數值匹配）

每個 type 用不同 γ_n 三元組，質量 ∝ γ_n²：

| Type | 最佳 γ_n 三元組 | ratio | SM ratio | MSE |
|:-----|:--------------:|:-----:|:--------:|:---:|
| up | γ₁², γ₅², γ₂₂² | 1:612:153000 | 1:477:133077 | **0.002** |
| down | γ₄², γ₉², γ₃₂² | 1:20:1480 | 1:20:1548 | **0.0009** |
| lepton | γ₃², γ₁₂², γ₂₈² | 1:206:3450 | 1:207:3483 | **0.0004** |

**🔴 注意**: 呢個係數值匹配，唔係結構推導。γₙ² 嘅物理意義（質量 ∝ 強度²）未建立。

### 4.2 γ_n × Yukawa block 模型（最可能嘅結構）

```
質量型: m_{g,k} = M₀ × γ_{n(g,k)} × f_g
```

- f_g: 每個 block 嘅 overall scale（來自 block 間 κ 密度差異）
- γ_{n(g,k)}: 每個 type 嘅 within-type hierarchy（來自不同 K_Chain 模式）
- M₀: 全局質量尺度

**結構性 gap**: f_g 同 γ_n 嘅乘積點樣自然湧現，而唔係自由參數？

### 4.3 γ_n = Yukawa 本徵值模型

如果 Yukawa 本徵值直接等於 γ_n（某個對應關係），咁 12×12 block 嘅 12 個本徵值就係 12 個不同 γ_n 值。但實際 Yukawa 本徵值譜同 γ_n 譜冇直接對應 — 一個係 36 個數 [-360, 180]，另一個係 88 個數 [0, 4]。

---

## 五、開放問題（🔴 未解決）

| # | 問題 | 類型 | 詳情 |
|:-:|:-----|:----:|:-----|
| 1 | **Within-block hierarchy 來源** | 結構性 | 12×12 Yukawa 嘅 top3 ratio 太淺，需要額外機制 |
| 2 | **γ_n² 物理意義** | 機制 | 質量 ∝ γ_n² 嘅 CYTools/幾何起源 |
| 3 | **γ_n ↔ Yukawa 本徵值聯繫** | 投影 | 66 態投影點樣將 K_Chain 譜映射到 Yukawa 矩陣 |
| 4 | **Q_ij clusters → type 標籤** | 映射 | 3 clusters [81,70,34] 嘅精確 SM 對應 |
| 5 | **Block 2 負本徵值** | 符號 | φ^(35-i) 下 Block 2 Yukawa 全負，但 φ^(-i) 下正常 |
| 6 | **66 態 → SM 粒子標籤** | 映射 | 與 O67 連動，需先解決 O67 先有進展 |

---

## 六、下一步建議

```
🔴 優先 1: 建立 γ_n² 嘅結構推導
   - 質量 = M₀ × γ_n² × f_g 嘅第一性原理
   - 可能同 W-field 強度嘅二次型有關
   - 參考 O57 docs/12 (Dirac/Majorana sector)

🟡 優先 2: 解開 γ_n ↔ Yukawa 本徵值聯繫
   - 用 66 態投影將 K_Chain 譜映射到 Yukawa 矩陣
   - 睇每個 block 嘅 12 個本徵值對應邊啲 γ_n
   - 可能同 CYTools cycle volume 有關

🟡 優先 3: 同 O67 連動
   - 66 態 → SM 標籤先解決到「邊個本徵值對應邊個粒子」
   - 呢個係 O64 嘅前置條件
```

---

## 七、檔案

```
scripts/01_block_analysis.py   ✅ 3×12 block Yukawa 本徵值譜分析
scripts/02_gamma_n_candidates.py ✅ γ_n 三元組質量候選搜尋
scripts/03_sector_structure.py ✅ 66 態 ↔ 3×12 block ↔ Q_ij 3 clusters
scripts/04_full_spectrum.py   ✅ 全 Yukawa 譜 vs γ_n 對比
data/01-04_*.json              ✅ 結果
```

---

## 八、誠實標記

| 發現 | 狀態 |
|:-----|:----:|
| 3×12 block 結構 = sector-dependent 幾何實現 | 🟢 O61 確認 |
| 每個 block 嘅 top3 ratio 由 κ_ggg 固定 | 🟢 數值事實 |
| γ_n 本身唔夠動態範圍 (max 785 vs SM 133077) | 🟢 數值事實 |
| γ_n² 夠動態範圍 (max 616169) | 🟢 數值事實 |
| γ_n² 模型 MSE < 0.002 | 🟡 數值匹配，非結構推導 |
| Within-block hierarchy 太淺嘅原因 | 🔴 未推導 |
| γ_n² 嘅物理意義 | 🔴 未推導 |
| 66 態 → SM 標籤 | 🔴 與 O67 連動 |