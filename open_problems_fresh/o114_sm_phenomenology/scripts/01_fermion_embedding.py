#!/usr/bin/env python3
"""
O114-1: 三代 SM 費米子嵌入 — 12 維向量劃分與 Charge 矩陣
=========================================================
定義 SU(12) fundamental 12 嘅 Pati-Salam 分量分解，
計算 6 個 extra U(1) 對每個費米子態嘅精確電荷量子數 Q^{(i)}。

目標:
  1. 12 維向量 Ψ₁₂ 嘅 Pati-Salam 分解
  2. 6 個 extra U(1) generator T^{(i)}_extra 嘅 12×12 作用
  3. 每個費米子態嘅 Q^{(i)} 電荷
  4. 與 SM 量子數嘅對照表 (Y, T₃, B-L, Color)
"""
import numpy as np
import json, os, math

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o114_sm_phenomenology"
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)

print("=" * 72)
print("O114-1: 三代 SM 費米子嵌入 — 12 維向量劃分與 Charge 矩陣")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============================================================
# 1. 12 維向量嘅 Pati-Salam 分解
# ============================================================
print("\n" + "=" * 72)
print("第1部分: 12 維向量嘅 Pati-Salam 分解")
print("=" * 72)

# SU(12) ⊃ SU(4) × SU(3) tensor embedding
# 12 = (4, 3) = B × N_gen
# SU(4) = Pati-Salam, SU(3) = generation symmetry
#
# 4-vector under SU(4): (q^r, q^g, q^b, l)
#   - q^r, q^g, q^b: color triplet (quark)
#   - l: color singlet (lepton)
#
# 3-vector under SU(3)_gen: generation index
#
# 12-vector indexing:
#   idx = (color_idx, gen_idx) where color_idx = 0..3, gen_idx = 0..2
#   idx = color_idx * 3 + gen_idx
#
# In Pati-Salam:
#   4 = (2, 2) under SU(2)_L × SU(2)_R
#   (2, 2)₁₁: T₃(L)=+½, T₃(R)=+½ → u-type
#   (2, 2)₁₂: T₃(L)=+½, T₃(R)=-½ → d-type
#   (2, 2)₂₁: T₃(L)=-½, T₃(R)=+½ → u-type
#   (2, 2)₂₂: T₃(L)=-½, T₃(R)=-½ → d-type

print("""
  SU(12) fundamental 12 = (4, 3) under SU(4) × SU(3)_gen

  SU(4) Pati-Salam 4-vector:
    ┌ q^r ┐      (color red, B-L = +1/3)
    │ q^g │      (color green, B-L = +1/3)
    │ q^b │      (color blue, B-L = +1/3)
    └ l   ┘      (lepton, B-L = -1)

  SU(3)_gen: 3 generations

  12-vector (12 components):
    Ψ₁₂ = (q^r₁, q^r₂, q^r₃, q^g₁, q^g₂, q^g₃, q^b₁, q^b₂, q^b₃, l₁, l₂, l₃)
""")

# ============================================================
# 2. 6 extra U(1) generators 嘅 12×12 矩陣
# ============================================================
print("=" * 72)
print("第2部分: 6 extra U(1) generator 嘅 12×12 矩陣")
print("=" * 72)

# 從 O107 嘅 Gram-Schmidt 結果提取 6 個 extra U(1) 生成元
# 12-vector basis: (q^r₁, q^r₂, q^r₃, q^g₁, q^g₂, q^g₃, q^b₁, q^b₂, q^b₃, l₁, l₂, l₃)

# O107 結果: E_1 to E_6 (Gram-Schmidt orthogonalized)
# 每個 E 係 12 維向量 (12 個分量 = 對角生成元嘅對角元素)
E_GS = np.array([
    # E_1: B-L like (quark/lepton separating)
    [+0.6124, -0.6124, +0.0000, -0.2041, +0.2041, +0.0000,
     -0.2041, +0.2041, +0.0000, -0.2041, +0.2041, +0.0000],
    # E_2
    [+0.3536, +0.3536, -0.7071, -0.1179, -0.1179, +0.2357,
     -0.1179, -0.1179, +0.2357, -0.1179, -0.1179, +0.2357],
    # E_3
    [-0.0000, -0.0000, -0.0000, -0.6667, +0.3333, +0.3333,
     +0.3333, -0.1667, -0.1667, +0.3333, -0.1667, -0.1667],
    # E_4
    [-0.0000, -0.0000, -0.0000, +0.0000, -0.5774, +0.5774,
     +0.0000, +0.2887, -0.2887, +0.0000, +0.2887, -0.2887],
    # E_5
    [-0.0000, -0.0000, -0.0000, +0.0000, +0.0000, +0.0000,
     -0.5774, +0.2887, +0.2887, +0.5774, -0.2887, -0.2887],
    # E_6
    [-0.0000, -0.0000, -0.0000, +0.0000, +0.0000, -0.0000,
     +0.0000, -0.5000, +0.5000, +0.0000, +0.5000, -0.5000],
])

# 生成元名稱
E_names = ["B-L (suggested)", "PQ (suggested)", "F1 (suggested)",
           "F2 (suggested)", "F3 (suggested)", "R (suggested)"]

# 費米子標籤
fermion_labels = [
    "q^r_1", "q^r_2", "q^r_3",   # 0,1,2: red quarks, gen 1,2,3
    "q^g_1", "q^g_2", "q^g_3",   # 3,4,5: green quarks, gen 1,2,3
    "q^b_1", "q^b_2", "q^b_3",   # 6,7,8: blue quarks, gen 1,2,3
    "l_1", "l_2", "l_3",          # 9,10,11: leptons, gen 1,2,3
]

print("\n  6 extra U(1) generators (12×12 diagonal values):")
print(f"  {'State':<10}", end="")
for i in range(6):
    print(f"{'E_'+str(i+1):<10}", end="")
    # 顯示建議名稱
print()
print(f"  {'─'*10:<10}", end="")
for i in range(6):
    print(f"{'─'*10:<10}", end="")
print()

for idx in range(12):
    print(f"  {fermion_labels[idx]:<10}", end="")
    for i in range(6):
        val = E_GS[i][idx]
        if abs(val) < 1e-4:
            print(f"{0:<10.4f}", end="")
        else:
            print(f"{val:<+10.4f}", end="")
    print()

# ============================================================
# 3. EM charge 同 SM 量子數嘅 Pati-Salam 映射
# ============================================================
print("\n" + "=" * 72)
print("第3部分: Pati-Salam → SM 量子數映射")
print("=" * 72)

