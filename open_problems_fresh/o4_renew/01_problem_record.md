# O4_renew — 完整獨立重驗證

> **狀態**: ✅ 完成 (2026-08-17, F 系列審計 2026-09-09) — 舊 O4 結論全部經獨立重算確認, 冇嚴重幻覺
> **結果**: `02_verification_result.md` · `03_discovery_correction.md`
> **審計**: F01 推導鏈核對 ✅ · F02 O3 文檔核對 ✅ · F03 冷斑百分位 ✅

## 背景

原 O4 (`o4_fib_motivation/`) 宣稱:
1. A₅ 60 節點圖 (Rhombicosidodecahedron, 120 邊, 26.09° 邊長)
2. λ₂ = φ⁻² (精確 8e-16)
3. ω₂ = √λ₂ = φ⁻¹
4. 節點振幅 = F₅·φ^(-d) 距離衰減 (Fibonacci ladder)
5. 冷斑 node 0 = rank 1/60
6. ΔE=0 節點 (k=2) 壓制
7. BIC: continuous φ^-d 勝出 (37.6)

後續獨立驗證 (`o4_fib_motivation/06_fatal_finding.md`, `07_tasks12_findings.md`) 發現:
- 距離衰減 = node 0 單點驅動
- 跨地圖 (NILC/Commander) 全部消失 — SMICA 特定
- BIC 遺漏 constant-mean 模型

**用戶懷疑: 所有結果可能都有 AI 幻覺 — 需要由頭重驗。**

## 推導時序索引 (Derivation Timeline Index)

> 每條: 步驟 → script → data 輸出 → 結果。時序由底向上 (最早→最新)。

| # | 時序 | 步驟 | Script | 輸出 | 結果 |
|:-:|:----:|:------|:-------|:-----|:-----|
| 1 | 08-17 16:05 | 幾何驗證: 60節點/120邊/degree4/邊長26.13°/面遍歷/BFS/阻挫 | A01_geometry_basics.py | A01_geometry.txt | ✅ 全部正確 |
| 2 | 08-17 16:06 | 圖譜: λ₂=φ⁻² (8.3e-16)/ω₂=φ⁻¹/vertex-transitive/隨機對照 | B01_spectrum_check.py | B01_spectrum.txt | ✅ 數學閉合 |
| 3 | 08-17 16:14 | 觀測: SMICA 載入/座標轉換/node0=-134.2/d1/d0=0.344/跨地圖 | C01_map_sampling.py | C01_map_sampling.txt | ✅ 數字正確 (⚠️ reference 修正) |
| 4 | 08-17 16:16 | Frame 審計: a5_nodes 存 ICRS, node0=冷斑 | C02_frame_audit.py | C02_frame_audit.txt | ✅ 定位一致 |
| 5 | 08-17 16:23 | 統計: BIC constant 33.5 贏 φ^-d 34.8/單點驅動/衰減唔穩定/ΔE=0 | D01_stats_full.py | D01_stats.txt | ✅ 假象確認 |
| 6 | 08-17 16:33 | 階梯判決: 層均唔單調/d=1 vs d=2 median 重疊 | D02_ladder_verdict.py | D02_ladder_verdict.txt | ✅ 冇階梯 |
| 7 | 08-17 16:43 | 冷斑定位: Galactic (209°,-57°) 同文獻一致 | D03_coldspot_position.py | D03_coldspot_position.txt | ✅ 定位不變 |
| 8 | 08-17 16:59 | 功能定位: node0 網絡功能普通 (vertex-transitive) | D04_node0_function.py | D04_node0_function.txt | ✅ 冇中心結構 |
| 9 | 08-17 17:04 | 發現+修正記錄 | — | 03_discovery_correction.md | ✅ 4 修正 |
| 10 | 09-09 09:06 | 推導鏈核對: F1 φ幾何/F3 特徵標/F4 λ₂/F7 冷斑150μK | F01_derivation_chain_verify.py | F01_derivation.txt | ✅ 全鏈閉合 |
| 11 | 09-09 09:08 | 冷斑百分位: 98.2% = 59/60 節點更暖 | F03_percentile_check.py | F03_percentile.txt | ✅ 文檔正確 |
| 12 | 09-09 09:09 | O3 文檔核對: 7 文檔跨一致性 + 公式重算 | F02_o3_docs_verify.py | F02_o3_docs.txt | ✅ 全通過 |

### 推導鏈 (驗證後)

```
0,1 → 2 bits → 2+1=3 → ε³ 截斷
→ A₅ 5-fold 幾何綁定 φ: cos72°=(φ-1)/2, cos36°=φ/2 ✅ F1
→ ε = φ⁻¹/4 = 0.1545084972 ✅ F2
→ A₅ 特徵標: Σdim²=60, χ₃(5A)=φ, χ₃(5B)=1-φ, ⟨χ₃,χ₃⟩=1 ✅ F3
→ A₅ Cayley 圖譜: λ₂ = φ⁻² = 0.381966011250 (8.3e-16) ✅ F4
→ 波主模: ω₂ = √λ₂ = φ⁻¹ = 0.618033988750 (6.7e-16) ✅ F5
→ RMS = ε⁵/8 × T_cmb = 30.00 μK; A = 5ε⁵/8 × T_cmb = 150.00 μK = F₅ ✅ F7
→ [斷裂] 每 hop 衰減 φ⁻¹ → A(d) = F₅·φ^(-d) ← 觀測唔支持 (BIC constant 33.5 贏 34.8)
```

### 驗證清單 (全部 ✅)

### A. 基礎幾何
- [x] A1: a5_nodes.txt 有 60 個節點 ✅
- [x] A3: 邊長 26.13°? 120 邊? degree 4 ✅
- [x] A4: Rhombicosidodecahedron 20Δ+30□+12⬠, Euler=2 ✅
- [x] A5: 阻挫 32? BFS profile 1+4+8+11+12+11+8+4+1 ✅

### B. 圖譜
- [x] B1: λ₂ = 0.381966011250 (8.3e-16) ✅
- [x] B2: 多重度 3 ✅
- [x] B3: vertex-transitive 60/60 ✅
- [x] B4: 隨機對照 λ₂ = 0.164±0.054 ✅

### C. 觀測
- [x] C1: SMICA nside 2048, 冇 NaN ✅
- [x] C2: ICRS→Galactic 轉換正確 (node0 = 冷斑) ✅
- [x] C3: node 0 = -134.2 μK (4.17°) ✅
- [x] C4: d1/d0 = 0.344 (4.17°) ✅
- [x] C5: 跨地圖 SMICA 特定 (NILC/Commander 消失) ✅

### D. 統計
- [x] D1: BIC constant-mean 33.5 贏 φ^-d 34.8 ✅
- [x] D2: 排除 node 0 → 相關消失 (單點驅動) ✅
- [x] D3: 每步衰減唔穩定 (0.593/0.570/1.052) ✅
- [x] D4: ΔE=0 壓制 0.5° p=0.037, 4.17° p=0.017 ✅

## 原則

1. **每個數字獨立重算** — 唔信任舊 scripts, 全部重新寫
2. **只信任原始數據** — a5_nodes.txt, SMICA/NILC/Commander fits
3. **每個結果寫入新文件** — 唔改舊 O4
4. **有幻覺就記錄** — 唔掩蓋
5. **禁止跨文檔污染** — O3 文檔只讀核對, 唔寫入新推導
