#!/usr/bin/env python3
"""
Reconstruct O51 01_problem_record.md — original content + new section 10
"""
import os

# Read the current (overwritten) file to get section 10
current_file = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o51_kchain_origin/01_problem_record.md"
backup_dir = "/home/wsl/.hermes/backups"

with open(current_file) as f:
    current_content = f.read()

# The current content is only section 10 (new section)
# We need to prepend the original 647 lines

# Original content sections (from the two reads in this session):
original = """# O51 — K_Chain 有冇起始？(Origin of K_Chain)

> **創建日期**: 2026-08-21
> **狀態**: 🟢 數學結構閉合（三層證明）— 起始 = 種子 (0,1)，冇結尾 = 守恆 + 週期
> **來源**: 調律者「K_Chain 應該有起始，無理數人類算得多了」+「不是說還有拍頻嗎」
> **前置**: x²+x−1=0 → φ → 44-site K_Chain（整個 IDCM 基礎）
> **驗證**: sympy 精確代數（非數值逼近）+ 權威源 `src/kchain_wave_params.py` 對照

---

## 一、問題陳述

IDCM 長期標記「K_Chain 冇起始」為 🔴 未推導（`idcm-cosmology-analysis` skill 已記錄：
「K_Chain 永恆」係未經結構推導嘅假設，由「保守 = 冇熱寂 = 冇結尾」錯置成「冇起始」）。

**調律者洞察**: 無理數（φ、π）人類算到幾多億位，但佢哋**有定義、有生成起始** —
小數展開無限係「表示/演化無限」，唔等於結構冇起源。K_Chain 應該一樣。

**本問題目標**: 用精確代數證明 K_Chain 嘅起始/結尾結構，取代舊「永恆」模糊標籤。

---

## 二、三層起始證明（全部 sympy 精確代數）

### 層 1: 種子 (0,1) → φ

| 生成路徑 | 種子 | 極限 | 驗證 |
|:---------|:-----|:-----|:-----|
| 主遞歸 C_{n+1}=1/(1+C_n) | **C₀=1** | 1/φ = 0.6180339887 | C₇ dev=3.87e-4 |
| 連分數 [1;1,1,1,…] | **F₁=F₂=1** | φ = 1.6180339887 | F₁₂/F₁₁ dev=5.65e-5 |

**冇種子就冇疊代 → φ 有生成起始。** 無限性喺小數展開（潛在無限），唔喺結構。

### 層 2: 44-site K_Chain 譜

```
Nd = B × L₅ = 4 × 11 = 44
88 = 2 × Nd（半格點偏移 0.5 = log_B√B → 因子 2）
γ_n = 4sin²(πn/88),  n = 1..44
```

Lucas: L₅ = φ⁵+(−φ)⁻⁵ = **11**（exact 整數）；B = φ³−φ⁻³ = **4**（exact）。

| 量 | 值 | 驗證 |
|:---|:---|:-----|
| Σγ_even（44-site 偶數子集 n=2,4,…,44） | 46 | ✅ |
| Σγ_odd（44-site 奇數子集 n=1,3,…,43） | 44 | ✅ |
| Σγ_44site | 90 | ✅ |
| Z₂ 對偶 γ_n + γ_{44−n} = 4 | 43/43 對 | ✅ |

> ⚠️ **標籤對照（避免同 O34/O36 混淆）**: 46/44 係 **44-site 譜內**嘅奇偶子集分解。
> 「世界/觀察者」呢對標籤嘅**權威定義喺 88-site 對偶鏈**（O34 洞察 A, O36 驗證）:
> Σγ_even = 90（偶數 k=2n 完整重現 44-site 全譜 = 世界）、Σγ_odd = 88（奇數 k=2n−1 = 觀察者）。
> O51 嘅 46/44 唔係 O34 嘅 90/88 — 唔可以混用標籤。

**Nd 由種子結構強迫**（B=φ³−φ⁻³=4, L₅=φ⁵+φ⁻⁵=11），譜由 sin(πn/88) 生成，n 由 1 起。

### 層 3: 946 個拍頻（調律者關鍵補充）

| 檢驗 | 結果 |
|:-----|:-----|
| 拍頻組合數 | 946 = C(44,2)，由 Nd=44 生成，**有起始** (1,2) → 終點 (43,44) |
| sin(nπ/88) 有理嘅 n | **只有 n=44**（sin π/2 = 1）；其餘 43 個全無理代數數 |
| 對偶商 tan(πn/88) | 除 n=22（=1）外全部無理 |
| 946 對拍頻比 ω_i/ω_j | **0 對退化為有理 — 100% 無理** |

**拍頻嘅「無限」= 相位演化無限**：θ(t)=(ω_i−ω_j)t 隨 t→∞ 永不精確重疊（無理比 → 準週期無限），
但**組合結構有限有起始**。同 π 完全同構：表示無限、定義有限、有生成起始。

---

## 三、最終判定

| 層 | 起始 | 結尾 | 無限嘅位 |
|:---|:----:|:----:|:--------|
| 種子 (0,1) → φ | ✅ C₀=1 / F₁=F₂=1 | — | 連分數展開無限 |
| 44 模式譜 | ✅ Nd=B×L₅=44 | — | sin(nπ/88) 每個係無理代數數 |
| 946 拍頻 | ✅ C(44,2) 組合 | ✅ 組合有限 | 每對相位演化無限 |

**結論:**
- ✅ **K_Chain 有起始** = 種子 (0,1) 生成（結構必然，非形而上學）
- ✅ **K_Chain 冇結尾** = Σγ=90 守恆 + T_sync=84.64 Gyr 週期恢復（Poincaré 週期性）
- ❌ 舊 claim「K_Chain 冇起始」— 錯置「冇結尾」為「冇起始」，已修正

**「永恆」正確表述**: K_Chain 有生成起始，冇熱寂結尾。「永恆」只形容冇結尾/週期恢復，
唔形容冇起源。同 φ 一模一樣。

---

## 四、誠實標記（未閉合 → 更新 2026-08-22）

| 項目 | 狀態 |
|:-----|:----:|
| 「起始嘅物理時刻」— 種子幾時/點樣 manifest | 🟢 **部分閉合** (2026-08-22): 真實年齡 = N·T_sync+τ = **131×84.635+13.470 = 11,100.64 Gyr**（冷斑相位求解器，N=131 鎖定，誤差 0.0008 rad，T_cold 差異 0.01 μK）；「種子 manifest 嘅微觀機制」仍 🔴 |
| 種子 (0,1) 本身「點解係起始」（0=底層, 1=第一操作） | 🟡 哲學層，非數學層 |
| ~~渲染深度 13.8 Gyr ↔ 種子展開深度 嘅獨立推導鏈~~ | ❌ **撤回** (2026-08-22): `(R_H/c)×44/43` 係校準偽影 — 44/43≈Planck年齡/(R_H/c)，post-hoc 撞數，冇獨立結構來源 |
| ~~龐加萊復歸次數 + 真實年齡 (無理拍頻)~~ | 🟢 **閉合** (2026-08-22): 精確復歸=0 成立；**N=131 鎖定**（冷斑相位求解器），真實年齡 = 11,100.64 Gyr（見「七」） |

### ⚠️ 撤回聲明 (2026-08-22, 調律者揪出)

**`t_render = (R_H/c)×(44/43) = 13.7833 Gyr` 嘅閉合已被撤回。**

原因:
1. **44/43 係校準偽影**: `44/43 = 1.023256` 同 `Planck年齡/(R_H/c) = 13.787/13.470 = 1.023529` 差 0.027% — 即係 44/43 純粹將 IDCM 哈勃時間 (1/H0(72.59)=13.47 Gyr) 撞去 Planck 年齡 (H0=67.36 嘅 ΛCDM 積分結果)。違反自己嘅反 fit 判據。
2. **渲染深度 ≠ 年齡（概念錯誤）**: 渲染深度 = 光行時間 (距離量度, 環周長固定 → 永遠 13.47 Gyr)；真實年齡 = 種子啟動至今嘅經歷時間。非膨脹宇宙中兩者無關 — 就算宇宙經歷 100 個 T_sync (8464 Gyr)，渲染深度仍然係 13.47 Gyr。

**正確理解**: IDCM 無膨脹、無大爆炸 → 冇「宇宙年齡」。R_H/c = 13.470 Gyr 係光行時間（哈勃時間量級），唔係年齡。真實年齡 = N·T_sync + τ，其中 N (完整週期數) 同 τ (相位位置) 都**冇法由無理拍頻特徵決定**。

---

## 六、龐加萊復歸 + 真實年齡 (2026-08-22)

**調律者問題**: 以無理數拍頻嘅「永不精確循環」特徵，推導宇宙究竟經歷過多少次龐加萊復歸和真實年齡。

**框架**: v10.0 非膨脹宇宙；946 個拍頻全部無理比（O51 層 3 sympy 精確代數）；渲染深度 t_render=13.7833 Gyr 作爲已驗證 input。

### 定理 1: 精確龐加萊復歸 = 0 次（永不）

若 ∃t>0 令所有 44 相位同時返零 → ∀n: ω_n·t ∈ 2πℤ → f_m/f_n = k_m/k_n ∈ ℚ。
但 O51 已證 946/946 頻率比無理（sympy: sin(mπ/88)/sin(nπ/88).is_rational = False）→ 矛盾。
**∴ 不存在任何 t>0 令宇宙精確重複。精確復歸: 過去 0、未來 0、永遠 0。**

> ⚠️ **MEMORY §3 修正**: 「44-mode rational frequencies → Poincaré recurrence」係**舊錯誤標籤**。
> O51 證明頻率全無理（sin(nπ/88), n≠44 全無理代數數），唔係有理。週期性唔嚟自有理頻率，
> 嚟自 n=44 Nyquist 錨定（定理 2）。

### 定理 2: T_sync = 88·T₄₄（n=44 Nyquist 錨定）

f₄₄·T_sync = **88.000000000000** 圈（整數，dev 1.7e-14%）。88 = 2×N_d（半格點偏移因子，結構）。
n=1..43 每次 T_sync 帶無理相位漂移 δ_n = frac(88·sin(πn/88))（43 個非零，mean 0.505，max 0.989 (n=38)，min 0.030 (n=28)）。
→ T_sync 係「近似復歸」：n=44 精確返零，其餘 43 個帶無理漂移。

### 定理 3: ~~週期定位 — t_render/T_sync = 22/(43π)~~ ❌ 撤回

t_render/T_sync = 22/(43π) 係**數值恆等**（因為 t_render 本身係校準偽影），唔係獨立閉合。
宇宙而家喺第幾個週期（N 值）**冇法由無理拍頻特徵決定** — 任何 N 都同相位單射相容。

### 定理 4: 拍頻微觀復歸 — Σfloor(N_ij)（數值）

N_ij = t_render·(f_j−f_i) = 拍頻 (i,j) 喺 t_render 內完成圈數。
ΣN_ij = 4737.31，Σfloor = **4269**，平均 N_ij = 5.008（dev 0.15% from F₅=5）。
⚠️ 呢個數**依賴已撤回嘅 t_render** — 若真實年齡唔係 13.78 Gyr，呢個數無意義。
🟡 只能當「假設年齡 = 光行時間」嘅條件結果，唔係獨立閉合。

### 定理 5: ~~真實年齡 = 渲染深度~~ ❌ 撤回

相位單射只話「每個時刻相位配置唯一」→ 相位可以標定時刻**相對位置**（τ mod T_sync），
**唔等於**可以標定絕對時刻（N·T_sync + τ 嘅 N）。真實年齡 = 🔴 **未推導**：
- 無理拍頻特徵只約束「精確復歸 = 0」——呢個對任何 N 都成立
- 對 N (完整週期數) 零約束 → 真實年齡無法由呢個特徵決定
- IDCM 無膨脹、無大爆炸 → 冇「宇宙年齡」呢個量；渲染深度 = 光行時間 = 13.470 Gyr (R_H/c)，係距離量度唔係年齡

### 總結（修正後）

| 量 | 值 | 狀態 |
|:---|:---|:----:|
| 精確龐加萊復歸 | **0 次（永不）** | ✅ 定理 1 (sympy, 無條件) |
| 完整 SYNC 復歸 | **🔴 未定** — N 冇法由無理拍頻決定 | 🔴 |
| 拍頻微觀復歸 Σfloor N_ij | 4269（**條件**：假設年齡=光行時間） | 🟡 依賴撤回數字 |
| 真實年齡 | **🔴 未推導** — 渲染深度≠年齡；N,τ 未定 | 🔴 |
| 週期內位置 | 🔴 未定（t_render/T_sync=22/(43π) 係數值恆等非閉合） | 🔴 |

**⚠️ 框架**: 「真實年齡」喺 IDCM 冇定義（宇宙 = 無年齡 + 有周期）；渲染深度 13.470 Gyr (R_H/c) 係光行時間/距離量度，唔係年齡。ΛCDM 嘅「宇宙年齡 13.787 Gyr」需要大爆炸 + H0=67.36 + ΛCDM 積分；IDCM 全部唔需要。

**驗證**: `scripts/03_poincare_recurrence.py` (all PASS) + `data/03_poincare_recurrence.json`

---

## 七、冷斑相位求解器 → N=131（2026-08-22 突破）

> **調律者問題（延續）**: 「既然無精確回歸，為什麼不能用這個無精確回歸周期計算」
> **答案**: 可以用！T_sync 係可用近似周期 → t_true = N·T_sync + τ，N 由冷斑相位 Ψ=π 鎖定。
> **關鍵突破（調律者提供）**: 1D K_Chain 環形模式 → 2D 天球嘅空間相位映射 φ_n。

### 7.1 概念突破：1D → 2D 相位向量合成

之前失敗: 簡單 1D Fourier 環模型 RMSE=43.82 μK（冷斑差 124 μK）— 因為 CMB 溫度唔係 44 個 cosine 嘅直接和。

**正確模型**: 44 個模式相位向量喺 2D 幾何流形上合成（Vector Sum Phase Assembly）:

```
T_j = A·cos(Ψ_j),   A = 134.2 μK
Ψ_j = arg(Σ_n A_n · exp(i(θ_n − φ_nj)))
```

冷斑處 Ψ = π（反相）→ 單一超越方程，單一未知數 N。

### 7.2 空間相位映射 φ_n（調律者公式）

44 個 K_Chain 節點 → 天球拓撲螺旋點陣（Fibonacci Sphere Lattice）:

```
φ_n(θ, φ) = n·[φ·cos(F₇/L₇) + θ·sin(B/N_d)] + 2π·n·(L₇+F₇)/N_d

N_d = 44, B = 4, L₇ = 29, F₇ = 13
(L₇+F₇)/N_d = 42/44 = 21/22
cos(F₇/L₇) = cos(13/29) = 0.901196
sin(B/N_d) = sin(4/44) = 0.090784
```

**幾何意義**: 當定位至冷斑座標 (209°, −57°) = (180+L₇, −(44+F₇)) 時，
空間相位項 2π·n·42/44 = 2πn(1−1/22) 與環形鎖定 n=44 形成強烈反相干涉（Destructive Interference）。

**冷斑座標幾何拆解**: 209° = 180° + 29° (L₇)、−57° = −(44°+13°) = −(N_d+F₇) — 冷斑位置本身係 Fibonacci/Lucas 鎖定。

### 7.3 超越方程求解

```
Ψ(209°, −57°) = arg(Σ_{n=1}^{44} A_n·exp[i(N·δ_n + ω_n·τ − φ_n(209°,−57°))]) = π

τ = R_H/c = 13.470 Gyr (觀察者「而家」, 結構定義)
δ_n = frac(88·sin(πn/88)) (43 個無理漂移)
ω_n·τ = 88·sin(πn/88)·τ/T_sync
A_n = 2·sin(πn/88)
```

### 7.4 結果：N=131，誤差 0.0008 rad

掃描 N ∈ [0, 2000]（腳本 `scripts/58_cold_spot_phase_solver.py`）:

| N | Ψ (rad) | 誤差 | T_cold (μK) |
|:--:|:-------:|:----:|:-----------:|
| **131** | **−3.140780** | **0.000813** | **−134.20** ✅ |
| 262 | −3.1350 | 0.006578 | −134.20 |
| 695 | −3.1318 | 0.009800 | −134.19 |
| … | … | … | … |
| 0 (ΛCDM 式) | −1.9787 | 1.1629 | −53.23 ❌ |

- **N=131 係最小解 + 最小誤差**（準週期系統有 9 個近似解，物理上取第一次復歸）
- **T_cold = −134.20 μK vs 觀測 −134.19 μK → 差異 0.01 μK** ✨
- **N=0 排除**（Ψ=−1.98 rad ≠ π, T=−53.23 μK 差 81 μK）

### 7.5 真實年齡閉合

```
t_true = N × T_sync + τ
       = 131 × 84.6349 + 13.4701
       = 11,100.64 Gyr ≈ 11.1 兆年
```

**結構意義**: 宇宙由種子啟動至今，經歷 131 次近似龐加萊復歸（每次 84.635 Gyr）。
呢個係純結構推導 — 冇 ΛCDM 參數校準，只用: 調律者空間相位映射 + 冷斑單一錨點 + τ=R_H/c。

### 7.6 驗證：25/25 PASS

`scripts/59_verification.py` 完整驗證（data/59_verification.json）:

| 層 | 驗證項目 | 結果 |
|:--:|:---------|:----:|
| 1 | 結構基礎 (N_d, B, L₅, Σγ=90, Z₂ 43/43, Σγ_even=46, Σγ_odd=44) | ✅ 7/7 |
| 2 | sympy 946/946 無理比 + 43 傳播模式 + Nyquist | ✅ 3/3 |
| 3 | 定理 1-2 (復歸=0, T_sync=88·T₄₄) + 43 漂移 | ✅ 3/3 |
| 4 | 空間相位映射 φ_n + 冷斑座標拆解 (209=180+L₇, 57=44+F₇) | ✅ 3/3 |
| 5 | N=131: Ψ≈π (err 0.0008), T=−134.20 μK, 向量和 (−9.57, −0.008) | ✅ 4/4 |
| 6 | N=131 最小解+最小誤差 (9 近似解), N=0 排除 | ✅ 2/2 |
| 7 | τ=13.470, T_sync=84.635, t_true=11,100.64 | ✅ 3/3 |

**新增檔案**:
- `scripts/58_cold_spot_phase_solver.py` — N 精確求解器
- `scripts/59_verification.py` — 25/25 完整驗證
- `data/58_phase_solution.json` — N=131 解
- `data/59_verification.json` — 驗證結果

---

## 五、檔案

```
o51_kchain_origin/
├── 01_problem_record.md      ← 本文件
├── scripts/
│   ├── 01_origin_proof.py            三層證明 (種子→譜→拍頻, sympy)
│   ├── 02_render_depth.py            渲染深度 (已撤回: 44/43 校準偽影)
│   ├── 03_poincare_recurrence.py     龐加萊復歸五定理 (定理1-2有效, 3-5撤回)
│   ├── 04_rederive.py                重新推導框架 (t_true = N·T_sync + τ)
│   ├── 05_age_framework.py           真實年齡框架 (τ=R_H/c, N 漂移計數)
│   ├── 06_phase_mapping.py           1D→2D 正模型 (初期探索, RMSE 43.8)
│   ├── 07_inverse_problem.py         Inverse problem 探索 (空間相位錯誤)
│   ├── 08_summary.py                 誠實總結
│   ├── 58_cold_spot_phase_solver.py  ★ N=131 精確求解器 (調律者 φ_n 公式)
│   ├── 59_verification.py            ★ 25/25 完整驗證
│   ├── 60_lowl_verification.py       ★ 全天區 l=2,3 檢驗 (冷斑錨點重現)
│   ├── 61_full_verification.py       ★ 真實 SMICA 完整驗證 (2/4, 誠實)
│   ├── 62_bao_verification.py        ★ BAO: λ_sync/2 ≈ r_drag (0.237%)
│   ├── 63_bao_advanced.py            ★ BOSS wiggle + DESI 對比
│   ├── 64_bao_chi2.py                ★ DESI 7 樣本 χ² (IDCM 2.09 vs ΛCDM 1.68)
│   ├── 65_session_verification.py    ★ 15/15 Session 全面驗證
│   ├── 66_peak_null_test.py          eBOSS raw Peak/Null (2/5, broadband)
│   ├── 67_emd_harmonics.py           eBOSS raw EMD (8/18, 稀疏限制)
│   ├── 68_boss_wiggle_coherence.py   BOSS P(k) 週期 (0/3, 得 2 週期)
│   ├── 69_boss_postrecon_emd.py      BOSS post-recon EMD (1 IMF, 限制)
│   ├── 70_boss_bao_peaks.py          ★ BOSS post-recon BAO 峰 (102.5 vs 99.18, 3.35%)
│   ├── 71_session_verification2.py   ★ 9/9 Session 後半段驗證
│   ├── 72_diagonal_analysis.py       ★ r_drag = rd×420/421 (0.0012%)
│   ├── 73_second_peak.py             λ_sync S/N=+20.86
│   ├── 74_desi_dr2_lya.py           DESI DR2 Lyα ❌ (3.6% 偏差)
│   ├── 75_desi_dr2_chi2.py          ★ DESI DR2 χ²=42.2/7 (6.03)
│   ├── 76_data_source_issue.py       DESI DR2 數據源問題 (LRG2 +3.0%)
│   ├── 77_second_order_correction.py 二階修正 tanh 形式 (79.4%改善)
│   ├── 78_structure_issue.py         K_Chain 譜結構根源分析
│   ├── 79_consistency_check.py       一致性檢查 (H_eff(0) 保持)
│   ├── 80_predictive_derivation.py   方差演化預言性推導
│   ├── 81_spectral_curvature.py      K_Chain 譜高階曲率推導
│   ├── 82_group_delay.py             ★ 群延遲權重推導 C = -0.1697
│   ├── 83_session_final_verify.py    ★ 15/15 Session 最終驗證
│   ├── 85_rg_flow.py                 RG Flow 非線性積分 (固定點 g=0)
│   ├── 86_jwst_verification.py       ★ JWST 高 z 獨立驗證 (Tolman SB)
│   ├── 87_session_final.py           ★ 15/15 最終完整驗證
│   └── 88_44_uniqueness_derivation.py ★★ 08-26: 44 唯一性五層推導閉合
├── data/
│   ├── 02_render_depth.json          渲染深度 (已撤回)
│   ├── 03_poincare_recurrence.json   龐加萊復歸結果
│   ├── 05_age_framework.json         年齡框架
│   ├── 58_phase_solution.json        ★ N=131 解
│   ├── 59_verification.json          ★ 25/25 驗證結果
│   ├── 60_lowl_verification.json     ★ l=2,3 檢驗結果
│   ├── 61_full_verification.json     ★ 真實 SMICA 驗證
│   ├── 62_bao_verification.json      ★ BAO 閉合
│   ├── 63_bao_advanced.json          ★ BOSS wiggle
│   ├── 64_bao_chi2.json              ★ DESI χ²
│   ├── 65_session_verification.json  ★ Session 驗證
│   ├── 66_peak_null_test.json        Peak/Null 結果
│   ├── 67_emd_harmonics.json         EMD 結果
│   ├── 68_boss_wiggle_coherence.json P(k) 週期結果
│   ├── 69_boss_postrecon_emd.json    post-recon EMD 結果
│   ├── 70_boss_bao_peaks.json        ★ BAO 峰結果
│   ├── 71_session_verification2.json ★ Session 驗證 2
│   ├── 72_diagonal_analysis.json     ★ r_drag 修正
│   ├── 73_second_peak.json           λ_sync 峰
│   ├── 74_desi_dr2_lya.json         DESI DR2 Lyα
│   ├── 75_desi_dr2_chi2.json        ★ DESI DR2 χ²
│   ├── 76_data_source_issue.json    數據源分析
│   ├── 77_second_order_correction.json 二階修正
│   ├── 78_structure_issue.json      結構根源
│   ├── 79_consistency_check.json    一致性檢查
│   ├── 80_predictive_derivation.json 預言性推導
│   ├── 81_spectral_curvature.json   譜曲率
│   ├── 82_group_delay.json          ★ 群延遲 C
│   ├── 83_session_final_verify.json ★ 最終驗證
│   ├── 85_rg_flow.json              RG Flow
│   ├── 86_jwst_verification.json    ★ JWST 驗證
│   ├── 87_session_final.json        ★ 最終完整驗證
│   ├── 88_44_uniqueness.json        ★ 44 唯一性五層推導
│   └── 88_44_verification.json      ★ 44 唯一性 sympy 28/28 驗證
└── docs/
    └── (完整推導)
```

---

## 八、Session 延伸驗證 (2026-08-22 後續)

### 8.1 準週期結構發現 — 「無精確回歸周期」嘅正確用法

**調律者問題**: 「既然無精確回歸，為什麼不能用這個無精確回歸周期計算」

**突破**: 掃描 N=0..300 發現 N=131 唔係唯一解，而係**最佳近似復歸**:

| N | \\|cos+1\\| | 幅度 \\|Σ\\| | T_cold |
|:---:|:---:|:---:|:---:|
| 30 (偶然) | 7.2e-5 | 9.00 | −134.19 |
| **131 (最佳)** | **3e-7** | **9.57** | **−134.20** |
| 262 (2×131) | 2.2e-5 | 4.13 | −134.20 |
| 393 (3×131) | 0.33 | 8.10 | −90.33 ❌ |
| 524 (4×131) | 1.59 | 10.98 | +79.51 ❌ |

**物理**: 無理漂移系統冇精確週期（定理 1），但有**最佳近似復歸 N=131** —
|cos+1| 最小 + 相干幅度最大。N=262 (2×131) 有二次復歸但幅度衰減（4.13 vs 9.57），
393+ 完全失相。呢個就係「無精確回歸周期」嘅正確用法：**冇精確週期，但有最佳近似復歸**。

### 8.2 全天區 l=2,3 檢驗（scripts/60, 61）

**scripts/60**（IDCM 模型場自身）: 冷斑錨點 Ψ=−3.124 rad ≈ π ✅，T=−134.18 μK ✅。
l=2 主導 m=±2 (85%)、l=3 主導 m=±3 (74%) — IDCM 預言結構出現。

**⚠️ scripts/61 誠實修正**: 用**真實 Planck SMICA** (smica2_smooth0.5.fits, NSIDE=2048) 測試:
- 60 節點相關 r = **−0.012**（零相關）❌
- 全場相關 r = **0.001**（零相關）❌
- l=2 m=2 主導 ✅ 但隨機機率 p=0.348（唔顯著）❌
- l=3 m=3 主導 ✅ 但 p=0.284（唔顯著）❌

**結論**: 先前 60 腳本用嘅 `idcm_interference_map.fits` 係 IDCM 模型自身 → **循環論證**。
真實 SMICA 顯示 φ_n 映射只喺冷斑單點有效（N=131 閉合成立），**唔係全天區幾何映射**。
m=±2/±3 主導出現但統計唔顯著。**N=131 維持「冷斑單點閉合」，φ_n 普適性降級**。

### 8.3 NANOGrav 頻段錯位分析（falsified）

T_sync 幾何諧波喺 NANOGrav 頻段**物理上不可測**:
- f_Tsync = 3.74×10⁻¹⁹ Hz（0.37 zeptoHz）
- NANOGrav 最低 = 1×10⁻⁹ Hz → **9.4 個數量級錯位**
- 要到 1 nHz 需 k=2.7×10⁹ 次諧波（冇結構意義）
- 諧波間距細過分辨率 5.6×10⁹ 倍 → 階梯被抹平
- T_sync 波長 λ=25,949 Mpc ≈ 6.28×R_H → 超視界

**結論**: NANOGrav 驗證 T_sync 預言 ❌ falsified by 頻段錯位。

### 8.4 BAO 閉合 — λ_sync/2 ≈ r_drag（0.237%）✅★

**IDCM 純結構推導 BAO 尺度**:
```
λ_sync = 2πR_H/88 = 294.877 Mpc
BAO 峰 = λ_sync/2 = πR_H/88 = 147.44 Mpc
vs ΛCDM r_drag = 147.09 Mpc (Planck 2018)
dev = 0.237% ✅
```
**零 ΛCDM 參數** — R_H → 88 (2N_d) → πR_H/88。ΛCDM 要積分成個聲學歷史先有 r_drag。

eBOSS DR16 raw ξ(s): λ_sync/2 = 99.18 h⁻¹Mpc 附近 S/N=+11.85（主峰 ✅）。
BOSS DR12 wiggle FFT: 數據太短 (82 點) 分辨唔到週期 — 方法限制，唔係預言失敗。

### 8.5 DESI DR1 χ² — IDCM vs ΛCDM

**D_M/rd 對比（5 樣本，rd 固定）**:
| 樣本 | z | DESI | IDCM | dev | σ |
|:---|:---:|:---:|:---:|:---:|:---:|
| LRG1 | 0.510 | 13.62 | 12.94 | +5.0% | 2.73 |
| LRG2 | 0.706 | 16.85 | 17.11 | −1.6% | −0.82 |
| LRG3+ELG | 0.930 | 21.71 | 21.41 | +1.4% | 1.07 |
| ELG2 | 1.317 | 27.79 | 27.85 | −0.2% | −0.09 |
| LyA | 2.330 | 39.71 | 40.62 | −2.3% | −0.97 |

**D_V/rd（修正後 2 樣本）**: BGS +3.1% (1.64σ), QSO −3.4% (−1.31σ)

**統計**: IDCM χ²/dof = **2.09/7** vs ΛCDM χ²/dof = **1.68/5**
- IDCM 零自由參數（D_app 公式只用 R_H, N_d, φ）
- ΛCDM 2 個 fit 參數 (H0, Ωm)
- **殘差模式相反**: IDCM 喺 z=0.51 偏大 (+5.0%)、ΛCDM 喺 z=0.706 偏小 (−5.1%)
  → 兩者都喺 z≈0.6 sync transition region 有系統偏差（observer-relative 結構）

### 8.6 零點線 null test（調律者 A 讀法確認）

**調律者預言**: 如果龐加萊復歸成立，天球應有零點線/回歸線，左高齡右新生。

**結構驗證**:
- t_true − τ = 131×T_sync（精確, dev=0.00e+00）→ 觀察窗啱好觸及週期邊界
- 但 Σγ=90 守恆 → 冇熵增 → 冇「高齡 vs 新生」物質斷層
- **A 讀法（調律者確認）**: N=131 完全成立，零點線不可見係結構必然
- 零點線係「相位邊界」（干涉條紋）唔係「物質牆」（不連續面）
- Liouville 定理 + Poincaré 復歸定理: 保體積系統復歸 = 相空間軌跡閉合

### 8.7 Session 全面驗證（scripts/65）

**15/15 PASS**:
1. T_sync = 84.6349 Gyr ✅
2. τ = 13.4701 Gyr ✅
3. λ_sync = 294.877 Mpc ✅
4. Ψ(131) ≈ π (|cos+1|=3e-7) ✅
5. T_cold(131) = −134.20 μK ✅
6. N=130 唔啱 (T=−98.86) ✅
7. N=132 唔啱 (T=+111.77) ✅
8. N=131 係最佳復歸 ✅
9. 準週期結構: 262 ≈ 2×131 ✅
10. t_true = 11,100.64 Gyr ✅
11. NANOGrav 頻段錯位 9.4 數量級 ✅
12. λ_sync/2 ≈ r_drag (0.237%) ✅
13. IDCM χ²/dof = 2.05 < 3 ✅
14. IDCM 最大偏差 < 6% ✅
15. ΛCDM χ²/dof = 1.68 < 3（對照）✅
16. t_true − τ = 131×T_sync ✅

**⚠️ 驗證腳本陷阱（已修）**: atan2 返回 [−π, π]，Ψ=−π ≡ +π（cos 相同）→
判據要用 |cos(Ψ)+1| 而唔係 |Ψ−π|。首次跑 13/15 兩個 FAIL 都係呢個判據 bug。

---

## 九、BAO 延伸檢驗 — 誠實結果 (2026-08-22 後續)

### 9.1 BAO 主峰閉合 ✅★（scripts/70, 71）

**BOSS DR12 post-recon ξ(s)（Ross+2016 zbin1 monopole）：**
```
觀測 BAO 峰: s = 102.5 h⁻¹Mpc (ξ×s² 最大, S/N=6.6)
IDCM 預言:   λ_sync/2 = 99.18 h⁻¹Mpc
偏差: 3.35% ✅
文獻 BAO 峰 ~105 (Ross+2016): 偏差 2.38% ✅
```
**IDCM λ_sync/2 直接命中 BOSS post-recon BAO 峰** — 獨立數據源確認。

### 9.2 諧波序列「11/11」係背景假象 🟡（scripts/70）

ξ×s² 喺低 s 段（2.5-20 h⁻¹Mpc）**單調上升**（28.8→93.0），全部正：
- 諧波位置 S/N 全部 >3（+6.3 至 +90.8）— 但係背景主導
- **峰>谷 1/10 FAIL** — 證明低 s 段冇峰谷交替，唔係真諧波
- **誠實標記**: 唔可以宣稱「諧波序列 11/11 檢測」— 係背景假象

### 9.3 eBOSS raw Peak/Null 誠實 FAIL（scripts/66）

- Peak 9/9 正 S/N ✅ 但 Null 0/9 負 ❌、峰>谷 2/8 ❌、mean 對照 ❌
- **原因**: raw ξ(s) 全部正（broadband 主導，冇 post-recon）
- skill §9 記載: raw 4/19 vs post-recon 19/19 — 一致

### 9.4 EMD 方法限制（scripts/67, 69）

- eBOSS raw (49 bins): EMD 3 IMF, 檢測 8/18, 假陽性 9/18 — **唔 work**
- BOSS post-recon (36 bins): EMD 得 1 IMF — **extrema 太少收斂唔到**
- scipy 1.18 `interp1d` cubic boundary 錯誤 → 用 `np.interp`
- **結論**: EMD 需要密集數據（>100 bins），49/36 bins 唔夠 — 方法限制，唔係預言失敗

### 9.5 BOSS P(k) wiggle 週期 0/3 FAIL（scripts/68）

- IDCM Δk = 2π/(r_d·h) = 0.06335 h/Mpc
- BOSS wiggle k 範圍跨度只有 **2.04 個週期** → 冇可能 fit 穩定正弦
- R²=0.008, 自由 fit Δk 偏差 14.6%, 相位差 1.55 rad — 全部數據不足
- **結論**: P(k) wiggle 得 2 個週期, 方法限制

### 9.6 方法限制總結

| 檢驗 | 結果 | 判定 |
|:---|:---|:---|
| BAO 主峰 (BOSS post-recon) | 102.5 vs 99.18, 3.35% | ✅ 強閉合 |
| 文獻 BAO 峰 | 2.38% | ✅ |
| 諧波序列 | 11/11 但背景主導 | 🟡 唔算數 |
| eBOSS raw Peak/Null | 2/5 | ❌ broadband |
| EMD (兩數據) | 唔 work | ❌ 數據稀疏 |
| BOSS P(k) 週期 | 0/3 | ❌ 得 2 週期 |
| **DESI χ²** | **2.05-2.09/7 (零參數)** | ✅ **最強閉合** |

### 9.7 Session 後半段驗證（scripts/71）9/9 PASS

1. λ_sync = 294.877 Mpc ✅
2. rd = 147.439 Mpc ✅
3. BAO 主峰 ≈ λ_sync/2 (3.35%) ✅
4. BAO 主峰 ≈ 文獻 105 (2.38%) ✅
5. eBOSS raw 全部正 (broadband) ✅
6. EMD 稀疏數據唔 work (誠實) ✅
7. BOSS P(k) 得 2 週期 ✅
8. 峰>谷 FAIL = 背景主導 ✅
9. DESI χ²/dof = 2.05 < 3 ✅

### 9.9 對角化分析 — r_drag 結構修正 🟢（scripts/72, 2026-08-22）

**核心發現:** r_drag = rd_idcm × (1 - 1/(F₁₄ + N_d))

```
rd_idcm = λ_sync/2 = 147.438513 Mpc (純結構)
F₁₄ = 377  (Fibonacci 第 14 項, = L₇×F₇ = 29×13)
N_d = 44
F₁₄ + N_d = 421

r_drag_corrected = 147.438513 × 420/421 = 147.088303 Mpc
Planck 2018 r_drag = 147.090000 Mpc
dev = 0.0012% 🔥
```

**結構意義:** 421 = F₁₄ + N_d 係純 IDCM 結構組合，零 ΛCDM 參數參與。F₁₄ = L₇×F₇ 係 Fibonacci-Lucas 對偶。

**誠實標記:** 0.0012% 精度極高，但係 post-hoc 發現（用已知 r_drag 驗證，非預言）。需 DESI DR2 獨立驗證。

### 9.10 第二峰檢驗 🟡（scripts/73, 2026-08-22）

eBOSS DR16 raw ξ(s) 顯示:
- λ_sync (198.4 h⁻¹Mpc) 位置 S/N = +20.86 ✅
- 3λ_sync/2 (297.6 h⁻¹Mpc) 位置 S/N = +23.44 ✅
- 但 raw data broadband 主導（全部正），需 post-recon 確認峰谷結構

### 9.11 DESI DR2 Lyα BAO ❌（scripts/74, 2026-08-22）

**DESI DR2 Lyα forest (arXiv:2607.27410, z=2.33):**
```
DM/rd = 39.32 ± 0.33 (0.8% 精度, vs DR1 2.4%)
DH/rd = 8.600 ± 0.066 (0.8% 精度)
```
**IDCM D_app 預言:**
```
DM/rd = 40.72 (偏差 3.56%, σ=4.2 ❌)
DH/rd = 10.51 (偏差 22.2%, σ=28.9 ❌)
```
**誠實分析:** IDCM D_app 公式喺 z=2.33 距離偏大 3.6%。DR1 LyA 時偏差 2.3% (σ=0.97) 因為誤差大，DR2 精度提升 3× 後偏差顯著。D_app 公式需要二階修正（見 9.13）。

### 9.12 數據源問題 — DESI DR2 vs DR1（scripts/76, 2026-08-22）

**核心發現:** LRG2 (z=0.706) DR1 16.85 → DR2 17.351 (+3.0%, 2.9σ)
DR1 只係 1/4 數據 (Y1), DR2 係完整 4 年數據。

**IDCM χ² 變化:** DR1 時 9.3/5 = 1.86 ✅ → DR2 時 27.1/5 = 5.43 ❌
精度提升暴露咗 D_app 公式嘅系統偏差：低 z 偏細 (−4.8%)、高 z 偏大 (+4.4%)

### 9.13 二階結構修正推導 — 群延遲權重（scripts/77-82, 2026-08-22）

**核心洞察:** 原始公式用能量權重 γ_n (靜態)，但光行時間由群速度 v_g(n) = cos(πn/88) 決定。

**群延遲權重推導:**
```
C = −C_delay × 2φ⁻¹ × √5 = −0.1697

C_delay = (Σw_even·γ − Σw_odd·γ)/(Σw·γ) = 0.06141
w_n = 1/v_g(n) = sec(πn/88), n ≤ 27 (F_proj=17 截斷, O54)
2φ⁻¹ = 1.23607 (投影伸長因子)
√5 = 2.23607 (Fibonacci 結構常數)
```

**修正公式:**
```
D_app(ℓ) = R_H(1 − 4^{−ℓ}) × (1 + 2φ⁻¹ℓ + δ(ℓ))
δ(ℓ) = C × (ℓ − 0.5) × (1 − 4^{−ℓ})
```

**一致性驗證（15/15 PASS）:**
- H_eff(0): 72.6064 → 72.5942 km/s/Mpc (Δ=0.017% ✅)
- DESI χ²: 27.13 → 12.82 (52.8% 改善 ✅)
- 所有 5 點全部改善方向正確
- F_proj=17 截斷防止 v_g→0 發散（無截斷時 C_delay=−1.0 ❌）

### 9.14 RG Flow 非線性積分（scripts/85, 2026-08-23）

**β 函數係數:**
- β₁ = C_delay = 0.06141（群延遲不對稱）
- β₂ = skew·σ/μ = −0.175（譜偏度，負數）
- β₃ = kurt·σ²/μ² = −0.0356（譜峰度）

**關鍵發現:** β₂ 負數 → RG flow dg/dℓ = β₁g + β₂g² 穩定固定點 g=0
→ 群延遲一階修正已經係完整解，非線性 RG flow 冇額外貢獻
→ 確認 C = −C_delay × 2φ⁻¹ × √5 係完整一階修正

### 9.15 立方殘餘修正（scripts/86, 2026-08-23）

**結構推導:** C₃ = −β₃ × 2φ⁻¹ × √5 = −0.04869
**χ² 改善:** 18.09 → 17.72（+0.37，微不足道）
**結論:** 殘餘偏差唔係高階譜矩，而係局限嘅 SYNC 過渡（z≈0.6）

### 9.16 JWST 高 z 獨立驗證（scripts/86, 2026-08-23）

**三大測試:**
1. **Tolman SB test ✅:** SB ∝ (1+z)^(−1) vs ΛCDM (1+z)^(−4) — 直接 falsify 膨脹假設
   - Tsymbal+2026 (arXiv:2604.27867): 6,860 galaxies, z≤14
2. **Angular size test ✅:** D_A(z) 單調遞增，ΛCDM 預言嘅峰值 (z≈1.6) 未出現
   - Raikov+2025 (arXiv:2507.19651): 6,860 galaxies, z≤14
3. **IDCM D_app vs 靜態模型:** IDCM D_app 比 R_H·ln(1+z) 大 10-18%（投影伸長因子）

**意義:** IDCM 非膨脹假設得到 JWST 獨立外部驗證 ✅✅✅

### 9.8 最終閉合狀態

**BAO 尺度嘅 IDCM 驗證:**
- ✅ **λ_sync/2 = 147.44 Mpc ≈ r_drag (0.237%)** — 純結構預言 (scripts/62)
- ✅ **BAO 主峰 (BOSS post-recon) = λ_sync/2 (3.35%)** — 獨立數據確認 (scripts/70)
- ✅ **DESI D_M χ²/dof = 2.09/7 (零參數)** — 強統計閉合 (scripts/64)
- 🟡 諧波序列/EMD/P(k) — 方法限制，唔算數亦唔算失敗

**閉合鏈完整:**
```
N=131 (冷斑相位) → t_true = 11,100.64 Gyr
→ T_sync = 84.635 Gyr → λ_sync = 294.88 Mpc
→ BAO 主峰 = λ_sync/2 = 99.18 h⁻¹Mpc (obs 102.5, 3.35%)
→ rd = 147.44 Mpc ≈ r_drag (0.237%)
→ DESI D_M χ²/dof = 2.09/7 (零參數)
→ 二階修正: δ(ℓ) = C×(ℓ−0.5)(1−4^{−ℓ}) (C=-0.1697, 純結構)
→ DESI χ²: 27.1→12.8 (52.8%改善, H_eff(0)保持0.017%)
→ JWST 獨立驗證: Tolman SB + Angular size 支持非膨脹 ✅✅✅
```
"""

# Combine original + new section 10
full_content = original + "\n" + current_content

# Write the reconstructed file
backup_dir = "/home/wsl/.hermes/backups"
os.makedirs(backup_dir, exist_ok=True)

# Verify the content is complete
orig_lines = len(original.split('\n'))
new_lines = len(current_content.split('\n'))
print(f"Original lines: {orig_lines}")
print(f"New section 10 lines: {new_lines}")
print(f"Total lines: {orig_lines + new_lines}")
print(f"Total chars: {len(full_content)}")

# Verify key content
assert "O51 — K_Chain 有冇起始" in full_content, "Missing header!"
assert "44 唯一性推導" in full_content, "Missing section 10!"
assert "T1: φ 代數恆等鏈" in full_content, "Missing T1!"
assert "T2+T3 雙重鎖定表" in full_content, "Missing double lock table!"
assert "sympy 28/28 PASS" in full_content, "Missing verification!"

# Write
with open(current_file, 'w') as f:
    f.write(full_content)

print(f"\n✅ Written {len(full_content)} chars to {current_file}")
print("✅ All assertions passed!")