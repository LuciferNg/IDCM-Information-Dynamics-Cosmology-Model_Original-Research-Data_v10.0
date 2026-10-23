# O216 — Δn_color 色荷纏繞 (Color-Charge Winding)

## 狀態: 🟢 已閉合 (2026-10-08)

## 結論
色荷 **唔可以由鏈層導出**（結構 no-go：鏈長族 2^a·11^b 冇 3 因子 ⟹ 無 Z₃ 扇區；
密度基準 q_obs = 45.73%/17.09% 🔴；O137 R19 事前 6 候選全 fail）。
色數 3 = B−1 = N_gen 已由規範嵌入層導出（O68/O88 閉合引用：SU(4)_PS → SU(3)_C×U(1)_{B−L}，
4 = 3_{1/3} ⊕ 1_{−1}，12 = (3,3)⊕(1,3)）。Δn_color = [0,12,28] 繞數規則**不存在**；
色荷係規範嵌入層標籤（同角色 σ_g 一層，O209/O67），唔係鏈層譜量。

## 關鍵公式
- 色數: 3 = B−1 = N_gen = 4−1（O68: SU(4)→SU(3)_C×U(1), 恆等分解）
- 表示: 12 = (4,3) = (3,3)_{1/3} ⊕ (1,3)_{−1} = 9 夸克(3色×3代) + 3 輕子(3代)（O88）
- Counting identity: 18 = 6×3 = 2N_gen² = L₆（唔當證據）
- 鏈長族 ℳ = 2^a·11^b ⟹ 3 ∤ 88/44/176 ⟹ 無模-3 扇區（O229 R4）
- Δn_color = {0,12,28}（O54 配對 |夸克奇部−輕子奇部|：0,0,12,28）

## 依賴
O137 → O216 ← O209 → O67（σ_g）; O68/O88/O210（引用, closed）

## 驗證
- scripts/01 密度基準 9/9；02 三路線 17/17；03 no-go 屏障 11/11；04 獨立重驗 28/28（唔 import 原 script，analytic hypergeometric 對照）
- run_chain.sh --execute：65 checks 全過（9+17+11+28）
- register: O216 + O216/delta-n-color 均 closed；check 無 O216 硬漂移

## 密度基準
- N_search = 5（差值集）／5984（C(34,3)）／6（O137 事前候選）
- N_mc = 200000，seed = 216
- d_obs = 0.333（嚴格）／0.667（寬鬆）；d_med = 0.667／1.000
- q_obs = 45.73%（嚴格）／17.09%（寬鬆）→ 🔴 密度效應，無訊號

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `bbe96c00442a3693` | 2026-10-24 | closed | 色荷 唔可以由鏈層導出（結構 no-go：鏈長族 2^a·11^b 冇 3 因子 ⟹ 無 Z₃ 扇區； 密度基準 qobs = 45.73%/17.09% 🔴；O137 R19 事前 6 候選全 fail）。 色數 3 = B−1 = N… | open_problems_fresh/o216_delta_n_color/final_result.md | — |
<!-- conclusion-history:end -->
