# O7: 阻挫邊 16/16 冷-冷/熱-熱分佈規律

## 狀態: ✅ 已完成 (2026-08-19) + 5 開放問題全數跟進 (A/B/C/D/E) + 2026-09-11 完整審計 (99d 133/133 PASS) + 2026-10-11 天然寫入機制 (16, 15/15 PASS)

## 問題陳述

冷斑項目確認 32 條阻挫邊（16 冷-冷 + 16 熱-熱），但佢哋嘅**分佈規律**未分析：
- 邊類型（Δ-□ vs ⬠-□）同阻挫邊有冇關聯？
- 16 冷-冷 同 16 熱-熱 係咪對稱？
- 阻挫邊喺網絡上嘅空間分佈（聚類定分散）？
- 阻挫邊 = 20Δ + 12⬠（奇面數），但每個面嘅阻挫邊分配？

## 結果

| 任務 | 結論 | 狀態 |
|:-----|:-----|:----:|
| 1. 邊類型關聯 | 20 Δ-□ + 12 ⬠-□ = 奇面數 (20Δ+12⬠), 完全結構性 | ✅ |
| 2. 冷熱對稱 | 16/16 完美空間對稱, 節點集不重疊 (0 overlap, 52/60 覆蓋) | ✅ |
| 3. 空間聚類 | 20 碎片化 components, CC=0.0000, 零三角形, degree={1:40, 2:12} | ✅ |
| 4. 面分配 | Δ=1 (20/20), □=0/2 (14/16), ⬠=1 (12/12), 全部對邊 | ✅ |
| 5. 物理意義 | 20 條局部縫合線 (單邊×10, 雙邊×8, 三邊×2), 最長 78.3° | ✅ |
| C. 端點 isotropy | R_len=0.0029 (82× 比隨機均勻), 阻挫飽和 signature | ✅ |
| A. 溫度梯度 | 排列檢定 p=0.024 🟡 端點>connector, 10 尺度方向一致 | ✅ 已驗證 |
| B. 拓撲位元 | 20 條縫合線翻轉完全獨立 (0 衝突) → 2^20 結構保證 | ✅ |
| D. 溫度模式 | Δ⬠ ΔT=69.7 vs Δ ΔT=27.4 μK (MW p=0.0085 🟡) | ✅ |
| E. O5 交叉 | 跨冷熱 14/20 (p=4.2%) 但剔除銀河面後 6/10 (p=0.75) 🟢 負結果 | ✅ |

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| 阻挫邊總數 | 32 (16 冷-冷 + 16 熱-熱) | 17_exact_graph_coloring.py |
| 阻挫飽和 | 32 = 20Δ + 12⬠ | 18_topological_closure.md |
| 面結構 | 20Δ + 30□ + 12⬠ = 62 | 18_face_verification.py |
| 雙峰預測 | 17.3σ (IDCM) vs 0.38σ (ΛCDM) | 19_bimodal_gradient.py |
| SMICA 檢驗 | 阻挫邊 34.5μK vs 正常邊 53.1μK | 22_smica_smoothed.py |
| **正方形 frust** | **0×14 + 2×16 (修正: 之前記錄 18/12 錯誤)** | O7 Task 4 |
| **縫合線段** | **20 條 (10 單邊 + 8 雙邊 + 2 三邊)** | O7 Task 5 |
| **總縫合線長度** | **835.8°** | O7 Task 5 |
| **端點 isotropy** | **R_len=0.0029 (82× 比隨機均勻)** | O7 開放問題 C |
| **唯一飽和著色** | **錨定著色 (up to global flip), 隨機 0/50000 到飽和** | O7 開放問題 C |
| **端點梯度** | **36.95 vs 19.84 μK (connector), 排列 p=0.0236** | O7 開放問題 A |
| **Bootstrap CI** | **[+3.92, +30.00] μK, 唔含 0** | O7 開放問題 A |
| **邊級雙峰** | **34.5 vs 53.1 μK, 排列 p=0.0192** | O7 開放問題 A |
| **縫合線翻轉獨立** | **20/20 完全獨立, 衝突圖 0 邊** | O7 開放問題 B |
| **縫合線級 MIS** | **20 條 (每條 1 bit) → 2^20** | O7 開放問題 B |
| **Δ⬠ vs Δ ΔT** | **69.7 vs 27.4 μK (2.5×), MW p=0.0085** | O7 開放問題 D |
| **S18 節點 47** | **全球第 2 冷點 (-123.4 μK), b=-8.6° 喺銀河面內** | O7 開放問題 D/E |

