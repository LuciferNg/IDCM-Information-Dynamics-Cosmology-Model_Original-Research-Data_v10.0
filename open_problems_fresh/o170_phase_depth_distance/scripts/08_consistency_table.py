#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/08 — 橫向×徑向一致性總表 (FRW 身份 D_H = dD_M/dz 檢驗)

對每個候選「距離定律 D(ℓ)」計算:
  χ²(D_M 6 bins) / χ²(D_H 由身份導出) / χ²_joint (含 ρ) / H0(z→0 斜率) / CMB D(ℓ_nyq)/R / BGS D_V
候選:
  L1 D_app + 獨立核 M=sec(25.5π/88)|√2   (即 docs/02 嘅做法, 身份唔成立)
  L2 D_app + ladder 過渡 (ℓ>ℓ_t 斜率 √2)  (身份成立)
  L3 統一相位深度律 D = R∫M dℓ, M = φ|√2   (身份成立)
  L4 統一相位深度律 D = R∫M dℓ, M = sec(25.5π/88)|√2  (身份成立)
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf("4129.94"); rd = mp.mpf("147.088"); C_D = mp.mpf("-0.1697")
ell_t = mp.log(3, 4); M_sh = mp.sec(mp.mpf("25.5")*mp.pi/88); M_dp = mp.sqrt(2)

def ell(z): return mp.log(1 + mp.mpf(str(z)), 4)
def D_app(z):
    e = ell(z)
    return R*(1-4**(-e))*(1 + 2*phi**-1*e + C_D*(e-mp.mpf("0.5"))*(1-4**(-e)))
def D_app_lad(z):
    e = ell(z)
    return D_app(z) if e <= ell_t else D_app(4**ell_t - 1) + R*M_dp*(e - ell_t)
def D_unif(z, msh):
    e = ell(z)
    return R*msh*e if e <= ell_t else R*(msh*ell_t + M_dp*(e - ell_t))
def M_id(Df, z):
    e = ell(z); h = mp.mpf("1e-10")
    return (Df(4**(e+h)-1) - Df(4**(e-h)-1))/(2*h)/R
def M_law(z, msh):
    return msh if ell(z) < ell_t else M_dp

TR = [('LRG1',0.510,13.588,0.167,21.863,0.425,-0.459),
      ('LRG2',0.706,17.351,0.177,19.455,0.330,-0.404),
      ('LRG3+ELG1',0.934,21.576,0.152,17.641,0.193,-0.416),
      ('ELG2',1.321,27.601,0.318,14.176,0.221,-0.434),
      ('QSO',1.484,30.512,0.760,12.817,0.516,-0.500),
      ('Lya',2.330,38.988,0.531,8.632,0.101,-0.431)]
BGS_z, BGS_DV, BGS_s = 0.295, mp.mpf("7.942"), mp.mpf("0.075")
ell_nyq = mp.log(mp.mpf("44")/mp.mpf("18") + 1, 4)

def report(name, DMf, Mf, ident):
    cm = mp.mpf(0); ch = mp.mpf(0); cj = mp.mpf(0)
    for t,z,dm,sm,dh,sh,r in TR:
        d1 = DMf(z)/rd - mp.mpf(str(dm)); d2 = Mf(z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd - mp.mpf(str(dh))
        e1 = mp.mpf(str(sm)); e2 = mp.mpf(str(sh)); r_ = mp.mpf(str(r))
        cm += (d1/e1)**2; ch += (d2/e2)**2
        cov = e1*e2*r_; det = e1**2*e2**2 - cov**2
        cj += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
    # H0 from slope at z->0  (dD/dz|0 = M(0)*R/ln4)
    H0 = mp.mpf("299792.458")/(M_law(1e-12, M_sh if 'sec' in name or '25.5' in name else phi)*R/mp.log(4)) if ident else mp.mpf("299792.458")/R
    DV = (BGS_z*(DMf(BGS_z)/rd)**2*(Mf(BGS_z)*R/((1+BGS_z)*mp.log(4))/rd))**(mp.mpf(1)/3)
    print(f"  {name:34s} χ²(D_M)={float(cm):6.2f}/6  χ²(D_H)={float(ch):6.2f}/6  joint={float(cj):6.2f}/12  H0={float(H0):6.2f}  D(nyq)/R={float(DMf(4**ell_nyq-1)/R):.5f}  BGS={float((DV-BGS_DV)/BGS_s):+.2f}σ")

print("="*130)
print("O170 scripts/08 — 橫向×徑向一致性總表")
print("="*130)
print(f"\n  參考: π = {float(mp.pi):.5f}   ℓ_nyq = {float(ell_nyq):.5f}   H0(SH0ES)=73.0±1.0   H0(Planck)=67.4±0.5")
print(f"  M_sh(sec 25.5π/88) = {float(M_sh):.6f}   M_sh(φ) = {float(phi):.6f}   M_dp = {float(M_dp):.6f}\n")
print("  --- L1: D_app + 獨立核 (身份唔成立) ---")
report("L1 D_app + M=sec25.5|√2", D_app, lambda z: M_law(z, M_sh), False)
print("  --- L2: D_app + ladder 過渡 (身份成立) ---")
report("L2 D_app+ladder (M=φ)", D_app_lad, lambda z: M_id(D_app_lad, z), True)
print("  --- L3/L4: 統一相位深度律 (身份成立) ---")
report("L3 unif ladder (M=φ)", lambda z: D_unif(z, phi), lambda z: M_law(z, phi), True)
report("L4 unif ladder (M=sec25.5)", lambda z: D_unif(z, M_sh), lambda z: M_law(z, M_sh), True)
print("\n  --- 對照: 舊 O167 kernel A (dD_app/dz 作徑向) ---")
report("O167 kernelA (D_app 導數)", D_app, lambda z: M_id(D_app, z), True)
print("\n  註: L1 嘅 χ²(D_H) 用獨立核 (身份唔成立) → 顯示「結構上兩條定律無關」嘅代價")
