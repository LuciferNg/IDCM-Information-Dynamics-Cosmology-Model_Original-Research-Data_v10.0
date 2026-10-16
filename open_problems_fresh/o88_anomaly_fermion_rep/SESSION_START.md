# O88 — Anomaly + Fermion Representations ✅

> **Session**: 2026-08-25→26
> **狀態**: 🟢 **46/46 PASS — 閉合完成**
> **來源**: O85 剩餘開放問題 #1
> **前置**: O85, O59, O54

---

## 定位

SU(12) → SM breaking chain 嘅 anomaly cancellation 檢查，以及 fermion 表示指定。

## 問題

1. SU(12) 嘅 anomaly coefficient 係咩？(SU(12)³, SU(12)²×U(1), grav²×SU(12))
2. 3 代 SM fermions (48 Weyl fermions) 點嵌入 SU(12) 表示？
3. Decomposition under SU(4)×SU(3) tensor embedding
4. Anomaly-free 嘅表示組合？

## 答案

**推薦嵌入: 3×(12⊕12̄) = 72-dimensional, anomaly-free (A=0)**
- 36 = 3×12 = h11 = K_tree + N_gen = 33+3 ✅ (IDCM 直接對應)
- 36̄ = 3×12̄ = h11 嘅共軛
- 48 SM Weyl fermions + 24 vector-like 配對

**12 = (4,3) → (3,3)_{1/3} ⊕ (1,3)_{-1} = 9 左旋夸克 + 3 左旋輕子**
**12̄ = (4̄,3̄) → (3̄,3̄)_{-1/3} ⊕ (1,3̄)_{1} = 9 右旋反夸克 + 3 右旋反輕子**

## 交接點

```
來源: O85 docs/02_breaking_chain_report.md
狀態: 🟢 46/46 PASS — 閉合完成
參考: docs/02_closure_report.md
```

## 相關資源

```
- O85 docs/02_breaking_chain_report.md — breaking chain 結構
- O59 scripts/22_su12_extension.py — su(12) 結構
- O54 — SM 質量閉合 (CKM/PMNS)
- O88 docs/02_closure_report.md — 完整閉合報告
- O88 scripts/03_verifier.py — 46/46 PASS
```

## 未閉合問題

| # | 問題 | 狀態 |
|:-:|:-----|:----:|
| 1 | Vector-like 配對質量譜 | 🟡 未推導 |
| 2 | 24 個 vector-like 配對的質量標度 | 🔴 未計算 |
| 3 | SU(12)²×U(1) 詳細驗證 | 🟡 需 U(1) embedding |
| 4 | 與 O89 mass hierarchy 耦合 | 🔴 獨立問題 |

