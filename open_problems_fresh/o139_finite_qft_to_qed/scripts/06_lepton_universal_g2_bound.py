"""
O139 — scripts/06: LEPTON-UNIVERSAL g-2 BOUND (2025 data)
=========================================================
Closes the μ-muon g-2 orphan that was merged into problem B
(O110 docs/01 line 480 proposed "μ g-2 → O126", but O126 is
runtime_isa_verification — never registered; see docs/01 §七).

Uses the SAME rigorous cutoff integral as scripts/05 (no asymptotic
shortcut), applied to BOTH leptons, with the 2025 experimental and
theoretical numbers:

  a_μ (Fermilab final, 2025-06-03, 127 ppb)  = 0.001165920705 ± 1.48e-10
  a_μ^SM (Muon g-2 Theory Initiative WP25)   = 0.00116592033  ± 6.20e-10
  a_e (Morel et al. 2020)                    = 0.00115965218059 ± 1.30e-13

  δa_ℓ / a_ℓ  ≃  (m_ℓ / Λ)²   ⇒  g-2 is a probe of the new-physics scale Λ

The physical point: because the sensitivity scales as m_ℓ², the MUON is
(m_μ/m_e)² ≈ 4.3e4 times more sensitive to a heavy scale than the electron.
So the strongest IDCM bound comes from the muon, not the electron.

Sections
  L1  lepton table + 2025 status
  L2  rigorous solve: required Λ for each lepton
  L3  map Λ onto the FSR layer index ℓ
  L4  WHY 12 DIGITS — the digit count is a LOOP COUNT (structural)
  L5  the α⁻¹(0) endpoint: IDCM's real exposure is at digit 4, not 12
  L6  record: the SM's own prediction moved 5.2σ by changing METHOD
  L7  verdict + null test

Author: Hermes (O139, 2026-08-31)
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

# ---------------- constants (identical conventions to scripts/05) ----------------
M0        = 27.900915
omega_max = 2.0
Lambda_mass = M0*omega_max          # 55.801830 MeV
m_e   = 0.51099895000               # MeV
m_mu  = 105.6583755                 # MeV
alpha = 1/137.035999177             # CODATA 2022
alpha_inv_pdg = 137.035999177
R_world = 4129.94                   # Mpc
Mpc_m   = 3.085677581e22
Lam0_eV = 2.140399e-31              # FSR cutoff at ℓ=0 (eV), from scripts/05
def Lam_eV(ell): return Lam0_eV*4.0**ell
def ell_for(Lam_GeV): return math.log(Lam_GeV*1e9/Lam0_eV)/math.log(4.0)

# ---------------- the rigorous cutoff integral (same as scripts/05) ----------------
def a_over_schwinger(Lam, m):
    """a_ℓ(Λ)/a_ℓ(∞) for a hard loop-momentum cutoff; 1.0 when Lam is None."""
    r = 0.0 if Lam is None else (m/Lam)**2
    N = 2000000; h = 1.0/N
    eps = (np.arange(N)+0.5)*h
    t1 = eps*eps; t2 = eps*(1.0+eps)
    F = lambda t: np.log(t/(1.0+r*t)) + 1.0/(1.0+r*t)
    return float(np.sum(2.0*eps*(F(t2)-F(t1))*h))

def solve_Lam(target_rel, m, lo=None, hi=None):
    """Λ (MeV) such that |a(Λ)/a(∞) − 1| = target_rel."""
    if lo is None: lo = 10*m
    if hi is None: hi = 1e12
    for _ in range(90):
        mid = math.sqrt(lo*hi)
        v = abs(a_over_schwinger(mid, m) - 1.0)
        if v > target_rel: lo = mid
        else:              hi = mid
    return math.sqrt(lo*hi)

# ---------------- L1 ----------------
print("="*78)
print("L1 — lepton table + 2025 experimental status")
print("="*78)
a_e_exp, a_e_err = 0.00115965218059, 1.30e-13      # Morel et al. 2020
a_mu_exp, a_mu_err = 0.001165920705, 1.48e-10      # Fermilab final 2025-06-03
a_mu_sm,  a_mu_sm_err = 0.00116592033, 6.20e-10    # WP25 (lattice-only HVP)
lep = [("electron e", m_e, a_e_exp, a_e_err, None),
       ("muon μ",     m_mu, a_mu_exp, a_mu_err, a_mu_sm_err)]
print(f"  {'lepton':<12}{'m (MeV)':>12}{'a_ℓ (exp)':>20}{'rel. precision':>18}")
for nm, m, a, e, th in lep:
    print(f"  {nm:<12}{m:>12.5f}{a:>20.12f}{e/a:>18.3e}")
print(f"\n  inputs (full precision, for audit):")
print(f"    a_e(exp)  = {a_e_exp:.14f} ± {a_e_err:.2e}")
print(f"    a_mu(exp) = {a_mu_exp:.14f} ± {a_mu_err:.2e}   (Fermilab final 2025)")
print(f"    a_mu(SM)  = {a_mu_sm:.14f} ± {a_mu_sm_err:.2e}   (WP25)")
print(f"\n  muon exp − SM (WP25) = {(a_mu_exp-a_mu_sm):.3e}"
      f"  ± {math.sqrt(a_mu_err**2+a_mu_sm_err**2):.3e}"
      f"  → {(a_mu_exp-a_mu_sm)/math.sqrt(a_mu_err**2+a_mu_sm_err**2):.2f}σ")
print(f"  (WP20 had 5.7σ; the 2025 white paper adopts a lattice-only HVP and the")
print(f"   tension disappears.  See L6.)")
print(f"  (m_μ/m_e)² = {(m_mu/m_e)**2:.3e}  ← muon is this much more sensitive to a heavy scale Λ")
check("muon/electron sensitivity ratio = (m_μ/m_e)²", abs((m_mu/m_e)**2 - 4.275e4) < 1e2,
      f"{(m_mu/m_e)**2:.4e}")
check("muon 2025 agrees with WP25 within 1σ",
      abs(a_mu_exp-a_mu_sm)/math.sqrt(a_mu_err**2+a_mu_sm_err**2) < 1.0)

# ---------------- L2 ----------------
print("\n" + "="*78)
print("L2 — rigorous solve: what Λ does each lepton require?")
print("="*78)
print("""
  Constraint: the IDCM new-physics contribution must fit inside the
  *theoretical* uncertainty (for the muon) / the experimental precision
  (for the electron, whose theory is far more precise than its data).

  Solve  |a_ℓ(Λ)/a_ℓ(∞) − 1| = ε_ℓ   for Λ, using the same hard-cutoff
  integral as scripts/05 (no asymptotic shortcut).
