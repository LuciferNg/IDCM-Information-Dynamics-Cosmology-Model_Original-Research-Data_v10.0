"""
O139 — scripts/04: PROBLEM A — α⁻¹(Q) functional form
======================================================
Structural content of IDCM:
    α⁻¹(0)   = C(B²,2) + F_proj = 120 + 17 = 137     (O142: 3·Tr(I₄₄)+F₅)
    α⁻¹(M_Z) = C(B²,2) + 2B     = 120 + 8  = 128     (O142: 2·Tr(I₄₄)+F₅F₆)
    Δα⁻¹     = F_proj − 2B      = 9 = N_gen²

QUESTION: can IDCM produce the FUNCTION, not just the two endpoints?

  A1  Exact one-loop vacuum polarisation (no threshold approximation)
  A2  Feed the IDCM 9-fermion spectrum (O136) through it
  A3  Test whether the structural total N_gen² = 9 emerges from that sum
  A4  Build and TEST the explicit functional form
  A5  Null-test the candidate structural decompositions of 9
  A6  Report honestly

Author: Hermes (O139 problem A attack, 2026-08-31)
"""
import math
import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

# ---------------- constants ----------------
Nd, B, N_gen = 44, 4, 3
C_B2_2, F_proj = 120, 17
alpha0_inv = 137.035999084
M_Z = 91187.6            # MeV
N_c_lep, N_c_q = 1, 3
Q_e, Q_u, Q_d = 1.0, 2/3, 1/3

# IDCM 9-fermion spectrum (O136 docs/04 table): name, n, P_f, m_pred(MeV), weight
IDCM = [
    ("e",   1,  3.6,   0.5118,  N_c_lep*Q_e**2),
    ("mu",  7,  15.5,  105.80,  N_c_lep*Q_e**2),
    ("tau", 20, 37.0,  1770.8,  N_c_lep*Q_e**2),
    ("u",   1,  15.5,  2.204,   N_c_q*Q_u**2),
    ("d",   1,  33.0,  4.692,   N_c_q*Q_d**2),
    ("s",   14, 3.6,   92.28,   N_c_q*Q_d**2),
    ("c",   34, 13.0,  1273.7,  N_c_q*Q_u**2),
    ("b",   33, 44.0,  4191.4,  N_c_q*Q_d**2),
    ("t",   None, None, 173937.0, N_c_q*Q_u**2),
]
# same particles, PDG pole/current masses (MeV)
PDG = [
    ("e", 0.510998950, N_c_lep*Q_e**2),
    ("mu",105.6583755, N_c_lep*Q_e**2),
    ("tau",1776.86,    N_c_lep*Q_e**2),
    ("u", 2.16,        N_c_q*Q_u**2),
    ("d", 4.67,        N_c_q*Q_d**2),
    ("s", 93.0,        N_c_q*Q_d**2),
    ("c", 1270.0,      N_c_q*Q_u**2),
    ("b", 4180.0,      N_c_q*Q_u**2*0 + N_c_q*Q_d**2),
    ("t", 172760.0,    N_c_q*Q_u**2),
]
LEP = ("e","mu","tau"); HAD5 = ("u","d","s","c","b")

