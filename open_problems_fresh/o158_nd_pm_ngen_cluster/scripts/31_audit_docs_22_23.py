#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/31_audit_docs_22_23.py — 獨立核對 docs/22-23 (audit round 5)
只核對已寫入 docs/22-23 嘅公式/數值, 純重算對照 (scripts/29-30 成果)。
"""
import mpmath as mp
mp.mp.dps = 60

N_d, B, N_gen, L4, L5, L6, F5, F7 = 44, 4, 3, 7, 11, 18, 5, 13
mu2 = 2
F_proj, K_tree = 17, 33

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("A. docs/22 — 2n_u=20 生成鏈")
print("="*72)
ck("A1 20 = 2(L₄+N_gen) = 2×10", 20 == 2*(L4+N_gen))
ck("A2 n_u = L₄+N_gen = 7+3", L4+N_gen == 10)
ck("A3 n_u = F₇−N_gen = 13−3", F7-N_gen == 10)
ck("A4 n_u = F_proj−L₄ = 17−7", F_proj-L4 == 10)
ck("A5 14 = SYNC(7)", 14 == 2*L4)
ck("A6 22 = SYNC(L₅)", 22 == 2*L5)
ck("A7 20 = SYNC(L₄+N_gen)", 20 == 2*(L4+N_gen))
ck("A8 magic rows 5/5: 7,14,22,33,20", 7==L4 and 14==2*L4 and 22==2*L5 and 33==K_tree and 20==2*(L4+N_gen))
# m_s/m_d (44,2)
r44 = mp.sin(44*mp.pi/176)/mp.sin(2*mp.pi/176)
ck("A9 √(γ₄₄/γ₂) = 19.8112 (±0.001)", abs(r44 - mp.mpf('19.8112')) < mp.mpf('0.001'))
phi = (1+mp.sqrt(5))/2
corr = phi**(mp.mpf(10)/528)
ck("A10 ×φ^(10/528) → 20.0 (±0.01)", abs(r44*corr - 20) < mp.mpf('0.01'))
ck("A11 (44,2): 和=46=N_d+μ²", 44+2 == N_d+mu2)
ck("A12 (44,2): 差=42=N_d−μ²", 44-2 == N_d-mu2)
print()

print("="*72)
print("B. docs/23 — 命中對成員算子化")
print("="*72)
ck("B1 86 = 2N_d−μ² = 88−2", 86 == 2*N_d-mu2)
ck("B2 86 = 2(N_d−1)", 86 == 2*(N_d-1))
ck("B3 39 = N_d−F₅ = 44−5", 39 == N_d-F5)
ck("B4 21 = 2B+F₇ = 8+13", 21 == 2*B+F7)
ck("B5 21 = L₆+N_gen = 18+3", 21 == L6+N_gen)
ck("B6 24 = 2N_gen·B", 24 == 2*N_gen*B)
ck("B7 13 = F₇", 13 == F7)
ck("B8 32 = 2L₄+L₆ = 14+18", 32 == 2*L4+L6)
ck("B9 32 = 2B²", 32 == 2*B*B)
ck("B10 46 = N_d+μ²", 46 == N_d+mu2)
ck("B11 1 = B−N_gen", 1 == B-N_gen)
ck("B12 44 = N_d, 2 = μ²", 44 == N_d and 2 == mu2)
ck("B13 H/W 和=125=F₅³", 86+39 == F5**3)
ck("B14 H/W 差=47=N_d+N_gen", 86-39 == N_d+N_gen)
print()

total = len(checks)
print("="*72)
print("AUDIT RESULT: %d/%d PASS (docs/22-23 round 5)" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)