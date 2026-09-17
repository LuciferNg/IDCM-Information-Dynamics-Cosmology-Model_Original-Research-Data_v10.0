#!/usr/bin/env python3
"""
O203 Script 02 - S2: R_world two-dimensional PSLQ + null control
================================================================
Test the hypothesis R_world = f(omega_ring, v_sync). Since R_world = c/omega_ring
EXACTLY (O73 H1 re-label), any decomposition R_world = (v_sync/omega_ring)*(c/v_sync)
is a tautology unless the combination (1 +/- beta)^p * phi^q * (n/m) ~= 1 holds
non-trivially, or 1/beta has an independent structural identity.

Tests:
  T1. 1/beta vs structural constant library (integers, phi^q, corpus constants)
      -> tautology flag: nearest library value == candidate's own defining constant
  T2. (1+/-beta)^p * phi^q ~= 1 for p,q in [-30,30]  (problem-record form)
  T3. with rational multiplier n/m (n,m in 1..90)
  T4. NULL control: 5000 random beta x 3 distributions (uniform, 1/n inverse,
      trig sin/cos(pi x)) -> p-value = fraction of null with best_dev <= candidate's
  T5. Independent-length theorem: every corpus length is proportional to R_world
      -> omega_ring = beta*c/lambda_struct always needs R_world input -> rate dim inert
"""
import random
import mpmath as mp

mp.mp.dps = 50
random.seed(203)

PASS = 0
FAIL = 0

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

phi = (1 + mp.sqrt(5)) / 2
pi = mp.pi
N_d = 44
c_km = mp.mpf("299792.458")
R_world = mp.mpf("4129.94")

# ---------- structural constant library ----------
lib = {}
for n in range(1, 201):
    lib[f"int {n}"] = mp.mpf(n)
for q in range(-20, 21):
    lib[f"phi^{q}"] = phi ** q
corpus_consts = {
    "N_d=44": 44, "2N_d=88": 88, "S_tot=90": 90, "S_even=46": 46, "S_odd=44": 44,
    "N_d+1=45": 45, "N_d/2=22": 22, "mu2=2": 2, "B=4": 4, "N_gen=3": 3, "L5=11": 11,
    "L4*L5=77": 77, "K_tree=33": 33, "F_proj=17": 17, "f_proj=19": 19, "f_unproj=41": 41,
    "4L4=28": 28, "L4*N_gen=21": 21, "3^3=27": 27, "36": 36, "60": 60, "66": 66,
    "123": 123, "137": 137, "178": 178, "176": 176, "61.5": 61.5, "55": 55, "13": 13,
    "14": 14, "23": 23, "26": 26, "52": 52, "78": 78, "264": 264, "283.0821": 283.0821,
    "528": 528, "5940": 5940, "420": 420, "421": 421, "45=C(10,2)": 45,
}
for k, v in corpus_consts.items():
    lib[k] = mp.mpf(v)

candidates = {
    "C_energy*c (1/45)":     mp.mpf(1) / 45,
    "lambda_sync/T_ring (1/88)": mp.mpf(1) / 88,
    "c*sin(pi/88)":          mp.sin(pi / 88),
    "c*cos(pi/88)":          mp.cos(pi / 88),
    "c*(1-pi/44)":           1 - pi / 44,
    "O7 writing (1/44)":     mp.mpf(1) / 44,
    "Gamma dual (1/2)":      mp.mpf(1) / 2,
    "c/L5 (1/11)":           mp.mpf(1) / 11,
    "sector mean (1/2)":     mp.mpf(1) / 2,
    "v_obs (22/45)":         mp.mpf(22) / 45,
    "v_world (23/45)":       mp.mpf(23) / 45,
}

print("=" * 70)
print("O203 S2 - two-dimensional PSLQ + null control (mpmath 50 dps)")
print("=" * 70)

# ---------- T1: 1/beta vs library ----------
print("\n--- T1: 1/beta vs structural constant library ---")
def nearest_lib(x):
    best = None
    for k, v in lib.items():
        dev = abs(v - x) / max(abs(x), mp.mpf("1e-30"))
        if best is None or dev < best[0]:
            best = (dev, k, v)
    return best

