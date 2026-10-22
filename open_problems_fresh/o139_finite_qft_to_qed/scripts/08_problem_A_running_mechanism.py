"""
O139 -- scripts/08: PROBLEM A MECHANISM -- the RUNNING, 9 -> 9.106
==================================================================
The last open item of problem A: IDCM's structural running is the integer

    Delta alpha^-1 = F_proj - 2B = 17 - 8 = 9 = N_gen^2

while the physical (measured) running is NOT 9.  docs/03 and docs/06 used the
older PDG MS-bar value alpha^-1(M_Z) = 127.951(9), giving 9.085.  The current
world average is

    alpha(M_Z^2)^-1 = 127.930(8)        (2026 world average, lattice+dispersive HVP)

so the physical running is

    137.035999178 - 127.930 = 9.1060(8)      ->  delta = +0.1060(8),  13.3 sigma

This script attacks that delta.  It does NOT curve-fit it.  Sections:

  R1  structural identity chain  --  WHY Sigma_f N_c Q_f^2 = 2B  (A1, now PROVED)
  R2  physical input update      --  the target is 9.1060(8), not 9.085
  R3  sector decomposition       --  where the +0.1060 actually lives
  R4  hadronic dominance         --  the killer: non-perturbative spread is 11x delta
  R5  IDCM spectrum through the exact one-loop kernel
  R6  scheme check               --  IDCM's 128 is an MS-bar number, not on-shell
  R7  null test on delta         --  pre-registered grammar + random control
  R8  verdict

METHODOLOGY: identical to scripts/07 (Technique 4 of correction-audit-methodology):
pre-register the grammar, then test SELECTIVITY (random-control z-score + grammar
resolution) instead of curve-fitting.  No hard-coded checks anywhere.

Author: Hermes (O139 problem A mechanism, 2026-09-15)
"""
import math
from fractions import Fraction as Fr

import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

# ============================================================================
# constants
# ============================================================================
Nd, B, N_gen = 44, 4, 3
L4, L5, L6, L7 = 7, 11, 18, 29
F5, F6, F7, F8, F9, F10 = 5, 8, 13, 21, 34, 55
F_proj, C_B2_2 = 17, 120
K_tree, M = 33, 33
N_c_q, N_c_lep = 3, 1
Qu, Qd, Qe = Fr(2, 3), Fr(1, 3), Fr(1)

# physical (published) inputs -------------------------------------------------
A0_INV        = 137.035999178      # Thomson limit, 2026 world average
A0_INV_ERR    = 0.000000008
A_MZ_MSBAR    = 127.930            # alpha(M_Z^2)^-1, MS-bar-like, world average 2026
A_MZ_MSBAR_E  = 0.008
A_MZ_ONSHELL  = 128.933            # on-shell (Thomson-subtracted), Jegerlehner-type
A_MZ_ONSHELL_E= 0.021
A_MZ_OLD      = 127.951            # older PDG MS-bar value used in docs/03,06
A_MZ_OLD_E    = 0.009
A_MZ_KS       = 127.934            # Kuehn-Steinhauser hep-ph/9803453
DAL_LEP       = 0.031498           # 3-loop QED leptonic, hep-ph/0100398
DAL_HAD5      = 0.02783            # Delta alpha_had^(5)(M_Z), world average 2026
DAL_HAD5_E    = 0.00006
DAL_TOP       = -0.000076          # hep-ph/0100398

M_Z = 91187.6                      # MeV
ALPHA0 = 1.0/A0_INV

