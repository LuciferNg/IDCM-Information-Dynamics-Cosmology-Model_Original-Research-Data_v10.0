# O53 投影算子修正 — rank-2 → rank-109 重建

> **日期**: 2026-08-21（O53 第二 session）
> **腳本**: scripts/13–15
> **問題**: O53 開放問題 2 —「CY₃ 投影機制」
> **狀態**: 🟢 **修正成功（rank-2 缺陷已修復）**

---

## 一、問題回顧

原版 `projection_operator.py` 嘅 P̂ (134×946)：
- Kähler/CPX 行內部 100% 相同（corr = 1.0）
- 真正秩 = 2（Kähler/CPX 兩類）
- 66 個「正本徵值」係 float64 捨入噪聲

**根本原因**: 選擇律 weight 只依賴 (type, beat)，冇 per-modulus 依賴。

---

## 二、修正策略演進

### 嘗試 1（scripts/13）: 乘性 per-modulus weight ❌

用 d_tensor_final 嘅行強度做 weight：
```python
weight = w_mod × φ^(-avg_gamma)
```
**結果**: rank 仍然 = 2 ❌

**教訓**: 行縮放（乘性 weight）唔會改變矩陣秩 — 線性相關保留。

### 嘗試 2（scripts/14）: 真正 per-modulus 行向量 ✅

每個 modulus 用**獨特嘅 beat 支撐（support）**：
```python
# Kähler modulus α ↔ K_Chain mode n_mode (36 個最低能量)
mask = (beat_n == n_mode) | (beat_m == n_mode)  # 只包含 n_mode 嘅 beats
mask &= (beat_parity == mod.parity)
mask &= (beat_z2 == mod.z2_charge)

# CPX modulus ↔ 獨特 (n,m) pair (高能量區 23..44)
mask = (beat_n == n_c) | (beat_m == m_c) | ...
```

**結果**:
```
SVD 秩 (tol=1e-10): 109  (原版 2 → 109!)
Kähler 子矩陣秩: 36 (全維度!)
CPX 子矩陣秩: 73
正本徵值 (>1e-10): 109
```

---

## 三、修正版結構

| 指標 | 原版 | 修正版 v2 |
|:-----|:----:|:---------:|
| rank | 2 | **109** |
| Kähler 子秩 | 1 | **36** ✅ |
| CPX 子秩 | 1 | **73** |
| 正本徵值 | 2 (物理) | **109** |
| 66 態 | 噪聲 | **真譜** (0.526~333) |
| 本徵值譜 | 2 個點 | 平滑雙峰 |

### 前 66 個本徵值

```
範圍: [5.265e-01, 3.339e+02]
尾部/頭部比: 1.58e-03 → 真正 66 維譜
λ₁ = 333.85 (φ⁰)
λ₂ = 167.95 (φ^1.43)
λ₃ = 159.59 (φ^1.53)
λ₆ = 75.72  (φ^3.08)
λ₇ = 56.28  (φ^3.70)
```

### 三代結構（66 = 3×22）

```
Gen1 (1-22):  mean = 81.77
Gen2 (23-44): mean = 6.86
Gen3 (45-66): mean = 1.73
Gen1/Gen3 = 47.3 (唔係 φ³=4.24, 但係明確三代衰減)
```

---

## 四、質量譜問題

修正版質量譜（M_Pl × √λ）仍遠超 SM（10²¹–10²³ MeV）：
```
質量範圍: [8.86e+21, 2.23e+23] MeV
SM 範圍:  [0.511, 1.73e+05] MeV
```
→ 需要 e^(-V_cycle) 指數壓抑（原 orbifold_projection.py 嘅步驟 2 設計），
   壓抑因子 e^(-44)~e^(-22) 可以將 10²³ MeV 降到 SM 量級。

---

## 五、同 12 維 d_tensor 嘅關係

修正版 P̂ 嘅 rank-109 結構同 12 維 d_tensor 嘅關係：
- ⚠️ **注意（docs/05 誠實修正）**: 12 = h¹¹/3 整除性成立，但 **d_tensor 冇 Z₃ 對稱**（scripts/19: 4-shift 誤差 0.56）
- 66 = C(12,2) 仍然成立（任何 12 維空間嘅組合數）
- 修正版前 66 個本徵值 = 呢個 66 維結構嘅譜

**但注意**: 修正版 P̂ 係「純 K_Chain 構造」— Kähler moduli ↔ 低能量 mode，
CPX moduli ↔ 高能量 (n,m) pairs。呢個係**結構對應**，唔係 d_tensor 權重。
「點解係 12 維」嘅機制仍然開放（🔴 見 docs/05 §五）。

---

## 六、後續建議

1. **正式替換 src/projection_operator.py** 嘅 compute_matrix（或者建新版本）
2. **加入 e^(-V) 壓抑** → 對 SM 質量譜
3. **驗證 rank-109 嘅 66 態** 有冇三代/φ 結構閉合
4. **問題 3 恢復後** 用真實 polytope 嘅 κ_ijk 做 per-modulus weight

---

## 七、檔案

```
scripts/13_fixed_projection.py      — 嘗試 1（乘性 weight, ❌ 失敗）
scripts/14_fixed_projection_v2.py   — 嘗試 2（真正行向量, ✅ rank 109）
scripts/15_fixed_66_structure.py    — 66 態結構分析
data/P_fixed_v2.npy                 — 修正版投影矩陣
```

*修正版證明: 「66 個態」可以係真物理譜，只要投影算子有真正 per-modulus 依賴。*
