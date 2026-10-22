#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/06 — ★ FRW 身份檢驗: D_H = dD_M/dz ?

IDCM 冇膨脹 → D_H = c/H(z) 唔係基本原理; 但 FRW 身份 D_H = dD_M/dz 係一個
「一致性要求」(O167 kernel A 用 dD_app/dz 作徑向 → χ² > 10⁴ FAIL).

本腳本: 對每個橫向候選律 D_M(ℓ), 用身份導出徑向核 M(ℓ) = dD_M/dℓ,
再同 DESI D_H 直接測量比較 → 檢驗邊個 D_M 律同徑向數據自洽。

橫向候選:
  (i)   D_app(ℓ) = R(1−4^{−ℓ})·(1+2φ⁻¹ℓ + C_D(ℓ−½)(1−4^{−ℓ}))   [O169 現行]
  (ii)  D_lin(ℓ) = R·φ·ℓ                                        [相位深度積分, k=5]
  (iii) D_lad(ℓ) = R·[φ·min(ℓ,ℓ_t) + √2·(ℓ−ℓ_t)_+]              [ladder k=5→4]
  (iv)  D_lad2(ℓ)= R·[φ·min(ℓ,ℓ_t) + √2·min((ℓ−ℓ_t)_+,ℓ_t) + 1·(ℓ−2ℓ_t)_+]  [k=5,4,3]

徑向核 M(ℓ) = dD_M/dℓ (無量綱, R 單位); 對照 DESI 直接測量 M_data = D_H·(1+z)·ln4/R.
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf("4129.94"); rd = mp.mpf("147.088"); C_D = mp.mpf("-0.1697")
ell_t = mp.log(3, 4)

def ell(z): return mp.log(1 + mp.mpf(str(z)), 4)
def D_app(z):
    e = ell(z)
    return R * (1 - 4**(-e)) * (1 + 2*phi**-1*e + C_D*(e - mp.mpf("0.5"))*(1 - 4**(-e)))
def D_lin(z): return R * phi * ell(z)
def D_lad(z):
    e = ell(z)
    return R * (phi*min(e, ell_t) + mp.sqrt(2)*max(mp.mpf(0), e - ell_t))
def D_lad2(z):
    e = ell(z)
    return R * (phi*min(e, ell_t) + mp.sqrt(2)*min(max(mp.mpf(0), e-ell_t), ell_t) + 1*max(mp.mpf(0), e-2*ell_t))

def M_from_DM(Df, z):
    e = ell(z); h = mp.mpf("1e-10")
    zp = 4**(e+h) - 1; zm = 4**(e-h) - 1
    return (Df(zp) - Df(zm)) / (2*h) / R      # (dD/dℓ)/R

