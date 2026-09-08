# O161 docs/02 — 鏈變數結構: link-space connection + Wilson line (T2)

> **日期**: 2026-09-08 · **腳本**: scripts/02_link_variables.py (35/35 PASS) · **狀態**: 🟢
> **目標**: 由譜導出 link-space 版本嘅 connection A_k (相鄰節點相位差 / beat phases),
> 驗證 1D 鏈唯一 gauge-invariant = Wilson line 嘅值。
> **原則**: links 係導出量, 唔係新自由度 (零參數鐵律)。

## 1. ★ Link 變數: U_k = e^{i·2θ_k} = e^{ikπ/88},  γ_k = |1 − U_k|²

O159 嘅 connection A_k = γ_k − μ² = −μ²cos(2θ_k) 係 **node 量** (mode index k)。
佢嘅 link-space 版本由**譜自身**導出:

```
site-link phase (D-D 行波每 site 相位) = 2θ_k = kπ/88   (script 01 C2.2 驗證)
U_k := e^{i·2θ_k} = e^{ikπ/88}
γ_k = |1 − U_k|² = 4sin²(kπ/176)        ← ★ 譜 = link 振幅平方 (1−U 嘅模長²)
```

- U_{k+88} = −U_k (link 變數反週期, 週期 176 — 同 odd 扇區 J² = −1 同源)
- **link 唔係新自由度**: U_k 完全由 θ_k = kπ/176 (譜格) 決定

## 2. Connection link-form: ΔA_k = Δγ_k, A 反週期

```
ΔA_k = A_{k+1} − A_k = γ_{k+1} − γ_k = Δγ_k   (∀k — link 差 = 譜斜率)
A_k = −μ²cos(2θ_k):  A_{k+88} = −A_k          (cos(2θ+π) = −cos 2θ — 反週期)
```

- **A = 譜流嘅 potential**: link 上嘅 connection 就係譜嘅離散導數; A 嘅
  反週期性 (mode index period 88) 係 J² = −1 結構喺 connection 層嘅重現
- 零偏差定理重現 (O159): Σ_odd A = 0 / Σ_even A = μ² / Σ_all A = μ²

## 3. Beat phase: 2Δθ = π/88 (fundamental beat quantum)

```
2Δθ_k = 2(θ_{k+1} − θ_k) = 2π/176 = π/88   均勻 (相鄰 mode 相位差)
beat 累積: j·π/88 — 跨 88 sites 累積 π
```

link-space connection = **譜格一步相位** (176-grid 嘅一步 = 1/88 圈)。
「beat phases 嘅譜來源」= 譜格步長本身, 唔係獨立參數。

## 4. ★★ Wilson line (mode-space): Π_k U_k = i

```
總相位 Σ_k 2θ_k = (π/88)·Σk = (π/88)·3916 = 44.5π = (F₁₁/2)π   (unwrapped)
Wilson line W = e^{i·44.5π} = i              ← Z₄ 生成元 (holonomy 階 4 = B)
holonomy mod 2π = π/2 = 2θ₄₄                ← 錨點相位 (connection 零點相位!)
winding = 44.5π/2π = 22.25 = F₁₁/4 = L₅ + ¼ (L₅ 全圈 + ¼ 錨圈)
```

**扇區分拆** (Wilson phase 嘅世界/觀察者分解):

| sector | Σ_k 2θ_k | Wilson line | 讀法 |
|:--|:--|:--|:--|
| 世界 (even) | 22.5π = N_d/2 + ½ 圈 | **i** | 攜帶複結構 (i = J) |
| 觀察者 (odd) | 22π = N_d/2 圈 = L₅·2π | **1** | 全圈閉合 (平凡) |
| 總 | 44.5π | **i** | 差 = π/2 = 錨相位 |

**閉合鏈**:
- i² = −1: 兩個世界圈 = 觀察者反週期 (**J² = −1**)
- i⁴ = 1: 四個世界圈 = double cover **352 = 4×88 = B·N_d** 閉合

Wilson line 嘅值 = **i** (總相位 44.5π = (F₁₁/2)π, mod 2π = π/2 = 錨相位)。

## 5. Wilson loop (site-space, 物理 88-cycle): e^{ikπ} = (−1)^k

```
每 site 相位 2θ_k, 88 sites: 總相位 88·2θ_k = kπ
Wilson loop_k = e^{ikπ} = (−1)^k = 扇區週期因子 (O159 A3: odd 反週期 / even 週期)
全體 Π_k e^{ikπ} = e^{iπ·3916} = 1 (Σk 偶數)
```

site-space Wilson loop = **扇區 Z₂ 電荷** (J² = ±1 嘅 loop 讀法)。

## 6. 1D pure-gauge 一致性 (「冇 plaquette」定量版)

```
局部曲率: 2·(π/88) − (2π/88) = 0        (任何局部閉環相位和 = 0 — flat)
最短零相位閉環: L·(π/88) = 2π ⟺ L = 176  (double cover 352 嘅一半)
88 links (半圈) = π/2 holonomy = i        (鏈 half-turn 未閉合 — 需 double cover)
```

- 1D 鏈曲率恆零 (均勻 link ⟹ 冇 local curvature); 唯一不變量 = **總 winding**
  (global/boundary 量) — 「1D 冇 plaquette」嘅定量表述
- **純 gauge**: 平連絡態 Φ_k = e^{−ikπ/88} 吸收成個 Wilson line (J ≡ 0, script 01 C5)

## 7. 判決 (R2, R4)

- ✅ **Link 變數導出**: U_k = e^{i2θ_k} (譜格導出, 唔係 postulate); γ_k = |1−U_k|²
- ✅ **Connection link-form**: ΔA_k = Δγ_k (link = 譜斜率); A_{k+88} = −A_k (反週期)
- ✅ **Beat phase**: 2Δθ = π/88 均勻 = 譜格一步
- ✅ **Wilson line 值**: mode-space W = i (總相位 (F₁₁/2)π, 世界 i / 觀察者 1,
  winding L₅ + ¼, holonomy 階 4 = B, i² = −1 ⟹ J², i⁴ = 1 ⟹ 352 閉合);
  site-space loop = (−1)^k (扇區 Z₂)
- ✅ 1D 冇 plaquette 定量版: 曲率恆零, holonomy = 總 winding (global)
- 🟡 剩: Wilson line = i 嘅「物理讀法」歸屬 (Z₄ = B 階 — 對應 B 譜頂 γ₈₈? —
  詮釋層); 完整連續規範場論 (gauge bundle 連續極限) 🔴 (O159 遺留)
