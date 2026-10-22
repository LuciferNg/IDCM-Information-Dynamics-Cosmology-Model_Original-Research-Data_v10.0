#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/01_verify_wfield_qm.py

R0 -- 引用清單之獨立驗證 (independent re-derivation of cited W-field / QM results)

原則 (o-series-research-workflow §交回重驗):
  (1) 判斷物件性質先於數值;
  (2) 由零重算, 唔 import 任何上游 script (zero-import);
  (3) 可證偽之數值斷言入 PASS/FAIL; 純結構聲稱印 [CLAIM] 並排除於 PASS 分母外;
  (4) 每個 check 標明慣例 (44-mode / 88-site / 176-L)。

被驗來源 (引用, 唔重推): O80 (path integral / propagator, 9/9),
  O138 (Born / N(s) / budget / decoherence), O126 (tick / Gamma 收口),
  O215 (Sigma sqrt(gamma) 閉式), O34 (Sigma gamma)。

慣例:
  [44-mode]  gamma_n = 4 sin^2(pi n / 88), n = 1..44          (44-site chain)
  [176-L]    gam_k  = 4 sin^2(pi k / 176), k = 1..88          (88-site dual chain)
  omega_n = sqrt(gamma_n) = 2 sin(pi n / 88)  (>0 for n=1..44)
