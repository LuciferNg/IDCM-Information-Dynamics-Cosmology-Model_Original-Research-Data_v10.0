"""
O139 — scripts/05: PROBLEM B — fermion-sector discretisation → g-2
==================================================================
Two DIFFERENT cutoffs exist in IDCM and they must not be conflated:

  (1) MASS-spectrum Nyquist cutoff   Λ_mass = M₀·ω_max = 55.80 MeV
      — the top of the K_Chain FERMION MASS spectrum (m_n = M₀ ω_n P_f)
  (2) SPACETIME momentum cutoff      Λ_ℓ = ħπ/a_ℓ,  a_ℓ = R_world/(44·4^ℓ)
      — the Brillouin-zone edge of the FSR spatial lattice (O140)

B's question: does either truncate the electron's QED loop, and what does
that do to g-2?

  B1  4-D master integral with a hard cutoff (analytic vs numeric)
  B2  a_e(Λ) — Schwinger term with a hard loop-momentum cutoff
  B3a RIGOROUS argument: Λ_mass cannot be a momentum cutoff (self-contradiction)
  B3b ILLUSTRATIVE quantitative estimate + coefficient caveat
  B4  Invert: what Λ does a_e require? (tolerance scan)
  B5  Map Λ onto the FSR layer index ℓ → structural constraint
  B6  CUTOFF effect vs DISCRETISATION effect (different things)
  B7  Null test on ℓ + VERDICT

Author: Hermes (O139 problem B attack, 2026-08-31)
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
M0        = 27.900915          # MeV
omega_max = 2.0                # sqrt(gamma_44), gamma_44 = 4
Lambda_mass = M0*omega_max     # MeV  = 55.801830
m_e       = 0.51099895000      # MeV
m_mu      = 105.6583755        # MeV
m_tau     = 1776.86            # MeV
alpha     = 1/137.035999084
a_e_exp   = 0.00115965218059   # Schwinger + higher orders
a_e_err   = 1.3e-13            # absolute experimental error
rel_prec  = a_e_err/a_e_exp    # relative precision
R_world   = 4129.94            # Mpc
Mpc_m     = 3.085677581e22     # m per Mpc
hbar_c_eVm = 1.973269804e-7    # eV·m

print("=" * 76)
print("B1 — 4-D master integral with a hard cutoff (analytic vs numeric)")
print("=" * 76)
print("""
  ∫_{|k|<Λ} d⁴k/(k²+Δ)³  =  π²·[ 1/(2Δ) − 1/(Λ²+Δ) + Δ/(2(Λ²+Δ)²) ]

  Equivalent form:  1/Δ_eff = 1/Δ · 1/(1+Δ/Λ²)²
""")
def master_analytic(Lam, D):
    return math.pi**2*(1/(2*D) - 1/(Lam**2+D) + D/(2*(Lam**2+D)**2))
def master_numeric(Lam, D, N=4000000):
    L2 = Lam**2
    u = (np.arange(N)+0.5)*(L2/N)
    return math.pi**2*float(np.sum(u/(u+D)**3*(L2/N)))
for (Lam, D) in [(10.0, 1.0), (3.0, 1.0), (100.0, 7.0), (1.0, 4.0)]:
    an = master_analytic(Lam, D); nu = master_numeric(Lam, D, 2000000)
    print(f"  Λ={Lam:7.2f} Δ={D:6.2f}  analytic={an:.10e}  numeric={nu:.10e}  dev={abs(an-nu)/an*100:.5f}%")
    check(f"master integral Λ={Lam}, Δ={D}", abs(an-nu)/an < 1e-5)
for (Lam, D) in [(10.0, 1.0), (3.0, 0.25), (100.0, 7.0)]:
    lhs = 2*master_analytic(Lam, D)/math.pi**2
    rhs = 1.0/(D*(1+D/Lam**2)**2)
    check(f"1/Δ_eff identity Λ={Lam}, Δ={D}", abs(lhs-rhs)/rhs < 1e-14, f"{lhs:.10e}")
check("Λ→∞ limit = π²/(2Δ)", abs(master_analytic(1e8, 3.0) - math.pi**2/6) < 1e-14)

print("\n" + "=" * 76)
print("B2 — a_e(Λ): Schwinger term with a hard loop-momentum cutoff")
print("=" * 76)
print("""
  Feynman-parameter form of the 1-loop vertex magnetic form factor at q²=0:

      a_e = (α/2π) · ∫₀¹dx ∫₀^{1−x}dy · 2(1−x) / [(1−x)² + y]        ( = α/2π )

  Inserting the hard cutoff through 1/Δ → 1/Δ_eff, with ε=1−x, r=m²/Λ²:

      a_e(Λ) = (α/2π) ∫₀¹ dε · 2ε · [ F(t₂) − F(t₁) ]
      F(t)   = ln(t/(1+rt)) + 1/(1+rt),  t₁ = ε²,  t₂ = ε(1+ε)

  (y-integral done analytically via 1/[t(1+rt)²] = 1/t − r/(1+rt) − r/(1+rt)².)
