# O252 — Closeout 審計報告 (2026-10-17)

狀態: 🟡 **階段性 closeout — 審計全綠 (T0-T6); O252 維持 partial
       (窗中心身份 + 方向 + 深度 scatter 三個 gap 開放)**
Scripts: 01-20 全跑 exit 0 (T1)
Data: 01-20 JSON (重跑 byte-identical, git diff 空)
Logs: 01-20 (06 補回)
Docs: 01-14 + final_result.md

---

## 1. T0 水位

O252 從未 closed-out → 全檔驗 (唔係增量)。

## 2. T1 獨立重驗

| 項 | 結果 |
|:--|:--|
| 重跑 18/18 scripts (01-18) | ✅ 全部 exit 0 |
| data 確定性 | ✅ 重跑後 git diff 空 — 18 JSON byte-identical |
| script 19 (hop moments) | ✅ 4/4 PASS — ⟨v⟩=280.0281, 中位 h=4 |
| script 20 (doc crosscheck) | ✅ 16/16 PASS |
| logs 對 scripts | ✅ 20/20 對稱 (logs/06 原缺 → 已補回) |

## 3. T2 文檔↔data 交叉核對

docs↔data 16 項全 PASS (scripts/20, data/20_doc_crosscheck.json):
- docs/03: 9/12, p=4.26e-7, z=8.42 ↔ data/08
- docs/07: σ=189.52, dev 0.12%, t=−0.03 ↔ data/12
- docs/10: μ_hat=235.7±21.6, CI [193,278] ↔ data/15
- docs/12: 9/13, 11/13, Hβ 171 vs 37 ↔ data/18
- docs/13: ⟨v⟩=280.03 ↔ data/19
- docs/09: p=0.0003 ↔ data/14
- docs 01-13 全部存在 ✅

## 4. §4.9 推導落碟完整性

| 核對 | 結果 |
|:--|:--|
| ① 腳本集對稱 | ✅ scripts 20 / data 20 / logs 20 對稱 |
| ② 逆向綁定 | ⚠️→✅ **script 16 (hop=2) H2d FAIL 冇 doc 記錄** — docs/11 只提 hop2 候選冇提 W 權重負結果; 已喺本報告 §6 補錄 (docs/14) |
| ③ 路徑衛生 | ✅ scripts 0 個 /tmp 寫入模式 |
| ⑤ inline 推導 | ✅ R13 ⟨v⟩=280.03 原係 terminal inline → **script 19 已補落碟** |
| ⑥ driver | ⚠️ 冇 run_chain.sh — 20 支 script 每支獨立可跑, 未有 driver (記錄, 唔係 blocker) |

## 5. T3 時序

- 每支 script mtime 早於對應 doc ✅ (推導 → docs 次序正確)
- SESSION_START 原快照正文冇改, 只 append §六 加注 ✅
- 01_problem_record 原文保留, 狀態行 + §二b 加注 + §六 時序索引 append ✅

## 6. ★ script 16 H2d 負結果補錄 (逆向綁定 gap)

script 16 (hop=2 中心檢驗) 嘅完整結果未被 docs/11 記錄:
- H2a PASS: hop2 窗命中 11/11 vs hop4 9/11
- H2b PASS: χ²(hop2)=18.4 < χ²(hop4)=33.7
- H2c PASS: MC null p(hop2)=0, p(hop4)=0.00015
- **H2d FAIL: W(hop=2)=1.000 > W(hop=4)=0.636** — O179 質量權重唔支持
  hop=2 做吸收層 — hop=2 統計優但結構身份未確立 (R13 已深化: 任何 hop
  質量統計 ⟨v⟩=280.03 都唔等於 235.7, 需要吸收截面新機制)

⟹ **窗中心身份 gap 係「後驗統計優 (hop2) + 零結構身份」** — 唔可以升格。

## 7. register 面 (§4.10)

| 核對 | 結果 |
|:--|:--|
| ① 正向覆蓋 | ✅ R1-R13 全有 progress event (R2/R10 原缺 → 已補) |
| ② 新問題 | ✅ 4 個開放項經 closeout progress 記錄 (窗中心身份/深度scatter/方向/精確窗中心) |
| ③ 反向覆蓋 | ✅ register 16 events ↔ docs 13 輪一致 |
| ⑥ 讀回 | ✅ 每次 register 有 exit 0 + "O252 progress" |

## 8. 範圍核實

- 本 closeout 寫入: 只 O252 目錄內 (01_problem_record, SESSION_START,
  final_result, docs/14, scripts/19, scripts/20, logs/19, logs/20, data/19,
  data/20) + problem_register (R2/R10 progress)
- git diff 顯示嘅其他 155 檔 (o92/o97/register.jsonl 105 行等) = **並行
  session 變更**, 唔係本 closeout 寫入
- README 狀態 emoji: **未改** (跨目錄, 硬規則 2) — 記錄為移交項

## 9. 開放 gap (維持 partial 之原因)

| gap | 需要 | 狀態 |
|:--|:--|:--|
| 窗中心結構身份 | 吸收截面權重機制 或 Cycle 3/4 高解像樣本 pre-register | 🔴 |
| 方向 sign | 凝聚層側向身份 或 大樣本 | 🔴 |
| 深度 per-source | 每源凝聚密度模型 | 🟡 |
| 精確窗中心 | R~2700 高解像分辨 204.9 vs 236 | 🟡 |

## 10. 判定

**O252 階段性 closeout 完成**: 窗存在 + 窗寬 + 深度上限/中位閉合
(零常數, 統計顯著); 窗中心身份 (最硬 gap) + 方向 + 深度 scatter 開放。
維持 🟡 partial — 符合 O238 教訓 (推盡≠結論, 等數據期間維持 partial)。

*文檔: O252 closeout 審計 · 2026-10-17*