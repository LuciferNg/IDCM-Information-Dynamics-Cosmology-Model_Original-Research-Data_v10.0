# O235 01_problem_record — C_f 鋸齒 Z₂ 嘅 tick-宇稱/時間處理假説 (88-chain checkerboard/staggered 對偶)

<!-- registry
pid:     O235
title:   C_f 鋸齒 Z₂ 嘅 tick-宇稱/時間處理假説 (88-chain checkerboard/staggered 對偶)
state:   registered
verdict: -
flags:   -
owner:   O235
created: 2026-10-07
updated: 2026-10-07
prereq:  O233（鋸齒閉合）
source:  O233 鋸齒閉合 (輕子/夸克分離) + 2026-10-07 調律者: ODD/EVEN 自然需要時間處理 → T1 就地診斷 (O234 scripts/06)
-->

> **狀態**: 📄 **已註冊 — 未開始**（2026-10-07 開 O；T2–T4 留待下一 session）
> **建立**: 2026-10-07
> **前置**: O233（鋸齒 Z₂ = 輕子/夸克分離，已閉合 partial）
> **位置**: `open_problems_fresh/o235_cf_sawtooth_tick_parity/`

---

## 一、問題陳述

**C_f 鋸齒嘅 Z₂（mass-rank 奇偶 = 輕子/夸克分離）有冇「時性」？**——即係咪 88 環
checkerboard/leapfrog 時間處理結構（二部圖偶/奇 sub-lattice 交替更新）喺 flavor 世界嘅投影。

假説（精確表述）：

> **鋸齒嘅 Z₂ 唔係空間宇稱，而係 tick 宇稱**：bipartite 88 環嘅時間演化必然以
> even/odd 兩半實現（leapfrog = U(2 steps) = 偶半步 × 奇半步）；C_f 流嘅 even/odd
> 交替 = 鏈 tick-parity 投射到質量 rank。輕子（≡1 mod 4 槽）= 觀察者半邊嘅 s1 扇區，
> 重夸克 c,b,t（≡3）= staggered 對偶拍檔 s3 扇區。

## 二、已確立嘅結構（T1 診斷, scripts/01, 全部精確閉式）

```
🟢 88 環係二部圖 (偶長環): adjacency ±配對 m<->m+44, max err 1.44e-15
   ⟹ checkerboard: 偶/奇 sublattice 可獨立交替更新 = leapfrog 定義結構
🟢 staggered 對偶 (4-γ 宇稱翻轉): k<->88-k, 87/87 對閉合 γ_k + γ_{88-k} = 4 (8.9e-16)
🟢 s1 (k≡1, 全輕子槽) <-> s3 (k≡3, 重夸克槽) 元素級雙射 (88-s1 == s3)
🟢 Σs1 + Σs3 = 88 = 22×4 精確: sec(π/88) transcendental 逐對對消
   (s1 = 44−sec = 42.99936 虧; s3 = 44+sec = 45.00064 盈)
🟢 μ² = 2 係 4-γ 對偶不動點 (γ_44=2, 88鏈自對點 n=22, O229), 其站波 =
   純奇-site 模 (W_even=0, W_odd=44) — checkerboard 邊界模企喺時間半格上面
🟢 tick 尺度 hint (非閉合): 88 = 2N_d half-tick/週期; tick 算子譜 ±[−1.999, +1.999]
   ≈ ±μ²; half-tick ∝ R_world/(44c) 同 λ_sync = πR_world/44 (O132) 同量級
🔴 T1 限制: 普通站波 site 權重平 (22/22) — 鋸齒 Z₂ 落喺 mode-label 翻轉 (k<->88-k),
   唔係波函數 site 集中; 「世界=even mode」係標籤性質, 未證明動力學角色
```

## 三、未確立（🔴 開放問題）

```txt
🔴 輕子 ⊆ s1 係 A_γ assignment 輸入（揀 {1,5,9}），唔係推導——「輕子企喺對偶負側」係
   assignment 尊重結構, 未係定理
🔴 T2 (未跑): tick 週期 <-> T_ring = 84.637 Gyr ／ τ = R_world/c 閉合
   (tick 算子譜 ±μ² 尺度點解同 ω_ring 掛鉤? 88 = 2N_d 半 tick 數嘅物理地位?)
🔴 T3 (未跑): 輕子槽 ≡1 (mod 4) 由 tick 相位推導——「點解 ≡1 唔係 ≡3」第二條獨立證據
   (T3×O210 之外)
🔴 T4 (未跑): C_f 兩步映射不動點判死——質量譜必須係 checkerboard 兩步映射嘅不動點;
   如果 two-step map 喺 C_f 空間冇不動點 → 假説死
```

## 四、攻擊路線（下一 session 起點）

```txt
1. T2: 構造 88 環 tick 算子 (H_cb = off-diag 塊) 嘅時間演化; 檢查其週期/特徵相位
   同 τ / T_ring / λ_sync 嘅結構關係 (O132/O213 時間幀參照)
2. T3: 4 步 checkerboard 循環相位 -> 4 個 residue 類; 查輕子 ≡1 是否 = tick 相位 1
   (B=4 = tick 週期步驟數?)
3. T4: 兩步映射喺 C_f 空間嘅不動點分析; 質量譜 = 靜態快照要求
4. 全部要過 4 道硬測試 (自由度/10⁷ null/樣本外/擾動); 禁把 assignment 輸入當推導
```

## 五、驗證標準

```txt
✅ T2: tick 週期由鏈結構推出並對上 τ / T_ring（零參數, 唔係後驗）
✅ T3: 輕子 ≡1 (mod 4) 由 tick 相位作為定理推出（零參數）
✅ T4: two-step map 不動點判決（有 = 支撐假説; 冇 = 假説死, 記錄負結果）
✅ 任何閉合宣稱過四道硬測試
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、禁區 / 交接紀律

```txt
⛔ O233 已閉合 (partial): 唔重推 C_f 生成器 hunt; 鋸齒本身唔重證
⛔ O136 純冪律障礙; O137 形狀屏障——唔好嘗試用 A₅ 幾何硬砌
⛔ 若用到質量數字: 必須凍結層 freeze v2 同 scheme 比 (O234 docs/03), 禁混標度
⚠️ 跨 O 交接只經 problem_register; 本 O 唔准寫 O233/O234/O209 任何檔案
   (T1 script 已由 O234 遷入本 O, O234 記錄唔含 scripts/06 引用——乾淨)
```

## 七、推導時序索引

> ⚠️ 只可 append 新行，禁回溯污染舊行。

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-07 | 開 O; T1 診斷承接自 O234 就地推 (scripts/06 → 本 O scripts/01) | scripts/01 |

## 八、相關文件

```txt
- O233 — C_f 結構身份（鋸齒閉合 partial; 生成器負閉合）
- O234 — 檢驗方法反推（T1 產地; 凍結層 freeze v2 規則）
- O132 / O213 — 時間幀（T_ring, τ, λ_sync）
- O229 — 88 鏈自對點 n=22 = B=2μ²
```