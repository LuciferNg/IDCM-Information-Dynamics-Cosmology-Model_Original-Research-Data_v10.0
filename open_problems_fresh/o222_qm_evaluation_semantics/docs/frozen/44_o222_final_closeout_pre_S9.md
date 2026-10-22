# O222 完整性 closeout（最終裁決及整合保留）（`o222-final-closeout-v1`）
> 依調律者指令 2026-09-30：「執行O222完整性closeout，更新問題註冊狀態，開新o，把剩下開題分開幾個o解決，保留o222開放作為最終裁決及整合」。

## §1 完整性核對（全量、可獨立重跑）
| 項目 | 值 | 工具 |
|:--|:--|:--|
| MANIFEST 凍結件數 | **344**（drift 0／missing 0／restored 0） | `scripts/07_artifact_integrity.py` |
| closeout 審計 | **15/15 PASS（14 輪）** | `scripts/32_closeout3_audit.py` |
| roles | scripts 01–78、docs 01–44、data 01–78、logs 01–78 全在 | MANIFEST |
| 活文檔 | `SESSION_START.md`／`final_result.md`／`01_problem_record.md`／`README` 已含 Session 19 節（舊副本 `*_pre_S19.md` 保留） | — |
| register 一致性 | `UNREGISTERED-DIR 0`、`PID-NO-FOLDER 0`、`STATUS-DRIFT 0`、`BLOCK-DRIFT 0` | `register.py check` |
| 遺留 drift（**非本輪造成**） | `DUPLICATE-DIR 4`（O1／O4／O17／O143 各有兩目錄）、`README-ONLY 1`（O198）、`REF-MISSING 3`（O220／O221 之 ref 為多路徑字串） = HARD DRIFT **8** | 同上（明細見 register check） |

## §2 目標達成度（session-start 四問）
| 問 | 狀態 | 精確結論 |
|:--|:--|:--|
| **Q1 判準本體化／可證偽性** | ✅ 已收束 | 判準 → 可計算結構謂詞（✅/🟡/🔴 機械可判）；互補性 `V²+D² ≤ 1` 證為**空洞**（D ≡ 0，62/62 邊際恰 1/2）；R7 預言集改寫為 P1–P7 |
| **Q2 表示定理（RT1/RT2/RT3）** | ✅ 已收束 | RT1 典範映射**單射 120/120**、字長 `{0:1,1:62,2:57}`、直徑 2；RT2 資源回收（秩 3 固定）；RT3 最小分離幀 = **4**（12,645 個、基準率 2.2668%）、秩-6 最小 = **6**（基 V00–V05）；字層冗餘 = **62 個長度-2 關係**（反逆封閉） |
| **Q3 回滾／時間** | ✅ 已收束（no-go） | 1 pass：3844 對、11532 讀、124 命中、3844 pop；回滾 = **深度 1** vs 2 ticks ⟹ **類型錯配**（非 88 倍數值差） |
| **Q4 連接通道** | ✅ 已收束（含邊界） | 對映表 13 格操作化；機制層三項量化為**結構性缺席**：K = ±1 完全平衡（120/120 列和 ≠ 1）⟹ 無 context Born 權重；隨機性 = 恰 60 行為 / log₂60 = 5.9069 bits；CHSH 可行 ≤ 2 vs 不可行 3（0 可行頂點） |
| **Q5 惰性邊界** | ✅ 已收束 | 17 於全部精確不變量中 **NOWHERE**；回滾 ≠ 2 tick；軸集冗餘 58/62 可刪；判準響應矩陣秩 = 1 |

## §3 register 狀態（O222 本體）
- **O222 = `partial`（保留開放）** —— 角色：**最終裁決及整合**（所有分流 o 之結果須回 O222 對賬；O222 之四問結論為裁決基準）
- 本輪新增：`R24`–`R29` 六輪全 `closed`；`Q1/Q2/Q3/Q4` 四項 progress（partial，附精確陳述）；十項 handoff（見 §5）
- pid 統計（O222 子項，53 pid）：closed **29→31**｜partial **16→14**｜negative **4**｜open **3**｜registered **1**（隨最後兩輪 progress 更新）