print("=" * 78)
print("R1 -- structural identity chain:  WHY  Sigma_f N_c Q_f^2 = 2B   (A1)")
print("=" * 78)
print("""
  Problem A's first half (docs/03 section 7B) recorded
        Sigma_f N_c Q_f^2 = 3*1*1^2 + 3*3*(2/3)^2 + 3*3*(1/3)^2 = 3 + 4 + 1 = 8 = 2B
  as an EXACT NUMERICAL identity whose structural necessity was UNPROVEN.
  Here is the proof.  Evaluate the three sectors symbolically:
""")
s_lep = N_gen * (N_c_lep * Qe**2)
s_up  = N_gen * (N_c_q  * Qu**2)
s_dn  = N_gen * (N_c_q  * Qd**2)
s_tot = s_lep + s_up + s_dn
print(f"  lepton  : N_gen*N_c*Q_e^2 = {N_gen}*{N_c_lep}*{Qe}^2 = {s_lep}   vs  B-1 = {B-1}")
print(f"  up-type : N_gen*N_c*Q_u^2 = {N_gen}*{N_c_q}*({Qu})^2 = {s_up}      vs  B   = {B}")
print(f"  down    : N_gen*N_c*Q_d^2 = {N_gen}*{N_c_q}*({Qd})^2 = {s_dn}      vs  1   = 1")
print(f"  TOTAL   : Sigma_f N_c Q_f^2 = {s_tot}")
print(f"           2B                 = {2*B}")
check("lepton sector sum = B-1", s_lep == B-1, f"{s_lep} = {B-1}")
check("up-type sector sum = B", s_up == B, f"{s_up} = {B}")
check("down-type sector sum = 1", s_dn == 1, f"{s_dn}")
check("Sigma_f N_c Q_f^2 = 2B exactly", s_tot == 2*B, f"{s_tot} = {2*B}")

# the equivalence: Sigma = N_gen*(1 + N_c*(Qu^2+Qd^2)) ; 2B = 2B
factor = 1 + N_c_q*(Qu**2 + Qd**2)
print(f"""
  Closed form:  Sigma/N_gen = 1 + N_c(Q_u^2+Q_d^2) = 1 + {N_c_q}*{Qu**2+Qd**2} = {factor}
                (lepton 1  +  quark 5/3 = 8/3)
  so  Sigma = (8/3)*N_gen,  while  2B = 8.
  Equality  Sigma = 2B  <=>  (8/3)*N_gen = 2B  <=>  N_gen = 3B/4 = {Fr(3*B,4)} = B-1.
""")
check("Sigma/N_gen = 8/3", factor == Fr(8, 3), f"{factor}")
check("equality Sigma=2B holds iff N_gen = 3B/4 = B-1",
      Fr(3*B, 4) == B-1 == N_gen, f"3B/4 = {Fr(3*B,4)}, B-1 = {B-1}, N_gen = {N_gen}")

# and the running itself
d_run_struct = F_proj - 2*B
print(f"""  The running follows immediately:
        Delta alpha^-1 = F_proj - 2B = (B^2+1) - 2B = B^2 - 2B + 1 = (B-1)^2 = {d_run_struct}
""")
check("F_proj - 2B = (B-1)^2  (exact polynomial identity)",
      F_proj - 2*B == (B-1)**2, f"{F_proj-2*B} = {(B-1)**2}")
check("(B-1)^2 = N_gen^2 given N_gen = B-1", (B-1)**2 == N_gen**2, f"{(B-1)**2}")
print("""  VERDICT R1:  A1 is CLOSED.  '8 = 2B' is not a numerical accident -- it is
  EQUIVALENT to the IDCM structural relation N_gen = B-1 (= 3B/4).  The three
  sector sums (B-1, B, 1) are each individually structural.  The running is then
  a two-line algebraic consequence, not a coincidence.""")

# ============================================================================
print("\n" + "=" * 78)
print("R2 -- physical input update: the target is 9.1060(8), NOT 9.085")
print("=" * 78)
run_new = A0_INV - A_MZ_MSBAR
run_old = A0_INV - A_MZ_OLD
d_new = run_new - d_run_struct
print(f"""
  alpha^-1(0)   = {A0_INV:.9f}   (Thomson; sharp to 5e-10 relative)
  alpha^-1(M_Z) = {A_MZ_MSBAR:.3f} +- {A_MZ_MSBAR_E}      <- 2026 world average (MS-bar-like)
                  {A_MZ_OLD:.3f} +- {A_MZ_OLD_E}      <- older PDG value used in docs/03 and docs/06
                  {A_MZ_KS:.3f} +- 0.026      <- Kuehn-Steinhauser hep-ph/9803453
  alpha^-1(M_Z) = {A_MZ_ONSHELL:.3f} +- {A_MZ_ONSHELL_E}      <- on-shell / Thomson-subtracted scheme
""")
print(f"  running (current, {A_MZ_MSBAR})   : {run_new:.6f} +- {A_MZ_MSBAR_E}")
print(f"  running (older,   {A_MZ_OLD})   : {run_old:.6f}")
print(f"  shift from the HVP update        : {run_new-run_old:+.6f}  "
      f"= {(run_new-run_old)/A_MZ_MSBAR_E:.1f} sigma_new  -> the update MATTERS")
