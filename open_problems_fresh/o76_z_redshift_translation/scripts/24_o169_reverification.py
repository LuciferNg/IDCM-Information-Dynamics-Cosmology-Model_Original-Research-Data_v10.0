#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O76/24: O169 修正點重驗 — 上游修正交回執行 (第一輪)
================================================================
來源: SESSION_START.md §「O169 修正點 (2026-09-15) — 待本 O 重驗」
角色: 交回任務執行記錄。狀態 [ ] -> [x]。

上游修正內容 (O169, 2026-09-15):
  【已證偽】E_OLD(l) = 1 + 2*phi^-1*l            (DESI DR2 D_M x6 排除 4.88 sigma)
  【新零參數】E_NEW(l) = <gamma>_odd/2 * l + 1/<v_g>_{1..22} = l + 1.11911398
  【δ 新身份】δ(l) = -phi^-3 (l - 1/2),  C = 1 - 2*phi^-1 = -(sqrt5 - 2) = -0.23606798 (EXACT)
  【舊補丁】C_D = -0.1697 (O51/82) 已證偽: 形狀啱但 (i) (1-4^-l) 因子多餘 (ii) 係數差 39%

本腳本 (A-F 段, 全部獨立重算, mpmath dps=40, 唔 import O169 任何腳本):
  A. O169 恆等式獨立重算 (10 項)
  B. DESI BAO chi2 三式對照 (6 D_M tracer)
  C. Nyquist 比: O76 舊「0.9990 自洽」 vs 新值
  D. Pantheon+ 1701 SNe 用新 D_A 重跑 + alpha 重 fit
  E. z_eff 指數: 2*phi^-1/ln4 -> 1/ln4
  F. 影響評估表 (O76 邊啲結論站得住 / 邊啲要改)
