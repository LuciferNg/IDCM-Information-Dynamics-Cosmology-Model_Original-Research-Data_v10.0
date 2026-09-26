# O125 — 散射振幅完整推導

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `open_problems_fresh/p_sa_scattering_amplitudes/`
> **前置**: O122 (Feynman 規則) 🔴, O124 (QCD 散射) 🔴, O82 (質量生成) 🟢
> **定位**: 從 v9.0 p_sa_scattering_amplitudes 遷移 — 完整 2→2 散射振幅從 W-field 晶格

---

## 一、問題

從 v9.0 p_sa_scattering_amplitudes 遷移 — 完整 2→2 散射振幅從 W-field 晶格

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `open_problems_fresh/p_sa_scattering_amplitudes/`
- 目標: 提取所有公式和數值

### 步驟 2：識別 v9.0 特有假設
- 列出所有依賴膨脹宇宙的假設
- 列出所有使用 v9.0 demote 參數的公式

### 步驟 3：在 v10.0 框架中重新驗證
- 用 v10.0 的 idcm_core.py 常數重新計算
- 與 v10.0 已閉合結果交叉驗證

### 步驟 4：遷移或重建
- 如果 v9.0 推導有效 → 遷移到 v10.0
- 如果 v9.0 推導失效 → 建立新推導

## 四、已知 v9.0 參考文件

- `open_problems_fresh/p_sa_scattering_amplitudes/`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

## 六、推導時序索引 (Derivation Timeline Index)

> ⚠️ 本節為 append-only 時序記錄 — 以上第一至五節原文一字不改。

### 6.1 事件表

| T# | 時間 | 事件 | Script | 結果 | 記錄 doc |
|:--:|:-----|:-----|:-------|:-----|:---------|
| T1 | 2026-08-29 | O125 建立 (從 v9.0 p_sa 遷移), 狀態 🔴 | — | 模板 only | `docs/01` (本文件) |
| T2 | 2026-09-03 | O122 (前置) 閉合 — 離散 Feynman 規則重建 | O122 scripts/01-03 | 47/47 PASS | O122 `docs/02-03` |
| T3 | 2026-09-26 | **O125 前置驗證**: v9.0 裁決 🔴 失效 | `scripts/01_preverification.py` | **16/16 PASS** | `docs/02_preverification.md` |
| T4 | 2026-09-26 | **O125 重建**: 1-loop 2→2 振幅 (有限離散框架) | `scripts/02_one_loop_scattering.py` | **20/20 PASS** | `docs/03_derivation.md` |
| T5 | 2026-09-26 | **O125 審計**: 交叉驗證 + 獨立重推 + 硬編碼掃描 | `scripts/03_cross_validation.py` | **14/14 PASS** | `docs/04_audit.md` |
| T6 | 2026-09-26 | **O125 §4 (O124 交接)**: gg→gg 完整極化求和 (16 組態 → 6 MHV; Σ = 1152 g⁴B) | `scripts/04_gg_gg_polarization.py` | **25/25 PASS** | `docs/05_gg_gg_polarization.md` |
| T7 | 2026-09-26 | **O125 §5 (docs/05 §9 🟡)**: 膠子 helicity λ=±1 **算子化** (ĥ = A₅ 反演 −I; ĥ²=1 ⟹ 譜 {+1×44, −1×44}; 88 = 2×44 = 2N_d; 幾何 chirality ⟹ 絕對定向) | `scripts/05_helicity_operator.py` | **51/51 PASS** | `docs/06_helicity_operatorization.md` |
| T8 | 2026-09-26 | **O125 §6 (docs/05 §9 🔴)**: B_disc 有限譜正則化 (collinear pole = 連續假象; Δω_min = 4sin²(π/176) ⟹ 冇 collinear 極限; 直接代入 ill-posed s+t+u≠0; 正確振幅 = V₄ 有限) | `scripts/06_bdisc_regularization.py` | **21/21 PASS** | `docs/07_bdisc_regularization.md` |

### 6.2 依賴鏈

```
v9.0 p_sa_scattering_amplitudes 🔴 (連續 φ⁴, 失效)
        │  遷移請求
        ▼
O80 (W-field Lagrangian) 🟢 ──► O82 (質量生成) 🟢 ──► O94 (有限 QFT) 🟢
        │                                                    │
        ▼                                                    ▼
O122 (離散 Feynman 規則) 🟢 ──────────────────────► O125 (1-loop 2→2) 🟢
        │                                                    ▲
        └── tree 2→2 (M⁽⁰⁾)                                  │
O142 (β = T̂ 不變量) 🟢 ──────────────────────────────────────┤
O211 (Σγ = B(N_d+1)/2 = 90) 🟢 ──────────────────────────────┘ (Σω_k² = 90 交叉)
```

### 6.3 譜定義注意 (邊個 script 用邊個譜)

| Script | 用嘅譜/對象 | 慣例 |
|:-------|:------------|:-----|
| `01_preverification.py` | v9.0 GeV 連續譜 vs v10.0 MeV 離散譜 (對照) | 88-site (2×N_d) |
| `02_one_loop_scattering.py` | `ω_n = 2sin(nπ/88)`, n=1..44 | K_Chain 44 模式 (正頻率) |
| `03_cross_validation.py` | 同上 + T̂ 特徵值 `φ,−1/φ` | mpmath 60 dps 獨立重推 |
| `04_gg_gg_polarization.py` | 88-ring 膠子 `ω_n = 2sin(nπ/88)`; SU(N) 生成元 `Tr(T^aT^b)=δ^{ab}` | 標準 color-ordered (Dixon); 離散 `s=(ω_a+ω_b)²` |
| `05_helicity_operator.py` | O182 88-grid (A₅ 透明邊中點); A₅ 反演 `−I` | 精確代數座標 Q(√5)³; 組合 + 幾何**雙路線** |
| `06_bdisc_regularization.py` | 88-ring 能階間距 (`Δω_min`); 連續 `B(s,t,u)` 對照 | 窮舉 56804 允許運動學 (非取樣) |

> ⚠️ **慣例陷阱**: O125 全部用 **88-site 鏈** (`ω_n = 2sin(nπ/88)`); 唔好同 176-Laplacian 或 K_Tree 33-節點譜混用 (O208 教訓)。

### 6.4 狀態更新

| 日期 | 狀態 |
|:-----|:-----|
| 2026-08-29 | 🔴 未開始 |
| 2026-09-26 | 🟢 **已閉合** (v9.0 失效裁決 + 重建 50/50 PASS; 唯一 🟡 = h 衰變通道 = N_gen 候選) |
| 2026-09-26 | 🟢 **O124 交接完成** (§4 gg→gg 完整極化求和, 25/25 PASS; Σ_{colors,spins}\|M\|² = 1152 g⁴B(s,t,u), 6/16 MHV 存活) |
| 2026-09-26 | 🟢 **§5 helicity 算子化完成** (`docs/05 §9 🟡` 解除): ĥ = A₅ 反演 `−I`; ĥ² = 1 ⟹ λ = ±1 **結構強迫**; 88 = 2×44 = 2N_d; 幾何 chirality ⟹ 絕對定向; 51/51 PASS |
| 2026-09-26 | 🟢 **§6 B_disc 正則化完成** (`docs/05 §9 🔴` 解除): collinear pole = **連續假象**; `Δω_min = 4sin²(π/176)` ⟹ 冇 collinear 極限; 直接代入 ill-posed (`s+t+u ≠ 0`); 正確振幅 = V₄ (有限); 21/21 PASS |

