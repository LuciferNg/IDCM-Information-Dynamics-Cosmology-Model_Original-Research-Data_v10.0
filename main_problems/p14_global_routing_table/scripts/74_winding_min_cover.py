#!/usr/bin/env python3
"""
P14 推進 — winding 寫入最小覆蓋定律 L_min(m) (2026-10-21)
===========================================================
docs/36 #2 開放項. 初測: L_min = {4,7,11,18} for m={1,2,3,5}
  4,7,11 碰巧 = Lucas L₃,L₄,L₅ (4,7,11,18,29...), m=5 實測 18=L₆ 唔係 L₇
  要分辨「真 Lucas」 vs「L_min ≈ 3.6m (≈φ²+1)」 vs 其他規律

方法: 對 m ∈ {1..10}, 掃 L = 2..L_max, 斜坡前 L 節點 0→2πm, 鬆弛後 winding 仲係 m?
L_min(m) = 最小 L 令 winding 保持
"""
import numpy as np

N = 88
K = 1/16.0
dt = 0.002

def deriv(theta, K):
    d = np.zeros(N)
    for i in range(N):
        jr = (i+1) % N
        jl = (i-1) % N
        d[i] = K*np.sin(theta[jr]-theta[i]) + K*np.sin(theta[jl]-theta[i])
    return d

def winding(theta):
    diff = np.diff(np.concatenate([theta, theta[:1]]))
    return np.sum(np.mod(diff+np.pi, 2*np.pi) - np.pi) / (2*np.pi)

def relax(theta, steps=100000):
    for s in range(steps):
        theta = theta + dt*deriv(theta, K)
        theta = np.mod(theta, 2*np.pi)
    return theta

print("=" * 72)
print("  L_min(m) 精確掃描 — Lucas 假說 vs 3.6m 假說")
print("=" * 72)
print(f"  {'m':>3} {'L_min':>5} {'L_min/m':>8} {'Lucas L_{m+2}?':>14} {'k=2πm/L':>10}")
lucas = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]
table = {}
for m in range(1, 11):
    Lmax = 5*m + 5
    found = None
    for L in range(2, Lmax+1):
        th = np.zeros(N)
        for i in range(L):
            th[i] = 2*np.pi*m*i / L
        w1 = winding(relax(th.copy()))
        if abs(w1 - m) < 0.05:
            found = L
            break
    table[m] = found
    lucas_pred = lucas[m+2] if m+2 < len(lucas) else None
    k = 2*np.pi*m/found if found else float('nan')
    match = "✓" if lucas_pred == found else "✗"
    print(f"  {m:>3} {found:>5} {found/m:>8.3f} {str(lucas_pred):>14} {k:>10.4f}")

print()
print("=== 假說檢驗 ===")
ms = list(table.keys())
# 假設 1: L_min = Lucas_{m+2}
lucas_ok = all(table[m] == lucas[m+2] for m in ms if m+2 < len(lucas))
print(f"  H1 Lucas_m+2: {'✅ 全部吻合' if lucas_ok else '❌ m=5 唔吻合 (18 vs 29)'}")
# 假設 2: L_min ≈ (φ²+1)·m = 3.618m
phi = (1+np.sqrt(5))/2
ratio = [table[m]/((phi**2+1)*m) for m in ms]
print(f"  H2 (phi^2+1)*m = 3.618m: 比 = {np.mean(ratio):.4f} +/- {np.std(ratio):.4f}")
# 假設 3: k=2πm/L_min 臨界相位差恆定?
ks = [2*np.pi*m/table[m] for m in ms]
print(f"  H3 臨界 k(2πm/L): {min(ks):.4f}..{max(ks):.4f} rad (恆定?)")
# 假設 4: Fibonacci: L_min = F_{m+3} + m?
fib = [1,1,2,3,5,8,13,21,34,55,89,144]
h4 = [fib[m+3]+m for m in ms if m+3 < len(fib)]
ok4 = all(table[m] == fib[m+3]+m for m in ms if m+3 < len(fib))
print(f"  H4 F_m+3 + m: m=1..5: {[(m, table[m], fib[m+3]+m) for m in [1,2,3,4,5]]} → {'✅' if ok4 else '❌ m=4: 15 vs 17'}")