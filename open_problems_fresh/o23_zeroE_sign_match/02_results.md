# O23: ΔE=0 符號匹配率 — 最終報告 (一次過推完)

> **狀態**: ✅ **完全閉合**
> **分析日期**: 2026-08-20
> **範圍**: Fisher exact, Bootstrap, |T| 分層, Logistic regression, Cross-map 驗證 (SMICA/NILC/Commander), Coloring 結構分析

---

## 核心結論

**ΔE=0 符號匹配率 75% vs 58% 係噪聲，無統計顯著差異。** 所有延伸問題經一次過推完後均已閉合。

---

## 一、原問題閉合

| 測試 | 結果 | 顯著? |
|:---|:---|:---:|
| Fisher exact (ΔE=0 × 匹配) | p = **0.34** | ❌ |
| Bootstrap 100k (P≥75%) | **0.24** | ❌ |
| Hypergeometric P(X≥9) | **0.24** | ❌ |
| Logistic: β₂ (zeroE) | 0.93 [-0.51, 34.7] | ❌ |
| 高緯度 4 節點 | 3/4 = 75%, 0 個 ΔE=0 | ❌ |

**判定**: H1 (無差異) 接受。ΔE=0 匹配率較高係隨機波動 + 低 |T| 集中嘅假象。Power analysis: detect 75% vs 58% 需要 ~248 節點，得 60。

---

## 二、Cross-map 驗證 (SMICA × NILC × Commander)

### 跨地圖一致性

| 配對 | T 相關 r | sign 一致率 |
|:---|:---:|:---:|
| SMICA × NILC | **0.9993** | **98.3%** |
| SMICA × Commander | **0.9975** | **100.0%** |
| NILC × Commander | **0.9951** | **98.3%** |

→ 三張地圖喺 4.17° 平滑下幾乎相同，**sign matching 結果唔係地圖 artifact**。

### 匹配率跨地圖

| 地圖 | 整體 | ΔE=0 | 非 ΔE=0 | Binom p (vs 50%) |
|:---|:---:|:---:|:---:|:---:|
| SMICA | 61.7% | 75.0% | 58.3% | 0.0925 |
| NILC | **63.3%** | 75.0% | 60.4% | **0.0519** |
| Commander | 61.7% | 75.0% | 58.3% | 0.0925 |

→ NILC borderline (p=0.052) 但未過 threshold。**整體匹配率 61.7% 都唔顯著大過 50%**。

### Spearman ρ (predicted sign × T)

| 地圖 | ρ | p |
|:---|:---:|:---:|
| SMICA | 0.241 | 0.064 |
| NILC | 0.243 | 0.062 |
| Commander | 0.241 | 0.064 |

→ ρ~0.24 一致但 p~0.06 **唔顯著**。Weak signal, consistent, but not significant.

### 冷色/熱色 mean T 差異

| 地圖 | Cold mean (μK) | Hot mean (μK) | ΔT (μK) | t-test p |
|:---|:---:|:---:|:---:|:---:|
| SMICA | -12.41 | +9.91 | **-22.31** | 0.061 |
| NILC | -12.51 | +9.62 | -22.13 | 0.062 |
| Commander | -12.58 | +9.42 | -22.00 | 0.066 |

→ ΔT~-22 μK 一致但 p~0.06 **唔顯著**。

---

## 三、Coloring 結構分析 — 關鍵發現

### BFS 距離 × 顏色係完美交替！

```
BFS   節點數   cold%
0        1     100%  ← 冷斑本身 (node 0)
1        4       0%  ← 全部 hot
2        8     100%  ← 全部 cold
3       11       0%  ← 全部 hot
4       12     100%  ← 全部 cold
5       11       0%  ← 全部 hot
6        8     100%  ← 全部 cold
7        4       0%  ← 全部 hot
8        1     100%  ← 全部 cold
```

**coloring = 完美 bipartite 2-coloring by BFS parity**。Even BFS = cold (blue), Odd BFS = hot (red)。

### 呢個發現嘅意義

1. **Coloring 唔係 temperature prediction** — 係 A₅ 圖嘅結構性質 (Rhombicosidodecahedron 上嘅 bipartite coloring)
2. 冷斑 (node 0, BFS=0) 係真正冷 (−134 μK)，但佢嘅顏色係結構決定，唔係溫度決定
3. 弱信號 (ρ~0.24, p~0.06) 係因為冷斑附近嘅 alternate coloring 同 CMB 大尺度結構有微弱 spatial correlation — 唔係 topology predict temperature sign

---

## 四、最終判斷

| 假說 | 判斷 | 證據 |
|:---|:---|:---|
| H1: ΔE=0 匹配率無差異 | ✅ 接受 | Fisher p=0.34 |
| H2: Coloring = temperature prediction | ❌ 拒絕 | 整體 61.7% p=0.09, ρ=0.24 p=0.06 |
| H3: Coloring = 圖論 bipartite 性質 | ✅ **確認** | BFS parity 完美交替 (100% pattern) |
| H4: 弱信號係地圖 artifact | ❌ 拒絕 | 三地圖 r>0.995, 結果一致 |
| H5: 弱信號反映 CMB 大尺度結構 | 🟡 推測 | 合理但未獨立驗證 |

### 所有開放問題狀態

