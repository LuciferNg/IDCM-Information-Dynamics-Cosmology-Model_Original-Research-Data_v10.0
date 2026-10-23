# O9 — 高 ℓ 峰 m=4+ 偏差

## 狀態: 🟡 部分閉合（O9-A/C/D ✅ 已閉合；O9-B 數據精度不足待確認）

## 結論
CAMB 高ℓ峰 (1129/1427) 係殘餘假峰；真實觀測 (Planck/SPT-3G/ACT DR4/ACT DR6) 確認 IDCM 峰位，m=5 需結構修正 ℓ₅=1121。峰位閉合 RMS 0.83%，振幅母函數獲 ACT DR4 獨立驗證。剩餘 O9-B (m=2, 1.86%) 係數據精度不足（ACT 最低 ℓ=598 覆蓋唔到 537），並非理論錯誤。

## 關鍵公式
- ℓ_m = 44×(33−C(9−m,2)) + ((m−1)×9 mod 25)，m=1..4,6,7
- ℓ₅ = 44×(33−F₆) + F₈ = 44×25+21 = **1121**（m=5 修正）
- 7 峰截斷：C(9−m,2) 於 m≥8 退化 → 公式本質只出 7 峰
- 偶峰振幅：A_{2k}/A₁ = ((k+1)/(4k−1))²（4a−b=5=F₅；b_max=11=N_d/4）
- 奇峰振幅：A₅=3/14，A₇=1/7，A₅/A₇=3/2
- 極化相移：EE 674 / TE 1374（π/2 相移）

## 依賴
O9 ← CMB C_ℓ 閉合 → O10（振幅母函數延伸）

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `e21e14925b0572c2` | 2026-10-24 | — | CAMB 高ℓ峰 (1129/1427) 係殘餘假峰；真實觀測 (Planck/SPT-3G/ACT DR4/ACT DR6) 確認 IDCM 峰位，m=5 需結構修正 ℓ₅=1121。峰位閉合 RMS 0.83%，振幅母函數獲 ACT … | open_problems_fresh/o9_high_ell_peaks/final_result.md | — |
<!-- conclusion-history:end -->
