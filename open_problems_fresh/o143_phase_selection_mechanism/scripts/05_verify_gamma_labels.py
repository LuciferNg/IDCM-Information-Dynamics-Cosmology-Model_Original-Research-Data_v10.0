#!/usr/bin/env python3
"""O143 verification part 2 — gamma labeling + vac ratio circularity"""
import numpy as np

N = 88
gammas = 4*np.sin(np.pi*np.arange(1, N+1)/(2*N))**2  # gamma_k, k=1..88 (1-indexed)

# Step 1 definition (matches O34): even k = 2,4,...,88 => world (sum 90)
#                         odd  k = 1,3,...,87 => observer (sum 88)
world_1 = gammas[1::2]   # 1-indexed even: k=2,4,...,88
obs_1   = gammas[::2]    # 1-indexed odd:  k=1,3,...,87
print("Step1 labels: world sum =", world_1.sum(), " observer sum =", obs_1.sum())

# Step 2 code definition: gamma_even = gamma_k[::2], gamma_odd = gamma_k[1::2]
step2_even = gammas[::2]    # k=1,3,...,87 => observer mode (sum 88)
step2_odd  = gammas[1::2]   # k=2,4,...,88 => world mode (sum 90)
print("Step2 code:  'even' sum =", step2_even.sum(), " 'odd' sum =", step2_odd.sum())
print("=> Step 2 labels are SWAPPED vs Step 1 / O34 (even=world 90, odd=observer 88)")
print()

# vac ratio: script builds psi_vac with weight_even=gamma_even/sum, weight_odd=gamma_odd/sum
wE = step2_even / step2_even.sum()
wO = step2_odd / step2_odd.sum()
vac_even = (wE**2).sum() / (wE**2 + wO**2).sum() * (wE**2 + wO**2).sum()  # normalized already
# script: psi_vac normalized => vac_even = sum(psi_vac[::2]^2) = wE^2/(wE^2+wO^2)
se = (wE**2).sum()
so = (wO**2).sum()
print("script vac_even =", round(se/(se+so), 6), " vac_odd =", round(so/(se+so), 6))
print("script ratio vac_odd/vac_even =", round((so/(se+so))/(se/(se+so)), 6), " (=", round(so/se,6), ")")
print("claimed 'theory 88/90' =", round(88/90, 6))
print("BUT the quantity is sum(gamma^2)/sum(gamma^2), NOT sum(gamma) ratio")
print("  actual sum ratio world/observer =", round(world_1.sum()/obs_1.sum(), 6), "= 90/88")
print("  actual sum^2 ratio =", round((world_1**2).sum()/(obs_1**2).sum(), 6))
print("  so comparing vac ratio to 88/90 is comparing different quantities — CIRCULAR")
print()

# theta_0 sign-convention dependence (structural non-invariance)
T = np.zeros((N, N))
for i in range(N):
    T[i, (i+1) % N] = 1.0
    T[i, (i-1) % N] = 1.0
evals, evecs = np.linalg.eigh(T)
idx = np.argsort(evals)
evecs = evecs[:, idx]
v = evecs[:, 0]  # Nyquist m=44
print("Nyquist eigenvector sums: even =", round(v[::2].sum(), 4), " odd =", round(v[1::2].sum(), 4))
print("theta_0 = arctan2(odd, even) =", round(np.degrees(np.arctan2(v[1::2].sum(), v[::2].sum())), 2), "deg")
# flip overall sign (legitimately another eigenvector of the same eigenvalue)
print("with global sign flip: theta_0 =", round(np.degrees(np.arctan2(-v[1::2].sum(), -v[::2].sum())), 2), "deg")
print("=> theta_0 is SIGN-CONVENTION dependent, not a spectral invariant; '135° 由88/90鎖定' unsupported")
