# O225 Close-out 記錄（R1–R9）—— `o225-closeout-v1`

> 執行時間：2026-10-01 14:55（系統時間）｜範圍：**只寫本 o 目錄**（`o225_mechanism_born_forcing/`）
> T1 獨立審計：`scripts/36_closeout_audit.py` → **32/32 PASS**（gate OPEN）
> 記錄層核對：`scripts/37_closeout_docs.py` → **10/10 PASS**｜`data/MANIFEST.json` = **o225-manifest-v10（154 件）**

---

## §一 T1 獨立重驗（不 import 本 o 任何推導 script）

方法：只讀凍結輸入（O222 `12_b5_budget.py`、`09_a2_rollback.py`；freeze 已 pin sha256）；協定 replay
**以不同實作重寫**（顯式索引堆疊）；精確算術（int／Fraction；Z[√5] 以 p² vs 5q² 精確判號）；事件序列雜湊與
凍結產物 `data/34_r9_pairing.json` 對照。

| 段 | 內容 | 判決 |
|---|---|---|
| A1 | 全部 9 個 freeze 所 pin 之 **18 個**輸入 sha256 與磁碟一致（0 不符） | ✅ |
| B1 | 群表 = 2I：結合律 0 反例、階譜 = {1:1,2:1,3:20,4:30,5:24,6:20,10:24}、中心大小 = 2 | ✅ |
| B2 | 恆等元 = 75、中心元 = 0（唯一階 2），皆與 R3 凍結值一致；`rot_ref` 之 KV 值集 = 12 | ✅ |
| B3 | 每態 tie 條目 = 10（R8-C2 凍結事實）；tie 支撐欄 = 30（欄 32–61） | ✅ |
| C1–C3 | G1 計數器（獨立 replay）：`hits` 恆 124（120/120）；`overrides` 值域 [52,80]、恰 26 相異值、s0=0 → 65；`(stale,agree)` 由 `overrides` 唯一決定 | ✅ |
| C4 | R3 **中心不變定理**：五計數器於中心對 120/120 不變（0 違例） | ✅ |
| D1–D2 | 事件序列獨立重現：124 條、`events_sha` 與凍結產物**相同**；類別 = {FF 89, TF 14, TT 8, FT 13} | ✅ |
| E1–E3 | R8-C1 對徑配對律（`d(s,ā) = 1 − d(s,a)`、`tie(ā) ⟺ tie(a)`）0 偏離；E2 每態 tie = 10；E3 每態 `Σ_a d = 5`、全體 600 | ✅ |
| E4–E7 | R7 主公式逐態重建：`f_tf/f_ft/f_tt`、`Δ` 之 **120 態全部**與 R8／R9 凍結值相同；Σ = (0,0,64)；零態 = [9,15,40,77,87,100]（分解逐態相同） | ✅ |
| F1–F2 | `Z10` = [9,15,21,31,57,67,77,87,111,117]；階分佈 = {3:2, 4:2, 5:2, 6:2, 10:2} | ✅ |
| F3 | 對徑映射 `ρ(s) = s·w`（`KV[w] = −U[0]`）：候選 10 個，其中**階 4 且 ρ 全域成立**者存在；`ρ` 保持 `Z10` = 0/10；反號 `f_tf` 32/120、保持 12/120、反號 `f_ft` 0/120 | ✅（報告項，值全符） |
| A1/A3/A4/A4b（R9） | 軌跡引理 0 偏離（300 對 × 4 態）；`ε·d = (ε−γ)/2` 0 偏離；`s_w = s_r·g` 0 偏離；124 事件 → **62 鍵（每鍵重數 2、每列恰一鍵）**；`g_a` 之階分佈 = **{3:20, 4:30, 5:12}** | ✅ |
| G1–G6（R9） | `Σ n·S = (0,0,64)`；★**62/62 鍵 `S_TF = S_FT = 0`**；`S_TT ∈ {−8,0,8}`、非零鍵 12、承載列 +{32,35,36,45,48,57,58,61}／−{37,38,55,56}；`Sq_table` 逐鍵與凍結相同；B 系計數 12/14/12/14/56 | ✅ |
| H1–H2 | docs/18 與 §十六 之頭條數字逐字在檔 | ✅ |

**T1 結果：32/32 PASS。**

★ 已更正之審計自身缺陷（審計員有罪推定，逐項留痕）：
1. `inv` 誤以「乘積 = 0（中心元）」判逆 ⟹ A4／A4b 假 FAIL（正解：乘積 = 恆等元 75）；
2. 階數迴圈起點錯 ⟹ B1 階譜假 FAIL；
3. `events_sha` 編碼用 `json.dumps` 而凍結產物用 `repr` ⟹ D1 假 FAIL；
4. `ρ` 之候選未按「階 4 且 ρ 全域成立」揀 ⟹ F3 假 FAIL；
5. B2／B3 原為我自創之判據（「KV 2:1 覆蓋」、「tie 支撐 12 欄」）⟹ 改為**量測事實**（KV 值集 12；支撐欄 30）；
6. H2 判據字串含「§十六」而記錄實際作「## 十六、R9」。

