# O232 SESSION_START — 恆星年齡下界 vs IDCM 因果視界 (rendering window) — 13.8 Gyr 宇宙年齡張力之結構裁決

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

> **Session**: 2026-10-05（新建立）
> **狀態**: 🟢 **已閉合（2026-10-05 closeout；診斷性負面閉合 —— R1/R3/R4/R6 + Q1–Q4 全裁決；R5 已交 O213）**
> **來源**: 使用者提供之 technews.tw 2026-07-20 報導節錄 → 追出原文 arXiv:2607.00764
> **前置**: O51, O213, O73, O167, O76
> **位置**: `open_problems_fresh/o232_stellar_age_vs_horizon/`

---

## 一、接手起點

原文已定位（arXiv:2607.00764v1, Banik et al. 2026 MNRAS）；IDCM 年齡階梯已重算（13/13 PASS）。
docs/01 已列 D1–D6 六條分歧與淨結論。**未消之核心**：τ = 13.4701 Gyr vs A_★ = 13.73 ⇒ 1.6σ / 2.4% 缺口；
且 IDCM「13.8」無結構推導（凍結池 0 命中）。

## 二、先做嘅第一步

```
1. 讀 docs/01_paper_vs_idcm_divergence.md（六條分歧 + R1–R3）
2. 攻 R1（可觀測視界語義）：由 O213 docs/06 + O51，判 τ 是否 cap「可觀測星齡」
3. 若 R1 判為「硬天花板」⇒ τ = 13.47 與 A_★ = 13.73 之 1.6σ 缺口須立新結構路線（R2），禁事後擴池
```

## 三、已知陷阱

```
⚠️ 範疇陷阱：論文之 age 預設 t=0 客觀齡；IDCM 無 t=0 ⇒ 兩者不可直接對減（D1/§四）
⚠️ 事後擴池陷阱：13.8/τ = 1.02449；寬池 42/41 係連續整數泛型巧合，**禁**當結構（D6，🔴）
⚠️ 外部值污染：13.8 係 ΛCDM 錨，唔係 IDCM 結構量；不可回填成「IDCM 預言 13.8」
⚠️ 執行環境：一律 /usr/bin/python3（background python3 = miniforge 缺 numpy）；mpmath dps≥40 前唔好引用 dev
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| τ = 1/ω_ring = R_world/c | 13.470063 Gyr | O51 / O213 docs/06；scripts/01 C1 |
| T_ring = 2πτ | 84.6349 Gyr | O213 docs/06；scripts/01 C3 |
| t_true = 131·T_ring + τ | 11,100.642 Gyr | O213 docs/06；scripts/01 C4 |
| ω_ring | 72.59002746 (km/s)/Mpc | O73；scripts/01 |
| ω_cmb = ω_ring(1−π/44) | 67.4071 | O73/O167；scripts/01 C5 |
| A_★（外部） | 13.73 (+0.18/−0.15) Gyr | arXiv:2607.00764 |
| A_★^CMB / A_U^CMB（外部） | 13.6 / 13.8 Gyr | arXiv:2607.00764 |
| A_★^ETS / A_U^ETS（外部） | 12.71 / 12.91 Gyr | arXiv:2607.00764 |
| H₀_local（外部） | 73.17 ± 0.86 | arXiv:2607.00764 |
| A_★ − τ | 0.25994 Gyr = 1.575σ | scripts/01 |

## 五、交接 / 依賴

```
- 前置: O51（τ = R_H/c, t_true）、O213（t_true 定義）、O73/O167（ω_ring/ω_cmb）、O76（投影層）
- 移交出: （暫無）
- 範圍警告: 唔重推 O51/O213 之年齡框架；唔改 h0_tension/o73/o167/o76 任何檔案
            （跨 O 交接只限 register handoff/note + mirror）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## 六、更新（2026-10-05 第二輪，append-only）— R1 攻堅完成

