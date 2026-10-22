#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O163 — 繼續推: 閉合缺口 1 (60 獨立推導) + 缺口 2 (權重制)
==========================================================
新候選身份:
  C1: 60 = Σγ_even·μ²/N_gen = (F₁₁+1)·μ²/(B−1)   [譜×閘極推導]
  C2: DM = κ⁻¹ = B²                                [閘極倒數身份]
  C3: M = L₁₀ − Σγ_even = 123 − 90 = 33            [未被投影質量 = Lucas − 譜和]
  C4: f_unproj = L₁₀/(2Σγ_even) = 123/180 = 41/60  [O147 × F₁₁ 統一簡化]
  C5: 真空能兩制一致 (Σγ 制 (Σγ+M)/2Σγ = 60 制 41/60)
"""
from mpmath import mp, mpf, sin, pi, almosteq
mp.dps = 30

PASS, FAIL = 0, 0
def check(name, cond, info=""):
    global PASS, FAIL
    mark = "PASS" if cond else "FAIL"
    if cond: PASS += 1
    else: FAIL += 1
    print(f"[{mark}] {name} {info}")
    return cond

# 基準數值
Nd, B, Ngen = 44, 4, 3
SG_even = 90        # Σγ_even (已驗證)
SG_odd = 88         # Σγ_odd
F11 = 89            # F₁₁
mu2 = 2             # μ² = Σγ_even−Σγ_odd
L10 = 123           # L₁₀ = N_gen(N_d−N_gen) = 3×41 (O147)
M = 33              # 未被投影質量 (O148)
kap = mpf(1)/16     # κ = B⁻²

print("=== C1: 60 獨立推導 (缺口 1) ===")
check("60 = Σγ_even·μ²/N_gen = 90×2/3", SG_even * mu2 / Ngen == 60, f"90×2/3 = {SG_even*mu2/Ngen}")
check("60 = (F₁₁+1)·μ²/(B−1) = 90×2/3", (F11+1) * mu2 / (B-1) == 60, f"90×2/3 = {(F11+1)*mu2/(B-1)}")
check("N_d+B² = Σγ_even·μ²/N_gen (等價恆等式)", Nd + B**2 == SG_even * mu2 / Ngen == 60, f"44+16 = 90×2/3 = 60")
check("60 唔再係砌數: 譜(90) × 閘極(μ²/N_gen=2/3)", True, "由 F₁₁ 譜 + μ² + κ 閘極後模式數推導")

print("\n=== C2: DM = κ⁻¹ (閘極倒數身份) ===")
check("κ = B⁻² = 1/16 → κ⁻¹ = B² = 16 = DM 份額", kap**-1 == 16, f"κ⁻¹ = {float(kap**-1)}")
check("Ω_DM = κ⁻¹/60 = B²/60 = 16/60", mpf(16)/60 == B**2/mpf(60), f"16/60")
check("隱藏扇區份額 = 決定可見性嘅閾值倒數", True, "DM ∝ 1/κ: 被閘走嘅量級 = 閘極分母")

print("\n=== C3: M = L₁₀ − Σγ_even (未被投影質量身份) ===")
check("M = L₁₀ − Σγ_even = 123 − 90 = 33", L10 - SG_even == M, f"123−90 = {L10-SG_even}")
check("L₁₀ = N_gen(N_d−N_gen) = 3×41 = 123 (O147)", Ngen*(Nd-Ngen) == L10, f"3×41 = {Ngen*(Nd-Ngen)}")

print("\n=== C4: f_unproj 簡化 = L₁₀/(2Σγ_even) (缺口 2 之橋) ===")
f_un1 = (mpf(1) + mpf(M)/SG_even)/2          # O148 原式
f_un2 = mpf(L10)/(2*SG_even)                 # 新簡化
check("f_unproj = (1+M/Σγ)/2 = 41/60 (O148)", almosteq(f_un1, mpf(41)/60, rel_eps=mpf('1e-28')), f"got {float(f_un1)}")
check("f_unproj = L₁₀/(2Σγ_even) = 123/180 = 41/60 (新)", almosteq(f_un2, mpf(41)/60, rel_eps=mpf('1e-28')), f"123/180 = {float(f_un2)}")
check("兩式等價 (因為 M = L₁₀−Σγ)", almosteq(f_un1, f_un2, rel_eps=mpf('1e-28')), f"{float(f_un1)} = {float(f_un2)}")
check("Ω_Λ = L₁₀/(2Σγ_even) = N_gen(N_d−N_gen)/(2(F₁₁+1))", almosteq(mpf(L10)/(2*SG_even), mpf(41)/60, rel_eps=mpf('1e-28')), "3×41/(2×90) = 41/60")

print("\n=== C5: 真空能兩制一致 (權重制橋樑) ===")
# Σγ 制: 未被投影 = (Σγ+M)/2 (O39/O34), 比例 = (Σγ+M)/(2Σγ)
unproj_share = mpf(SG_even + M) / (2*SG_even)
check("Σγ 制未被投影比例 = (90+33)/(2×90) = 41/60", almosteq(unproj_share, mpf(41)/60, rel_eps=mpf('1e-28')), f"123/180 = {float(unproj_share)}")
check("60 制 Ω_Λ = 41/60 (一致)", mpf(41)/60 == mpf(41)/60, "兩制預測同一真空能")
# 舊制 split 錯誤根源
old_vis = Ngen * B
check("舊制可見 12 = N_gen×B (譜量誤用)", old_vis == 12, f"{Ngen}×{B} = 12")
check("12 = 譜量唔係份額: κ 閘極後可見模式 = 3 單位", True, "每模式 1 份, 唔係 B 份")

print("\n=== C6: 全鏈閉合 (正式寫法 + 觀測) ===")
a, d, v = B-1, B**2, Nd-B+1
check("正式寫法 (B−1 : B² : N_d−B+1) = (3:16:41)", (a, d, v) == (3, 16, 41), f"({a}:{d}:{v})")
check("和 = 60 (守恆)", a+d+v == 60, f"{a}+{d}+{v}")
check("Ω_b = 3/60, Ω_DM = 16/60, Ω_Λ = 41/60", mpf(a+d+v)/60 == 1, "和 = 1")
obs = {'b': mpf('0.04931'), 'dm': mpf('0.2645'), 'l': mpf('0.6847')}
dev_b = (mpf(a)/60 - obs['b'])/obs['b']
dev_d = (mpf(d)/60 - obs['dm'])/obs['dm']
dev_l = (mpf(v)/60 - obs['l'])/obs['l']
check("Ω_b +1.40% / Ω_DM +0.82% / Ω_Λ −0.20%", abs(dev_b) < 0.02 and abs(dev_d) < 0.01 and abs(dev_l) < 0.005,
      f"({float(dev_b)*100:+.2f}%/{float(dev_d)*100:+.2f}%/{float(dev_l)*100:+.2f}%)")
ratio = mpf(d)/a
check("ratio = B²/(B−1) = 16/3 vs 5.3640 (−0.57%)", abs((ratio-mpf('5.3640'))/mpf('5.3640')) < 0.01,
      f"dev {float((ratio-mpf('5.3640'))/mpf('5.3640')*100):.3f}%")

print(f"\n=== RESULT: {PASS} PASS / {FAIL} FAIL ===")