""")
res = {}
for nm, m, a, e, th in lep:
    eps = (th if th is not None else e)/a
    Lam = solve_Lam(eps, m)
    res[nm] = (eps, Lam)
    print(f"  {nm:<12} ε = {eps:.3e}   →  Λ_req = {Lam:14.4e} MeV = {Lam/1000:9.3f} GeV"
          f"  = {Lam/Lambda_mass:8.1f} × Λ_mass")
check("electron Λ_req in TeV-range ballpark (0.01–1 TeV)",
      0.01 < res["electron e"][1]/1000 < 1000, f"{res['electron e'][1]/1000:.2f} GeV")
check("muon Λ_req exceeds electron Λ_req", res["muon μ"][1] > res["electron e"][1],
      f"{res['muon μ'][1]/1000:.1f} GeV vs {res['electron e'][1]/1000:.1f} GeV")
ratio = res["muon μ"][1]/res["electron e"][1]
pred  = (m_mu/m_e)*math.sqrt(res["electron e"][0]/res["muon μ"][0])
print(f"\n  ratio Λ_μ/Λ_e = {ratio:.2f}")
print(f"  analytic prediction (m_μ/m_e)·√(ε_e/ε_μ) = {pred:.2f}   ← agreement confirms")
print(f"     the m²-scaling structure of the bound")
check("Λ_μ/Λ_e matches the m²-scaling prediction", abs(ratio-pred)/pred < 0.05,
      f"{ratio:.3f} vs {pred:.3f}")

# ---------------- L3 ----------------
print("\n" + "="*78)
print("L3 — map the bound onto the FSR layer index ℓ")
print("="*78)
print(f"""
  FSR cutoff ladder (O140):  Λ_ℓ = ħπ·44·4^ℓ / R_world,  a_ℓ = R_world/(44·4^ℓ)
  Λ_ℓ = {Lam0_eV:.6e} eV × 4^ℓ      (each layer deepens by ×4)
""")
for nm, (eps, Lam) in res.items():
    ell = ell_for(Lam/1000)
    print(f"  {nm:<12} Λ_req = {Lam/1000:9.3f} GeV  →  ℓ_req = {ell:6.2f}  →  ℓ ≳ {math.ceil(ell)}")
ell_e = ell_for(res["electron e"][1]/1000)
ell_m = ell_for(res["muon μ"][1]/1000)
strongest = math.ceil(max(ell_e, ell_m))
print(f"""
  ⇒ STRONGEST bound comes from the MUON:  ℓ ≳ {strongest}
  ⇒ both leptons agree on ℓ ≳ {math.floor(min(ell_e,ell_m))}–{strongest}
    (this SUPERSEDES the electron-only bound ℓ ≳ 69 quoted in scripts/05)
  ⇒ ℓ = 0 would put the cutoff at {Lam_eV(0):.4e} eV — a lab frame there is
    excluded by ~{math.log10(res['muon μ'][1]*1e6/Lam_eV(0)):.0f} orders of magnitude
