# O161 docs/01 — 離散 Noether 電流 (T1)

> **日期**: 2026-09-08 · **腳本**: scripts/01_noether_current.py (34/34 PASS) · **狀態**: 🟢
> **目標**: 從 S = Σ_k (γ_k + μ²)|Φ_k|² 嘅 global U(1) 構造離散守恆流 —
> J_jj' = Im(Φ†_j U_jj' Φ_j'), Σ_j' J_jj' = 0, 電荷 Q = 44 = N_d 作為守恆流嘅總通量。
> **餵**: O122 (feynman_rules_wfield) — 離散 Noether 全鏈 (Lagrangian → EOM → Noether → 守恆律 → 電荷)。

## 1. 電荷算子: Q̂ = Σ_k w_k P_k

O159 嘅「電荷不對稱 Q = Σ_even k − Σ_odd k = 44」升級為 **charge operator**:

```
w_k = (−1)^k·k   (even 世界 +k / odd 觀察者 −k)
Q̂ = Σ_k w_k P_k,   P_k = |u_k⟩⟨u_k| (88-site half-site D-D 鏈模式投影)
Q = ⟨φ|Q̂|φ⟩ = Σ_k w_k |Φ_k|²
```

- canonical state (|Φ_k|² = 1 ∀k): **Q = 1980 − 1936 = 44 = N_d EXACT**
- **規範不變**: 任意 U(1) 相位旋轉 Φ_k → e^{iφ_k}Φ_k 唔改變 Q (occupation 不變)
- Parseval: φ†Mφ = Σ_k (γ_k+μ²)|Φ_k|² (mode/site 等價, 88/88 譜對齊)

## 2. Site-space Noether 電流 (global U(1), Q̂ = I)

```
J_{j,j+1} = Im(φ*_j φ_{j+1})      ← textbook lattice current (hopping −1)
```

**守恆律 (駐態無散)**: 對單模 φ = u_k, bulk Laplacian 恆等
2u_j − u_{j−1} − u_{j+1} = γ_k u_j (γ_k ∈ ℝ) ⟹ Im(u*_j u_{j+1}) = Im(u*_{j−1} u_j)
⟹ **J_j = J_{j−1}** — 電流沿鏈均勻 (divergence-free), Σ_{j'} J_{j,j'} = 0。

- **實駐波** (canonical Φ_k = 1): J ≡ 0 (實場冇淨流 — 正確物理, standing wave)
- **複行波** u^c_k(j) = e^{ij·2θ_k}/√88: J_j = sin(2θ_k)/88 — 均勻, 無散
  (site-link phase = **2θ_k = kπ/88**, 唔係 θ_k — γ_k = 4sin²(kπ/176) = 4sin²((2θ_k)/2))
- **k=88 Nyquist**: 2θ₈₈ = π — link 相位係實翻轉, J ≡ 0 (**Nyquist = 零流**)
  (對照: 錨 k=44 有 J = sin(π/2)/88 = 1/88 ≠ 0 — 「自對偶 = 零流」係錯讀, 已修正)
- D-D 實模結構: u_k(j) ∝ sin((j−½)·2θ_k) (half-site Dirichlet, 投影 = 1.000000000000)
- **反稱**: J_{j',j} = −J_{j,j'} ⟹ 閉鏈總通量 Σ_{jj'}J_{jj'} = 0 (冇源)

## 3. Twisted U(1) 電流: J^Q = Im(φ*_j (Q̂φ)_{j+1})

對單模 **因子化**: J^Q_k(j) = w_k · J^glob_k(j) (模式電荷抽出, 逐 link 驗證 k=7,21)。

canonical (實) 態: J^Q ≡ 0 (實駐波疊加)。

## 4. ★ 電荷 = 譜流總通量 (staircase flux)

```
J_k := Σ_{j≤k} w_j = (−1)^k·⌈k/2⌉   (1, −1, 2, −2, ..., +44)
w_k = J_k − J_{k−1}                  (電荷 = 譜流嘅散度)
Q = J_88 − J_0 = 44                  (譜鏈邊界淨通量)
Σ_k |J_k| = 1980 = Σ_even k          (總絕對通量 = 世界動量和!)
```

- **Q = 44 作為守恆流嘅總通量**: 兩個等價讀法 —
  (a) staircase flux: Q = J_88 (譜鏈邊界值);
  (b) site 密度積分: Q = Σ_j ρ_j, ρ_j = Re(φ*_j(Q̂φ)_j) = Σ_k w_k|u_k(j)|² (Σ = 44)。

## 5. Mode-space 電流 (T2 link 變數, 交叉驗證)

link 變數 U_{k,k+1} = e^{iπ/88} (T2 導出, script 02):

```
J_{k,k+1} = Im(Φ*_k U_{k,k+1} Φ_{k+1}) = sin(π/88)   (canonical Φ_k = 1, 均勻)
無散: Σ_k(J_{k,k+1} − J_{k−1,k}) = 0  (均勻流)
平連絡態 Φ_k = e^{−ikπ/88}: J ≡ 0     (相位抵消 link — 1D 純 gauge, Wilson line 吸收)
```

⚠️ throughput 88·sin(π/88) ≈ 3.1409 ≈ π — **小角極限數值, 🔴 唔係結構身份** (誠實標註)。

## 6. 判決 (R1)

- ✅ **J_jj' 顯式**: site-space J_{j,j+1} = Im(φ*_j(Q̂φ)_{j+1}) + mode-space J_{k,k+1} = Im(Φ*_k U Φ_{k+1})
- ✅ **ΣJ = 0**: 駐態無散 (bulk 恆等) + 反稱總通量 0 + 均勻 mode-space 流
- ✅ **Q = 44 = N_d 作為總通量**: staircase J_88 + 密度積分, 兩讀法一致, 規範不變
- ✅ 電荷算子化: w_k = (−1)^k k 由 O159 扇區符號直接搬入 (零新參數)
- 🟡 剩: 「電流載體係邊個態」嘅物理歸屬 (canonical 實態 J=0 vs 複行波 J≠0 —
  電流係 gauge-covariant, 電荷先係 invariant); 連續時空極限嘅 Noether 2-form 版本 🔴