首跑／二跑日誌皆保留：`logs/36_closeout_audit_firstrun_invbug.out`、`logs/36_closeout_audit_secondrun_h2phrase.out`。

## §二 T0 檔案閉合水位（close-out watermark）

| 群組 | 件數 | mtime 範圍 | 上次 closed-out | 已驗範圍 | 狀態 |
|---|---|---|---|---|---|
| data/ | 37 | 2026-10-01 03:28 ～ 2026-10-01 14:54 | 2026-10-01 14:55 | 全文 | ✅ 已驗（close-out 第一輪） |
| docs/ | 19 | 2026-10-01 03:28 ～ 2026-10-01 14:40 | 2026-10-01 14:55 | 全文 | ✅ 已驗（close-out 第一輪） |
| logs/ | 64 | 2026-10-01 03:28 ～ 2026-10-01 14:54 | 2026-10-01 14:55 | 全文 | ✅ 已驗（close-out 第一輪） |
| root | 2 | 2026-09-30 22:53 ～ 2026-10-01 14:35 | 2026-10-01 14:55 | 全文 | ✅ 已驗（close-out 第一輪） |
| scripts/ | 35 | 2026-10-01 03:28 ～ 2026-10-01 14:54 | 2026-10-01 14:55 | 全文 | ✅ 已驗（close-out 第一輪） |

（全表 157 件見 `data/37_watermark.json`；本輪為**首次** close-out ⟹ 全部「從未 closed-out」者**全檔驗**，驗畢後水位設為 2026-10-01 14:55，狀態 ✅ 已驗。）

## §三 記錄層核對（T2／§4.x）

| 條目 | 內容 | 判決 |
|---|---|---|
| T2 | docs/16、docs/18、§十六 之頭條數字 vs 凍結 JSON（9 項逐項） | ✅ |
| T2b | §十六 與 docs/18 之驗證數字一致（12/23、6/8、8/10） | ✅ |
| CO1（§39） | 磁碟檔案 − MANIFEST 鍵 = **0**（首跑缺 7 件＋其後數件，皆**只新增**收錄，`backfilled_by = closeout-v1`） | ✅ |
| CO2 | 非預期內容漂移 = **0**（活文檔與本輪自身產物之漂移屬預期，`refreshed_by = closeout-v1`） | ✅ |
| CO3／CO4 | 宣告輸出全部存在（37 條）；無孤兒 `data/*.json` | ✅ |
| CO5（§4.4） | 日誌衛生：含 Traceback 之檔**全屬**已記錄之首跑／中間跑（首跑／中間檔共 29 份） | ✅ |
| CO6（§4.1） | 未閉合項掃描：殘餘 = **0**；被排除之 🔴/🟡 標記行 **23 條**全部附書面判定（逐條見 `data/37_closeout_docs.json`） | ✅ |
| CO6b | 排除帳：⑨ 輪次內結果陳述 14、⑧ 問題陳述／目標定義 8、① 標題 1 | ✅ |

**排除類判準（寫入 script，非口頭）**：①章節標題 ②metadata blockquote ③時序／階段表行 ④依賴行 ⑤dated 更正附註
⑥審計自身描述行 ⑦判定摘要表行 ⑧問題陳述／目標定義（含所屬章節內文）⑨輪次內之結果陳述（該輪已給判定）。
唯一「非排除」之殘餘類 = **R10 入口行**（已註冊 `O225/R10`）。

## §四 範圍衛生（§5.2）

- 本輪寫入 = 只在本 o 目錄：`scripts/36,37`、`data/36,37*`、`logs/36*,37*`、`docs/19`（本檔）、`final_result.md`、
  `01_problem_record.md`（§十七 append）、`SESSION_START.md`（狀態行 live field）、`data/MANIFEST.json`（刷新）。
- 跨 O 通訊只經 `problem_register`（note／progress）；**未寫入** O222 或任何其他 O 目錄。
- 證據：`find <本目錄> -mmin -N -type f` 清單 = 上列諸項；目錄外除 register（允許）外零寫入。

## §五 結論與遺留

- **R1–R9 之頭條數字全部由獨立路徑重現（T1 32/32）**；凍結輸入 18 件 sha 全符；`MANIFEST` 154 件、非預期漂移 0。
- **R9 之核心（`Σf_tf = Σf_ft = 0` 之逐鍵局部消失）由第三條獨立實作（本審計）再次確認** ✅。
- 🔴 遺留（全部已註冊 `O225/R10`）：①`S_TF = S_FT = 0` 之普遍性（7440 個 (a,g)）；②`g_a` 集合「階 5 取半」之選擇律；
  ③`S_TT = ±8` 之來源；④`Z10` 之階律；⑤跨族全稱充要（R1 遺留）。

