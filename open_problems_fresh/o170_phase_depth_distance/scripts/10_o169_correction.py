#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/10 — O169 修正交回: 用新橫向律重驗徑向結論

背景 (O169 docs/01-02, SESSION_START §③ 交回任務):
  舊伸長律 E_OLD = 1 + 2*phi^-1 * ell  被 DESI DR2 D_M x6 排除 4.88 sigma
  新零參數律 E_new = <gamma>_odd/2 * ell + 1/<v_g>_{1..22} = ell + 1.11911398
  delta(ell) = -phi^-3 (ell - 1/2)   (冇 (1-4^-ell) 因子)
  舊 C_D = -0.1697 (O51/82 補丁) 已證偽

本腳本:
  T1  O169 恆等式重驗 (T1-T8)
  T2  M(ell) 表 (獨立於橫向律, 應不變) — 核對
  T3  4 個徑向定律 x 新橫向律 -> 2D 聯合 chi2 (含 rho)
  T4  piR 飽和張力 (O169 docs/04 O3) 用新律重算
  T5  O169 交回 checklist 逐項核對
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf("4129.94")
rd = mp.pi * R / 88 * mp.mpf(420) / 421      # = 147.088303 (O169 結構 r_d)
ln4 = mp.log(4)
B = 4
Ngen = 3
N_d = 44
ell_t = mp.log(Ngen, 4)
c_km = mp.mpf("299792.458")

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

def ell(z):
    return mp.log(1 + mp.mpf(str(z)), 4)

print("=" * 100)
print("O170 scripts/10 — O169 修正交回重驗 (新橫向律 E = ell + 1/<v_g>_{1..22})")
print("=" * 100)
print(f"R_world = {R} Mpc   r_d = piR/88 * 420/421 = {mp.nstr(rd, 12)} Mpc   ln4 = {mp.nstr(ln4, 12)}")

# ---------------- T1: O169 恆等式 ----------------
print("\n--- T1: O169 恆等式 (docs/02 §七 T1-T8) ---")
chk("T1  2*phi^-1 - phi^-3 = 1 (EXACT)", abs(2/phi - phi**-3 - 1) < mp.mpf("1e-35"))
chk("T2  sqrt5/2 = 1/2 + phi^-1 = 1 + phi^-3/2 (EXACT)", abs(mp.sqrt(5)/2 - (1 + phi**-3/2)) < mp.mpf("1e-35"))
chk("T3  1/2 = log_4(2) (EXACT)", abs(mp.log(2, 4) - mp.mpf("0.5")) < mp.mpf("1e-35"))

# gamma_n = 4 sin^2(pi n/88), n=1..44
gam = [4*mp.sin(mp.pi*n/88)**2 for n in range(1, 45)]
S_all = sum(gam)
S_even = sum(gam[n] for n in range(44) if (n+1) % 2 == 0)
S_odd = sum(gam[n] for n in range(44) if (n+1) % 2 == 1)
chk(f"T5  Sigma_gamma = 90 ({mp.nstr(S_all,10)}), even = 46 ({mp.nstr(S_even,10)}), odd = 44 ({mp.nstr(S_odd,10)})",
    abs(S_all-90) < mp.mpf("1e-30") and abs(S_even-46) < mp.mpf("1e-30") and abs(S_odd-44) < mp.mpf("1e-30"))
chk("T5b <gamma>_odd = 2 = mu^2 -> a = <gamma>_odd/2 = 1 EXACT", abs(S_odd/22 - 2) < mp.mpf("1e-30"))
z2max = max(abs(gam[n-1] + gam[44-n-1] - 4) for n in range(1, 23))
chk(f"T6  Z2: gamma_n + gamma_(44-n) = 4 (max dev {mp.nstr(z2max,3)})", z2max < mp.mpf("1e-35"))
chk("T6b gamma_22 = 2 = mu^2, v_g(22) = 1/sqrt2", abs(gam[21]-2) < mp.mpf("1e-35") and abs(mp.cos(mp.pi*22/88) - 1/mp.sqrt(2)) < mp.mpf("1e-35"))

# 截距 b = 1/<v_g>_{1..22}
Svg22 = sum(mp.cos(mp.pi*n/88) for n in range(1, 23))
b_new = 22 / Svg22
chk(f"T-b  b = 22/Sigma cos(pi n/88) = {mp.nstr(b_new, 12)} (=1.11911398)", abs(b_new - mp.mpf("1.11911398")) < mp.mpf("1e-8"))
chk("T7  E(1/2) = phi (sqrt5/2 讀法, 0.097% 簡併)", abs((mp.mpf("0.5") + mp.sqrt(5)/2) - phi) < mp.mpf("1e-6"))
C_new = 1 - 2/phi
chk(f"T4  C = 1 - 2*phi^-1 = -phi^-3 = -(sqrt5-2) = {mp.nstr(C_new,12)}", abs(C_new + phi**-3) < mp.mpf("1e-35"))

