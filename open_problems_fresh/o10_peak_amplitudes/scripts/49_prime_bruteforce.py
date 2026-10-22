#!/usr/bin/env python3
"""
O10 49: 質數峰公式系統搜索 (窮舉)
==================================
候選: A(p) = 3ε × φ^(-α) × F_β^γ × (p-1)^δ / (p+1)^ε × ...
窮舉有理指數, 找最佳匹配
"""
import numpy as np, math, itertools

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}

print("=" * 72)
print("質數峰公式窮舉搜索")
print("=" * 72)

# 候選公式庫
best = []
for a in [-4, -3, -2, -1, 0, 1, 2, 3, 4]:       # φ^a
    for b in [-4, -3, -2, -1, 0, 1, 2, 3, 4]:   # ε^b?  ε=φ⁻¹/4, 所以 ε^b = φ^(-b)×4^(-b)
        for c in [-2, -1, 0, 1, 2]:              # F_3^c = 2^c
            for d in [-2, -1, 0, 1, 2]:          # p^d
                for e in [0, 1, 2]:              # (p-1)^e
                    for f in [0, 1, 2]:          # (p+1)^-f
                        scores = []
                        for p in [2, 3, 5, 7]:
                            v = phi**a * eps**b * 2**c * p**d * (p-1)**e * (p+1)**(-f)
                            scores.append(abs(A[p]/v - 1))
                        rms = math.sqrt(np.mean(np.array(scores)**2))
                        if rms < 0.05:
                            best.append((rms, a, b, c, d, e, f))

best.sort(key=lambda x: x[0])
print(f"搵到 {len(best)} 個 rms<5% 候選:")
for rms, a, b, c, d, e, f in best[:10]:
    formula = f"3ε·φ^{a}·ε^{b}·2^{c}·p^{d}·(p-1)^{e}·(p+1)^-{f}"
    print(f"  rms={rms:.4f}: {formula}")
    # 驗證
    for p in [2, 3, 5, 7]:
        v = phi**a * eps**b * 2**c * p**d * (p-1)**e * (p+1)**(-f)
        print(f"    p={p}: pred {3*eps*v:.4f} vs {A[p]:.4f} ({(A[p]/(3*eps*v)-1)*100:+.1f}%)")

print()
print("注意: ε = φ⁻¹/4, 所以 ε^b 引入 4^-b 因子")
print("搜索可能過度擬合 4 個點 (2,3,5,7)")