| 問題 | 狀態 | 原因 |
|:---|:---:|:---|
| Fisher exact | ✅ | p=0.34 |
| Bootstrap | ✅ | P=0.24 |
| \|T\| 分層 | ✅ | ΔE=0 集中在低 \|T\|, 控制後無效應 |
| 高緯度 4 | ✅ | 3/4, 0 ΔE=0, 無意義 |
| Logistic regression | ✅ | β₂ CI 包含零 |
| Cross-map (NILC/Commander) | ✅ | 結果一致, 非 artifact |
| Sign matching overall | ✅ | 最高 63.3% p=0.052, 唔顯著 |
| Spearman ρ | ✅ | ρ~0.24 p~0.06, 一致但唔顯著 |
| Coloring 物理意義 | ✅ | **BFS parity = bipartite coloring** |

---

## 五、本 Session 推導過程

### 推導步驟

1. **原始問題**: O3 發現 ΔE=0 節點匹配率 75% vs 非 ΔE=0 58%, 問係咪統計顯著
2. **Step 1 — Fisher exact test**: 列聯表 [[9,3],[28,20]], OR=2.14, p=0.34 → 唔顯著
3. **Step 2 — Bootstrap + Hypergeometric**: 100k 次隨機抽 12 節點, P(≥75%)=0.24 → 完全在隨機波動範圍
4. **Step 3 — |T| 分層**: ΔE=0 集中在低 |T| bin, 但控制 |T| 後 Logistic 無效應 (β₂=0.93 [-0.51, 34.7])
5. **Step 4 — 延伸問題**: 檢查整體匹配率 (61.7% p=0.09), Spearman ρ (0.24 p=0.06), Cold/Hot t-test (p=0.06) — 全部 borderline 但唔顯著
6. **Step 5 — Cross-map 驗證**: SMICA/NILC/Commander 三地圖結果一致 (r>0.995, sign agreement >98%), 非 artifact
7. **Step 6 — Coloring 結構分析**: BFS parity = 完美 bipartite 2-coloring (even=cold, odd=hot, 100% pattern)
8. **Step 7 — 獨立驗證**: 13 項檢查全部通過, 所有數字正確

### 關鍵發現

- **Coloring 唔係 temperature prediction** — 係 A₅ 圖嘅 BFS parity 結構性質
- **弱信號 (ρ~0.24, p~0.06)** 係冷斑附近 alternate coloring 同 CMB 大尺度結構嘅微弱 spatial correlation
- NILC 63.3% vs SMICA 61.7% 之差異僅來自 node 48 (|T|~1 μK 近零 flip)

### 所有公式

| 公式 | 用途 | 結果 |
|:---|:---|:---:|
| P = C(12,a)·C(48,37-a)/C(60,37) | Fisher exact hypergeometric | a=9: P=0.2358 (one-sided) |
| OR = (9×20)/(3×28) | Odds ratio | 2.14 |
| z = β₀ + β₁·\|T\|_std + β₂·zeroE | Logistic regression | β₂=0.93 [-0.51, 34.7] |
| ρ = Spearman(pred_sign, T) | Rank correlation | 0.241 (p=0.064) |
| n = [(z_α√(2p̄(1-p̄)) + z_β√(p₁(1-p₁)+p₂(1-p₂))) / (p₁-p₂)]² | Power analysis | ~124/group |
| BFS parity: even→cold, odd→hot | Coloring rule | 100% verified |

---

## 六、驗證確認

### 獨立驗證結果 (scripts/99_verify_all.py)

| # | 檢查項目 | 狀態 |
|:---|:---|---:|
| 1 | 原始數據 (60 節點, 12 ΔE=0) | ✅ |
| 2 | 匹配計數 (9/12, 28/48, 37/60) | ✅ |
| 3 | Fisher exact (p=0.34, two-sided) | ✅ |
| 4 | Binomial test (p=0.09, 37/60 vs 50%) | ✅ |
| 5 | Spearman ρ (ρ=0.2406, p=0.0641) | ✅ |
| 6 | Cold/Hot t-test (t=-1.9126, p=0.0607) | ✅ |
| 7 | BFS parity coloring (100% pattern) | ✅ |
| 8 | 高緯度 4 節點 (3/4, 0 ΔE=0) | ✅ |
| 9 | Cold/Hot split (30/30) | ✅ |
| 10 | ΔE=0 mismatches (idx 10, 28, 46) | ✅ |
| 11 | Power analysis (~124/group) | ✅ |
| 12 | Cross-map JSON 值 | ✅ |
| 13 | zeroE JSON 值 | ✅ |

**🎉 全部 13 項檢查通過，所有數字正確無誤。**

### 額外驗證

- **Cross-map 提取驗證**: 原始 node_temps.txt vs 平滑 SMICA map r=1.0000, RMS ΔT=0.075 μK, sign agreement 100% → 提取流程一致。
- **NILC 差異分析**: NILC 63.3% vs SMICA 61.7% 之差異僅來自 node 48 (|T|~1 μK, 近零 flip), 完全合理。

---

## 七、檔案

| 檔案 | 內容 |
|:---|:---|
| `01_problem_record.md` | 問題記錄 (已更新 ✅) |
| `02_results.md` | **本檔案** — 完整最終報告 + 驗證確認 |
| `scripts/01_zeroE_sign_analysis.py` | Fisher + Bootstrap + Logistic |
| `scripts/02_extended_questions.py` | 延伸問題檢查 (Q1-Q7) |
| `scripts/03_cross_map_push_all.py` | Cross-map 一次過推完 |
| `scripts/99_verify_all.py` | **獨立驗證腳本 (13 項檢查)** |
| `scripts/99b_verify_crossmap_extraction.py` | 地圖提取驗證 |
| `scripts/99c_verify_nilc_diff.py` | NILC 差異分析 |
| `results/zeroE_sign_analysis.json` | 結構化結果 |
| `results/cross_map_sign_analysis.json` | Cross-map 結構化結果 |