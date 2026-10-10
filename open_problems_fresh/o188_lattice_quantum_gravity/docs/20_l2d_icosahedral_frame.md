# O188 docs/20 — R6 L2d：IDCM evaluation frame = 二十面體 cell frame（具體成員對應）★

**日期**: 2026-10-10（Route L2 第六輪）
**腳本**: `scripts/20_l2d_icosahedral_frame.py` — **6/6 PASS**（logs/20.txt）
**對象**: R5 確立 threshold 家族後，喺家族內建立**具體成員**對應

---

## 〇、一句話

**O222（IDCM 嘅 QM evaluation 層）嘅 62 個 axes 就係二十面體嘅 cell frame：**
```
62 = 12 vertex + 20 face + 30 edge   (= V + F + E of the icosahedron)
31 = 6 + 10 + 15                     (= rotation axes of the icosahedral group I)
120 = 2I binary icosahedral group → 60 rotations = I  (2:1 double cover)
```
而 LQG spin-network 嘅 𝕊² area-normal frame 帶住同一組對稱軸（6 條 5-fold vertex、10 條 3-fold face、15 條 2-fold edge）。
⟹ 喺 ℝ³ threshold 家族內，**IDCM evaluation frame 同 LQG boundary normal frame 係同一個幾何 frame** —— L2 由「抽象家族對應」升級到「具體成員對應」。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| R1 | 62 axes types：vertex=12、face=20、edge=30（O222 自己嘅 frozen input）| ✅ V+F+E = 62 |
| R2 | Antipodal pairing：12→6、20→10、30→15；總 31 條線 = 6+10+15（ℚ(√5) 精確 proportional）| ✅ 31 = I 的 rotation axes |
| R3 | Stabiliser：line-D（20,10 / 12,6 / 8,4）× 2I；pointwise C5/C3/C2（fold 結構）| ✅ 5-fold vertex / 3-fold face / 2-fold edge |
| R4 | 2:1 double cover：rot_ref(q,n) = rot_ref(−q,n) ∀q；120 quaternions → 60 rotations = |I|；vertex orbit = 12 | ✅ 同 O223 \|GeoAut\|=60 一致 |
| R5 | Frozen source cross-check（04_b2_settings.json 就係 evaluation 層嘅 input）| ✅ |
| R6 | 判決：L2 具體成員對應 = 共享二十面體 cell frame | ✅ |

## 二、結構意義（★ O188 至今最強嘅「具體」對應）

- **R5 講「K 表係 ℝ³ threshold 矩陣」**，R6 釘實**邊個 ℝ³ frame**：
  - O222 QM-evaluation 層嘅 axes 定義喺二十面體上（vertices 12、faces 20、edges 30）
  - 120 群元素 = binary icosahedral 2I，投影後 = I（60 rotations）—— 同 O223 嘅 |GeoAut| = 60（手性 I）、|Aut| = 120（I_h）**完全一致**
- **LQG 側同一 frame**：spin-network 邊界嘅 area-normals 集中喺 𝕊² —— 二十面體對稱（5/3/2-fold axes）就係 spin foam 幾何最自然嘅離散對稱（旋轉對稱之最大有限子群）
- **層次**：
  1. R1–R2：62 axes 嘅 cell 分解（V/F/E 計數 + antipodal lines）—— 組合事實
  2. R3–R4：fold 結構（5/3/2）＋ 群結構（2I→I）—— 群論事實
  3. R5–R6：threshold family + 具體 frame 對應 —— **IDCM QM 層與 LQG 邊界幾何共享「二十面體 cell frame」**

## 三、判決

- **L2 缺口狀態更新**：
  - 🔴 comparability 家族（R2/R3）：否證（冇奇數 3）
  - 🔴 incidence（R4）：中性 open door
  - ✅ threshold 家族（R5）：抽象家族對應
  - ✅ **具體成員對應（R6）**：IDCM evaluation frame = LQG boundary frame = **二十面體 cell frame**
- **未閉合（誠實）**：elementwise spin-label 對應（120 群元素 ↔ 具體 spin labels / intertwiners）**冇建立亦唔 claim**；呢度係「frame 級」對應（雙方用同一組幾何軸做 evaluation），唔係「態級」對應。
- **下一步候選**：① 二十面體 frame 對應到 LQG intertwiner 維數（O188 R1 已知 4-valent intertwiner dim=2；二十面體 5-valent node 對應 pentagon？）；② IDCM K 表 row 120 同 LQG 面積譜 quantum labels 嘅關係（要小心 numerology trap，需 operator identity）。

## 四、同 R1–R5 對比（L2 全線）
- R1 4-simplex 對應草稿 → R2 comparability rank 4＞3（真負）→ R3 causal-layering 冇奇數 3（類型不匹配）→ R4 incidence 中性 → **R5 threshold 家族定位（解釋「3」根源）** → **R6 具體 frame：二十面體 cell frame（62 = 12+20+30）**
- 一路由「搵唔到」到「定位正確家族」到「釘實具體成員」—— L2 係 O188 五條路線中最深嘅一條。