""")
def a_e_over_schwinger(Lam, m):
    r = 0.0 if Lam is None else (m/Lam)**2
    N = 2000000; h = 1.0/N
    eps = (np.arange(N)+0.5)*h
    t1 = eps*eps; t2 = eps*(1.0+eps)
    F = lambda t: np.log(t/(1.0+r*t)) + 1.0/(1.0+r*t)
    return float(np.sum(2.0*eps*(F(t2)-F(t1))*h))
lim = a_e_over_schwinger(None, m_e)
print(f"  no-cutoff limit of the ε-integral = {lim:.12f}   (must be 1.0)")
check("ε-representation reproduces Schwinger (α/2π)", abs(lim-1.0) < 1e-9, f"{lim:.12f}")
for L in (1e6, 1e4, 1000.0, 200.0):
    v = a_e_over_schwinger(L, m_e)
    print(f"  Λ = {L:9.1f} MeV  (Λ/m_e = {L/m_e:9.2f})  →  a_e(Λ)/a_e(∞) = {v:.10f}   Δrel = {(v-1):+.3e}")
    check(f"a_e(Λ) < a_e(∞) for Λ={L}", v < 1.0)

print("\n" + "=" * 76)
print("B3a — RIGOROUS argument (needs no loop integral at all)")
print("=" * 76)
print("""
  Λ_mass = 55.80 MeV is the top of the K_Chain FERMION MASS spectrum.
  If it were ALSO a momentum cutoff on QED loops, every fermion with mass
  above 55.80 MeV would have a loop that is identically ZERO — the integrand
  would have no support at all.  But IDCM's OWN spectrum contains:
""")
sp_all = [("tau", 1770.8), ("b", 4191.4), ("t", 173937.0)]
for nm, mm in sp_all:
    print(f"    {nm:>4}: m = {mm:8.1f} MeV = {mm/Lambda_mass:9.2f} × Λ_mass")
print(f"""
  ⇒ a momentum cutoff at 55.80 MeV would delete the τ, b and t loops from IDCM
    itself.  IDCM's own fermion spectrum CONTRADICTS reading Λ_mass as a
    momentum cutoff.  Self-consistency argument, no loop computation needed.
    ⇒ Λ_mass is a MASS-spectrum bound only.  🟢
""")
check("IDCM spectrum exceeds Λ_mass (self-contradiction proven)",
      all(mm > Lambda_mass for _, mm in sp_all),
      f"τ {1770.8/Lambda_mass:.1f}×, b {4191.4/Lambda_mass:.1f}×, t {173937.0/Lambda_mass:.0f}×")

print("\n" + "=" * 76)
print("B3b — ILLUSTRATIVE quantitative estimate (coefficient is O(1))")
print("=" * 76)
print(f"  Λ_mass = M₀·ω_max = {M0} × {omega_max} = {Lambda_mass:.6f} MeV")
print(f"  Λ_mass/m_e = {Lambda_mass/m_e:.3f}")
print(f"  r = (m_e/Λ)² = {(m_e/Lambda_mass)**2:.6e}")
v_e  = a_e_over_schwinger(Lambda_mass, m_e)
v_mu = a_e_over_schwinger(Lambda_mass, m_mu)
print(f"\n  electron: a_e(Λ)/a_e(∞) = {v_e:.10f}   → Δa_e/a_e = {v_e-1:+.4e}")
print(f"  muon    : a_μ(Λ)/a_μ(∞) = {v_mu:.10f}   → Δa_μ/a_μ = {v_mu-1:+.4e}")
print(f"           (m_μ = {m_mu} MeV > Λ = {Lambda_mass:.2f} MeV — the dominant")
print(f"            region of the muon loop lies ENTIRELY above the cutoff)")
d_a_e = abs(v_e-1)*a_e_exp
print(f"\n  implied shift in a_e = {d_a_e:.4e}")
print(f"  experimental error   = {a_e_err:.4e}   (relative {rel_prec:.3e})")
print(f"  ⇒ discrepancy = {d_a_e/a_e_err:.3e} × the experimental error")
print(f"  ⇒ discrepancy = {abs(v_e-1)/rel_prec:.3e} × the relative precision")
print("""
  ⚠️ CAVEAT on the coefficient: the hard cutoff is inserted through the scalar
     master integral ∫d⁴k/(k²+Δ)³, which is exact for the log-dominant piece.
     Sub-leading numerator structures (∝k^αk^β) carry a log-divergent piece that
     cancels between numerator terms in the exact F₂; the residual cutoff
     dependence is O(m²/Λ²) with an O(1) coefficient this representation does
     not fix.  The conclusion is a falsification at ~10⁶ σ, so an O(1)
     coefficient uncertainty is immaterial — and B3a settles it independently.
