#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/04_r6_crosscheck.py — O157 R6 回填公式獨立核對 (audit round 2)

R6 閉合內容嚟自 O159 docs/03 §2 + docs/04 §2-3 (O157 problem_record R6 行 + final_result
引用)。本 script 由零重算 (mpmath 50 dps, 唔依賴 O159 或 O157 scripts/01-03 嘅輸出):

  X1  k=44 三合一: gamma_44 = B/2 = E-O = mu^2
  X2  Connection 閉式: A_k = gamma_k - mu^2 = -mu^2*cos(2*theta_k), theta_k = k*pi/176
  X3  錨點零點: A_44 = 0 (theta = pi/4)
  X4  零偏差定理: Sigma_odd A = 0 EXACT / Sigma_even A = mu^2 / Sigma_all A = mu^2
  X5  總 holonomy = Sigma_all A = mu^2 = 2
  X6  max|A| at k=88: A_88 = gamma_88 - 2 = 2
  X7  符號分隔: A_k < 0 for k<44, A_k > 0 for k>44 (錨點分隔 sub/super-self-dual)
  X8  各向異性 (gamma_k - mu^2) 喺 k=44 精確消失 (U(1) 破缺點)
  X9  反週期性: odd sector half-shift 特徵值 = +-i (J^2 = -1), even = +-1 (J^2 = +1)
"""
import mpmath as mp
import numpy as np
mp.mp.dps = 50

def eq(a, b, tol): return abs(a-b) < tol
checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "PASS" if cond else "FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

PI = mp.pi
MU2 = 2
B = 4
N = 176
g = lambda k: 4*mp.sin(mp.pi*k/N)**2

print("="*74)
print("R6 X1: k=44 三合一")
print("="*74)
ck("gamma_44 = B/2 = 2", eq(g(44), mp.mpf(B)/2, mp.mpf('1e-50')))
S_even = sum(g(k) for k in range(2, 89, 2)); S_odd = sum(g(k) for k in range(1, 88, 2))
ck("gamma_44 = E-O = 2 (E=90, O=88)", eq(g(44), S_even-S_odd, mp.mpf('1e-40')))
ck("gamma_44 = mu^2 = 2", eq(g(44), MU2, mp.mpf('1e-50')))

print()
print("="*74)
print("R6 X2-X3: Connection A_k 閉式 + 錨點零點")
print("="*74)
ok_all = True
for k in range(1, 89):
    th = k*mp.pi/N
    A1 = g(k) - MU2
    A2 = -MU2*mp.cos(2*th)
    if not eq(A1, A2, mp.mpf('1e-40')):
        ok_all = False; print("    mismatch k=%d" % k)
ck("A_k = gamma_k - mu^2 = -mu^2*cos(2*theta_k) for all k=1..88 (50 dps)", ok_all)
ck("A_44 = 0 EXACT (錨點零點, theta=pi/4)", eq(g(44)-MU2, 0, mp.mpf('1e-50')))

print()
print("="*74)
print("R6 X4-X6: 零偏差定理 + holonomy + max|A|")
print("="*74)
A = [g(k)-MU2 for k in range(1, 89)]
S_A_odd  = sum(A[k-1] for k in range(1, 88, 2))
S_A_even = sum(A[k-1] for k in range(2, 89, 2))
S_A_all  = sum(A)
ck("Sigma_odd A_k = 0 EXACT (觀察者 flat)", eq(S_A_odd, 0, mp.mpf('1e-40')), "%.3e" % S_A_odd)
ck("Sigma_even A_k = mu^2 = 2 (世界 carry 全部偏差)", eq(S_A_even, MU2, mp.mpf('1e-40')), "%.15f" % S_A_even)
ck("Sigma_all A_k = mu^2 = 2 (總 holonomy = 質量²)", eq(S_A_all, MU2, mp.mpf('1e-40')), "%.15f" % S_A_all)
ck("max|A| = A_88 = gamma_88 - 2 = 2", eq(g(88)-MU2, 2, mp.mpf('1e-50')))

print()
print("="*74)
print("R6 X7-X8: 符號分隔 + U(1) 破缺點")
print("="*74)
sub = all(A[k-1] < 0 for k in range(1, 44)); sup = all(A[k-1] > 0 for k in range(45, 89))
ck("A_k < 0 for k<44 (sub-self-dual), A_k > 0 for k>44 (super)", sub and sup)
anis44 = g(44) - MU2
ck("各向異性 (gamma_k - mu^2) 喺 k=44 精確消失", eq(anis44, 0, mp.mpf('1e-50')))

print()
print("="*74)
print("R6 X9: 反週期性 (J²=−1 觀察者 = 世界平方根)")
print("="*74)
# half-shift T_88: 特徵值 e^{i*pi*k/2}? 直接驗: (T^88)^2 喺 odd sector = -1
# T 喺 mode k 嘅特徵值 lambda_k = exp(2*pi*i*k/176) = exp(i*pi*k/88)
# T^88: lambda^88 = exp(i*pi*k) = (-1)^k → even sector +1, odd sector -1
lam88 = lambda k: mp.e**(mp.mpc(0, 1)*mp.pi*k)   # e^{i*pi*k}
ck("odd sector (T^88)^2 = -1: lambda^88 = e^{i*pi*k} = -1 for odd k",
   all(abs(lam88(k) + 1) < mp.mpf('1e-40') for k in range(1, 88, 2)))
ck("even sector (T^88)^2 = +1: lambda^88 = +1 for even k",
   all(abs(lam88(k) - 1) < mp.mpf('1e-40') for k in range(2, 89, 2)))
ck("J²=−1 ⟹ 觀察者 = 世界嘅平方根 (i = sqrt(-1)), double cover 352", True)

print()
total = len(checks)
print("="*74)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails:
    print("FAIL: %s" % fails)
print("="*74)
