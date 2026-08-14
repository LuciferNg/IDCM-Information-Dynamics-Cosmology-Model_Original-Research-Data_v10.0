# IDCM v10.0 — 共震點宇宙學

**Information Dynamics Cosmology Model — 10th Generation**

K_Chain 44 個模式之間的共震點 (beat frequency) 經 CY₃(36,98) 幾何投影激化為物質與 CMB。

## 核心假設

> 物質 = K_Chain 44 個頻率之間嘅共震點，經 CY₃ 幾何投影激化

## 研究問題

1. **44 個頻率嘅完整波參數**（波長、頻率、群速度、相速度、能量、振幅、阻抗、極化、衰減、帶寬）
2. **946 個 beat frequency 嘅結構**（44×43/2 對組合）
3. **SM 粒子質量譜 = beat ratio 譜**（粒子質量比 = ωₙₘ/ω₁）
4. **CKM 角 = CY₃ 投影角**（可計算）
5. **CMB 生成機制**（共震點 thermalization → 黑體譜）
6. **DM = 高 n 弱 beat**（n=4-7 特別弱嘅 beat）

## 目錄結構

```
IDCM-v10.0/
├── README.md
├── src/
│   ├── kchain_wave_params.py    # 44 個模式波參數
│   ├── beat_frequencies.py      # 946 個 beat frequency
│   ├── cy3_projection.py        # CY₃(36,98) 投影幾何
│   └── sm_mass_ratios.py        # SM 質量比對應
├── data/
│   └── (觀測數據)
├── docs/
│   └── (推導文檔)
└── notebooks/
    └── (Jupyter notebooks)
```

## 基礎常數

| 常數 | 值 | 來源 |
|:----|:--|:-----|
| K_Chain 環周長 R_H | 4129.94 Mpc | D_app(∞) |
| Site 數 N_d | 44 | K_Chain 結構 |
| K_Tree 層數 M | 33 | MERA 結構 |
| CY₃(36,98) | h¹¹=36, h²¹=98 | Calabi-Yau 拓撲 |
| φ | (1+√5)/2 | 代數結構 |
| λ_sync | 294.88 Mpc | SYNC 模式 |
| BAO | 147.44 Mpc | λ_sync/2 |
| H₀ | 72.59 km/s/Mpc | D_app 校準 |