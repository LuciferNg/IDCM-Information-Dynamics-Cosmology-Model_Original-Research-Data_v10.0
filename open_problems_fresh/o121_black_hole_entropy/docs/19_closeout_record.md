# O121 — Close-out 記錄 (2026-10-02)

> **執行者**: Hermes (本對話框 session 鏈) ｜ **Workflow**: skill `idcm-closeout` **v3.8.0**（§0.3 六點交付）
> **審計器**: `scripts/19_closeout_audit.py` = **68 PASS / 0 FAIL 🟢** ｜ `logs/19_closeout_audit.out`
> **範圍**: 本 O 目錄**只**（§5.2 硬規則 2）；本地主題目錄以外零寫入（register 除外，屬明示機制）

---

## T0 — 閉合水位掃描（增量閉合，規則 3）

水位節**已於早前建立**（`01_problem_record.md` §「檔案閉合水位」line 116）。本輪**增量更新**：

| 條件 | 動作 | 結果 |
|:-----|:-----|:-----|
| `mtime ≤ 上次 closed-out` | skip | docs/**02–12**（水位內已驗，本輪無變更） |
| `mtime > 上次 closed-out` | 只驗新增／改動 | **docs/13–18 + SCRIPT_CHAIN + scripts/11–19 + data/12–19 + logs** |
| 從未 closed-out | 全檔驗 | `docs/13–18`、`scripts/19_closeout_audit.py` |

**本輪水位表更新**：19 → **26 行**（新增 docs/13–18、SCRIPT_CHAIN、scripts/11–19、data/12–19、logs/、`_prepatch_20261002/`）。

### ⚠️ 本輪對已閉合檔之**唯一**改動（log 格式，非計算）

`scripts/01–10 + audit_independent.py` 之 log 尾行 token `結果:` → **`RESULT:`**（統一 §4.9 正典格式）。
- 動機：§4.9 要求「每個鏈腳本有正典 log 帶 `RESULT:` 行」；scripts 11–18 已用 `RESULT:`，01–10 用 `結果:` ⟹ 機器不可查。
- **零計算改動證明**：改動前記 18 個 `data/*.json` sha256 → 重跑 → 全部 **18/18 一致**（`data/_closeout_20261002/pre_rerun_sha256.txt`）。
- 11 支檔之改前 sha256（前 12 位）已記錄（見下方 §E）。

---

## T1 — 獨立重驗（唔 import 原 script）

- **`scripts/audit_independent.py`**（獨立審計，零 import；自第一性原理重算）— 重跑 **0 deviations**，並補 `RESULT:` 行。
- **`scripts/19_closeout_audit.py`**（本輪新增，獨立於上面兩者）— §J 段由原始定義重算 25 個 headline 數字，**全 PASS**；A–K 共 **68 PASS / 0 FAIL**。
- **`scripts/run_chain.sh`**（本輪補建，driver of record）— 全鏈 20 支一次過重跑，**全 `exit=0`**（§4.9⑥）。
- **全鏈重跑**：`scripts/01–19` 逐支 `exit=0`，**`RESULT:` PASS 加總 = 195**（`audit_independent` 另計 0 偏差）。

| 段 | 腳本 | RESULT |
|:--|:--|:--|
| 01–10 | 主推導 | **88 PASS / 0 FAIL**（與記錄「88/88」吻合） |
| audit | 獨立審計 | 0 deviations |
| 11–18 | G8 鏈 | **107 PASS / 0 FAIL** |
| 19 | close-out 審計器 | **68 PASS / 0 FAIL** |

### §J 獨立重算（第一性原理，本輪）

`Σγ = 90` ✓ ｜ `E_sync = 61.5` ✓ ｜ `E_proj = 28.5` ✓ ｜ **`E_sync/E_proj = 41/19` EXACT ✓** ｜ `Ω_Λ = 61.5/90` ✓
`η = φ⁻²¹` ✓ ｜ `(N_d−μ²)/2 = 21` ✓ ｜ `583/2 = N_d×(53/8) = 291.5` ✓ ｜ `B·L = 26.5` ✓ ｜ `F₉ = F₈+F₇` ✓
`T_ring = 2π/ω_ring` ✓ ｜ `τ_pred = 2²⁰·T_ring = 8.8748e16` ✓ ｜ `M_BH = 5.88e18` ✓ ｜ **`τ_ref(修正) = 8.7594e14` ✓** ｜ `τ_pred/τ_ref = ×101.3` ✓
`V_world = 4π/3 R_world³ = 2.951e11` ✓ ｜ `V_comov/V_world = 40.669 ≈ 40.678` ✓ ｜ `M_crit = 7.90e4 kg` ✓ ｜ `E_27(a=ℓ) = 7.18e15 eV` ✓

---

## T2 — 文檔完整性 + 數值交叉核對

- **17 份 docs 逐份讀**；G8 鏈 6 份新檔（13–18）與 scripts/data 逐項對映。
- **必查七類**：百分比重算 ✓ / rounding drift ✓ / 跨文檔一致 ✓ / 量綱 ✓ / 計數 ✓ / primary source ✓ / 分類表 ✓
- **本輪抓到的錯**（全部屬**記錄層**，非推導層）：
  1. **`scripts/01–10` log token 不一致**（`結果:` vs `RESULT:`）→ 已統一（T0 節）。
  2. **§10-A#57 陷阱命中**：`01_problem_record` / `docs/18` 只用**代號**（`scripts/13`）而非**完整檔名** → 補建 **`docs/SCRIPT_CHAIN.md`**（19 支鏈腳本逐個列全名 + 產物 + RESULT）。
- **未發現任何推導數值錯誤**（§J 25 項獨立重算全過）。

---

## T3 — 時序完整性（禁回溯污染）

**證據來源**：`_prepatch_20261002/{01_problem_record.md, SESSION_START.md}`（10-02 追加前備份）＋ difflib 分類。

| 檔 | 行數 | 改動區塊 | 判定 |
|:---|:---|:---|:---|
| `01_problem_record.md` | 171 → **346** | **2 區塊 / 6 行** | ✅ **全部屬 live field**（狀態行 + 時序索引輪次列 + session 計數） |
| `SESSION_START.md` | 187 → **457** | **0 區塊 / 0 行** | ✅ **純 append，零改動** |

- **判準依 §0.1/T3**：「唯一污染判準 = 舊 artifact 載新推導內容（backfill）」。本輪檢查：**非 live 改動 = 0** ⟹ **無回溯污染**。
- ⚠️ 嚴格前綴 md5（`head -N` = 備份）**不相等** —— 因 10-02 session 於**中間插入**已標日期新節（T4 明文允許之機制）＋更新狀態行（§9.1 live field）。此屬**記錄格式**而非污染；本審計器改用 **difflib 分類**判（見 `scripts/19` §H）。
- **無 `N|` 行號污染**（三份檔皆 0）。
- **日期紀律**：本記錄所有日期由系統 `date` 取得（2026-10-02）。

---

## T4 — 推導時序索引（更新）

已 append 第 8–9 輪至 `01_problem_record.md` §「推導時序索引」：

- **第 8 輪 (2026-10-02 上午)** — G8 交接處理 + 三項攻堅 + 深化 + 預言登記 + τ_ref 體積審計
- **第 9 輪 (2026-10-02 下午)** — 修正後重評 + 三項收尾 + **完整 close-out**

---

## T5 — `final_result.md`

- **已存在**（前輪建立）；本輪 append G8 三項收尾節 + 修正後重評節。
- 段序**依 `open_problems_fresh/RESULT_TEMPLATE.md`**：`# O121 — 標題` → `## 狀態` → `## 結論` → `## 關鍵公式` → `## 依賴` ✓
- **狀態行已三份同步**（§9.1）：

| 檔 | 狀態行 |
|:---|:---|
| `01_problem_record.md` | `✅ 核心已閉合 … ｜ 🔴 G8 (τ_rec) 開放` |
| `SESSION_START.md` | `✅ 已閉合 (88/88 PASS …)` ⚠️ → **本輪同步** |
| `final_result.md` | `🟢 核心已閉合 … ｜ 🟡 G1–G7 ｜ 🔴 G8` |

---

## §4.1 — 未閉合項掃描（交付物 = 未登記行數，必須為 0）

- 掃 `01_problem_record.md` + `final_result.md` 全部 🔴/🟡：**45 行**（含判定摘要表行、狀態行、自指行）
- 排除後**真殘餘 26 行**，**全部帶書面判定 = 26/26** ⟹ **未覆蓋 = 0 ✅**
- 三級判準（O225 實錄）：(1) 已帶判定 token → 26；(2) 3-gram 對映 → 不適用（(1) 已全覆蓋）；(3) Rn 對照表 → 不適用。

## §4.2 — 宣告輸出 vs 實際檔案

- **`data/*.json` 孤兒 = 0**（18 鏈 JSON 全部有 producer）；script 宣告之輸出檔**全部存在**。
- ⚠️ 檢查器首版 regex 太窄（只認 `data/NN_x.json` 形式，漏 `os.path.join(BASE,"data","NN_x.json")`）→ 已修（§10-A#4「抽檔名 regex 要闊」）。

## §4.9 — 推導落碟完整性（六項，硬規則 5）

| # | 核對 | 結果 |
|:-:|:-----|:-----|
| ① | 腳本集對稱 | 磁碟 19 支鏈腳本 ⟷ `docs/SCRIPT_CHAIN.md` 所列，**兩側差集空** ✅ |
| ② | 逆向綁定 | 10 個 headline 數字 → 全部有磁碟 producer ✅ |
| ③ | 路徑衛生 | `scripts/*.py` 內 `/tmp` 等**寫入模式 = 0** ✅（1 個字面量命中屬唯讀／註解） |
| ④ | scratch 鏡射 | 本輪 scratch 僅 1 支維護腳本（token 統一），其效果已落 `scripts/01–10` 本身；**無本 O 歸屬之 scratch 產物** ✅ |
| ⑤ | inline 推導偵測 | session 鏈內 `execute_code` payload 已核：本輪之 `execute_code` 只做**讀取**（session DB 查詢、register 寫入），**零 headline 數字在此產生** ✅ |
| ⑥ | driver of record | ✅ **本輪補建** `scripts/run_chain.sh`（dry-run 預設 + `--execute`）；20 支全鏈 `exit=0` |

## §4.10 — 登記面覆蓋核對（七項，硬規則 6）

| # | 核對 | 結果 |
|:-:|:-----|:-----|
| ① | 正向覆蓋 | 本輪殘餘 🔴/🟡 → register 有對應事件 ✅ |
| ② | 新問題註冊 | 所有新開放項只經 register（無寫入 README／SESSION_START 作註冊）✅ |
| ③ | 反向覆蓋 | register O121* 事件 16 條 ⟷ 記錄所列項，**差集空** ✅ |
| ④ | `check` 對基線 | `HARD DRIFT = 62`（開輪前 = 收輪後，**未升**）✅ |
| ⑤ | 機器塊 | 本 O pid 無 `BLOCK-DRIFT` ✅ |
| ⑥ | 讀回 | 每條事件讀回傳行 ✅ |
| ⑦ | README | ⚠️ finding（見下） |

**register O121* 事件（16 條）**：
```
2026-09-25  registered  O121                 state=open
2026-10-02  registered  O121/return-rate     state=open
2026-10-02  note        O121
2026-10-02  closed      O121                 state=closed   ← 核心閉合
2026-10-02  note ×9     O121/return-rate
2026-10-02  handed_off  O121/return-rate → O175 ×1, O173 ×2, O72 ×1
```

---

## §5.1 — Session 鏈 provenance（以 **session DB** 為準，非上下文記憶）

**本鏈**（`session_key = agent:main:telegram:dm:7500748185:60050`，=本對話框）— **8 sessions / 1515 msgs**：

| # | session id | 起始 | end_reason | msgs |
|:-:|:-----------|:-----|:-----------|:-----|
| 1 | `20260903_110404_fef4b737` | 09-03 11:04 | compression | 222 |
| 2 | `20260903_131931_500459` | 09-03 13:19 | compression | 368 |
| 3 | `20260924_094052_649ac9c8` | 09-24 09:40 | session_switch | 0 |
| 4 | `20260924_235754_eed4f8` | 09-24 23:57 | compression | 297 |
| 5 | `20260925_145121_2dc569` | 09-25 14:51 | compression | 199 |
| 6 | `20261002_162334_10e33f` | 10-02 16:23 | compression | 152 |
| 7 | `20261002_164501_5c05c2` | 10-02 16:45 | compression | 157 |
| 8 | `20261002_172721_f20800` | 10-02 17:27 | (current) | 120 |

**相鄰 thread（不同 `session_key` ⟹ **不同鏈**，只作參考，§5.1 明禁混入）**：
- `20260829_054720_e72900b8`（thread **58401**，226 msgs）= **O121 建立** session
- `20260922_103251_5bf42cf1`（thread **85386**，357 msgs）= O208 越權 session
- `20261002_155039_70bf2d`（thread **56315**，117 msgs）= **G8 交接** session

⚠️ 依 §10-A#28「session 鏈係活嘅」：訊息數為**快照**（本輪觀察 1467 → 1515 一路增長）⟹ 本表只記錄**查詢時刻**之值。

**寫入 ledger 核實**：本輪之磁碟寫入全部落在本 O 目錄 + `problem_register/register.jsonl`（後者屬明示跨 O 機制）。

## §5.2 — 範圍硬規則證據

```bash
git status --short open_problems_fresh/o121_black_hole_entropy/
#   M  SESSION_START.md
#   ?? 01_problem_record.md / final_result.md / docs/ / scripts/ / data/ / logs/ / _prepatch_20261002/
#   ⟹ 全部在本 O 目錄內
```

**repo-wide 改動歸因**（§5.2：逐檔核實擁有權先講「越界」）：

| 檔 | 歸屬 | 判定 |
|:---|:---|:---|
| `open_problems_fresh/o121_black_hole_entropy/*` | **本鏈** | ✅ 範圍內 |
| `problem_register/register.jsonl` | **本鏈** | ✅ 明示機制 |
| `open_problems_fresh/README.md` | **非本輪**（O88/O220 行更新 + **O121 行** 早前 session 之 G8 交接註記） | ⚠️ **finding**（見下） |
| `.gitignore`、`crystal_stress/*`、`ckm_reconstruction/*` | **並行 session** | ✅ 非本輪 |

---

## §6.1 — 問題級閉合冗餘審計（G1–G8）

| 項目 | 狀態 | 閉合來源 / 裁決 |
|:---|:--:|:---|
| G1 面積律 `1/4 = 1/B` | 🟡 | MERA 邊界形式化（docs/03）— 外部依賴 |
| G2 M_P 第一性原理 | 🔴 | O110 B10 — **屬其他 O** |
| G3 次格點自由度身份 | 🟡 | 需次格點模型 — 外部依賴 |
| G4 `Ω(E)` 與 BH 對數修正 | 🟡 | 微態計數嚴格化 — 外部依賴 |
| G5 `ρ_max = ρ_P` + Hayward 耦合 | 🟡 | docs/10 — 部分（`M_crit` 已算，見 P-G8d） |
| G6 強場區 `⟨\|W(r)\|²⟩` | 🟡 | docs/09 — 外部依賴 |
| G7 `Ω(x)` 精確形式 | 🟡 | docs/08 — 外部依賴 |
| **G8 `τ_rec` 返池時標** | **🟡 有推導、無檢驗** | docs/13–18；register `O121/return-rate`（open） |

**G8 最終裁決**：主推導 `τ_rec = 2^{MIS}·T_ring` 成立於前提、零參數、**下界一致（無證偽）**，
但**現時不可檢驗**（可行域跨 2 個數量級，四類觀測全無判別力）。唯一有 ΛCDM 判別力之即時通道 = **P-G8d**。

---

## ▲ Findings（本輪發現，已記錄未就地修者）

| # | Finding | 類別 | 處置 |
|:-:|:--------|:-----|:-----|
| F1 | `scripts/run_chain.sh`（driver of record, §4.9⑥）**不存在** | 缺口 | ✅ **已修**：本輪補建（dry-run 預設 + `--execute`；20 支全鏈 `exit=0`） |
| F2 | `open_problems_fresh/README.md` 之 **O121 行被塞入長註記**（§4.10⑦ 規定只改狀態 emoji）；非本輪所為 | ⚠️ §5.2 越界（他人） | **只記錄不移交**（README 屬共享索引，就地修 = 再越界） |
| F3 | `_prepatch_20261002/` 留於 O 根目錄（§10-E.8 判為「非慣例」） | 檔案佈局 | **保留** —— 被 `SESSION_START`（不可變）引用 ⟹ 依 §10-E.8 判別準則「有 doc 引用」= **時序證據**，非工作備份 |
| F4 | O225 / O227 / O228 之 `BLOCK-DRIFT`（block state ≠ register state） | 他人 O | 已 register `note` flag（不改 state） |

## ▲ 修正（本輪已做）

| # | 修正 | 範圍 |
|:-:|:-----|:-----|
| M1 | `scripts/01–10 + audit_independent.py` log token `結果:` → `RESULT:` | 11 檔，**零計算改動**（18/18 data hash 不變） |
| M2 | 補建 **`docs/SCRIPT_CHAIN.md`**（§4.9①/§10-A#57 完整檔名） | 新檔 |
| M3 | 水位表 19 → 26 行（T0） | `01_problem_record.md` |
| M4 | 時序索引 append 第 8–9 輪（T4） | `01_problem_record.md` |
| M5 | `SESSION_START.md` 狀態行同步（§9.1） | 1 行 |
| M6 | 補建 **`scripts/run_chain.sh`**（§4.9⑥ driver of record） | 新檔 |
| M7 | 最終一跑：全鏈 20 支 `exit=0`；審計器 **68/68** | — |

---

## 交付物清單（§0.3 六點）

| 點 | 交付 | 位置 |
|:-:|:-----|:-----|
| 1 | 重跑全部 scripts + 獨立 verifier | `logs/01–19*.out`；`audit_independent` 0 偏差；`19` 66/66 |
| 2 | session 鏈 provenance + 原文保留 + 檔頭日期 | 本檔 §5.1；T3 表 |
| 3 | 時序表 + 範圍核實（嚴禁寫出本目錄） | 本檔 T3 + §5.2 |
| 4 | 開放問題 inventory + 推導時序索引 + register 雙向核 | 本檔 §4.1/§4.10/§6.1 |
| 5 | `final_result.md`（依 RESULT_TEMPLATE） | `final_result.md` |
| 6 | 推導落碟完整性（六項） | 本檔 §4.9 |

---

*本檔為 O121 close-out 記錄 ｜ workflow: skill `idcm-closeout` v3.8.0 ｜ 2026-10-02*
*審計器: `scripts/19_closeout_audit.py` (**68 PASS / 0 FAIL**) ｜ driver: `scripts/run_chain.sh` (20 支 all exit=0)*
