#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 57 — sector 解析 resultant + F₅ 收斂點檢驗
==============================================================
目標: (1) R(P_odd/P_even, P_T̂ⁿ) — resultant 細分到 sector 層面
      (2) P_odd(1), P_even(1), P_odd(μ²) 等 sector 求值
      (3) F₅ 收斂點: k-ladder / resultant / tanβ 分母共享 F₅ 嘅唯一性
"""
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def chk(name, val, target, tol, note=""):
    global PASS, FAIL
    val_f = float(val); tgt = float(target)
    dev = abs(val_f-tgt)/abs(tgt)*100 if abs(tgt) > 1e-30 else abs(val_f-tgt)*100
    ok = abs(val_f - tgt) <= tol * max(1.0, abs(tgt)) if abs(tgt) > 1e-30 else abs(val_f) <= tol
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val_f:.9f}  (dev {dev:+.4f}%) {note}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val_f:.9f} vs {tgt}  (dev {dev:+.4f}%) {note}")

N_d, N_gen, B, K_tree, mu2 = 44, 3, 4, 33, 2.0
T = mp.matrix([[1, 1], [1, 0]])
def Tn(n):
    M = mp.matrix([[1, 0], [0, 1]])
    for _ in range(n):
        M = M * T
    return M
L, F = {}, {}
for n in range(1, 16):
    M = Tn(n)
    L[n] = float(mp.nint(M[0,0]+M[1,1]))
    F[n] = float(mp.nint(M[0,1]))

gams = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]
odd  = [gams[k] for k in range(0, 88, 2)]
even = [gams[k] for k in range(1, 88, 2)]

def P_sec(sec, x):
    s = sum(mp.log(abs(x-g)) for g in sec)
    sign = -1 if sum(1 for g in sec if x-g < 0) % 2 else 1
    return sign*mp.e**s

def R_sec(sec, n):
    s = sum(mp.log(abs(g*g - L[n]*g + 1)) for g in sec)
    sign = -1 if sum(1 for g in sec if g*g-L[n]*g+1 < 0) % 2 else 1
    return sign*mp.e**s

print("=" * 72)
print("C1. ★★ sector resultant: R_odd × R_even = R_full")
print("=" * 72)
for n in [1, 2, 3, 4, 5, 10]:
    ro = R_sec(odd, n); re = R_sec(even, n)
    rf = ro*re
    print(f"  n={n:2d}: R_odd = {float(ro):+12.6f}   R_even = {float(re):+12.6f}   R_full = {float(rf):+.6e}")

print()
print("=" * 72)
print("C2. sector 特徵多項式求值: P_odd(1), P_even(1), P_odd(μ²)...")
print("=" * 72)
po1 = P_sec(odd, 1); pe1 = P_sec(even, 1)
chk("★ P_odd(1) × P_even(1) = P_Δ(1) = −3 = −N_gen", po1*pe1, -3, 1e-9)
print(f"  P_odd(1)  = {float(po1):+.9f}")
print(f"  P_even(1) = {float(pe1):+.9f}")
po2 = P_sec(odd, 2)   # μ²
pe2 = P_sec(even, 2)
print(f"  P_odd(2)  = {float(po2):+.9f}   (P_even(2) = 0 — γ₄₄ ∈ even)")
po4 = P_sec(odd, 4)   # B = Nyquist
pe4 = P_sec(even, 4)
print(f"  P_odd(4)  = {float(po4):+.9f}   (P_even(4) = 0 — γ₈₈ ∈ even)")
po5 = P_sec(odd, 5); pe5 = P_sec(even, 5)
print(f"  P_odd(5)  = {float(po5):+.9f}   P_even(5) = {float(pe5):+.9f}  (F₅ = 5!)")

print()
print("=" * 72)
print("C3. sector resultant 掃描 n=1..11 — 細小整數命中")
print("=" * 72)
for n in range(1, 12):
    ro = R_sec(odd, n); re = R_sec(even, n)
    rv = [("odd", float(ro)), ("even", float(re))]
    for nm, v in rv:
        tag = ""
        if abs(v) < 100 and abs(v - round(v)) < 1e-6:
            tag = f" ★整數 {round(v)}"
        if abs(v) < 100:
            print(f"  R_{nm}(P_T̂^{n}) = {v:+.6f}{tag}")

print()
print("=" * 72)
print("C4. F₅ 收斂點唯一性檢驗")
print("=" * 72)
chk("k-ladder g₃ 分子索引 = F₅ (k=3: F_{k+2}=F₅)", F[3+2], 5, 1e-9, "V_ub 閉式")
chk("R(P_Δ,P_T̂²) = −F₅", R_sec(gams, 2), -5, 1e-6, "resultant 黏合")
chk("tanβ 分母 = Tr(T̂⁵), 索引 5 = F₅", L[5], 11, 1e-9)
chk("tanβ 分子樹索引 10 = 2F₅", 2*F[5], 10, 1e-9)
chk("43 = B·L₅−1 = 2F₅+K_tree", B*L[5]-1, 2*F[5]+K_tree, 1e-9)
chk("F₁₁ = F₆·L₅+1 = 88+1", F[11], F[6]*L[5]+1, 1e-9, "chain 跡 2F₁₁ = 2F₆L₅+μ²")
# 唯一性: R(P_Δ,P_T̂ⁿ) = −5 只有 n=2
count5 = sum(1 for n in range(1, 12) if abs(float(R_sec(gams, n)) + 5) < 1e-6)
chk("R = −F₅ 唯一喺 n=2", count5, 1, 0)
count3 = sum(1 for n in range(1, 12) if abs(float(R_sec(gams, n)) + 3) < 1e-6)
chk("R = −N_gen 唯一喺 n=3", count3, 1, 0)

print()
print("=" * 72)
print("C5. tanβ 分子經 F₅ 收斂點重組")
print("=" * 72)
chk("TrΔ = 2F₁₁ = 2(F₆L₅+1) = 2F₆L₅+μ²", 2*F[11], 2*F[6]*L[5]+mu2, 1e-9,
    "← 176+2: det_even + det_odd")
chk("tanβ = (2F₆L₅ + L₅² + 2+μ²)/L₅ = (176+121+4)/11", (2*F[6]*L[5]+L[5]**2+2+mu2)/L[5], 301/11, 1e-9)
chk("tanβ = 2F₆ + L₅ + (2+μ²)/L₅ = 16+11+4/11", 2*F[6]+L[5]+(2+mu2)/L[5], 301/11, 1e-9,
    "← 世界 2F₆ + 樹 L₅ + 邊界 4/L₅ 三層分解!")

print()
print("=" * 72)
print("C6. 投影定理 v6 陳述 (F₅ 收斂)")
print("=" * 72)
print("  F₅ = 5 收斂點: k-ladder (g₃ 分子) ∧ resultant (R(P_Δ,P_T̂²)=−F₅) ∧")
print("                tanβ (分母索引 5, 分子索引 2F₅=10) ∧ 43 = 2F₅+K_tree")
print("  tanβ 三層分解: tanβ = 2F₆ + L₅ + (2+μ²)/L₅ — 世界/樹/邊界")
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
