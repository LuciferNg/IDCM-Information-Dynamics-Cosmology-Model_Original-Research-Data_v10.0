#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/04 — E(ℓ) 形狀統計裁決: 兩參數擬合區域 + 零參數候選 χ²

關鍵: D_M 六 tracer (DESI DR2 Table 6) 決定 E(ℓ) = D_M^obs·rd/[R(1−4^{−ℓ})]
      BGS 只有 D_V, 需要 D_H — 兩個選項 (a) dD_A/dz (O167 慣例) (b) O117 公式
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2
inv = 1/phi
pi = mp.pi
R = mp.mpf('4129.94')
rd = pi*R/88*mp.mpf(420)/421

DM = [  # name, z, D_M/rd, σ
    ('LRG1', mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167')),
    ('LRG2', mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177')),
    ('LRG3', mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152')),
    ('ELG2', mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318')),
    ('QSO',  mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760')),
    ('Lya',  mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531')),
]
BGS = ('BGS', mp.mpf('0.295'), mp.mpf('7.942'), mp.mpf('0.075'))
def ell(z): return mp.log(1+z, 4)

print("="*78)
print("O169/04 — E(ℓ) 統計裁決")
print("="*78)

# ---- E_req 表 ----
E = []
for n, z, dm, e in DM:
    l = ell(z); base = R*(1-4**(-l))
    E.append((n, l, dm*rd/base, e*rd/base))
print("\n--- E_req(ℓ) ---")
for n, l, Er, s in E:
    print(f"  {n:<6} ℓ={float(l):.4f}  E_req={float(Er):.5f} ± {float(s):.5f}")

# ---- 兩參數擬合 + 協方差 ----
A = mp.matrix(2,2); v = mp.matrix(2,1)
for n, l, Er, s in E:
    w = 1/s; f1 = 1; f2 = l
    A[0,0] += (w*f1)**2; A[0,1] += w*w*f1*f2; A[1,0] += w*w*f1*f2; A[1,1] += (w*f2)**2
    v[0] += w*w*f1*Er;   v[1] += w*w*f2*Er
sol = mp.lu_solve(A, v); Cm = A**-1
al, be = sol[0], sol[1]
sal, sbe = mp.sqrt(Cm[0,0]), mp.sqrt(Cm[1,1])
rho_ab = Cm[0,1]/(sal*sbe)
print(f"\n--- E = α + β·ℓ 兩參數擬合 ---")
print(f"  α = {mp.nstr(al,8)} ± {mp.nstr(sal,6)}    β = {mp.nstr(be,8)} ± {mp.nstr(sbe,6)}   ρ(α,β) = {mp.nstr(rho_ab,4)}")
print(f"  α vs √5/2 = {mp.nstr(mp.sqrt(5)/2,8)}: {float((al-mp.sqrt(5)/2)/sal):+.2f}σ")
print(f"  β vs 1: {float((be-1)/sbe):+.2f}σ")
print(f"  α vs 1+2φ⁻¹·0 = 1: {float((al-1)/sal):+.2f}σ   β vs 2φ⁻¹: {float((be-2*inv)/sbe):+.2f}σ")

def chi2_E(Efun):
    """D_M 六點 χ²"""
    t = mp.mpf(0)
    for n, l, Er, s in E:
        t += ((Efun(l)-Er)/s)**2
    return t

def resid_E(Efun):
    return [(n, (Efun(l)-Er)/s) for n, l, Er, s in E]

print("\n--- 零參數 / 單參數候選 (D_M 六點, 5 dof) ---")
cands = [
 ("OLD: 1+2φ⁻¹ℓ (δ=0)",              lambda l: 1+2*inv*l),
 ("OLD+δ: C=−0.1697 (ℓ−½)(1−4^{−ℓ})", lambda l: 1+2*inv*l - mp.mpf('0.1697')*(l-mp.mpf('0.5'))*(1-4**(-l))),
 ("OLD+δ: C=−φ⁻³(ℓ−½)",              lambda l: 1+2*inv*l - inv**3*(l-mp.mpf('0.5'))),
 ("★ NEW: ℓ + √5/2",                  lambda l: l + mp.sqrt(5)/2),
 ("★ NEW: (ℓ+½) + φ⁻¹",               lambda l: (l+mp.mpf('0.5')) + inv),
 ("NEW: ℓ + 1 + φ⁻³/2",               lambda l: l + 1 + inv**3/2),
 ("ℓ·(1+φ⁻³/2)+½",                    lambda l: l*(1+inv**3/2) + mp.mpf('0.5')),
 ("1 + ℓ",                            lambda l: 1 + l),
 ("1 + ℓ·(1−π/44)",                   lambda l: 1 + l*(1-pi/44)),
 ("ℓ + ⟨sec⟩_{1..22}−½",              lambda l: l + mp.fsum([1/mp.cos(n*pi/88) for n in range(1,23)])/22 - mp.mpf('0.5')),
 ("ℓ + 1/⟨v_g⟩_{1..22}−½",            lambda l: l + 1/(mp.fsum([mp.cos(n*pi/88) for n in range(1,23)])/22) - mp.mpf('0.5')),
]
for name, f in cands:
    c2 = chi2_E(f)
    r = resid_E(f)
    print(f"  {name:<36} χ² = {float(c2):>7.3f}/5   worst {max(float(abs(x[1])) for x in r):.2f}σ")
    print(f"      σ: " + " ".join(f"{x[0]}{float(x[1]):+.2f}" for x in r))

# ---- 單參數擬合: E = ℓ + c ----
num = mp.mpf(0); den = mp.mpf(0)
for n, l, Er, s in E:
    w = 1/s; num += w*w*(Er-l); den += w*w
c_best = num/den
print(f"\n--- E = ℓ + c 單參數擬合 ---")
print(f"  c = {mp.nstr(c_best,8)}   (√5/2 = {mp.nstr(mp.sqrt(5)/2,8)}, dev {float((c_best-mp.sqrt(5)/2)/(mp.sqrt(5)/2)*100):+.4f}%)")
print(f"  χ²(c_best) = {float(chi2_E(lambda l: l+c_best)):.3f}/5")
sc = 1/mp.sqrt(den)
print(f"  σ(c) = {mp.nstr(sc,6)}  → √5/2 偏離 {float((mp.sqrt(5)/2-c_best)/sc):+.2f}σ")

# ---- 單參數擬合: E = α + ℓ ----
num = mp.mpf(0); den = mp.mpf(0)
for n, l, Er, s in E:
    w = 1/s; num += w*w*(Er-l); den += w*w
# 同上 (c = α)
print(f"\n--- E = α + ℓ (同 c) : α = {mp.nstr(c_best,8)} vs √5/2 dev {float((c_best-mp.sqrt(5)/2)/(mp.sqrt(5)/2)*100):+.4f}%")

# ---- rd 敏感度 ----
print("\n--- rd 敏感度 (E = ℓ + √5/2 嘅 χ²) ---")
for rdv, tag in [(pi*R/88, 'rd_idcm=πR/88=147.442'), (pi*R/88*mp.mpf(420)/421, 'rd_corr=147.088')]:
    E2 = []
    for n, z, dm, e in DM:
        l = ell(z); base = R*(1-4**(-l))
        E2.append((n, l, dm*rdv/base, e*rdv/base))
    c2 = mp.mpf(0); worst=0
    for n, l, Er, s in E2:
        zz = ((l+mp.sqrt(5)/2)-Er)/s; c2 += zz**2; worst=max(worst,abs(zz))
    print(f"  {tag:<28} χ² = {float(c2):.3f}/5  worst {float(worst):.2f}σ")

# ---- BGS D_V ----
print("\n--- BGS D_V 檢定 (E = ℓ+√5/2 vs OLD) ---")
def DA_new(z): l=ell(z); return R*(1-4**(-l))*(l+mp.sqrt(5)/2)
def DA_old(z): l=ell(z); return R*(1-4**(-l))*(1+2*inv*l)
def DA_oldd(z):
    l=ell(z); return R*(1-4**(-l))*(1+2*inv*l-mp.mpf('0.1697')*(l-mp.mpf('0.5'))*(1-4**(-l)))
def DH(f, z):
    h=mp.mpf('1e-8'); return (f(z+h)-f(z-h))/(2*h)
for tag, f in [('NEW ℓ+√5/2', DA_new), ('OLD δ=0', DA_old), ('OLD+δ', DA_oldd)]:
    z = BGS[1]
    dv = (z*f(z)**2*DH(f,z))**(mp.mpf(1)/3)/rd
    print(f"  {tag:<14} D_V/rd = {float(dv):.4f}  vs {float(BGS[2])}  → {float((dv-BGS[2])/BGS[3]):+.2f}σ")
    # O117 D_H 版本
    l = ell(z); dk0 = inv**3*mp.e**(-(l-mp.mpf('0.5'))**2/(2*(mp.mpf('0.5')*mp.log(phi,4))**2))
    dgd = -mp.mpf('0.226311')*(l-mp.mpf('0.5'))*(1-4**(-l))
    dh117 = R*(1+dk0+dgd)/(1+z)
    dv2 = (z*f(z)**2*dh117)**(mp.mpf(1)/3)/rd
    print(f"                 (O117 D_H) D_V/rd = {float(dv2):.4f} → {float((dv2-BGS[2])/BGS[3]):+.2f}σ")

print("\nRESULT: 見上")
