# O125 — 散射振幅完整推導

> **Session**: 2026-08-29 (新建立，從 v9.0 遷移)
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計後發現不屬於 v10.0 O1-O114 任何現有系列
> **v10.0 位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o125_scattering_amplitudes/`
> **v9.0 來源**: `open_problems_fresh/p_sa_scattering_amplitudes/`

## 問題

見 `docs/01_problem_record.md`

## 前置驗證：v9.0 推導先行驗證

⚠️ **必須先驗證 v9.0 推導在 v10.0 非膨脹框架中是否仍然有效，然後才能開始攻堅。**

1. 讀取 `open_problems_fresh/p_sa_scattering_amplitudes/` 中的原始推導
2. 識別依賴膨脹宇宙假設的部分（v9.0 使用 v9.0 框架）
3. 在 v10.0 非膨脹框架中重新驗證每個公式
4. 如果 v9.0 推導在 v10.0 中仍然有效，則直接遷移
5. 如果 v9.0 推導在 v10.0 中失效，則需要建立新推導

## 前置

O122 (Feynman 規則) 🔴, O124 (QCD 散射) 🔴, O82 (質量生成) 🟢

---

## 閉合摘要 (2026-09-26) — 🟢 已閉合

> ⚠️ 以上原文保留為起點 snapshot; 本節為 append-only 閉合記錄。

### 前置狀態修正
- **O122 實為 🟢 已閉合 (47/47, 2026-09-03)** — 上面標 🔴 已過時。
- O82 🟢 已閉合。O124 🔴 未開始, 但屬 **gauge/膠子扇區**, 唔阻塞 O125 scalar 扇區。

### 前置驗證判決
🔴 **v9.0 推導在 v10.0 中失效 — 重建 (非遷移)**。6 個根本衝突:
連續圈積分 vs 有限譜圈和 / κ 混淆 (1/16 vs κ²=M₀ + λ=2/123) / GeV vs MeV 標度 (2206×) /
場縮放 1/M_GUT vs R_world/88 (56 數量級) / 單一 scalar vs 44 模式 / dim-reg vacuous。
另發現 v9.0 來源**自身** 2 個內部不一致 (running 0.6% vs 3.92%; RG 符號 (1±x)⁻¹) + 驗證鏈斷裂
(`02_verify.py` import 路徑 `/home/wsl/IDCM` 唔存在)。

### 重建成果 (50/50 PASS)
- `scripts/01_preverification.py` — **16/16** (v9.0 裁決)
- `scripts/02_one_loop_scattering.py` — **20/20** (1-loop 2→2 振幅)
- `scripts/03_cross_validation.py` — **14/14** (交叉 + 獨立重推 + 硬編碼掃描)

### 核心新結果
- **圖分類定理**: 模式對角 ⟹ 2→2 只有 s-channel (t/u/box 全禁止)
- **泡閉式**: `B_k(s) = (2θ_k/sin2θ_k)/(4πm_k²)`; `Π_h(0) = N_d/(4πM₀)` (每模式等貢獻)
- ★**結構恆等式**: `Σ_(k=1..44) ω_k² = 90 = B(N_d+1)/2 = Σγ` (同 O211 獨立交叉)
- **1-loop 振幅**: `M⁽¹⁾ = M⁽⁰⁾·Π_h(s)/(s−m_h²)`, `|δ| < 2.4%`
- **光學定理**: `Im Π_h = (1/(4M₀))Σ_on-shell csch(2χ_k)`; h 衰變通道 = 3 = N_gen (🟡 候選)
- **零重整化定理**: `δZ = δm = δλ = 0` (有限 QFT)
- **離散 β**: `b₀ = Tr(T̂⁴) = L₄ = 7`, `b₁ = 2F₇ = 26`; running `Δα⁻¹ = 9 = N_gen²`

### 檔案
```
o125_scattering_amplitudes/
├── final_result.md
├── docs/01_problem_record.md  (+推導時序索引)
├── docs/02_preverification.md
├── docs/03_derivation.md
├── docs/04_audit.md
├── scripts/01-03 (50/50 PASS)
└── data/
```

### 剩餘開放
- 🟡 h 衰變通道 = N_gen 嘅算子證明
- 🔴 完整 SM 費曼規則 (fermion/gauge 圈) → O85/O144
- 🔴 O124 (QCD 膠子散射) 未開始

---

## 交接閉合 (2026-09-26) — O124 → O125「gg→gg 完整極化求和」🟢

> ⚠️ 本節 append-only; 以上原文一字不改。

### 背景
O124 (QCD 膠子散射, 🟡 部分閉合) 閉合色結構 (`G_ss = 72`) 後, 明確交接「**gg→gg 完整極化求和 → 移交 O125**」。

### 成果 (25/25 PASS)
- `scripts/04_gg_gg_polarization.py` — **25/25 PASS**
- ★ **16 helicity 組態 → 10 樹層消失** (all-plus / all-minus / one-minus) **, 6 存活** (2+2−, MHV) = `C(4,2) = 2·N_gen`
- ★ **完整極化求和**: `Σ_{colours,spins}|M(gg→gg)|² = g⁴·N_c²(N_c²−1)·2(s²+t²+u²)³/(s²t²u²) = 1152 g⁴ B(s,t,u)`
- 初態平均: `⟨|M|²⟩ = (9/2) g⁴ B(s,t,u)` ✓ (標準文獻, Dixon eq.10/46)
- 色因子 `N_c²(N_c²−1) = 72 = C_A²(N_c²−1)` ✓ 同 O124 `G_ss = 72` 獨立一致
- 運動學括號: `B(s,t,u) = 3 − ut/s² − us/t² − st/u² = (s²+t²+u²)³/(8s²t²u²)`
- 自捉 3 錯: `Tr=δ/2` vs `Tr=δ` 歸一化 (因子 16); B3 動量守恆慣例 (`p₁+p₂=p₃+p₄`); §F collinear pole 模式選擇

### 檔案
`docs/05_gg_gg_polarization.md`, `scripts/04_gg_gg_polarization.py`, `data/04_gg_gg_stdout.txt`

### 剩餘開放
- 🟡 膠子 helicity `λ=±1 ↔ Z₂` 算子化
- 🔴 `B_disc` 有限譜正則化 (88-ring collinear pole)

---

## 算子化閉合 (2026-09-26) — 膠子 helicity λ = ±1 🟢

> ⚠️ 本節 append-only; 以上原文一字不改。

### 靶
上一節剩餘開放嘅 **🟡「膠子 helicity λ=±1 ↔ Z₂ 算子化」** — `docs/05 §6` 只做到**結構對應**, 冇算子。

### 成果 (51/51 PASS)
- `scripts/05_helicity_operator.py` — **51/51 PASS**, 0 字面 True, 兩條獨立路線
- ★ **算子**: ĥ = **A₅ 反演 `−I`** 作用於 88-grid 膠子扇區 (O182 精確代數座標)
- ★ **ĥ² = 1** (fixed-point-free 對合) ⟹ 譜 = **{+1 × 44, −1 × 44}**
- ★ **結構強迫**: `ĥ² = 1 ⟹ λ² = 1 ⟹ λ = ±1` — helicity 值域由對合**強迫**, 零擬合
- ★ **88 = 2 × 44 = 2 N_d**: 反演將 88 邊配成 **44 對 + 0 固定** ⟹ 冇 helicity-0 膠子
- ★ **幾何 chirality ⟹ 絕對定向**: canonical 88-grid `|Sym|=4` (含 `−I`, 非手性) vs
  冷斑軌道 88-grid `|Sym|=2` (全 proper, **手性**) ⟹ P 破缺 ⟹ helicity 符號係物理量
- 交叉: `Σ_{k=1..44} 4sin²(πk/88) = 90` (O124/O211); 16 = 2⁴, 6 = 2N_gen (docs/05)

### 檔案
`docs/06_helicity_operatorization.md`, `scripts/05_helicity_operator.py`, `data/05_helicity_operator_*`

### 剩餘開放
- 🟡 「ĥ 嘅 ±1 扇區 = 物理 helicity」係標準字典**詮釋** (非結構); 半移位模型 `(−1)^n` 未由幾何獨立導出
- 🔴 `B_disc` 有限譜正則化 (88-ring collinear pole)
- 🔴 完整 SM 費曼規則 (fermion/gauge 圈) → O85/O144