# In Pati-Salam: SU(4) × SU(2)_L × SU(2)_R
# 4 = (2, 2) under SU(2)_L × SU(2)_R
#
# Breaking chain:
#   SU(4) → SU(2)_L × SU(2)_R (Step 2, M_PS)
#   SU(2)_R × U(1)_{B-L} → U(1)_Y (Step 3, M_R)
#
# Y = T_3(R) + (B-L)/2
# Q_EM = T_3(L) + Y = T_3(L) + T_3(R) + (B-L)/2

# 手動定義 B-L 同 T₃ 量子數
# B-L charge: quarks = +1/3, leptons = -1
BL_charge = np.array([1/3]*9 + [-1]*3)  # q^r,q^g,q^b = 1/3, l = -1

# T₃(L) under SU(2)_L: 4 = (2, 2) decomposition
# (2, 2) = (T₃(L)=+½ component) + (T₃(L)=-½ component)
# In our 4-vector: (q^r, q^g, q^b, l) = (T₃(L)=+½, T₃(L)=-½, ...)
# Actually, the 4 = (2, 2) decomposition requires the SU(4) to be broken
# as SU(4) ⊃ SU(2)_L × SU(2)_R, which mixes the color and lepton directions.

# Let me define the 4-vector in the SU(2)_L × SU(2)_R basis:
# 4 = (2, 2) = (u_L, d_L, u_R, d_R) where u/d are the isospin states
# Under SU(3)_c, these are color triplets for quarks and singlets for leptons

# 4-vector components in PS basis:
# (q^r_L, q^g_L, q^b_L, l_L) = first SU(2)_L doublet → T₃(L) = +½
# (q^r_R, q^g_R, q^b_R, l_R) = second SU(2)_R doublet → T₃(R) = +½

# But wait, the 4-dimensional representation of SU(4) as (2,2)
# under SU(2)_L × SU(2)_R means:
# The 4 components transform as:
#   ψ'_{ab} = (L^\dagger)_{ac} ψ_{cd} R_{db}
# where L ∈ SU(2)_L, R ∈ SU(2)_R, a,c ∈ {1,2}, b,d ∈ {1,2}

# So the 4 components are:
# ψ_{11}: T₃(L) = +½, T₃(R) = +½
# ψ_{12}: T₃(L) = +½, T₃(R) = -½
# ψ_{21}: T₃(L) = -½, T₃(R) = +½
# ψ_{22}: T₃(L) = -½, T₃(R) = -½

# These are the 4 components of each (4, 3) = (2, 2, 3) multiplet
# Under SU(3)_c: each component is a color singlet (lepton) for the
# lepton direction, or a color triplet for the quark direction.

# Actually, the mapping between SU(3)_c × U(1)_{B-L} and SU(2)_L × SU(2)_R
# within SU(4) is not diagonal. The 4 decomposes as:
# SU(4) → SU(3)_c × U(1)_{B-L}: 4 = 3₁/₃ ⊕ 1₋₁
# SU(4) → SU(2)_L × SU(2)_R: 4 = (2, 2)
# These are two different Cartan subalgebra choices.

# The B-L generator is part of the SU(4) Cartan subalgebra.
# In the SU(2)_L × SU(2)_R basis, the B-L charge is:
# B-L = diag(1/3, 1/3, -1, -1) in the (q^r, q^g, q^b, l) basis? No.

# Actually, let me think about this differently.
# Under SU(4) → SU(3)_c × U(1)_{B-L}:
# The SU(4) generators include:
# - SU(3)_c generators (8 of them): act on the first 3 components
# - U(1)_{B-L} generator: proportional to diag(1/3, 1/3, 1/3, -1)
#   (normalized so that Tr = 0: 3×1/3 + (-1) = 0 ✓)

# Under SU(4) → SU(2)_L × SU(2)_R:
# The SU(4) generators include:
# - SU(2)_L generators (3 of them)
# - SU(2)_R generators (3 of them)
# Remaining 9 = 15 - 3 - 3 = (3, 3) bifundamental

# The B-L generator in the SU(2)_L × SU(2)_R basis:
# B-L = diag(1/3, 1/3, 1/3, -1) in the (q^r, q^g, q^b, l) basis
# Under SU(2)_L × SU(2)_R, this needs to be re-expressed

# Let me take a simpler approach: define the 4-vector in the
# SU(2)_L × SU(2)_R basis directly, and compute the charges.

# In the Pati-Salam breaking SU(4) → SU(2)_L × SU(2)_R:
# 4 = (2, 2) = ψ_{ab} where a = L index, b = R index
# ψ_{11} = u_L (T₃(L)=+½, T₃(R)=+½)
# ψ_{12} = d_L (T₃(L)=+½, T₃(R)=-½)
# ψ_{21} = u_R (T₃(L)=-½, T₃(R)=+½)
# ψ_{22} = d_R (T₃(L)=-½, T₃(R)=-½)

# Under SU(3)_c, each of these is a color triplet for the quark part
# and a color singlet for the lepton part.

# But the (2, 2) decomposition doesn't distinguish quarks vs leptons.
# The distinction q vs l comes from the SU(3)_c embedding.

# In our 12-vector basis:
# (q^r₁, q^r₂, q^r₃, q^g₁, q^g₂, q^g₃, q^b₁, q^b₂, q^b₃, l₁, l₂, l₃)
# Each of the 4 components of the PS 4-vector is replicated 3 times (generations)

# For the 4-vector (q^r, q^g, q^b, l):
# - q^r, q^g, q^b are color triplet (SU(3)_c fundamental)
# - l is color singlet
# - Under SU(2)_L × SU(2)_R: 4 = (2, 2)
#   ψ_{11} = q^r (T₃(L)=+½, T₃(R)=+½)
#   ψ_{12} = q^g (T₃(L)=+½, T₃(R)=-½)  -- wait, this doesn't work
#   ψ_{21} = q^b (T₃(L)=-½, T₃(R)=+½)
#   ψ_{22} = l (T₃(L)=-½, T₃(R)=-½)

# Hmm, but the SU(3)_c triplet (q^r, q^g, q^b) should all have the same
# T₃(L) and T₃(R) values. They can't be split across different components.

# I think the issue is that the SU(3)_c × U(1)_{B-L} and SU(2)_L × SU(2)_R
# subgroups of SU(4) share the same Cartan subalgebra but in different bases.
# The 4 decomposes as:
# - Under SU(3)_c × U(1)_{B-L}: 4 = 3 ⊕ 1, where the 3 has B-L=1/3, 1 has B-L=-1
# - Under SU(2)_L × SU(2)_R: 4 = (2, 2)

# For the SU(4) adjoint 15:
# - Under SU(3)_c × U(1)_{B-L}: 15 = 8₀ ⊕ 3₄/₃ ⊕ 3̄₋₄/₃ ⊕ 1₀
# - Under SU(2)_L × SU(2)_R: 15 = (3,1) ⊕ (1,3) ⊕ (3,3)

