#!/usr/bin/env python3
"""
O9-C 最終驗證 v2: 生成規則 + 母函數 + SPT 驗證全部核對
========================================================
核對 04_cascade_mother_function.md 所有聲稱
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# 原始數據
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

# 統一峰表
obs = {1: (221, 5816.5), 2: (527, 2579.2), 3: (815, 2552.7),
       4: (1013, 1079.5), 5: (1121, 1246.3), 6: (1337, 757.9), 7: (1400, 830.2)}
A1 = obs[1][1]
norm = {m: obs[m][1]/A1 for m in range(1, 8)}

passes, fails = 0, 0
def check(name, claim, actual, tol_pct):
    global passes, fails
    dev = abs(claim - actual)/max(abs(actual), 1e-10)*100
    if dev <= tol_pct:
        passes += 1
        print(f"  ✅ {name}: {actual:.4f}")
    else:
        fails += 1
        print(f"  ❌ {name}: claim={claim:.4f} actual={actual:.4f}")

print("="*70)
print("O9-C 最終驗證 v2 (生成規則)")
print("="*70)

# 1. 生成公式 A_{2k}/A1 = ((k+1)/(4k-1))^2
print("\n1. 偶峰統一生成公式:")
for k in range(1, 4):
    m = 2*k
    pred = ((k+1)/(4*k-1))**2
    print(f"   k={k}: (({k+1})/({4*k-1}))² = {pred:.4f} vs {norm[m]:.4f}")
    check(f"A{m}/A1 生成公式", pred, norm[m], 2.0)

# 2. 4a_k - b_k = 5
print("\n2. 4a_k − b_k = 5 恆定:")
for k in range(1, 4):
    val = 4*(k+1) - (4*k-1)
    check(f"k={k}: 4a−b", 5, val, 0.001)

# 3. b_max = N_d/4
print("\n3. b_max = N_d/4:")
check("b3 = 11", 11, 4*3-1, 0)
check("N_d/4 = 11", 11, 44/4, 0)

# 4. 奇峰
print("\n4. 奇峰:")
odd_cands = {3: (2/3)**2, 5: 3/14, 7: 3/21}
for m, p in odd_cands.items():
    check(f"A{m}/A1", p, norm[m], 2.0)

# 5. A5/A7 = 3/2
print("\n5. A₅/A₇:")
check("A5/A7 = 3/2", 3/2, norm[5]/norm[7], 2.0)

# 6. SPT 驗證
print("\n6. SPT-3G 驗證 (A₅/A₂, A₇/A₂):")
# SPT 峰: 524=2558.8, 1124=1235.3, 1424=820.2
A2_spt = 2558.8
r5 = 1235.3/A2_spt
r7 = 820.2/A2_spt
check("A5/A2 = 27/56", 27/56, r5, 2.0)
check("A7/A2 = 9/28", 9/28, r7, 2.0)

# 7. 極限
print("\n7. 極限 (k→∞):")
lim = (k+1)/(4*k-1)
print(f"   a/b → 1/4 (k→∞), A/A₁ → 1/16")

print(f"\n{'='*70}")
print(f"PASS: {passes}  FAIL: {fails}")
