# O137 docs/37 — 未閉合點分流與交接（Round 19 跨 O 審計）

> **日期**: 2026-09-25（HKT）
> **狀態**: 🟢 分流完成（7 個新 O 建立 + 4 個已有主 O 交接）
> **性質**: **新檔**（非修改舊文檔）；本輪唯一改動 = 本檔 + SESSION_START/final_result 之 append 節
> **來源**: 調律者指令「把剩下的所有問題各自開新o系列，寫入目錄結構及交接文件待其他session處理」
> **前置**: `docs/36_gap_attack_round19.md`（Round 19 遺留 9 項 + 新遺留 8 項）

---

## 〇. 一句話

Round 19 之未閉合點已**全部**分流：**7 項開新 O（O216–O222）**，
**4 項已有主（O70/O206/O67/O64）→ 寫交接文件**，
並在過程中揪出 **3 個真跨 O 矛盾**（其中 1 個係 O137 自身結論被推翻）。

---

## 一、跨 O 歸屬審計（建新 O 之前強制執行）

依 skill `idcm-o-series-management` Step 2「Cross-O-series closure audit」，
逐項 grep 全 corpus（`o*/docs/*.md` + `final_result.md` + `SESSION_START.md`）搵已有主。

| # | O137 未閉合點 | 已有主 | 狀態 | 裁定 |
|:-:|:--|:--|:--|:--|
| 1 | **Mori rays / PF discriminant**（遺留 5）| **O70** `155_curves` | 🟢 **已閉合** | **唔開新 O** → 交回 O70 |
| 2 | C_f 投影因子生成器（遺留 3）| **O206** 開放項 2 / **O64** | 🟡 | 開 **O221**（含衝突裁決）+ 交回 |
| 3 | 角色置換 σ_g（遺留 8）| **O67**（孤兒）| ⚠️ 矛盾 | 開 **O222**（接手）+ 交回 |
| 4 | 幾何 chirality 物理映射（遺留 4）| **O137 gap 5**（自己）| 🔴 | 併入 **O222** |
| 5 | 塊內質量階級 | **O64**（孤兒）| ⚠️ 矛盾 | 交回 O64（O222 同源）|
| 6 | 角色多重集 | **O88** | 🟢 已閉合 | 引用，唔開 |
| 7 | 前提「費米子模式 = 全息保護模式」| **O209 docs/09** | 🟢 **已解除** | 唔開（見 §四）|
| 8 | H₀ 反解 72.5912 | **O170**（部分裁決）| 🟡 | 開 **O220** |
| 9 | M₀ 2 參數欠定 | **O38 / O212 / O213** | 已分配 | 唔開（標度無缺口）|
| 10 | cytools triangulate 非決定性 | **O70**（Sage PPL 繞過）| 🟢 方法已解 | 唔開（見 §三）|
| 11 | Δn_color 色荷纏繞（遺留 6）| **無主** | 🔴 | 開 **O216** |
| 12 | 「為何 4-正則」| **無主** | 🔴 | 開 **O217** |
| 13 | 目錄身份判準 + 「47」非唯一 | **無主** | 🔴 | 開 **O218** |
| 14 | pt↔mode 索引前提（A3）| **無主** | 🔴 | 開 **O219** |

---

## 二、★ 三個真跨 O 矛盾（本輪新發現）

### 矛盾 1 — **O137 遺留 5（Mori）早已被 O70 閉合**（推翻 O137 自身結論）

```
O137 docs/36 §十一 記「Mori cone 受阻（rays 硬限時內未返回）」→ 列為遺留 5 未閉合

★ O70（o70_155_curves，2026-09-03）已閉合，用【同一個 polytope 檔】:
   o53_cy3_reality/data/polytopes/cy36_98_sage_export.json（md5 63536d17…）
   · CYTools: toric_mori_cone(in_basis=True) -> 185 exact integer rays
   · CYTools: toric_kahler_cone()          -> 185 hyperplanes
   · 46 facet-defining Mori rays（185 中 139 redundant）
   · 3732 exact extreme rays（SageMath 10.9 PPL，24s）
   · 舊 99 rays ⊂ 3732（99/99）

⟹ O137 之「受阻」係【方法問題】（cytools sc.rays() 喺 C 擴展層阻塞），
   唔係「Mori cone 不可得」。O137 之 PF discriminant 路線應改由 O70 之 46 rays 展開。
⚠️ 待核: O137 之 secondary cone 得 185 超平面（RR^37）與 O70 之 185 Kähler 超平面
   （32D）數字相同 — 兩者是否同一物件（維度約定唔同）。
```

