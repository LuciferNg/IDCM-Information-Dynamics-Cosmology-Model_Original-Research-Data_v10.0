# O53 方向①+② 最終結果

> **日期**: 2026-08-22
> **狀態**: 🔴 **方向① GW 唔實際（計算太慢）；方向② 1/3 結構唔係家族普適**
> **腳本**: scripts/105-112

---

## 一、方向①：A2 J* 來源 — GW invariants

### 嘗試咗：

| 方法 | 結果 |
|:-----|:-----|
| compute_gw (mcap rays, max_deg=2) | ❌ dimensions mismatch (37D vs 32D) |
| compute_gw (basis 修正) | ⏳ hang >5min |
| compute_gw (max_deg=2, 全計算) | ⏳ hang >5min (killed) |
| compute_gw (min_points=3) | ⏳ hang >5min |
| compute_gw (5 rays) | ⏳ hang |
| compute_curve_volumes (tip) | ✅ 185 個值 |
| compute_divisor_volumes (tip) | ✅ 36 個值 |

### curve volumes 分析：
```
範圍 [1, 912], 1 佔 22%
φ 近整數: 27% vs 隨機 7.6% (3.6 倍)
但 curve volumes 依賴 tip → 唔係 invariant → 唔可以閉合
block 分析: z=0.62 唔顯著
```

### J* 結構：
```
φ 指數近整數 (Δ<0.05): 7/36 = 19%
1/12 格點: z = -0.98 (完全唔顯著)
→ J* 冇 φ 結構 (確認)
```

## 二、方向②：(36,98) 100 實例 1/3 結構

```
tip (合法 J) 下 20 實例: 有精確 1/3 = 0/20 (0%)
全譜近1/3: 33% vs 隨機 30.8% (無差異)
→ 1/3 結構唔係家族普適
→ J* 特有確認 (J* 唔合法但「調律」出 1/3)
```

## 三、結論

| 項目 | 狀態 |
|:-----|:----:|
| GW/GV invariants | 🔴 唔實際（32D CY 計算太慢）|
| curve volumes φ 信號 | 🟡 有但唔係 invariant |
| J* 冇 φ 結構 | ✅ 確認 |
| 1/3 結構家族普適 | ❌ 否定 |
| **A2 (J* 來源)** | 🔴 仍開放 |
| **c_f n/3 (A1)** | 🔴 仍開放 |

## 四、教訓

1. **GW invariants 對高維 CY (h11=32) 計算量爆炸** — 唔適合快速驗證
2. **curve volumes 唔係 invariant** — 唔可以用嚟做 φ 閉合
3. **J* 嘅 1/3 結構係「調律」產物** — 有啲神秘但冇幾何合法性
