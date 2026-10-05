#!/usr/bin/env python3
"""
O53 A2 新角度: J* 喺 mirror CY₃(98,36) 嘅 Kähler cone?
==========================================================
Mirror symmetry: CY₃(36,98) ↔ CY₃(98,36)
Mirror 嘅 Kähler cone = original 嘅 Mori cone
J* 可能喺 mirror 嘅 Kähler cone 入面!
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 A2: J* + mirror Kähler cone")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
print(f"[1] Original polytope: {len(p.vertices())}v, h11={p.h11()}, h12={p.h12()}")

# 2. Dual polytope = mirror
p_dual = p.dual()
print(f"\n[2] Dual (mirror) polytope:")
print(f"  {len(p_dual.vertices())}v, h11={p_dual.h11()}, h12={p_dual.h12()}")
print(f"  Mirror: CY₃({p_dual.h11()}, {p_dual.h12()})")
print(f"  Reflexive: {p_dual.is_reflexive()}")

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# 3. Mirror 嘅 Kähler cone
try:
    tri_m = p_dual.triangulate()
    cy_m = tri_m.get_cy()
    kc_m = cy_m.toric_kahler_cone()
    print(f"\n[3] Mirror Kähler cone:")
    print(f"  dim = {kc_m.dim()}")
    
    # J* 36D → need to map to mirror's divisor basis
    with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
        jstar = json.load(f)
    J0 = np.array(jstar['Jstar_36D'])
    
    # Mirror 嘅 divisor basis
    db_m = np.array(cy_m.divisor_basis()) - 1
    print(f"  mirror divisor basis: {db_m[:5]}...{db_m[-5:]} ({len(db_m)} 個)")
    print(f"  J* 長度: {len(J0)}")
    
    # J* 投影到 mirror basis (如果 dim match)
    # mirror h11 = 98, 所以 Kähler cone dim = 98
    # J* 只有 36D — 唔夠長!
    if len(db_m) <= len(J0):
        J_m = J0[db_m]
        in_cone = kc_m.contains(J_m)
        print(f"  J*[db_m] 喺 mirror cone? {in_cone}")
    else:
        print(f"  Mirror cone dim ({len(db_m)}) > J* dim (36) — 唔可以直接比較")
        print(f"  J* 可能係 mirror cone 嘅 subspace (投影?)")
        
except Exception as e:
    print(f"  FAIL: {str(e)[:150]}")

# 4. 替代: 用 mori cone (original) 嘅 dual
print(f"\n[4] Original Mori cone cap:")
try:
    tri = p.triangulate()
    cy = tri.get_cy()
    mcap = cy.mori_cone_cap()
    rays = np.array(mcap.extremal_rays())
    print(f"  extremal rays: {rays.shape}")
    print(f"  ray dim: {rays.shape[1]}")
    
    # Mori cone 嘅維度 = h11 = 36? 定係 37?
    # 如果 rays 嘅 dim = 36, J* 可以係 Mori cone 嘅點
    J0_32 = J0[np.array(cy.divisor_basis()) - 1]
    if rays.shape[1] == 32:
        # Mori cone rays 32D — check J*_32
        # 需要檢查 J*_32 係咪 Mori cone 嘅正組合
        print(f"  J* basis 32D: min={J0_32.min()}, max={J0_32.max()}")
        # 簡單檢查: J* 係咪全部正? (Mori cone 係正 cone)
        all_positive = all(J0_32 > 0)
        print(f"  J* 全正? {all_positive}")
        # 如果全正 → 可能喺 Mori cone
    else:
        print(f"  Mori cone dim = {rays.shape[1]}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)