---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **6 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o88_anomaly_fermion_rep/scripts/01_anomaly_coefficients.py:362` | `open_problems_fresh/o88_anomaly_fermion_rep/data/01_anomaly_coefficients.json` |
| 2 | `o88_anomaly_fermion_rep/scripts/01_anomaly_coefficients.py:363` | `open_problems_fresh/o88_anomaly_fermion_rep/data/01_anomaly_coefficients.json` |
| 3 | `o88_anomaly_fermion_rep/scripts/02_fermion_embedding.py:243` | `open_problems_fresh/o88_anomaly_fermion_rep/data/02_fermion_embedding.json` |
| 4 | `o88_anomaly_fermion_rep/scripts/02_fermion_embedding.py:244` | `open_problems_fresh/o88_anomaly_fermion_rep/data/02_fermion_embedding.json` |
| 5 | `o88_anomaly_fermion_rep/scripts/03_verifier.py:398` | `open_problems_fresh/o88_anomaly_fermion_rep/data/03_verifier_results.json` |
| … | （另有 1 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：6 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。

---

## ★ Closeout 審計註記（2026-10-02，append-only）

> **本節唔改動上方任何內容。**
> 觸發：調律者指令「執行新推導前先作一次整個 o88 session 鏈進行一次完整 closeout」。
> 完整記錄：`docs/03_audit_report.md` ／ 提交摘要：`final_result.md`

### 〇. 對上文「全樹路徑衛生審計註記」之裁決

```
✅ 已接納  ✅ 已處理（就地修，屬本 O 自己目錄，符 §5.2）
```

| 項 | 外部審計稱 | 實際 | 處置 |
|:---|:----------|:-----|:-----|
| ghost-tree call site | 6 處 | **3 條源碼行**（01:361、02:242、03:20）× 各自 makedirs/open 使用點 = 6 | 3 行全部改 `__file__`-相對；`grep /home/wsl scripts/*.py` → **0 命中** |
| `03_verifier.py:398` 之 `OUT_DIR` | ghost 下路徑 | 同源 | 改 `OUT_DIR = BASE` |

**實測後果（本輪親自驗證）**：真樹跑 `scripts/01` → exit 0、印「✅ 結果已保存」，
但**真樹 data/01 mtime 不變**（仍 2026-08-26 17:55:39），ghost tree 被即場創建副本
⟹ **重跑從未更新本目錄產物**；「46/46 PASS」若靠重跑確認，確認嘅係 ghost 副本。

修正後重跑：本目錄 `data/*.json` mtime **全部 → 2026-10-02 14:22** ✅
（`data/02`、`data/03` byte-identical = 確定性；`data/01` 按 §三 有 2 值更正）。
本輪於 ghost tree 建立之探針（`_baseprobe`、o88 ghost 目錄）**已即時刪除**，恢復原狀。

### 一. 審計發現（詳見 docs/03）

| # | 發現 | 嚴重度 |
|:-:|:-----|:------:|
| F1 | **A(Λ⁴) 18 → 48、A(Λ⁵) −14 → 42**（封閉式不成立；Λ⁵ 原式給 −13.5 被 `//` 掩蓋） | ★★ 真錯 |
| F2 | `avail` 字典**硬編碼** 495→55、792→78（同檔第三個值）⟹ 組合搜尋受污染 | ★★ 真錯 |
| F3 | `scripts/01` 搜尋空間「≤4 槽」**容納唔到** 3×(12⊕12̄)（需 6 槽）| ★ 設計缺陷 |
| F4 | 全部 script 硬編碼 ghost path ⟹ 重跑唔更新本目錄 | ★★ 真缺陷（已修） |
| F5 | `03_verifier.py` 46/46 中 **18 項為 `check(..., True)` 空洞斷言** | ★ 方法論 |
| F6 | 異常自由組合數 78 → **80**（01 空間）／**205**（權威多重集空間） | 連帶 |
| F7 | O88 目錄**零 git 追蹤**；docs/01 曾於 08-26 被整檔覆寫 | 記錄層風險 |

### 二. 主結論判定

```
🟢 主結論 3×(12⊕12̄) = 72、A = 0 —— 不受影響，且經獨立方法（權重法）確認
   A(12) = +1、A(12̄) = −1 本就正確；A(66)=8、A(78)=16、A(143)=0 亦正確
```

**新增強化證據（權威密度基準）**：

```
N_search = 12217（SU(12) 不可約表示多重集，總維度 ≤ 400）
A = 0 且 dim ≥ 48 → 205 個
dim = 72 ∧ A = 0 → 恰 1 個 = 3×(12⊕12̄)          ★ 唯一
N_mc = 10⁷ (seed 88)；MC z = 1.31 ✅；q_obs = 1.93% 🟢
結構剛性：2(K_tree+N_gen) = 72 只在 N = 12 成立
```

### 三. 新登記面

```
register:  O88/proton-decay  ← 2026-10-02 調律者指示（v9 τ_p 6.1×10³⁴ yr 之 v10 重建）
狀態:      🆕 registered（本輪攻堅）
```

### 四. 未閉合問題表（更新，取代上方 §「未閉合問題」）

| # | 問題 | 狀態 | 歸屬裁決 |
|:-:|:-----|:----:|:---------|
| 1 | Vector-like 配對質量譜 | ✅ 已閉合 | **O108**（23/23，2026-08-29）— 唔重做 |
| 2 | 24 個 VL 配對之質量標度 | ✅ 已閉合 | **O108** — 唔重做 |
| 3 | SU(12)²×U(1) 詳細驗證 | 🟡 | O88（需 U(1) embedding 細節）|
| 4 | 與 O89 mass hierarchy 耦合 | ✅ 已閉合 | **O89**（46/46）— 唔重做 |
| 5 | 規範耦合統一 @ M_GUT（o110 B1 掛 O88）| ✅ 已閉合 | **O89** — 屬上游 stale，只記錄 |
| 6 | 質子衰變 τ_p | 🆕 | **O88 本輪** |

### 五. 交叉 O 裁決（§8.1：只登記，唔改上游檔案）

| O | 其檔內 stale 項 | 裁決 |
|:--|:----------------|:-----|
| O96 | `docs/01:307`、`SESSION_START.md:113` 遺留 5「VL 質量譜 72→48」標「需新 O (O88 延伸)」🔴 | 實已由 **O108** 閉合 ⟹ **上游 stale，只記錄** |
| O110 | `docs/03` B1 規範耦合統一掛「關鍵 O = O88」 | 實已由 **O89** 閉合 ⟹ **上游 stale，只記錄** |
| O110 | `docs/03` B11 質子衰變掛 O88 | ✓ 正確 ⟹ 本輪攻堅 |
| O137 | `docs/37` #6「O88 已閉合，引用唔開」 | ✓ 正確 |
| O137 | `docs/36:415` 質子衰變指數 528/37/47 | 併入本輪攻堅 |

> ⚠️ 依 skill `idcm-closeout` §8.1，**唔改上游任何檔案**（含其 SESSION_START）。
> 本裁決記於此 ＋ register 事件。

---

## ★ 質子衰變推導註記（2026-10-02，append-only）

> register `O88/proton-decay` 攻堅完成。**本節唔改動上方任何內容。**
> 報告：`docs/04_proton_decay_report.md` ／ 腳本：`scripts/06_proton_decay.py`（10/11 PASS）

```
結構 : N_LQ = 48 個色三重態 leptoquark ∈ (15,8) @ M_GUT = M_Pl·γ₁ = 6.2214e16 GeV
公式 : arXiv:2401.16907 eq.(4.47)，已用 minimal SU(5) 校準 ✅
預言 : τ_p(p→e⁺π⁰) ∈ [2.89e38, 1.39e40] yr
判定 : 🔴 超出 Hyper-K 10yr 投影 (1e35 yr) 3–5 個數量級
       ⟹ v9「在 Hyper-K 靈敏度範圍內」唔成立
★ v9 legacy 偽證: 6.1e34 yr 用 v9 自己 M_X 都重現唔到（差 47–2200 倍），
        v9 樹冇推導腳本 ⟹ 不可重現 legacy claim
🔴 外部依賴: QCD 矩陣元 0.134 GeV²、A_L = 1.4
```

### 登記
```
register: O88/proton-decay → 已計算（progress）
```


---

# O88 檔案位置對齊 (2026-10-02) — `01_problem_record.md` 移至 O 根目錄 (⚠️ 本段為新增, 以上原文一字不刪)

> 調律者指令: 「O88 的 problem record 現時放在 docs, 調整文件位置跟隨其他 o 相同」

## 事項

| # | 項 | 內容 |
|:-:|:---|:-----|
| 1 | **搬遷** | `docs/01_problem_record.md` → **`01_problem_record.md`（O 根目錄）** |
| 2 | **零字節改動** | sha256 搬遷前後皆 `f0a00870ffdfc0d1…9a703b`（byte-identical ✅） |
| 3 | **備份** | `~/.hermes/backups/docs__01_problem_record.md.v22pre.20261002_161427`（正典備份庫，O 目錄外） |
| 4 | **`docs/01` 保留為路徑指標** | 令 `docs/02_closure_report.md:15`、`docs/03_audit_report.md:24/196/286` 既有引用仍可解析 —— 該等屬**審計記錄（歷史事實）**，依文檔歷史完整性規則**不予改寫** |

## 慣例依據（實測全 222 個 O 目錄）

| 形態 | 數目 |
|:-----|:----|
| `01_problem_record.md` 在 **O 根目錄** | **151** |
| 只在 `docs/` | 55 |
| 兩者兼有（root = 正本，docs/ = 歷史快照） | 16 |

→ **root 為慣例**。對照範本: `o175_entropy_theorem/`（`o175` 為 root 形態）。

## 目錄形態（對照後）

```
o88_anomaly_fermion_rep/
├── 01_problem_record.md      ← 本輪搬入（正本；原 docs/01_problem_record.md）
├── SESSION_START.md
├── final_result.md
├── docs/   01（路徑指標）02 閉合 03 審計 04 質子衰變
├── scripts/  01–06
├── data/  +  logs/
（搬遷前備份已置於正典備份庫 `~/.hermes/backups/docs__01_problem_record.md.v22pre.20261002_161427`
     及 `…/o88_anomaly_fermion_rep__SESSION_START.md.v22pre.20261002_161427`，O 目錄外）
```

> ⚠️ 本節為**附加記錄**，以上原文一字不改。


---

## 2026-10-02（晚）— PD #1 推導：N_LQ = 48 相干 vs 非相干（群論 Clebsch）

> ⚠️ 本節為**附加記錄**（append-only）。以上原文一字未改。

**承接**：§「O88/PD — 質子衰變」建立後，`docs/04` §未釘死項 #1 = 「N_LQ 相干 vs 非相干（群論 Clebsch）🔴 48× 不確定度」。
本輪完成該項，並**否證其核心前提**。

### 產物

| 檔案 | 狀態 | 大小 / sha |
|:--|:--|:--|
| `scripts/07_clebsch_closure.py` | 新增（v3，24 檢查）| 17,855 B |
| `logs/07_clebsch_closure.out` | 新增（執行輸出）| — |
| `data/07_clebsch_closure.json` | 新增（結構化結果）| — |
| `logs/07_clebsch_closure.v2_superseded.py` | 新增（v2 全文；修訂時序證據）| sha `06b7530d4677205f…` |
| `docs/06_pd1_clebsch_closure.md` | 新增（報告）| — |
| `01_problem_record.md` | 附加 §十（+2,150 B；前綴 byte-identical）| 前 sha `f0a00870ffdfc0d1` |
| `docs/04_proton_decay_report.md` | 附加「更正附註」（+1,863 B；前綴 byte-identical）| 前 sha `7167ad649ca23391` |
| `final_result.md` | 附加「PD #1 收口」（前綴 byte-identical）| 前 sha `8efae55f52d66807` |

備份：4 檔皆先硬編碼備份至 `~/.hermes/backups/*.pd1pre.20261002_205712`（sha 逐檔核對一致）。

### 推導摘要

1. **結構設定**：`(15,8)` coset generator = `T^A_PS ⊗ t^a_F`（張量積）；`12 = 4 ⊗ 3`。
2. **主結果**：LQ generator support 只喺 `(q,l)/(l,q)` ⟹ **無 diquark 耦合**
   ⟹ 單 boson 交換 `max|ΔB| = 2/3 < 1`（全 120 coset）⟹ **`N_channel(|ΔB|=1) = 0`**。
3. **副定理**：48-生成元和 `= (6-和)×(8-和)`（實測 maxdev 3.469e-18）；
   `SU(3)_F` adjoint 對 family-singlet 收縮 = 0（Schur）⟹ 48 / 48² / 8 / 6 全排除。
4. **處置**：`τ_p ∈ [2.89×10³⁸, 1.39×10⁴⁰] yr` **撤回**（前提失效）。
5. **新開放項**：ΔB=1 須由 **scalar 扇區**（Higgs leptoquark）提供 —— 未分析。

**檢查**：24/24 PASS。

### 修訂時序（append-only）

- **v1** → S7 FAIL 抓到閉式漏 colour 索引限制
- **v2** → 修正閉式；但「pair-tensor 冪等」命題本身錯誤（正確命題係 Casimir），
  且不變張量收縮全為 0 而未被解讀 → crash。全文保留爲 `logs/07_clebsch_closure.v2_superseded.py`
- **v3** → 解讀全 0 收縮 ⟹ 發現主結果；24/24 PASS

### 待辦（本 O 未閉合）

- 🔴 ΔB=1 算子之 scalar 扇區來源（新 PD 項）
- 🔴 `scripts/03_verifier.py:75` 錯閉式未收口（見 `docs/05_record_chain_audit.md` §八）
- 🟡 `docs/04` §9.5 #2–#4（SU(3)-family gauge/global 身份、QCD 矩陣元、其他衰變道）


---

## 2026-10-02 — PD #2（Scalar 扇區之 ΔB=1 算子）收口

**範圍**：PD #1 直接生成之餘項 —— 「`ΔB=1` 須由 scalar 扇區供給」之完整群論收口。
**腳本**：`scripts/08_pd2_scalar_sector.py` v1，**39/39 PASS**。
**報告**：`docs/07_pd2_scalar_sector.md`。

### 產物
* `scripts/08_pd2_scalar_sector.py`（v1，39 項檢查）
* `logs/08_pd2_scalar_sector.out`、`data/08_pd2_scalar_sector.json`
* `docs/07_pd2_scalar_sector.md`
* 記錄 append：`01_problem_record.md` §十一、`final_result.md`、`docs/04`（更正附註）、本檔
* 備份：`~/.hermes/backups/*.pd2pre.20261002_221101`

### 三項主結果
1. **T1 定理**：Adjoint 143 **唔可能**實現 `SU(12) → SU(4)×SU(3)`
   （`143` 冇 `(1,1)`；`12 = (4,3)` 不可約 ⟹ Schur ⟹ commutant = `ℂ·1`；
   實測維數 1；獨立判據：adjoint 保秩 11 ≠ 5；陽性對照 SU(5) commutant = 2 ✓）
2. **記錄框架內零個 ΔB=1 算子** ⟹ **質子絕對穩定**（renormalizable level）；
   重力壓低 `τ_p ~ 6.4×10⁴⁴ yr`
3. **ΔB=1 之最小 scalar 來源** = `Λ²(12) = 66`（`= 2·K_tree`）或 `Sym²(12) = 78`；
   `N_{ΔB=1} = 9`（**唔係 48**）

### 對舊 claim 之處置
* `docs/04` `N_LQ = 48` / `τ_p` 範圍 → 已撤回（PD #1）
* `docs/04` 「120 個 (15,8) boson」之 group 身份 → 否證（PD #2）
* O85 `docs/02` 鏈第一步 → 否證（PD #2）⟹ **開放項移交 O85，只在 register 登記**

### 修訂時序（自我抓到）
| 版本 | 錯 | 抓法 |
|:--|:--|:--|
| v1 S14 | commutant 生成元用 `E_ij⊗E_00` 而非 `E_ij⊗I_3`（nullity 37） | 自身檢查 FAIL |
| v1 S18 | 硬編 `dim(2,1) = 594`（正確 `572 = 12·143/3`） | hook formula 自檢 |
| v1 S25 | `τ_p` 換算倒轉（1.47e93 yr → 6.37e44 yr） | 量級自檢 |

### 下一步
PD 線（#1 gauge 扇區 + #2 scalar 扇區）**兩者已閉環** ⟹ O88 之 proton-decay 子題**結構性結案**。
餘：`scripts/03_verifier.py:75` 錯閉式（未就地收口，見 `docs/05`）；鏈第一步之正確 Higgs ⟹ O85。


---

## 2026-10-02 — 缺陷收口 + PD #3（剛性測試）

### 本輪產物
* `scripts/09_anomaly_first_principles.py`（v2-int，**20/20 PASS**）—— 三階異常第一性原理計算
* `scripts/10_pd3_rigidity.py`（**10/10 PASS**）—— PD #2 判定之結構剛性測試
* `docs/08_anomaly_verifier_closure.md`、`docs/09_pd3_rigidity.md`
* `scripts/03_verifier.py` **已修**（46/46 PASS；`A(495) 18→48`、`A(792) −14→42`）
* 備份：`~/.hermes/backups/*.vfix.20261002_231256`（03 三檔）、`…*.pd3pre.20261002_2317xx`
* 時序證據：`logs/03_verifier.v1_superseded.py`（sha `5b9f83c5a81fc1da…`）、
  `logs/09_anomaly_first_principles.v1_superseded.py`（sha `e489747064a0a9b3…`）

### A. 缺陷收口（root cause）
`03_verifier.py:75-76` 之擬合閉式（Λ⁴→18、Λ⁵→−14）已**刪除**，改為第一性原理：
`A(R) = Σ_μ m_μ t_a t_b t_c / Σ_fund t_a t_b t_c`（`t_a = μ_a − μ_{a+1} ∈ ℤ`）。
三重驗證：13 known（N=5..13）／60–66 triple 共識／對偶律。
★ 原閉式只在 N=7 對（由對偶律強制）⟹ 單點吻合 = 假訊號。
恆真斷言（`check(..., True, ...)`）亦拆除 → 13 條實質檢查。
**⟹ `docs/05` 所述「唯一真缺陷」收口；O88 自身無未閉合項。**

### B. PD #3 剛性
* 完備判據：ΔB=1 ⟺ scalar 含 SU(4) `6`/`10`（合格者恰 `{6,10}`）
* 記錄 scalar 集合 → 0（重現 PD #2）；完備普查最小 = `Λ²(12) = 66 = 2·K_tree`
* ★★ 擾動：fundamental VEV（T1 後最自然之代替）色三重態 `B−L = 1/3` ⟹ 仍無 ΔB=1
* ⟹ **判定對 T1 之修正剛性成立**；逃生路線 = 加 `66`/`78`，`N = 9`，`τ_p` 變一自由參數

### 修訂時序（自我抓到）
| 版本 | 錯 | 抓法 |
|:--|:--|:--|
| 09 v1 | `Fraction` 版太慢 + tuple 相減 / ntr 未綁定 | Pyright + 計時 |
| 10 v1 §4 | 判據寫窄（`λ==(1,1)`，漏 SU(4) 對偶律） | **與 scripts/08 交叉比對** |
| 10 v1 §S2b/S3 | 期望清單範圍 / 排序假設錯 | 自身檢查 FAIL |

### 下一步
PD 線三輪全閉環。餘：O85 鏈第一步 Higgs（register 已移交）；
`66 = 2·K_tree` 與 ΔB=1 通道之結構關聯（是否結構強逼）🟡。


### 追加（同日，遲到通知觸發）
* 遲到背景通知 `proc_dc340220815c`（v1）鑑定：sha `e489747064a0a9b3…`，行 92/105/151 逐字命中 ⟹ 身份確定，**只核不重跑**。
* ★ 通知携真資訊：v1 crash 真因 = **空權重集**（該 N 下唔存在之 rep）。
  v2 同一輸入由「大聲 crash」變成「**靜靜回 A = 0**」（維數守衛兩邊都係 0 ⟹ 失效）—— silent 類缺陷。
* 修法 v2.1：`consensus_A` 對空集 **raise**；`REPS` 對 dim=0 明確跳過；新增 **S0** 實質檢查。
  **21/21 PASS**（原 20 + S0），`A(Λ⁴)=48` / `A(Λ⁵)=42` / `N12` 全部不變。
* 時序：v2 → `logs/09_anomaly_first_principles.v2_superseded.py`（sha `064bb461bd927aee`）。
* 教訓：**v1 crash 之位置唔可當效能問題** —— 換版要問「同一輸入新版會點」，唔 crash 就要問「處理咗抑或吞咗」。

### 追加更正（同日，用戶指正）—— ★ 撤回「重力壓低 dim-6」
* 用戶指正：「重力壓低好像並非 IDCM 的理論」。**查證成立**。
* 鑑定：`重力壓低` **唔喺** 08-26 原始 `docs/04`；由**本輪 PD #2 `docs/07 §6` 引入**，
  傳播至 `docs/07`(4處)、`final_result.md`(3處)、`01_problem_record.md`、`docs/04` banner、`SESSION_START.md`、`README.md`。
* 理由：`Γ ~ m_p⁵/M_Pl⁴` 係 **Wilsonian EFT**（4D 連續度規 + `M_Pl` 作 cutoff + 局部算子）；
  IDCM 係離散晶格 `K_chain⊗K_tree`；且 `M_Pl` 於 O212 只係**單位換算錨**；
  更根本 —— dim-6 來源 `(15,8)` coset 交換已由 PD #1 排除 ⟹ 對唔存在之算子談 Planck 壓低 = **空運算**。
* 更正後：IDCM 內部**冇任何** `ΔB=1` 算子 ⟹ **`τ_p = ∞`（結構判定）**；唔可用外部 EFT 式填有限值。
  可證偽性 = 「框架內無此道 ⟹ 永不見到」（去掉「除重力壓低外」）。
* IDCM 內部破 `B` 候選（全部 🔴 未推導）：① 拓撲位元寫入（阻挫邊／相位滑移 `π`）② 返池（`η=φ⁻²¹`，率🔴）③ 晶格端點缺陷（O229）。
* **不受影響**：PD #1(24/24)、T1 定理、零 `ΔB=1`、PD #3(10/10)、`03_verifier`(46/46)、`09`(21/21) —— 皆零外部輸入。
* 教訓：引入外部估計式必須**當場標明「外部」**。


### PD #4（2026-10-02，用戶指令 A+B）
* 交付：`scripts/11_branch_pair_protection.py`（**11/11 PASS**）、`docs/10_branch_pair_proposition.md`
* **A**：`B = 4` = `K_tree` 分支數（結構整數）；O229 九路線全唔用 `N_c`（可證偽表獨立重現）；
  命題 P 形式化 + 三個可否證條件
* **B**：★ 裁定「**唔係等價**」—— PD#1/#2 之「含 6/10」判據係**充分非必要**；分支對偶只刻劃最小載體
* ★★ **自我更正**：PD #3 §2.1「完備判據」**不完備** —— 正確 = 「colour (反)三重態 ∧ |B−L| = 2/3」；
  合格 `SU(4)` dims = `{6, 10, 64, 70, 270, 300}`；工具 = Pieri + 維數守恆自檢（違例 0）
* v1 兩 bug（時序）：`horiz_strip` 非交錯條件；`μ` 只枚舉 `|μ|=|λ|` → `logs/11_...v1_superseded.py`（sha `0ac41263a9b020d7`）
* **結論不變**：記錄 reps `{4,4̄,15,1}` 全部唔合格 ⟹ `τ_p = ∞` 維持；逃生路線擴大
* 教訓：**「只用維數判據」＋「自稱完備」＝最高風險組合**；自稱完備須配獨立守恆律自檢


### PD #4 殘留項完成（2026-10-03）：外部約束登記
* 交付：`scripts/12_external_constraints.py`（**7/7 PASS**；首跑 6/7 = check bug，已修並保留首跑 log）、
  `docs/11_external_constraints.md`
* **E1**：三端點算術對比（零重推 O139）—— `137/137.035999177`（−0.026269%）、`128/127.930(8)`（+8.750 σ）、
  `9/9.1060(8)`（δ = +0.105999）；★ 名義 pull 唔係正確儀器
* **🚫 v7 禁區**：`134+3+15/(φ·256) = 137.036212929` 已由 O204 null 否證（rank 38/7497；12,623 ≫ 9,326）
* **E2**：SK `2.4×10³⁴` / Hyper-K `~1×10³⁵` ⟹ 相容但**零檢驗力**（單向可否證）
* ★★ **九路線逐條各自充分**（真算 `B=1..12`）⟹ **零外部接觸 6 條**（R2/R3/R4/R6/R7/R12）；R5/R8 有保留
* **不可外部驗證清單 6 項** + 逐條 N/A 理由；**拒絕假做 MC**（代數恆等無定義域）
* 更正：`docs/04` Super-K 行（banner 之三）；`docs/10` §11（A 節 E1 遺漏 + 「8 條」措辭）
* 裁定：`B = 4` 對 E1 **不敏感**；E2 **單向** ⟹ 核心判定外部數據既唔能確認亦唔能推翻


### 第二輪殘留完成（2026-10-03）：逃生路線完整枚舉 + ★★ 封閉性撤回
* 交付：`scripts/13_escape_route_enumeration.py`（**8/8 PASS**；首跑 6/8 = check 期望錯）、
  `docs/12_composite_channel_audit.md`
* **(A)** 逃生路線完整規格：`Λ^k(12)`／`Sym^k(12)` 含合格分量 **⟺ `k ≡ 2 (mod 4)`**（`{2,6,10}`）；
  維數守恆 `k=2..12` 違例 0；`Λ⁶(12)` 含**四個**合格分量（首輪「例」核實並升級）
* **(B) ★★ 封閉性撤回**：`4 ⊗ 4 = Λ²(4) ⊕ Sym²(4) = 6 ⊕ 10` 兩者**皆合格** ⟹
  「封閉組合生唔出合格載體」**為假**；含 adjoint 之案真算無合格分量 ✓（首輪此部分正確）；
  錯誤位置 = `elementary 場清單 → 全算子空間`（**non sequitur**）
* **(C)** `τ_p = ∞` 改**條件式**：(i) elementary 扇區 ✓ 已證 ＋ (ii) 算子扇區（`dim ≥ 5`）🟡 未排除
* **(D)** 維持：PD #1、PD #2/#3 表示論結論、PD #4 判據修正、最小 `66/78`、九路線、零外部 6 條、
  `docs/11` E1／E2
* **(E)** 新開放問題：`O88/composite-dB1-channel`（register, open）
* 方法：兩獨立算法（SU(3)⊗U(1) 分裂；SSYT 支配序剝去法）+ 維數守恆自檢
* 陷阱：GL(4) 標籤 ≠ SU(4) 標籤（GL `(1,1,1,1)` = 行列式 = SU(4) 平凡）
* 算法 bug 一處（剝去方向）已修；v1 憑記憶之分解已廢棄（sha `bed6f6dfcc9689af`）

---

## 附註（append-only，2026-10-15）

> ⚠️ **舊鏈標籤提示**：本檔所引 `SU(4)×SU(3)`／`(4,3)`／`T₃R`／`B−L = 4=3⊕1` 屬 O85 **舊鏈**框架。
> O85 已由零重建（新鏈 `12 = (3,1) ⊕ (1,2) ⊕ 7×(1,1)`；O85 `docs/05_fermion_reps.md` 22/22、
> `docs/11_rep_consistency.md` 14/14）。
> 本檔之**數值結論**維持 ✓；**表示論推導路徑**之新鏈審查見 O88
> `docs/13_composite_channel_verdict.md`（O210 判定吸收，71/71）＋
> `docs/14_fermion_rep_newchain.md`（費米子重核，41/41）。
> ★ 本附註為**新增**，本檔原文一字未改。


### 2026-10-15 — O85 新鏈重核（docs/13、docs/14）

* **docs/13_composite_channel_verdict.md**（`scripts/14_o210_verdict_absorb.py` **71/71 PASS**）：
  吸收 O210 判定（T2 docs/07、T3 docs/08）——三條充分條件全閉合：① **假**（T2 類型層零壓制，
  `Λ^k/Sym^k` 可由 ⊗+Proj 構造；S1 維數全 k 真算）；② **超代數層不可達**；③ **唔壓制**
  （T3：分支荷中性 ⟺ `k ≡ 2 (mod B)` = T1；S4 暴力子集 k∈{2,6,10} 全過；S5 反例 k=0/4/8 非中性）。
  ⟹ **`τ_p = ∞` 唔可以由 IDCM 現行代數／譜結構導出**。
  ★★ **鏈依賴審查（本 O 新判）**：T2 鏈無關 🟢 維持；T3 之分支荷 = `SU(B)=SU(4)` 中心荷屬
  **舊鏈 `12=B·N_c=4·3`** ⟹ 新鏈下**定義域消失** 🔴；條件③ 重新開放（約束：須過三檢）。
* **docs/14_fermion_rep_newchain.md**（`scripts/15_fermion_newchain.py` **41/41 PASS**）：
  新鏈 `12 = (3,1) ⊕ (1,2) ⊕ 7×(1,1)`。鏈無關維持 ✓：`3×(12⊕12̄)=72=2h11`、`A(12⊕12̄)=0`、
  `12≇12̄`（Dynkin `(1,0¹⁰)≠(0¹⁰,1)`）、SM 48=3×16、**異常 8 條 = 0**（Y 版+B−L 版，精確 Fraction）、
  電荷 ⊂ (1/3)ℤ。🔴 舊鏈標籤作廢：`(4,3)`、`Y=T₃R+(B−L)/2`、`B−L=4=3⊕1`、`M_GUT/M_PS/M_R` 階梯。
  ★★ **新鏈 SM 場來自複合層**：`66 = Λ²(12) = 3̄ ⊕ (3,2) ⊕ 7(3,1) ⊕ 1 ⊕ 7(1,2) ⊕ 21(1,1)`；
  每代 16 = 66 提供 10（Q_L、u^c、e^c）+ 12̄ 直接 6（d^c、L、ν^c）；fundamental 層**冇 (3,2)**；
  66 剩餘 **56 場**待完整 `y_i` 指派（7 個單態超荷）。
* **開放項 4 條**：① 新鏈 `ΔB=1` 合格判據（`Λ^k(12)` 分解 + `SU(3)_c×SU(2)_L×U(1)⁸` 語義）；
  ② 新鏈分支荷定義（過三檢）；③ 66 剩餘 56 場 vl/molecule（y_i 屬 O85 開放項）；④ X/Y 載 B−L。
* 11 個既有檔（`01_problem_record`／`final_result`／`SESSION_START`／`docs/02,04,06,07,09,10,11,12`）
  加 **append-only 橫註**（舊鏈提示，指 docs/13、14）—— 原文一字未改。
* ⚠️ 本輪只寫 O88 目錄；O85 / O210 檔案一字未動（跨 O 只經 register）。


### 2026-10-15（續）— Gap #1：新鏈 ΔB=1 判據（docs/15）

* **docs/15_newchain_db1_judgement.md**（`scripts/16_newchain_db1_judgement.py` **36/36 PASS**）
* **S1** adjoint 143 新鏈分解：`19 + 12 + 42 + 28 + 42 = 143` ✓；**X/Y = 12 個色-弱交叉** `(3,2)+c.c.`
  （adjoint 跨塊分量，唔喺 fundamental 層）
* **S2/S3** `Λ^k(12)` 新鏈分解全 k=0..12 維數和 = `C(12,k)` 精確；★ **新鏈 fundamental 層已有色載體**
  （k=1 即 `(3,1)`），舊鏈要 `Λ²(4)=6⊕10` 先有 —— 根本不同；`Λ³(3)=1` ⟹ 3 色可成 singlet
* **S4 ★★ 新鏈超荷指派閉合**：`Y(色 fund) = a = −1/3`、`Y(弱 fund) = b = +1/2`
  ⟹ `Q_L=a+b=1/6`、`u^c=2a=−2/3`、`d^c=−a=1/3`、`L=−b=−1/2`、`e^c=2b=1`、`ν^c=0`
  **六個 SM 超荷全部自動出，零額外參數**；`a:b = −2:3 = H(2,−3)` 方向（O85 docs/03 §B 一致）
  ⚠️ 跨 O：此係 O85 docs/05 §六 🟡 開放項，**只經 register 交 O85 裁決**（本檔唔改 O85 檔案）
* **S5 🔴 B 數唔喺 `U(1)⁸`**：色:弱 需 2:−3，但 `B = diag(1/3·I₃, 0…)` 弱=0 ⟹ α 矛盾（0 vs 1/6）
  ⟹ **B 係外部／全域量子數**（舊鏈由 `SU(4)_PS` 之 `4=3⊕1` 提供 `B−L`，新鏈**冇**此來源）
  X/Y 之 `ΔB = ±1/3`（色-弱交叉），3 色合成 `ΔB = 1`
* **S6** 舊/新鏈判據對照表；裁定：載體層**已重推** ✓、量子數層**待 B 算子定義** 🟡
* 新增開放項 3 條（B 算子定義、`y_i` 指派（掛 O85）、`Λ^k` 帶色分量 gauge-invariant 完備普查）
* ⚠️ 本輪只寫 O88 目錄；O85 / O210 檔案一字未動


### 2026-10-15（續）— Gap #2：新鏈分支荷 → 條件③ 可達性（docs/16）

* **docs/16_newchain_branch_charge_verdict.md**（`scripts/17_newchain_branch_charge.py` **42/42 PASS**）
* **候選①`SU(3)_c` 中心荷 `ℤ₃`**（`χ = p+2q mod 3`，Dynkin）：三檢全過 —— dim 重核
  `(p+1)(q+1)(p+q+2)/2` 中；χ 表 `1(0),3(1),3̄(2),6(2),6̄(1),8(0),15(1)`；(a) 加 fundamental ⟹ `χ+1`；
  (b) 真分解 `3⊗3̄, 3⊗3, 3⊗8, 8⊗8` 維數守恆 + 每分量 χ 一致；(c) 純組合 ⟹ **well-typed ✓**
* **壓制判定 ❌**：`ΔB=1`（3 色 fundamental）`χ_total ≡ 0` 中性；但 `χ=0` 集 = `{1,8}` = 可成色 singlet
  ⟹ **`χ` 中性 ⟺ gauge 不變性本身** ⟹ 零額外選擇定則 ⟹ **唔壓制**
* **候選②③ `B` / `B−L`**：`U(1)⁸` 強制色:弱 = `2:−3`；`B` 弱 = 0（`α` 矛盾）、`B−L` 比 = `−1:3`
  ⟹ 皆**唔喺 `U(1)⁸`** ⟹ 外部量子數 ⟹ 作選擇定則為**定義性恆真**（無鑑別力）
* **候選④⑤** ill-typed（U(1) 無中心荷；`Λ²` 恆偶無分級）
* ★★ **條件③ 新鏈下唔可達**：唯一 well-typed 候選與 gauge 不變性重合；舊鏈（O210-T3）「有 SU(4)
  中心荷但唔壓制」，新鏈「定義域消失 + 唯一候選唔壓制」—— **兩鏈結論一致、理由不同**
* **`τ_p` 裁定**：🟡 條件式維持（elementary ✓ + 算子扇區未排除）；三條件可達者 = **0**
  ⟹ 要壓制 `ΔB=1` 必須**新增結構**（新算子／新型別規則／動力學機制）
* 新增開放項 3 條（Wilson 動力學層【跨 O】、X/Y 交換圖【掛 O85】、帶色分量完備普查）
* ⚠️ 本輪只寫 O88 目錄；O85 / O210 檔案一字未動


### 2026-10-15（續）— 開放項 1：新鏈 ΔB=1 算子完備普查（docs/17）

* **docs/17_db1_operator_census.md**（`scripts/18_db1_operator_census.py` **14/14 PASS**，v2）
* **v1 更正**：初版混入 12̄ factor（m）—— `Λ^k(12)` 冇 12̄，色分量 ≤ 3（`Λ^a(3), a>3=0`）
  v2 正確設定下重算，結論收斂且強（唯一解）
* ★★ **s=0（唔含單態）唯一 ΔB=1 載體 = k=5**：`Λ⁵(12)`，n=3 色 + p=2 弱，
  `Y = 3·(−1/3) + 2·(+1/2) = 0`、`ΔB = 3/3 = 1`、色 singlet `Λ³(3)=1`、弱 singlet `Λ²(2)=1`、
  `C(12,5) = 792`；純分量重數 = 1（真實存在）
* **逃生規格對照**：舊鏈 `k∈{2,6,10}`（`k≡2 mod 4`，SU(4) 中心荷週期）↔ 新鏈 **`{5}`**（Y 平衡）
  ⟹ **重疊 ∅，逃生規格完全改變**；含單態 k≥4 全 y_i-conditional
* **裁定**：elementary 扇區 ✅ 維持；算子扇區 🟡 未排除 **已具體化**（載體 = `Λ⁵(12)`）
  ⟹ `τ_p = ∞` **唔可升格**（唔係「質子會衰變」—— Wilson 係數屬動力學層，未推）
* 開放項更新：本項收口 ✅；剩 含單態（y_i，掛 O85）、Wilson（跨 O）、X/Y 交換圖（掛 O85）
* ⚠️ 本輪只寫 O88 目錄；O85 / O210 檔案一字未動


### 2026-10-15（續）— 收口兩項（docs/02 #5、docs/03 附註）

* **docs/02 §七 #5 SU(12)²×U(1)異常閉合**（`scripts/19_u1_anomaly_closure.py` **11/11 PASS**）：
  `ΣY(12)=7y`、`ΣY(12̄)=−7y` ⟹ 自消對任意 y_i；SU(12)³ / grav²×SU(12) = 0；
  ⚠️ SU(12)=global（O85 Q6）⟹ 非 gauge anomaly，雙重保險
* **docs/03 附註 B**: §四交接表 B11/B1 行 stale 閉環更新 —— B11 已由 O88/PD#1-3 閉環
  （2026-10-02，τ_p=∞ 結構判定，新鏈重核後條件式維持）、B1 已由 O89 閉合（46/46, M_GUT=M_Pl·γ₁）


### 2026-10-15（續）— X/Y 玻色子結構性質（docs/18）＋ O88/proton-decay 遺留複核

* **docs/18_xy_structure.md**（`scripts/20_xy_structure.py` **16/16 PASS**）
* adjoint 143 = 12⊗12̄ − 1 完整分解（144−1）重核；色-弱交叉塊 = `(3,2̄)+(3̄,2)` = 12 態
* ★ **X**（(3,2̄), 來源 (3,1)⊗(1,2̄)）：`Y=−5/6, ΔB=+1/3, Q={−1/3,−4/3}`；
  **Y**（(3̄,2), 來源 (1,2)⊗(3̄,1)）：`Y=+5/6, ΔB=−1/3, Q={+4/3,+1/3}` —— **零 y_i 依賴**（塊無單態）
* ★ 對照 SU(5)：新鏈 Y 電荷譜 = SU(5) X 電荷譜（角色錯位）；新鏈 X 與 SU(5) X 無重疊
* ★ `ΔB=1` 最低階 = 3 個 X/Y 交換（±1/3×3：3X=+1, 3Y=−1, 2X+1Y=+1/3…）—— 與 docs/17 `Λ⁵(12)` 載體自洽
* v1 兩錯誤（decomp 漏 (1,1)₂、Q(X) 正負號）已修正重跑 → v2 16/16
* **O88/proton-decay 遺留複核**：closed negative ✅；closeout 遺留（鏈第一步 Higgs→O85、
  PD#4→composite-dB1-channel）兩項都已移交＋本 session 推完 ⟹ **無新遺留**


### 2026-10-16 — 階段性 Closeout（O88/composite-dB1-channel 收口）

* **docs/19_stage_closeout_audit.md**（`scripts/21_audit_stage1.py` **38/38 PASS**，獨立第三層）
* 21 script 全重跑：freeze vs 重跑 **差集 0**（04=40/42 已知 2 FAIL、06=10/11 已知偽證 FAIL、09 21/21）
* data/_stagecloseout_20261016/ freeze（20 JSON + 15 logs）
* 殘餘開放項：已全數 handoff（O85 ×2：含單態載體 + X/Y 交換圖；O81 ×2：Wilson 係數）
* O88 側六層收口：代數/結構/表示/算子/異常/X-Y；τ_p=∞ 條件式維持
