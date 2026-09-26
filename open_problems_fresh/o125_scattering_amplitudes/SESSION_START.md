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
