#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/11 (v2) — O1 攻堅: 徑向載波 n_c(ell) 存活判據

⚠️ v1 bug: mk_arch 用 sin(pi*e/P), P=2 時實際 = sin(pi*ell/2) (arch 寬度 2 levels),
   同 mpmath 核對段 (sin(pi*ell)) 唔一致 -> 兩段數字矛盾。v2 統一: arch 寬度 W (單位: level)。

結構形式 (候選):
    n_c(ell) = N_d/2 + B*sin(pi*ell/W)      ell < ell_t
    n_c(ell) = N_d/2                        ell >= ell_t = log4(N_gen)
    M(ell)   = sec(pi*n_c/88) = 1/v_g(n_c)

判據 (scripts/10):
    - 深極限 n_c -> 22 = N_d/2 (Z2 自對偶中心模), M -> sqrt2  [Lyalpha 0.30 sigma 最緊]
    - 淺區非單調, 峰值 M ~ 1.67 @ ell ~ 0.5  -> n_c 峰值 ~ 26 = N_d/2 + B
    - H0: M(0) 必須 ~ ln4..sqrt2 (step M(0)=1.63 -> H0=61.7, 被 SH0ES 排除 11 sigma)

測試:
  A  自由 3 參數擬合 (A, W, ell_t) -> 結構值 (A=B=4, W=1, ell_t=log4 3) 係咪被數據選出?
  B  結構參數掃描
  C  零參數形式比較
  D  8 點 (含獨立驗證 tracer)
  E  BGS D_V
  F  過渡連續性診斷
  G  H0 + 低 ell 行為
  H  mpmath 40dps 獨立核對 (float vs mpmath 一致性)