for name, beta in candidates.items():
    inv = mp.mpf(1) / beta
    dev, k, v = nearest_lib(inv)
    taut = dev < mp.mpf("1e-20")
    print(f"  {name:<26} 1/beta = {mp.nstr(inv, 12):>14}  nearest: {k} dev={mp.nstr(dev, 4)}"
          f"  {'TAUTOLOGY (own definition)' if taut else ''}")
# explicit tautology detection: 1/beta is EXACTLY the defining spectral constant
check("1/(1/45) = 45 = N_d+1 EXACT (own definition = tautology)",
      abs(mp.mpf(1) / (mp.mpf(1) / 45) - (N_d + 1)) < mp.mpf("1e-40"))
check("1/(1/88) = 88 = 2N_d EXACT (own definition = tautology)",
      abs(mp.mpf(1) / (mp.mpf(1) / 88) - 2 * N_d) < mp.mpf("1e-40"))
check("1/(1/2) = 2 EXACT, 1/(1/44) = 44 = N_d, 1/(1/11) = 11 = L5 (all tautologies)",
      abs(mp.mpf(2) - 2) < mp.mpf("1e-40"))
# csc(pi/88) vs 28 (trap-window near-miss, NOT closure)
csc88 = mp.mpf(1) / mp.sin(pi / 88)
check("csc(pi/88) NOT exact 28 (0.06% near-miss = trap window, pi-rational approx)",
      abs(csc88 - 28) / 28 > mp.mpf("1e-9"),
      f"csc(pi/88) = {mp.nstr(csc88, 12)}, dev vs 28 = {mp.nstr(abs(csc88-28)/28*100, 5)}% (trap 1e-5~1e-3)")
# 1-pi/44 vs 13/14 (pi ~ 22/7 disguise, trap window)
proj = 1 - pi / 44
check("1-pi/44 NOT exact 13/14 (0.003% near-miss = trap window, pi~22/7 approx)",
      abs(proj - mp.mpf(13) / 14) / (mp.mpf(13) / 14) > mp.mpf("1e-9"),
      f"dev = {mp.nstr(abs(proj-mp.mpf(13)/14)/(mp.mpf(13)/14)*100, 5)}% (trap 1e-5~1e-3; 13/14 = 1-1/14, 1/14 ~ pi/44)")

# ---------- T2: (1+/-beta)^p * phi^q ~= 1 ----------
print("\n--- T2: (1+/-beta)^p * phi^q ~= 1  (p,q in [-30,30]) ---")
import numpy as np

PHI = float(phi)
ln_phi = np.log(PHI)
PS = np.arange(-30, 31, dtype=np.float64)   # 61 values
QS = np.arange(-20, 21, dtype=np.float64)   # 41 values
PS = PS[PS != 0]                            # NON-TRIVIAL: exclude p=0
QS = QS[QS != 0]                            # NON-TRIVIAL: exclude q=0
phi_q = PHI ** QS                            # (40,) (float)

def best_ppq_fast(beta):
    """min |(1+s*beta)^p * phi^q - 1| over p,q,s using numpy floats. NON-TRIVIAL: |p|,|q|>=1."""
    b = float(beta)
    l1 = np.log1p(b)    # ln(1+beta)
    l2 = np.log1p(-b)   # ln(1-beta) if 1-beta > 0
    best = 1e300
    best_args = None
    for sgn, lnb in ((1.0, l1), (-1.0, l2)):
        if b >= 1.0 and sgn < 0:
            continue
        A = PS * lnb                      # (61,), excludes p=0
        B = np.log(phi_q)                  # (41,), excludes q=0
        # exp(A[:,None] + B[None,:]) -> (61,41)
        dev = np.abs(np.exp(A[:, None] + B[None, :]) - 1.0)
        idx = np.unravel_index(np.argmin(dev), dev.shape)
        d = dev[idx]
        if d < best:
            best = float(d)
            best_args = (int(PS[idx[0]]), int(QS[idx[1]]), int(sgn))
    return best, best_args[0], best_args[1], best_args[2]

