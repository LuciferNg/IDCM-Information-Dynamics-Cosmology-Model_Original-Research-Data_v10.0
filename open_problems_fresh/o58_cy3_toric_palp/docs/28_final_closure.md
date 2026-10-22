# O58 — 最終閉合：開放問題解答 + Master Audit 記錄

> **狀態**: 🟢 完成（2026-08-24）
> **Master Audit: 35/35 PASS**（scripts/72_master_audit.py）

---

## 開放問題 1: Σ|det| ≈ 4.4×npts 嘅幾何根源 ✅

### 25 實例擴展驗證

```
mean Σ|det|/npts = 4.311（std 0.205）
corr(npts, Σ|det|) = 0.9907
```

### 結論：統計趨勢，唔係精確公式

- Σ|det| = 4×npts + c（c ∈ [4, 32]，無固定值）
- 6n-88 假設：mean|res|=6.4（唔精確）
- **真正根源：更多 lattice points → 更多/更大 cones → 更大 Σ|det|**
- 精確值由每個 polytope 嘅 triangulation 決定，冇簡單代數公式
- 4.4 = N_d/10 只係統計近似（corr 0.99 係強趨勢，但唔係 exact law）

## 開放問題 2: pts ordering「細數字優先」機制 ✅

### e-positions 分佈分析

```
(36,98)：86% e-positions 集中喺 1-10
1-10 入面 Lucas 密度 = 5/10 = 50%（1,2,3,4,7）
11-55 入面 Lucas 密度 = 4/45 = 8.9%
```

### 結論：機制完全解明

1. **CYTools/polytope 排序先排「簡單」點**（細 norm、細座標、unit vectors 最前）
2. e₁-e₄（unit vectors）必然喺最前幾個位置（1-10）
3. 細數字 1-10 有 50% Lucas 密度 → Lucas 率高係自然結果
4. **AC 嘅 46% pooled + AA 嘅假 z=10σ 完全由呢個機制解釋**

## 開放問題 3: canonical 200 = -χ+L₉ 嘅巧合意義 ✅

### Σ|det| - |χ| 分析

| instance | Σ|det|-124 |
|:---|:---|
| canonical | **76 = L₉**（唯一 Lucas！）|
| inst 1 | 116 |
| inst 2 | 56 |
| inst 3 | 124 |
| inst 5 | 108 |
| inst 10 | 106 |
| inst 20 | 120 |
| inst 50 | 112 |
| inst 89 | 110 |
| inst 15 | 88 |

### 結論：純巧合

- 只有 canonical 嘅 Σ|det|-|χ| = 76 = L₉
- 其他 9 個實例嘅值（56,88,108,110,112,116,120,124）冇 Lucas 結構
- **200 = -χ + L₉ 係 canonical polytope 撞啱**（Σ|det|=200 剛好 = 124+76）
- 真正規律 = Σ|det| ≈ 4.4×npts（統計）

---

## Master Audit 完整記錄（35/35 PASS）

| Section | 內容 | 結果 |
|:---|:---|:---|
| [1] | Polytope identity（h11=36, h21=98, χ=-124, M:48 6）| ✅ |
| [2] | (1,1,0,0) ↔ K=-232 4/4 | ✅ |
| [3] | HF swap | ✅ |
| [4] | True κ（350 nnz, K000=-360, K888=-232, rank 36）| ✅ |
| [5] | Block partial order 0 violations | ✅ |
| [6] | GLSM mirror | ✅ |
| [7] | h11 = L₄+L₇ = 36 | ✅ |
| [8] | Vertex cutoff（h21≥98→≤19v）| ✅ |
| [9] | Σ|det| ≈ 4.4×npts（corr 0.99）| ✅ |
| [10] | e-position control（46% pooled）| ✅ |
| [11] | K000 grouping | ✅ |
| [12] | co-simplex 904 = 554+350 | ✅ |
| [13] | h11=36 family dist | ✅ |
| [14] | Open problems Q1-Q3 | ✅ |

## 修正記錄（本 audit 發現）

1. **h21=97 有 1 個 20v 例外** → 界限由「h21≥92」修正為「h21≥98」
   （docs/16 + SESSION_START 已更新）