### 矛盾 2 — **C_f / F_proj 三方衝突**

```
O64  (08-31) 🟢 自報「9 費米子質量零參數湧現」
     m = M0 x gamma_n x F_proj x Z_topology；M0 = 27.9009 MeV
     F_proj 值 = {18/5 = 3.6, 15.5, 37, 42}（+ sqrt(12), sqrt(5), sqrt(3), sqrt(6/44)）
     9/9 偏差 0.00%–0.85%
O206 (09-21) 🟢 主體收束（CSSG-v3 承接）
     C_f 池 = {3.6, 13, 15.5, 33, 37, 44, 1554}；max Δ 2.02%
O137 R19 (09-25)
     phi=9 目錄 Phi_ij = 1 + x3_i·x3'_j 上限 64（18 值）
     C_t = 7722.8；需 2149x ⟹ 4/9 費米子（c, tau, b, t）超出

★ F_proj ∩ C_f = {3.6, 15.5, 37} ⟹ 極可能係同一框架之兩次記錄
★ 線索: 7722.8 / 1554 = 4.969 ≈ F_5 = 5
⟹ 去向: O221（首要任務 = 裁決三方）
```

### 矛盾 3 — **O64 / O67 自稱閉合 vs O209 重開**

```
O67 (08-31) 「✅ 全部解決 — 5 個開放問題全部閉合」（41/42 PASS）
O209 docs/10 (09-25) 「角色置換 σ_g -> O67，🟡 未閉合」
O64 (08-31) 「🟢 最終閉合 — 9 費米子質量零參數湧現」
O209 docs/10 (09-25) 「塊內質量階級（hierarchy 太淺）-> O64，🔴 未閉合」

診斷（兩個可能，唔可即時判）:
   A 粒度唔同: O67 = 66 態→SM 整體對應（粗）；O209 = 邊個模式 = 邊個角色（細）
   B O67 路線被證偽: O209 已證 E_n = 4sin²(nπ/88) 喺 SEL 上 injective
     ⟹ O67 之「eigenvalue 結構區分角色」只係【空洞相容】（零信息）
⟹ 去向: O222 首要任務 = 讀 O67 docs/01_derivation_record.md 判 A 抑或 B
```

---

## 三、方法層（唔開 O，只入 skill）

```
🔴→🟢 cytools triangulate 非決定性 + C 擴展層阻塞 + 截斷 log + 退出碼陷阱
   · O70 已用 SageMath PPL 繞過（3732 exact extreme rays）
   · O137 已修 scripts/71（subprocess 硬限時）+ scripts/72（200 剖分集成）
   · 三條鐵律已入 skill `idcm-cy3-verification`
⟹ 屬【驗證基礎設施】，唔值得獨立開 O（O218 已涵蓋「判準」層面）
```

---

## 四、★ 前提「費米子模式 = 全息保護模式」— 已由 O209 解除

```
O137 遺留 9/A 記: 前提「費米子模式 = 全息保護模式」仍 conditional
   （塊定義循環論證；A₅ 動差準則 P = 0.0155 未達 5σ）

★ O209 docs/09（2026-09-24）已【獨立】導出同一 9 模式集，路徑完全唔用 A₅ 幾何:
   · 兩個質量無關生成元: G1 反週期 + G2 A₅ 動差等向
   · 閾值定理 Sel(S) = {odd n < 15} ∪ {even n < 6}
   · 二十面體不變量環【獨立重推】（由 60 節點集反推 |G| = 60 = A₅，
     Molien P(t) = (1+t^15)/((1-t^2)(1-t^6)(1-t^10)) ⟹ primary degrees {2,6,10}）
   · 9! 窮舉唯一最小 RMS 0.587228（與 O137 scripts/65 一致）
⟹ 「塊定義循環論證」之批評【已解除】—— 有第二條獨立路徑
⚠️ 但 O137 之 A₅ 動差準則 P = 0.0155 仍為弱證據；O209 之閾值定理係較強路徑
⟹ 去向: 唔開新 O；記錄於此，O209 已擁有
```

---

## 五、本輪建立之 7 個新 O（O216–O222）

