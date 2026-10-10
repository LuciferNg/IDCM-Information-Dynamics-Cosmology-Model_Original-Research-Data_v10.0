# O188 docs/18 — R5 L2c：K 表係 ℝ³ 閾值矩陣（threshold family 定位）

**日期**: 2026-10-10（Route L2 第五輪）
**腳本**: `scripts/18_l2c_threshold_identity.py` — **6/6 PASS**（logs/18.txt）
**對象**: L2 殘留「incidence open door 但未構造 rank-3」

---

## 〇、一句話

**點解 R2/R3 嘅 causal-comparability 家族（{2,2,4,{4,5}}）永遠冇奇數 3，但 IDCM 嘅 K 表 sign_rank=3？**
因為 **K 表根本唔係 comparability/incidence 型矩陣** —— 佢係
```
K[i][a] = sign( ⟨ rot_ref(q_i, U₀), u_a ⟩ )
```
即 **ℝ³ 內積符號閾值（sign-projection / threshold）矩陣**：rows = 120 個群元素旋轉 reference axis 得嚟嘅 ℝ³ 向量，cols = 62 個 axes。
**By construction sign_rank(K) ≤ 3**（Gram factor rank ≤ 3）。

**LQG 側對應物 = spin network boundary 嘅 area-normal 向量 n_i ∈ 𝕊²** —— 互閾值表 T[i][j] = sign(⟨n_i, n_j⟩) 係**同一家族**（ℝ³ threshold）。

⟹ **L2 缺失嘅 rank-3 結構唔喺因果序（comparability）亦唔喺 cell incidence —— 佢喺「幾何閾值家族」（geometric threshold family），而 IDCM 嘅 evaluation 表同 LQG 嘅 normal frame 都屬於呢個家族。**

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| O1 | K slice（30 群元素 × 62 axes）：entries ∈ {−1, 0, +1}；**0 = 精確正交 dot=0**（O222 真實 K 亦有） | ✅ |
| O2 | 閾值身份驗證：K = sign(⟨rot, axis⟩)（16 樣本全對）；factor 分解 R（30 vec, ℝ³）＋ U（62 vec, ℝ³） | ✅ |
| O3 | **sign_rank ≤ 3 by construction**：K = sign(A·Bᵀ)，A,B ∈ ℝ³ ⟹ rank(ABᵀ)≤3 ⟹ sign_rank≤3 | ✅ |
| O4 | LQG normal frame：16 個 𝕊² normals（12 icosahedron + 4 extra）⟹ T = sign(⟨n_i,n_j⟩) 同一 threshold 型 ⟹ sign_rank≤3（同一 factor-rank bound） | ✅ |
| O5 | **Contrast**：comparability/incidence 同 {0,±1} 字母但 **唔係**固定 ℝ³ 內積符號（編碼 reachability / cell membership）⟹ 解釋佢哋嘅 sign_rank 家族永遠唔會出現奇數 3 | ✅ |
| O6 | **判決**：L2 對應候選 = GEOMETRIC THRESHOLD FAMILY；機制層對應（共享家族），**唔係 elementwise**（冇 bijection 120↔𝕊²） | ✅ |

## 二、結構意義（★ O222 嘅 sign_rank=3 真正根源）

- **O222 嘅「sign_rank(K) = 3」由 600/600 completion 認證，但唔係原因——係數值見證**。真正原因：K 表本身就係 ℝ³ 閾值投影（group action 嘅線性輸出），rank-3 係 **構造性必然**。
- 呢個解釋咗一個懸案：R2/R3 點解喺「序關係」度搵唔到 3 —— **搵錯家族**。causal-layering 係 order-reachability（冇固定幾何），incidence 係 cell membership（稀疏）——兩者都唔係 threshold。
- **LQG 側同一件事**：spin network 邊界 data = 每條 edge 嘅 normal vector 喺 𝕊²（area-normal 幾何由 intertwiner 相干態定義）—— 佢哋嘅互閾值表自然 rank≤3。即 **LQG 本身就內建 rank-3 threshold 結構**（3 維空間幾何！），而 IDCM K 表撞正同一數學型。

## 三、判決

- **L2 缺口狀態更新**：
  - 🔴 comparability 家族（R2/R3）：否證維持（冇奇數 3）
  - 🔴 incidence（R4）：中性（sparse 容許低秩，冇構造）
  - ✅ **threshold 家族（R5）**：**對應候選定位** —— IDCM evaluation K ∧ LQG normal frame T 都係 ℝ³ sign-projection 表，sign_rank≤3 by construction；L2嘅「3」唔喺組合序入面，而喺幾何閾值入面
- **未閉合**：機制層對應（共享家族）已確立；elementwise 對應（120 群元素 ↔ 16+ normals 嘅具體符號映射）**冇建立，亦唔 claim**（誠實）。
- **下一步候選**：為 threshold 家族建立「上下文」—— 例如 O222 嘅 K 表行 120 同二十面體 normals 12 嘅關係（120 = 10×12？）—— 但係呢個容易落入 numerological，除非有 operator 身份。

## 四、同 R2–R4 對比
- R2 4-simplex comparability rank 4＞3（真負結果）→ R3 維數序列冇 3（類型不匹配）→ R4 incidence 中性（open door）→ **R5 threshold 家族：搵到 rank-3 嘅正確「家族」** —— L2 由「排除了錯誤家族」到「定位正確家族」。