""")
check("Λ=55.8 MeV is FALSIFIED as a momentum cutoff", abs(v_e-1)/rel_prec > 1e3,
      f"{abs(v_e-1)/rel_prec:.2e} sigma (O(1) coefficient)")

print("\n" + "=" * 76)
print("B4 — Invert: what Λ does a_e require?")
print("=" * 76)
def solve_Lam(target_rel, m):
    lo, hi = 1e3, 1e12
    for _ in range(200):
        mid = math.sqrt(lo*hi)
        if abs(a_e_over_schwinger(mid, m)-1.0) > target_rel:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo*hi)
Lam_req = solve_Lam(rel_prec, m_e)
print(f"  target relative precision (experiment) = {rel_prec:.3e}")
print(f"  ⇒ required Λ ≳ {Lam_req/1000:.2f} GeV  ({Lam_req:.3e} MeV)")
print(f"     ratio to Λ_mass = 55.80 MeV : {Lam_req/Lambda_mass:.1f} ×")
print("  tolerance scan (coefficient-robust statement of the bound):")
for tol in (1e-12, 1e-10, 1e-8, 1e-6):
    L = solve_Lam(tol, m_e)
    print(f"    |Δa_e/a_e| < {tol:.0e}  →  Λ ≳ {L/1000:9.3f} GeV   ({L/Lambda_mass:8.1f} × Λ_mass)")
Lam_1e6 = solve_Lam(1e-6, m_e)
check("required Λ > 10 × Λ_mass even at 1e-6 tolerance", Lam_1e6/Lambda_mass > 10,
      f"{Lam_1e6/Lambda_mass:.0f}× at 1e-6")
check("required Λ > 100 × Λ_mass at experimental precision", Lam_req/Lambda_mass > 100,
      f"{Lam_req/Lambda_mass:.0f}×")

print("\n" + "=" * 76)
print("B5 — Map Λ onto the FSR layer index ℓ (O140 spatial lattice)")
print("=" * 76)
print("""
  FSR (O140 scripts/01):  a = R_world/44,  p_n = ħπn/(44a)
  Scale refinement:       a_ℓ = R_world/(44·4^ℓ)
  ⇒ Brillouin-zone edge   Λ_ℓ = ħπ/a_ℓ = ħπ·44·4^ℓ / R_world
  ⇒ fundamental quantum   p_min = ħπ/R_world      (LAYER-INDEPENDENT)
