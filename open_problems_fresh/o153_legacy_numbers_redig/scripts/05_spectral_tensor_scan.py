#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 05: Spectral-tensor scan over all demoted numbers (R6)
====================================================================
Exhaustive identity scan: every demoted number vs the O152 operator family
(T-hat traces, K_chain spectrum, beats, projection ratios, C-ladder,
half-integer seams, FSR ladder, spectral zeta values).

Demoted numbers:
  eps:   0.1545, 0.1545085 (phi^-1/4), 0.1544715 (19/123)
  alpha: 1.025, 1.0246483 (19*sqrt44/123)
  N_h:   42, 41.9086 (1/eps^2)
  N_EW:  2.5e33, 2.4579e33 (exact), 4.9577e16 (M_Pl/v)
  N_gal: 1e6
  Ncrit: 150, 150.41;  N_cont: 15030
Operator value bank (all mpmath 50 dps):
  T-hat: L_n (1..16), F_n (1..16), ratios, L_n/F_n
  K_chain: gamma_n = 4 sin^2(pi n/88), n=1..44
  v_g ladder: cos(pi n/88)
  beats: 4 sin(d pi/176) cos(s pi/176) for d,s in 1..44 (d<=s, subset)
  projection: 19/41, 41/60, 19/60, 19/123, 123/176, 123/88, 61/88
  C-ladder: 88,132,264,528; 176,178,180,360; 90,46,45,60
  FSR: 4^ell for ell 0..12, csc(pi n/176), zeta values
  half-integer seams: (2k+1)/2
Hit rule: |ratio-1| < 1e-3 -> candidate; < 1e-8 -> strong; ==0 -> exact.
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1 + mp.sqrt(5)) / 2

# ---- operator value bank ----
bank = {}

# T-hat Lucas
L = {}
a, b = mp.mpf(2), mp.mpf(1)   # L_0 = 2, L_1 = 1
L[0], L[1] = a, b
for n in range(2, 17):
    a, b = b, a + b
    L[n] = b
# T-hat Fibonacci
F = {0: mp.mpf(0), 1: mp.mpf(1)}
for n in range(2, 17):
    F[n] = F[n-1] + F[n-2]
for n, v in L.items():
    bank[f"L{n}"] = v
for n, v in F.items():
    bank[f"F{n}"] = v
for n in range(1, 16):
    if L[n] != 0:
        bank[f"L{n}/L{n+1}"] = L[n] / L[n+1]
        bank[f"L{n+1}/L{n}"] = L[n+1] / L[n]
for n in range(1, 15):
    bank[f"F{n}/F{n+1}"] = F[n] / F[n+1]
    bank[f"F{n+1}/F{n}"] = F[n+1] / F[n]
    bank[f"L{n}/F{n}"] = L[n] / F[n] if F[n] else None
    bank[f"F{n}/L{n}"] = F[n] / L[n]

# K_chain spectrum
for n in range(1, 45):
    bank[f"gamma{n}"] = 4 * mp.sin(mp.pi * n / 88) ** 2
    bank[f"vg{n}"] = mp.cos(mp.pi * n / 88)
    bank[f"csc{n}"] = 1 / mp.sin(mp.pi * n / 88)

# beats (representative subset: d<=s, d,s in 1..44 step selected)
beat_vals = []
for d in range(1, 44):
    for s in range(d, 44):
        bv = 4 * mp.sin(d * mp.pi / 176) * mp.cos(s * mp.pi / 176)
        beat_vals.append((f"beat({d},{s})", bv))
# keep all (946 entries ok)

# projection ratios
for name, v in {
    "f_proj/f_unproj": mp.mpf(19)/41, "f_unproj": mp.mpf(41)/60,
    "f_proj": mp.mpf(19)/60, "eps_exact": mp.mpf(19)/123,
    "E_min": mp.mpf(123)/176, "E_min*2": mp.mpf(123)/88,
    "61/88": mp.mpf(61)/88, "41/88": mp.mpf(41)/88,
    "90/88": mp.mpf(90)/88, "88/90": mp.mpf(88)/90,
    "176/178": mp.mpf(176)/178, "178/176": mp.mpf(178)/176,
    "360/176": mp.mpf(360)/176, "alpha": mp.mpf(19)*mp.sqrt(44)/123,
}.items():
    bank[name] = v