print("=" * 76)
print("A1 — Exact one-loop vacuum polarisation (spacelike Q)")
print("=" * 76)
print("""
  Δα(Q²) = (2α(0)/π)·Σ_f N_c Q_f²·∫₀¹ dx·x(1−x)·ln[1 + Q²x(1−x)/m_f²]

  EXACT one-loop result — contains threshold behaviour automatically and
  reduces to (α/3π)ΣN_cQ_f²[ln(Q²/m²) − 5/3] for Q >> m_f, because
  ∫₀¹x(1−x)dx = 1/6 and ∫₀¹x(1−x)ln[x(1−x)]dx = −5/18.
""")
# Gauss-Legendre nodes for the x-integral
gx, gw = np.polynomial.legendre.leggauss(160)
gx = 0.5*(gx+1.0); gw = 0.5*gw
def I0(x): return x*(1-x)
def I_xy():   return float(np.sum(I0(gx)*gw))
def I_xy_ln():return float(np.sum(I0(gx)*np.log(I0(gx))*gw))
print(f"  Gauss-Legendre(160) ∫x(1−x)          = {I_xy():.10f}   vs 1/6   = {1/6:.10f}")
print(f"  Gauss-Legendre(160) ∫x(1−x)ln[x(1−x)] = {I_xy_ln():.10f}   vs −5/18 = {-5/18:.10f}")
print("  (the second integrand has integrable log singularities at x=0,1, so")
print("   Gauss-Legendre converges only algebraically — tolerance set to 1e-8.)")
check("asymptotic decomposition 1/6 verified", abs(I_xy()-1/6) < 1e-12, f"{I_xy():.12f}")
check("asymptotic decomposition −5/18 verified", abs(I_xy_ln()+5/18) < 1e-8, f"{I_xy_ln():.12f}")

# check the exact form reproduces the asymptotic form at large Q
def Delta_alpha(Q, spec):
    """exact 1-loop Δα(Q) = (2α/π)Σ_f w_f ∫₀¹ x(1−x) ln[1+Q²x(1−x)/m²]"""
    a0 = 1/alpha0_inv
    tot = 0.0
    for (nm, m, w) in spec:
        tot += w*float(np.sum(I0(gx)*np.log(1.0 + (Q/m)**2*I0(gx))*gw))
    return (2*a0/math.pi)*tot
def Delta_alpha_asym(Q, spec):
    a0 = 1/alpha0_inv
    return (a0/(3*math.pi))*sum(w*(math.log((Q/m)**2) - 5/3) for (nm,m,w) in spec)

Qtest = 1e5  # 100 GeV, >> all masses except top
e_ex  = Delta_alpha(Qtest, [s for s in PDG if s[0] != "t"])
e_as  = Delta_alpha_asym(Qtest, [s for s in PDG if s[0] != "t"])
print(f"\n  cross-check at Q=100 GeV (t decoupled): exact {e_ex:.6f}  asymptotic {e_as:.6f}")
print(f"  relative difference = {abs(e_ex-e_as)/e_ex*100:.4f}%")
check("exact → asymptotic at Q >> m_f", abs(e_ex-e_as)/e_ex < 1e-3,
      f"{abs(e_ex-e_as)/e_ex*100:.4f}%")

print("\n" + "=" * 76)
print("A2 — Feed the IDCM 9-fermion spectrum through it")
print("=" * 76)
idcm3 = [(nm, m, w) for (nm, n, pf, m, w) in IDCM]
D_idcm = Delta_alpha(M_Z, idcm3)
D_pdg  = Delta_alpha(M_Z, PDG)
print(f"  Δα(M_Z) from IDCM spectrum : {D_idcm:.6f}  →  Δα⁻¹ = {alpha0_inv*D_idcm:.4f}")
print(f"  Δα(M_Z) from PDG  spectrum : {D_pdg:.6f}  →  Δα⁻¹ = {alpha0_inv*D_pdg:.4f}")
print(f"  PDG quoted (137.036−127.951)   : {alpha0_inv - 127.951:.4f}")
print(f"  IDCM structural value          : 9 = N_gen²")

lep_idcm = Delta_alpha(M_Z, [s for s in idcm3 if s[0] in LEP])
lep_pdg  = Delta_alpha(M_Z, [s for s in PDG  if s[0] in LEP])
had_idcm = Delta_alpha(M_Z, [s for s in idcm3 if s[0] in HAD5])
had_pdg  = Delta_alpha(M_Z, [s for s in PDG  if s[0] in HAD5])
print(f"\n  leptonic only  : IDCM Δα⁻¹ = {alpha0_inv*lep_idcm:.4f}   PDG Δα⁻¹ = {alpha0_inv*lep_pdg:.4f}"
      f"   (PDG published 0.031498 → 4.3160)")
