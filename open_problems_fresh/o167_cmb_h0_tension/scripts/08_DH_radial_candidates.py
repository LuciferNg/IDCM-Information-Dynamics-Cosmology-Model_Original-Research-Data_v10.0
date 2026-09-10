#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/08 — O1: D_H 徑向 BAO 候選機制

DESI Lyα (z=2.33): D_H/rd = 8.600 ± 0.066 (0.77%)
IDCM 冇膨脹 → D_H = c/H(z) 冇直接對應。候選幾何定義:
  (a) dD_A/dz                      (現狀, +13.5%)
  (b) dD_L/dz, D_L = (1+z)^{1-n/p}·D_A   (O76 光度距離, n/p = γ₇/γ₂₀)
  (c) dD_C/dz, D_C = (1+z)·D_A           (ΛCDM comoving 對應)
  (d) D_H = R_world·dℓ/dz = R/((1+z)ln4) (紅移層幾何)
  (e) D_H = (1+z)^{-n/p}·dD_A/dz  (O76 指數修正)
"""
import mpmath as mp
mp.mp.dps = 40

def eq(a, b, tol):
    return abs(a - b) < tol

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

print("="*70)
print("O167 scripts/08 — D_H 徑向候選機制 (Lyα z=2.33)")
print("="*70)

R = mp.mpf("4129.94")
phi = (1 + mp.sqrt(5)) / 2
C_D = mp.mpf("-0.1697")
n_over_p = mp.mpf("0.14262")    # γ₇/γ₂₀ (O76)
rd = mp.mpf("147.09")           # rd_corrected (V3)
DESI_DH_rd = mp.mpf("8.600")
DESI_err = mp.mpf("0.066")

def ell_of(z):
    return mp.log(1+z, 4)

def D_A(z, use_delta=True):
    ell = ell_of(z)
    base = R * (1 - 4**(-ell))
    corr = 1 + 2*phi**(-1)*ell
    if use_delta:
        corr += C_D * (ell - mp.mpf("0.5")) * (1 - 4**(-ell))
    return base * corr

def ddz(f, z, h=mp.mpf("1e-5")):
    return (f(z+h) - f(z-h)) / (2*h)

z_lya = mp.mpf("2.33")

# 候選
cands = []
# (a) dD_A/dz
cands.append(("(a) dD_A/dz", ddz(D_A, z_lya)))
# (b) dD_L/dz, D_L = (1+z)^{1-n/p}·D_A
def D_L(z):
    return (1+z)**(1-n_over_p) * D_A(z)
cands.append(("(b) dD_L/dz", ddz(D_L, z_lya)))
# (c) dD_C/dz, D_C = (1+z)·D_A
def D_C(z):
    return (1+z) * D_A(z)
cands.append(("(c) dD_C/dz", ddz(D_C, z_lya)))
# (d) R/((1+z)ln4)
cands.append(("(d) R/((1+z)ln4)", R/((1+z_lya)*mp.log(4))))
# (e) (1+z)^{-n/p}·dD_A/dz
cands.append(("(e) (1+z)^(-n/p)·dD_A/dz", (1+z_lya)**(-n_over_p) * ddz(D_A, z_lya)))

print(f"{'候選':<30} {'IDCM D_H/rd':<12} {'dev':<9} {'σ'}")
best = (mp.inf, None)
for name, dh in cands:
    dh_rd = dh / rd
    dev = (dh_rd - DESI_DH_rd)/DESI_DH_rd
    sig = (dh_rd - DESI_DH_rd)/DESI_err
    print(f"{name:<30} {mp.nstr(dh_rd,8):<12} {float(dev)*100:+.2f}%  {float(sig):+.1f}σ")
    if abs(sig) < best[0]:
        best = (abs(sig), name)
print(f"\n最佳: {best[1]}")

# 裁決
chk("候選 (a)-(e) 有冇 |σ| < 3?", best[0] < 3)
print(f"    最佳 |σ| = {float(best[0]):.1f} (全部候選 ≥ {float(best[0]):.1f}σ)")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("裁決: 五種幾何定義全 miss → D_H 徑向 = c/H(z) 膨脹率概念, IDCM 冇對應 → 🔴 結構缺口")
