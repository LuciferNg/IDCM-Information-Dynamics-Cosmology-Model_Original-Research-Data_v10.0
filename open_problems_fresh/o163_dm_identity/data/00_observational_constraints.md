# O163 — 觀測約束資料層 (Observational Constraints Data)

> 日期: 2026-09-09 | 狀態: 數據層 (未推導)
> 目的: 約束 13.8 MeV DM 候選嘅觀測數據錨點。所有數字附 arXiv/journal 來源。
> 注意: 網絡搜索日期 2026-09-09, 數字以搜索時為準。

---

## C1 — DM 衰變壽命 → e⁺e⁻ (間接, 最強)

**來源**: arXiv:2412.00180 "Strong Constraints on Dark Photon and Scalar Dark Matter Decay from INTEGRAL and AMS-02"
- INTEGRAL/SPI 16 年數據 (30 keV–8 MeV) + AMS-02
- DM → e⁺e⁻ FSR 通道, 1 MeV–2 TeV
- **世界最強約束 (10 GeV–2 TeV), 超過以往 CMB/Lyman-α**:
  - τ ≳ 10²⁵ s (m < 10 GeV)
  - τ ≳ 10²⁹ s (m > 10 GeV)
- scalar DM mixing angle: |θ| ~ 10⁻¹⁶ @ 1 MeV → 10⁻²⁰ @ 10 GeV

**對 13.8 MeV**: τ_DM ≳ 10²⁵–10²⁹ s (插值 ~10²⁵–10²⁶ s 量級)

## C2 — 511 keV 線 (INTEGRAL/SPI 16yr)

**來源**: arXiv:2312.04907 (De la Torre Luque, Balaji, Silk; ApJL 973 L6 + erratum ApJL 991 L29)
- sub-GeV DM → e⁺e⁻ → 正電子 → 正電子素 → 511 keV
- 全正電子傳播/損失 + 銀道面自由電子密度下降
- 排除 ⟨σv⟩ ≲ 10⁻³² cm³ s⁻¹ @ m_χ ~ 1 MeV
- **衰變壽命: τ ≳ 10²⁹ s @ 1 MeV, τ ≳ 10²⁷ s @ 5 GeV** (NFW profile, 系統不確定性 factor few)

**對 13.8 MeV**: τ ≳ ~10²⁷–10²⁸ s (插值)

## C3 — CMB 能量注入 (Planck)

**來源**: Slatyer & Wu, PRD 95, 023010 (2017); arXiv:1308.2578; CERN indico 簡報
- Planck + ACT + SPT + BAO + HST + SN
- DM 衰變到 e⁺e⁻: **τ ≳ 10²⁵ s (sub-GeV)**
- 短壽命衰變: 10⁻¹¹ 份額 @ 10¹⁴ s 已被排除
- 21cm 未來: τ ~ 10²⁷ s @ 100 MeV

## C4 — SN1987A 冷卻

