# O228 / R3＋R4 — §五 硬測試（null 樣本帶 ＋ 擾動剛性）與 null 口徑審計（結果）

- 合約：`docs/03_r3_contract.md`（`o228-r3-hardtests-v1`，預註冊 H1／H2a／H2b／H2c／H2d／H2v）
  ＋ 登記 `O228/R4`（口徑審計，預註冊 J1／J1b／J2／J3／J4）
- 腳本／日誌／資料：`scripts/06_r3_hard_tests.py`、`scripts/07_null_scope_audit.py`
  → `logs/06_r3_hard_tests.out`、`logs/07_null_scope_audit.out`、`data/06/07_*.json`
- 判定：**06 → 5/8 PASS（3 FAIL 原樣保留）**；**07 → 5/5 PASS**
- 首跑 FAIL 節錄：`logs/06_r3_firstrun_FAIL_excerpt.out`（原樣保留，內含 H1／H2a／H2b 之首跑 FAIL 與 H2c 前之崩潰）

---

## §0 預註冊與 FAIL 記錄（鐵律：被偽證者不改寫成 PASS）

| tag | 狀態 | 說明 |
|---|---|---|
| **H1**（首跑） | ❌ FAIL 保留 | 10⁷ draws MC = 0.034112／0.034104 vs 記錄值 0.034618 | 
| **H1**（校正後） | ✅ PASS | 口徑修正後：MC(10⁷, distinct) = 0.034560 vs 0.034618（dev **1.0σ**）|
| **H2a** | ❌ FAIL 保留 | 預測「單列刪除恰 3 值、重數 (12,20,30)」；實測 **4 值**，重數 (15,25,15,7) |
| **H2b** | ❌ FAIL 保留 | 預測「單線刪除恰 3 值、重數 (6,10,15)」；實測 **7 值**（幾何線配對修正後）|
| **H2c** | ✅ PASS | 隨機單線替換 200 次，**199 次**改變 F_4（門檻 ≥190）|
| **H2v** | ❌ FAIL 保留 | 判決式自身沿用 H2a/H2b 之已偽證條件 ⟹ 條件不成立（判決**內容**由 H2v-c 承載）|
| H2a-c、H2b-c、H2v-c | ✅ PASS | 更正後之量測與判決（見 §2）|
| J1、J1b、J2、J3、J4 | ✅ PASS | 口徑審計（見 §1）|

---

## §1 H1：null 樣本帶 ＋ 口徑審計（§五②履行）

### 1.1 首跑 FAIL 之真因（兩個缺陷，皆在**我嘅測試設計**，非 R1 之值）

1. **口徑錯配（主因）**：R1 C17 之精確值 `p₀ = 6240/180251` 之分母係 **C(462,4)**（**distinct** 4-子集），
   而首跑 H1 以 **with-replacement**（462⁴）抽樣比較 ⟹ 比緊兩個唔同嘅量。
2. **RNG 診斷作廢**：首跑另記「LCG 序列相關漂移」——**證偽**：LCG 版 0.034112 與 MT 版 0.034104 幾乎相同
   （皆 ≈ with-replacement 之真值 0.03415）⟹ 無漂移，偏離 100% 來自口徑。

校正：H1 改以 **10⁷ 次 distinct 4-子集均勻抽樣**（Mersenne Twister，宣告種子）比較 `p₀` ✓。

### 1.2 R4 口徑審計（`scripts/07`，5/5 PASS）

| tag | 檢定 | 結果 |
|---|---|---|
| **J1** | C17 之 Möbius code path（**獨立重寫**，唔 import 02）vs 全枚舉 brute force | m=6：**195 = 195**；m=8：**22050 = 22050** ✓ |
| **J1b** | m=10（brute force C(126,4)≈10⁷ 不可行）vs 3×10⁶ distinct MC | Möbius 1436400/10009125 = 0.143509 vs MC 0.143514（dev 5.3e-6，**0.03σ**）✓ |
| **J2** | 10⁷ draws distinct MC vs `p₀` | 0.034597 vs 0.034618（dev 2.14e-5 = **0.37σ**）✓ |
| **J3** | with-replacement 係**另一個量** | distinct 0.034597 vs with-repl 0.034154，差 **5.7σ** ⟹ 兩口徑不可互比 ✓ |
| **J4** | 精確約分 | Möbius F_4(m=12) = 64864800、C(462,4) = 1873709145 ⟹ **6240/180251 = 0.03461839**（最低項）✓ |