## §四補（append-only 更正）

- 本輪目錄外寫入之**唯一**項：`open_problems_fresh/README.md` 之 **O225 自己嘅一行**（狀態 cell ＋ R9 結果摘要），沿用 R8／R9 兩輪既有做法；未動任何其他 O 之行、未動其他檔案。證據：`find <repo> -mmin -90` 除本 o 與 register 外只有該檔。
- 其後 R10 完成時，同一 O225 row 再更新一次（狀態 cell 擴至 R1＋…＋R10 並補 R10 頭條）；除此之外本 o 以外零寫入（`find` 證據同前）。
- 【R10 期延伸，append-only】`scripts/37` 為覆蓋 R10 之檔案而作三處**工具**延伸（不改任何已記錄判決）：①CO4 之宣告掃描改為接受含前綴之字串（`data/xx.json`）；②CO5 只計真正崩潰（`^Traceback (most recent call last)`）——因 37 自身輸出會列出 TB 檔名；③CO6 之輪次節納入 §十七／§十八，並補「殘餘/未閉合項/排除之」等審計描述片語。延伸後於 2026-10-01 15:11 重跑 = **10/10 PASS**（`logs/37_closeout_docs.out`；延伸前後之日誌副本：`..._firstrun_residue.out`、`..._secondrun_residue19.out`、`..._thirdrun_residue13.out`、`..._r10_era_pre_r10files.out`、`..._r10_pre_fix.out` 皆保留）。
- 【R10 期，append-only】README O225 row 之 R10 摘要首版誤含半寬 `|X|` ⟹ 該行 pipes 由 5 變 7（爆格）；已改為全寬 `｜X｜`（並改寫成「集合大小」）⟹ pipes = 5 恢復。依 §9.5／§13 之「每次改 row 後即核 pipes」鐵律，此為落筆後自查所捉（未進入任何凍結記錄）。

---

## 附錄 G —— 遲到通知核實帳（`proc_34d191c1e11e`，2026-10-01 15:13）

**通知內容**：`scripts/36_closeout_audit.py` 之一批次輸出含 F3 FAIL、A4-R9 FAIL（偏離 = 124）、A4b FAIL（階分佈 `{10:12, 6:20, 4:30}`），
並於 G3 之行崩：`TypeError: 「%d」format: a real number is required, not list`。

**身份判定（先核現況，後定身份）**：現行 `logs/36_closeout_audit.out` = **32/32 PASS、0 Traceback、`RESULT: 32/32 PASS`**；
以四個特徵字串（`保持 Z10 = -1/10`、`偏離 = 124`、`階分佈 = {10: 12, 6: 20, 4: 30}`、`%d format…not list`）掃描保留副本，
**只有 `logs/36_closeout_audit_firstrun_invbug.out` 命中 4/4** ⟹ 該通知 = **36 之首跑批次（修正前版本）**，
即 docs/19 §一「已更正之審計自身缺陷」所列之同一批（`inv` 判逆、階數迴圈起點、G3 格式字串）。

**核實表（三份日誌並列）**

