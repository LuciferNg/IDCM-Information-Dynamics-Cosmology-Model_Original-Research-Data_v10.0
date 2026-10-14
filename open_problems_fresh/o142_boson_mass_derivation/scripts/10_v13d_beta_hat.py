#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13d - QCD beta coefficients at Nf=6: T-hat identities?

Check whether SM beta-function coefficients at N_f=6 are T-hat invariants:
b0 = 11 - 2Nf/3        (1-loop, MS-bar)
b1 = 102 - 38Nf/3      (2-loop)
b2 = 2857/2 - 5033Nf/18 + 325Nf^2/54              (3-loop, MS-bar)
b3 = (150653/486 - 449/9 z3) + Nf(-39143/162 + 136/3 z3)
     + Nf^2(1093/729 - 32/27 z3) + Nf^3(10475/8748 - 224/243 z3)   (4-loop)
z3 = zeta(3) = 1.202056903159...
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)

Nf = mp.mpf(6)

b0 = 11 - 2*Nf/3
b1 = 102 - 38*Nf/3
z3 = mp.zeta(3)
b2 = mp.mpf(2857)/2 - mp.mpf(5033)*Nf/18 + mp.mpf(325)*Nf*Nf/54
b3 = (mp.mpf(150653)/486 - mp.mpf(449)/9*z3) \
     + Nf*(-mp.mpf(39143)/162 + mp.mpf(136)/3*z3) \
     + Nf*Nf*(mp.mpf(1093)/729 - mp.mpf(32)/27*z3) \
     + Nf*Nf*Nf*(mp.mpf(10475)/8748 - mp.mpf(224)/243*z3)

print("Nf = 6, MS-bar")
print("b0 =", mp.nstr(b0, 15))
print("b1 =", mp.nstr(b1, 15))
print("b2 =", mp.nstr(b2, 15))
print("b3 =", mp.nstr(b3, 15))

print("\n=== T-hat identity check ===")
print("b0 vs L4 (Tr T^4):", mp.nstr(L(4), 12), " diff:", mp.nstr(b0-L(4), 8))
print("b1 vs 2*F7:", mp.nstr(2*F(7), 12), " diff:", mp.nstr(b1-2*F(7), 8))

# b2 = -65/2 = -F5*F7/2 ?
print("\nb2 =", mp.nstr(b2, 15), "= -65/2:", mp.nstr(-mp.mpf(65)/2, 15), " diff:", mp.nstr(b2+mp.mpf(65)/2, 8))
print("65 = F5*F7 = 5*13:", mp.nstr(F(5)*F(7), 12))
print("b2 = -F5*F7/2 ? diff:", mp.nstr(b2 + F(5)*F(7)/2, 8))

# b3 candidates
print("\nb3 =", mp.nstr(b3, 15))
for (name, val) in [
    ("-F7^2/2", -F(7)**2/2),
    ("-L6^2/2", -L(6)**2/2),
    ("-F9*F5", -F(9)*F(5)),
    ("-851", mp.mpf(-851)),
    ("-850.77", mp.mpf('-850.77')),
]:
    print(f"  candidate {name:12s} = {mp.nstr(val,10)}  diff = {mp.nstr(b3-val, 6)}")

# general: find small a,b,c: b3 = a + b*sqrt(5) ?
# b3/...  check b3 mod simple rationals
print("\n=== b3 structural test: near-integer ratios ===")
for k in range(1, 13):
    print(f"  b3/({k}) = {mp.nstr(b3/k, 8)}")

# b2 structure: -65/2 = -(L5+F4?...)/2 .  65 = L4*? +? .. 65=5*13=F5*F7 EXACT
print("\n=== b2 as F5*F7/2 ===")
print("F5 =", mp.nstr(F(5), 8), " F7 =", mp.nstr(F(7), 8), " F5*F7 =", mp.nstr(F(5)*F(7), 8))
print("so b2 = -F5*F7/2  (3-loop, Nf=6)  EXACT")

# consistency: does b1 also admit 2F7? yes:
print("\nb1 = 102-38*6/3 = 26 = 2*F7  EXACT (O144 confirmed)")
print("b0 = 11-12/3 = 7 = L4  EXACT (O144 confirmed)")

# What about Nf=5 for comparison?
print("\n=== Nf=5 (PDG Lambda_5 reference) ===")
Nf5 = mp.mpf(5)
b0_5 = 11 - 2*Nf5/3
b1_5 = 102 - 38*Nf5/3
b2_5 = mp.mpf(2857)/2 - mp.mpf(5033)*Nf5/18 + mp.mpf(325)*Nf5*Nf5/54
print("b0_5 =", mp.nstr(b0_5, 10), " (= 23/3)")
print("b1_5 =", mp.nstr(b1_5, 10), " (=? F?)")
print("b2_5 =", mp.nstr(b2_5, 10))
print("23/3 = ? L?: L6/.. no. 23/3 = (F7+F8)/.. F7+F8=21+13?")

# Nf=6 uniqueness: verify b2=-F5*F7/2 forces Nf=6 only?
# b2(Nf) = -65/2 has roots from quadratic; check integer solutions
print("\n=== b2(Nf) = -F5*F7/2 solutions (quadratic) ===")
# (325/54)Nf^2 - (5033/18)Nf + (2857/2 + 65/2) = 0
# *54: 325 Nf^2 - 15099 Nf + (2857+65)*27 = 0 -> 2922*27=78894
# disc = 15099^2 - 4*325*78894
a_c, b_c, c_c = mp.mpf(325), mp.mpf(-15099), mp.mpf(78894)
disc = b_c*b_c - 4*a_c*c_c
print("discriminant =", mp.nstr(disc, 12))
r1 = (-b_c + mp.sqrt(disc))/(2*a_c)
r2 = (-b_c - mp.sqrt(disc))/(2*a_c)
print("roots:", mp.nstr(r1, 8), mp.nstr(r2, 8))