⟹ **結論**：R1 C17 之精確 null **正確且已獨立驗證**（兩級獨立：① 公式 vs 全枚舉（m=6,8）② 公式 vs 10⁷ MC（m=10,12））；
R1 之「機器率 0.022668 < null 0.034618」判讀**不變**（同口徑：12645/C(62,4) vs 6240/C(462,4)）。
首跑 H1 之 FAIL 屬**測試口徑缺陷**，已保留原樣並以 H1 校正版重測 ✓（此即 §五② 之履行）。

---

## §2 H2：擾動／結構剛性（§五④履行）

基準：𝔐_2I，m = 12、N = 62、**F_4 = 12645**（獨立重算，與 R1 一致）。

### 2.1 單列刪除（62 變體）

- 4 個相異值：**{11726×15, 11832×25, 11890×15, 11910×7}**（總 62），**全部 < 12645** ⟹ **無任何單列冗餘**。
- 族內分裂：V → {11832, 11910}；F → {11726, 11890}；E → {11726, 11832, 11890, 11910}。
- **預註冊之「V/F/E 軌道遞移 ⟹ 3 值」被偽證**：凍結平手規則 τ 讀「該列自身第一個非零分量」⟹
  **非 2I-等變**（座標依賴）⟹ 刪除譜細化群軌道。**與 R1 C18「慣例敏感」同源**（同一非等變性）。

### 2.2 單線刪除（31 條幾何線，配對 = `U[b] = −U[a]` 精確驗證）

- 7 個相異值：**{10807×5, 11019×5, 11026×5, 11064×5, 11135×5, 11136×5, 11175×1}**，全部 < 12645。
- 族內：V → {11019, 11175}（其中 11175 為**唯一**一條線）；F → {10807, 11135}；E → {11026, 11064, 11136}。
- 首跑之「符號夥伴配對」缺陷：edge 線兩列在 4 個平手位**同號**而非相反（τ 於平手位非奇）⟹ 首跑只配出 21 條偽線；
  本輪改以**幾何 ± 配對**（`(0,11),(1,10),…` 每族鏡像對稱，31/31 精確）。

### 2.3 隨機單線替換（200 次，seed 228228，MT）

- **199/200** 改變 F_4；F_4 ∈ [**10987, 17507**]，中位數 12262（基準 12645）⟹ 相對擺幅可達 ±38%。

### 2.4 剛性判決（H2v-c，PASS）

**資源計數不具結構剛性**，四路證據：
① 62/62 單列刪除、31/31 單線刪除**全部**令 F_4 嚴格下降（無冗餘軸）；
② 刪除譜分裂成 4／7 個類（**非**群軌道，因 τ 非等變）；
③ 199/200 隨機替換改變 F_4（±38%）；
④ 慣例擾動（R1 C18 等變平手規則）F_4 = 12645 → **1000**（**12.6×**）。
併合 R1 C17-c（機器率 0.0227 **低於** null 0.0346 ⟹ 無超額）⟹ **F_4 = 12645 係具體 31 線排列之產物，
唔係結構不變量**（判 🟡；與「無效才是正確」一致：無超額 + 高敏感 = 資源計數無結構簽名）。

---

## §3 §五 四道硬測試之履行狀態（O228 全輪）

| 硬測試 | 狀態 | 證據 |
|---|---|---|
| ① 零參數 | ✅ | R1/R2/R3 全程零新參數；容差皆精確整數／Fraction（浮點只在明示 MC 與顯示） |
| ② MC null（10⁷、5σ） | ✅ | **本輪履行**：H1 PASS（distinct 口徑）＋ R4 口徑審計 5/5；R1 C17 精確值經兩級獨立驗證 |
| ③ 可證偽＋樣本外盲測 | ✅ | R2 B1–B5（24/25 命中，1 MISS 已更正為 B1-c）；R3 H1/H2 皆預註冊可證偽 |
| ④ 結構剛性（擾動） | ✅（**否定式結論**） | H2a-c/H2b-c/H2c/H2v-c：計數非剛性（刪除全降 + 199/200 替換 + 慣例 12.6×） |

