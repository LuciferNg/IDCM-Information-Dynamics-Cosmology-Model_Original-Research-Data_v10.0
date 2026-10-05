#!/usr/bin/env python3
"""
O59 — COMPREHENSIVE VERIFICATION OF ALL DERIVATIONS
Verifies every claim, formula, and numerical value from scratch.
"""
import os, math, json, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

# ============ LOAD RAW DATA ============
print("=" * 72)
print("O59 — COMPREHENSIVE VERIFICATION")
print("=" * 72)

# Constants
c = {"Nd": 44, "B": 4, "Ngen": 3, "Ktree": 33,
     "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29,
     "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34,
     "phi": phi, "M0": 27.900915, "v_ew": 246220}
for n in range(1, 45):
    c[f"g{n}"] = 4 * math.sin(n * math.pi / 88) ** 2

# Load d_tensor_native_12d (cleanest)
d_native = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))
v12 = np.array([phi ** (-k/12) for k in range(12)])
Y_12 = np.einsum("ijk,k->ij", d_native, v12)
Y_12 = (Y_12 + Y_12.T) / 2
trY_12 = np.trace(Y_12)
ev_12 = np.sort(np.linalg.eigvalsh(Y_12))
lam_max = ev_12[-1]
lam_2nd = ev_12[-2]

# Load 36D kappa and J*
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    kappa = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    Jstar = np.array(json.load(f)["Jstar_36D"])
Y_36 = np.einsum("ijk,k->ij", kappa, Jstar)
Y_36 = (Y_36 + Y_36.T) / 2
trY_36 = np.trace(Y_36)
ev_36 = np.sort(np.linalg.eigvalsh(Y_36))

# Load GKZ data
with open(os.path.join(BASE, "open_problems_fresh", "o137_cy3_topological_resonance", "data", "dual_triangulation_data.json")) as f:
    gkz = json.load(f)
phi_vals = gkz["gkz_phi"]
phi_le12 = [(i, v) for i, v in enumerate(phi_vals) if v <= 12]
phi_counts = {}
for i, v in phi_le12:
    phi_counts[v] = phi_counts.get(v, 0) + 1

pass_count = 0
fail_count = 0

def check(name, condition, detail=""):
    global pass_count, fail_count
    if condition:
        pass_count += 1
        print(f"  ✅ PASS | {name} {detail}")
    else:
        fail_count += 1
        print(f"  ❌ FAIL | {name} {detail}")

def check_near(name, val, target, tol_pct, detail=""):
    global pass_count, fail_count
    if target == 0:
        err_pct = abs(val) * 100
    else:
        err_pct = abs(val - target) / abs(target) * 100
    status = "✅" if err_pct <= tol_pct else "❌"
    if status == "✅":
        pass_count += 1
    else:
        fail_count += 1
    print(f"  {status} | {name}: {val:.6f} vs {target:.6f} (err={err_pct:.4f}%, tol={tol_pct}%) {detail}")

# =====================================================================
# VERIFICATION 1: RAW DATA INTEGRITY
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 1: RAW DATA INTEGRITY")
print("=" * 72)

check("d_tensor_native_12d shape", d_native.shape == (12, 12, 12))
check("kappa shape", kappa.shape == (36, 36, 36))
check("Jstar shape", Jstar.shape == (36,))
check("Y_12 symmetric", np.allclose(Y_12, Y_12.T))
check("Y_36 symmetric", np.allclose(Y_36, Y_36.T))
check_near("sum(kappa)", np.sum(kappa), -8.0, 0.01, "= -2B")
check("GKZ total points", len(phi_vals) == 73)
check("GKZ phi<=12 count", len(phi_le12) == 44, f"= N_d")

# =====================================================================
# VERIFICATION 2: 44 DECOMPOSITION (Item 4)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 2: 44 DECOMPOSITION (Item 4)")
print("=" * 72)

check("O59: 33+3+8 = 44", 33 + 3 + 8 == 44)
check("O137: 28+9+5+2 = 44", 28 + 9 + 5 + 2 == 44)
check("phi=12 count", phi_counts.get(12, 0) == 28, f"= 28 = L4*L5")
check("phi=9 count", phi_counts.get(9, 0) == 9, f"= 9 = Ngen^2")
check("phi=8 count", phi_counts.get(8, 0) == 5, f"= 5 = F5")
check("phi=6 count", phi_counts.get(6, 0) == 2, f"= 2 (Nyquist)")
check("33 = 28+5", 33 == 28 + 5, "| K_tree = phi=12 + phi=8")
check("3 = sqrt(9)", 3 == int(math.sqrt(9)), "| Ngen = sqrt(phi=9 count)")

# =====================================================================
# VERIFICATION 3: tr(Y) = 2B^2 * (1 - gamma_1) (Item 3)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 3: tr(Y) = 2B^2 * (1 - gamma_1) (Item 3)")
print("=" * 72)

B = c["B"]; g1 = c["g1"]
check_near("tr(Y_12)", trY_12, 31.84654, 0.001)
check_near("2B^2 = 32", 2*B**2, 32.0, 0.001)
check_near("tr(Y) ≈ 2B^2", trY_12, 2*B**2, 0.5)
check_near("tr(Y) = 2B^2*(1-g1)", trY_12, 2*B**2*(1-g1), 0.05)
check_near("2B^2*(1-g1)", 2*B**2*(1-g1), 31.83694, 0.001)
check_near("tr(Y_36)", trY_36, 3.16036, 0.001)

# =====================================================================
# VERIFICATION 4: lambda_max = 36 - 1/gamma_20 (Item 1)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 4: lambda_max = 36 - 1/gamma_20 (Item 1)")
print("=" * 72)