# The Cartan subalgebra of SU(4) has rank 3. In the SU(3)_c × U(1)_{B-L} basis:
# H₁ = λ₃/2, H₂ = λ₈/2, H₃ = B-L (where B-L = diag(1/3, 1/3, 1/3, -1))

# In the SU(2)_L × SU(2)_R basis:
# H₁ = T₃(L), H₂ = T₃(R), H₃ = something orthogonal

# The transformation between these two bases is a rotation in the
# Cartan subalgebra. Let me compute it explicitly.

print("\n  SU(4) Cartan subalgebra in two bases:")
print("  Basis 1 (SU(3)_c × U(1)_{B-L}):")
print("    H₁ = λ₃/2, H₂ = λ₈/2, H₃ = B-L = diag(1/3, 1/3, 1/3, -1)")
print("  Basis 2 (SU(2)_L × SU(2)_R):")
print("    H₁' = T₃(L), H₂' = T₃(R), H₃' = orthogonal")

# The 4-vector components in the SU(2)_L × SU(2)_R basis:
# ψ_{ab} = (2, 2) where a = L index, b = R index
# Under SU(3)_c, each ψ_{ab} contains both a color triplet (quark) and
# a color singlet (lepton) component.

# Let me define the 4-vector more carefully:
# In the SU(3)_c × U(1)_{B-L} basis:
# 4 = (q^r, q^g, q^b, l)
# q^r, q^g, q^b: color triplet under SU(3)_c, B-L = 1/3
# l: color singlet, B-L = -1

# The SU(2)_L × SU(2)_R decomposition of the 4:
# 4 = (2, 2) means the 4 components transform as:
# ψ' = L ψ R^T where L ∈ SU(2)_L, R ∈ SU(2)_R

# Writing the 4 as a 2×2 matrix Ψ:
# Ψ = [[ψ_{11}, ψ_{12}], [ψ_{21}, ψ_{22}]]
# Ψ' = L Ψ R^†

# Under SU(3)_c, each ψ_{ab} has:
# - color triplet ("quark") component: q_{ab}
# - color singlet ("lepton") component: l_{ab}
# But the full SU(4) 4-vector is only 4-dimensional, so it can't
# contain both a color triplet AND a color singlet per component.

# I think the correct interpretation is:
# The 4-vector has 4 components. Each component is a specific
# combination of color and isospin.

# In the (2, 2) basis:
# ψ_{11} = q^r (T₃(L)=+½, T₃(R)=+½, color=red)
# ψ_{12} = q^g (T₃(L)=+½, T₃(R)=-½, color=green)
# ψ_{21} = q^b (T₃(L)=-½, T₃(R)=+½, color=blue)
# ψ_{22} = l (T₃(L)=-½, T₃(R)=-½, lepton)

# This is the standard Pati-Salam assignment where:
# - The 4-plet contains 3 quarks (one per color) + 1 lepton
# - Under SU(2)_L × SU(2)_R, they form a (2, 2) bifundamental
# - The SU(3)_c color is embedded in the off-diagonal structure

# With this assignment:
# B-L charges: q^r, q^g, q^b = 1/3, l = -1
# T₃(L): q^r, q^g = +½, q^b, l = -½
# T₃(R): q^r, q^b = +½, q^g, l = -½

# SM quantum numbers:
# Y = T₃(R) + (B-L)/2
# Q = T₃(L) + Y = T₃(L) + T₃(R) + (B-L)/2

# For each 4-plet component:
# ψ_{11} = q^r: T₃(L)=+½, T₃(R)=+½, B-L=1/3
#   → Y = ½ + ⅙ = 2/3, Q = ½ + ⅔ = 4/3... that's wrong for a quark

# Hmm, that doesn't work. Let me reconsider.

# Actually, in standard Pati-Salam:
# The 4 = (2, 2) decomposition gives:
# ψ_{ab} = (q_{ab}, l_{ab}) where a,b are SU(2) indices
# The SU(3)_c acts on the "color" index which is carried by...

# I think the issue is that in Pati-Salam, the 4 of SU(4) is
# identified with (r, g, b, y) where y is the "lepton color".
# Under SU(2)_L × SU(2)_R, these organize as:
# (r, g) = (2, 1) SU(2)_L doublet (2 components)
# (b, y) = (1, 2) SU(2)_R doublet (2 components)
# Wait, that gives 4 = (2, 1) ⊕ (1, 2), NOT (2, 2).

# Actually, (2, 2) = 2 × 2 = 4, which is the correct dimension.
# Under SU(2)_L × SU(2)_R, the 4 of SU(4) transforms as a (2, 2).

# There are two inequivalent ways to embed SU(2)_L × SU(2)_R in SU(4):
# 1. The diagonal embedding where SU(2)_L × SU(2)_R ⊂ SO(4) ⊂ SU(4)
# 2. The regular embedding

# In the (2, 2) = 4 decomposition:
# The 4 = (2, 2) means it's a bifundamental of SU(2)_L × SU(2)_R.
# The 4 components can be labeled as ψ_{ab} where a = 1,2 is L-index
# and b = 1,2 is R-index.

# For the SU(3)_c embedding:
# SU(3)_c is embedded in SU(4) such that 4 = 3 ⊕ 1 under SU(3)_c.
# The 3 is the anti-fundamental of SU(3)_c (or fundamental, depending on convention).
# The 1 is the lepton singlet.

# In the standard Pati-Salam model:
# SU(4) × SU(2)_L × SU(2)_R
# 4 = (q^r, q^g, q^b, l) under SU(3)_c × U(1)_{B-L}
# 4 = (2, 2) under SU(2)_L × SU(2)_R

# The (2, 2) decomposition means:
# (q^r, q^g) = SU(2)_L doublet portion (T₃(L) = ±½)
# (q^b, l) = SU(2)_R doublet portion (T₃(R) = ±½)

# Wait, but that gives 4 = (2, 1) ⊕ (1, 2), not (2, 2).
# (2, 1) ⊕ (1, 2) = 2 + 2 = 4 ✓

# Let me check: (2, 2) = 2 × 2 = 4 as well.
# So both (2, 2) and (2, 1) ⊕ (1, 2) have dimension 4.
# The difference is in how they transform under SU(2)_L × SU(2)_R.

# For (2, 2): the full 4 rotates as a matrix
# For (2, 1) ⊕ (1, 2): it's a direct sum of two doublets

# In Pati-Salam, the correct assignment is:
# SU(4) → SU(2)_L × SU(2)_R, 4 = (2, 2)
# This means: 4 = (2, 2) = 2 × 2 = 4-dimensional bifundamental

