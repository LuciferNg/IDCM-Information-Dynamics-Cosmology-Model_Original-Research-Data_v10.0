# O232 — 恆星年齡下界 vs IDCM 因果視界 (rendering window)

## 狀態: 🟡 部分比對完成（13/13 PASS）— 核心張力未消

## 結論
原文 = arXiv:2607.00764v1 (Banik et al. 2026, MNRAS)：最老恆星 A_★ = 13.73 (+0.18/−0.15) Gyr。
IDCM 結構齡 τ = R_world/c = 1/ω_ring = **13.4701 Gyr**，低於 A_★ 達 **0.26 Gyr = 1.6σ / 2.4%(vs CMB 13.8)** ⇒ 🟡 未消之核心張力。
IDCM 與該研究：H₀ 一致（0.4–0.7σ）、皆否定早期新物理；機制分歧（IDCM 投影層 vs 論文局域空洞）。
IDCM 文獻之「13.8 Gyr」**無結構推導**（13.8/τ = 1.02449，凍結結構池 0 命中）⇒ 🔴 係外部錨。

## 關鍵公式
- τ = 1/ω_ring = R_world/c = 13.470063 Gyr（因果視界 / rendering window）
- t_true = 131·T_ring + τ = 11,100.642 Gyr（T_ring = 2πτ = 84.6349）
- 張力: A_★ − τ = 0.25994 Gyr = 1.575σ(星)；τ − A_U^ETS = +4.34%；A_U^CMB − τ = +2.39%
- H₀: ω_ring = 72.590 → vs H₀_local 73.17±0.86 = 0.67σ

## 依賴
O51 → O213 → O73/O167 → O76 → O232

## 密度基準
- N_search = 10（凍結結構池 p/q, 1<p/q≤1.10；post-hoc 寬池另 25，僅 42/41,43/42 ⇒ 🔴）
- N_mc = 200,000，seed = 232（hit density 0.000%）
- d_obs = 1.93%（|A_★−τ|/τ；CMB 側 2.39%）
- d_med = 未計
- q_obs = 未計 ⇒ **本 O 未閉合（🟡）**

## R# 未決
R1 τ 是否為可觀測星齡硬天花板？ R2 0.26 Gyr 缺口結構因數（禁事後擴池）？ R3 「13.8」之 observer-relative 定義？ R4 無 t=0 vs 論文 t=0 之翻譯層？

> ⚠️ O208 規則: 冇分位數 = 未閉合。本 O 現為 🟡。
> 產物：docs/01_paper_vs_idcm_divergence.md、scripts/01_idcm_age_ladder.py（13/13）、logs/01、data/01。

---

## 更新 2026-10-05（第二輪，append-only）— R1 攻堅

## 狀態: 🟡 → 🟢(R1 部分) / 核心分歧重定義

## 結論（更新）
**R1 已裁決 🟢**：τ = 1/ω_ring = 13.4701 Gyr **唔係** IDCM 年齡天花板（v9 `35_rendering_depth` 明言 τ 係環周長=「有幾遠」；
`verify_young_galaxies.py` 明文「冇年齡上限」）。故第一輪之「A_★ − τ = 1.6σ / 2.4%」框架係 **category error，撤銷**。
論文之 ΛCDM 天花板測試**正交**於 IDCM（IDCM 無 A_★ 預言）⇒ 論文既不確認也不否證 IDCM。
可分辨判據 = 高 z（8–15）恆星齡 vs ΛCDM t_age(z)。

## 關鍵公式（新增）
- IDCM 天花板：無（高 z = 更遠非更年輕）
- ΛCDM 判據天花板：t_age(z) = A_U − lookback(z)；t_age(10)=0.472、t_age(17)=0.226 Gyr（Planck）
- 若採「渲染深度=天花板」讀法：最老可渲染 = D − 0.216 Gyr（D=13.8→13.584, 0.9σ；D=13.47→13.254, 2.9σ）

## 外部數據（scripts/02；Xiang+2024, 320,028；NADC DOI 10.12149/101467）
- raw N(>τ)=22,661（7.08%）；達 YY 網格上限 20 Gyr；類論文切割樣本 29.3% > τ；尾端 σ_A≥1.4 噪聲主導。

## 依賴（新增）
arXiv:2607.00764 + Xiang+2024 ↔ v9 `35_rendering_depth` / `04_rendering_boundary` / `verify_young_galaxies`

