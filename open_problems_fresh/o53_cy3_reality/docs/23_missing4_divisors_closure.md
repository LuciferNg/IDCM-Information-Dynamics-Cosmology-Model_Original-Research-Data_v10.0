# O53 重大閉合 — 缺失 4 divisors [2,3,6,7] = B = 4

> **日期**: 2026-08-22
> **狀態**: 🟢 **結構閉合 — 3×12 block 嘅起源：4 個 Kähler-redundant divisors 全部喺 Block 0**
> **腳本**: scripts/98-101

---

## 一、發現

CYTools `divisor_basis()` 返回 32 個 divisors（1-based [1,2,5,6,9,10,...,36]），缺失 4 個：

```
缺失 (1-based): [3, 4, 7, 8]
缺失 (0-based): [2, 3, 6, 7]
```

**關鍵：4 個缺失 divisor 全部喺 Block 0（0-11）！**

## 二、結構閉合

| 身份 | 數值 | 狀態 |
|:-----|:----:|:----:|
| 缺失 divisor 數 | **4** | ✅ = B（K_Chain 邊界數）|
| 全部喺 Block 0 | [2,3,6,7] | ✅ |
| dim Kähler cone | 32 = 36−4 = h11−B | ✅ |
| 36 = Nd−2B | 44−8 | ✅ |

**3×12 block 結構嘅起源**：
- Block 0: 12 個 divisors，但 4 個（[2,3,6,7]）唔喺 Kähler basis（redundant）
- Block 1/2: 全部 12 個都係 independent
- → Block 0 特別強（ratio 3.05 主要來自佢）

## 三、divisor 身份

| divisor (0-based) | polytope point | 強度 |
|:-----------------:|:--------------:|:----:|
| 2 | [-15,-10,-4,0] | 90 |
| 3 | [0,0,1,0] | 386 |
| 6 | [-7,-5,-2,0] | 84 |
| 7 | [0,0,0,1] | 140 |

（注意：最高強度 divisor 0（1984, origin）同 8（1414）係喺 basis 入面，唔係缺失）

## 四、意義

1. **4 = B 直接連結 K_Chain**（邊界數）— 缺失 divisor 數 = 邊界數
2. **Block 0 嘅「特別」有幾何起源** — 4 個 redundant divisors 集中
3. **3×12 唔係人工分組** — 佢反映 Kähler cone 嘅真實結構
4. **12 = (Nd−2B)/3** — Block 0 有 4 個 redundant = B，所以「有效」12−4 = 8 = 2B？

## 五、後續

- 🔴 4 個缺失 divisors 嘅 exact 關係（點解係呢 4 個？）
- 🟡 缺失 divisors 同 c_f = n/3 有冇直接連結？（Block 0 redundant → 分數結構？）
