# O167 — 觀測約束表 (Observational Constraints)

> 日期: 2026-09-10 | 來源: arXiv (見每行) | 狀態: 數據先行層, 供 scripts 引用

## C1-C10: CMB 家族 H₀ (早宇宙 / 聲學視界錨定)

| # | 方法 | H₀ (km/s/Mpc) | 誤差 (68%) | 出處 | 備註 |
|:-:|:-----|:--------------|:-----------|:-----|:-----|
| C1 | Planck 2018 (TT+TE+EE+lowE+lensing) | 67.36 | ±0.54 | Planck 2020, arXiv 1807.06209 | ΛCDM fit |
| C2 | ACT DR6 + Planck (P-ACT, 冇 BAO) | 67.62 | ±0.50 | La Posta 2025 / Louis 2025, arXiv 2503.14452 | ACT+Planck 合併 |
| C3 | P-ACT + CMB lensing + DESI DR1 BAO | 68.22 | ±0.36 | Louis 2025, arXiv 2503.14452 | 含晚宇宙 BAO |
| C4 | P-ACT + DESI DR2 | 68.43 | ±0.27 | Louis 2025, arXiv 2503.14452 | 含晚宇宙 BAO |
| C5 | SPT-3G D1 alone | 66.66 | ±0.60 | Camphuis 2025, arXiv 2506.20707 | CMB only |
| C6 | SPT-3G D1 + DESI CMB-SPA | 68.21 | ±0.31 | Camphuis 2025 | 含 BAO |
| C7 | SPT-3G D1 + DESI sampled | 68.06 | ±0.24 | Camphuis 2025 | 含 BAO |
| C8 | TDCOSMO IV (kinematics, MST) | 67.4 | +4.1/−3.2 | Birrer 2020, arXiv 2007.10441 | 透鏡+動力學 |
| C9 | TDCOSMO XVI (WGD 2038−4008) | 65 | +23/−14 | Wong 2024, arXiv 2406.02683 | 單系統, 大誤差 |
| C10 | TDCOSMO XXV (SDSSJ1433+6007, blind) | 待列 | 6.5% | Sheu 2026, arXiv 2604.14145 | 2026 新盲測 |

**判讀**: C1/C2/C5/C8 = CMB-only / 透鏡 — 唔依賴晚宇宙 BAO。
C3/C4/C6/C7 = CMB + DESI BAO 聯合 — BAO 係晚宇宙距離尺度, 加入推高 H₀ (68.2-68.4)。

## D1-D5: 距離階梯 / 晚宇宙 H₀ (對照組)

| # | 方法 | H₀ (km/s/Mpc) | 誤差 | 出處 | 備註 |
|:-:|:-----|:--------------|:-----|:-----|:-----|
| D1 | SH0ES (Cepheid+SN Ia) | 73.17 | ±0.86 | Breuval 2024 (SH0ES 2024) | 距離階梯 |
| D2 | SH0ES 2022 | 73.04 | ±1.04 | Riess 2022, arXiv 2112.04510 | 距離階梯 |
| D3 | CCHP TRGB (HST+JWST, 24 cal) | 70.39 | ±1.22 stat ±1.33 sys | Freedman 2025, arXiv 2408.06153 | 一步測定 |
| D4 | H0LiCOW (6 lens) | 73.3 | +1.7/−1.8 | Wong 2020 | 透鏡 (power-law) |
| D5 | Maser NGC 4258 錨定 | 73.9 | ±3.0 | Pesce 2020 | 幾何距離 |

## E1-E4: 聲學視界 θ* 同 r_d (CMB 反推 H₀ 嘅核心輸入)

| # | 量 | 值 | 誤差 | 出處 |
|:-:|:---|:----|:-----|:-----|
| E1 | 100θ* (Planck 2018) | 1.04110 | ±0.00031 | Planck 2020, arXiv 1807.06209 |
| E2 | 100θ* (ACT DR6) | 1.04110 | ±0.00010 (待確認) | O73 docs/07 引用; ACT DR6 |
| E3 | 100θ* (SPT-3G D1 alone) | 1.04227 | ±0.00056 | Camphuis 2025 |
| E4 | 100θ* (SPT-3G D1 + DESI) | 1.04180 | ±0.00022 | Camphuis 2025 |
| E5 | r_d drag (Planck 2018) | 147.09 Mpc | ±0.26 | Planck 2020 |

**θ* 實驗間一致性**: E1 vs E3 差 0.112% ≈ 2σ — 三個 CMB 實驗 θ* 本身唔完全一致
(Planck 1.04110 / ACT 1.04110 / SPT-3G 1.04227)。IDCM 預言 100θ* = 1.04125 落喺
Planck-ACT 同 SPT-3G 之間。

## F1-F3: IDCM 結構量 (交叉目標)

| # | 量 | 值 | 身份 |
|:-:|:---|:----|:-----|
| F1 | ω_ring = c/R_world | 72.5895 (km/s)/Mpc | 世界環角頻率 (O73, 幾何恒等) |
| F2 | R_world | 4129.94 Mpc | 世界環半徑 (O73) |
| F3 | λ_sync = 2πR_world/88 | 294.883 Mpc | 同步波長 = L_ring/88 (O73/O164) |
| F4 | r_s = λ_sync/2 | 147.441 Mpc | IDCM 聲學視界候選 (O73/O74: r_s = λ_sync/2) |
| F5 | D_A(z*) = (24/7)R_world | 14159.79 Mpc | O73 docs/06 (24 = 2B·N_gen, 7 = L₄) |
| F6 | θ* = 7π/2112 | 0.01041248 rad | O74 script 04 SU(12) 推導 (25/25) |

## 判準 (o163 繼承)

1. 零新常數 — 全部預言只用 F1-F6 結構量
2. 觀測數據先於推導 — 本表即 C1-E5 全部 arXiv 可追溯
3. 反秘數 — 5%/7% 裸數唔直接用, 只用結構因子 (π/44, 7/24, κφ⁻¹)
4. σ 化閉合判斷 (O158) — dev 先轉 σ, 誤差內 = 一致預測, 唔係殘差
