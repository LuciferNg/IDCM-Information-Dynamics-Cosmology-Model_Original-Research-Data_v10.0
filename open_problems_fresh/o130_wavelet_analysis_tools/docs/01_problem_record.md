# O130 — 小波工具箱宇宙學應用

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `open_problems_fresh/wavelet_toolbox/`
> **前置**: O9 (高 ℓ CMB 峰) 🟢, O42/O122 (冷斑分析) 🔴
> **定位**: 從 v9.0 wavelet_toolbox/ 遷移 — EMD 小波分析在 IDCM 宇宙學中的應用驗證

---

## 一、問題

從 v9.0 wavelet_toolbox/ 遷移 — EMD 小波分析在 IDCM 宇宙學中的應用驗證

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `open_problems_fresh/wavelet_toolbox/`
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

- `open_problems_fresh/wavelet_toolbox/`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

## 六、v9.0→v10.0 遷移驗證 (2026-09-27) — 前置步驟完成

> **狀態**: 🔴 未開始 → 🟡 **遷移判決完成**
> **腳本**: `scripts/01_migration_inventory.py` (18/18) · `02_wavelet_emd_rerun.py` (9/9) · `03_significance_null.py` (5/5) = **32/32 PASS + 14 結構聲稱**
> **判決文檔**: `docs/02_migration_verdict.md` · **結論**: `final_result.md`

### 6.1 判決摘要 (P/R/A/X)

- **P 遷移 (5 項)**: `γ_n = 4 sin²(πn/88)` (88 環精確譜) / `λ_sync = πR_world/44` (dev=0) /
  `v_g = cos(πn/88)` (O99) / `B=4, z=4^ℓ−1` (O76) / 小波+EMD broadband 移除**方法**。
- **A 🟡 (1 項)**: 阻抗 `Z_n=γ_n/|v_g|`、反射 `R_n`、`s_ref=λ_sync/(2n|R_n|)` — 部件係 P 量，
  但「反射偵測」係 v9.0 數據構造。
- **R 🔴 (2 項)**: φ-ratio `A_n∝φ^n` (v9.0 自己已證偽) / z=17 尖銳視界 aliasing
  (z=17=F_proj 存活但 ℓ=log₄18 非 rung)。
- **X 🔴 (2 項)**: `H(z)=H₀(1+z)^α` with ζ(z) (05) / sync dip `z_c=0.6` (O126 已撤回)。

### 6.2 新發現

1. **「EMD 17/19 諧波」= 單調斜坡偽影**: 重跑複現 v9.0 數字 (BOSS EMD 17/18, wavelet 3/18,
   eBOSS 0–10/18)，但 S/N 對 n 嚴格單調 (Spearman ρ=0.9979)，只抽 1 IMF ⟹ 斜坡越 3σ。
2. **BOSS 解析度極限 n_max = 8.53**: 諧波間距 Δs_n=λ/[n(n+1)]，BOSS bin=5 h⁻¹Mpc ⟹
   只有 n=3..8 解析得到；n=9..20 全係 sub-bin aliasing。
3. **φ-ratio 不可辨識**: log A_n vs n 斜率 0.2937 vs log φ=0.4812 (39%)；γ_n 模型擬合更佳。

### 6.3 推導時序索引

| 時間 | Script | 結果 | 記錄 |
|:-----|:-------|:-----|:-----|
| 2026-08-29 | — | O130 建立 (v9.0 審計遷移) | SESSION_START.md |
| 2026-09-27 | `01_migration_inventory.py` | 18/18 — 幾何/譜/阻抗/H(z)/z=17/φ-ratio 分類 | `data/01_*` |
| 2026-09-27 | `02_wavelet_emd_rerun.py` | 9/9 — 實數據 DWT+EMD 重跑 + k-space 對照 | `data/02_*` |
| 2026-09-27 | `03_significance_null.py` | 5/5 — φ-ratio / 斜坡 / 解析度 null | `data/03_*` |
| 2026-09-27 | — | 判決 + final_result | `docs/02`, `final_result.md` |

**依賴鏈**: v9.0 `wavelet_toolbox/` → O130; 交叉: O133 (k-space) / O129 (λ_sync) / O126 (ζ 撤回) /
O138 (z=17) / O76 (離散 z) / O99 (色散) / O135 (P/R/A/X 分類法) / O131 (同批 stacking 遷移) /
O118 (裁定唔做阻抗模型)。

---

## 七、有用層繼續推進 (2026-09-28) — 不合併，X/R 封存歷史

> **指示**: 「不合併，只把有用的繼續在這裏推，廢棄的留作歷史記錄」(2026-09-28)。
> **文檔**: `docs/03_useful_continuation.md` · **腳本**: 04 (5/5) / 05 (9/9) / 06 (5/5) = **19/19**（累計 **51/51**）

### 7.1 分類修訂（僅新增，不改寫 §6）

| 項 | §6 (2026-09-27) | §7 (2026-09-28) |
|:--|:--|:--|
| 阻抗/反射模型 | A 🟡 | **A→🔴 排除**（部件結構但無 v10 擁有者；O118 裁定唔做；O131 一致） |
| φ-ratio / z=17 / H(z)ζ / sync dip | R·X 🔴 | **歷史記錄，封存不改寫** |
| P 骨架 + 方法 | 已遷移 | ★ 就地推到底（calibrated test / 解析度定律 / out-of-sample） |

### 7.2 新推導（有用層）

1. **校準化偵測檢定** (`04`): K_Chain 階梯當完整模板 (matched filter, 只放振幅 A)，broadband=三次樣條，
   `D=max_{knots×δ}Δχ²`，null="broadband+噪聲"。**D_obs=+14.57 vs null mean +15.50 ⟹ p=0.500 ⟹ 零偵測**；
   Δχ² 隨 broadband 自由度 +10.7→+0.4 崩潰 ⟹ 同 broadband 退化。