"""

import json
import os
from mpmath import mp, mpf, sin, cos, pi, cot, sqrt, exp, nstr

mp.dps = 50

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)

RESULTS = []


def chk(tag, name, ok, detail):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    mark = "PASS" if ok else "FAIL"
    print("[%s] %-6s %-58s %s" % (mark, tag, name, detail))
    return ok


def claim(tag, name, text):
    RESULTS.append({"tag": tag, "name": name, "ok": None, "detail": text})
    print("[CLAIM] %-6s %-58s %s" % (tag, name, text))


def rel(a, b):
    a = mpf(a)
    b = mpf(b)
    if b == 0:
        return abs(a - b)
    return abs(a - b) / abs(b)


# ---------------------------------------------------------------- constants
N_D = 44
NGEN = 3
B = 4
L8 = 47          # Lucas L8 = 47
L10 = 123        # Lucas L10 = 123
F11 = 89
WVAC2 = mpf(123) / 2          # <W>^2 = 61.5  (O39)
LAM = mpf(2) / 123            # lambda = 2/123 (O39)
MU2 = mpf(2)                  # mu^2 = 2 (O34)
R_WORLD = mpf("4129.94")      # Mpc (O171/O73)
T_RING_GYR = mpf("84.635")    # Gyr (O126)
SEC_PER_GYR = mpf("3.155693e16")
T_REG_GAMMA = mpf("1.647400e-17")   # s^-1, O138 registered

print("=" * 100)
print("O222 R0 -- independent verification of cited W-field / QM results (zero import, mp.dps=%d)" % mp.dps)
print("=" * 100)

# ---------------------------------------------------------------- A. path integral / propagator (O80)
print("\n--- A. Path integral / propagator  [source: O80 docs/01 s5, scripts/05 (9/9)] ---")

gam44 = [4 * sin(pi * n / 88) ** 2 for n in range(1, N_D + 1)]
om44 = [sqrt(g) for g in gam44]

# A1 gamma_n = omega_n^2 exact, omega_44 = 2 (Nyquist)
maxd = max(abs(g - o ** 2) for g, o in zip(gam44, om44))
chk("[44-mode]", "A1 gamma_n = omega_n^2 exact; omega_44 = 2 (Nyquist)",
    maxd < mpf("1e-45") and rel(om44[-1], 2) < mpf("1e-45"),
    "max dev = %s ; omega_44 = %s" % (nstr(maxd, 3), nstr(om44[-1], 20)))

# A2 sums
s44 = sum(gam44)
gam176 = [4 * sin(pi * k / 176) ** 2 for k in range(1, 89)]
s176 = sum(gam176)
s_odd = sum(gam176[i] for i in range(0, 88, 2))     # k = 1,3,..,87
s_even = sum(gam176[i] for i in range(1, 88, 2))    # k = 2,4,..,88
chk("[44-mode]", "A2a sum_{n=1..44} gamma_n = 2(N_d+1) = 90", rel(s44, 90) < mpf("1e-45"),
    "sum = %s" % nstr(s44, 25))
chk("[176-L]", "A2b sum_{k=1..88} gam_k = 178 = 2F_11 ; odd = 88 = 2N_d ; even = 90",
    rel(s176, 2 * F11) < mpf("1e-45") and rel(s_odd, 88) < mpf("1e-45") and rel(s_even, 90) < mpf("1e-45"),
    "total = %s ; odd = %s ; even = %s" % (nstr(s176, 20), nstr(s_odd, 20), nstr(s_even, 20)))

# A3 mode-product  prod omega_n = 2 sqrt(N_d) ; prod gamma_n = 4 N_d = 176  (sine product, N=88)
#    NOTE: first attempt wrongly claimed prod omega = 176 -> FAILED (13.2665). Corrected below;
#    the FAIL is kept in the record on purpose (verification caught its own author).
prod_w = mpf(1)
prod_g = mpf(1)
for o, g in zip(om44, gam44):
    prod_w *= o
    prod_g *= g
chk("[44-mode]", "A3a [CORRECTED] prod_{n=1..44} omega_n = 2 sqrt(N_d) = 2 sqrt(44)",
    rel(prod_w, 2 * sqrt(N_D)) < mpf("1e-40"),
    "prod omega = %s ; 2 sqrt(44) = %s" % (nstr(prod_w, 25), nstr(2 * sqrt(N_D), 25)))
chk("[44-mode]", "A3b prod_{n=1..44} gamma_n = (prod omega)^2 = 4 N_d = 176 EXACT (spectral product)",
    rel(prod_g, 4 * N_D) < mpf("1e-40"),
    "prod gamma = %s ; 4N_d = 176" % nstr(prod_g, 30))
#    PROVENANCE (dedup 2026-09-29): ALREADY EXISTS -- owner = O144
#    (o144_boson_identity/scripts/25_epistemology_reclass.py L96/L106: 44-site chain full spectral
#     product = 176 = prod gamma_even). Here a REPRODUCTION, not new.

# A4 propagator zero-time sum  sum 1/gamma_n = 1291/4 = 322.75
#    PROVENANCE (dedup 2026-09-29): ALREADY EXISTS -- owner = O32
#    (o32_galaxy_rotation/05_open_problems_closed.md L48/L183, 06_verification_audit.md L102-107,
#     scripts/17_orthogonal_fit.py L93; csc^2 identity QED). Here a REPRODUCTION, not new.
sum_inv = sum(1 / g for g in gam44)
sum_inv_43 = sum(1 / gam44[i] for i in range(43))
chk("[44-mode]", "A4 sum_n G_n(0) = sum 1/gamma_n = 1291/4 = 322.75 EXACT",
    rel(sum_inv, mpf(1291) / 4) < mpf("1e-40"),
    "sum = %s ; exact = 322.75" % nstr(sum_inv, 30))
chk("[44-mode]", "A4b pitfall: omitting n=44 (Nyquist) gives 322.5 (O204 note)",
    rel(sum_inv_43, mpf(1290) / 4) < mpf("1e-40"),
    "partial = %s ; exact = 322.5" % nstr(sum_inv_43, 25))

# A5 cited closed form  sum omega_n = 1 + cot(pi/176)   (O215)
sum_w = sum(om44)
target = 1 + cot(pi / 176)
chk("[44-mode]", "A5 sum_n omega_n = 1 + cot(pi/176) (O215 cited)",
    rel(sum_w, target) < mpf("1e-40"),
    "sum = %s ; target = %s ; rel dev = %s" % (nstr(sum_w, 25), nstr(target, 25), nstr(rel(sum_w, target), 3)))

# A6 thermal path integral Z0(beta), high-T limit -> beta^-44 / prod omega
#    NEW (dedup 2026-09-29: full-corpus search beta^-44 / high-T limit = 0 hits outside this O)
#    => the free path-integral normalisation knows dim H = N_d = 44. First O80 <-> O138 link.
beta = mpf("1e-3")
Z0 = mpf(1)
for o in om44:
    Z0 *= exp(-beta * o / 2) / (1 - exp(-beta * o))
Z0_lim = beta ** (-N_D) / prod_w
chk("[44-mode]", "A6 Z_0(beta->0) = beta^-44 / prod omega = beta^-44 / (2 sqrt(N_d)); mode count = dim H = 44",
    rel(Z0, Z0_lim) < mpf("1e-4"),
    "Z0(%s) = %s ; limit = %s ; rel dev = %s" % (nstr(beta, 3), nstr(Z0, 20), nstr(Z0_lim, 20), nstr(rel(Z0, Z0_lim), 3)))

# A7 UV cutoff scales
aW = R_WORLD / 88
lmin = R_WORLD / 44
chk("[44-mode]", "A7a UV cutoff scales: a = R_world/88 ; lambda_min = R_world/44",
    rel(aW, mpf("46.93")) < mpf("2e-4") and rel(lmin, mpf("93.86")) < mpf("2e-4"),
    "a = %s Mpc (46.93) ; lambda_min = %s Mpc (93.86)" % (nstr(aW, 10), nstr(lmin, 10)))
chk("[44-mode]", "A7b omega_max = omega_44 = 2 (Nyquist); no UV divergence (finite spectrum)",
    rel(max(om44), 2) < mpf("1e-45"),
    "omega_max = %s" % nstr(max(om44), 20))

# ---------------------------------------------------------------- B. measurement layer (O138 / O126)
print("\n--- B. Measurement / execution layer  [source: O138 (43/61/47) + O126 docs/04-05] ---")

# B1 Born rule
p_n = [g / s44 for g in gam44]
chk("[44-mode]", "B1 Born p_n = gamma_n/90 ; sum_n p_n = 1 EXACT", rel(sum(p_n), 1) < mpf("1e-45"),
    "sum p = %s ; p_7 = %s (gamma_7/sum)" % (nstr(sum(p_n), 25), nstr(p_n[6], 20)))

# B2 budget
Bf = mpf(L10) / (2 * N_D)
dE = N_D * Bf
Emin = mpf(L10) / (4 * N_D)
chk("[44-mode]", "B2a B(n) = L10/(2N_d) = 123/88 ; dE_read = N_d*B = 61.5 = <W>^2",
    rel(Bf, mpf(123) / 88) < mpf("1e-45") and rel(dE, WVAC2) < mpf("1e-45"),
    "B = %s ; dE = %s ; <W>^2 = %s" % (nstr(Bf, 20), nstr(dE, 20), nstr(WVAC2, 20)))
chk("[44-mode]", "B2b dim H forced: 61.5/B(n) = 44 EXACT ; E_min = 123/176",
    rel(WVAC2 / Bf, 44) < mpf("1e-45") and rel(Emin, mpf(123) / 176) < mpf("1e-45"),
    "61.5/B = %s ; E_min = %s" % (nstr(WVAC2 / Bf, 20), nstr(Emin, 20)))

# B3 decoherence / tick (O138 + O126)
T_ring_s = T_RING_GYR * SEC_PER_GYR
f_ring = 1 / T_ring_s
Gamma = N_D * f_ring
tick_gyr = T_RING_GYR / (2 * N_D)
tick_s = tick_gyr * SEC_PER_GYR
Gamma_tick = 1 / (2 * tick_s)
tau_deco_gyr = T_RING_GYR / N_D
chk("[44-mode]", "B3a Gamma = N_d*f_ring = 1/(2*tick) ; vs O138 registered 1.647400e-17",
    rel(Gamma, Gamma_tick) < mpf("1e-30") and rel(Gamma, T_REG_GAMMA) < mpf("1e-4"),
    "Gamma = %s ; 1/(2tick) = %s ; rel dev vs reg = %s" % (nstr(Gamma, 12), nstr(Gamma_tick, 12), nstr(rel(Gamma, T_REG_GAMMA), 3)))
chk("[44-mode]", "B3b tick = T_44 = T_sync/(2N_d) = 0.96176 Gyr ; tau_deco = T_ring/N_d = 2*tick = 1.923521 Gyr",
    rel(tick_gyr, mpf("0.96176")) < mpf("1e-4") and rel(tau_deco_gyr, 2 * tick_gyr) < mpf("1e-30") and rel(tau_deco_gyr, mpf("1.923521")) < mpf("1e-5"),
    "tick = %s Gyr ; tau_deco = %s Gyr" % (nstr(tick_gyr, 10), nstr(tau_deco_gyr, 10)))

# B4 introspection map N(s): zeros = lambda/(n+1/2), poles = lambda/n  (lambda set = 1: scale invariant)
zeros = [mpf(1) / (n + mpf(1) / 2) for n in range(1, N_D + 1)]
poles = [mpf(1) / n for n in range(1, N_D + 1)]


def Sfun(s):
    """S(s) = f'/f = sum 1/(s-s_n) - sum 1/(s-p_n)  (exact, no removable roundoff)"""
    tot = mpf(0)
    for z in zeros:
        tot += 1 / (s - z)
    for p in poles:
        tot -= 1 / (s - p)
    return tot


