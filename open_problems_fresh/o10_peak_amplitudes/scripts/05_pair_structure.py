#!/usr/bin/env python3
"""O10 05: 簡併對結構分析"""
import numpy as np, math

phi = (1+5**0.5)/2
eps = phi**-1/4

A = {1: 1.0, 2: 0.4523, 3: 0.4430, 4: 0.1820, 5: 0.1839, 6: 0.1282, 7: 0.1423}

P1 = 0.4476  # pair (2,3) avg
P2 = 0.1830  # pair (4,5) avg
P3 = 0.1353  # pair (6,7) avg

print('P2/P1 =', round(P2/P1, 4), '  P3/P2 =', round(P3/P2, 4))
print()
print('eps^2*17 =', round(eps**2*17, 4))
print('3/4 =', 0.75)
print()
print('S(m) = P_m/3eps:')
for i, P in enumerate([P1, P2, P3], 1):
    print(f'  pair {i}: {P/(3*eps):.4f}')
print()
print('phi^-2 =', round(phi**-2, 4))
print('phi^-3 =', round(phi**-3, 4))
print()
# 試: P_m 直接對比 3eps * phi^{-a(m)}
# P1 ~ 3eps (k=0)
# P2 ~ 3eps*phi^-2 = 0.1771 (dev 3.3%)
# P3 ~ ?
print('3eps*phi^-3 =', round(3*eps*phi**-3, 4))
print('P3 vs 3eps*phi^-3:', round(P3/(3*eps*phi**-3), 4))
print()
# 另一角度: 峰高對數 vs 峰位
print('ln(A_m) vs ell_m:')
for m in range(2, 8):
    print(f'  m={m}: ln={math.log(A[m]):.4f}')
print()
# 連續 ln 差
for m in range(2, 7):
    print(f'  ln(A_{m+1})-ln(A_{m}) = {math.log(A[m+1])-math.log(A[m]):+.4f}')
