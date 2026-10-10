# O48 — CMB 質數峰機制 (Prime Peak Mechanism)

> **狀態**: 🟡 主體已閉合 — Q1/Q2 系列 2026-10-09/10 完成; 谷距身份 k=[10,11,9,7] 仍開放
> **建立**: 2026-10-10 closeout 盤點補建（原 O48 目錄冇 SESSION_START.md）
> **來源**: O10 peak amplitudes 遺留 — 「點解峰喺質數位置 {1,2,3,5,7}?」

## 問題陳述

CMB 真峰 ℓ ∈ {221, 527, 815, 1121, 1409}（m ∈ {1,2,3,5,7} 質數位置）嘅質數性
點嚟？點解合數 m=4,6 被抑制？峰+谷一體 C_ℓ 模型（峰位/峰高/峰寬/谷深/谷位）可否
喺多實驗數據上閉合？

## 核心結論（Q1/Q2, 2026-10-09/10）

- **雙重篩選定理**: ℓ_m = 44(33−C(9−m,2)) + frac; 相位 s ∈ {±1,±21} =
  (Z/44Z)^× 對合元; N ∈ {L₅,L₆,F₅,F₅²,F₂⁵}
- **峰+谷閉合**: 峰位 44N+s / 峰高 3ε/F_j telescoping / 峰寬 γ=297/6=49.5
  (Lorentz, CAMB 前向 + PR4 co-add 雙重確認) / 谷深 ½=N_d/88 / 谷位 V¾
- **樣本外**: 四數據盲測全過 — PR3 純 TT +0.629 / PR4 NPIPE +0.425 /
  SPT-3G +0.475 / ACT DR4 +0.272; 谷 mod-9 ≡5 (8 點 p≈2.3e-8)
- **Register**: state=open（2026-09-12 註冊, 未 close）; 30 events

## 驗證水位（closeout 盤點 2026-10-10）

| 範圍 | 狀態 |
|:-----|:-----|
| scripts/01-11 (2026-08-31/10-09) | ✅ 有 logs/01-10 |
| scripts/12-65 (2026-10-09/10, 54 支) | ⏳ closeout 補 log 中（run_chain_closeout.sh） |
| docs/01-28 | ✅ 全入 record; docs/20+28 補 register note |
| final_result.md | ✅ 更新至 Q1/Q2 最終狀態 |
| register | 🟡 30 events; docs/20+28 補 note; 未 close |

## 檔案清單（closeout 盤點）

- `01_problem_record.md`（669+ 行, 推導時序索引至 Q1.48）
- `docs/01-28`（28 份 Q 系列 doc）+ 2 張疊圖（fig_q1_peak_valley_overlay.png 舊污染版,
  fig_q1_peak_valley_overlay_pureTT.png 純 TT 版）
- `scripts/01-65`（65 支, 含 46/46b/47/47b 版本對）+ data/ 空目錄
- `logs/01-10` + closeout 補 11-65

## 歷史

- 2026-08-31: O48 開項（源 O10）
- 2026-09-12: register registered state=open
- 2026-10-09: 調律者指示 reopen → Q1/Q2 推導 → 閉合至三層結構 + 峰+谷模型
- 2026-10-09/10: AUDIT（Plik-lite 三 block 污染）+ PR4 NPIPE 樣本外 + 峰形閉合
- 2026-10-10: closeout 盤點（本檔補建）