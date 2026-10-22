#!/usr/bin/env python3
"""
O76/10: DESI vs SNe 距離要求 — 真矛盾定假矛盾?
================================================================
O76/09: 飽和修正 SNe↑ 但 DESI↓ — 兩者要求唔同 D_app 形狀?

診斷: DESI 要求嘅 D_app(z) vs SNe 要求嘅 D_app(z)
  DESI: D_M/rd = 38.99 (z=2.33) → D_M = 38.99 × rd_idcm = 5735 Mpc
  SNe:  D_req(z=2.33) = ?

如果兩者一致 → 冇矛盾, 係 D_app 公式問題 (要更高階修正)
如果不一致 → 距離對偶有問題 (D_L ≠ (1+z)·D_A?)
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
print("O76/10: DESI vs SNe 距離要求")
print("=" * 70)

# ============ 1. DESI 要求 ============
rd_idcm = math.pi * R_WORLD / 88 * 420/421
print(f"rd_idcm = {rd_idcm:.3f} Mpc")
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
print(f"\n{'樣本':<12} {'z':<6} {'D_M/rd':<8} {'D_M req':<10} {'D_app(ℓ)':<10} {'dev':<8}")
for name, z, dm, err in desi:
    ell = math.log(1+z, 4)
    D_req_desi = dm * rd_idcm
    D_app_ell = R_WORLD * (1-4**(-ell)) * (1 + 2*PHI**(-1)*ell + C_DELAY*(ell-0.5)*(1-4**(-ell)))
    print(f"{name:<12} {z:<6} {dm:<8} {D_req_desi:<10.1f} {D_app_ell:<10.1f} {(D_req_desi-D_app_ell)/D_app_ell*100:+.2f}%")

# ============ 2. SNe 要求 (D_req from O76/07) ============
print("\n--- 2. SNe 要求 D_req ---")
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

ell_arr = np.log(1+zs) / np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
M_idcm = fit_M(mu_idcm0)
resid = mb - (mu_idcm0 + M_idcm)
D_req = d_app(ell_arr) * 10**(resid/5)

# DESI z 點附近嘅 SNe D_req
print(f"\nDESI z 點附近 SNe 要求:")
for name, z, dm, err in desi:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() >= 2:
        Dreq_sn = np.median(D_req[m])
        Ddesi = dm * rd_idcm
        print(f"  {name:<12} z={z:<6} N={m.sum():<3} D_req(SNe)={Dreq_sn:8.1f}  D_req(DESI)={Ddesi:8.1f}  差={(Dreq_sn-Ddesi)/Ddesi*100:+.1f}%")
    else:
        print(f"  {name:<12} z={z:<6} 附近冇 SNe (N={m.sum()})")

# ============ 3. 關鍵: D_L vs D_M 轉換 ============
print("\n--- 3. 距離對偶驗證: SNe D_L → D_A ---")
# SNe 量 D_L = (1+z)·D_app (IDCM 對偶)
# DESI 量 D_M = D_A (角直徑)
# 如果對偶正確: D_L/(1+z) = D_A = D_M
# 用 SNe D_req 轉 D_A_req = D_req/(1+z) 同 DESI 比較!
print(f"\n如果 D_L = (1+z)·D_A:")
print(f"{'樣本':<12} {'z':<6} {'D_A(SNe)':<10} {'D_A(DESI)':<10} {'dev':<8}")
for name, z, dm, err in desi:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() < 2: continue
    Dreq_sn = np.median(D_req[m])
    DA_sn = Dreq_sn / (1+z)
    DA_desi = dm * rd_idcm
    print(f"{name:<12} {z:<6} {DA_sn:<10.1f} {DA_desi:<10.1f} {(DA_sn-DA_desi)/DA_desi*100:+.1f}%")

# ============ 4. 如果 D_L = (1+z)²·D_A 呢? ============
print(f"\n如果 D_L = (1+z)²·D_A (ΛCDM 對偶):")
print(f"{'樣本':<12} {'z':<6} {'D_A(SNe)':<10} {'D_A(DESI)':<10} {'dev':<8}")
for name, z, dm, err in desi:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() < 2: continue
    Dreq_sn = np.median(D_req[m])
    DA_sn = Dreq_sn / (1+z)**2
    DA_desi = dm * rd_idcm
    print(f"{name:<12} {z:<6} {DA_sn:<10.1f} {DA_desi:<10.1f} {(DA_sn-DA_desi)/DA_desi*100:+.1f}%")

result = {
    'note': '比較 DESI 同 SNe 要求嘅距離',
    'pass': PASS, 'fail': FAIL
}
with open('data/10_desi_vs_sn.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/10_desi_vs_sn.json")