# ---------------- T2: M(ell) 表 ----------------
print("\n--- T2: M(ell) 表 (M = D_H*(1+z)*ln4/R_world; 唔依賴橫向律) ---")
# (name, z, D_M/rd, s_M, D_H/rd, s_H, rho, role)
DATA = [
    ('LRG1',      0.510, 13.588, 0.167, 21.863, 0.425, -0.459, 'cosmo'),
    ('LRG2',      0.706, 17.351, 0.177, 19.455, 0.330, -0.404, 'cosmo'),
    ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416, 'cosmo'),
    ('ELG2',      1.321, 27.601, 0.318, 14.176, 0.221, -0.434, 'cosmo'),
    ('QSO',       1.484, 30.512, 0.760, 12.817, 0.516, -0.500, 'cosmo'),
    ('Lyalpha',   2.330, 38.988, 0.531,  8.632, 0.101, -0.431, 'cosmo'),
    ('LRG3',      0.922, 21.648, 0.178, 17.577, 0.213, -0.406, 'valid'),
    ('ELG1',      0.955, 21.707, 0.335, 17.803, 0.297, -0.462, 'valid'),
]
rows = []
print(f"{'tracer':<11} {'z':<7} {'ell':<8} {'D_H/rd':<9} {'M':<9} {'sM':<8}")
for name, z, dm, sm, dh, sh, rho, role in DATA:
    e = ell(z)
    M = mp.mpf(str(dh)) * rd * (1 + mp.mpf(str(z))) * ln4 / R
    sM = mp.mpf(str(sh)) * rd * (1 + mp.mpf(str(z))) * ln4 / R
    rows.append(dict(name=name, z=z, e=e, dm=dm, sm=sm, dh=dh, sh=sh, rho=rho, role=role, M=M, sM=sM))
    print(f"{name:<11} {z:<7.3f} {float(e):<8.4f} {dh:<9.3f} {float(M):<9.4f} {float(sM):<8.4f}")
chk("T2a LRG1 M = 1.6300 (O167 scripts/12 值 1.630) ✓",
    abs(rows[0]['M'] - mp.mpf("1.6300")) < mp.mpf("0.001"))
chk("T2b Lyalpha M = 1.4192 -> sqrt2 (0.30 sigma)",
    abs((rows[5]['M'] - mp.sqrt(2))/rows[5]['sM']) < 1)

# ---------------- 橫向律 ----------------
def D_M_old(z):
    """O169 證偽: E_OLD = 1 + 2 phi^-1 ell, 加 O51/82 補丁 C_D"""
    e = ell(z); x = 4**(-e)
    C_D = mp.mpf("-0.1697")
    return R*(1-x)*(1 + 2*phi**-1*e + C_D*(e-mp.mpf("0.5"))*(1-x))

def D_M_new(z):
    """O169 新零參數: E = ell + 1/<v_g>_{1..22}"""
    e = ell(z)
    return R*(1 - 4**(-e))*(e + b_new)

def D_M_phi(z):
    """φ-代數影子: E = ell + sqrt5/2 (簡併 0.097%)"""
    e = ell(z)
    return R*(1 - 4**(-e))*(e + mp.sqrt(5)/2)

print("\n--- T3: 橫向律 D_M/rd 逐項殘餘 ---")
for tag, fn in [("OLD+CD (C=-0.1697)", D_M_old), ("NEW (ell+1.11911)", D_M_new), ("NEW-phi (ell+sqrt5/2)", D_M_phi)]:
    chi = mp.mpf(0); ss = []
    for r in rows:
        if r['role'] != 'cosmo':
            continue
        p = fn(r['z'])/rd
        d = (p - mp.mpf(str(r['dm'])))/mp.mpf(str(r['sm']))
        chi += d**2; ss.append(f"{r['name'][:5]}{float(d):+.2f}")
    print(f"  {tag:<22} chi2(D_M) = {float(chi):7.3f}/6   " + " ".join(ss))

# ---------------- T3: 徑向核候選 ----------------
print("\n--- T3b: 徑向核候選 (零參數) ---")
M_sh_sec = mp.sec(mp.mpf("25.5")*mp.pi/88)
M_arch = lambda e: mp.sec(mp.pi*(mp.mpf(N_d)/2 + B*mp.sin(mp.pi*e))/88)
M_step = lambda e: M_sh_sec if e < ell_t else mp.sqrt(2)
M_step25 = lambda e: M_sh_sec                      # 無過渡 (對照)
M_phi = lambda e: phi if e < ell_t else mp.sqrt(2)
M_arch_cut = lambda e: (mp.sec(mp.pi*(mp.mpf(N_d)/2 + B*mp.sin(mp.pi*e))/88) if e < ell_t else mp.sqrt(2))

CAND = [
    ("arch  n_c = 22+4sin(pi*ell)", M_arch),
    ("arch + hard cut @ell_t", M_arch_cut),
    ("step  25.5 | sqrt2 @log4(3)", M_step),
    ("step  phi | sqrt2 @log4(3)", M_phi),
    ("const sec(25.5pi/88)", M_step25),
    ("const sqrt2", lambda e: mp.sqrt(2)),
    ("const phi", lambda e: phi),
]

