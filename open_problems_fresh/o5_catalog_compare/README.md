# O5 — 冷斑 Catalogue 對比

## 狀態: 完成 (2026-08-17)

**問題**: 除咗大冷斑 (節點 0)，其他 59 個 A₅ 節點有冇對應公開冷斑/熱斑目錄？

**答案**: 只有節點 0 跨尺度一致命中。其他節點冇對應目錄冷斑/熱斑 (命中率同隨機冇分別)。

## 關鍵發現

1. 📝 文獻無「10+ 冷斑目錄」— Cruz 2005 (astro-ph/0405341) 只確認大冷斑
2. 🟢 節點 0 = 大冷斑，距離 0.00°，三尺度 (1.0°/3.0°/5.0°) 一致命中
3. 🔴 SMICA 自建目錄 15 冷 + 14 熱，只有 1 冷 + 2 熱命中 (隨機水平)
4. 🟡 全局 mean-nearest p=0.042 弱信號，主要由大冷斑驅動
5. 🔴 熱斑 F₆/F₇ 距離節點 8-9°，唔喺節點上

## 快速開始

```bash
# 完整 pipeline
python3 scripts/01_fetch_catalogs.py     # 文獻目錄
python3 scripts/02_smica_catalog.py      # SMICA 5.0° 目錄
python3 scripts/03_match_nodes.py        # 位置對比
python3 scripts/04_significance.py       # 顯著性
python3 scripts/05_scale_check.py        # 尺度匹配
python3 scripts/06_cross_scale_match.py  # 交叉尺度
python3 scripts/07_verify.py             # 雙重驗證
python3 scripts/08_node9_deepdive.py     # node9 多尺度
python3 scripts/09_node9_null.py         # node9 環空檢驗
python3 scripts/10_node9_hop.py          # node9 hop 統計
python3 scripts/11_node9_crossmap.py     # node9 三地圖
python3 scripts/12_file_verify.py        # FILE SIMULATION VERIFIER (37/37 ✅)
```

詳細結果: [NN_results.md](NN_results.md) · [NODE9_ANALYSIS.md](NODE9_ANALYSIS.md) · [FULL_RERUN_LOG.md](FULL_RERUN_LOG.md) · [VERIFIER_RESULT.md](VERIFIER_RESULT.md) · 問題記錄: [01_problem_record.md](01_problem_record.md)

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 標準檔 | — |
| `SESSION_START.md` | 標準檔 | — |
| `final_result.md` | 標準檔 | — |
| `scripts/` | 16 個腳本 | — |
