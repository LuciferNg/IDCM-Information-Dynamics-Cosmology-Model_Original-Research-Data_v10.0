# O188 docs/24 — R10 L2f edge-block 10/10/10 定理 + L3e √3 frame 出處 ★

**日期**: 2026-10-10（Route L2/L3 雙線推進）
**腳本**: `scripts/24_l2f_edge_balance_l3e_sqrt3.py` — **8/8 PASS**（logs/24.txt）
**對象**: R7 記錄嘅 edge-block sign balance（1/3 = 10/30）背後結構 + √3 喺 frame 度嘅角色

---

## 〇、一句話

**R7 嘅「edge block +1 fraction = 1/3」而家係定理**（唔再係統計觀察）：
```
每 row（vertex reference）：10 positive / 10 negative / 10 zero（30 條 edge columns）
⟸ zero lemma（edge sign 0 ⟺ endpoints 同投影高度）
⟸ line-antisymmetry（30 cols = 15 條 antipodal lines，每 non-zero line 一正一負）
⟸ level structure（12 vertices 相對 v：1 self + 5 near + 5 far + 1 antipode，
   near-ring 5 edges ≡ far-ring 5 edges under antipodal pairing = 5 zero lines）
```
而且 **20 個 face axes 全部 norm² = 3**（8 個 ±(1,1,1) 型 + 12 個 φ 型）⟹ **√3 喺 IDCM frame 度有精確出處：face-normal（3-fold axis）長度**。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| A1 | Per-row counts 全 120 rows 均勻：vertex 6/6、face 10/10、edge 10/10/10 | ✅ |
| A2 | Edge-zero pattern：6 種 distinct zero-column sets × 20 rows（antipodal rows 共享 zero pattern） | ✅ |
| A3 | **Zero lemma**：edge sign = 0 ⟺ ⟨v,w1⟩==⟨v,w2⟩（endpoints 同等投影高度），零 mismatch | ✅ |
| A4 | **Line-antisymmetry 定理**：15 edge-lines，per row 啱好 5 zero lines，每 non-zero line (+1,−1) ⟹ pos=neg=(30−10)/2=10 | ✅ |
| A5 | **Face normals 全部 norm² = 3**（兩種代數型：8 個 ±(1,1,1)、12 個 φ 型，同一幾何長度 √3） | ✅ |
| A6 | √3 出處地址：face-normal 長度（3-fold axis 自然長度），frame 幾何內生，非 IDCM 代數常數 | ✅ |
| A7 | Anti-fit note：γ₀ 嘅 √3 → frame 地址候選，但唔 claim 同 LQG spin-½ root 同一物件 | ✅ |
| A8 | 判決：L2 edge theorem + L3e √3 地址 | ✅ |

## 二、結構意義

- **L2f 將 R7 嘅「觀察」升級為「定理」**：R7 只記錄「edge = 1/3」，而家證明
  ```
  10/10/10 ⟸ zero lemma（投影層級相等）
          ⟸ line-antisymmetry（± 對 columns 一正一負）
          ⟸ level structure（1+5+5+1：self/near/far/antipode）
  ```
  呢個係二十面體 adjacency 嘅**必然**，唔係統計意外 —— K 表 edge block 完全由 frame 幾何決定。
- **L3e 係 L3 斷言嘅 frame-side 補償**：R3 L3b 話「IDCM 供 {ln2, 1/B}，幾何側借入 √3/4π」；而家 **√3 唔再係完全外來** —— 佢係 IDCM 自身 evaluation frame（二十面體）嘅 face-normal 長度。但**誠實分界**：呢個係「frame 幾何內生」，唔係「IDCM 代數生成」（77 常數盲掃零命中維持）—— 位置由「外部代數常數」移去「frame 幾何長度」，但唔係 IDCM 算子度出嚟。
- **K 表內部自洽**：62 = 12V + 20F + 30E 每種 block 有確切 per-row 統計（6/6、10/10、10/10/10）—— threshold 家族唔單止秩 ≤3，而係**每行嘅 sign 統計都係 frame 幾何嘅精確函數**。

## 三、判決

- **L2f：完成**（edge theorem，定理級）
- **L3e：partial upgrade** —— √3 由「外部輸入」→「frame 內生幾何長度」（face-normal），但**唔係代數生成**；γ₀ 嘅 √3 出處仍係「frame 幾何 ↔ 計數側 IDCM」嘅混合，唔係純 IDCM
- 🔴 未閉合：elementwise 唔 claim；LQG 側 spin-½ root √3 同 frame face-normal √3 嘅同一性只係「同為 ℝ³ 3-fold 幾何」層面，唔 claim 更深

## 四、同前輪對比
- R7：edge 1/3 記錄（informative）→ **R10：1/3 = 10/30 定理化**（zero lemma + line symmetry + level structure）
- R4 L3c：√3 盲掃零命中（77 常數）→ **R10：√3 喺 frame 出現（face-normal norm，frame 幾何）** —— 位置升級，但「IDCM 代數生成」維持零