""")
a0_m = R_world*Mpc_m/44
print(f"  R_world = {R_world} Mpc = {R_world*Mpc_m:.6e} m")
print(f"  a_0 = R_world/44 = {a0_m:.6e} m")
Lam0_eV = hbar_c_eVm*math.pi/a0_m
print(f"  Λ_0 = ħπ/a_0 = {Lam0_eV:.6e} eV = {Lam0_eV/1e6:.6e} MeV")
pmin_eV = hbar_c_eVm*math.pi/(R_world*Mpc_m)
print(f"  p_min = ħπ/R_world = {pmin_eV:.6e} eV   (same at every ℓ)")
print(f"  p_min/m_e = {pmin_eV/(m_e*1e6):.3e}   → loop-momentum DISCRETISATION is harmless")
def Lam_of_ell(ell):   # MeV
    return Lam0_eV*4.0**ell/1e6
def ell_of_Lam(Lam_MeV):
    return math.log(Lam_MeV/(Lam0_eV/1e6))/math.log(4.0)
print(f"\n  {'ℓ':>4} | {'a_ℓ (m)':>14} | {'Λ_ℓ (MeV)':>14} | {'Λ_ℓ/m_e':>12} | a_e(Λ)/a_e(∞)")
print("  " + "-"*74)
for ell in [0, 30, 60, 63, 65, 69, 70, 75]:
    a_l = R_world*Mpc_m/(44*4.0**ell)
    L   = Lam_of_ell(ell)
    v   = a_e_over_schwinger(L, m_e)
    note = "" if L > m_e else "   <- cutoff BELOW m_e"
    print(f"  {ell:4d} | {a_l:14.4e} | {L:14.6e} | {L/m_e:12.4e} | {v:.10f}{note}")
ell_req = ell_of_Lam(Lam_req)
print(f"\n  required Λ = {Lam_req/1000:.2f} GeV  →  ℓ_req = {ell_req:.4f}")
print(f"  so the lab frame must sit at  ℓ ≳ {math.ceil(ell_req)}")
check("ℓ_req finite and in a plausible range", 60 < ell_req < 80, f"{ell_req:.4f}")
lam_C = 2.42631023867e-12  # m
ell_C = math.log(R_world*Mpc_m/lam_C)/math.log(4.0)
Lam_C = Lam_of_ell(ell_C)
v_C   = a_e_over_schwinger(Lam_C, m_e)
print(f"\n  [cross-check] layer that resolves λ_C(e) = {lam_C:.4e} m : ℓ = {ell_C:.2f}")
print(f"                (the WITHDRAWN ℓ_min = 60 criterion, refined to {ell_C:.1f})")
print(f"                Λ_{ell_C:.1f} = {Lam_C:.4f} MeV = {Lam_C/m_e:.2f} × m_e")
print(f"                a_e(Λ)/a_e(∞) = {v_C:.8f}  →  Δa_e/a_e = {v_C-1:+.3e}")
print(f"                = {abs(v_C-1)/rel_prec:.3e} × the experimental precision")
print(f"  ⇒ resolving λ_C is NOT sufficient: it leaves a {abs(v_C-1)*100:.3f}% error in a_e.")
a_req = R_world*Mpc_m/(44*4.0**ell_req)
print(f"  required lattice spacing a_ℓ = {a_req:.4e} m = λ_C(e) / {lam_C/a_req:.3e}")
check("λ_C-resolving layer still fails a_e", abs(v_C-1)/rel_prec > 1e3,
      f"{abs(v_C-1)/rel_prec:.2e} sigma at ℓ={ell_C:.1f}")
print(f"""
  COEFFICIENT SENSITIVITY: an O(1) uncertainty in the O(m²/Λ²) coefficient
  rescales the required Λ by 1/sqrt(coeff), shifting ℓ by log₄(1/sqrt(c)).
  A factor c = 10 smaller coefficient moves ℓ_req from {ell_req:.2f} down by only
  {math.log(math.sqrt(10))/math.log(4):.2f} layers → ℓ ≳ {math.ceil(ell_req-math.log(math.sqrt(10))/math.log(4))}.  The bound is robust.

  CONVENTION SENSITIVITY: the project has an internal conflict on the lattice
  spacing — O140 FSR and src/kchain_wave_params.py line 32 use a = R_world/44,
  while O86 docs/02 line 46 and O82 docs/02 line 28 use a = R_world/88.
  Doubling a halves Λ_ℓ, shifting ℓ_req by −log₄2 = −0.50:
    a = R_world/44  →  ℓ_req = {ell_req:.2f}
    a = R_world/88  →  ℓ_req = {ell_req - math.log(2)/math.log(4):.2f}
  ⇒ the quoted bound ℓ ≳ {math.ceil(ell_req)} is unchanged under either convention.
""")

print("\n" + "=" * 76)
print("B6 — CUTOFF effect vs DISCRETISATION effect (they are different!)")
print("=" * 76)
print(f"""
  DISCRETISATION: the momentum quantum is p_min = ħπ/R_world = {pmin_eV:.3e} eV
    — set by the WORLD SIZE, not by ℓ. The Schwinger loop is dominated by
    k ~ m_e = {m_e*1e6:.3e} eV, i.e. {m_e*1e6/pmin_eV:.3e} quanta above the fundamental.
    ⇒ discretisation is unobservable. NOT a problem.

  CUTOFF: the highest momentum the layer-ℓ lattice supports is Λ_ℓ = ħπ/a_ℓ.
    At ℓ = 0, Λ_0 = {Lam0_eV:.3e} eV << m_e → the electron loop cannot even
    be represented. At ℓ = {math.ceil(ell_req)}, Λ = {Lam_of_ell(math.ceil(ell_req))/1000:.2f} GeV → consistent with a_e.

  ⇒ The binding constraint is the CUTOFF, not the discretisation.