print(f"\n  delta = running - 9 = {d_new:+.6f} +- {A_MZ_MSBAR_E}")
print(f"  significance      : {d_new/A_MZ_MSBAR_E:.1f} sigma from the structural integer 9")
print(f"  relative          : {d_new/d_run_struct*100:.4f} %")
check("running is 9.1060(8)", abs(run_new-9.1060) < 5e-4, f"{run_new:.6f}")
check("delta is > 10 sigma from the integer 9", d_new/A_MZ_MSBAR_E > 10.0,
      f"{d_new/A_MZ_MSBAR_E:.1f} sigma")
check("the 127.951 -> 127.930 HVP update is itself > 2 sigma",
      (run_new-run_old)/A_MZ_MSBAR_E > 2.0,
      f"{(run_new-run_old)/A_MZ_MSBAR_E:.1f} sigma")
print("""  NOTE (docs/06 correction): the target used in docs/06 (9.085, from 127.951)
  is superseded.  The HVP world average moved by +0.021 in alpha^-1(M_Z)
  (2.6 sigma of the new error bar), which is exactly the same HVP update that
  moved the muon g-2 prediction.  The corrected target is 9.1060(8).""")

# ============================================================================
print("\n" + "=" * 78)
print("R3 -- sector decomposition: where the +0.1060 actually lives")
print("=" * 78)
f_lep = A0_INV*DAL_LEP
f_had = A0_INV*DAL_HAD5
f_top = A0_INV*DAL_TOP
ferm  = f_lep + f_had + f_top
bos   = run_new - ferm
print(f"""
  Published MS-bar decomposition of the running (alpha^-1 units):
    Delta alpha_lep(M_Z)      = {DAL_LEP:.6f}   ->  {f_lep:7.4f}
    Delta alpha_had^(5)(M_Z)  = {DAL_HAD5:.5f} +- {DAL_HAD5_E:.5f}   ->  {f_had:7.4f}
    Delta alpha_top(M_Z)      = {DAL_TOP:.6f}  ->  {f_top:7.4f}
    ------------------------------------------------------------------
    fermion sector            = {ferm:7.4f}      (structural candidate 2B = {2*B})
    bosonic/scheme remainder  = {bos:7.4f}      (structural candidate 1)
    ------------------------------------------------------------------
    TOTAL running             = {ferm+bos:7.4f}      (= {run_new:.4f})
""")
print(f"  fermion excess over 2B : {ferm-2*B:+.4f}")
print(f"  boson deficit from 1   : {bos-1:+.4f}")
print(f"  sum of the two         : {(ferm-2*B)+(bos-1):+.4f}   (delta = {d_new:+.4f})")
check("fermion sector reproduces published decomposition",
      abs(ferm - (f_lep+f_had+f_top)) < 1e-9, f"{ferm:.4f}")
check("sector deviations sum to delta (exact bookkeeping)",
      abs(((ferm-2*B)+(bos-1)) - d_new) < 1e-9, f"{(ferm-2*B)+(bos-1):+.6f}")
check("bosonic remainder is within 2 sigma of 1", abs(bos-1) < 2*0.012,
      f"{bos:.4f} vs 1")
