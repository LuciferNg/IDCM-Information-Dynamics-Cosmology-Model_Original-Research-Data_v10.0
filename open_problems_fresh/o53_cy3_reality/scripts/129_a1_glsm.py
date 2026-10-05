#!/usr/bin/env python3
"""
O53 A1: GLSM charge matrix — 1/3 量化?
==========================================
GLSM charge matrix: 32×37 (32 U(1) × 37 fields)
cy36_98_final.json 有 glsm_coord3 (32 entries)
檢查: GLSM charges 有冇 1/3 倍數模式?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 A1: GLSM charges + 1/3")
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

# 1. GLSM charge matrix
glsm = np.array(cy.glsm_charge_matrix())
print(f"[1] GLSM charge matrix: {glsm.shape}")
print(f"  (n_curves × n_fields) = ({glsm.shape[0]} × {glsm.shape[1]})")

# 2. GLSM charges 分佈
all_charges = glsm.flatten()
print(f"\n[2] Charges 分佈:")
print(f"  min = {all_charges.min()}, max = {all_charges.max()}")
print(f"  unique values: {np.unique(all_charges)[:30]}")

# 3. 1/3 倍數?
non_zero = all_charges[all_charges != 0]
mod3 = non_zero % 3
print(f"\n[3] 1/3 量化:")
print(f"  non-zero charges: {len(non_zero)}")
print(f"  mod 3 = 0: {(mod3 == 0).sum()} ({((mod3==0).mean()*100):.0f}%)")
print(f"  mod 3 = 1: {(mod3 == 1).sum()} ({((mod3==1).mean()*100):.0f}%)")
print(f"  mod 3 = 2: {(mod3 == 2).sum()} ({((mod3==2).mean()*100):.0f}%)")

# 4. 每 field 嘅 charges 和
field_sums = glsm.sum(axis=0)
print(f"\n[4] Field charge sums:")
print(f"  min = {field_sums.min()}, max = {field_sums.max()}")
print(f"  unique: {np.unique(field_sums)}")

# 5. glsm_coord3 (from original data — 喺 cy_search/data/)
orig_base = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "IDCM-Original", "ICDM-v6.0--Information-Dynamics-Cosmology-Model", "data", "cy_search", "data")
try:
    with open(os.path.join(orig_base, 'cy36_98_final.json')) as f:
        final = json.load(f)
    gc3 = np.array(final['glsm_coord3'])
    print(f"\n[5] glsm_coord3 (32 entries):")
    print(f"  {gc3}")
    print(f"  min = {gc3.min()}, max = {gc3.max()}")
    print(f"  mod 3: {gc3 % 3}")
    print(f"  全部 ≡ 0 mod 3? {all(gc3 % 3 == 0)}")
except FileNotFoundError:
    print(f"\n[5] glsm_coord3: 檔案唔存在 (預期)")

# 6. 1/3 量化檢查: charges 係咪全部整除 3?
print(f"\n[6] 1/3 倍數測試:")
print(f"  GLSM charges 全部 ≡ 0 mod 3? {all(all_charges % 3 == 0)}")
print(f"  field_sums 全部 ≡ 0 mod 3? {all(field_sums % 3 == 0)}")

# 7. 3×12 block 結構: GLSM 有冇?
# 32 curves = 32 divisors in basis
# 37 fields = 36 toric divisors + 1 CY
print(f"\n[7] 3×12 block 結構喺 GLSM:")
# 前 32 行 = curve basis divisors
# 前 12 行 = Block 0, 12-24 = Block 1, 24-32 = Block 2 (partial)
b0 = glsm[:12, :]
b1 = glsm[12:24, :]
b2 = glsm[24:32, :]
print(f"  Block 0 charges (12×37): mean |Q| = {np.abs(b0).mean():.3f}")
print(f"  Block 1 charges (12×37): mean |Q| = {np.abs(b1).mean():.3f}")
print(f"  Block 2 charges (8×37): mean |Q| = {np.abs(b2).mean():.3f}")

# 第 37 field (CY hypersurface) 嘅 charges
print(f"\n[8] CY hypersurface field (col 36):")
cy_field = glsm[:, 36]
print(f"  charges: {cy_field}")
print(f"  mod 3: {cy_field % 3}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)