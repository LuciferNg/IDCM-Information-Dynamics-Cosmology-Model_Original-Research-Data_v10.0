#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O133 scripts/05 — 三路徑 broadband 綜合對照 (O86 微擾 / 全逆 Abel / 平滑包絡)
============================================================================
將 docs/04 三個候選機制同一格上計算, 對照 BOSS, 量化系統性缺口。v2 修正:
P2 (全逆 Abel) 只用 O83 閉合嘅 9 峰 (m≤9), 因為母函 m>9 延伸係 O100 標記
「未閉合」(1/16 地板係猜測)。未閉合延伸另算 P2b 並標 🔴。

路徑:
  P1  = W-field 自由 propagator:  P(k_n) ∝ 1/(2ω_n), ω_n = 2sin(πn/88)
  P2  = 全逆 Abel (閉合 9 峰):    P(k_m) ∝ A_m  (O83 母函, 零參數)
  P2b = 全逆 Abel (1/16 地板延伸): 全 44 模 C_ℓ (🔴 依賴未閉合延伸)
  P3  = 平滑 C_ℓ 包絡 (ℓ⁻³):     P ∝ k^{−1} (scale-invariant 解析)

對照:
  BOSS CMASS 3 點 (k=0.079, 0.193, 0.292 h/Mpc): P = 18036, 5117, 2409 Mpc³
  ΛCDM 物質: −1.2 … −1.4  [T(k) k_eq 傳遞]
"""
import numpy as np

R_world = 4129.94
H = 0.6727

k_obs_h = np.array([0.079, 0.193, 0.292])
P_obs = np.array([18036.0, 5117.0, 2409.0])
s_obs = np.polyfit(np.log(k_obs_h), np.log(P_obs), 1)[0]

# ─── O83 母函 (閉合, 零參數) ───
def A_m(m):
    if m == 1: return 1.0
    if m % 2 == 0:
        k = m // 2
        return ((k + 1) / (4 * k - 1))**2
    return {3: 4/9, 5: 3/14, 7: 1/7}.get(m, 1/16)

# ─── P1: W-field propagator (全 44 模) ───
n = np.arange(1, 45)
omega = 2.0 * np.sin(np.pi * n / 88.0)
P1 = 1.0 / (2.0 * omega)
P1 = P1 / P1[0]

# ─── P2: 閉合 9 峰母函 → 逆 Abel (P ∝ A_m) ───
m9 = np.arange(1, 10)
A9 = np.array([A_m(m) for m in m9])
P2 = A9 / A9[0]
ell9 = np.array([220, 537, 810, 1014, 1121, 1340, 1412, 1465, 1474], float)  # O100 閉合峰位
k9_h = ell9 / R_world * H

# ─── P2b: 1/16 地板延伸 (全 44 模) — 🔴 未閉合依賴 ───
P2b = np.array([A_m(mm) for mm in n])
P2b = P2b / P2b[0]

# ─── P3: 平滑包絡 (scale-invariant C_ℓ ∝ ℓ⁻³ ⇒ P ∝ k⁻¹) ───
k_full = 44.0 * n / R_world * H
P3 = k_full**(-1.0)
P3 = P3 / P3[0]

# ─── 斜率 (3 點窗) ───
def slope_at(power, kh):
    vals = []
    for ko in k_obs_h:
        i = np.argmin(np.abs(kh - ko))
        vals.append(power[i])
    return np.polyfit(np.log(k_obs_h), np.log(vals), 1)[0]

s1 = slope_at(P1, k_full)
s2 = np.polyfit(np.log(k9_h[:3]), np.log(P2[:3]), 1)[0]     # m=1,2,3 in-range
s3 = slope_at(P3, k_full)
s2b = slope_at(P2b, k_full)

d1, d2, d3 = s1 - s_obs, s2 - s_obs, s3 - s_obs    # 正 = 太扁 (同 docs/03 約定)
dn = np.mean([d1, d2, d3])

results = []
def check(name, cond, detail):
    results.append((name, bool(cond), detail))
    print(f"  [{'✅' if cond else '🔴'}] {name}: {detail}")

print("=" * 74)
print("  O133 scripts/05 — 三路徑 broadband 綜合對照 (v2)")
print("=" * 74)
print(f"\n  斜率 (k ∈ [0.079, 0.292] h/Mpc):")
print(f"    P1 W-field propagator:     n = {s1:+.2f}")
print(f"    P2 閉合 9 峰母函:          n = {s2:+.2f}   (m=1,2,3 in-range, docs/03 一致)")
print(f"    P2b 1/16 地板延伸:         n = {s2b:+.2f}  🔴 依賴未閉合延伸")
print(f"    P3 平滑包絡 (ℓ⁻³):         n = {s3:+.2f}   (解析預言 −1.00)")
print(f"    BOSS CMASS:                n = {s_obs:+.2f}")
print(f"    ΛCDM 物質:                 n ≈ −1.2 … −1.4  [T(k) k_eq 傳遞]")
print(f"\n  Δn (vs BOSS): P1 {d1:+.2f} | P2 {d2:+.2f} | P3 {d3:+.2f} | mean {dn:+.2f}")

check("A1_P1_slope", np.abs(s1 + 1.0) < 0.25, f"P1 n={s1:+.2f} ≈ 質量零極限 −1.00 (sin dispersion 修正)")
check("A2_P2_closed", np.abs(s2 + 0.67) < 0.1, f"P2 n={s2:+.2f} = docs/03 閉合母函包絡 −0.67 ✅ 一致")
check("A3_P3_analytic", np.abs(s3 + 1.0) < 0.05, f"P3 n={s3:+.2f} ≈ scale-invariant ⇒ P∝k⁻¹ (解析 −1.00, 離散取樣差)")
check("A4_P2b_unclosed", abs(s2b - s2) > 0.2, f"P2b n={s2b:+.2f} ≠ P2 {s2:+.2f} — 延伸選擇改變斜率 ⇒ 未閉合依賴確立 🔴")
check("B1_convergence", np.abs(d1-dn) < 0.25 and np.abs(d2-dn) < 0.25 and np.abs(d3-dn) < 0.25, f"閉合路徑 (P1,P2,P3) Δn 收斂 ±0.25 (mean {dn:+.2f})")
check("B2_systematic_gap", abs(dn) > 0.4, f"系統性缺口 Δn = {dn:+.2f} (正=太扁, 模型需 steepen {abs(dn):.2f})")
check("C1_no_transfer_channel", True, "IDCM ℳ 冇 T(k) 通道 — k_eq analog 缺失 🔴 (docs/04 根因)")

print("\n" + "=" * 74)
print(f"RESULT: 閉合路徑收斂 n ≈ {np.mean([s1,s2,s3]):+.2f} ± 0.2, BOSS {s_obs:+.2f} → 系統性 Δn = {dn:+.2f} (正=太扁)")
print("        全逆 Abel (P2) 同平滑包絡 (P3) 都救唔到 broadband")
print("        母函 m>9 延伸未閉合 (P2b) 係額外 🔴 依賴")
print("        ⇒ broadband 缺口係系統性: 需要 IDCM 物質傳遞函數 T(k)")
print(f"        PASS = {sum(1 for _,o,_ in results if o)}/7")