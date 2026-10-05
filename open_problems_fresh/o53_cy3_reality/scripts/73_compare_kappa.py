#!/usr/bin/env python3
"""
O53 路徑三: CYTools κ vs 舊 κ_36d_raw.json 對比
====================================================
驗證 λ₁ = φ^(1/3) 喺真實 CYTools κ 上重現
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
print("O53: CYTools κ vs 舊 κ")
print("=" * 70)

# CYTools κ (32×32 matrix? 定 32×32×32?)
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
kappa_ct = np.array(ck['kappa'])
print(f"CYTools κ shape: {kappa_ct.shape}")

# 舊 κ_36d_raw.json
with open(os.path.join(BASE, 'kappa_36d_raw.json')) as f:
    old = json.load(f)
print(f"舊 κ keys: {list(old.keys())}")
print(f"舊 κ shape: {old.get('shape', 'N/A')}")

# κ_36d_raw 係 3-tensor (36×36×36)
K_old = np.zeros(tuple(old['shape']))
for key, val in old['kappa'].items():
    i, j, k = map(int, key.split(','))
    K_old[i, j, k] = val
    K_old[i, k, j] = val
    K_old[j, i, k] = val
    K_old[j, k, i] = val
    K_old[k, i, j] = val
    K_old[k, j, i] = val

# CYTools κ 係咪 3-tensor?
if kappa_ct.ndim == 2:
    print(f"\nCYTools κ 係 2D (32×32) — 呢個係 kappa_matrix 唔係完整 3-tensor")
    print(f"  compute_kappa_matrix 返回 κ_ijk·t^k (對 tip 收縮)")
    print(f"  → 需要 compute_kappa_vector 或者直接用 2D matrix")
    
    # 用 CYTools κ 2D matrix 做 Y = κ_ij(tip)
    Y_ct = kappa_ct
    ev = np.linalg.eigvalsh(Y_ct)
    ev_sorted = np.sort(ev)[::-1]
    print(f"\nCYTools Y(tip) 譜 (32×32):")
    print(f"  λ₁ = {ev_sorted[0]:.6f}")
    print(f"  λ₂ = {ev_sorted[1]:.6f}")
    print(f"  λ₁ vs φ^(1/3) = {phi**(1/3):.6f}: 誤差 {abs(ev_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%")
    check("CYTools λ₁ = φ^(1/3) (<1%)", abs(ev_sorted[0]-phi**(1/3))/phi**(1/3) < 0.01,
          f"({abs(ev_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%)")
    
    # tr(Y²)
    trY2 = np.trace(Y_ct @ Y_ct)
    print(f"  tr(Y²) = {trY2:.4f} vs 5 = B+1: 誤差 {abs(trY2-5)/5*100:.2f}%")
    check("CYTools tr(Y²) = 5", abs(trY2-5)/5 < 0.05, f"({abs(trY2-5)/5*100:.2f}%)")
else:
    print(f"\nCYTools κ 係 {kappa_ct.ndim}D — 直接比較")
    # 同 K_old 比對
    if kappa_ct.shape == K_old.shape:
        diff = np.abs(kappa_ct - K_old)
        print(f"  max diff: {diff.max():.2f}")
        print(f"  mean diff: {diff.mean():.2f}")
        check("CYTools κ = 舊 κ", diff.max() < 0.01, f"(max {diff.max():.4f})")
    else:
        print(f"  shape 唔同: {kappa_ct.shape} vs {K_old.shape}")

# 對比 tip vs J*
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
tip = np.array(ck['tip'])
print(f"\n[對比] CYTools tip (32D) vs J* (36D):")
print(f"  tip: {tip.shape}, J*: {J0.shape}")
print(f"  tip[:10]: {tip[:10]}")
print(f"  J*[:10]:  {J0[:10]}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)