# O256 SESSION_START — C_ℓ 連續譜包絡 (lensed Silk 複合形式) — 由 K_Chain/K_Tree 推出, 閉合 O202 R6

<!-- registry
pid:     O256
title:   C_ℓ 連續譜包絡 (lensed Silk 複合形式) — 由 K_Chain/K_Tree 推出, 閉合 O202 R6
state:   partial
verdict: partial
flags:   -
owner:   O256
created: 2026-10-21
updated: 2026-10-21
prereq:  O202; O180; O48; O214
source:  P3/high-l-tail-transfer 第二輪攻堅流向 + O202 R6 delivery C; 2026-10-21 開題只註冊禁推
-->

> ⚠️ **機器塊 live field (2026-10-23)**: registry block 已同步 register `state=partial, verdict=partial`（階段性 closeout 2026-10-21；本文 §〇 為開題快照，正文保留原文不改）。

> **Session**: 2026-10-21（新建立）
> **狀態**: 📄 **已註冊 — 未開始（只註冊，禁推）**
> **來源**: P3/high-l-tail-transfer 第二輪攻堅流向 + O202 R6 delivery C
> **前置**: O202; O180; O48; O214
> **位置**: `open_problems_fresh/o256_cl_continuum_envelope/`

---

## 〇、開題閘（調律者 2026-10-21）

- 原話: 「先開新O, 標準規範, 但是現在不直接推」
- **執行狀態**: 已開題 (scaffold + record + SESSION_START + README row)；
  **scripts/docs/data 零建立**；register `state=registered`。
- **解閘條件**: 調律者明示開始推（舊「繼續？」都要先確認閘先開）。

## 一、接手起點

未開始。本 session 只完成開題架構 + 將 P3 兩輪攻堅嘅完整結論載入 problem record §二/§三/§四。

**承接 session 唔可以由「掃 λ」開始** — P3 R1-R12 已掃盡全部結構候選
（297/306/484/505/527/533/537/1411/9055），結論全部喺 record §二 排除表。

## 二、承接第一件事（解閘後）

```
1. 讀 P3 main_problems/p3_cmb_cl/docs/09_highl_tail_transfer.md 全文（兩輪攻堅主記錄）
2. 讀 record §五 三條攻擊路線，揀一條開始（唔准由新 λ 掃描開始）
3. 開題時明示: 呢個 O 唯一許可方向 = K_Chain/K_Tree 結構機制,
   唔係再 fit 一個數值
```

## 三、已知陷阱

```
⚠️ 陷阱1: 306 vs 316 不可分 (Δχ²<3) — 峰間隙 306 已判 = lensed ΛCDM 巧合,
   唔可以再當 IDCM 結構候選閉合 (P3 R12 判決)
⚠️ 陷阱2: Planck txt 第二列係 C_ℓ 唔係 D_ℓ — 任何新 script 必乘 ℓ(ℓ+1)/2π
   (P3 R1 實錄; O241 06 script 有乘, O48 15 script 冇乘但用 ratio 冇影響)
⚠️ 陷阱3: O214 CAMB 前向承托唔可以當「IDCM 連續形式」 — 本 O 目標正正係
   填補 O202 R6 缺口, 引用 O214 做承托 = 循環
⚠️ 陷阱4: CAMB smooth 譜 log-polyfit RMS 不可靠 (P3 R6 實錄) — 用 local
   derivative (R7 λ_loc) 先有意義
⚠️ 陷阱5: sacc cov 127×127 = TT45 + TE40 + EE42 — ACT DR6 TT block = cov[:45,:45]
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 高ℓ尾起始 | ℓ>1409 (m=7=1409 之後) | O48 docs/02 |
| 峰間隙序列 | 306/288 交替 (221→527→815→1121→1409) | O48, 離散層面 |
| 分段 λ₁ (1418-1700) | 307±9 (SPT) / 308±5 (ACT) | P3 R11 |
| 分段 λ₂ (1700-2000) | ≈410 (SPT/ACT) | P3 R10 |
| 分段 λ₄ (2400-3000) | ≈646 (lensing floor) | P3 R10 |
| 共同範圍 λ (1418-2195) | SPT 526 / ACT 512 / Planck 490 | P3 R10 |
| 峰高殘差阻尼尺度 (層級1) | ℓ_D = 9055 (只可層級1) | O48/O241 |
| G_n(0) | 1/(4sin(nπ/88)) | O83 (Q1 起點) |

## 五、交接 / 依賴

```
- 前置: O202 (R6 缺口定義) / O180 (投影核, Q3 候選) / O48 (峰結構+峰形) / O214 (前向承托, 測試底線)
- 移交出: 承接 session 開始推時 register progress → partial
- 範圍警告: 唔做 O214 前向重推 (CAMB 層); 唔重推 O48 峰形 (閉合);
  唔重掃 λ 數值 (P3 已掃盡); 唔做 O241 層級1 (9055 專用)
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。