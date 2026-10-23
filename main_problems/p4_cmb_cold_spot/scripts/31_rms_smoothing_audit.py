#!/usr/bin/env python3
"""驗證 O83 handoff: Planck 全天空 RMS + 14.57° 平滑 claim (P4 修復用)"""
import numpy as np

p = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o171_a5_partition_theory/data/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt"
d = np.loadtxt(p)
ell, Dl = d[:, 0], d[:, 1]
Tcmb = 2.7255e6
Cl = Dl * 2 * np.pi / (ell * (ell + 1))
m = (ell >= 2) & (ell <= 2507)
l, C = ell[m], Cl[m]

var = np.sum((2 * l + 1) * C) / (4 * np.pi)
print(f"N ell = {len(l)} (expect 2506)")
print(f"full-sky RMS (l=2..2507) = {np.sqrt(var):.4f} uK   (O83: 110.777)")
print(f"dT/T                      = {np.sqrt(var)/Tcmb:.6e}   (O83: 4.0645e-5)")

eps5_8 = (0.1545084972**5) / 8
print(f"\neps^5/8 = {eps5_8:.6e} = {eps5_8*Tcmb:.4f} uK")
print(f"偏差 (eps5/8 vs Planck) = {100*(eps5_8 - np.sqrt(var)/Tcmb)/(np.sqrt(var)/Tcmb):+.1f}%")


def rms_sm(fwhm_deg):
    sig = np.radians(fwhm_deg) / np.sqrt(8 * np.log(2))
    bl2 = np.exp(-l * (l + 1) * sig ** 2)
    v = np.sum((2 * l + 1) * C * bl2) / (4 * np.pi)
    return np.sqrt(v), np.sqrt(v) / Tcmb


print("\n平滑角 -> RMS(uK), dT/T, vs eps5/8 偏差")
for f in [1.0, 4.17, 10.0, 13.0, 14.57, 15.0]:
    r, dt = rms_sm(f)
    print(f"  {f:>6.2f}deg: {r:8.3f} uK  {dt:.4e}  dev={100*(dt-eps5_8)/eps5_8:+.1f}%")

# bisection for exact angle
lo, hi = 5.0, 40.0
for _ in range(80):
    mid = (lo + hi) / 2
    if rms_sm(mid)[0] > eps5_8 * Tcmb:
        lo = mid
    else:
        hi = mid
print(f"\n要達 eps^5/8 = 30.00 uK 需平滑角 = {(lo+hi)/2:.4f} deg  (O83: 14.57)")
print(f"F7 = {13}deg, L7 = {29}deg, L5 = {11}deg -> 14.57 唔等於任何結構角")
