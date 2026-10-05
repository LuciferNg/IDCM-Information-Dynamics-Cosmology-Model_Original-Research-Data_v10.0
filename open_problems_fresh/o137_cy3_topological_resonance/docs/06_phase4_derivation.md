# O137 — Phase 4 推導記錄: P_f 拓撲重疊算子 (方向乙)

**狀態**: 🔴 證偽 (P_f 重疊算子冇選擇律; 質量譜冇 match SM)
**日期**: 2026-08-30
**檔案**: scripts/10-13 + docs/06_phase4_derivation.md

---

## 0. 方向乙目標 (用戶指示)

從 CY₃ 幾何正向推導 P_f 嘅拓撲選擇律:
1. P_f(n) = Σ_ijk κ_ijk·c_n(i)·c_n(j)·c_n(k) 零模波函數重疊算子 (零參數)
2. SR-ideal 代數消去律: 非物理模式 (n=15,21,25,35) 因幾何相消自然歸零
3. 解決 L 類內選擇 (開放問題 #1) + τ (n=20) 幾何歸宿 (開放問題 #2)
4. 質量階層: m_f = M₀·γ_n·P_f(n) (+e^{-S_inst} 融合)

---

## 1. ★ 對應修正 (Phase 4 重要發現)

**CYTools divisor label = 1-36 (1-based) = pt index = mode index (1-based)**

| 項 | 發現 |
|:---|:---|
| prime_toric_divisors() | **(1, 2, ..., 36)** — 1-based labels |
| divisor_basis() | [1,2,5,6,9,...,36], 缺 [0,3,4,7,8] |
| intersection keys | 涉及 **37 個 indices (0-36)** |
| κ index 0 | = pt 0 = origin (star apex), K[0,0,0] = −360, |κ| 強度最大 (1984) |
| JSON 36³ | = 完整 37³ 嘅 (0-35) 子張量 (0 entries 差別) — 冇截斷, 只係冇存 index 36 |
| **正確對應** | **κ index i ↔ pt i ↔ mode i (1-based, i=1..36)** |

**修正**: 之前 Phase 2-3 scripts 用 κ index 0-35 配 c_n(1..36) 有 1-offset 錯;
正確應該用 κ index 1-36 (prime divisors) 配 c_n(1..36)。Phase 2 嘅
「mode n ↔ pt n」映射仍然正確 (sr 36 點 = pt 1-36 確認)。

**SR-ideal 對應問題**: sr pairs (1-based pt) ↔ κ index 相同 1-based。
κ 非零 pairs (175 個, 0-based) vs sr pairs: 重疊 88 個 — **κ 有 88 個非零
entries 喺 sr 宣稱「冇相交」嘅 pairs 上** → 或者 (a) κ index 同 pt 對應
唔係恆等, 或者 (b) sr ideal 唔直接反映喺 κ 零結構 (SR ideal 係
Stanley-Reisner ring 嘅 quotient 結構, 唔係 divisor pair 相交)。

**Z₃ 不變性: False** (671/3456 差異) — κ 唔尊重 3×12 block 嘅 Z₃ 對稱,
所以「Z₃ parity 消去」機制唔可能 work。

---

## 2. P_f 重疊算子 — 8 個組合全部無選擇律 🔴

### 測試矩陣

| 版本 | 波函數 | 對應 | 結果 |
|:---|:---|:---|:---|
| V_cos | cos(2πni/88), i=1..36 | κ 0-35 (0-based) | 冇 |
| V_sin | sin(πni/88) | κ 0-35 | 冇 |
| V_abs | cos × \|κ\| | κ 0-35 | 冇 |
| H1 × cos | cos, shift=1 | κ i↔mode i+1 | 冇 |
| H2 × sin | sin, shift=0 | κ i+1↔mode i | 冇 |
| **修正 × sin** | sin(πni/88), i=1..36 | **κ 1-36 (1-based, 正確)** | **冇** |
| **修正 × cos** | cos(2πni/88) | κ 1-36 | **冇** |
| **修正 × chain** | sin/√γ (正規化本徵) | κ 1-36 | **冇** |

### 修正對應後嘅選擇律統計

| 版本 | 候選排名 (of 44) | 玻色子/候選分離 |
|:---|:---|:---|
| sin | [27, 38, 25, 5, 1, 22] (b 排 1, τ 排 5, e/μ 排尾) | False |
| cos | [32, 39, 4, 18, 41, 34] (s 排 4, 其他尾) | False |
| chain | [0, 9, 17, 30, 36, 20] (e⁻ 排 0 = 最大 35271!) | False |

**冇任何版本產生「候選突出 + 玻色子抑制」**。n=15, 21, 25, 35 (方向甲風險
模式) 嘅 P_f 都唔係特別零 (n=15: P_sin=+65.5, n=21: +44.4, n=25: −175.8,
n=35: −191.3)。

### 質量譜 (m_f = M₀·γ_n·P_f)

| 粒子 | SM 質量 | P_sin 預測 | P_cos 預測 |
|:---|:---:|:---:|:---:|
| e⁻ | 0.511 MeV | 1.82 MeV (3.6×) | 13.4 MeV (26×) |
| μ⁻ | 105.7 MeV | 103.2 MeV (2.4%) | 469 MeV (4.4×) |
| τ⁻ | 1776.9 MeV | 384 MeV (0.22×) | — |
| s | 95 MeV | 377 MeV (4×) | — |

**μ⁻ 意外命中 2.4%** (M₀·γ₇·P_sin(7) = 103.2 vs 105.66 MeV) — 但呢個係
單一命中 (density artifact 嫌疑, 同 Phase 3 嘅 0.4% 一樣需要 order statistics
檢驗), 且其他 5 個都唔 match。**唔可以當閉合。**

---

## 3. Phase 4 結論

### 已確立 ✅
1. **對應修正**: κ index i ↔ pt i ↔ mode i (1-based); CYTools prime divisors
   = 1-36; κ 完整係 37³ (index 0 = origin apex)。
2. **Z₃ 不變性 False** — 3×12 block 嘅 Z₃ 對稱唔係 κ 嘅對稱,
   Z₃ parity 消去機制排除。

### 證偽 🔴
3. **P_f 重疊算子 (8 版本) 全部冇選擇律** — 候選唔突出, 玻色子冇抑制,
   n=15/21/25/35 唔歸零。
4. **質量譜冇 match SM** (μ⁻ 單一 2.4% 命中係 density artifact 嫌疑)。
5. **SR-ideal 代數消去唔 work** — κ 有 88 個非零 entries 喺 sr pairs 上。

### 結構性結論 🟡
6. **模式選擇 (充分性) 唔係 CY₃ κ 幾何算子決定** — 無論波函數形式或對應,
   κ 重疊都產生唔到選擇律。呢個同 Phase 1-3 一致: 選擇係 chain-side
   離散結構 (v₂(n) 子環 + 自旋結構), CY₃ 幾何只提供質量比例 (P_f 數值),
   唔提供模式存在性。

---

## 4. O137 整體狀態 (Phase 1-4)

| 項目 | 狀態 | 內容 |
|:---|:---:|:---|
| A 耦合方程 | ✅ | O80 → M⁴×CY₃, P̂ 投影, parity 選擇律 |
| B 駐波條件 | ✅ | 費米子反週期 n·L ≡ 44 (mod 88) |
| C 特徵值流 | ✅(必要) | v₂(n) ≤ 2, 純玻色子 {8,16,24,32,40} 排除 |
| L 類內選擇 | 🔴 | 特徵值匹配 = 密度效應; P_f 重疊算子證偽 |
| P_f 質量階層 | 🔴 | 重疊算子質量譜冇 match SM |

**已閉合 (零參數, 結構性)**: 費米子必要條件 v₂ ≤ 2 + 純玻色子排除。
**未閉合**: L 類內選擇 (6 候選中邊個係邊個) + P_f 數值 (3.6/15.5/37) 來源。

**開放問題更新**:
- #1 L 類內選擇: κ 重疊算子排除 → 需要 chain-side 更細結構 (mode 算術性質)
  或者量子調和/鏡像對稱對象
- #2 n=20 (τ): 所有幾何算子都 miss — 佢嘅唯一結構係 v₂(20)=2 (L=11 類)
- #3 n=33 雙重費米子 + n=11 鏡像區分: 開放

---

*scripts: 10_pf_overlap_operator.py, 11_pf_variants_sr.py, 12_hypothesis_scan.py,
13_pf_correct_full_kappa.py*
