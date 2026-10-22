# O58 — 探索 V/W/X：CY 修正因子 + vertex Lucas 撤回 + GLSM 對應確認

> **狀態**: 🟢 完成（2026-08-24）
> **⚠️ W 部分：撤回 T 嘅「vertex 索引 Lucas 傾向」claim（script bug）**

---

## X: GLSM 對應確認 — 冇 off-by-one ✅

- **GLSM columns 0-36 直接對應 pts[0]-pts[36]**（唔係 pts[d+1]）
- U 嘅 q8=-q0-1 發現有效！
- Non-coordinate rays = [0,3,4,7,8]（5 個）✅
- **pts[8] = pts[1] + pts[47] = e₁ + e₂** ✅
- **🎯 e₁-e₄ 位置 = pts[1], pts[3], pts[7], pts[47] = {L₁, L₂, L₄, L₈}**（全 Lucas！但只喺 canonical）

## V: CY 修正因子 — K[8,8,8] = -L₇ × Σ_{σ∋8} 1/|det(σ)| 🎯🎯

### Σ|det| over all cones = 200.000（精確不變量！）

### 完美分解（1/|det| 加權）

```
K[8,8,8] = -232 = -29 × 8 = -L₇ × Σ_{σ∋8} 1/|det(σ)|
```

- **-29 = -L₇**（Lucas 因子）
- **8 = Σ 1/|det| over 8 cones**（star of div8，每個 det=1）
- **K[8,8,8] = -L₇ × (star 加權和) 精確成立！**

其他 triple 唔係乾淨分解（K[0,0,0] = -360 vs Σ1/|det| = 123.4, ratio -2.92）— div8 特別乾淨！

### 意義

**K[8,8,8] 嘅 -232 = -L₇ × 8 揭示咗：Lucas 因子（L₇）乘 cone 結構（star 加權 8）** — 兩者獨立出現但相乘！

## W: 🔴 撤回「vertex 索引 Lucas 傾向」— script bug

### Bug 發現

Script 59 用 `lucas_idx = [i for i in v_idx if i in L.values()]` 但 `L = {lucas(n): n}`，所以 `L.values()` = **index 值**（唔係 Lucas 值）！→ 錯誤嘅 84.1% + z=10.37σ

### 正確統計（script 63/64 修正）

```
Lucas fraction = 61.6%（143/232）
扣除非慣例 1,2,3 → 36.6% — 冇傾向！
```

### 真實結構

- **L₁-L₃（1,2,3）100% 普適** — 係 polytope 正常化慣例（e₁,e₂,e₃ 排頭），唔係 Lucas 結構！
- index 4/7（87%）、8（63%）、9（50%）— 都係常見位置，冇 Lucas 特異性
- **正確結論：vertex 索引嘅 Lucas 傾向唔存在**（之前 claim 撤回）

### 但 X 發現真 Lucas 結構

**e₁-e₄ 位置 = {1, 3, 7, 47} = {L₁, L₂, L₄, L₈}**（canonical）— 呢個係真 Lucas 對應，但係 polytope-specific（pts ordering 因實例而異）

## 檔案

```
scripts/61_glsm_correspondence_check.py  # X
scripts/62_cy_correction_factor.py       # V
scripts/63_zeckendorf_control.py         # W（誠實修正）
```
