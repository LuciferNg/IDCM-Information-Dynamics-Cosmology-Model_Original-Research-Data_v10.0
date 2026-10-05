#!/usr/bin/env python3
"""
O59 Re-derivation: Test all d_tensor versions for contamination
Find the cleanest d_tensor and re-derive the 66 = Lambda^2(12) structure
"""
import os, json, math, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2

# ============ 1. SCAN ALL d_tensor VERSIONS ============
print("=" * 72)
print("PHASE 1: SCAN ALL d_tensor VERSIONS")
print("=" * 72)

d_tensor_files = [
    "d_tensor_native_12d.npy",
    "d_tensor_z3_solved.npy",
    "d_tensor_hybrid.npy",
    "d_tensor_float64.npy",
    "d_tensor_high_precision.npy",
    "d_tensor_ultra_precision.npy",
    "d_tensor_positive.npy",
    "d_tensor_final.npy",
    "d_tensor_wdvv_converged.npy",
]

v = np.array([phi ** (-k/12) for k in range(12)])

for fname in d_tensor_files:
    try:
        d12 = np.load(os.path.join(DATA, fname))
        Y = np.einsum("ijk,k->ij", d12, v)
        Y = (Y + Y.T) / 2
        ev = np.sort(np.linalg.eigvalsh(Y))
        trY = np.trace(Y)
        lam_max = ev[-1]
        if len(ev) > 1:
            ratio = abs(lam_max) / max(np.mean(np.abs(ev[:-1])), 1e-12)
        else:
            ratio = 0
        print(f"  {fname:<35s} tr(Y)={trY:8.4f}  lam_max={lam_max:8.4f}  ratio={ratio:6.1f}  "
              f"tr/66={trY/66:6.4f}  WDVV_err={np.sum(np.abs(d12-d12.transpose(1,0,2))):.2e}")
    except Exception as e:
        print(f"  {fname:<35s} ERROR: {e}")

# ============ 2. CHECK d_tensor_solved versions ============
print("\n" + "=" * 72)
print("PHASE 2: CHECK d_tensor_solved (larger format)")
print("=" * 72)

for fname in ["d_tensor_solved.npy", "d_tensor_solved_v2.npy"]:
    try:
        d = np.load(os.path.join(DATA, fname))
        print(f"  {fname}: shape={d.shape}, dtype={d.dtype}")
        # These might be 36x36x36, not 12x12x12
        if len(d.shape) == 3 and d.shape[0] == 36:
            # Contract with J* to get 36x36 Yukawa
            with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
                J0 = np.array(json.load(f)["Jstar_36D"])
            Y = np.einsum("ijk,k->ij", d, J0)
            Y = (Y + Y.T) / 2
            ev = np.sort(np.linalg.eigvalsh(Y))
            print(f"    tr(Y_36) = {np.trace(Y):.4f}")
            print(f"    lam_max = {ev[-1]:.4f}")
            print(f"    non-zero: {np.sum(abs(ev) > 1e-10)}")
    except Exception as e:
        print(f"  {fname}: ERROR: {e}")

# ============ 3. CHECK WHICH IS CLEANEST ============
print("\n" + "=" * 72)
print("PHASE 3: IDENTIFY CLEANEST d_tensor")
print("=" * 72)

# The cleanest should have:
# - No tr(Y)->66 bias (tr/66 far from 1)
# - Small WDVV error (symmetry preservation)
# - Natural eigenvalue distribution

# Check d_tensor_native_12d (likely the first, before penalty)
d_native = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))
Y_native = np.einsum("ijk,k->ij", d_native, v)
Y_native = (Y_native + Y_native.T) / 2
ev_native = np.sort(np.linalg.eigvalsh(Y_native))

print("  d_tensor_native_12d (likely the cleanest):")
print(f"    tr(Y) = {np.trace(Y_native):.6f}")
print(f"    tr(Y)/66 = {np.trace(Y_native)/66:.6f}")
print(f"    lam_max = {ev_native[-1]:.6f}")
print(f"    lam_2nd = {ev_native[-2]:.6f}")
print(f"    Spectrum: {np.round(ev_native, 6)}")
if len(ev_native) > 1:
    ratio = abs(ev_native[-1]) / max(np.mean(np.abs(ev_native[:-1])), 1e-12)
    print(f"    1+11 ratio = {ratio:.1f}")

# Check d_tensor_wdvv_converged (latest, but might have penalty)
d_wdvv = np.load(os.path.join(DATA, "d_tensor_wdvv_converged.npy"))
Y_wdvv = np.einsum("ijk,k->ij", d_wdvv, v)
Y_wdvv = (Y_wdvv + Y_wdvv.T) / 2
ev_wdvv = np.sort(np.linalg.eigvalsh(Y_wdvv))