| O | Slug | 問題 | 優先度 |
|:-:|:--|:--|:--|
| **O216** | `o216_delta_n_color` | Δn_color 色荷纏繞（色荷自由度缺失）| ★★ |
| **O217** | `o217_four_regular_necessity` | 4-正則必要性（RH 型前提）| ★★ |
| **O218** | `o218_catalog_identity_criteria` | 目錄身份判準（密度基準形式化 + 非唯一表示）| ★★★ |
| **O219** | `o219_pt_mode_index_premise` | pt↔mode 索引前提審計（審計項 A3）| ★★ |
| **O220** | `o220_h0_three_value_adjudication` | H₀ 三值裁決（72.5912 / 71.157 / 67.407112）| ★★★ |
| **O221** | `o221_cf_projection_generator` | C_f 投影因子生成器（含三方衝突裁決）| ★★★ |
| **O222** | `o222_gauge_embedding_chirality` | 規範嵌入層：角色 σ_g + 幾何手徵橋 | ★★★ |

每個新 O 含: `docs/01_problem_record.md`（依 `RESULT_TEMPLATE`/skill 模板）+ `SESSION_START.md`
+ `RESULT.md` + 空 `scripts/` + 空 `data/`。

**編號說明**: max = O215；O216–O222 全部非墓碑（墓碑 = 178, 184–189, 198, 205）。

---

## 六、寫入已有主 O 之交接文件

| 目標 O | 動作 | 檔案 | 驗證 |
|:--|:--|:--|:--|
| **O70** | append 接收註記 | `SESSION_START.md` | 76 → 127 行（前 76 行 byte-identical ✅）|
| **O206** | append 接收註記 | `SESSION_START.md` | 686 → 740 行（前 686 行 byte-identical ✅）|
| **O170** | append 接收註記 | `SESSION_START.md` | 110 → 154 行（前 110 行 byte-identical ✅）|
| **O67** | **建立**（原本缺失）| `SESSION_START.md`（71 行）| 新檔；O67 既有檔零改動 ✅ |
| **O64** | **建立**（原本缺失）| `SESSION_START.md`（75 行）| 新檔；O64 既有檔零改動 ✅ |

**孤兒註記**: O64 / O67 / O137 三者**均無 README 行**（未註冊）⟹ 本輪已補 O137 行；
O64/O67 之行留待其 owner session 決定（唔越權改其狀態行）。

---

## 七、README 更新

```
README.md: 171 → 179 行（+8 行插入於 O215 行之後）
  · O137 行【新增】（原本完全缺失 — 未註冊）
  · O216–O222 七行【新增】
  · 插入點前後之行 byte-identical ✅（程式化斷言驗證）
```

---

## 八、零污染核實

```
受保護舊行 md5（本輪全部 append-only，逐 byte 驗證）:
  o70/SESSION_START.md    前  76 行 ✅
  o206/SESSION_START.md   前 686 行 ✅
  o170/SESSION_START.md   前 110 行 ✅
  README.md               插入點前後 ✅（程式化 assert）
  o221 / o222（本輪新檔）  追加前之內容 ✅

禁區核實（未觸碰）:
  docs/19, docs/25, docs/26, docs/28–docs/34（O137 舊文檔）
  ../o209_selection_algebra/ 及其他 O 目錄之既有檔案
  ⚠️ 例外（用戶明示授權「寫入目錄結構及交接文件待其他session處理」）:
     · 新建 o216–o222/ 七個目錄
     · O70/O206/O170 SESSION_START append 註記
     · O64/O67 SESSION_START 建立（原本缺失）
     · README.md 插入 8 行
```

---

## 九、與 docs/36 之關係

```
docs/36 = Round 19 攻堅記錄（9 項遺留 + 審計 A1–A10 + 新遺留）
docs/37 = 本檔 — 遺留分流與交接（唔重複 docs/36 之推導內容，只做歸屬與去向）
⟹ 兩者互補；docs/36 一字未改
```

## 十、待調律者裁決

```
🔴 O64 / O67 是否併入新 O（O221 / O222）抑或保留獨立（依 O137 先例 O199 併回 O136）
🔴 O221 是否獨立，抑或併回 O206（其開放項 2 與 O221 重疊）
🔴 O222 是否獨立，抑或併回 O67
🔴 O218「目錄身份判準」是否升為全項目層級（影響所有 O 系列）
🔴 墓碑編號（178, 184–189, 198, 205）是否重用
```


---

## 十一、並行 session 協調註記（2026-09-25，append-only）

### 〇. 事實

本輪開新 O 期間，`open_problems_fresh/` 有**另一個並行 session** 正在工作
（O213 `world_dynamics` — 其 git commits: `01c9954` O213 第七輪 / `b38b6b3` 第六輪 / `fea6ec5` 第五輪）。

**其 `SESSION_START.md` line 84 明寫**:

