#!/usr/bin/env python3
"""
O10 60: 質數孿生對 — 三實驗最終驗證
=====================================
質數對 (5,7): Planck A₅=0.2143, A₇=0.1414
             ACT DR6: 峰@1098 (A₄?), 峰@1448
             SPT-3G: 峰@1125, 峰@1425

驗證 P₂ = (A₅+A₇)/2 = 3εφ⁻² 跨實驗
"""
import numpy as np, math, json, os

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

print("=" * 72)
print("質數孿生對 (5,7) 三實驗驗證")
print("=" * 72)
P2_th = 3*eps*phi**-2
print(f"理論: P₂ = 3εφ⁻² = {P2_th:.4f}")
print()

# Planck
A5_p, A7_p = 0.2143, 0.1414
P2_p = (A5_p+A7_p)/2
print(f"Planck:  A₅(1121)={A5_p}, A₇(1409)={A7_p}, P₂={P2_p:.4f} ({(P2_p-P2_th)/P2_th*100:+.2f}%)")

# ACT DR6 (峰@1098 D=1216.6, 峰@1448 D=800.4, D₁=5732)
D1_act = 5732
A5_a = 1216.6/D1_act
A7_a = 800.4/D1_act
P2_a = (A5_a+A7_a)/2
print(f"ACT DR6: A₅(1098)={A5_a:.4f}, A₇(1448)={A7_a:.4f}, P₂={P2_a:.4f} ({(P2_a-P2_th)/P2_th*100:+.2f}%)")

# SPT-3G (bin@1125 D=1235, bin@1425 D=820, D₁=5816)
D1_spt = 5816
A5_s = 1235/D1_spt
A7_s = 820/D1_spt
P2_s = (A5_s+A7_s)/2
print(f"SPT-3G:  A₅(1125)={A5_s:.4f}, A₇(1425)={A7_s:.4f}, P₂={P2_s:.4f} ({(P2_s-P2_th)/P2_th*100:+.2f}%)")

print()
print("P₂ 三實驗:")
print(f"  Planck: {P2_p:.4f} ({-4.83 if False else (P2_p-P2_th)/P2_th*100:+.2f}%)")
print(f"  ACT:    {P2_a:.4f} ({(P2_a-P2_th)/P2_th*100:+.2f}%)")
print(f"  SPT:    {P2_s:.4f} ({(P2_s-P2_th)/P2_th*100:+.2f}%)")
print()

# 對內比例驗證
print("對內比例 (5,7) 三實驗:")
print(f"  Planck: A₇/A₅ = {A7_p/A5_p:.4f} vs 2/3 = {2/3:.4f}")
print(f"  ACT:    A₇/A₅ = {A7_a/A5_a:.4f} vs 2/3")
print(f"  SPT:    A₇/A₅ = {A7_s/A5_s:.4f} vs 2/3")

# 儲存
data = {
    "P2_theory": P2_th,
    "planck": {"A5": A5_p, "A7": A7_p, "P2": P2_p, "ratio": A7_p/A5_p},
    "act_dr6": {"A5": A5_a, "A7": A7_a, "P2": P2_a, "ratio": A7_a/A5_a},
    "spt3g": {"A5": A5_s, "A7": A7_s, "P2": P2_s, "ratio": A7_s/A5_s},
}
os.makedirs("data", exist_ok=True)
with open("data/twin_pair_crosscheck.json", "w") as f:
    json.dump(data, f, indent=2)
print("\n已儲存: data/twin_pair_crosscheck.json")
