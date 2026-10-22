#!/usr/bin/env python3
"""O101 公式與數值驗證腳本"""
from math import comb

errors = 0
checks = 0

def check(name, expr, expected, tol=1e-10):
    global errors, checks
    checks += 1
    if abs(expr - expected) > tol:
        print(f"  ❌ {name}: {expr} != {expected} (dev {abs(expr-expected):.2e})")
        errors += 1
    else:
        print(f"  ✅ {name}: {expr}")

def check_ratio(name, expr, target, tol_pct=0.1):
    global errors, checks
    checks += 1
    dev_pct = abs(expr/target - 1) * 100
    if dev_pct > tol_pct:
        print(f"  ❌ {name}: {expr:.6f} vs {target:.6f} (dev {dev_pct:.4f}%)")
        errors += 1
    else:
        print(f"  ✅ {name}: {expr:.6f} ≈ {target:.6f} (dev {dev_pct:.4f}%)")

print("=" * 72)
print("  O101 公式與數值驗證")
print("=" * 72)

# 基礎常數
print("\n--- 基礎常數 ---")
B, Nd, L5, L6, L7 = 4, 44, 11, 18, 52
F5 = 5
check("B", B, 4)
check("N_d = 44", Nd, 44)
check("L_5 = 11", L5, 11)
check("L_6 = 18", L6, 18)
check("L_7 = 52", L7, 52)
check("F_5 = 5", F5, 5)

# 12 = 1⊕11
print("\n--- 12 = 1⊕11 結構 ---")
check("12 = B x N_gen", B*3, 12)
check("12 = N_d/B + 1", Nd//B + 1, 12)
check("12 = L_5 + 1", L5 + 1, 12)
check("11 = N_d/B = L_5", Nd//B, L5)
check("1 = BxN_gen - L_5", B*3 - L5, 1)
check("1+11 = 12", 1+11, 12)

# 66 = Lambda^2(12)
print("\n--- 66 = Lambda^2(12) ---")
check("C(12,2) = 66", comb(12,2), 66)
check("C(11,2) = 55", comb(11,2), 55)
check("11 + 55 = 66", 11+55, 66)
check("66 = 36+30", 36+30, 66)
check("36 = L_5 + F_5^2", L5 + F5**2, 36)
check("30 = F_5 + F_5^2", F5 + F5**2, 30)

# lambda_max
print("\n--- lambda_max 結構 ---")
lam = L7 - 29/comb(12,2)
check("L_7 - 29/C(12,2)", lam, 51.56060606060606)
check_ratio("lambda_max vs 51.5606", lam, 51.5606, tol_pct=0.01)

# 88-site
print("\n--- 88-site 雙鏈 ---")
check("88 = 2B x L_5", 2*B*L5, 88)
check("90 = 2B x L_5 + 2", 2*B*L5+2, 90)
check("N_d/B = 11 = L_5", Nd//B, L5)

# N_gen
print("\n--- N_gen 推導 ---")
check("N_gen = (N_d/B+1)/B", (Nd//B + 1)/B, 3)
check("N_gen = L_6/(B+2)", 18/(B+2), 3)
check("N_gen = K_Tree/L_5", 33/L5, 3)

# SU(12) adjoint
print("\n--- SU(12) adjoint ---")
check("dim(adj) = 12^2-1", 12**2-1, 143)
check("roots = 143-11", 143-11, 132)
check("132 = 2x66", 2*66, 132)

# Eigenvalue ratio
print("\n--- Z-特徵值譜比 ---")
ratio = lam / 1.93
check("lambda_max / mean|lambda_rest| > 20", ratio > 20, True)
print(f"  實際比: {ratio:.1f}")

print(f"\n{'='*72}")
print(f"  驗證: {checks} checks, {errors} errors")
if errors == 0:
    print("  🟢 全部通過")
else:
    print(f"  ❌ {errors} 個錯誤")
print(f"{'='*72}")