---

## §4 更正史（append-only 記錄，原文不改）

| 校正 tag | 原 FAIL | 更正內容 |
|---|---|---|
| **H1 校正** | 首跑 8.9σ 偏離 | 口徑錯配（with-replacement vs distinct）；RNG 漂移診斷**作廢**；改 distinct MC ⟹ 1.0σ |
| **H2b 校正** | 線配對只得 21 條 | 符號夥伴 → 幾何 ± 配對（`U[b] = −U[a]`，31/31）|
| **H2a-c／H2b-c** | 軌道遞移假設偽證 | 記錄 4／7 類刪除譜 ＋ 成因（τ 非等變）|
| **H2v-c** | 判決式沿用已偽證條件 | 判決內容改綁「全部下降 ＋ 類數 ＋ 替換率 ＋ 慣例擺幅」四路證據 |
| **B1-c**（R2） | 𝔐_T F₃ 預言 212 vs 實測 244 | 手算家族 (f) 誤判 `C={v₁v₄\|v₂v₃}` 不切 `{v₂,v₄}`（實際切）⟹ 64→96，232+12=244 |
| **T2-c**（R2） | 二分割 ⟺ 無平手（雙向偽）| 二分割 ⟺ 軌道**中心對稱**（τ 奇 ⟹ 平手自動平衡），6/6 命中 |

---

## §5 遲到通知排除（records 完整性）

本輪收到一則**遲到通知**（`scripts/01_r1_census.py` 之舊 run，exit 0，`RESULT: 12/12 PASS`）。
依協議核身份後**零動作**：輸出與 R1 凍結記錄逐項一致（C4 = 31 線 6/10/15、C5 = 全 (6,6)、C6 = {3:10,5:5,7:1}、
C7 = split 15 edge、C8 = 120 零點、C9 = 16 雙射、C10 = V 型 (3×5+5)、C11 = 6/6 閉鄰域）；
`logs/01_r1_census.out` 與 `data/01_r1_census.json` 為**確定性重跑**（同輸入同輸出）；
4 件 o222 唯讀對象 sha256 核對**全部不變**（見 §6）；**活躍進程核對 = 0**（收尾時）。

### 第二則（SIGTERM，exit 143，`scripts/02_r1_closed_form.py`）

同輪另收一則**遲到通知**：某背景 `02_r1_closed_form.py` 進程以 **143（SIGTERM）** 結束（無輸出）。
依協議**只核不重跑**，逐件以**雜湊**定身份（唔以通知為準）：

| 標的 | 即時 sha256 | MANIFEST 記錄 | 判定 |
|---|---|---|---|
| `logs/02_r1_closed_form.out` | `f22567c0…76dcd2` | `f22567c0…76dcd2` | **相同 ✓ 未污染** |
| `data/02_r1_closed_form.json` | `89da6055…22ed23` | `89da6055…22ed23` | **相同 ✓ 未污染** |

補證：兩檔 mtime = **07:26**（成功之正式跑）；`logs/02…out` 尾部完整（`RESULT: 8/8 PASS (0 FAIL) elapsed 224.3 s`）、
`grep -c Traceback = 0`；`data/02…json` 可解析、`claims 8/8 PASS`、`null_all_bisections.p0 = 6240/180251` ✓；
活躍進程 = **0**。⟹ 該 SIGTERM 進程之重定向**從未落地**（被 07:26 之正式跑完全覆寫）⟹ **零動作、無需重跑**。

### 第三則（exit 1，`proc_057006188c7b`，同一 `02` 劇本之首個背景啟動）

另一則更舊之遲到通知（**首輪**啟動之 `02_r1_closed_form.py` 背景進程，exit 1，無輸出）。
同樣**只核不重跑**：

| 標的 | 即時 sha256 | MANIFEST 記錄 | mtime | 判定 |
|---|---|---|---|---|
| `logs/02_r1_closed_form.out` | `f22567c0…76dcd2` | 同 | 07:26:44 | **未污染 ✓** |
| `data/02_r1_closed_form.json` | `89da6055…22ed23` | 同 | 07:26:44 | **未污染 ✓** |

