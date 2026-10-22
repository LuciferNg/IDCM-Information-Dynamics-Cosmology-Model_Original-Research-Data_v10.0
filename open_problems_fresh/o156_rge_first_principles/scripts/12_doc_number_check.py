#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
12_doc_number_check.py — T2: docs 數字獨立核對 (audit round, 2026-09-07)
=======================================================================
核對 docs 內未被 scripts/11 覆蓋嘅數字 (只核對, 唔加新推導):
A. docs/01 §2 曲率 d²θ/dlnN²|₈₈ ≈ −0.0036
B. docs/01 §5 Gemini β_top vs 精確 dθ/dlnN (表)
C. docs/02 §2 家族密度 (2/61, 16 命中) — 重跑 scripts/03 邏輯
D. docs/06 §0 質量比 6 個 (ω_a/ω_b 88-convention)
E. docs/04 §4 beat(6,7) = 4sin(π/176)·v_g(6.5)
"""
import math
import mpmath as mp
mp.mp.dps = 50
DEG = mp.mpf(180)/mp.pi
RAD = mp.pi/mp.mpf(180)

PASS, FAIL = 0, 0
def check(name, got, expect, tol=1e-6, unit=""):
    global PASS, FAIL
    ok = abs(got-expect) <= tol*max(1.0, abs(expect))
    g = mp.nstr(got, 8) if isinstance(got, mp.mpf) else str(got)
    e = mp.nstr(expect, 8) if isinstance(expect, mp.mpf) else str(expect)
    print(f"   [{'✅' if ok else '❌'}] {name}: {g}{unit} vs {e}{unit}" + ("" if ok else f" (dev {abs(got-expect)})"))
    PASS += ok; FAIL += (not ok)

def th(N, k1=7, k2=6):
    return mp.atan(mp.sin(k1*mp.pi/mp.mpf(N))/mp.sin(k2*mp.pi/mp.mpf(N)))

def gamma(n, N=88):
    return 4*mp.sin(n*mp.pi/mp.mpf(N))**2

print("A) docs/01 §2: 曲率 d²θ/dlnN²|₈₈ (scripts/02 用 (dθ/dlnN(89)−dθ/dlnN(87))/2)")
# dθ/dlnN = N·u'/(1+u²); u = sin(7π/N)/sin(6π/N)
def dtheta_dlnN(N):
    a, b = 7*mp.pi/mp.mpf(N), 6*mp.pi/mp.mpf(N)
    u = mp.sin(a)/mp.sin(b)
    up = (-7*mp.pi*mp.cos(a)*mp.sin(b) + 6*mp.pi*mp.sin(a)*mp.cos(b)) / (mp.mpf(N)**2 * mp.sin(b)**2)
    return mp.mpf(N)*up/(1+u*u)*DEG
curv = (dtheta_dlnN(89) - dtheta_dlnN(87))/2
print(f"   曲率 ≈ {mp.nstr(curv, 6)} °/ln² (docs/01: −0.0036)")
check("曲率 |值|", abs(curv), mp.mpf("0.0036"), 1e-4, " °/ln²")

print("\nB) docs/01 §5: Gemini β_top vs 精確 dθ/dlnN")
d88 = dtheta_dlnN(88)
print(f"   精確 dθ/dlnN(88) = {mp.nstr(d88, 6)} °/ln-unit (docs/01: +1.58e-1)")
check("dθ/dlnN(88)", d88, mp.mpf("1.58e-1"), 1e-2, " °/ln-unit")
# Gemini β_top: (1/2π)·√(γ₇γ₆)/(γ₇+γ₆)·(∂lnγ₇/∂N − ∂lnγ₆/∂N) — ∂N 版本 (scripts/02 line 83-85)
dln_g7_dN = -2*(7*mp.pi/mp.mpf(88)**2)*mp.cos(7*mp.pi/88)/mp.sin(7*mp.pi/88)
dln_g6_dN = -2*(6*mp.pi/mp.mpf(88)**2)*mp.cos(6*mp.pi/88)/mp.sin(6*mp.pi/88)
beta_gem = (1/(2*mp.pi))*mp.sqrt(gamma(7)*gamma(6))/(gamma(7)+gamma(6))*(dln_g7_dN - dln_g6_dN)*DEG
print(f"   Gemini β_top(88) = {mp.nstr(beta_gem, 6)} °/N-unit (docs/01: +5.7e-4)")
check("Gemini β_top", beta_gem, mp.mpf("5.7e-4"), 2e-4, " °/N-unit")

print("\nC) docs/02 §2: 家族密度 (重跑 scripts/03 邏輯)")
# 家族 1/n: n = ≤3 框架常數乘積 ∈ [300,700]
FC = [2, 3, 4, 5, 6, 7, 8, 11, 13, 16, 21, 33, 42, 44, 46, 55, 66, 88, 176]
prod3 = set()
for a in FC:
    for b in FC:
        if a*b > 700: continue
        for c in FC:
            p = a*b*c
            if 300 <= p <= 700: prod3.add(p)
RESID = mp.mpf("0.1222")*RAD
hits1n = [n for n in sorted(prod3) if abs(1/mp.mpf(n)*DEG - mp.mpf("0.1222"))/mp.mpf("0.1222") < 0.015]
print(f"   1/n 家族: {len(prod3)} 個候選, tol 1.5% 命中 {len(hits1n)} 個: {hits1n} (docs/02: 61 候選, 2 命中 462/468)")
check("1/n 候選數", len(prod3), 61)
check("1/n 命中數", len(hits1n), 2)
# 家族 (γ_a−γ_b)/c
Cs = [5, 6, 8, 15, 30, 33, 42, 44, 66, 88]
hitsB = []
for a in range(1, 44):
    for b in range(a+1, 45):
        for c in Cs:
            v = (gamma(b)-gamma(a))/c*DEG
            if abs(v - mp.mpf("0.1222"))/mp.mpf("0.1222") < 0.02:
                hitsB.append((a, b, c))
print(f"   (γ_a−γ_b)/c 家族: tol 2% 命中 {len(hitsB)} 個 (docs/02: 16)")
check("(γ_a−γ_b)/c 命中數", len(hitsB), 16)

print("\nD) docs/06 §0: 質量比 6 個 (88-convention ω_n = 2sin(nπ/88))")
cases = [
    ("m_W/m_Z (30,41)", 30, 41, "0.8827", "0.88136", "+0.16%"),
    ("m_H/m_W (38,19)", 38, 19, "1.5573", "1.55844", "−0.07%"),
    ("m_u/m_d (10,24)", 10, 24, "0.4624", None, "−0.02%"),
    ("m_c/m_b (8,33)", 8, 33, "0.3049", None, "+0.38%"),
    ("m_μ/m_τ (1,18)", 1, 18, "0.0596", None, "+0.10%"),
    ("m_s/m_d (22,1)", 22, 1, "19.811", None, "−0.94%"),
]
for name, a, b, exp, pdg, dev in cases:
    r = mp.sin(a*mp.pi/88)/mp.sin(b*mp.pi/88)
    print(f"   {name}: ω_{a}/ω_{b} = {mp.nstr(r, 6)} (docs/06: {exp})")
    check(f"{name}", r, mp.mpf(exp), 1e-3)

print("\nE) docs/04 §4: beat(6,7) = 4sin(π/176)·v_g(6.5)")
# v_g(n) = cos(nπ/88) (O152 縫); beat(6,7) = |ω₇−ω₆|, ω_n = 2sin(nπ/88)
w7 = 2*mp.sin(7*mp.pi/88); w6 = 2*mp.sin(6*mp.pi/88)
beat = abs(w7-w6)
vg65 = mp.cos(6.5*mp.pi/88)
rhs = 4*mp.sin(mp.pi/176)*vg65
print(f"   |ω₇−ω₆| = {mp.nstr(beat, 10)}; 4sin(π/176)·v_g(6.5) = {mp.nstr(rhs, 10)}")
check("beat(6,7) 公式", beat, rhs, 1e-9)

print("\n" + "="*60)
print(f"T2 核對: {PASS} PASS / {FAIL} FAIL")
print("="*60)
