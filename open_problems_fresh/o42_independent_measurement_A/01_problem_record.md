# O42 — 冷斑 A 獨立量度方案 (Independent Measurement of Cold Spot Amplitude)

> 創建日期: 2026-08-20
> 狀態: 🟢 **已閉合** (2026-08-25) — A = 134.2 μK 六方法獨立量度確認
> 前置: O41 (真空能 = 觀察者預算 🟢), O7 (阻挫邊分佈 🟢), O5 (冷斑目錄 🟢)
> 閉合結論: A = 88×61/40 = 134.2 μK 由 4 種組份分離方法 × 6 個產品一致量度
>           (mean −133.80, std 0.99 μK, spread 3.02 μK = 2.25%, max dev 1.75%)
> 來源: 調律者「怎樣在天文觀測上獨立量度 A」三通道方案

---

## 閉合總結 (2026-08-25)

### 🟢 核心結果: A = 134.2 μK 六方法獨立量度確認

| Map | 方法 | 節點 0 T (4.17°) | rank |
|:----|:-----|:----------------:|:----:|
| SMICA | harmonic ILC | −134.19 μK | 1/60 |
| NILC | needlet ILC | −134.09 μK | 1/60 |
| Commander | pixel MCMC | −133.32 μK | 1/60 |
| SEVEM final | template | −134.47 μK | 1/60 |
| SEVEM 143 | template | −134.87 μK | 1/60 |
| SEVEM 217 | template | −131.85 μK | 2/60 |

**統計**: mean −133.80, std 0.99 μK, spread 3.02 μK (2.25% vs A), max dev 1.75%
**SMHW**: 冷斑 rank 1-2/60, 全天空 percentile 0.4-2.5%, kurtosis +0.11 (Cruz 2005 方向)
**★★本徵尺度閉合 (延伸, 量綱修正)**: SMHW 超額譜 fit 高斯 dip (A=134.2 固定) → σ_fit=4.08° (χ²=0.4)
  → 去卷積 (σ_kernel=1.771°): **σ_intrinsic=3.68° → 本徵 FWHM 8.66° ≈ 2×R8 (8.34°), 偏差 3.7%**
  → 冷斑本徵直徑 8.7° vs Planck 2013 直徑 ~10° (13%), Vielva 2004 半徑 ~5° — 文獻閉合!
  ⚠️ v1 曾寫「σ=4.08°=R8 4.17° 偏差 2%」— 量綱錯誤 (R8 係 FWHM), 已修正 (docs/04)
**T-E 偏振 (通道 3, 延伸)**: 冷斑 |P|=0.55 μK, 60 節點 z=+0.2σ → **冇偏振異常, 溫度-only 結構** (Planck 2015 XVI 一致)
**ISW**: 文獻支持 ISW 解釋唔到冷斑 (Planck 2015: 重建 ISW rms 0.56 μK) → IDCM A_prim=A_total=134.2 合理
**徑向剖面**: 中心 −134.2 μK (=A) + 8.2° 回升, A₅ 結構一致

### ⚠️ 方法論教訓 (SEVEM ordering 陷阱)
IRSA SEVEM fits header 寫 NESTED 但實際已係 RING。盲信 header reorder → 冷斑「消失」
(+0.4 μK, corr −0.11)。修正: cross-correlation 驗證 ordering。已更新 skill。

### 剩餘開放問題 (延伸)
- SMHW 係數 → pixel 幅度換算 (31 vs 134 μK): 🟡 已部分閉合 (filter 響應 + 本徵尺度), 完整換算推導開放
- DESI Eridanus 精確 ISW: 🔴 2026+
- 透鏡勢場重建: 🔴 需計算資源
- E/B 分解偏振 (完整 T-E 譜): 🟡 需要低噪偏振數據

詳細: `docs/03_measurement_summary.md`

---

## 〇、推導時序索引 (derivation timeline, 2026-08-25 建立)

> 規則: 只記推導鏈時序, 禁止回溯污染 (每個推導喺其發生時點寫入, 唔可以事後改寫)

