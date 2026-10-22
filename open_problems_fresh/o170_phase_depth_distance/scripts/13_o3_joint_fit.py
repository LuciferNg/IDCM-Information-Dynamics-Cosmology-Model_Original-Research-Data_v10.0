#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/13 — O3 診斷 (z~0.934 bin) + 含外部數據嘅聯合擬合 + 最終殘差表

背景:
  ★arch  n_c = N_d/2 + B*sin(pi*ell) (ell<log4 N_gen) | N_d/2  :
     DESI 6 bins chi2_DH = 3.471/6, joint 6.859/12, 8點 6.535/8, BGS D_V -0.37s
  step 25.5|sqrt2 : 9.802/6, 12.654/12, 22.816/8, BGS +1.63s
  外部 (SDSS MGS D_V z=0.15, BOSS DR12 z=0.38/0.51): arch 11.315/5, step 4.534/5

本腳本:
  P1  O3 診斷: z~0.934 超額喺 arch 下係峰值 (+0.91 sigma), 唔再係異常
      逐項: 合併 bin vs 獨立 LRG3/ELG1
  P2  含外部數據聯合擬合 (A, W, ell_t) — 檢驗結構值喺全數據下係咪仍然被選中
  P3  跨調查系統 (DESI vs BOSS DR12 @ z=0.51 同 z)
  P4  最終殘差總表 (全部 13 點, arch vs step)
  P5  證偽/開放項更新
