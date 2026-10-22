# O232 — 恆星年齡下界 vs IDCM 因果視界 (rendering window) — 13.8 Gyr 宇宙年齡張力之結構裁決

<!-- registry
pid:     O232
title:   恆星年齡下界 vs IDCM 因果視界 (rendering window) — 13.8 Gyr 宇宙年齡張力之結構裁決
state:   closed
verdict: closed
flags:   external-observational-test
owner:   O232
created: 2026-10-05
updated: 2026-10-05
prereq:  O51, O213, O73, O167, O76
source:  arXiv:2607.00764 (Banik et al. 2026, MNRAS) 星系最老恆星普查；technews.tw 2026-07-20 報導
-->

> **狀態**: 🟢 **已閉合（2026-10-05 closeout；診斷性負面閉合 —— R1/R3/R4/R6 + Q1–Q4 全裁決；R5 已交 O213）**
> **建立**: 2026-10-05
> **前置**: O51（age framework）、O213（t_true / arrow）、O73/O167（ω_ring/ω_cmb）
> **位置**: `open_problems_fresh/o232_stellar_age_vs_horizon/`

---

## 一、問題陳述

外部研究（arXiv:2607.00764，Banik et al. 2026 MNRAS）以 155,600 顆 subgiant 樣本測得最老恆星 **A_★ = 13.73 (+0.18/−0.15) Gyr**，宣稱**
宇宙確為 13.8 Gyr、並排除「早期宇宙新物理早期解（ETS，A_U = 12.91 Gyr）」。問題：**IDCM 之結構齡 τ = R_world/c = 1/ω_ring = 13.4701 Gyr
（因果視界 / rendering window）** 與此量測之關係為何？核心質疑點：τ = 13.4701 **低於**量測之最老星齡 13.73 達 **0.26 Gyr（1.6σ / 2.4% vs CMB 13.8）**，
且 IDCM 文件常引「13.8 Gyr」而**無結構推導**。本 O 判定：該量測係**排除 IDCM、抑或與 IDCM 相容**。

---

## 二、已確立嘅結構

```
🟢 原文已定位：arXiv:2607.00764v1，Banik, Kudakolawa Kaluarachchige, Cookson & Desmond (2026)，MNRAS accepted（scripts 外，web 提取）
🟢 IDCM 年齡階梯重現（13/13 PASS）：τ = 13.470063 Gyr、T_ring = 84.6349 Gyr、t_true = 11,100.642 Gyr、ω_cmb = 67.4071
🟢 τ = 1/ω_ring 與 R_world/c 恆等（同一 dof，C2 PASS）
🟢 H₀ 側一致：ω_ring = 72.590 vs H₀_local = 73.17±0.86 ⇒ 0.67σ；vs SH0ES 73.04±1.04 ⇒ 0.43σ
🟢 τ = 13.4701 夾於 ETS(A_U=12.91, +4.3%) 與 CMB(A_U=13.8, −2.4%) 之間 ⇒ 殺 ETS 之測試不殺 IDCM
🟡 核心張力（未消）：A_★ − τ = 0.2599 Gyr = 1.575σ（星）；τ 低於 CMB 宇宙齡 2.391%
🔴 IDCM 文獻之「13.8」無結構推導：13.8/τ = 1.0244941，凍結結構池 0 命中（null 0.2）；post-hoc 42/41 係泛型巧合（禁宣稱）
```

---

## 三、未確立（🔴 開放問題）

```
R1 🔴 τ = R_world/c 是否為「可觀測星齡」之硬天花板？—— IDCM 未定義「可觀測」與「齡」之界線
R2 🔴 0.26 Gyr（1.6σ）缺口有無結構因數？—— 凍結池 0 命中，須新結構路線（禁事後擴池）
R3 🔴 「13.8」能否由 observer-relative 定義導出（τ + 首代星形成期 t_f），抑或永遠係外部錨？
R4 🔴 論文的 age 量測預設 t=0；IDCM 無 t=0 ⇒ 兩者「齡」不可直接對減（範疇不相容，需翻譯層）
```

---

## 四、攻擊路線

