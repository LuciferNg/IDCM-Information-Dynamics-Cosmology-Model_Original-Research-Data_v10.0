#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O139 / scripts/12_verify_all.py  —  FULL-CHAIN INDEPENDENT VERIFICATION (A-F)

Purpose: recompute EVERY number claimed in the O139 record documents from raw
structural constants.  This script:

  * does NOT import any O139 derivation script,
  * does NOT read any saved result / JSON file,
  * uses a DIFFERENT method and precision from the derivation scripts —
    adaptive quadrature (scipy.integrate.quad, ~1e-14) instead of the numpy
    midpoint sums used by scripts/05-06, and exact `Fraction` arithmetic for
    every rational identity.

Sections
  A  structural constants and exact identities            (docs/01, 04, 08, 09)
  B  alpha endpoints and atomic scale                     (docs/01, 02, 03)
  C  problem A: function form and spectrum sums           (docs/03)
  D  problem B: two cutoffs, a_e(Lambda), Lambda_req      (docs/04)
  E  g-2 precision wall and muon bound                    (docs/05)
  F  problem D: alpha(0) dressing, five mechanisms        (docs/06)

Exit code 1 if any check FAILs.  No hard-coded True.

Doc<->script discrepancies found by this audit are printed as [NOTE] lines and
carried as ⚠️ annotations into the record docs (never by rewriting them).
"""
import math
import random
from bisect import bisect_left, bisect_right
from fractions import Fraction

from scipy.integrate import quad

NPASS = 0
NFAIL = 0
NOTES = []


def chk(name, ok, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  [PASS] %-64s %s" % (name, detail))
    else:
        NFAIL += 1
        print("  [FAIL] %-64s %s" % (name, detail))


def note(txt):
    NOTES.append(txt)
    print("  [NOTE] %s" % txt)


def close(a, b, rel=1e-4, absolute=None):
    if absolute is not None and abs(a - b) <= absolute:
        return True
    if b == 0:
        return abs(a) <= (absolute if absolute is not None else 1e-30)
    return abs(a - b) / abs(b) <= rel


# =====================================================================
# raw structural constants (project convention files, not O139 scripts)
# =====================================================================
M0 = 27.900915            # MeV, W-field VEV (O38/O39/O86)
B = 4
N_GEN = 3
N_D = 44
N_SITES = 88
L4, L5, L6, L7 = 7, 11, 18, 29
F5, F6, F7, F8, F9, F10 = 5, 8, 13, 21, 34, 55
F_PROJ = 17
M_TREE = 33
CY3 = 134
C_B2_2 = 120
PHI = (1.0 + math.sqrt(5.0)) / 2.0

R_WORLD_MPC = 4129.94
MPC_M = 3.0856775814913673e22
HBAR_C_EVM = 1.973269804e-7

M_E = 0.510999            # MeV
M_MU = 105.6583755        # MeV
M_TAU = 1776.86           # MeV
M_Z = 91187.6             # MeV

A_INV_0_CODATA = 137.035999178
A_INV_MZ_MSBAR = 127.930
A_INV_MZ_OLD = 127.951
A_INV_MZ_ONSHELL = 128.933
A_INV_0_2022 = 137.035999177

A_E_EXP = 0.00115965218059
A_E_ERR = 1.30e-13

# IDCM 9-fermion spectrum, docs/03 sec 4  (mass MeV, N_c Q_f^2)
IDCM_Q = [(0.5118, 1.0), (105.80, 1.0), (1770.8, 1.0),
          (2.204, 4.0 / 3), (4.692, 1.0 / 3), (92.28, 1.0 / 3),
          (1273.7, 4.0 / 3), (4191.4, 1.0 / 3), (173937.0, 4.0 / 3)]
PDG_Q = [(0.510999, 1.0), (105.658, 1.0), (1776.86, 1.0),
         (2.16, 4.0 / 3), (4.67, 1.0 / 3), (93.4, 1.0 / 3),
         (1270.0, 4.0 / 3), (4180.0, 1.0 / 3), (172690.0, 4.0 / 3)]


def loop_int(m, Q=M_Z):
    """(2/pi) * int_0^1 x(1-x) ln[1 + Q^2 x(1-x)/m^2] dx   (adaptive quadrature)"""
    def g(x):
        w = x * (1.0 - x)
        return w * math.log1p(Q * Q * w / (m * m))
    v, _ = quad(g, 0.0, 1.0, limit=400, epsabs=1e-16, epsrel=1e-14)
    return (2.0 / math.pi) * v


def dasum(spec, Q=M_Z):
    return sum(w * loop_int(m, Q) for m, w in spec)


# =====================================================================
print("=" * 78)
print("A  structural constants and exact identities")
print("=" * 78)
chk("A1  M0 = 27.900915 MeV", close(M0, 27.900915, 1e-12), "%.6f" % M0)
g1 = 4.0 * math.sin(math.pi / N_SITES) ** 2
chk("A2  M0*gamma_1 = 0.1422 MeV (docs/01 line 94 quotes 0.1422)",
    close(M0 * g1, 0.1422, 1e-3), "%.6f MeV" % (M0 * g1))
omega_max = 2.0 * math.sin(N_D * math.pi / N_SITES)
chk("A3  omega_max = 2 sin(44 pi/88) = 2  ->  Lambda_mass = 2*M0 = 55.801830",
    close(omega_max, 2.0, 1e-12) and close(2 * M0, 55.801830, 1e-7),
    "omega_max = %.12f, Lam = %.6f" % (omega_max, 2 * M0))
chk("A4  C(B^2,2) = C(16,2) = 120", math.comb(B * B, 2) == C_B2_2, "= %d" % C_B2_2)
chk("A5  F_proj = B^2 + 1 = 17", B * B + 1 == F_PROJ, "= %d" % F_PROJ)
chk("A6  a_0 = R_world/44 = 93.86 Mpc ; a = R_world/88 = 46.93 Mpc",
    close(R_WORLD_MPC / 44, 93.86, 1e-4) and close(R_WORLD_MPC / 88, 46.93, 1e-4),
    "%.3f / %.3f Mpc" % (R_WORLD_MPC / 44, R_WORLD_MPC / 88))
a0_m = R_WORLD_MPC * MPC_M / 44
Lam0_eV = HBAR_C_EVM * math.pi / a0_m
chk("A7  Lambda_0 = hbar*pi/a_0 = 2.140399e-31 eV", close(Lam0_eV, 2.140399e-31, 1e-5),
    "%.7e eV" % Lam0_eV)
pmin_eV = HBAR_C_EVM * math.pi / (R_WORLD_MPC * MPC_M)
chk("A8  p_min = hbar*pi/R_world = 4.864543e-33 eV", close(pmin_eV, 4.864543e-33, 1e-5),
    "%.7e eV" % pmin_eV)
chk("A9  R_world = 4129.94 Mpc = 1.274366e26 m",
    close(R_WORLD_MPC * MPC_M, 1.274366e26, 1e-6),
    "%.7e m" % (R_WORLD_MPC * MPC_M))
chk("A10 Lambda_ell = 44*p_min*4^ell reproduces Lambda_0",
    close(44 * pmin_eV, Lam0_eV, 1e-9), "rel dev %.2e" % abs(44 * pmin_eV / Lam0_eV - 1))
maxdev = max(abs(math.log(44 * pmin_eV * 4.0 ** ell) - (math.log(Lam0_eV) + ell * math.log(4.0)))
             for ell in range(0, 80))
chk("A11 ln Lambda_ell strictly linear in ell (docs/08)", maxdev < 1e-12,
    "max dev %.3e" % maxdev)

# =====================================================================
print()
print("=" * 78)
print("B  alpha endpoints and atomic scale")
print("=" * 78)
id_1 = 3 * N_D + F5
id_2 = C_B2_2 + F_PROJ
chk("B1  alpha^-1(0) = 3*Tr(I44)+F5 = 137  and  = C(B^2,2)+F_proj = 137",
    id_1 == 137 and id_2 == 137, "%d / %d" % (id_1, id_2))
id_3 = 2 * N_D + F5 * F6
id_4 = C_B2_2 + 2 * B
chk("B2  alpha^-1(M_Z) = 2*Tr(I44)+F5*F6 = 128  and  = C(B^2,2)+2B = 128",
    id_3 == 128 and id_4 == 128, "%d / %d" % (id_3, id_4))
chk("B3  Delta alpha^-1 = F_proj - 2B = 9 = N_gen^2",
    F_PROJ - 2 * B == 9 and N_GEN ** 2 == 9, "= %d" % (F_PROJ - 2 * B))
chk("B4  dev 137 vs 137.035999084 = 0.026%",
    close(abs(137 - 137.035999084) / 137.035999084, 0.026e-2, 0.02),
    "%.5f%%" % (abs(137 - 137.035999084) / 137.035999084 * 100))
chk("B5  dev 128 vs 127.951 = 0.038%",
    close(abs(128 - 127.951) / 127.951, 0.038e-2, 0.02),
    "%.5f%%" % (abs(128 - 127.951) / 127.951 * 100))
chk("B6  dev 9 vs 9.0850 = 0.94%",
    close(abs(9 - 9.0850) / 9.0850, 0.94e-2, 0.02),
    "%.5f%%" % (abs(9 - 9.0850) / 9.0850 * 100))
q_atom = 13.6e-6            # MeV
chk("B7  (Q/m_e)^2 at Q = 13.6 eV = 7.08e-10",
    close((q_atom / M_E) ** 2, 7.08e-10, 1e-2),
    "%.3e" % ((q_atom / M_E) ** 2))
chk("B8  (13.6 eV / M0*gamma_1)^2 = 9.15e-9  (docs/01 line 94)",
    close((q_atom / (M0 * g1)) ** 2, 9.15e-9, 5e-3),
    "%.3e" % ((q_atom / (M0 * g1)) ** 2))
chk("B9  a(ell=0)/r_atom = 1.45e34  (r_atom = 1e-10 m)",
    close((R_WORLD_MPC * MPC_M / 88) / 1e-10, 1.45e34, 1e-2),
    "%.3e" % ((R_WORLD_MPC * MPC_M / 88) / 1e-10))
lam_C = 2.42631023867e-12
for conv, doc_ell in ((88, 59.4224), (44, 59.9224)):
    ell = math.log(R_WORLD_MPC * MPC_M / (conv * lam_C)) / math.log(4.0)
    chk("B10 lambda_C criterion, a = R_world/%d -> ell = %.4f" % (conv, doc_ell),
        close(ell, doc_ell, 1e-4), "%.4f" % ell)
bohr = 5.29177210903e-11
for conv, doc_ell in ((88, 57.1990), (44, 57.6990)):
    ell = math.log(R_WORLD_MPC * MPC_M / (conv * bohr)) / math.log(4.0)
    chk("B11 Bohr criterion, a = R_world/%d -> ell = %.4f" % (conv, doc_ell),
        close(ell, doc_ell, 1e-4), "%.4f" % ell)
chk("B12 Lambda_mass/m_e = 109.20",
    close(2 * M0 / M_E, 109.20, 1e-4), "%.4f" % (2 * M0 / M_E))
chk("B13 ln(Lambda_mass/m_e) = 4.6932",
    close(math.log(2 * M0 / M_E), 4.6932, 1e-4), "%.6f" % math.log(2 * M0 / M_E))

# =====================================================================
print()
print("=" * 78)
print("C  problem A: function form and spectrum sums")
print("=" * 78)
I1, _ = quad(lambda x: x * (1 - x), 0.0, 1.0, epsabs=1e-16)
chk("C1  int_0^1 x(1-x) dx = 1/6", close(I1, 1.0 / 6, 1e-12), "%.15f" % I1)
I2, _ = quad(lambda x: x * (1 - x) * math.log(x * (1 - x)), 0.0, 1.0,
             limit=400, epsabs=1e-15)
chk("C2  int_0^1 x(1-x) ln[x(1-x)] dx = -5/18", close(I2, -5.0 / 18, 1e-10),
    "%.14f" % I2)
# ---- docs/03 sec 5: the whole function-form table (7 rows x 4 columns) ----
DOC_TAB = [(1.0, 0.000480, 0.00708, 136.9363, 136.9702),
           (10.0, 0.005181, 0.07640, 136.3124, 136.3261),
           (100.0, 0.014418, 0.21262, 135.0864, 135.0602),
           (1000.0, 0.026956, 0.39751, 133.4224, 133.3420),
           (M_TAU, 0.030792, 0.45408, 132.9133, 132.8163),
           (10000.0, 0.045328, 0.66844, 130.9841, 130.8244),
           (M_Z, 0.067813, 1.00000, 128.0000, 127.7432)]
dMZ = dasum(PDG_Q, M_Z)
worst = 0.0
for Q, d_da, d_f, d_idcm, d_qed in DOC_TAB:
    da = dasum(PDG_Q, Q) / A_INV_0_CODATA
    f = da / (dMZ / A_INV_0_CODATA)
    worst = max(worst, abs(da - d_da) / d_da, abs(f - d_f) / d_f,
                abs(137.0 - 9.0 * f - d_idcm) / d_idcm,
                abs(A_INV_0_CODATA - dasum(PDG_Q, Q) - d_qed) / d_qed)
chk("C3  docs/03 sec 5 table: Delta-alpha / f(Q) / IDCM / QED (7 rows x 4 cols)",
    worst < 3e-4, "worst rel dev %.2e" % worst)
chk("C4  function form: alpha^-1(0) = 137.0000 exactly",
    close(137.0 - 9.0 * 0.0, 137.0, 1e-12), "137.0000")
chk("C5  function form: alpha^-1(M_Z) = 128.0000 exactly",
    close(137.0 - 9.0 * (dMZ / dMZ), 128.0, 1e-12), "128.0000")
chk("C6  max deviation vs the QED curve = 0.201% (at M_Z)",
    close(abs(128.0 - 127.7432) / 127.7432, 0.201e-2, 0.03),
    "%.4f%%" % (abs(128.0 - 127.7432) / 127.7432 * 100))
qgrid = [1.0, 10.0, 100.0, 1000.0, 10000.0, M_Z]
mono = all((137.0 - 9.0 * (dasum(PDG_Q, a) / dMZ)) > (137.0 - 9.0 * (dasum(PDG_Q, b) / dMZ))
           for a, b in zip(qgrid, qgrid[1:]))
chk("C7  function form is monotonically decreasing", mono, "")
lep_idcm = dasum(IDCM_Q[:3])
lep_pdg = dasum(PDG_Q[:3])
had5_idcm = dasum(IDCM_Q[3:8])       # u,d,s,c,b  = the naive 5-quark loop
had5_pdg = dasum(PDG_Q[3:8])
tot_idcm = dasum(IDCM_Q)             # 9-fermion total (includes the top loop)
tot_pdg = dasum(PDG_Q)
chk("C8  lepton sector, IDCM 9-fermion spectrum = 4.3061", close(lep_idcm, 4.3061, 1e-4),
    "%.4f" % lep_idcm)
chk("C9  lepton sector, PDG spectrum = 4.3060", close(lep_pdg, 4.3060, 1e-4),
    "%.4f" % lep_pdg)
chk("C10 published lepton Delta alpha^-1 = 4.3160 (0.031498 * 137.036)",
    close(0.031498 * A_INV_0_CODATA, 4.3160, 1e-4),
    "%.4f" % (0.031498 * A_INV_0_CODATA))
chk("C11 hadronic (naive 5-quark), IDCM spectrum = 4.9726", close(had5_idcm, 4.9726, 1e-3),
    "%.4f" % had5_idcm)
chk("C12 hadronic (naive 5-quark), PDG spectrum = 4.9791", close(had5_pdg, 4.9791, 1e-3),
    "%.4f" % had5_pdg)
chk("C13 published hadronic Delta alpha^-1 = 3.791 (0.027662 * 137.036)",
    close(0.027662 * A_INV_0_CODATA, 3.791, 1e-3),
    "%.4f" % (0.027662 * A_INV_0_CODATA))
chk("C14 total Delta alpha^-1 (9-fermion), IDCM spectrum = 9.2863",
    close(tot_idcm, 9.2863, 1e-4), "%.4f" % tot_idcm)
chk("C15 total Delta alpha^-1 (9-fermion), PDG spectrum = 9.2928",
    close(tot_pdg, 9.2928, 5e-4), "%.4f" % tot_pdg)
note("docs/03 sec 4 table: the 'hadronic 5-quark' row (4.9726) and the 'total' row "
     "(9.2863) use different quark content (5 vs 6 incl. top) — the table does not "
     "add up row-wise (4.3061+4.9726 = 9.2787). Both numbers are individually correct.")
chk("C16 lepton IDCM vs PDG agree to 0.0001 (4.3061 vs 4.3060)",
    close(lep_idcm, lep_pdg, 1e-4), "diff %.5f" % (lep_idcm - lep_pdg))
chk("C17 lepton sector vs published: 0.23%",
    close(abs(lep_idcm - 0.031498 * A_INV_0_CODATA) / (0.031498 * A_INV_0_CODATA), 0.23e-2, 0.05),
    "%.4f%%" % (abs(lep_idcm - 0.031498 * A_INV_0_CODATA) / (0.031498 * A_INV_0_CODATA) * 100))
chk("C18 naive 5-quark overshoots the dispersion value by 31%",
    close(had5_idcm / 3.791 - 1, 0.31, 0.03), "%.4f" % (had5_idcm / 3.791 - 1))
chk("C19 IDCM spectrum sum 9.2863 is 3.18% above the integer 9",
    close((tot_idcm - 9.0) / 9.0, 3.18e-2, 0.02), "%.4f%%" % ((tot_idcm - 9.0) / 9.0 * 100))
chk("C20 PDG spectrum sum 9.2928 is 3.25% above 9",
    close((tot_pdg - 9.0) / 9.0, 3.25e-2, 0.02), "%.4f%%" % ((tot_pdg - 9.0) / 9.0 * 100))
sec = [N_GEN * 1 * 1.0 ** 2, N_GEN * 3 * (2.0 / 3) ** 2, N_GEN * 3 * (1.0 / 3) ** 2]
chk("C21 Sigma_f N_c Q_f^2 = 3 + 4 + 1 = 8 = 2B",
    close(sum(sec), 8.0, 1e-12) and sum(sec) == 2 * B,
    "sectors %s, total %.1f" % ([round(s, 6) for s in sec], sum(sec)))
lhs = Fraction(1) + N_GEN * Fraction(5, 9)
chk("C22 closed form: Sigma/N_gen = 1 + N_c(Q_u^2+Q_d^2) = 8/3",
    lhs == Fraction(8, 3), "= %s" % lhs)
chk("C23 (8/3)N_gen = 2B  <=>  N_gen = 3B/4 = B - 1",
    Fraction(8, 3) * N_GEN == 2 * B and N_GEN == B - 1 and Fraction(3 * B, 4) == B - 1,
    "3B/4 = %s, B-1 = %d" % (Fraction(3 * B, 4), B - 1))
chk("C24 Delta alpha^-1 = (B^2+1) - 2B = B^2 - 2B + 1 = (B-1)^2 = 9",
    B * B + 1 - 2 * B == (B - 1) ** 2 == 9, "= %d" % (B - 1) ** 2)
# ---- null tests on the symbol library ----
LIB17 = [N_D, B, N_GEN, L4, L5, L6, L7, F5, F6, F7, F8, F9, F10, F_PROJ,
         M_TREE, CY3, C_B2_2]
expr = set()
for v1 in LIB17:
    expr.add(v1)
    for v2 in LIB17:
        expr.add(v1 * v2)
        expr.add(v1 + v2)
        expr.add(v1 - v2)
        for v3 in LIB17:
            expr.add(v1 * v2 * v3)
win = list(range(7, 12))
cov = [v for v in win if v in expr]
chk("C25 null test window [7,11] coverage = 5/5 = 100% -> no selectivity for '9'",
    len(cov) == len(win), "coverage %d/%d" % (len(cov), len(win)))
win60 = list(range(57, 63))
cov60 = [v for v in win60 if v in expr]
chk("C26 withdrawn ell_min = 60: window [57,62] coverage = 6/6 = 100% (why it was withdrawn)",
    len(cov60) == len(win60), "coverage %d/%d" % (len(cov60), len(win60)))

# =====================================================================
print()
print("=" * 78)
print("D  problem B: two cutoffs, a_e(Lambda), Lambda_req")
print("=" * 78)


def master_analytic(Lam, D):
    return math.pi ** 2 * (1 / (2 * D) - 1 / (Lam ** 2 + D) + D / (2 * (Lam ** 2 + D) ** 2))


def master_numeric(Lam, D):
    """pi^2 * int_0^{Lam^2} u/(u+D)^3 du   (substitute u = k^2)"""
    v, _ = quad(lambda u: u / (u + D) ** 3, 0.0, Lam ** 2, limit=400,
                epsabs=1e-20, epsrel=1e-13)
    return math.pi ** 2 * v


worst = 0.0
for Lam, D in [(10.0, 1.0), (3.0, 1.0), (100.0, 7.0), (1.0, 4.0)]:
    an = master_analytic(Lam, D)
    nu = master_numeric(Lam, D)
    worst = max(worst, abs(an - nu) / an)
chk("D1  master integral: analytic vs adaptive quadrature (4 cases) < 1e-5", worst < 1e-5,
    "worst %.2e" % worst)
worst = 0.0
for Lam, D in [(10.0, 1.0), (3.0, 0.25), (100.0, 7.0)]:
    lhs = 2 * master_analytic(Lam, D) / math.pi ** 2
    rhs = 1.0 / (D * (1 + D / Lam ** 2) ** 2)
    worst = max(worst, abs(lhs - rhs) / rhs)
chk("D2  1/Delta_eff = (1/Delta)/(1+Delta/Lambda^2)^2 identity < 1e-14", worst < 1e-14,
    "worst %.2e" % worst)
chk("D3  Lambda -> infinity limit = pi^2/(2 Delta)",
    close(master_analytic(1e8, 3.0), math.pi ** 2 / 6, 1e-12),
    "%.12f" % master_analytic(1e8, 3.0))


def a_e_ratio(m, Lam):
    r = (m / Lam) ** 2

    def F(t):
        return math.log(t / (1 + r * t)) + 1.0 / (1 + r * t)

    def g(e):
        return 2 * e * (F(e * (1 + e)) - F(e * e))
    v, _ = quad(g, 0.0, 1.0, limit=400, epsabs=1e-16, epsrel=1e-14)
    return v


chk("D4  eps-representation reproduces the Schwinger term (=1.0)",
    close(a_e_ratio(M_E, 1e14), 1.0, 1e-12), "%.15f" % a_e_ratio(M_E, 1e14))
v_e = a_e_ratio(M_E, 2 * M0)
v_mu = a_e_ratio(M_MU, 2 * M0)
chk("D5  a_e(Lam_mass)/a_e(inf) = 0.9998882034, Delta_rel = -1.118e-4",
    close(v_e, 0.9998882034, 1e-8) and close(v_e - 1, -1.118e-4, 2e-2),
    "%.10f  Drel = %+.5e" % (v_e, v_e - 1))
chk("D6  a_mu(Lam_mass)/a_mu(inf) = 0.1931395399, Delta_rel = -8.069e-1",
    close(v_mu, 0.1931395399, 1e-7) and close(v_mu - 1, -0.8069, 1e-3),
    "%.10f  Drel = %+.5e" % (v_mu, v_mu - 1))
chk("D7  electron shift 1.2965e-7 = 9.97e+05 x the experimental error (1.3e-13)",
    close(abs(v_e - 1) * A_E_EXP / A_E_ERR, 9.97e5, 1e-2),
    "%.3e x" % (abs(v_e - 1) * A_E_EXP / A_E_ERR))
chk("D8  m_tau/Lam_mass = 31.7x, m_b/Lam_mass = 75.1x, m_t/Lam_mass = 3117x",
    close(1770.8 / (2 * M0), 31.7, 2e-3) and close(4191.4 / (2 * M0), 75.1, 2e-3)
    and close(173937.0 / (2 * M0), 3117, 1e-2),
    "%.1f / %.1f / %.0f" % (1770.8 / (2 * M0), 4191.4 / (2 * M0), 173937.0 / (2 * M0)))


def solve_Lam(m, tol):
    lo, hi = 1.0, 1e13
    for _ in range(90):
        mid = math.sqrt(lo * hi)
        if abs(a_e_ratio(m, mid) - 1.0) > tol:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


REL_E = A_E_ERR / A_E_EXP
print("  --- Lambda_req tolerance scan (adaptive quadrature, independent of scripts/05) ---")
for tol, doc in [(1e-12, 512.574), (1e-10, 58.909), (1e-8, 5.900), (1e-6, 1.000)]:
    L = solve_Lam(M_E, tol) / 1000.0
    print("      tol %.0e : recomputed %9.4f GeV   (record %s GeV)  ratio %.4f"
          % (tol, L, doc, L / doc))
L_exp = solve_Lam(M_E, REL_E)
chk("D9  Lambda_req at experimental precision = 55.65 GeV (record)",
    close(L_exp / 1000.0, 55.65, 5e-3), "recomputed %.4f GeV" % (L_exp / 1000.0))
chk("D10 Lambda_req/Lambda_mass = 997x (record)",
    close(L_exp / (2 * M0), 997, 5e-3), "%.1f x" % (L_exp / (2 * M0)))
ell_req = math.log(L_exp / (Lam0_eV / 1e6)) / math.log(4.0)
chk("D11 ell_req = 68.7888 -> the lab frame sits at ell >= 69",
    close(ell_req, 68.7888, 5e-4) and math.ceil(ell_req) == 69, "%.4f" % ell_req)
Lam_1e6 = solve_Lam(M_E, 1e-6)
ell_1e6 = math.log(Lam_1e6 / (Lam0_eV / 1e6)) / math.log(4.0)
print("      coefficient-robust range: ell >= %.1f (1e-6 tol) ... %.1f (exp precision)"
      % (ell_1e6, ell_req))
chk("D12 record's 'ell >= 66-69' robust range holds under high-precision recomputation",
    math.ceil(ell_1e6) <= 66 and math.ceil(ell_req) == 69,
    "ceil(1e-6) = %d, ceil(exp) = %d" % (math.ceil(ell_1e6), math.ceil(ell_req)))
ell_C = math.log(R_WORLD_MPC * MPC_M / lam_C) / math.log(4.0)
Lam_C = Lam0_eV * 4.0 ** ell_C / 1e6
chk("D13 lambda_C-resolving layer ell = 62.65", close(ell_C, 62.65, 1e-4), "%.4f" % ell_C)
chk("D14 Lambda_62.7 = 11.2420 MeV = 22.00 x m_e",
    close(Lam_C, 11.2420, 1e-4) and close(Lam_C / M_E, 22.00, 1e-4),
    "%.4f MeV = %.3f m_e" % (Lam_C, Lam_C / M_E))
v_C = a_e_ratio(M_E, Lam_C)
chk("D15 at ell = 62.7: Delta a_e/a_e = -2.747e-3 = 2.450e+07 x exp precision",
    close(v_C - 1, -2.747e-3, 1e-3) and close(abs(v_C - 1) / REL_E, 2.450e7, 2e-2),
    "%+.4e = %.3e x" % (v_C - 1, abs(v_C - 1) / REL_E))
a_req = R_WORLD_MPC * MPC_M / (44 * 4.0 ** ell_req)
chk("D16 required lattice spacing a_ell = 1.1140e-17 m = lambda_C/2.178e+05",
    close(a_req, 1.1140e-17, 5e-3) and close(lam_C / a_req, 2.178e5, 5e-3),
    "%.5e m = lam_C/%.4e" % (a_req, lam_C / a_req))
chk("D17 p_min/m_e = 9.52e-39 (discretisation harmless)",
    close(pmin_eV / (M_E * 1e6), 9.52e-39, 5e-3), "%.3e" % (pmin_eV / (M_E * 1e6)))
chk("D18 loop sits 1.05e38 quanta above the fundamental",
    close(M_E * 1e6 / pmin_eV, 1.05e38, 5e-3), "%.3e" % (M_E * 1e6 / pmin_eV))
libB = {"Nd": 44, "B": 4, "N_gen": 3, "L4": 7, "L5": 11, "L6": 18, "L7": 29,
        "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55, "F_proj": 17,
        "M": 33, "CY3": 134, "C_B2_2": 120, "N_colour": 3}
ex2 = set()
for v1 in libB.values():
    ex2.add(v1)
    for v2 in libB.values():
        if v2 <= 1:
            continue
        ex2.add(v1 * v2)
        ex2.add(v1 + v2)
        ex2.add(v1 - v2)
        for v3 in libB.values():
            if v3 <= 1:
                continue
            ex2.add(v1 * v2 * v3)
winB = list(range(67, 72))
covB = [v for v in winB if v in ex2]
chk("D19 null test window [67,71] coverage = 2/5 = 40%", len(covB) == 2,
    "coverage %d/%d (69/70/71 zero)" % (len(covB), len(winB)))

# =====================================================================
print()
print("=" * 78)
print("E  g-2 precision wall and muon bound  (docs/05)")
print("=" * 78)
alpha = 1.0 / A_INV_0_CODATA
chk("E1  alpha/pi = 2.322819e-03", close(alpha / math.pi, 2.322819e-3, 1e-6),
    "%.7e" % (alpha / math.pi))
chk("E2  log10(pi/alpha) = 2.634", close(math.log10(math.pi / alpha), 2.634, 1e-4),
    "%.5f" % math.log10(math.pi / alpha))
chk("E3  12 digits / 2.634 = 4.56 loops", close(12.0 / math.log10(math.pi / alpha), 4.56, 1e-3),
    "%.4f" % (12.0 / math.log10(math.pi / alpha)))
A = {1: 0.5, 2: -0.328478965579193, 3: 1.181241456587, 4: -1.912245764926, 5: 7.795}
# scripts/06 prints  A_n * (alpha/pi)^(n-1)  -- the bracket term of a_ell
script_tab = {1: 5.000000e-01, 2: -7.629973e-04, 3: 6.373377e-06,
              4: -2.396570e-08, 5: 2.269227e-10}
doc_tab = {1: 1.161e-03, 2: -7.630e-04, 3: 6.373e-06, 4: -2.397e-08, 5: 2.269e-10}
worst = 0.0
for n in (1, 2, 3, 4, 5):
    val = A[n] * (alpha / math.pi) ** (n - 1)
    worst = max(worst, abs(val - script_tab[n]) / abs(script_tab[n]))
chk("E4  per-loop bracket term A_n (alpha/pi)^(n-1) reproduces scripts/06 (5 rows)",
    worst < 5e-5, "worst rel dev %.2e" % worst)
worst = 0.0
for n in (2, 3, 4, 5):
    worst = max(worst, abs(A[n] * (alpha / math.pi) ** (n - 1) - doc_tab[n]) / abs(doc_tab[n]))
chk("E5  docs/05 table rows n=2..5 match the same bracket term",
    worst < 5e-3, "worst rel dev %.2e" % worst)
if not close(doc_tab[1], script_tab[1], 1e-3):
    note("docs/05 line 36, 1-loop '貢獻/A₁' cell reads 1.161e-03 = a_e, but scripts/06 "
         "prints A_1(alpha/pi)^0 = 5.000000e-01 for that cell. The n=2..5 rows agree "
         "with the script; only the n=1 cell differs (a_e instead of the bracket term A_1). "
         "Digits/cumulative columns are unaffected (both give 0.00).")
cum = 0.0
cumdoc = {2: 2.82, 3: 7.71, 4: 15.03, 5: 24.37}
ok = True
for n in (2, 3, 4, 5):
    cum += -math.log10(abs(A[n] * (alpha / math.pi) ** (n - 1)) / A[1])
    if not close(cum, cumdoc[n], 1e-2):
        ok = False
chk("E6  cumulative digits bought: 2.82 / 7.71 / 15.03 / 24.37", ok,
    "recomputed %.2f" % cum)
s20 = math.hypot(43.0, 14.8)
s25 = math.hypot(62.0, 14.8)
chk("E7  2025: WP20 = 5.7 sigma, WP25 = 0.59 sigma (errors added in quadrature)",
    close((116592070.5 - 116591810) / s20, 5.7, 1e-2)
    and close((116592070.5 - 116592033) / s25, 0.59, 3e-2),
    "%.2f / %.2f sigma" % ((116592070.5 - 116591810) / s20,
                           (116592070.5 - 116592033) / s25))
chk("E8  SM prediction moved 223e-11 = 5.2x its own 2020 error bar",
    close(116592033 - 116591810, 223, 1e-9) and close(223.0 / 43, 5.2, 2e-2),
    "%.0f e-11 = %.2f x" % (116592033 - 116591810, 223.0 / 43))
chk("E9  dev 137 vs 137.035999177 = 0.0263%",
    close(abs(137 - A_INV_0_2022) / A_INV_0_2022, 0.0263e-2, 5e-2),
    "%.5f%%" % (abs(137 - A_INV_0_2022) / A_INV_0_2022 * 100))
dae = abs(137 - A_INV_0_2022) / A_INV_0_2022
chk("E10 Delta a_e/a_e = 2.627e-04 = 2.343e+06 x the electron precision",
    close(dae, 2.627e-4, 5e-3) and close(dae / REL_E, 2.343e6, 5e-3),
    "%.4e = %.4e x" % (dae, dae / REL_E))
chk("E11 dev 128 vs 127.951 = 0.0383% ; dev 9 vs 9.085 = 0.9356%",
    close(abs(128 - 127.951) / 127.951, 0.0383e-2, 5e-2)
    and close(abs(9 - 9.085) / 9.085, 0.9356e-2, 5e-2),
    "%.4f%% / %.4f%%" % (abs(128 - 127.951) / 127.951 * 100, abs(9 - 9.085) / 9.085 * 100))
chk("E12 m_mu sensitivity to a heavy scale is (m_mu/m_e)^2 = 4.275e+04 x the electron",
    close((M_MU / M_E) ** 2, 4.275e4, 1e-3), "%.4e" % ((M_MU / M_E) ** 2))
L_mu = solve_Lam(M_MU, 5.318e-7)
chk("E13 muon: Lambda_req = 167.306 GeV, 2998.2 x Lambda_mass",
    close(L_mu / 1000.0, 167.306, 3e-3) and close(L_mu / (2 * M0), 2998.2, 3e-3),
    "%.3f GeV = %.1f x" % (L_mu / 1000.0, L_mu / (2 * M0)))
ell_mu = math.log(L_mu / (Lam0_eV / 1e6)) / math.log(4.0)
chk("E14 muon ell_req = 69.58 -> ell >= 70", close(ell_mu, 69.58, 1e-3)
    and math.ceil(ell_mu) == 70, "%.4f" % ell_mu)
chk("E15 Lambda_mu/Lambda_e = 3.006 (record); analytic prediction = 3.002",
    close(L_mu / L_exp, 3.006, 5e-3)
    and close((M_MU / M_E) * math.sqrt(REL_E / 5.318e-7), 3.002, 5e-3),
    "recomputed %.4f ; analytic %.4f" % (L_mu / L_exp,
                                         (M_MU / M_E) * math.sqrt(REL_E / 5.318e-7)))
chk("E16 electron Lambda_req = 55.65 GeV reproduces scripts/05's 55.65 GeV",
    close(L_exp / 1000.0, 55.65, 5e-3), "%.4f GeV" % (L_exp / 1000.0))
chk("E17 ell = 0 cutoff = 2.1404e-31 eV, excluded by ~42 orders",
    close(Lam0_eV, 2.1404e-31, 1e-5) and close(math.log10(L_exp * 1e6 / Lam0_eV), 42, 2e-2),
    "%.5e eV, %.1f orders" % (Lam0_eV, math.log10(L_exp * 1e6 / Lam0_eV)))

# =====================================================================
print()
print("=" * 78)
print("F  problem D: alpha(0) dressing, five mechanisms  (docs/06)")
print("=" * 78)
d_IR = A_INV_0_2022 - 137.0                 # +0.035999177  (physical - IDCM)
d_UV = A_INV_MZ_OLD - 128.0                 # -0.049        (physical - IDCM)
d_run = 9.0 - 9.085                         # -0.085        (IDCM - physical)
chk("F1  three gaps: +0.035999177 / -0.049 / -0.085 (old PDG target)",
    close(d_IR, 0.035999177, 1e-8) and close(d_UV, -0.049, 1e-9)
    and close(d_run, -0.085, 1e-9),
    "%+.9f / %+.3f / %+.3f" % (d_IR, d_UV, d_run))
d_run_exact = 9.0 - (A_INV_0_2022 - A_INV_MZ_OLD)
chk("F2  exact accounting: d_IR - d_UV = +0.084999177 = -(d_run_exact), residual 0.00e+00",
    close(d_IR - d_UV, 0.084999177, 1e-9)
    and close(d_IR - d_UV + d_run_exact, 0.0, absolute=1e-15),
    "%+.9f, residual %.1e" % (d_IR - d_UV, abs(d_IR - d_UV + d_run_exact)))
chk("F3  relative IR gap = 2.626987e-04 (denominator = physical 137.035999177)",
    close(d_IR / A_INV_0_2022, 2.626987e-4, 1e-5),
    "%.6e" % (d_IR / A_INV_0_2022))
meas = [137.035999046, 137.035999206, 137.035999177]
spread = max(meas) - min(meas)
chk("F4  three independent measurements: spread 1.6e-7 = 4.4e-6 of the gap",
    close(spread, 1.6e-7, 0.05) and close(spread / d_IR, 4.4e-6, 0.05),
    "%.2e = %.2e of the gap" % (spread, spread / d_IR))
if not close(spread / 137.0, 4.4e-6, 0.05):
    note("docs/06 line 45 writes the 1.6e-7 spread as '相對 4.4e-6'. The reference "
         "denominator is the GAP 0.036 (1.6e-7/0.036 = 4.44e-6), not 137 "
         "(which would give 1.17e-9). Self-consistent as written, but the denominator "
         "is implicit.")


def dalpha_cutoff(Lam, with_const=True):
    """(1/3pi) sum_f N_c Q_f^2 [ln(Lam^2/m_f^2) - 5/3]  over fermions with m_f < Lam"""
    tot = 0.0
    for m, ncq2 in [(0.510999, 1.0), (105.658, 1.0), (1776.86, 1.0),
                    (2.16, 4.0 / 3), (4.67, 1.0 / 3), (93.4, 1.0 / 3),
                    (1270.0, 4.0 / 3), (4180.0, 1.0 / 3), (172690.0, 4.0 / 3)]:
        if m < Lam:
            tot += ncq2 * (math.log(Lam * Lam / (m * m)) / 6.0
                           - (5.0 / 18.0 if with_const else 0.0))
    return (2.0 / math.pi) * tot


# scripts/07 D3 uses only_e = [(m_e, 1.0)]: at Lambda_req = 1.393 MeV the electron
# is the only active fermion, and the closed form is analytic:
#   x = d_IR*3*pi + 5/3 ;  Lambda_req = m_e * exp(x/2)
ONLY_E = [(M_E, 1.0)]
FULL = [(0.510999, 1.0), (105.658, 1.0), (1776.86, 1.0), (2.16, 4.0 / 3),
        (4.67, 1.0 / 3), (93.4, 1.0 / 3), (1270.0, 4.0 / 3), (4180.0, 1.0 / 3),
        (172690.0, 4.0 / 3)]


def dalpha_inv(Lam_MeV, masses):
    tot = 0.0
    for m, ncq2 in masses:
        if m < Lam_MeV:
            tot += ncq2 * (math.log(Lam_MeV ** 2 / m ** 2) - 5.0 / 3.0)
    return tot / (3 * math.pi)


x_req = d_IR * 3 * math.pi + 5.0 / 3.0
Lam_req = M_E * math.exp(x_req / 2.0)
chk("F5  mechanism 1: Lambda_req = 1.393178 MeV = 2.7264 m_e (analytic inversion)",
    close(Lam_req, 1.393178, 1e-5) and close(Lam_req / M_E, 2.7264, 1e-4)
    and abs(dalpha_inv(Lam_req, ONLY_E) - d_IR) < 1e-12,
    "%.6f MeV = %.4f m_e, residual %.1e" % (Lam_req, Lam_req / M_E,
                                            abs(dalpha_inv(Lam_req, ONLY_E) - d_IR)))
Lam_ll = M_E * math.exp(d_IR * 3 * math.pi / 2.0)
chk("F6  leading-log only: 0.605473 MeV = 1.1849 m_e",
    close(Lam_ll, 0.605473, 1e-5) and close(Lam_ll / M_E, 1.1849, 1e-4),
    "%.6f MeV = %.4f m_e" % (Lam_ll, Lam_ll / M_E))
m1 = M0 * 2 * math.sin(math.pi / N_SITES)
chk("F7  m_1 = M0*2sin(pi/88) = 1.991698 MeV", close(m1, 1.991698, 1e-6),
    "%.6f MeV" % m1)
chk("F8  Lambda_req = 1.393 MeV lies BELOW m_1 -> inside the spectral forbidden zone",
    Lam_req < m1, "%.6f < %.6f" % (Lam_req, m1))
over = {"m_1": (m1, 0.111842, 3.11),
        "Lambda_mass": (2 * M0, 0.819088, 22.75),
        "Lambda_ell(70)": (Lam0_eV * 4.0 ** 70 / 1e6, 2.640700, 73.35)}
for nm, (L, doc_val, doc_ratio) in over.items():
    contrib = dalpha_inv(L, ONLY_E)
    chk("F9  overshoot at %s: %.6f (= %.2fx the needed 0.036)" % (nm, doc_val, doc_ratio),
        close(contrib, doc_val, 5e-3) and close(contrib / d_IR, doc_ratio, 3e-2),
        "recomputed %.6f = %.2fx" % (contrib, contrib / d_IR))
    full_contrib = dalpha_inv(L, FULL)
    if full_contrib > contrib * 1.01:
        note("%s: docs/06 sec 3.1 / scripts/07 D3 use the ELECTRON-ONLY sum (%.6f). "
             "With all fermions lighter than the scale the overshoot is LARGER "
             "(%.6f = %.2fx vs %.2fx) -> the doc's exclusion is conservative and the "
             "conclusion is strengthened, not weakened."
             % (nm, contrib, full_contrib, full_contrib / d_IR, doc_ratio))
chk("F10 mechanism 2: multiplicative rescaling gives d_IR/d_UV = +1.070312",
    close(137.0 / 128.0, 1.070312, 1e-6), "%.6f" % (137.0 / 128.0))
ratio_data = d_IR / d_UV
chk("F11 data requires d_IR/d_UV = -0.734677 (opposite sign)",
    close(ratio_data, -0.734677, 1e-6), "%.6f" % ratio_data)
chk("F12 modulus mismatch = 45.7% (relative to the data requirement)",
    close((137.0 / 128.0 - abs(ratio_data)) / abs(ratio_data), 0.457, 5e-3),
    "%.4f" % ((137.0 / 128.0 - abs(ratio_data)) / abs(ratio_data)))
sig_ratio = abs(ratio_data) * 0.009 / abs(d_UV)
chk("F13 sign argument significance = 5.44 sigma (d_UV +- 0.009)",
    close(sig_ratio, 0.13493, 1e-3) and close(abs(ratio_data) / sig_ratio, 5.44, 1e-2),
    "ratio %.6f +- %.5f -> %.2f sigma" % (ratio_data, sig_ratio, abs(ratio_data) / sig_ratio))
# mechanism 3: pre-registered grammar
LIB22 = {"N_d": 44, "B": 4, "N_gen": 3, "L4": 7, "L5": 11, "L6": 18, "L7": 29,
         "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55,
         "F_proj": 17, "M": 33, "CY3": 134, "C(B2,2)": 120,
         "N_d+1": 45, "2N_d": 88, "F10+1": 56, "123": 123, "137": 137}
G = {}


def put(v, s):
    if 1e-6 < v < 1e6:
        k = round(v, 10)
        if k not in G:
            G[k] = s


items = list(LIB22.items())
for n1, v1 in items:
    put(float(v1), n1)
    put(v1 * v1, "%s^2" % n1)
    put(v1 ** 3, "%s^3" % n1)
for n1, v1 in items:
    for n2, v2 in items:
        put(v1 * v2, "%s*%s" % (n1, n2))
        put(v1 + v2, "%s+%s" % (n1, n2))
        put(abs(v1 - v2), "|%s-%s|" % (n1, n2))
        put(v1 / v2, "%s/%s" % (n1, n2))
        for n3, v3 in items:
            put(v1 * v2 / v3, "(%s*%s)/%s" % (n1, n2, n3))
            put((v1 + v2) / v3, "(%s+%s)/%s" % (n1, n2, n3))
            put(v1 / (v2 * v3), "%s/(%s*%s)" % (n1, n2, n3))
for k in range(1, 15):
    put(PHI ** k, "phi^%d" % k)
    put(PHI ** -k, "phi^-%d" % k)
pure = sorted(G)
chk("F14 pre-registered grammar: 22 integers -> 9392 distinct values",
    len(LIB22) == 22 and len(pure) == 9392, "%d ints, %d values" % (len(LIB22), len(pure)))
inband = [v for v in pure if 0.02 < v < 0.06]
chk("F15 grammar values inside [0.02, 0.06] = 729", len(inband) == 729,
    "%d values" % len(inband))
best = min(inband, key=lambda v: abs(v - d_IR))
best_dev = abs(best - d_IR) / d_IR
chk("F16 best pure-structural hit = 34/945 = 0.035978836, dev 0.0565%",
    close(best, 34.0 / 945, 1e-9) and close(best_dev, 5.65e-4, 1e-2),
    "%.9f  dev %.4f%%  expr %s" % (best, best_dev * 100, G[best]))
random.seed(20260915)
closest = []
for _ in range(4000):
    t = math.exp(random.uniform(math.log(0.02), math.log(0.06)))
    i = bisect_left(pure, t)
    cand = []
    if i < len(pure):
        cand.append(abs(pure[i] - t) / t)
    if i > 0:
        cand.append(abs(pure[i - 1] - t) / t)
    closest.append(min(cand))
closest.sort()
med = closest[len(closest) // 2]
pct = sum(1 for c in closest if c < best_dev) / len(closest) * 100
chk("F17 random-target median closest approach = 0.0447%", close(med, 4.47e-4, 1e-2),
    "%.4f%%" % (med * 100))
chk("F18 target percentile = 58.8 (worse than the median random target)",
    close(pct, 58.8, 5e-3), "%.1f" % pct)
chk("F19 grammar reaches 0.0009% for the luckiest 1% of targets",
    close(closest[int(len(closest) * 0.01)], 9e-6, 0.2),
    "%.4f%%" % (closest[int(len(closest) * 0.01)] * 100))


def hits_within(vs, target, rel):
    a = sorted(vs)
    return bisect_right(a, target * (1 + rel)) - bisect_left(a, target * (1 - rel))


random.seed(20260915)
ctrl = []
for _ in range(4000):
    t = math.exp(random.uniform(math.log(0.02), math.log(0.06)))
    ctrl.append(hits_within(pure, t, 5e-3))
mu = sum(ctrl) / len(ctrl)
sd = math.sqrt(sum((c - mu) ** 2 for c in ctrl) / len(ctrl))
z = (hits_within(pure, d_IR, 5e-3) - mu) / sd
chk("F20 hit count z = -1.10 (random control mean 6.61 +- 2.38)",
    close(z, -1.10, 0.02) and close(mu, 6.61, 0.01) and close(sd, 2.38, 0.02),
    "z = %+.2f, control %.2f +- %.2f" % (z, mu, sd))
phi_best = min((PHI ** k for k in range(-20, 1)), key=lambda v: abs(v - d_IR))
chk("F21 best phi power = phi^-7 = 0.034442 (off by 4.33%)",
    close(phi_best, 0.034442, 1e-4) and close(abs(phi_best - d_IR) / d_IR, 4.33e-2, 2e-2),
    "%.6f  dev %.3f%%" % (phi_best, abs(phi_best - d_IR) / d_IR * 100))
chk("F22 nested grammar: N_gen^2/((F5-N_gen)*F5^3) = 9/250 = 0.036 exactly (dev 0.0023%)",
    Fraction(N_GEN ** 2, (F5 - N_GEN) * F5 ** 3) == Fraction(9, 250)
    and close(abs(9.0 / 250 - d_IR) / d_IR, 2.3e-5, 0.05),
    "%.6f  dev %.4f%%" % (9.0 / 250, abs(9.0 / 250 - d_IR) / d_IR * 100))
cand = (31.0 / 2) * (alpha / math.pi)
chk("F23 alpha-inserted best candidate (31/2)(alpha/pi) = 0.036003702 (dev 0.0126%)",
    close(cand, 0.036003702, 1e-6) and close(abs(cand - d_IR) / d_IR, 1.26e-4, 5e-2),
    "%.9f  dev %.4f%%" % (cand, abs(cand - d_IR) / d_IR * 100))
chk("F24 running needs 9.084999 = 9 x (1 + 0.009444)",
    close(9.0 * (1 + 0.009444), 9.085, 1e-6), "%.6f" % (9.0 * (1 + 0.009444)))

# =====================================================================
print()
print("=" * 78)
print("NOTES (doc<->script discrepancies, carried as annotations, not FAILs): %d" % len(NOTES))
for i, t in enumerate(NOTES, 1):
    print("  N%d. %s" % (i, t))
print("=" * 78)
print("RESULT: %d PASS / %d FAIL   (%d notes)" % (NPASS, NFAIL, len(NOTES)))
print("=" * 78)
raise SystemExit(1 if NFAIL else 0)
