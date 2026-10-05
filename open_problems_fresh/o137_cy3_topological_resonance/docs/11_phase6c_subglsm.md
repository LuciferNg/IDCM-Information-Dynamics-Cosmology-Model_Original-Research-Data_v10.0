# O137 — Phase 6c: 44-point Sub-GLSM 判別式盲測

**狀態**: 🟡 44-point Sub-GLSM 成功提取; 鏡像映射判別式測試全部負面
**日期**: 2026-08-30
**檔案**: scripts/19_subglsm_discriminant.py, data/sub_glsm_44_charges.npy

## 一、44-point Sub-GLSM 成功提取

從 72 個 anticanonical charges 中過濾出對應 φ≤12 的 44 個點。

| φ 值 | 點數 | 數論分解 |
|:---:|:---:|:---|
| 12 | 28 | L₄·L₅ = 4×7 |
| 9 | 9 | 3² = N_gen² |
| 8 | 5 | F₅ |
| 6 | 2 | — |
| **總和** | **44** | **= N_d** |

## 二、鏡像映射判別式測試

### 公式 q(n) = exp(2πi·γ(n)/scale)

測試了 10 種 scaling factor，全部結果相同：**所有模式的 |z-(-1)| ≈ 2.0，無法區分任何模式。**

| Scale | 結果 |
|:---|:---:|
| φ_origin=360 | 全部 |z-(-1)|≈2.0 |
| B=4 | 全部 |z-(-1)|≈2.0 |
| Σφ=1800 | 全部 |z-(-1)|≈2.0 |
| 88 | 全部 |z-(-1)|≈2.0 |
| φ_origin/44≈8.18 | 全部 |z-(-1)|≈2.0 |

**原因**: γ(n) ≤ 4 對所有 n，t = γ(n)/scale << 1，z(n) ≈ 1 永遠不接近 -1。

### 完整 GKZ 週期反演

| k | log|c_k^full| (72 charges) | log|c_k^44| (44 charges) |
|:---:|:---:|:---:|
| 1 | -116,830 | -73,049 |
| 2 | -266,851 | -166,757 |
| 3 | -429,482 | -268,313 |

c_k ≈ 0 對於 k > 0 → 鏡像映射反演是平凡的: z(q) = q。

## 三、結論

1. ✅ **44-point Sub-GLSM 成功提取** — 維度從 ℝ⁸⁰ 降至 ℝ³⁹
2. 🔴 **鏡像映射判別式無法區分模式** — γ(n) 太小，z(n) ≈ 1 永遠
3. 🔴 **GKZ 週期係數消失** — 鏡像映射反演平凡
4. 🟢 **44=Nd φ 結構是唯一堅實的發現**

## 四、正確方向

鏡像映射判別式測試失敗的原因是：在 anticanonical 方向，Kähler modulus t = γ(n)/scale << 1，z(n) 永遠不接近判別式。

真正的模式選擇機制可能不在 mirror period integrality，而在：
- **K_Chain 自身的 2-adic 代數結構**（Phase 2 已確認 v₂(n) 子環規則）
- **K_Chain 與 CY₃ 的 44 點 φ 結構的幾何配對**
- **44 個 φ≤12 點在 28/9/5/2 分組下的 Lukas 數系結構**

## 五、存檔資料

- `data/sub_glsm_44_charges.npy`: 44 個 anticanonical charges
- `data/sub_glsm_44_indices.json`: 44 點索引及 φ 值
- `scripts/19_subglsm_discriminant.py`: 完整測試腳本