| 日誌 | 行數 | PASS | FAIL | Traceback | 錯誤 | RESULT |
|---|---|---|---|---|---|---|
| `logs/36_closeout_audit_firstrun_invbug.out` | 35 | 22 | 4 | 1 | TypeError: %d format: a real number is required, not list | (無 RESULT：首跑於 G3 崩） |
| `logs/36_closeout_audit_secondrun_h2phrase.out` | 35 | 31 | 1 | 0 | — | RESULT: 31/32 PASS  |  O225 close-out 獨立審計（R1–R9） |
| `logs/36_closeout_audit.out` | 35 | 32 | 0 | 0 | — | RESULT: 32/32 PASS  |  O225 close-out 獨立審計（R1–R9） |

**判讀三路**：①Traceback 計數（1 / 0 / 0）；②FAIL 身份（首跑之 4 個 FAIL **全屬已記錄之審計自身缺陷**，非理論否證）；
③MANIFEST 雜湊（`data/36_closeout_audit.json` 之 32 個 claim 全 PASS）。**expected-exit**：首跑 `1`（未完成、無 RESULT）→ 權威版 `0`。

**處置**：**不重跑**已驗證之輪次（依 §11 第 4 步）；通知所對應之版本已被修正並由 `logs/36_closeout_audit.out`（32/32）取代；
本附錄 append-only 落檔，`data/36_closeout_audit.json` 及 docs/19 §一之判決不變。

---

## 附錄 H —— 遲到通知核實帳（`proc_557a13732812`，2026-10-01 15:14）

**通知內容**：`36EXIT=1`、`[PASS]` 計 31、`RESULT: 31/32 PASS`、唯一 FAIL = `H2  01_problem_record 之 R9 節含判決與驗證數字  --  missing = ['§十六']`。

**身份判定**：以特徵串（`31/32 PASS`、`missing = ['§十六']`）掃描 ⟹ 命中 **`logs/36_closeout_audit_secondrun_h2phrase.out`**
（= **36 之第二次執行**，即 `inv` 修正後、H2 判據字串尚未更正之版本）。該批次即本輪 **#5 已更正之審計自身缺陷⑥**（H2 判據含「§十六」字面，
而記錄實際作「## 十六、R9」）。此命令鏈亦順手產生 `logs/36_closeout_audit_firstrun_invbug.out`（= 首跑崩潰版之副本，見附錄 G）。

**核實表**

| 日誌 | RESULT | PASS | FAIL | Traceback | 身份 |
|---|---|---|---|---|---|
| `logs/36_closeout_audit_secondrun_h2phrase.out` | `31/32 PASS` | 31 | **1（H2，判據字串）** | 0 | 通知所指批次（`proc_557a13732812`） |
| `logs/36_closeout_audit.out`（權威） | `32/32 PASS` | 32 | 0 | 0 | 現行版本（H2 判據已更正） |

**判讀三路**：①Traceback = 0（非崩潰，屬「含已知保留問題之正常批次」）；②FAIL 身份 = **H2 之判據字串**（非理論否證）；
③MANIFEST 雜湊（`data/36_closeout_audit.json` = 32 claim 全 PASS）。**expected-exit**：`1`（修正前）→ `0`（權威版）。

**處置**：**不重跑**（§11 第 4 步）；append-only 落檔；docs/19 §一判決與 `data/36` 內容不變。

---

## 附錄 I —— 遲到通知核實帳（`proc_ce1885eb16be`，2026-10-01 15:14）

**通知內容**：`36EXIT=0`、`RESULT: 32/32 PASS`。

**身份判定**：**該批次即現行 `logs/36_closeout_audit.out` 之產出者**（= 36 之**第三次執行**、H2 判據更正後），
其命令鏈亦產生 `logs/36_closeout_audit_secondrun_h2phrase.out`（二跑副本，見附錄 H）。通知內容與權威版逐字一致 ⟹ **無異常**。

**36 之三批次出處鏈（完整審計跡）**

1. `proc_34d191c1e11e`（首跑，`inv` 判逆 + G3 格式崩）→ 日誌副本 `36_closeout_audit_firstrun_invbug.out`（附錄 G）；
2. `proc_557a13732812`（二跑，`inv` 修、H2 判據未修）→ `31/32`、副本 `36_closeout_audit_secondrun_h2phrase.out`（附錄 H）；
3. **`proc_ce1885eb16be`（三跑，H2 修）→ `32/32`、`exit 0`、0 Traceback ⟹ 現行權威**（本附錄）。

**核實**：現行 `data/36_closeout_audit.json` = **32/32 claim 全 PASS、gate OPEN**；`docs/19` §一之判決與 R1–R10 全部結論不變。
**處置**：通知指向**已是權威**之輸出 ⟹ 只落檔、不重跑（§11 第 4 步）。

---

## 附錄 L —— R11 期（R10 已閉合後）之審計工具延伸（append-only，2026-10-01 15:30）

R11 落檔後 `scripts/37_closeout_docs.py` 由 **10/10** 降為 **8/10**，兩 FAIL 皆屬**新內容漂移**（非舊判決失效）；依「工具延伸」紀律只改儀器、不改任何已記錄判決：

1. **CO4**：孤兒 data JSON 報出 `data/38_r10_freeze_firstrun.json`、`data/41_r11_freeze_firstrun.json` ⟹ 兩者屬**首跑副本 by design**
   （凍結檔之首跑留存），延伸：`*_{firstrun,secondrun,thirdrun}.json` 不入孤兒掃描。
2. **CO6**：§十九（R11）之「遺留之動態」「新 🔴」行 ＋ `final_result.md` 之「新 🔴 四項見 docs/23…」指引行被判為殘餘
   ⟹ 延伸三處：`round_pat` 納入「十九」；殘餘白名單容 `O225/R\d+`；新增排除類 **⑩「跨檔摘要指引行」**（🔴/🟡 之判定在所指結果檔內已逐條給出）。
3. 延伸後重跑：**10/10 PASS**（`data/37_closeout_docs.json`）；延伸前之日誌副本 `logs/37_closeout_docs_r11_pre_ext.out` 保留。
4. 舊判決不變：§一 T1 32/32、T2 10/10 之結論與 `data/36/37` 內容皆未受影響。