"""
import json, math
from pathlib import Path
import mpmath as mpm

mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent          # o76_.../
ROOT = BASE.parent                                      # open_problems_fresh/

PASS = []
FAIL = []
def chk(name, cond, computed=None, docval=None, tol=None, unit=''):
    ok = bool(cond)
    (PASS if ok else FAIL).append(name)
    s = f"  {'[OK]' if ok else '[FAIL]'} {name}"
    if computed is not None:
        s += f"   computed={computed}"
        if docval is not None:
            s += f"  doc={docval}"
        if unit:
            s += f" {unit}"
    print(s)

def near(name, computed, docval, tol, unit=''):
    d = abs(mp.mpf(computed) - mp.mpf(docval))
    chk(name, d <= mp.mpf(tol), mp.nstr(computed, 14), docval, tol, unit)

print("=" * 78)
print("O76/24 - O169 修正點重驗 (上游修正交回)")
print("=" * 78)

# ================= 結構常數 =================
R   = mp.mpf('4129.94')
phi = (1 + mp.sqrt(5)) / 2
inv = 1 / phi
pi  = mp.pi
N   = 44
gam = {n: 4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N + 1)}
vg  = {n: mp.cos(pi * n / 88) for n in range(1, N + 1)}
rd  = pi * R / 88 * mp.mpf(420) / 421
L6, Fp = 18, 17
l_nyq = mp.log(L6, 4)

def ell(z):
    return mp.log(1 + mp.mpf(z), 4)

def DA_old(l):                      # O76 原式 (C_D = -0.1697)
    return R * (1 - 4 ** (-l)) * (1 + 2 * inv * l
                                  - mp.mpf('0.1697') * (l - mp.mpf('0.5')) * (1 - 4 ** (-l)))

def DA_new(l, b=None):
    if b is None:
        b = b_spec
    return R * (1 - 4 ** (-l)) * (l + b)

b_spec = 22 / mp.fsum(vg[n] for n in range(1, 23))

print(f"\n  R = {R} Mpc | rd = {mp.nstr(rd, 12)} | l_nyq = log4(18) = {mp.nstr(l_nyq, 12)}")
print(f"  b_spec = 22/Sum_{{1..22}} cos(pi n/88) = {mp.nstr(b_spec, 14)}")

# ================= A. O169 恆等式獨立重算 =================
print("\n" + "=" * 78)
print("A. O169 恆等式獨立重算 (mpmath dps=40)")
print("=" * 78)

# A1  phi^-3 = sqrt5 - 2 = 2*phi^-1 - 1
a1 = inv ** 3
near("A1  phi^-3 = sqrt5 - 2", a1, mp.sqrt(5) - 2, '1e-35')
near("A1b phi^-3 = 2*phi^-1 - 1", a1, 2 * inv - 1, '1e-35')
# A2  C = 1 - 2 phi^-1 = -phi^-3
C_new = 1 - 2 * inv
near("A2  C = 1 - 2*phi^-1", C_new, -a1, '1e-35')
near("A2b C = -(sqrt5 - 2) = -0.23606798", C_new, '-0.2360679774997896964', '1e-18')
# A3  2 phi^-1 - phi^-3 = 1
near("A3  2*phi^-1 - phi^-3 = 1", 2 * inv - a1, 1, '1e-35')
# A4  sqrt5/2 = 1/2 + phi^-1 = 1 + phi^-3/2
near("A4  sqrt5/2 = 1/2 + phi^-1", mp.sqrt(5) / 2, mp.mpf('0.5') + inv, '1e-35')
near("A4b sqrt5/2 = 1 + phi^-3/2", mp.sqrt(5) / 2, 1 + a1 / 2, '1e-35')
# A5  Sum gamma: total / odd / even
S_all = mp.fsum(gam[n] for n in range(1, N + 1))
S_odd = mp.fsum(gam[n] for n in range(1, N + 1) if n % 2 == 1)
S_eve = mp.fsum(gam[n] for n in range(1, N + 1) if n % 2 == 0)
near("A5  Sum gamma = 90", S_all, 90, '1e-30')
near("A5b Sum gamma_odd = 44 = N_d", S_odd, 44, '1e-30')
near("A5c Sum gamma_even = 46", S_eve, 46, '1e-30')
near("A5d Sum_even - Sum_odd = gamma_22 = 2", S_eve - S_odd, gam[22], '1e-30')
# A6  <gamma>_odd = 2 = mu^2 = gamma_22 ; v_g(22) = 1/sqrt2
n_odd = len([n for n in range(1, N + 1) if n % 2 == 1])
near("A6  <gamma>_odd = 44/22 = 2", S_odd / n_odd, 2, '1e-30')
near("A6b gamma_22 = mu^2 = 2", gam[22], 2, '1e-30')
near("A6c v_g(22) = 1/sqrt2", vg[22], 1 / mp.sqrt(2), '1e-35')
# A7  Z2: gamma_n + gamma_{44-n} = 4
dev7 = max(abs(gam[n] + gam[N - n] - 4) for n in range(1, N))
chk("A7  Z2: gamma_n + gamma_{44-n} = 4 (max dev)", dev7 < mp.mpf('1e-38'),
    mp.nstr(dev7, 4))
# A8  a = <gamma>_odd / 2 = 1  (斜率)
a_slope = (S_odd / n_odd) / 2
near("A8  a = <gamma>_odd/2 = 1 (斜率 EXACT)", a_slope, 1, '1e-30')
near("A8b a = mu^2/2", a_slope, gam[22] / 2, '1e-30')
# A9  <v_g> closed form
cf = mp.sin(pi / 8) * mp.cos(23 * pi / 176) / (22 * mp.sin(pi / 176))
near("A9  <v_g> closed form = 0.8935640302", cf, '0.8935640302', '1e-10')
near("A9b <v_g> = b_spec^-1", 1 / b_spec, cf, '1e-30')
# A10 E_new(1/2) vs phi (兩種讀法)
near("A10 E_spec(1/2) = 0.5 + 1.11911398", mp.mpf('0.5') + b_spec, '1.61911398', '1e-8')
near("A10b E_phi(1/2) = 0.5 + sqrt5/2 = phi EXACT", mp.mpf('0.5') + mp.sqrt(5) / 2, phi, '1e-35')
# A11 O169 數值 b (譜讀法) vs phi 讀法 簡併
dev11 = abs(b_spec - mp.sqrt(5) / 2) / b_spec * 100
near("A11 b_spec vs sqrt5/2 dev = 0.0966%", dev11, '0.0966', '5e-4', '%')

# ================= B. DESI BAO chi2 三式對照 =================
print("\n" + "=" * 78)
print("B. DESI BAO chi2(D_M x6) 三式對照")
print("=" * 78)
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3+ELG', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]

def chi2_DM(DAfun):
    t = mp.mpf(0); sig = []
    for nm, z, dm, em in TR:
        l = ell(z)
        s = (DAfun(l) / rd - mp.mpf(dm)) / mp.mpf(em)
        sig.append(float(s)); t += s * s
    return t, sig

def E_old_only(l):
    return R * (1 - 4 ** (-l)) * (1 + 2 * inv * l)

def E_old_delta(l):
    return DA_old(l)

c_old, s_old = chi2_DM(E_old_only)
c_oldd, s_oldd = chi2_DM(E_old_delta)
c_new, s_new = chi2_DM(DA_new)
print(f"  OLD      E = 1+2 phi^-1 l        chi2 = {mp.nstr(c_old, 8)}   sigma = {[round(x,2) for x in s_old]}")
print(f"  OLD+del  C_D = -0.1697           chi2 = {mp.nstr(c_oldd, 8)}   sigma = {[round(x,2) for x in s_oldd]}")
print(f"  NEW      E = l + 1.11911398      chi2 = {mp.nstr(c_new, 8)}   sigma = {[round(x,2) for x in s_new]}")
near("B1  OLD chi2 = 27.1635 (O169 值)", c_old, '27.1635', '5e-3')
near("B2  OLD+delta chi2 = 13.0888 (O169 值)", c_oldd, '13.0888', '5e-3')
near("B3  NEW chi2 = 2.4528 (O169 值)", c_new, '2.4528', '5e-3')
chk("B4  NEW |sigma|max <= 1.0", max(abs(x) for x in s_new) <= 1.0,
    f"max = {max(abs(x) for x in s_new):.3f}")
chk("B5  NEW 改善 O76 舊式 (C_D=-0.1697)", c_new < c_oldd,
    f"chi2 {mp.nstr(c_new,6)} < {mp.nstr(c_oldd,6)}")

# O76 原用 5 tracer (缺 QSO) - 重現舊值作對照
TR5 = [t for t in TR if t[0] != 'QSO']
def chi2_5(DAfun):
    t = mp.mpf(0)
    for nm, z, dm, em in TR5:
        t += ((DAfun(ell(z)) / rd - mp.mpf(dm)) / mp.mpf(em)) ** 2
    return t
c_new5 = chi2_5(DA_new)
c_old5 = chi2_5(E_old_delta)
print(f"  [5-tracer, O76 原用集] OLD+del = {mp.nstr(c_old5,8)}   NEW = {mp.nstr(c_new5,8)}")
near("B6  O76 5-tracer 舊值 = 12.82", c_old5, '12.82', '2e-2')

# ================= C. Nyquist 比 =================
print("\n" + "=" * 78)
print("C. Nyquist 比 (環幾何上界)")
print("=" * 78)
r_old = DA_old(l_nyq) / (pi * R)
r_new = DA_new(l_nyq) / (pi * R)
print(f"  O76 舊: D_A(l_nyq) = {mp.nstr(DA_old(l_nyq), 8)} Mpc = {mp.nstr(r_old, 6)} piR")
print(f"  新式  : D_A(l_nyq) = {mp.nstr(DA_new(l_nyq), 8)} Mpc = {mp.nstr(r_new, 6)} piR")
near("C1  O76 舊值 0.9990", r_old, '0.9990', '5e-4')
near("C2  新值 = 0.9632 piR (O169 docs/04)", r_new, '0.9632', '5e-4')
chk("C3  新式滿足環幾何上界 D_A(l_nyq) < piR", DA_new(l_nyq) < pi * R,
    f"餘 {float((1-r_new)*100):.2f}%")
# 飽和點
try:
    l_sat = mp.findroot(lambda l: DA_new(l) - pi * R, mp.mpf('2.3'))
    print(f"  新式飽和點 l_sat = {mp.nstr(l_sat, 8)}  (z = {mp.nstr(4**l_sat - 1, 6)})")
    chk("C4  飽和點 l_sat > l_nyq (唔喺觀測域內)", l_sat > l_nyq,
        f"l_sat = {mp.nstr(l_sat,6)} > {mp.nstr(l_nyq,6)}")
except Exception as e:
    chk("C4  飽和點求解", False, str(e))

# ================= D. Pantheon+ 1701 SNe 重跑 =================
print("\n" + "=" * 78)
print("D. Pantheon+ 1701 SNe 用新 D_A 重跑 + alpha 重 fit")
print("=" * 78)
import numpy as np
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
chk("D0  1701 SNe 載入", NS == 1701, f"N = {NS}")

ell_np = np.log(1 + zs) / np.log(4)
base_np = R_float = 4129.94
def DA_np(l, b):
    return base_np * (1 - 4.0 ** (-l)) * (l + b)
def DA_np_old(l):
    return base_np * (1 - 4.0 ** (-l)) * (1 + 2 * 0.6180339887498949 * l
                                          - 0.1697 * (l - 0.5) * (1 - 4.0 ** (-l)))

def fit_M(mu_model):
    J = np.ones(NS)
    return float((J @ Cinv @ (mb - mu_model)) / (J @ Cinv @ J))

def chi2_of(mu_model):
    r = mb - mu_model
    return float(r @ Cinv @ r)

def run(DAfun, alpha):
    DA = DAfun(ell_np)
    DL = (1 + zs) ** (1 + alpha) * DA
    mu0 = 5 * np.log10(DL * 1e6 / 10)
    M = fit_M(mu0)
    return M, chi2_of(mu0 + M)

b_float = float(b_spec)
# 舊式 + 舊 alpha
M_old0, c_old0 = run(DA_np_old, 0.0)
M_old_a, c_old_a = run(DA_np_old, -float(0.142618))
# 新式 + alpha = 0
M_new0, c_new0 = run(lambda l: DA_np(l, b_float), 0.0)
print(f"  [舊 D_A, alpha=0        ] M = {M_old0:.4f}  chi2 = {c_old0:.1f}")
print(f"  [舊 D_A, alpha=-n/p     ] M = {M_old_a:.4f}  chi2 = {c_old_a:.1f}")
print(f"  [新 D_A, alpha=0        ] M = {M_new0:.4f}  chi2 = {c_new0:.1f}")

# 新 D_A 下重 fit alpha (numpy, 粗掃 + 細掃)
best = None
for a in np.arange(-0.40, 0.21, 0.002):
    M_, c_ = run(lambda l: DA_np(l, b_float), a)
    if best is None or c_ < best[1]:
        best = (a, c_, M_)
alpha_new, chi2_new_alpha, M_new_a = best
print(f"  [新 D_A, alpha 重 fit   ] alpha = {alpha_new:+.4f}  M = {M_new_a:.4f}  chi2 = {chi2_new_alpha:.1f}")

# LambdaCDM 對照
CLIGHT = 299792.458
def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om * (1 + zz) ** 3 + (1 - Om))
    return CLIGHT / H0 * np.trapezoid(1 / E, zz)
mu_l = 5 * np.log10((1 + zs) * np.array([dc_lcdm(zi, 67.4, 0.315) for zi in zs]) * 1e6 / 10)
M_l = fit_M(mu_l); c_l = chi2_of(mu_l + M_l)
print(f"  [LambdaCDM Planck       ] M = {M_l:.4f}  chi2 = {c_l:.1f}")

near("D1  舊式 alpha=-n/p chi2 = 2006.8 (O76 記錄)", c_old_a, '2006.8', '1.0')
near("D2  LambdaCDM chi2 = 2002.1 (O76 記錄)", c_l, '2002.1', '1.0')
print(f"  delta chi2 (新式 alpha=0 vs LambdaCDM) = {c_new0 - c_l:+.1f}")
print(f"  delta chi2 (新式 重fit  vs LambdaCDM) = {chi2_new_alpha - c_l:+.1f}")

# n/p 對照
g7 = 4 * math.sin(7 * math.pi / 88) ** 2
g20 = 4 * math.sin(20 * math.pi / 88) ** 2
np_ratio = g7 / g20
print(f"  n/p = gamma_7/gamma_20 = {np_ratio:.6f}")
c_np = run(lambda l: DA_np(l, b_float), -np_ratio)[1]
print(f"  [新 D_A, alpha=-n/p     ] chi2 = {c_np:.1f}")
chk("D3  ★發現: 新 D_A 下 alpha=-n/p 已被排除 (舊 alpha 係補償錯誤 D_A)",
    c_np - chi2_new_alpha > 20.0, f"delta chi2 = {c_np - chi2_new_alpha:+.2f}")

# 分 bin 殘差 (新式, alpha=-n/p)
DA_use = DA_np(ell_np, b_float)
mu_use = 5 * np.log10((1 + zs) ** (1 - np_ratio) * DA_use * 1e6 / 10)
M_use = fit_M(mu_use)
resid = mb - (mu_use + M_use)
print("\n  分 bin 殘差 (新 D_A, alpha=-n/p):")
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
bin_res = {}
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3:
        continue
    r = float(resid[m].mean())
    bin_res[f"{lo}-{hi}"] = (int(m.sum()), r)
    print(f"    {lo:.2f}-{hi:.2f}: N={m.sum():<4} <resid> = {r:+.4f}")

# ================= E. z_eff 指數 =================
print("\n" + "=" * 78)
print("E. z_eff 指數 (低 z Hubble 律)")
print("=" * 78)
p_old = 2 * inv / mp.log(4)
p_new = 1 / mp.log(4)
print(f"  舊 (E = 1 + 2 phi^-1 l): 指數 = 2 phi^-1 / ln4 = {mp.nstr(p_old, 8)}")
print(f"  新 (E = l + b)         : 指數 = 1 / ln4        = {mp.nstr(p_new, 8)}")
near("E1  舊指數 = 0.891635 (data/01 p 值)", p_old, '0.891635', '1e-6')
near("E2  新指數 = 1/ln4 = 0.72135", p_new, '0.7213475', '1e-6')

# ================= F. 影響評估 =================
print("\n" + "=" * 78)
print("F. 影響評估 (O76 結論逐項)")
print("=" * 78)
print("""
  # | O76 原結論                          | 修正後                        | 判定
  --+-------------------------------------+-------------------------------+--------
  1 | E = 1 + 2 phi^-1 l (伸長律)         | E = l + 1.11911398            | 換新 (上游)
  2 | C_D = -0.1697 (群延遲權重)          | C = -phi^-3 = -0.23606798     | 換新 (上游)
  3 | Nyquist 自洽 0.9990 piR             | 0.9632 piR (係 delta 調出)     | 降級 (非獨立檢驗)
  4 | z_eff 指數 0.891635                 | 0.7213475 (= 1/ln4)           | 換新
  5 | D_L = (1+z)^(1-n/p) * D_A           | 同形式, alpha 需重 fit         | 重驗
  6 | Pantheon+ chi2 = 2006.8 (alpha=-n/p)| 見 D 段                       | 重驗
  7 | DESI 5-tracer chi2 = 12.82          | 見 B 段                       | 重驗
  8 | time dilation = (1+z)               | 不變 (機制 B)                  | 不變
  9 | 可證偽 D_L/D_A = (1+z)^0.857        | 指數 = 1-n/p 仍成立, 值待重算    | 重驗