log 首 3 行（header）與尾 2 行（`RESULT: 8/8 PASS (0 FAIL) elapsed 224.3 s`）完整、`grep -c Traceback = 0`；
`08:10` 之後 O228 以外之寫入 = **空**（早前之 `o229` 檔屬 sibling session）；活躍腳本進程 = **0**
（先前 `ps` 之 2 命中經核實為**本 shell 自身包裝**，非腳本）。⟹ 首輪進程既無成功亦無落地寫入（exit 1 於
`data/` 之前中止）⟹ **零動作**。**三則遲到通知全部排除完畢。**

### 第四則（exit 1，`proc_be165de40657`，同族：R1 期間之第 2 個 `02` 背景啟動）

以 `sha256sum -c` 逐件核（**唔重跑**）：

```
f22567c0…76dcd2  logs/02_r1_closed_form.out: OK
89da6055…22ed23  data/02_r1_closed_form.json: OK
```
mtime 仍 = **07:26:44**（兩檔）、`MANIFEST.json` ↔ 即時雜湊 = **一致 ✓**、活躍腳本進程 = **0**、
`08:15` 之後 O228 以外寫入 = **空**。⟹ 同族 stale 進程（R1 前置之多次 `02` 啟動）逐一結束，**全部無落地寫入** ⟹
**零動作**。四則遲到通知皆以「雜湊先行」定身份，**無一觸發重跑**；凍結產物之 sha256 全程未變。

### 第五則（exit 0，`proc_965498c67686`，R1 之 **02→03 鏈**）

訊息自稱「completed normally (exit 0)」——但**核身份後發現係 07:26–07:27 之同一條鏈**（非新 run）：

| 標的 | 即時 sha256 vs MANIFEST | mtime |
|---|---|---|
| `logs/02_r1_closed_form.out` | **MATCH** `f22567c0…` | 07:26:44 |
| `data/02_r1_closed_form.json` | **MATCH** `89da6055…` | 07:26:44 |
| `logs/03_r1_audit.out` | **MATCH** `77f417a5…` | 07:27:25 |
| `data/03_r1_audit.json` | **MATCH** `3fe4eaf2…` | 07:27:25 |
| `logs/03_chain.status` | **MATCH** `c04f8aa5…` | 07:26:47 |

⟹ **零改動、零動作**。★ 延伸發現（本則通知之唯一實際價值）：該 status 檔載 **`03 exit=1` / `11/12 PASS (1 FAIL)`**
（首跑之 B3 實作缺陷），與現行 `logs/03_r1_audit.out` 之 **12/12 PASS** 形成**雙階段歷史**；已加註
`logs/03_chain.status.NOTE` ＋ `docs/01_r1_results.md` §9c（**原檔一字不改**）。

### 第六則（exit 0，`proc_9cc96100ff71`，`04` 之**修正前**版本，崩潰）

最舊之一則：`scripts/04_r2_general_machine.py` **前置修正版**之首跑，shell exit 0 但內容為
`IndexError: ... poly[k]` 崩潰（exit=1）。

| 標的 | 即時 sha256 vs MANIFEST | mtime | 判定 |
|---|---|---|---|
| `logs/04_r2_general_machine.out` | **MATCH** `1cf32f26…` | 07:42:32 | **未污染 ✓**（內容 = `RESULT: 13/15 PASS (2 FAIL) elapsed 44.9 s`、`grep -c Traceback = 0`）|
| `data/04_r2_general_machine.json` | **MATCH** `3416e8dc…` | 07:42:32 | **未污染 ✓** |

⟹ 首跑之 `tee` 輸出既未落地亦已被正式跑完全覆寫 ⟹ **零動作、無需重跑**。
★ **但通知係該崩潰輸出之唯一現存副本** ⟹ 依「崩潰痕跡要留首跑副本」紀律，原文逐字存入
`logs/04_r2_firstrun_CRASH_excerpt.out`（內附三個已修缺陷：缺 ± doubling 令 `N=7/13/5`、`m` 標錯（`edge 20`／`face 12`）、
`fk_typeset` 越界）。

### 第七則（exit 0，`proc_9003d0a762d1`，同族：`04` 之另一前置修正版）