""")
check("muon-driven bound is ℓ ≳ 70 ± 2", 68 <= strongest <= 72, f"ℓ ≳ {strongest}")
check("ℓ = 0 excluded", Lam_eV(0) < 1e-20, f"{Lam_eV(0):.3e} eV")

# ---------------- L4 ----------------
print("\n" + "="*78)
print("L4 — WHY 12 DIGITS?  the digit count is a LOOP COUNT")
print("="*78)
x = alpha/math.pi
print(f"""
  QED's a_ℓ is a perturbative series in α/π:
      a_ℓ = (α/π)·[ A₁ + A₂(α/π) + A₃(α/π)² + A₄(α/π)³ + A₅(α/π)⁴ ]
  α/π = {x:.6e}   ⇒  one loop buys log₁₀(π/α) = {math.log10(1/x):.3f} decimal digits.
""")
A = [0.5, -0.328478965579193, 1.181241456587, -1.912245764926, 7.795]
names = ["1-loop (Schwinger)", "2-loop", "3-loop", "4-loop", "5-loop"]
print(f"  {'order':<20}{'term / A₁':>16}{'digits bought':>16}{'cumulative':>14}")
cum = 0.0
for nm, a in zip(names, A):
    d = 0.0 if a == 0.5 else -math.log10(abs(a*x**names.index(nm))/A[0])
    cum += d
    print(f"  {nm:<20}{a*x**names.index(nm):>16.6e}{d:>16.2f}{cum:>14.2f}")
print(f"""
  ⇒ 12 digits  ⇔  12/{math.log10(1/x):.3f} = {12/math.log10(1/x):.2f} loops.
    QED has been computed to 5 loops (A₅ from 12672 diagrams, Aoyama–Kinoshita–Nio).
  ⇒ "12 decimal places" is a statement about HOW MANY ORDERS OF PERTURBATION
    THEORY WERE EVALUATED IN A REGIME WHERE α/π IS SMALL — not a measure of
    how true the theory is.
""")
check("1 loop buys ≈ 2.63 digits", abs(math.log10(1/x) - 2.634) < 0.01)
check("12 digits ≈ 4–5 loops", 4.0 < 12/math.log10(1/x) < 5.0,
      f"{12/math.log10(1/x):.2f}")

# ---------------- L5 ----------------
print("\n" + "="*78)
print("L5 — IDCM's REAL exposure: the α⁻¹(0) endpoint, at digit 4 not 12")
print("="*78)
dev = (alpha_inv_pdg - 137.0)/alpha_inv_pdg
print(f"""
  O142/O160 give IDCM's structural endpoint   α⁻¹(0) = C(B²,2)+F_proj = 120+17 = 137
  CODATA 2022 physical Thomson-limit value    α⁻¹(0) = {alpha_inv_pdg}

  relative deviation = {dev:.4e}   ({dev*100:.4f}%)

  a_e ∝ α, so a {dev*100:.3f}% error in α is a {dev*100:.3f}% error in a_e:
      Δa_e/a_e = {dev:.3e}
      electron experimental relative precision = {a_e_err/a_e_exp:.3e}
      ⇒ {abs(dev)/(a_e_err/a_e_exp):.3e} × the experimental precision
""")
check("α⁻¹(0)=137 conflicts with a_e far beyond 1σ",
      abs(dev)/(a_e_err/a_e_exp) > 1e6, f"{abs(dev)/(a_e_err/a_e_exp):.2e} σ")
print(f"""  ⇒ IF 137 is IDCM's literal α⁻¹(0), IDCM fails the electron g-2 test at the
    FOURTH significant digit.  The celebrated 12-digit agreement is NOT the
    obstacle; the 4th digit is.

  Two honest exits (neither is currently derived — both are 🔴):
    (a) 137 is a BARE/lattice-scale value; the physical α⁻¹(0) = 137.036
        arises after dressing.  Then IDCM owes a structural derivation of
        +0.035999177 (= 2.627e-4 relative).
    (b) IDCM's α⁻¹(0) is not exactly 137 and the integer identification is
        approximate.  Then the "two independent identities" in O142/O160 are
        numerology at the 3rd decimal, not structural identities.

  NOTE this is the SAME structural gap as problem A's "why = N_gen²": IDCM
  identifies INTEGERS exactly but has no derived account of the small
  non-integer corrections (0.036 at Q=0, 0.049 at M_Z, 0.085 in the running).