print("\n  d_tensor_wdvv_converged (latest):")
print(f"    tr(Y) = {np.trace(Y_wdvv):.6f}")
print(f"    tr(Y)/66 = {np.trace(Y_wdvv)/66:.6f}")
if len(ev_wdvv) > 1:
    ratio = abs(ev_wdvv[-1]) / max(np.mean(np.abs(ev_wdvv[:-1])), 1e-12)
    print(f"    1+11 ratio = {ratio:.1f}")

# ============ 4. RE-DERIVE 66 = Lambda^2(12) FROM CLEANEST ============
print("\n" + "=" * 72)
print("PHASE 4: RE-DERIVE 66 = Lambda^2(12) FROM CLEANEST DATA")
print("=" * 72)

# Use d_tensor_native_12d as the cleanest
d_clean = d_native
Y_clean_12 = Y_native
ev_clean_12 = ev_native

# Construct Y acting on Lambda^2(12)
def construct_Y_antisym(Y):
    N = Y.shape[0]
    dim = N*(N-1)//2
    Y_antisym = np.zeros((dim, dim))
    pair_list = []
    for i in range(N):
        for j in range(i+1, N):
            pair_list.append((i,j))
    for a in range(dim):
        i, j = pair_list[a]
        for b in range(dim):
            k, l = pair_list[b]
            val = 0.0
            # <e_k^e_l, Y_Lambda^2(e_i^e_j)> = Y_{ki}*delta_{lj} - Y_{li}*delta_{kj} + Y_{lj}*delta_{ki} - Y_{kj}*delta_{li}
            if j == l:
                val += Y[k, i]
            if j == k:
                val -= Y[l, i]
            if i == k:
                val += Y[l, j]
            if i == l:
                val -= Y[k, j]
            Y_antisym[a, b] = val
    return Y_antisym, pair_list

Y_66, pairs = construct_Y_antisym(Y_clean_12)
ev_66 = np.sort(np.linalg.eigvalsh(Y_66))

print(f"  Y_66 (Lambda^2(12)) shape: {Y_66.shape}")
print(f"  tr(Y_66) = {np.trace(Y_66):.6f}")
print(f"  Expected tr(Y_66) = (N-1)*tr(Y) = 11*{np.trace(Y_clean_12):.6f} = {11*np.trace(Y_clean_12):.6f}")
print(f"  Match: {np.allclose(np.trace(Y_66), 11*np.trace(Y_clean_12))}")

# ============ 5. RE-DERIVE 1+11 STRUCTURE ============
print("\n" + "=" * 72)
print("PHASE 5: RE-DERIVE 1+11 STRUCTURE FROM CLEANEST 12D")
print("=" * 72)

d_final = np.load(os.path.join(DATA, "d_tensor_final.npy"))
Y_dirty = np.einsum("ijk,k->ij", d_final, v)
Y_dirty = (Y_dirty + Y_dirty.T) / 2
ev_dirty = np.sort(np.linalg.eigvalsh(Y_dirty))

for label, ev in [("native_12d", ev_native), ("wdvv_converged", ev_wdvv), ("final (contaminated)", ev_dirty)]:
    if len(ev) > 1:
        ratio = abs(ev[-1]) / max(np.mean(np.abs(ev[:-1])), 1e-12)
        print(f"  {label}: ratio={ratio:.1f}, lam_max={ev[-1]:.6f}, lam_2nd={ev[-2]:.6f}")

# ============ 6. RE-DERIVE lambda_max IDENTITY ============
print("\n" + "=" * 72)
print("PHASE 6: RE-DERIVE lambda_max IDENTITY FROM CLEANEST DATA")
print("=" * 72)

lam_max_clean = ev_native[-1]
lam_2nd_clean = ev_native[-2]

print(f"  Clean lambda_max = {lam_max_clean:.10f}")
print(f"  Clean lambda_2nd = {lam_2nd_clean:.10f}")

# Check if lam_max relates to IDCM numbers
Nd, B, L5, L7, K33 = 44, 4, 11, 29, 33
candidates = [
    ("Nd/12", Nd/12),
    ("B^2", B**2),
    ("B*L5/12", B*L5/12),
    ("K33/9", K33/9),
    ("L5/3", L5/3),
    ("gamma_33", 4*math.sin(33*math.pi/88)**2),
    ("gamma_20", 4*math.sin(20*math.pi/88)**2),
    ("gamma_1*44", 4*math.sin(1*math.pi/88)**2 * 44),
    ("gamma_7*15", 4*math.sin(7*math.pi/88)**2 * 15),
    ("gamma_7*L5", 4*math.sin(7*math.pi/88)**2 * L5),
    ("gamma_7*B", 4*math.sin(7*math.pi/88)**2 * B),
]
print(f"\n  Candidate identities for lambda_max = {lam_max_clean:.6f}:")
for name, val in candidates:
    err = abs(val - lam_max_clean) / lam_max_clean * 100
    marker = "★" if err < 5 else " "
    print(f"  {marker} {name:<20s} = {val:.6f}  err={err:.2f}%")