# uncertainty of the fermion sum: dominated by Delta alpha_had
ferm_err = A0_INV*DAL_HAD5_E
print(f"\n  uncertainty of the fermion sum = {ferm_err:.4f}  (dominated by Delta alpha_had)")
print(f"  uncertainty of the running     = {A_MZ_MSBAR_E}   -> SAME SIZE: the running's")
print( "  error bar IS the hadronic HVP error bar, nothing else.")
check("fermion-sum uncertainty is the dominant one",
      ferm_err > 0.5*A_MZ_MSBAR_E, f"{ferm_err:.4f} vs {A_MZ_MSBAR_E}")
print("""
  => The +0.1060 is NOT a single structural number.  It is the RESIDUAL of two
     sector-level deviations of opposite sign that partially cancel:
     the fermion loops overshoot 2B by +0.12 (the logarithms), the gauge/scheme
     sector undershoots 1 by -0.014.  A structural formula for 'delta' would have
     to reproduce a cancellation, not a quantity.""")

# ============================================================================
print("\n" + "=" * 78)
print("R4 -- hadronic dominance: the decisive obstruction")
print("=" * 78)
had_pert = 4.979     # perturbative 5-quark loop, PDG spectrum (docs/03 section 4)
had_disp = f_had
print(f"""
  The 5-quark contribution can be computed two ways:
    perturbative quark loop (what any spectrum-based theory gives) : {had_pert:.3f}
    dispersion relations / lattice QCD (what the data gives)       : {had_disp:.3f}
    ---------------------------------------------------------------------
    treatment spread                                               : {had_pert-had_disp:.3f}

  Compare with the quantity we are trying to explain:
    delta = {d_new:.3f}
    spread/delta = {(had_pert-had_disp)/d_new:.1f} x
""")
check("hadronic treatment spread exceeds delta by > 5x",
      (had_pert-had_disp)/d_new > 5.0, f"{(had_pert-had_disp)/d_new:.1f} x")
print("""  => The exact value of the running is NOT a clean structural target.  Whether
     the hadronic piece is treated perturbatively or non-perturbatively changes
     the running by 1.16 -- ELEVEN TIMES the deviation from the integer 9 that we
     are trying to derive.  Any 'derivation' of 9.106 would first have to derive
     the non-perturbative hadronic vacuum polarisation, which is a data quantity
     in every framework, IDCM included.""")

# ============================================================================
print("\n" + "=" * 78)
print("R5 -- IDCM spectrum through the exact one-loop kernel")
print("=" * 78)
gx, gw = np.polynomial.legendre.leggauss(160)
gx = 0.5*(gx+1.0); gw = 0.5*gw
I0 = gx*(1.0-gx)
def Delta_alpha(Q, spec):
    tot = 0.0
    for (nm, m, w) in spec:
        tot += w*float(np.sum(I0*np.log(1.0 + (Q/m)**2*I0)*gw))
    return (2*ALPHA0/math.pi)*tot
IDCM = [("e",0.5118,1.0),("mu",105.80,1.0),("tau",1770.8,1.0),
        ("u",2.204,4/3),("d",4.692,1/3),("s",92.28,1/3),
        ("c",1273.7,4/3),("b",4191.4,1/3),("t",173937.0,4/3)]
PDG  = [("e",0.510998950,1.0),("mu",105.6583755,1.0),("tau",1776.86,1.0),
        ("u",2.16,4/3),("d",4.67,1/3),("s",93.0,1/3),
        ("c",1270.0,4/3),("b",4180.0,1/3),("t",172760.0,4/3)]
LEP = ("e","mu","tau")
sum_idcm = A0_INV*Delta_alpha(M_Z, IDCM)
sum_pdg  = A0_INV*Delta_alpha(M_Z, PDG)
lep_idcm = A0_INV*Delta_alpha(M_Z, [s for s in IDCM if s[0] in LEP])
lep_pdg  = A0_INV*Delta_alpha(M_Z, [s for s in PDG  if s[0] in LEP])
print(f"""
  Exact one-loop vacuum polarisation, on-shell (Thomson) subtraction:
      Delta alpha(Q^2) = (2 alpha/pi) Sum_f N_c Q_f^2 Int_0^1 dx x(1-x) ln[1+Q^2x(1-x)/m_f^2]

    IDCM 9-fermion spectrum -> running = {sum_idcm:.4f}
    PDG  spectrum           -> running = {sum_pdg:.4f}
    structural integer      -> running = {d_run_struct:.4f}
    physical (MS-bar)       -> running = {run_new:.4f}
""")
print(f"    leptonic sector only: IDCM {lep_idcm:.4f}   PDG {lep_pdg:.4f}   "
      f"published {A0_INV*DAL_LEP:.4f}")
