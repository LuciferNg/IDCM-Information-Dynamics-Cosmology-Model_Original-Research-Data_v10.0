# O228 — CLOSEOUT 審計（2026-10-02，第 5 輪；唯讀）

> 用戶指令：「執行 closeout，推導鏈累積太長，一次過審計、更新文檔及 register 更新和核查。」
> 範圍：本 O 目錄內（`open_problems_fresh/o228_evaluation_resource_geometry/`）。跨 O 一律只經 register。
> 審計器：`scripts/24_closeout_audit.py`（**獨立**：唔 import 本 O 任何推導 script；K 由 o222 凍結載入器
> `load_machine()` 取得 = 輸入，非本 O 推導）；`data/24_closeout_audit.json`、`logs/24_closeout_audit.out`。

## 1 判定：**32/32 PASS**（83.4 s）

四類核心獨立重算全部通過：凍結輸入、K 性質、**幀計數**（F_6／F_7／F_4／F_5）、憑證直接核對、
R11 普查聚合、T/O/D4 機器獨立重建、MANIFEST 雙向、register 三向、衛生、文檔覆蓋。

## 2 首輪 28/32 → 4 個 FAIL **全部係審計器自身**（已修，原樣留檔）

| FAIL | 成因 | 處置 |
|:--|:--|:--|
| `B2` | 審計員把 R11 之「60 個相異列向量（30 列機器）」誤當 K 之全列值域 —— K 全列（120 維）**32**，R1 記錄正確 | 改為 `= 32`，另立 `C1b` 核 30 列機器 = **60**（raw 與 ± 類皆 60）|
| `D1`×2 | 比較式 `for k in recd` 越出已算範圍（`M_O`／`M_D4` 只算到 k_min） | 改為 k ≤ 4 全算＋逐 k 對照（`M_O` 1..4、`M_D4` 1..4 全等）|
| `F1` | MANIFEST 生成器自身之宣告式排除未鏡射 | 兩側對稱排除（skill lesson #40／#56②）|
| `H1` | 掃描器**自指命中**（自己原始碼含 forbidden 字面量） | 掃描器排除自身檔 ＋ 字串拼接寫清單（skill lesson #45）|

首跑 log 保留：`logs/24_closeout_firstrun_expectation_bugs.out`；二跑：`logs/24_closeout_secondrun_manifest_sync.out`。

## 3 ★ 獨立重算之 headline（本審計器 vs 原記錄）

| 量 | 獨立重算 | 原記錄 | 節點／耗時 |
|:--|:--|:--|:--|
| `F_6(M_edge)` | **0** | 0（R2/R5）| 38,704,793 節點／8.3 s |
| `F_7(M_edge)` | **8584** | 8584（R2、R11）| **304,315,585** 節點／66.2 s |
| `F_4(M_2I)` | **12645** | 12645（R1/R2）| 700,679 節點／0.2 s |
| `F_5(M_face)` | **320** | 320（R2）| 8,509,971 節點／1.8 s |
| `M_T／M_O／M_D4 F_k` | **全等**（0/12/244/911；0/0/1080/10692；10/45/120/210）| `data/04` | — |
| 逐列出現次數 | **min 812／max 1306**（30 個相異值、全 62 列用）| R11 | — |
| 兩兩互斥 | **17,659,238** | R11 | 3.4 s |
| 幀型（mod ± 列類）| **6960** | R11 | — |
| K：形態／值域／全列相異／秩 | 120×62／{±1}／32／**6** | R1 | 獨立 Fraction RREF |

★ **方法論註（節點數 vs 計數）**：本審計器之 `F_7` 節點數（304,315,585）與 R11（152,157,793）**不同**
（剪枝次序不同），但**計數相同 8584**。⟹ 節點數係實作指紋、計數係不變量；報節點數時必須同時報計數。

## 4 憑證直接核對（由 K 重建，零 import）

- `C2` R10 之顯式 7-覆蓋 `[0,1,4,9,10,15,23]` 分離全部 435 對 ✓（獨立重驗）
- `C3` 根 LP 支撐 `S = [3,4,6,8,9,13,15,18,19,32]`（10 列）之 `x* = ½·1_S` 分數覆蓋全部 435 對
  ⟹ **LP* ≥ 5**（弱對偶原式側）✓
- `C4` `S` 具 **9-冗餘性**：`S∖{a}` 對**每個** `a ∈ S` 仍覆蓋 435 對（10/10）✓ = R12 主結果之獨立重驗

