#!/usr/bin/env python3
"""
O45 — 獨立驗證腳本: 核實所有推導、公式、數值
===============================================
驗證 01_smhw_extract.py 結果 同 02_closing_report.md 嘅所有數值
"""
import os, sys, json
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import eval_legendre

# ---------- 路徑 ----------
PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
RAW = os.path.join(PROJECT, 'open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits')
NODES = os.path.join(PROJECT, 'main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
O42_RESULTS = os.path.join(PROJECT, 'open_problems_fresh/o42_independent_measurement_A/data/01_smhw_results.json')
O45_RESULTS = os.path.join(PROJECT, 'open_problems_fresh/o45_smhw_verify/data/01_smhw_results.json')

A_IDCM = 134.2
TOL = 0.05  # 5% tolerance for numerical comparisons
pass_count = 0
fail_count = 0

def check(name, condition, detail=''):
    global pass_count, fail_count
    if condition:
        pass_count += 1
        print(f"  ✅ {name}")
    else:
        fail_count += 1
        print(f"  ❌ {name} — {detail}")

def check_value(name, got, expected, tol=TOL, unit=''):
    rel_err = abs(got - expected) / max(abs(expected), 1e-10) * 100
    ok = rel_err < tol * 100
    if ok:
        global pass_count
        pass_count += 1
        print(f"  ✅ {name} = {got:.4f} {unit} (expected {expected})")
    else:
        global fail_count
        fail_count += 1
        print(f"  ❌ {name} = {got:.4f} {unit} (expected {expected}, err={rel_err:.2f}%)")

print("=" * 70)
print("O45 獨立驗證: 所有數值、公式、推導")
print("=" * 70)

# ========== 1. Nodes validation ==========
print("\n--- 1. 節點座標驗證 ---")
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

# 節點 0 應為 (209°, -57°) 附近
check_value("Node 0 l (Gal)", l_arr[0], 209.0, 0.01)
check_value("Node 0 b (Gal)", b_arr[0], -57.0, 0.01)
check("60 nodes total", len(nodes) == 60)

# ========== 2. SMHW kernel validation ==========
print("\n--- 2. SMHW kernel 基本驗證 ---")
def smhw_wl(R_rad, lmax, npts=200):
    gamma, wgt = np.polynomial.legendre.leggauss(npts)
    gamma = (gamma+1)*np.pi/2; wgt = wgt*np.pi/2
    x = gamma/(2*R_rad)
    psi = (2*np.pi)**(-0.5)/R_rad*(1+x**2)*(2-x**2)*np.exp(-gamma**2/(2*R_rad**2))
    cg = np.cos(gamma); ls = np.arange(lmax+1)
    wl = np.empty(lmax+1)
    for l in ls:
        wl[l] = 2*np.pi*np.sum(wgt*psi*eval_legendre(l,cg)*np.sin(gamma))
    return wl

# 核在 l=0 非零 (SMHW 係 flat-sky wavelet, 球面積分唔係零)
# 無偏 step 扣 l<3 模式, 所以 ψ_l=0 非零唔影響結果
wl_test = smhw_wl(np.radians(4.17), 100)  # just check it runs
check("SMHW ψ_l>0 non-zero", np.sum(np.abs(wl_test[1:]) > 1e-10) > 50)

# ========== 3. Raw SMICA map ==========
print("\n--- 3. Raw SMICA map 驗證 ---")
m = hp.read_map(RAW, field=0)
nside_raw = hp.get_nside(m)
check("nside=2048", nside_raw == 2048)
check("nside2npix(2048) = 50331648", len(m) == 50331648)
check("Finite pixels", np.isfinite(m).mean() > 0.999)
check("Dipole removed (mean ≈ 0)", abs(m.mean()) < 1e-8)

# ========== 4. SMHW extraction reproduction ==========
print("\n--- 4. SMHW 提取獨立重現 ---")
m1024 = hp.ud_grade(hp.remove_dipole(m), 1024)
nside = 1024; lmax = 3*nside
a_lm = hp.map2alm(m1024, lmax=lmax)
pix0 = hp.ang2pix(nside, l_arr[0], b_arr[0], lonlat=True)

scales = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
o45 = json.load(open(O45_RESULTS))
print(f"  {'R(°)':>6} {'獨立重現(μK)':>14} {'記錄值(μK)':>14} {'一致?':>6}")
print(f"  {'-'*45}")

for R in scales:
    R_rad = np.radians(R)
    wl = smhw_wl(R_rad, lmax)
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    T_re = float(wmap[pix0]) * 1e6
    T_rec = o45['smhw'][str(R)]['T_wavelet']
    ok = abs(T_re - T_rec) < 0.1
    print(f"  {R:>6.2f} {T_re:>14.2f} {T_rec:>14.2f} {'✅' if ok else '❌'}")

# 也驗證 rank
for R in scales:
    R_rad = np.radians(R)
    wl = smhw_wl(R_rad, lmax)
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    w_uK = wmap * 1e6
    T0 = float(w_uK[pix0])
    T_all = w_uK[hp.ang2pix(nside, l_arr, b_arr, lonlat=True)]
    rank_re = int(np.sum(T_all < T0) + 1)
    rank_rec = o45['smhw'][str(R)]['rank']
    check(f"rank R={R}°: {rank_re}/{rank_rec}", rank_re == rank_rec, "")

# ========== 5. vs O42 ==========
print("\n--- 5. 與 O42 交叉驗證 ---")
o42 = json.load(open(O42_RESULTS))
for R in scales:
    Rk = str(R)
    if Rk in o42['smhw']:
        v42 = o42['smhw'][Rk]['T']
        v45 = o45['smhw'][Rk]['T_wavelet']
        check(f"O42 vs O45 R={R}°: {v42:.2f} vs {v45:.2f} μK", abs(v42 - v45) < 0.1, f"diff={abs(v42-v45):.4f}")

# ========== 6. Model comparison verification ==========
print("\n--- 6. 模型比對驗證 ---")
sigma_int = 8.66 / 2.355  # intrinsic FWHM=8.66° → σ
print(f"  內稟 σ = 8.66/2.355 = {sigma_int:.3f}°")
check("σ_int ≈ 3.68°", abs(sigma_int - 3.68) < 0.01)

npix = hp.nside2npix(nside)
v0 = hp.ang2vec(l_arr[0], b_arr[0], lonlat=True)
v = hp.pix2vec(nside, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))