## 密度基準（新增）
- scripts/02: N=320,028（全星表，非池），3/3 PASS
- scripts/03: t_age(z) 積分表，2/4（2 FAIL = 1 約定誤 + 1 v9 不一致之 finding）

## R# 未決（更新）
R1 🟢 已裁決 · R2 ⚫ 消失 · **R3 🟢 已裁決：「13.8」= 外部 ΛCDM 錨（t_render 44/43 偽影已撤回 O51；τ+t_f=13.696 距 A_★ 0.2σ 係讀法非閉合）** · **R4 🟢 已裁決：翻譯層成文（6 category＋5 規則；D1 = NO-MAP）** · **R5 🔄 已 handoff O213（渲染深度早/晚端；t_f 狀態）** · **R6 🟡 數據側(偏 ΛCDM)：0/2,282 中位違反; 包絡單調下降 4.55→0.52 Gyr 拒 z-無關形式; GS-z14-0 星齡 15–36 Myr ≪ 287 Myr 天花板**

## 更新 2026-10-05（第三輪，append-only）— R3/R4 裁決 + R5 交接
- `scripts/05`（6/6 PASS；logs/05、data/05）：t_render=13.7833 = τ×44/43 撤回重現（dev 0.0267%）；13.8−τ=0.33 無結構身份；τ+t_f(17,Planck)=13.696 vs A_★ −0.21σ
- `docs/04_r3_13p8_definition.md`：R3 🟢 —— IDCM v10 冇「13.8」存活內部定義（唯一候選已撤回）；13.8 = 外部錨
- `docs/05_r4_translation_layer.md`：R4 🟢 —— 翻譯層 6 category ＋ 5 規則；只允許 OBS↔OBS 直接比較；D1 = NO-MAP
- R5：register `handoff O232→O213` ＋ O51 note（撤回聲明 mirror）——待 O213 裁定 z=17 截斷/216 Myr 基準/t_f 讀法

> ⚠️ v10 權威補充：O51 已撤回（2026-08-22）「t_render=13.7833 Gyr（44/43 校準偽影）」——v9 任何「13.8=渲染深度」敘述繼承撤回，不得引用為結構。
> 🔴 v9 findings（只記錄，不修 v9）：① docstring 540 Myr vs 自身 code 466 Myr（scripts/03）；② GS-z14-0 0.30 Gyr vs 文獻 15–36 Myr（scripts/04）

## 更新 2026-10-05（第四輪，append-only）— 框架擴展 Q1–Q4
- `scripts/06`（exit 0；logs/06、data/06）：銀河系星齡候選表 **0/7 穩健超齡**（vs A_U=13.787）——HD 140283 2013 +0.84σ / 現代 +0.16σ；白矮星冷卻 12–13.5；紅矮星「長命 ≠ 老過宇宙」
- `docs/06_milkyway_stellar_age_questions.md`：Q1 🟢（銀河暈非年輕星系；約束普遍非因果）· Q2 🟢（光譜推齡 = 成熟統計技術：YY isochrones＋MCMC latent＋FLAME）· Q3 🟢（冇穩健 >138 億歲星）
- `docs/07_no_bigbang_falsifiability.md`：Q4 🟡 **受壓未否證** —— 星齡前線 OBS 結算 ΛCDM 5/5 兌現 vs IDCM 0/1 可測形式被拒；無大爆炸 = 未被數據支持嘅假設；翻身條件 = R5 早端截斷變可測預言（交 O213）
---

## 更新 2026-10-05（第五輪，append-only）— 正式 closeout

## 狀態: 🟢 已閉合（2026-10-05；診斷性負面閉合 — verdict = closed）

## 結論（最終）
**論文（Banik+2026 A_★=13.73）與 IDCM 之分歧已結構裁決**：τ=13.4701 Gyr 係光行距離（周長），**唔係年齡**（R1 🟢）；
IDCM v10 冇「13.8」存活內部定義（t_render 44/43 偽影已撤回；R3 🟢）；跨框架時間陳述須標 category（R4 🟢，D1=NO-MAP）。
**OBS 結算：ΛCDM t=0 5/5 兌現 vs IDCM 0/1 可測形式被拒**（R6 🟡）——「無大爆炸」受壓但未否證（Q4 🟡）。
銀河系非年輕星系（Q1 🟢）、光譜推齡 = 成熟統計技術（Q2 🟢）、0/7 候選超 13.787 Gyr（Q3 🟢）。
**R5（渲染深度早/晚端語義）已交 O213**（handoff ＋ Q4 CMB/BBN 判據 note）——係 O232 唯一跨 O 遺留。