# integers
for v in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 16, 17, 18, 19, 21, 22, 24,
          30, 32, 33, 36, 40, 41, 43, 44, 45, 46, 60, 61, 66, 77, 84, 87, 88,
          90, 98, 123, 124, 132, 137, 143, 176, 178, 180, 192, 264, 369, 528,
          946, 1496]:
    bank[f"int{v}"] = mp.mpf(v)

# FSR refinement
for ell in range(0, 13):
    bank[f"4^ell{ell}"] = mp.mpf(4) ** ell
for n in range(1, 45):
    bank[f"F4*{n}"] = mp.mpf(4) * n
# sqrt / logs
for v, nm in [(44, "sqrt44"), (88, "sqrt88"), (176, "sqrt176"), (178, "sqrt178"),
              (2, "sqrt2"), (3, "sqrt3"), (5, "sqrt5"), (11, "sqrt11")]:
    bank[nm] = mp.sqrt(v)
bank["1/sqrt44"] = 1 / mp.sqrt(44)
bank["1/sqrt88"] = 1 / mp.sqrt(88)

# ---- targets ----
targets = {
    "eps_v1 (0.1545)": mp.mpf('0.1545'),
    "eps_corpus (phi^-1/4)": 1 / (4 * phi),
    "eps_exact (19/123)": mp.mpf(19) / 123,
    "alpha_v1 (1.025)": mp.mpf('1.025'),
    "alpha_exact": mp.mpf(19) * mp.sqrt(44) / 123,
    "N_h_MCMC (42)": mp.mpf(42),
    "N_h_alpha1 (41.9086)": 1 / (mp.mpf(19) / 123) ** 2,
    "N_EW_claim (2.5e33)": mp.mpf('2.5e33'),
    "N_EW_exact (2.4579e33)": (mp.mpf('1.220890e19') / mp.mpf('246.2196')) ** 2,
    "M_Pl/v (4.9577e16)": mp.mpf('1.220890e19') / mp.mpf('246.2196'),
    "N_gal (1e6)": mp.mpf('1e6'),
    "N_crit_formula (150.41)": (4 * mp.pi / (mp.mpf(19) * mp.sqrt(44) / 123)) ** 2,
    "N_crit_claim (150)": mp.mpf(150),
    "N_cont_claim (15030)": mp.mpf(15030),
}

def scan(target_name, target, tol=mp.mpf('1e-3')):
    hits = []
    for name, v in bank.items():
        if v is None or v == 0 or target == 0:
            continue
        r = target / v
        if abs(r - 1) < tol:
            hits.append((name, mp.nstr(v, 8), mp.nstr(abs(r - 1), 5)))
    for name, v in beat_vals:
        if v == 0:
            continue
        r = target / v
        if abs(r - 1) < tol:
            hits.append((name, mp.nstr(v, 8), mp.nstr(abs(r - 1), 5)))
    # sort by deviation
    hits.sort(key=lambda h: float(h[2]))
    return hits

print("=" * 90)
print("SPECTRAL-TENSOR SCAN: demoted numbers vs O152 operator family")
print("Hit rule: |target/op - 1| < 1e-3 (candidate), <1e-8 (strong), ==0 (exact)")
print("=" * 90)
summary = []
for tname, tval in targets.items():
    hits = scan(tname, tval)
    summary.append((tname, len(hits), hits[:6]))
    print(f"\n### {tname} = {mp.nstr(tval, 12)}")
    if not hits:
        print("    NO HITS within 1e-3")
    for h in hits[:8]:
        strong = "STRONG" if float(h[2]) < 1e-8 else ("EXACT" if float(h[2]) == 0 else "cand")
        print(f"    {h[0]:<24s} = {h[1]:>12s}   dev {h[2]:>8s}  [{strong}]")

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)
for tname, nhits, _ in summary:
    print(f"  {tname:<28s} {nhits:3d} hits")
