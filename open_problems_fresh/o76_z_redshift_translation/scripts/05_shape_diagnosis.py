#!/usr/bin/env python3
"""
O76/05: D_app 形狀診斷 — 殘差結構分析 + 超新星專用修正
================================================================
發現: IDCM D_L=(1+z)·D_app 喺 Pantheon+ 有 S 形殘差
  低 z: +0.067 (偏亮)
  中 z: -0.03 (match)
  高 z: -0.10~-0.13 (偏暗)

問題: 係咪 D_app 形狀錯, 定係超新星有額外效應?

診斷:
  1. 畫出 IDCM/ΛCDM 距離比 vs z
  2. 睇殘差嘅 z 依賴 (係咪 smooth? 有冇特徵尺度?)
  3. 嘗試: D_app 嘅 C 係咪要 fit (超新星獨立校準)?
  4. 比較: 如果 C fit 超新星, DESI BAO 仲 fit 唔 fit?
"""
import numpy as np
import math
import json
from scipy import optimize

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
OMEGA_RING = 72.59
C_DELAY = -0.1697

print("=" * 70)
print("O76/05: D_app 形狀診斷 + 超新星專用修正")
print("=" * 70)

# ============ 1. 載入 ============
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

def fit_M(mu_model):
    J = np.ones(N)
    return (J @ cov_inv @ (mb - mu_model)) / (J @ cov_inv @ J)

def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def mu_idcm(z, M, C=C_DELAY):
    ell = np.log(1+z) / np.log(4)
    DL = (1+z) * d_app(ell, C)
    return M + 5*np.log10(DL*1e6/10)

# ============ 2. 距離比: D_app vs ΛCDM D_C ============
print("\n--- 2. D_app/ΛCDM 距離比 (H0=72.59 標尺) ---")
def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

print(f"{'z':<6} {'D_app':<9} {'D_C(ΛCDM)':<10} {'比':<8}")
for z in [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    ell = math.log(1+z, 4)
    da = d_app(ell)
    dc = dc_lcdm(z, OMEGA_RING, 0.315)
    print(f"{z:<6} {da:<9.1f} {dc:<10.1f} {da/dc:<8.4f}")

# ============ 3. Fit C (超新星獨立校準) ============
print("\n--- 3. Fit C (超新星獨立校準, M 同時 fit) ---")
def loss(params):
    C, M = params
    resid = mb - mu_idcm(zs, M, C)
    return resid @ cov_inv @ resid

best = None
for C0 in [-0.3, -0.2, -0.1697, -0.1, 0.0, 0.1, 0.2]:
    r = optimize.minimize(loss, [C0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 300, 'xatol': 1e-7, 'fatol': 1e-2})
    if best is None or r.fun < best.fun:
        best = r

C_fit, M_fit = best.x
chi2_C_fit = best.fun
print(f"C_fit = {C_fit:.4f} (vs O51 C = {C_DELAY})")
print(f"M_fit = {M_fit:.4f}")
print(f"χ² = {chi2_C_fit:.1f} (vs 固定 C: 2096.0)")

# ============ 4. C fit 後 DESI BAO 仲 fit 唔 fit? ============
print("\n--- 4. C_fit 對 DESI BAO 影響 ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
chi2_desi_fixed = 0
chi2_desi_fit = 0
print(f"{'樣本':<12} {'z':<6} {'DESI':<8} {'C=-0.1697':<12} {'C_fit':<10}")
for name, z, obs, err in desi:
    ell = math.log(1+z, 4)
    pred_fixed = d_app(ell, C_DELAY) / rd_idcm
    pred_fit = d_app(ell, C_fit) / rd_idcm
    chi2_desi_fixed += ((pred_fixed - obs)/err)**2
    chi2_desi_fit += ((pred_fit - obs)/err)**2
    print(f"{name:<12} {z:<6} {obs:<8} {pred_fixed:<12.3f} {pred_fit:<10.3f}")
print(f"DESI χ² (C=-0.1697): {chi2_desi_fixed:.2f}")
print(f"DESI χ² (C_fit):     {chi2_desi_fit:.2f}")

# ============ 5. 綜合分析 ============
print("\n--- 5. 綜合分析 ---")
print(f"SNe χ²:  固定 C → 2096.0,  fit C → {chi2_C_fit:.1f} (改善 {2096-chi2_C_fit:.1f})")
print(f"DESI χ²: 固定 C → {chi2_desi_fixed:.2f},  fit C → {chi2_desi_fit:.2f} (變化 {chi2_desi_fit-chi2_desi_fixed:+.2f})")

# 如果 C_fit 令 DESI 惡化太多 → C 唔可以為超新星改
if chi2_desi_fit > chi2_desi_fixed + 10:
    print("⚠️ C_fit 令 DESI 惡化 >10 → 唔可以單獨為 SNe 改 C")
else:
    print("🟢 C_fit 對 DESI 影響細 → 有可能兩者相容")

# ============ 6. 殘差結構: 有冇特徵尺度? ============
print("\n--- 6. 殘差 vs z (固定 C) ---")
mu_model = mu_idcm(zs, fit_M(mu_idcm(zs, 0, C_DELAY)), C_DELAY)
resid = mb - mu_model
# 分 bin 加權平均
bins = [(0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3),
        (0.3, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
print(f"{'z bin':<12} {'N':<6} {'<resid>':<10} {'σ':<8}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    r = resid[m]
    w = 1/np.sqrt(np.diag(cov)[m])
    rw = np.average(r, weights=w)
    print(f"{lo:.2f}-{hi:.2f}    {m.sum():<6} {rw:<+10.4f} {r.std():<8.4f}")

result = {
    'C_fit_sn': round(float(C_fit), 4),
    'chi2_C_fixed': 2096.0,
    'chi2_C_fit': round(float(chi2_C_fit), 1),
    'chi2_desi_fixed': round(float(chi2_desi_fixed), 2),
    'chi2_desi_fit': round(float(chi2_desi_fit), 2),
    'pass': PASS, 'fail': FAIL
}
with open('data/05_shape_diagnosis.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/05_shape_diagnosis.json")
