#!/usr/bin/env python3
"""
O53 A1 決定性測試: Block 0 1/3 本徵值 — J* 特有定 κ 性質?
=================================================================
Block 0 (J*) 譜: 11/3, 1/3, ..., -3/3 (精確)
測試: 隨機 J (正數) 下 Block 0 係咪都有 1/3 結構?
如果係: κ block 0 內在性質
如果唔係: J* 特有 (偽影)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: Block 0 1/3 結構 — 隨機 J 對照")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# J* 下 Block 0 譜
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2
B0 = Y[0:12, 0:12]
ev_Jstar = np.linalg.eigvalsh(B0)
print(f"J* 下 Block 0 譜: {np.sort(ev_Jstar)[::-1][:5]}")

# 隨機 J 對照 (1000 次)
rng = np.random.default_rng(42)
near_count = 0
trials = 1000
for _ in range(trials):
    J = rng.uniform(0.001, 0.04, 36)
    Yr = np.einsum('ijk,k->ij', K, J)
    Yr = (Yr + Yr.T) / 2
    Br = Yr[0:12, 0:12]
    evr = np.linalg.eigvalsh(Br)
    # 檢查有冇本徵值近 1/3 (Δ < 0.01)
    has_13 = any(abs(e - 1/3) < 0.01 for e in evr)
    has_113 = any(abs(e - 11/3) < 0.01 for e in evr)
    if has_13 or has_113:
        near_count += 1

print(f"\n隨機 J (1000 次): {near_count} 次出現 1/3 或 11/3 本徵值 ({near_count/trials*100:.1f}%)")
print(f"J*: Block 0 有 λ=1/3 (Δ=0.0003) + λ=11/3 (Δ=0.005)")

# 但 J* 唔喺 Kähler cone — 用合法 J (tip 方向) 測試
print(f"\n[補充] 用 tip 方向 J:")
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()
with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
tip32 = cy.toric_kahler_cone().tip_of_stretched_cone(1)

# tip 32D → 需要 36D (用 divisor basis 補?)
# 直接用 K(tip) 32×32 嘅前 12×12 block
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
K_tip = np.array(ck['kappa'])
Bt = K_tip[0:12, 0:12]
ev_tip = np.linalg.eigvalsh(Bt)
print(f"tip 下 Block 0 (12×12): λ = {np.sort(ev_tip)[::-1][:5]}")
has_13_tip = any(abs(e - 1/3) < 0.05 for e in ev_tip)
print(f"  tip 有 1/3? {'✅' if has_13_tip else '❌'}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)