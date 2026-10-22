# O43: 全息框架未測試項目 — 交接清單 (O26 衍生)

> **來源**: O26 閉合後剩餘未測試項目 (2026-08-21)
> **狀態**: 🟢🟢 全部完成 (2026-08-31)
> **前置**: O26 已完成 (o26_node57_region/, 15 個記錄文檔 + 25 個腳本)

---

## 背景

O26 (節點 57 + A₅ 對徑結構) 已完整閉合:
- 幾何定理全部成立 (對徑 = 右乘 r₀, ε=5.34°, k 分佈不變量, 三角形匹配)
- 全息「軸對齊」預測 (G2 溫度 + G3 偏振) 被數據否決
- **✅ 以下項目已測試 (2026-08-31 session)**

---

## 未測試項目清單

### 1. 🟢 O43-A: M=33 = F₉−1 相干截斷驗證
- **主張**: 全息屏相干模式上限 M=33, 高 ℓ 截斷 (ℓ>1448) 係「相位空間飽和」而唔係 Silk 阻尼
- **測試**: 對比 O9 高 ℓ 峰數據 (o9_high_ell_peaks/) 同 Silk 阻尼理論曲線
- **判決**: 🟢 Planck 數據顯示平滑衰減, ℓ=1452 處冇階梯式截斷。全息 M=33 硬截斷被否定。詳見 02_o43a_silk_truncation.md

### 2. 🟡 O43-B: 「同調群 = Fibonacci 級聯」詮釋驗證
- **主張**: 振幅級聯 A_{m+1}/A_m 係全息屏邊界同調群 (H_k) 嘅縮放不變量
- **已確認**: A₅=3/14, A₇=1/7, A₅/A₇=2/3 (O9 閉合)
- **未確認**: H_k(邊界) 嘅階數同 F_m 有冇對應
- **測試**: 計算圖嘅 Betti 數: β₀=1, β₁=41, β₂=0 — 與 Fibonacci 數無直接對應 ❌
- **但**: 振幅級聯 Fibonacci 比仍然成立 (A₅/A₇=F₃/F₄, 偶峰 (F₃/F₄)²)
- **新發現**: 圖係平面圖 (Rhombicosidodecahedron), 非 O26 聲稱嘅非平面
- 詳見 03_o43b_homology_fibonacci.md

### 3. 🟡 O43-C: 全球 β = 0.277° 嘅方向依賴 (等 LiteBIRD)
- **已確認**: 全球 β = 0.277°±0.057° (4.8σ, ACT+Planck joint 2026-08)
- **未確認**: β 有冇方向依賴 (anisotropic birefringence)
- **現狀**: Planck PR4 map-space 冇發現 dipole; tomographic 冇發現 anisotropy
- **未來**: LiteBIRD (2029+, MDR 夏季 2026)
- 詳見 04_o43c_beta_anisotropy.md

### 4. 🟢 O43-D: k↔溫度分層推廣 (bootstrap)
- **問題**: 60 節點小樣本限制統計力
- **測試結果**: Bootstrap 93.4% k0>k1>k2; Permutation p=0.0011; MW p=0.0194; Cohen's d=1.329
- **移除極端後**: 即使移除 0,9,53, 分層仍成立 (33.1 > 30.4 > 19.0)
- **結論**: k0>k1>k2 分層統計魯棒
- 詳見 05_o43d_bootstrap.md

### 5. 🟢🟢 O43-E: 非平面性 minor 檢查 (Kuratowski)
- **問題**: 4-regular 60 節點圖冇 K5/K3,3 子圖, 但「面結構唔係平面嵌入」已證
- **測試**: NetworkX Hopcroft-Tarjan 平面性測試
- **結果**: 🟢🟢 **圖係平面圖!** — O26 非平面結論錯誤
- **正確身份**: Rhombicosidodecahedron (60v/120e/62f, 20△+30□+12⬠)
- 詳見 06_o43e_kuratowski.md

### 6. 🟢 O43-F: k=0 節點「容許極端」機制
- **已證偽**: k=0 = 必然極端 (6/8 唔極端)
- **找到機制**: k=0 = 冇阻挫散射 → 自由度最大 → 原始相位穿透
- **極端決定因素**: hop 距離 (原始相位強度) + 大尺度環境
- Node 0 極冷: cold spot anchor; Node 53 極熱: CMB 偶極反相
- 詳見 07_o43f_k0_mechanism.md

