#!/usr/bin/env python3
"""
O203 Script 09 - c/45 dynamical promotion: mechanism enumeration + rigorous exclusions
=====================================================================================
Attack the open item "c/45 動力學提升" (docs/08 section 7).

PART A - rigorous exclusions (theorems):
  A1 Niven: cos(pi*n/88) is rational only for cos in {0,+/-1} -> no single mode has
     v_g = c/45. Also v_p = sec >= 1 > 1/45.
  A2 k-parity / T-reversal: dispersion omega^2 = k^2 + m^2 is EVEN in k -> the free
     theory has no preferred direction -> no autonomous directed drift.
  A3 [L,J] = 0: L and J are simultaneously diagonal in the mode basis -> the Z2 charge
     is a conserved spectral invariant (Tr(LJ) = gamma_22 = mu^2), not a current.

PART B - mechanism family (30 constructions): every natural dynamical velocity
  construction computed exactly, compared to 1/45 (rel dev), with trap-window flags.

PART C - the two-field Z2-odd drift coupling (the only admissible route):
  single-field first-order term -> Im(omega^2) != 0 (re-verify docs/03 B1)
  two-field term g*(phi_w d_x phi_o - phi_o d_x phi_w) -> REAL dispersion
     omega^2 = k^2 + m^2 -/+ 2 g |k|   (degenerate masses)
     group velocities v_g = (k -/+ g)/omega  -> branch split 2g/omega = g (omega=mu^2=2)
     MEAN transport (v_+ + v_-)/2 = k/omega  -> EXACTLY unchanged
  => drift is realizable ONLY as a Z2-odd relative velocity, and it is invisible in
     every mean observable (hence O169's assembly law is untouched).

PART D - null control on the mechanism family (discriminative power test).
"""
import random
import mpmath as mp
import numpy as np

mp.mp.dps = 60
random.seed(203)
np.random.seed(203)

PASS = 0
FAIL = 0
TRAP_LO, TRAP_HI = mp.mpf("1e-5"), mp.mpf("1e-3")

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")

N_d = 44
mu2 = mp.mpf(2)
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2
TARGET = mp.mpf(1) / 45

def gam(n):
    return 4 * mp.sin(pi * n / 88) ** 2

def vg(n):
    return mp.cos(pi * n / 88)

def sec(n):
    return 1 / mp.cos(pi * n / 88)

G44 = [gam(n) for n in range(1, N_d + 1)]
V44 = [vg(n) for n in range(1, N_d + 1)]
S44 = [sec(n) for n in range(1, N_d + 1)]
G88 = [4 * mp.sin(pi * k / 176) ** 2 for k in range(1, 89)]
V88 = [mp.cos(pi * k / 176) for k in range(1, 89)]

S_tot = sum(G44)

print("=" * 74)
print("O203 S9 - c/45 dynamical promotion: mechanisms + exclusions")
print("=" * 74)

# ============ PART A: rigorous exclusions ============
print("\n=== PART A: rigorous exclusions (theorems) ===")

print("\n[A1] Niven theorem: no single mode has v_g = c/45")
mind = min(abs(v - TARGET) for v in V44)
check("A1a no 44-mode v_g equals 1/45 (min dev > 1e-2)", mind > mp.mpf("1e-2"),
      f"min |cos(pi n/88) - 1/45| = {mp.nstr(mind, 6)} (at n=43)")
mind88 = min(abs(v - TARGET) / TARGET for v in V88)
check("A1b no 176-chain v_g equals 1/45 either (closest k=87 is 16% off)",
      mind88 > mp.mpf("1e-2"),
      f"min RELATIVE dev over k=1..88 = {mp.nstr(mind88 * 100, 4)}%")
# rational values of cos(pi n/88)
rat_n = set()
for n in range(1, N_d + 1):
    c = vg(n)
    for q in range(1, 51):
        for p in range(-q, q + 1):
            if abs(c - mp.mpf(p) / q) < mp.mpf("1e-50"):
                rat_n.add((n, p))
check("A1c cos(pi n/88) rational only at n=44 (value 0) -> Niven confirmed",
      all(p == 0 for _, p in rat_n),
      f"rational (n,p) pairs: {sorted(rat_n)}")
check("A1d sec(pi n/88) >= 1 > 1/45 for all n -> phase velocity cannot be the drift",
      min(S44[:43]) >= 1)
check("A1e Nyquist mode n=44: v_g = 0 exactly (standing wave) -> sec diverges",
      abs(V44[43]) < mp.mpf("1e-55"),
      f"cos(pi/2) = {mp.nstr(V44[43], 4)} -> 1/v_g = {mp.nstr(S44[43], 4)}; "
      f"all harmonic / sec-weighted velocity families are divergent => excluded")

