# O123 docs/02 — Stage B: 路線 no-go 判定 + 230° numerology 判證

> **日期**: 2026-09-27
> **腳本**: `scripts/01_treephase_nogo.py` (2/4 PASS), `scripts/02_tensor_phase_nogo.py` (4/4 PASS),
> `scripts/04_numerology_null_230.py`
> **性質**: 攻堅前置判定 — 收窄 δ_PMNS 嘅可能機制空間
> **前置**: O54 🟢, O59 🟢, O53 🟢; ckm_reconstruction (T1–T13); ChronologicalStringSpectralGeometry-v2/docs/06

---

## 0. 為甚麼要 Stage B

`SESSION_START.md` 指定路線 = 「先補 δ_CP 本體推導（由 **CY₃ 投影 / Z₅ twisted sector**）」。
本輪先驗該路線 + 上游現存 4 個互相矛盾嘅 δ_PMNS 候選，再落推導。

**上游候選清單（互相矛盾）**:

| 候選 | 值 | 出處 | 本輪裁決 |
|:--|:--:|:--|:--:|
| 360°/φ | 222.492° | v9.0 `p_nu_delta_cp`; v10 `docs/pmns_derivation.md` 混用 | 🔴 φ-trap |
| 2π/5 | 72.0° | O65; `docs/pmns_derivation.md`; CSG-v2/docs/06 | 🔴 Z₅ no-go |
| 4π/5 | 144.0° | O65 twisted; `jcp_derivation.md` | 🔴 Z₅ no-go |
| 72.6° | 72.6° | O137 `docs/15` | 🔴 無來源 |
| (K_tree+F₇)(L₅−2N_gen) | 230.00° | ckm `docs/09` §14.4; Master Theorem T9 | 🔴 numerology |

---

## 1. B(a) — tree-sector 相位算子 no-go (`scripts/01`)

### 1.1 T1 複結構事實 (✔)
T̂ = [[1,1],[1,0]] 譜 = {φ, −1/φ} **全實**；φ, β, ε, K_tree, Lucas/Fibonacci 全實。
⇒ tree sector ⊂ ℝ ⇒ 任何 tree 算子 O 嘅 arg(O) ∈ {0, π}
⇒ **tree sector 內嘅相位只可能係 `atan(實比) + {0°,180°,360°}`**。

### 1.2 T2 null control (✔) — 關鍵
生成式家族 = `atan(a/b)`（常數池 42 個、預算 ≤2 常數）+ 0/180/360 offset，共 2751 式。
400 個隨機 target：
- 命中率 (tol = 1e-6) = **0.0%**
- 命中率 (tol = 1e-9) = **0.0%**
- 平均最近距離 = 5.60°

⇒ `atan(實比)` 家族**有結構選擇性**（對比：整數度數算術家族覆蓋 100%，見 §3）。

### 1.3 T3 候選最佳命中 (✘)
| 候選 | 值° | 最近生成式 | dev° |
|:--|:--:|:--|:--:|
| NuFIT 6.1 NO | 212.0 | `180+atan(F₅/F₆)` | 5.4e-3 |
| PDG 2025 | 217.8 | `180+atan(ω₇/ω₉)` | 1.2e-1 |
| NuFIT 6.0 NO | 177.0 | `180+atan(γ₁/γ₄₄)` | 3.0 |
| IDCM 230 | 230.0 | `180+atan(β²/ω₉)` | 5.2e-2 |
| v9.0 222.5 | 222.49 | `180+atan(42/46)` | 9.5e-2 |
| Z₅ 144 | 144.0 | `180+atan(γ₁/γ₄₄)` | 36.0 |

**冇任何候選達結構級 (dev < 1e-8 ∧ mult = 1)** — 但最佳式 `180+atan(F₅/F₆) = 212.0054°` 值得追（→ Stage A）。

### 1.4 T4 剛性 (✘)
`(N_gen·L₅+F₇)(L₅−2N_gen)` 在 ±1 擾動下存活 1/27 → 剛性形式上有，但配合 §3 嘅 115 witness 無意義。

---

## 2. B(b) — 張量相位 / 複結構來源 no-go (`scripts/02`, 4/4 PASS)