""")

# ================= 總結 =================
print("=" * 78)
print(f"O76/24 總結: PASS = {len(PASS)}  FAIL = {len(FAIL)}")
if FAIL:
    print("FAIL 項:")
    for f in FAIL:
        print("   -", f)
print("=" * 78)

out = {
    'o169_b_spec': float(b_spec),
    'o169_C_new': float(C_new),
    'o169_S_odd': float(S_odd),
    'o169_a_slope': float(a_slope),
    'desi_chi2_old': float(c_old),
    'desi_chi2_old_delta': float(c_oldd),
    'desi_chi2_new': float(c_new),
    'desi_chi2_old_5tr': float(c_old5),
    'desi_chi2_new_5tr': float(c_new5),
    'nyquist_ratio_old': float(r_old),
    'nyquist_ratio_new': float(r_new),
    'sn_chi2_old_alpha_np': float(c_old_a),
    'sn_chi2_new_alpha0': float(c_new0),
    'sn_chi2_new_alpha_fit': float(chi2_new_alpha),
    'sn_alpha_new_fit': float(alpha_new),
    'sn_chi2_new_alpha_np': float(c_np),
    'sn_chi2_lcdm': float(c_l),
    'z_eff_exp_old': float(p_old),
    'z_eff_exp_new': float(p_new),
    'bin_residuals': {k: [v[0], v[1]] for k, v in bin_res.items()},
    'pass': len(PASS), 'fail': len(FAIL),
}
with open(BASE / 'data' / '24_o169_reverification.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"-> data/24_o169_reverification.json")