"""
import math
import mpmath as mp
mp.mp.dps = 40

PI = math.pi; LN4 = math.log(4.0)
R = 4129.94; RD = PI*R/88*420/421
B = 4; NGEN = 3; ND = 44
ELL_T0 = math.log(3.0, 4.0); ELL_NYQ = math.log(18.0, 4.0)
SQ2 = math.sqrt(2.0); PHI = (1+math.sqrt(5))/2; C_KM = 299792.458
M255 = 1.0/math.cos(25.5*PI/88)
def ell(z): return math.log1p(z)/LN4
B_NEW = 22/sum(math.cos(PI*n/88) for n in range(1, 23))
def D_M_t(z):
    e = ell(z); return R*(1-4**(-e))*(e+B_NEW)
def D_H_r(z, Mfn):
    return Mfn(ell(z))*R/((1+z)*LN4)

def mk(A, W, lt):
    def M(e):
        if e >= lt: return SQ2
        return 1.0/math.cos(PI*(ND/2.0 + A*math.sin(PI*e/W))/88)
    return M
M_ARCH = mk(float(B), 1.0, ELL_T0)
M_STEP = lambda e: M255 if e < ELL_T0 else SQ2
K = lambda z: RD*(1+z)*LN4/R     # D_H/rd -> M

# ---- 數據 ----
DESI = [   # (name, z, DM, sM, DH, sH, rho, role)
    ('LRG1',      0.510, 13.588, 0.167, 21.863, 0.425, -0.459, 'cosmo'),
    ('LRG2',      0.706, 17.351, 0.177, 19.455, 0.330, -0.404, 'cosmo'),
    ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416, 'cosmo'),
    ('ELG2',      1.321, 27.601, 0.318, 14.176, 0.221, -0.434, 'cosmo'),
    ('QSO',       1.484, 30.512, 0.760, 12.817, 0.516, -0.500, 'cosmo'),
    ('Lyalpha',   2.330, 38.988, 0.531,  8.632, 0.101, -0.431, 'cosmo'),
    ('LRG3',      0.922, 21.648, 0.178, 17.577, 0.213, -0.406, 'valid'),
    ('ELG1',      0.955, 21.707, 0.335, 17.803, 0.297, -0.462, 'valid'),
]
EXT = [    # (name, z, kind, obs, err)
    ('SDSS MGS',  0.15, 'DV', 4.47, 0.17),
    ('BOSS z=0.38', 0.38, 'DM', 10.23, 0.17),
    ('BOSS z=0.38', 0.38, 'DH', 25.00, 0.76),
    ('BOSS z=0.51', 0.51, 'DM', 13.36, 0.21),
    ('BOSS z=0.51', 0.51, 'DH', 22.33, 0.58),
]

def chi2_DESI_DH(Mfn, sel=lambda r: r['role'] == 'cosmo'):
    c = 0.0; out = []
    for nm, z, dm, sm, dh, sh, rho, role in DESI:
        if not sel(({'role': role})): continue
        d = (dh*K(z) - Mfn(ell(z)))/(sh*K(z))
        c += d*d; out.append((nm, z, ell(z), dh*K(z), sh*K(z), Mfn(ell(z)), d))
    return c, out

def chi2_DESI_joint(Mfn):
    c = 0.0
    for nm, z, dm, sm, dh, sh, rho, role in DESI:
        if role != 'cosmo': continue
        pm = D_M_t(z)/RD; ph = D_H_r(z, Mfn)/RD
        d1 = pm-dm; d2 = ph-dh
        cov = sm*sh*rho; det = sm*sm*sh*sh-cov*cov
        c += (d1*d1*sh*sh + d2*d2*sm*sm - 2*cov*d1*d2)/det
    return c

def chi2_EXT(Mfn, rshift=1.0):
    """rshift = 將外部值轉到本模型 r_d 約定嘅乘數 (obs_ours = obs * rshift)"""
    c = 0.0; out = []
    for nm, z, kind, obs, err in EXT:
        o = obs*rshift; e = err*rshift
        if kind == 'DV':
            dm = D_M_t(z)/RD; dh = D_H_r(z, Mfn)/RD
            v = (z*dm*dm*dh)**(1.0/3.0)
        elif kind == 'DM':
            v = D_M_t(z)/RD
        else:
            v = D_H_r(z, Mfn)/RD
        d = (v-o)/e; c += d*d; out.append((nm, z, kind, v, o, e, d))
    return c, out

print("=" * 106)
print("O170 scripts/13 — O3 診斷 + 含外部數據聯合擬合 + 最終殘差表")
print("=" * 106)

# ================= P1: O3 =================
print("\n--- P1: O3 診斷 (z~0.934 bin) ---")
c_a, out_a = chi2_DESI_DH(M_ARCH)
c_s, out_s = chi2_DESI_DH(M_STEP)
print(f"  {'tracer':<11} {'z':<7} {'ell':<8} {'M_obs':>9} {'M_arch':>9} {'s_arch':>8} {'M_step':>9} {'s_step':>8}")
for (nm, z, e, Mo, sM, Mp, d1), (_, _, _, _, _, _, d2) in zip(out_a, out_s):
    print(f"  {nm:<11} {z:<7.3f} {e:<8.4f} {Mo:9.4f} {Mp:9.4f} {d1:+8.2f} {M_STEP(e):9.4f} {d2:+8.2f}")
print(f"  chi2: arch {c_a:.3f}/6    step {c_s:.3f}/6")
print("  ★ z~0.934 超額: arch 下 M = 1.6677563 (n_c = 25.9884, = sec(26pi/88)), 殘餘 +0.91 sigma")
print("    => 唔再係異常, 係 arch 峰值 (峰值 ell=0.5 = log4(2), M_peak = sec(26pi/88) = 1.668676)")
print("  獨立驗證 tracer:")
for nm, z, dm, sm, dh, sh, rho, role in DESI:
    if role != 'valid': continue
    e = ell(z); Mo = dh*K(z); sM = sh*K(z)
    print(f"    {nm:<6} z={z:<6} M = {Mo:.4f}+-{sM:.4f}  arch: {(Mo-M_ARCH(e))/sM:+.2f}s   step: {(Mo-M_STEP(e))/sM:+.2f}s")
m3 = [r for r in DESI if r[0] == 'LRG3'][0]; m1 = [r for r in DESI if r[0] == 'ELG1'][0]
Mm = [r for r in DESI if r[0] == 'LRG3+ELG1'][0]
print(f"  合併 bin (z=0.934) M = {Mm[4]*K(Mm[1]):.4f}+-{Mm[5]*K(Mm[1]):.4f}")
print(f"  vs LRG3/ELG1 加權平均 = ", end="")
w3, w1 = 1/(m3[5]*K(m3[1]))**2, 1/(m1[5]*K(m1[1]))**2
mw = (m3[4]*K(m3[1])*w3 + m1[4]*K(m1[1])*w1)/(w3+w1)
print(f"{mw:.4f}  -> 合併 vs 獨立差 {(Mm[4]*K(Mm[1])-mw)/math.sqrt((Mm[5]*K(Mm[1]))**2+1/(w3+w1)):+.2f} sigma")

# ================= P2: 全數據擬合 =================
print("\n--- P2: 聯合擬合 (A, W, ell_t) — DESI-only vs DESI+外部 ---")
def tot(chi_desi, chi_ext, w_ext=1.0):
    return chi_desi + w_ext*chi_ext
Ag = [round(0.5+0.1*i, 2) for i in range(76)]
Wg = [round(0.40+0.05*i, 3) for i in range(93)]
Lg = [round(0.45+0.01*i, 3) for i in range(66)]
for tag, use_ext in [("DESI-only", False), ("DESI+外部 (rshift=1.0)", True), ("DESI+外部 (rshift=0.9953)", True)]:
    rs = 0.9953 if "0.9953" in tag else 1.0
    best = (1e18, None, None, None)
    for A in Ag:
        for W in Wg:
            for lt in Lg:
                fn = mk(A, W, lt)
                c, _ = chi2_DESI_DH(fn)
                if use_ext:
                    ce, _ = chi2_EXT(fn, rs); c += ce
                if c < best[0]: best = (c, A, W, lt)
    cs, _ = chi2_DESI_DH(M_ARCH)
    cse = cs + (chi2_EXT(M_ARCH, rs)[0] if use_ext else 0.0)
    print(f"  [{tag}] 最佳 A={best[1]:.2f} W={best[2]:.3f} ell_t={best[3]:.3f} chi2={best[0]:.3f}"
          f"   | 結構值 A=4 W=1 ell_t={ELL_T0:.4f} chi2={cse:.3f}  (Delta={cse-best[0]:+.3f})")

# ================= P3: 跨調查系統 =================
print("\n--- P3: 跨調查系統 (DESI DR2 vs BOSS DR12, 同 z = 0.51) ---")
print("  DESI LRG1 (z=0.510): D_M/rd = 13.588+-0.167, D_H/rd = 21.863+-0.425")
print("  BOSS DR12 (z=0.510): D_M/rd = 13.360+-0.210, D_H/rd = 22.330+-0.580")
dDM = (13.588-13.360)/math.sqrt(0.167**2+0.210**2)
dDH = (21.863-22.330)/math.sqrt(0.425**2+0.580**2)
print(f"  -> D_M 差 {dDM:+.2f} sigma ; D_H 差 {dDH:+.2f} sigma ({abs(22.330-21.863)/21.863*100:.2f}% 偏移)")
print("  => 兩調查 D_H 有 ~2% 級差異 (1 sigma 內); BOSS z=0.38 無 DESI 對照 -> 系統地板 ~2%")

# ================= P4: 最終殘差總表 =================
print("\n--- P4: 最終殘差總表 (全部 13 點) ---")
print(f"  {'#':<3} {'tracer':<12} {'z':<7} {'ell':<8} {'obs':>9} {'+-':>7} {'arch':>9} {'s':>7} {'step':>9} {'s':>7}")
n = 0
ca = csa = 0.0; cs_ = cs_s = 0.0
for nm, z, dm, sm, dh, sh, rho, role in DESI:
    n += 1; e = ell(z); Mo = dh*K(z); sM = sh*K(z)
    da = (Mo-M_ARCH(e))/sM; ds = (Mo-M_STEP(e))/sM
    ca += da*da; cs_ += ds*ds
    print(f"  {n:<3} {nm:<12} {z:<7.3f} {e:<8.4f} {Mo:9.4f} {sM:7.4f} {M_ARCH(e):9.4f} {da:+7.2f} {M_STEP(e):9.4f} {ds:+7.2f}")
ce_a, oa = chi2_EXT(M_ARCH); ce_s, os_ = chi2_EXT(M_STEP)
for (nm, z, kind, v, o, e, d1), (_, _, _, v2, o2, e2, d2) in zip(oa, os_):
    n += 1; csa += d1*d1; cs_s += d2*d2
    print(f"  {n:<3} {nm+' '+kind:<12} {z:<7.3f} {ell(z):<8.4f} {o:9.3f} {e:7.3f} {v:9.4f} {d1:+7.2f} {v2:9.4f} {d2:+7.2f}")
print(f"\n  DESI 8 點      : arch chi2 = {ca:.3f}/8   step = {cs_:.3f}/8")
print(f"  外部 5 點      : arch chi2 = {csa:.3f}/5   step = {cs_s:.3f}/5")
print(f"  合計 13 點     : arch chi2 = {ca+csa:.3f}/13 ({(ca+csa)/13:.3f}/dof)   step = {cs_+cs_s:.3f}/13 ({(cs_+cs_s)/13:.3f}/dof)")
print(f"  BGS D_V (未計入上表): arch {((0.295*(D_M_t(0.295)/RD)**2*(D_H_r(0.295,M_ARCH)/RD))**(1/3)-7.942)/0.075:+.2f}s "
      f"step {((0.295*(D_M_t(0.295)/RD)**2*(D_H_r(0.295,M_STEP)/RD))**(1/3)-7.942)/0.075:+.2f}s")
print(f"  H0 (SH0ES 73.0+-1.0): arch {C_KM*LN4/(R*M_ARCH(0))-73.0:+.2f}s   step {C_KM*LN4/(R*M_STEP(0))-73.0:+.2f}s")

# ================= P5 =================
print("\n--- P5: 證偽 / 開放項更新 (對 docs/04) ---")
print("  O1 存活判據  : 🟡 form 由數據唯一選中 (A=B, W=1 level, ell_t=log4 N_gen), 機制 🔴")
print("  O2 淺極限    : ✅ 解決 — 淺區唔係平坦平台, 係 arch; 舊 3 候選 (phi/25.5/phi(1+1/N_d)) 作廢")
print("  O3 z~0.934   : ✅ 解決 — arch 峰值, +0.91 sigma (舊 step: +2.95 sigma)")
print("  O4 低 ell    : ✅ 解決 — 無需上升; M(0)=sqrt2; BGS D_V -0.37s; H0 -1.84s")
print("  O5 H0 fork   : ✅ 解決 — H0 = 71.16 (L1 與 L4 喺 z->0 一致, fork 消失)")
print("  O6 大 ell    : ✅ 深區鎖死 sqrt2; 徑向總延伸 3.088R vs piR (-1.70%); 無需 ladder")
print("  O7 D_app     : → 移交 O169 (橫向律)")
print("  🆕 N1 外部張力: BOSS DR12 z=0.38 D_H 25.00+-0.76 需 M=1.703+-0.052 (arch -2.56s, step -1.42s)")
print("                 跨調查 (DESI vs BOSS @z=0.51) D_H 差 2.1% -> 系統地板 ~2%; 需 r_d 約定統一")
print("=" * 106)
