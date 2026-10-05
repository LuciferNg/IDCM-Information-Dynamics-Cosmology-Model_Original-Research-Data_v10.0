# O53 方向①進展 — J* 結構 + curve volumes

> **日期**: 2026-08-22
> **狀態**: 🟡 **進行中 — GW/GV 計算 background；J* 確認冇 φ 結構**
> **腳本**: scripts/105-110

---

## 一、J* 結構（scripts/110）

```
φ 指數近整數 (Δ<0.05): 7/36 = 19% (threshold 0.2 計法 17/36 = 47%)
q = -ln(J*)/2π ∈ [0.518, 1.072]
1/12 格點: mean|Δ| = 0.0195 vs 隨機 0.0215 (z = -0.98)
→ J* 冇 φ 結構 (確認之前 findings)
```

## 二、curve volumes（scripts/106-107）

用 tip 計算 185 個 curve volumes：
```
範圍 [1, 912], mean 43.1, median 7
1 嘅數量: 40 (22%)
φ 近整數: 27% vs 隨機 7.6%
```

**但 curve volumes 依賴 tip（J 縮放）— 唔係拓撲不變量** → 唔可以宣稱閉合。

## 三、GW/GV invariants（進行中）

- mori_cone_cap: 4485 rays (37D)
- extremal_rays: 44 rays (37D)
- GLSM charge matrix: 32×37
- **compute_gw 喺 background 跑緊**（cygv 大型計算）
- GW/GV 先係拓撲不變量 — 如果成功可以同 J* 對照

## 四、狀態

- 🔴 J* 冇 φ 結構（確認）
- 🟡 curve volumes 有微弱 φ 信號但唔係 invariant
- ⏳ GW/GV 計算中 — 等結果
