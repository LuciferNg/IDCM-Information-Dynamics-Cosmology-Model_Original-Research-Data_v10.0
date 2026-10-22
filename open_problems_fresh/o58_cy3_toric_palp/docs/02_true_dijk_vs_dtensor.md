# O58 — 真實 d_ijk vs d_tensor_final（O50 升級驗證）— 修正版

> **狀態**: 🟢 完成 — 真實 κ 已由 canonical polytope 直接計算（index 修正後）
> **日期**: 2026-08-24（2026-08-24 修正 index bug）
> **修正**: 之前用 `i-1,j-1,k-1` double-shift，nnz=1359 係錯；正確係 350

---

## ⚠️ Index Convention（重要教訓）

**CYTools `cy.intersection_numbers()` 返回 0-based divisor index（0..36），divisor d ↔ pts[d]**。直接用 raw key，**唔可以再 shift**！

## 真實 κ_ijk（canonical (36,98) polytope，修正後）

```python
P = Polytope(canonical_6_vertex)   # 48 pts, h11=36, h21=98
tri = P.triangulate(backend="qhull")
cy = tri.get_cy()
inter = cy.intersection_numbers()  # 361 entries, keys 0..36
K = zeros((36,36,36)); K[i,j,k] = v  # 直接用 raw key（0-based）
```

| 性質 | 值（修正） | 舊（錯） |
|:-----|:---|:---|
| 非零 entry | **350**（0.75% 稀疏） | 1359 ❌ |
| K[0,0,0]（divisor 0） | **-360** | 4 ❌ |
| K[1,1,1]（divisor 1） | 4 | — |
| K[8,8,8]（divisor 8 = pts[8]=(1,1,0,0)） | **-232** | — |
| mode-flatten rank | **36 / 36 / 36**（滿 rank） | 35 ❌ |
| 12³ block (0,0,0) | 79 nnz, rank 11 | 214 nnz, rank 12 ❌ |

### 負對角 divisor（0-based）

| divisor | pts | K | 值 |
|:---|:---|:---|:---|
| 0 | origin (ray 0) | **-360** | -8×45（= -8×(Σγ/2) = -8×(N_d+1)）|
| 8 | (1,1,0,0) | **-232** | **-8×L₇（L₇=29）普適閉合** |
| 12 | (-23,-15,-6,-2) | -5 | — |
| 17 | (-11,-6,-3,-1) | -5 | — |

## d_tensor_final.npy（IDCM 12³）

| 性質 | 值 |
|:-----|:---|
| shape | (12,12,12) |
| rank | **12（滿 rank）** |
| nnz | 1300（96.6% 稠密） |

## 關鍵結論

### d_tensor_final 唔係真實 CY₃ triple intersection ❌（結論不變）

- **corr(K[0:12], d_tensor) = -0.0258**（修正後；舊 0.0094 都係 ~0）— 無線性關係
- 真實 κ 稀疏（0.75%）、d_tensor 稠密（96.6%）
- 真實 κ 整數、d_tensor float
- 真實 κ mode-rank 36、d_tensor rank 12

**O50 結論確認**: IDCM `d_tensor_final` 係 **K_Chain 離散拓撲嘅 WDVV-solved 構造**（12³, rank 12），**唔係** CY₃(36,98) 嘅幾何相交數。兩者概念解耦。

### kappa_36d_raw.json 重新審計（修正）

| 性質 | 值 |
|:-----|:---|
| entries | **303**（唔係 1122！） |
| 0-based 解讀 | nnz=303, shared=81, identical=25 |
| 1-based 解讀 | nnz=265, shared=72, identical=17 |
| 結論 | **同 true κ 唔一致**（shared 少）— 舊檔唔可信 |

⚠️ 舊 docs/02 話「1122 nnz、97.8% 一致」係基於舊 index 嘅錯誤分析。kappa_36d_raw.json 實際上只有 303 條，同 true κ 重疊少，**唔可以當 true κ 子集**。

## 對 IDCM 嘅意義

1. **d_tensor = K_Chain 拓撲構造**（保持 O50 結論）✅
2. **真實 κ 已可計算**（O58 交付物，350 nnz 稀疏結構）
3. **負對角結構：divisor 0 (-360) + divisor 8 (-232=-8×L₇) 普適**
4. K[0,0,0] = -360 = -8×(Σγ/2)（canonical 專屬）

## 開放問題

- 🔴 12³ block 同 d_tensor 有冇**非線性**映射？
- 🔴 divisor 0 嘅 -360 = -8×45 喺其他實例唔普適（值域 -336..-640）— 有冇 K_Chain 結構？
- 🟡 350 nnz 嘅稀疏 pattern 有冇結構？

## 檔案

```
data/kappa_36d_true.npy       # 真實 36³ κ（350 nnz，修正版）
data/true_kappa_summary.json  # 摘要（更新）
scripts/31_true_dijk_corrected.py # ✅ 修正版
scripts/08_true_dijk.py       # ⚠️ 舊（double-shift bug）
```