同族再次到達。核帳：`logs/04_r2_general_machine.out` **MATCH** `1cf32f26…`（mtime 07:42:32）、
`data/04_r2_general_machine.json` **MATCH** `3416e8dc…`、`logs/04_r2_firstrun_CRASH_excerpt.out` **MATCH**（08:13:49）；
`pgrep -af 'scripts/0[1-8]_'` = **0 命中** ⟹ **零動作、無需重跑**。
（`pgrep -fc 'python3 -u scripts/04'` 之命中為**本 shell 自身命令行含 pattern** 之自匹配，非真進程。）

### 遲到通知總結（十則；表格隨新則增量更新，逐則判據不變）

| # | 進程 | 家族 | 即時雜湊 vs MANIFEST | 動作 |
|---|---|---|---|---|
| 1 | `01` 舊 run（12/12 PASS） | R1 census | 一致（同輸出） | 零 |
| 2 | `02`（SIGTERM 143） | R1 | `f22567c0…` MATCH | 零 |
| 3 | `02`（exit 1，首輪） | R1 | 同上 MATCH | 零 |
| 4 | `02`（exit 1，第 2 輪） | R1 | 同上 MATCH | 零 |
| 5 | `02→03` 鏈（exit 0） | R1 | 五件全 MATCH | 零（＋加註 status.NOTE／§9c）|
| 6 | `04`（崩潰，前置版） | R2 | 兩件 MATCH | 零（＋留 CRASH 節錄）|
| 7 | `04`（exit 0，前置版） | R2 | 三件 MATCH | 零 |
| 8 | `04`（exit 0，前置版） | R2 | `1cf32f26…`／`3416e8dc…` MATCH | 零 |
| 9 | scratch 探針（SIGKILL −9） | R2 | 輸出檔已清除、coverage 0 缺口 | 零 |
| 10 | `04`（exit 0，前置版，`proc_2704db4fac47`） | R2 | `1cf32f26…`／`3416e8dc…` MATCH，真進程 0 | 零 |
| 11 | `04`（exit 0，`proc_d54ba47241df`，**即現行權威 log 之產出 run**） | R2 | `1cf32f26…`／`3416e8dc…` MATCH，真進程 0 | 零（通知內容 = 已在檔之同一結果）|
| 12 | `06`（exit 0，`proc_db4e15a15a91`，加 H2v-c **之前**之 4/7 版） | R3 | 現行 `logs/06…out` = 5/8 版 MATCH，真進程 0 | 零（被 H2v-c 版取代；FAIL 集相同 ⟹ 無科學內容遺失）|
| 13 | `06`（exit 0，`proc_84856e123f4a`，同為 H2v-c 前之版本） | R3 | `f3426df0…`／`2fcef4fb…` MATCH，真進程 0 | 零（同上）|
| 14 | `06`（exit 0，`proc_61af065557cb`，同族舊版） | R3 | `f3426df0…`／`2fcef4fb…` MATCH，真進程 0 | 零（同上）|

| 15 | `07`（exit 0，`proc_f3d483e0ff45`，**即現行權威 `07` log 之產出 run**） | R4 | `logs/07…out`／`data/07…json` MATCH，真進程 0 | 零（通知內容 = 已在檔之 5/5 PASS）|
| 16 | **scratch 探針**（`~/.hermes/cache/scratch/o228_null_probe2.py`，exit 0） | R4 血脈 | 非交付物（O 目錄零缺口）；其 `exact_p` 為**有 weighting 缺陷之版本** | 零（結論已被 `scripts/07` **J1／J3** 取代）|

> 第 16 則之探針意義（僅供追溯）：其輸出 `m=6: exact 0.468 vs MC 0.684` 正係**觸發**本輪口徑調查嘅信號；
> 其後以獨立全枚舉（`o228_mini6.py`）判定 **MC 對、reduction 錯**，最終由 `scripts/07` 之 **J1**（Möbius path vs
> brute force m=6：195 = 195、m=8：22050 = 22050）與 **J3**（with-replacement 5.7σ 唔同量）收束。
> 探針為 scratch 檔（O 目錄外），依紀律不入交付物、由 runtime 自動清理。

