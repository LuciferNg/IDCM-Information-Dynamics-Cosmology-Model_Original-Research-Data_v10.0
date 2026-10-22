# O236 SESSION_START — 質量來源推導路線（O235 續推）

<!-- registry
pid:     O236
title:   質量來源推導路線 (O235 續推)
state:   partial
verdict: partial
flags:   -
owner:   O236
created: 2026-10-07
updated: 2026-10-07
prereq:  O235（T1–T5 閉合資產）
source:  O235 T5 續推（2026-10-07 調律者: 開O236, 把路線放進去, 下一session處理）
-->

> **Session**: 2026-10-07（重開；同日早前開 O236 被調律者撤回「不開」→ 而家明確授權重開）
> **狀態**: 🔴 **開放 — 路線已列（docs/01, R1–R7），下一 session 處理**
> **來源**: O235 T5（s1↔s3 對偶槽／雙重篩／C_f 代際塊）→ 調律者「開O236, 把路線放進去, 下一session處理」
> **前置**: O235
> **位置**: `open_problems_fresh/o236_mass_origin_integration_n_c_f/`

---

## 一、接手起點

本 O 今 session 只做兩件事：**重開 O236**（retracted → reopened → open）＋**方法路線放進
`docs/01_mass_origin_routes.md`（R1–R7）**。所有可證偽內容、執行次序、驗證標準已預先註冊。
**下一 session 先執行 R1–R7**（建議次序: R1 → R2 → R3/R4 → R6 → R5; R7 只等數據）。

## 二、先做嘅第一步（下一 session 用）

```txt
1. 讀 docs/01_mass_origin_routes.md + O235 docs/05 (T5) → 確認 R1-R7 內容
2. R1: 輕子格定理形式化 → scripts/01 枚舉 (rank%2, n%4) 格 + 四道硬測試
3. R2: 對偶 partner 槽 → scripts/02 (88−k 元素級雙射; 已係 T1 資產延伸)
```

## 三、已知陷阱

```txt
⚠️ C_f 值 hunt 已三面負 + P1 循環證明 —— R 系列唔准再開 C_f 數值配對 (O208)
⚠️ γ 雙定義: 44-site (C_f 層) vs 88-site dual (相位類和層) —— 唔好混 (O235 T5 已標)
⚠️ s1↔s3 對偶 / 手性橋: 警惕同構重述 (O210 common-measure no-go 陰影)
⚠️ 塊間比 9.559/5.580: 目前觀察級, 冇 MC 唔准升格 (T5 E2 承諾)
⚠️ 質量數字 scheme: 任何 C_f 池匹配必須 freeze v2 同 scheme 比 (O234 docs/03)
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 相位類和 | Σs0=46, Σs1=44−sec, Σs2=44, Σs3=44+sec | O235 T3 |
| 輕子槽 | {e,μ,τ} → modes {1,5,9} ⊆ s1; t → 13 (VEV) | O233/O235 |
| 重夸克槽 | {d,c,b} → modes {3,7,11} ⊆ s3 | O235 T5 |
| (rank%2, n%4) 格 | {(1,1):4, (0,3):2, (1,3):1, (0,0):1, (0,2):1} | O236 docs/01 預算 |
| C_f 代際塊 | 3.685 / 35.226 / 196.581 (幾何中位) | O235 T5 |
| P2 純 γ u/d | γ3/γ2 = 2.245223121（真值; 手抄 2.245204 已被 O234 F1 標記）; 雙尺 z=0.853/0.506σ | O234 docs/04＋docs/05 |

## 五、交接 / 依賴

```txt
- 前置: O235 (T1–T5; 本 O 唯一直接上游; 全數數值資產已喺 docs/01 引用)
- 移交出: R7 數據等待 → O234 (P2/P3/P4 觸發條件已註冊); 發現新質量 → O233/O209 層
- 範圍警告: 唔做 C_f 數值生成 hunt (已負閉合); 唔做新質量預測 (需對撞機);
           唔重推 O210 common-measure no-go
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。