def Nmap(s):
    """N(s) = s - f(s)/f'(s) = s - 1/S(s)"""
    return s - 1 / Sfun(s)


# interleaving: sorted union has no two consecutive zeros
allpts = sorted([(z, "z") for z in zeros] + [(p, "p") for p in poles], key=lambda t: -t[0])
types = "".join(t for _, t in allpts)
inter = "zz" not in types and "pp" not in types
chk("[scale-free]", "B4a 44 zeros s_n = 1/(n+1/2) and 44 poles p_n = 1/n strictly interleave",
    len(zeros) == 44 and len(poles) == 44 and inter,
    "pattern head = %s ..." % types[:12])

eps = mpf("1e-8")
z_dev = max(abs(Nmap(z + eps) - z) for z in zeros[:6])
p_dev = max(abs(Nmap(p + eps) - (p + 2 * eps)) / (p + 2 * eps) for p in poles[:6])
chk("[scale-free]", "B4b N'(zero) = 0 (super-attracting) ; N(p+eps) = p+2eps (N'(pole) = 2, repelling)",
    z_dev < mpf("1e-6") and p_dev < mpf("1e-6"),
    "max |N(z+eps)-z| = %s ; max rel dev at pole = %s" % (nstr(z_dev, 3), nstr(p_dev, 3)))

