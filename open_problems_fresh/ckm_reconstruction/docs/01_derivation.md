# CKM Reconstruction — 推導記錄

## 方法概述

CKM 夸克混合矩陣從 K_Chain 44 個拍頻 (beat frequencies) 重建，經 CY₃(36,98) 投影算子的選擇規則篩選。

## 主要推導路徑

1. **拍頻生成**: beat(i,j) = sin(iπ/88)·cos(jπ/88), i=1..44, j=1..43
2. **投影選擇**: CY₃(36,98) 投影算子 P(134×946) 篩選物理態
3. **VEV profile**: 世代 V_cycle 從 d_tensor 本徵值推導
4. **CKM 矩陣**: 從 up-type 和 down-type Yukawa 矩陣計算 V_CKM = U_u†·U_d
5. **CP 破壞**: J_CP = Im(V_ij V_kl V_il* V_kj*), δ_CKM = 66.40° 結構閉合

## 腳本對應

| 腳本 | 功能 |
|:-----|:-----|
| ckm_derivation.py | 基礎 CKM 推導 |
| ckm_final.py | 最終 CKM 計算 |
| delta_analysis.py / delta_optimize.py | δ_CKM 分析與優化 |
| derivation_4line.py / derivation_deep.py | 4 行推導 / 深度推導 |
| final_verify.py | 最終驗證 |
| kchain_44_ckm.py 系列 | K_Chain 44 模式 CKM |
| pmns_derivation.py 系列 | PMNS 中微子混合推導 |
| theta13_derivation.py | θ₁₃ 推導 |
| twisted_sector_phase.py | Twisted sector 相位 |
| z3xz5_projection.py | Z₃×Z₅ 投影 |

## 開放問題

- 🔴 θ₂₃ (目前 3.97° vs PDG 2.38°): 需要更精確 VEV profile
- 🔴 θ₁₃ (目前未推導): 需要 12D 完整結構推導
- 🔴 CP 相位 δ (144° 候選): 需要 twisted sector 精確計算