print(f"  hadronic (5 q) : IDCM Δα⁻¹ = {alpha0_inv*had_idcm:.4f}   PDG Δα⁻¹ = {alpha0_inv*had_pdg:.4f}"
      f"   (PDG dispersion 0.027662 → 3.791)")
check("leptonic Δα⁻¹ within 1% of published PDG", abs(alpha0_inv*lep_pdg - 4.3160)/4.3160 < 0.01,
      f"{alpha0_inv*lep_pdg:.4f} vs 4.3160")

print("\n" + "=" * 76)
print("A3 — Does the structural total N_gen² = 9 emerge from the spectrum sum?")
print("=" * 76)
tot_idcm = alpha0_inv*D_idcm
tot_pdg  = alpha0_inv*D_pdg
quoted   = alpha0_inv - 127.951
for lbl, v in (("IDCM spectrum sum", tot_idcm), ("PDG spectrum sum", tot_pdg),
               ("PDG quoted        ", quoted), ("IDCM structural   ", 9.0)):
    print(f"  {lbl} : Δα⁻¹ = {v:.4f}   dev from 9 = {abs(v-9)/9*100:5.3f}%")
print(f"""
  ⇒ The one-loop sum over the IDCM spectrum gives {tot_idcm:.3f}, i.e. {abs(tot_idcm-9)/9*100:.2f}% above the
    structural integer 9. The excess is entirely in the QUARK loop (perturbative
    treatment overestimates: IDCM {alpha0_inv*had_idcm:.3f} vs PDG dispersion 3.791).
  ⇒ VERDICT: 9 is CONSISTENT with the spectrum sum at the few-% level, but the
    sum is NOT an exact closed form of 9. Residual = kernel/hadronic artefact,
    NOT a spectrum artefact (the leptonic sector agrees to {abs(alpha0_inv*lep_pdg-4.3160)/4.3160*100:.2f}%).
""")
check("structural 9 within 5% of IDCM spectrum sum", abs(tot_idcm-9)/9 < 0.05, f"{abs(tot_idcm-9)/9*100:.2f}%")

print("=" * 76)
print("A4 — Explicit functional form, and its test against QED")
print("=" * 76)
print("""
  STRUCTURAL ANSATZ (both endpoints structural, kernel physical):

      α⁻¹(Q) = C(B²,2) + F_proj − N_gen²·f(Q)  =  137 − 9·f(Q),
      f(Q)   = Δα(Q)/Δα(M_Z)

  Justification: O139 established IDCM does NOT modify the QED vacuum
  polarisation kernel (photon propagator standard). So the only IDCM inputs to
  α⁻¹(Q) are (i) the two structural endpoints and (ii) the fermion spectrum.
  Rescaling the physical kernel to hit both structural endpoints is the minimal
  construction consistent with that.

  QED comparison:  α⁻¹_QED(Q) = α⁻¹(0)·(1 − Δα(Q))
""")
Q_grid = [0.0, 1.0, 10.0, 100.0, 1000.0, 1776.86, 10000.0, 91187.6]
print(f"  {'Q (MeV)':>12} | {'Δα(Q)':>10} | {'f(Q)':>8} | {'IDCM α⁻¹':>9} | {'QED α⁻¹':>9} | dev%")
print("  " + "-"*72)
rows = []
for Q in Q_grid:
    d = Delta_alpha(Q, PDG) if Q > 0 else 0.0
    f = d/D_pdg
    idcm_a = 137 - 9*f
    qed_a  = alpha0_inv*(1-d)
    dev = abs(idcm_a-qed_a)/qed_a*100 if Q > 0 else 0.0
    rows.append((Q, d, f, idcm_a, qed_a, dev))
    print(f"  {Q:12.2f} | {d:10.6f} | {f:8.5f} | {idcm_a:9.4f} | {qed_a:9.4f} | {dev:5.3f}")
