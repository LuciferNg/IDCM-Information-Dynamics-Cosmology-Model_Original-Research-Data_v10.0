# O255 SESSION_START — c 結構上限 → no-signaling: 色散結構必然 v≤c, 非時空公設

<!-- registry
pid:     O255
title:   c 結構上限 → no-signaling: 色散結構必然 v≤c, 非時空公設 (O254 scripts/03 概念結論)
state:   partial
verdict: partial
flags:   -
owner:   O255
created: 2026-10-20
updated: 2026-10-20
prereq:  O73（c 第一性原理）, O254（scripts/03 + 否證）
source:  O254 概念答覆 → 立項（用戶指示: 只開不推）
-->

> **Session**: 2026-10-20（新建立）
> **狀態**: 🟡 **部分閉合 — Round 1: c 結構上限定理 3538/3538 PASS（只開不推 已解除, 2026-10-20 用戶指示開推）**
> **來源**: O254 概念答覆（scripts/03 c 結構上限驗證 3/3 PASS）→ 立項
> **前置**: O73（光 = W-field Goldstone 相位模, c_W = R_world·ω_ring）、O254（拓撲同步否證）
> **位置**: `open_problems_fresh/o255_c_structural_no_signaling/`

## 起手材料（已立項, 未推導）

- **O254 scripts/03** `c_upper_bound_dispersion.py`: K_Chain v_g(n)=cos(πn/88) ≤ 1 = c; Goldstone n=0 唯一達 c（3/3 PASS）
- **O254 docs/01-03**: 能量圍堵 / 文獻審 / 拓撲同步否證（本 O 嘅語境: 宏觀「共享陳數超 c 同步」靠唔住 → 但底層係咪有 c 上限定理?）
- **O73 §10**: c = W-field Goldstone 相位模 → 零色散 → 唯一達光速; 有質量模 v < c

## 核心問題（推導時才開始）
- 資訊交換上限 v ≤ c 喺 IDCM 係**結構定理**定「巧合」？
- 即時關聯（Goldstone 全域相干, EPR/Bell 型）與資訊（需有色散載體）嘅嚴格界
- no-communication theorem 嘅 IDCM 結構版

## 禁區
- ~~用戶指示「開新獨立 o, 但不立即推」~~ **已解除 (2026-10-20 用戶指示「先按資料夾標準規格修正後開始推」)**
- 本 O 已開始攻堅 (Round 1 2026-10-20) — 禁區更新: 唔好「證明 SR」, 係「證明 IDCM 結構重現 c 上限」; 唔好引用外部模型當證據

---

## Session 1 (2026-10-20, Round 1 — c 上限結構定理)

**資料夾標準化**: 補建 `docs/ scripts/ data/ logs/`（原只得兩個 md, 2026-10-16 起標準規格）。

**結果**: 🟢 3538/3538 PASS（三支 scripts）
- `scripts/01_speed_mass_circle.py` (231/231): **速度-質量圓定理** — v_g(n)=cos(πn/88), v_g²+γ/4=1 EXACT, v_g≤1=c 唯一 n=0 (Goldstone), v_g(44)=0 (Nyquist), 色散曲率零 ⟺ Goldstone
- `scripts/02_generality_beats.py` (3205/3205): **N 普適性** — γ=4sin²(πn/N) ⟹ v_g≤1 for N∈{44,88,176,352}; 半整數 shift 唔改變速度界; O149 beat 定理 946/946 EXACT; 扇區和 Σγ_odd=88/Σγ_even=90 (176 半集) 重現
- `scripts/03_no_communication.py` (102/102): **no-comm 結構定理** — 零模=全域相干 (uniform), 信息載體必屬 n>0 ⟹ v_g<c 嚴格; τ_n(L)≥L/c 等號唯一 n=0 但 n=0 冇局部分辨能力; 即時關聯模態 {0} ∩ 信息載體 {1..44} = ∅

docs: `docs/01_structural_c_bound.md` (c 結構上限定理) + `docs/02_no_communication_structure.md` (no-comm 結構版)

**判據修正紀錄**（判據譜慣例 bug, 非結構失敗）:
- U2: k=176 嘅 cos(π) = −1 唔係 +1 ⟹ Goldstone 係雙向 (+c/−c)
- U5: 88/90 屬 176-Laplacian 半集 (O201 慣例), 唔屬 K_Chain 半譜 (44/46)
- U6: 互補對 v_g(88−n)=−v_g(n) = 反向行波同速, 唔係同向

**剩餘 (partial 原因)**: 半整數 shift 喺 FSR 精化層 (44·4^ℓ) 嘅 v_g 動態; K_Tree 樹狀譜 (λ=4sin²(cπ/68) 族) 嘅 v_g 上界；Bell 實驗觀測檢定非本 O 範圍

---

## Session 2 (2026-10-20, Round 2 — FSR 精化層 + K_Tree 樹狀譜 + SR 對比)

**結果**: 🟢 1937716/1937716 PASS（兩支 scripts）
- `scripts/04_fsr_tree_bound.py` (1937618/1937618): **gap 定理** — gap(N)=1−cos(π/N)=2sin²(π/2N) 半角形式; 精化層 N_ℓ=44·4^ℓ 每層 v_g≤1 唯一 n=0, gap 單調收縮→0 (SR ℓ→∞); **O140 速度階梯 ≡ v_g + Lorentz γ_L=csc=2/√γ_n EXACT**; **自對偶模統一: 鏈 n=22 同樹 c=17 (λ₁₇=μ²) 都 v_g=c/√2**; K_Tree 樹譜 v_g≤1 c=0 唯一; Σλ=66=2K_tree; 半整數層 |v_g|≤1
- `scripts/05_sr_comparison.py` (98/98): **快度格仔** η_n=atanh(v_g/c)=ln cot(πn/176) EXACT (三讀法); O190 質量殼 csc²−cot²=1 逐模; SR 對比 — c=Goldstone 譜速度非公設

docs: `docs/03_sr_structural_comparison.md` (SR 對比 + 全譜族定理)

**判據修正（Round 2）**: F1/F2 初版用固定 1e-9/1e-12 閘, ℓ≥6 時 gap(N_ℓ) 細過閘 ⟹ 假 FAIL; 改 gap 判據 (半角形式 2sin²(π/2N)), 內容昇華「嚴格 <c」→「gap>0 且單調收縮」(判據昇華, 非放寬)

**剩餘 (partial 原因)**: ~全譜族定理已閉合 (K_Chain+樹+精化+半整數); Bell 實驗觀測檢定非本 O 範圍 (spectral boundary 已完成, 觀測層屬 sky 系)

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。