# O130 — v9.0 wavelet_toolbox → v10.0 遷移判決

> **日期**: 2026-09-27
> **方法**: 逐項 P/R/A/X 分類 (O135 分類法) + 實數重算 (3 scripts, 32/32 PASS)
> **v9.0 來源**: `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/wavelet_toolbox/` (9 scripts + emd_engine)

---

## 一、範圍

v9.0 `wavelet_toolbox/` 做三件事:

1. **方法層** — 用離散小波 (DWT sym6) / EMD sifting 取代多項式擬合，分離 BOSS/eBOSS ξ(s) 嘅
   broadband 同 K_Chain 諧波信號 (01/02/03/04/06)。
2. **偵測層** — 喺 λ_sync/n 位置搵諧波峰；喺 λ_sync/(2n|R_n|) 位置搵阻抗反射尺度 (01/02/03/04)。
3. **兩個定量聲稱** — φ-ratio (A_n ∝ φ^n, 08/09) 同 z=17 宇宙視界 aliasing 截止 (07/09)。

SESSION_START 前置要求：先判 v9.0 推導喺 v10.0 **非膨脹框架** 下邊啲存活、邊啲失效。

---

## 二、P/R/A/X 判決表

| 類 | v9.0 項 | 判決 | 依據 |
|:--:|:--------|:-----|:-----|
| **P** | `γ_n = 4 sin²(πn/88)` K_Chain 譜 | ✅ 遷移 | 88-site 環 Laplacian 精確譜 (B1, dev<1e-12)；Σγ=176=4N_d (B2)；γ₄₄=4=B (B3)；鏡像 γ_n+γ_{44−n}=4 (B4)；v10.0 O124/O211 同式 |
| **P** | `λ_sync = 2πR_H/88 ≡ πR_world/44` | ✅ 遷移 | 代數恆等 dev=0 (A1)；R 註冊捨入 3.78e-7 (A2)；BAO=λ/2=147.44 (A3)；sync = 88 環諧和 m=88 精確 (A4, O133) |
| **P** | `v_g = cos(πn/88)` 群速度 | ✅ 遷移 | v10.0 O99 色散 (B5) |
| **P** | `B = L₃ = 4` MERA 分支、`z = 4^ℓ − 1` | ✅ 遷移 | v10.0 O76 離散 z (E2) |
| **P** | 小波 + EMD broadband 移除**方法** | ✅ 遷移 | 框架無關 (方法層)；emd_engine.py 原樣遷入 scripts/ |
| **A→🔴** | 阻抗 `Z_n=γ_n/|v_g,n|`、反射 `R_n`、`s_ref=λ_sync/(2n|R_n|)` | 🔴 排除 (部件 P / 模型無主) | 部件全部係 P 量 (C1/C2)，但模型本身**無 v10.0 對應算子**，且 **O118 已裁定「唔需要局部阻抗模型、唔需要搬遷 v9.0 SYNC 系列」**（與 O131 判決一致；本輪反射階梯 169–190 h⁻¹Mpc 同 O131 完全吻合） |
| **R** | φ-ratio `A_n ∝ φ^n` | 🔴 已證偽 | v9.0 自己 (09_math_verify) 已證偽；本輪獨立複核 (F1/F2, A1/A2) |
| **R** | z=17 尖銳視界截止 / Nyquist aliasing | 🟡 部分 | z=17 = F_proj 存活 (O138 量子-經典邊界)；但 ℓ=log₄18=2.085 **唔係 rung** (E2)；aliasing 讀法需 v10.0 載體 |
| **X** | `H(z)=H₀(1+z)^α` with ζ(z) (05_emd_hz) | 🔴 膨脹紀元 | ζ(z) 已 demote；Ω_Λ=41/60 常數 ⟹ 無 DE(z) 放電載體 (D2) |
| **X** | sync dip `z_c = 3/5 = 0.6` (經 ζ) | 🔴 已撤回 | O126 §D；ℓ(0.6)=0.339 非 rung (D1) |

---

## 三、關鍵發現 (新，非 v9.0 原有)

### 3.1 「EMD 偵測 17/19 諧波」係單調斜坡偽影 🔴

本輪重跑 (scripts/02) **複現** v9.0 數字：BOSS EMD 17/18、BOSS wavelet 3/18、
eBOSS EMD 10/18、eBOSS wavelet 0/18 — 同 v9.0 嵌入聲稱 (17/19 / 3/19 / 11/19 / 0/19) 一致。

但 scripts/03 §B 揭示：EMD residual 嘅 S/N 序列對 n **嚴格單調**
(Spearman ρ = **0.9979**, p = 1.65e-20)，且 EMD 只抽出 **1 個 IMF** (C1 in script 02) —
即「residual」= 一條平滑趨勢斜坡。「17/18 諧波偵測」= 斜坡喺細 s 處越過 3σ，
**唔係 17 個解析到嘅諧波**。

### 3.2 K_Chain 階梯喺 BOSS DR12 只解析到 n ≤ 8 🔴

