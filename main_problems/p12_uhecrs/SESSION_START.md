# P12 SESSION_START — UHECR 超高能宇宙射線（晶體應力釋放詳情）

<!-- registry
pid:     uhecrs
title:   UHECR 超高能宇宙射線（晶體應力釋放詳情）
state:   open
verdict: -
flags:   -
owner:   uhecrs
created: 2026-10-05
updated: 2026-10-18
prereq:  O7, O110, O121, O173
source:  遷移自 open_problems_fresh/crystal_stress/uhecrs（2026-09-27 分拆；register 2026-10-05）
-->

> **Session**: 2026-10-18（結構重整 session——非研究攻堅）
> **狀態**: 🔴 開放（register 權威；主體閉合屬 P5）
> **來源**: P5 crystal_stress SESSION_START（2026-10-17）交接建議 → 本 session
> **前置**: O7, O110, O121, O173
> **位置**: `main_problems/p12_uhecrs/`

---

## 一、接手起點

P12 = UHECR 詳情目錄（2026-09-27 由 P5 分拆）。之前未入 git（untracked），結構唔合慣例（得 records/，冇 root 四檔）。
本 session（2026-10-18）已完成：records/→docs/、root 建 README / 01_problem_record / SESSION_START / final_result、
register 同步（O7/O110/O121/O173 交接 + P12_REF_FIX 翻譯層）、git 提交。研究內容本身未開工。

P5 交接建議（2026-10-17, docs/08）：**CluMPR 3.0° p 改 Gaussian 估計 + 更密 inner grid** 係「確認性」工作，
已 clamp 保守報導，唔影響 4.69σ 結論——屬可選，非緊急。

## 二、先做嘅第一步

```
1. 已讀 docs/03_uhecrs_record.md（主記錄）+ docs/05_psz1_vacuum_result.md（真空 3.43σ）——結論齊
2. 若開研究攻堅：先讀 P5 docs/08_routes_2_3_execution.md + scripts/17-19（路線 2+3 執行記錄），
   再做 CluMPR 3.0° Gaussian p 重估（scripts/17 同款管線）
3. register 狀態以 problem_register 為準；docs 改動後跑 idcm_problem_find reindex
```

## 三、已知陷阱

```
⚠️ 結構已變（2026-10-18）：records/ 已搬去 docs/；舊 ref 指向 records/ 由 P12_REF_FIX 翻譯層承接，
   唔好再開 records/（會製造新 REF-MISSING）
⚠️ data/ 同 stdout 一致性：任何重跑後 json 數字對唔上要修正（唔准留矛盾）
⚠️ 跨 O 引用數字核歸一化：本目錄結論（2.18% / 1.08% / 3.43σ / 3.99σ / 4.69σ）以 P5 docs/08 為最新權威
⚠️ 時序潔癖：新發現只可 append，唔准改 docs/03/05 舊結論
⚠️ 全譜缺口屬 O110，唔好喺 P12 內扮閉合低能段
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| λ_min（晶格承載極限） | L_P·φ⁴⁴ = 2.535×10⁻²⁶ m | docs/03 §2.1 |
| E_GZK = hc/λ_min | 4.891×10¹⁹ eV（GZK 偏差 2.18%） | docs/03 §2.2 |
| E_max = 4φ·E_GZK | 3.166×10²⁰ eV（OMG 上限 1.08%） | docs/03 §2.3 |
| 證偽線 | >316.6 EeV 確認事件 → IDCM 錯 | docs/03 §3 |
| Auger 各向異性（109 events） | Fisher 2.66σ / 能量加權 3.99σ | docs/03 §4.3 |
| 節點核心真空（4 目錄） | Fisher4 p=0.0003 = 3.43σ | docs/05 |
| DESI 第 5 重（P5, 10-17） | Fisher5 = 4.69σ；2.0° z=7.72σ | P5 docs/08 |
| 盲測功效 | N_for_5σ = 53（雙比例） | P5 docs/08 |
| A₅ 節點 | 60 個（±8°）｜阻挫邊：32 條（±5°） | docs/03 §4.1 |

## 五、交接 / 依賴

```
- 前置: O7（阻挫邊重聯機制）→ O173（應變能池）→ O121（返池 f_UHECR=0.8028）→ O110（全譜缺口）
- 移交出: P5（主體閉合 45/45 + 路線 1/4 預註冊）；P14（相位滑移 = 寫入端）
- 範圍警告: LRD → P11；低能段全譜 → O110；偏振 mask 技術規格 → P5（10-17 已凍結）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 register 為準；生命週期事件以 `problem_register/` 為準。