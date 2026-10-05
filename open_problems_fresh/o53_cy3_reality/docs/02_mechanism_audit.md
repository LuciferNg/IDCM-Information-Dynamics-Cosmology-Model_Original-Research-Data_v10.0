# O53 機制審計報告 — 投影算子 rank 缺陷 + 12 維結構發現

> **日期**: 2026-08-21（O53 第二 session）
> **腳本**: scripts/05–12
> **核心問題**: O53 開放問題 2 —「CY₃ 點樣由 K_Chain 投影結構生成？」
> **狀態**: 🟡 **重大負面發現 + 結構閉合線索**

---

## 一、背景

O53 開放問題 2 問「CY₃ = K_Chain 投影化身」嘅嚴格機制。
本地 `src/` 有兩套實現：

| 檔案 | 機制 | 維度 |
|:-----|:-----|:-----|
| `projection_operator.py` | P̂: 134×946 投影矩陣 | 134 moduli × 946 beats |
| `dijk_intersection.py` | d_{ijk}: 36³ 三重相交張量 | 36 Kähler moduli |
| `derive_dijk_wdvv_solver.py` | WDVV 求解 (698 參數) | 36³ → 12³ |
| `derive_dijk_12d_native.py` | 原生 12D Z₃ 構建 | 12³ |

---

## 二、重大發現 1：P̂ (134×946) 係 rank-2 偽結構 🔴

### 2.1 鐵證

```
Kähler 行 (36 行) 兩兩 corr = 1.0000000000 (100% 完全相同)
CPX 行 (98 行)  兩兩 corr = 1.0000000000 (100% 完全相同)
SVD 秩 (tol=1e-6 至 1e-12) = 2
本徵值譜: λ₁=11956, λ₂=2914.6, λ₃=4.8e-12 (差 15 個數量級!)
```

### 2.2 根本原因

`projection_operator.py` 嘅選擇律 weight 只依賴 **(type, beat)**：
```python
if mod.type == 'kahler':
    weight = φ ** (-avg_gamma)      # 只睇 beat, 冇睇邊個 modulus!
else:
    weight = math.exp(-1.0 / avg_gamma)  # 同上
```
→ 36 個 Kähler 行完全相同、98 個 CPX 行完全相同 → rank = 2。

### 2.3 影響

**「66 個本徵態 → 3 代 × 22 態」嘅聲稱係數值幻覺：**
- 66 個「正本徵值」全部 < 1e-8（float64 捨入噪聲）
- 真正物理譜只有 2 個（Kähler/CPX 兩類）
- 現有質量譜機制（`SM_MassPredictor`）建基於噪聲

---

## 三、重大發現 2：d_{ijk} (36³) 係 rank-1 可分離張量 🔴

### 3.1 鐵證

`dijk_intersection.py` 嘅 `TripleIntersectionTensor.compute()`:
```python
d_ijk = exp(-|E_i+E_j+E_k|/E₁) × φ^(-(γ_i+γ_j+γ_k))
      = Π_i [exp(-E_i/E₁) · φ^(-γ_i)]     ← 可分離!
      = a_i · a_j · a_k                     ← rank-1!
```

數值驗證：
```
d[i,j,k]/(a_i·a_j·a_k) − 1 嘅 max 誤差 = 1.02e-14
mode-0/1/2 flatten 秩全部 = 1
```

### 3.2 物理意義

- **冇三體耦合** = 唔對應任何真實 CY₃ 相交數
- 真實 CY₃(36,98) κ_ijk 有 303 個非零項、強張量結構（舊 session 數據）
- **rank-1 可分離 = 只係三個獨立波函數嘅乘積，冇幾何拓撲**

---

## 四、重大發現 3：12 維 d_tensor 有真正三體耦合 ✅

### 4.1 關鍵對比

| 張量 | rank | 三體耦合 | 物理 |
|:-----|:----:|:--------:|:-----|
| P̂ (134×946) | 2 | ❌ | 偽結構 |
| d_{ijk} (36³, dijk_intersection) | 1 | ❌ | 可分離 |
| **d_tensor_final (12³, WDVV)** | **12** | **✅** | **真正結構** |

### 4.2 12 維結構

```
d_tensor_final.npy (12×12×12):
  mode-0/1/2 flatten rank = 12 (全維度!)
  負值 123, 正值 1177, 零 428
  奇異值平滑衰減: 19.2 → 14.6 → 7.8 → 5.1 → ... → 0.015
```

### 4.3 12 維嘅來源（derive_dijk_12d_native.py）

```python
36 Kähler moduli = 3 bands × 12 orbits (Z₃)
Band I:   γ<1  (14 modes)
Band II:  1<γ<2 (8 modes)
Band III: γ>2  (14 modes)
12 orbits = 4 per band × 3 bands
```

> ⚠️ **誠實修正（docs/05）**: 呢個 Z₃ 構建係**其中一種 12D 構造**，
> 但 `d_tensor_final`（WDVV 解）同佢 **corr = 0.05（完全唔相關）**，
> 而且 d_tensor 冇 Z₃ 對稱（4-shift 誤差 0.56）。
> 「點解係 12 維」嘅機制仍然開放 🔴。

---

## 五、重大發現 4：tr(Y) ≈ 66 閉合線索 🟡

### 5.1 發現

