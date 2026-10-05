# O59 — 項目 5 投影映射最終分析

> **日期**: 2026-08-30
> **狀態**: 🟡 **12D d_tensor 與 36D κ 係不同數學物件，經 GKZ φ≤12 截斷相關聯**
> **腳本**: scripts/29_projection_mapping.py

---

## 核心結論

**12D d_tensor 唔係 36D κ 嘅簡單投影。** 佢哋係兩個不同數學物件，經 GKZ φ≤12 截斷相關聯。

---

## 關鍵發現

### 1. SVD 比 = 47 = K_tree + 2L₄

```
kappa SVD top singular value: 608.57
d_tensor SVD top singular value: 12.95
Ratio: 47.00 = K_tree + 2L₄ = 33 + 14
```

**47 = tr(Block 0 of kappa)** — 係 kappa 嘅第一個 12×12×12 block 嘅跡。

### 2. 特徵值譜完全不同

| 譜 | 12D Y | 36D Y |
|:--|:-----:|:-----:|
| λ_max | 35.42 | 3.70 |
| λ_2nd | 2.35 | 0.78 |
| 負特徵值 | -5.50 | -1.01 |
| tr(Y) | 31.85 | 3.16 |

**12D/36D 特徵值比唔係常數** (範圍從 0.14 到 -216)，所以唔存在簡單嘅常數縮放。

### 3. 投影矩陣 Π 係正交嘅

```
Π^T @ Π = I_12 ✅
```

但 Π 係 Y_36 嘅 top 12 eigenvectors，唔係對應 d_tensor 嘅投影。

### 4. Kähler 勢縮放唔 work

```
e^(-K/2) = sqrt(V) = 0.0082
需要縮放 ≈ 10
比 = 1218 (唔係結構數)
```

---

## 真實關係

```
12D d_tensor (WDVV solution, φ≤12 subspace)
    ↓
    ├── GKZ φ≤12: 44 points → 12D fundamental
    ├── WDVV: associativity condition (0.00 error)
    ├── Scaling: 47 = K_tree + 2L₄ (SVD ratio)
    └── NOT a simple projection of 36D kappa
    
36D kappa (CY₃ intersection numbers, full moduli)
    ├── Symmetric: 3-tensor (0.00 error)
    ├── Traces: Block 0=47, Block 1=17, Block 2=104
    └── Sum(κ) = -8 = -2B ✅
```

---

## 檔案

- `scripts/29_projection_mapping.py` — 完整分析