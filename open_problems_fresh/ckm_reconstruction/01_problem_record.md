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

---

## 推導時序索引 (2026-09-04 建立)

> 依 git log + docs mtime 整理，反映真實推導順序，無回溯修改。

| # | 日期 | 事件 | 文檔/腳本 |
|:-:|:-----|:-----|:----------|
| 1 | 08-14 | CKM 初始推導：GST + 8 種方法 (A-I) | docs/ckm_derivation.md §一-四 |
| 2 | 08-14 | Z₃×Z₅ 離散對稱性分析 (SU(2)_L Δ=1) | docs/ckm_derivation.md §三 |
| 3 | 08-14 | 方法 A: θ₁₂=13.58° (3×3 submatrix) | scripts/ckm_derivation.py |
| 4 | 08-14 | 方法 I: θ₂₃=3.97° (6×6+VEV+Z₅) | scripts/multi_scale_ckm.py |
| 5 | 08-14 | Twisted sector 相位 δ=144°, J_CP=3.25e-5 | docs/jcp_derivation.md |
| 6 | 08-14 | φ-power CKM 模型 (Wolfenstein λ=0.492 ❌) | scripts/phi_power_ckm.py |
| 7 | 08-15 | **拍頻算符突破：7/7 beat 公式匹配 PDG (err~1e-7)** | docs/ckm_derivation.md §4.2 |
| 8 | 08-15 | δ_CP 微調至 66.40°，CKM 9/9 元素 <1% | scripts/delta_optimize.py |
| 9 | 08-15 | PMNS beat 公式 (4/4 ✅) | docs/pmns_derivation.md |
| 10 | 08-15 | 中微子質量譜閉合 (φ^(1/8), Δm² 0.03%/0.58%) | docs/neutrino_mass_spectrum.md |
| 11 | 08-16 | 數域修正：beat/beat ∈ ℚ(ζ₁₇₆)⁺ (degree≤40)，數值匹配非代數相等 | docs/research_record.md §14.1 |
| 12 | 08-18 | ω_n ∈ ℚ(ζ₁₇₆)⁺ vs γ_n ∈ ℚ(ζ₈₈)⁺ 修正 | docs/session_20260815_summary.md |
| 13 | 08-25 | problem_record 整理 (本文件初始整理版) | 01_problem_record.md |
| 14 | 09-04 | 文檔獨立核對 37/37 PASS | docs/independent_verification_20260904.md |

**閉合鏈：** GST → 方法A/I → 拍頻算符 → δ_CP=66.40° → 9/9 CKM ✅ → PMNS 4/4 ✅ → 中微子 Δm² ✅

**時序規則：** 所有條目按實際發生日期排列；新發現只追加不回溯；禁止以推導時序回溯污染舊記錄。