# SESSION_START — O42 冷斑 A 獨立量度方案

> 日期: 2026-08-20
> 狀態: 🟢 **已閉合** (2026-08-25)
> 前置: O41 (真空能 = 觀察者預算 🟢), O7 (阻挫邊分佈 🟢), O5 (冷斑目錄 🟢)
> 技能: idcm-cmb-analysis (CMB map 操作)

## 背景

O41 已閉合 A = 88×61/40 = 134.2 μK (dev=0)。三通道方案已執行完畢。

## 閉合結果 (2026-08-25)

### 🟢 核心: A = 134.2 μK 六方法獨立量度確認
SMICA −134.19 / NILC −134.09 / Commander −133.32 / SEVEM_final −134.47 / SEVEM_143 −134.87 / SEVEM_217 −131.85
mean −133.80, std 0.99 μK, spread 3.02 μK (2.25%), max dev 1.75%

### 三通道全部完成
1. **SMHW 小波** (exact harmonic-space + kurtosis): 冷斑 rank 1-2/60, 全天空 percentile 0.4-2.5%, kurtosis +0.11
2. **組份分離** (6 量度): 4 種方法 × 6 產品一致 −134 μK ✅✅
3. **ISW 文獻**: Planck 2015 重建 ISW rms 0.56 μK → ISW 解釋唔到冷斑, IDCM A_prim=A_total=134.2 合理
4. **徑向剖面**: 中心 −134.2 μK (=A) + 8.2° 回升

### 延伸閉合 (2026-08-25)
- **★★本徵尺度 (量綱修正)**: SMHW 超額譜 fit σ_fit=4.08° (χ²=0.4) → 去卷積 (σ_kernel=1.771°)
  σ_int=3.68° → 本徵 FWHM 8.66° ≈ 2×R8 (8.34°) 偏差 3.7% (Planck 2013 直徑~10°)
  ⚠️ R8=4.17° 係 FWHM 唔係 σ — v1「σ=4.08°=R8」量綱錯已修正
- **T-E 偏振**: 冷斑 z=+0.2σ 正常, 溫度-only 結構 (Planck 2015 XVI 一致)

## 已知坑

- **SEVEM ordering 陷阱 (新增)**: IRSA SEVEM fits header 寫 NESTED 但實際已 RING。盲信 reorder → 冷斑消失。用 raw SMICA cross-correlation 驗證。
- **單位陷阱**: o26 raw SMICA 已係 K_CMB (TUNIT1=K_CMB), 唔好乘 T_cmb (會變 K² → −365 μK 假象)
- **PLA 直連**: 頻段圖 ID 404; 用 IRSA mirror (`irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/`)
- **SMHW 係數 ≠ pixel 幅度**: band-pass 係數 (31 μK) vs low-pass pixel (134 μK) 係 filter 響應差異, 互補唔係矛盾

## 檔案

```
o42_independent_measurement_A/
├── 01_problem_record.md        ← 已閉合
├── SESSION_START.md
├── scripts/
│   ├── 01_smhw_verification.py     SMHW 小波 (exact harmonic-space + DoG)
│   ├── 01b_smhw_kurtosis.py        SMHW kurtosis (Cruz 2005 方法)
│   ├── 02_multifrequency_check.py  6 方法量度 (SEVEM ordering 修正)
│   ├── 03_isw_literature.py        ISW 文獻整合
│   ├── 04_radial_profile.py        徑向剖面
│   ├── 05_summarize.py             結果彙整 → docs/03
│   └── 06_verify.py                18/18 無幻覺驗證
├── data/
│   ├── bands/                      SEVEM final/143/217 fits (IRSA)
│   └── 0*.json                     結果數據
└── docs/
    ├── 01_independent_measurement_plan.md
    ├── 02_isw_literature.md
    └── 03_measurement_summary.md   ← 閉合文件
```
