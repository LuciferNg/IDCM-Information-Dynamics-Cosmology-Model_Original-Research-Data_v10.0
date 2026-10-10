# O188 docs/06 — R2 L2-深推：causal-set 橋樑（sign-rank 3 ⟺ 2+1 分解）＋ 4-simplex 否證

**日期**: 2026-10-04（Route L2 深推）
**腳本**: `scripts/06_l2_causal_bridge.py` — **3 PASS + 1 記錄 REFUTED**（logs/06.txt）
**對象**: 🔴 缺口 L2「IDCM rank-3 與 spin-foam causality 冇形式化定理」

---

## 〇、一句話

試圖建形式橋樑：「comparability sign_rank ≤ 3 ⟺ causet 係 2+1 可分解」。
結果：**IDCM chain（全序）確實 fit rank-3 類；但 spin-foam 4-simplex 因果 split（3+2）被精確否證** —— sign_rank = 4 > 3。
橋樑喺 4-simplex 層面被 REFUTE；L2 缺口由「冇定理」收窄為「**具體障礙**」。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| G1 | 全序 44-chain comparability：staircase sign_rank = 2（≤3 成立） | ✅ |
| G2 | **4-simplex 因果 split（2 past + 3 future，5 tetra）：sign_rank = 4 > 3** 全 256 completion 窮舉 | 🔴 REFUTED |
| G3 | 隨機 poset n=8：91% raw rank > 3（rank≤3 唔係 generic） | ✅ |
| G4 | 橋樑狀態：只對 IDCM chain/total-order 成立，4-simplex 唔成立 | ✅（誠實） |

## 二、結構發現（G2 嘅精確內容）

- **IDCM chain = 全序 = 2+1 可分解**（rank 2 staircase）⟹ IDCM 嘅 sign_rank(K)=3（O222）確實坐喺「低秩因果」類。
- **4-simplex 因果 split（2+3）需要 rank 4**：兩塊（past 2 tetra, future 3 tetra）之間全可比、塊內不可比 → **3+2 分解** —— 唔係 2+1。
- ⟹ **若 IDCM 因果秩 3 對應 causet 嘅「2+1 分解」類，則 4-simplex vertex 唔屬於該類**；形式定理只能係：

> **sign_rank(comparability) ≤ 3 ⟺ causet 係 2+1 可分解（非 3+2 或更複雜）**

而 4-simplex 最低因果 split 就係 3+2 → 自然 rank 4。

## 三、判決

- **L2 缺口收窄（未閉合）**：由「冇形式化定理」→「**候選定理被 4-simplex 層明確否證，缺口有精確結構内容**」。
- **誠實標記**：呢個 REFUTED 係**真負結果**，唔係模型 bug —— 5-vertex 2+3 split 嘅 comparability 在所有 ±1 completion 下 min rank = 4（窮舉 256 種）。判準冇放寬。
- **後續候選**（未完成）：若 spin network 嘅 causal structure 用「面（三角形）」而唔係「tetra」做節點，可能會唔同 —— 留做 L2-3 方向（本輪唔開）。

## 四、同 O222 嘅連結

- O222：sign_rank(K) = 3（62×62 correlation 表，M3 閉合）。
- 本輪 G1 顯示「鏈/全序」類烏龜係 rank-2/staircase；但 IDCM K 表唔係全序 —— **K 嘅 rank-3 與 causet 嘅 rank-3 係兩個唔同嘅矩陣秩**（correlation vs comparability）—— 呢個差別喺 G4 已明確標記。