# O238 — 質量 = 代價^{φ²}：逆推質量譜 (mass as geometric cost)

<!-- registry
pid:     O238
title:   質量 = 代價^{φ²}：逆推質量譜 (mass as geometric cost)
state:   partial
verdict: partial
flags:   -
owner:   O238
created: 2026-10-11
updated: 2026-10-11
prereq:  O209 / O136
source:  O209 docs/19 交接 (2026-10-11)
-->

> **狀態**: 📄 **已註冊 — 未開始**（session start 已寫，推導未開始）
> **建立**: 2026-10-11
> **前置**: O209（docs/19 逆推攻堅）、O136（docs/25/29 觀察代價先例）
> **位置**: `open_problems_fresh/o238_mass_as_cost/`

---

## 一、問題陳述

質量譜最優形式係 **m_n = C·|dm|_n^α**（|dm| = 幾何連結代價 = 位置算子二階自能，O136 docs/25 定理），freeze scheme 下 **α ≈ φ² = 4cos²(π/5)**。**但標度 C = 1.47e−6 MeV ≠ M₀ 未接入框架；且 C_f ∝ |dm|^{φ²}/γ 反推 FAIL（slope 0.374）——C_f 仍然無算子身份（O233 維持）；c/s 離群仍然未解。** 本 O 係「質量 = 代價」逆推路線之正式攻堅。

## 二、已確立嘅結構

```
🟢 |dm| = V²G 對角 = 位置算子二階效應 = 幾何連結代價 —— 質量譜 9 點 fit 最佳候選（RMS 0.5802，優於 sin 1.9×；O136 docs/25 + O209 docs/19 P1）
🟢 freeze OLS α = 2.616977 ± 0.151 ≈ φ² = 4cos²(π/5)（20面體角，−0.01σ）——freeze scheme 下首選斜率（79/30 −0.11σ 退次選）
🟢 φ² = 4cos²(π/5) EXACT，π/5 係二十面體角 —— O223 / O137 二十面體線既有幾何，唔係新常數
🟢 中心性候選（eigenvector/degree/betweenness/closeness）全敗 —— 質量代價 = 能量倒數耦合，唔係圖論位置
🔴 標度 C = m/|dm|^{φ²} ≈ 1.47e−6 MeV ≠ M₀ = 27.9 MeV（差 1.9e7）—— 未接入框架
🔴 C_f ∝ |dm|^{φ²}/γ FAIL（slope 0.374 需 1，RMS 0.555）—— O233「C_f 無算子」維持
🔴 c/s 離群喺 φ² 固定下仍在（c +0.80、s +1.18）—— 離群同斜率無關，鎖 C_f 生成層
```

## 三、未確立（🔴 開放問題）

```
🔴 標度 C 嘅框架身份 —— C 應該係 M₀ 嘅咩函數？（O38/O170 M₀ = √(E_PħH₀)·φ^… 已係宇宙錨；C 要接返呢個標度）
🔴 φ² vs 79/30 統計判別 —— σ_α = 0.15 太大，兩者都喺 1σ 內（0.01σ vs 0.11σ）；需要 freeze v2 質量集或樣本外盲測先分到
🔴 c/s 離群機制 —— C_f 生成層；κ 張量非對角（O53/O59）係最終候選，未喺本 O 驗證
🔴 C_f 算子身份 —— |dm|^{φ²}/γ 已死；仲有咩幾何量組合未試
```

## 四、攻擊路線

```
1. 標度 C 攻堅 → 測試 C = M₀·|dm|_ref^{−φ²}（邊個模式係 ref？|dm| 中位/最大/γ 特殊位）；預期將 m_n = C·|dm|_n^{φ²} 變成零參數公式
2. φ² vs 79/30 判別 → freeze v2 質量集（O234 更新）或樣本外盲測（新質量比）；流程見 O209 docs/16 準則
3. c/s 離群 → C_f 生成層內 κ 張量非對角測試（O233 docs/16 §八）；跨 O 需授權
4. （備援）C_f 其他幾何組合掃描 → 但 5 線負已排除大多數；低優先
```

## 五、驗證標準

```
✅ m_n = C·|dm|_n^{φ²} 全零參數（C 由框架常數表達）且 9 點 RMS < 0.05
✅ φ² vs 79/30 樣本外判別（freeze v2 / 新質量點）
✅ c/s 離群機制閉合（κ 非對角或等價結構）
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-11 | 註冊 + session start（由 O209 docs/19 交接；聲明「先重現 scripts/19 驗證再推」） | 01_problem_record.md + SESSION_START.md |
| 2 | 2026-10-11 | **推導鏈完整性重現 PASS**（O209 scripts/19 5/5 + 16 7/8 + 全鏈 423/426 + 04 181/181；git clean 確認未被並行改動）；標度 C 身位診斷：`C=M₀·|dm|_mode^{−φ²}` 排除（ref=603.2 最近 1.1%）、C/M₀ 池 0 命中、★C_n spread=RMS ⇒ 標度同 c/s 離群同源 | docs/02-03 + scripts/01-07 + data/01-07 + register note |
| 3 | 2026-10-11 | **路線 1/2 收窄**：標度 C 凍結池+譜泛函+雙參數全排除；α≈φ² LOOCV 全域穩健（剔任何一點 0.42σ 內）；φ² vs 79/30 LOOCV 不可分（ratio 0.9983, P=0.50）；c/s 遮蔽標度（剔後 C −24.6%、RMS 0.252）；n≡1 mod4 族修正假象排除（P=0.22） | docs/03（整合） |

## 七、相關文件

```
- O209 open_problems_fresh/o209_selection_algebra/docs/19_inverse_cost.md — 逆推攻堅出處（5/5 PASS，commit 63252ee）
- O209 scripts/19_inverse_cost.py + data/19_inverse_cost.json — 要重現嘅腳本
- O136 docs/25_observer_interaction_attack.md + docs/29_gemini_b4_and_observation_cost.md — 「質量=代價」先例（位置算子二階自能 + 觀察代價族）
- O234 docs/02_round2_doff_census.md — freeze 質量集 + 不可證偽性定理
- O233 — C_f 5 線負閉合（本 O 要維持）
```