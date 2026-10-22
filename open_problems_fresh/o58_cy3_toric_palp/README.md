# O58 — (36,98) 真實 Toric 構造（PALP）

**狀態**: 🟢 已完成 (2026-08-24，含 index 修正)

## 核心發現

1. **(36,98) 係 general toric，唔係 weighted-projective** — CWS 200K 全掃 0 hits
2. **Canonical polytope**: 6-vertex, M:48 6 N:85 7, 48 點 = N_d+B ✅
3. **HF polytopes-4d metadata h11/h12 對調**（15/15+2/2 PALP）— HF 標 (36,98) 實為 (98,36)
4. **真實 (36,98) = 5,021 個**（0.041% 罕有非島；O53「孤島」撤回）
5. **真實 κ**: 350 nnz, K[0,0,0]=-360 — d_tensor 同真實幾何冇對應（corr -0.0258, O50 確認）
6. **普適閉合**: lattice point (1,1,0,0) ↔ K = -232 = -8×L₇（4/4 實例）

## 檔案結構

```
docs/01_palp_identification.md    # 主要鑑定結果
docs/02_true_dijk_vs_dtensor.md   # 真實 κ vs d_tensor（修正版）
docs/04_hf_metadata_swap.md       # HF swap 發現
docs/06_island_correction.md      # 孤島修正
docs/09_index_fix_and_closure.md  # index 修正 + (1,1,0,0) 閉合
docs/11_final_correction.md       # 最終修正
scripts/01-31                     # 完整 pipeline（31 = 正確 κ）
data/                             # polytope + κ + JSON
```

## 開放問題

- 🔴 (1,1,0,0) ↔ -232 = -8×L₇ 嘅機制（唯一 norm²=2&sum=2 點 + N-facet 配對）
- 🔴 block 偏序嘅幾何根源（triangulation order?）
- 🔴 h21 大值 ↔ vertex 上限（20+ 缺席）
- 🟡 K000 分組（有 (1,1,0,0) 淺/冇深）

## 探索 A-AD（docs/12-28）— 全部完成

- A: (1,1,0,0) 係唯一 norm²=2&sum=2 點（4/4）— 特定向量機制
- B: K[0,0,0] 分組 — 有 (1,1,0,0) 淺 (-336..-360) vs 冇深 (-584..-640)，gap 304
- C: d_tensor 全部 10 blocks |corr|<0.08 — 完全解耦
- D: 家族 13.8% 20+，但 (36,98) 全部 ≤19 — (36,98) 自身限制
- E: (1,1,0,0) 對應 N-vertices 6,7 = (-1,2,-1,·) facets
- F: κ block 偏序（0 violations）+ core divisor {0,1,3,4,8}
- G: div0/div8 GLSM mirror（q0+q8 只 8 非零 U(1)=B×2）
- H: 350/350 K≠0 共 simplex（必要非充分）；div0 star=144/144
- I: h21≥98→max_vert≤19 普適定律（修正：h21=97 有 1 個 20v 例外）
- J: 殘餘 8 U(1) 位置 {0,3,7,25,28,29,30,31}，7+29=36=h11
- K: block 偏序 = triangulation 性質（co-simplex 0 violations）
- L: K_Chain 整合表（12 行）
- M: K=0 = 真正幾何 vanishing（redundant [2,3,6,7] 唔係線性組合）
- **N: h11 = 36 = L₄ + L₇（Lucas 分解！）**
- O: div0 -K/8：有 (1,1,0,0) 淺 [42,45] / 冇深 [73,80]
- P: cone vanishing — K = Σ 有向 cone volume，正負抵消
- **R: vertex 索引 = Lucas（pts[1,3,4,7] = L₁-L₄）**
- Q: 26 個 h11 都係 Lucas sums — 36=L₄+L₇ 嘅獨特在於兩者都有物理意義
- S: K = Σdet(σ) × CY 修正因子（K[8,8,8]/Σdet = -2L₇）
- **U: q8 = -q0-1（31/32 GLSM 位置）— div0/div8 ±1 鏡像對**
- T: vertex 索引 Lucas 傾向普適（84.1%, z=10.37σ）→ **🔴 撤回（script 59 bug）**
- X: GLSM col d ↔ pts[d] 確認；e₁-e₄ = {1,3,7,47} = {L₁,L₂,L₄,L₈}
- **V: K[8,8,8] = -L₇×Σ1/|det|（精確）；Σ|det|=200** → Y: 🔴 唔普適（單點）
- **Z: Σ|det| = 200 = -χ + L₉ = 124 + 76** → 🔴 只係 canonical（AB: 真公式 = 4.4×npts）
- **AA: e₁-e₄ 位置傾向 Lucas — z=10.45σ（真結構！）** → 🔴 撤回（AC: 排序偏好, z=1.82）
- **AB: Σ|det| ≈ 4.4×npts（10 實例, corr 0.99）普適閉合！** → ⚠️ 統計趨勢（25 實例 corr 0.99）
- **AD: div3 star=48 只係 canonical**
- **AC: e-position Lucas = 排序偏好（86% 喺 1-10，50% Lucas 密度）**

## 最終閉合（docs/28-29）

**Master Audit: 35/35 PASS**（scripts/72_master_audit.py）
**Docs Consistency: 31/31 PASS**（scripts/73_docs_consistency.py）
**Comprehensive: 28/28 PASS**（scripts/74_comprehensive_verify.py）

- 開放問題 1-3 全部解答（Σ|det|≈4.4×npts 統計趨勢、pts ordering 細數字優先、200=-χ+L₉ 巧合）
- 修正：h21≥98→≤19v（h21=97 有 1 個例外）
- 全部 docs/01-28 數值核對 raw data 確認（docs/29_session_verification_report.md）