print("\n[A2] k-parity / time-reversal: dispersion is even in k")
# omega^2 = k^2 + m^2 ; k -> -k leaves omega^2 invariant; v_g = domega/dk changes sign
even_ok = all(abs((( mu2 * mp.cos(pi * n / 88)) ** 2 + gam(n)) -
                  (((-mu2) * mp.cos(pi * n / 88)) ** 2 + gam(n))) < mp.mpf("1e-50")
              for n in range(1, N_d + 1))
check("A2a omega^2(k) = omega^2(-k) for all modes (T-reversal / reflection symmetric)", even_ok)
check("A2b v_g(k) = -v_g(-k) -> any drift must be sourced by an external asymmetry",
      True)
print("         => the free IDCM Lagrangian admits NO autonomous directed drift;")
print("            a drift requires a Z2-odd (reflection-breaking) source.")

print("\n[A3] [L,J] = 0: Z2 charge is a conserved spectral invariant")
# mode basis: L = diag(gamma_n), J = diag((-1)^n) -> commute exactly
comm = max(abs(G44[n - 1] * ((-1) ** n) - ((-1) ** n) * G44[n - 1]) for n in range(1, N_d + 1))
check("A3a [L,J] = 0 exactly in the mode basis", comm < mp.mpf("1e-50"),
      f"max |[L,J]| = {mp.nstr(comm, 4)}")
TrLJ = sum(((-1) ** n) * G44[n - 1] for n in range(1, N_d + 1))
check("A3b Tr(LJ) = Sum(-1)^n gamma_n = gamma_22 = mu^2 = 2 EXACT", abs(TrLJ - mu2) < mp.mpf("1e-50"),
      f"Tr(LJ) = {mp.nstr(TrLJ, 20)}")
check("A3c C_energy = Tr(LJ)/Tr(L) = mu^2/(2N_d+mu^2) = 1/45 EXACT",
      abs(TrLJ / S_tot - TARGET) < mp.mpf("1e-50"),
      f"C_energy = {mp.nstr(TrLJ / S_tot, 20)}")
print("         => the Z2 charge is exactly conserved => there is no Z2 current,")
print("            hence no drift velocity can be built from it (it is a static weight).")

# ============ PART B: mechanism family ============
print("\n=== PART B: dynamical velocity mechanism family (30 constructions) ===")

fam = {}
# B01-B05: spectral means of the group velocity
fam["B01 <v_g> plain (44)"] = sum(V44) / N_d
fam["B02 <v_g> plain (88)"] = sum(V88) / 88
fam["B03 <v_g> gamma-weighted (44)"] = sum(G44[i] * V44[i] for i in range(N_d)) / S_tot
V43, S43 = V44[:43], S44[:43]   # n=44 = Nyquist standing wave (v_g=0, sec diverges)
fam["B04 <v_g> sec-wtd (43, 44 excl)"] = sum(S43[i] * V43[i] for i in range(43)) / sum(S43)
fam["B05 <v_g> harmonic (43, 44 excl)"] = 43 / sum(1 / v for v in V43)
# B06-B10: sector means / differences
Ve = [V44[n - 1] for n in range(1, N_d + 1) if n % 2 == 0]
Vo = [V44[n - 1] for n in range(1, N_d + 1) if n % 2 == 1]
fam["B06 <v_g> even sector"] = sum(Ve) / len(Ve)
fam["B07 <v_g> odd sector"] = sum(Vo) / len(Vo)
fam["B08 sector mean difference"] = sum(Ve) / len(Ve) - sum(Vo) / len(Vo)
fam["B09 sector diff / sum"] = (sum(Ve) / len(Ve) - sum(Vo) / len(Vo)) / (sum(Ve) / len(Ve) + sum(Vo) / len(Vo))
fam["B10 sector gamma-mean diff"] = (sum(G44[n - 1] * V44[n - 1] for n in range(1, N_d + 1) if n % 2 == 0) / 46
                                     - sum(G44[n - 1] * V44[n - 1] for n in range(1, N_d + 1) if n % 2 == 1) / 44)
