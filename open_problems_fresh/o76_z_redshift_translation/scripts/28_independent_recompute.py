#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O76/28: 獨立重算 (第 2 輪) — 不同數學路線 + 不同線代路徑
================================================================
★ 獨立性聲明:
  - 唔 import scripts/01-26 任何一個
  - 數值路線: mpmath dps=40 + 純 Python (DESI / Nyquist / T(z) / Fisher / 階梯)
  - 線代路線: scipy.linalg.cho_factor/cho_solve (Cholesky) ← 唔用 np.linalg.inv
  - 解析路線: γ 和用 Z₂ 配對恆等式 (唔用逐項求和)
  - 目標: 重現第 2 輪全部 headline 值
"""
import json, math, sys
from pathlib import Path
import mpmath as mpm

mp = mpm.mp
mp.dps = 40
BASE = Path(__file__).resolve().parent.parent

PASS, FAIL = [], []
def chk(name, cond, computed=None, ref=None):
    ok = bool(cond)
    (PASS if ok else FAIL).append(name)
    s = f"  {'[OK]' if ok else '[FAIL]'} {name}"
    if computed is not None:
        s += f"   computed={computed}"
        if ref is not None:
            s += f"  ref={ref}"
    print(s)

def near(name, comp, ref, tol):
    chk(name, abs(mp.mpf(comp) - mp.mpf(ref)) <= mp.mpf(tol), mp.nstr(comp, 14), ref)

print("=" * 78)
print("O76/28 - 獨立重算 (第 2 輪)")
print("=" * 78)

R = mp.mpf('4129.94')
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2
inv = 1 / phi
N = 44
L6, Fp = 18, 17
l_nyq = mp.log(L6, 4)
rd = pi * R / 88 * mp.mpf(420) / 421

# ============ G1. b_spec 兩條路線 ============
print("\n--- G1. b_spec 兩條路線 ---")
b_sum = 22 / mp.fsum(mp.cos(pi * n / 88) for n in range(1, 23))
b_closed = 1 / (mp.sin(pi / 8) * mp.cos(23 * pi / 176) / (22 * mp.sin(pi / 176)))
near("G1a b_spec (逐項求和)", b_sum, '1.1191139820348', '1e-12')
near("G1b b_spec (閉式, 獨立路線)", b_closed, '1.1191139820348', '1e-12')
chk("G1c 兩路線一致 (< 1e-30)", abs(b_sum - b_closed) < mp.mpf('1e-30'),
    mp.nstr(abs(b_sum - b_closed), 4))

# ============ G2. γ 和 — 解析路線 (Z₂ 配對) ============
print("\n--- G2. γ 和 (解析 Z₂ 配對路線, 唔用逐項求和) ---")
# Σ_{n=1}^{44} cos(πn/44) = -1 ; Σ_{odd} = 0 (Z₂ 配對) ; Σ_{even} = -1
# γ_n = 4 sin²(πn/88) = 2(1 - cos(πn/44))
S_odd_analytic = 2 * (22 - 0)
S_eve_analytic = 2 * (22 - (-1))
near("G2a Σγ_odd (解析) = 44", S_odd_analytic, 44, '1e-30')
near("G2b Σγ_even (解析) = 46", S_eve_analytic, 46, '1e-30')
near("G2c Σγ (解析) = 90", S_odd_analytic + S_eve_analytic, 90, '1e-30')
S_odd_dir = mp.fsum(4 * mp.sin(pi * n / 88) ** 2 for n in range(1, 45) if n % 2 == 1)
S_eve_dir = mp.fsum(4 * mp.sin(pi * n / 88) ** 2 for n in range(1, 45) if n % 2 == 0)
chk("G2d 解析 = 逐項 (奇)", abs(S_odd_analytic - S_odd_dir) < mp.mpf('1e-30'),
    mp.nstr(abs(S_odd_analytic - S_odd_dir), 4))
chk("G2e 解析 = 逐項 (偶)", abs(S_eve_analytic - S_eve_dir) < mp.mpf('1e-30'),
    mp.nstr(abs(S_eve_analytic - S_eve_dir), 4))
near("G2f a = Σγ_odd/N_d = 1 (斜率)", S_odd_analytic / 44, 1, '1e-30')

# ============ G3. C 同 φ 恆等式 ============
print("\n--- G3. C = 1 - 2φ⁻¹ = -φ⁻³ (獨立路線: 用 √5 直接算) ---")
C1 = 1 - 2 * inv
C2 = -(mp.sqrt(5) - 2)
near("G3a C (由 φ)", C1, '-0.2360679774997896964', '1e-18')
near("G3b C (由 √5)", C2, '-0.2360679774997896964', '1e-18')
chk("G3c 兩路線一致", abs(C1 - C2) < mp.mpf('1e-35'), mp.nstr(abs(C1 - C2), 4))

# ============ G4. DESI χ²(D_M×6) 三式 (mpmath, 無 numpy) ============
print("\n--- G4. DESI χ²(D_M×6) 三式 ---")
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3+ELG', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]

def DA(l, kind):
    base = R * (1 - 4 ** (-l))
    if kind == 'old':
        return base * (1 + 2 * inv * l)
    if kind == 'old_delta':
        return base * (1 + 2 * inv * l - mp.mpf('0.1697') * (l - mp.mpf('0.5')) * (1 - 4 ** (-l)))
    return base * (l + b_sum)

def chi2_desi(kind, trs=TR):
    t = mp.mpf(0)
    for nm, z, dm, em in trs:
        l = mp.log(1 + mp.mpf(z), 4)
        t += ((DA(l, kind) / rd - mp.mpf(dm)) / mp.mpf(em)) ** 2
    return t

near("G4a OLD χ² = 27.1635", chi2_desi('old'), '27.1635', '5e-4')
near("G4b OLD+δ χ² = 13.0888", chi2_desi('old_delta'), '13.0888', '5e-4')
near("G4c NEW χ² = 2.4528", chi2_desi('new'), '2.4528', '5e-4')
TR5 = [t for t in TR if t[0] != 'QSO']
near("G4d NEW 5-tracer χ² = 1.5305", chi2_desi('new', TR5), '1.5305', '5e-4')
near("G4e OLD+δ 5-tracer χ² = 12.8190 (O76 舊記錄 12.82)",
     chi2_desi('old_delta', TR5), '12.8190', '5e-4')

# ============ G5. Nyquist 比 ============
print("\n--- G5. Nyquist 比 ---")
r_old = DA(l_nyq, 'old_delta') / (pi * R)
r_new = DA(l_nyq, 'new') / (pi * R)
near("G5a 舊 0.9990", r_old, '0.9990', '5e-5')
near("G5b 新 0.9632", r_new, '0.9632', '5e-5')
near("G5c 新式 D_A(ℓ_nyq) = 12497.5 Mpc", DA(l_nyq, 'new'), '12497.497', '0.05')
near("G5d ℓ_Nyq = log₄18 = 2.0849625", l_nyq, '2.0849625', '1e-7')

# ============ G6. z_eff 指數 ============
print("\n--- G6. z_eff 指數 ---")
near("G6a 舊 2φ⁻¹/ln4 = 0.891635", 2 * inv / mp.log(4), '0.891635', '1e-6')
near("G6b 新 1/ln4 = 0.7213475", 1 / mp.log(4), '0.7213475', '1e-7')

# ============ G7. T(z) χ² (純 Python) ============
print("\n--- G7. CMB T(z) χ² (β = 0) ---")
T0 = 2.72548
meas = [(0.89, 5.0791, 0.0994), (1.7293, 7.5, 1.4), (1.7738, 7.8, 0.65),
        (2.0377, 8.6, 1.05), (2.4184, 9.15, 0.72), (2.6896, 10.5, 0.7),
        (3.025, 12.1, 2.45), (6.34, 23.1, 6.9)]
c0 = sum(((T - T0 * (1 + z)) / e) ** 2 for z, T, e in meas)
near("G7a T(z) χ²(β=0) = 1.63", c0, '1.63', '5e-3')
near("G7b χ²/dof = 0.203", c0 / 8, '0.203', '1e-3')
cmin = min(sum(((T - T0 * (1 + z) ** (1 - b)) / e) ** 2 for z, T, e in meas)
           for b in [i / 10000 for i in range(-1000, 1001)])
chk("G7c 自由擬合 β 改善 < 0.01 (數據唔需要偏離 β=0)", c0 - cmin < 0.01,
    f"Δχ² = {c0 - cmin:.5f}")

# ============ G8. Fisher σ_α (手寫 2x2 逆) ============
print("\n--- G8. Fisher σ_α (手寫 2x2 逆, 唔用 numpy) ---")
def sigma_alpha_hand(N, sig=0.12, zlo=0.5, zhi=3.0, seed=1):
    import random
    rng = random.Random(seed)
    zs = [zlo + (zhi - zlo) * rng.random() for _ in range(N)]
    S11 = sum((5 / math.log(10) * math.log(1 + z)) ** 2 for z in zs) / sig ** 2
    S12 = sum(5 / math.log(10) * math.log(1 + z) for z in zs) / sig ** 2
    S22 = N / sig ** 2
    det = S11 * S22 - S12 * S12
    return math.sqrt(S22 / det)

sa500 = sigma_alpha_hand(500)
sa3000 = sigma_alpha_hand(3000)
print(f"     σ_α(500) = {sa500:.5f}   σ_α(3000) = {sa3000:.5f}")
print("     ★ 註: 本段用 Python random (唔同 numpy default_rng) ⟹ MC 實現唔同, 容差放寬至 15%")
chk("G8a σ_α(500) 同 0.00902 一致 (<15%, 唔同 RNG 實現)",
    abs(sa500 - 0.00902) / 0.00902 < 0.15, f"{sa500:.5f} vs 0.00902")
chk("G8b σ_α(3000) 同 0.00364 一致 (<5%)",
    abs(sa3000 - 0.00364) / 0.00364 < 0.05, f"{sa3000:.5f} vs 0.00364")
# N 需要
lo, hi = 100, 200000
for _ in range(50):
    mid = (lo + hi) // 2
    if sigma_alpha_hand(mid) > 0.0392 / 3:
        lo = mid
    else:
        hi = mid
print(f"     N_need (3σ on Δα=0.0392) = {hi}")
chk("G8c N_need ≈ 248 (±30)", abs(hi - 248) <= 30, f"N = {hi}")

# ============ G9. z 階梯計數 (純 Python) ============
print("\n--- G9. z 階梯尖銳區計數 ---")
zs_l = []
with open(BASE / 'data' / 'pantheon' / 'Pantheon+SH0ES.dat') as f:
    hdr = f.readline().split()
    ci = hdr.index('zCMB')
    for line in f:
        p = line.split()
        if len(p) < len(hdr):
            continue
        zs_l.append(float(p[ci]))
rungs = [4.0 ** (m / 33) - 1 for m in range(1, 34)]
tol = 0.002
n_obs = sum(1 for z in zs_l if min(abs(z - r) for r in rungs) < tol)
print(f"     N(z) = {len(zs_l)}   rung 數 = {len(rungs)}   N_obs(tol=0.002) = {n_obs}")
chk("G9a N(z) = 1701", len(zs_l) == 1701, f"{len(zs_l)}")
near("G9b N_obs(tol=0.002) = 81", n_obs, '81', '0')
near("G9c 最低階 z = 0.042904", rungs[0], '0.042904', '1e-6')

# ============ G10. Pantheon+ χ² — Cholesky 路線 ============
print("\n--- G10. Pantheon+ χ² (scipy Cholesky, 唔用 np.linalg.inv) ---")
import numpy as np
from scipy.linalg import cho_factor, cho_solve
dat = BASE / 'data' / 'pantheon' / 'Pantheon+SH0ES.dat'
covf = BASE / 'data' / 'pantheon' / 'Pantheon+SH0ES_STAT+SYS.cov'
with open(dat) as f:
    hdr = f.readline().split()
    ci, mi = hdr.index('zCMB'), hdr.index('m_b_corr')
    Z, MB = [], []
    for line in f:
        p = line.split()
        if len(p) < len(hdr):
            continue
        Z.append(float(p[ci])); MB.append(float(p[mi]))
Z = np.array(Z); MB = np.array(MB)
with open(covf) as f:
    nd = int(f.readline().strip())
COV = np.loadtxt(covf, skiprows=1).reshape(nd, nd)
cf = cho_factor(COV, lower=True)

def cinv_d(d):
    return cho_solve(cf, d)

def fit_and_chi2(mu0):
    d = MB - mu0
    cd = cinv_d(d)
    J = np.ones(len(Z))
    cJ = cinv_d(J)
    M = float((J @ cd) / (J @ cJ))
    r = d - M
    return M, float(r @ cinv_d(r))

ell = np.log(1 + Z) / np.log(4)
b_f = float(b_sum)
DA_np = R_ = 4129.94
def DAf(l, kind):
    base = R_ * (1 - 4.0 ** (-l))
    if kind == 'old_delta':
        return base * (1 + 2 * 0.6180339887498949 * l - 0.1697 * (l - 0.5) * (1 - 4.0 ** (-l)))
    return base * (l + b_f)

npp = 4 * math.sin(7 * math.pi / 88) ** 2 / (4 * math.sin(20 * math.pi / 88) ** 2)

def sn_chi2(kind, alpha):
    DL = (1 + Z) ** (1 + alpha) * DAf(ell, kind)
    mu0 = 5 * np.log10(DL * 1e6 / 10)
    return fit_and_chi2(mu0)

M_a, c_a = sn_chi2('old_delta', -npp)
near("G10a 舊 D_A + α=-n/p χ² = 2006.8 (回歸)", c_a, '2006.8', '0.6')
M_b, c_b = sn_chi2('new', 0.0)
near("G10b 新 D_A + α=0 χ² = 1989.9", c_b, '1989.9', '0.6')
M_c, c_c = sn_chi2('new', -npp)
near("G10c 新 D_A + α=-n/p χ² = 2138.2", c_c, '2138.2', '0.6')
near("G10d n/p = γ₇/γ₂₀ = 0.142618", npp, '0.142618', '1e-6')

# ΛCDM 對照
CL = 299792.458
def dc_arr(zarr):
    zmax = float(np.max(zarr))
    zz = np.geomspace(1e-8, zmax, 4000)
    E = np.sqrt(0.315 * (1 + zz) ** 3 + 0.685)
    integ = 1 / E
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (integ[1:] + integ[:-1]) * np.diff(zz))])
    return np.interp(zarr, zz, cum) * CL / 67.4
mu_l = 5 * np.log10((1 + Z) * dc_arr(Z) * 1e6 / 10)
M_l, c_l = fit_and_chi2(mu_l)
near("G10e ΛCDM Planck χ² = 2002.1", c_l, '2002.1', '0.6')
print(f"     M: 舊α=-n/p {M_a:.4f} | 新α=0 {M_b:.4f} | 新α=-n/p {M_c:.4f} | ΛCDM {M_l:.4f}")

# ============ 總結 ============
print("\n" + "=" * 78)
print(f"O76/28 獨立重算: PASS = {len(PASS)}  FAIL = {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print("   -", f)
print("=" * 78)
with open(BASE / 'data' / '28_independent_recompute.json', 'w') as f:
    json.dump({'pass': len(PASS), 'fail': len(FAIL), 'fails': FAIL}, f, indent=2, ensure_ascii=False)
print("-> data/28_independent_recompute.json")
sys.exit(1 if FAIL else 0)
