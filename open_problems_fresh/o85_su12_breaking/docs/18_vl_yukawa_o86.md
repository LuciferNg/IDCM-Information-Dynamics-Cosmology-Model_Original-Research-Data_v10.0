# O85 — 開放項攻關 ③：y_Y 承接 O86 湯川第一性原理（docs/16 開放項①收窄）

> **建立**: 2026-10-05（開放項攻關第二輪） | **狀態**: 🟢 **19/19 PASS**（`scripts/20_vl_yukawa_o86.py`; 19 項真計算、0 字面聲明）
> **本檔 append-only**: `docs/01`–`docs/17` 一字不改；本檔為新推導記錄
> **觸發**: 用戶 focus 注入「**IDCM 應該已經對湯川耦合以第一性原理攻破**」—— 指正 docs/16 將 y_Y 標「🔴 需收窄」係冇承接 IDCM 現有湯川框架

---

## 〇、IDCM 已閉合嘅湯川第一性原理框架（v10.0）

| 來源 | 內容 | 狀態 |
|:--|:--|:--|
| **O86 §3.1** | `y_f = √2·M₀·γ_k·S_f / v`（質量 m_f = M₀·γ_k·S_f）| 🟢 34/34 PASS; 輕子 e/μ/τ 0.16%/0.13%/0.34% |
| **O59 docs/05** | 12D Yukawa 譜 **1+11** = Cartan(1) + Rank(11) = Higgs VEV + 11 Cartan generators | 🟢 閉合 |
| **O59 docs/08**（clean）| λ_max_clean = Nd−2B−1/γ₂₀ = 36−1/γ₂₀ = **35.4170**; tr(Y_clean) ≈ **2B² = 32**（0.48%）| 🟢 |
| **O65** | Rank-1 Yukawa 結構 `Y_ij ∝ ω_i·ω_j = √(γ_i·γ_j)` → CKM/PMNS 閉合 | 🟢 |
| O86 N4 | 夸克質量譜 (s,c,b,t) 🔴 **未閉合** —— 交 O120/O136 | ⚠️ 唔可以過度宣稱 |

**★ 關鍵**: γ_k = 4sin²(πk/88) = **同 O85 嘅 λ_m 譜同一 K_Chain 譜**（§A 複現 γ₁/γ₇/γ₂₀）

## 一、★★ y_Y 升格（O86 結構管轄）

```
O86:  y_f = √2·M₀·γ_k·S_f / v
O85:  y_Y(m) = √2·M₀·γ_m / v   （S=1 基礎單態）—— 由 O86 結構管轄, 唔再係純自由參數
```

- y_Y(m) = √2·M₀·γ_m/v: m=1 → 8.17×10⁻⁷, m=13 → 1.28×10⁻⁴（單調增）
- VL 質量階梯: `m_VL = y_Y·λ_m·Λ = (√2·M₀/v)·λ_m²·Λ·S(m)`
- λ² 跨度 = (λ₁₃/λ₁)² ≈ **24736×**（比 docs/16 嘅 λ 跨度 157× 更陡——兩個極端都承接 O86 譜）

## 二、★★ O59 1+11 ↔ O85 VL 11/rep 同源（§E）

- **O85 VL 11/rep 嘅「11」 = O59 1+11 譜嘅「11」 = rank(su(12)) = L₅ = 11**（Cartan generator 數）
- O59 clean 主模身份: λ_max = 36 − 1/γ₂₀（E1 獨立複現 35.4170 vs 35.4178 ✓）
- ⚠️ 誠實區分（E6）: O59 12D 譜嘅 11 = **rank 生成元數**；O85 VL 嘅 11 = **額外 Weyl 數**（66 層額外5 + 單態6）——兩者同源於 L₅=11 但唔係同一物件
- ⚠️ λ_max_clean/λ₁₃ = 44.19 ≈ N_d+0.19 —— 記錄但**唔宣稱結構**（E5, 可能巧合）

## 三、開放項狀態更新

| 開放項 | 狀態 |
|:--|:--|
| docs/16 開放項①「🔴 y_Y 需收窄」| ✅ **已收窄**——由 O86 湯川結構管轄（y_Y = √2M₀γ_m/v）|
| 剩餘 🟡 | **S(m)**（VL 幾何重疊）未定——需 O59 12D clean 譜完整 S_f 或 CY₃ 重疊積分 |
| 剩餘 ⚠️ | O86 夸克質量譜本身未閉合（O120/O136）——「IDCM 湯川全閉合」宣稱須限輕子＋混合 |

## 四、檔案

```
scripts/20_vl_yukawa_o86.py   ✅ 19/19 PASS
data/20_vl_yukawa_o86.json    ✅
docs/18_vl_yukawa_o86.md      ← 本檔
```

## 五、參考（跨 O 只讀）

- `open_problems_fresh/o86_sm_gr_coupling/docs/02_derivation_record.md` §3.1-3.2
- `open_problems_fresh/o59_z3_12_subspace/docs/05_su12_extension_closure.md` §三-四
- `open_problems_fresh/o59_z3_12_subspace/docs/08_rederivation.md` §2.3-3.2
- `open_problems_fresh/o65_mixing_first_principles/docs/01_closure.md` §二-三