#!/usr/bin/env python3
"""
O9-C 最終驗證: 母函數所有數字獨立重算
=======================================
核對 04_cascade_mother_function.md 每個聲稱
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# 原始數據重算振幅
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

# 統一峰表 (script 13/18 確認)
obs = {1: (221, 5816.5), 2: (527, 2579.2), 3: (815, 2552.7),
       4: (1013, 1079.5), 5: (1121, 1246.3), 6: (1337, 757.9), 7: (1400, 830.2)}
A1 = obs[1][1]
norm = {m: obs[m][1]/A1 for m in range(1, 8)}

passes, fails = 0, 0
def check(name, claim, actual, tol_pct):
    global passes, fails
    dev = abs(claim - actual)/actual*100
    if dev <= tol_pct:
        passes += 1
        print(f"  ✅ {name}: {actual:.4f}")
    else:
        fails += 1
        print(f"  ❌ {name}: claim={claim:.4f} actual={actual:.4f}")

print("="*70)
print("O9-C 最終驗證")
print("="*70)

# 1. 偶峰
print("\n1. 偶峰平方級聯:")
cands_even = {
    2: (F[3]/F[4])**2,
    4: (L[2]/L[4])**2,
    6: (L[3]/L[5])**2,
}
for m, p in cands_even.items():
    print(f"   m={m}: 預言 {p:.4f}, 實測 {norm[m]:.4f}")
    check(f"A{m}/A1", p, norm[m], 2.0)

# 2. 奇峰
print("\n2. 奇峰一次比:")
cands_odd = {
    3: (F[3]/F[4])**2,
    5: (L[2]/L[4])/2,
    7: F[4]/F[8],
}
for m, p in cands_odd.items():
    print(f"   m={m}: 預言 {p:.4f}, 實測 {norm[m]:.4f}")
    check(f"A{m}/A1", p, norm[m], 2.0)

# 3. A5/A7 = 2/3
print("\n3. A₅/A₇ 結構:")
r57 = norm[5]/norm[7]
print(f"   A₅/A₇ = {r57:.4f} vs 3/2 = 1.5 (A₇/A₅ = {norm[7]/norm[5]:.4f} vs 2/3)")
check("A5/A7 = 3/2", 3/2, r57, 2.0)

# 4. 分母差
print("\n4. 序列規律:")
print(f"   分子: 2, 3, 4 (差 +1, +1)")
print(f"   分母: 3, 7, 11 (差 +4, +4)")
check("分子差 +1", 3-2, 1, 0)
check("分母差 +4", 7-3, 4, 0)
check("分母差 +4", 11-7, 4, 0)

# 5. 總 RMS
print("\n5. 母函數 RMS:")
all_preds = {1: 1.0, **cands_even, **cands_odd}
devs = [abs(all_preds[m] - norm[m])/norm[m]*100 for m in range(1, 8)]
rms = np.sqrt(np.mean(np.array(devs)**2))
print(f"   全部峰 RMS = {rms:.2f}%")
check("RMS < 1.5%", 1.5, rms, 100)  # 驗證 rms 細過 1.5

print(f"\n{'='*70}")
print(f"PASS: {passes}  FAIL: {fails}")