**接手起點（更新）**：R1 已裁決 🟢 —— τ = 13.4701 Gyr **唔係** IDCM 年齡天花板
（v9 `35_rendering_depth`：τ 係環周長=「有幾遠」；`verify_young_galaxies.py`：明文「冇年齡上限」）。
首輪「1.6σ 缺口」框架係 **category error，已撤銷**（見 `docs/02`、`01_problem_record.md` §九）。

**先做嘅第一步（更新）**：
```
1. 讀 docs/02_r1_rendering_depth_verdict.md（R1 裁決 + 互斥讀法 + 判據）
2. 攻 R6：高 z (8–15) 恆星齡 vs scripts/03 之 t_age(z) 判據表 → JWST NIRSpec + Prospector/Bagpipes
3. R5（渲染深度早/晚端語義）→ 跨 O，交 register 予 O51/O213
```

**已知陷阱（新增）**：
```
⚠️ 範疇陷阱（實中）：τ 係「長度（周長）」, A_★ 係「年齡」——相減 = category error（首輪誤犯）
⚠️ 長度單位陷阱：Xiang+2024 LOGDIS = log10(d/pc)，5 kpc = 3.699，唔係 log10(5)=0.699
⚠️ 天文學約定陷阱：t_age(z) 隨 (H0,Ω_m) 變；v9 用 (70,0.3)、Planck 用 (67.4,0.315) —— 引數字必核約定
⚠️ 星表尾端污染：raw 高齡尾端 σ_A≥1.4，唔可當真齡（論文之 13.73 係清洗後 latent 值）
```

**關鍵數字（新增）**：
| 量 | 值 | 出處 |
|:---|:---|:-----|
| ΛCDM t_age(17) | 0.226 Gyr（Planck） | scripts/03 |
| raw N(>τ) (320,028) | 22,661（7.08%） | scripts/02 |
| 切割樣本 N(>τ) | 12,958（29.3%） | scripts/02 |
| 最老可渲染 (D=13.8) | 13.584 Gyr（0.9σ） | docs/02 §2 |

**產物（新增）**：`docs/02_r1_rendering_depth_verdict.md`、`scripts/02`（3/3）、`scripts/03`（2/4）、`data/raw/`（.gitignore 覆蓋）。

---

## 七、更新（2026-10-05 第三輪，append-only）— R6 攻堅（真數據）

**接手起點（更新）**：R6 已攻——數據側 🟡 偏 ΛCDM：JADES 高 z 星系星齡**未**違反 ΛCDM 天花板，且包絡隨 z 單調下降。
詳見 `docs/03_r6_highz_ceiling_verdict.md`。

**先做嘅第一步（更新）**：
```
1. 讀 docs/03（R6 判決＋v9 finding #2）+ docs/02（R1 裁決）
2. 攻 R3/R4：「13.8」之 observer-relative 定義 + 無 t=0 vs 論文 t=0 翻譯層（文獻/結構層）
3. R5（渲染深度早/晚端語義）→ register 交 O51/O213（跨 O）
```

**已知陷阱（新增）**：
```
⚠️ v9 示範數值不可靠：GS-z14-0「0.30 Gyr」實為 15–36 Myr（文獻）；引 v9 案例必核原文
⚠️ SED prior 壓制「星齡 > 宇宙齡」違反 ⟹ 違反數為零唔係獨立證據（要睇包絡形狀）
⚠️ 包絡判別：ΛCDM = max(age) 隨 z 降（跟 t_age）；IDCM「無天花板」可測形式 = max(age) 與 z 無關
⚠️ 選樣效應：亮選星偏年輕，高 z 包絡可能被低估
```

**關鍵數字（新增）**：
| 量 | 值 | 出處 |
|:---|:---|:-----|
| de la Vega+2025 違反 (mwa_50>t_age) | 0/2,282 | scripts/04 |
| 上包絡 max mwa_50 (z 升序) | 4.55 / 4.15 / 1.86 / 1.50 / 0.78 / 0.52 Gyr | scripts/04 |
| GS-z14-0 文獻星齡 | 15–36 Myr（Helton+24 / Carniani+24） | docs/03 §2 |
| t_age(14.32) | 287 Myr | scripts/04 |

