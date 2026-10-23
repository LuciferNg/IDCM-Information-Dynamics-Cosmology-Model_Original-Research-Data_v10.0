# O228 closeout-2 獨立審計報告（R1–R14 全鏈；2026-10-02）

- 審計腳本 `scripts/27_closeout2_audit.py`；輸出 `logs/27_closeout2_audit.out`；機讀 `data/27_closeout2_audit.json`
- **判定：24/24 PASS，0 FAIL，0 N/A**（零新參數、零擬合；整數／bitmask 精確；浮點只作百分比顯示）
- 上游唯讀：o222 四釘檔 sha256 與 closeout-1 記錄一致（4/4）；本輪審計期間 o222 新檔 = 0

## 1 重算對照（全部獨立、非引用）

| 項 | 獨立結果 | 對應原記錄 |
|:--|:--|:--|
| M_edge 形狀 | 30 行 × 62 欄，435 行對 | R1/R6 |
| 8584 幀 | 8584 條、兩兩相異、每幀覆蓋 435 對、每幀極小 | R11/R13 |
| S 覆蓋 | union_{a in S} cme[a] = ALLP（435/435 bits） | R14 主定理前提 |
| C∩S 分佈 | {0:3569, 1:2569, 2:1384, 3:703, 4:271, 5:68, 6:18, 7:2} | R14 |
| M_all | **= 1 EXACT**（LB max|C∩S| ≤ 10；UB mu_S = 1） | R14 P13-3 |
| 8-集伴隨計數 | 472,120 = 8584×55；含 ≥2 幀 25,578；含 ≥1 幀 **446,542** | R14 P13-7c |
| A8 | p_hat·C(62,8) = 13/12500 × 3,381,098,545 = **3.5163e6** | R14（±5σ 帶） |
| F'_8 | 3.5163e6 − 446,542 = **3.0698e6 = 357.6 × 8584** | R14 |

## 2 本輪審計發現並修正之記錄問題

| # | 問題 | 處置 |
|:-:|:--|:--|
| ① | **BLOCK-DRIFT**：`01_problem_record.md` 塊 `state: registered / verdict: -` vs register `partial` | 改塊 `state: partial, verdict: partial, updated: 2026-10-02` ＋ 人手狀態行；`check`：O228 行清零（HARD DRIFT 32→31，BLOCK-DRIFT 23→22） |
| ② | **R1–R5 只發 `progress`，無 `close` 事件**（state 停留 registered） | 補發 `close`（verdict 沿用當時記錄：R1/R2/R4 = closed、R3/R5 = partial；判定不變），註明 backfill |
| ③ | `SESSION_START.md` 人手狀態行仍「已註冊（未開始）」 | 改 🟡 partial（R1–R14）｜更新 2026-10-02（內容不動） |
| ④ | **事故（誠實披露）**：審計首版 import `scripts/25_r13_separation.py` 觸發其模組級 main ⟹ R13 重跑 24.1 s 並**覆寫** `data/25_r13_separation.json` | 即 `git checkout --` 還原；現檔 sha256 **≡ MANIFEST 原值** ✓；改用 import `scripts/04/09/10`（皆有 `__main__` 守衛）重建機器；此後 R13/R14 凍結產物零觸碰 |
| ⑤ | backfill 之 ref 目標 `docs/00_closeout_audit.md` 首跑不存在 ⟹ 5 條 REF-MISSING | 本檔即該目標 ⟹ 已清零（`check` 無 O228 行 ✓） |

## 3 移交（非本 O，就地不改）
- 全域 **BLOCK-DRIFT 22**：o225、o227、o231×2、v11 M1/M2/M3 等（屬主各 O）。
- 全域 **REF-MISSING 5**：非 O228（O137/O206 超前類等）。
- 依 `register-drift` 鐵律 5：他人 pid 只記錄移交，唔就地改。

## 4 殘餘（保持 partial；不阻 closeout）
R14 §3 五項：① size ≥ 8 極小覆蓋精確計數（瓶頸 = A8 精確值）② 8584 幀於 |GeoAut|=60 之軌道分解 ③ CG 秩 ≥ 2 ④ T|(1,1,2) 之 LP 不緊 ⑤ 幀側零冗餘 vs 生成側 58/62。
α 必要性攻堅已按用戶指示交 **O218**（register handoff 2026-10-02）；O228 不處理。