### 2.1 U1 張量積譜全實 (✔)
K = K_chain ⊗ K_tree (dim 616)：`max|Im(λ)| = 0.00e+00`，`max|K−Kᵀ| = 0.00e+00`。
⇒ 張量積**無內在複相位**。

### 2.2 U2 複結構來源清單
| 物件 | 實/複 | 備註 |
|:--|:--:|:--|
| ℚ(ζ₅) Z₅ twist ω = e^{2πi/5} | **複** | 唯一複結構 |
| Fibonacci F-matrix 元 −φ⁻¹ | 實 | 只有符號 π 相位 |
| A₅ 鄰接 cos = (19+8√5)/41 | 實 | 純實譜 |
| 88-鏈 Laplacian γ_k = 4sin²(kπ/176) | 實 | 實對稱 |
| T̂ tree 轉移矩陣 | 實 | 譜 {φ, −1/φ} |

### 2.3 U3 P4 no-go 重現 (✔)
up/down 每代 Z₅ 電荷：gen3 (0,1)、gen2 (3,4)、gen1 (1,2) ⇒ Δq = (1,1,1) **uniform**
⇒ V = diag(e^{2πiΔq/5}) 全對角 ⇒ J = Im(V₀₀V₁₁V₀₁*V₁₀*) = **0.000e+00**。

### 2.4 U4 non-uniform Z₅ twist 全枚舉 (✔)
可達相位角 (mod 360) = {0°, 72°, 144°, 216°, 288°}。
**包含 212°? False；包含 230°? False。**

### 2.5 U5 相位來源計數
複結構來源數 = 1（Z₅）；被 P4 no-go 殺 ⇒ **可用 = 0**。
⇒ **複結構路線全滅 ⇒ δ_PMNS 唯一可能機制 = 「實比 arctan」**（同 δ_CKM 同款）。

---

## 3. 230° = 5×46 嘅 4 Hard Tests (`scripts/04`)

`ckm_reconstruction/docs/09` §14.4 + Master Theorem T9 宣稱
`δ_PMNS = (K_tree+F₇)(L₅−2N_gen) = 46×5 = 230.00° EXACT`，並有「雙重選擇規則 (mod-5 ∧ J_CP) 唯一鎖定」。

| Hard Test | 結果 | 裁決 |
|:--|:--|:--:|
| ① dof 成本 | 形式 0 參數 | ✔ |
| ② 窮舉 null (35 常數, 預算 ≤3) | **[0,360) 可達 360/360 = 100%**；命中 230 嘅 distinct 式 = **115 條** | ✘ |
| ③ 可證偽/盲測 | 判準「J_CP 0.4%」用 δ=232°（同一擬合）導出 ⇒ **循環**；現行 J(212) ≈ 0.0177 vs J(230) = 0.0257 → 44% off；無 CP-獨立預言 | ✘ |
| ④ 剛性 | ±1 擾動存活 1/27（但配合 115 witness 無意義） | ✘ |

**裁決**: coverage 100% ⟹ p(hit) ≈ 1 ⟹ **零信息量**。「唯一」係假象（115 條 witness）。
δ_PMNS = 230° = **numerology 級 🔴**，唔可以宣稱閉合。

**但**: `46 = Σγ(k≡0 mod 4, k=4..88) = 46.000000` 係**真身份 🟢**（追蹤至 γ 譜）；
`46 = N_d⁻ + B = K_tree + F₇` 亦精確。**死嘅係「×5」同「唯一」**，唔係 46。

---

## 4. Stage B 收窄結論

```
B(a): tree sector ⊂ ℝ        ⟹ 相位形式 = atan(實比) + offset  (且有選擇性, null 0%)
B(b): 複結構來源 = 0          ⟹ 排除 complex-phase / Z₅ twist / 張量內在相位
     230° 4 Hard Tests 3 關 FAIL ⟹ 排除「整數度數算術」類候選 (含 230)
────────────────────────────────────────────────────────────
剩餘機制空間: δ_PMNS = n·180° + atan(r),  r = tree-sector 實比
```

⇒ 交 Stage A（`docs/03`）做 `r` 嘅結構選擇。