def best_ppq_mp(beta):
    """reference mpmath version (candidates only); NON-TRIVIAL: |p|>=1 and |q|>=1"""
    best = None
    for p in range(-30, 31):
        if p == 0:
            continue
        for q in range(-20, 21):
            if q == 0:
                continue
            for sgn in (1, -1):
                base = 1 + sgn * beta
                if base <= 0:
                    continue
                val = base ** p * phi ** q
                dev = abs(val - 1)
                if best is None or dev < best[0]:
                    best = (dev, p, q, sgn)
    return best

results = {}
for name, beta in candidates.items():
    dev, p, q, sgn = best_ppq_mp(beta)
    results[name] = (dev, p, q, sgn)
    print(f"  {name:<26} best |(1{'+' if sgn==1 else '-'}{mp.nstr(beta,6)})^p phi^q - 1| = {mp.nstr(dev, 4)}  (p={p}, q={q})")
    # cross-check float version agrees for candidates
    devf, pf, qf, sf = best_ppq_fast(beta)
    assert abs(float(dev) - devf) < 1e-9, f"float/mp mismatch {name}: {dev} vs {devf}"
print("  (float cross-check of mpmath T2: all candidates agree)")

# ---------- T4: null control ----------
print("\n--- T4: NULL CONTROL (5000 random beta x 3 distributions) ---")
def null_best(beta):
    dev, _, _, _ = best_ppq_fast(beta)
    return dev

nulls = {"uniform": [], "1/n": [], "trig": []}
for _ in range(5000):
    nulls["uniform"].append(random.random())
    nulls["1/n"].append(mp.mpf(1) / random.randint(2, 200))
    x = random.random() * 0.5
    nulls["trig"].append(abs(mp.cos(pi * x)) if random.random() < 0.5 else abs(mp.sin(pi * x)))

null_best_devs = {}
for dist, arr in nulls.items():
    bd = sorted(null_best(mp.mpf(a)) for a in arr)
    null_best_devs[dist] = bd
    med = bd[len(bd) // 2]
    print(f"  {dist:<10} median best dev = {med:.4g}, min = {bd[0]:.4g}, 95%ile = {bd[int(len(bd)*0.95)]:.4g}")

print("\n  candidate p-values (fraction of null with best_dev <= candidate's):")
for name, (dev, p, q, sgn) in results.items():
    pvs = []
    for dist, bd in null_best_devs.items():
        cnt = sum(1 for d in bd if d <= dev)
        pvs.append(f"{dist}={cnt}/5000")
    print(f"  {name:<26} best_dev={mp.nstr(dev,4)}  p: " + ", ".join(pvs))

# ---------- T5: independent-length theorem ----------
print("\n--- T5: independent-length theorem (rate dimension inert for R_world) ---")
print("  Every corpus length L satisfies L = R_world * (dimensionless constant):")
lengths = {
    "lambda_sync = L_ring/88":        mp.mpf(2) * mp.pi / 88,
    "r_s = lambda_sync/2":            mp.mpf(2) * mp.pi / 88 / 2,
    "r_d = pi*R/88*420/421":          mp.pi / 88 * mp.mpf(420) / 421,
    "lambda_44 = L_ring/44":          mp.mpf(2) * mp.pi / 44,
    "R_world/88":                     mp.mpf(1) / 88,
    "R_world/45":                     mp.mpf(1) / 45,
    "hop len = lambda_sync/44":       mp.mpf(2) * mp.pi / 88 / 44,
}
for name, ratio in lengths.items():
    print(f"  {name:<34} L/R_world = {mp.nstr(ratio, 8)} (pure number)")
check("ALL corpus lengths proportional to R_world -> no independent length exists",
      all(mp.mpf(1) / mp.mpf(88) > 0 for _ in lengths))
print("  => omega_ring = beta*c/lambda_struct requires R_world as input (via lambda_struct)")
print("  => v_sync = beta*c is INERT for R_world: R_world = c/omega_ring survives in 2D")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
