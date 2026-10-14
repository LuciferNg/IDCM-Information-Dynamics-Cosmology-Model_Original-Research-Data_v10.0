#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v16 AUDIT - independent recomputation (NOT re-running 13_v16*).

Method: isolated math path. Fraction for exact rational identities,
symbolic trig-identity proof for gamma_20, mpmath 60 dps for numeric,
own uniqueness scans. Audit each claim of docs/16 line by line.
No import of the v16 scripts.
"""
from fractions import Fraction as F
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1;  print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

print("="*70)
print("A. EXACT RATIONAL IDENTITIES (Fraction precision)")
print("="*70)
# A1: m/88 = 3/11
chk("m/88 = rho = 3/11", F(24,88) == F(3,11), F(24,88))
# A2: 20 + 24 = 44 = N_d
chk("20+24 = 44", 20+24 == 44)
# A3: mode20 = N_d - 2B*N_gen
chk("20 = 44-2*4*3", 44-2*4*3 == 20)
# A4: 36 = B*N_gen^2 = N_d-2B = 2L6  (three structural readings)
chk("36 = 4*3^2", 4*3**2 == 36)
chk("36 = 44-2*4", 44-2*4 == 36)
chk("L6=18 => 2L6=36", 2*18 == 36)
# A5: L5 = N_d/B
chk("L5 = N_d/B = 11", F(44,4) == 11)

print("="*70)
print("B. SYMBOLIC TRIGONOMETRY (gamma_20 = 4cos^2(3pi/11))")
print("="*70)
# sin(a) = cos(pi/2 - a).  20*pi/88 = 5*pi/22.  pi/2 - 5pi/22 = (11-5)pi/22 = 6pi/22 = 3pi/11.
a1 = F(20,88)  # = 5/22
a2 = F(1,2) - a1  # pi/2 - 20pi/88
print(f"  pi/2 - 20pi/88 = {a2} * pi  ;  3/11 = {F(3,11)}")
chk("symbolic: pi/2 - 20pi/88 = 3pi/11", a2 == F(3,11))
# numeric cross-check at 60 dps
sin20 = mp.sin(mp.pi*20/88)
cos3  = mp.cos(3*mp.pi/11)
chk("numeric: sin(20pi/88) == cos(3pi/11)", mp.almosteq(sin20, cos3, rel_eps=mp.mpf('1e-50')))
gam20_mode = 4*sin20**2
gam20_rho  = 4*cos3**2
chk("gamma_20 mode-form == rho-form", mp.almosteq(gam20_mode, gam20_rho, rel_eps=mp.mpf('1e-50')))

print("="*70)
print("C. NUMERIC RECOMPUTATION (mpmath 60 dps, isolated)")
print("="*70)
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2
M0 = mp.mpf('27.900915')
M_Z = mp.mpf('91.1876')
B = mp.mpf(4); N_gen = mp.mpf(3); N_d = mp.mpf(44); L5 = mp.mpf(11)
rho = N_gen/L5

lam_max = 36 - 1/gamma(20)
core = mp.sqrt(lam_max)*M0
Lam = core*rho
Lam_op = M0*rho*mp.sqrt(B*N_gen**2 - 1/(4*mp.cos(rho*mp.pi)**2))
print(f"  lambda_max  = {mp.nstr(lam_max, 15)}")
print(f"  sqrt(l)*M0  = {mp.nstr(core, 12)} MeV")
print(f"  Lambda_IDCM(v13 form)    = {mp.nstr(Lam, 12)} MeV")
print(f"  Lambda_IDCM(operator f)  = {mp.nstr(Lam_op, 12)} MeV")
chk("Lambda v13-form == operator-form", mp.almosteq(Lam, Lam_op, rel_eps=mp.mpf('1e-40')))
chk("Lambda == 45.2848693374 (docs/12 audit)", mp.almosteq(Lam, mp.mpf('45.2848693374'), rel_eps=mp.mpf('1e-10')))

# sigma chain
Sg_odd = 88
sig = Sg_odd*(Lam/1000)**2
sig_op = 2*N_d*M0**2*rho**2*lam_max/1e6
chk("sigma == 0.180463306 GeV^2 (v15b P7)", mp.almosteq(sig, mp.mpf('0.180463306'), rel_eps=mp.mpf('1e-6')))
chk("sigma operator-form == direct", mp.almosteq(sig, sig_op, rel_eps=mp.mpf('1e-30')))

print("="*70)
print("D. UNIQUENESS SCANS (own implementation)")
print("="*70)
# D1: modes with gamma_n == 4cos^2(3pi/11)
tgt = 4*mp.cos(3*mp.pi/11)**2
hits = [n for n in range(1,89) if mp.almosteq(gamma(n), tgt, rel_eps=mp.mpf('1e-30'))]
print(f"  modes 1..88 with gamma_n=4cos^2(3pi/11): {hits}")
chk("mode hits = {20,68} (68 = 88-20 symmetry)", set(hits) == {20,68})
h1 = [n for n in range(1,45) if mp.almosteq(gamma(n), tgt, rel_eps=mp.mpf('1e-30'))]
chk("unique mode in 1..44: [20]", h1 == [20])

# D2: target ratio L5/N_gen = 11/3 in dense scan (v13 criterion-4 style)
# check nearest structural rational within 0.5% over vocab
vocab = [2,3,4,5,7,8,11,13,17,18,21,29,33,34,35,36,44,47,55,71,88,89,90]
tgt_r = mp.mpf(11)/3
near = []
for a in vocab:
    for b in vocab:
        v = mp.mpf(a)/b
        if abs(v-tgt_r)/tgt_r < mp.mpf('0.005'):
            near.append((a,b,mp.nstr(v,8)))
print(f"  rationals a/b in 0.5% of 11/3: {near}")
chk("11/3 unique in 0.5% (plus trivials 33/9,22/6)", all(F(a,b1)==F(11,3) for a,b1,_ in near))

# D3: sqrt(lambda_max) in V_core window 0.2% (docs/16 claim 0 hits)
rt = mp.sqrt(lam_max)
hits3 = []
for a in vocab:
    for b in vocab:
        v = mp.mpf(a)/b
        if abs(v-rt)/rt < mp.mpf('0.002'):
            hits3.append((a,b,mp.nstr(v,8)))
print(f"  V_core ratios within 0.2% of sqrt(lam_max): {hits3}")
chk("sqrt(lam_max) V_core window: 0 hits", len(hits3) == 0)

print("="*70)
print("E. RHO FIXITY (own perturb scan)")
print("="*70)
Lam0 = Lam
for eps in [mp.mpf('1e-3'), mp.mpf('-1e-3')]:
    rp = rho + eps
    lp = 36 - 1/(4*mp.cos(rp*mp.pi)**2)
    Lam_p = M0*rp*mp.sqrt(lp)
    print(f"  rho{'+' if eps>0 else ''}{mp.nstr(eps,3)}: Lambda={mp.nstr(Lam_p,10)} MeV  dLam={mp.nstr((Lam_p-Lam0)*1000,6)} keV")
chk("rho perturb 1e-3 -> Lambda drifts (163 keV, != 0)",
    abs((M0*(rho+mp.mpf('1e-3'))*mp.sqrt(36-1/(4*mp.cos((rho+mp.mpf('1e-3'))*mp.pi)**2)) - Lam0)*1000 - mp.mpf('163.3')) < mp.mpf('1.0'))

print("="*70)
print("F. LAMBDA_MS(5) footnote check (docs/16 6.1)")
print("="*70)
print(f"  sqrt(lam_max)*M0 = {mp.nstr(core, 8)} MeV  (docs claim 166.0445)")
chk("sqrt(l)*M0 == 166.0445", mp.almosteq(core, mp.mpf('166.0445'), rel_eps=mp.mpf('1e-5')))
print(f"  v15b P9 2-loop implicit cross = 166.0064 MeV (locked in data/12_v15b_out.txt)")
dev166 = (core-166.0064)/166.0064*100
print(f"  dev = {mp.nstr(dev166,5)}% (docs claim +0.023%)")
chk("dev ~ +0.023% (stated as non-closing footnote)", abs(dev166 - mp.mpf('0.0230')) < mp.mpf('0.001'))

print("="*70)
print("G. DOCS/16 SECTION-BY-SECTION CONSISTENCY")
print("="*70)
import re, pathlib
p = pathlib.Path("docs/16_v16_lambda_operator_derivation.md").read_text()
checks = {
  "mode id 20 = N_d-2B*N_gen": "20 = N_d − 2B·N_gen" in p,
  "gamma20 = 4cos^2(N_gen*pi/L5)": "4cos²(N_gen·π/L₅)" in p,
  "lambda_max = B*N_gen^2 - 1/g20": "B·N_gen² − 1/γ₂₀" in p,
  "operator form present": "M₀ · ρ · √(B·N_gen² − 1/(4cos²(ρπ)))" in p,
  "sigma chain present": "2N_d·M₀²·ρ²·λ_max" in p,
  "r=3/11 stated": "ρ = N_gen/L₅ = 3/11" in p or "3/11 = ρ" in p or "ρ = N_gen/L5" in p,
  "uniqueness claimed": "唯一" in p and "n=20" in p,
  "rho fixity stated": "擾動 ρ" in p or "漂 163 keV" in p or "163 keV" in p,
  "footnote non-closing": "唔升格" in p or "唔落結論" in p,
  "lattice tension open": "445(6)" in p and "開放" in p,
  "criterion 6 judgement": "機制 ⑥" in p and ("🟢" in p or "升做" in p),
}
for k,v in checks.items():
    chk(f"docs/16 contains: {k}", v)

print("="*70)
print(f"AUDIT RESULT: {ok} PASS / {fail} FAIL")
print("="*70)