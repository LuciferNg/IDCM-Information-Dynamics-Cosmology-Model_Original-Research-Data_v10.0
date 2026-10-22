# O159 docs/01 — 邊界值問題嚴格解 (T1, R4)

> **日期**: 2026-09-08 · **腳本**: scripts/01_dirichlet_fieldtheory.py (A1–A4) · **狀態**: 🟢
> **問題**: R4 — Dirichlet → odd sector / Neumann → even sector 嘅邊界值問題嚴格解

## 1. 核心結果 (三個精確 BVP 事實)

### 事實 1: 176-Laplacian = 88-site half-site D-D 鏈

88 個 dual half-sites（位置 x_j = (j−½)a, j=1..88），邊界點 x=0 同 x=88a
（dual boundary points）夾制 φ=0。對應嘅離散 Laplacian 矩陣：

```
L_dual = diag(3, 2, ..., 2, 3),  off-diag −1    (88×88)
```

端點 diag=3（half-spacing 邊界修正）。本徵譜（88/88 驗證, tol 1e-9）:

```
γ_k = 4sin²(kπ/176),  k = 1..88        ← 176-Laplacian
Σγ = Tr = 178 = 2F₁₁
γ₁ = 0.00127435 (聲學支), γ₄₄ = 2, γ₈₈ = 4 = B
```

→ **O155 嘅「176-Laplacian 首 88 模」就係 88-site dual 鏈 D-D BVP 嘅嚴格譜**。

### 事實 2: Dirichlet−Neumann 跡差 = 2 = E−O (邊界夾制成本)

site 鏈（ghost 約束）兩個 BC 嘅跡:

| BC | 矩陣 | 譜 | Σ |
|:---|:-----|:---|:--|
| Dirichlet (pinned) | diag 2, off-diag −1 | 4sin²(kπ/178), k=1..88 | **176** |
| Neumann (free) | 同上, 兩端 diag 1 | 4sin²(kπ/176), k=0..87 | **174** |

```
Tr(Dir) − Tr(Neu) = 176 − 174 = 2 = E−O = γ₄₄ = μ²
```

**邊界夾制成本 = 扇區能量隙 = 自對偶本徵值** — 三樣嘢同一個 2。
(33-tree 鏈版本 66−64 = 2 亦成立, O155 05 C3；本處係 88 鏈版本。)
樹鏈 2 由端點度數虧缺 (2N vs 2N−2)；88 鏈 2 = 奇偶扇區和差 — 同值但不同機制,
兩者都精確, 唔好混埋。

### 事實 3: 奇偶扇區 = 反週期/週期 sector (J² = ±1)

Mode 函數 e^{ijkπ/176} 喺 176-shift 下:

```
e^{i(j+176)kπ/176} = (−1)^k · e^{ijkπ/176}
```

- **even k** (世界): 週期 (period 176), J² = +1 → 實扇區
- **odd k** (觀察者): **反週期** (period 352 — double cover 先閉合), J² = −1 → 虛扇區

half-shift J = T₈₈: odd sector 上 J² = −1 — **觀察者扇區自帶複結構 (imaginary unit)**。
「even = cos 實部 / odd = sin 虛部」(O155 T32 B) 由此獲得算子內容:
odd sector 嘅 J 就係 U(1) 相位旋轉嘅生成元骨架 (見 docs/03)。

## 2. 扇區譜分解 (T26 深度分層, 全部精確)

```
Σγ_even = 90  = 21×B + γ₄₄ + γ₈₈ = 84 + 2 + 4      (21 = F₈)
Σγ_odd  = 88  = 22×B                                (22 = 2L₅ 完整 Z₂ 對)
E−O      = 2  = γ₄₄
```

Z₂ 配對 k ↔ 88−k: γ_k + γ_{88−k} = 4 = B (sin²+cos² = 1 畢氏, k=1..43)；
k=44 自對偶 (88−44=44), γ₄₄ = B/2；k=88 Nyquist (γ=4) 配真空 k=0 (γ=0)。

## 3. 判決 (R4)

- ✅ 176-Laplacian 88-mode 譜 = half-site D-D 鏈 BVP 嚴格解 (88/88 模)
- ✅ Dirichlet−Neumann 跡差 = 2 = E−O = μ² (邊界夾制成本)
- ✅ odd = 反週期 (J²=−1, 虛/觀察者) / even = 週期 (J²=+1, 實/世界)
- 🟡 詮釋層 (O155 T32 B 讀法, 現有精確支持): Dirichlet (錨定/反週期) = 觀察者;
  Neumann (自由/週期) = 世界 — 字面上嘅「Dirichlet → odd」應讀作
  **「odd sector = 反週期 (twisted) sector」**, 唔係 site 鏈嘅 pinned BC;
  精確內容以本 doc 事實 1–3 為準