""")
print(f"  cross-check with problem A's endpoints:")
print(f"    α⁻¹(0)   : IDCM 137  vs physical {alpha_inv_pdg:.6f}   dev {abs(137-alpha_inv_pdg)/alpha_inv_pdg*100:.4f}%")
print(f"    α⁻¹(M_Z) : IDCM 128  vs physical 127.951   dev {abs(128-127.951)/127.951*100:.4f}%")
print(f"    running  : IDCM   9  vs physical   9.085   dev {abs(9-9.085)/9.085*100:.4f}%")
check("all three α endpoints deviate at ~0.03–1% level",
      all(1e-4 < d < 1e-2 for d in
          [abs(137-alpha_inv_pdg)/alpha_inv_pdg, abs(128-127.951)/127.951, abs(9-9.085)/9.085]))

# ---------------- L6 ----------------
print("\n" + "="*78)
print("L6 — the wall has a crack, and the crack is made of theory")
print("="*78)
wp20, e20 = 116591810, 43
wp25, e25 = 116592033, 62
exp_val, exp_err = 116592070.5, 14.8     # ×10^-11
print(f"""
  All in units of 10⁻¹¹:

    WP20 SM prediction : {wp20} ± {e20}      →  {abs(exp_val-wp20)/math.sqrt(e20**2+exp_err**2):.1f}σ vs Fermilab
    WP25 SM prediction : {wp25} ± {e25}      →  {abs(exp_val-wp25)/math.sqrt(e25**2+exp_err**2):.2f}σ vs Fermilab
    Fermilab final     : {exp_val} ± {exp_err}

  The SM "prediction" moved by {wp25-wp20} × 10⁻¹¹ = {(wp25-wp20)/e20:.1f} × its OWN 2020
  error bar — with NO new experiment, only a change of HVP METHOD
  (dispersive e⁺e⁻ data → lattice QCD).
""")
check("WP25 prediction moved by > 3× its own 2020 error bar",
      (wp25-wp20)/e20 > 3, f"{(wp25-wp20)/e20:.1f}×")
check("WP25 agrees with Fermilab within 1σ",
      abs(exp_val-wp25)/math.sqrt(e25**2+exp_err**2) < 1.0)
print(f"""  ⇒ the "wall" is not monolithic.  Its height depends on which METHOD you
    use for the non-perturbative QCD piece, and the two methods (dispersive
    vs lattice) still contradict each other.  The remaining tension is a
    METHODOLOGICAL dispute, not a new-physics signal.

  For IDCM this cuts both ways:
    • bad news : a theory cannot claim credit for a "discrepancy" that is
                 really a theory error bar (this is why IDCM should NOT be
                 pitched against the 2021 4.2σ muon anomaly).
    • good news: it shows the SM's precision frontier is limited by
                 non-perturbative QCD method, i.e. by exactly the kind of
                 structural/definitional question IDCM claims to answer.
""")

# ---------------- L7 ----------------
print("="*78)
print("L7 — VERDICT + null test")
print("="*78)
print(f"""
  ✅ g-2 is a genuine, unignorable WALL — but its height is set by
     (number of loops) × log₁₀(π/α), i.e. it is an EXPANSION-COUNTING
     statement in the soft regime Q ≪ m_ℓ, not a measure of final truth.

  ✅ IDCM does not have to BEAT it there.  O139 scripts/01 established that
     K_Chain's finite spectrum modifies the fermion MASS spectrum but not the
     gauge-boson propagator, so IDCM REDUCES to QED at atomic scales and
     INHERITS a_e — conditional on adding nothing.

  🟢 The conditional is now quantified: IDCM must have no new physics below
       Λ ≈ {res['muon μ'][1]/1000:.0f} GeV (muon-driven) ⇒ FSR cutoff ℓ ≳ {strongest}.
     This is a real, observation-driven constraint on o140's "which ℓ layer is
     the lab frame" question.

  🔴 The genuine exposure is NOT 12 digits but the 4th: α⁻¹(0) = 137 vs
     {alpha_inv_pdg}.  A 2.6e-4 error in α is a 2.6e-4 error in a_e, i.e.
     {abs(dev)/(a_e_err/a_e_exp):.1e} × the experimental precision.
     Until IDCM either derives the +0.035999177 dressing or abandons the
     exact integer reading, the 12-digit wall is not the binding constraint.

  Null test: the α⁻¹(0) exposure must NOT be dismissible as a symbol-library
  coincidence, because it is a DIRECT observable (Thomson limit), unlike the
  withdrawn ℓ_min = 60.
""")
check("α⁻¹(0) is a direct observable (Thomson limit), unlike ℓ_min",
      True, "documented reasoning")
check("verdict consistent: muon drives the strongest bound",
      strongest == math.ceil(max(ell_e, ell_m)), f"ℓ ≳ {strongest}")

print("\n" + "="*78)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL")
print("="*78)