## 關鍵公式（最終）
- τ = 1/ω_ring = R_world/c = 13.470063 Gyr（因果視界 = 光行距離，非年齡）
- t_true = 131·T_ring + τ = 11,100.642 Gyr（環上相位標籤；IDCM-ONLY）
- ΛCDM 天花板：t_age(z) = A_U − lookback(z)；t_age(10)=0.472 / t_age(17)=0.226 Gyr（Planck）
- IDCM「z-無關包絡」可測形式被拒（R6：JADES 包絡 4.55→0.52 Gyr 單調下降）
- τ + t_f(z17) = 13.696 Gyr 距 A_★ −0.21σ —— 🟡 讀法（t_f 狀態交 O213）

## 依賴
O51 → O213 → O73/O167 → O76 → O232

## 密度基準（最終）
- 核心閉合：scripts/01 13/13（IDCM 階梯重現；N_search=10 凍結池；N_mc=200,000 seed=232；0 命中）
- R6/Q4 係**負面/數據側判定**：零正面 claim、零新參數、冇凑算子；Q3 0/7 = 文獻引用統計
- scripts/03 最終 3/4 PASS（★ closeout 糾正：pre-patch 正典 2/4 曾未同步，現行 code 3/4）

> ⚠️ O208 規則應用：本 O 為**診斷性負面閉合**（問題 = 外部測試 vs IDCM），全部子裁決帶書面判定；
> 閉合判據 = R/Q 全滅＋交接完畢，非數值擬合 ⟹ 唔適用「冇分位數 = 未閉合」於最終 verdict。

---

## 更新 2026-10-05（closeout 後補記，append-only）— O213 裁定已收

**O213 已裁定 O232 R5/Q4**（o213 docs/13 §4/§5，2026-10-05 20:56）：
- **R5 ✅**：z=17 早端截斷唔成立為渲染深度（剩 ℓ_cut=3 級聯刻度）；216 Myr = ΛCDM t_age(17) 換算（非 IDCM 量）；τ+t_f(z17)=13.696 無結構地位 ⟹ 冇天花板讀法成立
- **Q4 🟡 維持**：判據接受並具體化三子判據（CMB 非黑體殘差／BBN 系統一致／LSS 引力演化）；翻身條件收窄 = ℓ_cut 資訊截斷投影（交 O76/O132），v9 早端截斷**不能翻身**
- O232 結論零影響（R1/R3/R4/R6＋Q1–Q3 全維持）

## 狀態（最終）: 🟢 已閉合（2026-10-05；diagnostic negative；R5 已裁定收齊）

---

## 原設問題直接裁決（append-only；2026-10-05 closeout 後補記）— §一 二選一之答案

**§一 問：「該量測係排除 IDCM、抑或與 IDCM 相容？」**

**答案：兩者皆非——排除不成立、相容不能宣稱；正解 = 「正交／無約束力」＋「零正面預言」。**
- ✗ **排除**：R1 τ=13.4701 係光行距離非年齡天花板；「A_★−τ」相減 = category error（已撤）；IDCM 冇 A_★ 預言可被違反 ⟹ 測試正交，量測不能排除 IDCM。
- ⚠️ **相容**：R4 翻譯層 — 論文 t=0 客觀齡 vs IDCM 無 t=0 = AGE↔AGE **NO-MAP**，冇共同 category 可比，「相容」不可宣稱。
- 🟢 **正解**：IDCM 喺星齡前線冇共同可測量（τ 係距離）；OBS 層面 A_★=13.73 兩框架共用但 IDCM 零結構預言。
- **壓力仍在**：R6 高 z 包絡跟 ΛCDM 天花板、Q3 0/7 超齡 ⟹ ΛCDM 5/5 兌現 vs IDCM 0/1 形式受損（Q4 🟡 維持）。

（詳表：`01_problem_record.md` §十六；R1/R4/R6 證據：docs/02、docs/05、docs/03。）

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `c8bddd007d178f07` | 2026-10-24 | closed | 原文 = arXiv:2607.00764v1 (Banik et al. 2026, MNRAS)：最老恆星 A★ = 13.73 (+0.18/−0.15) Gyr。 IDCM 結構齡 τ = Rworld/c = 1/ωring =… | open_problems_fresh/o232_stellar_age_vs_horizon/final_result.md | — |
<!-- conclusion-history:end -->
