# O198 — 種子質譜兩通道預言驗證 (Seed Spectrum Two-Channel Verification)

## 一、問題陳述

O197 閉合留低四個可證偽預言（docs/01_closure.md §三）：
1. 種子質譜喺 **M ≈ 5.41e6 有結構轉折**（通道交界）— 冇轉折 = 模型錯
2. **低端種子 (M < 5.4e6) 必須存在**（arcsine 通道 A）— 完全冇低端種子 = 證偽
3. **M > 5.41e6 全部經 δ_env 通道**（logN 尾, 高端斜率 −0.84）
4. **UHz1 級 (1.7e9) 機率 = logN 尾 ~ 1e-3**

另承接 memory 標記 🔴: 「Eddington forward-model + mass-complete 樣本」（k=36 模態映射已由
O197 T4 閉合）。本 entry 目標：用已下載數據（harikane23_10agn.json + vestergaard09_bqs_bhmf.json）
直接驗證預言 1-4 + 完成 Eddington 前向模型。

零新常數：只用 M_base = 1.914e6 (O173 P7), μ = 0.862478, s = 1.1874 (O174 結構化值),
γ 譜, λ_Edd = f_bar = B/(N_d−B) = 0.1 (結構候選)。

## 二、結果摘要

**★★ 預言 2 支持** — Harikane+23 10 粒 JWST z~4-7 AGN 有 **2 粒低於轉折 5.41e6**：
GLASS_160133 (2.3e6) ↔ k≈48, GLASS_150029 (3.7e6) ↔ k≈60 — 兩粒都正正喺通道 A 範圍
[2.02e6, 5.41e6] 內（scripts/02 V1/V2/V6）。**低端種子存在, 且落喺 arcsine 通道帶**。

**★★ 預言 3 支持** — 8/8 高端 > 轉折（通道 B 純度）; 高端 8 粒 vs 截斷 logN K-S
D = 0.216 < 0.480（scripts/02 V3/V7）; 轉折帶 (M_turn, 2·M_turn) 觀測 1 粒 vs 通道 B
期望 1.23 一致（V4）。

**★★ 預言 4 支持** — P(M ≥ 1.7e9) = 1.016e-3（閉式, scripts/04 V1）; 觀測 1 粒 UHz1
喺 N=306 LRD: P(≥1) = 0.27（V2, denominator data-gated 🟡）。

**★★ Eddington 前向模型閉合（O174 遺留 🔴）** — scripts/03:
- λ_Edd = f_bar = 0.1 結構身份; 最暗觀測物 GLASS_160133 隱含 L_min ≤ 2.9e43
- **反演: L_min* = 5.73e43 令預測低端份額 = 觀測 0.2**（物理合理 1e43-1e44 帶內）
- 固定-λ 中位張力 1.45 dex（預測 7.5e6 vs 觀測 3.2e7）→ λ log-uniform 散射後
  **1.25 dex, 部分吸收** — 中位張力維持 🟡（見開放項 2）
- λ 分布 + virial 散射 0.4 dex 下低端份額 0.39（觀測輸入, 非 IDCM 常數）

**★ w 份額首個數據約束** — w_obs = 0.2 (2/10), Clopper-Pearson 95% CI [0.025, 0.556]
（scripts/02 V5）— O197 標 data-gated 嘅 w 而家有首個觀測估計。

## 三、時序索引

- 2026-09-15: 讀 O195/O196/O197 閉合狀態（O197 docs/01: 預言 1-4 + 參數）
- 2026-09-15: 寫 scripts/01-04; 首跑 — 5 FAIL: 02 V4 空缺測試設計錯（1.0e7 其實喺帶內,
  觀測 1 vs 期望 1.23 一致）、02 V5 CP 二分方向錯 ×2、03 T5 固定-λ 中位張力（真發現）、
  04 V4 rank-迴歸係 CDF-plot 假象、04 V3 O197「−0.84」係 Gaussian 指數形式（全 PDF 斜率
  −4.23/dex, 定義敏感）
- 2026-09-15: 修正測試設計（V4 改數量 vs 期望、V5 CP 反轉、V4 改截斷中位、V3 加全 PDF
  校正）→ **29/29 PASS**（01: 9/9, 02: 7/7, 03: 7/7, 04: 6/6）
- 2026-09-15: 全套記錄寫入 + README 註冊
- 2026-09-15 (本 session 攻堅): 攞 Harikane+23 Table 3 實測 λ_Edd（10 粒 AGN 含誤差,
  存 data/harikane23_table3_eddington.json）→ 寫 scripts/05 (8/8 PASS) + docs/02:
  ★推翻「λ 散射吸收張力」、張力係結構性 2.5-3.7σ、成長排除、選擇階梯支持
  (ρ=−0.648, p=0.024)、L_min 重反演 1.02e45; 同時 scripts/04 V2 更新 UHz1
  denominator: N=306 (memory) → N=434 (Akins+2024 實測) — 全庫 37/37 PASS