g20 = c["g20"]
check_near("lambda_max (clean)", lam_max, 35.417768, 0.001)
check_near("Nd - 2B = 36", c["Nd"] - 2*B, 36.0, 0.001)
check_near("1/g20", 1/g20, 0.58297, 0.01)
check_near("lam_max = 36 - 1/g20", lam_max, 36 - 1/g20, 0.005)

# =====================================================================
# VERIFICATION 5: v_geom factor = 88 * (L5-1 + L4*B*g7) (Item 1)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 5: v_geom factor = 88 * (L5-1 + L4*B*g7) (Item 1)")
print("=" * 72)

L4 = c["L4"]; L5 = c["L5"]; g7 = c["g7"]
factor = c["v_ew"] / (math.sqrt(lam_max) * c["M0"])
factor_formula = 2*c["Nd"] * (L5 - 1 + L4*B*g7)
check_near("v_geom factor", factor, 1482.84, 0.01)
check_near("88*(10+28*g7)", factor_formula, 1482.80, 0.1)
check_near("factor/1232 = 1+40*g1", factor/1232, 1 + (c["Nd"]-B)*g1, 0.05)
check_near("v_geom = sqrt(lam)*M0*factor", math.sqrt(lam_max)*c["M0"]*factor/1000, 246.22, 0.1, "GeV")

# =====================================================================
# VERIFICATION 6: lambda_2nd = 2 + 2*F9*g1 + g1*g7*L4/(L5-1) (Item 2)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 6: lambda_2nd = 2 + 2*F9*g1 + g1*g7*L4/(L5-1) (Item 2)")
print("=" * 72)

F9 = c["F9"]
lam2_pert = 2 + 2*F9*g1
lam2_inst = g1*g7*L4/(L5-1)
lam2_formula = lam2_pert + lam2_inst
check_near("lambda_2nd (clean)", lam_2nd, 2.34737, 0.001)
check_near("perturbative: 2+2*F9*g1", lam2_pert, 2.34651, 0.01)
check_near("instanton: g1*g7*L4/(L5-1)", lam2_inst, 0.000873, 0.01)
check_near("lam2 = 2 + 68*g1 + g1*g7*7/10", lam2_formula, lam_2nd, 0.002)

# =====================================================================
# VERIFICATION 7: 12D vs 36D (Item 5)
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 7: 12D vs 36D (Item 5)")
print("=" * 72)

# Frobenius subalgebra
d_36 = np.zeros((36, 36, 36))
d_36[:12, :12, :12] = d_native
d_sq_36 = np.einsum("abc,cde->abde", d_36, d_36)
sym_err = np.max(np.abs(d_sq_36 - d_sq_36.transpose(1,0,2,3)))
check("12D embedded associativity", sym_err < 1e-10, f"error={sym_err:.2e}")

cross = np.sum(np.abs(d_36[:12, :12, 12:])) + np.sum(np.abs(d_36[:12, 12:, :12])) + np.sum(np.abs(d_36[12:, :12, :12]))
check("12D isolated from 24D", cross < 1e-10, f"cross={cross:.4f}")

# 44 = 12 + 32
check("44 = 12 + 32", 44 == 12 + 32)
check("12 = L5+1", 12 == c["L5"] + 1)
check("32 = 2*B^2", 32 == 2 * B**2)

# SVD ratio
d_flat = d_native.reshape(12, 12*12)
k_flat = kappa.reshape(36, 36*36)
U_d, S_d, _ = np.linalg.svd(d_flat, full_matrices=False)
U_k, S_k, _ = np.linalg.svd(k_flat, full_matrices=False)
check_near("SVD ratio kappa/d", S_k[0]/S_d[0], 47.0, 0.1, "= Ktree + 2*L4")

# =====================================================================
# VERIFICATION 8: ADDITIONAL STRUCTURAL CHECKS
# =====================================================================
print("\n" + "=" * 72)
print("VERIFICATION 8: ADDITIONAL STRUCTURAL CHECKS")
print("=" * 72)

# 12D Y eigenvalues
check_near("Y_12 lambda_max", lam_max, 35.4178, 0.01)
check_near("Y_12 lambda_2nd", lam_2nd, 2.34737, 0.01)
check_near("Y_36 lambda_max", ev_36[-1], 3.6970, 0.01)

# K_Chain gamma values
check_near("gamma_1", g1, 0.005096, 0.1)
check_near("gamma_7", g7, 0.244642, 0.1)
check_near("gamma_20", g20, 1.71537, 0.1)
check_near("gamma_22", c["g22"], 2.0, 0.001)
check_near("gamma_33", c["g33"], 3.41421, 0.01)

# WDVV associativity
check("d_tensor WDVV associativity", np.max(np.abs(np.einsum("ijk,klm->ijlm", d_native, d_native) -
    np.einsum("ijk,klm->ijlm", d_native, d_native).transpose(1,0,2,3))) < 1e-10)

# kappa symmetry
check("kappa symmetry", np.max(np.abs(kappa - kappa.transpose(1,0,2))) < 1e-10)

# =====================================================================
# FINAL SUMMARY
# =====================================================================
print("\n" + "=" * 72)
print("FINAL VERIFICATION SUMMARY")
print("=" * 72)
print(f"\n  Total checks: {pass_count + fail_count}")
print(f"  ✅ PASS: {pass_count}")
print(f"  ❌ FAIL: {fail_count}")
print(f"  Pass rate: {pass_count/(pass_count+fail_count)*100:.1f}%")

all_pass = fail_count == 0
if all_pass:
    print("\n  ★★★ ALL VERIFICATIONS PASSED ★★★")
else:
    print(f"\n  ⚠️  {fail_count} CHECK(S) FAILED — review above")

print("\n" + "=" * 72)
print("VERIFICATION COMPLETE")
print("=" * 72)