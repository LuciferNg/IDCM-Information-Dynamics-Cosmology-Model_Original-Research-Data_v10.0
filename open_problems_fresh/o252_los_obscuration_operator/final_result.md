# O252 — 視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip)

## 狀態: 🟡 部分閉合 (R1-R13 + closeout 審計; 2026-10-17)

## 結論
τ(v) = τ₀·ℓ_band(θ(v)) + τ_w·exp(−(v∓v_abs)²/2σ²) 第一版由世界環幾何零新常數推出:
窗存在（含冇-dip 反例）＋窗寬統計閉合, 深度上限/中位雙命中; 窗中心結構身份
(μ_hat=235.7±21.6 未命中任何 hop 質量統計) ＋方向 sign 兩個 gap 開放。

## 關鍵公式
- v_abs = V_max/√2 = 289.76 km/s（hop=4 事前, 🔴 出 CI 已降級）／ V_max/2 = 204.9（hop=2 後驗候選）
- σ = σ₃·(17/15) = 189.52 km/s（FSR ℓ=3 quantum × 帶厚比, obs 189.29, dev 0.12% ✅）
- τ_w = ⟨hop⟩ = 4 → depth 0.9817（上限 top-3 0.923 ✅）／ τ_eff = 4·M₄/M₀ = 28/15 → 0.845（中位 dev 3.5% 🟡）
- 窗存在: 11/13 命中 hop2 窗 (p=0), 9/13 hop4 窗 (p=0.0004) ✅
- 方向: 10/13 藍側 two-sided p=0.092 🔴

## 依賴
O252 ← O180（投影核 v=√(a₀r)）← O179（hop 階梯）← O140（FSR ℓ=3）← O143（𝒫 天球）

## 密度基準
- 窗存在 MC null: 9-11/13 vs 均勻 null p=0.0004-0 (seed 42/7)
- 窗中心: N_search = 2（hop=2 204.9 vs hop=4 289.76）, 觀測 μ_hat 兩者皆未鎖定 → 🟡
- 深度: 上限 τ_w=4（top-3 0.923, 6%）＋中位 τ_eff=28/15（3.5%）→ 🟡
- 方向: two-sided p=0.092 → 🔴 未閉合

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `455c6b213fc39930` | 2026-10-24 | partial | τ(v) = τ₀·ℓband(θ(v)) + τw·exp(−(v∓vabs)²/2σ²) 第一版由世界環幾何零新常數推出: 窗存在（含冇-dip 反例）＋窗寬統計閉合, 深度上限/中位雙命中; 窗中心結構身份 (μhat=235.7±… | open_problems_fresh/o252_los_obscuration_operator/final_result.md | — |
<!-- conclusion-history:end -->