**產物（新增）**：`docs/03_r6_highz_ceiling_verdict.md`、`scripts/04`（exit 0）、`data/04_jades_age_ceiling.json`、`data/raw/dlv.txt`（gitignored）。

---

## 八、更新（2026-10-05 第三輪，append-only）— R5 交接 + R3/R4 裁決

**接手起點（更新）**：R1/R3/R4/R6 已裁決，R2 消失，R5 已 handoff O213。O 已進入閉合整理階段。

**先做嘅第一步（更新）**：
```
1. 讀 docs/03–05（R6/R3/R4 判決）+ 01_problem_record §九–§十一（附註更正鏈）
2. 等 O213 回 R5（z=17 截斷/216 Myr 基準/t_f 讀法）——經 register，唔喺本 O 推
3. 若 R5 裁定後 O232 全系列閉合 → 正式 close（RESULT_TEMPLATE 格式, 附 category 標記）
```

**已知陷阱（新增）**：
```
⚠️ v9「13.8 = 渲染深度」敘述繼承 O51 撤回（44/43 偽影）——引用即違反版本隔離
⚠️ AGE↔DISTANCE 相減 = category error（R1 案例）；跨框架比較先標 category（R4 規則）
⚠️ τ+t_f(z17)=13.696 距 A_★ 0.2σ 係「讀法」唔係閉合——t_f 狀態未審計（R5 已交 O213）
```

**關鍵數字（新增）**：
| 量 | 值 | 出處 |
|:---|:---|:-----|
| t_render（撤回） | 13.7833 Gyr；44/43 vs Planck/τ dev 0.0267% | scripts/05 |
| τ + t_f(z17, Planck) | 13.6956 Gyr；vs A_★ −0.21σ | scripts/05 |
| 13.8 − τ | 0.3299 Gyr（無結構身份 🔴） | scripts/05 |

**產物（新增）**：`docs/04_r3_13p8_definition.md`、`docs/05_r4_translation_layer.md`、`scripts/05`（6/6）、`data/05_r3_r4_definition_ladder.json`。register：O232→O213 handoff、O51 note（mirror）、progress（R3+R4）。

---

## 九、更新（2026-10-05 第四輪，append-only）— 框架擴展 Q1–Q4

**接手起點（更新）**：調律者將 O232 框架擴展到「銀河系星齡 vs IDCM 無起始」——Q1–Q4 已全數裁決（docs/06–07）。

**先做嘅第一步（更新）**：
```
1. 讀 docs/06（Q1–Q3 星齡三問）+ docs/07（Q4 無大爆炸評估）+ scripts/06 表
2. O232 星齡側已完 — 剩低 = O213 回 R5（早端截斷 216 Myr 可測化）→ 先可以正式 close
3. 若調律者想推 CMB/BBN「不可投影化」判據 → 屬 O51/O213 範圍, 經 register 開題
```

**已知陷阱（新增）**：
```
⚠️ 白矮星「冷卻齡」係總齡下界（要 + 前身主序 ~0.5–1 Gyr）——引用時唔好當總齡
⚠️ 紅矮星「壽命 10^3–10^4 Gyr」唔等於「有咁老嘅星」——t=0 令形成時間 ≥ 0
⚠️ 「冇星 > 13.8」本身唔違反 IDCM（IDCM 冇星齡預言）——真正壓力係 R6 包絡形狀
⚠️ Q4 係「假設受壓 vs 被否證」之分——唔可以過度宣稱 IDCM 錯
```

**關鍵數字（新增）**：
| 量 | 值 | 出處 |
|:---|:---|:-----|
| 穩健超齡候選 | 0/7（HD 140283 +0.84σ 最接近） | scripts/06 |
| WD 冷卻齡 | 12.1–13.5 Gyr（M4/NGC6752） | scripts/06 |
| 紅矮星主序壽命 | 10³–10⁴ Gyr（長命 ≠ 老過宇宙） | scripts/06 |
| OBS 結算 | ΛCDM 5/5 兌現 vs IDCM 0/1 被拒 | docs/07 §1 |