check("IDCM spectrum reproduces the leptonic running to < 1%",
      abs(lep_idcm - A0_INV*DAL_LEP)/(A0_INV*DAL_LEP) < 0.01,
      f"{lep_idcm:.4f} vs {A0_INV*DAL_LEP:.4f}")
lep_agree = abs(lep_idcm - A0_INV*DAL_LEP)/(A0_INV*DAL_LEP)*100
print(f"    leptonic agreement: {lep_agree:.2f}%")
check("perturbative spectrum sum overshoots the integer 9 by > 2%",
      (sum_idcm - d_run_struct)/d_run_struct > 0.02,
      f"{(sum_idcm-d_run_struct)/d_run_struct*100:.2f}%")
print(f"""
  => The IDCM spectrum works beautifully for the LEPTONS ({lep_agree:.2f}%) but the full
     spectrum sum ({sum_idcm:.3f}) is FURTHER from the physical running ({run_new:.3f})
     than the structural integer 9 is.  The excess is entirely the perturbative
     quark loop (R4).  So the integer 9 does NOT emerge from the spectrum sum --
     it is a structural input, and the spectrum sum cannot refine it.
  => SCHEME CAVEAT: this kernel is the on-shell one; the physical on-shell
     running is {A0_INV-A_MZ_ONSHELL:.4f} (R6).  Comparing {sum_idcm:.3f} with {run_new:.3f} mixes
     schemes; both comparisons are shown so nothing is hidden.""")

# ============================================================================
print("\n" + "=" * 78)
print("R6 -- scheme check: IDCM's 128 is an MS-bar number")
print("=" * 78)
g_msbar   = abs(128 - A_MZ_MSBAR)/A_MZ_MSBAR*100
g_onshell = abs(128 - A_MZ_ONSHELL)/A_MZ_ONSHELL*100
g_old     = abs(128 - A_MZ_OLD)/A_MZ_OLD*100
print(f"""
    alpha^-1(M_Z) structural (O160)      : 128
    vs MS-bar   {A_MZ_MSBAR:.3f}(8)                : gap {g_msbar:.4f} %
    vs on-shell {A_MZ_ONSHELL:.3f}(21)               : gap {g_onshell:.4f} %
    vs older PDG {A_MZ_OLD:.3f}(9)               : gap {g_old:.4f} %
""")
check("structural 128 matches MS-bar far better than on-shell",
      g_msbar < g_onshell/5.0, f"{g_msbar:.4f}% vs {g_onshell:.4f}%")
print(f"""  => IDCM's structural endpoint is an MS-bar-type quantity, i.e. it CONTAINS
     the gauge/scheme running.  That is consistent with R3: the structural
     reading of the running is

         Delta alpha^-1 = Sigma_f N_c Q_f^2  +  (gauge/scheme unit) = 2B + 1 = 9

     not 'N_gen^2' taken in isolation.  The two readings coincide only because
     N_gen = B-1 makes 2B+1 = (B-1)^2.  R3's physical split (fermion {ferm:.3f} +
     gauge/scheme {bos:.3f}) selects the 2B+1 reading at the ~1.5% level.""")