## 驗證路徑 (全部 ✅)

| # | 路徑 | 方法 | 結果 |
|:-:|:----|:-----|:----:|
| 1 | 邊類型關聯 | 面-邊關聯 + χ² + Fisher | 20:12 = 20Δ:12⬠ 結構性 |
| 2 | 冷熱對稱 | 半球/緯度/經度 + 隨機對照 | 完全對稱, 節點集不重疊 |
| 3 | 空間分佈 | 聚類係數 + 隨機著色/選邊對照 | CC=0, 20 components (100%) |
| 4 | 面分配 | 每面 frust 計數 | Δ=1, □=0/2 (對邊), ⬠=1 |
| 5 | 物理意義 | 縫合線追蹤 + SMICA | 20 條局部縫合線, 冇 global seam |
| C | 端點 isotropy | 3D Rayleigh + 隨機對照 | R_len=0.0029, 飽和 signature |
| A | 溫度梯度 | 多尺度掃描 + 排列檢定 + Bootstrap | 端點>connector p=0.024 🟡 |
| B | 拓撲位元 | 縫合線翻轉獨立性 + 衝突圖 | 0 衝突, 縫合線級 MIS=20 |
| D | 溫度模式 | 奇面組合 ΔT + 檢定 + S18 深入 | Δ⬠>Δ 2.5× (p=0.0085) |
| E | O5 交叉 | 端點距離 + 跨冷熱排列 + 銀河面剔除 | 跨冷熱 4.2% 但銀河面後 75% |
|| 99c | 獨立重算 | 32 項 (A/B/D/E 全數, 唔依賴 08-15) | 32/32 ✅ 與文檔一致 |
|| 99d | 由零重算 | 133 項 (圖論/溫度/拓撲/O5 交叉, 唔 import 原 scripts) | 133/133 ✅ 與文檔一致 (2026-09-11) |
|| 16 | 機制推導 | 15 項 (G1 flip=π 相位橋 / G2 ΔE「2」裁定 / G3 12-節點 / G4 θ_i 偵察) | 15/15 ✅ (2026-10-11) |

## 可證偽預測

| # | 預測 | 狀態 |
|:-:|:-----|:----:|
| 1 | 冇連續縫合線 > 78.3° (3 邊) | 🟢 結構保證 |
| 2 | 正方形 connector 永遠對邊 | 🟢 結構保證 |
| 3 | 端點 (deg-1) 溫度梯度 > connector (deg-2) | ✅ 排列 p=0.024 + CI 唔含 0 |
| 4 | Δ:⬠:□-connector = 20:12:32 | 🟢 結構保證 |
| 5 | 縫合線 = 拓撲位元骨幹, 2^20 自由度 | ✅ 0 衝突圖 + MIS=20 |
| 6 | 任何飽和 2-著色端點 R_len < 0.01 | 🟢 已驗證 (0.0029) |
| 7 | 大 ΔT 縫合線 = 跨冷熱邊界 | ✅ S18 含全球第2冷點 |
| 8 | 縫合線唔沿住 O5 目錄組件邊界 | 🟢 端點距離 = 隨機水平 |

## 相關檔案

