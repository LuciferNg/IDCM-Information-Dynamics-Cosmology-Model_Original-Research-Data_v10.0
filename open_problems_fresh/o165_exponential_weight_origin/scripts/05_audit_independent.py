#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O165 scripts/05 — 獨立核對審計 (INDEPENDENT AUDIT)
==================================================
由原始定義重新計算 o165 全部 docs (01-04) + final_result 每個數值。
零 import 自身 scripts/00-04 — 全部由 φ = (1+√5)/2, κ = 1/16, γ_k = 4sin²(πk/176)
等原始定義出發, 對照 doc 記載值。
"""
from mpmath import mp, mpf, e, exp, log, sqrt, sin, pi, power, nstr, almosteq
mp.dps = 60

PASS = FAIL = 0
def chk(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  {info}")
    return cond

phi = (1 + sqrt(5)) / 2
kappa = mpf(1) / 16
B = 4
N_d = 44
N_gen = 3

print("=" * 72)
print("A. docs/01_ekappa_label_audit.md 核對")
print("=" * 72)
# A1: phi^2 vs e
d_phi2e = abs(1 - phi**2/e)
chk("A1 φ²≈e 偏差 3.69%", abs(d_phi2e - mpf('0.03687911925')) < mpf('1e-10'),
    f"got {nstr(d_phi2e, 12)}")
# A2: 2lnφ vs 1
d_rate = abs(2*log(phi) - 1)
chk("A2 2lnφ≈1 偏差 3.76%", abs(d_rate - mpf('0.0375763')) < mpf('1e-6'),
    f"got {nstr(d_rate, 8)}")
# A3: relative diffs at n=1,2,3
for n, target in [(1, '0.036879'), (2, '0.0724'), (3, '0.1066')]:
    rel = abs(power(phi, -2*n) - exp(-n)) / power(phi, -2*n)
    chk(f"A3 n={n} rel diff {target}%", abs(rel - mpf(target)) < mpf('5e-4'),
        f"got {nstr(rel*100, 6)}%")
# A4: phi^-2 = 2-phi = (3-sqrt5)/2
chk("A4 φ⁻² = 2−φ", almosteq(power(phi,-2), 2-phi, rel_eps=mpf('1e-50')), "")
chk("A4 φ⁻² = (3−√5)/2", almosteq(power(phi,-2), (3-sqrt(5))/2, rel_eps=mpf('1e-50')), "")
# A5: tree scale
mu0 = power(phi, mpf('291.5'))
mu1 = power(phi, mpf('290.5'))
chk("A5 μ_{l+1}/μ_l = φ⁻¹", almosteq(mu1/mu0, power(phi,-1), rel_eps=mpf('1e-50')), "")
chk("A5 μ_0 = φ^291.5 (8.316e60)", abs(mu0 - mpf('8.316e60'))/mpf('8.316e60') < mpf('1e-3'),
    f"got {nstr(mu0, 5)}")

print()
print("=" * 72)
print("B. docs/02_phi_weight_derivation.md 核對")
print("=" * 72)
p4 = power(phi, -4); p6 = power(phi, -6)
chk("B1 φ⁻⁴ = 0.14589803375", abs(p4 - mpf('0.145898033750315')) < mpf('1e-15'),
    f"got {nstr(p4, 15)}")
chk("B2 φ⁻⁶ = 0.0557280900008", abs(p6 - mpf('0.055728090000841')) < mpf('1e-15'),
    f"got {nstr(p6, 15)}")
chk("B3 夾層 φ⁻⁴ > κ > φ⁻⁶", p4 > kappa > p6, "")
chk("B4 φ⁴ = 3φ+2 = 6.85410196624968", almosteq(3*phi+2, power(phi,4), rel_eps=mpf('1e-50'))
    and abs(3*phi+2 - mpf('6.854101966249685')) < mpf('1e-14'), f"got {nstr(3*phi+2, 15)}")
chk("B5 φ⁶ = 8φ+5 = 17.9442719099992", almosteq(8*phi+5, power(phi,6), rel_eps=mpf('1e-50'))
    and abs(8*phi+5 - mpf('17.94427190999916')) < mpf('1e-13'), f"got {nstr(8*phi+5, 15)}")
chk("B6 夾層 ⇔ 3φ+2 < 16 < 8φ+5", 3*phi+2 < 16 < 8*phi+5, "")
chk("B7 邊距 9.146 / 1.944", abs((16-(3*phi+2)) - mpf('9.145898033750315')) < mpf('1e-13')
    and abs(((8*phi+5)-16) - mpf('1.944271909999159')) < mpf('1e-13'), "")
chk("B8 κ/φ⁻⁶ = 1.1215 (緊邊)", abs((kappa/p6) - mpf('1.1215')) < mpf('1e-4'),
    f"got {nstr(kappa/p6, 8)}")
# B9: visible layers
vis = [l for l in range(8) if power(phi, -2*l) > kappa]
chk("B9 可見層 {0,1,2}", vis == [0, 1, 2], f"got {vis}")
# B10: threshold
n_star = log(16) / (2*log(phi))
chk("B10 快子閾值 2.88084", abs(n_star - mpf('2.88084')) < mpf('1e-4'),
    f"got {nstr(n_star, 8)}")
# B11: mass formula old vs new
m_old = {1: mpf('-0.11234282'), 2: mpf('-0.0098571837'), 3: mpf('0.0006329396')}
m_new = {1: mpf('-0.12202516'), 2: mpf('-0.012167609'), 3: mpf('0.00037738561')}
for l in [1, 2, 3]:
    mn = (kappa - power(phi, -2*l)) * power(phi, -2*l)
    mo = (kappa - exp(-l)) * exp(-l)
    chk(f"B11 l={l} 新 m {nstr(m_new[l], 8)}", abs(mn - m_new[l]) < mpf('1e-7'),
        f"got {nstr(mn, 10)}")
    chk(f"B11 l={l} 舊 m {nstr(m_old[l], 8)}", abs(mo - m_old[l]) < mpf('1e-7'),
        f"got {nstr(mo, 10)}")
    chk(f"B11 l={l} 比 {nstr(mn/mo, 6)}", abs((mn/mo) - m_new[l]/m_old[l]) < mpf('1e-5'), "")
chk("B12 l=1,2 快子 / l=3 穩定", (kappa-power(phi,-2)) < 0 and (kappa-power(phi,-4)) < 0
    and (kappa-power(phi,-6)) > 0, "")
# B13: kappa = B^-2
chk("B13 κ = B⁻² = 4⁻²", almosteq(kappa, mpf(1)/B**2, rel_eps=mpf('1e-50')), "")

print()
print("=" * 72)
print("C. docs/03_uniqueness.md 核對")
print("=" * 72)
# C1: Gaussian
vis_g = [n for n in range(6) if exp(-n*n) > kappa]
chk("C1 高斯可見 {0,1}", vis_g == [0, 1], f"got {vis_g}")
chk("C1 e⁻⁴ = 0.0183 < κ", exp(-4) < kappa, f"e⁻⁴ = {nstr(exp(-4), 6)}")
# C2: power law range
p_hi = log(16)/log(3)
chk("C2 p 上限 ln16/ln3 = 2.52372", abs(p_hi - mpf('2.52372')) < mpf('1e-4'),
    f"got {nstr(p_hi, 8)}")
for p in ['2.0', '2.3', '2.524']:
    v = [n for n in range(1, 8) if power(n, -mpf(p)) > kappa]
    exp_v = [1, 2, 3] if p != '2.524' else [1, 2]
    chk(f"C2 p={p} 可見 {exp_v}", v == exp_v, f"got {v}")
# C3: geometric interval
r_hi = power(16, mpf(-1)/3)
chk("C3 r 區間上界 16^(-1/3) = 0.39685026", abs(r_hi - mpf('0.39685026')) < mpf('1e-7'),
    f"got {nstr(r_hi, 10)}")
chk("C3 φ⁻² ∈ (0.25, 0.397]", mpf(1)/4 < power(phi,-2) <= r_hi, "")
# C4: candidate counts
cands = {"φ⁻¹": power(phi,-1), "φ⁻²": power(phi,-2), "1/4": mpf(1)/4, "1/2": mpf(1)/2,
         "1/7": mpf(1)/7, "1/3": mpf(1)/3, "e⁻¹": e**(-1), "0.35": mpf('0.35')}
expected = {"φ⁻¹": [0,1,2,3,4,5], "φ⁻²": [0,1,2], "1/4": [0,1], "1/2": [0,1,2,3],
            "1/7": [0,1], "1/3": [0,1,2], "e⁻¹": [0,1,2], "0.35": [0,1,2]}
for name, r in cands.items():
    v = [n for n in range(8) if power(r, n) > kappa]
    chk(f"C4 {name} 可見 {expected[name]}", v == expected[name], f"got {v}")
# C5: degeneracies
chk("C5 1/4 退化: 4⁻² = κ", abs(power(mpf(1)/4, 2) - kappa) < mpf('1e-50'), "")
chk("C5 1/2 退化: 2⁻⁴ = κ", abs(power(mpf(1)/2, 4) - kappa) < mpf('1e-50'), "")
# C6: Boltzmann linear ladder
chk("C6 φ⁻²ˡ = e^(−2l·lnφ)", almosteq(power(phi,-2), exp(-2*log(phi)), rel_eps=mpf('1e-50')), "")

print()
print("=" * 72)
print("D. docs/04_ontology_and_handoff.md 核對")
print("=" * 72)
# D1: IPR
import math as m
iprs = []
for k in range(1, 45):
    vk = [m.sin(m.pi * k * j / 88) for j in range(1, 45)]
    nrm = sum(x*x for x in vk)
    iprs.append(sum(x**4 for x in vk) / nrm**2)
chk("D1 IPR 下限 0.03358", abs(min(iprs) - mpf('0.03358')) < mpf('1e-4'), f"got {min(iprs):.5f}")
chk("D1 IPR 上限 0.04545 (k=44)", abs(max(iprs) - mpf('0.04545')) < mpf('1e-4'),
    f"got {max(iprs):.5f}")
chk("D1 延展基準 2/44 = 0.04545", abs(max(iprs) - mpf(2)/44) < mpf('1e-4'), "")
# D2: Green's function xi (E = -0.1)
E = mpf('-0.1')
Gj = []
for j in range(1, 12):
    g = sum(m.sin(m.pi*k*1/88) * m.sin(m.pi*k*j/88) / (E - 4*m.sin(m.pi*k/88)**2) for k in range(1, 45))
    Gj.append(abs(g))
ratios = [Gj[i+1]/Gj[i] for i in range(len(Gj)-1) if Gj[i] != 0]
r_mean = float(sum(ratios)/len(ratios))
xi = float(-1/m.log(mpf(r_mean)))
chk("D2 ξ ≈ 8.29 sites @ E=−0.1", abs(xi - 8.2918) < 0.05, f"got {xi:.4f}")
# D3: chain gamma identity (used implicitly)
chk("D3 γ_k = 4sin²(πk/176) 譜頂 = 4 @ k=88", abs(4*sin(pi*88/176)**2 - 4) < mpf('1e-50'), "")

print()
print("=" * 72)
print("E. final_result.md 核對")
print("=" * 72)
chk("E1 3.69% (φ² vs e)", abs(d_phi2e - mpf('0.03687911925')) < mpf('1e-10'), "")
chk("E2 閾值 2.88084", abs(n_star - mpf('2.88084')) < mpf('1e-4'), "")
chk("E3 夾層代數形式", 3*phi+2 < 16 < 8*phi+5, "")
chk("E4 可見層 3 = N_gen", len([l for l in range(8) if power(phi,-2*l) > kappa]) == N_gen, "")

print()
print("=" * 72)
print(f"審計總計: {PASS} PASS / {FAIL} FAIL")
print("=" * 72)