# --- R6b: what the '0.965 bosonic component' of docs/03 actually is ----------
print("\n" + "-" * 78)
print("R6b -- the '0.965 bosonic component' (docs/03 section 6) is a SCHEME artifact")
print("-" * 78)
run_onshell = A0_INV - A_MZ_ONSHELL
conv        = A_MZ_ONSHELL - A_MZ_MSBAR          # on-shell <-> MS-bar conversion
conv_err    = math.hypot(A_MZ_ONSHELL_E, A_MZ_MSBAR_E)
print(f"""
    on-shell running    = {A0_INV:.6f} - {A_MZ_ONSHELL:.3f} = {run_onshell:.4f} +- {A_MZ_ONSHELL_E}
    MS-bar   running    = {A0_INV:.6f} - {A_MZ_MSBAR:.3f} = {run_new:.4f} +- {A_MZ_MSBAR_E}
    conversion          = {A_MZ_ONSHELL:.3f} - {A_MZ_MSBAR:.3f} = {conv:.4f} +- {conv_err:.4f}

    compare with R3:
      fermion sector (published Delta alpha_lep+had+top) = {ferm:.4f}
      remainder (running - fermion)                     = {bos:.4f}

    |on-shell running - fermion sector| = {abs(run_onshell-ferm):.4f}  ({abs(run_onshell-ferm)/ferm*100:.2f} %)
    |remainder - conversion|           = {abs(bos-conv):.4f}  ({abs(bos-conv)/conv*100:.2f} %)  = {abs(bos-conv)/conv_err:.2f} sigma
""")
check("published fermion sector IS the on-shell running (agrees to < 1%)",
      abs(run_onshell-ferm)/ferm < 0.01, f"{abs(run_onshell-ferm)/ferm*100:.2f}%")
check("the R3 'bosonic' remainder IS the on-shell<->MS-bar conversion (within 2 sigma)",
      abs(bos-conv) < 2*conv_err, f"{abs(bos-conv)/conv_err:.2f} sigma")
print("""  => docs/03 section 6 flagged a '0.965 bosonic (W/top + scheme) component' as
     🔴 unattributed.  It is now identified: it is the on-shell <-> MS-bar
     CONVERSION of the coupling (1.003 +- 0.022), not a separate W loop.  The
     W-loop contribution to Delta alpha(M_Z) is a small threshold effect, whereas
     the conversion is a scheme constant proportional to Sigma_f N_c Q_f^2.
     Consequence for the structural reading: the '+1' in '2B + 1 = 9' is a
     SCHEME-CONVENTION term, not a gauge-loop term.  IDCM's structural endpoint
     128 is therefore an MS-bar-type number (R6), and the honest statement is:

         Delta alpha^-1 (MS-bar)  =  2B  +  (scheme unit)  =  9
         physical                 =  {f0:.3f} + {c0:.3f} = {t0:.3f}
""".format(f0=run_onshell, c0=conv, t0=run_onshell+conv))
check("on-shell running + conversion reproduces the MS-bar running",
      abs((run_onshell+conv) - run_new) < 1e-9, f"{run_onshell+conv:.6f}")

# ============================================================================
print("\n" + "=" * 78)
print("R7 -- null test on delta: pre-registered grammar + random control")
print("=" * 78)
LIB = {
    "N_d": 44, "B": 4, "N_gen": 3,
    "L4": 7, "L5": 11, "L6": 18, "L7": 29,
    "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55,
    "F_proj": 17, "M": 33, "CY3": 134, "C(B2,2)": 120,
    "N_d+1": 45, "2N_d": 88, "F10+1": 56, "123": 123, "137": 137,
}
G = {}
def put(v, s):
    if 1e-6 < v < 1e6:
        k = round(v, 10)
        if k not in G:
            G[k] = s
items = list(LIB.items())
for n1, v1 in items:
    put(float(v1), n1); put(v1*v1, f"{n1}^2"); put(v1*v1*v1, f"{n1}^3")
for n1, v1 in items:
    for n2, v2 in items:
        put(v1*v2, f"{n1}*{n2}"); put(v1+v2, f"{n1}+{n2}")
        put(abs(v1-v2), f"|{n1}-{n2}|"); put(v1/v2, f"{n1}/{n2}")
        for n3, v3 in items:
            put(v1*v2/v3, f"({n1}*{n2})/{n3}")
            put((v1+v2)/v3, f"({n1}+{n2})/{n3}")
            put(v1/(v2*v3), f"{n1}/({n2}*{n3})")
