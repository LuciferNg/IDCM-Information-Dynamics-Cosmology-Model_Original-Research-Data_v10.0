# O5: 冷斑 Catalogue 對比 — WMAP/Planck 冷斑目錄 vs A₅ 節點

> 狀態: ✅ **已完成 (2026-08-17)** — 結果見 NN_results.md

## 問題陳述

IDCM 預測 60 個 A₅ 節點係「拓撲縫合節點」— 應該全部有溫度異常 (冷或熱)。已驗證大冷斑 (209°,-57°) = 節點 0。但其他節點有冇對應已知冷斑目錄?

**O5 目標: 對比公開冷斑/熱斑目錄 (WMAP, Planck, 文獻) vs 60 節點位置, 計算命中率!**

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| 60 節點 | a5_nodes.txt (ICRS) | 08_a5_group_nodes.py |
| 大冷斑 | (209°,-57°) = 節點 0 | 官方確認 |
| SMICA 冷斑 | -134.2 μK | 22_smica_smoothed.py |
| 節點 47 (次冷) | -123.4 μK | 26_anchor_control.py |
| 節點 57 (對徑) | +8.2 μK | 同上 |

## 目錄候選（最終核實結果）

| # | 目錄 | 描述 | 來源 | 核實 |
|:-:|:-----|:-----|:-----|:-----|
| 1 | Vielva 2004 | WMAP 冷斑 (SMHW 方法) | astro-ph/0310273 | ✅ 大冷斑 (209,-57) |
| 2 | Cruz et al. 2005 | WMAP cold spots catalogue | astro-ph/**0405341** | ✅ 大冷斑 + Table 4 子斑；**無 10+ 目錄** |
| 3 | Planck 2013 | CMB 各向異性異常 | 1303.5083 | ✅ 大冷斑 + **gp10 冷斑 (32°,-8°)** |
| 4 | Gurzadyan 2007/2014 | 冷斑統計 | 1404.6347 | ✅ 同一大冷斑 |
| 5 | 文獻熱斑 | WMAP 最大熱斑 | Planck 2013/2015 | ✅ 熱斑區域，無座標目錄 |
| 6 | Planck 2015 XVI | 冷斑統計 | 1506.07135 | ✅ 大冷斑；無目錄表 |

⚠️ **SESSION_START 錯誤**: astro-ph/0505341 係 Saviane et al. dwarf galaxy 論文，唔係 Cruz 冷斑論文！正確 ID = astro-ph/0405341。

## 結果總結

| 量 | 值 | 判定 |
|:---|:---|:-----|
| 文獻確認冷斑命中 | 1/2 (大冷斑) | 🟢 |
| SMICA 冷斑命中 (5.0°) | 1/15 | 🔴 冇額外 |
| SMICA 熱斑命中 (5.0°) | 2/14 | 🔴 冇額外 |
| 交叉尺度一致命中 | **只有節點 0** | 🟢 |
| 全部 35 mean-nearest p | **0.042** | 🟢 弱 |
| 全部 35 hits p | 0.113 | 🟡 |
| 減冷斑後 mean-nearest p | 0.072 | 🟡 唔再顯著 |
| 熱斑 F₆/F₇ 距節點 | 8-9° | 🔴 唔喺節點 |

**最終結論**: 節點 0 (大冷斑) 係唯一跨尺度確認命中；其他 59 節點冇對應目錄冷斑/熱斑。文獻「10+ 冷斑目錄」係誤記。

## 檔案

```
scripts/01_fetch_catalogs.py   # 文獻目錄 (已完成)
scripts/02_smica_catalog.py    # SMICA flood-fill 目錄 (已完成)
scripts/03_match_nodes.py      # 位置對比 (已完成)
scripts/04_significance.py     # 1000 次旋轉顯著性 (已完成)
scripts/05_scale_check.py      # 尺度匹配 (已完成)
scripts/06_cross_scale_match.py # 交叉尺度 (已完成)
scripts/07_verify.py           # 雙重驗證 12/12 ✅ (已完成)
data/literature_catalog.json
data/smica_catalog.json
data/match_results.json
data/cross_scale_match.json
data/catalogs/                 # 論文 PDF + txt
NN_results.md                  # 完整結果
```

## 後續

1. 節點 9 (1.0° 冷斑唯一額外命中) — 檢查 BFS 等級
2. 熱斑幾何歸屬 (F₆/F₇ 唔喺節點上)
3. 潛伏冷斑假說 — O3 節點溫度堆疊分析

---

## 附錄 A: 推導時序索引（導航索引，非推導內容 — 2026-09-11 建立）

> 本附錄為導航索引，用嚟串起 O5 全部推導歷史，唔代表新推導，
> 亦唔修改正文嘅創建時刻認知。建立日期：2026-09-11（獨立審計 session）。

| 日期 | 事件 | 檔案/腳本 |
|:-----|:-----|:----------|
| 2026-08-16 | O5 開題：SESSION_START 起稿，載入 skills | SESSION_START.md |
| 2026-08-17 03:52 | 文獻目錄下載/提取（7 篇論文）+ Cruz 2005 正確 ID 確認 (astro-ph/0405341) | scripts/01_fetch_catalogs.py · data/literature_catalog.json · data/catalogs/ |
| 2026-08-17 04:18-04:27 | 匹配 + 顯著性 + 雙重驗證 scripts 初版 | scripts/03_match_nodes.py · 04_significance.py · 07_verify.py |
| 2026-08-17 04:28 | 問題記錄建立（含目錄候選核實表 + SESSION_START 錯誤標註） | 01_problem_record.md |
| 2026-08-17 10:59-11:03 | 節點 9 深挖（多尺度/環空/三地圖）+ 完整結果文檔 | scripts/11_node9_crossmap.py · NODE9_ANALYSIS.md · NN_results.md |
| 2026-08-17 11:33-12:18 | 完整重跑（raw 重平滑，無 cache；06 OOM×2 → foreground int64 成功） | scripts/master_full_rerun.sh · FULL_RERUN_LOG.md |
| 2026-08-17 12:13-12:17 | cache 檔名統一修正 (5.0 vs 5) + CACHE_DIR/import 修正 | scripts/02/05/06/08/09/10 |
| 2026-08-17 12:34 | File Simulation Verifier 37/37 + README/VERIFIER_RESULT | scripts/12_file_verify.py · VERIFIER_RESULT.md · README.md |
| 2026-08-17 13:03 | 開放問題現狀核查 script | scripts/13_open_issues.py |
| 2026-08-22 | O5 開放問題 inventory 最終更新（O27/O28/O29/O52 全部閉合） | O5_OPEN_ISSUES.md |
| 2026-09-11 | 獨立審計：全套 scripts 重跑（02-13 全 exit=0）+ 文檔獨立核對 + 本附錄 | scripts/14_audit_independent.py · data/audit_rerun_20260911.log · data/audit_independent_20260911.log · AUDIT_20260911.md · final_result.md |

**時序完整性聲明**：以上 mtime 序列單調遞增（08-16 → 08-22 → 09-11），
正文保持創建時刻認知原貌；2026-09-11 審計發現全部寫入新 dated 文檔
（AUDIT_20260911.md），冇回溯污染任何舊文檔。

## 附錄 B: 原文數值發現記錄表（2026-09-11 審計）

> 以下為審計時發現嘅原文引述值，按 O49 慣例唔修改原文，
> 只喺此表標註出處、現值、說明。

| 原文位置 | 原文值 | 本 O 標準值 | 說明 |
|:---------|:-------|:------------|:-----|
| 正文「已知事實」節點 47 | -123.4 μK（出自 26_anchor_control.py） | 3.0° = -135.7 μK | 唔同來源/尺度嘅歷史引述；O5 重跑後標準值 = NODE9_ANALYSIS + O5_OPEN_ISSUES 一致嘅 -135.7 μK（13_open_issues 重跑確認） |
| 正文「已知事實」節點 57（對徑） | +8.2 μK（出自 26_anchor_control.py） | 4.0° = +8.4 μK；3.0° = +4.8 μK | +8.2 最接近 4.0° 尺度值；「對徑」定義正確 — 距節點 0 = 174.66°（SESSION_START 一致） |
| SESSION_START「Cruz 2005 (astro-ph/0505341)」 | 錯 ID | astro-ph/0405341 | 正文已於 2026-08-17 標註此錯誤（0505341 = Saviane dwarf galaxy 論文） |