## §4 剩餘開放問題之分流（五個新 o，全部已註冊）
| 新 o | 題目 | 承接之 O222 項目 |
|:--|:--|:--|
| **O224** | amplitude／複相位層之構造 | Q4（機制層複相位/張量層）、B1／B2／B3R2、R25、R27C、R29(a)(c) |
| **O225** | 機制層 Born 權重／概率結構之強制 | C2G7（判準獨立性）、Q4（Born 層）、Q5（動態 17）、K3（G1 語義）、G2c、D6 |
| **O226** | 回滾與退相干之時間結構 | Q3、B5、D6（時間部分） |
| **O227** | 連接通道：對映表、無信號與糾纏熵 | Q1、B4、D6、Q4（通道）、G8 |
| **O228** | 求值語義之資源幾何與最小性 | Q2（RT1/RT2/RT3）、K6、N2a／N2b／N2e、B3R2（資源） |
- 目錄：`open_problems_fresh/<slug>/`（scaffold 生成之註冊路徑＝保持 register 歷史 ref 一致；pid = O224–O228）
- 初始狀態：全部 `registered`（未開始）；每 o 之 `01_problem_record.md` 含：問題陳述／已確立／🔴未確立／攻擊路線／驗證標準／O222 交接依據（只讀指針）／紀律

## §5 交接記錄（只經 register，無在其他 O 寫檔）
- 10 條 `handoff` 事件：`O222 → O224/O225/O226/O227/O228`（每 o 兩條：項目＋ref）✓ append-only
- 明示：**禁止**在 O222 或其他 O 目錄寫入檔案；跨 O 只可經 register（handoff／note／mirror）✓ 本輪遵守

## §6 已定位但非待辦（理論邊界，屬 O224/O225 之判決對象）
```
🔴 複相位層：古典界 2 vs Tsirelson 2√2（差 41.42%）
🔴 二分張量層：K 之核 = 2I ⊆ SU(2) = 單系統
🔴 機制層 Born：K 帶號 + 120/120 列和 ≠ 1 ⟹ 無非負歸一權重
🔴 糾纏熵：可及深度 1、單副本 ⟹ 熵量空缺（R_indep = 1 被決定性強迫）
```
以上皆為**結構性 no-go 陳述**（非 to-do），惟其**終局性**由 O224／O225 裁決。

## §7 本輪紀律遵守
全量無優化（零剪枝、精確算術）✓；預註冊先於運算 ✓；零新參數 ✓；自更正（R29 Pr-4 比較器瑕疵）保留更正前副本 ✓；文檔歷史完整性（舊記錄只加指針）✓；MANIFEST 回填 344 件 ✓


## §8 追補（同日 append）：drift 自我檢討（本 session 造成並已更正）
- 本輪開新 o 時，scaffold 以 slug 命名目錄；隨後一次命名往返（改 oNNN_slug 再改回）**造成 6 條歷史 ref 指向中間態路徑** ⟹ register 為 **append-only**，該 6 條歷史事件無法抹除。
- **已更正**：目錄定為 scaffold 之註冊路徑（slug ✓）；handoff ref 全部重發為**存在路徑**（O222↔O224–O228 雙向 10 條 ＋ 避免中間態 ✓）；`UNREGISTERED-DIR 0`／`PID-NO-FOLDER 0` 維持 ✓
- **drift 最終明細（14 = 4+1+9）**：`DUPLICATE-DIR 4`（O1／O4／O17／O143，**遺留**）、`README-ONLY 1`（O198，**遺留**）、`REF-MISSING 9`（O220／O221 三條**遺留** ＋ 本輪 6 條**中間態歷史**，已更正並記錄）✓
- 教訓（寫入 o-series workflow）：**開新 o 必須一次過命名正確**；scaffold 之後唔好改目錄名（append-only register 會累積 missing ref）✓