---

## 〇、推導時序索引 (derivation timeline, 2026-08-31 建立)

> 規則: 只記推導鏈時序, 禁止回溯污染 (每個推導喺其發生時點寫入, 唔可以事後改寫)
> 驗證: master verify 40/40 PASS (2026-08-31)

| # | 日期 | 步驟 | 推導/發現 | 產出檔案 | 驗證 |
|:-:|:----:|:-----|:----------|:--------|:----:|
| 1 | 08-31 | 計劃 | 讀 SESSION_START + 01_problem_record, 6 項目優先度確認 | SESSION_START | — |
| 2 | 08-31 | 執行 | **O43-C**: 文獻監測 (LiteBIRD 2024-10 KEK 變更 → 2025-09 重規劃通過 → 2026 夏 MDR), β 測量值整合 (Eskilt 2022 0.34° / Louis 2025 0.20° / joint 0.277°) | 04_o43c_beta_anisotropy.md | 文獻 2 篇 |
| 3 | 08-31 | 執行 | **O43-A v1**: 峰振幅 Silk 擬合 → β=4.465 退化, 初步結論「支持全息截斷」⚠️ | run_o43a.py, data_o43a.txt | 擬合退化 |
| 4 | 08-31 | 執行 | **O43-B**: 圖 Laplacian 譜 (λ₁=0.382×3, λ₄=1.075×5), Betti 數 β₀=1/β₁=41/β₂=0, χ=-40 → 同調群≠Fibonacci | run_o43b.py, data_o43b.txt | 60V/120E/20△ |
| 5 | 08-31 | 執行 | **O43-D v1**: Bootstrap k0>k1>k2 93.4%, permutation p=0.0011, MW p=0.0194, Cohen's d=1.329 | run_o43d.py, data_o43d.txt | 重算一致 |
| 6 | 08-31 | 執行 | **O43-F**: k=0 節點詳細, 極端 (0,9,53) mean hop=1.3 vs 普通 mean hop=5.6 → 機制: 原始相位穿透 | run_o43f.py, data_o43f.txt | hop 重算一致 |
| 7 | 08-31 | 修正 | **O43-A v2**: 改完整譜擬合 (ℓ>800), β≈0.0003 退化, 數據跳變 39.2 vs Silk 22.1 → 平滑衰減, 冇階梯 → **修正 v1 結論** | run_o43a_v2.py, data_o43a_v2.txt | d²D@1452=13.2<17.8 |
| 8 | 08-31 | 修正 | **O43-D v2**: leave-one-out 修正 (v1 全 Δ=-39.6 有 bug), 移除 0,9,53 後 33.1>30.4>19.0 仍成立 | run_o43d_v2.py, data_o43d_v2.txt | 每節點 Δ 重算 |
| 9 | 08-31 | 執行 | **O43-E**: NetworkX Hopcroft-Tarjan → **圖係平面圖!** O26 非平面結論錯誤; 冇 K5/K3,3 | run_o43e.py, data_o43e.txt | check_planarity=True |
| 10 | 08-31 | 記錄 | 寫 6 個結論文檔 (02-07) | 02-07_*.md | — |
| 11 | 08-31 | 記錄 | 更新 01_problem_record + SESSION_START 狀態 | 01_problem_record, SESSION_START | — |
| 12 | 08-31 | 驗證 | **Master verify 40/40 PASS** — 所有文檔聲稱值與原始數據重算一致 | run_o43_master_verify.py, data_o43_master_verify.txt | 40/40 |

---

## 交接注意

1. 全部 O26 記錄文檔喺 `o26_node57_region/` (01-16 + README)
2. 驗證腳本: `scripts/25_final_verify.py` — 18/18 核心數值已核對
3. 完整 SMICA IQU 2048 map: `o26_node57_region/data/smica_iqu_2048.fits` (2.0 GB)
4. 修正記錄: k=1 mean|T| 29.71→30.44; p 值 0.024→0.019 (見 16_verification_report.md)
5. 用戶原則: 不取巧不加速, 完整數據, 嚴謹性>速度