## 5 記錄完整性發現（本輪真 finding；非推導錯）

1. **★ LP 對偶憑證（`y` 向量）未落碟** —— `data/10` 只存證書 flags 與 `sum_x`／`sum_y`，**缺 `x`、`y` 向量**
   ⟹ 上界側（`LP* ≤ 5`）**無法由憑證獨立重驗**（本輪只由原式側確認 `LP* ≥ 5`）。建議 R13 補存向量
   （**不需重算**：重跑 `scripts/10` 並把 `x`／`y` 序列化即可）。
2. **docs 編號債**：`02_r2_contract.md` 與 `02_r2_results.md` **同前綴 02**（R2 兩份），其後自 03 起 —— 沿用
   （register `ref` 已釘死，改名 = 永久 `REF-MISSING`），**記為命名債**，不作更動。
3. **R4（null 口徑審計）無獨立 docs 對**：結果落 `data/07_null_scope_audit.json` ＋ 併入 `docs/04_r3_results.md`；
   已由 `I1` 覆蓋率核實（非缺漏）。
4. **`01_problem_record.md` 自 2026-09-30 22:53 未再更新**（R1–R12 全程零寫入）⟹ 本輪補回 **§八 檔案水位**
   ＋ **§九 推導時序索引**（見該檔）。
5. **`scripts/08_manifest.py` 修訂（impl-only）** —— 見 §7。

## 6 範圍／衛生

- o222 四件 sha256 **4/4 相符**；`find -newermt` 於 o222 之寫入 **0**（全程唯讀）
- 本輪寫入＝本 O 目錄 ＋ `problem_register/register.jsonl`（唯一之跨目錄動作，屬明文允許之 register 通道）
- `scripts/*.py` 內 `/tmp` **寫入模式命中 0**（自指已排除）；scratch 檔（`o228_*`，非交付物）清單見 `data/24`
- MANIFEST 雙向：uncovered 0／stale 0／mismatch 0（審計自身產物兩側對稱排除）

## 7 `scripts/08` amendment（impl-only）

| 項 | 值 |
|:--|:--|
| 修訂前 sha256 | `c942dfb0162be7360efd4bb366e446cedab6a1bc0b2aff4b2d1afcdcc010d46e`（由現檔反推原文重建後哈希，未落碟）|
| 修訂後 sha256 | `7048717d9c04a4aa9be6ae71e2975be70a132c4386068998684ca20fd4cc0e81` |
| 內容 | 新增 `SELF_PREFIX = ('logs/24_closeout','data/24_closeout')` ＋ `rel` 起始比對 ＋ note 文字 |
| 判定謂詞 | **不變**（仍為：docs／scripts／data／logs ＋ 三個 root .md 全收錄，上游 4 件核 sha256）|
| 理由 | 否則審計自身每次執行都令 MANIFEST 恆差 2 件（永久假 FAIL）|
| 影響 | 覆蓋數變動（新檔加入）；`upstream_all_match` 仍 True |

## 8 未閉合項（殘餘）與下一步

母項 `O228` = **partial**（12 輪：R1／R2／R4 closed、R3／R5／R7／R9／R10／R11 partial、R6／R8／R12 negative）。
殘餘 🔴（**同 O 續推，不另開 O**）：① `k_min=7` 短下界憑證（六類憑證空間已窮盡）② `pat(k=6)=26` 精確
③ `λ_min=12`（11 線）④ 缺口律非 m 之函數 ⑤ 最小關係長度 ↔ 幀最小性（Zarankiewicz）⑥ 刪除譜類數
⑦ 幀側零冗餘 vs 生成側 58/62 冗餘 ⑧ `T|(1,1,2)` LP 不緊之結構原因 ⑨ 8584 幀在 `|GeoAut|=60` 下之軌道分解
⑩ **R13 候選**：普查型非負係數割判別 `M`（10×8584 小 LP；`M>2` ⟺ 存在分離割）＋ 本報告 §5.1 之
`x`／`y` 向量補存。

## 9 最終唯讀核對（MANIFEST 之後；本輪最後一步）

`MANIFEST.json`（`scripts/08`，**本輪最後一個寫入動作**）刷新後，只跑唯讀核對：覆蓋雙向 0 差、
逐檔 sha256 mismatch 0、上游 4/4、無殘留背景進程。輸出：`logs/24_closeout_final_verify.out`（24 族，屬
宣告式排除之審計自產物）。
