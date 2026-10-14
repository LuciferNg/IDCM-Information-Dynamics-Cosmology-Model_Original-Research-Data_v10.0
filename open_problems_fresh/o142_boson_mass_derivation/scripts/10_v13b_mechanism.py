#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13b - mechanism hunt: why Lambda_IDCM = sqrt(lmax)*M0*N_gen/L5?

Question: what is the spectral identity of (Lambda_IDCM/M0) = 1.6230604?
Candidates: gamma_n combos, omega ratios, L_n/F_n combos, phi terms.
Also test: is sqrt(lmax)*N_gen/L5 expressible via T-hat invariants?
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2
omega = lambda n: 2*mp.sin(mp.pi*n/88)

M0 = mp.mpf('27.900915')
N_d = mp.mpf(44); B = mp.mpf(4); N_gen = mp.mpf(3)
lam_max = 36 - 1/gamma(20)
strong = mp.sqrt(lam_max)*M0
Lam_IDCM = strong*N_gen/L(5)
ratio = Lam_IDCM/M0          # 1.6230604  <- target identity

print("strong_scale =", mp.nstr(strong, 10), "MeV")
print("Lambda_IDCM  =", mp.nstr(Lam_IDCM, 10), "MeV")
print("Lambda/M0    =", mp.nstr(ratio, 12), "  <-- target identity")

print("\n=== Candidates for ratio 1.6230604 ===")

# A. phi - related
print("\n[A] phi combos")
print("  phi           =", mp.nstr(phi, 12), "dev", mp.nstr((phi-ratio)/ratio*100, 5), "%")
print("  1 + 1/phi    =", mp.nstr(1+1/phi, 12), "dev", mp.nstr((1+1/phi-ratio)/ratio*100, 5), "%")
print("  phi^2/phi_?   no")
print("  sqrt(phi+1)  =", mp.nstr(mp.sqrt(phi+1), 12), "dev", mp.nstr((mp.sqrt(phi+1)-ratio)/ratio*100, 5), "%")

# B. gamma_n ratios / combos
print("\n[B] gamma/omega combos")
for n in [1, 3, 7, 19, 20, 21, 25, 41, 44]:
    g = gamma(n)
    print(f"  gamma_{n:2d} = {mp.nstr(g,10)}  ratio/g = {mp.nstr(ratio/g,10)}")
# sqrt(gamma_n) = omega_n
for n in [3, 7, 11, 19, 20, 21, 25, 32, 41]:
    w = omega(n)
    dev = (w - ratio)/ratio*100
    if abs(dev) < 5:
        print(f"  omega_{n:2d} = {mp.nstr(w,12)} dev {mp.nstr(dev,5)}%")
print("  omega_44 =", mp.nstr(omega(44), 8))

# C. ratios of omega
print("\n[C] omega ratios (near 1.62)")
for a in [19, 20, 21, 25, 32, 41, 44]:
    for b in [3, 7, 11, 13, 19]:
        r = omega(a)/omega(b)
        dev = (r-ratio)/ratio*100
        if abs(dev) < 2:
            print(f"  omega_{a}/omega_{b} = {mp.nstr(r,10)} dev {mp.nstr(dev,4)}%")

# D. sqrt(lmax) combos with T-hat numbers
print("\n[D] sqrt(lmax)/k  or  sqrt(lmax)*k/(m)")
sl = mp.sqrt(lam_max)
print("  sqrt(lmax) =", mp.nstr(sl, 10))
for k in [1,2,3,4,5,7,8,11]:
    print(f"  sqrt(lmax)/{k:2d} = {mp.nstr(sl/k, 10)}  (target/this = {mp.nstr(ratio/(sl/k), 8)})")
# find integer a,b: ratio = sqrt(lmax)*a/b -> a/b = ratio/sqrt(lmax) = 0.272727
target_ab = ratio/(sl)
print("\n  a/b target = ratio/sqrt(lmax) =", mp.nstr(target_ab, 12), " <-- expect 3/11 =", mp.nstr(mp.mpf(3)/11, 12))
print("  dev 3/11 vs target =", mp.nstr((mp.mpf(3)/11 - target_ab)/target_ab*100, 6), "%")
# why 3/11?  is 3/11 = N_gen/L5 special?
print("  N_gen/L5 =", mp.nstr(N_gen/L(5), 12))
print("  B/L4     =", mp.nstr(B/L(4), 12))
print("  F5/L6    =", mp.nstr(F(5)/L(6), 12))

# E. phi + gamma_1
print("\n[E] phi + gamma_1 (0.004% hit from earlier check?)")
for n in [1, 2, 3, 7]:
    print(f"  phi + gamma_{n} = {mp.nstr(phi+gamma(n), 12)}  dev {mp.nstr((phi+gamma(n)-ratio)/ratio*100, 6)}%")
print("  phi + gamma1      =", mp.nstr(phi+gamma(1), 12))
print("  target            =", mp.nstr(ratio, 12))
print("  1/(phi+gamma1)    =", mp.nstr(1/(phi+gamma(1)), 12))

# F. L/F combos
print("\n[F] L/F combos near 1.623")
for a in [1,2,3,4,5,6,7,8,9,11,13]:
    for b in [1,2,3,4,5,6,7,8,9,11,13]:
        for op in ['/', '*']:
            va = L(a) if a <= 13 else F(a-8)
            vb = L(b) if b <= 13 else F(b-8)
            r = va/vb if op=='/' else va*vb
            dev = (r-ratio)/ratio*100
            if abs(dev) < 0.5:
                print(f"  {op} {a}:{b} = {mp.nstr(r,10)} dev {mp.nstr(dev,4)}%")

# G. exact check: sqrt(lam_max)*3/11 vs (phi+gamma1)
print("\n[G] comparison")
r1 = sl*mp.mpf(3)/11
r2 = phi + gamma(1)
print("  sqrt(lmax)*3/11 =", mp.nstr(r1, 15))
print("  phi+gamma1      =", mp.nstr(r2, 15))
print("  deviation       =", mp.nstr((r1-r2)/r2*100, 8), "%")