"""
import math
import mpmath as mp
mp.mp.dps = 40

PI = math.pi
LN4 = math.log(4.0)
R = 4129.94
RD = PI * R / 88 * 420 / 421
B = 4
NGEN = 3
ND = 44
ELL_T0 = math.log(3.0, 4.0)
SQ2 = math.sqrt(2.0)
PHI = (1 + math.sqrt(5)) / 2
C_KM = 299792.458

def ell(z):
    return math.log1p(z)/LN4

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
for name, z, dm, sm, dh, sh, rho, role in DATA:
    e = ell(z)
    k = RD*(1 + z)*LN4/R
    rows.append(dict(name=name, z=z, e=e, dm=dm, sm=sm, dh=dh, sh=sh, rho=rho,
                     role=role, M=dh*k, sM=sh*k))

B_NEW = 22/sum(math.cos(PI*n/88) for n in range(1, 23))

def D_M_new(z):
    e = ell(z)
    return R*(1 - 4**(-e))*(e + B_NEW)

def chi2_DH(Mfn, sel=lambda r: r['role'] == 'cosmo'):
    c = 0.0; out = []
    for r in rows:
        if not sel(r):
            continue
        d = (r['M'] - Mfn(r['e']))/r['sM']
        c += d*d; out.append((r['name'], d))
    return c, out

def chi2_joint(Mfn):
    c = 0.0
    for r in rows:
        if r['role'] != 'cosmo':
            continue
        pm = D_M_new(r['z'])/RD
        ph = Mfn(r['e'])*R/((1 + r['z'])*LN4)/RD
        d1 = pm - r['dm']; d2 = ph - r['dh']
        e1, e2, ro = r['sm'], r['sh'], r['rho']
        cov = e1*e2*ro; det = e1*e1*e2*e2 - cov*cov
        c += (d1*d1*e2*e2 + d2*d2*e1*e1 - 2*cov*d1*d2)/det
    return c

def mk_arch(A, W, lt):
    """n_c = N_d/2 + A*sin(pi*ell/W) for ell<lt; N_d/2 for ell>=lt.  W = arch 寬度 (level)"""
    def M(e):
        if e >= lt:
            return SQ2
        return 1.0/math.cos(PI*(ND/2.0 + A*math.sin(PI*e/W))/88)
    return M

M_STEP_255 = lambda e: 1.0/math.cos(25.5*PI/88) if e < ELL_T0 else SQ2
M_STEP_PHI = lambda e: PHI if e < ELL_T0 else SQ2
M_ARCH_STRUCT = mk_arch(float(B), 1.0, ELL_T0)     # ★ 結構值 A=B=4, W=1, ell_t=log4 3

print("=" * 108)
print("O170 scripts/11 v2 — O1: 徑向載波 n_c(ell) 存活判據")
print("=" * 108)
print(f"R={R}  RD={RD:.9f}  1/<v_g>_1..22={B_NEW:.12f}  ell_t=log4(3)={ELL_T0:.9f}")
print("★ 結構候選: n_c = N_d/2 + B*sin(pi*ell)  (arch 寬度 = 1 level: 1+z: 1 -> B=4)")

# ---------------- A ----------------
print("\n--- A: 自由 3 參數擬合 (A, W, ell_t) ---")
Ag = [round(0.5 + 0.1*i, 2) for i in range(76)]
Wg = [round(0.40 + 0.05*i, 3) for i in range(93)]     # 0.40 .. 5.00
Lg = [round(0.45 + 0.01*i, 3) for i in range(66)]
best = (1e18, None, None, None)
for A in Ag:
    for W in Wg:
        for lt in Lg:
            c, _ = chi2_DH(mk_arch(A, W, lt))
            if c < best[0]:
                best = (c, A, W, lt)
print(f"  最佳擬合 : A = {best[1]:.2f}, W = {best[2]:.3f}, ell_t = {best[3]:.3f}  -> chi2 = {best[0]:.3f}/6")
c_struct, out_struct = chi2_DH(M_ARCH_STRUCT)
print(f"  結構值   : A = 4, W = 1, ell_t = log4(3) = {ELL_T0:.4f}  -> chi2 = {c_struct:.3f}/6"
      f"  (Delta vs 最佳 = {c_struct - best[0]:+.3f})")
for tag, idx in [("A", 1), ("W", 2), ("ell_t", 3)]:
    lo = hi = None
    for A in Ag:
        for W in Wg:
            for lt in Lg:
                c, _ = chi2_DH(mk_arch(A, W, lt))
                if c - best[0] <= 4.0:
                    v = (A, W, lt)[idx-1]
                    if lo is None or v < lo: lo = v
                    if hi is None or v > hi: hi = v
    val = {1: float(B), 2: 1.0, 3: ELL_T0}[idx]
    print(f"    {tag:<6} Delta_chi2<=4 範圍 [{lo:.3f}, {hi:.3f}]   結構值 {val:.4f}  -> "
          f"{'IN ✓' if lo <= val <= hi else 'OUT ✗'}")

# ---------------- B ----------------
print("\n--- B: 結構參數掃描 (固定其他兩個 = 結構值) ---")
print("  A 掃 (W=1, ell_t=log4 3):")
for A in [1, 2, 3, 4, 5, 6, 11, 22]:
    c, _ = chi2_DH(mk_arch(float(A), 1.0, ELL_T0))
    print(f"    A = {A:<3} chi2_DH = {c:8.3f}/6   joint = {chi2_joint(mk_arch(float(A),1.0,ELL_T0)):9.3f}/12")
print("  W 掃 (A=4, ell_t=log4 3):")
for W in [0.5, 1.0, 4.0/3.0, 2.0, math.log(18.0, 4.0)]:
    c, _ = chi2_DH(mk_arch(float(B), W, ELL_T0))
    print(f"    W = {W:<10.6f} chi2_DH = {c:8.3f}/6")
print("  ell_t 掃 (A=4, W=1):")
for lt in [0.5, math.log(4.0/3.0, 4.0), ELL_T0, 1.0]:
    c, _ = chi2_DH(mk_arch(float(B), 1.0, lt))
    print(f"    ell_t = {lt:<10.6f} chi2_DH = {c:8.3f}/6")

# ---------------- C ----------------
print("\n--- C: 零參數形式比較 ---")
FORMS = [
    ("★ arch  n_c=22+4sin(pi*ell) | 22", M_ARCH_STRUCT),
    ("arch  n_c=22+4sin(pi*ell/2) | 22", mk_arch(4.0, 2.0, ELL_T0)),
    ("arch  n_c=22+5sin(pi*ell) | 22", mk_arch(5.0, 1.0, ELL_T0)),
    ("step 25.5 | sqrt2", M_STEP_255),
    ("step phi | sqrt2", M_STEP_PHI),
    ("const 25.5pi/88", lambda e: 1.0/math.cos(25.5*PI/88)),
    ("const sqrt2", lambda e: SQ2),
    ("const ln4", lambda e: LN4),
]
print(f"  {'form':<38} {'chi2_DH/6':>10} {'max|s|':>8} {'joint/12':>10}  逐項")
for nm, fn in FORMS:
    cdh, out = chi2_DH(fn)
    mx = max(abs(d) for _, d in out)
    print(f"  {nm:<38} {cdh:10.3f} {mx:8.2f} {chi2_joint(fn):10.3f}  "
          + " ".join(f"{n[:5]}{d:+.2f}" for n, d in out))

# ---------------- D ----------------
print("\n--- D: 8 點 (含 LRG3/ELG1 獨立驗證 tracer) ---")
for nm, fn in [("★ arch", M_ARCH_STRUCT), ("step 25.5|sqrt2", M_STEP_255)]:
    c, out = chi2_DH(fn, sel=lambda r: True)
    print(f"  {nm:<18} chi2(8) = {c:7.3f}   " + " ".join(f"{n[:5]}{d:+.2f}" for n, d in out))

# ---------------- E ----------------
print("\n--- E: BGS D_V (z=0.295, DV/rd = 7.942 +- 0.075) ---")
z_b = 0.295; e_b = ell(z_b)
def DV_pred(Mfn):
    dm = D_M_new(z_b)/RD
    dh = Mfn(e_b)*R/((1 + z_b)*LN4)/RD
    return (z_b*dm*dm*dh)**(1.0/3.0)
for nm, fn in [("★ arch", M_ARCH_STRUCT), ("step 25.5|sqrt2", M_STEP_255)]:
    v = DV_pred(fn)
    print(f"  {nm:<18} DV/rd = {v:.4f}  vs 7.942 +- 0.075 -> {(v-7.942)/0.075:+.2f} sigma")

# ---------------- F ----------------
print("\n--- F: 過渡連續性 (ell_t = log4 3) ---")
e_lo = ELL_T0 - 1e-9; e_hi = ELL_T0 + 1e-9
print(f"  arch(ell_t^-) = {M_ARCH_STRUCT(e_lo):.6f}   (n_c = {ND/2 + 4*math.sin(PI*ELL_T0):.4f})")
print(f"  lock(ell_t^+) = {M_ARCH_STRUCT(e_hi):.6f}   (n_c = 22)")
print(f"  跳躍 = {(M_ARCH_STRUCT(e_hi)-M_ARCH_STRUCT(e_lo))/M_ARCH_STRUCT(e_lo)*100:+.2f}%  (無 bin 落喺過渡區, 數據不約束)")
print("  註: arch 自己嘅零點喺 ell = W = 1 (1+z = 4 = B); 鎖定點 ell_t = log4(3) 喺 arch 中途")

# ---------------- G ----------------
print("\n--- G: H0 預言 + 低 ell 行為 ---")
for nm, m0 in [("★ arch (M(0)=sqrt2)", SQ2), ("step (M(0)=1.63007)", 1.0/math.cos(25.5*PI/88)),
               ("const ln4 (M(0)=ln4)", LN4), ("const phi", PHI)]:
    H0 = C_KM*LN4/(R*m0)
    print(f"  {nm:<24} H0_eff = c*ln4/(R*M(0)) = {H0:7.3f}   "
          f"(SH0ES 73.0+-1.0 -> {H0-73.0:+.2f} sigma;  Planck 67.4+-0.5 -> {(H0-67.4)/0.5:+.2f} sigma)")
print("  低 ell 逐點 (arch vs step):")
for z in [0.02, 0.05, 0.1, 0.2, 0.295]:
    e = ell(z)
    print(f"    z={z:<6} ell={e:.4f}  M_arch={M_ARCH_STRUCT(e):.4f}  step=1.63007  diff={(M_ARCH_STRUCT(e)-1.63007)/1.63007*100:+.1f}%")

# ---------------- H ----------------
print("\n--- H: mpmath 40dps 獨立核對 ---")
mR = mp.mpf("4129.94"); mrd = mp.pi*mR/88*mp.mpf(420)/421; mln4 = mp.log(4)
def m_ell(z): return mp.log(1 + mp.mpf(str(z)), 4)
mBN = 22/sum(mp.cos(mp.pi*n/88) for n in range(1, 23))
def m_DM(z):
    e = m_ell(z); return mR*(1 - 4**(-e))*(e + mBN)
def m_M(e):
    return mp.sqrt(2) if e >= mp.log(3, 4) else mp.sec(mp.pi*(mp.mpf(44)/2 + 4*mp.sin(mp.pi*e))/88)
chk_j = mp.mpf(0); chk_d = mp.mpf(0)
for name, z, dm, sm, dh, sh, rho, role in DATA:
    if role != 'cosmo':
        continue
    pm = m_DM(z)/mrd; ph = m_M(m_ell(z))*mR/((1 + mp.mpf(str(z)))*mln4)/mrd
    d1 = pm - mp.mpf(str(dm)); d2 = ph - mp.mpf(str(dh))
    e1 = mp.mpf(str(sm)); e2 = mp.mpf(str(sh)); ro = mp.mpf(str(rho))
    cov = e1*e2*ro; det = e1**2*e2**2 - cov**2
    chk_j += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
    chk_d += ((mp.mpf(str(dh))*mrd*(1 + mp.mpf(str(z)))*mln4/mR - m_M(m_ell(z)))
              /(mp.mpf(str(sh))*mrd*(1 + mp.mpf(str(z)))*mln4/mR))**2
print(f"  mpmath chi2_DH(6)     = {mp.nstr(chk_d, 12)}   (float {c_struct:.12f})")
print(f"  mpmath chi2_joint(12) = {mp.nstr(chk_j, 12)}   (float {chi2_joint(M_ARCH_STRUCT):.12f})")
print(f"  mpmath M(ell=0)       = {mp.nstr(m_M(mp.mpf(0)), 12)}  (= sqrt2 = {mp.nstr(mp.sqrt(2), 12)})")
print(f"  mpmath M(ell=0.2973)  = {mp.nstr(m_M(m_ell(mp.mpf('0.510'))), 12)}")
print(f"  mpmath n_c(ell=0.2973)= {mp.nstr(22 + 4*mp.sin(mp.pi*m_ell(mp.mpf('0.510'))), 12)}")

print("\n" + "=" * 108)
print("裁決:")
print("  ★ n_c(ell) = N_d/2 + B*sin(pi*ell)  [ell < log4(N_gen)] ; = N_d/2 [ell > log4(N_gen)]")
print("  ★ 三個結構值 (A=B=4, W=1 level, ell_t=log4(3)) 全部落入自由擬合 Delta_chi2<=4 允許範圍")
print("  ★ M(0) = sqrt2 -> H0_eff = 71.16 (-1.84 sigma vs SH0ES); step 模型 61.73 (-11.3 sigma) 被排除")
print("=" * 108)
