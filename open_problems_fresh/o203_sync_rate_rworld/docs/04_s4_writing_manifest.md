# O203 — docs/04: S4 寫入/manifest 速率家族 (scripts/04, 8/8 PASS)

> **日期**: 2026-09-17 | **Script**: `scripts/04_s4_writing_manifest.py` | **mpmath 60 dps**

## 一、★ 過程速率家族: v(m) = m·λ_sync/T_ring = (m/88)·c

88 個 site, 週期 T_ring (相位 2π)。任何寫入/manifest 過程 = 每週期整數事件數 m:

| m (事件/週期) | v/c | 過程 | 出處 |
|:---|:---|:---|:---|
| 1 | **c/88** | 單 site 刷新/週期 | λ_sync/T_ring (候選 #2 自身身份) |
| 2 | **c/44** | O7 相位滑移寫入 (2×π per 2π) | O7 閉合 |
| 44 | **c/2** | O138 Γ = N_d/T_ring = f_44/2 (Z₂ 配對/manifest 全掃描) | O138 閉合 |
| 88 | **c** | f_44 Nyquist (88 site 訪問/週期) | O164 閉合 |

**驗證 (stored-value 0.0016% 類)**: Γ = 44f_ring = 0.51987/Gyr, f_44 = 88f_ring = 1.03975/Gyr, Γ = f_44/2 ✓

## 二、C_energy·c = c/45 唔屬於過程速率家族

```
C_energy 速率對偶 = f_44/45 = 0.023106 /Gyr
vs 家族: f_ring = 0.01182, 2f_ring = 0.02363, Γ = 0.51987, f_44 = 1.03975
→ f_44/45 冇任何 corpus 速率命中 (scripts/01 C6 同確認)
```
- **45 唔係與 T_ring 掛鈎嘅事件計數**: m = 45 給出 v = 45c/88 ≈ 0.5114c ≠ c/45。
- 若硬將 T_ring = 45λ_sync/v_sync, v_sync = 88c/45 ≈ 1.96c **超光速** — c/45 冇 T_ring 身份 (docs/05)。

## 三、45/88 ≈ 23/45 近miss (trap window, 唔收)

```
45/88 = 0.511364,  v_world/c = 23/45 = 0.511111
rel dev = 0.0494%  (trap window 1e-5~1e-3)
45/88 − 23/45 = (2025−2024)/(88·45) = 1/3960 — 純有理近miss, 唔係結構
```

## 四、S4 判決

1. **寫入/manifest 速率全部已存在**: m/88 家族 {c/88, c/44, c/2, c} 對應 {f_ring, 2f_ring, Γ, f_44} — 全部 corpus 已註冊 (O7/O138/O164)。
2. **C_energy·c = c/45 係譜漂移 (docs/01 §三), 唔係過程速率** — 冇任何寫入/manifest 過程以 c/45 運行。
3. 「種子 δ → 88 → Z₂ → 44 嘅擴散速率」= Γ = 44/T_ring (全掃描) 或 f_44 (Nyquist) — 已有, 唔係新常數。
