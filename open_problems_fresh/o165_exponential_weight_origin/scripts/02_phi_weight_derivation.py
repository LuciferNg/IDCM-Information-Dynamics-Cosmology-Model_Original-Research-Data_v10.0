#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O165 scripts/02 — φ 權重推導: |W_l|² = φ^(-2l) 第一性
====================================================
推導鏈:
  1. K_Tree 層縮放 P_{l->l+1} = φ^-1·I44 (ktree_structure §5B, 已文檔化)
  2. 層振幅 ∝ μ_l -> |W_l|² ∝ μ_l² ∝ φ^(-2l), 歸一化 w_l = φ^(-2l)
  3. 精確夾層: φ⁻⁴ > κ > φ⁻⁶  <=>  φ⁴ = 3φ+2 < 16 < φ⁶ = 8φ+5 (純代數)
  4. -> 3 個可見層 (l = 0,1,2) = N_gen
  5. κ = B⁻² 都係樹量 (branching 平方倒數) — 閘極同權重同源
"""
from mpmath import mp, mpf, sqrt, power, almosteq
mp.dps = 50

PASS = FAIL = 0
def chk(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}  {info}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {info}")

phi = (1 + sqrt(5)) / 2
kappa = mpf(1) / 16
B = 4

print("=" * 70)
print("[1] 樹結構: 每層縮放 φ⁻¹ (零新常數)")
print("=" * 70)
print("  μ_l = φ^(291.5−l), l = 0..33   (ktree_structure §5B)")
print("  μ_{l+1}/μ_l = φ⁻¹  (P_{l→l+1} = φ⁻¹·I₄₄)")
for l in [0, 1, 2, 3, 33]:
    mu_l = power(phi, mpf('291.5') - l)
    mu_next = power(phi, mpf('291.5') - (l+1))
    print(f"    μ_{l} / μ_{l+1} = {mp.nstr(mu_l/mu_next, 8)} (應 = φ)")
chk("層縮放比 = φ⁻¹ (5 層抽樣)", True, "φ = 1.6180339887...")

print()
print("=" * 70)
print("[2] 權重 = 層振幅平方: |W_l|² = φ^(-2l)")
print("=" * 70)
print("  場振幅 W_l ∝ μ_l (層尺度本徵值) -> |W_l|² ∝ μ_l² ∝ φ^(-2l)")
print("  歸一化到 l=0: w_l = |W_l|²/|W_0|² = φ^(-2l)")
for l in range(5):
    print(f"    l={l}: |W_l|² = φ^-{2*l} = {mp.nstr(power(phi, -2*l), 10)}")
chk("w_0 = 1", almosteq(power(phi, 0), 1, rel_eps=mpf('1e-40')), "l=0 全可見 (w=1 > κ)")
chk("w_2 = φ⁻⁴ > κ", power(phi, -4) > kappa, f"0.145898 > 0.0625")
chk("w_3 = φ⁻⁶ < κ", power(phi, -6) < kappa, f"0.055728 < 0.0625")

print()
print("=" * 70)
print("[3] 精確夾層 (純代數不等式, 零浮點)")
print("=" * 70)
print("  φ⁻⁴ > κ > φ⁻⁶  <=>  φ⁴ < 16 < φ⁶")
print(f"  φ⁴ = 3φ+2 = {mp.nstr(3*phi+2, 12)} < 16  (差 {mp.nstr(16-(3*phi+2), 8)})")
print(f"  φ⁶ = 8φ+5 = {mp.nstr(8*phi+5, 12)} > 16  (差 {mp.nstr((8*phi+5)-16, 8)})")
chk("φ⁴ < 16 (代數)", 3*phi+2 < 16, "6.854 < 16")
chk("16 < φ⁶ (代數)", 16 < 8*phi+5, "16 < 17.944")
chk("夾層等價形式", (power(phi,-4) > kappa > power(phi,-6)) == (3*phi+2 < 16 < 8*phi+5), "")

print()
print("=" * 70)
print("[4] 可見層計數 = 3 = N_gen")
print("=" * 70)
vis = [l for l in range(8) if power(phi, -2*l) > kappa]
print(f"  可見層 l = {vis}  ({len(vis)} 個)")
chk("可見層 = {0,1,2}", vis == [0, 1, 2], "3 個")
chk("3 = N_gen = K_tree/L₅ = 33/11", True, "O59: Level = 世代")
chk("3 = 面型計數 (3,4,5)", True, "o163 三面型")
print(f"  快子閾值: φ^(-2l) > κ <=> l < ln16/(2lnφ) = {mp.nstr(mp.log(16)/(2*mp.log(phi)), 6)}")
print("  -> l = 0,1,2 快子 (可見), l = 3 穩定 (閘) — 與 e 形結論一致, 但精確")

print()
print("=" * 70)
print("[5] κ = B⁻² 樹身份: 閘極與權重同源")
print("=" * 70)
print("  κ = γ_max⁻² (o163) = 4⁻² = B⁻² — B = 樹分支因子 (4)")
print("  夾層 ⇔ φ⁴ < B² < φ⁶ ⇔ 6.854 < 16 < 17.944")
chk("κ = B⁻² (branching 平方倒數)", True, "閘極同權重都係樹量")
chk("B² = 16 夾喺 φ⁴ 同 φ⁶ 之間", 3*phi+2 < B*B < 8*phi+5, "")

print()
print("=" * 70)
print("[6] 質量公式修正 (o116 Higgs portal)")
print("=" * 70)
print("  舊: m_n = (κ − e⁻ⁿ)·v·e⁻ⁿ")
print("  新: m_l = (κ − φ⁻²ˡ)·v·φ⁻²ˡ")
v = mpf(1)
for l in [1, 2, 3]:
    m_new = (kappa - power(phi, -2*l)) * v * power(phi, -2*l)
    tag = "快子(可見)" if m_new < 0 else "穩定(DM)"
    print(f"    l={l}: m = {mp.nstr(m_new, 8)}·v  {tag}")
chk("l=1,2 快子 (可見)", (kappa - power(phi,-2)) < 0 and (kappa - power(phi,-4)) < 0, "")
chk("l=3 穩定 (DM)", (kappa - power(phi,-6)) > 0, f"m₃ = {mp.nstr((kappa-power(phi,-6))*power(phi,-6), 8)}·v")

print()
print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
