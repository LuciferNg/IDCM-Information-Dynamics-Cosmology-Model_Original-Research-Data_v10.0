# O238 SESSION_START — 質量 = 代價^{φ²}：逆推質量譜 (mass as geometric cost)

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

> **Session**: 2026-10-11（新建立）
> **狀態**: 📄 **已註冊 — 未開始**
> **來源**: O209 docs/19（逆推「質量 = 幾何連結代價」攻堅，commit `63252ee`）
> **前置**: O209（docs/19 + scripts/19 + data/19）、O136（docs/25/29）、O234（freeze v1.1 質量集）
> **位置**: `open_problems_fresh/o238_mass_as_cost/`

---

## 一、接手起點

O209 docs/19（2026-10-11，scripts/19 = 5/5 PASS）確立咗「質量 = 代價^{φ²}」為現行最佳質量譜形式，但**三項未閉合**：① 標度 C = 1.47e−6 MeV ≠ M₀；② C_f ∝ |dm|^{φ²}/γ 反推 FAIL（O233 維持）；③ c/s 離群（c +0.80、s +1.18）鎖 C_f 生成層。**本 O 未開始推導**——開 session 第一步係重現 O209 嘅 scripts 同驗證，確認基礎穩固先推。

## 二、先做嘅第一步（推導鏈完整性）

```bash
# 1. 重現 O209 逆推攻堅（跳去 O209 目錄，唔好喺 O238 度複製）
cd open_problems_fresh/o209_selection_algebra
/usr/bin/python3 scripts/19_inverse_cost.py        # 期望 RESULT: 5/5 — freeze OLS α ≈ φ² (0.01σ)、C_f slope 0.374 FAIL、中心性全敗
# 2. 重現 scheme 重推（α_OLS 嘅 freeze 數值來源）
/usr/bin/python3 scripts/16_scheme_rerun.py        # 期望 RESULT: 7/8 — freeze OLS = 2.61697737
# 3. 全鏈確認（O209 總計 423/426）
for s in 11 12 13 14 15 16 17 18 19; do /usr/bin/python3 scripts/${s}_*.py | tail -1; done
/usr/bin/python3 scripts/04_doc_crosscheck.py      # 期望 181/181
# 4. 驗證 data/19_inverse_cost.json 同 docs/19 對照（alpha_ols_frz=2.616977, phi2_sigma=-0.01 等）
# 5. 先讀 O209 docs/19 + O136 docs/25/29 再開始推（标度 C 路線）
```

**重現失敗 / 數值唔對 ⇒ 停低，唔好開始推。** 檢查 O209 是否被並行 session 改動（git log + git status）。

## 三、已知陷阱

```
⚠️ 標度 C 嘅「唔等於 M₀」係誠實現狀——唔好為咗湊 M₀ 硬拗（docs/25 C=5.39e−5 都係咁）
⚠️ φ² vs 79/30 統計不可分（σ_α=0.15）——唔可以話「驗證咗 φ²」，只可話「freeze 下更自然」；要樣本外先判
⚠️ c/s 離群唔係斜率問題——換 α 唔會令離群消失（φ² 固定下 c +0.80、s +1.18 仍在）
⚠️ 跨 O：κ 張量非對角係 O53/O59 幾何線——本 O 只可以驗證/提議，正式攻堅要授權
⚠️ 質量層分析默認用 O234 freeze v1.1 質量集，唔准再 fit PDG 混標度絕對質量（O209 §十二準則）
⚠️ |dm| 用 NC=88 完整譜（O136 scripts/63 權威定義）；退化對 a+b=88 以 1/d→0 處理
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| freeze OLS α | 2.61697737 ± 0.151 | O209 scripts/16 P1 / docs/19 |
| φ² = 4cos²(π/5) | 2.61803399（−0.01σ） | O209 docs/19 P2 |
| 79/30 | 2.63333333（−0.11σ，退次選） | O209 docs/19 P2 |
| 固定 φ² freeze RMS | 0.580174（79/30: 0.580655） | O209 docs/19 P2 |
| 標度 C = m/\|dm\|^{φ²} | ≈ 1.47e−6 MeV（≠ M₀ = 27.900915） | O209 docs/19 P4 |
| C_f ∝ \|dm\|^{φ²}/γ slope | 0.374（需 1）FAIL | O209 docs/19 P3 |
| c/s resid（φ² 固定） | c +0.80、s +1.18 | O209 docs/19 |

## 五、交接 / 依賴

```
- 前置: O209（docs/19 逆推攻堅 — 本 O 起點）; O136（docs/25/29 質量=代價先例; 留意 O136 未閉合嘅「C≠M₀」+「Dyson 自洽」next-step）
- 移交出: 無（未開始）
- 範圍警告:
  · 唔好喺本 O 重複 O233 已 5 線負嘅 C_f 算子掃描方向（除非新幾何量）
  · κ 張量非對角屬 O53/O59 幾何線 — 本 O 只記錄候選，正式攻堅要授權
  · freeze 質量集版本由 O234 管 — 本 O 用 v1.1，v2 出咗要核對
  · 唔推 O209（O209 🟡 已定格，新工作屬 O238）— 唔好喺 O209 目錄寫嘢
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。