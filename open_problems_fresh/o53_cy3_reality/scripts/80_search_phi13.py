#!/usr/bin/env python3
"""
O53 積極方向: 用真 κ 搜尋 J ∈ Kähler cone 令 λ₁ = φ^(1/3)
================================================================
如果搵到一個合法 Kähler form J 令 Y = κ·J 嘅最大本徵值 = φ^(1/3)，
咁 λ₁ 閉合就 survive（只係 J* 錯咗，閉合本身啱）
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
target = phi**(1/3)

print("=" * 70)
print("O53: 搜尋合法 Kähler J → λ₁ = φ^(1/3)")
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

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

# Kähler cone 資訊
kc = cy.toric_kahler_cone()
print(f"Kähler cone: dim={kc.dim()}")

# 攞 cone generators / inequalities
try:
    ineq = kc.inequalities() if hasattr(kc, 'inequalities') else None
    if ineq is not None:
        print(f"  inequalities: {ineq.shape}")
except Exception as e:
    print(f"  ineq FAIL: {e}")

# 方法: 隨機採樣 cone 內 J (用 tip 做中心, 縮放)
# tip 係 stretched cone 嘅 tip — 合法 Kähler
tip_full = None
try:
    tip32 = cy.toric_kahler_cone().tip_of_stretched_cone(1)
    print(f"\ntip (32D): {tip32[:5]}...")
    # tip 32D → 需要對應 36D κ 嘅座標
    # CYTools 用 divisor basis (36 個 divisors 但 cone dim 32)
    # 4 個 redundant divisors 需要處理
    print(f"  tip 係 32D 但 κ 係 36³ — 需要 basis 轉換")
except Exception as e:
    print(f"tip FAIL: {e}")

# 直接方法: 用 tip 32D 對應嘅 κ 32×32×32 (用頭 32 個 dims)
# 或者: 用 divisor_basis
try:
    db = cy.divisor_basis()
    print(f"\ndivisor basis: {db}")
except Exception as e:
    print(f"divisor basis FAIL: {e}")

# 搜尋策略 1: tip 嘅縮放
# Y(tip) 32×32: λ₁ = 2587.8 (好大)
# 需要 normalize tip 令 λ₁ = φ^(1/3)
# 如果 Y(λ·tip) = λ·Y(tip), 咁 λ = φ^(1/3) / 2587.8
# 但 Y(tip) 嘅 λ₁ 係 2587.8, 用 λ = 1.174/2587.8 = 0.000454
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
K_tip32 = np.array(ck['kappa'])  # 32×32 = κ·tip
ev_tip = np.linalg.eigvalsh(K_tip32)
l1_tip = np.sort(ev_tip)[::-1][0]
scale = target / l1_tip
print(f"\n[tip scaling]")
print(f"  λ₁(tip) = {l1_tip:.4f}")
print(f"  scale = {scale:.6f}")
print(f"  如果 J = scale·tip: λ₁ = {l1_tip * scale:.6f} = φ^(1/3) ✅")
print(f"  但呢個只係線性縮放 — 唔係新發現, 係平凡 scaling")

# 搜尋策略 2: 用 random 正 J (嘗試)
print(f"\n[random positive J search]")
rng = np.random.default_rng(42)
best_err = 1e9
best_J = None
for trial in range(500):
    J = rng.uniform(0.001, 0.04, 36)
    Y = np.einsum('ijk,k->ij', K, J)
    Y = (Y + Y.T) / 2
    ev = np.linalg.eigvalsh(Y)
    l1 = np.sort(ev)[::-1][0]
    # 用比例不變量: λ₁/|tr| 或者 normalized
    # Y 係線性喺 J — 所以 λ₁ 可以 scaling 到任意值
    # 真正嘅測試係: λ₁ / (mean |λ|) 或者 ratio λ₁/λ₂
    err = abs(l1 / max(np.abs(ev).mean(), 1e-9))
    if err < best_err:
        best_err = err
        best_J = J

print(f"  完成 500 次採樣")

# 策略 3: 用 tip 嘅方向 (喺 cone 入面) 做 Y, 睇 spectrum 結構
print(f"\n[tip 方向分析]")
# κ(tip) 32×32 嘅譜
ev_all = np.sort(ev_tip)[::-1]
print(f"  λ₁ = {ev_all[0]:.2f}, λ₂ = {ev_all[1]:.2f}, λ₃ = {ev_all[2]:.2f}")
print(f"  λ₁/λ₂ = {ev_all[0]/abs(ev_all[1]):.2f}")
print(f"  λ₁/λ₃ = {ev_all[0]/abs(ev_all[2]):.2f}")
# φ 相關?
print(f"  φ² = {phi**2:.3f}, φ = {phi:.3f}")
print(f"  λ₁/λ₂ vs φ²: 誤差 {abs(ev_all[0]/abs(ev_all[1]) - phi**2)/phi**2*100:.1f}%")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)