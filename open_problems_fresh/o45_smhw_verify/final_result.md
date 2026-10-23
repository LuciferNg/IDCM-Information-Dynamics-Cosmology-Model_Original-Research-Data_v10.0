# O45 — SMHW 小波獨立驗證冷斑 A=134.2μK

## 狀態: 🟢 已閉合 (2026-08-31 主閉合, 2026-09-12 兩項 🟡 攻堅閉合)

## 結論
SMHW 小波獨立驗證冷斑係全天空最極端 wavelet 結構 (rank 1-2/60 @ R=3-5°),
SMHW 譜峰值 R=4-5° 與內稟 FWHM=8.66° 一致。2026-09-12 攻堅閉合兩項:
(1) 1.4× 偏差來源 = 冷斑係 super-Gaussian 頂帽狀輪廓 (σ*=5.70°, n*=12), 唔係高斯;
(2) SMHW↔pixel 完整換算 = 解析公式 + 雙通道同時閉合 (w Δ=0.13%, T_pix Δ=0.83%)。
⚠️ 原始問題記錄判定標準「小波 A=134.2±2 μK」有量綱錯誤 — SMHW 係 band-pass filter,
小波係數 (~31 μK @ R=4.17°) ≠ pixel 溫度 (−134.19 μK), 兩者互補而非可直接比較。

## 關鍵公式
- A = Σγ_odd(Σγ_even − L₇)/40 = 88×61/40 = 134.2 μK (O41, 零參數) — 引用, 非本 O 推導
- SMHW kernel (harmonic): ψ(γ;R) = (2π)^(−1/2) R⁻¹ [1+(γ/2R)²][2−(γ/2R)²] exp(−γ²/2R²)
  w_l(R) = 2π ∫₀^π ψ(γ;R) P_l(cos γ) sin γ dγ (Antoine & Vandergheynst 1999)
- 冷斑 SMHW 係數: R=4.17° → −31.17 μK (rank 2/60), R=5.0° → −30.28 μK (rank 2/60)
- **1.4× 偏差閉合 (2026-09-12)**: 冷斑輪廓 = super-Gaussian T(θ) = −A·exp(−(θ/σ)ⁿ/2),
  (σ*, n*) = (5.70°, 12) → w 預言 −31.13 (Δ=0.13%), T_pix 預言 −133.08 (Δ=0.83%)
- **SMHW↔pixel 換算 (2026-09-12)**: T_pix = −A·σ²/(σ²+σ_sm²), σ_sm=1.771° (驗證 0.00%);
  完整換算表 w(R)/T_pix vs σ 喺 data/04_conversion_curve.json
- kurtosis: +0.09~+0.14 全尺度正超高斯 (Cruz 2005 方向)

## 依賴
O41 → O42 → O45 (SMHW 獨立方法), 前置數據 O5/O7
(O41 A 結構公式 → O42 六方法獨立量度 → O45 SMHW 小波獨立驗證 → 09-12 輪廓/換算閉合)

## 審計
- scripts/03_verify.py: 67/67 PASS (2026-08-31, 全推導鏈獨立重現)
- scripts/04_doc_audit.py: 49/49 PASS (2026-09-12, 文檔公式/數值/時序/目錄範圍)
- scripts/06_profile_closure.py: 實測 profile 入 SMHW R=4.17° 偏差 1.82% (2026-09-12)
- scripts/07_conversion_curve.py: 解析 T_pix 公式 0.00%, 換算表 7×23 (2026-09-12)
- scripts/08_supergauss_closure.py: σ*=5.70°, n*=12, nside512=1024 (2026-09-12)
- scripts/10_ring_nature.py: 三 map 正環一致 (2026-09-12)
- scripts/11_ring_control.py: 正環 z=1.85σ (p=2.6%) → 背景 (2026-09-12)
- scripts/12_model_decomposition.py: SG+R χ²=104, 三通道閉合 (2026-09-12)
- scripts/13_sech2_closure.py: sech² 孤子證偽 (χ²=2505); top-hat 證偽 (χ²=304) (2026-09-12)
- 推導時序索引: 01_problem_record.md §〇 (25 步, 2026-09-12 更新)
- 🟡 待推導: 疇壁厚度 ← O7 阻挫邊/調律者耦合 (建議新 O-series: 相位滑移疇輪廓)

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `dc14257a9de211c4` | 2026-10-24 | — | SMHW 小波獨立驗證冷斑係全天空最極端 wavelet 結構 (rank 1-2/60 @ R=3-5°), SMHW 譜峰值 R=4-5° 與內稟 FWHM=8.66° 一致。2026-09-12 攻堅閉合兩項: (1) 1.4× 偏… | open_problems_fresh/o45_smhw_verify/final_result.md | — |
<!-- conclusion-history:end -->