def chi2_DM(fn):
    c = mp.mpf(0)
    for r in rows:
        if r['role'] != 'cosmo':
            continue
        c += ((fn(r['z'])/rd - mp.mpf(str(r['dm'])))/mp.mpf(str(r['sm'])))**2
    return c

def chi2_DH(fn):
    c = mp.mpf(0); out = []
    for r in rows:
        if r['role'] != 'cosmo':
            continue
        d = (r['M'] - fn(r['e']))/r['sM']
        c += d**2; out.append((r['name'], float(d)))
    return c, out

def chi2_joint(fn):
    """2D 聯合, 含 rho; D_M 用 O169 新律"""
    c = mp.mpf(0)
    for r in rows:
        if r['role'] != 'cosmo':
            continue
        pm = D_M_new(r['z'])/rd
        ph = fn(r['e'])*R/((1 + mp.mpf(str(r['z'])))*ln4)/rd
        d1 = pm - mp.mpf(str(r['dm'])); d2 = ph - mp.mpf(str(r['dh']))
        e1 = mp.mpf(str(r['sm'])); e2 = mp.mpf(str(r['sh'])); ro = mp.mpf(str(r['rho']))
        cov = e1*e2*ro; det = e1**2*e2**2 - cov**2
        c += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
    return c

print(f"  {'candidate':<30} {'chi2_DH/6':>10} {'max|s|':>8} {'chi2_joint/12':>14}  逐項 sigma")
for nm, fn in CAND:
    cdh, out = chi2_DH(fn)
    mx = max(abs(d) for _, d in out)
    cj = chi2_joint(fn)
    ss = " ".join(f"{n[:5]}{d:+.2f}" for n, d in out)
    print(f"  {nm:<30} {float(cdh):10.3f} {float(mx):8.2f} {float(cj):14.3f}  {ss}")

chi_dm_new = chi2_DM(D_M_new)
print(f"\n  [ref] chi2(D_M) NEW = {float(chi_dm_new):.3f}/6 (橫向律自身)")

# ---------------- T4: piR 飽和 ----------------
print("\n--- T4: piR 飽和張力 (O169 docs/04 O3) ---")
ell_nyq = mp.log(18, 4)
print(f"  ell_nyq = log_4(18) = {mp.nstr(ell_nyq, 8)};  pi*R = {mp.nstr(mp.pi*R, 10)} Mpc")
for tag, fn in [("NEW (ell+b)", D_M_new), ("arch", lambda z: R*(1-4**(-ell(z)))*(ell(z) + b_new))]:
    val = fn(mp.mpf("17"))   # z -> large, 4^-ell -> 0
    print(f"  {tag:<12} D_M(z->inf) = {float(val/R):.4f} piR" if False else
          f"  {tag:<12} D_M(z->inf) = {mp.nstr(val/R, 8)} R = {mp.nstr(val/(mp.pi*R), 8)} piR")

# ---------------- T5: 交回 checklist ----------------
print("\n--- T5: O169 交回 checklist (SESSION_START §③) ---")
print("  1. C_D -> delta=-phi^-3(ell-1/2): 本 O 舊 scripts 01-09 用舊 C_D;")
print("     修正後重驗結果 = 本腳本 T3 (橫向部分), 徑向核 T3b")
print("  2. kernel 掃描加 O169 baseline (a=1, b=1/<v_g>_{1..22}) 作對照: T3 已列 NEW")
print("  3. D_H 六 tracer <1 sigma 判準 + ell->1 收斂 sqrt2: T3b 逐項 sigma 已列")
print("  4. 唔重複 O117 partial trace 推導: ✓ (本 O 只做徑向本徵映射)")
d_half = abs((rows[0]['M'] - M_arch(rows[0]['e']))/rows[0]['sM'])
chk("T5b 新 arch 核 LRG1 |sigma| < 1", d_half < 1)
chk("T5c 新 arch 核 Lyalpha |sigma| < 1",
    abs((rows[5]['M'] - M_arch(rows[5]['e']))/rows[5]['sM']) < 1)

# ---------------- T6: H0 由 M(0) ----------------
print("\n--- T6: H0 由徑向核 z->0 斜率 ---")
for tag, m0 in [("step 25.5 (M(0)=1.63007)", M_sh_sec), ("arch (M(0)=sqrt2)", mp.sqrt(2)),
                ("const ln4 (M(0)=ln4)", ln4), ("const phi", phi)]:
    H0 = c_km*ln4/(R*m0)
    print(f"  {tag:<26} H0_eff = c*ln4/(R*M(0)) = {float(H0):7.3f} km/s/Mpc"
          f"   (SH0ES 73.0+-1.0 -> {float((H0-73.0)/1.0):+.2f} sigma; Planck 67.4+-0.5 -> {float((H0-67.4)/0.5):+.2f} sigma)")

print("\n" + "=" * 100)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("=" * 100)