# generic convex combination of two adjacent zeros.
#   STRUCTURE: zeros 1/(n+1/2) and poles 1/n interleave, so the interval [zeros[1], zeros[0]]
#   necessarily contains the pole 1/2. At the pole N(p) = p (a fixed point) -> residual 0;
#   everywhere else strictly positive.
z1, z2 = zeros[0], zeros[1]
hits_pole = []
res_pos = []
res_min = None
res_arg = None
for i in range(1, 200):
    a = mpf(i) / 200
    s_pt = a * z1 + (1 - a) * z2
    d_pol = min(abs(s_pt - q) for q in poles)
    if d_pol < mpf("1e-30"):
        hits_pole.append((a, s_pt))
        continue
    r = abs(Nmap(s_pt) - s_pt)
    res_pos.append(r)
    if res_min is None or r < res_min:
        res_min, res_arg = r, a
alpha_pole = None
for a0, s0 in hits_pole:
    if abs(s0 - mpf(1) / 2) < mpf("1e-30"):
        alpha_pole = a0
chk("[scale-free]", "B4c 199 interior convex combinations: exactly 1 IS the pole 1/2 (a fixed point); other 198 residual > 0",
    len(hits_pole) == 1 and len(res_pos) == 198 and res_min > 0 and alpha_pole is not None,
    "pole hit at alpha = %s (s = 1/2, algebraic alpha = 3/8 = 0.375) ; 198/198 positive ; min residual = %s at alpha = %s"
    % (nstr(alpha_pole, 5) if alpha_pole is not None else "none", nstr(res_min, 6), nstr(res_arg, 4)))

