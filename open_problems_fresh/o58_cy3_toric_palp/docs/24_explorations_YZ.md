# O58 — 探索 Y/Z：K formula 誠實否定 + Σ|det|=200 = -χ+L₉

> **狀態**: 🟢 完成（2026-08-24）
> **Y: 誠實否定 — K[8,8,8] = -L₇×Σ1/|det| 唔普適（特例）**
> **Z: 🎯 Σ|det| = 200 = -χ + L₉ 閉合！**

---

## Y: K = -L₇×Σ1/|det| 唔普適 — 誠實否定 🔴

### 全 350 nonzero triples 掃描

- 只有 **1 個** triple (8,8,8) 有 ratio = -29 = -L₇
- 其他 ratio 分佈散：-1（8 個）、1（2 個）、8（2 個）、-8（1 個）、2（1 個）
- ratio 按 cone count 分佈：mean -0.97 到 +2.31，std 好大

### 結論

**K[8,8,8] = -L₇×Σ1/|det| 係單點巧合**，唔係通用公式。V 嘅「精確閉合」只喺 (8,8,8) 成立。

但呢個巧合本身仍然有趣 — (8,8,8) 嘅特殊幾何（div8 = (1,1,0,0) 唯一 norm²=2 點 + star=8 全部 det=1）令 K = -29×8 精確成立。

## Z: 🎯 Σ|det| = 200 = -χ + L₉！

### 閉合

```
Σ|det| over all 144 cones = 200.000（精確）

χ = 2(h11-h21) = 2(36-98) = -124
L₉ = 76（Lucas 9）

200 = -χ + L₉ = 124 + 76 ✅
```

### star Σ|det| 結構

| divisor | star Σ|det| |
|:---|:---|
| 0 (origin) | 200.000（= 全體總和 — origin 喺所有 cones）|
| 1 | 27.000 |
| 3 | **48.000 = N_d+B = M points！** |
| 4 | 14.000 |
| 7 | 40.000 |
| 8 | 8.000 |

### 意義

1. **Σ|det| = 200 = -χ + L₉** — toric 幾何（Euler 數）同 Lucas 數嘅直接結合！
2. div 3 star = 48 = N_d+B — vertex (0,0,1,0) 嘅 cone 加權和 = M 點數
3. div 8 star = 8 = B×2 — (1,1,0,0) 嘅 cone 加權和 = 2B

### 開放

- 🔴 點解 Σ|det| 恰好 = -χ + L₉？（Batyrev 公式嘅結構）
- 🔴 div 3 star = 48 同 div 8 star = 8 嘅意義

## 檔案

```
scripts/65_k_invdet_generalization.py  # Y（否定）
scripts/66_sumdet_200_meaning.py       # Z（閉合）
```
