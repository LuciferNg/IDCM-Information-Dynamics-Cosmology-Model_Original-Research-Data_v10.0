# O133 docs/04 — O86 W-field 線性微擾判決 🔴

> 日期: 2026-09-02 · 狀態: **🔴 微擾傳遞唔閉合 broadband** · scripts: `scripts/04_o86_perturbation.py` (3/5 PASS)

## 背景

O86 統一 Lagrangian 已閉合 34/34，但其 §6 剩餘開放 #6「W-field 宇宙學微擾 (δg, δW, δφ) 🔴」係 broadband P(k) 傳遞嘅關鍵缺口。O133 docs/03 判定母函包絡 in-range 太扁 (Δn=+0.86)。本輪攻 O86 線性微擾 → P(k) 傳遞。

## 線性化（零自由參數）

```
L_W = ½(∂W)² + μ²|W|² − λ|W|⁴,   ⟨W⟩² = μ²/2λ = 61.5,  ⟨W⟩ = 7.842
      (μ² = 2 [O39: Σγ_even−Σγ_odd], λ = 2/123 [O39: 2/(3(N_d−3))])
W = v + δW:  V''(v) = 4μ² (單位制) ⇒ 物理 m_δW ~ M₀/2 = 13.95 MeV (O100 m_7)
δW EOM: (□ + m_δW²)δW = −ζ·v·δR + ...      (ζWR metric 耦合)
δ = δρ/ρ = 2δW/v                             (ρ ∝ |W|²)
空間譜: P(k_n) ∝ G_n(0) = 1/(2ω_n), ω_n = 2sin(πn/88), k_n = 44n/R_world
```

## 結果（scripts/04 v2: 修正單位換算 + 3 點取模 + Δn sign）

| 檢查 | 狀態 | 數值 |
|:-----|:-----:|:-----|
| A1 δW 宇宙尺度質量可忽略 | ✅ | m_δW ~ 13.95 MeV = 2.29e-9 Mpc⁻¹ (保守上限 M₀ = 4.58e-9 Mpc⁻¹) ≪ k_min = 0.0107 Mpc⁻¹ (r=4.3e-7) |
| A2 ζWR 耦合可忽略 | ✅ | κζ = 9.4e-22 ≪ 1 (O100 docs/06 量化驗證值) — 低能修正不影響傳遞 |
| B1 W-field propagator 下降功率律 | ✅ | P ∝ k^{−0.75} (3 點), full −0.88, 連續極限 −1.00 |
| B2 對照 BOSS | 🔴 | IDCM −0.75 vs BOSS −1.53 → **Δn = +0.78** (正=太扁) |
| C1 補充斜率來源 | 🔴 | 需要 steepen 0.78; K_Chain sin dispersion 只會更扁 (Nyquist v_g→0) |

**符號約定**: Δn ≡ n_model − n_BOSS, 正 = 模型太扁（需要 steepening）。docs/03 用 n_BOSS−n_model（+0.86 表示太扁）— 語義相同, 只係 sign flip；本輪起統一為「正 = 太扁」。

## 結構根因（升級自 docs/03）

**O100 ℳ 嘅逆 Abel 係純幾何映射：P(k) ∝ k²·C_ℓ(k·R_world)。** 代入 C_ℓ ∝ A_m/ℓ² (D_ℓ=A_m·D₁, C_ℓ=D_ℓ·2π/ℓ²)：

```
P ∝ [Poisson k⁴] · [C_ℓ ∝ A_m/ℓ²] · [1/k³] · [(2ℓ+1)] ∝ A_m   ← k 依賴完全抵消
```

IDCM P(k) 因此直接繼承 **CMB 聲學峰包絡 A_m**（含奇偶 zigzag），而**冇繼承物質傳遞函數 T(k)**。ΛCDM 入面：
- C_ℓ 峰 = 聲學振盪（A_m 型）
- 物質 P(k) = 初態譜 × T(k)², T(k) ∝ k^{−2} (k > k_eq, radiation-era Mészáros 壓制)

兩者來源唔同。IDCM 嘅 ℳ 將聲學包絡當成物質 P(k)，**缺少 k_eq 傳遞通道** — 呢個先係 broadband 太扁嘅真正結構原因。

## 三路徑收斂預覽（docs/05 完成, 此處只記 W-field 行）

> ⏱ 時序註記: 下表 P2/P3 行嘅最終數值由 **docs/05（scripts/05）** 喺 docs/04 之後完成 — 此處僅作前向引用預覽, 唔係 docs/04 嘅原始推導。W-field 行（本文件原始結果）+0.78 由 scripts/04 v2 支援。

| 機制 | P(k) 斜率 | Δn (正=太扁) |
|:-----|:-----:|:-----:|
| W-field 自由 propagator (O86) — scripts/04 原始 | −0.75 (−1.00 連續極限) | +0.78 |
| 全逆 Abel (閉合 9 峰) — docs/05 | −0.67 | +0.85 |
| 平滑 C_ℓ 包絡 (scale-invariant C_ℓ ∝ ℓ⁻³) — docs/05 | −1.01 | +0.51 |
| **BOSS/ΛCDM 物質 (需要)** | **−1.2 … −1.4** | — |

全部收斂到 k^{−0.7..−1.0}，觀測要 −1.2..−1.4 → **系統性 Δn ≈ +0.5..+0.8 缺口**（docs/05 最終: mean +0.71）。

## 判決

1. **O86 W-field 自由微擾唔係 broadband 形狀來源**（P ∝ 1/ω, 太扁）— A1/A2/B1 PASS 表明: 即使係 massless 傳遞（連續極限 −1.00）都唔夠 steep
2. m_δW 同 κζ 可忽略性 PASS → 傳遞唔受 W-field 物理修改（質量零、耦合零）
3. **真正缺口 = IDCM 缺少物質傳遞函數 T(k)（k_eq analog）** — 新結構需要 🔴
4. 下一步: (a) 識別 IDCM k_eq analog; (b) 完成 bias b²(k) 轉換 🟡 再對比; (c) 接受 flatness 為 IDCM 結構預言 vs ΛCDM 差異

## 檔案

- `scripts/04_o86_perturbation.py` — v2, 3/5 PASS (A1,A2,B1 ✅; B2,C1 🔴)
