#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O168 盲測攻堅 (2026-10-16): 1/1749 樣本外判決 (scripts/30)
============================================================
docs/26 盲測判準 (η_B 教訓): 1/1749 = 1/(N_gen·L₅·k) 必須通過樣本外先升格。
判準: 同一修正必須出現喺其他比率鎖; 若 (1)(2) 都唔係 1/1749 結構 → 降級 🔴。

樣本外測試點:
  1. 137^{E_proj} 比率鎖 (docs/14): R_world/l_P = 137^{28.5}·(1+r₁), 求 1/r₁
  2. λ_sync = R_world/14 (docs/21): R_world/λ_sync = 44/π (O73 恆等), vs 14: r₂ = (44/π)/14 − 1, 求 1/r₂
  3. (追加) e 公式 (docs/13): φ²(1+1/2F₇) vs e: r₃ — 樣本外擴展

判決規則:
  - 任一 r 最近整數 = 1749 (且因子 = 3·11·53) → 部分確認
  - 全部最近整數 素數/無結構 (2273 素數等) → 1/1749 降級 🔴 (掃描巧合)
  - 全部有結構但唔係 1749 → 1/1749 降級 🔴 (結構家族泛濫 = 非唯一)
方法: /usr/bin/python3 + mpmath (dps=50)
"""
from mpmath import mp, mpf, sqrt, pi, exp, log
mp.dps = 50

PASS = 0
FAIL = 0
def chk(name, got, target, tol=1e-6, desc=""):
    global PASS, FAIL
    g, t = mpf(got), mpf(target)
    rel = abs(g - t) / abs(t)
    ok = rel < tol
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {mp.nstr(g,12)} vs {mp.nstr(t,12)} rel {mp.nstr(rel,3)} {desc}")

def factor(n):
    """試除分解 (n 細, 直接)"""
    n = int(n)
    orig = n
    facs = []
    d = 2
    while d*d <= n:
        while n % d == 0:
            facs.append(d)
            n //= d
        d += 1
    if n > 1:
        facs.append(n)
    return facs

def best_int(frac, lo=1000, hi=5000):
    """掃描 lo..hi: 邊個整數最接近 1/frac"""
    best, bestv = None, None
    for n in range(lo, hi+1):
        v = abs(mpf(1)/n/frac - 1)
        if bestv is None or v < bestv:
            bestv, best = v, n
    return best, bestv

# ── 基礎常數 (同 scripts/29) ──
hbar = mpf('1.054571817e-34')
c = mpf('299792458')
G_cod = mpf('6.67430e-11')
MP_cod = sqrt(hbar*c/G_cod)
Mpc_m = mpf('3.0856775814913673e22')
R_world = mpf('4129.94') * Mpc_m
E_proj = mpf(57)/2
N_d = mpf(44); B = mpf(4); N_gen = mpf(3); mu2 = mpf(2)
K_tree = mpf(33); L5 = mpf(11); F7 = mpf(13); phi = (1+sqrt(5))/2

print("═"*70)
print("O168 blind test 1/1749 (10-16) — 樣本外判決")
print("═"*70)

# ── 基準: M_P(ω_ring) 殘餘 ──
print("\n── 基準: M_P(ω_ring) 殘餘 ──")
wp = c / R_world
MP_pred = hbar * (137**E_proj) * wp / c**2
f0 = MP_cod / MP_pred - 1
n0, d0 = best_int(f0)
print(f"  M_P 殘餘 r₀ = {mp.nstr(f0,10)};  1/r₀ 最近整數 = {n0} (dev {mp.nstr(d0,3)}); 因子 {factor(n0)}")
print(f"  → 1749 = 3·11·53 = N_gen·L₅·k (docs/26 已申報)")

# ── 樣本外 1: 137^{E_proj} 比率鎖 ──
print("\n── 樣本外 1: R_world/l_P = 137^{E_proj} (docs/14) ──")
l_P = sqrt(hbar*G_cod/c**3)
ratio = R_world / l_P
r1 = ratio / (137**E_proj) - 1
n1, d1 = best_int(r1)
print(f"  ratio = {mp.nstr(ratio,12)};  137^{{28.5}} = {mp.nstr(137**E_proj,12)}")
print(f"  殘餘 r₁ = {mp.nstr(r1,10)};  1/r₁ 最近整數 = {n1} (dev {mp.nstr(d1,3)}); 因子 {factor(n1)}")
print(f"  ⚠️ r₁ == r₀ EXACT (差異 {mp.nstr(abs(r1-f0),3)}) — 137^E 比率鎖同 M_P(ω_ring) 係同一恆等嘅兩面")
print(f"  → 唔係獨立樣本, 剔除盲測 (docs/26 判準修正)")

# ── 樣本外 2: λ_sync = R_world/14 ──
print("\n── 樣本外 2: R_world/λ_sync = 44/π vs 14 (docs/21, O73 恆等) ──")
ratio2 = mpf(44)/pi
r2 = ratio2 / 14 - 1
n2, d2 = best_int(r2)
print(f"  R_world/λ_sync = 44/π = {mp.nstr(ratio2,10)}")
print(f"  殘餘 r₂ = {mp.nstr(r2,10)};  1/r₂ 最近整數 = {n2} (dev {mp.nstr(d2,3)}); 因子 {factor(n2)}")
is1749_2 = (n2 == 1749)
print(f"  → 係 1/1749? {'YES' if is1749_2 else 'NO'}")

# ── 樣本外 3 (追加): e 公式 ──
print("\n── 樣本外 3: e = φ²(1+1/2F₇) (docs/13) ──")
e_formula = phi**2 * (1 + mpf(1)/(2*F7))
r3 = e_formula / exp(1) - 1
n3, d3 = best_int(r3, 100, 50000)
print(f"  e_formula = {mp.nstr(e_formula,10)};  殘餘 r₃ = {mp.nstr(r3,8)}")
print(f"  1/r₃ 最近整數 = {n3} (dev {mp.nstr(d3,3)}); 因子 {factor(n3)}")
is1749_3 = (n3 == 1749)
print(f"  → 係 1/1749? {'YES' if is1749_3 else 'NO'}")

# ── 判決 ──
print("\n" + "═"*70)
print("盲測判決")
print("═"*70)
print(f"  基準 r₀ (M_P):     1/r₀ ≈ {n0} = 1749 = N_gen·L₅·k (結構)")
print(f"  樣本外 r₁ (137^E): 1/r₁ ≈ {n1} ({'結構' if len(factor(n1))>1 else '素數'})")
print(f"  樣本外 r₂ (λ_sync): 1/r₂ ≈ {n2} ({'結構' if len(factor(n2))>1 else '素數'})")
print(f"  樣本外 r₃ (e):     1/r₃ ≈ {n3} ({'結構' if len(factor(n3))>1 else '素數'})")

hits = sum([is1749_2, is1749_3])   # r₁ 剔除 (同恆等, 非獨立)
print(f"\n  ✓ 1/1749 命中獨立樣本外: {hits}/2 (r₁ = 同恆等剔除)")
if hits == 0:
    verdict = "🔴 降級 — 1/1749 係 1749.02 掃描巧合 (η_B 教訓第三次重演); M_P 殘餘維持無結構"
elif hits == 1:
    verdict = "🟡 部分確認 — 一個樣本外命中, 需第三樣本"
else:
    verdict = "🟢 升格候選 — ≥2 樣本外命中, 1/1749 係結構修正"
print(f"  ★ 裁決: {verdict}")

# 判準 echo (docs/26 原文)
print("\n  (docs/26 判準: 若 (1)(2) 都唔係 1/1749 結構 → 降級 🔴)")