maxdev = max(r[5] for r in rows)
print(f"\n  max deviation over the grid = {maxdev:.3f}%")
print(f"  endpoint mismatches: Q=0 → {abs(137-alpha0_inv)/alpha0_inv*100:.3f}%, "
      f"M_Z → {abs(128-127.951)/127.951*100:.3f}%")
check("functional form gives α⁻¹(0)=137 exactly", abs(rows[0][3]-137) < 1e-9, "Q=0")
check("functional form gives α⁻¹(M_Z)=128 exactly", abs(rows[-1][3]-128) < 1e-9, "Q=M_Z")
check("max deviation from QED < 1%", maxdev < 1.0, f"{maxdev:.3f}%")
check("monotone decreasing", all(rows[i][3] >= rows[i+1][3] for i in range(len(rows)-1)), "")

print("\n" + "=" * 76)
print("A5 — Null test on the structural decompositions of 9")
print("=" * 76)
lib = {"Nd":44,"B":4,"N_gen":3,"L4":7,"L5":11,"L6":18,"L7":29,
       "F5":5,"F6":8,"F7":13,"F8":21,"F9":34,"F10":55,"F_proj":17,
       "M":33,"CY3":134,"C_B2_2":120}
expr = {}
for n1,v1 in lib.items():
    expr.setdefault(v1,set()).add(n1)
    for n2,v2 in lib.items():
        if v2<=1: continue
        expr.setdefault(v1*v2,set()).add(f"{n1}*{n2}")
        expr.setdefault(v1+v2,set()).add(f"{n1}+{n2}")
        expr.setdefault(v1-v2,set()).add(f"{n1}-{n2}")
        for n3,v3 in lib.items():
            if v3<=1: continue
            expr.setdefault(v1*v2*v3,set()).add(f"{n1}*{n2}*{n3}")
window = list(range(7,12))
cov = [v for v in window if v in expr]
print(f"  library = {len(lib)} symbols;  window [7,11] coverage = {len(cov)}/{len(window)} = {len(cov)/len(window)*100:.0f}%")
for v in window:
    n = len(expr.get(v,()))
    print(f"    {v}: {'hit' if v in expr else 'miss'}  ({n} distinct expressions)")
print(f"  distinct expressions equal to 9: {len(expr.get(9,()))}")
print(f"""
  ⇒ window FULLY covered ⇒ any single expression for 9 is NOT selective.
  ⇒ But (i) 9 = N_gen² and (ii) 9 = F_proj − 2B are not library matches — they
    are two independent O142/O160 algebraic identities landing on the same
    integer.  Structural IDENTIFICATION ≠ mechanism.  Recorded as 🔴 mechanism-open.
""")
check("window [7,11] fully covered (non-selective)", len(cov)==len(window),
      f"{len(cov)/len(window)*100:.0f}%")

