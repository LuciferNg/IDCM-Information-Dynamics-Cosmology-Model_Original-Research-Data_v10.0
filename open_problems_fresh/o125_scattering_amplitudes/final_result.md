# O125 — 散射振幅完整推導 (1-loop 2→2)

## 狀態: 🟢 已閉合 (v9.0 失效 → v10.0 重建完成; 50/50 PASS; 唯一 🟡 候選已標記)

## 結論
v9.0 散射振幅推導 (連續 φ⁴ + dim-reg) 在 v10.0 非膨脹框架中**整體失效** (6 衝突: 有限譜圈和/κ 混淆/GeV 標度/場縮放/模式結構/dim-reg vacuous), 已用有限離散 QFT 重建: 模式對角 ⟹ 2→2 只有 s-channel, 1-loop = h 自能泡 `M⁽¹⁾ = M⁽⁰⁾·Π_h(s)/(s−m_h²)`, 零重整化定理成立 (δZ=δm=δλ=0), 離散 β = T̂ 譜不變量 (`b₀ = L₄ = 7`)。

## 關鍵公式
- 圖分類: 模式對角頂點 `h φ_k φ_k` ⟹ 只有 s-channel (t/u/box 全禁止)
- 泡閉式: `B_k(s) = (2θ_k/sin2θ_k)/(4π m_k²)`, `θ_k = arcsin(√s/(2m_k))`
- ★結構恆等式: `Σ_(k=1..44) ω_k² = 90 = B(N_d+1)/2 = Σγ` (O211 交叉)
- 零動量泡: `Π_h(0) = N_d/(4πM₀) = 0.1254944` (每模式等貢獻)
- 1-loop 振幅: `M⁽¹⁾(s) = M⁽⁰⁾(s)·Π_h(s)/(s−m_h²)`, `|δ| < 2.4%`
- 光學定理: `Im Π_h(s) = (1/(4M₀))Σ_{on-shell} csch(2χ_k)`
- h 衰變通道: `2m_k < m_h ⟺ ω_k < 1/4 ⟺ k ∈ {1,2,3}` (3 = N_gen, 🟡 候選)
- 零重整化: `δZ = δm = δλ = 0` (有限 QFT, 無 1/ε)
- 離散 β: `b₀ = Tr(T̂⁴) = L₄ = 7`, `b₁ = 2F₇ = 26`; running `Δα⁻¹ = 9 = N_gen²`

## 依賴
O80 → O82 → O94 → O122 → O142 → O211 → **O125**
(另: v9.0 p_sa_scattering_amplitudes 🔴 失效 — 非遷移, 已重建)

## 密度基準
- N_search = 1（純代數恆等式: `Σω_k² = 90` 由 `Σsin² = N/2` 閉式; `Π_h(0) = N_d/(4πM₀)` 由 `g_k²/m_k² = 1/M₀` 精確抵消; 各為唯一候選）
- N_mc = N/A（無隨機擬合; 全部閉式/結構斷言）
- d_obs = 0（無外部觀測數據可對; 結構精確性以 60 dps 獨立重推為準, dev < 10⁻⁵⁰）
- q_obs = N/A → 🟢（精確恆等式 + 結構定理, 非統計匹配）

> ⚠️ O208 規則: 純代數恆等式 `N_search = 1` + 唯一候選聲明可跳過 MC。O125 全部頭條結果屬此類 (閉式/結構定理), 無擬合參數。

## 驗證
- `scripts/01_preverification.py`: 16/16 PASS (v9.0 裁決)
- `scripts/02_one_loop_scattering.py`: 20/20 PASS (1-loop 重建)
- `scripts/03_cross_validation.py`: 14/14 PASS (交叉 + 獨立重推 + 硬編碼掃描)
- `scripts/04_gg_gg_polarization.py`: 25/25 PASS (O124 交接: gg→gg 完整極化求和)
- `scripts/05_helicity_operator.py`: 51/51 PASS (helicity λ=±1 算子化; 組合 + 幾何雙路線)
- 硬編碼字面 True: **0** (AST 掃描)
- 上游交叉: O122 / O82 / O94 / O142 / O211 全部核實

## §O124 交接 — gg→gg 完整極化求和 (2026-09-26, 25/25 PASS)
- 16 helicity 組態: 10 樹層消失 (all±/one±), **6 存活** (2+2−, MHV) = `C(4,2) = 2·N_gen`
- ★**完整極化求和**: `Σ_{colours,spins}|M(gg→gg)|² = g⁴·N_c²(N_c²−1)·2(s²+t²+u²)³/(s²t²u²) = 1152 g⁴ B(s,t,u)`
- 初態平均: `⟨|M|²⟩ = (9/2) g⁴ B(s,t,u)` (標準文獻 ✓, Dixon hep-ph/9601359 eq.10/46)
- 色因子 `N_c²(N_c²−1) = 72 = C_A²(N_c²−1)` = O124 `G_ss` ✓
- 運動學: `B(s,t,u) = 3 − ut/s² − us/t² − st/u² = (s²+t²+u²)³/(8s²t²u²)`
- 詳見 `docs/05_gg_gg_polarization.md`

## §helicity 算子化 (2026-09-26, 51/51 PASS)
- ★ **算子**: ĥ = **A₅ 反演 `−I`** 作用於 88-grid 膠子扇區 (O182 精確代數座標 Q(√5)³)
- ★ **ĥ² = 1** (fixed-point-free 對合) ⟹ 譜 = **{+1 × 44, −1 × 44}**; `Tr = 0`, `det = +1`
- ★ **結構強迫**: `ĥ² = 1 ⟹ λ² = 1 ⟹ λ = ±1` — helicity 值域由對合**強迫** (零擬合)
- ★ **88 = 2 × 44 = 2 N_d**: 反演配成 **44 對 + 0 固定** ⟹ **冇 helicity-0 膠子** (無質量 spin-1)
- ★ **幾何 chirality ⟹ 絕對定向**: canonical 88-grid `|Sym|=4` (含 `−I`, 非手性) vs
  冷斑軌道 88-grid `|Sym|=2` (全 proper, **手性**) ⟹ P 破缺 ⟹ helicity 符號係物理量
- 交叉: `Σ_{k=1..44} 4sin²(πk/88) = 90` (O124/O211); 16 = 2⁴, 6 = 2N_gen (docs/05)
- 誠實邊界: 「±1 扇區 = 物理 helicity」用標準字典 (P 反轉 helicity); 屬**詮釋**, 非結構
- 詳見 `docs/06_helicity_operatorization.md`
