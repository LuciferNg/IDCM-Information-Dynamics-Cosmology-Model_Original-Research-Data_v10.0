#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 - verify ALL incoming handoffs from other O's were independently recomputed.

Incoming handoffs to O142 (register):
  H1 2026-10-04 O144->O142: alpha_s^-1 = F6+sin^2 th_W+1/B ruled non-closed
      (input resolution 0.763% >> candidate spacing 0.118%)
  H2 2026-10-09 O144->O142: sigma_phys/confinement scale bridge lock
      (sigma_phys <- Lambda_QCD <- alpha_s)
  H3 2026-10-13 O124->O142: alpha_EM^-1(0)=137.036 vs integer 137, 0.026% shift

This script INDEPENDENTLY recomputes the core numbers of O144 docs/20 verdict
claimed in O142 docs/10 (which says 'all numbers mpmath/float recomputed'):
  1. alpha_s^-1 = F6 + sin^2 th_W + 1/B  (v9-v11 form)
  2. input resolution sigma(1/a)/1*a = 0.7627%
  3. candidate spacing |A-B| rel = 0.1178% ; |A-B| = 0.155 sigma
  4. b_eff via Beta-decay route (b0=7 -> Lambda=0.0455 GeV, dev 4.6x; b0=23/3 -> 0.0881, 2.4x)
  5. H3 numbers (done in docs/18, scripts/14_verify_o124_handoff.py - spot check)
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
G = mp.mpf
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("H1: O144 non-closure verdict core numbers (docs/10 claims)")
print("="*72)
# alpha_s^-1 = F6 + sin^2_thW + 1/B ; B=4
F6 = F(6)
sin2w = mp.mpf('0.220776')   # v2 structural value 1-(mW/mZ)^2
invB = mp.mpf(1)/4
a_inv_form = F6 + sin2w + invB
print(f"  F6 = {mp.nstr(F6,6)}; form value 1/a = {mp.nstr(a_inv_form, 8)}")
chk("form: F6+sin2w+1/B = 8.470776", mp.almosteq(a_inv_form, mp.mpf('8.470776'), rel_eps=mp.mpf('1e-5')))

# PDG alpha_s(MZ); 1/alpha space sigma
a_PDG = mp.mpf('0.1179'); sig_a = mp.mpf('0.0009')
s_inv = sig_a/a_PDG**2          # sigma(1/a)
rel = s_inv/(1/a_PDG)*100       # 0.7627% claim
print(f"  sigma(1/a) = {mp.nstr(s_inv,6)}  rel = {mp.nstr(rel,5)}%")
chk("input resolution sigma(1/a)/1*a = 0.7627%", abs(rel - 0.7627) < 0.002)

# candidate spacing: O144 docs/20 compares v1-form alpha_s=1/(8+3/13+1/4)=0.117914
# vs v9-v11 form alpha_s=1/(F6+sin^2w+1/B)=0.118053. |A-B| = 0.000139 in alpha space.
A = a_inv_form                                          # 8.470776 (v9-v11 form inverse)
B_v1 = mp.mpf('8.480769')                               # 1/0.117914 (v1 form inverse)
dAB = abs(A - B_v1)
relAB = dAB/((A+B_v1)/2)*100
print(f"  |A-B| (v1 vs v9 form, inv space) = {mp.nstr(dAB,7)}  rel = {mp.nstr(relAB,6)}%  z = {mp.nstr(dAB/s_inv,4)}")
chk("|A-B| = 0.009993 (docs/10)", abs(dAB - 0.009993) < 0.00005)
chk("|A-B| rel ~ 0.1178-0.118%", abs(relAB - 0.1178) < 0.002)
chk("|A-B| = 0.155 sigma", abs(dAB/s_inv - 0.155) < 0.02)

print("="*72)
print("H1-route: beta-decay Lambda check (docs/10 criterion 6)")
print("="*72)
MZ = G('91.1876')
Lam_QCD = G('0.210')
for b0, name in [(G(7), 'b0=7=L4'), (G('23')/3, 'b0=23/3 (Nf=5)')]:
    lam = MZ * mp.e**(-2*mp.pi*a_inv_form/b0/1000)  # wrong: alpha_s^-1=(b0/2pi)ln(MZ/Lam) -> Lam = MZ exp(-2pi a_inv/b0)
    # units: MZ GeV, Lam GeV
    lam_G = MZ * mp.e**(-2*mp.pi*a_inv_form/b0)
    dev = lam_G/Lam_QCD
    print(f"  {name}: Lambda_eff = {mp.nstr(lam_G,6)} GeV  dev vs 0.210 = {mp.nstr(dev,4)}x")
    chk(f"{name} dev ~ documented", None) if False else None
# docs/10: b0=7 -> Lambda=0.0455 GeV dev 4.6x ; b0=23/3 -> 0.0881 dev 2.4x
lam7 = MZ*mp.e**(-2*mp.pi*a_inv_form/7)
lam5 = MZ*mp.e**(-2*mp.pi*a_inv_form/(23/3))
chk("b0=7 -> 0.0455 GeV (4.6x miss)", abs(mp.log(lam7/0.0455)) < 0.01)
chk("b0=23/3 -> 0.0881 GeV (2.4x miss)", abs(mp.log(lam5/0.0881)) < 0.01)
print(f"  b0=7: Lambda = {mp.nstr(lam7,6)} GeV dev {mp.nstr(lam7/0.21,3)}x")
print(f"  b0=23/3: Lambda = {mp.nstr(lam5,6)} GeV dev {mp.nstr(lam5/0.21,3)}x")

print("="*72)
print("H2: O144 scale-bridge lock (sigma_phys <- Lambda_QCD <- alpha_s)")
print("     - dependency statement; structural not numeric")
print("     - RESOLVED: v15 P7 sigma=0.1804633 GeV^2 Regge +0.26% 🟢;")
print("       v16 Lambda_IDCM operatorized 45.2849 MeV; docs/19 notified unlock")
print("="*72)

print("="*72)
print("H3: O124 137.036 endpoint (docs/18 verification recap)")
print("="*72)
a0 = mp.mpf('137.035999074'); aZ = mp.mpf('127.930'); sZ = mp.mpf('0.008')
d = a0 - aZ
chk("H3 Delta = 9.1060 ±0.008 (13.25σ vs 9)", mp.almosteq(d, mp.mpf('9.1060'), rel_eps=mp.mpf('1e-4')))
frac = (a0-137)/137*100
chk("H3 0.02628% offset", abs(frac - 0.02628) < 0.002)
print(f"  (full verification in scripts/14_verify_o124_handoff.py, 6/7 PASS)")

print("="*72)
print(f"HANDOFF RE-RECOMPUTE RESULT: {ok} PASS / {fail} FAIL")
print("="*72)