```text
o7_frustration_distribution/
├── SESSION_START.md
├── 01_problem_record.md
├── README.md
├── docs/
│   ├── 01_o7_complete_report.md
│   ├── 02_audit_20260911.md    (2026-09-11 完整審計報告)
│   ├── 03_natural_write_mechanism.md  (2026-10-11 天然寫入機制推導 G1-G4)
│   ├── 04_natural_write_theta_audit.md (2026-10-11 θ_i 身份偵察 II + R6 隱藏前提)
│   ├── 05_theta_sky_spectrum.md       (2026-10-11 θ_i 場 sky 側結構 + 嵌入 reformulation)
│   ├── 06_three_channel_spectra.md    (2026-10-11 三通道 ℓ 譜 — 已撤回結構性主張)
│   ├── 07_channel_structure_tests.md  (2026-10-11 通道 ℓ 統計檢定 0/3 — 分化推翻)
│   ├── 08_kl_irrep_closure.md         (2026-10-11 k↔ℓ 子空間閉合: A₅ irrep, 8/8 PASS)
│   ├── 09_kl_mapping_details.md       (2026-10-11 k↔m bijection 7/7 + 88 中點負結果)
│   ├── 10_a5_group_algebra.md         (2026-10-11 ★面邊長=群元素階定理 120/120 + 88鏈負結果)
│   ├── 11_face_level_frustration.md   (2026-10-11 ★面級阻挫定理: 每奇面1邊 20×1+12×1)
│   ├── 12_saturated_coloring_family.md (2026-10-11 ★面級定理 30/30 家族通用 — 結構閉合)
│   └── 13_session_audit.md            (2026-10-11 Session Audit 27/27 — 全鏈驗證)
└── scripts/
    ├── 01_edge_type_correlation.py
    ├── 02_cold_hot_symmetry.py
    ├── 03_spatial_clustering.py
    ├── 04_face_allocation.py
    ├── 05_physical_meaning.py
    ├── 06_endpoint_isotropy.py
    ├── 07_endpoint_temperature_gradient.py
    ├── 08_multiscale_gradient.py       (開放 A: 10 尺度掃描)
    ├── 09_permutation_gradient.py      (開放 A: 排列檢定 + Bootstrap)
    ├── 10_seam_topological_bits.py     (開放 B: 縫合線翻轉獨立性)
    ├── 11_seam_temperature_profile.py  (開放 D: ΔT 模式)
    ├── 12_seam_combo_analysis.py       (開放 D: 奇面組合)
    ├── 13_cross_validate_o5.py         (開放 E: 目錄交叉)
    ├── 14_node47_cross.py              (開放 E: 節點 47)
    ├── 15_cross_stats_galactic.py      (開放 E: 銀河面剔除)
    ├── 16_natural_write_mechanism.py   (2026-10-11: 天然寫入機制, 15/15 ✅)
    ├── 17_theta_sky_spectrum.py        (2026-10-11: θ_i 場 sky 譜 + 圖譜投影, 5/5 ✅)
    ├── 18_three_channel_spectra.py     (2026-10-11: 三通道 ℓ 譜, 6/6 ✅ — 結論已由 19 撤回)
    ├── 19_channel_structure_tests.py  (2026-10-11: 通道統計檢定, 0/3 — MC 推翻分化)
    ├── 20_a5_ell3_verification_and_klmap.py (2026-10-11: ℓ3 驗證 + 圖模交叉, 4/4 ✅)
    ├── 21_kl_irrep_subspace_map.py   (2026-10-11: A₅ 子空間重合, 4/4 ✅)
    ├── 22_kl_mapping_details_and_88_embedding.py (2026-10-11: k↔m bijection + 88 中點, 2/4 🟡)
    ├── 23_a5_group_algebra_labels.py (2026-10-11: A₅ 群代數 + 面階定理, 8/10 ✅)
    ├── 24_seam_type_cross.py       (2026-10-11: 面級阻挫定理, 6/6 ✅)
    ├── 25_saturated_coloring_family_test.py (2026-10-11: 30家族通用 7/7 ✅)
    ├── 26_session_audit.py        (2026-10-11: Session Audit 27/27 ✅)
    └── 99_verification.py  (47/47 ✅)
    └── 99d_audit_independent.py  (133/133 ✅, 2026-09-11)
```

數據來源: `main_problems/p4_cmb_cold_spot/data/`
多尺度 cache: `open_problems_fresh/o5_catalog_compare/data/smooth_cache/`

## 技能

- polyhedral-graph-analysis（核心）
- idcm-cmb-analysis（CMB 內容）

## 審計日誌 (2026-09-11)

完整報告: `docs/02_audit_20260911.md`。99d 由零重算 133/133 PASS，文檔層面零錯誤；發現 4 個 script 層面問題（全部非文檔錯誤）:

| # | 發現 | 性質 | 處理 |
|:-:|:-----|:-----|:-----|
| F1 | ghost-tree symlink 令 script 08 經 symlink truncate 真樹 `o7_multiscale_gradient.txt` (12→2 行) | ⚠️ 資料事故 | git checkout 還原, md5 與 HEAD + 重算版一致 ✅ |
| F2 | script 04 自查 `odd_frust//2` 錯除 2 (實值 32 正確) | check bug | 記錄, 唔改原 script |
| F3 | script 01 總結 print Δ-□=0; script 07 兩行都印 bandpass | display bug | 記錄, 唔改原 script |
| F4 | 主 README 缺 O7 條目行 | 條目外 gap | 記為待辦 (本輪唔改條目外檔案) |

## 推導時序索引

> 時序完整性規則: 禁止以推導時序回溯污染 — 舊文檔 (docs/01, 08-19) 只可追加審計記錄, 唔可以改寫舊結論; 新發現一律入 docs/02 + 本索引。