> **裁決**: **唔開 O216** — 4 路線全部已有專屬 O；按「同一項目缺口唔開新 O」
> 寫入各自 O 嘅 SESSION_START。

### 一. 核實：無撞題

```
O213 之「唔開 O216」係針對【宇微同構 (Cosmos-Microcosm Isomorphism)】之 4 路線
（Gemini 提案），路線 ② 之歸屬寫 O136/O137 + O65。

本輪 O216 = Δn_color 色荷纏繞（O137 遺留 6）— 完全唔同題目。
⟹ 並行 session 只係【考慮過】216 然後放棄；本輪使用 216 唔構成撞號。
```

### 二. 方法論一致（值得記錄）

```
並行 session 之裁決理由「4 路線全部已有專屬 O ⟹ 唔開新 O，寫入各自 O 嘅 SESSION_START」
與本輪之處理【完全一致】:
  · 已有主 → 唔開新 O（本輪: Mori → O70 已閉合；前提 → O209 已解除）
  · 寫入目標 O 之 SESSION_START（本輪: O70/O206/O170 append；O64/O67 補建）
⟹ 兩個 session 獨立得出同一紀律 ⟹ 該紀律可升為項目級慣例
```

### 三. 並行 session 之檔案（本輪【未觸碰】）

```
以下檔案之 mtime 落喺本輪時段，但**唔係本輪寫入** — 屬並行 session 之工作:
  o100_cl_to_pk/SESSION_START.md                        (20:18)
  o9_high_ell_peaks/SESSION_START.md                    (20:18)
  o73_h0_first_principles/SESSION_START.md              (20:19)
  o86_sm_gr_coupling/final_result.md                    (20:19)
  o86_sm_gr_coupling/docs/08_rworld_absolute_derivation.md (22:37)
  o213_world_dynamics/SESSION_START.md                  (22:37)
  o182_88grid_geometry/scripts/15_explore_ideal_structure.py (23:26)
  o182_88grid_geometry/scripts/16_ideal_chirality.py    (23:30)

核實方法: 逐檔 grep「O216–O222 / O137 遺留」→ 全部 0 命中（除 o213 之「唔開 O216」meta 行）
⟹ 判定為並行 session 正常工作，**唔係本輪越界**（依 skill 範圍核實紀律:
   「唔好一見 mtime 新就報違規，亦唔好靜靜當冇事，要分清本 session 越界 vs 並行 session 正常工作」）
```

### 四. 風險提示

```
⚠️ o182 之 scripts/15, 16 於 23:26/23:30 建立 — 主題「ideal structure / ideal chirality」
   與 O222（規範嵌入層手徵橋）及 O137 docs/08 §5 之「理想 88-grid 命題」相關。
   O213 R5 已證該命題**作廢**（88-格 under I 最大偏差 16.1070° ⟹ 染色非 I-等變）。
   ⟹ 若 o182 session 正重推該路線，需與 O213 R5 之結論對齊（本輪唔干預）。
```

### 五. 本輪寫入清單（最終，供核實）

```
o137_cy3_topological_resonance/  docs/37（新）+ SESSION_START append + final_result append
o216_delta_n_color/              docs/01 + SESSION_START + RESULT（全新建）
o217_four_regular_necessity/     同上
o218_catalog_identity_criteria/  同上
o219_pt_mode_index_premise/      同上
o220_h0_three_value_adjudication/ 同上
o221_cf_projection_generator/    同上（+ §十 三方衝突 / §十一 密度警告 / §十二 註冊狀態）
o222_gauge_embedding_chirality/  同上（+ §九 O67 矛盾 / §十 O64 同源矛盾）
o70_155_curves/SESSION_START.md        append（76 → 126 行）
o206_per_mode_frequency/SESSION_START.md append（686 → 739 行）
o170_phase_depth_distance/SESSION_START.md append（110 → 153 行）
o64_sector_fermions/SESSION_START.md   建立（原本缺失，74 行）
o67_sm_labels/SESSION_START.md         建立（原本缺失，70 行）
README.md                         插入 8 行（0 刪除 / 0 修改）
```

### 六. 零污染最終核實

```
README.md 與改動前備份 diff: 刪除/修改行 = 0 ✅ ; 新增行 = 8 ✅
o70 / o206 / o170 SESSION_START: 追加前之內容 byte-identical ✅（程式化 assert）
o64 / o67 既有檔案（01_problem_record.md / docs/ / scripts/ / data/）: 零改動 ✅
o137 禁區文檔（docs/19, 25, 26, 28–34）: 零改動 ✅
其他 O 目錄（o100/o9/o73/o86/o182/o213 等）: 零寫入 ✅（mtime 變動屬並行 session）
```


