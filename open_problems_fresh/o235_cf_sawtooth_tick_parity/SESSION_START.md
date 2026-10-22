# O235 SESSION_START — C_f 鋸齒 Z₂ 嘅 tick-宇稱/時間處理假説 (88-chain checkerboard/staggered 對偶)

<!-- registry
pid:     O235
title:   C_f 鋸齒 Z₂ 嘅 tick-宇稱/時間處理假説 (88-chain checkerboard/staggered 對偶)
state:   partial
verdict: partial
flags:   -
owner:   O235
created: 2026-10-07
updated: 2026-10-07
prereq:  O233（鋸齒閉合）
source:  O233 鋸齒閉合 (輕子/夸克分離) + 2026-10-07 調律者: ODD/EVEN 自然需要時間處理 → T1 就地診斷 (O234 scripts/06)
-->

> **Session**: 2026-10-07（新建立）
> **狀態**: 📄 **已註冊 — 未開始**（T2–T4 留待下一 session）
> **來源**: O233（鋸齒閉合）→ 調律者 2026-10-07「既然涉及ODD和EVEN就自然需要時間處理」
> **前置**: O233
> **位置**: `open_problems_fresh/o235_cf_sawtooth_tick_parity/`

---

## 一、接手起點（T1 已完成，本 session 只開 O，唔攻堅）

- **scripts/01_tick_parity_T1.py**（由 O234 scripts/06 遷入；O234 記錄冇 06 引用——乾淨）
- T1 全部分數閉式（詳見 01_problem_record §二）：
  - 二部圖 ±配對 1.44e−15 ✅
  - staggered 4−γ 對偶 87/87（8.9e−16）✅
  - s1 ↔ s3 元素級雙射；Σs1+Σs3 = 88 = 22×4（transcendental 對消）✅
  - μ²=2 純奇-site 模（checkerboard 邊界模）✅
  - tick 尺度 hint（88=2N_d; tick 譜 ±μ²; half-tick ∝ λ_sync 尺度）＝ 未閉合

## 二、下一 session 起點（T2 → T3 → T4）

```txt
1. T2: 88 環 tick 算子時間演化 ↔ τ / T_ring / λ_sync 閉合（掛鉤 ω_ring 嘅結構理由）
2. T3: tick 相位推導輕子槽 ≡1（第二條獨立證據，唔重複 T3×O210）
3. T4: C_f 兩步映射不動點——武斷判死（冇不動點 → 假説死）
4. 全部過四道硬測試先閉合
```

## 三、時間幀 / 參數（T2 用）

```txt
T_ring    = 84.637 Gyr      (環週期, O121)
τ         = R_world/c       (環幀)
t_true    = 11100.9 Gyr     (O213: 箭頭 = 投影冪等, 非 T_ring)
λ_sync    = πR_world/44     (O132, 結構 z-不變)
88        = 2N_d            (每週期 half-tick 數)
γ_44      = 2 = μ²          (4−γ 對偶不動點; B = 2μ², O229 自對點 n=22)
sec(π/88) = 1.000637580593  (s1/s3 transcendental ±)
```

## 四、修正紀錄（2026-10-07，T1 開發期）

- scripts/01 [C] 段初次印 `max|λ_A(m)+λ_A(88−m)| = 3.99`——配錯 index；二部图 ±配對正確
  係 **m ↔ m+44**（cos 偶函數, 88−m 唔係反號拍檔）。已修正（1.44e−15）。呢個係檢驗方法
  層教訓：bipartite ±配對喺環上要按半週期平移配（m ↔ m+N/2），唔好靠直覺。

## 五、已知陷阱

```txt
⚠️ 88 環「even/odd」有三種：mode-index 奇偶（k 奇偶）、site 宇稱（站波權重）、
   mass-rank 奇偶（鋸齒）——唔好混埋（O233 docs/12 assignment 隔離先例）
⚠️ sympy summation 對 AP sin² 會錯（O148 S5）——呢類和用手推閉式 + 數值確認
⚠️ 「世界=even mode」係標籤性質（T1 [C2] 普通模 site 權重平 22/22）；要講
   動力學角色必須 T2-T4 證明
```

## 六、交接 / 依賴

```txt
- 前置: O233（鋸齒 Z₂ 已閉合; 本 O 唔重證）
- 產出依賴: O234 凍結層 freeze v2（若用質量數字）
- 移交出: 無（T2-T4 全部本 O 內完成）
- 範圍警告: 唔做 C_f 生成器 hunt（O233 負閉合）; 唔做 A₅ 幾何硬砌（O136/O137）
```

> ⚠️ **本檔係接手點快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。