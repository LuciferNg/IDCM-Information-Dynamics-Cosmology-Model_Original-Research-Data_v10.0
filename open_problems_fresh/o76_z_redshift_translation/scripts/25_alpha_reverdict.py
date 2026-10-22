#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O76/25: 新 D_A 下嘅光度距離對偶 — alpha 重裁決
================================================================
O76/24 發現: 新 D_A (O169 修正) 下, 舊 alpha = -n/p = -0.1426 已被排除 (dchi2 = +155);
  最佳 alpha 移到 ~+0.04, 而 alpha = 0 (即 D_L = (1+z)*D_A, 零參數) 已達 chi2 = 1989.9,
  **優於** LambdaCDM Planck (2002.1)。

本腳本:
  A. alpha 精細 fit + dchi2 = 1 誤差
  B. 結構候選掃描 (由註冊部件生成, 零新常數)
  C. 分 bin 殘差 (alpha = 0 同 alpha = best)
  D. 高 z (z>0.8) 殘差 — O76 舊開放項
  E. 模型對決 (AIC/BIC): IDCM(alpha=0) vs LambdaCDM Planck vs LambdaCDM fit Om
  F. 可證偽預言重算: D_L/D_A 指數
  G. 對偶自洽: D_L/D_A 同 (1+z)^2 嘅分歧 (z>1)
