# O235 docs/01 — T1 重新建立 + 接手接收（2026-10-07）

> O235 開 O 時只承接 scripts（O234 scripts/06 → O235 scripts/01）；本 doc 將 T1 正式建立為
> O235 自有產物：接手接收記錄 + 重跑複現證據 + 閉式總結。T1 本身無 PASS 語義（診斷性），
> 所有數值以重跑 log 為準。

## 〇、接手接收（cross-O intake）

| 來源 | 內容 | 性質 | 處置 |
|:-----|:-----|:-----|:-----|
| O233 (handoff 2026-10-07T00:59:26) | 鋸齒 Z₂ 時性攻堅 → O235 tick-宇稱假説；T1 診斷已完成 | 新開放問題（即本 O 本身） | 承接；T1 重新建立後進入 T2 |
| 跨 O 掃描 `grep -rln "O235" --include="*.md"` | 僅 `open_problems_fresh/README.md`（本 O 自己 row） | — | 無其他 O 提及需分流 |
| register 基線 `check` (2026-10-07) | HARD DRIFT 總數 = 1（既有基線）；O235 出現次數 = 0 | — | 基線記錄，本 O 未引入漂移 |

前置狀態：O233 = `partial`（5 正 + 1 負，10-06 審計還原後最終狀態）；O235 = `registered`。

## 一、重跑複現證據

- 命令：`PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 o235_cf_sawtooth_tick_parity/scripts/01_tick_parity_T1.py`
- Log：`logs/01_tick_parity_T1.out`（2026-10-07 本 session 重跑）
- 結果：exit 0；全部宣告數字複現如下。

| Check | 宣告值（SESSION_START/01 記錄） | 重跑值 | 狀態 |
|:------|:------|:------|:----:|
| 44-site Σ（canon） | 90 | 90.000000000000 | ✅ |
| dual even Σ（世界） | 90 | 90.000000000000 | ✅ |
| dual odd Σ（觀察者） | 88 | 88.000000000000 | ✅ |
| staggered 4−γ 對數 | 87/87 | 87/87 | ✅ |
| 元素級 max err | 8.9e−16 | 8.88e−16 | ✅ |
| s1 ↔ s3 元素級雙射 | True | True（88−s1 == s3） | ✅ |
| Σs1 + Σs3 | 88 = 22×4 | 88.000000000000 | ✅ |
| bipartite ±配對 m↔m+44 | 1.44e−15 | 1.44e−15 | ✅ |
| μ² = γ₄₄ = 2 站波（m=22） | W_even=0, W_odd=44 | W_even=0.0, W_odd=44.0, Δ=−44 | ✅ |
| tick 譜（hint） | ±[−1.999, +1.999] | ±1.998726 | ✅ (hint 層) |

## 二、閉式總結（T1 確立嘅結構事實）

```txt
🟢 88 環 = 偶長環 = 二部圖: L=2I−A 特徵值 4sin²(πm/88); adjacency A 特徵值 2cos(2πm/88)
   ±配對係 m ↔ m+44（半週期平移），**唔係** 88−m（cos 偶函數, 88−m 同號）
🟢 staggered 對偶 4−γ: γ_k + γ_{88−k} = 4 對 k=1..87（87 對, 8.88e−16）; k=88 γ=4 自對
🟢 s1 (k≡1 mod 4, 全輕子槽) ↔ s3 (k≡3, 重夸克槽): 元素級 88−s1 == s3
   Σs1 = 44 − sec(π/88) = 42.999362419407（虧, 唯一非整數殘差, 負方向）
   Σs3 = 44 + sec(π/88) = 45.000637580593（盈）
   Σs1+Σs3 = 88 = 22×4: sec(π/88) 逐對對消（transcendental 零貢獻）
🟢 μ² = 2 = γ₄₄ = 4−γ 對偶不動點: 對應站波 u₂₂(n) = sin(πn/2) = 純奇-site 模
   (W_even = 0, W_odd = 44): checkerboard 邊界模企喺時間半格上面 (O229 自對點 n=22)
🟡 tick 算子 H_cb = P_even·L·P_odd + P_odd·L·P_even: 譜 hint ±2cos((2m+1)π/88)
   ≈ ±μ² 尺度（1.9987）；「88=2N_d half-tick/週期」嘅物理地位 = T2 唔閉合嘅 hint
```

## 三、已知陷阱（SESSION_START 四 + O-series 慣例）

```txt
⚠️ bipartite ±配對喺環上要按半週期平移配（m ↔ m+N/2），唔好靠直覺（T1 開發期修正,
   初次錯配成 88−m 出 max 3.99）
⚠️ 88 環「even/odd」有三種: mode-index 奇偶 / site 宇稱（站波權重）/ mass-rank 奇偶
   （鋸齒）——唔好混埋（O233 docs/12 assignment 隔離先例）
⚠️ sympy summation 對 AP sin² 會錯（O148 S5）——呢類和用手推閉式 + 數值確認
⚠️ 「世界=even mode」係標籤性質（普通模 site 權重平 22/22）; 要講動力學角色必須
   T2-T4 證明 —— 本 O 唔准把 assignment 輸入當推導
```

## 四、T1 限制（🔴 未閉合，T2 開場）

```txt
🔴 tick 算子嘅**真譜**（H_cb 對角化）未驗證: T1 [D] 只印公式 2cos((2m+1)π/88)
   做 hint, 冇實際構建算子 → T2 第一項 = 構建 H_cb + 精確譜 + 躍遷週期
🔴 tick 週期 ↔ T_ring / τ / λ_sync 嘅結構關係未閉合（88 = 2N_d half-tick 嘅地位）
🔴 輕子槽 ≡1 (mod 4) 由 tick 相位推導（T3）未做
🔴 C_f 兩步映射不動點判死（T4）未做
```

## 五、來源 / 產物

```txt
- scripts/01_tick_parity_T1.py（由 O234 scripts/06 遷入, O234 記錄零引用——乾淨）
- logs/01_tick_parity_T1.out（本 doc 重跑 log）
- 前置: O233 final_result.md（鋸齒閉合 partial）+ docs/14（even/odd 兩流 = 輕子/夸克分離）
- 時間幀參照: O132（λ_sync = πR_world/44, 結構 z-不變）, O121/O213（T_ring, τ, t_true）