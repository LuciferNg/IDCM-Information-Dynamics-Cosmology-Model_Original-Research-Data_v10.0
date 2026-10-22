# O133 — docs/01: v9.0 P(k) 鏈譜推導驗證報告 (v10.0 非膨脹框架)

> **日期**: 2026-09-02
> **scripts/01_v9_validation.py** · **2/9 PASS → 判定: 🔴 v9.0 推導喺 v10.0 中失效**
> **前置**: O100 (C_ℓ→P(k)) 🟢, O76 (z) 🟢, O31 (ξ↔P(k) wiggle) 🟢, O51 (BAO) ✅

---

## 0. 一句結論

> **v9.0 嘅 P(k) = Σ γ_n·G(k−k_n) 喺 v10.0 非膨脹框架中失效: 用錯 grid (44-site 鏈整數諧和 2πn/R_world), 用錯權重 (γ_n 升到 Nyquist), 導致同真 BOSS P(k) 反相關 (r=−0.914), χ²/dof=1.4×10⁴。根因: 觀察結構 (C_ℓ 峰 + BAO wiggle) 係喺 88-site 環/sync 諧和 grid 上, 唔係 44-site 鏈 grid 上 — sync 模 = 環嘅第 88 諧和 (精確整數), 但唔係 44-site 鏈嘅整數模 (n=14.0056)。正確 P(k) = O100 逆投影算符 ℳ (已閉合 🟢), 見 docs/02。**

## 1. v9.0 推導摘要 (open_problems_fresh/pk_chain_spectrum/01_derive_pk.py)

```
P(k) = Σ_{n=1}^{43} γ_n · exp(−(k − k_n)²/(2σ²))     (高斯展寬線譜)
γ_n = 4 sin²(πn/88)         K_Chain eigenvalue (能量/質量)
k_n = 2πn/R_world            λ_n = R_world/n  (整數諧和)
σ   = 2π/(R_world/4)         K_Tree level-1 粗粒化窗口
對照: BOSS DR12 P(k)         (路徑 /tmp/public_material_BAO/, 已死)
```

## 2. 膨脹依賴假設審計

| # | v9.0 假設 | v10.0 狀態 | 判決 |
|:-:|:----------|:-----------|:----:|
| E1 | R_H = c/72.59 作「哈伯半徑」 | O73: R_world = 4129.94 Mpc, 世界環**半徑**, 72.59 = ω_ring (角頻率, 非膨脹率) | 🔴 數值存活, 角色替換 |
| E2 | k_n = 2πn/R_H (λ=R_H/n 鏈諧和) | 44-site 鏈 λ_n = R_world/n 確存在 (kchain_wave_params.py) | 🟢 鏈諧和本身有效, 但**唔係**觀察結構 grid (見 §4) |
| E3 | σ = 2π/(R_world/4) (K_Tree L1) | O140 FSR: N_ℓ = N·4^ℓ, L1 窗口 = R_world/4 ✓ | 🟢 存活 (遷移後沿用) |
| E4 | h = 0.7259 單位轉換 | O100 用 h_BOSS = 0.6727 (BOSS/Planck 慣例) | 🟢 純單位, 用 BOSS h |
| E5 | γ_n 作 P(k) 幅度權重 | O100: 幅度 = C_ℓ 母函 A_m × 轉換 2ℓ², **唔係 γ_n** | 🔴 權重錯誤 (核心) |
| E6 | 數據 /tmp/public_material_BAO/ | 已死; 用 v10.0 數據 (boss_dr12_bao_wiggles + GilMarin16) | 🔴 重指 |

## 3. 逐項驗證 (scripts/01, 9 項)

### A — 模型基本能力 (v9.0 自身品質)

| 檢查 | 結果 | 狀態 |
|:-----|:-----|:----:|
| A1 覆蓋 BOSS 範圍 ≥80% | 只覆蓋 k<0.097 h/Mpc (n=1..43) = **63%** | ❌ FAIL |
| A2 模型平滑 (應無 BAO wiggle) | 振盪 RMS 0.066 > 0.1×BOSS 0.0528 | ❌ FAIL (σ/δk=4 仍出鋸齒, 插值混疊) |

### B — 結構 grid 審計 (核心診斷)

