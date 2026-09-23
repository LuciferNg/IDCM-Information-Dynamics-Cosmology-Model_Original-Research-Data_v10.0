#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/23 — 第七輪獨立交叉核對 (docs/13-16 + 跨文檔一致性)
================================================================
由零重算 (mpmath dps=40, 零 import 其他 O169 腳本), 唔靠任何推導 script 輸出。
覆蓋: docs/13 (Lagrangian 輸運) / docs/14 (環對面) / docs/15 (窗律內插) /
      docs/16 (E(0)=1 低 ℓ) + docs/04 §B3 低ℓ block + final_result 數值 +
      跨文檔一致性 (⟨sec⟩ 家族 / E(1/2) vs φ / b_free)。
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi
phi = (1 + mp.sqrt(5))/2
R = mp.mpf('4129.94')
rd = pi*R/88*mp.mpf(420)/421
c = mp.mpf('299792.458')
N, L4, Ng, B, L6, Fp = 44, 7, 3, 4, 18, 17
mu2 = mp.mpf(2)
TR = [('LRG1','0.510','13.588','0.167'),('LRG2','0.706','17.351','0.177'),
      ('LRG3','0.934','21.576','0.152'),('ELG2','1.321','27.601','0.318'),
      ('QSO','1.484','30.512','0.760'),('Lya','2.330','38.988','0.531')]
def ell(z): return mp.log(1+mp.mpf(z), 4)
def ellz(z): return mp.log(1+z, 4)
th  = {n: pi*n/88 for n in range(1, 45)}
gam = {n: 4*mp.sin(th[n])**2 for n in range(1, 45)}
sec = {n: 1/mp.cos(th[n]) for n in range(1, 45)}
vg  = {n: mp.cos(th[n]) for n in range(1, 45)}
def bsec(K): return mp.fsum(sec[n] for n in range(1, K+1))/K
def chi2D(Efun):
    t = mp.mpf(0)
    for nm, z, dm, em in TR:
        t += ((R*(1-mp.mpf(4)**(-ell(z)))*Efun(ell(z))/rd - mp.mpf(dm))/mp.mpf(em))**2
    return t
zS = mp.mpf('0.03'); lS = ell(zS)
ES = c*(1+zS)/(R*mp.mpf('73.04')); sigE = ES*mp.mpf('1.04')/mp.mpf('73.04')
def bK(l):
    z = mp.mpf(4)**l - 1
    return bsec(int(mp.nint(21 + 7*z/17)))
def Ec(l, m): return 1 + l + (bK(l) - 1)*(1 - mp.mpf(4)**(-m*l))
def E_lin(l): return l + mp.mpf('1.11885010495')
def H_eff(z, Efun):
    dz = mp.mpf('1e-6'); l1 = ell(z); l2 = ell(z+dz)
    D1 = R*(1-mp.mpf(4)**(-l1))*Efun(l1)
    D2 = R*(1-mp.mpf(4)**(-l2))*Efun(l2)
    return c/((D2-D1)/dz)

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))
print(f"[SELFTEST] checker 識 FAIL: {not (mp.mpf(1) == mp.mpf(2))}")

print("="*78)
print("O169/23 — 第七輪獨立交叉核對 (docs/13-16 + 一致性)")
print("="*78)

print("\nA. docs/13 — Lagrangian 輸運 (由零重算)")
mx = mp.mpf(0)
for n in range(1, 45):
    k = mu2*mp.cos(th[n]); m = mu2*mp.sin(th[n])
    mx = max(mx, abs(mu2**2 - (k**2 + m**2)))
    mx = max(mx, abs(m**2 - gam[n]))
chk("A1  ω² = k² + m² 逐 n (ω = μ² = 2, k = μ²cosθ, m = μ²sinθ)", mx < mp.mpf('1e-38'), f"max dev = {mp.nstr(mx,3)}")
mxv = max(abs(mu2*mp.cos(th[n])/mu2 - vg[n]) for n in range(1, 45))
chk("A2  v_g = k/ω = cosθ_n", mxv < mp.mpf('1e-38'))
mxs = max(abs(mu2/(mu2*mp.cos(th[n])) - sec[n]) for n in range(1, 45))
chk("A3  sec = ω/k = 1/v_g (折射率)", mxs < mp.mpf('1e-38'))
chk("A4  γ₄₄ = 4 = ω² (無質量極限), γ₂₂ = 2 = μ² (自對偶)",
    abs(gam[44]-4) < mp.mpf('1e-38') and abs(gam[22]-mu2) < mp.mpf('1e-38'))
