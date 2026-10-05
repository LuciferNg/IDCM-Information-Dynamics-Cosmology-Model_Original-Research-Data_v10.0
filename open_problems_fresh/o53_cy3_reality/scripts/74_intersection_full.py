#!/usr/bin/env python3
"""
O53 路徑三: CYTools 完整 intersection numbers → κ_ijk
===========================================================
用 intersection_numbers() 攞完整 3-tensor
然後用 J* 重現 λ₁ = φ^(1/3) 分析
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53: CYTools intersection numbers")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
print(f"CY: h11={cy.h11()}, h12={cy.h12()}")

# intersection numbers
inter = cy.intersection_numbers()
print(f"intersection_numbers: {len(inter)} entries")
print(f"  sample keys: {list(inter.keys())[:5]}")

# 轉成 dense 3-tensor
# keys 係 tuple (i,j,k) → value
n_div = cy.h11()
K = np.zeros((n_div, n_div, n_div))
for key, val in inter.items():
    if isinstance(key, tuple) and len(key) == 3:
        i, j, k = key
        if i < n_div and j < n_div and k < n_div:
            K[i, j, k] = val
            K[i, k, j] = val
            K[j, i, k] = val
            K[j, k, i] = val
            K[k, i, j] = val
            K[k, j, i] = val

print(f"κ tensor: {K.shape}, non-zero: {np.count_nonzero(K)}")

# 儲存
out = os.path.join(BASE, 'cy36_98_intersection_full.json')
with open(out, 'w') as f:
    json.dump({'kappa': K.tolist(), 'shape': list(K.shape)}, f)
print(f"✅ κ saved: {out}")

# --- [1] 用 J* 做 Y = κ·J* ---
print(f"\n[1] Y = κ_ijk·J*^k (J* 36D):")
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
print(f"  J*: {J0.shape}")

# J* 36D vs κ 36D? κ 係 36×36×36 (cy.h11() = 36)
if K.shape[0] == 36:
    Y = np.einsum('ijk,k->ij', K, J0)
    Y = (Y + Y.T) / 2
    ev = np.linalg.eigvalsh(Y)
    l1 = max(ev)
    print(f"  λ₁ = {l1:.6f}")
    print(f"  φ^(1/3) = {phi**(1/3):.6f}")
    print(f"  誤差 = {abs(l1 - phi**(1/3))/phi**(1/3)*100:.2f}%")
    check("CYTools κ λ₁ = φ^(1/3)", abs(l1 - phi**(1/3))/phi**(1/3) < 0.05,
          f"({abs(l1 - phi**(1/3))/phi**(1/3)*100:.2f}%)")
    trY2 = np.trace(Y @ Y)
    print(f"  tr(Y²) = {trY2:.4f}")
    check("tr(Y²) ≈ 5", abs(trY2-5)/5 < 0.1, f"({abs(trY2-5)/5*100:.2f}%)")
else:
    print(f"  κ dim 唔匹配: {K.shape[0]} vs 36")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)