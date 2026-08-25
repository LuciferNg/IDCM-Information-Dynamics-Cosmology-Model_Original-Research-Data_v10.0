# CKM Reconstruction — 夸克混合矩陣與 PMNS 從 K_Chain 拍頻重建

> **創建日期**: 2026-08-14 (初始) / 2026-08-25 (整理)
> **狀態**: 🟡 **部分閉合** — CKM θ₁₂=13.58° (PDG 13.04°, 0.54°), J_CP=3.25e-5 (PDG 3.08e-5, ratio 1.05), δ_CKM=66.40° 結構閉合; 🔴 θ₂₃, θ₁₃ 需完整 12D 結構推導
> **前置**: O34 (88-site 奇偶分解) 🟢, O35 (拍頻→質量 Link-Up) 🟢, O53 (CY₃ 36,98) 🟢
> **腳本**: 25 個 (scripts/)
> **數據**: 58 個 (.npy + .txt, data/)
> **文檔**: docs/01_derivation.md

## 目錄結構

```
ckm_reconstruction/
├── 01_problem_record.md    # 本文件
├── docs/
│   └── 01_derivation.md    # 推導記錄
├── scripts/                # 25 個 Python 腳本
│   ├── ckm_derivation.py
│   ├── ckm_final.py
│   ├── comprehensive_verify.py
│   ├── delta_analysis.py / delta_optimize.py
│   ├── derivation_4line.py / derivation_deep.py
│   ├── final_verify.py
│   ├── kchain_44_ckm.py / kchain_44_ckm_final.py / kchain_44_ckm_v2.py
│   ├── kchain_44_beat_ckm_results.txt
│   ├── mcomp_derivation.py
│   ├── multi_scale_ckm.py
│   ├── phi_power_ckm.py / phi_power_full.py / phi_power_simplify.py
│   ├── pmns_beat_search.py / pmns_beat_search_corrected.py / pmns_derivation.py
│   ├── structural_phi_power.py
│   ├── theta13_derivation.py
│   ├── twisted_sector_phase.py
│   ├── verify_session_20260815.py
│   ├── vev_profile_ckm.py
│   └── z3xz5_projection.py
└── data/                   # 58 個數據檔案 (.npy + .txt)
    ├── V_ckm_*.npy         # 多種 CKM 矩陣版本
    ├── PMNS_*.npy          # PMNS 矩陣
    ├── U_*.npy / Y_*.npy   # 混合矩陣 / Yukawa
    └── *_results.txt       # 推導結果
```

## 關鍵結果

| 量 | IDCM | PDG | 誤差 | 狀態 |
|:---|:----|:----|:----:|:----:|
| θ₁₂ | 13.58° | 13.04° | 0.54° | 🟢 |
| θ₂₃ | 3.97° | 2.38° | 需精確 VEV | 🟡 |
| θ₁₃ | — | 0.201° | 需 12D 結構 | 🔴 |
| J_CP | 3.25e-5 | 3.08e-5 | ratio 1.05 | 🟢 |
| δ_CKM | 66.40° | 65.9° | 0.50° | 🟢 結構 |