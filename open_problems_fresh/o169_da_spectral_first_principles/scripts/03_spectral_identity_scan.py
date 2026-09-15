#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/03 — E(ℓ) 擬合常數嘅譜身份搜尋 + 零參數候選 χ² 檢定
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2
pi = mp.pi
inv = 1/phi

N = 44
gam = [4*mp.sin(n*pi/88)**2 for n in range(1, N+1)]
sec = [1/mp.cos(n*pi/88) for n in range(1, N+1)]

def dev(x, y): return float((x-y)/y*100)

print("="*72)
print("O169/03 — 譜身份搜尋")
print("="*72)

# 由 scripts/02 C5 嘅兩參數擬合
a_fit = mp.mpf('1.2374181'); b_fit = mp.mpf('-0.24313981')
slope = a_fit + b_fit
const = 1 + b_fit/2
print(f"\n兩參數擬合 (D_M 六點):  a = {mp.nstr(a_fit,10)}   b = {mp.nstr(b_fit,10)}")
print(f"  → E(ℓ) = {mp.nstr(const,10)} + {mp.nstr(slope,10)}·ℓ")
print(f"  a vs 2φ⁻¹ = {mp.nstr(2*inv,10)}  dev {dev(a_fit,2*inv):+.4f}%")

print("\n--- 常數項身份 ---")
sec22 = mp.fsum(sec[:22])/22
print(f"  ⟨sec(πn/88)⟩_{{n=1..22}} = {mp.nstr(sec22, 12)}")
print(f"  const = 1 + b/2        = {mp.nstr(const, 12)}   dev {dev(sec22, const):+.4f}%")
for Nn in [11, 22, 27, 33, 44]:
    v = mp.fsum(sec[:Nn])/Nn
    print(f"  ⟨sec⟩_{{1..{Nn}}} = {mp.nstr(v,12)}  dev vs const {dev(v,const):+.4f}%")

print("\n--- 斜率身份 ---")
print(f"  slope = a+b = {mp.nstr(slope,12)}   vs 1: dev {dev(slope, mp.mpf(1)):+.4f}%")
print(f"  2φ⁻¹ − 2φ⁻²/π = {mp.nstr(2*inv - 2*inv**2/pi, 12)}")
print(f"  44/45 = {mp.nstr(mp.mpf(44)/45,12)}, 89/90 = {mp.nstr(mp.mpf(89)/90,12)}")
print(f"  Σγ/90 = {mp.nstr(mp.fsum(gam)/90,12)}")

print("\n--- b 結構身份 ---")
cands_b = {
    "−2φ⁻²/π": -2*inv**2/pi,
    "−(2φ⁻¹)²/2π": -(2*inv)**2/(2*pi),
    "−φ⁻³": -inv**3,
    "−(√5−2)": -(mp.sqrt(5)-2),
    "−4/(9φ²)": -4/(9*phi**2),
    "−(2−φ)·2/π": -(2-phi)*2/pi,
    "−1/(2φ+1.53)": -1/(2*phi+mp.mpf('1.53')),
}
for k, v in cands_b.items():
    print(f"  {k:<14} = {mp.nstr(v,12)}   dev vs b_fit: {dev(v,b_fit):+.4f}%")

print("\n--- C (純半整數形式 δ=C(ℓ−½), D_M 加權擬合) ---")
Cb = mp.mpf('-0.24256')
cands_C = {
    "−2φ⁻²/π": -2*inv**2/pi,
    "−φ⁻³": -inv**3,
    "−4/(9φ²)": -4/(9*phi**2),
    "−1/(2φ²+1)": -1/(2*phi**2+1),
    "−φ⁻²·2/π": -inv**2*2/pi,
    "−(2−φ)/π·2": -(2-phi)/pi*2,
}
for k, v in cands_C.items():
    print(f"  {k:<14} = {mp.nstr(v,12)}   dev vs Cb: {dev(v,Cb):+.4f}%")

print("\n--- 譜部分和身份 (核對) ---")
print(f"  Σγ_{{1..22}} = {mp.nstr(mp.fsum(gam[:22]),12)}   (= N_d?)")
print(f"  Σγ = {mp.nstr(mp.fsum(gam),12)}, even = {mp.nstr(mp.fsum(gam[1::2]),12)}, odd = {mp.nstr(mp.fsum(gam[0::2]),12)}")
print(f"  Σ_{{1..44}}γ² = {mp.nstr(mp.fsum(g*g for g in gam),12)}")
print(f"  Σ sec·γ (n≤27) = {mp.nstr(mp.fsum(sec[i]*gam[i] for i in range(27)),12)}")