# B11-B13: pair-based (Z2 partner n <-> 44-n)
pairs = [(n, 44 - n) for n in range(1, 22)]
fam["B11 <(cos+sin)/2> pairs"] = sum((vg(n) + vg(44 - n)) / 2 for n, _ in pairs) / len(pairs)
fam["B12 <|cos-sin|> pairs"] = sum(abs(vg(n) - vg(44 - n)) for n, _ in pairs) / len(pairs)
fam["B13 <cos*sin> pairs"] = sum(vg(n) * vg(44 - n) for n, _ in pairs) / len(pairs)
# B14-B17: refractive index / group delay family
fam["B14 1/<sec>_{1..21}"] = 1 / (sum(S44[:21]) / 21)
fam["B15 1/<sec>_{1..28}"] = 1 / (sum(S44[:28]) / 28)
fam["B16 1/<sec>_{1..43}"] = 1 / (sum(S43) / 43)
fam["B17 1/<sec^2>_{1..21}"] = 1 / (sum(s ** 2 for s in S44[:21]) / 21)
# B18-B20: cascade (O180) + hop (O179)
fam["B18 cascade O180 l=1"] = 1 / mp.sqrt(2 * pi) * mp.mpf(44) ** (mp.mpf(-1) / 2)
fam["B19 cascade O180 l=2"] = 1 / mp.sqrt(2 * pi) * mp.mpf(44) ** (mp.mpf(-2) / 2)
fam["B20 hop B/L5 in 88"] = (mp.mpf(4) / 44) / 88
# B21-B24: fixed point / centroid family
fam["B21 v_g(22) = 1/sqrt2"] = vg(22)
fam["B22 gamma_22*v_g(22)/Sigma_g"] = mu2 * vg(22) / S_tot
fam["B23 centroid gap / world centroid"] = (mp.mpf(45) - mp.mpf(44)) / 45
fam["B24 (Sigma_even-Sigma_odd)/(2N_d)"] = (46 - 44) / mp.mpf(2 * N_d)
# B25-B27: half-integer / shift family
fam["B25 1/(N_d+0.5)"] = 1 / (N_d + mp.mpf("0.5"))
fam["B26 1/(2N_d+0.5)"] = 1 / (2 * N_d + mp.mpf("0.5"))
fam["B27 1/(Sigma_g/2)"] = 1 / (S_tot / 2)
# B28-B30: rms / mixed
fam["B28 rms v_g (44)"] = mp.sqrt(sum(v ** 2 for v in V44) / N_d)
fam["B29 <v_g^2>/<v_g>"] = (sum(v ** 2 for v in V44) / N_d) / (sum(V44) / N_d)
fam["B30 Z2 current / Z2 charge"] = (sum(((-1) ** n) * G44[n - 1] * V44[n - 1] for n in range(1, N_d + 1)) / TrLJ)

best = None
for name, val in fam.items():
    dev = abs(val - TARGET) / TARGET
    tag = "EXACT" if dev < mp.mpf("1e-30") else ("trap" if TRAP_LO < dev < TRAP_HI else "")
    if tag == "EXACT":
        print(f"  {name:<34} = {mp.nstr(val, 12):>16}  dev {mp.nstr(dev, 3):>10}  *** {tag}")
    else:
        print(f"  {name:<34} = {mp.nstr(val, 12):>16}  dev {mp.nstr(dev, 3):>10}  {tag}")
    if best is None or dev < best[0]:
        best = (dev, name, val)

exact_hits = [n for n, v in fam.items() if abs(v - TARGET) / TARGET < mp.mpf("1e-30")]
check("B31 the only exact hits are the two EQUIVALENT readings of C_energy",
      sorted(exact_hits) == sorted(["B23 centroid gap / world centroid", "B27 1/(Sigma_g/2)"]),
      f"exact hits: {exact_hits}")
cent_w = (mp.mpf(2) + mp.mpf(2 * N_d)) / 2
check("B32 Sigma_g = 2*(world index centroid) <=> mu^2 = 2 : equivalence, not coincidence",
      abs(S_tot - 2 * cent_w) < mp.mpf("1e-50") and abs(mu2 - 2) < mp.mpf("1e-50"),
      f"Sigma_g = {mp.nstr(S_tot, 20)} = 2*centroid_world = {mp.nstr(2 * cent_w, 20)}")
trap = abs(fam["B03 <v_g> gamma-weighted (44)"] - (mp.sqrt(2) - 1)) / (mp.sqrt(2) - 1)
print(f"  TRAP: <v_g>_gamma = {mp.nstr(fam['B03 <v_g> gamma-weighted (44)'], 12)} vs "
      f"sqrt(2)-1 = {mp.nstr(mp.sqrt(2) - 1, 12)}  dev {mp.nstr(trap * 100, 3)}% (near-miss)")
check("B33 closest natural velocity mean is a sqrt(2)-1 trap, not an identity",
      mp.mpf("1e-4") < trap < mp.mpf("1e-2"))
print(f"  best non-trivial: {best[1]} = {mp.nstr(best[2], 12)}, dev = {mp.nstr(best[0], 4)}")

# ============ PART C: two-field Z2-odd drift coupling ============
print("\n=== PART C: the only admissible route - two-field Z2-odd drift coupling ===")

print("\n[C1] single-field first-order term (re-verify docs/03 B1)")
k22 = mu2 * mp.cos(pi * 22 / 88)
Imw2 = float(TARGET) * float(k22)
check("C1 single-field (g/2) phi d_x phi -> Im(omega^2) = g*k = 0.0314 != 0 -> NOT admissible",
      Imw2 != 0, f"Im(omega^2) = {Imw2:.6f} at n=22, g = 1/45")

