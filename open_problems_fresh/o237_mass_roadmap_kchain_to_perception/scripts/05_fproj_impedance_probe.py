#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — R3 補試: O145 複阻抗 Z(G8, n) 對 A5 mode (docs/01 指定候選)
================================================================================
O145: Z(G, n) = Σ_{a∈G} exp(2πi·n·a/88)·v₂(a)  — 純 operator identity (零新常數)
C_e = Σv₂(G8)/|G8| = 18/5 已由此家族生成。
本 script: Z(G8, n), Z(G6, n), Z(G9, n), Z(G12, n) 對 A5 mode n ∈ {1,2,3,4,5,7,9,11}
之實部/虛部/模，盲測 C_f(n) 有冇對應 (唔 fit，用 operator identity 直接定義)。
"""
import math, cmath
import numpy as np

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = abs(float(got)-float(exp)) < tol
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2; c += 1
    return c

G6 = {22, 44}
G8 = {8, 16, 24, 32, 40}
G9 = set(range(1, 19, 2))
G12 = set(range(1, 45)) - G6 - G8 - G9

def Z(G, n):
    return sum(cmath.exp(2j*math.pi*n*a/88)*v2(a) for a in G)

M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
def gam(n): return 4*math.sin(math.pi*n/88)**2
CF = {p: MASS[p]/(M0*gam(MODES[p])) for p in MASS}

print("="*88)
print("O237 U2 R3 — O145 複阻抗 Z(G,n) vs A5 C_f")
print("="*88)

print("\n[1] Z(G8,n) 實部/模 對 A5 mode (G8 係 C_e=18/5 嘅生成扇區):")
print(f"    {'n':>3} {'C_f':>10} {'Re Z8':>10} {'Im Z8':>10} {'|Z8|':>10} {'ReZ8/Cf':>10}")
rel = []
for p, n in MODES.items():
    z = Z(G8, n)
    rel.append((abs(z.real)/CF[p] if z.real != 0 else float('inf'), n, p))
    print(f"    {n:>3} {CF[p]:>10.4f} {z.real:>10.4f} {z.imag:>10.4f} {abs(z):>10.4f} {z.real/CF[p]:>10.4f}")
# 檢驗: |ReZ8|/C_f 係咪常數 (即 C_f ∝ |Re Z(G8,n)|)
r_vals = [r for r,_,_ in rel if r != float('inf')]
print(f"    |ReZ8|/Cf spread = {max(r_vals)/min(r_vals):.3f}× (常數 = 結構)")
ck("Z(G8,n) 實部 ∝ C_f 唔成立 (spread > 1.1)", max(r_vals)/min(r_vals) > 1.1, True)

print("\n[2] 全部扇區 阻抗模 (Z6, Z8, Z9, Z12) vs C_f 嘅相關性:")
mods = {"|Z8|": [], "|Z12|": [], "ReZ8": [], "ReZ12": []}
corrs = {}
for p, n in MODES.items():
    z8 = Z(G8, n); z12 = Z(G12, n); z6 = Z(G6, n); z9 = Z(G9, n)
    for key, val in [("|Z8|", abs(z8)), ("|Z12|", abs(z12)), ("ReZ8", z8.real), ("ReZ12", z12.real)]:
        mods.setdefault(key, []).append(val)
    print(f"    n={n:>2} C_f={CF[p]:>10.4f}  |Z8|={abs(z8):>8.4f} ReZ8={z8.real:>8.3f} |Z12|={abs(z12):>8.3f} |Z6|={abs(z6):>8.3f} |Z9|={abs(z9):>8.3f}")
for key, vals in mods.items():
    c = np.corrcoef(vals, list(CF.values()))[0,1]
    corrs[key] = c
    print(f"    corr(C_f, {key}) = {c:+.4f}")
best_c = max(abs(v) for v in corrs.values())
ck("全部扇區阻抗/模嘅 |corr| < 0.9 (冇線性結構)", best_c < 0.9, True)

print("\n[3] 判定")
print(f"""  O145 複阻抗家族 (Z(G8/G6/G9/G12, n)) 對 A5 C_f **冇線性/比例結構**:
  - Re Z(G8,n)/C_f spread = {max(r_vals)/min(r_vals):.3f}×
  - 全扇區相關 max |corr| = {best_c:.4f}
  ⟹ R3 複阻抗家族亦為負。C_e = Σv₂(G8)/|G8| 仍係唯一由 2-adic 扇區生成嘅 F_proj。
  下一步唯一剩餘候選: R1b (κ 非對角修正) —— 但 κ_ijk=18·I₉ 係 CSSG-v3 定理閉合,
  非對角修正需要新幾何輸入 (O206 第十輪已定: C_f 生成器開放, 等新幾何)。
  U2 總結維持 🔴 (docs/04 一致)。""")

print("\n" + "="*88)
print(f"U2 R3 round: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*88)
print("PASS" if not FAIL else "FAIL")