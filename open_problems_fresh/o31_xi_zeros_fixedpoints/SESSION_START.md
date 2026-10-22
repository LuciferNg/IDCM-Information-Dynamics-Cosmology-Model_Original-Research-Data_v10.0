# SESSION_START — O31 ξ(s) 零點 vs K_Chain 不動點

> 交接日期: 2026-08-17
> 來源: 當日討論 (非平凡零點 vs 非平凡不動點)
> 靈感: Kawahira (2016) — RH 等價於無吸引不動點

## 問題

IDCM 的 ξ(s) 零點 (nulls at λ_sync/(n+0.5)) 與 K_Chain/K_Tree 系統的不動點 (φ, R_H, SYNC) 之間是否存在形式化雙向等價?

## 已確認

- Kawahira (2016): RH + 零點單 ⟺ 某亞純函數無吸引不動點 ✅
- Brent (2017): ζ 變體不動點沿對數螺旋收斂, 中心是黎曼零點 ✅
- IDCM ξ(s) nulls: s_n = λ_sync/(n+0.5) ✅
- IDCM φ: golden map T(x)=1+1/x 的不動點 ✅
- IDCM R_H: K_Tree 深度 ℓ→∞ 吸引子 ✅
- SYNC: n=44 模式飽和, 宇宙熱寂逆轉 ✅

## 未做

- [ ] 方向 A: K_Chain 生成函數 G(z) — 零點=nulls, 不動點=?
- [ ] 方向 B: 黃金映射疊代與 γ_n 譜關係
- [ ] 方向 C: SYNC 轉換作爲不動點分歧
- [ ] 方向 D: Kawahira 類比 — Newton 映射 N_IDCM(s) = s − ξ(s)/ξ'(s)

## 資源

- K_Chain 波參數: `../../src/kchain_wave_params.py`
- ξ(s) 驗證: `../../kchain_cosmic_web/09_peak_null_test.py`
- 核心常數: `../../kchain_cosmic_web/_core.py`
- 色散推導: `../../kchain_cosmic_web/` 相關文件

## 判定

