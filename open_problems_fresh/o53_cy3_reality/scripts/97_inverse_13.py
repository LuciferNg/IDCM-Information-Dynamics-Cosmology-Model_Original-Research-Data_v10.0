#!/usr/bin/env python3
"""
O53 A1: 反問題 — 搵 J 令 Block 0 有 1/3 本徵值
===================================================
J* 下 Block 0: λ = 11/3, 1/3, ..., -3/3 (精確 1/3 格點)
問題: J* 唔喺 Kähler cone
測試: 有冇合法 J ∈ Kähler cone 令 Block 0 有 1/3?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 反問題 — 1/3 本徵值嘅 J")
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

# Kähler cone
kc = cy.toric_kahler_cone()
tip32 = kc.tip_of_stretched_cone(1)

# 問題: tip 32D, κ 36³ — 唔可以直接用
# 但 compute_kappa_matrix(tip) 得 32×32
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
K_tip = np.array(ck['kappa'])

# 檢查 32×32 有冇 3×12 子結構 (32 = 12+12+8)
# 如果 Block 0 (0:12, 0:12) 喺 32×32 都存在
B0_tip = K_tip[0:12, 0:12]
ev0 = np.linalg.eigvalsh(B0_tip)
print(f"[1] tip 下 Block 0 (12×12, 32×32 嘅左上):")
print(f"  λ = {np.sort(ev0)[::-1][:6]}")
print(f"  有 1/3? {'✅' if any(abs(e-1/3) < 0.01 for e in ev0) else '❌'}")

# 縮放: λ 係線性, 可以 scale 但唔可以製造 1/3
# 真正問題: tip 方向冇 1/3 → 需要唔同 J

# 方法: 用 cone 內隨機 J (tip + 隨機組合)
# 或者: 用 CYTools 隨機 triangulation 嘅唔同 cone tip
print(f"\n[2] 唔同 triangulation 嘅 tip:")
for seed_name in ['a', 'b']:
    try:
        tri2 = p.triangulate()
        cy2 = tri2.get_cy()
        tip2 = cy2.toric_kahler_cone().tip_of_stretched_cone(1)
        kappa2 = cy2.compute_kappa_matrix(tip2)
        B2 = kappa2[0:12, 0:12]
        ev2 = np.linalg.eigvalsh(B2)
        has = any(abs(e - 1/3) < 0.01 for e in ev2)
        print(f"  triangulation {seed_name}: λ_max = {np.sort(ev2)[::-1][0]:.4f}, 有 1/3? {has}")
    except Exception as e:
        print(f"  FAIL: {str(e)[:60]}")

# 方法 3: 搜尋 cone 內 J (用 32D tip + 隨機方向)
print(f"\n[3] 搜尋 Kähler cone 內 J 令 Block 0 有 1/3:")
rng = np.random.default_rng(123)
found = 0
for trial in range(200):
    # 隨機 cone 內 J: tip 嘅隨機正組合
    w = rng.uniform(0.1, 2.0, 32)
    J_try = w * tip32
    # J_try 32D → κ(tip) 32×32 係 κ_ij(t) — 唔係 κ_ijk·J
    # 需要 3-tensor 收縮: K 36³ 用頭 32?
    # 唔啱: 32 維 divisor basis 同 36 維唔同
    # 跳過 — 呢個方法需要正確 basis 轉換
    break

print(f"  需要 divisor basis 轉換 (32D ↔ 36D) — 待續")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)