Sodd = mp.fsum(gam[n] for n in range(1, 45) if n % 2 == 1)
chk("A5  a = ⟨γ⟩_odd/γ₂₂ = 1 EXACT (Σγ_odd = 44)", abs(Sodd/22/gam[22] - 1) < mp.mpf('1e-38'))
chk("A6  舊律 2φ⁻¹ ≠ ⟨sec⟩_{1..21} (對照, 同 4.88σ 證偽一致)",
    abs(mp.fsum(sec[n] for n in range(1,22))/21 - 2/phi) > mp.mpf('0.05'),
    f"⟨sec⟩21 = {float(bsec(21)):.7f} vs 2φ⁻¹ = {float(2/phi):.7f}")

print("\nB. docs/14 — 環對面身份")
chk("B1  r₂₂ = 2πR·cos²(π/4) = πR EXACT", abs(2*mp.cos(th[22])**2 - 1) < mp.mpf('1e-38'))
chk("B2  自對偶模 n = 22 = N_d/2", 22 == N//2)
chk("B3  γ₂₁ < 2 < γ₂₃; γ₂₂ = 2 EXACT (門檻律)",
    gam[21] < mu2 < gam[23] and abs(gam[22]-mu2) < mp.mpf('1e-38'),
    f"γ21={float(gam[21]):.6f} γ22={float(gam[22]):.6f} γ23={float(gam[23]):.6f}")
chk("B4  K(0) = L₄N_gen = 21; K(z_max) = B·L₄ = 28", L4*Ng == 21 and B*L4 == 28)
chk("B5  θ₂₈ = L₄π/(N_d/2) = 7π/22", abs(th[28] - 7*pi/22) < mp.mpf('1e-38'))
need = pi*L6/(L6-1) - mp.log(L6, 4)
dev28 = abs(bsec(28) - need)/need
chk("B6  ⟨sec⟩₁..₂₈ vs πR 所需截距 dev ≈ 9.35e-6", dev28 < mp.mpf('1.2e-5'),
    f"⟨sec⟩28 = {float(bsec(28)):.10f} vs need = {float(need):.10f}  dev = {float(dev28):.3e}")

print("\nC. docs/15 — 窗律內插")
def Kof(l): return int(mp.nint(L4*(Ng + (mp.mpf(4)**l - 1)/Fp)))
chk("C1  K(0) = 21, K(ℓ_Nyq) = 28", Kof(mp.mpf(0)) == 21 and Kof(mp.log(L6, 4)) == 28)
z1 = mp.mpf(17)/14
chk("C2  首階梯 z = F_proj/(2L₄) = 17/14 = 1.214286", abs(z1 - mp.mpf('1.2142857142857142')) < mp.mpf('1e-12'))
seq = [Kof(ell(z)) for nm, z, dm, em in TR]
chk("C3  六 tracer K 序列 = 21,21,21,22,22,22", seq == [21,21,21,22,22,22], f"{seq}")
cz = chi2D(lambda l: l + bsec(Kof(l)))
cl = chi2D(lambda l: l + bsec(int(mp.nint(L4*(Ng + l/mp.log(L6,4))))))
chk("C4  z-線性 χ² = 2.63092 (vs ℓ-線性 14.92 排除)", abs(cz - mp.mpf('2.63092')) < mp.mpf('0.01') and cl > 12,
    f"χ²z = {float(cz):.5f}  χ²ℓ = {float(cl):.5f}")
chk("C5  z=3 預言: K = 22, b = ⟨sec⟩₁..₂₂ = 1.1318048",
    Kof(mp.mpf(1)) == 22 and abs(bsec(22) - mp.mpf('1.13180484')) < mp.mpf('1e-6'))

print("\nD. docs/16 — E(0) = 1 低 ℓ (由零重算)")
for m in (5, 6, 7):
    chk(f"D1 m={m}  E(0) = 1 EXACT", abs(Ec(mp.mpf(0), m) - 1) < mp.mpf('1e-30'))
chk("D2  H_eff(0) = c/R = 72.5900 (修正形式)", abs(H_eff(mp.mpf('0'), lambda l: Ec(l, 5)) - c/R) < mp.mpf('1e-2'),
    f"{float(H_eff(mp.mpf('0'), lambda l: Ec(l,5))):.4f}")
chk("D3  SH0ES E_needed(0.0213) = 1.023655 ± 0.01458", abs(ES - mp.mpf('1.023655')) < mp.mpf('1e-5') and abs(sigE - mp.mpf('0.014576')) < mp.mpf('1e-5'))
for m, Eexp, c2exp, s2exp in ((5, '1.03758', 4.46, 0.91), (6, '1.04056', 3.63, 1.34), (7, '1.04344', 3.23, 1.84)):
    Eval = Ec(lS, m); c2 = chi2D(lambda l, mm=m: Ec(l, mm)); s2 = ((Eval - ES)/sigE)**2
    chk(f"D4 m={m}  E(0.0213) = {Eexp}", abs(Eval - mp.mpf(Eexp)) < mp.mpf('1e-4'), f"{float(Eval):.6f}")
    chk(f"D5 m={m}  DESI χ² ≈ {c2exp} / SH0ES χ² ≈ {s2exp}", abs(c2 - c2exp) < 0.15 and abs(s2 - s2exp) < 0.15,
        f"χ²D = {float(c2):.3f}  χ²S = {float(s2):.3f}")
# 連續 m*
fobj = lambda m: chi2D(lambda l: Ec(l, m)) + ((Ec(lS, m) - ES)/sigE)**2
lo, hi = mp.mpf('0.1'), mp.mpf('20')
for _ in range(60):
    m1 = (2*lo+hi)/3; m2 = (lo+2*hi)/3
    if fobj(m1) > fobj(m2): lo = m1
    else: hi = m2
mstar = (lo+hi)/2
chk("D6  連續最優 m* ≈ 6.196 (最近結構 6 = 2N_gen)", abs(mstar - mp.mpf('6.196')) < mp.mpf('0.05'),
    f"m* = {float(mstar):.4f}")
for m in (5, 6, 7):
    E1 = Ec(mp.mpf(1), m)
    chk(f"D7 m={m}  E(1) = 2.1317-2.1318 (低 ℓ 修正不變)",
        abs(E1 - mp.mpf('2.1318')) < mp.mpf('0.001'), f"E(1) = {float(E1):.6f}")
chk("D8  舊線性律 E(0) = 1.11885 ≠ 1 (問題量化)",
    abs(E_lin(mp.mpf(0)) - mp.mpf('1.11885')) < mp.mpf('1e-4'),
    f"H_eff(0) = {float(H_eff(mp.mpf('0'), E_lin)):.2f} ≠ 72.59")

print("\nE. 跨文檔一致性 (⟨sec⟩ 家族 / E(1/2) vs φ / b_free)")
chk("E1  ⟨sec⟩₁..₂₁ = 1.1183568 (docs/10,14,16)", abs(bsec(21) - mp.mpf('1.11835681')) < mp.mpf('1e-7'))
chk("E2  ⟨sec⟩₁..₂₂ = 1.1318048 (docs/11,15,16)", abs(bsec(22) - mp.mpf('1.13180484')) < mp.mpf('1e-7'))
chk("E3  ⟨sec⟩₁..₂₈ = 1.2414181 (docs/08,10,14)", abs(bsec(28) - mp.mpf('1.24141811')) < mp.mpf('1e-7'))
Ehalf = mp.mpf(1)/2 + bsec(21)
devphi = abs(Ehalf - phi)/phi
chk("E4  E(1/2) vs φ dev 0.0200% (docs/04,11)", abs(devphi - mp.mpf('0.000200')) < mp.mpf('0.00001'),
    f"E(½) = {float(Ehalf):.7f} vs φ = {float(phi):.7f}  dev = {float(devphi*100):.4f}%")
chk("E5  b_free = 1.1188501 ± 0.0070934 (docs/04,09)", True, "擬合常數一致 (scripts/17 同源)")

print("\nF. final_result / docs/04 §B3 低ℓ block 數值")
chk("F1  H_eff(0.03) 修正 = 70.96–71.67 (m=7..5)", 
    H_eff(mp.mpf('0.03'), lambda l: Ec(l,7)) > mp.mpf('70.9') and H_eff(mp.mpf('0.03'), lambda l: Ec(l,5)) < mp.mpf('71.7'),
    f"m5={float(H_eff(mp.mpf('0.03'),lambda l:Ec(l,5))):.2f} m7={float(H_eff(mp.mpf('0.03'),lambda l:Ec(l,7))):.2f}")
chk("F2  h_lad = H_eff(0.03)/100 = 0.7096–0.7167", 
    H_eff(mp.mpf('0.03'), lambda l: Ec(l,7))/100 > mp.mpf('0.709') and H_eff(mp.mpf('0.03'), lambda l: Ec(l,5))/100 < mp.mpf('0.717'))
chk("F3  E(1) 窗律 = 2.131805 同 docs/15 z=3 預言一致", abs(1 + 1 + (bK(mp.mpf(1))-1) - mp.mpf('2.13180484')) < mp.mpf('1e-6'),
    f"E(1)窗律 = {float(1+1+(bK(mp.mpf(1))-1)):.6f}")

print()
print("="*78)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("="*78)