✅ 推導 1: F_IDCM(s) 零點 = nulls, 與 φ 不動點代數關係
✅ 推導 2: K_Chain 疊代映射不動點 ↔ ξ(s) 零點 (雙向)
✅ 推導 3: SYNC = 不動點分歧, 給出分歧條件
🟢 部分推導
🔴 無結果

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `scripts/13_desi_jwst_verification.py:98` — D_app(ℓ) = (44-44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。

---

## ⚠️ O131 跟進項 (2026-09-27) — 數據腳本路徑失效 (待本 O 自行處理)

> **來源**: O131 (`o131_stacking_analysis/`), 前置驗證輪 `scripts/03_cross_o_coverage.py` (24/24 PASS)
> **狀態**: 🔴 未處理
> **背景**: O131 = v9.0 `stacking_toolbox/01_stacked_waveform.py` → v10.0 遷移判決。
> 判決發現 O131 之 v9.0 物件全部已有 v10.0 現行擁有者，其中 **②諧波階梯 λ_sync/n 與 ③ξ(s) 零點
> λ_sync/(n+0.5) 嘅擁有者正正係本 O (O31, 🟢 已閉合)**。

### 事項

| # | 事項 | 詳情 | 建議動作 |
|:-:|:-----|:-----|:---------|
| 1 | **數據腳本不可重跑** | 本 O `scripts/07_boss_dr12_empirical{,_v2}.py` · `08_emd_empirical.py` · `09_pk_wiggle_source.py` · `11_bao_geometric_protection.py` 全部硬編碼 `os.path.expanduser('~/IDCM/sync_bump_analysis/...')`，而 `/home/wsl/IDCM` **已不存在** ⟹ 5 個腳本會 `FileNotFoundError`（data 輸出仍在，但唔可重現） | 將原始數據複製入本 O `data/` + 改用 `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` 相對路徑，然後逐個重跑 |
| 2 | 所需數據檔 | `ross_dr12_corrfunc.zip` · `eboss_dr16_lrg_xi.txt` · `boss_dr12_bao_wiggles.txt`（v9.0 `sync_bump_analysis/` 仍有副本；`boss_dr12_bao_wiggles.txt` 亦已在 `o133_pk_chain_spectrum/data/`） | 複製入本 O `data/` |
| 3 | 參考做法 | O129 (`o129_sigma_sync_transition/data/`) 與 O131 (`o131_stacking_analysis/data/`) 已示範同型修法 | — |

### 驗證標準
`scripts/07/08/09/11` 由本 O 目錄 root 跑（`python3 scripts/NN.py`）全部 exit 0，且輸出同既有 `data/*_results.txt` 一致。

### ★ 補充 (同日第二輪, 2026-09-27) — λ_sync「÷h」換算 + 折疊檢定（含 O31 自己嘅 406.1）

> **來源**: O131 `scripts/04_ladder_fold_test.py`（**11/11 PASS**，seed 20260927）

**① 單位換算問題**：本 O `LAMBDA_SYNC = 406.1  # h⁻¹ Mpc`（`scripts/04,05,06,07,07_v2,08,09,10,11,12,13,19` 硬編；
`scripts/01` 亦硬編 `LAMBDA_SYNC_HMPC = 406.1`）。
錨 `c/H₀ = 2997.92 h⁻¹Mpc`（h 無關）⟹ **Mpc → h⁻¹Mpc 係「乘 h」**；
406.1 = 294.877/0.7259 係「**除 h**」⟹ **方向錯**（源頭 = v9.0 `kchain_cosmic_web/_core.py` 嘅 `LAMBDA_SYNC/H`）。
交叉驗證：`r_d = λ_sync/2 = 147.4386 Mpc`（O127，eBOSS −0.23%）乘 h(0.676) = **99.67 h⁻¹Mpc** ≈ 觀測 BAO ~100 ✅
（除 h 得 218 ✗）。
正確：`λ_sync = 199.34 h⁻¹Mpc`（h=0.676）/ 214.05（h=0.7259）⟹ `Δk = 2π/199.34 = 0.031520 h/Mpc`（本 O 用 0.015472，錯 2.04×）。

⚠️ **本 O 兩條分支都受影響**（同一個 406.1 餵晒兩邊）：
- **s-space**（`λ/(n+0.5)` 零點、`λ/n` 峰）：`scripts/01,04,05,06,07,07_v2,08,09,11`
- **k-space**（`2π(n+0.5)/λ`、`2πn/λ`）：`scripts/09,11,19`
（本 O data 檔亦自標「88 fixed-point theorem (k-space): **NEEDS REVIEW**」、「Extra fixed points (k-space): 14」。）

**② 折疊檢定（零參數，2×10⁵ null）**：
- BOSS DR12 P(k) 相位折疊：α=1 → **p = 0.872**（觀測功率低於 null 中位）；α-scan best α=1.712 → **p = 0.994**。
- eBOSS DR16 ξ(s) 峰/零差：
  | λ_sync | 來源 | Δ | p |
  |:-------|:-----|:--|:-:|
  | 199.34 | 正確 (×h, 0.676) | +0.08σ | 0.360 |
  | 214.05 | 正確 (×h, 0.7259) | +0.03σ | 0.458 |
  | **406.10** | **本 O 硬編** | **+1.71σ** | **0.026** |
  | 436.21 | o133 ÷h | −0.97σ | 0.752 |
- **★ 用本 O 自己嘅 406.1 直接測，得 +1.71σ（單一 λ p = 0.026）—— 但 λ 掃描 100→600 h⁻¹Mpc（26 點）
  後，觀測 `max|Δ/σ| = 1.58` 而 null `max|Δ/σ|` 中位 = **1.57**、95% 界 = 2.36 ⟹
  look-elsewhere 校正後 `p_scan = 0.479`。即 406.1 嘅 +1.71σ 係掃描雜訊，唔係訊號。**

**③ 建議動作（本 O 自行判斷，O131 唔代改）**：
- 核 `LAMBDA_SYNC` 定義：應為 `λ_sync[Mpc] × h`（並註明用邊個 h）；重跑 `scripts/01,04,05,06,07,08,09,11,19`。
- 核 `final_result.md`「P(k) Wiggle 獨立驗證: 9/9 理論零點匹配（平均偏差 1.74×10⁻³ h/Mpc）」——
  該 9 個零點建基於 0.015472 h/Mpc 週期 ⟹ 按新週期 0.031520 重評（範圍內零點數會由 9 變 ~4）。
- 核「88 不動點定理」嘅 s-space 部分：`s_n = λ_sync/(n+0.5)` 用同一個 406.1 ⟹ 諧波位置整體偏 2×。
- **區分**：`r_d = λ_sync/2` 命中 BAO 尺度（−0.23%）係**結構成功**，與「階梯對比唔顯著」係兩件事。

**④ 交叉引用（同 bug 已被其他 O 記錄/引用）**：
- **O132 `docs/05_unit_correction_multibin.md`** 已引用本段 ①，並**用數據判定方向**：
  11 bin BAO 峰 **101.01 ± 0.62 h⁻¹Mpc** vs 修正值 `s₂ = λ_sync/2 = 99.668`（dev +1.35%），
  錯值 `s₂ = 203.1` 差 101% ⟹ **×h 正確**；修正值（h_fid = 0.676）**λ_sync = 199.337 h⁻¹Mpc**。
- **O130 `docs/04_unit_correction.md`**：406.2227 → **198.63** h⁻¹Mpc（DESI fiducial 0.6736），
  修正後全線重跑；**四巡天 BOSS/eBOSS/DESI DR1/DESI DR2、17 tracer 全部無偵測**；
  DESI DR2 官方 best-fit 曲線實測 BAO bump = 102.0 h⁻¹Mpc（另一條獨立證據）。
- **O131（本 O）**：以**相位折疊 + λ-scan look-elsewhere** 喺 **k-space**（BOSS DR12 P(k)）獨立測試，
  同樣無偵測 ⟹ 三條方法互相印證。

> 只加註, 未改本 O 任何結論檔；核對與修正由本 O 自行執行（O131 唔代改）。