**來源**: Fayet et al. (1509.05901); 1803.00993; 1706.08871
- SN 核心 T_c ≈ 30 MeV, Raffelt criterion: 新粒子光度 < 中微子光度
- **m_χ ≤ 10 MeV + thermal relic → 被排除** (冷卻動力學不可接受)
- 13.8 MeV: 1–30 MeV 區間, 約束視乎耦合強度 (dark photon mixing ε ≲ 10⁻⁹ 量級, plasma 效應對 m_A' < 10 MeV 弱化)
- 若 δW 只係 CR 共振 (產生率細) → 冇 SN 約束問題

## C5 — 核反衝直接探測

**來源**:
- XENONnT WIMP: PRL 131, 041003 (2023): σ_SI < 2.58×10⁻⁴⁷ cm² @ 28 GeV (90% CL), SR0 1.1 t·yr
- XENONnT light DM: arXiv:2409.17868: 3–12 GeV, 進入 neutrino fog (6 GeV)
- XENONnT S2-only: arXiv:2601.11296: 7.8 t·yr, SR0+SR1+SR2 (579.5 天, 2021-05 → 2025-03), 3–8 GeV, DM-電子 + ALP + dark photon

**對 13.8 MeV**: **冇核反衝約束** — 能量低於探測閾值幾個數量級

## C6 — DM-電子散射直接探測 (sub-GeV 唯一通道)

**來源**:
- SENSEI at SNOLAB: PRL 134, 161002 (2025): 單電子率破紀錄, sub-GeV DM 約束, 1e⁻ 通道最強區 m_χ ≲ 1–10 MeV
- SENSEI diurnal: arXiv:2510.20889: m_χ < 2 MeV 改良
- DAMIC-M: PRL 132, 101006 (2024): sub-GeV DM-電子

**對 13.8 MeV**: σ̄_e ≲ 10⁻³⁷ cm² 量級 (只排除強耦合 mediator)。freeze-in benchmark 目標線遠低於現有約束 → 13.8 MeV 弱耦合 DM 完全未受約束

## C7 — Sterile Neutrino DM (ν_s → νγ 射線)

**來源**: NuSTAR (2405.17861, 11 年 stray light); PRD 101.103011; PRD 99.083005; PRD 95.123002
- keV 區 (6–40 keV): NuSTAR 約束到理論預測底部, νMSM 幾乎封死
- m_νs < 10 keV: Chandra/Suzaku/XMM; > 50 keV: INTEGRAL
- **MeV 區 (0.2–100 MeV) = "MeV gap": 最未被探索**
  - 最後專用望遠鏡 COMPTEL 2000 退役
  - COSI (NASA) 2027 發射; MeVCube/GECCO/AMEGO/e-ASTROGAM/GRAMS 提議中
  - arXiv:2604.18674: MeV gap sterile ν 展望 — 未來儀器改善幾個數量級

**對 13.8 MeV**: 正喺 MeV gap 中央 — **未被排除, 亦未有任何探測**

## C8 — 溫 DM / 結構形成

**來源**: 文獻綜合 (Lyα forest: m_wdm ≳ 5–10 keV; 衛星計數)
- 13.8 MeV >> 10 keV → 完全 cold, 結構形成冇約束問題

## C9 — 宇宙學預算 (Planck 2018)

**來源**: arXiv:1807.06209 (Planck 2018 VI, Table 2)
- TT,TE,EE+lowE: Ω_m = 0.3153 ± 0.0073, Ω_Λ = 0.6847 ± 0.0073
- +BAO: Ω_m = 0.3111 ± 0.0056, Ω_Λ = 0.6889 ± 0.0056
- Ω_b h² = 0.02237 ± 0.00015, Ω_c h² = 0.1200 ± 0.0012, h = 0.6736 ± 0.0054

**IDCM 對照 (O148/O116)**:
- Ω_m = 19/60 = 0.316667 (+0.43% vs TT,TE,EE+lowE)
- Ω_Λ = 41/60 = 0.683333 (−0.20%)
- Ω_b h² = 0.042229 × 0.7259² = 0.02224 (−0.6%)
- Ω_DM h² = 0.274489 × 0.7259² = 0.1446 (+20.5% vs Ω_c h²) ← h 張力 (o11/h0_tension)

## C10 — AMS-02 正電子 (O119 內部已有)

**來源**: AMS-02 公開數據 (O119 scripts/data)
- e⁺/(e⁺+e⁻): ~10% @ 10 GeV → ~20% @ 300 GeV
- O119 已閉合: f_W(E) = (1/25)·E^(8/31) 零參數, χ²/dof = 1.094
- m_δW = 13.95 MeV ∈ (2m_e, 2m_μ) → 只衰變 e⁺e⁻

---

## 數據層總結 (對 o163 推導嘅硬約束)

1. **τ_DM ≳ 10²⁵ s** (C1+C2+C3 一致) — 任何 DM 身份必須結構穩定
2. **13.8 MeV 未被排除** (C5+C6+C7) — 正喺 MeV gap, 觀測前沿
3. **衰變通道鎖死 e⁺e⁻** (2m_e < 13.8 MeV < 2m_μ) — C1-C3 最相關
4. **δW (τ=7.1×10⁻¹⁸ s) 唔可以做穩定 DM** (F1) — 43 個數量級矛盾
5. **split 張力**: Ω_DM h² +20.5% (C9) — 屬 h 張力, 非 DM 身份問題