諧波間距 `Δs_n = λ_sync/[n(n+1)]`；BOSS DR12 bin 間距 = 5 h⁻¹Mpc。
解 `Δs_n ≥ 5` 得 **n_max = 8.53** ⟹ 只有 n = 3..8 (6 個) 解析得到；
n = 9..20 全部係 **sub-bin aliasing** (scripts/03 §C)。v9.0 報嘅「19 諧波」有 12 個超出解析度。

### 3.3 φ-ratio 不可辨識 🔴

EMD 幅度 A_n 係單調序列 → φ^n 同 γ_n 兩者都擬合得到；
log A_n vs n 斜率 = 0.2937，距 log φ = 0.4812 **39%** (A1) ⟹ φ-law 證偽；
γ_n 模型 RMS 0.3115 明顯優於 φ^n 模型 0.6064 (A2)。

### 3.4 方法敏感度 = 非結構預測 🟡

同一份 BOSS 數據，broadband 移除法唔同 → 偵測率 4/19 (多項式) / 3/19 (小波) / 17/19 (EMD)。
偵測率係**方法依賴**量，唔係結構預測 (scripts/02 §F)。

---

## 四、可遷移資產 (v10.0-native)

- **`λ_sync = πR_world/44`** 諧波階梯位置 `s_n = λ_sync/n` (同 O129 σ_sync 階梯一致)。
- **k-space 對應** `k_n = n·(2π/λ_sync) = 88n/R_world` — 同 **O133** BAO wiggle 位置一致
  (sync = 88 環諧和 m=88 精確；44-site 鏈諧和 = 44/π = 14.0056 非整數 = 錯 grid)。
- **小波 / EMD 工具** 作為 broadband 移除方法 (框架無關)。
- **阻抗階梯** `Z_n = γ_n/|v_g,n|`, `R_n`, `s_ref` — 部件係結構，但**模型無 v10.0 擁有者**，
  O118 已裁定唔做 ⟹ **排除**（非可遷移資產）。

> ⚠️ 同 **O131**（stacking_toolbox 遷移，2026-09-27）判決一致：v9.0 阻抗反射模型
> 「🔴 無 v10 對應 + O118 已裁定唔做」；兩 O 獨立重跑得同一反射階梯 169–190 h⁻¹Mpc。

---

## 五、交叉引用

| O | 關係 |
|:--|:-----|
| O133 | k-space 對應 (sync = 88 環諧和, 7/9 命中 BOSS)；本 O 嘅 06_emd_pk 同 O133 同 grid |
| O129 | λ_sync 幾何 (dev=0) + σ_sync = λ_sync/(2n) 階梯；σ_sync 算子歸屬 O100/O133/O128 |
| O126 | sync dip z_c=0.6 撤回 (本 O 05_emd_hz 用同一 ζ 模型 → X) |
| O138 | z=17 = F_proj 量子-經典邊界 (存活) |
| O76 | z 離散 `1+z=4^ℓ` (rungs 0,3,15,63) |
| O99 | v_g = c·cos(πn/88) 色散 (相位扇區) |
| O135 | P/R/A/X 遷移分類法 (本 O 沿用) |
| **O131** | **同批 stacking_toolbox 遷移 (2026-09-27)**；獨立重跑得同一阻抗階梯 169–190 h⁻¹Mpc；判阻抗模型 🔴 無 v10 對應 |
| **O118** | 裁定「唔需要局部阻抗模型、唔需要搬遷 v9.0 SYNC 系列」(前提作廢) |

---

## 六、驗證統計

| Script | PASS | 內容 |
|:-------|:----:|:-----|
| `scripts/01_migration_inventory.py` | **18/18** | λ_sync 幾何 / γ_n 精確譜 / 阻抗階梯 / H(z) ζ / z=17 / φ-ratio / P-R-A-X 表 |
| `scripts/02_wavelet_emd_rerun.py` | **9/9** | 實數據 DWT+EMD broadband 移除重跑 + 諧波掃描 + 反射階梯 + k-space 對照 |
| `scripts/03_significance_null.py` | **5/5** | φ-ratio 不可辨識 / 斜坡診斷 / BOSS 解析度極限 |
| **合計** | **32/32** | + 14 結構聲稱 |

---

## 七、開放問題

1. **eBOSS 反射尺度** 🟡: eBOSS 範圍 (7.5–247.5 h⁻¹Mpc) 覆蓋全部 s_ref (169–190) —
   可作獨立檢驗；本輪只做 BOSS。
2. **解析度升級** 🟡: DESI DR2 ξ(s) bin 更細 → n_max 提升；可重跑諧波階梯檢驗。
3. **aliasing 機制** 🔴: v9.0「z=17 視界 aliasing」喺 v10.0 離散 z 下無載體 —
   需決定是否重新形式化 (或併入 O76)。
4. **阻抗/反射算子** 🟡: v10.0 有無 native 阻抗概念？若無，Z_n/R_n 只係 v9.0 傳輸線類比。