# The 4-vector components:
# ψ_{11} = q^r (color red, T₃(L)=+½, T₃(R)=+½)
# ψ_{12} = q^g (color green, T₃(L)=+½, T₃(R)=-½)
# ψ_{21} = q^b (color blue, T₃(L)=-½, T₃(R)=+½)
# ψ_{22} = l (lepton, T₃(L)=-½, T₃(R)=-½)

# B-L charges:
# q^r, q^g, q^b have B-L = 1/3 (quarks)
# l has B-L = -1 (lepton)

# Y = T₃(R) + (B-L)/2:
# q^r: Y = ½ + ⅙ = 2/3
# q^g: Y = -½ + ⅙ = -1/3
# q^b: Y = ½ + ⅙ = 2/3
# l: Y = -½ + (-½) = -1

# Q = T₃(L) + Y:
# q^r: Q = ½ + ⅔ = 4/3... WRONG

# OK, this doesn't work. Let me try a different assignment.

# Alternative: what if the SU(2)_L × SU(2)_R embedding is different?
# SU(4) ⊃ SU(2)_L × SU(2)_R where the 4 splits as:
# 4 = (2, 1) ⊕ (1, 2) = 2 ⊕ 2

# In this case:
# (2, 1): SU(2)_L doublet (T₃(L) = ±½), SU(2)_R singlet (T₃(R) = 0)
# (1, 2): SU(2)_L singlet (T₃(L) = 0), SU(2)_R doublet (T₃(R) = ±½)

# Under SU(3)_c × U(1)_{B-L}:
# 4 = 3₁/₃ ⊕ 1₋₁

# So the SU(2)_L doublet (2, 1) = (q^r, q^g)? Or = (q^r, q^g, q^b)?
# A doublet only has 2 components, but we have 3 colors.

# I think the issue is that the SU(3)_c and SU(2)_L × SU(2)_R
# are embedded in SU(4) in a way that's not simultaneously diagonalizable
# in the simple way I'm trying. The SU(4) → SU(2)_L × SU(2)_R
# and SU(4) → SU(3)_c × U(1)_{B-L} are two different maximal subgroups.

# Let me try yet another approach:
# Use the known SM fermion content and work backwards.

# In the SM, per generation:
# Left-handed doublet: Q_L = (u_L, d_L), Y = 1/6, (3, 2) under SU(3)_c × SU(2)_L
# Right-handed up: u_R, Y = 2/3, (3, 1)
# Right-handed down: d_R, Y = -1/3, (3, 1)
# Left-handed lepton: L_L = (ν_L, e_L), Y = -1/2, (1, 2)
# Right-handed electron: e_R, Y = -1, (1, 1)
# Right-handed neutrino: ν_R, Y = 0, (1, 1)

# Total: 16 Weyl fermions per generation (counting both chiralities)
# 3 generations: 48 SM Weyl fermions

# Under Pati-Salam SU(4) × SU(2)_L × SU(2)_R:
# Per generation: (4, 2, 1) ⊕ (4̄, 1, 2)
# 4 = (q^r, q^g, q^b, l) under SU(3)_c × U(1)_{B-L}
# 4̄ = (q̄^r, q̄^g, q̄^b, l̄) conjugate

# So per generation:
# (4, 2, 1): 4 × 2 = 8 Weyl fermions (left-handed)
# (4̄, 1, 2): 4 × 2 = 8 Weyl fermions (right-handed)
# Total: 16 Weyl fermions per generation ✓

# Under SU(12) ⊃ SU(4) × SU(3)_gen:
# 12 = (4, 3) = 3 × (4) = 3 generations of Pati-Salam 4-plets
# But this is only 12 Weyl fermions, not 16 per generation!

# So 12 = (4, 3) only gives the (4, 2, 1) part? Or only part of it?
# The 12 fundamental gives 12 Weyl fermions of one chirality.
# The 12̄ gives the conjugate.

# For 3 generations of SM fermions (48 Weyl), we need:
# 3 × [(4, 2, 1) ⊕ (4̄, 1, 2)] = 3 × (8 + 8) = 48

# Under SU(12) ⊃ SU(4) × SU(3)_gen:
# 12 = (4, 3) → gives 3 × 4 = 12 Weyl fermions (one chirality)
# 12̄ = (4̄, 3̄) → gives 3 × 4 = 12 Weyl fermions (opposite chirality)
# 66 = Λ²(12) = (6, 3) ⊕ (4̄, 3) → gives more fermions
# 66̄ = Λ²(12̄) = (6̄, 3̄) ⊕ (4, 3̄) → gives more fermions

# From O88: 3 × (12 ⊕ 12̄) = 72 Weyl fermions
# 48 SM + 24 VL

# The 12 and 12̄ give 24 Weyl fermions (12 + 12 = 24)
# But we need 48 SM + 24 VL = 72 total
# 72 = 3 × 24 = 3 × (12 ⊕ 12̄)

# So each (12 ⊕ 12̄) gives 24 Weyl fermions.
# 12 = (4, 3) under SU(4) × SU(3)_gen
# Under Pati-Salam: (4, 3) = 3 × (4) = 3 generations of Pati-Salam 4-plets

# Under SU(2)_L × SU(2)_R:
# 4 = (2, 2) → so 12 = (2, 2, 3)

# Each 4-plet = (2, 2) contains:
# - One SU(2)_L doublet (2 components)
# - One SU(2)_R doublet (2 components)
# Total: 4 Weyl fermions per generation per 12

# So 12 = 3 × 4 = 12 Weyl fermions
# 12̄ = 3 × 4̄ = 12 Weyl fermions (conjugate)
# Total from (12 ⊕ 12̄): 24 Weyl fermions

# But per SM generation we need 16 Weyl fermions, and 3 generations = 48.
# 24 < 48, so 12 ⊕ 12̄ alone is not enough!

# The remaining 48 - 24 = 24 come from:
# 66 = Λ²(12) = (6, 3) ⊕ (4̄, 3) → 6×3 + 4×3 = 18 + 12 = 30
# 66̄ = Λ²(12̄) = (6̄, 3̄) ⊕ (4, 3̄) → 30

# Total: 24 + 30 + 18 = 72 ✓ (but we need 48 SM + 24 VL)

# Actually, the O88 result says 3 × (12 ⊕ 12̄) = 72.
# I think this means we have 3 copies of the (12 ⊕ 12̄), i.e., 
# 3 copies of the 24-dimensional representation = 72 Weyl fermions.
# (Not 12 ⊕ 12̄ = 24, and then 3 × 24 = 72)

# Each copy of 12 ⊕ 12̄ gives 24 Weyl fermions = 1 generation of PS fermions?
# 12 = (4, 3) under SU(4) × SU(3)_gen

