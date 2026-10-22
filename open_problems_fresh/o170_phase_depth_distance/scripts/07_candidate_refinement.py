#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/07 — 候選細分: (a) D_app + ladder 過渡 (b) 淺極限 1/N_d 修正

(a) D_app+ladder: D_M = D_app(ℓ) for ℓ<ℓ_t, 之後斜率 √2 → 滿足 FRW 身份且 H0 = c/R ✓
(b) M_shallow = φ(1+1/N_d) vs φ vs sec(25.5π/88) (半位點量化)
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf("4129.94"); rd = mp.mpf("147.088"); C_D = mp.mpf("-0.1697")
ell_t = mp.log(3, 4); N_d = 44

def ell(z): return mp.log(1 + mp.mpf(str(z)), 4)
def D_app(z):
    e = ell(z)
    return R * (1 - 4**(-e)) * (1 + 2*phi**-1*e + C_D*(e - mp.mpf("0.5"))*(1 - 4**(-e)))

TR = [('LRG1', 0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
      ('LRG2', 0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
      ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
      ('ELG2', 1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
      ('QSO', 1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
      ('Lya', 2.330, 38.988, 0.531, 8.632, 0.101, -0.431)]
VAL = [('LRG3', 0.922, 21.648, 0.178, 17.577, 0.213, -0.406),
       ('ELG1', 0.955, 21.707, 0.335, 17.803, 0.297, -0.462)]

def D_applad(z):
    e = ell(z)
    if e <= ell_t: return D_app(z)
    zt = 4**ell_t - 1
    return D_app(zt) + R*mp.sqrt(2)*(e - ell_t)

def M_id(Df, z):
    e = ell(z); h = mp.mpf("1e-10")
    return (Df(4**(e+h)-1) - Df(4**(e-h)-1))/(2*h)/R

print("="*96)
print("O170 scripts/07 — 候選細分")
print("="*96)

print("\n--- F1: D_app + ladder 過渡 (ℓ_t = log₄3) ---")
c = sum(((D_applad(z)/rd - mp.mpf(str(dm)))/mp.mpf(str(sm)))**2 for t,z,dm,sm,dh,sh,r in TR)
print(f"  χ²(D_M) = {float(c):.2f}/6")
c8 = mp.mpf(0); c6 = mp.mpf(0)
for t,z,dm,sm,dh,sh,r in TR+VAL:
    pred = M_id(D_applad, z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd
    v = ((pred - mp.mpf(str(dh)))/mp.mpf(str(sh)))**2
    c8 += v
    if t not in ('LRG3','ELG1'): c6 += v
print(f"  χ²(D_H, 身份導出) = {float(c6):.2f}/6 (8 點 {float(c8):.2f}/8)")
cj = mp.mpf(0)
for t,z,dm,sm,dh,sh,r in TR:
    d1 = D_applad(z)/rd - mp.mpf(str(dm))
    d2 = M_id(D_applad, z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd - mp.mpf(str(dh))
    e1=mp.mpf(str(sm)); e2=mp.mpf(str(sh)); r_=mp.mpf(str(r))
    cov=e1*e2*r_; det=e1**2*e2**2-cov**2
    cj += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
print(f"  χ²_joint = {float(cj):.2f}/12")
print(f"  H0 = c/(dD/dz|₀) = {float(mp.mpf('299792.458')/(M_id(D_applad, mp.mpf('1e-6'))*R/mp.log(4))):.3f} km/s/Mpc")
zny = 4**mp.mpf("2.08496")-1
print(f"  CMB 橫向 D_M(z=17)/R = {float(D_applad(zny)/R):.5f} (π = {float(mp.pi):.5f})")
zb = mp.mpf("0.295")
dmv = D_applad(zb)/rd; dhv = M_id(D_applad, zb)*R/((1+zb)*mp.log(4))/rd
DV = (zb*dmv**2*dhv)**(mp.mpf(1)/3)
print(f"  BGS D_V/rd = {float(DV):.4f} vs 7.942±0.075 → {float((DV-mp.mpf('7.942'))/mp.mpf('0.075')):+.2f}σ")
print("  逐點 M(身份):")
for t,z,dm,sm,dh,sh,r in TR+VAL:
    e = ell(z); Md = mp.mpf(str(dh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
    sMd = mp.mpf(str(sh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
    mi = M_id(D_applad, z)
    print(f"    {t:<11} ℓ={float(e):.4f}  M_data={float(Md):.4f}±{float(sMd):.4f}  M_id={float(mi):.4f}  ({float((Md-mi)/sMd):+.2f}σ)")

print("\n--- F2: 淺極限常數候選 (6 bins D_H; z=0.934 標記) ---")
cands = [("φ = 2cos(π/5)", phi),
         ("φ(1+1/N_d) = φ(1+1/44)", phi*(1+mp.mpf(1)/N_d)),
         ("φ(1+1/L₁₀) = φ(1+1/123)", phi*(1+mp.mpf(1)/123)),
         ("sec(25.5π/88) 半位點", mp.sec(mp.mpf("25.5")*mp.pi/88)),
         ("2cos(π/5.05)", 2*mp.cos(mp.pi/mp.mpf("5.05")))]
for nm, Mv in cands:
    tot = mp.mpf(0); no934 = mp.mpf(0)
    for t,z,dm,sm,dh,sh,r in TR:
        e = ell(z)
        M = Mv if e < ell_t else mp.sqrt(2)
        v = ((M*R/((1+mp.mpf(str(z)))*mp.log(4))/rd - mp.mpf(str(dh)))/mp.mpf(str(sh)))**2
        tot += v
        if t != 'LRG3+ELG1': no934 += v
    print(f"  {nm:<26} M={float(Mv):.6f}  χ²(6 bins)={float(tot):7.2f}  排除 z=0.934: χ²(5)={float(no934):6.2f}")

print("\n--- F3: 淺極限加權平均 (各子集) ---")
def wmean(sel):
    w=mp.mpf(0); sw=mp.mpf(0)
    for t,z,dm,sm,dh,sh,r in TR+VAL:
        e=ell(z)
        if e>=ell_t or not sel(t): continue
        M = mp.mpf(str(dh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
        sM = mp.mpf(str(sh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
        ww = 1/sM**2; w += M*ww; sw += ww
    return w/sw, 1/mp.sqrt(sw)
for nm, sel in [("全部淺點 (7)", lambda t: True),
                ("排除 z=0.934", lambda t: t not in ('LRG3+ELG1',)),
                ("只有 DESI 推論 bins (5)", lambda t: t not in ('LRG3','ELG1','LRG3+ELG1')),
                ("排除全部 z≈0.93 (LRG3/ELG1/合併)", lambda t: t not in ('LRG3','ELG1','LRG3+ELG1'))]:
    m, s = wmean(sel)
    print(f"  {nm:<32} ⟨M⟩ = {float(m):.5f} ± {float(s):.5f}   vs φ: {float((m-phi)/s):+.2f}σ   vs φ(1+1/44): {float((m-phi*(1+mp.mpf(1)/44))/s):+.2f}σ")

print("\n" + "="*96)
print("裁決: (a) D_app+ladder 滿足 FRW 身份 + H0 = c/R = 72.59 ✓; (b) 淺極限常數鑑別需未來數據")
print("="*96)
