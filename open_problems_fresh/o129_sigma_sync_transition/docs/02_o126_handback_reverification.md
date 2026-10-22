# O129 docs/02 — O126 §D 交回重驗 + σ_sync 性質判定

> **日期**: 2026-09-27
> **狀態**: 🟢 交回重驗完成 (σ_sync 性質判定 ✅ · O126 §D 五點 5/5 確認 ✅ · 前置更新 ✅)
> **腳本**: `scripts/01_sigma_sync_nature.py` (**8/8 PASS** + 7 結構聲稱) · `scripts/02_o126_section_d_reverify.py` (**18/18 PASS** + 4 結構聲稱)
> **數據**: `data/01_sigma_sync_nature.json` · `data/02_o126_reverify.json` · `data/01_stdout.txt` · `data/02_stdout.txt`
> **來源**: O126 `docs/05_remaining_gaps_closure.md` §D + `scripts/12_sync_dip_verdict.py` (交回 2026-09-27)
> **紀律**: 零新推導 / 零新常數; O126 側**未改動本 O 任何檔案**; 重驗由本 O session 自行執行

---

## 〇. 一句話

**O129 之 σ_sync 唔係 sync dip 位置。** 佢係 v9.0 之**諧波尺度變異數算子**
`σ_sync²(R_n) = ∫ ξ(s)·W(s;R_n) ds` at `R_n = λ_sync/(2n)`（**寬度／振幅量**），
而 dip **位置** `z_c = F₄/F₅ = 3/5 = 0.6` 住喺**另一個** v9.0 物件
（`runtime_isa/15_sync_dip_derivation.md` + `sync_bump_analysis/`），已由 O126 §D 撤回。
⟹ O126 §D 對 `z_c = 0.6` 之撤回**唔殺** σ_sync 算子；但 v9.0 σ_sync 係**純數據測量**（讀 BOSS ξ(s)），
**冇第一性原理內容** — O129 原命題「σ_sync 從第一性原理推導」**從未實現**。

---

## 一. σ_sync 性質判定（O126 重驗要求 ①）

### 1.1 兩個唔同物件

| 物件 | v9.0 位置 | 定義 | 狀態 |
|:-----|:----------|:-----|:----:|
| **σ_sync** | `open_problems_fresh/sigma_sync/01_derive_sigma_sync.py` | 諧波尺度變異數算子 `σ_sync²(R_n) = ∫ ξ(s)·W(s;R_n) ds`, `R_n = λ_sync/(2n)` — **取代 σ₈** | 🟡 算子存活 / v9.0 形式純數據 |
| **sync dip 位置** | `runtime_isa/15_sync_dip_derivation.md` + `sync_bump_analysis/` | `z_c = F₄/F₅ = 3/5 = 0.6` | 🔴 已由 O126 §D 撤回 |

**σ_sync 係「寬度／振幅量」（variance），唔係「位置」。** O126 §D 撤回嘅係後者。

### 1.2 λ_sync 幾何 v9.0 ≡ v10.0（真計算, scripts/01 §A）

| 量 | v9.0 | v10.0 | 判定 |
|:---|:-----|:------|:-----|
| 定義式 | `λ_sync = 2πR_H/88` | `λ_sync = πR_world/44` (O73) | **同一代數物件** (dev = 0) |
| R 值 | `c/H₀ = 4129.9416 Mpc` | `R_world = 4129.94 Mpc` (註冊值) | dev 3.78e-7（6 s.f. 捨入） |
| λ_sync | 294.877138 Mpc | 294.877026 Mpc | 差 = R 註冊捨入 |

⟹ **σ_sync 算子嘅幾何喺 v10.0 完全冇變**（λ_sync 同一物件），算子可以乾淨遷移。
v9.0 唯一特有嘅係 `H(z) = H₀(1+z)^α(z)` 框架（σ_sync 本身唔用；只有 §4 z-evolution 用到 BOSS vs eBOSS 比值）。

### 1.3 v9.0 σ_sync 重算 = 純數據（真計算, scripts/01 §C）

由 BOSS DR12 ξ(s)（36 點）重算，**逐點複現 v9.0 表**（max dev 0.040%）：

