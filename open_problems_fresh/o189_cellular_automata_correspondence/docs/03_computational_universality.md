# O189 docs/03 — 計算能力（C3）：O222 求值語義 vs CA class IV 通用性

> **2026-10-10 | R1 | 產物: `scripts/03_computational_universality.py`（13/13 PASS）、`data/03_computational_universality.json`、`logs/03_computational_universality.out`**

---

## 一、結論（先寫死——含起手式聲稱之更正）

🔴 **更正起手式聲稱**：O189 SESSION_START 原文寫「O222 求值語義層已證 IDCM 可通用計算 — 這比 CA class IV『可通用』更強」。本輪**機械審計**（掃 O222 全部非凍結 docs，模式 `通用計算|Turing|universal|universality|圖靈`）：**零條**真通用性/圖靈陳述。O222 唯一含「通用」字樣嘅係「**機器語義之通用性質**」（E1/E2 超 CHSH 2 係 ledger/memo 動態嘅 artifact 歸因，非通用計算證明）。⟹ **該聲稱 REFUTED-as-written**（屬假設，非 O222 成果）。

🟢 **C3 實答**：
1. O222 已證嘅係**資源界限確定性語義**（force 單值、memo 命中≡冷算、62²=3844 對、sign_rank ≤ 3 LHV 分類）——**與 Turing 完備性無關，反而係其反面（bounded）**；
2. IDCM 88-ring 晶格動力學係**有限維線性 unitary**：頻率比 ω₁/ω₂ = 1/(2cos(π/88)) 無理（Niven）⟹ 軌道**準週期**（2000 步內最小回歸距 0.9966，即從不精確回歸）；**可逆、等距、零資訊損失**；
3. 對照：Rule 90（線性 CA）核維 2、軌道 preperiod/period = 3/248（資訊毀滅）；Rule 110 單 bit 擾動非單調擴散（1→max 5 bits）、Hamming 距離**唔守恆**（無度量等距）；
4. **分類**：IDCM 88-ring = **class II⁺（準週期、線性、可逆）**，**非 class IV**。Wolfram class IV 通用性（Rule 110, Cook 2004 經 cyclic tag system）需要：**(a) 非線性**（glider 碰撞邏輯）、**(b) 無界格**（TM 帶）、**(c) 可配置嵌入**——晶格層三者皆無。

## 二、三層區分（關鍵——唔可以混）

| 層 | 對象 | 計算能力 | 狀態 |
|:--|:--|:--|:--:|
| **L1 晶格動力學** | 88-ring 線性 unitary（本輪） | class II⁺：bounded、可判定、無 halting problem | 🟢 本輪已證 |
| **L2 求值語義** | O222 thunk/force/memo 機器 | 資源界限確定性；**冇** Turing 證明 | 🟢 審計確認 |
| **L3 模擬嵌入** | 任意系統可互相模擬（圖靈完備對圖靈完備） | 平凡真，**唔構成結構對應** | 🟡 排除項 |

起手式原文把 L2 誤升為「通用計算」——L2 實際只係 O222 已凍結嘅**有限資源語義**（O228 再證 k_min ≥ ⌈log₂ m⌉ 資訊下界）。

## 三、結果表

| 檢查 | 值 | 狀態 |
|:---|:---|:---:|
| O222 文件真通用性陳述數 | **0**（非凍結 docs 掃描） | 🔴 更正 |
| ω₁/ω₂ = 1/(2cos(π/88))（CF 24 項不止） | 無理（Niven） | 🟢 |
| 44-mode 流 2000 步最小回歸距 | 0.9966 @ t=1841（零精確回歸） | 🟢 準週期 |
| 有理 2-mode 玩具對照 | ‖c(2π)−c₀‖ = 2.6e-16（精確回歸） | 🟢 對照 |
| Rule 90 環軌道 | preperiod 4, period 248 | 🟢 |
| IDCM 位置 Shannon 熵（單源擴散） | 5.86→6.03 bits（< log₂88 = 6.46） | 🟢 |
| IDCM 等距 ‖U(a−b)‖ | 0.0014142136 → **0.0014142136**（精確） | 🟢 |
| Rule 110 單 bit 擾動 | hdist 1→max 5，非恆定 | 🟢 非等距 |
| 88-ring 離散步容量 | 2^88（有限） | 🟢 |
| O228 資訊下界 k_min ≥ ⌈log₂ m⌉ | 識別全 88-ring 態 ≥ 88 bits | 🟢 引用 |

## 四、判讀

1. **無界 vs 有界**係分水嶺：Rule 110 嘅不可判定性（Cook 2004：某 bit 序是否出現、是否終成週期，皆**形式上不可判定**）來自**無界 tape + 非線性 glider**；88-ring 係有限態（可完全列舉 ⟹ 一切問題可判定）。IDCM **晶格**唔可能係 class IV 通用——但 IDCM **理論整體**（含 O222 語義層 + 無界鏈族）另論，本輪唔聲稱。
2. **準週期 vs 週期**：CA class II 係週期（有限態必然）；IDCM 線性 unitary 因**無理頻率比**係準週期（更「rich」）但仍屬可逆、零熵增一族——**唔係** class III（混沌，正 Lyapunov）/class IV（計算）。
3. **資訊守恆嘅嚴格形式**：IDCM 係 Hilbert 空間等距（unitary）；Rule 90/110 係非單射（核/碰撞）⟹ 每步有資訊瓶子。這條線本身即係 class 分類嘅拓撲不變量（單位 vs 非單射）。

## 五、等價 / 模擬 / 類比

- **等價**：🔴 否（class II⁺ vs class IV；可逆 vs 不可逆）
- **模擬**：🟢 平凡（排除）
- **類比**：🟡 兩者都係離散時步 + 局部規則家族（CHL 家族），但 IDCM 側係線性/可逆/有限維，ECA 側係非線性/不可逆/無界可擴——**計算類唔同**

## 六、未閉合（🔴 殘餘，唔阻塞本輪）

1. IDCM **理論整體**（O222 語義層 + 無界鏈 refinement，O221 細化流）之計算類——本輪只答**固定 88-ring**。
2. sign_rank ≤ 3（O222）對「計算類」嘅約束力（LHV 類 vs 通用類之關係）——留 O224/O228。
3. Rule 110 通用性喺 Lean 之形式化仍未無條件（社群狀態，2026）；本輪引用 Cook 2004 數學證明為權威。

## 七、檔案

- `scripts/03_computational_universality.py`：13/13 PASS
- `data/03_computational_universality.json`
- 引用：Cook 2004（*Complex Systems* 15(1):1–40，DOI 10.25088/ComplexSystems.15.1.1）；O222（語義層）；O228（資源幾何）；O221（細化流）