**產物（新增）**：`docs/06_milkyway_stellar_age_questions.md`、`docs/07_no_bigbang_falsifiability.md`、`scripts/06`（exit 0）、`data/06_stellar_age_candidates.json`。
---

## 十、更新（2026-10-05 第五輪，append-only）— 正式 closeout

**⭐ O232 正式閉合（verdict = closed，診斷性負面閉合）** — 2026-10-05 closeout 完成：

- **全鏈重跑**：scripts/01–06 全部 exit 0；5/6 logs byte-identical；data 5/6 sha 一致（對 `~/.hermes/backups/o232_closeout_20261005_1412/`）
- **★ scripts/03 正典漂移修正**：C2-c 曾 patch（v9 540/466 finding 斷言）但 patch 後未重跑 ⟹ logs/03/data/03 停留 pre-patch 2/4；closeout 重跑現行 code = **3/4**，正典已更新（舊 2/4 留備份）
- **R 最終**：R1 🟢 / R2 ⚫ / R3 🟢 / R4 🟢 / R5 🔄 handoff O213（12:25 ＋ Q4 判據 note）/ R6 🟡 數據側偏 ΛCDM
- **Q 最終**：Q1–Q3 🟢（銀河非年輕星系；光譜推齡成熟；0/7 超齡）；Q4 🟡 無大爆炸受壓未否證，OBS 結算 ΛCDM 5/5 vs IDCM 0/1
- **交接**：R5 渲染深度早/晚端語義 → O213（handoff event ＋ Q4 CMB/BBN 不可投影化判據 note）；目標 O 零檔案寫入
- **產物**：`01_problem_record.md` §十三（水位）＋§十四（決算）、`data/MANIFEST.json`（trail C4）、README row 🟢、register close

---

## 十一、更新（2026-10-05 closeout 後補記，append-only）— O213 已裁定 R5/Q4

**O213 已於 2026-10-05 20:56 closeout 裁定**（`o213_world_dynamics/docs/13_handoff_adjudications.md` §4/§5）：

- **R5 ✅ 已裁定**：① v10 中 z=17 早端截斷 **唔再成立**為渲染深度語義——剩低只係 ℓ = log₄18 ≈ 2.085 級聯內部刻度（`ℓ_cut = ⌈log₄18⌉` = 3），非宇宙生時；② **216 Myr = ΛCDM t_age(17) 換算**（Planck 225.7 Myr／H0=70 222.6 Myr），非 IDCM 結構量；③ **τ+t_f(z17)=13.696 讀法無結構地位**（category error 同 R1 源）；(A) 冇天花板讀法成立。
- **Q4 判據 ✅ 接受**：具體化三子判據——① CMB「非黑體殘差」（μ/y 譜畸變；黑體投影不變性⟹純黑體唔判別投影 vs 熱浴）② BBN 三比值系統一致（Ω_b=1/20 現狀一致）③ LSS 真實引力演化需要（T(k) 留 O100/O133）。
- **翻身條件收窄**：v9 z=17 早端截斷**不能翻身為年齡分佈預言**；可測方向 = ℓ_cut 級聯資訊截斷投影（高 z 源密度邊界；同 ΛCDM z≈17 第一顆星唔同一物理）→ 交 O76/O132。
- **O232 結論零影響**：所有 R/Q 維持；Q4 維持 🟡 受壓未否證。
- 產物：`01_problem_record.md` §十五（收據）、本節、final_result §更新、時序索引 row 16。

---

## 十二、更新（2026-10-05 closeout 後補記 2，append-only）— 原設問題直接裁決

**§一 原設問題（「該量測係排除 IDCM、抑或相容？」）之直接答案已補**（`01_problem_record.md` §十六）：

**兩者皆非——排除不成立（R1：τ≠天花板，測試正交）、相容不能宣稱（R4：AGE↔AGE NO-MAP）；正解 = 「正交／無約束力」＋「星齡前線零正面預言」**。壓力面不變（R6 包絡跟 ΛCDM、Q3 0/7、Q4 🟡）。
