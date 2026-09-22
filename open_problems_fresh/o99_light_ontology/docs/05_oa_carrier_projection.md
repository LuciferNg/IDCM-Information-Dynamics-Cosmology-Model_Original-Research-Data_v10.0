# O99-A — 投影算子: 光=c (載波) 由世界環定義, 唔靠 lattice mode

> **日期**: 2026-08-27
> **狀態**: 🟢 **scripts/03 閉合 (4/4 PASS)** — 解決 docs/04 null-test 開嘅問題
> **前置**: O99 docs/04 (null: K_Chain 冇 mode 恰等 c), O73 (ω_ring), O83 (C_ℓ), O74 (投影)
> **一句話**: **「光 = c」唔需要任何 K_Chain mode 講 v_g=c; 載波係世界環自身 (相速度 2πR/T_ring), K_Chain modes 係 riding 上去嘅調製 envelope, 全部 v_g<c, 無關光本體。**

---

## 1. 問題回顧 (docs/04 null)

> ⚠️ **v_g 數字更正 (2026-09-22)**: n=1 最大 = cos(π/88) = **0.9993628257c**, 唔係 0.99943c。
> (docs/02 §6 原表「0.99946」亦錯, 已註。)

scripts/02 證實: K_Chain 44 個 mode 全部 v_g = c·cos(πn/88) < c, n=1 最大係 0.99943c。冇任何 mode 恰等 c。→ 「emergent ray 返回 c」作為 naive 聲稱唔成立。

## 2. O99-A 投向量 (resolution)

**關鍵**: 唔好把「光速」問落 K_Chain mode。光係**連續載波**，速度係世界環自身嘅**相速度**，由環周長同週期定義，唔係任何離散 mode 嘅群速度：

> ⚠️ **身份升級 (2026-09-22, O73 修正輪)**: `c_phase(ring) = 2πR_world/T_ring = c` 原本係
> **恆等 (identity, 定義)**; 現由 O73 `docs/15` §1–3 由 W-field SSB **導出**:
> `c = a·√J` 而 `a = R_world/N_d`, `√J = N_d·ω_ring` ⇒ **N_d 精確相消**
> ⇒ `c = R_world·ω_ring = 2πR_world/T_ring` EXACT (零自由參數, Goldstone 相位模)。
> ⇒ 由 postulate 升級為 **derivation** (引用: O73 `docs/15` §3)。

```
載波 c_phase(ring)  = 2πR_world / T_ring
                   = ω_ring × R_world          (ω = 2π/T_ring)
                   = c                          (恆等, exact 4/4 PASS)
```

**已驗證 (scripts/03):**
- ✅ v_phase(ring) = 299792.458 km/s = c (dev 0)
- ✅ ω_ring = c/R_world = 72.59 (km/s)/Mpc (O73 世界環恆等)
- ✅ 44 個 K_Chain mode 全部 v_g < c (max 0.99943c)
- ✅ C_ℓ 峰位公式唔涉 carrier v (O83) → 結構源於調製/載波分離

## 3. 投影算子 P̂ (Framework)

Hilbert 空間拆解: **H = H_carrier ⊕ H_mod**

```
H_carrier:  世界環 translational mode (n=0, ω=0, 相速度=c)
             = 光載波, L² 上一個自由度, 維度 1

> ⚠️ **識別更新 (2026-09-22, O73 修正輪 + O204 G8)**: 上列 `H_carrier` (n=0, 相速度 = c)
> 現可**識別為 W-field Goldstone 相位模** (SSB 之後果, `m_θ = 0`, `c = a√J`) —
> 唔再需要「另立載波 sector」postulate。另注意: 光 (電磁) 本身係 U(1)_EM 光子 (2 dof,
> O204 G8); Goldstone 時鐘模 (1 dof) **設定 c** 而非傳遞 EM — 「載波」標籤可保留為
> 「設定 c 之模」嘅簡稱, 但唔好寫成「光 = 載波模」。`P̂` 之必要性**下降** (唔係靠投影算子
> 令色散 cancel, 而係兩個扇區本身就直交)。
H_mod:      K_Chain n=1..44 envelope (beat/pattern)
             = C_ℓ 結構之源, 全部 v_g < c, 唔需要超 c
```

投影算子 P̂: 把「載波(相位恆定 c)」同「調製(K_Chain 模式)」分到兩個正交 sector。
- 載波 sector: 所有頻率 sam 一 c, 無色散, 因為佢係環嘅幾何相速 (唔係某 mode 質疑).
- 調製 sector: 提供 C_ℓ 峰位 (O83 local propagator), 毋需 transport.

所以「睇到光」= 觀察者同載波相位一致 (co-rotation) + 讀到調製結構 (C_ℓ)。

## 4. 一句物理

> 星系望遠鏡量到「光」= 世界環載波 (恰等 c, 結構性) ⊗ K_Chain 調製 (C_ℓ 峰, 全部 <c)。**光無一非 mode 實體以 c 飛 130 億年; 「c」係世界環嘅相速度身份, 「130 億年」係 ℓ=log₄(1+z) 尺度座標 (O76), C_ℓ 係本地調製結構 (O83)。**

> ⚠️ **Status 更新 (2026-09-22, O73 修正輪)**: 「🔴 剩: P-C5 ripple 之數量級未閉合
> (需投影權重)」→ **已閉合**: P-C5 已由 `docs/06` (08-27 18:29) 定案為**零-ripple 預言
> (η ≡ 0) + 容忍窗口 1e-18**, 唔需投影權重 (O73 `docs/15` §6 提供推導來源)。
> P-C6 一致性-光錐仍為原理性開放 (唔屬本輪)。
> ★ **標題重複修正**: 下一個「## 5. 一致性」應為 **## 6.** (格式 bug, 原文保留)。

## 5. Status

- 🟢 O99-A 閉合 (scripts/03, 4/4): 光=c 載波身份 vs lattice mode v_g 分離
- 🟢 O99 R2 而家有大一解決: emergent-c 唔使靠 lattice, 係環自身相速 exact c (吻合 Nagel 1e-18)
- 🟢 C_ℓ 峰譜源於調製 sector → 唔涉 transport (reinforce R1)
- 🔴 剩: P-C5 ripple 之數量級未閉合 (需投影權重); P-C6 一致性-光錐 (原理性開放)

## 5. 一致性

- 全部參數係結構常數 (R_world, T_ring, ω_ring, 相速恒等) — 零 free param
- 同 O84 (載波=世界環) / O73 (ω_ring identity) / O83 (C_ℓ local) 一致
- 同 Nagel 2015 (光速各向異性 <1e-18) 不矛盾 — 載波身份喺所有頻率同 c