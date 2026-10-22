#!/usr/bin/env python3
"""
O51/86d: Extended scan to find the true C₃ minimum
"""
import json, math, numpy as np

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
rd_c = math.pi * R_H / 88 * 420/421

desi_data = [
    ('BGS',      0.295, 'DV', 7.942, 0.075),
    ('LRG1',     0.510, 'DM', 13.588, 0.167),
    ('LRG2',     0.706, 'DM', 17.351, 0.177),
    ('LRG3+ELG', 0.934, 'DM', 21.576, 0.152),
    ('ELG2',     1.321, 'DM', 27.601, 0.318),
    ('QSO',      1.484, 'DV', 26.055, 0.398),
    ('Lyα',      2.330, 'DM', 38.988, 0.531),
]

gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
n_cut = 27
w_gd = [1/v_g[n] for n in range(n_cut)]
w_weighted = [w_gd[n]*gamma[n] for n in range(n_cut)]
sum_w_w = sum(w_weighted)
mean_gd = sum((n+1)*w_weighted[n] for n in range(n_cut)) / sum_w_w
var_gd = sum((n+1-mean_gd)**2*w_weighted[n] for n in range(n_cut)) / sum_w_w
kurt_gd = sum((n+1-mean_gd)**4*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**2 - 3
w_even = sum(w_gd[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_gd[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
beta1 = C_delay; beta3 = kurt_gd * var_gd / (mean_gd**2)
C1 = -beta1 * 2 * phi**(-1) * 5**0.5
C3_kurt = -beta3 * 2 * phi**(-1) * 5**0.5

def D_func_cub(ell, scale):
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    delta3 = C3_kurt * scale * (ell - 0.5)**3 * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1 + delta3)

def DH_from_z(Dfunc, z):
    dz = 1e-6; ell = math.log(1+z, 4)
    ep = math.log(1+z+dz, 4); em = math.log(1+z-dz, 4) if z-dz > 0 else 0
    if z-dz <= 0: return 0
    return (Dfunc(ep) - Dfunc(em)) / (2*dz)

def DV_from_DM(dm, dh, z): return (z * dm**2 * dh)**(1/3)

def compute_chi2(scale):
    Dfunc = lambda e: D_func_cub(e, scale)
    chi2 = 0
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4); d_app = Dfunc(ell)
        pred = d_app / rd_c if dtype == 'DM' else DV_from_DM(d_app, DH_from_z(Dfunc, z), z) / rd_c
        chi2 += ((pred - obs)/err)**2
    return chi2

# Extended scan
scales = np.linspace(-10, 100, 1101)
chi2s = np.array([compute_chi2(s) for s in scales])
best_idx = np.argmin(chi2s)
best_scale = scales[best_idx]
best_chi2 = chi2s[best_idx]

print(f"Extended scan [-10, 100]: best scale = {best_scale:.2f}, chi2 = {best_chi2:.2f}")

# Fine scan around the minimum
delta = 5
scales2 = np.linspace(best_scale - delta, best_scale + delta, 201)
chi2s2 = np.array([compute_chi2(s) for s in scales2])
best_idx2 = np.argmin(chi2s2)
best_scale2 = scales2[best_idx2]
best_chi2_2 = chi2s2[best_idx2]

print(f"Fine scan [{best_scale-delta:.1f}, {best_scale+delta:.1f}]: best scale = {best_scale2:.4f}, chi2 = {best_chi2_2:.2f}")
print(f"Best C3 = C3_kurt x {best_scale2:.4f} = {C3_kurt * best_scale2:.6f}")
print(f"Improvement over linear: {18.09 - best_chi2_2:.2f} chi2 points")

# Print key values
print(f"\nKey values at optimal scale:")
for s in [0, best_scale2]:
    chi2 = compute_chi2(s)
    print(f"  scale={s:.2f}: chi2={chi2:.2f}")

# Generate the final result JSON
result = {
    'C3_structural': round(C3_kurt, 6),
    'C3_optimal': round(C3_kurt * best_scale2, 6),
    'optimal_scale': round(best_scale2, 4),
    'chi2_original': 42.23,
    'chi2_linear': 18.09,
    'chi2_cubic_structural': round(compute_chi2(1), 2),
    'chi2_cubic_optimal': round(best_chi2_2, 2),
    'C1': round(C1, 6),
    'beta1': round(beta1, 6),
    'beta3': round(beta3, 6),
    'kurtosis_gd': round(kurt_gd, 6),
    'beta2sq_beta3_ratio': 3.1,
    'C3_C1_ratio': round(abs(C3_kurt/C1), 4),
}

with open('data/86d_cubic_extended.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\n-> data/86d_cubic_extended.json")