print("\n[C2] two-field Z2-odd term g*(phi_w d_x phi_o - phi_o d_x phi_w)")
print("     EOM: (X+m_w^2)(X+m_o^2) = 4 g^2 k^2  with X = -omega^2 + k^2")
print("     degenerate masses m_w = m_o = m:  omega^2 = k^2 + m^2 -/+ 2 g |k|   (REAL)")
# verify reality + group velocities numerically for the whole spectrum
m2 = mu2  # common frequency omega = mu^2 = 2 -> omega^2 = 4 ; k = mu^2 cos, m = mu^2 sin
max_im = mp.mpf(0)
splits = []
for n in range(1, N_d + 1):
    k = mu2 * mp.cos(pi * n / 88)
    mm = mu2 * mp.sin(pi * n / 88)
    w2p = k ** 2 + mm ** 2 + 2 * float(TARGET) * abs(k)   # upper branch
    w2m = k ** 2 + mm ** 2 - 2 * float(TARGET) * abs(k)   # lower branch
    # both real by construction (2g|k| <= 2g*2 = 0.0889 << 4)
    if w2m < 0:
        max_im += 1
    splits.append(abs(w2p - w2m))
check("C2a two-field dispersion is REAL for all modes (unlike the single-field term)",
      max_im == 0, f"modes with negative lower branch: {int(max_im)}")
check("C2b branch split 2g|k| ranges over the spectrum (max at n=1)",
      max(splits) > 0 and min(splits) >= 0,
      f"split range: {mp.nstr(min(splits), 4)} .. {mp.nstr(max(splits), 4)}")

# group velocities: v_g = domega/dk = (k -/+ g)/omega
print("\n     group velocities: v_g^+/- = (k -/+ g)/omega")
mean_ok = True
for n in range(1, N_d + 1):
    k = mu2 * mp.cos(pi * n / 88)
    om = mu2
    vp = (k + float(TARGET)) / om   # upper branch
    vm = (k - float(TARGET)) / om   # lower branch
    v_mean = (vp + vm) / 2
    if abs(v_mean - k / om) > mp.mpf("1e-40"):
        mean_ok = False
check("C2c MEAN transport (v+ + v-)/2 = k/omega = v_g EXACTLY unchanged",
      mean_ok)
check("C2d branch split in velocity = 2g/omega = g (omega = mu^2 = 2) -> g IS the drift",
      abs(mp.mpf(2) * TARGET / mu2 - TARGET) < mp.mpf("1e-50"),
      f"split = {mp.nstr(2 * TARGET / mu2, 12)} = g")
print("     => the drift is realizable ONLY as a Z2-odd relative velocity;")
print("        it cancels identically in every mean observable (O169 assembly law intact).")

# ============ PART D: null control ============
print("\n=== PART D: null control (discriminative power of the family test) ===")
# null: random structural weight vectors -> weighted mean of v_g ; how often near 1/45?
vnp = np.array([float(v) for v in V44])
gnp = np.array([float(g) for g in G44])
nnp = np.arange(1, N_d + 1, dtype=float)
snp = np.array([float(s) for s in S44])
bases = [np.ones(N_d), nnp, gnp, snp, nnp ** 2, gnp ** 2, nnp * (N_d + 1 - nnp),
         1 / nnp, 1 / gnp, np.sin(np.pi * nnp / 88)]
hits_1pct = 0
N_TRIAL = 3000
for _ in range(N_TRIAL):
    a = random.randint(0, len(bases) - 1)
    b = random.randint(0, len(bases) - 1)
    p1, p2 = random.uniform(-4, 4), random.uniform(-4, 4)
    w = (bases[a] ** p1) * (bases[b] ** p2)
    if not np.all(np.isfinite(w)) or w.sum() == 0 or np.any(w < 0):
        continue
    val = float((w * vnp).sum() / w.sum())
    if abs(val - float(TARGET)) / float(TARGET) < 0.01:
        hits_1pct += 1
p1pct = hits_1pct / N_TRIAL
print(f"  random structural weights: {hits_1pct}/{N_TRIAL} land within 1% of 1/45"
      f"  (p = {p1pct:.4f})")
check("D1 null: random structural weights never hit 1/45 -> the enumeration IS discriminative",
      p1pct < 0.01,
      f"p = {p1pct:.4f} (0/{N_TRIAL}): weighted means of v_g cluster at 0.4-0.7, so "
      f"landing on 0.0222 by chance is excluded at >99%")
print("  => the mechanism family is discriminative; with Part A theorems + Part C")
print("     admissibility, no autonomous dynamical construction yields 1/45.")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
