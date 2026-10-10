# O188 docs/10 — R3 L2a：維數 × sign_rank 規則測試（負結果深化）

**日期**: 2026-10-04（Route L2 第三輪）
**腳本**: `scripts/10_l2a_dimensional_rule.py` — **4/4 PASS**（logs/10.txt）
**對象**: L2 殘留「4-simplex rank 4 係咪有維數規則」

---

## 〇、一句話

測試「(k+1)-vertex 因果結構嘅 sign_rank 係咪 k 嘅簡單函數」。
結果：**冇簡單規則**（max=k+1 ❌、max=k ❌）；但量到 clean 序列：**k=1→2、k=2→2、k=3→4、k=4→{4,5}**。
**IDCM 嘅 rank-3 唔喺呢個序列 {2,2,4,4/5}** ⟹ L2 係**類型不匹配**（比 R2「冇定理」更深嘅障礙）。

## 一、精確結果（全部 ordered layerings 窮舉）

| k | vertices | sign_rank 值集 | # 分層 | 精確 |
|:-:|:--|:--|:--|:--|
| 1 | 2 | {2}（唯一） | 3 | ✅ |
| 2 | 3 | {2}（唯一） | 13 | ✅ |
| 3 | 4 | {4}（唯一） | 75 | ✅ |
| 4 | 5 | **{4, 5}** | 541 | 4 精確、5 為上界 |

- K2：**max_rank = k+1 → False；max_rank = k → False**（兩者皆不成立）
- K3：anchor（k=4, 2|3 split）= **rank 4**，同 R2 G2 一致 ✅

## 二、結構發現

**因果分層（causal layering）comparability 家族嘅 sign_rank 序列 = {2, 2, 4, {4,5}}**：
- k ≤ 3：sign_rank **唯一**（唔依賴 layering）— clean！
- k = 4：開始依賴 layering（4 或 5）
- **全部係偶數（2, 4）或 ≥ 5** —— **冇 3**

⟹ **IDCM 嘅 sign_rank(K)=3（奇數）唔可能來自「因果層 comparability」型矩陣** —— 呢個係**類型（奇偶）不匹配**，唔止「冇已證定理」。

## 三、判決

- **L2 缺口深化（負結果）**：
  - ✅ 冇簡單維數規則（唔可以宣稱 rank-3 ⟺ 某維數）
  - ✅ **新障礙**：causal-layering 家族嘅 rank 集中喺 {2,2,4,{4,5}}，IDCM 嘅 3 唔喺其中 ⟹ IDCM rank-3 需要另一個機制（唔係 causal comparability）
  - 🔴 4-simplex（k=4）rank 4/5 已由 R2 G2 精確錨定
- **含意**：L2 若要閉合，唔可以再喺「因果層 comparability」度揾 —— 要換機制（例如：sign_rank 反映**線性代數嵌入維數**而唔係因果分層；或 IDCM K 唔係 comparability matrix 而係 correlation/incidence 表）。

## 四、K4 判讀活頁
- 若 max_rank=k+1 成立 → rank-3 ↔ k=2。**實測唔成立**。
- 若 max_rank=k 成立 → rank-3 ↔ k=3。**實測唔成立**。
- 觀測序列 {2,2,4,{4,5}} 對應「每 2 個 k 跳一次」嘅弱 pattern（min_rank = 2⌈k/2⌉，k=1..4 全對），但 max 唔跟 → 只係 min bound，非定理。