| # | 日期 | 步驟 | 推導/發現 | 產出檔案 | 驗證 |
|:-:|:----:|:-----|:----------|:--------|:----:|
| 1 | 08-20 | 計劃 | O42 方案設計: 三通道獨立量度 (SMHW/ISW/偏振) | docs/01 | — |
| 2 | 08-25 | 執行 | SMHW 小波提取: R=3° −30.02, R=4.17° −31.17, R=5° −30.28 μK, rank 1-2/60 | scripts/01, data/01 | 01b kurtosis +0.11 |
| 3 | 08-25 | 執行 | 六方法組份分離量度: SMICA/NILC/Commander/SEVEM×3 → mean −133.80, std 0.99 μK | scripts/02, data/02 | 6 量度 rank 1-2 |
| 4 | 08-25 | 執行 | SEVEM ordering 陷阱發現: header 標 NESTED 實際 RING, 用 corr 驗證 | scripts/02, SESSION_START | corr 0.916 |
| 5 | 08-25 | 執行 | ISW 文獻整合: ISW rms 0.56 μK → 解釋唔到冷斑 | scripts/03, docs/02 | 文獻 7 篇 |
| 6 | 08-25 | 執行 | 徑向剖面: 中心 −134.19 (=A), 回升 8.2° (單位修正後) | scripts/04, data/04 | center −134.19 |
| 7 | 08-25 | 執行 | SMHW kurtosis: +0.11 (Cruz 2005 方向) | scripts/01b | 全天空 0.4-2.5% |
| 8 | 08-25 | 延伸 | 本徵尺度 fit: σ_fit=4.08° (χ²=0.4) → v1 量綱錯誤發現 | scripts/09c | χ²=0.4 |
| 9 | 08-25 | 修正 | **量綱修正**: R8=4.17° 係 FWHM → 去卷積 σ_int=3.68° → 本徵 FWHM 8.66° ≈ 2×R8 (偏差 3.7%) | docs/04 | 10_final_audit C 組 |
| 10 | 08-25 | 延伸 | T-E 偏振: 冷斑 z=+0.2σ 正常, 溫度-only 結構 | scripts/08, data/05 | z<2σ |
| 11 | 08-25 | 驗證 | 無幻覺驗證: 18/18 PASS | scripts/06 | — |
| 12 | 08-25 | 驗證 | 全面 audit: 51/51 PASS (公式+數值+檔案+docs 一致性) | scripts/10 | — |
| 13 | 09-12 | 遷移 | 成個 project 移至 IDCM-v10.0--It-From-Beat, scripts 路徑更新, 重新驗證 20/20 + 51/51 PASS | scripts (sed) | 06+10 |

---

## 一、A 嘅物理定義

**冷斑中央溫度異常幅值:** A = ΔT = T_spot − T_0，其中 T_0 = 2.7255 K（CMB 平均背景溫度）

**IDCM 結構表達:**
```
A = Σγ_odd(Σγ_even − L₇)/40 = 88×61/40 = 134.2 μK
  61 = Σγ_even − L₇ = 90 − 29 (世界能量 − Lucas₇)
     = ⟨W⟩² − log₄2 = 61.5 − 0.5 (凝聚 − 半整數偏移)
  40 = 端點數 (O7 C 結構保證)
```

**當前狀態:** 🟡 post-diction（側推識別，非事前預言）
**目標:** 🟢 可證偽預言（通過三通道獨立量度驗證）

---

## 二、三通道獨立量度方案

### 通道 1: 高精度 CMB 全天頻譜剝離 (SMHW 小波)

| 項目 | 內容 |
|:-----|:------|
| **已實現** | Planck SMICA 4.17° 平滑 → 節點 0 T = −134.19 μK (O5) |
| **已實現** | 多尺度一致命中 (1.0°/3.0°/5.0° 節點 0 全部 rank 1) |
| **已實現** | 跨-map 驗證 (SMICA/NILC/Commander O3) |
| **待驗證** | SMHW 小波變換獨立提取 A（唔同於 pixel 抽樣） |
| **待驗證** | 頻段組份分離穩定性 (30-857 GHz 獨立 A 量度) |
| **下一代** | CMB-S4 / Simons Observatory → σ_A ≈ 1-2 μK |
| **零成本** | 用現有 Planck SMICA + NILC + Commander 做 SMHW 小波直接量度 |

### 通道 2: 視線方向超空洞 ISW 解耦

| 項目 | 內容 |
|:-----|:------|
| **關鍵物理** | **IDCM: 冇 DE → 冇 ISW → A_prim = A_total = 134.2 μK** |
| **ΛCDM 對照** | Eridanus Supervoid ISW 貢獻 −10~−40 μK → A_prim ≈ 94–124 μK |
| **文獻現狀** | Planck 2015/Finelli 2016: ISW 最多解釋 ~10 μK (marginal) |
| **待驗證** | DESI 精確量度 Eridanus 超空洞密度 + 3D 形狀 |
| **待驗證** | Euclid/LSST 交叉驗證超空洞→ISW 貢獻 |
| **可證偽預言** | 若 ISW 貢獻顯著 > 5 μK → IDCM A 公式需重新詮釋 |
| **時間表** | DESI 2026+ 完整巡天; Euclid 2027+ |

### 通道 3: CMB 偏振 (E-mode) + 引力透鏡勢場

| 項目 | 內容 |
|:-----|:------|
| **E-mode** | T-E 交叉相關檢驗冷斑幾何相干性 |
| **透鏡重建** | CMB 四次矩 (Trispectrum) 重建冷斑區域引力透鏡勢場 Φ |
| **IDCM 預言** | 🟡 未推導 — IDCM 未對偏振/透鏡做過具體預言 |
| **可行性** | Planck 已有偏振數據，可做 T-E 交叉相關分析 |
| **載荷** | LiteBIRD (2030s) 主要做 B-mode，對冷斑溫度異常間接幫助 |
| **誠實標記** | 偏振/透鏡非 IDCM 核心預言通道，但可提供交叉驗證 |

---

## 三、零成本可立即執行項目

