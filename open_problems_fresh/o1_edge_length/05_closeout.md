# 05 — 新O1 階段性 Closeout（2026-10-22）

<!-- registry
pid:     O1/edge-length
title:   新O1: 邊長 26.09° — A₅ 群論精確閉合
state:   closed
verdict: closed
flags:   -
owner:   O1
created: 2026-10-22
updated: 2026-10-22
prereq:  O1
source:  scripts 01-12 + 04_audit_full
-->

## 狀態

🟢 **階段性 closeout 完成** — `closed` / verdict `closed`（register `O1/edge-length`，2026-10-22）

---

## T0 — 閉合水位（首次建立）

本 O 首次 closed-out ⟹ 全部檔案全檔驗（無水位豁免）。

| # | 檔案 | mtime | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:------|:----------------|:---------|:-----|
| 1 | `01_problem_record.md` | 2026-10-22 (本輪) | 2026-10-22 20:05 | 全文 | ✅ 已驗 |
| 2 | `02_results.md` | 2026-10-15 23:34 | 2026-10-22 | 全文 | ✅ 已驗 |
| 3 | `03_delta_closure.md` | 2026-10-15 23:34 | 2026-10-22 | 全文 | ✅ 已驗 |
| 4 | `04_audit_full.md` | 2026-10-22 (本輪) | 2026-10-22 20:05 | 全文 | ✅ 已驗 |
| 5 | `05_closeout.md` | 2026-10-22 (本檔) | — | — | ✅ 本輪產物 |
| 6 | `final_result.md` | 2026-10-22 (本輪) | 2026-10-22 | 全文 | ✅ 已驗 |
| 7 | `SESSION_START.md` | 2026-10-22 (本輪新建) | 2026-10-22 | 全文 | ✅ 已驗 |
| 8-17 | `scripts/01…10` | 2026-08-16 14:50–15:01 | 2026-10-22 | 全文+重跑 | ✅ 已驗 |
| 18 | `scripts/11_audit_fix_theta_field.py` | 2026-10-22 | 2026-10-22 | 全文+執行 | ✅ 已驗 |
| 19 | `scripts/12_audit_independent.py` | 2026-10-22 (本輪) | 2026-10-22 | 全文+執行 | ✅ 已驗 |
| 20-27 | `data/*.txt` (7 + 1 備份) | 2026-10-22 19:57–20:03 | 2026-10-22 | 內容核對 | ✅ 已驗 |

⚠️ 4 個歷史 md（02/03 及已被覆檢嘅 01/final_result 舊版）mtime 全部 2026-10-15 23:34:45 = 批次搬移產物，非逐檔寫入證據；內容與推導時序索引一致 ⟹ 判無回溯污染。

---

## T1 — 獨立重驗（`scripts/12_audit_independent.py`，**21/21 PASS**）

**獨立性措施**：零 import 原 script 01-11；由原始輸入（`cmb_cold_spot/data/a5_nodes.txt` 節點 0 + φ 幾何定義）重算；**算法層獨立** = quaternion 旋轉（原用 3×3 矩陣）＋ mpmath dps=40（原用 numpy float64）。

| 段 | 驗證 | 結果 |
|:--:|:-----|:-----|
| A | 幾何基元：20 頂點 / 12 面心 / 頂點球心角 41.8103148958° | 3/3 ✅ |
| B | δ = 15.1085157437°、δ5 = 22.6509381463° | 2/2 ✅ |
| C | θ **三條獨立路徑**：球面餘弦定律 / quaternion 120° / 代數 `cos²δ−sin²δ/2` 全部 = **26.0913571445°**，三路差 **1.1e-39°** | 4/4 ✅ |
| D | 邊長 mean 26.091345605°、min 26.0913194302°、max 26.0913823494°、60 節點全部 ≈26.09° | 5/5 ✅ |
| E | 旋轉不變性：逐節點 nn 最大差 **4.4e-39°**（真·不變量） | 2/2 ✅ |
| F | A₅ 群大小 **60**（mod ±q 雙覆蓋）、角譜命中 26.0914←120°、26.1664←72°、31.6787←180°、42.9712←144° | 5/5 ✅ |

**副產物（新資訊，非矛盾）**：群元素角距離譜完整 37 個值（26.0914 … 174.6599）。文檔只列 4–5 個（實際用嘅殼層）。
**交叉確認**：角譜含 **113.5425°** = 07 腳本 bug 寫入 data 嘅原值 ⟹ 證實「該值係群元素角，非公式值」嘅診斷正確。

### T1 過程實錄（審計員有罪推定 ×3）

首跑 15/21，4 個 FAIL 全部喺**我嘅 verifier**（文檔零錯），按 skill §10-A 逐個拆：
1. `qrot` 用 closure 捕獲全域 `qx,qy,qz`，**忽略傳入 q** ⟹ 所有群元素當同一旋轉（角譜只得一個值）
2. quaternion **SU(2)→SO(3) 雙覆蓋**：q 同 −q 同一旋轉 ⟹ 群算成 120 而非 60（需 canonical key）
3. α 計算雙重錯（`tr = 2|w|` 再 `acos(tr)`，應為 `α = 2·acos(|w|)`）
4. std 檢查**對象錯**：文檔「std=0」指「同一節點旋轉前後不變」，我誤驗「60 節點間離散度」（後者天然 2.15e-5°）
5. `acos` 浮點略超 1 返回 complex ⟹ 加 clip 保護