# --- reproduce O138's cited value 9.387 EXACTLY (their scheme: float64 + FD h=1e-7 + LAM=406.1) ---
#   O138 scripts/05 line 300-323: LAM = 406.1, s1 = LAM/1.5, s2 = LAM/2.5, alpha in {0.1..0.9},
#   N(s) = s - f(s)/((f(s+h)-f(s-h))/(2h)) with h = 1e-7 in float64.
#   At scale 406 the relative step is 2.5e-10 -> the central difference of an 88-factor product
#   loses all significance -> f' is noise -> |N-s| is inflated.
LAM_F = 406.1


def _f64(x):
    out = 1.0
    for n in range(1, N_D + 1):
        out *= (x - LAM_F / (n + 0.5))
    for n in range(1, N_D + 1):
        out /= (x - LAM_F / n)
    return out


def _N64(x, h=1e-7):
    return x - _f64(x) / ((_f64(x + h) - _f64(x - h)) / (2 * h))


_a = [0.1, 0.25, 0.5, 0.75, 0.9]
_s1, _s2 = LAM_F / 1.5, LAM_F / 2.5
mix_f64 = min(abs(_N64(a * _s1 + (1 - a) * _s2) - (a * _s1 + (1 - a) * _s2)) for a in _a)
# same quantity, exact algebra (mpmath 50 dps, analytic f'/f)
mix_hp = min(abs(Nmap(mpf(a) * (mpf(1) / mpf("1.5")) + (1 - mpf(a)) * (mpf(1) / mpf("2.5")))
                  - (mpf(a) * (mpf(1) / mpf("1.5")) + (1 - mpf(a)) * (mpf(1) / mpf("2.5")))) for a in _a)
print("      [DIAGNOSTIC] O138 scheme (float64, h=1e-7, LAM=406.1): min |N-s| = %.6f" % mix_f64)
print("      [DIAGNOSTIC] same quantity, exact analytic (mpmath 50 dps)   : min |N-s| = %s" % nstr(mix_hp, 8))
chk("[scale-free]", "B4d O138's cited 9.387 reproduced by their float64 FD(h=1e-7) at LAM=406.1; exact analytic value is O(1e-2) -> cited magnitude = numerical artifact, positivity survives",
    abs(mix_f64 - 9.387) < 0.5 and mix_hp < mpf("0.5"),
    "float64 FD = %.6f (O138: 9.387) ; exact = %s" % (mix_f64, nstr(mix_hp, 8)))

# B5 dispersion / group velocity
vg1 = cos(pi / 88)
vg22 = cos(pi * 22 / 88)
chk("[44-mode]", "B5 v_g(k) = c cos(pi k/88): v_g(44) = 0 ; v_g(22) = cos(pi/4) = 1/sqrt(2)",
    rel(vg22, 1 / sqrt(2)) < mpf("1e-45") and abs(cos(pi / 2)) < mpf("1e-45"),
    "v_1/c = %s ; v_22/c = %s ; v_44/c = 0" % (nstr(vg1, 20), nstr(vg22, 20)))

# ---------------------------------------------------------------- C. structural claims (excluded from PASS denominator)
print("\n--- C. Structural claims (NOT counted in the PASS denominator) ---")
claim("[claim]", "C1 O221: 'IDCM = QM 之離散實現, 非導出 QM'", "quoted, not re-derived here")
claim("[claim]", "C2 'Lazy Load' not formalised in v10.0 corpus", "grep -i lazy = 0 hits (2026-09-29)")
claim("[claim]", "C3 Bell inequality / CHSH / Tsirelson untouched in corpus", "0 hits (see docs/01)")

# ---------------------------------------------------------------- summary
n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
n_claim = sum(1 for r in RESULTS if r["ok"] is None)
print("\n" + "=" * 100)
print("RESULT: %d/%d PASS  (%d FAIL, %d claims excluded)" % (n_pass, n_pass + n_fail, n_fail, n_claim))
print("=" * 100)

with open(os.path.join(DATA, "01_wfield_qm_verification.json"), "w", encoding="utf-8") as fh:
    json.dump({"pass": n_pass, "fail": n_fail, "claims": n_claim, "checks": RESULTS}, fh, ensure_ascii=False, indent=1)
print("saved: data/01_wfield_qm_verification.json")