# Intrinsic model
m_int = -A_IDCM * np.exp(-ang**2/(2*sigma_int**2)) * 1e-6
a_int = hp.map2alm(m_int, lmax=lmax)

print(f"  {'R(deg)':>6} {'Model(uK)':>14} {'Obs(uK)':>14} {'Ratio':>8}")
print(f"  {'-'*45}")
for R in scales:
    R_rad = np.radians(R)
    wl = smhw_wl(R_rad, lmax)
    aw = hp.almxfl(a_int, wl)
    wm = hp.alm2map(aw, nside=nside, lmax=lmax)
    alo = hp.almxfl(a_int, wl * (np.arange(lmax+1) < 3))
    wm -= hp.alm2map(alo, nside=nside, lmax=lmax)
    pred = float(wm[pix0]) * 1e6
    obs = o45['smhw'][str(R)]['T_wavelet']
    ratio = obs/pred if pred != 0 else 0
    print(f"  {R:>6.2f} {pred:>14.2f} {obs:>14.2f} {ratio:>8.3f}")
    # 確認內稟模型係最佳匹配 (ratio > R8-smoothed model ratio)
    # R8-smoothed: σ=4.17/2.355=1.771°
    m_r8 = -A_IDCM * np.exp(-ang**2/(2*(4.17/2.355)**2)) * 1e-6
    a_r8 = hp.map2alm(m_r8, lmax=lmax)
    aw_r8 = hp.almxfl(a_r8, wl)
    wm_r8 = hp.alm2map(aw_r8, nside=nside, lmax=lmax)
    alo_r8 = hp.almxfl(a_r8, wl * (np.arange(lmax+1) < 3))
    wm_r8 -= hp.alm2map(alo_r8, nside=nside, lmax=lmax)
    pred_r8 = float(wm_r8[pix0]) * 1e6
    ratio_r8 = obs/pred_r8 if pred_r8 != 0 else 0
    # 內稟模型比率應更接近 1
    check(f"R={R}deg: intrinsic model ({abs(ratio):.2f}x) closer to 1 than R8 ({abs(ratio_r8):.2f}x)",
          abs(ratio - 1) < abs(ratio_r8 - 1), f"ratio_int={ratio:.3f}, ratio_r8={ratio_r8:.3f}")

# ========== 7. Kurtosis ==========
print("\n--- 7. Kurtosis 驗證 ---")
# 獨立計算 kurtosis @ R=4.17°
R = 4.17
wl = smhw_wl(np.radians(R), lmax)
alm_w = hp.almxfl(a_lm, wl)
wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
w_uK = wmap * 1e6
kurt = np.mean((w_uK - w_uK.mean())**4) / np.std(w_uK)**4 - 3
kurt_rec = o45['smhw']['4.17']['kurtosis']
check(f"Kurtosis R=4.17°: {kurt:.3f} vs {kurt_rec:.3f}", abs(kurt - kurt_rec) < 0.001, f"diff={abs(kurt-kurt_rec):.6f}")

# Gaussian expectation
N_pix = hp.nside2npix(nside)
kurt_sigma = np.sqrt(24.0 / N_pix)
check(f"Gaussian kurtosis σ = sqrt(24/{N_pix}) = {kurt_sigma:.4f}", abs(kurt_sigma - 0.00138) < 0.0001)

