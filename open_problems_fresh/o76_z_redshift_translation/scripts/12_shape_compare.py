#!/usr/bin/env python3
"""
O76/12: 形狀比較 — 分離 M 效應, IDCM vs ΛCDM 殘差
================================================================
O76/11: 低 z 殘差係 M global fit 效應 (用共同 M 後 IDCM 更好)

關鍵問題: z>0.3 高 z 區, IDCM vs ΛCDM 邊個形狀啱?

方法: 用「共同 M」+ 分 bin 殘差
  1. fit M 喺低 z (z<0.1) — 用低 z 數據定 M (唔受高 z 形狀影響)
  2. 用呢個 M, 比較全 z 殘差
  3. 睇 IDCM 同 ΛCDM 邊個形狀 match 高 z
"""
import numpy as np
import math
import json

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

C_LIGHT = 299792.458
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697
OMEGA_RING = 72.59

print("=" * 70)
print("O76/12: 形狀比較 — 分離 M 效應")
print("=" * 70)

data_path = 'data/pantheon/Pantheon+SH0ES.dat'
cov_path = 'data/pantheon/Pantheon+SH0ES_STAT+SYS.cov'
with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}
zs, mb = [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        zs.append(float(parts[col['zCMB']]))
        mb.append(float(parts[col['m_b_corr']]))
zs = np.array(zs); mb = np.array(mb)
N = len(zs)
with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_inv = np.linalg.inv(cov)

def fit_M(mu_model, mask=None):
    if mask is None:
        mask = np.ones(N, bool)
    J = np.ones(mask.sum())
    Cm = cov_inv[np.ix_(mask, mask)]
    mub = mu_model[mask]
    return (J @ Cm @ (mb[mask] - mub)) / (J @ Cm @ J)

def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

ell_arr = np.log(1+zs)/np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
mu_lcdm0 = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, OMEGA_RING, 0.315) for zi in zs])*1e6/10)

# ============ 1. 低 z fit M (z<0.1) ============
print("\n--- 1. 低 z fit M (z<0.1, N=741) ---")
mask_low = zs < 0.1
M_idcm_low = fit_M(mu_idcm0, mask_low)
M_lcdm_low = fit_M(mu_lcdm0, mask_low)
print(f"M_IDCM (低z fit) = {M_idcm_low:.4f}")
print(f"M_ΛCDM (低z fit) = {M_lcdm_low:.4f}")
print(f"差 = {M_idcm_low - M_lcdm_low:+.4f}")

# ============ 2. 分 bin 殘差 (低 z fit M) ============
print("\n--- 2. 分 bin 殘差 (低 z fit M) ---")
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5),
        (0.5, 0.8), (0.8, 1.2), (1.2, 1.8), (1.8, 2.3)]
print(f"{'z bin':<12} {'N':<5} {'IDCM':<9} {'ΛCDM':<9} {'Δ(IDCM-ΛCDM)':<14}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    r1 = (mb - (mu_idcm0 + M_idcm_low))[m].mean()
    r2 = (mb - (mu_lcdm0 + M_lcdm_low))[m].mean()
    print(f"{lo:.2f}-{hi:.2f}  {m.sum():<5} {r1:<+9.4f} {r2:<+9.4f} {r1-r2:<+14.4f}")

# ============ 3. 高 z χ² (低 z fit M) ============
print("\n--- 3. χ² 分解 (低 z fit M) ---")
mask_hi = zs >= 0.1
chi2_idcm_hi = (mb - (mu_idcm0 + M_idcm_low)) @ cov_inv @ (mb - (mu_idcm0 + M_idcm_low))
chi2_lcdm_hi = (mb - (mu_lcdm0 + M_lcdm_low)) @ cov_inv @ (mb - (mu_lcdm0 + M_lcdm_low))
# 全樣本
chi2_idcm_all = (mb - (mu_idcm0 + M_idcm_low)) @ cov_inv @ (mb - (mu_idcm0 + M_idcm_low))
chi2_lcdm_all = (mb - (mu_lcdm0 + M_lcdm_low)) @ cov_inv @ (mb - (mu_lcdm0 + M_lcdm_low))
print(f"IDCM χ²:  全樣本 {chi2_idcm_all:.1f}")
print(f"ΛCDM χ²:  全樣本 {chi2_lcdm_all:.1f}")
print(f"→ Δχ² = {chi2_idcm_all - chi2_lcdm_all:+.1f}")

# 只用高 z
mask_hi = zs >= 0.3
C_hi = cov_inv[np.ix_(mask_hi, mask_hi)]
r_idcm_hi = (mb - (mu_idcm0 + M_idcm_low))[mask_hi]
r_lcdm_hi = (mb - (mu_lcdm0 + M_lcdm_low))[mask_hi]
chi2_idcm_hi = r_idcm_hi @ C_hi @ r_idcm_hi
chi2_lcdm_hi = r_lcdm_hi @ C_hi @ r_lcdm_hi
print(f"\n只用 z>0.3 ({mask_hi.sum()} SNe):")
print(f"  IDCM χ² = {chi2_idcm_hi:.1f} / {mask_hi.sum()} dof")
print(f"  ΛCDM χ² = {chi2_lcdm_hi:.1f} / {mask_hi.sum()} dof")
print(f"  Δχ² = {chi2_idcm_hi - chi2_lcdm_hi:+.1f}")

# ============ 4. 關鍵: 高 z 形狀 ============
print("\n--- 4. 高 z 形狀要求 (z>0.3) ---")
# 用低 z fit M, 反推高 z D_req
D_req_hi = d_app(np.log(1+zs[mask_hi])/np.log(4)) * 10**((mb - (mu_idcm0 + M_idcm_low))[mask_hi]/5)
print(f"{'z':<6} {'N':<4} {'D_req(SNe)':<11} {'D_app':<9} {'D_ΛCDM':<9}")
for z in [0.35, 0.5, 0.65, 0.8, 1.0, 1.3, 1.6, 2.0]:
    m = (zs >= z*0.85) & (zs < z*1.15) & (zs >= 0.3)
    if m.sum() < 2: continue
    Dreq = np.median(d_app(np.log(1+zs[m])/np.log(4)) * 10**((mb - (mu_idcm0 + M_idcm_low))[m]/5))
    ell = math.log(1+z, 4)
    Da = d_app(ell)
    Dc = dc_lcdm(z, OMEGA_RING, 0.315)
    print(f"{z:<6} {m.sum():<4} {Dreq:<11.1f} {Da:<9.1f} {Dc:<9.1f}")

result = {
    'M_idcm_lowz': round(float(M_idcm_low), 4),
    'M_lcdm_lowz': round(float(M_lcdm_low), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/12_shape_compare.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/12_shape_compare.json")
