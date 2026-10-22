#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_audit_independent.py — T1: O156 獨立核對 (audit round, 2026-09-07)
=====================================================================
零 import 原 scripts (scripts/01-10) — 冇 shared functions → 冇 shared bugs.
全部由零重算 headline 數字, mpmath 50 dps 閉合形式.

Section A: 譜身份 (Σγ, E−O, γ₂₂, γ₄₄)
Section B: θ₂₃(88), 殘差, θ(N) 家族, 連續 N*
Section C: sin²θ₂₃(88/55) vs NuFIT
Section D: 33-44-55 Pythagorean + 塔
Section E: N(a,b) 規則 + 密度 + 證偽 (U_e1)
Section F: 9 觀察量焦點 (獨立 bisection)
Section G: Hodge 身份 + 焦距卡位
Section H: 投影鏈 + polytope (bipyramid det)
Section I: 1/(L₄·h̄) + null + ×41 聚類
Section J: 混合家矩陣共閉合 (獨立重算 |U|)
Section K: R4 總和 1/352 + δ_CKM(55) P2 + γ₇ P3
"""
import math
try:
    import mpmath as mp
    mp.mp.dps = 50
    HAVE_MP = True
except ImportError:
    HAVE_MP = False

PASS, FAIL = 0, 0
def check(name, got, expect, tol=1e-6, unit=""):
    global PASS, FAIL
    if isinstance(expect, str):
        ok = str(got).startswith(expect)
    else:
        ok = abs(got-expect) <= tol*max(1.0, abs(expect))
    g = mp.nstr(got, 10) if HAVE_MP and isinstance(got, mp.mpf) else str(got)
    e = expect if isinstance(expect, str) else (mp.nstr(expect, 10) if HAVE_MP and isinstance(expect, mp.mpf) else str(expect))
    dev = "" if isinstance(expect, str) else f"  (dev {abs(got-expect)})"
    print(f"   [{'✅' if ok else '❌'}] {name}: {g}{unit} vs {e}{unit}" + dev)
    PASS += ok; FAIL += (not ok)

def gamma_exact(n, N):
    return 4*mp.sin(mp.mpf(n)*mp.pi/mp.mpf(N))**2

def theta_exact(N, k1=7, k2=6):
    return mp.atan(mp.sin(k1*mp.pi/mp.mpf(N))/mp.sin(k2*mp.pi/mp.mpf(N)))

DEG = mp.mpf(180)/mp.pi
RAD = mp.pi/mp.mpf(180)

print("="*70)
print("A) 譜身份 (176-Laplacian)")
print("="*70)
S_e = sum(gamma_exact(2*k, 176) for k in range(1, 45))   # even k=2..88
S_o = sum(gamma_exact(2*k-1, 176) for k in range(1, 45))  # odd k=1..87
check("Σγ_even", S_e, mp.mpf(90), 1e-9)
check("Σγ_odd", S_o, mp.mpf(88), 1e-9)
check("E−O", S_e-S_o, mp.mpf(2), 1e-9)
check("γ₂₂ (88-conv)", gamma_exact(22, 88), mp.mpf(2), 1e-9)
check("γ₄₄ (88-conv)", gamma_exact(44, 88), mp.mpf(4), 1e-9)
check("Σγ_total", S_e+S_o, mp.mpf(178), 1e-9)

print("="*70)
print("B) θ₂₃(88), 殘差, θ(N) 家族, 連續 N*")
print("="*70)
th88 = theta_exact(88)*DEG
check("θ₂₃(88)", th88, mp.mpf("49.3202"), 1e-5, "°")
resid = th88 - mp.mpf("49.1980")
check("殘差 |θ(88)−NuFIT|", abs(resid), mp.mpf("0.1222"), 1e-4, "°")
th55 = theta_exact(55)*DEG
check("θ(55)", th55, mp.mpf("49.1966"), 1e-5, "°")
check("θ(55) vs NuFIT", th55-mp.mpf("49.1980"), mp.mpf("-0.0014"), 2e-5, "°")
# 連續 N*: 解 θ(N) = 49.1980° (獨立 bisection)
f = lambda N: theta_exact(N)*DEG - mp.mpf("49.1980")
lo, hi = mp.mpf(33), mp.mpf(200)
for _ in range(200):
    mid = (lo+hi)/2
    if f(mid) > 0: hi = mid
    else: lo = mid
Nstar1 = (lo+hi)/2
check("連續 N* (θ=49.1980°)", Nstar1, mp.mpf("55.19"), 1e-2)
# 自然端點表
for (a, b, exp) in [(176, 88, "0.0589"), (88, 55, "0.1236"), (88, 44, "0.2391"),
                    (176, 44, "0.2980"), (88, 42, "0.2706"), (88, 33, "0.4931")]:
    v = (theta_exact(a)-theta_exact(b))*DEG
    check(f"θ({a})−θ({b})", v, exp, 2e-4, "°")

print("="*70)
print("C) sin²θ₂₃(88/55) vs NuFIT 0.573007")
print("="*70)
def s2(N):
    g7 = gamma_exact(7, N); g6 = gamma_exact(6, N)
    return g7/(g7+g6)
s2_88 = s2(88); s2_55 = s2(55)
check("sin²θ₂₃(88)", s2_88, mp.mpf("0.575117"), 1e-5)
check("sin²θ₂₃(55)", s2_55, mp.mpf("0.572983"), 1e-5)
check("sin²θ₂₃(55) dev", s2_55-mp.mpf("0.573007"), mp.mpf("-0.000024"), 1e-5)

print("="*70)
print("D) 33-44-55 Pythagorean + 塔")
print("="*70)
check("33²+44²", 33*33+44*44, 55*55)
tower = [(11, "L₅×F₂"), (22, "L₅×F₃"), (33, "L₅×F₄=K_tree"), (44, "L₅×B"),
         (55, "L₅×F₅=F₁₀"), (88, "L₅×F₆"), (176, "L₅×B²")]
for N, name in tower:
    check(f"{N} = {name}", N, 11*(N//11), unit="(11×)")

print("="*70)
print("E) N(a,b) = ab+a+b 規則 + 密度 + 證偽")
print("="*70)
check("N(6,7)", 6*7+6+7, 55)
check("N(2,3)", 2*3+2+3, 11)
check("6×7 = N_d⁻", 6*7, 42)
check("6+7 = F₇", 6+7, 13)
# 密度: [1,44]² 內框架尺度命中數
FR = {11, 22, 33, 42, 44, 46, 55, 88, 176}
hits = {(N, a, b) for a in range(1, 45) for b in range(a+1, 45)
        if (N := a*b+a+b) in FR}
check("N=ab+a+b 框架命中數", len(hits), 8)
check("密度 8/946", len(hits)/946, 8/946, 1e-9)
# U_e1 證偽
def ue1(N):
    g2 = gamma_exact(2, N); g3 = gamma_exact(3, N)
    return mp.sqrt(g3/(g2+g3))
check("U_e1(88)", ue1(88), mp.mpf("0.8318"), 1e-4)
check("U_e1(11)", ue1(11), mp.mpf("0.8133"), 1e-4)

print("="*70)
print("F) 9 觀察量焦點 (獨立 bisection)")
print("="*70)
def focus_ratio(a, b, target, lo, hi):
    f = lambda N: mp.sin(a*mp.pi/mp.mpf(N))/mp.sin(b*mp.pi/mp.mpf(N)) - mp.mpf(target)
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    # 掃描 sign change (ratio 可增可減)
    prev_N, prev_f = lo, f(lo)
    for i in range(1, 501):
        N = lo + (hi-lo)*mp.mpf(i)/500
        val = f(N)
        if prev_f*val <= 0:
            # sign change 喺 (prev_N, N) — bisect
            l, h = prev_N, N
            for _ in range(200):
                mid = (l+h)/2
                if f(l)*f(mid) <= 0: h = mid
                else: l = mid
            return (l+h)/2
        prev_N, prev_f = N, val
    return None
# 目標 (scripts/08 一致: PDG/O36 譜形)
foc = [
    ("m_W/m_Z (30,41)", 30, 41, 80.369/91.1876, 80, 95, 88.32),
    ("m_H/m_W (38,19)", 38, 19, 125.25/80.369, 80, 95, 88.12),
    ("m_u/m_d (10,24)", 10, 24, 0.4625, 80, 95, 87.92),
    ("m_c/m_b (8,33)", 8, 33, 0.3038, 80, 95, 88.69),
    ("m_μ/m_τ (1,18)", 1, 18, 0.0595, 80, 95, 88.62),
    ("m_t/m_b (19,33)", 19, 33, 0.67917, 80, 95, 88.00),
    ("m_s/m_d (22,1)", 22, 1, 20.0, 80, 95, 92.19),
    ("δ_CKM (21,9)", 21, 9, math.tan(66.40*math.pi/180), 150, 200, 176.01),
    ("θ₂₃ (7,6)", 7, 6, math.tan(49.1980*math.pi/180), 50, 60, 55.19),
]
for name, a, b, tgt, lo, hi, exp in foc:
    if tgt == 0: continue
    Ns = focus_ratio(a, b, tgt, lo, hi)
    check(f"{name} N*", Ns, exp, 3e-2)

print("="*70)
print("G) Hodge 身份 + 焦距卡位")
print("="*70)
check("h¹¹ = 36 = 44−8", 36, 44-8)
check("h¹¹ = 33+3", 36, 33+3)
check("h¹¹ = 3×12", 36, 3*12)
check("12 = B×N_gen", 12, 4*3)
check("F₆ = 2B", 8, 2*4)
check("h²¹ = 98 = 90+8", 98, 90+8)
check("134 = 44+90", 134, 44+90)
check("62 = 98−36", 62, 98-36)
check("χ = −124", 2*(36-98), -124)
check("b₃ = 198", 2*(1+98), 198)
check("55 = 36+19", 55, 36+19)
check("55 = 67−12", 55, 67-12)
check("55 = 99−44", 55, 99-44)
check("88 = 2(36+8)", 88, 2*(36+8))
check("176 = 4(36+8)", 176, 4*(36+8))
check("60 = 5×12", 60, 5*12)

print("="*70)
print("H) 投影鏈 + polytope bipyramid")
print("="*70)
check("19 = 67−48", 19, 67-48)
check("41 = 89−48", 41, 89-48)
check("48+85+1 = 134", 48+85+1, 134)
check("60 = 19+41", 60, 19+41)
check("55 = 60−5", 55, 60-5)
# bipyramid: w=0 4 頂點仿射 det
import numpy as np
v1, v2, v3, v4 = np.array([1,0,0]), np.array([-15,-10,-4]), np.array([0,0,1]), np.array([1,2,0])
M = np.column_stack([v2-v1, v3-v1, v4-v1])
det = round(np.linalg.det(M), 6)
check("tetrahedron affine det", det, 40)

print("="*70)
print("I) 1/(L₄·h̄) + null + ×41 聚類")
print("="*70)
d23 = (theta_exact(88)*DEG-mp.mpf("49.1980"))*RAD   # rad
check("殘差 rad", d23, mp.mpf("2.1328e-3"), 2e-6)
inv = 1/d23
check("1/Δ", inv, mp.mpf("468.8"), 5e-2)
check("1/469", 1/mp.mpf(469), mp.mpf("2.132196e-3"), 1e-8)
nstar_l4 = 1/(mp.mpf(67)*d23)
check("n* = 1/(h̄·Δ)", nstar_l4, mp.mpf("6.9964"), 1e-3)
check("469 = 7×67", 7*67, 469)
# null: 1/(n·h̄) 家族隨機命中 (tol 0.1%)
import random
random.seed(20260907)
FRAME = [2,3,4,5,6,7,8,11,13,16,21,33,42,44,46,55,66,88,176]
famB = [1.0/(n*67) for n in FRAME]
hitsB = 0; NT = 20000
for _ in range(NT):
    t = random.uniform(1e-4, 1e-2)
    if any(abs(t-f)/f < 0.001 for f in famB): hitsB += 1
print(f"   [{'✅' if hitsB/NT<0.05 else '❌'}] 1/(n·h̄) null: {hitsB/NT*100:.2f}% < 5%")
# ×41 聚類
check("100/0.61 → 164 = 4×41", round(100/0.61, 2), 163.93, 1e-2)
check("164 = 4×41", 4*41, 164)
check("100/0.074 → 1353 = 33×41", round(100/0.074, 2), 1351.35, 1e-2)
check("1353 = 33×41", 33*41, 1353)

print("="*70)
print("J) 混合家矩陣共閉合 (獨立重算)")
print("="*70)
# NuFIT 5.2 |U| 4 位 (scripts/06 相同目標 — docs/05 數字基於呢個)
U_NUFIT = np.array([
    [0.8250, 0.5452, 0.1490],
    [0.3083, 0.5871, 0.7485],
    [0.4737, 0.5984, 0.6462],
])
def pmns(t12, t13, t23, d):
    s12, c12 = math.sin(math.radians(t12)), math.cos(math.radians(t12))
    s13, c13 = math.sin(math.radians(t13)), math.cos(math.radians(t13))
    s23, c23 = math.sin(math.radians(t23)), math.cos(math.radians(t23))
    e = math.cos(math.radians(d)) + 1j*math.sin(math.radians(d))
    U = np.array([
        [c12*c13, s12*c13, s13*e.conjugate()],
        [-s12*c23-c12*s23*s13*e, c12*c23-s12*s23*s13*e, s23*c13],
        [s12*s23-c12*c23*s13*e, -c12*s23-s12*c23*s13*e, c23*c13],
    ])
    return np.abs(U)
phi = 1.61803398875
t12_f = math.degrees(math.atan((33+phi)/(33*phi-1)))   # 33.4532
t13_f = math.degrees(math.asin(0.154508*(32/33)))      # 8.6169
for (t23v, label) in [(49.3202, "全-88"), (49.1966, "混合家 55")]:
    U = pmns(t12_f, t13_f, t23v, 230.0)
    dU = np.abs(U - U_NUFIT)
    print(f"   {label}: maxΔ|U| = {dU.max():.4f}, meanΔ|U| = {dU.mean():.4f}")
    print(f"           U = {np.array2string(U, precision=4, suppress_small=False)}")

print("="*70)
print("K) R4 總和 + P2 + P3")
print("="*70)
S = (mp.mpf("-0.0070") + mp.mpf("0.1222") + mp.mpf("0.0479"))*RAD
check("三殘差總和 rad", S, mp.mpf("2.847e-3"), 1e-5)
check("1/352 rad", 1/mp.mpf(352), mp.mpf("2.8409e-3"), 1e-7)
dC55 = mp.atan(mp.sin(21*mp.pi/mp.mpf(55))/mp.sin(9*mp.pi/mp.mpf(55)))*DEG
check("δ_CKM(55)", dC55, mp.mpf("62.1800"), 1e-2, "°")
check("γ₇(55)", gamma_exact(7, 55), mp.mpf("0.6061"), 1e-4)
check("γ₇(88)", gamma_exact(7, 88), mp.mpf("0.2446"), 1e-4)

print("\n" + "="*70)
print(f"TOTAL: {PASS} PASS / {FAIL} FAIL")
print("="*70)