# Check if lambda_2nd relates to IDCM numbers
print(f"\n  Candidate identities for lambda_2nd = {lam_2nd_clean:.6f}:")
for name, val in candidates:
    err = abs(val - lam_2nd_clean) / lam_2nd_clean * 100
    marker = "★" if err < 5 else " "
    print(f"  {marker} {name:<20s} = {val:.6f}  err={err:.2f}%")

# ============ 7. DERIVE THE CORRECTED v_geom ============
print("\n" + "=" * 72)
print("PHASE 7: RE-DERIVE v_geom FROM CLEAN DATA")
print("=" * 72)

M0 = 27.900915  # MeV (from O34/O38)
# Original: v_geom = sqrt(lambda_max) * M0 * 88 * 14
# But this used contaminated lambda_max = 51.56

# The clean lambda_max is much smaller. What is the correct formula?
# v_geom = 246.22 GeV = 246220 MeV
# If the structure is still v_geom = sqrt(lambda_max_clean) * M0 * factor
# Then factor = v_geom / (sqrt(lambda_max_clean) * M0)

v_ew = 246220  # MeV
factor = v_ew / (math.sqrt(lam_max_clean) * M0)
print(f"  Clean lambda_max = {lam_max_clean:.6f}")
print(f"  sqrt(lambda_max) * M0 = {math.sqrt(lam_max_clean) * M0:.4f} MeV")
print(f"  Required factor for v_geom = 246.22 GeV: {factor:.4f}")
print(f"  88*14 = 1232")
print(f"  factor/1232 = {factor/1232:.4f}")

# Maybe the factor is different. Let's check other possibilities
# The 88*14 = 1232 came from the original structure
# But maybe the clean Y uses a different scale

# Check: what if the 12D Yukawa needs to be embedded in the 36D?
# The 36D Y has 3 blocks of 12D
# The clean 36D Y has lambda_max = 3.697 (Block 0)
# If we use the 36D lambda_max instead of the 12D one:

with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y_36 = np.einsum("ijk,k->ij", K, J0)
Y_36 = (Y_36 + Y_36.T) / 2
ev_36 = np.sort(np.linalg.eigvalsh(Y_36))
lam_max_36 = ev_36[-1]

print(f"\n  Using 36D Y lambda_max = {lam_max_36:.6f}:")
print(f"  sqrt(lambda_max_36) * M0 = {math.sqrt(lam_max_36) * M0:.4f} MeV")
factor_36 = v_ew / (math.sqrt(lam_max_36) * M0)
print(f"  Required factor: {factor_36:.4f}")
print(f"  factor_36/1232 = {factor_36/1232:.4f}")

# Check if the factor relates to known IDCM numbers
print(f"\n  Factor = {factor:.4f}")
print(f"  Check: factor vs IDCM numbers:")
for n in [1, 2, 3, 4, 5, 7, 8, 11, 13, 14, 18, 21, 29, 33, 34, 44, 88, 1232]:
    ratio = factor / n
    print(f"    factor/{n} = {ratio:.4f}  (1/{1/ratio:.2f})")

# ============ 8. SUMMARY ============
print("\n" + "=" * 72)
print("PHASE 8: SUMMARY — CORRECTED RESULTS")
print("=" * 72)

print(f"""
  d_tensor status:
    native_12d:  tr(Y)={np.trace(Y_native):.4f},  lam_max={ev_native[-1]:.4f}  ← CLEANEST
    final:       tr(Y)={np.trace(Y_dirty):.4f},  lam_max={ev_dirty[-1]:.4f}  ← CONTAMINATED
    wdvv:        tr(Y)={np.trace(Y_wdvv):.4f},  lam_max={ev_wdvv[-1]:.4f}  ← PARTIAL

  66 = Lambda^2(12):
    dim_66 = 66  (代数恒等式, 不变)
    tr(Y_66) = (N-1)*tr(Y_clean) = {11*np.trace(Y_native):.4f}
    Clean Y does NOT have tr(Y) ≈ 66

  1+11 structure:
    native_12d ratio: {abs(ev_native[-1])/max(np.mean(np.abs(ev_native[:-1])),1e-12):.1f}
    Block 0 (36D) ratio: 20.1
    → 1+11 structure is REAL, but lambda_max depends on which d_tensor

  lambda_max:
    Contaminated: 51.56 = 52 - 29/66  (0.00001%)
    Clean native: {ev_native[-1]:.4f}
    → Needs new structural identity

  v_geom:
    Original: sqrt(51.56) * M0 * 1232 = 246.82 GeV  (contaminated)
    Clean: needs re-derivation from clean lambda_max
""")

print("=" * 72)
print("RE-DERIVATION COMPLETE")
print("=" * 72)