**第 17 則起（同族續報，合併計）**：`proc_3e2c6054e452`（exit 0，即**現行權威 `06` log 之產出 run**，其命令內含
`rm -rf scripts/__pycache__` 之清潔步驟）經核：`logs/06…out`／`data/06…json` **MATCH**（08:07:37，`5/8 PASS (3 FAIL)`）、
真進程 **0** ⟹ 零動作。**同族續報累計至第 18 則**（第 18 則 = `proc_6444388b3242`，scratch 探針 `o228_null_probe2.py`
之第二次跑，輸出落 scratch `probe2.out`，O 目錄零影響）；每則仍逐次以雜湊核對（判據不變），僅在此累計記錄，
不再逐條列示。

> 註：第 6–15 則皆屬**同一族**（R2/R3/R4 修正過程中之舊版背景 run，或其正式產出 run）。
> 自第 15 則起，同族類同者將**合併為一列**（列「則號區間 ＋ 家族 ＋ 共享判據」），免文檔冗長；
> 判據本身不變（雜湊先行、零動作、記一筆）。

⟹ **七則全部以「雜湊先行」定身份、無一觸發重跑**，凍結產物 sha256 全程未變。

### 第八則（exit 0，`proc_a3bb0c369de9`，同族：`04` 之另一前置修正版）

`logs/04_r2_general_machine.out` **MATCH** `1cf32f268012`（mtime 07:42:32）、`data/04_r2_general_machine.json`
**MATCH** `3416e8dc2471`；真腳本進程 = **0**（`pgrep -af` 過濾後為空）⟹ **零動作、無需重跑**。
（本則與第六／七則同族：R2 修正前之多次 `04` 啟動；三則之共同指紋 = 崩潰/無落地輸出 ＋ 現行檔雜湊不變。）

### 第九則（exit **−9**（SIGKILL），`proc_a3726c2a472c`，**scratch 探針** `logs/08_edge_kmin_probe.out`）

最舊之一則：R2 期間為「M_edge / M_face 之 k_min 上界」而寫之**臨時探針**（非交付物），當時已被
`kill -9` 終止、其輸出檔亦已 `rm` 清除（該探針**已被** `06` 之 early-exit `k_min_search(7)` 取代，
M_edge `k_min = 7` 已由正式引擎給出）。

核帳：`logs/08_edge_kmin_probe.out` **不存在**（經刻意清除）✓；`MANIFEST.json` 覆蓋檢查
**uncovered 0 / stale 0 / hash_mismatch 0**，即磁碟上**冇**任何未覆蓋之殘檔 ⟹ **零動作**。
（依紀律「探針一律寫去 scratch 或收尾前 rm」：本次為**正當清除**，非遺失交付物。）

---

## §6 唯讀完整性（收尾核對）

```
f2cb54fa5df094a1e2f7b4910a4c16726a37160f39b194f0157988823aeb1e7a  o222/scripts/12_b5_budget.py
d8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace  o222/scripts/09_a2_rollback.py
2357006c68e0165dc9fd7d8d73524593a776e1bf6a8b62ddbc8dc2c1a8af20ee  o222/data/04_b2_settings.json
adeaf8a7fb5495ea57be194c1a704c973a9208026cdd10ef615cd59c58005b66  o222/data/08_a2_h_table.json
```
`find o222_qm_evaluation_semantics -newermt 2026-10-02 -type f` = **空**（本輪對上游**零寫入**）。
本輪寫入範圍：`o228_evaluation_resource_geometry/{docs,scripts,data,logs}` ＋ `problem_register/`（登記事件）。

---

## §7 交付物清單

| 檔案 | 內容 |
|---|---|
| `docs/03_r3_contract.md` | R3 凍結合約（H1/H2a-d/v 預註冊）|
| `docs/04_r3_results.md` | 本檔（R3＋R4 結果）|
| `scripts/06_r3_hard_tests.py` | H1（10⁷ distinct MC）＋ H2a-c/b-c/c/v/v-c |
| `scripts/07_null_scope_audit.py` | J1/J1b/J2/J3/J4（口徑審計，獨立重寫 Möbius path）|
| `data/06_r3_hard_tests.json`、`data/07_null_scope_audit.json` | 逐 claim 記錄 |
| `logs/06_r3_hard_tests.out`、`logs/07_null_scope_audit.out` | 完整 stdout |
| `logs/06_r3_firstrun_FAIL_excerpt.out` | 首跑 FAIL 原樣節錄（H1/H2a/H2b）|