```
1. 可觀測視界語義      → 由 O51/O213 之 rendering/投影語義，判定 τ 是否 cap 星齡（零新參數；成本 低）
2. 缺口結構因數        → 凍結「τ→13.8/13.73」之結構族，做 MC null（10⁷）＋樣本外盲測（成本 中；⚠️ 禁事後擴池）
3. 翻譯層定義          → 用 O76 之 z↔D_A 投影，建立 IDCM 版 lookback/age 對應（成本 中）
4. ETS 對照            → 證 IDCM 之 13.47 不走 ETS 路線（已初步：+4.3% vs ETS）⇒ 完成（成本 低）
```

## 五、驗證標準

```
✅ 原文定位（標題、作者、樣本、數值）逐項對得上 —— 已達
✅ IDCM 年齡階梯獨立重算，與 O51/O213 報值一致（13/13 PASS）—— 已達
✅ 12.8 之 13.8 結構身份以凍結密度前驗判定（命中有／無）—— 已達（0 命中）
🔴 R1 收斂：τ 是否硬天花板 —— 未達
🔴 R2 收斂：缺口結構因數（10⁷ MC，5σ；樣本外盲測）—— 未達
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

> ⚠️ **本 O 現未閉合（🟡）。** 任何「τ = 13.47 吻合 13.8」之主張現階段**不成立**（post-hoc）。

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-05 | 註冊（register next-number = 232，無撞號；歸屬審計 fencing O51/O213） | `problem_register/` |
| 2 | 2026-10-05 | 原文定位（arXiv:2607.00764v1）＋ 逐項對比，寫 docs/01 | `docs/01_paper_vs_idcm_divergence.md` |
| 3 | 2026-10-05 | 年齡階梯重算 + 密度前驗（13/13 PASS） | `scripts/01_idcm_age_ladder.py`, `logs/01`, `data/01` |
| 4 | 2026-10-05 | R1 攻堅：τ ≠ 年齡天花板（IDCM 明文『冇年齡上限』）；外部數據尾端（Xiang+2024, 320,028）；天花板判據 | `docs/02_r1_rendering_depth_verdict.md`, `scripts/02`（3/3）, `scripts/03`（2/4） |
| 5 | 2026-10-05 | ★ 撤銷 pass-1「A_★−τ = 1.6σ 缺口」框架（category error：周長 vs 年齡） | `docs/02` §0 |
| 6 | 2026-10-05 | R6 攻堅：JADES 真數據 (de la Vega+2025, 2,282) 上包絡 vs t_age(z) | `scripts/04`（exit 0）, `docs/03`, `data/04` |
| 7 | 2026-10-05 | ★ GS-z14-0 文獻核：星齡 15–36 Myr ≪ 287 Myr 天花板；v9 0.30 Gyr 錯（finding #2） | `docs/03` §2–3 |
| 8 | 2026-10-05 | R5 交接：渲染深度早/晚端語義 → handoff O213（v9 doc04 13.8+NaN vs v10 O51 撤回） | register handoff O232→O213 |
| 9 | 2026-10-05 | R3 裁決：「13.8」= 外部 ΛCDM 錨；t_render 44/43 偽影已撤回（O51 權威）；τ+t_f 讀法 🟡 | `docs/04_r3_13p8_definition.md`, `scripts/05`（6/6） |
| 10 | 2026-10-05 | R4 裁決：翻譯層成文（6 category ＋ 5 規則）；D1 正式化為 NO-MAP | `docs/05_r4_translation_layer.md` |
| 11 | 2026-10-05 | 框架擴展（調律者）：Q1 銀河年輕？Q2 光譜推齡？Q3 有冇 >138 億歲星？（0/7 候選超齡） | `scripts/06`（exit 0）, `docs/06` |
| 12 | 2026-10-05 | Q4 無大爆炸假設評估：🟡 受壓未否證；星齡前線 0 正面預言；OBS 結算 ΛCDM 5/5 vs IDCM 0/1 | `docs/07_no_bigbang_falsifiability.md` |
| 13 | 2026-10-05 | **closeout 全鏈重跑**：scripts/01–06 全部 exit 0；5/6 logs byte-identical（sha 對備份）；★ 發現並修正 scripts/03 正典漂移（pre-patch 2/4 → 現行 code 3/4；舊版留 `~/.hermes/backups/o232_closeout_20261005_1412/`） | `logs/01–06`（03 更新）, `data/01–06` |
| 14 | 2026-10-05 | **closeout 決算**：R1/R3/R4 🟢、R2 ⚫ 消失、R6 🟡 數據側偏 ΛCDM、R5 已 handoff O213、Q1–Q4 已答；OBS 結算 ΛCDM 5/5 vs IDCM 0/1 ⟹ 診斷性負面閉合 | `docs/01–07`, `01_problem_record.md` §十三–§十四 |
| 15 | 2026-10-05 | **register close O232**（verdict=closed；R5 交接 O213 via handoff+note；Q4 CMB/BBN 判據 note 落 O213）＋ README row 更新＋ MANIFEST.json 建立 | `problem_register/`, `README.md`, `data/MANIFEST.json` |
| 16 | 2026-10-05 | **O213 裁決已收**：R5 ✅ 已裁定（z=17 截斷唔成立；216 Myr = ΛCDM t_age(17) 換算非 IDCM 量；τ+t_f 讀法無結構地位）；Q4 🟡 判據接受＋三子判據（非黑體殘差/BBN 一致/LSS 引力）；翻身條件收窄 = ℓ_cut 投影（O76/O132） | `01_problem_record.md` §十五, `SESSION_START.md` §十一, register note O213→O232 |
| 17 | 2026-10-05 | **原設問題直接裁決（§一 二選一）**：排除 ✗（R1 正交）、相容 ⚠️（R4 NO-MAP）、正解 = 正交/無約束力＋零正面預言（R1+R4+R6 三合一） | `01_problem_record.md` §十六, `final_result.md`, `SESSION_START.md` §十二 |

## 七、相關文件

```
- O51  — age framework（τ = R_H/c, t_true），本 O 引用，不重推
- O213 — world dynamics，docs/06 定義 t_true = 131·T_sync + τ
- O73  — ω_ring 第一性原理；ω_cmb = ω_ring(1−π/44)
- O167 — CMB H₀ 張力（投影層）
- O76  — z ↔ D_A 投影層翻譯
- docs/01_paper_vs_idcm_divergence.md — 本 O 主比對文
- scripts/01_idcm_age_ladder.py — 年齡階梯重算 + 密度前驗
```

---

## 八、歸屬審計（開 O 前強制）

```
✅ O232 編號：register next-number = 232；無目錄、無 register 行、無 reserved tombstone ⇒ 無撞號
✅ 無平行 session 佔用（最高既有 = O231）
⚠️ 鄰接持有者：O51（age framework / render depth）、O213（t_true / arrow）—— 本 O 只「引用」，不重推；新客體 = 外部恆星年齡下界之裁決
```

---

## 九、附註更正（append-only；2026-10-05 第二輪）— 不刪改上文

> ⚠️ 以下為**附註**，原文（§一–§四 關於「1.6σ / 2.4% 缺口」）保持不動，僅此更正。

**更正 1（範疇錯誤）**：§二 之「核心張力：A_★ − τ = 0.26 Gyr = 1.6σ」**不成立**。
依 v9 `35_rendering_depth_structural_derivation.md`：τ_depth = 環之 light-crossing time = **「有幾遠」（長度）**，
**唔係年齡**；與 A_★（Gyr）相減係 **category error**。v9 `verify_young_galaxies.py` 明文「**冇年齡上限**」。

**更正 2（R1 裁決）**：🟢 τ = 13.4701 Gyr **唔係** IDCM 年齡天花板。論文之 ΛCDM 天花板測試**正交**於 IDCM
（IDCM 無 A_★ 預言）⇒ 論文既不確認也不否證 IDCM。

**更正 3（R2）**：⚫ 無「0.26 Gyr 結構因數」可尋（因該缺口不存在）。
條件性：若採 doc 04 之「渲染深度 = 天花板」讀法，數據偏好 D = 13.8（最老可渲染 13.584, 0.9σ）而非 13.47（13.254, 2.9σ）。

**新增 R5**：IDCM 渲染深度係「早端截斷（z=17 ↔ 216 Myr）」抑或「晚端（D）」？→ 疑屬 O51/O213 語義（跨 O，只限 register）。
**新增 R6**：可分辨判據 = 高 z（8–15）恆星齡 vs ΛCDM t_age(z)（`scripts/03` 判據表）→ 交觀測攻堅。

**外部數據（`scripts/02`；Xiang+2024, 320,028, NADC DOI 10.12149/101467）**：
raw N(>τ) = 22,661（7.08%）、達 YY 網格上限 20 Gyr；類論文切割樣本（FEH<−0.6 ∧ α/Fe>0.15 ∧ d<5kpc, N=44,222）中 **29.3% > τ**；
但尾端 σ_A ≥ 1.4 ⟹ 噪聲主導，**不作 IDCM 正面證據**。

**附帶 finding 🔴**：v9 `verify_young_galaxies.py` docstring 宣稱 `t_age(10)=540 Myr`，其自身 code（H0=70,Ω_m=0.3）得 **466 Myr**
⟹ **v9 文件/數值不一致（~14%）**。本 O 只記錄，不修改 v9。

---

## 十、附註更正 #2（append-only；2026-10-05 第三輪）— R6 攻堅

**R6 🟡 數據側（偏 ΛCDM）——高 z 恆星齡 vs 天花板，真數據實測（`scripts/04`, `docs/03`）**：
1. **de la Vega+2025（JADES 2,282 星系）**：mwa_50 > t_age(z) = **0/2,282**；上包絡隨 z **單調下降**（4.55 → 0.52 Gyr）⟹ 形狀跟住 ΛCDM 天花板；IDCM「z-無關包絡」形式被拒。
2. **JADES-GS-z14-0（z=14.32）**：文獻質量加權齡 = **15 Myr**（Helton+2024 BAGPIPES）/ **36 Myr**（Carniani+2024）= 天花板 287 Myr 之 5–12% —— **遠低於天花板**。
3. **v9 finding #2 🔴**：v9 `verify_young_galaxies.py` line 103 用 GS-z14-0 星齡 **0.30 Gyr** 示範「微超天花板」——文獻係 0.015–0.036 Gyr，**高咗 ~10–20 倍，示範無效**。

**對 IDCM 實質意義**：τ 非星齡預言（docs/02），故高 z 未違反天花板**唔係** IDCM 敗績；但「冇年齡上限」若要以「z-無關包絡」形式現身已被拒 ⟹ **R5（渲染深度早/晚端語義）由可選變必須**：IDCM 須以早端截斷 216 Myr 自洽解釋「高 z 星系存在但星齡年輕且隨 z 下降」。

---

## 十一、附註更正 #3（append-only；2026-10-05 第三輪）— R5 交接 + R3/R4 裁決

**R5 🔄 已交接（跨 O，只經 register）**：`handoff O232→O213` —— v9 doc04「渲染深度固定 13.8 + z=17 NaN 截斷 216 Myr」vs v10 O51 撤回（44/43 偽影；渲染深度 = 13.470 Gyr = 光行距離，冇宇宙年齡）。待 O213 裁定：v10 中 z=17 早端截斷是否仍成立、216 Myr 基準系乜、τ+t_f 讀法狀態。（O51 已附註 mirror。）

**R3 🟢 裁決（`docs/04`，`scripts/05` 6/6）**：IDCM v10 **冇「13.8」嘅內部定義**：
- (ii) t_render = τ×44/43 = 13.7833 **已撤回**（O51 2026-08-22，調律者揪出；dev 0.0267% 重現）⟹ v9「13.8 = 渲染深度」敘述一律作廢
- (iii) 13.8 = 外部 ΛCDM 錨（13.8/τ=1.02449，凍結池 0 命中）
- (iv) τ + t_f(z=17) = 13.696 Gyr 距 A_★=13.73 僅 **−0.21σ**——唯一有望嘅「IDCM 側 13.7」讀法，但 t_f(216 Myr) 繼承 v9 撤回狀態，**未經審計**（交 R5/O213）

**R4 🟢 裁決（`docs/05`）**：翻譯層成文——6 類 category（AGE/DISTANCE/OBS/INTERNAL-LCDM/NO-MAP/IDCM-ONLY）＋ 5 條執行規則；**只允許 OBS↔OBS 直接比較，AGE↔DISTANCE 相減 = category error**；D1（無 t=0 vs 論文 t=0）正式化為 **NO-MAP**（非數值分歧，係範疇無對應）。

**R 系列結算（2026-10-05 三輪攻堅後）**：
```
R1 🟢 已裁決 (τ ≠ 年齡天花板, category error 撤銷)      R2 ⚫ 消失
R3 🟢 已裁決 (13.8 = 外部錨; t_render 撤回)              R4 🟢 已裁決 (翻譯層)
R5 🔄 已 handoff O213 (渲染深度早/晚端; t_f 狀態)        R6 🟡 數據側偏 ΛCDM (0/2282; 包絡單調下降)
```

---

## 十二、框架擴展（append-only；2026-10-05 第四輪）— 調律者新問題

**擴展問題**（由「論文星齡不超宇宙齡 vs IDCM 無起始」觸發）：
```
Q1 銀河系係咪「年輕星系」，所以恆星年齡先至不過？
Q2 係咪真係可以從恆星光譜推出年齡？
Q3 銀河系有冇超過 138 億歲恆星（紅矮星／白矮星）？
Q4 IDCM 無大爆炸理論係咪錯誤假設？
```

**Q1 🟢（`docs/06`）**：銀河暈／球狀星團 = 宇宙最老成員（13.5–13.7 Gyr），唔係年輕星系；
「恆星 ≤ 宇宙齡」喺 ΛCDM 係**普遍約束**（形成 ≥ t=0），同星系年齡無關 ⟹ 「年輕星系所以不過齡」係錯因果。

**Q2 🟢（`docs/06`）**：係——次巨星分支係恆星時鐘；YY isochrones + LAMOST 光譜 + Gaia 視差 + MCMC latent + FLAME 交叉；
但係**統計性**（latent 分佈極端 A_★=13.73），單星誤差 ±1–2 Gyr；白矮星冷卻／球狀星團 turnoff／星震學作獨立交叉。

**Q3 🟢（`scripts/06`，0/7）**：**冇一粒恆星被穩健證實超過 13.787 Gyr**：
- HD 140283（唯一曾名義超齡）：2013 = 14.46±0.8 → **+0.84σ** 相容；Gaia 複審 13.9±0.7 → +0.16σ
- 白矮星冷卻 12–13.5 Gyr（NGC 6752/M4/NGC 6397，全部低於天花板）
- 紅矮星：主序壽命 10³–10⁴ Gyr ≫ 13.787——「長命」唔係「老過宇宙」；最老暈紅矮星 13.5–13.7

**Q4 🟡（`docs/07`）**：**受壓但未否證**：
- 星齡前線 OBS 結算：ΛCDM t=0 預言 **5/5 兌現**（R6 包絡下降 ＋ 0 違反 ＋ GS-z14-0 ＋ 0/7 超齡 ＋ 普遍約束）；IDCM 唯一可測形式（z-無關包絡）**0/1 被拒**
- IDCM 冇星齡預言（τ=距離）⟹ 上述證據唔係直接殺 IDCM；但「無大爆炸」目前 = **未被數據支持嘅假設**
- 可證偽判據兩邊都未觸發：穩健超齡星（>3σ）＝殺 ΛCDM 撐 IDCM；CMB/BBN 不可投影化＝殺 IDCM（後者屬 O51/O213 範圍）
- **翻身條件**：R5 早端截斷（216 Myr）必須變成可測預言並過 O213 裁定

**⚠️ 範疇提醒（R4 翻譯層）**：ΛCDM「大爆炸」vs IDCM「無起始」皆 NO-MAP 陳述，唔可以直接比「誰啱」；
只能比 OBS 層面兌現——天平而家喺 ΛCDM 嗰邊。
---

## 十三、檔案閉合水位（close-out watermark，2026-10-05 closeout 建立）

| # | 檔案 | 上次檔案更新 (mtime) | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:---------------------|:----------------|:---------|:-----|
| 1 | docs/01_paper_vs_idcm_divergence.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（98 行） | ✅ 已驗 |
| 2 | docs/02_r1_rendering_depth_verdict.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（88 行） | ✅ 已驗 ⚠️ §7 03 數 2/4 見 §十四 |
| 3 | docs/03_r6_highz_ceiling_verdict.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（72 行） | ✅ 已驗 |
| 4 | docs/04_r3_13p8_definition.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（51 行） | ✅ 已驗 |
| 5 | docs/05_r4_translation_layer.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（53 行） | ✅ 已驗 |
| 6 | docs/06_milkyway_stellar_age_questions.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（55 行） | ✅ 已驗 |
| 7 | docs/07_no_bigbang_falsifiability.md | 2026-10-05 12:38 | 2026-10-05 closeout | 全文（54 行） | ✅ 已驗 |
| 8 | scripts/01–06 | 2026-10-05 12:38 | 2026-10-05 closeout | 全鏈重跑 6/6 exit 0；5/6 log byte-identical | ✅ 已驗 |
| 9 | data/01–06 JSON | 2026-10-05 14:13（重跑） | — | sha 對備份：5/6 一致；03 更新（見 §十四） | ✅ 已驗 |
| 10 | logs/01–06 | 2026-10-05 12:38 / 03=14:13 | — | 對 /tmp 重跑 diff：5/6 一致；03 更新 | ✅ 已驗 |
| 11 | SESSION_START.md | 2026-10-05 12:39 | 2026-10-05 closeout | 全文（199 行，append-only 快照） | ✅ 已驗 |
| 12 | final_result.md | 2026-10-05 12:39 | 2026-10-05 closeout | 全文（append §十五） | ✅ 已驗 |

> 水位規則：本 O 全部檔案 mtime ≤ 2026-10-05 12:39（closeout 前最後改動），closeout 本輪只 append
> 01_problem_record / SESSION_START / final_result 尾部 + 重跑 logs/data（scripts 自寫 data ⟹ mtime 更新，內容由 sha 驗證）。

---

## 十四、closeout 決算（append-only；2026-10-05 第五輪 — 閉合）

**⭐ O232 正式閉合 — 診斷性負面閉合（verdict = closed）**

**R 系列最終決算**：
```
R1 🟢 τ ≠ 年齡天花板（category error 撤銷；docs/02）          R2 ⚫ 消失（無缺口）
R3 🟢 「13.8」= 外部錨；t_render 44/43 偽影已撤回（docs/04）    R4 🟢 翻譯層 6 category＋5 規則（docs/05）
R5 🔄 已 handoff O213（渲染深度早/晚端＋t_f 狀態；12:25 handed_off event）
R6 🟡 數據側偏 ΛCDM：JADES 0/2,282；包絡 4.55→0.52 Gyr 單調下降；GS-z14-0 15–36 Myr ≪ 287 Myr
```

**Q 系列最終決算**：Q1 🟢（銀河暈非年輕星系）· Q2 🟢（光譜推齡 = 成熟統計技術）· Q3 🟢（0/7 候選超 13.787）· Q4 🟡（無大爆炸受壓未否證；OBS 結算 ΛCDM 5/5 vs IDCM 0/1）

**OBS 最終結算**：ΛCDM t=0 預言 5/5 兌現（R6 包絡下降＋0 違反＋GS-z14-0＋0/7 超齡＋普遍約束）；IDCM 唯一可測形式（z-無關包絡）0/1 被拒。**天平在 ΛCDM 側；IDCM「無大爆炸」= 未被數據支持嘅假設，但未被否證。**

**closeout 全鏈重跑**（T1，2026-10-05 14:12–14:13）：
- scripts/01–06 全部 `/usr/bin/python3` 重跑 exit 0
- 5/6 logs byte-identical（diff 對正典＝0）；data 5/6 sha 一致
- ★ **scripts/03 正典漂移修正**：scripts/03.py 嘅 C2-c 曾 patch（改為 v9 540/466 不一致 finding 斷言），
  但 patch 後 logs/03＋data/03 從未重跑（停留 pre-patch 2/4 版）。closeout 重跑現行 code = **3/4 PASS**
  （C2-c finding 確立 PASS；C2 約定誤仍 FAIL）。已將 logs/03 更新為現行 code 之正典；data/03 同；
  舊 2/4 版 log/data 留 `~/.hermes/backups/o232_closeout_20261005_1412/`（sha256.before.txt 對照）。
  ⚠️ docs/02 §7 及 final_result 舊文引用「scripts/03（2/4；2 個誠實 FAIL 之一為約定誤、一為 v9 不一致之 finding）」
  —— 該描述係 **pre-patch 狀態**；現行 = 3/4（finding 已 PASS 確立）。原文保留，本節為更正。

**交接（R5 → O213）**：handed_off event（12:25）＋ Q4 CMB/BBN 不可投影化判據 note 落 O213（closeout 輪補齊）。
目標 O 零檔案寫入（register-only，符合調律者紀律）。

**密度基準（最終）**：核心閉合 claim = scripts/01 13/13（IDCM 階梯重現，N_search=10 凍結池＋N_mc=200,000 seed=232）；
R6 係**負面/數據側**判定（零正面 claim，冇參數可湊）⟹ 唔涉見數後湊算子。Q3 0/7 係文獻引用統計，冇新參數。

---

## 十五、O213 裁決回覆（append-only；2026-10-05 closeout 後補記 — R5/Q4 已裁定）

**O213 已於 2026-10-05 20:56 closeout 完成裁決**（`o213_world_dynamics/docs/13_handoff_adjudications.md` §4/§5；register note 20:56:55/20:57:04；O213 全驗 291/291）。本節記錄 O232 收到裁決後之最終狀態。

### R5 🔄 → ✅ 已裁定（O213 §4）

O213 裁定三問：
1. **v10 中 z=17 早端截斷「唔再成立」為渲染深度語義**——佢係 v9 用 ΛCDM 齡（t_age(17)）反推製造嘅敘事；44/43 撤回後輸入唔存在，截斷失卻結構地位。剩低 z=17 只係 ℓ = log₄18 ≈ 2.085 之**級聯內部刻度**（Nyquist 類比資訊截斷），**唔係宇宙生時**（若未來講「早端」只能叫 `ℓ_cut = ⌈log₄18⌉` = 3，唔可以叫宇宙齡）。
2. **216 Myr 基準 = ΛCDM t_age(z=17) 換算**（O213 scripts/14 H1：Planck 225.7 Myr／H0=70 222.6 Myr；v9 記 211/216 接近）⟹ 216 Myr = **外部 ΛCDM 換算，非 IDCM 結構量**。
3. **τ + t_f(z17) = 13.696 讀法 = 無結構地位**：「−0.2σ 命中」係 category error（O232 R1 已撤 1.6σ 框架同源）⟹ **(A) 冇天花板讀法成立**；(B) z=17 截斷讀法唔成立。

**可測預言判決（回應 O232 Q4 之翻身要求）**：v9 z=17 早端截斷 **不能翻身為「年齡分佈形狀預言」**——因為 v10 冇宇宙齡函數（O51 撤回）。可翻身方向 = **ℓ 級聯資訊截斷之投影**：`1+z = B^ℓ`，ℓ_cut = 3 有 shell 熵 ΔS 跳變，投影 = 特定 z 觀測者不可見現場（高 z 源密度邊界）——該邊界同 ΛCDM z≈17「第一顆星」邊界**唔同一物理**（IDCM：級聯資訊；ΛCDM：再電離前無光）。可測方向承交 O76/O132 翻譯層。

### Q4 🟡 → ✅ 判據接受（O213 §5）

O232 closeout 提出之可證偽判據（CMB/BBN/LSS 若證明唔可能係投影 = 殺 IDCM 無大爆炸）**被 O213 接受為正式判據**（閉合 ≠ 免疫；O213/O51/O232 共用，關聯在 register），並具體化三子判據：
- **① CMB「非黑體殘差」**（μ/y 型譜畸變；COBE/FIRAS 上限 1e-5 級）——黑體之**投影不變性**令純黑體本身唔判別投影 vs 熱浴，判據係「殘差非零」非「黑體」本身；
- **② BBN 三比值系統一致**（Ω_b = 1/20；Ω_c/Ω_b 13/2 17.6σ、Ω_b/Ω_m 2/15 14.5σ）——現狀**一致**；
- **③ LSS 真實引力演化需要**——現狀 IDCM 零參數 D_A/D_H 吻合（O76 🟢）；T(k) 判據留 O100/O133。

### 對 O232 最終結論之影響

**零影響（結論不變，但翻身條件收窄）**：
- 「τ ≠ 年齡天花板」✓、「13.8 = 外部錨」✓、「翻譯層」✓、「R6 數據側偏 ΛCDM」✓、「Q1–Q3」✓ —— 全部維持。
- **Q4 翻身條件收窄**：原說「R5 早端截斷 216 Myr 須變可測預言先可以翻身」——O213 裁定**該形式不可翻身**（非 IDCM 量）；可測方向改為 ℓ_cut 級聯資訊截斷投影（O76/O132 承接）。「無大爆炸」現狀維持 **🟡 受壓未否證**，三子判據任何一項被觸發即升級。
- register：O213→O232 兩條 note（20:56:55 #s4、20:57:04 #s5）為裁決記錄；本節為 O232 側收據。

**R 系最終決算（含 O213 裁定後）**：
```
R1 🟢  R2 ⚫  R3 🟢  R4 🟢  R5 ✅ 已裁定 (O213: 截斷唔成立; 216Myr=ΛCDM換算; τ+t_f 無結構地位)
R6 🟡 數據側偏 ΛCDM    Q1–Q3 🟢    Q4 🟡 受壓未否證 + 判據接受 (三子判據)
```

---

## 十六、原設問題最終裁決（append-only；2026-10-05 closeout 後補記 — 直接回答 §一 之二選一）

**§一 原設問題**：「本 O 判定：該量測係**排除 IDCM、抑或與 IDCM 相容**？」

**裁決：兩者皆非正確表述——該量測對 IDCM「無約束力（正交）」；兌現層面係「零正面預言」。**

| 選項 | 裁決 | 理由（證據） |
|:---|:---|:---|
| **排除 IDCM** | ✗ 不成立 | R1（docs/02）：τ = 13.4701 Gyr 係**光行距離**，唔係年齡天花板；「A_★ − τ = 0.26 Gyr」相減係 **category error**（已撤銷）。IDCM **冇 A_★ 預言**可被違反 ⟹ 論文之 ΛCDM 天花板測試對 IDCM **正交**，量測不能排除 IDCM。 |
| **與 IDCM 相容** | ⚠️ 不能宣稱 | R4（docs/05）：論文之 age 預設 t=0 客觀齡；IDCM 冇 t=0 ⟹ 兩者嘅「齡」喺翻譯層內係 **AGE↔AGE = NO-MAP**（冇共同 category 可比）。「相容」需要有共同 AGE 量先可以成立——呢度冇。 |
| **正解 = 無約束力／正交** | 🟢 唯一正確表述 | 兩個框架喺星齡前線**冇共同可測量**：OBS 層面（A_★ = 13.73 觀測值）兩者直接共用，但對 IDCM **冇對應結構預言**（τ 係距離，唔係齡）。 |

**但——「無約束力」只係「排除/相容」二分之外嘅正解，唔等於 IDCM 冇壓力**：
- R6（docs/03）：同一批高 z 數據嘅星齡包絡**跟住 ΛCDM 天花板**（0/2,282 違反；4.55→0.52 Gyr 單調下降；GS-z14-0 15–36 Myr ≪ 287 Myr）；IDCM 唯一可測形式（z-無關包絡）**被拒**。
- Q3（docs/06）：0/7 候選超 13.787 Gyr——數據與 ΛCDM t=0 一致。
- ⟹ 綜合：論文（Banik+2026）**既不排除亦不確認 IDCM**（正交），但**同一數據集顯示 ΛCDM 星齡預言 5/5 兌現 vs IDCM 0/1 可測形式受損**（Q4 天平）。

**一句結論（對 §一 之直接回答）**：該量測係**排除唔到 IDCM**（因 IDCM 冇可被我哋違反之預言，測試正交），**亦不能確立相容**（範疇 NO-MAP）；正確裁決 = **「正交／無約束力」＋ IDCM 喺星齡前線零正面預言**——依 R4 翻譯層，呢個先係 OBS↔OBS 層面可比嘅完整答案（docs/02 R1 + docs/05 R4 + docs/03 R6 三合一）。

> 更正註：closeout §十四/十五 用「診斷性負面閉合」概括本 O——本節補上對 §一 二選一之**直接**文字答案（上述表格），兩者一致（§十四之「負面」= 零正面預言；本節為其問題層對齊）。
