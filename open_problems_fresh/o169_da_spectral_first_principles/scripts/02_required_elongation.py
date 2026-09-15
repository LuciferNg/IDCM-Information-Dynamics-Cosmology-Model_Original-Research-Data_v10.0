#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/02 — 必需伸長因子 E_req(ℓ) 提取 + δ 形狀候選 χ² 比較

目標: 由 DESI DR2 BAO 七 tracer 反推 D_A(ℓ) = R(1−4^{−ℓ})·E(ℓ) 嘅 E_req(ℓ),
      再比較 δ 形狀候選, 搵出數據真正要求嘅形狀 (唔靠 O51/82 經驗式)。

模型:  D_A(ℓ) = R(1−4^{−ℓ})·(1 + 2φ⁻¹ℓ + δ(ℓ)),  ℓ = log₄(1+z)
       BGS 只有 D_V = (z·D_A²·D_H)^{1/3}, D_H = dD_A/dz (幾何導數, O167 慣例)
       R = 4129.94 Mpc, rd = πR/88·420/421 = 147.088 Mpc

數據: DESI DR2 Table 6 (arXiv 2503.14738) — O167 data/02 表
"""
import mpmath as mp
mp.mp.dps = 30

R    = mp.mpf('4129.94')
phi  = (1 + mp.sqrt(5)) / 2
phi_inv = 1/phi
rd   = mp.pi * R / 88 * mp.mpf(420)/421
C0   = mp.mpf('-0.1697')

TRACERS = [
    # name, z, D_M/rd, σ_M, D_H/rd, σ_H, ρ
    ('BGS',   mp.mpf('0.295'), None,                None,              None,                None,              None),
    ('LRG1',  mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167'), mp.mpf('21.863'), mp.mpf('0.425'), mp.mpf('-0.459')),
    ('LRG2',  mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177'), mp.mpf('19.455'), mp.mpf('0.330'), mp.mpf('-0.404')),
    ('LRG3',  mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152'), mp.mpf('17.641'), mp.mpf('0.193'), mp.mpf('-0.416')),
    ('ELG2',  mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318'), mp.mpf('14.176'), mp.mpf('0.221'), mp.mpf('-0.434')),
    ('QSO',   mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760'), mp.mpf('12.817'), mp.mpf('0.516'), mp.mpf('-0.500')),
    ('Lya',   mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531'), mp.mpf('8.632'),  mp.mpf('0.101'), mp.mpf('-0.431')),
]
BGS_DV, BGS_E = mp.mpf('7.942'), mp.mpf('0.075')

def ell_of(z): return mp.log(1+z, 4)

# ---------- 模型 ----------
def delta_of(ell, form, C):
    if form == 'A':   # O51/82 經驗式: C(ℓ−0.5)(1−4^{−ℓ})
        return C*(ell - mp.mpf('0.5'))*(1 - mp.mpf(4)**(-ell))
    if form == 'B':   # 純半整數位移: C(ℓ−1/2)
        return C*(ell - mp.mpf('0.5'))
    if form == 'C':   # 半整數 + Z₂ 對偶權重: C(ℓ−1/2)(1−4^{−ℓ})²
        return C*(ell - mp.mpf('0.5'))*(1 - mp.mpf(4)**(-ell))**2
    if form == 'D':   # 半整數 × γ 平均權重 (2N/(N+1) 邊界比): C(ℓ−1/2)·(1−4^{−ℓ})·44/45
        return C*(ell - mp.mpf('0.5'))*(1 - mp.mpf(4)**(-ell))*mp.mpf(44)/45
    if form == 'E':   # 無 δ
        return mp.mpf(0)
    raise ValueError(form)

def DA(z, form, C):
    ell = ell_of(z)
    return R*(1 - mp.mpf(4)**(-ell))*(1 + 2*phi_inv*ell + delta_of(ell, form, C))

def DH(z, form, C):
    h = mp.mpf('1e-8')
    return (DA(z+h, form, C) - DA(z-h, form, C)) / (2*h)

def DV(z, form, C):
    return (z*DA(z, form, C)**2*DH(z, form, C))**(mp.mpf(1)/3)

# ---------- 殘餘 ----------
def residuals(form, C):
    """回傳 [(name, ell, resid_sigma_DM, resid_sigma_DH, joint)]"""
    out = []
    for name, z, dm, em, dh, eh, rho in TRACERS:
        ell = ell_of(z)
        if name == 'BGS':
            dv = DV(z, form, C)/rd
            out.append((name, ell, None, None, (dv - BGS_DV)/BGS_E))
            continue
        pm = DA(z, form, C)/rd
        ph = DH(z, form, C)/rd
        rm = pm - dm
        rh = ph - dh
        cov = em*eh*rho
        det = em**2*eh**2 - cov**2
        chi2 = (rm**2*eh**2 + rh**2*em**2 - 2*cov*rm*rh)/det
        # 邊際 σ
        sm = rm/em
        sh = rh/eh
        out.append((name, ell, sm, sh, mp.sqrt(chi2)))
    return out

def chi2_of(form, C):
    tot = mp.mpf(0)
    for name, z, dm, em, dh, eh, rho in TRACERS:
        if name == 'BGS':
            tot += ((DV(z, form, C)/rd - BGS_DV)/BGS_E)**2
            continue
        pm = DA(z, form, C)/rd; ph = DH(z, form, C)/rd
        rm = pm - dm; rh = ph - dh
        cov = em*eh*rho; det = em**2*eh**2 - cov**2
        tot += (rm**2*eh**2 + rh**2*em**2 - 2*cov*rm*rh)/det
    return tot

print("="*76)
print("O169 scripts/02 — E_req(ℓ) 提取 + δ 形狀 χ² 比較")
print("="*76)
print(f"R = {R} Mpc,  rd = {mp.nstr(rd, 10)} Mpc,  2φ⁻¹ = {mp.nstr(2*phi_inv, 10)}")

# ---------- C1: 基線 (δ=0) 殘餘 ----------
print("\n=== C1: 基線殘餘 (δ=0) ===")
print(f"{'tracer':<7}{'z':>7}{'ℓ':>8}{'D_M/rd':>9}{'obs':>8}{'σ_M':>8}{'D_H/rd':>9}{'obs':>8}{'σ_H':>8}{'joint':>8}")
for name, ell, sm, sh, j in residuals('E', mp.mpf(0)):
    z = [t[1] for t in TRACERS if t[0] == name][0]
    if name == 'BGS':
        print(f"{name:<7}{float(z):>7.3f}{float(ell):>8.4f}{'—':>9}{'—':>8}{'—':>8}{'—':>9}{'—':>8}{'—':>8}{float(j):>8.2f}")
    else:
        t = [t for t in TRACERS if t[0] == name][0]
        print(f"{name:<7}{float(z):>7.3f}{float(ell):>8.4f}{float(DA(z,'E',mp.mpf(0))/rd):>9.3f}{float(t[2]):>8.3f}{float(sm):>8.2f}"
              f"{float(DH(z,'E',mp.mpf(0))/rd):>9.3f}{float(t[4]):>8.3f}{float(sh):>8.2f}{float(j):>8.2f}")
print(f"χ²(δ=0) = {mp.nstr(chi2_of('E', mp.mpf(0)), 8)}")

# ---------- C2: 必需伸長因子 E_req(ℓ) ----------
print("\n=== C2: 必需伸長因子 E_req(ℓ) = D_M^obs·rd / [R(1−4^{−ℓ})] ===")
print(f"{'tracer':<7}{'ℓ':>8}{'E_req':>10}{'σ(E)':>8}{'1+2φ⁻¹ℓ':>10}{'ΔE':>10}{'ΔE/σ':>8}{'ΔE/(ℓ−½)':>11}")
E_data = []
for name, z, dm, em, dh, eh, rho in TRACERS:
    if dm is None: continue
    ell = ell_of(z)
    base = R*(1 - mp.mpf(4)**(-ell))
    E_req = dm*rd/base
    sig = em*rd/base
    E_mod = 1 + 2*phi_inv*ell
    dE = E_req - E_mod
    E_data.append((ell, E_req, sig, dE))
    print(f"{name:<7}{float(ell):>8.4f}{float(E_req):>10.5f}{float(sig):>8.5f}{float(E_mod):>10.5f}"
          f"{float(dE):>10.5f}{float(dE/sig):>8.2f}{float(dE/(ell-mp.mpf('0.5'))):>11.5f}")

# ---------- C3: 形狀候選 χ² ----------
print("\n=== C3: δ 形狀候選 (C 自由擬合) ===")
from mpmath import findroot
for form, desc in [('A','C(ℓ−½)(1−4^{−ℓ})  [O51/82]'), ('B','C(ℓ−½)  [純半整數]'),
                   ('C','C(ℓ−½)(1−4^{−ℓ})²'), ('D','C(ℓ−½)(1−4^{−ℓ})·44/45')]:
    # 最佳 C: 用 D_M 六點最小二乘 (解析, 1 參數線性)
    num = mp.mpf(0); den = mp.mpf(0)
    for name, z, dm, em, dh, eh, rho in TRACERS:
        if dm is None: continue
        ell = ell_of(z)
        d = delta_of(ell, form, mp.mpf(1))     # C=1 時嘅 δ
        base = R*(1 - mp.mpf(4)**(-ell))
        # D = base·(1+2φ⁻¹ℓ+C·d); 對 C 線性
        a = base*d/(rd*em)                      # 每單位 C 嘅 σ 單位貢獻
        b = (base*(1+2*phi_inv*ell)/rd - dm)/em
        num += -a*b; den += a*a
    C_best = num/den
    r = residuals(form, C_best)
    r2 = chi2_of(form, C_best)
    worst = max(r, key=lambda t: abs(t[4]))
    print(f"  {form} {desc}")
    print(f"     C_best = {mp.nstr(C_best, 8)}   χ²(D_M+BGS) = {mp.nstr(r2, 6)}   最差 {worst[0]} {mp.nstr(worst[4],4)}σ")
    print(f"     σ: " + "  ".join(f"{t[0]}{float(t[4]):+.2f}" for t in r))

# 固定 C = −0.1697 比較
print("\n=== C4: 固定 C = −0.1697 ===")
for form in ['A', 'B', 'C', 'D']:
    r = residuals(form, C0)
    r2 = chi2_of(form, C0)
    print(f"  {form}: χ² = {mp.nstr(r2, 6)}   σ: " + "  ".join(f"{t[0]}{float(t[4]):+.2f}" for t in r))

# ---------- C5: 兩參數 (a·ℓ + b·(ℓ−½)) ----------
print("\n=== C5: E = 1 + a·ℓ + b·(ℓ−½) 兩參數擬合 (D_M 六點) ===")
import mpmath
A = mp.matrix(2, 2); v = mp.matrix(2, 1)
for name, z, dm, em, dh, eh, rho in TRACERS:
    if dm is None: continue
    ell = ell_of(z)
    base = R*(1 - mp.mpf(4)**(-ell))
    y = (dm*rd/base - 1)             # 需要嘅 (a·ℓ + b·(ℓ−½))
    w = base/(rd*em)                 # 權重 (σ 單位)
    f1 = ell; f2 = ell - mp.mpf('0.5')
    A[0,0] += w*w*f1*f1; A[0,1] += w*w*f1*f2; A[1,0] = A[0,1]; A[1,1] += w*w*f2*f2
    v[0] += w*w*f1*y;    v[1] += w*w*f2*y
sol = mp.lu_solve(A, v)
a_fit, b_fit = sol[0], sol[1]
print(f"  a = {mp.nstr(a_fit, 8)}   (2φ⁻¹ = {mp.nstr(2*phi_inv, 8)})")
print(f"  b = {mp.nstr(b_fit, 8)}   (C₀ = {mp.nstr(C0, 8)})")
print(f"  a − 2φ⁻¹ = {mp.nstr(a_fit - 2*phi_inv, 6)}")

print("\nRESULT: 見 C1-C5")
