#!/usr/bin/env python3
"""O143 verification — targeted bug checks (independent, stdlib+numpy only)"""
import numpy as np

# ── Step 2 bug check: "基態 (m=0)" labeling ──
N = 88
T = np.zeros((N, N))
for i in range(N):
    T[i, (i+1) % N] = 1.0
    T[i, (i-1) % N] = 1.0
eigvals, eigvecs = np.linalg.eigh(T)
idx = np.argsort(eigvals)
eigvals_sorted = eigvals[idx]
eigvecs_sorted = eigvecs[:, idx]

m = np.arange(N)
theory = 2*np.cos(2*np.pi*m/N)
print("eigvals_sorted[0] =", eigvals_sorted[0], " (theory min = -2.0 => Nyquist m=44)")
print("theory argmin mode m =", m[np.argmin(theory)])
v0 = eigvecs_sorted[:, 0]
print("eigvecs[:,0][:8] =", np.round(v0[:8], 4))
print("pattern alternating? ", np.allclose(np.abs(v0), 1/np.sqrt(N)))
print("sum even sites =", round(v0[::2].sum(), 6), " sum odd sites =", round(v0[1::2].sum(), 6))
print("arctan2(odd, even) =", np.degrees(np.arctan2(v0[1::2].sum(), v0[::2].sum())), "deg")
print("=> theta_0[0]=135deg comes from Nyquist alternating vector, NOT m=0 ground mode")
print()

print("eigvals_sorted[87] =", eigvals_sorted[87], " (theory max = 2.0 => m=0 uniform)")
v_uniform = eigvecs_sorted[:, 87]
print("uniform vec sums: even =", round(v_uniform[::2].sum(), 6), " odd =", round(v_uniform[1::2].sum(), 6))
print("arctan2 =", np.degrees(np.arctan2(v_uniform[1::2].sum(), v_uniform[::2].sum())), "deg (should be 45)")
print()

# ── theta_0 independence from gamma weights ──
gammas = 4*np.sin(np.pi*np.arange(1, N+1)/(2*N))**2
print("gamma_even sum =", gammas[1::2].sum(), " gamma_odd sum =", gammas[::2].sum())
print("theta_0[m] = arctan2(Σ_eigvec_odd, Σ_eigvec_even): NO gamma weights in formula")
print("=> '由奇偶不對稱性(88/90)鎖定' claim not backed by the computed quantity")
print()

w_even = gammas[1::2]/gammas[1::2].sum()
w_odd = gammas[::2]/gammas[::2].sum()
ratio = (w_odd**2).sum()/(w_even**2).sum()
print("vac odd/even energy ratio (computed) =", round(ratio, 6), " vs 'theory' 88/90 =", round(88/90, 6))
print("deviation:", round(abs(ratio - 88/90)/(88/90)*100, 4), "% — CIRCULAR: construction forces closeness")
print()

# ── Step 3 key bug: reproduce partition ──
# node0 & node9 in proj_idx? (we verify with the saved JSON cos_theta etc.)
# JSON: node0_in_unproj=false, node9_in_unproj=true (but key mislabeled; actual check was proj_idx)
print("JSON step3: 'node9_in_unproj': true — but code computes bool(node9 in proj_idx)")
print("code line 221: 'node9_in_unproj': bool(node9_idx in proj_idx)  <- key/value MISMATCH")
print("print line 81: node9 (第二冷) 喺未被投影: False  <- contradicts JSON key name")
