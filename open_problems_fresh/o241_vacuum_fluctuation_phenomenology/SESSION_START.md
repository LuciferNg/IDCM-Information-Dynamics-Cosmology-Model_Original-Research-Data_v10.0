# O241 SESSION_START — 量子漲落實證現象之 IDCM 推導: Casimir/零點譜差 + 量子-經典動力學

<!-- registry
pid:     O241
title:   量子漲落實證現象之 IDCM 推導: Casimir/零點譜差 + 量子-經典動力學
state:   partial
verdict: partial
flags:   -
owner:   O241
created: 2026-10-07
updated: 2026-10-08
prereq:  O36, O38, O41, O84, O86, O121, O138, O204, O213
source:  2026-10-07 調律者提問:「量子漲落純數學自洽定巨觀實測」; 實證盤點 Lamoreaux 1997/Mohideen-Roy 1998/DCE 2011
-->

> **Session**: 2026-10-07（新建立）
> **狀態**: 🟡 **部分閉合 — 主體完成 (Q1–Q5 + R1–R14, 2026-10-08)**
> **來源**: 調律者提問「量子漲落到底是純數學上自洽還是已經在巨觀下有測量結果 — 例如兩片近距離金屬片之間的吸引力」(2026-10-07)
> **前置**: O36, O38, O41, O84, O86, O121, O138, O204, O213 (+ cmb_cl theme)
> **位置**: `open_problems_fresh/o241_vacuum_fluctuation_phenomenology/`

---

## 一、接手起點

未開始。調律者指示 (2026-10-07): 「開新o後禁止開始推，我有其他問題要問」— 本 O 只註冊, 未有任何推導/script。可觀測性/本體論層見 O242; 真空能攻堅見 O240。

## 二、先做嘅第一步

```
1. 讀 o204_wfield_constitution/docs/08_cross_version_audit.md §7.6 (v9 QFT 審計) — 決定 Q1 決策位起點
2. 讀 skill structural-forcing-protocol (DTO 立場) + o138 docs/03 §6.5 (退相干殘餘)
3. 讀 o121 docs/13–17 (τ_rec G8 現狀: 修正 τ_ref 後 ×101, 下界太鬆)
4. 文獻核實: Lamoreaux PRL 78,5 (1997) / Mohideen-Roy PRL 81,4549 (1998) / Wilson Nature 479,376 (2011)
```

## 三、已知陷阱

```
⚠️ v9 量子漲落數字 (√⟨Δφ²⟩=0.540–0.652, E₀=½Σħω_k, bounce 2×10⁸ Gyr) 唔可以引用為 v10 預言 — O204 docs/08 §7.6 裁定唔相容 (對數勢 vs Mexican-hat)
⚠️ v7 φ⁻⁴「Casimir 反饋」= 邊界項命名類比, 唔係力學推導 — 引用時要講清楚
⚠️ 退相干動力學屬 O138 §6.5 🔴 — 本 O 承接要做 register 記錄, 唔可以當獨立新發現
⚠️ Casimir 目標公式 π²ħc/(240d⁴) 係理想導體; 真實金屬要有限電導修正 (Lifshitz 用度到嘅光學性質)
⚠️ 單位混用會殺閉合 script (O39 前科) — 用明確換算常數, 先對已知目標校準再跑
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| F/A (Casimir @1 μm) | 1.30e-3 Pa ≈ 130 nN/cm² | π²ħc/(240d⁴), 理想導體 |
| Lamoreaux 1997 | 0.6–6 μm, 5% 內 | PRL 78, 5–8 |
| Mohideen-Roy 1998 | 0.1–0.9 μm, ~1% | PRL 81, 4549–4552 |
| DCE | 真光子對 + two-mode squeezing | Wilson et al. Nature 479, 376 (2011) |
| Lamb shift | ~1057.8 MHz | 標準 QED |
| F_proj (量子-經典邊界) | 17 = L₆−1 = N_d−n* | O138/O121 |

## 五、交接 / 依賴

```
- 前置: O204 (本體論/審計), O138 (邊界+Born), O121 (τ_rec), O36 (測量), cmb_cl (C_ℓ)
- 移交出: Q3 結果 → O138; Q5 結果 → O121 (G8); 讀法判準 → O242
- 範圍警告: CMB C_ℓ 譜形閉合屬 cmb_cl; 冷斑屬 O7/O182; 唔重推
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。