# O58 — 探索 M/N/O：K=0 幾何 vanishing + h11 Lucas 分解 + div0 條件

> **狀態**: 🟢 完成（2026-08-24）

---

## M: co-simplex K=0 消去 — 真正幾何 vanishing，唔係 redundancy

### Redundant divisors（divisor basis 之外）

```
divisor_basis (0-based) = [0,1,4,5,8,9,...,35]  (32 個)
REDUNDANT (0-based)     = [2, 3, 6, 7]          (4 個 = B = 4 ✅)
```

**⚠️ 注意：7 係 redundant！** 而 7 就係殘餘 U(1) 位置 + L₄=7！

### 線性組合測試

- Redundant divisor rows fit residual：0.13 – 0.69（**唔係 0**）
- → Redundant divisors **唔係** basis divisor 嘅線性組合
- → **K=0 唔係 basis redundancy 造成，係真正幾何 vanishing**

### 消去分析

- 904 co-simplex triples：554 零 + 350 非零
- 388 個 zero triples 係純 basis（冇 redundant）— redundancy 只解釋 ~30%
- zero triples redundant-count：{0:388, 1:113, 2:47, 3:6}
- nz triples redundant-count：{0:227, 1:88, 2:28, 3:7}
- **div0 出現率：zero 33.8% vs nz 16.6%**（2x — div0 傾向消去）

**結論**：K=0 嘅主因係**幾何 vanishing**（triple 嘅 cone product 唔命中 CY hypersurface），唔係 divisor basis 冗餘。

## N: h11 = 36 = L₄ + L₇ — 🎯 強新閉合！

### Lucas 分解

```
L₄ = 7    (γ₇ mode index + 殘餘 U(1) 位置 7)
L₇ = 29   (-232 因子 + 殘餘 U(1) 位置 29)

h11 = 36 = L₄ + L₇ = 7 + 29
```

- **36 唯一非平凡兩個-Lucas 分解**（另一個 L₆+L₆=18+18 係平凡重複）
- L₅ + L₆ = L₇（11+18=29 — Lucas 加法性質）
- Lucas identity：L₁₁ = L₇·L₄ − L₃ = 29×7 − 4 = 199 ✓
- **殘餘 U(1) 位置 7 同 29 直接編碼 h11 嘅 Lucas 分解！**

### 意義

1. **h11=36 本身係 Lucas 加法結構**（L₄+L₇）
2. L₄=7 = γ₇ mode（O13 n/p 機制）— mode index 就係 Lucas 數
3. L₇=29 = (1,1,0,0) K=-232 因子 — 幾何同 GLSM 都出現
4. **兩條獨立路徑（幾何 K + GLSM 殘餘 U(1)）指向同一個 Lucas 分解**

## O: div0 K 值 — 45=N_d+1 只喺 canonical

### 跨實例數據

| inst | npts | nvert | K000 | -K/8 | 有 (1,1,0,0)? |
|:---|:---|:---|:---|:---|:---|
| 0 | 48 | 6 | -360 | **45** | ✅ |
| 1 | 53 | 6 | -340 | 42.5 | ✅ |
| 2 | 44 | 7 | -640 | **80** | ❌ |
| 3 | 54 | 7 | -336 | 42 | ✅ |
| 5 | 52 | 7 | -584 | 73 | ❌ |
| 10 | 52 | 8 | -594 | 74.25 | ❌ |
| 20 | 54 | 8 | -596 | 74.5 | ❌ |
| 50 | 53 | 9 | -342 | 42.75 | ✅ |
| 89 | 52 | 10 | -610 | 76.25 | ❌ |

### 發現

1. **-K/8 = 45 = N_d+1 只喺 canonical（inst 0）**
2. **有 (1,1,0,0) → -K/8 ∈ [42, 45]（淺）**；**冇 → [73, 80]（深）** — 完全分離
3. **inst 2（npts=44 = N_d 唯一）→ -K/8 = 80 = N_d + h11 = 44+36**
4. 冇簡單線性關係（corr with npts/nvert/interior 都低）
5. 45 = L₇+B² = 29+16；80 = 44+36 = N_d+h11

**結論**：-K[0,0,0]/8 反映 polytope「大細」（有 (1,1,0,0) 淺 / 冇深），45 係 canonical 特有（M:48=44+B 唯一 6v+npts=48 組合）。

## 檔案

```
scripts/49_cosimplex_redundancy.py   # M
scripts/50_lucas_h11_decomposition.py # N
scripts/51_div0_k_condition.py       # O
```