---

## 十二、★ 調律者裁決：合併方向（2026-09-25，append-only）

> **裁決原文（逐字）**: 「只會後來的併入原先的，不可能倒轉來，所以應該是221併入206，
> 222併入67，218作為獨立系列，其他重複的就按平常一樣把新問題加入session start，
> 等各自的專屬session 自行解決」

### 〇. 原則

```
★ 合併方向鐵律: 【後來者併入原先者，不可倒轉】
   ⟹ 當一個新 O 之問題本屬一個較早 O 之專屬範圍時，新 O 併入舊 O；
      唔可以反過來（唔可以將舊 O 併入新 O）
```

### 一. 執行結果

| 原新 O | 原先擁有者 | 裁定 | 動作 |
|:--|:--|:--|:--|
| **O221** C_f 投影因子生成器 | **O206**（開放項 2）| 🔀 **併入 O206** | 目錄刪除；內容 → `o206_per_mode_frequency/merged_o221/` |
| **O222** 規範嵌入層 σ_g + 手徵橋 | **O67**（σ_g 原指派）| 🔀 **併入 O67** | 目錄刪除；內容 → `o67_sm_labels/merged_o222/` |
| **O220** H₀ 三值裁決 | **O170**（H₀ 量之擁有者）| 🔀 **併入 O170** | 目錄刪除；內容 → `o170_phase_depth_distance/merged_o220/` |
| **O218** 目錄身份判準 | 無（跨項目判準）| ✅ **獨立系列**（調律者明示）| 保留 |
| **O216** Δn_color 色荷纏繞 | 無（O137 遺留 6）| ✅ 保留 | 保留 |
| **O217** 4-正則必要性 | 無（O137 §5.2 誠實界限）| ✅ 保留 | 保留 |
| **O219** pt↔mode 索引前提 | 無（O137 審計 A3）| ✅ 保留 | 保留 |

### 二. 「其他重複的」之判定依據（本輪核實）

```
判定準則 = 該新 O 之問題是否已屬一個【較早 O】之專屬範圍（由該 O 自己之
          開放項清單 / 量之擁有權判定）。

逐項核實結果:
  O221 → O206 開放項 2「C_f 池 {13,33,37,44} label 機制 🟡」✅ 直接命中 ⟹ 併入
  O222 → O209 docs/10 明寫「角色置換 σ_g → O67，🟡 未閉合」✅ 直接命中 ⟹ 併入
  O220 → H₀ 量之擁有者 = O170（H₀ = 71.157 由其導出）⟹ 併入
  O216 → 核實 O136 docs/24 提及 n_color: 0 命中；無 O 擁有色荷纏繞 ⟹ 保留
  O217 → 核實 O143 docs/08 只把「4-正則」列為【事實】而非開放項；O182 🟢 已閉合
         ⟹ 無 O 擁有 4-正則必要性 ⟹ 保留
  O219 → 核實 72.5912 / pt↔mode 只出現於 O137 自身文檔 ⟹ 無較早擁有者 ⟹ 保留
```

### 三. 併入後之 O 編號狀態

```
O 編號 max = 219（O220/221/222 目錄已刪，編號不重用）
墓碑 (README 有行、無目錄): 178, 184–189, 198, 205 + 【新增】220, 221, 222
README 三行已標: 🔀 已合併回 O{170,206,67} (2026-09-25 調律者裁決: 後來併入原先)
```

### 四. 零污染核實

```
o206/SESSION_START.md  前 740 行 byte-identical ✅（併入註記 + 更正皆 append）
o170/SESSION_START.md  前 154 行 byte-identical ✅
o67/SESSION_START.md   前  71 行 byte-identical ✅
o64/SESSION_START.md   前  74 行 byte-identical ✅
README.md              只 3 行改動（O220/221/222 狀態欄），其餘 byte-identical ✅
```

### 五. 本輪最終交付（調律者裁決後）

```
✅ 獨立新 O（4 個）: O216 Δn_color · O217 4-正則 · O218 目錄身份判準 · O219 pt↔mode 前提
🔀 已併入（3 個）  : O221→O206 · O222→O67 · O220→O170
📝 交接註記        : O70（Mori 已閉合）· O206 · O170 · O64 · O67（後兩者補建 SESSION_START）
📄 O137 記錄       : docs/37（新）+ SESSION_START/final_result append
📋 README          : +8 行（含【新增】O137 行）；O220/221/222 改 🔀
```