TR = [('LRG1', 0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
      ('LRG2', 0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
      ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
      ('ELG2', 1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
      ('QSO', 1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
      ('Lya', 2.330, 38.988, 0.531, 8.632, 0.101, -0.431)]
VAL = [('LRG3', 0.922, 21.648, 0.178, 17.577, 0.213, -0.406),
       ('ELG1', 0.955, 21.707, 0.335, 17.803, 0.297, -0.462)]
BGS = (0.295, 7.942, 0.075)

print("=" * 100)
print("O170 scripts/06 — FRW 身份檢驗: D_H = dD_M/dz ?")
print("=" * 100)

LAWS = [("D_app (O169 現行)", D_app), ("D_lin = φRℓ", D_lin),
        ("D_ladder k=5|4", D_lad), ("D_ladder k=5|4|3", D_lad2)]

print("\n--- E1: 橫向 χ²(D_M) 6 bins ---")
for nm, f in LAWS:
    c = sum(((f(z)/rd - mp.mpf(str(dm)))/mp.mpf(str(sm)))**2 for t, z, dm, sm, dh, sh, rho in TR)
    print(f"  {nm:<20} χ²(D_M) = {float(c):8.2f}/6")

print("\n--- E2: 身份導出徑向核 M(ℓ) = (dD_M/dℓ)/R vs DESI 直接測量 ---")
hdr = f"  {'tracer':<11} {'ℓ':<8} {'M_data':<9} {'±':<8}"
for nm, f in LAWS: hdr += f" {nm[:12]:<13}"
print(hdr)
for t, z, dm, sm, dh, sh, rho in TR + VAL:
    e = ell(z)
    Md = mp.mpf(str(dh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
    sMd = mp.mpf(str(sh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R
    line = f"  {t:<11} {float(e):<8.4f} {float(Md):<9.4f} {float(sMd):<8.4f}"
    for nm, f in LAWS:
        line += f" {float(M_from_DM(f, z)):<13.4f}"
    print(line)

print("\n--- E3: 每個 D_M 律 → 身份 χ²(D_H) 6 bins / 8 點 ---")
for nm, f in LAWS:
    c6 = mp.mpf(0); c8 = mp.mpf(0)
    for t, z, dm, sm, dh, sh, rho in TR + VAL:
        pred = M_from_DM(f, z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd
        v = ((pred - mp.mpf(str(dh)))/mp.mpf(str(sh)))**2
        c8 += v
        if t not in ('LRG3', 'ELG1'): c6 += v
    print(f"  {nm:<20} χ²(D_H) = {float(c6):8.2f}/6 (8 點 {float(c8):.2f}/8)")

print("\n--- E4: 每個 D_M 律 → 聯合 χ²(D_M+D_H, 含 ρ) 6 bins ---")
for nm, f in LAWS:
    cj = mp.mpf(0)
    for t, z, dm, sm, dh, sh, rho in TR:
        d1 = f(z)/rd - mp.mpf(str(dm))
        d2 = M_from_DM(f, z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd - mp.mpf(str(dh))
        e1 = mp.mpf(str(sm)); e2 = mp.mpf(str(sh)); r_ = mp.mpf(str(rho))
        cov = e1*e2*r_; det = e1**2*e2**2 - cov**2
        cj += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
    print(f"  {nm:<20} χ²_joint = {float(cj):8.2f}/12")

print("\n--- E5: 混合: D_M 用 D_app, 徑向用結構核 M = 2cos(π/k) (獨立假設) ---")
c_h = mp.mpf(0); c_j = mp.mpf(0)
for t, z, dm, sm, dh, sh, rho in TR:
    e = ell(z)
    M = 2*mp.cos(mp.pi/(5 if e < ell_t else 4))
    d1 = D_app(z)/rd - mp.mpf(str(dm))
    d2 = M*R/((1+mp.mpf(str(z)))*mp.log(4))/rd - mp.mpf(str(dh))
    c_h += (d2/mp.mpf(str(sh)))**2
    e1 = mp.mpf(str(sm)); e2 = mp.mpf(str(sh)); r_ = mp.mpf(str(rho))
    cov = e1*e2*r_; det = e1**2*e2**2 - cov**2
    c_j += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
print(f"  D_app + M=2cos(π/k):  χ²(D_H) = {float(c_h):.2f}/6,  χ²_joint = {float(c_j):.2f}/12")

print("\n--- E6: z→0 斜率 → H0 (每個律) ---")
c_km = mp.mpf("299792.458")
for nm, f in LAWS:
    slope = M_from_DM(f, mp.mpf("1e-6"))          # dD_M/dℓ / R
    DH0 = slope*R/mp.log(4)                        # = dD_M/dz at z=0
    print(f"  {nm:<20} dD/dℓ|₀/R = {float(slope):.5f}  →  H0 = c/(dD/dz|₀) = {float(c_km/DH0):.3f} km/s/Mpc")
print(f"  (參考: SH0ES 73.0±1.0; Planck 67.4±0.5)")

print("\n--- E7: 橫向飽和 (ℓ_nyq = 2.08496, 1+z = 18) ---")
for nm, f in LAWS:
    zny = 4**mp.mpf("2.08496") - 1
    print(f"  {nm:<20} D_M(z=17)/R_world = {float(f(zny)/R):.5f}   (π = {float(mp.pi):.5f})")
print("\n--- E8: 世界徑向總延伸 (ladder 外推, 推測) ---")
tot = ell_t*(phi + mp.sqrt(2) + 1)
print(f"  ∫M dℓ (k=5,4,3,2) = {float(tot):.5f} R_world = {float(tot*R):.1f} Mpc   vs πR = {float(mp.pi*R):.1f} Mpc ({float((tot-mp.pi)/mp.pi*100):+.2f}%)")

print("\n--- E9: BGS D_V (z=0.295, 7.942 ± 0.075) 每個律 ---")
z_b = mp.mpf("0.295")
for nm, f in LAWS:
    dmv = f(z_b)/rd
    dhv = M_from_DM(f, z_b)*R/((1+z_b)*mp.log(4))/rd
    DV = (z_b*dmv**2*dhv)**(mp.mpf(1)/3)
    print(f"  {nm:<20} D_M/rd={float(dmv):.4f} D_H/rd={float(dhv):.4f} D_V/rd={float(DV):.4f} → {float((DV-mp.mpf('7.942'))/mp.mpf('0.075')):+.2f}σ")

print("\n" + "=" * 100)
print("裁決: FRW 身份 (D_H = dD_M/dz) 對 D_app 唔成立 (χ² > 10⁴); 對相位深度律 D_lin/D_ladder 成立 ✓")
print("      但身份成立嘅律 → H0 = c·ln4/(φR_world) = 62.19 (SH0ES 73.0 → 10.8σ) ✗")
print("=" * 100)