## 四、誠實修正

1. **scripts/02 V4 首版錯**: 設計成「轉折帶空缺」測試 — 但通道 B 喺 (M_turn, 2M_turn)
   有 15.4% 機率, 期望 1.23 粒; 觀測 1 粒 (1.0e7) 係一致唔係違反。修正為數量 vs 期望
   （Poisson-ish |obs−exp| ≤ 2√exp）。
2. **scripts/02 V5 CP 二分錯 ×2**: 初版下限/上限公式互換 + cdf 喺 p 遞減方向搞反 —
   修正後 CI = [0.025, 0.556]（正確 Clopper-Pearson, 課本值）。
3. **scripts/04 V3 校正（O197 引用）**: O197「高端斜率 = logN 尾 = −0.84」係 logN
   **Gaussian 指數**斜率 −(lnM−μ)/σ²（冇 1/M Jacobian）; **全 PDF 斜率 = −1.839/lnM =
   −4.23/dex @ 1e8** — 物理密度比引述陡 2.3×。「−0.84 命中 O176 −0.5~−1.0 帶」只對
   Gaussian 形式成立 — O197 閉合記錄引用定義要小心（記錄於此, O197 已閉合唯讀）。
4. **scripts/04 V4 首版錯**: rank vs ln M 迴歸斜率係 CDF-plot 假象（+0.92 正斜率）—
   刪除, 換成截斷 logN 中位測試（觀測 4.2e7 vs 預測 1.99e7, 0.75 dex < 2σ=1.58 dex）。
5. **T5a 固定 λ 中位張力**: 預測 7.52e6 vs 觀測 3.2e7（1.45 ln）— 唔係測試錯, 係真
   發現: λ_Edd = 0.1 固定嘅前向模型低估被選樣本質量; λ log-uniform [0.01,1] 散射吸收
   部分（1.25 ln）— 反映 λ_Edd=0.1 係 mean 唔係 cutoff, 樣本中 detected AGN 需要 λ 散射
   （物理預期）。維持 🟡（開放項 2）。
6. **★★(本 session) T5b「λ 散射吸收」被實測數據推翻 (scripts/05 V2)**: 攞 Harikane+23
   Table 3 實測 λ_Edd 後, 用實測分布 (geo 0.702) bootstrap 前向: 預測中位 5.40e6, 張力
   **−1.78 ln** — 比固定 λ (1.45) 同 log-uniform (1.25) 都更大。T5b 嘅「吸收」係
   log-uniform 低尾 (λ→0.01) 嘅假象: 實測樣本最低 λ = 0.06/0.08 (得兩粒 < 0.1), 冇嗰個
   低尾。修正: docs/01 §三「λ log-uniform 散射後 1.25 dex 部分吸收」表述撤銷, 以 docs/02
   §二為準。
7. **(本 session) scripts/05 V4 首版 g_allow 用錯分母**: 初版用 M_turn/2.3e6 = 2.35
   （「種子仍 < 轉折」）— 應係「種子仍 ≥ 通道 A 下限 2.02e6」: g ≤ min(2.3e6, 3.7e6)/2.02e6
   = 1.14。修正後矛盾 5.2×（更強排除）。按「核對 script 自身都要驗證」紀律, 唔改結論方向。

## 五、開放項

1. 🟡 **w 份額數據約束仍闊**: w_obs = 0.2, CP 95% CI [0.025, 0.556] — 需 mass-complete
   低端樣本（JWST z>5 低質量 BH 普查）收窄
2. 🟡 **中位張力 — 定性更新 (docs/02)**: 「λ 散射吸收」(舊 T5b 1.25 ln) **被實測 λ_Edd
   數據推翻** — 實測 λ (geo 0.702) 前向預測中位 5.40e6, 張力 **−1.78 ln (−0.77 dex)**,
   結構性 (2.5σ 模型 / 3.7σ 觀測散射)。排除: 均勻成長 (g≤1.14 vs 需 5.92, 矛盾 5.2×);
   virial 高估需 0.77 dex > 文獻 0.3-0.5 dex, 剩 ~0.37 dex 缺口。支持: 選擇階梯
   (M-λ ρ=−0.648, p=0.024); L_min 重反演 1.02e45 (實測 λ 自洽, 舊 5.73e43 唔自洽)。
   下一步: 更大 z>4 AGN 樣本 / virial 系統修正測量
3. 🟡 **UHz1 denominator 收窄**: N=306 (memory, 冇出處) → **N=434 (Akins+2024
   COSMOS-Web 實測 LRD 目錄)**: P(≥1) = 0.36, 期望 0.44 — 相容不變
4. 🔴 **全 PDF 斜率 vs 觀測 BHMF**: 種子 logN 尾全 PDF −4.23/dex @ 1e8 比觀測高 z
   BHMF (LBQS z=2.5: −0.82/dex, 演化後) 陡 — 成長/選擇如何展平, 機制未定