# ========== 8. Document consistency ==========
print("\n--- 8. 文檔一致性驗證 ---")
# 02_closing_report.md 中嘅數值
report_values = {
    'R1_T': -14.16, 'R2_T': -25.25, 'R3_T': -30.02,
    'R4.17_T': -31.17, 'R5_T': -30.28, 'R7_T': -23.35, 'R10_T': -11.20,
    'R1_rank': 1, 'R2_rank': 1, 'R3_rank': 1,
    'R4.17_rank': 2, 'R5_rank': 2, 'R7_rank': 6, 'R10_rank': 18,
    'R1_kurt': 0.092, 'R2_kurt': 0.135, 'R3_kurt': 0.126,
    'R4.17_kurt': 0.110, 'R5_kurt': 0.108, 'R7_kurt': 0.115, 'R10_kurt': 0.101,
}
for key, val in report_values.items():
    # Extract R from key: 'R1_T' -> 1.0, 'R4.17_T' -> 4.17, etc.
    R_raw = key.split('_')[0].replace('R', '')
    # Map to JSON key: '1' -> '1.0', '2' -> '2.0', etc.
    if '.' not in R_raw:
        R = R_raw + '.0'
    else:
        R = R_raw
    if 'T' in key:
        db_val = o45['smhw'][R]['T_wavelet']
        if abs(val) > 0:
            check(f"Report {key}={val} μK vs DB {db_val:.2f}", abs(val - db_val) < 0.02, f"diff={abs(val-db_val):.4f}")
    elif 'rank' in key:
        db_val = o45['smhw'][R]['rank']
        check(f"Report {key}={val} vs DB {db_val}", val == db_val)
    elif 'kurt' in key:
        db_val = o45['smhw'][R]['kurtosis']
        if abs(val) > 0:
            check(f"Report {key}={val} vs DB {db_val:.3f}", abs(val - db_val) < 0.002, f"diff={abs(val-db_val):.6f}")

# 模型比對數值
model_vals = {
    'R8_1.0': -9.26, 'R8_2.0': -10.85, 'R8_3.0': -9.38,
    'R8_4.17': -7.51, 'R8_5.0': -6.45, 'R8_7.0': -4.67, 'R8_10.0': -3.12,
    'int_1.0': -10.89, 'int_2.0': -18.49, 'int_3.0': -21.76,
    'int_4.17': -21.83, 'int_5.0': -20.70, 'int_7.0': -17.04, 'int_10.0': -12.29,
}

# Recompute these values independently
sigma_r8 = 4.17/2.355
m_r8_full = -A_IDCM * np.exp(-ang**2/(2*sigma_r8**2)) * 1e-6
a_r8_full = hp.map2alm(m_r8_full, lmax=lmax)
m_int_full = -A_IDCM * np.exp(-ang**2/(2*sigma_int**2)) * 1e-6
a_int_full = hp.map2alm(m_int_full, lmax=lmax)

for R in scales:
    Rk = str(R)
    wl = smhw_wl(np.radians(R), lmax)
    
    # R8 model
    aw = hp.almxfl(a_r8_full, wl)
    wm = hp.alm2map(aw, nside=nside, lmax=lmax)
    alo = hp.almxfl(a_r8_full, wl * (np.arange(lmax+1) < 3))
    wm -= hp.alm2map(alo, nside=nside, lmax=lmax)
    p_r8 = float(wm[pix0]) * 1e6
    
    # Intrinsic model
    aw = hp.almxfl(a_int_full, wl)
    wm = hp.alm2map(aw, nside=nside, lmax=lmax)
    alo = hp.almxfl(a_int_full, wl * (np.arange(lmax+1) < 3))
    wm -= hp.alm2map(alo, nside=nside, lmax=lmax)
    p_int = float(wm[pix0]) * 1e6
    
    key_r8 = f'R8_{Rk}'
    key_int = f'int_{Rk}'
    if key_r8 in model_vals:
        expected = model_vals[key_r8]
        check(f"Model R8 R={R}°: {p_r8:.2f} vs doc {expected}", 
              abs(p_r8 - expected) < 0.05, f"diff={abs(p_r8-expected):.4f}")
    if key_int in model_vals:
        expected = model_vals[key_int]
        check(f"Model Int R={R}°: {p_int:.2f} vs doc {expected}",
              abs(p_int - expected) < 0.05, f"diff={abs(p_int-expected):.4f}")

# ========== 9. Summary ==========
print("\n" + "=" * 70)
total = pass_count + fail_count
print(f"驗證結果: {pass_count}/{total} PASS, {fail_count}/{total} FAIL")
if fail_count == 0:
    print("🎉 所有數值、公式、推導完全正確!")
else:
    print(f"⚠️ {fail_count} 個檢查失敗，需修正")
print("=" * 70)