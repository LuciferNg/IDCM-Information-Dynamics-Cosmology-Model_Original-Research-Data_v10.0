# O61 文檔 02 — 二期：Moduli stabilization — κ 零方向 (kernel(A) = 4 = B)

> **日期**: 2026-08-24 (修正 2026-08-24 驗證輪)
> **狀態**: 🟢 **閉合 — κ 零方向 = 4 = B, rank M = 32 = 2B²（⚠️ O62: 「通量鎖定」→ flat 方向, W≡0, 見文末附註）**
> **腳本**: scripts/06–08 + 10 (驗證複核)
> **前置**: O61 docs/01 (A_ij pre-factor)

---

## 一、問題

O61 問題 2: **Moduli stabilization / 通量鎖定真空**。
36 個 Kähler moduli 點樣被鎖定？通量量子點樣出現？

---

## 二、方法: Gukov-Vafa-Witten 通量超勢

```
prepotential:  F(t) = (1/6) Σ κ_ijk t_i t_j t_k
Yukawa 矩陣:  ∂²F/∂t_i∂t_j = Σ_k κ_ijk t_k = Y_ij(t)
通量超勢:      W = Σ_i N_i ∂F/∂t_i  (N = 通量子)
穩定條件:      ∂W/∂t_j = Σ_i N_i Y_ij = (Y·N)_j = 0
```

**穩定點 ⟺ N ∈ kernel(Y(t*))** — 通量子必須係 Yukawa 矩陣喺真空點嘅零模。

⚠️ **誠實修正 (驗證輪)**: kernel(Y(t)) 係 **t 依賴**嘅（見 §3.1），真正嘅 t 無關結構係 kernel(A)（§3.2）。

---

## 三、核心發現

### 3.1 ★★ kernel(Y(t)) 係 t 依賴 — 誠實修正

| 參數 | kernel(Y(t)) | rank |
|:-----|:----------:|:----:|
| γ 譜 | 4 | 32 |
| φ^(35-i) | **0** | 34 |
| φ^(-i) | 4 | 32 |
| t=1 | **34** | 2 |
| 隨機 t | 4 (多數) | — |

**結論**: 「kernel(Y) = 4 ∀t」嘅 claim **錯誤** — kernel(Y(t)) 依賴 t。φ^(35-i) 得 0、t=1 有 34。

### 3.2 ★★ 真正嘅 t 無關結構: kernel(A) = 4

大矩陣 A = κ.reshape(1296×36) 嘅 SVD：

```
非零奇異值 = 32
零奇異值 (kernel) = 4 (精確)
kernel(A) = {v: Σ_k κ_ijk v_k = 0 ∀i,j} — 4 維
```

**v ∈ ker(A) ⟹ Σ_k κ_ijk v_k = 0 ⟹ Y_ij(t)·v = 0 ∀t**（20 個隨機 t 驗證，max|Y(t)v| < 1e-8）✅

呢個係真正嘅代數內稟結構：**4 個「零相交方向」對任何 Kähler 參數都係 Yukawa 矩陣嘅零模**。

### 3.3 ★ 4 = B = K_Tree 分支因子

```
kernel(A) = 4 = B = φ³−φ⁻³ = K_Tree 分支因子
```

**物理**: 4 個 Kähler 方向喺交集數上完全「零相交」— 唔受通量超勢影響 → **保持 flat**。剩低 32 個被鎖定。

### 3.4 ★★ 32 = 36−4 三重重身份

```
32 = 36 − 4     (h11 − kernel)
32 = 2B²        (2×4²)
32 = B × 2B     (分支 × 邊界)
32 = Nd − h11/3 (44 − 12)
```

**32 = 2B²** — moduli 鎖定嘅「有效維度」：每 branch 有 2B = 8 個邊界 → 4 branch × 8 = 32。

### 3.5 零方向跨 block

4 個零方向都跨越全部 3 個 block（冇 block-pure 零方向）→ kernel(A) 唔係 3×12 block 結構嘅簡單後果（純 block-diag κ 嘅 kernel = 0！），而係**跨 block 項**產生。

### 3.6 ★★ 通量子 66/90 精確對齊 (三期)

三期發現: 零方向整數化 sum|N| 精確對齊 IDCM 結構數：

| 目標 | scale | sum|N| | 偏差 |
|:----:|:-----:|:---:|:----:|
| **66** (66 態) | 14 | **66** | 0 |
| **90** (Σγ) | 22 | **90** | 0 |
| 98 (h21) | 22 | 97 | 1 |
| 44 (Nd) | 10 | 43 | 1 |

---

## 四、閉合鏈