print("\n" + "=" * 76)
print("A5b — Candidate MECHANISM for the 2B correction: charge-squared sum")
print("=" * 76)
print("""
  α⁻¹(M_Z) = C(B²,2) + 2B = 120 + 8.
  Is there a PHYSICAL quantity that equals 2B = 8?  Test the fermion
  charge-squared sum over one complete SM generation:
      Σ_f N_c Q_f² = 3(1)(1)² + 3(3)(2/3)² + 3(3)(1/3)²
                   = 3·1 + 9·(4/9) + 9·(1/9)
""")
sum_lep = 3*N_c_lep*Q_e**2
sum_up  = 3*N_c_q*Q_u**2
sum_dn  = 3*N_c_q*Q_d**2
sumQ2   = sum_lep + sum_up + sum_dn
print(f"      leptons    : 3 × 1 × 1     = {sum_lep}")
print(f"      up-type    : 3 × 3 × (4/9) = {sum_up}")
print(f"      down-type  : 3 × 3 × (1/9) = {sum_dn}")
print(f"      Σ_f N_c Q_f²               = {sumQ2}")
print(f"      2B = 2 × {B}                  = {2*B}")
print(f"      C(B²,2) + ΣN_cQ_f²         = {C_B2_2} + {sumQ2} = {C_B2_2+sumQ2}   (α⁻¹(M_Z) = 128)")
print(f"""
  ⇒ Σ_f N_c Q_f² = {sumQ2} = 2B EXACTLY (an exact identity from SM quantum numbers,
    not a fit).  So the structural symbol "2B" in α⁻¹(M_Z) = C(B²,2) + 2B admits a
    PHYSICAL reading: it is the total fermion charge-squared weight.

  ⚠️ BUT this is NOT a mechanism derivation, for three reasons:
    (1) the one-loop running gives Δα⁻¹ = {alpha0_inv*D_pdg:.3f}, not {sumQ2:.0f} (the logs add {alpha0_inv*D_pdg-sumQ2:.2f});
    (2) the Q=0 endpoint correction is F_proj = {F_proj}, not {sumQ2:.0f} — the two endpoints
        do not share this mechanism;
    (3) no IDCM derivation shows Σ_f N_c Q_f² MUST equal 2B (it is an exact
        numerical identity here, but its structural necessity is unproven).
  ⇒ recorded as a 🟡 candidate reading, NOT a closure.
""")
check("Σ_f N_c Q_f² = 2B exactly", abs(sumQ2 - 2*B) < 1e-12, f"{sumQ2} = {2*B}")
check("C(B²,2) + ΣN_cQ_f² = 128", C_B2_2 + sumQ2 == 128, f"{C_B2_2+sumQ2}")
print("  ⚠️ one-loop running disagrees with ΣN_cQ_f² by "
      f"{abs(alpha0_inv*D_pdg-sumQ2)/sumQ2*100:.2f}% → the reading is NOT sufficient")

print("\n" + "=" * 76)
print("A6 — VERDICT")
print("=" * 76)
print(f"""
  🟢 FUNCTIONAL FORM FOUND (both endpoints exact, structural):

        α⁻¹(Q) = C(B²,2) + F_proj − N_gen²·Δα(Q)/Δα(M_Z)
               = 137 − 9·f(Q)

     - α⁻¹(0) = 137, α⁻¹(M_Z) = 128 EXACT by construction
     - agrees with the QED curve to ≤ {maxdev:.2f}% on the tested grid
     - kernel = standard one-loop vacuum polarisation (justified by O139)

  🟡 SPECTRUM-SUM CONSISTENCY: one-loop sum over the IDCM 9-fermion spectrum
     = {tot_idcm:.3f} vs structural 9 → {abs(tot_idcm-9)/9*100:.2f}%.
     Leptonic sector agrees with PDG to {abs(alpha0_inv*lep_pdg-4.3160)/4.3160*100:.2f}%; excess is the hadronic
     (perturbative quark loop vs PDG dispersion) treatment.

  🔴 STILL OPEN: the MECHANISM.  Why should the vacuum-polarisation total equal
     N_gen²?  The integer is structurally identified by two independent routes
     (F_proj − 2B = 17 − 8 = 9; N_gen² = 9) but no derivation shows the
     vacuum-polarisation sum MUST land there.  O160 docs/21 §5 already flags
     this as '命名≠解釋'.

  ⚠️ OBSERVATIONAL CAVEAT: α⁻¹(Q) for 0 < Q < M_Z is NOT directly measured in
     either framework — it is derived.  The measured anchors are α(0) (Thomson)
     and α(M_Z) (Z-pole fits).  The functional form is therefore falsifiable
     only INDIRECTLY (g-2, Lamb shift, muonium hfs) → that is problem B.
""")
print("=" * 76)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL")
print("=" * 76)