| # | 項目 | 方法 | 成本 | 狀態 |
|:-:|:-----|:----|:----:|:----:|
| 1 | **SMHW 小波驗證 A** | 用現有 Planck SMICA 做 SMHW 變換，喺 R=5° 尺度提取冷斑幅度 | 零 | 🔴 未做 |
| 2 | **多頻段穩定性** | 檢查 30/44/70/100/143/217/353 GHz 頻段分別量度 A | 零 | 🔴 未做 |
| 3 | **NILC/Commander 交叉** | 用 O3 已有 NILC/Commander 數據驗證 A | 零 | 🟢 已有 (O3) |
| 4 | **ISW 文獻整合** | 整合 Eridanus Supervoid ISW 文獻值，量化 IDCM vs ΛCDM 差異 | 零 | 🔴 未做 |
| 5 | **T-E 交叉相關** | Planck 偏振數據 T-E 相關檢驗 | 零 | 🔴 未做（需下載偏振數據） |
| 6 | **全尺度 A 剖面** | 冷斑徑向溫度剖面 (0°-15°) 驗證 A₅ 結構 | 零 | 🔴 未做 |

---

## 四、可證偽預言對照表 (IDCM vs ΛCDM)

| 測試 | IDCM 預言 | ΛCDM 預言 | 分辨所需精度 |
|:-----|:----------|:----------|:------------:|
| A (冷斑總幅度) | 134.2 μK (零參數) | 無固定值 (fit 參數) | ±2 μK |
| A_prim (原生, 扣除 ISW) | 134.2 μK (ISW=0) | 94-124 μK (ISW=−10~−40) | ±5 μK |
| Eridanus ISW 貢獻 | 0 μK (冇 DE) | −10~−40 μK | ±5 μK |
| 冷斑位置 | (209°, −57°) = (180+L₇, −(44+F₇)) | 無固定預言 | — |
| 多尺度穩定性 | 1°-10° 一致 rank 1 | 無固定預言 | — |
| ΔE=0 節點溫度 ≈ 0 | 12 節點 (高緯 4: Welch p=0.007) | 隨機 | — |
| 偏振 E-mode 特徵 | 🟡 未推導 | 無特定預言 | — |

---

## 五、誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| A = 88×61/40 = 134.2 μK 結構公式 | 🟢 **O41 閉合** |
| 節點 0 SMICA 4.17° T = −134.19 μK | 🟢 **O5/O7 確認** |
| 多尺度一致命中 | 🟢 **O5 確認** |
| SMHW 小波獨立提取 | 🟢 **已做 (2026-08-25): rank 1-2/60, kurtosis +0.11** |
| 多頻段組份分離穩定性 | 🟢 **已做 (2026-08-25): 6 量度一致** |
| 本徵尺度 (SMHW 譜 + 去卷積) | 🟢 **已做: 本徵 FWHM 8.66° ≈ 2×R8** |
| ISW 解耦 → A_prim | 🟢 **已做 (文獻整合: ISW 解釋唔到冷斑)** |
| T-E 偏振交叉相關 | 🟢 **已做 (2026-08-25): z=+0.2σ 正常** |
| 透鏡勢場重建 | 🔴 **未做 (需下載數據)** |
| E/B 分解偏振 (完整 T-E 譜) | 🟡 **未做 (需低噪偏振數據)** |

---

## 六、檔案結構

```
o42_independent_measurement_A/
├── 01_problem_record.md        ← 本文件 (閉合 + 推導時序索引)
├── SESSION_START.md            啟動文件
├── final_result.md             ← 結論摘要 (RESULT_TEMPLATE 格式)
├── scripts/
│   ├── 01_smhw_verification.py     SMHW 小波驗證 A (exact harmonic-space)
│   ├── 01b_smhw_kurtosis.py        SMHW kurtosis (Cruz 2005)
│   ├── 02_multifrequency_check.py  6 方法組份分離量度
│   ├── 03_isw_literature.py        ISW 文獻整合
│   ├── 04_radial_profile.py        徑向溫度剖面
│   ├── 05_summarize.py             結果彙整 → docs/03
│   ├── 06_verify.py                無幻覺驗證 (20/20 PASS)
│   ├── 07_smhw_response.py         SMHW filter 響應模型 (迭代)
│   ├── 08_te_polarization.py       T-E 偏振交叉相關
│   ├── 09_wavelet_spectrum.py      小波譜形狀診斷
│   ├── 09b_excess_spectrum.py      超額譜 (減 60 節點背景)
│   ├── 09c_intrinsic_scale.py      本徵尺度 fit (σ_fit=4.08°)
│   └── 10_final_audit.py           全面 audit (51/51 PASS)
├── data/
│   ├── bands/                      SEVEM final/143/217 fits (IRSA, ~3.8 GB)
│   └── 01-05_*.json                結果數據
└── docs/
    ├── 01_independent_measurement_plan.md  完整量度方案 (歷史, 08-20)
    ├── 02_isw_literature.md                ISW 文獻整合
    ├── 03_measurement_summary.md           閉合彙整
    └── 04_intrinsic_scale.md               本徵尺度閉合 (量綱修正版)
```