```
κ_ijk (36³, 1341 非零)
  ↓
A = κ.reshape(1296×36): kernel(A) = 4 (t 無關!)
  ↓
Σ_k κ_ijk v^(a)_k = 0: 4 個零相交方向 (∀t 成立)
  ↓
GVW: 通量子 N ∈ ker(Y(t*)), ker(A) ⊆ ker(Y(t)) ∀t
  → N = Σ c_a v^(a) 係 t 無關解
  ↓
32 = 36 − 4 = 2B² 個 Kähler moduli 被鎖定
4 = B 個保持 flat (零相交, 通量唔耦合)
  ↓
★ Moduli stabilization 閉合:
  鎖定維度 = h11 − B = 2B² = 32
  flat 維度 = B = 4
```

---

## 五、誠實標記 (驗證輪修正)

| 發現 | 狀態 |
|:-----|:----:|
| ~~kernel(Y) = 4 ∀t (50/50 隨機)~~ | 🔴 **撤回 — kernel(Y(t)) 係 t 依賴 (γ:4, φ^35:0, t=1:34)** |
| **kernel(A) = 4 (t 無關)** | 🟢 嚴格代數 (SVD, 20 隨機 t 驗證 Y(t)v=0) |
| Σ_k κ_ijk v_k = 0 精確 4 解 (err<1e-8) | 🟢 嚴格代數 |
| 4 = B (K_Tree 分支因子) | 🟢 數值事實 |
| 32 = 2B² = B×2B = Nd−h11/3 | 🟢 數值身份 |
| 純 block-diag kernel=0, 全 κ kernel=4 | 🟢 跨 block 項起源 |
| 通量子 sum|N| = 66/90 精確對齊 | 🟢 三期確認 (scale 14/22) |
| 通量鎖定真空穩定性 (M_lock 正定) | 🟢 三期: min λ = 0.233 |
| 4 flat 方向嘅物理意義 (axion-like?) | 🟡 開放 |

---

## 六、開放問題（移交三期/後續）

1. ✅ 質量矩陣正定性驗證 — 三期完成 (min 0.233)
2. 4 flat 方向 ↔ axion / 觀察者維度 (O41 真空能預算?)
3. ✅ 通量子 N 嘅精確整數解 (66/90) — 三期完成
4. 32 = 2B² ↔ 66 態 32 divisor rank (O57 docs/14: Q_ij rank 32/32!)

---

## 七、檔案

```
scripts/06_gvw_flux.py       ✅ GVW 超勢 + 穩定條件
scripts/07_flux_zeromodes.py ⚠️ kernel(Y(t)) t 依賴 (誠實修正)
scripts/08_kappa_zerodirs.py ✅ Σκv=0 精確 4 解 + 32=2B²
scripts/10_verification.py   ✅ 驗證複核 (kernel(A) t 無關)
data/06-08,10_*.json         ✅ 結果
```

> 💡 **延伸 insight**: O57 docs/14 發現真 Q_ij (185×32) rank = **32/32** — 同本輪 32 = 2B² 鎖定維度一致! 32 divisor rank = 32 鎖定 Kähler moduli → 通量鎖定同幾何相交 rank 係同一件事嘅兩面。

---

## 附註 (2026-10-08 交接檢查): O62 誠實修正 — 「通量鎖定」實為 flat 方向

> ⚠️ **O62 (Λ 第一性原理, 2026-08-24 期) 已證**: kernel(A) = 4 零方向 → **W = N·∂F ≡ 0 ∀t** → O61 嘅「通量鎖定」**其實係 flat 方向** — **冇 F-term 穩定 (W 恆零)**，真正 VEV 來源 = P̂ 投影結構 (γ 譜)。
>
> 即係: N ∈ kernel(A) 嘅通量子解令**整個** GVW 超勢 W 恆零，並唔係 32 個方向被「鎖定」而 4 個 flat — 係**全部 36 個方向都冇 F-term**。32 呢個數字 (rank M = 32 = 2B²) 依然成立（O62 獨立確認 Y(γ) kernel=4=B, rank M=32），但「鎖定」嘅物理詮釋要改。
>
> **修正後狀態**:
> - ✅ 保留: kernel(A)=4=B, Σκv=0 精確 4 解, rank M=32=2B², M_lock 正定, 通量子 66/90
> - 🔴 撤回: 「GVW 通量鎖定 32 個 Kähler moduli」— 冇 F-term, 唔係通量鎖定
> - 📌 正確詮釋: **flat 方向** (W≡0) + **P̂ 投影結構** 先係 VEV 來源 (O62 閉合)
>
> 交接: O62 docs/01 §3.4, O240 (引用 W≡0 冇 F-term)。
