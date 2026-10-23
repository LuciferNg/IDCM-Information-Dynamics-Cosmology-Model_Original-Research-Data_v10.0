# O119 — 正電子超出 (AMS-02)：W-field 衰變通道

## 狀態: 🟡 部分閉合（in-frame 全部可攻項已閉合）— 核心保留 = 運動學窗口 ✅；全譜數值閉合 🔴

## 結論
W-field 運動學窗口（m_δW ∈ (2m_e, 2m_μ)，整條 44 模式塔 44/44）係唯一保留嘅結構結果；
「結構化正電子分數 f_W = (1/25)·E^(8/31) 零參數閉合」🔴 降級 —— 密度基準唔過
（q_obs = 0.678）且真實 AMS-02 74 點下 χ²/dof ≈ 6781。剩餘開放項（p_CR、次級背景、
40 MeV 拐點）全部係 CR 加速/傳播物理（框架外）或量級層次錯配。★ 第四輪非透明通道
窮舉（scripts/17）：6 個非透明機制中 5 個屬框架外（QCD/CR 加速/CR 傳播）⟹「框架外」
判定由「搵唔到」升級為**窮舉證明**。★ 第五輪（scripts/18）：DRAGON2 獨立 CR 傳播
code 算純次級正電子分數（谷底 0.020 @ 10 GeV），確認 AMS-02 有大正超出
（峰 +0.124 @ 262 GeV, 12.5σ）⟹ 次級背景 = CR 散裂（框架外）獲**獨立數值確認**。
★ 第六輪（scripts/19）：C2（最後 in-frame 項）**閉合** —— 生產截面 σ_W ∝ |D_h(s)|²
由 **O125 離散 QFT** 推導（高能 s^(−2)，44 閾值 + 共振喺 MeV 尺度）；分數層面檢定
證明 σ_W 修正令分數反轉（−1.562，同觀測 +0.360 矛盾）⟹ **唔產生 8/31**；
觀測上升天然由 CR 譜指數差（p_e − p_CR）解釋。**O119 in-frame 全部可攻項已閉合**。

## 關鍵公式
- 運動學窗口: 2m_e < m_δW = M₀/2 = 13.95 MeV < 2m_μ ✅（只開 e⁺e⁻ 通道）
- 產生率譜形: Γ_n = M₀·γ_n = M₀·ω_n²（γ_n = ω_n² 精確恆等）
- 衰變寬度: Γ(W→e⁺e⁻) = 9.26×10⁻⁵ MeV, τ = 7.1×10⁻¹⁸ s（O37 Lagrangian）
- 🔴 降級: f_W = (1/25)·E^(8/31) — 密度基準 q_obs = 0.678；真實 χ²/dof ≈ 6781
- 譜指數透明性定理: dN_e/dE ∝ E^(−p) EXACT ⟹ γ_obs = p_sec − p_CR 係 CR 傳播量

## 依賴
O37 → O36 → O54 → O119

## 密度基準（O208）
- f_W γ = 8/31: N_search = 108,578, d_med = 0.0137%, d_obs = 0.0221%, q_obs = 67.8% → 🔴
- f_W C = 1/25: N_search = 108,578, q_obs = 98.4% → 🔴
- p_CR = 2.7: N_search = 108,578, q_obs = 100.0% → 🔴
- δ = 0.775 (傳播): N_search = 28,182, q_obs = 99.1% → 🔴
- f_sec (0.055, 0.33, 0.005): q_obs = 98.5% / 99.7% / 76.8% → 🔴
- 真實數據: AMS-02 74 點（CRDB），Voyager 1 電子 9 點（Cummings+2016）

## 檔案
- docs/01_derivation_record.md（首輪，2026-09-03）
- docs/02_session2_density_baseline_audit.md（密度基準 + 透明性定理，scripts 10-12）
- docs/03_session3_real_data_closure.md（真實數據 + 剩餘開放攻堅，scripts 13-16）
- docs/04_session4_opaque_channel_enumeration.md（非透明通道窮舉，scripts 17）
- docs/05_session5_dragon2_crosscheck.md（DRAGON2 次級背景數值確認，scripts 18）
- docs/06_session6_c2_production_closure.md（C2 閉合：σ_W 由 O125 推導，scripts 19）
- scripts/01-19, data/obs/（真實公開數據）

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `34d197b99e468560` | 2026-10-24 | partial | W-field 運動學窗口（mδW ∈ (2me, 2mμ)，整條 44 模式塔 44/44）係唯一保留嘅結構結果； 「結構化正電子分數 fW = (1/25)·E^(8/31) 零參數閉合」🔴 降級 —— 密度基準唔過 （qobs = … | open_problems_fresh/o119_positron_excess/final_result.md | — |
<!-- conclusion-history:end -->
