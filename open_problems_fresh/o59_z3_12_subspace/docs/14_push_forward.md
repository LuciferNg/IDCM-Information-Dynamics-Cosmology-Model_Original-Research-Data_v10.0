# O59 — 項目 5 推前分析：Frobenius 子代數嵌入

> **日期**: 2026-08-30
> **狀態**: 🟢 **12D d_tensor 係 36D 嘅 Frobenius 子代數，完全隔離**
> **腳本**: scripts/30_push_forward.py

---

## 核心發現

### 1. 12D Frobenius 子代數 ✅

12D d_tensor 嵌入 36D（補零後）:
- **Associativity error = 0.00e+00** ✅
- **Cross terms (12D × 24D) = 0.0000** ✅（完全隔離！）

**12D d_tensor 係 36D Frobenius 代數嘅完美子代數。**

### 2. 44 = 12 + 32 = (L₅+1) + 2B² 🆕

```
44 = 12 + 32
   = (L₅+1) + 2B²
   = (11+1) + 2×16
   = 12 + 32
```

- **12** = SU(12) fundamental = **active** 子空間
- **32** = 2B² = **passive** 規範扇區

### 3. 12D 唔係 36D κ 嘅投影 ❌

| 測試 | 結果 |
|:----|:----:|
| Y_12 係 Y_36 嘅 submatrix？ | ❌ 完全唔同 |
| Π^T@Y_36@Π = Y_12？ | ❌ 誤差 892% |
| 常數縮放？ | ❌ 比唔係常數 (0.14 到 -216) |
| Kähler 勢縮放？ | ❌ e^(-K/2) = 0.008 |

## 真實關係

```
12D d_tensor (WDVV solution)  ─── Frobenius 子代數 ─── 36D kappa (CY₃ intersection)
        │                                                    │
        ├── associativity: 0.00 error                        ├── associativity: 0.00 error
        ├── 12D algebra (L₅+1 = 12 active)                   ├── 36D algebra (full)
        ├── isolated from 24D ✅                              ├── Block traces: 47, 17, 104
        └── 44 = 12 + 32 = (L₅+1) + 2B²                      └── Sum(κ) = -8 = -2B
```

**12D d_tensor 同 36D κ 係唔同嘅 Frobenius 代數，經 GKZ φ≤12 截斷相關聯，但唔存在簡單線性投影關係。**

---

## 檔案

- `scripts/30_push_forward.py` — 推前分析
- `docs/14_push_forward.md` — 本報告

---

> ⚠️ **驗證修正附註 (2026-10-05, O59 closeout docs/16)**: 本報告「12D d_tensor 係 36D 嘅
> Frobenius 子代數（associativity error = 0.00e+00）」之 associativity 論證**係同義反覆**：
> `scripts/30_push_forward.py:50-52` 只檢 `d_sq − d_sq.transpose(1,0,2,3)`（三階對稱張量自動成立），
> 唔係 associativity。真正 WDVV associativity（`C^q_ab = d_abp g^{pq}`，g = Y）實測：
> 12D `d_tensor_native_12d` err **0.759**；36D κ 對照 err **6.5e7** ⇒ 此數據集未建立 associativity。
> **收窄**：associativity 部分 🟡 未證實；**不受影響**：「完全隔離」（cross-terms = 0 ✅）、
> 「SVD 比 47 = K_tree+2L₄」（47.001 ✅）、「12D 唔係 36D 簡單投影」（✅）。原文保留作時序歷史。