""")
check("discretisation harmless (p_min << m_e)", pmin_eV < m_e*1e6*1e-30, f"p_min/m_e = {pmin_eV/(m_e*1e6):.2e}")

print("\n" + "=" * 76)
print("B7 — Null test on the resulting ℓ, and VERDICT")
print("=" * 76)
lib = {"Nd":44,"B":4,"N_gen":3,"L4":7,"L5":11,"L6":18,"L7":29,
       "F5":5,"F6":8,"F7":13,"F8":21,"F9":34,"F10":55,"F_proj":17,
       "M":33,"CY3":134,"C_B2_2":120,"N_colour":3}
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
target = math.ceil(ell_req)
window = list(range(target-2, target+3))
cov = [v for v in window if v in expr]
print(f"  target ℓ = {target};  window [{window[0]},{window[-1]}] coverage = {len(cov)}/{len(window)} = {len(cov)/len(window)*100:.0f}%")
for v in window:
    print(f"    {v}: {'hit' if v in expr else 'miss'}  ({len(expr.get(v,()))} expressions)")
print(f"""
  ⇒ window coverage {len(cov)}/{len(window)} = {len(cov)/len(window)*100:.0f}% — NOT fully covered; ℓ = {target}, {target+1}, {target+2} have
    ZERO expressions in the library.  So ℓ ≳ {target} is NOT a symbol-library
    artefact (contrast the WITHDRAWN ℓ_min = 60, which had 100% window coverage).
    But it is still not a structural IDENTITY: it is an OBSERVABLE-DERIVED BOUND
    (from a_e), which is exactly what it should be.

  VERDICT
  ───────
  🟢 Λ_mass = 55.80 MeV is NOT a momentum cutoff — proven by self-contradiction
     (B3a): IDCM's own spectrum has τ/b/t at {1770.8/Lambda_mass:.0f}×/{4191.4/Lambda_mass:.0f}×/{173937.0/Lambda_mass:.0f}× Λ_mass.  A momentum cutoff there would
     delete those loops.  It is a MASS-spectrum bound.
     Illustratively, treating it as a momentum cutoff would shift a_e by
     {abs(v_e-1):.2e} relative = {abs(v_e-1)/rel_prec:.1e} × the experimental precision (O(1) coefficient).

  🟢 The FSR spatial lattice's DISCRETISATION is harmless: p_min = ħπ/R_world
     = {pmin_eV:.2e} eV is layer-independent and {m_e*1e6/pmin_eV:.1e}× below m_e.

  🟢 NEW STRUCTURAL CONSTRAINT: the FSR CUTOFF Λ_ℓ = ħπ·44·4^ℓ/R_world must
     exceed ~{Lam_req/1000:.0f} GeV for a_e to match experiment ⇒ ℓ ≳ {target}.
     Coefficient-robust range: ℓ ≳ {ell_of_Lam(Lam_1e6):.1f} (1e-6 tolerance) … {ell_req:.1f} (experimental
     precision) → quote as ℓ ≳ {math.ceil(ell_of_Lam(Lam_1e6))}–{target}.
     At ℓ = 0 the cutoff is {Lam0_eV:.1e} eV, so the lab frame cannot be ℓ = 0.
     This is an OBSERVABLE-DRIVEN bound on FSR's open question
     "which layer is the local reference frame?" (o140 🔴), replacing the
     withdrawn symbol-match claim ℓ_min = 60 (❌).

  🔴 STILL OPEN: whether IDCM identifies the FSR lattice with the electron's
     loop-momentum measure.  Branch 1: the chain is ONLY a mass/spectral
     lattice → no truncation at all, B closes trivially.  Branch 2: the FSR
     spatial reading applies (the framework's own reading, since FSR derives
     p_n = ħπn/(44a)) → the ℓ ≳ {target} bound stands as a constraint on o140.
     Both branches recorded; B is 🟡 (framework-conditional), not 🔴.
""")
check("window coverage reported (null test executed)", len(cov) > 0, f"{len(cov)}/{len(window)}")

print("=" * 76)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL")
print("=" * 76)
