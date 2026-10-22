# O159 docs/06 — O161 開項分析 (scoping audit)

> **日期**: 2026-09-08 · **對象**: Gemini 建議開 O161 (Observer-Mass Gauge Action & Discrete EL)
> **判決**: **應該開, 但 scope 要砍 3 樣、修正 1 個類別錯誤、收窄到 2 個真新目標**

## 一、前置狀態 (無衝突)

- O157 P1 (懲罰泛函, mixing-angle) 🟢 閉合 54/54 — O161 嘅 matter action 唔重疊
- O159 (Dirichlet 場論) 🟢 閉合 92/92 — O161 係佢嘅動態層延續
- 順序: 可以開; 建議問題記錄以描述性命名 (離散作用量 + Noether + 鏈結構),
  「觀察者-質量規範場」留詮釋層並列 (observer 係 🟡 本體論命名)

## 二、✖ 砍 (Gemini roadmap 嘅三項)

1. **F² plaquette 項** — 88-site 鏈係 **1D, 冇 plaquette** → 幾何曲率 F_kk' 恆零/未定義。
   Gauge curvature 需要 2D 閉環 (K_chain⊗K_tree board / CY₃), 唔係 88 鏈嘅嘢。
   「唔可以滑向連續場論」嘅反面教訓: 亦唔可以偷 2D 結構入 1D 鏈。
2. **L_int = g_obs·Φ_world†·J·Φ_obs** — 三重問題:
   (a) g_obs 係新自由參數 — Gemini 自己話「拒絕人為貼上耦合常數 g」然後自己貼 g_obs,
   自相矛盾; (b) 將「觀察者介入」寫成 interaction term = post-hoc labeling
   (用戶鐵律: 拒絕貼標籤當結構推導); (c) 混合扇區會**破壞 O159 已閉合嘅
   U(1)/E−O/pair 結構** — 變咗新理論, 唔係延續。
3. **Dynamical gauge links U_ij = e^{iA_ij}** — 88 個新變數, 冇導出佢哋嘅作用量。
   零參數鐵律: A_ij 必須由框架內結構導出 (候選: beat phases / connection A_k 嘅
   link-space 版), 唔可以 postulate。1D 鏈唯一 gauge-invariant = Wilson line
   (總相位) — 動態規範場喺 1D 係 pure gauge。

## 三、⚠️ 修正 (類別錯誤)

4. **「μ² = 2 從極值條件自然解出」係類別錯誤** — 變分原理決定**場構型**,
   唔決定**質量參數**; 質量係 action 嘅參數, 唔係變分輸出。
   O159 已由譜身份 (E−O, γ₄₄, BC-trace 三路) 定 μ² = 2; 變分原理只係再產出
   EOM (Δ+μ²)Φ = 0 + propagator — **已做** (T2 B3/B4)。
   誠實嘅「mass from variation」版本 = **約束乘子**: 將 sector-locking 寫成約束
   (Σ_even|Φ|² − Σ_odd|Φ|² = Δ), μ² 做 Lagrange multiplier:
   S' = S + λ·C → 扇區隙 2λ, 要求 2λ = E−O = 2 → λ = 1, μ² = 2λ = 2。
   乘子值仍由 E−O = 2 (譜身份) 定 — **形式統一, 唔係新物理**, 但係「變分導出」嘅
   誠實版本, 有形式價值。

## 四、✔ 真新目標 (O161 應收窄到呢度)

5. **★ 離散 Noether 電流**: J_jj' = Im(Φ†_j U_jj' Φ_j'), ΣJ = 0 (守恆),
   電荷 Q = 44 = N_d 作為守恆流嘅總通量 — 完備 field theorist 全鏈
   (Lagrangian → EOM → Noether → 守恆律 → 電荷), 餵 O122 (feynman_rules_wfield)。
6. **鏈變數結構 (導出, 唔好 postulate)**: 框架內已有 connection A_k = −μ²cos(2θ_k)
   (mode space, T5); link-space 版本 (相鄰節點相位差 / beat phases) 要由譜導出,
   驗證佢係咪就係 A_k 嘅 Fourier/離散導數。
7. **(形式) 約束乘子重構**: 上述 §3 嘅 mass-as-multiplier — 將 O159 譜身份重寫為
   變分語言 (統一性, 唔係新物理)。

## 五、陷阱 (開項時直接寫入 01_problem_record)

- 1D 鏈冇 plaquette → F² 項 void
- 零參數鐵律: g 必須由幾何拓撲量導出, 唔可以 postulate (g_obs 被否決)
- 變分唔出質量參數 — mass = 乘子 or 譜身份, 二揀一, 唔好混
- links 要導出 (beat/connection), 唔係新自由度
- 「觀察者」命名 = 詮釋層 🟡, 精確內容用算子語言