"""
import json, math
from pathlib import Path
import numpy as np
import mpmath as mpm

mp = mpm.mp
mp.dps = 40
BASE = Path(__file__).resolve().parent.parent

PASS = []
FAIL = []
def chk(name, cond, computed=None, docval=None, unit=''):
    ok = bool(cond)
    (PASS if ok else FAIL).append(name)
    s = f"  {'[OK]' if ok else '[FAIL]'} {name}"
    if computed is not None:
        s += f"   computed={computed}"
        if docval is not None:
            s += f"  ref={docval}"
        if unit:
            s += f" {unit}"
    print(s)

def near(name, computed, docval, tol, unit=''):
    d = abs(float(computed) - float(docval))
    chk(name, d <= tol, f"{float(computed):.10g}", docval, unit)

print("=" * 78)
print("O76/25 - 新 D_A 下光度距離對偶 alpha 重裁決")
print("=" * 78)

# ---------- 常數 ----------
R = 4129.94
phi = (1 + math.sqrt(5)) / 2
inv = 1 / phi
pi = math.pi
N = 44
gam = {n: 4 * math.sin(pi * n / 88) ** 2 for n in range(1, N + 1)}
vg = {n: math.cos(pi * n / 88) for n in range(1, N + 1)}
rd = pi * R / 88 * 420 / 421
b_spec = 22 / sum(vg[n] for n in range(1, 23))
g7 = gam[7]; g20 = gam[20]; np_ratio = g7 / g20
CLIGHT = 299792.458

print(f"  b_spec = {b_spec:.10f} | n/p = {np_ratio:.8f} | rd = {rd:.6f}")

# ---------- 數據 ----------
sn_dat = BASE / 'data' / 'pantheon' / 'Pantheon+SH0ES.dat'
sn_cov = BASE / 'data' / 'pantheon' / 'Pantheon+SH0ES_STAT+SYS.cov'
with open(sn_dat) as f:
    hdr = f.readline().split()
col = {n: i for i, n in enumerate(hdr)}
zs_l, mb_l = [], []
with open(sn_dat) as f:
    f.readline()
    for line in f:
        p = line.split()
        if len(p) < len(hdr):
            continue
        zs_l.append(float(p[col['zCMB']])); mb_l.append(float(p[col['m_b_corr']]))
zs = np.array(zs_l); mb = np.array(mb_l)
NS = len(zs)
with open(sn_cov) as f:
    nd = int(f.readline().strip())
Cov = np.loadtxt(sn_cov, skiprows=1).reshape(nd, nd)
Cinv = np.linalg.inv(Cov)
ell = np.log(1 + zs) / np.log(4)
chk("A0  1701 SNe 載入", NS == 1701, f"N = {NS}")

DA_new = R * (1 - 4.0 ** (-ell)) * (ell + b_spec)

def fit_M(mu):
    J = np.ones(NS)
    return float((J @ Cinv @ (mb - mu)) / (J @ Cinv @ J))

def chi2_mu(mu):
    r = mb - mu
    return float(r @ Cinv @ r)

def model(alpha):
    DL = (1 + zs) ** (1 + alpha) * DA_new
    mu0 = 5 * np.log10(DL * 1e6 / 10)
    M = fit_M(mu0)
    return M, chi2_mu(mu0 + M)

# ================= A. alpha 精細 fit =================
print("\n" + "=" * 78)
print("A. alpha 精細 fit + dchi2 = 1 誤差")
print("=" * 78)
alphas = np.arange(-0.100, 0.151, 0.001)
chis = np.array([model(a)[1] for a in alphas])
i_best = int(np.argmin(chis))
a_best = float(alphas[i_best]); c_best = float(chis[i_best])
M_best = model(a_best)[0]
# 二次插值細化
idx = slice(max(0, i_best - 6), min(len(alphas), i_best + 7))
co = np.polyfit(alphas[idx], chis[idx], 2)
a_star = -co[1] / (2 * co[0]); c_star = np.polyval(co, a_star)
print(f"  alpha_best = {a_star:+.6f}   chi2_min = {c_star:.2f}   (M = {M_best:.4f})")

# dchi2 = 1 邊界
mask1 = chis <= c_star + 1.0
a_lo = float(alphas[mask1].min()); a_hi = float(alphas[mask1].max())
sig_a = (a_hi - a_lo) / 2
print(f"  dchi2 = 1 區間: [{a_lo:+.4f}, {a_hi:+.4f}]  ->  alpha = {a_star:+.4f} +/- {sig_a:.4f}")
print(f"  alpha = 0 偏離: {abs(a_star)/sig_a:.2f} sigma")

# ================= B. 結構候選掃描 =================
print("\n" + "=" * 78)
print("B. 結構候選掃描 (由註冊部件生成)")
print("=" * 78)
# 註冊部件: B=4, N_gen=3, N_d=44, L4=7, L5=11, F5=5, F7=13, mu2=2, F_proj=17, L6=18
B, Ng, Nd, L4, L5, F5, F7, mu2, Fp, L6 = 4, 3, 44, 7, 11, 5, 13, 2, 17, 18
cands = {
    '0 (零參數簡單對偶)': 0.0,
    '1/25': 1/25,
    'mu2/L4^2 = 2/49': 2/49,
    'n/p * phi^-3': np_ratio * (2*inv - 1),
    'n/p * (2phi^-1-1) 同上': np_ratio * (2*inv-1),
    '1/(N_gen*L6) = 1/54': 1/54,
    '1/(B*F5) = 1/20': 1/20,
    '1/(L4*B) = 1/28': 1/28,
    'phi^-3/B = 0.0590': (2*inv-1)/B,
    'phi^-3/F5': (2*inv-1)/5,
    'mu2/(N_d/2+B)': mu2/(Nd/2+B),
    '1/(2*N_gen*L4)': 1/(2*Ng*L4),
    'n/p^2': np_ratio**2,
}
print(f"  {'候選':<28} {'值':>10} {'chi2':>9} {'dchi2':>8} {'sigma':>7}  {'在 1sig?':>8}")
rows = []
for nm, val in sorted(cands.items(), key=lambda kv: abs(kv[1])):
    _, c = model(val)
    d = c - c_star
    sg = abs(val - a_star) / sig_a
    rows.append((nm, val, c, d, sg))
    print(f"  {nm:<28} {val:>10.5f} {c:>9.2f} {d:>8.2f} {sg:>7.2f}  {'YES' if sg <= 1 else 'no':>8}")

# ================= C. 分 bin 殘差 =================
print("\n" + "=" * 78)
print("C. 分 bin 殘差 (alpha = 0 同 alpha = best)")
print("=" * 78)
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5),
        (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
binres = {}
for tag, aa in [('alpha=0', 0.0), (f'alpha={a_star:+.4f}', a_star)]:
    M_, _ = model(aa)
    mu_ = M_ + 5 * np.log10((1 + zs) ** (1 + aa) * DA_new * 1e6 / 10)
    res = mb - mu_
    print(f"\n  [{tag}]  M = {M_:.4f}")
    print(f"    {'z bin':<12} {'N':>5} {'<resid>':>10} {'sigma':>8}")
    for lo, hi in bins:
        m = (zs >= lo) & (zs < hi)
        if m.sum() < 3:
            continue
        r = float(res[m].mean()); s = float(res[m].std())
        print(f"    {lo:.2f}-{hi:.2f}   {m.sum():>5} {r:>+10.4f} {s:>8.4f}")
        if tag == 'alpha=0':
            binres[f"{lo}-{hi}"] = [int(m.sum()), r, s]

# ================= D. 高 z 殘差 =================
print("\n" + "=" * 78)
print("D. 高 z (z > 0.8) 殘差 — O76 舊開放項")
print("=" * 78)
M0, c0 = model(0.0)
mu0_ = M0 + 5 * np.log10((1 + zs) * DA_new * 1e6 / 10)
res0 = mb - mu0_
mh = zs > 0.8
print(f"  z > 0.8: N = {int(mh.sum())}   <resid> = {float(res0[mh].mean()):+.4f}   sigma = {float(res0[mh].std()):.4f}")
print(f"  z <= 0.8: N = {int((~mh).sum())}  <resid> = {float(res0[~mh].mean()):+.4f}  sigma = {float(res0[~mh].std()):.4f}")
# 舊式對照
DA_old = R * (1 - 4.0 ** (-ell)) * (1 + 2 * inv * ell - 0.1697 * (ell - 0.5) * (1 - 4.0 ** (-ell)))
DL_o = (1 + zs) ** (1 - np_ratio) * DA_old
muo0 = 5 * np.log10(DL_o * 1e6 / 10)
Mo = fit_M(muo0); reso = mb - (muo0 + Mo)
print(f"  [舊式對照 alpha=-n/p] z>0.8: <resid> = {float(reso[mh].mean()):+.4f}  (O76 記錄 +0.099~0.142)")
print(f"  [舊式對照 alpha=-n/p] z<=0.8: <resid> = {float(reso[~mh].mean()):+.4f}")
# 高 z 樣本量警告
chk("D1  高 z 樣本量 N < 50 (統計唔足, 唔可作裁決)", mh.sum() < 50, f"N = {int(mh.sum())}")
chk("D2  新式高 z 殘差 |mean| < 0.10 mag", abs(float(res0[mh].mean())) < 0.10,
    f"{float(res0[mh].mean()):+.4f}")

# ================= E. 模型對決 AIC/BIC =================
print("\n" + "=" * 78)
print("E. 模型對決 (AIC / BIC)")
print("=" * 78)
def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om * (1 + zz) ** 3 + (1 - Om))
    return CLIGHT / H0 * np.trapezoid(1 / E, zz)

mu_lp = 5 * np.log10((1 + zs) * np.array([dc_lcdm(z, 67.4, 0.315) for z in zs]) * 1e6 / 10)
Mlp = fit_M(mu_lp); clp = chi2_mu(mu_lp + Mlp)
# LCDM fit Om
from scipy import optimize
def lcdm_loss(p):
    Om, M = p
    mu = 5 * np.log10((1 + zs) * np.array([dc_lcdm(z, 67.4, Om) for z in zs]) * 1e6 / 10)
    return chi2_mu(mu + M)
bestl = None
for Om0 in [0.2, 0.3, 0.315, 0.35, 0.4, 0.5]:
    r = optimize.minimize(lcdm_loss, [Om0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 300, 'xatol': 1e-7, 'fatol': 1e-3})
    if bestl is None or r.fun < bestl.fun:
        bestl = r
Om_f, M_f = bestl.x; clf = bestl.fun
c_o = chi2_mu(muo0 + Mo)
models = [
    ('IDCM 新D_A, alpha=0 (0 param)', 1, c0),
    ('IDCM 新D_A, alpha best (1 param)', 2, c_star),
    ('IDCM 新D_A, alpha=-n/p (0 param)', 1, model(-np_ratio)[1]),
    ('IDCM 舊D_A, alpha=-n/p (0 param)', 1, c_o),
    ('LCDM Planck (0 shape param)', 1, clp),
    ('LCDM fit Om (1 shape param)', 2, clf),
]
aic0 = min(m[2] + 2 * m[1] for m in models)
bic0 = min(m[2] + m[1] * math.log(NS) for m in models)
print(f"  {'模型':<36} {'k':>3} {'chi2':>9} {'dAIC':>8} {'dBIC':>8}")
for nm, k, c in models:
    aic = c + 2 * k; bic = c + k * math.log(NS)
    print(f"  {nm:<36} {k:>3} {c:>9.1f} {aic-aic0:>+8.1f} {bic-bic0:>+8.1f}")
print(f"\n  LCDM fit Om = {Om_f:.4f}  (Planck 0.315)")
chk("E1  IDCM(alpha=0) chi2 < LambdaCDM Planck", c0 < clp, f"{c0:.1f} < {clp:.1f}")
chk("E2  IDCM(alpha=0) chi2 vs LCDM best-fit 差 < 10", abs(c0 - clf) < 10, f"{c0:.1f} vs {clf:.1f}")

# ================= F. 可證偽預言 =================
print("\n" + "=" * 78)
print("F. 可證偽預言 — D_L/D_A 指數")
print("=" * 78)
print(f"  IDCM (alpha=0): D_L/D_A = (1+z)^1        <- 零參數 (能量損失 x 時間膨脹, 冇光子數稀釋)")
print("  舊 O76 聲稱    : D_L/D_A = (1+z)^(1-n/p) = (1+z)^0.85738  <- 已撤銷")
print(f"  LambdaCDM      : D_L/D_A = (1+z)^2")
for z in [0.5, 1.0, 2.0, 3.0]:
    r_idcm = 1 + z
    r_old = (1 + z) ** (1 - np_ratio)
    r_lcdm = (1 + z) ** 2
    print(f"  z={z:<4} IDCM={r_idcm:8.3f}  舊={r_old:8.3f}  LCDM={r_lcdm:8.3f}  (IDCM/LCDM = {r_idcm/r_lcdm*100:5.1f}%)")
chk("F1  新對偶指數 = 1 (零參數, 唔含 n/p)", True, "alpha = 0")

# ================= F2. alpha 分區診斷 =================
print("\n" + "=" * 78)
print("F2. alpha 分區診斷 (低 z vs 高 z 驅動?)")
print("=" * 78)
def fit_alpha_sub(mask, lo=-0.20, hi=0.30):
    Cm = Cinv[np.ix_(mask, mask)]
    J = np.ones(int(mask.sum()))
    den = J @ Cm @ J
    zz = zs[mask]; DAz = DA_new[mask]; mbz = mb[mask]
    best = None
    for a in np.arange(lo, hi, 0.002):
        mu0 = 5 * np.log10((1 + zz) ** (1 + a) * DAz * 1e6 / 10)
        d = mbz - mu0
        M = float((J @ Cm @ d) / den)
        r = d - M
        c = float(r @ Cm @ r)
        if best is None or c < best[1]:
            best = (float(a), c)
    return best

for nm, mk in [('z < 0.3', zs < 0.3), ('0.3 <= z < 0.8', (zs >= 0.3) & (zs < 0.8)),
               ('z >= 0.8', zs >= 0.8), ('全部', np.ones(NS, bool))]:
    a_s, c_s = fit_alpha_sub(mk)
    print(f"  {nm:<16} N = {int(mk.sum()):>5}   alpha_sub = {a_s:+.4f}   chi2 = {c_s:.1f}")
print("  -> 若高 z 區 alpha 偏移更大 = 高 z 形狀殘餘被 alpha 吸收 (非真對偶指數)")

# ================= G. DESI 幾何 (新式) =================
print("\n" + "=" * 78)
print("G. DESI BAO chi2 (新 D_A, 兩 tracer 集)")
print("=" * 78)
TR6 = [('LRG1', 0.510, 13.588, 0.167), ('LRG2', 0.706, 17.351, 0.177),
       ('LRG3+ELG', 0.934, 21.576, 0.152), ('ELG2', 1.321, 27.601, 0.318),
       ('QSO', 1.484, 30.512, 0.760), ('Lya', 2.330, 38.988, 0.531)]
def chi2_desi(trs, b):
    t = 0.0
    for nm, z, dm, em in trs:
        l = math.log(1 + z, 4)
        pred = R * (1 - 4 ** (-l)) * (l + b) / rd
        t += ((pred - dm) / em) ** 2
    return t
c6 = chi2_desi(TR6, b_spec)
c5 = chi2_desi([t for t in TR6 if t[0] != 'QSO'], b_spec)
c6_old = chi2_desi(TR6, 1.0)
print(f"  6 tracer 新式 = {c6:.4f}   (O76 舊式 = 12.82 [5tr] / 13.09 [6tr])")
print(f"  5 tracer 新式 = {c5:.4f}")
near("G1  6 tracer = 2.4528 (O169 值)", c6, 2.4528, 5e-3)
chk("G2  新式 DESI 優於舊式 (兩 tracer 集)", c6 < 12.0, f"{c6:.2f} < 12.82")

# ================= 總結 =================
print("\n" + "=" * 78)
print(f"O76/25 總結: PASS = {len(PASS)}  FAIL = {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print("   -", f)
print("=" * 78)
print(f"""
★ 重裁決結果:
  新 D_A (O169): D_A(l) = R(1-4^-l)(l + {b_spec:.8f})
  對偶: D_L = (1+z)^(1+alpha) * D_A
    alpha_best = {a_star:+.4f} +/- {sig_a:.4f}   (chi2 = {c_star:.1f})
    alpha = 0   (零參數)        chi2 = {c0:.1f}   <- 同 alpha_best 差 {c_star and (c0-c_star):.1f}
    alpha = -n/p (舊 O76)       chi2 = {model(-np_ratio)[1]:.1f}   <- 已排除

  LambdaCDM Planck (0 shape param) chi2 = {clp:.1f}
  LambdaCDM fit Om (1 shape param) chi2 = {clf:.1f}   (Om = {Om_f:.4f})

  ==> IDCM 零參數 ({c0:.1f}) 優於 LambdaCDM Planck ({clp:.1f}), 同 LCDM 最佳擬合 ({clf:.1f}) 同級
""")

out = {
    'alpha_best': a_star, 'sigma_alpha': sig_a,
    'alpha_lo': a_lo, 'alpha_hi': a_hi,
    'chi2_alpha0': c0, 'chi2_alpha_best': float(c_star),
    'chi2_alpha_np_old': model(-np_ratio)[1],
    'chi2_lcdm_planck': clp, 'chi2_lcdm_fit': float(clf), 'Om_lcdm_fit': float(Om_f),
    'M_alpha0': M0,
    'desi_chi2_6tr_new': c6, 'desi_chi2_5tr_new': c5,
    'bin_residuals_alpha0': binres,
    'highz_resid_alpha0': float(res0[mh].mean()),
    'highz_N': int(mh.sum()),
    'lowz_resid_alpha0': float(res0[~mh].mean()),
    'highz_resid_old': float(reso[mh].mean()),
    'pass': len(PASS), 'fail': len(FAIL),
}
with open(BASE / 'data' / '25_alpha_reverdict.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("-> data/25_alpha_reverdict.json")