# Hmm, I think the 3 in (4, 3) IS the generation index.
# So 12 = (4, 3) = 3 generations of Pati-Salam 4-plets.
# Each 4-plet gives 4 Weyl fermions of one chirality.
# 12 gives 12 Weyl fermions (one chirality, 3 generations).

# 12̄ = (4̄, 3̄) = 3 generations of PS 4̄-plets.
# Each 4̄-plet gives 4 Weyl fermions of opposite chirality.
# 12̄ gives 12 Weyl fermions (opposite chirality, 3 generations).

# Total from (12 ⊕ 12̄): 24 Weyl fermions = 3 generations.
# But 24 ≠ 48 (SM per 3 gen). So we need 66 and 66̄ too.

# 66 = Λ²(12) = (6, 3) ⊕ (4̄, 3) under SU(4) × SU(3)_gen
# (6, 3): 6 × 3 = 18 Weyl fermions
# (4̄, 3): 4 × 3 = 12 Weyl fermions
# Total: 30 Weyl fermions

# 66̄ = Λ²(12̄) = (6̄, 3̄) ⊕ (4, 3̄): 30 Weyl fermions

# Total from (66 ⊕ 66̄): 60 Weyl fermions

# Grand total: 24 + 60 = 84... but O88 says 72 = 3 × (12 ⊕ 12̄)

# I think I'm overcomplicating this. Let me just use the O88 result:
# 3 × (12 ⊕ 12̄) = 72 Weyl fermions, giving 48 SM + 24 VL.

# The key point is that the 12 fundamental gives us the Pati-Salam
# fermions, and the extra U(1) charges are computed from the
# Cartan generators acting on the 12.

print("""
  ★★★ 重要澄清: 12 嘅費米子內容 ★★★

  SU(12) ⊃ SU(4) × SU(3)_gen
  12 = (4, 3) = 3 generations of Pati-Salam 4-plets

  Under SU(2)_L × SU(2)_R:
  4 = (2, 2) = SU(2)_L doublet ⊕ SU(2)_R doublet

  Each 4-plet (per generation):
    ψ_{11} = q^r (T₃(L)=+½, T₃(R)=+½, B-L=+⅓, color=red)
    ψ_{12} = q^g (T₃(L)=+½, T₃(R)=-½, B-L=+⅓, color=green)
    ψ_{21} = q^b (T₃(L)=-½, T₃(R)=+½, B-L=+⅓, color=blue)
    ψ_{22} = l  (T₃(L)=-½, T₃(R)=-½, B-L=-1,  lepton)

  SM quantum numbers (Y = T₃(R) + (B-L)/2, Q = T₃(L) + Y):
    q^r (u_R-like):  Y = ½ + ⅙ = ⅔,  Q = ½ + ⅔ = 7/6... 
    q^g (d_R-like):  Y = -½ + ⅙ = -⅓, Q = ½ + (-⅓) = ⅙... 
    q^b (u_L-like):  Y = ½ + ⅙ = ⅔,  Q = -½ + ⅔ = ⅙...
    l:              Y = -½ + (-½) = -1, Q = -½ + (-1) = -³/₂...

  *** 注意: 以上量子數唔 match SM！***
  原因: (2, 2) 嘅 T₃ assignment 需要同 SU(3)_c 嵌入一致。
  正確嘅量子數需要從 SU(4) generators 嘅顯式矩陣計算。
""")

# ============================================================
# 4. 用 SU(4) generators 嘅顯式矩陣計算量子數
# ============================================================
print("=" * 72)
print("第4部分: 用 SU(4) generators 顯式計算量子數")
print("=" * 72)

# SU(4) generators (Gell-Mann basis, 4×4 matrices)
# We need the 15 generators of SU(4) to find the Cartan subalgebra
# and the B-L, T₃(L), T₃(R) generators.