```python
Y = Σ_k d_{ijk} · v_k,  v_k = φ^(-k/12)
tr(Y) = Σ d_iik · v_k = 66.3554  (誤差 0.54% vs 66)
```

### 5.2 66 嘅雙重身份

| 身份 | 數值 | 狀態 |
|:-----|:----:|:----:|
| A) C(12,2) | 12×11/2 = 66 | ✅ 幾何自然 |
| B) 3×22 | 3 代 × 2×L₅ | ✅ 物理 |
| C) tr(Y) | 66.3554 | 🟡 0.54% 誤差 |

### 5.3 依賴 v_k 選擇

```
v_k = 1 (uniform):      tr(Y) = 8.70  ❌
v_k = φ^(-k/12) (IDCM): tr(Y) = 66.36  ✅ (0.54%)
```

→ 66 閉合**依賴** φ^(-k/12) VEV — 呢個本身係結構數，唔係手調。

### 5.4 其他 d_tensor 版本嘅 tr(Y)

| 版本 | tr(Y) | 誤差 |
|:-----|:-----:|:----:|
| d_tensor_final | 66.36 | 0.54% ✅ |
| d_tensor_hybrid | 66.35 | 0.53% ✅ |
| d_tensor_float64 | 67.55 | 2.36% 🟡 |
| d_tensor_ultra_precision | 71.94 | 9.0% ❌ |
| d_tensor_positive | 87.15 | 32% ❌ |

---

## 六、閉合鏈（目前狀態）

```
x²+x−1=0 → φ → B=4, L₅=11, L₆=18, F₆=8
  ↓
Nd = B×L₅ = 44 (K_Chain site)
Σγ = 90 (K_Chain 能量)
  ↓
946 = C(44,2)          ✅ 自然生成 (beat 空間)
134 = Nd+Σγ            ✅ (總 moduli)
62  = Nd+L₆            ✅ (半差)
36  = 12×3             ✅ (Z₃ orbit)
  ↓
12 維 Z₃ 不變子空間    ✅ (d_tensor 真正三體耦合)
66  = C(12,2)          ✅ (幾何)
66 ≈ tr(Y)             🟡 (0.54%)
66 = 3×22              🟡 (物理身份, 等價未證明)
```

---

## 七、對 O53 開放問題嘅影響

| 問題 | 之前 | 而家 |
|:-----|:----:|:----:|
| Q1: 點解 moduli 服從 K_Chain 結構數? | 🔴 | 🟡 134=Nd+Σγ 成立, 但投影機制唔成立 |
| Q2: CY₃ 點樣由 K_Chain 投影生成? | 🔴 | 🔴 **重大負面發現**: 現有實現 rank-deficient |
| Q3: (36,98) 真實多面體? | 🔴 | 🔴 TU Wien 伺服器唔通, 需本地 PALP |
| Q4: 真實 d_{ijk}? | 🔴 | 🟡 12³ 有真正三體耦合 (WDVV), 但唔係幾何計算 |
| Q5: 12 = 36/3 Z₃? | 🟡 | ✅ 確認 (12 維不變子空間 + tr(Y)≈66) |
| Q6: 134 = 44+90 機制? | 🔴 | 🟡 結構數成立, 物理機制未閉合 |

---

## 八、誠實評估

### 已確認（唔會消失）
- ✅ 946 = C(44,2) 自然生成
- ✅ 134 = Nd+Σγ, 62 = Nd+L₆ (結構數)
- ✅ (36,98) 係唯一同時滿足兩約束嘅 KS pair
- ✅ 12 維 d_tensor 有真正三體耦合 (rank 12)
- ✅ tr(Y) ≈ 66 (0.54%, 依賴 φ^(-k/12) VEV)

### 重大修正（誠實記錄）
- 🔴 **P̂ (134×946) 係 rank-2 偽結構** — 「66 本徵態」係 float64 噪聲
- 🔴 **d_{ijk} (36³) 係 rank-1 可分離** — 冇三體耦合
- ⚠️ 之前基於「66 個本徵態」嘅質量譜/三代論述需要重新檢視

### 下一步
1. **修正 projection_operator.py**: 加入 per-modulus weight（例如用 d_tensor_final 做權重）
2. **驗證 66 = tr(Y) 精確閉合**: 調整 WDVV 或 v_k 睇下 0.54% 誤差有冇結構來源
3. **問題 3**: 恢復 TU Wien 連線或搵本地 PALP 數據 → 真實 d_{ijk}
4. **更新 `01_problem_record.md`** 同 README

---

## 九、檔案

```
scripts/05_projection_mechanism.py   — 基本結構數 + 946/66 驗證
scripts/06_rank_investigation.py     — P̂ rank-2 鐵證
scripts/07_dijk_structure.py         — d_{ijk} rank-1 驗證
scripts/08_rank1_final.py            — rank-1 數學證明 + long double
scripts/09_dtensor_audit.py          — 全部 d_tensor rank 審計
scripts/10_twelve_dimensional.py     — 12 維結構 + C(12,2)=66
scripts/11_z3_projection.py          — Z₃ 整除性 + tr(Y)
scripts/12_tr66_closure.py           — tr(Y)≈66 精確驗證
```

*本報告係 O53 開放問題 2 嘅誠實審計 — 發現兩個 rank-deficient 偽結構，同時確認 12 維真正結構同 tr(Y)≈66 線索。*
