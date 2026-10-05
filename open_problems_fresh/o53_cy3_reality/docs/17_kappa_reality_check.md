# O53 重大發現 — 舊 κ_36d_raw.json 唔係真 intersection numbers

> **日期**: 2026-08-22（路徑三攻堅中發現）
> **狀態**: 🔴 **重大 — 需要重新驗證所有基於舊 κ 嘅閉合**

---

## 一、發現經過

1. 用戶下載咗 HuggingFace `calabi-yau-data/polytopes-4d` 完整數據集（30GB, 473M polytopes）
2. 提取咗 (36,98) polytope（20 vertices normal form）
3. CYTools 由真實 polytope（Sage export 48 points）成功計算：
   - h11=36, h12=98, χ=-124 ✅
   - intersection numbers（完整 3-tensor, 1341 non-zero entries）
   - **triangulation 獨立**（3 次計算完全一致）→ 真 intersection numbers
4. **對比發現**：CYTools κ vs `kappa_36d_raw.json`：

```
CYTools: 1341 non-zero entries
舊 κ:    1122 non-zero entries
共同:     201 entries (其中只有 67 個完全一樣)
只喺 CYTools: 1140
只喺舊:      921
共同 entries 數值差好大 (mean diff 6.18, max 364)
```

## 二、影響

**`kappa_36d_raw.json` 唔係真正嘅 CY₃(36,98) intersection numbers！**

之前基於佢嘅閉合需要重新檢驗：
- ❓ λ₁ = φ^(1/3)（0.004%）
- ❓ tr(Y²) ≈ 5 = B+1
- ❓ 3×12D block-triangular 結構
- ❓ J* ≈ φ^(-n)

**初步用 CYTools κ + J* 收縮：**
```
λ₁ = 3.697 (vs φ^(1/3) = 1.174, 誤差 215%)
tr(Y²) = 16.14 (vs 5, 誤差 223%)
```

⚠️ 但呢個係用 J*（36D）直接收縮 CYTools κ（36D）— J* 本身可能唔係 CYTools κ 嘅自然座標，所以結果未定論。

## 五、重分析結果（scripts/77）

用 CYTools 真 κ 重新分析（Y = κ·J*）：

```
λ₁ = 3.697  (φ^(1/3) = 1.174, 誤差 215%)  ❌
tr(Y²) = 16.14  (5 = B+1, 誤差 223%)  ❌
3×12 off-diag = 0.43/0.26/0.31 (唔係零)  ❌
Schur 下三角 = 0.00e+00 (block-triangular 成立!)  ✅
```

## 六、最終結論

| 之前閉合 | 狀態 | 備註 |
|:---------|:----:|:-----|
| λ₁ = φ^(1/3) (0.004%) | 🔴 **撤銷** | 舊 κ 偽影 |
| tr(Y²) ≈ 5 = B+1 | 🔴 **撤銷** | 舊 κ 偽影 |
| 3×12D block-triangular | ✅ **成立** | CYTools κ 都確認 |
| J* ≈ φ^(-n) | ❓ 待查 | J* 可能唔喺 CYTools κ 座標 |

**重要教訓**：`kappa_36d_raw.json` 來源不明（可能係舊 Sage 計算 bug 或者唔同 basis），導致 λ₁/tr(Y²) 閉合建基於錯誤數據。**3×12 block 結構係唯一 survive 嘅幾何閉合**。

## 七、下一步

1. 🔴 檢查 J* 係咪喺 CYTools κ 嘅 Kähler cone（可能 J* 需要轉換 basis）
2. 🔴 用 CYTools tip 重新做 λ₁ 分析
3. 🟡 用 CYTools κ 檢查 block 結構嘅 su(12) 解讀

## 四、新數據檔案

- `data/polytopes/cy36_98_intersection_full.json` — CYTools 完整 intersection numbers（36³, 1341 nnz）
- `data/polytopes/cy36_98_cytools_kappa.json` — κ(tip) 2D matrix + tip 值
- `data/polytopes/cy36_98_hf.poly` — HF normal form
- `data/polytopes/control_h11_36_h12_94.poly` — 對照 polytope（HF 提取）
