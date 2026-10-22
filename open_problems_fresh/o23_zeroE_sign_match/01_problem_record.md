# O23: ΔE=0 節點符號匹配率偏高 — 75% vs 58%

> **來源**: O3 衍生 (o3_node_temperatures)
> **狀態**: ✅ **完全閉合** — 無統計顯著差異 + 所有延伸問題已推完
> **建立**: 2026-08-17

## 問題陳述

ΔE=0 節點 (12 個, k=2, 零能量寫入位元) 嘅「冷色/熱色」符號匹配率係 **75%** (9/12), 非 ΔE=0 節點 (48 個) 係 **58%** (28/48)。

**呢個差異 (75% vs 58%) 有冇統計意義?**

## 已知數據

| 量 | 值 |
|:---|:---|
| ΔE=0 匹配率 | 9/12 = **75%** |
| 非 ΔE=0 匹配率 | 28/48 = **58%** |
| 整體匹配率 | 37/60 = 61.7% |

## 注意 (混淆因素)

1. **ΔE=0 節點溫度接近零** (mean|T|=19.05 vs 36.18) — 小值容易 flip 符號, 匹配率高可能係「符號唔重要」嘅假象
2. 但 75% > 58% 方向係「ΔE=0 更匹配」— 如果反過來先係問題
3. 12 個樣本太少, Fisher exact test 可能冇力

## 開放問題

1. Fisher exact test: 75% vs 58% 嘅 p 值?
2. 排列檢驗: 隨機抽 12 個節點, 匹配率 ≥75% 嘅概率?
3. 溫度和匹配率嘅關係: 符號匹配率隨 |T| 點變化? (大值節點匹配率高係正常)
4. 高緯度 4 節點: 3/4 匹配 (75%) — 單獨檢驗

## 方法

1. Fisher exact 2×2: (ΔE=0, 非) × (匹配, 不匹配)
2. Bootstrap: 從 60 節點隨機抽 12 個, 計匹配率分佈
3. |T| 分層: 按絕對溫度分桶, 計各桶匹配率
4. 控制 |T| 後, ΔE=0 係咪仍然匹配率高? (logistic regression 或分層)

## 假說

- H1 (無差異): 75% vs 58% 係噪聲 (p>0.05)
- H2 (真實差異): ΔE=0 節點確實更符合「冷色=冷, 熱色=熱」
- H3 (|T| 混淆): 匹配率高純粹因為 ΔE=0 溫度細, flip 容易

## 狀態

- [x] Fisher exact → p=0.34 ❌
- [x] Bootstrap → P(≥75%)=0.24 ❌
- [x] |T| 分層 → ΔE=0 集中在低 |T| bin, 但控制後無顯著效應
- [x] 高緯度 4 → 3/4 (75%), 0 ΔE=0, 無統計意義
- [x] Logistic regression → β₂=0.93 [-0.51, 34.7] ❌
- [x] Cross-map (NILC/Commander) → 三地圖一致, 非 artifact
- [x] Sign matching overall → 最高 63.3% p=0.052, 唔顯著
- [x] Spearman ρ → ρ~0.24 p~0.06, 一致但唔顯著
- [x] Coloring 物理意義 → **BFS parity = bipartite 2-coloring** ✅

## 結果

見 `02_results.md` (最終報告) 和 `scripts/`。

---

## 推導時序索引

> 本索引記錄 O23 由建立至閉合嘅實際推導時序，供歷史追溯。所有數值經獨立驗證 (scripts/99_verify_all.py, 13/13 通過)。

| # | 日期 | 步驟 | 文件/腳本 | 關鍵結果 |
|:--|:--|:--|:--|:--|
| 1 | 2026-08-17 | O23 建立 (O3 衍生) | `SESSION_START.md`, `01_problem_record.md` | 問題定義: 75% vs 58% 有冇統計意義 |
| 2 | 2026-08-20 | Fisher exact + Bootstrap + Hypergeometric | `scripts/01_zeroE_sign_analysis.py` | p=0.34, P(≥75%)=0.24 → 唔顯著 |
| 3 | 2026-08-20 | \|T\| 分層 + Logistic regression | `scripts/01_zeroE_sign_analysis.py` | β₂=0.93 [-0.51, 34.7] → 無效應 |
| 4 | 2026-08-20 | 高緯度 4 節點 | `scripts/01_zeroE_sign_analysis.py` | 3/4, 0 ΔE=0 → 無意義 |
| 5 | 2026-08-20 | 延伸問題 Q1-Q7 | `scripts/02_extended_questions.py` | 整體 61.7% p=0.09, ρ=0.24 p=0.06, 全部唔顯著 |
| 6 | 2026-08-20 | Cross-map 驗證 (SMICA/NILC/Commander) | `scripts/03_cross_map_push_all.py` | r>0.995, sign 一致 >98% → 非 artifact |
| 7 | 2026-08-20 | Coloring 結構分析 | `scripts/03_cross_map_push_all.py` | **BFS parity = bipartite 2-coloring** ✅ |
| 8 | 2026-08-20 | Power analysis | `scripts/02_extended_questions.py` | detect 75% vs 58% 需 ~248 節點 |
| 9 | 2026-08-20 | 獨立驗證 (13 項檢查) | `scripts/99_verify_all.py` | **13/13 全部通過** |
| 10 | 2026-08-20 | Cross-map 提取 + NILC 差異驗證 | `scripts/99b`, `99c` | r=1.0000; node 48 近零 flip 係唯一差異 |
| 11 | 2026-08-20 | 文檔更新 + final_result.md | `01_problem_record.md`, `02_results.md`, `final_result.md` | O23 完全閉合 |

### 推導鏈

```
O3 (節點溫度) ──► O23 (ΔE=0 符號匹配率)
                    │
                    ├─► Fisher exact → p=0.34 (H1 接受)
                    ├─► Bootstrap → P=0.24
                    ├─► |T| 分層 → ΔE=0 集中低 |T|, 控制後無效應
                    ├─► Cross-map → 三地圖一致, 非 artifact
                    └─► BFS parity → coloring 係圖論性質, 唔係 temperature prediction
                         │
                         └─► 弱信號 (ρ~0.24, p~0.06) = CMB 大尺度微弱 spatial correlation (🟡 推測)
```

### 文檔完整性聲明

- 本索引為 **時序回溯記錄**, 不包含任何新推導 — 所有條目均對應已存在於 scripts/ 嘅實際計算
- 所有數值已喺新位置 (`IDCM-Original/IDCM-v10.0--It-From-Beat`) 重新執行驗證, 結果一致
- 除修復 scripts/ 內 3 個腳本嘅 BASE 路徑常數外, 冇修改任何推導邏輯
