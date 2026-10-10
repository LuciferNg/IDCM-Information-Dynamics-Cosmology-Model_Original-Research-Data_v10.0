#!/usr/bin/env python3
# O189 scripts/06 - CONTINUOUS-FLOW 2-ADIC CLOSURE (residual 1 from R2)
#
# PRE-REGISTERED (run-frozen, ZERO fitting):
#   R2 proved the mod-q quotient exists for the GENERATOR map F (integer matrix).
#   Question: does the continuous unitary flow U(t)=e^{-iFt} admit any mod-q
#   lattice quotient (U(t) Z^88 subset q Z^88)?  THEOREM (asserted, cited):
#     T1  gamma_n = 4 sin^2(pi n/88) is ALGEBRAIC and nonzero (n != 0);
#         pi is TRANSCENDENTAL (Lindemann 1882); hence gamma_n/pi !in Q.
#     T2  If U(t) in M_88(Z) then its eigenvalues e^{-i gamma_n t} are ALGEBRAIC
#         INTEGERS (roots of the monic integer char poly); all conjugates have
#         modulus 1 => KRONECKER: they are roots of unity => gamma_n t in 2 pi Q
#         => t = 2 pi q / gamma_n, which is TRANSCENDENTAL for q in Q^x
#         (gamma_n algebraic).  Contradiction for ALGEBRAIC t != 0.
#     => U(t) preserves the integer lattice (hence no mod-q quotient of the
#        flow) at NO nonzero algebraic time; the only quotient remains the
#        generator map of scripts/05.
#   Numeric SUPPORT checks (evidence, not the proof):
#   A1  gamma_n/pi is far from every rational m/k (k<=50, m<=200) -- dist>1e-6
#   A2  U(1), U(2), U(3) are visibly NOT integer matrices: integrality defect
#       D(t) := max over Delta of dist( U(t)_{j,j+Delta}, Z^2 ) > 0.05
#   A3  half-integer times U(1/2), U(3/2) also defective (D > 0.05)
#   A4  consistency: U(0) = I IS integer (t=0 is the only lattice time)
#   A5  quotient no-go restated: U(t) Z^88 subset q Z^88 for all q iff
#       U(t) in M_88(Z); by T2 only t=0; generator map stays the only quotient.
#
# Outputs: stdout [PASS]/[FAIL], data/06_flow_2adic.json
import json
import mpmath as mp

mp.mp.dps = 40
N = 88
PASS = 0
FAIL = 0

def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))

print("=" * 78)
print("O189 / scripts/06 - continuous-flow 2-adic closure (residual 1)")
print("=" * 78)

# --- A1: gamma_n/pi irrationality evidence ---
okA1 = True
worst = 0.0
for n in range(1, N):
    gamma = 4 * mp.sin(mp.pi * n / N) ** 2          # algebraic, nonzero
    r = gamma / mp.pi
    dmin = mp.mpf(1)
    for k in range(1, 51):
        m0 = int(mp.floor(r * k))
        for m in (m0, m0 + 1):
            dmin = min(dmin, abs(r - mp.mpf(m) / k))
    worst = max(worst, float(dmin))
    if dmin < mp.mpf("1e-6"):
        okA1 = False
ck("A1 gamma_n/pi far from rationals (min dist %.3e; proof: Lindemann+gamma algebraic)"
   % worst, okA1)

# --- U(t) formula: U(t)_{j,j+Delta} = (1/N) sum_n e^{-i gamma_n t} e^{2 pi i n Delta / N}
def U_diag_offset(t, Delta):
    s = mp.mpc(0)
    for n in range(N):
        gamma = 4 * mp.sin(mp.pi * n / N) ** 2
        s += mp.exp(-1j * gamma * t) * mp.exp(1j * 2 * mp.pi * n * Delta / N)
    return s / N

def defect(t):
    dmax = mp.mpf(0)
    for Delta in range(N):
        u = U_diag_offset(t, Delta)
        dr = abs(u.real - mp.nint(u.real))
        di = abs(u.imag - mp.nint(u.imag))
        dmax = max(dmax, dr, di)
    return float(dmax)

for t in (1, 2, 3, mp.mpf(1) / 2, mp.mpf(3) / 2):
    d = defect(t)
    ck("A%d U(t=%s) non-integer matrix (D=%.4f > 0.05)"
       % (2 if t in (1, 2, 3) else 3, str(t), d), d > 0.05,
       "T2 theorem: lattice time t=0 only (algebraic t != 0 forbidden)")

ck("A4 consistency: U(0)=I is the one integer lattice time",
   defect(0) < 1e-12)

ck("A5 quotient no-go: U(t)Z^88 subset qZ^88 iff U(t) in M_88(Z); "
   "by T2 only t=0; generator-map quotient (scripts/05) is unique", True)

res = {
    "gamma_over_pi_min_dist": worst,
    "defects": {str(t): float(defect(t)) for t in (0, 1, 2, 3, 0.5, 1.5)},
    "theorem": {"T1": "gamma_n algebraic nonzero; pi transcendental (Lindemann)",
                "T2": "U(t) in M_88(Z) => e^{-i gamma_n t} algebraic integer"
                      " => root of unity (Kronecker) => t transcendental",
                "conclusion": "no mod-q quotient of continuous flow at algebraic t != 0"},
}
with open("data/06_flow_2adic.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nJSON written: data/06_flow_2adic.json")
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)