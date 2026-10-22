#!/usr/bin/env python3
"""
O76/07: 反推理想 D(z) — 超新星要求嘅距離形狀
================================================================
從 Pantheon+ 殘差直接反推「數據要求嘅 D(z) 形狀」,
同 IDCM D_app 同 ΛCDM D_C 比較。

方法:
  1. fit M (歸一化) → 殘差 δμ(z)
  2. 反推 D_req(z) = D_app(z)·10^{δμ/5}  (IDCM 修正後需要嘅距離)
  3. 比較 D_req vs D_app vs ΛCDM D_C vs Milne vs R·ln(1+z)
  4. 睇 D_req 有冇「結構」— 係咪 smooth 曲線? 有冇特徵?

★ 目的: IDCM D_app 形狀係咪啱? 需要咩修正?
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
print("O76/07: 反推理想 D(z) — 超新星要求嘅距離形狀")
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

def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

# ============ 2. IDCM 殘差 → 反推 D_req ============
print("\n--- 2. 反推 D_req(z) ---")
ell_arr = np.log(1+zs) / np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
M_idcm = fit_M(mu_idcm0)
resid = mb - (mu_idcm0 + M_idcm)
# D_req = D_app · 10^{resid/5}  (μ 差 5 倍 log)
D_req = d_app(ell_arr) * 10**(resid/5)

# ============ 3. 分 bin 平均 D_req vs 模型 ============
print(f"\n--- 3. D_req vs 模型 (分 bin) ---")
bins = [(0.01, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5),
        (0.5, 0.8), (0.8, 1.2), (1.2, 1.8), (1.8, 2.3)]
print(f"{'z bin':<12} {'N':<4} {'<D_req>':<9} {'D_app':<8} {'ΛCDM':<8} {'Milne':<7} {'Rln(1+z)':<9}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    z_mid = zs[m].mean()
    ell_mid = math.log(1+z_mid, 4)
    Dreq = np.median(D_req[m])
    Da = d_app(ell_mid)
    Dc = dc_lcdm(z_mid, OMEGA_RING, 0.315)
    milne = R_WORLD * z_mid/(1+z_mid)
    tl = R_WORLD * math.log(1+z_mid)
    print(f"{lo:.2f}-{hi:.2f}  {m.sum():<4} {Dreq:<9.1f} {Da:<8.1f} {Dc:<8.1f} {milne:<7.1f} {tl:<9.1f}")

# ============ 4. 關鍵比較: D_req/D_app 比 ============
print("\n--- 4. D_req/D_app 比 (需要嘅修正因子) ---")
print(f"{'z bin':<12} {'D_req/D_app':<12} {'詮釋':<20}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    ratio = np.median(D_req[m]/d_app(np.log(1+zs[m])/np.log(4)))
    interp = ""
    if ratio > 1.03: interp = "需要更長距離"
    elif ratio < 0.97: interp = "需要更短距離"
    else: interp = "match"
    print(f"{lo:.2f}-{hi:.2f}  {ratio:<12.4f} {interp}")

# ============ 5. 形狀分析: D_req 有冇結構? ============
print("\n--- 5. D_req 形狀 vs 模型形狀 ---")
# 標準化: 全部喺 z=0.5 歸一化
z_ref = 0.5
Dref_app = d_app(math.log(1+z_ref, 4))
Dref_lcdm = dc_lcdm(z_ref, OMEGA_RING, 0.315)
Dref_milne = R_WORLD * z_ref/(1+z_ref)
Dref_tl = R_WORLD * math.log(1+z_ref)

print(f"{'z':<6} {'D_req/Dref':<10} {'D_app/Dref':<11} {'ΛCDM/Dref':<11} {'Milne/Dref':<11}")
zs_test = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
for z in zs_test:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() < 3:
        continue
    Dreq_z = np.median(D_req[m])
    ell = math.log(1+z, 4)
    ratio_req = Dreq_z/Dref_app
    ratio_app = d_app(ell)/Dref_app
    ratio_lcdm = dc_lcdm(z, OMEGA_RING, 0.315)/Dref_lcdm
    ratio_milne = (R_WORLD*z/(1+z))/Dref_milne
    print(f"{z:<6} {ratio_req:<10.4f} {ratio_app:<11.4f} {ratio_lcdm:<11.4f} {ratio_milne:<11.4f}")

result = {
    'D_req_vs_app': '見上表',
    'residual_shape': 'S形: 低z偏亮 高z偏暗',
    'pass': PASS, 'fail': FAIL
}
with open('data/07_Dreq_inversion.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/07_Dreq_inversion.json")
