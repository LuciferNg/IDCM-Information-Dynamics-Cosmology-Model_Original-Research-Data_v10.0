# O198 最終結果 — 種子質譜兩通道預言驗證 (Seed Spectrum Two-Channel Verification)

## 狀態
🟢 **已閉合**（scripts/01-05: 37/37 PASS — 預言 1-4 全部數據驗證 + Eddington 前向模型閉合 + 實測 λ_Edd 攻堅）

## 結果摘要

**★★ 預言 1/2 直接支持** — Harikane+23 10 粒 JWST z~4-7 AGN 有 2 粒低於轉折
5.41e6: GLASS_160133 (2.3e6 ↔ k≈48) + GLASS_150029 (3.7e6 ↔ k≈60)，正正喺通道 A
(arcsine) 帶 [2.02e6, 5.41e6] 內 — 低端種子存在，且落喺預言位置（呢兩粒本身係
文獻「重種子模型難題」來源）。

**★★ 預言 3 支持** — 8/8 高端 > 轉折（通道 B 純度）；高端 8 粒 vs 截斷 logN
K-S D = 0.216 < 0.480；轉折帶 1 vs 期望 1.23 一致。

**★★ 預言 4 支持** — P(M ≥ 1.7e9) = 1.016e-3 閉式（z = 3.085）；N=306 LRD:
期望 0.31 粒, P(≥1) = 0.27 — 與 1 粒 UHz1 觀測相容。

**★★ Eddington 前向模型閉合（O174 遺留 🔴 → ✅）** — λ_Edd = f_bar = 0.1 結構
身份；最暗觀測物隱含 L_min ≤ 2.9e43；**反演 L_min* = 5.73e43 令預測低端份額 =
觀測 0.2**（物理合理帶內）— 預言 2 未被證偽，樣本自洽。

**★ w 份額首個數據約束** — w_obs = 0.2 (2/10), CP 95% CI [0.025, 0.556]
（O197 data-gated → 有觀測估計）。

## 誠實修正（§四, 7 項）
1. V4 首版「空缺」測試錯 — 1.0e7 喺帶內, 觀測 1 vs 期望 1.23 係一致
2. V5 CP 二分方向錯 ×2 → 修正 CI [0.025, 0.556]
3. **★O197「高端斜率 −0.84」= Gaussian 指數形式**; 全 PDF 斜率（含 1/M Jacobian）
   = −4.23/dex @ 1e8 — 「命中 O176 −0.5~−1.0 帶」只對 Gaussian 形式成立
4. V4 rank-迴歸 = CDF-plot 假象 → 換截斷 logN 中位測試 (0.75 dex < 2σ)
5. **T5a 固定-λ 中位張力 1.45 ln = 真發現**（λ_Edd=0.1 係 mean 唔係 cutoff;
   λ log-uniform 散射吸收至 1.25 ln）— 維持 🟡
6. **★★T5b「λ 散射吸收」被實測數據推翻 (scripts/05 V2)**: 實測 λ_Edd (Harikane+23
   Table 3, geo 0.702) 前向預測中位 5.40e6, 張力 **−1.78 ln (−0.77 dex)** — 比固定 λ
   (1.45) 同 log-uniform (1.25) 更大; log-uniform 低尾 (λ→0.01) 係假象, 實測樣本冇嗰個
   低尾。張力結構性: 2.5σ (模型) / 3.7σ (觀測散射)。均勻成長排除 (g≤1.14 vs 需 5.92,
   矛盾 5.2×); virial 需 0.77 dex > 文獻 0.3-0.5 dex, 剩 ~0.37 dex 缺口 🟡
7. scripts/05 V4 首版 g_allow 用錯分母 (M_turn vs A_min) → 修正後矛盾 5.2× (更強)

## 攻堅新增 (本 session, docs/02)
- **★實測 λ_Edd 分布**: geo 0.702, arith 1.275, median 1.060, σ_lnλ 1.39 — 結構值
  0.1 偏置 7.0× (0.85 dex), flux-limited 方向正確
- **★選擇階梯機制支持**: log M vs log λ Spearman ρ = −0.648, p = 0.024 (n=10) —
  低質量種子要高 λ 先被探測
- **★L_min 重反演**: 實測 λ 下 L_min* = 1.02e45 (舊 5.73e43 喺 λ=0.1 假設下同實測
  唔自洽), 喺觀測 L_bol 範圍 [1.8e44, 1.1e46] 內 ✓
- UHz1 denominator: N=306 (memory) → **N=434 (Akins+2024 COSMOS-Web 實測)**, P(≥1)=0.36

## 驗證
- scripts/01: 9/9（轉折閉式 M_base·2^{3/2}、通道 A 譜、Π 閉式、中位、域分離）
- scripts/02: 7/7（預言 1-3 放置、w 反演、k-映射、K-S）
- scripts/03: 7/7（λ_Edd 身份、L_min 反演、中位、λ/virial 靈敏度 MC）
- scripts/04: 6/6（UHz1 機率、發生率、斜率校正、截斷中位、LBQS context）
- scripts/05: 8/8（實測 λ_Edd 分布、前向中位、顯著性、成長排除、virial、Spearman、
  低端份額、L_min 重反演）
- **全庫 37/37 PASS**

## 檔案
- `01_problem_record.md` / `docs/01_seed_spectrum_verification.md` /
  `docs/02_measured_eddington_attack.md` / `SESSION_START.md`
- `data/harikane23_table3_eddington.json`（Harikane+23 Table 3, 含誤差）
- `scripts/01`-`05`（37/37 PASS）
- README: O198 已註冊（依賴 O197）

## 交收
🟢 已閉合。預言 1-4 全部冇被證偽，預言 2/3 有直接數據支持；Eddington 前向閉合
O174 遺留；實測 λ_Edd 攻堅 (scripts/05, docs/02) 推翻「λ 散射吸收」、確認張力結構性
2.5-3.7σ、排除均勻成長、支持選擇階梯 (ρ=−0.648)。剩餘 🟡: w 需 mass-complete 低端
樣本收窄、中位張力剩 ~0.37 dex 結構缺口（virial 系統修正 or 更大樣本可攻）、UHz1
denominator 已收窄至 N=434; 🔴 種子全 PDF 尾 (−4.23/dex @1e8) vs 觀測 BHMF
(−0.82/dex LBQS z=2.5) 展平機制未定。