2. **可解析度定律** (`05`): `n_max(Δs_bin)=(−1+√(1+4λ/Δs_bin))/2`（5→8.53, 4→9.59, 2→13.76, 0.5→28.01）；
   Rayleigh `Δn_res=λ_sync/T`（BOSS 2.32>1）；leakage matrix 相鄰 max 0.18（功率 ~3%）；
   門檻 n=N_d/2=22 → Δs≤0.8028、n=N_d=44 → 0.2052 h⁻¹Mpc。
3. **v10.0-native aliasing** (`05`§D): `F_proj=17=L₆−1 ⟹ ℓ=log₄18=2.08496 非整數`、`n_obs=44/18=2.4444 非整數`
   ⟹ **中階切斷，冇整數 fold 點**；v9.0 尖銳視界 aliasing **無 v10.0 載體**。
   ★ 交叉佐證: **O132** (2026-09-28, commit `96ca0a3`) 獨立證明 K_Chain 階梯 **z-不變**
   (`λ_sync` ℓ-無關 ⟹ `s_n` 每深度固定; 4:1 自相似) ⟹ v9.0「模態隨紅移激活」結構上 FALSE。
4. **Out-of-sample 複現** (`06`): eBOSS DR16 LRG 同一統計量、唔調參 ⟹ 亦零顯著 (p=0.078)；
   ★ 振幅正負號不一致（+1.05e−02 vs −1.53e−01）⟹ 噪聲。滿足 Hard Test ③。
5. **DESI DR1 官方數據** (`07`, 11/11): `data.desi.lbl.gov` DR1 clustering VAC — **7 tracer ξ(s)
   (ξ₀/ξ₂/ξ₄) + 官方 RascalC covariance 135×135 + window matrix**, sha256 全通過
   (`scripts/00_download_desi_dr1.sh`); 官方 4 h⁻¹Mpc binning (n_max=9.59)。
   **首次用相關 χ²**：全局限 p = **0.813**; **結構 δ=0 檢定 p = 0.030 (≈2.2σ, LRG3)** 🟡
   (未達 5σ ⟹ 唔算偵測; 唯一兩個邊緣 tracer LRG3 + LRG+ELG 係同一批星系 ⟹ 非獨立);
   結構 δ=0 max Δχ² = +3.29, 振幅 **3 正 / 4 負**。
   ⚠️ **自己嘅假設被否證**: 「DESI window 洗掉階梯」**錯** — W₀₀ 行和 = 1.000000,
   階梯結構振幅**保留 97.8%** ⟹ window **唔係**障礙。
   **三巡天 (BOSS / eBOSS / DESI)、10 tracer 樣本：structural λ_sync 全部無偵測。**

### 7.3 推導時序索引（續 §6.3）

| 時間 | Script | 結果 | 記錄 |
|:-----|:-------|:-----|:-----|
| 2026-09-28 | `04_calibrated_detection.py` | 5/5 — matched filter + trial-corrected null ⟹ 零偵測 | `data/04_*` |
| 2026-09-28 | `05_resolvability_forecast.py` | 9/9 — 解析度定律/Rayleigh/leakage/門檻/F_proj 中階 | `data/05_*` |
| 2026-09-28 | `06_eboss_replication.py` | 5/5 — eBOSS DR16 out-of-sample 複現 | `data/06_*` |
| 2026-09-28 | `00_download_desi_dr1.sh` | — DESI DR1 clustering VAC 下載 (14 檔, sha256 OK) | `data/desi/*.h5` |
| 2026-09-28 | `07_desi_dr1_test.py` | 11/11 — DESI DR1 7 tracer 相關 χ²; δ=0 p=0.030 🟡; window 假設否證 | `data/desi/07_*` |
| 2026-09-28 | — | 有用層推進完成 + 處置裁定 (不合併) | `docs/03`, `SESSION_START.md`, `final_result.md` |
| 2026-09-28 | `08_desi_dr2_test.py` | 19/19 — DESI DR2 官方 Zenodo 16644577 補充 multipoles (8 tracer, [62.04,150.02], 23 bin, Δs≈4, size+md5 已驗) | `data/08_*`, `data/desi/dr2/*` |
| 2026-09-28 | **全線單位修正** | ⚠️ `λ_sync` 406.2227 → **198.63 h⁻¹Mpc**（v9.0 `_core.py` 用除，應為乘；錯 1.897×）⟹ 03–08 全部重算，**83/83 PASS**；所有巡天所有 tracer 皆 null | **`docs/04_unit_correction.md`**, `data/0*_stdout.txt` |

> ⚠️ **2026-09-28 修正註**：上表 §7.2 第 1、2、5 項（及 §7.3 首 6 行的 p 值）係在**錯尺度**
> λ_sync = 406.2227 h⁻¹Mpc 下計算，**全部作廢**。正確值 198.63 h⁻¹Mpc：
> 節點 s_n = 66.2/49.7/39.7…（非 135.4/101.6/81.2…）、n_max(5)=5.823、n_max(4)=6.565、
> 門檻 n=22→0.3925、n=44→0.1003 h⁻¹Mpc；BOSS p=**0.935**、eBOSS p=**0.432**、
> DESI DR1 δ=0 p=**1.000**（原 p=0.030 🟡 作廢）、DESI DR2 p_global=**1.000**（原 raw Δχ²=12.83 作廢）。
> 詳見 `docs/04_unit_correction.md`（O132/O31 已獨立記錄同一 bug）。