def su4_gellmann():
    """Return the 15 Gell-Mann generators of SU(4) as 4×4 matrices."""
    # Gell-Mann matrices for SU(4) (generalized)
    gm = []
    # 1. σ₁⊗I₂ off-diagonal: λ₁
    gm.append(np.array([[0,1,0,0],[1,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=complex))
    # 2. σ₂⊗I₂ off-diagonal: λ₂
    gm.append(np.array([[0,-1j,0,0],[1j,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=complex))
    # 3. σ₃⊗I₂ diagonal: λ₃
    gm.append(np.array([[1,0,0,0],[0,-1,0,0],[0,0,0,0],[0,0,0,0]], dtype=complex))
    # 4. off-diagonal: λ₄
    gm.append(np.array([[0,0,1,0],[0,0,0,0],[1,0,0,0],[0,0,0,0]], dtype=complex))
    # 5. off-diagonal: λ₅
    gm.append(np.array([[0,0,-1j,0],[0,0,0,0],[1j,0,0,0],[0,0,0,0]], dtype=complex))
    # 6. off-diagonal: λ₆
    gm.append(np.array([[0,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,0]], dtype=complex))
    # 7. off-diagonal: λ₇
    gm.append(np.array([[0,0,0,0],[0,0,-1j,0],[0,1j,0,0],[0,0,0,0]], dtype=complex))
    # 8. diagonal: λ₈ = diag(1,1,-2,0)/√3
    gm.append(np.array([[1,0,0,0],[0,1,0,0],[0,0,-2,0],[0,0,0,0]], dtype=complex) / math.sqrt(3))
    # 9. off-diagonal: λ₉
    gm.append(np.array([[0,0,0,1],[0,0,0,0],[0,0,0,0],[1,0,0,0]], dtype=complex))
    # 10. off-diagonal: λ₁₀
    gm.append(np.array([[0,0,0,-1j],[0,0,0,0],[0,0,0,0],[1j,0,0,0]], dtype=complex))
    # 11. off-diagonal: λ₁₁
    gm.append(np.array([[0,0,0,0],[0,0,0,1],[0,0,0,0],[0,1,0,0]], dtype=complex))
    # 12. off-diagonal: λ₁₂
    gm.append(np.array([[0,0,0,0],[0,0,0,-1j],[0,0,0,0],[0,1j,0,0]], dtype=complex))
    # 13. off-diagonal: λ₁₃
    gm.append(np.array([[0,0,0,0],[0,0,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex))
    # 14. off-diagonal: λ₁₄
    gm.append(np.array([[0,0,0,0],[0,0,0,0],[0,0,0,-1j],[0,0,1j,0]], dtype=complex))
    # 15. diagonal: λ₁₅ = diag(1,1,1,-3)/√6
    gm.append(np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-3]], dtype=complex) / math.sqrt(6))
    return gm

su4_gm = su4_gellmann()

# Cartan subalgebra of SU(4): 3 diagonal generators
# λ₃ = diag(1, -1, 0, 0)
# λ₈ = diag(1, 1, -2, 0)/√3
# λ₁₅ = diag(1, 1, 1, -3)/√6

H1 = su4_gm[2]   # λ₃: diag(1, -1, 0, 0)
H2 = su4_gm[7]   # λ₈: diag(1,1,-2,0)/√3
H3 = su4_gm[14]  # λ₁₅: diag(1,1,1,-3)/√6

print("\n  SU(4) Cartan generators (diagonal):")
print(f"    H₁ = λ₃ = diag({np.diag(H1).real})")
print(f"    H₂ = λ₈ = diag({np.diag(H2).real})")
print(f"    H₃ = λ₁₅ = diag({np.diag(H3).real})")

# SU(3)_c Cartan: λ₃ and λ₈ (first 3 components)
# U(1)_{B-L} = the part of SU(4) Cartan orthogonal to SU(3)_c
# B-L generator: diag(1/3, 1/3, 1/3, -1) normalized

# In the Gell-Mann basis, the B-L generator is:
# B-L_gen = diag(1, 1, 1, -3) / (2√3) = λ₁₅ * √6 / (2√3) = λ₁₅ * √2/2
# (Check: eigenvalues 1,1,1,-3 mean B-L = 1/3, 1/3, 1/3, -1)

# Actually, let me be more precise:
# The SU(4) generators include SU(3)_c × U(1)_{B-L}:
# The 8 SU(3)_c generators are λ₁,...,λ₈ acting on the first 3 components.
# The U(1)_{B-L} generator is proportional to diag(1,1,1,-3) normalized.
# This is λ₁₅ = diag(1,1,1,-3)/√6.

# For the 4-vector (q^r, q^g, q^b, l):
# B-L = diag(1/3, 1/3, 1/3, -1)
# = (1/3) × diag(1, 1, 1, -3) = (1/3) × √6 × λ₁₅ = √(2/3) × λ₁₅

# So B-L generator = √(2/3) × λ₁₅ (in the Gell-Mann normalization)
BL_gen = math.sqrt(2/3) * su4_gm[14]  # diag(1/3, 1/3, 1/3, -1)

print(f"\n  B-L generator: diag({np.diag(BL_gen).real})")

# SU(2)_L × SU(2)_R embedding in SU(4):
# This is a different maximal subgroup from SU(3)_c × U(1)_{B-L}
# The SU(2)_L generators are:
# T₁(L) = (λ₁ + λ₁₃)/2? No, this is not right.

# In the (2, 2) basis, the SU(2)_L generators act on the first index:
# T_a(L) = σ_a/2 ⊗ I₂ acting on the 4-vector organized as a 2×2 matrix
# SU(2)_R generators: T_a(R) = I₂ ⊗ σ_a/2

# The 4-vector as a 2×2 matrix:
# Ψ = [[ψ_{11}, ψ_{12}], [ψ_{21}, ψ_{22}]]
#   = [[q^r, q^g], [q^b, l]]
# T₃(L) = σ₃/2 ⊗ I₂: eigenvalues +½ for ψ_{1*}, -½ for ψ_{2*}
# T₃(R) = I₂ ⊗ σ₃/2: eigenvalues +½ for ψ_{*1}, -½ for ψ_{*2}

# In the 4-vector (q^r, q^g, q^b, l):
# T₃(L) = diag(½, ½, -½, -½)
# T₃(R) = diag(½, -½, ½, -½)

T3L = np.diag([0.5, 0.5, -0.5, -0.5])
T3R = np.diag([0.5, -0.5, 0.5, -0.5])

print(f"\n  T₃(L) generator: diag({np.diag(T3L).real})")
print(f"  T₃(R) generator: diag({np.diag(T3R).real})")

# Now compute SM quantum numbers for each 4-plet component:
# Y = T₃(R) + (B-L)/2
# Q = T₃(L) + Y = T₃(L) + T₃(R) + (B-L)/2

# 4-vector in SU(3)_c × U(1)_{B-L} basis: (q^r, q^g, q^b, l)
# But T₃(L) and T₃(R) are defined in the (2,2) basis: (q^r, q^g, q^b, l)
# These are the same basis!

# Let me check: in the (2,2) basis, each component has:
# ψ_{11} = q^r: T₃(L)=+½, T₃(R)=+½, B-L=+⅓
#   → Y = ½ + ⅙ = ⅔, Q = ½ + ⅔ = 7/6... wrong for SM

# This doesn't work. Let me try a different (2,2) assignment:
# ψ_{11} = l: T₃(L)=+½, T₃(R)=+½, B-L=-1
# ψ_{12} = q^r: T₃(L)=+½, T₃(R)=-½, B-L=+⅓
# ψ_{21} = q^g: T₃(L)=-½, T₃(R)=+½, B-L=+⅓
# ψ_{22} = q^b: T₃(L)=-½, T₃(R)=-½, B-L=+⅓

# Then:
# l: Y = ½ + (-½) = 0, Q = ½ + 0 = ½... still wrong

# I think the issue is more fundamental. The SU(2)_L × SU(2)_R 
# embedding in SU(4) is not simply aligned with the 
# SU(3)_c × U(1)_{B-L} embedding. The two subgroups have 
# different Cartan subalgebras.

# The correct approach is to define the 4-vector in the
# SU(3)_c basis, and then find the SU(2)_L × SU(2)_R generators
# as specific linear combinations of the SU(4) Gell-Mann matrices.

# SU(2)_L × SU(2)_R ⊂ SU(4) embedding:
# The SU(2)_L generators are combinations of λ₁, λ₂, λ₃ (for the first 2×2 block)
# and λ₁₃, λ₁₄ (for the third and fourth components)?
# No, that's not right either.

# In the standard Pati-Salam embedding:
# SU(4) ⊃ SU(2)_L × SU(2)_R where:
# SU(2)_L: acts on indices (1,2) of the 4 → generators λ₁, λ₂, λ₃
# SU(2)_R: acts on indices (3,4) of the 4 → generators λ₁₃, λ₁₄, ? 

# But the 4 doesn't decompose as 4 = (2, 1) ⊕ (1, 2) in this embedding.
# For the (2, 2) = 4 bifundamental, the embedding is different.

# For the (2, 2) embedding, think of the 4 as Ψ_{ab} = 2×2 matrix.
# SU(2)_L acts on the left index: Ψ → LΨ
# SU(2)_R acts on the right index: Ψ → ΨR^T

# The generators of SU(2)_L in the 4 representation:
# T_a(L) = σ_a/2 ⊗ I₂ in the (11, 12, 21, 22) basis
# = σ_a/2 ⊗ I₂ in the (q^r, q^g, q^b, l) basis

# T₃(L) = σ₃/2 ⊗ I₂ = diag(½, ½, -½, -½)

# The generators of SU(2)_R:
# T_a(R) = I₂ ⊗ σ_a/2
# T₃(R) = I₂ ⊗ σ₃/2 = diag(½, -½, ½, -½)

# This is correct. The issue is that in the SU(3)_c × U(1)_{B-L} basis,
# the 4-vector components have different B-L charges:
# q^r, q^g, q^b: B-L = 1/3
# l: B-L = -1

# But in the (2, 2) basis, the components are mixed. The mapping
# between the two bases is not identity.

# What if the (2, 2) decomposition doesn't map 1:1 to (q^r, q^g, q^b, l)?
# What if the mapping is:
# ψ_{11} = (q^r + q^g + q^b + l)/2 (some linear combination)
# etc.

# Actually, I think the correct statement is:
# The 4 of SU(4) can be decomposed in two different ways:
# 1. Under SU(3)_c × U(1)_{B-L}: 4 = 3₁/₃ ⊕ 1₋₁
# 2. Under SU(2)_L × SU(2)_R: 4 = (2, 2)

# The 4-vector components are the SAME in both cases. The difference
# is which subgroup generators we consider.

# So the 4-vector components are (q^r, q^g, q^b, l) in both cases.
# Under SU(2)_L × SU(2)_R, these organize as:
# (q^r, q^g) = SU(2)_L doublet (T₃(L) = ±½)?
# (q^b, l) = SU(2)_R doublet (T₃(R) = ±½)?

# But then the transformation is 4 = (2, 1) ⊕ (1, 2), not (2, 2).
# The dimension is the same (2+2=4), but the representation theory is different.

# In the (2, 2) representation, the 4 rotates as a matrix:
# Ψ → LΨR^T where L ∈ SU(2)_L, R ∈ SU(2)_R
# This is different from the direct sum (2, 1) ⊕ (1, 2).

# For the (2, 2) representation, the 4-vector is a 2×2 matrix Ψ.
# The components can be organized as:
# Ψ = [[ψ_{11}, ψ_{12}], [ψ_{21}, ψ_{22}]]
# Under SU(2)_L: Ψ → LΨ (acts on left index)
# Under SU(2)_R: Ψ → ΨR^T (acts on right index as transpose)

# In the SU(3)_c × U(1)_{B-L} basis, the 4-vector components are (q^r, q^g, q^b, l).
# These can be organized as a 2×2 matrix:
# Ψ = [[q^r, q^g], [q^b, l]]

# But this assigns:
# ψ_{11} = q^r: T₃(L)=+½, T₃(R)=+½
# ψ_{12} = q^g: T₃(L)=+½, T₃(R)=-½
# ψ_{21} = q^b: T₃(L)=-½, T₃(R)=+½
# ψ_{22} = l: T₃(L)=-½, T₃(R)=-½

# With B-L = diag(1/3, 1/3, 1/3, -1):
# q^r: B-L=1/3, T₃(L)=½, T₃(R)=½ → Y=⅔, Q=7/6... still wrong!

# OK, I think the issue is that the (2, 2) in Pati-Salam doesn't
# assign the indices the way I think. Let me try:
# ψ_{11} = l: T₃(L)=+½, T₃(R)=+½, B-L = -1
# ψ_{12} = q^r: T₃(L)=+½, T₃(R)=-½, B-L = 1/3
# ψ_{21} = q^g: T₃(L)=-½, T₃(R)=+½, B-L = 1/3
# ψ_{22} = q^b: T₃(L)=-½, T₃(R)=-½, B-L = 1/3

# l: Y = ½ + (-½) = 0, Q = ½ + 0 = ½... that's a lepton with Q=½? No.

# Hmm. Let me try yet another arrangement:
# In the standard Pati-Salam 4-plet per generation:
# The 4 = (q^r, q^g, q^b, ν_e) for the first generation
# (identifying the 4th component with ν_e instead of e)

# q^r, q^g, q^b = quarks, B-L = 1/3
# ν_e = neutrino, B-L = -1

# Under SU(2)_L × SU(2)_R, 4 = (2, 2):
# ψ_{11} = q^r → T₃(L)=+½, T₃(R)=+½
# ψ_{12} = q^g → T₃(L)=+½, T₃(R)=-½
# ψ_{21} = q^b → T₃(L)=-½, T₃(R)=+½
# ψ_{22} = ν_e → T₃(L)=-½, T₃(R)=-½

# q^r: Y = ½ + ⅙ = ⅔, Q = ½ + ⅔ = 7/6... still wrong

# I think the problem is that I'm assigning the wrong electric charges.
# Let me just compute what the standard Pati-Salam assignment gives.

# In Pati-Salam:
# 4 = (q^r, q^g, q^b, l) where l = (ν_e, e) combined
# But the 4 is only 4-dimensional, so l is just one field.
# Usually, l = ν_e (the left-handed neutrino) and e is in the 4̄.

# Under SU(2)_L × SU(2)_R, 4 = (2, 2):
# This means the 4 components form a 2×2 matrix.
# The standard assignment is:
# ψ_{11} = u^r (up quark, red)
# ψ_{12} = u^g (up quark, green)
# ψ_{21} = d^b (down quark, blue)
# ψ_{22} = ν_e (electron neutrino)

# But this mixes up and down quarks, which doesn't make sense physically.

# I think the real point is that the (2, 2) decomposition of the 4
# is NOT the same as the (3, 1) ⊕ (1, 3) decomposition of the adjoint.
# The 4 in (2, 2) means the 4 components transform as a 2×2 matrix
# under SU(2)_L × SU(2)_R, but the actual physical identification
# of the components with specific quarks/leptons requires going
# through the full breaking chain.

# Since I'm stuck on the manual assignment, let me just compute 
# the extra U(1) charges numerically and NOT try to identify them
# with specific SM fermions. The key result is the charge matrix.

print("""
  ⚠️ 注意: Pati-Salam (2, 2) 嘅量子數分配需要小心處理。
  以下直接計算 6 個 extra U(1) 對 12 維向量嘅 charge，
  唔做 SM 量子數嘅手動分配 — 呢個需要完整 breaking chain 嘅
  generator 對角化先做到。
""")

# ============================================================
# 5. 6 extra U(1) 對 12 維向量嘅 charge 分佈
# ============================================================
print("=" * 72)
print("第5部分: 6 extra U(1) charge 分佈")
print("=" * 72)

# The 6 extra U(1) generators from O107 act on the 12-dimensional
# fundamental representation. Each generator is a diagonal 12×12 matrix.
# The charge of each fermion state under each extra U(1) is the
# corresponding eigenvalue.

print("\n  6 extra U(1) charges per fermion state:")
print(f"  {'State':<10} {'E_1':<10} {'E_2':<10} {'E_3':<10} {'E_4':<10} {'E_5':<10} {'E_6':<10}")
print(f"  {'─'*10:<10} {'─'*10:<10} {'─'*10:<10} {'─'*10:<10} {'─'*10:<10} {'─'*10:<10} {'─'*10:<10}")

for idx in range(12):
    label = fermion_labels[idx]
    vals = [E_GS[i][idx] for i in range(6)]
    # 將接近 0 嘅值 truncate
    rounded = [0 if abs(v) < 1e-4 else round(v, 4) for v in vals]
    print(f"  {label:<10} {rounded[0]:<+10.4f} {rounded[1]:<+10.4f} {rounded[2]:<+10.4f} {rounded[3]:<+10.4f} {rounded[4]:<+10.4f} {rounded[5]:<+10.4f}")

# Check charge patterns
# E_1: separates quarks from leptons? q^r: +0.6124, q^g: -0.2041, q^b: -0.2041, l: -0.2041
# Not a clean B-L separation.

# Let me check if we can find a linear combination of the 6 extra U(1)
# generators that gives a clean B-L charge.

# B-L charge in the 12-vector basis:
# q^r_1, q^r_2, q^r_3 = 1/3 each
# q^g_1, q^g_2, q^g_3 = 1/3 each
# q^b_1, q^b_2, q^b_3 = 1/3 each
# l_1, l_2, l_3 = -1 each

BL_target = np.array([1/3]*9 + [-1]*3)

# Project BL_target onto the extra U(1) subspace
# E_GS is 6×12, we want coefficients c such that sum(c_i * E_GS_i) ≈ BL_target
# c = BL_target @ E_GS^T (since E_GS_i are orthonormal)

c_BL = BL_target @ E_GS.T  # 6 coefficients
BL_reconstructed = c_BL @ E_GS  # 12-vector

print(f"  B-L charge target: {BL_target}")
print(f"  B-L reconstructed: {[round(v, 4) for v in BL_reconstructed]}")
print(f"  B-L coefficients (c_i): {[round(v, 4) for v in c_BL]}")
print(f"  Reconstruction error: {np.linalg.norm(BL_reconstructed - BL_target):.2e}")

# The fact that BL_reconstructed ≠ BL_target means B-L is NOT purely
# in the extra U(1) subspace — it has components in the tensor Cartan too.

# The part of B-L in the extra U(1) subspace:
BL_extra = c_BL @ E_GS
BL_tensor = BL_target - BL_extra
print(f"\n  B-L in extra U(1) subspace: {[round(v, 4) for v in BL_extra]}")
print(f"  B-L in tensor subspace: {[round(v, 4) for v in BL_tensor]}")
print(f"  |B-L_extra|/|B-L_total| = {np.linalg.norm(BL_extra)/np.linalg.norm(BL_target):.4f}")

# Same for hypercharge
# Y = T₃(R) + (B-L)/2 in the 12-vector basis
# We need to extend T₃(R) from 4-vector to 12-vector
# T₃(R) = diag(½, -½, ½, -½) in the 4-vector (q^r, q^g, q^b, l)
# Extend to 12-vector: replicate 3 times (generations)

T3R_4 = np.array([0.5, -0.5, 0.5, -0.5])
T3R_12 = np.tile(T3R_4, 3)  # [0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5]
# Wait, the 12-vector is (q^r_1, q^r_2, q^r_3, q^g_1, q^g_2, q^g_3, q^b_1, q^b_2, q^b_3, l_1, l_2, l_3)
# T₃(R) in the 4-vector (q^r, q^g, q^b, l) = (½, -½, ½, -½)
# So T₃(R) in 12-vector = (½, ½, ½, -½, -½, -½, ½, ½, ½, -½, -½, -½)
T3R_12 = np.array([0.5]*3 + [-0.5]*3 + [0.5]*3 + [-0.5]*3)

Y_target = T3R_12 + BL_target / 2
print(f"\n  Hypercharge target: {[round(v, 4) for v in Y_target]}")

# Project Y onto extra U(1) subspace
c_Y = Y_target @ E_GS.T
Y_extra = c_Y @ E_GS
Y_tensor = Y_target - Y_extra
print(f"  Y in extra U(1): {[round(v, 4) for v in Y_extra]}")
print(f"  |Y_extra|/|Y_total| = {np.linalg.norm(Y_extra)/np.linalg.norm(Y_target):.4f}")

# ============================================================
# 6. 總結
# ============================================================
print("\n" + "=" * 72)
print("O114-1 總結")
print("=" * 72)

print(f"""
  ✅ 12 維向量 Pati-Salam 分解定義:
     12 = (4, 3) = (q^r, q^g, q^b, l) × 3 generations

  ✅ 6 extra U(1) generators 嘅 12×12 作用已計算:
     每個 generator 對 12 個費米子態嘅 charge 已列出

  ✅ B-L charge 分析:
     B-L 佔 extra U(1) subspace 比例 = {np.linalg.norm(BL_extra)/np.linalg.norm(BL_target):.4f}
     → B-L 主要喺 tensor Cartan subspace, 唔係 extra U(1)

  🟡 需要進一步:
     - 完整 SU(2)_L × SU(2)_R generators 喺 12-vector 嘅作用
     - SM 量子數 (Y, T₃, Q) 嘅精確分配
     - 6 extra U(1) 嘅 charge sum rules 檢查

  🔴 誠實限制:
     - Pati-Salam (2, 2) 同 SU(3)_c x U(1)_B-L 嵌入嘅 mapping 未完全解開
     - 需要 SU(4) → SU(2)_L × SU(2)_R 嘅 generator 顯式旋轉
""")

# 保存結果
results = {
    "id": "O114-1",
    "name": "Fermion Embedding",
    "fermion_states": fermion_labels,
    "extra_u1_charges": E_GS.tolist(),
    "BL_charge_target": BL_target.tolist(),
    "BL_in_extra_u1": BL_extra.tolist(),
    "BL_extra_ratio": np.linalg.norm(BL_extra)/np.linalg.norm(BL_target),
    "hypercharge_target": Y_target.tolist(),
    "Y_in_extra_u1": Y_extra.tolist(),
    "Y_extra_ratio": np.linalg.norm(Y_extra)/np.linalg.norm(Y_target),
    "status": "🟡 PARTIAL",
    "open_issues": [
        "SM quantum number assignment needs SU(4) generator rotation",
        "SU(2)_L × SU(2)_R embedding in SU(4) not fully resolved",
        "Need to extend to 3×(12⊕12̄) = 72 fermions",
    ],
    "timestamp": "2026-08-29",
}

with open(os.path.join(BASE, "data", "01_fermion_embedding.json"), "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ 結果已保存到 data/01_fermion_embedding.json")