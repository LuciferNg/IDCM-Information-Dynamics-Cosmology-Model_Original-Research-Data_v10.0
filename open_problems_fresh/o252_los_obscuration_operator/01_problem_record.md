# O252 — 視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip)

<!-- registry
pid:     O252
title:   視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip)
state:   registered
verdict: -
flags:   -
owner:   O252
created: 2026-10-17
updated: 2026-10-17
prereq:  O180, O143, O179
source:  p11_little_red_dots records 25-30 (死因定案: 遮蔽層從缺)
-->

> **狀態**: 📄 **已註冊 — 未開始**（用戶指令：禁立即開始推）
> **建立**: 2026-10-17
> **前置**: O180（世界環投影核）、O143（𝒫 天球投影）、O179（hop 階梯/W 權重）
> **位置**: `open_problems_fresh/o252_los_obscuration_operator/`

---

## 一、問題陳述

**推導「視線遮蔽算子」τ(v)：觀測光譜 = 固有對稱模態對 × e^(−τ(v))，
τ(v) 由世界環幾何第一性原理推出（零新常數），禁看到目標凑 dip 位置。**

動機（P11 死因定案）：LRD 光譜 T1/T2/T3 判別全傾向唔支持對稱雙峰
（records 19-24），但死因分診（record 25）顯示真正缺口唔係數學、
唔係數據 — 而係 **「固有對稱 × 視線遮蔽」嘅遮蔽算子喺 IDCM 架構內
從缺**。Record 27 證明固有等權係代數必然（γ_k = γ_{176−k}）；record 28-30
三次排除已閉合結構（O180 位置層 / O143 天球 / O179 位置權重 / 𝒫∘W
複合）都唔可以充當遮蔽算子 ⟹ 需要**新建** τ(v) 結構。

## 二、已確立嘅結構

```
🟢 模態對運動學: v_k = c·cosθ_k, θ_{176−k} = π−θ_k, Δv = 2√(a₀r_k) EXACT
   (O180, script 21: 9/9)
🟢 固有等權: γ_k = γ_{176−k} 代數必然 (sin²恆等) — 等權唔係假設 (record 27)
🟢 散射保對稱: 對稱 kernel 卷積保對稱 (script 27, record 21) ⟹ 唔對稱
   必來自非散射 channel (吸收/遮蔽/幾何)
🟢 O179 hop 階梯: [1,4,8,11,12,11,8,4,1] Σ=60 對稱, ⟨hop⟩=4=B;
   W(i) 位置權重 (434/434 錨定) — 屬位置/質量層
🔴 遮蔽算子 τ(v): 光譜層視線光深 — 三次排除後確認架構內從缺
🔴 觀測 dip 結構: A Hα −283 km/s (depth 0.98), E Hα +47 (paper) —
   待新 τ(v) 盲測, 禁反推
```

## 三、未確立（🔴 開放問題）

```
🔴 τ(v) 嘅幾何來源: 世界環 π 方向有兩分支 (近/遠), 視線穿越光深點計?
   (候選: hop 層沿視線投影? cosθ 幾何因子? 但全部未推, 禁猜)
🔴 遮蔽與速度嘅耦合形式: τ := τ(v_k) 直接? 定 τ := τ(θ_k) 經投影?
🔴 點區分「遮蔽」vs「個別模態唔發射」(態選擇規則, record 25 後門)?
   — 兩者觀測上都係單峰/唔對稱, 需要獨立判別
🔴 零新常數約束下, τ(v) 嘅歸一化/絕對尺度由邊個已閉合量定?
   (候選: O179 W(i)? O180 Σγ? hop Σ=60? 未定)
```

## 四、攻擊路線

```
1. 世界環幾何第一性原理: 由 O180 r_k = 2πR cos²θ_k + hop 層結構
   推視線穿越層數 → τ(θ) 零參數形式 → 預言 dip → 盲測
2. 態選擇規則對照: 推「唔對稱 = 唔等權投影」嘅選擇規則 (O209/O144
   先例), 同遮蔽型 τ(v) 區分 (兩者觀測形狀不同: 遮蔽 dip 係吸收,
   選擇係發射缺失 — P-Cygni vs 單邊峰)
3. 樣本外盲測: 用推出嘅 τ(v) 預言 A/C/G/E dip 位置+深度 (禁反推),
   同 Nikopoulos+2026 absorber 參數對照
```

## 五、驗證標準

```
✅ τ(v) 零自由參數, 由已閉合譜量生成 (自由度成本 = 0)
✅ 盲測: 預言 dip 位置/深度, 同 A Hα −283 等 4+ 光源對照
   (MC null 10⁷, 5σ; 禁看到目標凑)
✅ 結構剛性: hop 微擾 / θ 微擾下 τ(v) 定性唔變
✅ 同外部 absorber 參數 (Nikopoulos+2026) 一致 (預言, 非 fit)
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-17 | 開題（用戶：開新 O 但禁立即開始推） | records 25-30 死因定案 → O252 |

## 七、相關文件

```
- p11_little_red_dots/records/25_death_cause.md — 死因分診: 應用層假設
- p11_little_red_dots/records/26_root_cause_equal_weight.md — script 21 全運動學
- p11_little_red_dots/records/27_line_of_sight_operator.md — 固有等權 + 遮蔽缺失
- p11_little_red_dots/records/28_truth_convergence.md — 三層投影, ③從缺
- p11_little_red_dots/records/29_o179_crosscheck.md — hop 階梯更正, W 係位置層
- p11_little_red_dots/records/30_pw_channel_exclusion.md — 𝒫∘W category error
- p11_little_red_dots/records/24_absorber_t1_final.md — 觀測 dip (盲測目標)
- O180/O143/O179 — 前置結構
```