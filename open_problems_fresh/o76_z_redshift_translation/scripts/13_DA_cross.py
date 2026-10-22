#!/usr/bin/env python3
"""
O76/13: D_A_req vs DESI — 距離對偶交叉驗證
================================================================
O76/12: SNe D_L 要求 D_req 貼近 ΛCDM D_C (唔係 D_app)

但 IDCM 距離對偶係 D_L = (1+z)·D_A (O76/06)
→ D_A_req = D_req/(1+z) 先係 SNe 要求嘅「角直徑距離」
→ 呢個先應該同 DESI D_M 比較!

如果 D_A_req 貼近 D_app → IDCM 對偶自洽, 問題喺 D_L 定義
如果 D_A_req 貼近 ΛCDM D_A → 對偶有問題
如果 D_A_req 喺兩者之間 → 兩者都錯

★ 關鍵: DESI BAO 量嘅係 D_M (角直徑) = D_A
  SNe 量嘅係 D_L (光度)
  如果 IDCM 對偶 D_L = (1+z)·D_A 正確:
    D_A_req(SNe) 應該 = D_A_req(DESI)
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
print("O76/13: D_A_req vs DESI — 距離對偶交叉驗證")
print("=" * 70)

# ============ 1. 載入 SNe + 反推 D_req ============
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
    if mask is None: mask = np.ones(N, bool)
    J = np.ones(mask.sum())
    Cm = cov_inv[np.ix_(mask, mask)]
    return (J @ Cm @ (mb[mask] - mu_model[mask])) / (J @ Cm @ J)

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
mask_low = zs < 0.1
M_idcm = fit_M(mu_idcm0, mask_low)
resid = mb - (mu_idcm0 + M_idcm)
D_req = d_app(ell_arr) * 10**(resid/5)   # D_L 要求
DA_req = D_req / (1+zs)                    # D_A 要求 (IDCM 對偶)

# ============ 2. DESI D_A 要求 ============
print("\n--- 2. DESI vs SNe D_A 要求 (IDCM 對偶 D_L=(1+z)D_A) ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
print(f"{'樣本':<12} {'z':<6} {'D_A(DESI)':<10} {'D_A(SNe)':<10} {'D_app':<9} {'D_A(ΛCDM)':<10}")
for name, z, dm, err in desi:
    m = (zs >= z*0.85) & (zs < z*1.15) & (zs >= 0.3)
    if m.sum() < 2:
        print(f"{name:<12} {z:<6} {dm*rd_idcm:<10.1f} — SNe 不足 —")
        continue
    DA_desi = dm * rd_idcm
    DA_sn = np.median(DA_req[m])
    ell = math.log(1+z, 4)
    Da = d_app(ell)
    DA_lcdm = dc_lcdm(z, OMEGA_RING, 0.315)/(1+z)
    print(f"{name:<12} {z:<6} {DA_desi:<10.1f} {DA_sn:<10.1f} {Da:<9.1f} {DA_lcdm:<10.1f}")

# ============ 3. 用 ΛCDM 對偶 (D_L=(1+z)²D_A) 比較 ============
print("\n--- 3. 如果用 ΛCDM 對偶 D_L=(1+z)²D_A ---")
DA_req2 = D_req / (1+zs)**2
print(f"{'樣本':<12} {'z':<6} {'D_A(DESI)':<10} {'D_A(SNe)':<10} {'D_A(ΛCDM)':<10}")
for name, z, dm, err in desi:
    m = (zs >= z*0.85) & (zs < z*1.15) & (zs >= 0.3)
    if m.sum() < 2: continue
    DA_desi = dm * rd_idcm
    DA_sn = np.median(DA_req2[m])
    DA_lcdm = dc_lcdm(z, OMEGA_RING, 0.315)/(1+z)
    print(f"{name:<12} {z:<6} {DA_desi:<10.1f} {DA_sn:<10.1f} {DA_lcdm:<10.1f}")

# ============ 4. 總結 ============
print("\n--- 4. 結論 ---")
print(f"""
IDCM 對偶 (D_L=(1+z)·D_A) 驗證:
  D_A(SNe) vs D_A(DESI):
    如果兩者一致 → IDCM 對偶 OK, D_app 形狀錯
    如果唔一致 → 對偶本身要改

ΛCDM 對偶 (D_L=(1+z)²·D_A) 驗證:
  同上
""")

result = {
    'note': '交叉驗證距離對偶',
    'pass': PASS, 'fail': FAIL
}
with open('data/13_DA_cross.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/13_DA_cross.json")