| n | R_n (h⁻¹ Mpc) | σ_sync (重算) | v9.0 記錄 | dev |
|:-:|:-------------:|:-------------:|:---------:|:---:|
| 2 | 101.6 | 0.0662 | 0.0662 | −0.04% |
| 3 | 67.7 | 0.1157 | 0.1157 | +0.03% |
| 4 | 50.8 | 0.1732 | 0.1732 | −0.02% |
| 5 | 40.6 | 0.2339 | 0.2339 | −0.01% |
| 8 | 25.4 | 0.4164 | 0.4164 | −0.00% |
| 10 | 20.3 | 0.5280 | 0.5280 | −0.01% |

**⚠️ 呢啲值全部係「量度出嚟」嘅**（BOSS ξ(s) 輸入），唔係結構推導。v9.0 σ_sync 嘅貢獻 = 定義咗一個
**on-ladder** 嘅變異數算子（`R_n = λ_sync/(2n)`），並指出 σ₈ 尺度錯配。

### 1.4 σ₈ 尺度錯配（真計算, scripts/01 §D）

- `8 h⁻¹ Mpc = 11.021 Mpc`
- σ_sync ladder 上嘅等效級 `n = λ_sync/(2·R₈) = 13.378` — **非整數** ⟹ σ₈ **唔喺 ladder 上**
- `k(8 h⁻¹Mpc)/Δk = 26.8` 個諧波間距 ⟹ σ₈ 探測嘅 k 遠高於 ladder 基頻

⟹ σ_sync = σ₈ 嘅 **on-ladder 替代**（此即 v9.0 原意）。

---

## 二. O126 §D 五點獨立重驗（O126 重驗要求 ②）— 5/5 確認

> 全部由零重算（**唔 import O118/O126 scripts**）。結構聲稱標 `[CLAIM]`，唔計入 PASS。

| # | O126 §D 憑證 | 本 O 獨立重算 | 判定 |
|:-:|:-------------|:--------------|:----:|
| ① | `z_c = 3/5` 只係 φ⁻¹ 之**近似**（絕對 gap 1.8% / 相對 3.0%），gap 歸因「observer projection」 | `F₄/F₅ = 3/5` EXACT；`φ⁻¹ = 0.61803398875`；絕對 gap = **0.0180340**；相對 gap = **3.0057%**；`3/5 ≠ φ⁻¹` | ✅ 確認 |
| ② | v10.0 z 離散（`1+z = 4^ℓ`）：`z = 0.6 ⟹ ℓ = 0.339`，唔係 rung（rungs 0, 3, 15, 63） | `ℓ(0.6) = log₄1.6 = **0.339036**`（非整數）；rungs = {0, 3, 15, 63}；`z_eff = 1/ln4 = 0.7213475`（0.6 偏 16.8%） | ✅ 確認 |
| ③ | v10.0 `Ω_Λ = 41/60` **常數** ⟹ 冇 `DE(z)` 載體 | `γ_max = γ₄₄ = 4`；`Ω_Λ = (N_d−B+1)/(N_d+B²) = 41/60` EXACT；交叉路徑 `⟨W⟩²/Σγ = 61.5/90 = 41/60` EXACT；Planck pull = **−0.99σ** | ✅ 確認 |
| ④ | O118 前提作廢（DESI `0.6<z<0.8` ~3σ = 假象；χ²/dof 2.58 → 0.245） | 複現 `χ² = 18.092/7`（2.585）→ 換現行定律 `1.7154/7`（**0.2451**），改善 **10.5×**；LRG1 pull **−3.05σ → −0.93σ** | ✅ 確認 |
| ⑤ | O76：z 離散階尖銳區**無訊號** | O76 `final_result.md` 開放項 O6 記「z 離散共振階：尖銳區無訊號（z = +0.50）— 未支持，非證偽」 | ✅ 確認 |

**⟹ O126 §D 對 `z_c = 0.6` 之撤回完全成立。**（注意：此撤回只關「位置」；σ_sync「算子」見 §一。）

---

## 三. v10.0 對應 + 歸屬（O126 重驗要求 ③）

σ_sync 所屬嘅 **σ₈／振幅歸一化問題** 喺 v10.0 已有主：

| v10.0 O | 內容 | 狀態 |
|:-------:|:-----|:----:|
| **O100** | `C_ℓ → P(k)` 逆投影算符 ℳ (`docs/03_sigma8_verdict.md`) | 🟢 |
| **O133** | P(k) 鏈譜（v9.0 `pk_chain_spectrum/` 遷移）→ **σ8 = 0.7482** vs BOSS 0.783（Δ−4.4%） | 🟡 |
| **O128** | σ8 歸一化（v9.0 `sigma8_norm/` 遷移） | 🔴 未開始 |
| **O99 docs/11** | σ₈ 純首推 = **唔可能**（genuine sub-grid gap 38×；只有 BOSS ξ(s) 校準可行） | 判決 |