| 檢查 | 結果 | 狀態 |
|:-----|:-----|:----:|
| B1 sync = 88-site 環第 88 諧和 | m = 2πR_world/λ_sync = **88.0000000000** | ✅ PASS ★ |
| B2 sync 唔係 44-site 鏈整數模 | n = R_world/λ_sync = **14.0056** (44/π) | ✅ PASS ★ 診斷確認 |
| B3 γ_n 權重唔單調升 | γ_43=3.995 ≫ γ_1=0.005 (升到 Nyquist) | ❌ FAIL |

### C — 決定性數值對照 (overlap 52 點, vs 真 BOSS P(k))

| 檢查 | 結果 | 狀態 |
|:-----|:-----|:----:|
| C1 形狀相關 r > 0.5 | **r = −0.914** (反相關!) | ❌ FAIL |
| C2 χ²/dof < 3 | **χ²/dof = 1.39×10⁴** | ❌ FAIL |
| C3 包絡 log 斜率同號 | BOSS −16.0 (下降) vs 模型 **+26.4** (上升) | ❌ FAIL |

### D — v10.0 結構交叉檢驗

| 檢查 | 結果 | 狀態 |
|:-----|:-----|:----:|
| D1 sync 諧和峰命中 BOSS | 9 峰中 **7** 命中 (Δk<0.004 h/Mpc) | ✅ PASS ★ |
| D2 line2↔BOSS wiggle 峰 | 55-bin 太疏 (峰止 0.13, line2@0.193); 引用 O100-A Δ=+0.5% | 🟡 REF |

**★ B1/B2/D1 嘅「通過」係 v10.0 結構事實, 唔係 v9.0 模型有效 — 反而揭示正確 grid。**

## 4. 根因: 鏈 grid vs 環 grid vs sync grid (結構診斷)

三族諧和 (h 無關, Mpc⁻¹):

| 諧和族 | 公式 | spacing | 角色 |
|:-------|:-----|:-------:|:-----|
| 44-site 鏈 | k_n = 2πn/R_world | 0.001522 | K_Chain 本徵模 (弦/鏈) — **v9.0 誤用** |
| 88-site 環 | k_m = m/R_world | 0.000242 | 世界環 full-ring 模 |
| **sync** | k = 88/R_world | 0.021308 | λ_sync = πR_world/44 = 2πR_world/88 |
| C_ℓ grid | k = 44n/R_world | 0.010654 | 半-sync (O100 峰階梯) |

**結構恆等**:
```
λ_sync = 2πR_world/88  ⇒  sync = 88-site 環嘅第 88 諧和 (m=88, 精確整數)
        = πR_world/44  ⇒  喺 44-site 鏈上需要 n = 44/π = 14.0056 (非整數)
```

⇒ **觀察到的 C_ℓ 峰 + BAO wiggle 全數喺 環/sync grid 上; 44-site 鏈嘅整數諧和 (2πn/R_world) 永遠對唔上 (偏差 44/π = 14.0056)。** v9.0 用鏈 grid 做「full ring mode」係把鏈 (chord) 誤當環 (ring) — 呢個就係 PARADIGM BREAK 後 O73「R_world = 半徑」嘅直接後果 (v9.0 隱含當 R_H 係周長)。

## 5. 判決

| 項目 | 結果 | 狀態 |
|:-----|:-----|:----:|
| v9.0 推導喺 v10.0 有效? | **失效** (2/9 PASS, r=−0.91, χ²/dof=1e4) | 🔴 |
| 需要新推導? | 已存在: **O100 逆投影算符 ℳ** (σ8=0.748 已閉合) | 🟢 |
| 遷移策略 | 遷移 O100 構建; v9.0 僅 σ 展寬概念存活 | ✅ |
| 遷移後 P(k) 鏈譜 | 見 docs/02_v10_pk_chain_spectrum.md | ✅ |

## 6. 剩餘開放 (誠實標記)

| 項目 | 狀態 | 說明 |
|:-----|:----:|:-----|
| P(k) 平滑 broadband (功率律包絡) 首推 | 🔴 | O100 只俾 9 條線; broadband 需 O86 W-field 線性微擾完整解 (O99/11 已標記) |
| 線譜 vs 星系 P(k) 嘅 bias 轉換 | 🟡 | BOSS 係星系 (b²~3-4), Δ²_ID/Δ²_obs~0.07-0.24 唔係乾淨形狀檢驗 (k 依賴 bias) |
| line2↔0.1923 獨立複檢 (55-bin 太疏) | 🟡 | 需密 bin Beutler 120-bin 重檢 (O100-A 已用, 現得 Δ=+0.5%) |