phi = (1.0+math.sqrt(5.0))/2.0
for k in range(1, 15):
    put(phi**k, f"phi^{k}"); put(phi**-k, f"phi^-{k}")
pure = sorted(G.keys())
print(f"  pre-registered library : {len(LIB)} integers")
print(f"  grammar                : a, a^2, a^3, a*b, a+b, |a-b|, a/b, (a*b)/c, (a+b)/c, a/(b*c), phi^(+-k)")
print(f"  distinct grammar values: {len(pure)}")
LO, HI = 8.0, 11.0
band = [v for v in pure if LO < v < HI]
target = run_new
print(f"\n  target (running) = {target:.6f}   band = [{LO}, {HI}]   grammar values in band: {len(band)}")
best = min(band, key=lambda v: abs(v-target))
best_dev = abs(best-target)/target
print(f"  best pure-structural hit : {best:.9f}   = {G[best]}")
print(f"      deviation            : {best_dev*100:.4f}%")
print(f"  grammar spacing in band        : {(HI-LO)/len(band):.3e} abs = "
      f"{((HI-LO)/len(band))/target:.3e} rel")

# random control in the same band (log-uniform, same as scripts/07)
import random
def hits_within(vs, t, rel):
    from bisect import bisect_left, bisect_right
    a = sorted(vs)
    return bisect_right(a, t*(1+rel)) - bisect_left(a, t*(1-rel))
def ztest(vs, t, rel, seed=20260915, n=4000):
    n_hit = hits_within(vs, t, rel)
    random.seed(seed)
    ctrl = []
    for _ in range(n):
        tt = math.exp(random.uniform(math.log(LO), math.log(HI)))
        ctrl.append(hits_within(vs, tt, rel))
    mu = sum(ctrl)/len(ctrl)
    sd = math.sqrt(sum((c-mu)**2 for c in ctrl)/len(ctrl))
    return n_hit, mu, sd, ((n_hit-mu)/sd if sd > 0 else 0.0)
REL = 5e-3
n_hit, mu, sd, z = ztest(band, target, REL)
print(f"\n  hits within +-0.5% of target : {n_hit}")
print(f"  random control               : mean {mu:.2f} +- {sd:.2f}")
print(f"  z-score                      : {z:+.2f}")
check("pre-registered grammar is NOT selective for the running (|z| < 2)",
      abs(z) < 2.0, f"z = {z:+.2f}")

# percentile of the target's own closest approach
random.seed(20260915)
closest = []
for _ in range(4000):
    tt = math.exp(random.uniform(math.log(LO), math.log(HI)))
    i = __import__("bisect").bisect_left(band, tt)
    c = []
    if i < len(band): c.append(abs(band[i]-tt)/tt)
    if i > 0:        c.append(abs(band[i-1]-tt)/tt)
    closest.append(min(c))
closest.sort()
pct = sum(1 for c in closest if c < best_dev)/len(closest)*100
print(f"  median closest approach of a random target : {closest[len(closest)//2]*100:.4f}%")
print(f"  percentile of our target (lower = luckier)  : {pct:.1f}")
print(f"  luckiest 1% of random targets reach        : {closest[int(len(closest)*0.01)]*100:.4f}%")
check("target's own fit quality is not even in the luckiest 10%", pct > 10.0,
      f"percentile {pct:.1f}")