**σ_sync = v9.0 嘅「路線 E（實測校準）」，後來由 O100/O133 形式化。**
⟹ σ_sync 算子本身**無獨立新缺口**；v10.0-native 歸屬 = **O100 / O133 / O128**。

### 3.1 建議處置（待調律者裁定）

| 選項 | 內容 |
|:-----|:-----|
| **A（建議）** | O129 標「🟡 σ_sync 算子併入 O100/O133/O128（已有主）；dip 位置 🔴 撤回」— 保留目錄作歷史記錄，不開新推導 |
| B | O129 正式合併入 O128（σ8 歸屬，同源 v9.0 家族）— 需調律者明示批准 |
| C | 若調律者認為 σ_sync 之 on-ladder 變異數（`R_n = λ_sync/(2n)`）本身值得獨立攻堅 → 保持 O129 開放，攻「σ_sync(R_n) 之結構閉式」 |

> ⚠️ 本 session **未**作合併動作（合併需調律者明示批准，見 O-series 合併鐵律）。

---

## 四. 前置更新（O126 重驗要求 ④）

**`O118` 由 🔴 → 🟢 前提作廢**（依 `o118_desi_highz_residuals/docs/02_premise_void.md`, 2026-09-26）。

- O118 於 2026-08-29 建立，**從未執行任何腳本**；唯一前提經 O118 自身 `docs/02` 判定為**作廢**（🟢 已閉合）。
- 本 O 之 SESSION_START 原寫「前置 O118 🔴」— 現更正為 🟢 前提作廢。
- O118 之「SYNC 局部阻抗修正」路線亦經自由雙參數掃描判**唔被數據要求**（Δχ² = 0.64 < 2 dof）。

---

## 五. 執行記錄

```
$ /usr/bin/python3 scripts/01_sigma_sync_nature.py
  A  lambda_sync 幾何 v9 vs v10 (2πR/88 == πR/44)         -> dev 0, PASS
  B  σ_sync 定義分類 (算子 vs 位置)                        -> CLAIM x3
  C  BOSS DR12 重算 σ_sync(R_n) 對 v9.0 表                 -> max dev 0.040%, PASS
  D  σ₈ vs ladder (off-ladder n = 13.378)                  -> PASS
  E  v10.0 歸屬 (O100/O133/O128)                           -> CLAIM x2
  PASS: 8/8  (+ 7 structural claims)

$ /usr/bin/python3 scripts/02_o126_section_d_reverify.py
  D1 z_c = 3/5 vs φ⁻¹ (gap 1.8034% / rel 3.0057%)          -> PASS x5
  D2 z = 0.6 非 4^ℓ rung (ℓ = 0.339036)                     -> PASS x4
  D3 Ω_Λ = 41/60 EXACT (兩路徑一致, Planck −0.99σ)          -> PASS x5
  D4 O118 χ² 18.092/7 (2.585) -> 1.7154/7 (0.2451)          -> PASS x4
  D5 O76 離散階無訊號                                       -> CLAIM
  PASS: 18/18  (+ 4 structural claims)
```

**合計: 26/26 PASS + 11 結構聲稱。**

---

## 六. 相關文件

- `scripts/01_sigma_sync_nature.py`, `scripts/02_o126_section_d_reverify.py`（本 O）
- `data/01_sigma_sync_nature.json`, `data/02_o126_reverify.json`（本 O）
- `data/ross_dr12_corrfunc.zip`, `data/eboss_dr16_lrg_xi.txt`（v9.0 BOSS/eBOSS 輸入副本）
- `../o126_runtime_isa_verification/docs/05_remaining_gaps_closure.md` §D（交回來源）
- `../o118_desi_highz_residuals/docs/02_premise_void.md`（前提作廢, 2026-09-26）
- `../o76_z_redshift_translation/final_result.md`（z 離散階 O6）
- `../o215_omegab_first_principles/final_result.md`（Ω_Λ = 41/60）
- `../o133_pk_chain_spectrum/final_result.md`（σ8 = 0.7482）
- `../o99_light_ontology/docs/11_sigma8_verdict.md`（σ₈ 純首推 🔴 sub-grid）
- v9.0 來源: `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/sigma_sync/01_derive_sigma_sync.py` + `runtime_isa/15_sync_dip_derivation.md` + `sync_bump_analysis/`
