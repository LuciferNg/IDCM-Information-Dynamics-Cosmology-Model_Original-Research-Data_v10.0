# O58 — 探索 G/H：core divisor GLSM 結構 + triangulation 根源

> **狀態**: 🟢 完成（2026-08-24）

---

## G: Core divisor GLSM 身份 — 精確 mirror 結構！

### GLSM charge 分析（canonical）

| divisor | pts | vertex? | glsm_sum | 非零 charges | diagK |
|:---|:---|:---|:---|:---|:---|
| 0 | (0,0,0,0) | ❌ | -742 | 31/32 | -360 |
| 1 | (1,0,0,0) | ✅ | +1 | **1** | 4 |
| 3 | (0,0,1,0) | ✅ | 137 | 29 | 0 |
| 4 | (1,2,0,0) | ✅ | -194 | 31 | 8 |
| 7 | (0,0,0,1) | ✅ | 34 | 19 | 0 |
| **8** | (1,1,0,0) | ❌ | **+733** | **32/32** | **-232** |
| 17 | (-11,-6,-3,-1) | ❌ | +1 | **1** | -5 |
| **33** | (-11,-7,-3,-1) | ❌ | +1 | **1** | **+40** |

### 🎯 關鍵發現：div 0 同 div 8 係 GLSM 近似 mirror 對！

```
q8 = [-2, +20, +64, +9, +53, ...]（32 非零，sum=+733）
q0 = [ 0, -20, -64, -10, -53, ...]（31 非零，sum=-742）

q0 + q8 = 只有 8 個非零位置！
```

- **喺 24/32 個 U(1) 上，q8 = -q0 精確抵消**
- **殘餘 8 個 U(1)（位置 0,3,7,25,28,29,30,31）= B×2 = 2³**
- 24 = 3×8 = 3×2B
- div 8 係「全 U(1) 參與」點（32/32 非零）— 同 div 0（31/32）組成正負對

### 其他發現

- div 17/33 都係「純 coordinate ray」（單一 q=+1）但 diagK 唔同（-5 vs +40）— 位置決定
- Σ diag K = -380
- K=8 diagonal 有 11 個 divisor（generic 值）
- 46 個大值 entry 嘅 divisor usage：0(24次), 8(21), 1(13), 4(12), 3(9), 33(9)

## H: Block 偏序嘅 triangulation 根源

### 🎯 必要條件閉合：共 simplex = K≠0 嘅必要條件

- Triangulation 有 **144 個 maximal simplices**（5-vertex cones）
- **350/350 K≠0 triples 全部喺同一個 maximal simplex 入面** ✅
- 但 554 個 co-simplex triples 有 K=0 → 必要唔充分

### Star size（simplex 包含數）

| divisor | star |
|:---|:---|
| **0** | **144（全部！）** |
| 8 | 8 |
| 4/5/9 | 6（最少）|
| 17 | 30 |

**divisor 0 = origin 喺所有 144 個 maximal simplices** — 佢係 triangulation 嘅「universal member」，解釋咗超大負自交 -360！

### 結論

- **K[i,j,k]≠0 → i,j,k 共 simplex**（幾何必要條件，350/350）
- **block 偏序 = simplex 包含結構嘅反射**
- K=0 嘅額外條件（即使共 simplex）可能係 intersection 數值計算嘅消去

## 意義

1. **div 0 ↔ div 8 嘅 GLSM mirror 對**（24/32 U(1) 抵消）係真正嘅「Z₂ mirror」— 唔係坐標 mirror
2. **8 個殘餘 U(1) = B×2** — K_Chain 邊界結構浮現
3. **div 0 嘅 universality（144/144 simplex）** 解釋 -360

## 開放問題

- 🔴 殘餘 8 U(1) 位置（0,3,7,25,28,29,30,31）有冇 K_Chain 意義？
- 🔴 554 個 co-simplex 但 K=0 — 消去機制
- 🟡 div 17/33 純 coordinate 但 diagK 唔同

## 檔案

```
scripts/41_core_divisor_identity.py   # G
scripts/43_triangulation_origin.py    # H（simplices 版）
data/core_divisor_identity.json
```