修完 21/21。**教訓**：驗「不變量」要 pin 清楚「邊個量對邊個量不變」。

---

## T2 — 文檔完整性 + 數值交叉核對

見 `04_audit_full.md` §5：9 條文檔數值聲稱全部對上實測，**零文檔數值錯誤**。
唯一錯誤欄位在 `data/edge_formula.txt`（07 L121 loop 變量覆蓋 bug），已由 `scripts/11` 修正並備份。

## T3 — 時序完整性

- scripts 01-10 mtime 2026-08-16 14:50:42 → 15:01:55 **逐檔遞增** = 真實推導次序
- 11/12 及本輪 md = 2026-10-22（append-only，最後加入）
- 無回溯污染；無跨文檔污染（舊 doc 保留原文，新結論只入新檔）

## T4 — 推導時序索引

`01_problem_record.md` §推導時序索引：13 行（14:50 → 15:02 原始 + 10-22 審計/修正/closeout 行）。

## T5 — final_result.md

依 `open_problems_fresh/RESULT_TEMPLATE.md`：狀態 / 結論 / 關鍵公式 / 依賴 / 審計。已加獨立驗證 21/21。

## T6 — Git 提交

見 `git log`（本輪 scoped commit：只 add 本 O 目錄檔案）。

---

## §4.9 推導落碟完整性（六項）

| # | 核對 | 結果 |
|:-:|:-----|:-----|
| ① | 腳本集對稱（磁碟 12 ↔ 時序索引 12） | ✅ 差集空 |
| ② | 逆向綁定（每個 headline 數字有 producer script） | ✅ 26.09/15.1085/θ/群元素 全部有 01/06/07/08/12 |
| ③ | 路徑衛生（`/tmp`、`/var/tmp`、`cache` 寫入模式） | ✅ **0 命中** |
| ④ | scratch 鏡射 | 審計 log 留 scratch（`o1_audit/`），關鍵結論已入 `04`/`05` |
| ⑤ | inline 推導偵測 | ✅ 全部 headline 數字有落碟 script（無幽靈推導） |
| ⑥ | driver of record | 缺 `run_chain.sh` — 🟡 記錄為後續項（非阻塞，鏈短且逐支可跑） |

## §4.10 登記面覆蓋

| 核對 | 結果 |
|:-----|:-----|
| 正向（每個結果 → register 事件） | ✅ registered + closed + note×2 |
| 新問題註冊 | ✅ `O1/edge-length`（ref 恰一條路徑） |
| 反向（register ↔ 記錄） | ✅ 無幽靈項 |
| `check` 對基線 | ✅ HARD DRIFT 52（= 開輪前）、STATUS-DRIFT 0、BLOCK-UNREGISTERED 0、本 pid 零 REF-MISSING |
| 機器塊 | ✅ 01 + SESSION_START 各一，`state=closed` 三邊一致（NO-BLOCK 646→645） |
| README | ⚠️ 未加 O1 行（README 在 O 目錄外，需明示批准才改）→ **記錄為待批項** |

---

## 殘餘項（階段性 closeout 定義）

| # | 項 | 狀態 | 說明 |
|:-:|:---|:----:|:-----|
| 1 | `run_chain.sh` driver | ✅ **已建** | §4.9⑥ 完成：`scripts/run_chain.sh`（預設 dry-run，`--execute` 真跑）；**實測 12/12 rc=0**，`logs/` 12 份正典 log；11 排喺 07 之後（07 已知 bug 需 11 修正）|
| 2 | README O1 行 | ✅ **已加** | 行 220 `\| **O1/edge-length** \|` 🟢 已閉合（含全部關鍵數值）；**第一 cell 用子 pid**（非 O1 主號）以避免與 register `O1=merged` 誤配 |
| 3 | COLLISION-STALE O1 | ✅ **已 retire** | `register.py` 新增 `collision --retire NUM`（與 `unreserve` 對稱：原 collision 事件永久保留 + 追加 `collision_resolved`，replay 時 DELETE）；rebuild 2850 events 一致；COLLISION-STALE **3 → 2** |
| 4 | `07` L121 變量覆蓋 bug | ✅ | 已修 data + 記錄；**舊 script 保留**（不回溯改，歷史完整性）|
| 5 | STATUS-DRIFT（本輪引入） | ✅ **已修** | README 行寫 `O1` 令 readme_nums 誤認 O1 主號 ⟹ `O1 register=merged README=closed`；改第一 cell 為 `O1/edge-length`（regex 不匹配）⟹ **STATUS-DRIFT 0** |

**check 對基線**：HARD DRIFT **52 → 49**（改善 3：COLLISION-STALE −1、BLOCK-DRIFT −2）；STATUS-DRIFT **0**；本 pid 零 drift。

**階段性 closeout 判定**：核心結論（θ 閉合 0.000011°）**三重獨立驗證全綠**（原鏈 8/8 + 全量重跑 10/10 + 獨立 verifier 21/21）；文檔零數值錯；登記面完整；**殘餘 5 項全部完成/關閉，零結構性缺口**。
