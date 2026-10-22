#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/09 — 最終殘差表 (採用模型) + 全腳本一致性確認

採用模型: M(ℓ) = sec(π n_c/88), n_c = 25.5 (1+z<3) | 22 (1+z>3)
輸出: 每個 tracer 嘅 D_H/r_d 預言, 偏差 %, σ; M(ℓ) 表; χ² 匯總。
"""
import mpmath as mp
mp.mp.dps = 40
R = mp.mpf("4129.94"); rd = mp.mpf("147.088")
M_sh = mp.sec(mp.mpf("25.5")*mp.pi/88); M_dp = mp.sqrt(2); ell_t = mp.log(3, 4)

def ell(z): return mp.log(1 + mp.mpf(str(z)), 4)
def M(z):
    e = ell(z); return M_sh if e < ell_t else M_dp
def DH(z): return M(z)*R/((1+mp.mpf(str(z)))*mp.log(4))/rd

TR = [('LRG1',0.510,13.588,0.167,21.863,0.425),('LRG2',0.706,17.351,0.177,19.455,0.330),
      ('LRG3+ELG1',0.934,21.576,0.152,17.641,0.193),('ELG2',1.321,27.601,0.318,14.176,0.221),
      ('QSO',1.484,30.512,0.760,12.817,0.516),('Lya',2.330,38.988,0.531,8.632,0.101)]
VAL = [('LRG3',0.922,21.648,0.178,17.577,0.213),('ELG1',0.955,21.707,0.335,17.803,0.297)]

print("="*104); print("O170 scripts/09 — 最終殘差表 (M = sec(25.5π/88) | √2, ℓ_t = log₄3)"); print("="*104)
print(f"\n  M_shallow = sec(25.5π/88) = {float(M_sh):.6f}   M_deep = √2 = {float(M_dp):.6f}   ℓ_t = {float(ell_t):.6f}  (1+z=3)\n")
print(f"  {'tracer':12s} {'z':>6s} {'ℓ':>8s} {'M(ℓ)':>9s} {'D_H/r_d 預言':>13s} {'DESI':>7s} {'σ':>6s} {'dev':>8s} {'dev%':>8s}")
print("  " + "-"*96)
c6 = mp.mpf(0); c8 = mp.mpf(0)
for tag, lst in [("宇宙學 bin", TR), ("★驗證 tracer", VAL)]:
    print(f"  --- {tag} ---")
    for t,z,dm,sm,dh,sh in lst:
        p = DH(z); d = p - mp.mpf(str(dh)); sig = d/mp.mpf(str(sh))
        print(f"  {t:12s} {z:6.3f} {float(ell(z)):8.5f} {float(M(z)):9.6f} {float(p):13.4f} {dh:7.3f} {sh:6.3f} {float(sig):+8.2f} {float(100*d/mp.mpf(str(dh))):+7.2f}%")
        c8 += sig**2
        if lst is TR: c6 += sig**2
print("  " + "-"*96)
print(f"\n  χ²(D_H 6 宇宙學 bins) = {float(c6):.3f}/6  ({float(c6/6):.3f}/dof)")
c5 = c6 - ((DH(0.934) - mp.mpf('17.641'))/mp.mpf('0.193'))**2
print(f"  χ²(排除 LRG3+ELG1)   = {float(c5):.3f}/5  ({float(c5/5):.3f}/dof)")
print(f"  χ²(8 點含驗證)        = {float(c8):.3f}/8")
print(f"\n  M(ℓ) 表 (同一模型):")
for t,z,dm,sm,dh,sh in TR+VAL:
    print(f"    {t:12s} ℓ={float(ell(z)):.5f}  M_obs={float(mp.mpf(str(dh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R):.4f} ± {float(mp.mpf(str(sh))*rd*(1+mp.mpf(str(z)))*mp.log(4)/R):.4f}  M_model={float(M(z)):.6f}")
