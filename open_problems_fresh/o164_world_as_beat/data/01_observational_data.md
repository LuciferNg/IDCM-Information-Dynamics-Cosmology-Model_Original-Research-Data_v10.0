# O164 — 觀測數據檔 (Observational Data)

> 搜集日期: 2026-09-10 | 用途: P2/P3 交叉閉合基準 (觀測數據先於推導)

## 1. H₀ 家族 (km/s)/Mpc

| 觀測 | 值 | 誤差 | 來源 |
|:-----|:---|:-----|:-----|
| SH0ES 2022 | 73.04 | ±1.04 | Riess et al. 2022 (距離階梯) |
| Miras (NIR) | 73.3 | ±2.6 | Huang et al. 2020 |
| Maser | 73.9 | ±3.0 | Pesce et al. 2020 (M87/NGC4258) |
| JAGB | 72.4 | ±2.2 | Freedman et al. 2020 |
| TRGB | 69.85 | ±1.75 | Freedman et al. 2020 |
| Planck 2018 | 67.36 | ±0.54 | CMB 功率譜 |
| ACT DR4 | 68.3 | ±1.5 | CMB |
| SPT-3G | 68.8 | ±1.5 | CMB |
| TDCOSMO | 67.4 | ±1.2 | 強透鏡 (時延) |
| H0LiCOW | 73.3 | ±1.8 | 強透鏡 (時延) |

## 2. 宇宙年齡

| 量 | 值 | 來源/性質 |
|:---|:---|:---------|
| ΛCDM 年齡 | 13.797 ± 0.023 Gyr | Planck 2018 flat ΛCDM (模型依賴!) |
| IDCM 真年齡 | 11,100.64 Gyr | O51 三層證明 (K_chain 冇起始) |

## 3. 溫度 / 質量

| 量 | 值 | 來源 |
|:---|:---|:-----|
| T_CMB | 2.72548 ± 0.00057 K | Fixsen 2009 (COBE/FIRAS) |
| k_B T_CMB | 2.348637e-4 eV | 導出 |
| M₀ (M0_fund) | 27.900915 MeV | O82 (源自 O38/O34: m_n = M₀·2sin(nπ/88)) |

## 4. IDCM 基本常數 (src/kchain_wave_params.py 一致)

| 常數 | 值 | 身份 |
|:-----|:---|:-----|
| ω_ring | 72.59 (km/s)/Mpc = 2.35248e-18 rad/s | 世界環角頻率 = c/R_world (O73) |
| R_world | 4129.94 Mpc | 世界環半徑 |
| T_ring | 84.63 Gyr | 世界環周期 (T_ring·ω_ring = 2π) |
| λ_sync | 294.877 Mpc | 同步波長 = L_ring/88 |
| γ_n | 4sin²(πn/88) | 44-site K_chain 譜 |
| κ | 1/16 = γ_max⁻² | O163 (Nyquist 模譜值平方倒數) |
| B | 4 | Lucas L₃ = γ_max (O59) |
| N_gen | 3 | 可見模式數 (O116/O163 κ 夾層) |

## 5. 派生頻率標度 (script 01 驗證, 7/7 PASS)

| 量 | 值 (Hz) | 周期 | 身份 |
|:---|:--------|:-----|:-----|
| f_ring | 3.7441e-19 | 84.63 Gyr | ω_ring/2π |
| f_1 | 1.1760e-18 | 26.946 Gyr | ≈ ω_ring/2 (sinc dev 0.021%) |
| f_22 | 2.3298e-17 | — | c/(√2·λ_sync) |
| f_44 = f_scale | 3.2948e-17 | 0.962 Gyr | 88·f_ring = c/λ_sync ←「1e-17 Hz」 |