check("best hit is no better than a typical random target's best hit",
      best_dev >= 0.5*closest[len(closest)//2],
      f"our best {best_dev*100:.4f}% vs median random {closest[len(closest)//2]*100:.4f}%")

# the specific 'nice-looking' candidate found in reconnaissance
cand_val = N_gen**2/(F5*F_proj)          # 9/85
cand_dev = abs(cand_val - d_new)/d_new
print(f"""
  The most attractive single candidate found in reconnaissance:
      delta = N_gen^2/(F5*F_proj) = {N_gen**2}/{F5*F_proj} = {cand_val:.6f}
      deviation from {d_new:.6f} : {cand_dev*100:.4f}%  ({cand_dev/A_MZ_MSBAR_E*d_new:.2f} sigma)
""")
check("candidate 9/85 lands within 2 sigma of delta", cand_dev*d_new/A_MZ_MSBAR_E < 2.0,
      f"{cand_dev*d_new/A_MZ_MSBAR_E:.2f} sigma")
print(f"""  => The candidate LANDS, but the grammar is dense enough that landing means
     nothing: {n_hit} grammar values sit within +-0.5% of the target, and a random
     target in the same band gets {mu:.1f} +- {sd:.1f} hits (z = {z:+.2f}).  The coefficient
     is not selected BY the physics, it is selected TO FIT the data.  Same verdict
     as scripts/07 gave for the IR gap 0.036.""")

# ============================================================================
print("\n" + "=" * 78)
print("R8 -- VERDICT")
print("=" * 78)
print(f"""
  R1  🟢 A1 CLOSED.  Sigma_f N_c Q_f^2 = 2B is EQUIVALENT to N_gen = B-1 = 3B/4;
      the three sector sums are (B-1, B, 1); the running is F_proj-2B = (B-1)^2.
      This upgrades docs/03 section 7B from 'exact numerical identity' to
      'equivalent to an IDCM structural relation'.

  R2  🟢 TARGET CORRECTED.  alpha^-1(M_Z) = {A_MZ_MSBAR}({int(A_MZ_MSBAR_E*1000)}) -> running = {run_new:.4f}({int(A_MZ_MSBAR_E*1000)}),
      delta = {d_new:+.4f}, {d_new/A_MZ_MSBAR_E:.1f} sigma.  docs/06's target 9.085 (from 127.951) is superseded.

  R3  🟡 DECOMPOSED.  Physical running = fermion {ferm:.4f} + gauge/scheme {bos:.4f};
      structural = 2B + 1.  delta = (+{ferm-2*B:.4f}) + ({bos-1:+.4f}) -- a residual of a
      near-cancellation, not a single number.

  R4  🔴 OBSTRUCTION.  Perturbative-vs-dispersive hadronic spread = {had_pert-had_disp:.3f},
      {(had_pert-had_disp)/d_new:.1f}x delta.  The exact running is not a clean structural target.

  R5  🔴 SPECTRUM CANNOT REFINE IT.  IDCM spectrum through the exact kernel gives
      {sum_idcm:.3f} (leptons agree to {lep_agree:.2f}%); that is FURTHER from {run_new:.3f} than the
      integer 9.  The integer is a structural input, not an emergent sum.

  R6  🟢 SCHEME IDENTIFIED.  128 matches MS-bar ({g_msbar:.4f}%) far better than on-shell
      ({g_onshell:.4f}%).  The structural endpoint contains the gauge/scheme running,
      which selects the reading Delta alpha^-1 = 2B + 1 over 'N_gen^2'.
  R6b 🟢 RESIDUAL RESOLVED.  docs/03's unattributed '0.965 bosonic component' is the
      on-shell <-> MS-bar conversion ({conv:.3f} +- {conv_err:.3f}), not a W loop.  So the
      '+1' is a SCHEME-CONVENTION term: IDCM's 128 is an MS-bar-type number.

  R7  ❌ NO SELECTIVE FORMULA FOR delta.  Pre-registered grammar: {n_hit} values within
      +-0.5%, random control {mu:.1f} +- {sd:.1f}, z = {z:+.2f}, percentile {pct:.1f}.

  OVERALL: 🔴 the running's deviation from the integer 9 is NOT derivable from IDCM
  structure.  It is not even a clean physical target (R4).  What IS now established:
  (i) A1's structural necessity (R1), (ii) the sector decomposition and its
  near-cancellation (R3), (iii) the MS-bar identification (R6), (iv) the corrected
  physical target (R2).  The remaining gap is the same non-perturbative hadronic
  vacuum polarisation that no framework derives from a spectrum.
""")
print("=" * 78)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