| 時間 | 事件 | 產出 | 驗證 |
|:-----|:-----|:-----|:----:|
| 2026-08-15 | 冷斑項目確認 32 條阻挫邊 (16 冷-冷 + 16 熱-熱) — O7 嘅數據基礎 (cmb_cold_spot 本體) | a5_nodes/anchored_coloring/frustration_edges | cmb_cold_spot 項目 |
| 2026-08-19 | O7 主推導 Task 1: 邊類型關聯 → 20Δ-□ + 12⬠-□ = 奇面數, χ²=2.0 | 01_edge_type_correlation.py | docs/01 T1 |
| 2026-08-19 | Task 2: 冷熱對稱 16/16, 節點集不重疊 52/60, 7N/9S + 9N/7S | 02_cold_hot_symmetry.py | docs/01 T2 |
| 2026-08-19 | Task 3: 空間聚類 CC=0, 20 components, degree {1:40, 2:12} | 03_spatial_clustering.py | docs/01 T3 |
| 2026-08-19 | Task 4: 面分配 Δ=1×20, □=0×14+2×16 (對邊), ⬠=1×12 | 04_face_allocation.py | docs/01 T4 |
| 2026-08-19 | Task 5: 縫合線 20 條 (10/8/2), 總長 835.8°, 最長 78.3° | 05_physical_meaning.py | docs/01 T5 |
| 2026-08-19 | 開放 C: 端點 isotropy R_len=0.0029 (82×), 唯一飽和著色 | 06_endpoint_isotropy.py | docs/01 開放 C |
| 2026-08-19 | 開放 A: 端點梯度 36.95 vs 19.84 μK (4.17°), 帶通 27.97/42.89 | 07_endpoint_temperature_gradient.py | docs/01 開放 A |
| 2026-08-19 | 開放 A: 多尺度 10 尺度掃描, 方向一致 | 08_multiscale_gradient.py | docs/01 開放 A |
| 2026-08-19 | 開放 A: 排列檢定 p=0.0236, Bootstrap CI 唔含 0, 邊級 34.5/53.1 p=0.0192 | 09_permutation_gradient.py | docs/01 開放 A |
| 2026-08-19 | 開放 B: 縫合線翻轉獨立 (衝突圖 0 邊), 2^20, MIS=20 | 10_seam_topological_bits.py | docs/01 開放 B |
| 2026-08-19 | 開放 D: 縫合線 ΔT 52.3 μK, 隨尺度單調減小 | 11_seam_temperature_profile.py | docs/01 開放 D |
| 2026-08-19 | 開放 D: 奇面組合 Δ⬠ 69.7 vs Δ 27.4 μK (MW p=0.0085) | 12_seam_combo_analysis.py | docs/01 開放 D |
| 2026-08-19 | 開放 E: O5 目錄交叉 28.1°, 跨冷熱 14/20 (p=4.2%) | 13_cross_validate_o5.py | docs/01 開放 E |
| 2026-08-19 | 開放 E: 節點 47 (-123.4 μK, 全球第 2 冷, b=-8.6°) | 14_node47_cross.py | docs/01 開放 E |
| 2026-08-19 | 開放 E: 銀河面剔除後 6/10 (p=0.7539) 🟢 負結果 | 15_cross_stats_galactic.py | docs/01 開放 E |
| 2026-08-19 | Session 末驗證: 47/47 + 89/89 + 99c 獨立重算 32/32 | 99/99b/99c | ✅ 與文檔一致 |
| 2026-09-11 | 完整審計: 18 scripts 重跑 + 99d 由零重算 133/133 PASS | 99d_audit_independent.py + docs/02 | ✅ 文檔零錯誤 |
|| 2026-09-11 | RESULT_TEMPLATE → final_result.md | final_result.md | ✅ 已建立 |
|| 2026-09-19 | **下游更正 (O159, 原 O205): 唯一性聲稱證偽** — 60 個 BFS 根 → 30 個相異飽和著色, 全部符合 O7 全部結構條件 | O205 scripts/04 + docs/03 | ⚠️ 見下節 |
|| 2026-10-11 | **天然寫入機制 G1**: 翻轉 = Z₂ = U₈₈ = e^{iπ} 相位橋 — 32 阻挫邊全同色, 翻轉端點令 4 鄰邊相位差反轉 | 16_natural_write_mechanism.py | ✅ G1 5/5 |
|| 2026-10-11 | **G2**: ΔE「2」兩層裁定 (譜側 2×E_min 成本 / 圖側 3−1 邊淨變化, 平行唔混) | 16_natural_write_mechanism.py | ✅ G2 4/4 |
|| 2026-10-11 | **G3 負結果**: 「12 近零 ΔE=0 節點」係 threshold 依賴 (thr=7.5→12, 5→9, 10→15), 冇自然 gap — O162 候選降格 | 16_natural_write_mechanism.py | ✅ G3 3/3 |
|| 2026-10-11 | **G4**: θ_i 三假設全否證 (角距離 corr .111 / 方位 .117 / kπ/88 譜格 frac .273); θ_i 身份 🔴 維持開放 | 16_natural_write_mechanism.py | ✅ G4 3/3 |
|| 2026-10-11 | 天然寫入機制報告 | docs/03_natural_write_mechanism.md | ✅ 已建立 |
|| 2026-10-11 | **θ_i 身份偵察 II**: half-site 格否證 (frac .274), 鏈序否證 (corr −.146); O143 R3 k-層 100% 獨立重現 (corr(k,\|T\|)=−.3819 EXACT); Ising 觀測 H=+6 (≠基態 −56, 寫入已發生) | /tmp explore_theta2/3 → docs/04 | ✅ 負結果閉合 |
|| 2026-10-11 | **O162 兩處修正建議**: ① 12 connector ≠ 12 ΔE=0 (connector 平均 \|T\|=19μK≠0) ② R6 φ_k = πP_k/N_k 係理想 88-site 屏, 未經真實 60 節點屏驗證 | docs/04 §4 | ⚠️ 記錄 (未改 O162) |
|| 2026-10-11 | **唯一剩餘缺口定位**: O7 幾何 ↔ 88-site 鏈嵌入 (同 O162 最後 🔴 同源) | docs/04 §5 | 🔴 開放 |
|| 2026-10-11 | **θ_i 場 sky 側 (S1-S3, 5/5)**: O7 圖 Laplacian 投影主導模 k=13 (λ=φ², P=−1.27); cosθ 場球面諧波 **ℓ=3 主導** (0.697 vs ℓ≤2 0.16/0.12, 4.25×; 同 O143 ℓ=3 破缺一致); 嵌入問題 reformulated = k↔ℓ 譜映射 (非逐點) | 17_theta_sky_spectrum.py + docs/05 | ✅ 5/5 |
|| 2026-10-11 | **三通道 ℓ 譜 (C1-C6, 6/6)**: A5 節點 + G88 透明中點 = **ℓ=3 主導** (93.6/75.5); G32 阻挫寫入通道 = **ℓ=4 主導** (72.2) — 透明 vs 寫入通道分化 (O182 預言 3 嘅 ℓ 譜實現); A5 odd-ℓ 主導 2.23 vs 中點通道 even 主導 0.78/0.65; k↔ℓ 具體映射仍開放 (新錨: 透明=ℓ3, 寫入=ℓ4) | 18_three_channel_spectra.py + docs/06 | ✅ 6/6 |
|| 2026-10-11 | **⚠️ 通道分化撤回 (C7-C9, 0/3)**: MC 檢定推翻 docs/06 — 隨機 32-subset P(dom=ℓ4)=0.487, 觀察 z=+0.09; Δ 分割 z=+0.11 p=0.80; 翻轉家族 p=0.875。根因 = 32 點 ℓ 譜欠定/過擬合。保留: A5 ℓ3 (60點較穩) + O143 定理。k↔ℓ「錨」無效 | 19_channel_structure_tests.py + docs/07 | ⚠️ 撤回 |
|| 2026-10-11 | **O220 交接 (只限交接)**: natural-write-closure 剩餘三瓶頸 (亞熱障/SNR/定址) = O220 docs/19 範圍, register handoff 記錄 | register O7→O220 | 📎 交接 |
|| 2026-10-11 | **ℓ3 驗證加強 + k↔ℓ 子空間閉合 (20: 4/4, 21: 4/4)**: A5 ℓ3 主導 permutation z=+2.93 p=0.0015 (≈3σ), 幾何 null 無角色; 圖模↔球面模交叉 (k13 λφ² ↔ ℓ3 |corr|0.846); **子空間重合矩陣近乎對角: ℓ1↔λ0.382(ρ₃) 0.996, ℓ2↔λ1.075(ρ₅) 0.983, ℓ3↔λ1.764⊕2.618(ρ₄⊕ρ₃') 0.986, ℓ4↔λ3.0⊕3.448(ρ₄⊕ρ₅) 0.956** — k↔ℓ = A₅ irrep 正則副本兩個幾何實現, 🔴 閉合 | 20+21 + docs/08 | ✅ 8/8 |
|| 2026-10-11 | **k↔m bijection + 88 中點負結果 (22: 2/4)**: ℓ3 嘅 7 個 m 全被 k=9..15 一一覆蓋 (k13↔m+3 |c|0.846); 88 中點 line graph 唔係鏈 (度 3-6, 譜共有點 11/88) — 排除天真 88=鏈嵌入, O162 R6 理想屏無實幾何佐證; φ² 近似命中 (Δ0.027) 未過 | 22 + docs/09 | 🟡 |
|| 2026-10-11 | **★面邊長=群元素階 + 88 鏈負結果 ×2 (23: 8/10)**: 頂點標籤=A₅ 元素 (自由作用 bijection); 120 邊差分類零誤配 — 三角面邊=3A (60/60), 五邊面邊=5A (60/60), 冇 2A; 阻挫 32=20△+12⬠ 超幾何 p=0.074 唔顯著; G88 connected 但 40 奇度冇 Euler 鏈 | 23 + docs/10 | ✅ |
|| 2026-10-11 | **★面級阻挫定理 (24: 6/6)**: 每個非正方形面剛好 1 條阻挫邊 — △{1:20}、⬠{1:12}、□{0:30}; 32 阻挫邊 = #{奇面} = 20+12; 20 縫合線(位元) ↔ 20△面 bijection; 單型縫合線 10/20 記錄 | 24 + docs/11 | ✅ |
|| 2026-10-11 | **★面級定理 30/30 家族通用 (25: 7/7)**: 30 飽和著色家族全部不變 — 每奇面1邊 30/30、3A/5A=20/12 30/30、縫合線(20,10) 30/30、縫合線↔△ bijection 30/30; 阻挫分佈結構層閉合 (幾何/代數到底) | 25 + docs/12 | ✅ |
|| 2026-10-11 | **Session Audit (26: 27/27)**: scripts 16-25 重跑 PASS 數同文檔全一致; docs 03-12 引用 10/10; 撤回鏈完整 (06 標注/07 0/3); docs/01 mtime 不變; 跨 O 零污染 (o171/o182 M 全為 9 月舊修改); 3 個 handoff 全註冊 | 26 + docs/13 | ✅ |

---

## ⚠️ 下游更正 (2026-09-19, 來自 O159 — 原 O205 併入)

> 原推導/原文零改動; 本節 = 新增 dated 更正記錄 (o159 docs/09 + scripts/07, 原 O205)。

**證偽項**: 「錨定著色係唯一嘅阻挫飽和 2-著色 (up to global flip)」(docs/01 §開放 C + 已知事實表
「唯一飽和著色」行)。

**證據** (`o159_dirichlet_fieldtheory/scripts/07_saturation_test.py`, 原 O205):
- 面結構獨立重構 ✅ (face-walk 平面嵌入): 20Δ + 30□ + 12⬠ = 62, 每邊屬 2 面 ✓
- 60 個 BFS 根 → **30 個相異阻挫邊集**, 每個 32 條
- **全部 30 個符合 O7 列出嘅全部飽和條件**: 每奇面啱啱 1 條阻挫邊 ✓ / 正方形 0 或 2 (**對邊**) ✓ /
  30-30 平衡 ✓ / k 分佈 8-40-12 ✓ / 端點 R_len = 0.0029 ✓
- 但幾何唔等價 (88 中點距離多重集相異; 唔係 icosahedral 對稱等價)
- 隨機二分對照 (4000 次): 同色邊 min 42 > 32 → 32 確實係最小值 ✓
  (O7 嘅「隨機 0/50000 到飽和」成立, 但**唔蘊含唯一性**)

**論證缺口**: 唯一性論證用「隨機著色唔飽和」做證據 — 但 BFS 家族係**結構性構造**,
唔喺隨機樣本嘅分佈內。飽和條件係必要非充分。

**影響**:
1. 任何用著色定義嘅量 (k 阻挫度 / 88 格 / ΔE=0 集) 都係「**30 選 1**」
2. R_len = 0.0029 係**飽和家族嘅共同性質**, 唔係唯一性 signature ✓
   (O7 嘅可證偽預測「任何飽和著色 R_len < 0.01」方向正確 — 已驗證 30/30 命中)
3. 下游: O182 88 格 = 代表元 (非唯一); O143 k-selector 只 1/30 顯著 (見 o159 docs/09, 原 O205)
