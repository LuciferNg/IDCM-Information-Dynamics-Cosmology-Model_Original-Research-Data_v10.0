# O120 — 輕夸克質量 (u, d)

## 狀態: 🟢 已閉合（診斷性閉合, 2026-10-06）

## 結論
u/d 質量喺三框架下全部數值閉合（<2.1%）；原問題「n=1 三態靠 P_f 分化」已裁決 —— P_f={3.6,15.5,33} 係 O136 search + 目錄密度巧合（zombie），由 A₅ 指派（e,u,d→n=1,2,3）取代；「第一代坐純 γ-階梯」係唯一真實結構訊號（gen1 C_f 跨度 1.058 = 84 三子集唯一最小, p=0.0119）。殘餘（C_f 生成器, 2149× 跨度）→ O206。

## 關鍵公式
- v9.0 第一代: `m_u = m_t·(F₉+ε³K₉)/CY₃³`（0.5125%）, `m_d = m_b·(F₈+ε³K₈)/CY₃²`（0.4043%）
- O136 M₀×γ×P_f: `m_u = M₀·γ₁·15.5`（2.0249% 🟡）, `m_d = M₀·γ₁·33`（0.4675% ✅）; `m_u/m_d = 15.5/33`（Δ1.5502%）
- up_quark_correction: `m_u = λ₇·M_Pl·exp(−V_Gen1)·√φ`（0.4720%）, `m_d = ·×5.3`（0.2443%）
- ★ 合法模式集兩判準一致 = `{1,2,3,4,5,7,9,11,13}`；A₅ C_f = m/(M₀γ_n): gen1 {3.5941, 3.8029, 3.6620} → 跨度 1.058
- ★ 預言: 若 C_f ≡ L₆/F₅ = 3.6 → m_e 0.164% ✅ / m_d 1.69% 🟡 / **m_u 5.34% 🔴**（需 C_u/C_d = 1.038476）

## 密度基準
- N_search = 84（C(9,3) 全三子集精確枚舉；gen1 rank = **1**）
- N_mc = 200k × 3 seeds {7, 123, 20260926}，p = 0.0119/0.0122/0.0126
- q_obs = **1/84 = 1.19%** → 🟢（<5%）；gen2 rank 3/84 (p=0.036) · gen3 rank 16/84 (p=0.19)
- 目錄 1..176 結構數密度 = 49.4%（P_f 三數零判別力 → 唔計為閉合證據）

## 依賴
O54 → O137 → O136 → **O120**（殘餘 → O206 via register）

> 完整closeout記錄: `docs/04_closeout_record.md` · 驗證: `scripts/01` 35/35 + `scripts/02` 78/78

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `4296c913cf7465ac` | 2026-10-24 | partial | u/d 質量喺三框架下全部數值閉合（<2.1%）；原問題「n=1 三態靠 Pf 分化」已裁決 —— Pf={3.6,15.5,33} 係 O136 search + 目錄密度巧合（zombie），由 A₅ 指派（e,u,d→n=1,2,3… | open_problems_fresh/o120_light_quark_masses/final_result.md | — |
<!-- conclusion-history:end -->
