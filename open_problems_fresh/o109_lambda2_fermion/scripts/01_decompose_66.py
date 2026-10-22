#!/usr/bin/env python3
"""
O109 — 66 = Λ²(12) fermion 對應: Phase 1+2
===========================================
Decompose 66 = Λ²(12) under SU(12)→SU(4)×SU(3)→SM breaking chain.
Map each component to SM fermion states and identify the 18 extra.
"""

import json
from collections import OrderedDict

# ============================================================
# 1. 66 = Λ²(12) under SU(4)×SU(3)
# ============================================================
# 12 = (4,3) under SU(4)_PS × SU(3)_gen
# Λ²(12) = (Λ²(4), Sym²(3)) ⊕ (Sym²(4), Λ²(3))
#        = (6, 6) ⊕ (10, 3̄)
# dim: 6×6 + 10×3 = 36 + 30 = 66 ✓

branching_su4su3 = {
    "component": "Λ²(12)",
    "total_dim": 66,
    "under_SU4xSU3": [
        {"rep": "(6, 6)", "dim": 36, "idcm_id": "h11 = K_tree+N_gen = 33+3"},
        {"rep": "(10, 3̄)", "dim": 30, "idcm_id": "Nd−2L₄ = 44−14"},
    ]
}

# ============================================================
# 2. Decompose SU(4) reps under SU(3)_c × U(1)_{B-L}
# ============================================================
# SU(4)_PS → SU(3)_c × U(1)_{B-L}
# 4 = 3_{1/3} ⊕ 1_{-1}
# 6 = Λ²(4) = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀
# 10 = Sym²(4) = 6_{2/3} ⊕ 3̄_{-2/3} ⊕ 1_{-2} ⊕ 1_{2/3}... wait let me compute properly

# SU(4) branching: 4 = 3_{q} ⊕ 1_{q'} under SU(3)×U(1)
# Standard Pati-Salam: 4 = 3_{1/3} ⊕ 1_{-1} under SU(3)_c × U(1)_{B-L}
# where B-L charge is normalized so that q=1/3 for triplet, q=-1 for singlet

# Λ²(4): 4 ∧ 4
# (3_{1/3} ⊕ 1_{-1}) ∧ (3_{1/3} ⊕ 1_{-1})
# = Λ²(3_{1/3}) ⊕ (3_{1/3} ⊗ 1_{-1}) ⊕ Λ²(1_{-1})
# = 3̄_{2/3} ⊕ 3_{1/3-1} ⊕ 0
# = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1_0 ⊕ 1_0
# Wait: Λ²(3) = 3̄, and the U(1) charge adds: 1/3+1/3=2/3
# 3_{1/3} ⊗ 1_{-1} = 3_{1/3-1} = 3_{-2/3}
# So 6 = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1_0 ⊕ 1_0

# Sym²(4): 4 ⊙ 4
# = Sym²(3_{1/3}) ⊕ (3_{1/3} ⊗ 1_{-1}) ⊕ Sym²(1_{-1})
# = 6_{2/3} ⊕ 3_{1/3-1} ⊕ 1_{-2}
# = 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}

# Let me verify: dim check for SU(4) reps
# Λ²(4) = 6 ✓, Sym²(4) = 10 ✓

su4_breaking = {
    "4": {"under_SU3xU1": "3_{1/3} ⊕ 1_{-1}", "dim": 4},
    "6=Λ²(4)": {"under_SU3xU1": "3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀", "dim": 6},
    "10=Sym²(4)": {"under_SU3xU1": "6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}", "dim": 10},
}

# ============================================================
# 3. Decompose SU(3)_gen reps under SU(3)_c (flavor)
# ============================================================
# For the (6, 6) component: 6 under SU(3)_gen
# 6 = Sym²(3) = 6 dimensional symmetric representation
# 3̄ = Λ²(3) = 3̄ dimensional antisymmetric representation

# But wait — SU(3)_gen here is a flavor symmetry, not SU(3)_c color.
# The tensor embedding 12 = (4,3) uses SU(3) as the "generation" group.
# Under SU(3)_gen: 3 = fundamental (generation index)
# 6 = Sym²(3) = symmetric generation pairs
# 3̄ = Λ²(3) = antisymmetric generation pairs

# So (6, 6) means: SU(4) rep 6 × SU(3)_gen rep 6 = 36
# And (10, 3̄) means: SU(4) rep 10 × SU(3)_gen rep 3̄ = 30

# ============================================================
# 4. Full decomposition under SM gauge group
# ============================================================
# SM gauge group: SU(3)_c × SU(2)_L × U(1)_Y
# Breaking chain: SU(4)_PS → SU(3)_c × U(1)_{B-L} → SU(3)_c × U(1)_Y
#                 SU(2)_R × U(1)_{B-L} → U(1)_Y
# SU(3)_gen → remains as flavor index (broken by Yukawa)

# Let me decompose the (6, 6) component:
# 6 of SU(4) → 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀
# 6 of SU(3)_gen → generation pairs (symmetric)

# Each of these carries a generation index from 6 of SU(3)_gen
# 6 = {11, 22, 33, 12, 13, 23} (symmetric pairs)

# (6, 6) = [3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀] × 6_gen
# = 4 SU(4) components × 6 gen pairs = 24 states
# Wait, but (6, 6) = 36 total. 4 × 6 = 24 ≠ 36.
# That's wrong because 6 of SU(3)_gen is not the same as "6 generation pairs".

# Let me reconsider. Under SU(3)_gen:
# 6 is the Sym²(3) rep — symmetric tensor product of two generation indices.
# This means (6, 6) has states that are symmetric in both color-family and generation.

# The full decomposition needs to track both SU(4) and SU(3)_gen quantum numbers.

# Let me think about this differently. The key question is:
# How does 66 = Λ²(12) decompose into SM fermion states?

# 12 = (4, 3) = left-handed fermions per generation
# Λ²(12) = antisymmetric product of two "12" states
# Physically: two-fermion composites, or more likely, the 66 carries
# the right-handed fermions that pair with the left-handed ones from 12.

# Actually, let me reconsider the whole approach.
# In the 3×(12⊕12̄) = 72 scheme from O88:
# - 3×12 = 36 left-handed fermions (3 generations)
# - 3×12̄ = 36 right-handed antifermions
# Total 48 SM + 24 VL

# 66 = Λ²(12) is a DIFFERENT rep from both 12 and 12̄.
# It's not the fermion content itself — it's the antisymmetric product.

# Perhaps the 66 states correspond to:
# 1. Composite fermions (diquark-like)?
# 2. The 66 positive roots of SU(12)?
# 3. Something else entirely?

# Let me look at this from the IDCM perspective:
# 66 = 2×K_tree = 2×33
# This suggests 66 = left + right copies of the 33 tree structure.

# In the 3×12 = 36 framework:
# 36 = h11 = K_tree + N_gen = 33 + 3
# 33 = K_tree (tree structure)
# 3 = N_gen (generation index)

# 66 = 2×33 = 2×K_tree
# This is TWICE the tree structure, without the generation index.

# Maybe: 66 = 33_L ⊕ 33_R = left-handed tree + right-handed tree?

# Under SU(4)×SU(3):
# 66 = (6, 6) ⊕ (10, 3̄) = 36 ⊕ 30

# 36 = (6, 6) = 6_SU(4) × 6_SU(3)_gen
# 30 = (10, 3̄) = 10_SU(4) × 3̄_SU(3)_gen

# In terms of SM states, let me decompose (6, 6) and (10, 3̄):

def decompose_6_of_su4():
    """Decompose 6 = Λ²(4) of SU(4) under SU(3)_c × U(1)_{B-L}"""
    # 4 = 3_{1/3} ⊕ 1_{-1}
    # Λ²(4) = (3 ⊕ 1) ∧ (3 ⊕ 1)
    # = Λ²(3) ⊕ (3 ⊗ 1) ⊕ Λ²(1)
    # = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1_0 ⊕ 1_0
    return {
        "3̄_{2/3}": {"dim": 3, "SU3_c": "3̄", "U1_BL": "2/3", "count": 3},
        "3_{-2/3}": {"dim": 3, "SU3_c": "3", "U1_BL": "-2/3", "count": 3},
        "1₀ (a)": {"dim": 1, "SU3_c": "1", "U1_BL": "0", "count": 1},
        "1₀ (b)": {"dim": 1, "SU3_c": "1", "U1_BL": "0", "count": 1},
    }

def decompose_10_of_su4():
    """Decompose 10 = Sym²(4) of SU(4) under SU(3)_c × U(1)_{B-L}"""
    # Sym²(4) = (3 ⊕ 1) ⊙ (3 ⊕ 1)
    # = Sym²(3) ⊕ (3 ⊗ 1) ⊕ Sym²(1)
    # = 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}
    return {
        "6_{2/3}": {"dim": 6, "SU3_c": "6", "U1_BL": "2/3", "count": 6},
        "3_{-2/3}": {"dim": 3, "SU3_c": "3", "U1_BL": "-2/3", "count": 3},
        "1_{-2}": {"dim": 1, "SU3_c": "1", "U1_BL": "-2", "count": 1},
    }

# Now combine with SU(3)_gen reps
# (6, 6): 6_SU4 × 6_gen
# (10, 3̄): 10_SU4 × 3̄_gen

# Under SU(3)_gen, the 6 = Sym²(3) splits into generation pairs:
# 6 = {11, 22, 33, 12, 13, 23} — symmetric under gen↔gen'
# 3̄ = Λ²(3) = {[12], [13], [23]} — antisymmetric under gen↔gen'

# But this is a FLAVOR symmetry, not a gauge symmetry.
# The physical interpretation is that the 66 carries generation indices
# that can be symmetric or antisymmetric.

# Let me compute the full SM content of (6, 6):

print("=" * 70)
print("O109 PHASE 1: 66 = Λ²(12) FULL DECOMPOSITION")
print("=" * 70)

# Summary
print("\n## 1. 66 = Λ²(12) under SU(4)×SU(3)")
print("   12 = (4, 3) under SU(4)_PS × SU(3)_gen")
print("   Λ²(12) = (6, 6) ⊕ (10, 3̄)")
print("   dim: 6×6 + 10×3 = 36 + 30 = 66 ✓")

print("\n## 2. (6, 6) = 36 — SU(4) rep 6 × SU(3)_gen rep 6")
print("\n### 2a. 6 of SU(4) → SU(3)_c × U(1)_{B-L}")
print("   4 = 3_{1/3} ⊕ 1_{-1}")
print("   Λ²(4) = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀")
print("   dim: 3+3+1+1 = 6 ✓")

six_su4 = decompose_6_of_su4()
print("\n   Component | SU(3)_c | U(1)_{B-L} | dim")
print("   " + "-"*45)
for name, info in six_su4.items():
    print(f"   {name:>12s} | {info['SU3_c']:>8s} | {info['U1_BL']:>10s} | {info['dim']}")

print("\n### 2b. 6 of SU(3)_gen = Sym²(3)")
print("   6 = {11, 22, 33, 12, 13, 23} (symmetric generation pairs)")
print("   Each SU(4) component above gets 6 generation copies")
print("   Total: 4 SU(4) components × 6 gen = 24 ... ?")
print("   NO! Each 6_SU4 component has dim 3, 3, 1, 1 respectively.")
print("   Total = (3+3+1+1) × 6 = 8 × 6 = 48 ≠ 36")
print("   This is WRONG — 6 of SU(4) is NOT a sum of 4 irreps.")

# CORRECT approach:
# (6, 6) = 6_SU(4) ⊗ 6_SU(3)_gen
# As a tensor product, each SU(4) state combines with each SU(3)_gen state
# 6 × 6 = 36 states total

# Under SU(3)_c × U(1)_{B-L}:
# 6_SU(4) → 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀
# So (6, 6) → (3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀) ⊗ 6_gen
#         = 3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen ⊕ 1₀⊗6_gen ⊕ 1₀⊗6_gen
# dim: 3×6 + 3×6 + 1×6 + 1×6 = 18+18+6+6 = 48
# That's still wrong! 48 ≠ 36

# The issue is that 6 of SU(4) is an IRREDUCIBLE representation.
# We can't just sum the dimensions of the SU(3)×U(1) components.
# The 6 is 6-dimensional, and under SU(3)×U(1) it splits as:
# 6 → 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀
# So the total number of states in (6, 6) = 6 × 6 = 36
# Under SU(3)_c × U(1)_{B-L} × SU(3)_gen:
# (3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀) ⊗ 6_gen
# = 3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen ⊕ 1₀⊗6_gen ⊕ 1₀⊗6_gen
# dims: 3×6 + 3×6 + 1×6 + 1×6 = 18+18+6+6 = 48

# WAIT. 48 ≠ 36. Something is wrong with my decomposition.
# Let me recheck: 6 of SU(4) under SU(3)×U(1)
# 
# 4 = 3_a ⊕ 1_b under SU(3)×U(1)
# Λ²(4) = Λ²(3_a) ⊕ (3_a ⊗ 1_b) ⊕ Λ²(1_b)
# = 3̄_{2a} ⊕ 3_{a+b} ⊕ 0
# 
# With a=1/3, b=-1:
# = 3̄_{2/3} ⊕ 3_{1/3-1} ⊕ 0
# = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 0
# 
# But what about the U(1) charges? Let me be more careful.
# The U(1) charge of the 3 state in 4 is q=1/3 (B-L charge)
# The U(1) charge of the 1 state in 4 is q=-1
# 
# Λ²(3_{1/3}): antisymmetric product of 3 and 3
#   = 3̄ with U(1) charge = 1/3 + 1/3 = 2/3
# 
# 3_{1/3} ⊗ 1_{-1}: tensor product
#   = 3 with U(1) charge = 1/3 + (-1) = -2/3
# 
# Λ²(1_{-1}): antisymmetric product of 1 and 1
#   = 1 with U(1) charge = (-1) + (-1) = -2... wait, no
#   Λ²(1) = 0 (antisymmetric product of a 1D space is 0)
#   Actually, for a 1-dimensional vector space, Λ²(V) = 0.
#   So Λ²(1_{-1}) = 0, not 1_{-2}.
# 
# So 6 = 3̄_{2/3} ⊕ 3_{-2/3} ⊕ 1₀ ⊕ 1₀
# The two 1₀ come from the fact that the 4 has two 1-dimensional subspaces
# that contribute to the antisymmetric product.
# No wait, Λ²(1_{-1}) = 0. So where do the two 1₀ come from?
# 
# Let me recalculate more carefully:
# 
# 4 = 3 ⊕ 1 under SU(3)×U(1)
# Basis: {e₁, e₂, e₃} (color triplet), {e₄} (lepton singlet)
# 
# Λ²(4) has basis: {e₁∧e₂, e₁∧e₃, e₂∧e₃, e₁∧e₄, e₂∧e₄, e₃∧e₄}
# = 6 basis vectors
# 
# Under SU(3): e₁∧e₂, e₁∧e₃, e₂∧e₃ transform as 3̄
#              e₁∧e₄, e₂∧e₄, e₃∧e₄ transform as 3
# 
# U(1) charges:
# q(e₁) = q(e₂) = q(e₃) = 1/3
# q(e₄) = -1
# q(e₁∧e₂) = 1/3 + 1/3 = 2/3
# q(e₁∧e₄) = 1/3 + (-1) = -2/3
# 
# So: 3̄_{2/3} ⊕ 3_{-2/3} — that's only 6 states. Where are the 1₀ singlets?
# 
# OH! I think I made an error. Let me reconsider.
# 
# 4 = 3_{1/3} ⊕ 1_{-1}
# The 4 is 4-dimensional. Λ²(4) = 6-dimensional.
# 3̄_{2/3} = 3 states (from e₁∧e₂, e₁∧e₃, e₂∧e₃)
# 3_{-2/3} = 3 states (from e₁∧e₄, e₂∧e₄, e₃∧e₄)
# Total = 6 = dim(Λ²(4)) ✓
# 
# There are NO 1₀ singlets in Λ²(4)! My earlier decomposition was wrong.
# Λ²(1) = 0, not 1₀. So:
# 6 of SU(4) → 3̄_{2/3} ⊕ 3_{-2/3} under SU(3)_c × U(1)_{B-L}
# 
# And for Sym²(4):
# 4 = 3_{1/3} ⊕ 1_{-1}
# Sym²(4) = Sym²(3_{1/3}) ⊕ (3_{1/3} ⊗ 1_{-1}) ⊕ Sym²(1_{-1})
# = 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}
# 
# Sym²(3_{1/3}) = 6_{2/3} (6 states, U(1)=2/3)
# 3_{1/3} ⊗ 1_{-1} = 3_{-2/3} (3 states)
# Sym²(1_{-1}) = 1_{-2} (1 state)
# Total = 6+3+1 = 10 = dim(Sym²(4)) ✓

# So let me redo the decomposition:

print("\n\n## CORRECTED DECOMPOSITION")
print("\n### 6 = Λ²(4) under SU(3)_c × U(1)_{B-L}")
print("   6 = 3̄_{2/3} ⊕ 3_{-2/3}")
print("   dim: 3 + 3 = 6 ✓")

print("\n### 10 = Sym²(4) under SU(3)_c × U(1)_{B-L}")
print("   10 = 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}")
print("   dim: 6 + 3 + 1 = 10 ✓")

# ============================================================
# Now decompose (6, 6) = 36 and (10, 3̄) = 30
# ============================================================

print("\n" + "=" * 70)
print("## 3. FULL SM CONTENT OF 66 = Λ²(12)")
print("=" * 70)

# (6, 6) = 36: 6_SU4 × 6_SU3_gen
# 6_SU4 → 3̄_{2/3} ⊕ 3_{-2/3}
# 6_SU3_gen → Sym²(3) = generation symmetric pairs
# Total: (3̄_{2/3} ⊕ 3_{-2/3}) ⊗ 6_gen
# dim: 3×6 + 3×6 = 18 + 18 = 36 ✓

print("\n### 3a. (6, 6) = 36 states")
print("   (3̄_{2/3} ⊕ 3_{-2/3}) ⊗ 6_gen")
print("   = 3̄_{2/3}⊗6_gen  ⊕  3_{-2/3}⊗6_gen")
print("   dim: 3×6 + 3×6 = 18 + 18 = 36 ✓")

# (10, 3̄) = 30: 10_SU4 × 3̄_SU3_gen
# 10_SU4 → 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}
# 3̄_SU3_gen → Λ²(3) = generation antisymmetric pairs
# Total: (6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}) ⊗ 3̄_gen
# dim: 6×3 + 3×3 + 1×3 = 18 + 9 + 3 = 30 ✓

print("\n### 3b. (10, 3̄) = 30 states")
print("   (6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}) ⊗ 3̄_gen")
print("   = 6_{2/3}⊗3̄_gen  ⊕  3_{-2/3}⊗3̄_gen  ⊕  1_{-2}⊗3̄_gen")
print("   dim: 6×3 + 3×3 + 1×3 = 18 + 9 + 3 = 30 ✓")

# ============================================================
# 4. SM fermion correspondence
# ============================================================
print("\n" + "=" * 70)
print("## 4. SM FERMION CONTENT COMPARISON")
print("=" * 70)

# From O88: 3×(12⊕12̄) = 72 contains 48 SM Weyl fermions
# 3×12 = 36 left-handed: 27 quarks + 9 leptons
# 3×12̄ = 36 right-handed: 27 antiquarks + 9 antileptons

# Let's list the SM fermion content per generation:
# Under SU(3)_c × SU(2)_L × U(1)_Y:
sm_per_gen = {
    "Q_L": {"rep": "(3, 2)_{1/6}", "count": 6, "type": "left-handed quark doublet"},
    "u_R": {"rep": "(3, 1)_{2/3}", "count": 3, "type": "right-handed up-type quark"},
    "d_R": {"rep": "(3, 1)_{-1/3}", "count": 3, "type": "right-handed down-type quark"},
    "L_L": {"rep": "(1, 2)_{-1/2}", "count": 2, "type": "left-handed lepton doublet"},
    "e_R": {"rep": "(1, 1)_{-1}", "count": 1, "type": "right-handed charged lepton"},
    "ν_R": {"rep": "(1, 1)_0", "count": 1, "type": "right-handed neutrino"},
}
sm_total = sum(v["count"] for v in sm_per_gen.values())
print(f"\n   SM fermions per generation: {sm_total} Weyl")
print(f"   SM fermions total (3 gen):  {sm_total * 3} Weyl")

print("\n   Per generation breakdown:")
print("   {:>8s} | {:>20s} | {:>5s}".format('State', 'Rep', 'Count'))
print("   {:>8s}-+-{:>20s}-+-{:>5s}".format('-'*8, '-'*20, '-'*5))
for name, info in sm_per_gen.items():
    print("   {:>8s} | {:>20s} | {:>5d}".format(name, info['rep'], info['count']))

# ============================================================
# 5. Map 66 components to SM fermions
# ============================================================
print("\n" + "=" * 70)
print("## 5. MAPPING: 66 → SM FERMIONS")
print("=" * 70)

# The key insight: 66 = Λ²(12) is the antisymmetric product of two
# fundamental 12 representations. Under the PS embedding:
# 12 = (4, 3) = left-handed fermions
# Λ²(12) = antisymmetric two-fermion states

# Physically, 66 can represent:
# 1. RIGHT-HANDED fermions (12̄ = anti-fundamental) embedded in Λ²(12)
#    Because Λ²(12) contains 12̄ via the SU(12) embedding?
#    Actually, 12 ⊗ 12 = 66 ⊕ 78, and 12 ⊗ 12̄ = 1 ⊕ 143
#    So 66 does NOT contain 12̄.

# 2. Gauge bosons? 66 = adj(SO(12)), but SO(12) is not the SM gauge group.
#    The gauge bosons of SU(12) are in the 143 (adjoint), not 66.

# 3. Higgs-like scalars? Possible but not fermions.

# 4. Exotic fermions at high scale?

# Let me think about what 66 = 2×K_tree means physically.
# K_tree = 33 = tree structure depth
# 2×K_tree = 66 = two copies of the tree

# In the 3×12 = 36 framework:
# 36 = K_tree + N_gen = 33 + 3
# 33 = K_tree modes
# 3 = N_gen generation indices

# 66 = 2×33 = 2×K_tree
# This is EXACTLY the tree structure counted twice.

# Hypothesis: 66 = Λ²(12) = SO(12) gauge bosons
# Under the breaking SU(12) → SO(12), the 66 decomposes as:
# 66 = adj(SO(12)) = SO(12) gauge bosons
# And the remaining 77 = 143 - 66 = SU(12)/SO(12) coset = Higgs

# This is the P7 decomposition from O96!
# 66 = adj(SO(12)) = gauge bosons of SO(12)
# 77 = coset = broken generators (Higgs)

# But the question is about FERMION correspondence, not gauge bosons.

# Let me reconsider. The 66 = Λ²(12) = (6, 6) ⊕ (10, 3̄)
# Under SU(4)×SU(3), these are:

# (6, 6) = 36 states:
# Under SU(3)_c × U(1)_{B-L}: 6→3̄_{2/3}⊕3_{-2/3}
# With SU(3)_gen rep 6 (symmetric generation pairs)
# = 3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen
# These are color antitriplet/antiquark-like states with generation pairs

# (10, 3̄) = 30 states:
# Under SU(3)_c × U(1)_{B-L}: 10→6_{2/3}⊕3_{-2/3}⊕1_{-2}
# With SU(3)_gen rep 3̄ (antisymmetric generation pairs)
# = 6_{2/3}⊗3̄_gen ⊕ 3_{-2/3}⊗3̄_gen ⊕ 1_{-2}⊗3̄_gen

# Now let me compare with the SM fermion content from 3×(12⊕12̄):
# 12 = (4, 3) = 3_{1/3}⊕1_{-1} ⊗ 3_gen
# 12̄ = (4̄, 3̄) = 3̄_{-1/3}⊕1_{1} ⊗ 3̄_gen

# 3×12 = left-handed: 3×(3_{1/3}⊕1_{-1})⊗3_gen
#        = 3×(3_{1/3}⊗3_gen) ⊕ 3×(1_{-1}⊗3_gen)
#        = 27_{1/3} + 9_{-1} (with generation indices)

# 3×12̄ = right-handed: 3×(3̄_{-1/3}⊕1_{1})⊗3̄_gen
#         = 3×(3̄_{-1/3}⊗3̄_gen) ⊕ 3×(1_{1}⊗3̄_gen)
#         = 27_{-1/3} + 9_{1} (with generation indices)

# 66 = Λ²(12) contents:
# (6, 6) = 36: 3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen
# (10, 3̄) = 30: 6_{2/3}⊗3̄_gen ⊕ 3_{-2/3}⊗3̄_gen ⊕ 1_{-2}⊗3̄_gen

# Key observation: The 66 states have DIFFERENT U(1)_{B-L} charges
# from the SM fermions in 12/12̄!

# SM fermions in 12: q_{B-L} = 1/3 (quarks) or -1 (leptons)
# SM antifermions in 12̄: q_{B-L} = -1/3 (antiquarks) or 1 (antileptons)

# 66 states: q_{B-L} = 2/3, -2/3, or -2
# These are NOT the same as SM fermion charges!

# 3̄_{2/3}: B-L=2/3 — this is different from quarks (1/3) or antiquarks (-1/3)
# 3_{-2/3}: B-L=-2/3 — different from either
# 6_{2/3}: B-L=2/3 — color sextet! Not in SM
# 1_{-2}: B-L=-2 — exotic!

# So 66 does NOT contain the SM fermions directly.
# The SM fermions are in 3×(12⊕12̄) = 72.

# Then what is 66? Some possibilities:
# 1. 66 = gauge bosons of SO(12) (adjoint rep)
# 2. 66 = vector-like fermion partners (the 24 VL + extra)
# 3. 66 = something else entirely

# Let me compute: 48 SM fermions + 24 VL = 72 from 3×(12⊕12̄)
# 66 = Λ²(12) is a different rep
# 66 - 48 = 18, but 66 is not a subset of 72.

# Actually, let me reconsider. The 3×(12⊕12̄) = 72 is the TOTAL fermion
# content of the theory. 66 = Λ²(12) is a DIFFERENT representation,
# carrying different physical states.

# The question is: what PHYSICAL states does 66 carry?

# Possibilities:
# A) Gauge bosons of SO(12) subalgebra
# B) Extra fermions beyond the 3×(12⊕12̄) = 72
# C) Higgs-like scalars
# D) The 66 = 2×K_tree could represent the tree-level mass spectrum

# Let me check option (A): 66 = adj(SO(12))
# Under SU(4)×SU(3):
# 66 = (6, 6) ⊕ (10, 3̄)
# Under SU(3)_c × U(1)_{B-L} × SU(3)_gen:
# (6, 6) = (3̄_{2/3} ⊕ 3_{-2/3}) ⊗ 6_gen
#        = 3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen
# (10, 3̄) = (6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}) ⊗ 3̄_gen
#         = 6_{2/3}⊗3̄_gen ⊕ 3_{-2/3}⊗3̄_gen ⊕ 1_{-2}⊗3̄_gen

# If 66 = gauge bosons, these would be the SO(12) gauge bosons that
# are NOT in the SM gauge group. The SM gauge bosons are in 143 = adj(SU(12)),
# specifically in the (15, 1) ⊕ (1, 8) ⊕ (15, 8) decomposition.

# 143 = (15, 1) ⊕ (1, 8) ⊕ (15, 8) under SU(4)×SU(3)
# 66 = (6, 6) ⊕ (10, 3̄) under SU(4)×SU(3)
# 77 = 143 - 66 = coset

# So the SM gauge bosons (8 gluons + 3 weak + 1 B + ...) are in 143, not 66.
# 66 contains the EXTRA gauge bosons of SO(12) ⊂ SU(12).

# This is getting complex. Let me just write the comprehensive analysis
# script and output the results.

print("\n\n" + "=" * 70)
print("KEY FINDING: 66 = Λ²(12) B-L CHARGES vs SM")
print("=" * 70)

print("""
SM fermions in 12:    q_{B-L} =  1/3 (quarks), -1 (leptons)
SM antifermions in 12̄: q_{B-L} = -1/3 (antiquarks), 1 (antileptons)

66 states:            q_{B-L} =  2/3, -2/3, -2
                          → DIFFERENT from SM fermion charges!
                          → 66 does NOT contain SM fermions directly.
""")

# So the 66 states are NOT the SM fermions.
# They are either:
# 1. Gauge bosons of SO(12) ⊂ SU(12)
# 2. Vector-like fermion partners at high scale
# 3. Something else

# Let me count the 24 VL fermions from 3×(12⊕12̄):
# 72 total - 48 SM = 24 VL
# These 24 VL must have SM quantum numbers.
# Under SU(4)×SU(3):
# 12 = (4, 3) → SM: (3, 3)_{1/3} ⊕ (1, 3)_{-1}
# 12̄ = (4̄, 3̄) → SM: (3̄, 3̄)_{-1/3} ⊕ (1, 3̄)_{1}
# 3×(12⊕12̄) = 3 copies of each

# The 24 VL come from 3 copies of (12⊕12̄) but only 1 copy of 12 is
# "active" as SM fermions? Or 3 copies of specific components?

# Actually from O88: the 24 VL come from the extra 2 copies of 12⊕12̄
# beyond the 1 copy that gives SM fermions.
# 3×(12⊕12̄) = 72
# SM fermions = 48 (1 copy of 12⊕12̄ per generation)
# VL = 24 (the remaining 2 copies of 12⊕12̄ = 24)
# WAIT: 1 copy of 12⊕12̄ = 24, not 48.
# And 3 copies = 72. So SM = 48 = 2 copies of 12⊕12̄?
# Or SM = 1 copy of 12⊕12̄ per generation = 24, but we have 48 SM fermions?

# Let me re-read O88 more carefully.
# From O88 closure report:
# "3×(12⊕12̄) = 72-dimensional"
# "SM fermions: 48 (3 generations × 16 Weyl)"
# "Extra vector-like pairs: 24 (獲得質量 at high scale)"

# So: 72 total = 48 SM + 24 VL
# 48 SM = 3 × 16 = 3 generations of 16 Weyl fermions each
# 24 VL = extra vector-like pairs

# Under SU(4)×SU(3):
# 12 = (4, 3) → (3, 3)_{1/3} ⊕ (1, 3)_{-1}
# 12̄ = (4̄, 3̄) → (3̄, 3̄)_{-1/3} ⊕ (1, 3̄)_{1}

# Per copy of 12⊕12̄ = 24:
# (3, 3)_{1/3} = 9 quarks
# (1, 3)_{-1} = 3 leptons
# (3̄, 3̄)_{-1/3} = 9 antiquarks
# (1, 3̄)_{1} = 3 antileptons
# Total = 24

# 3 copies = 72. Which 48 are SM?
# Probably: 1 copy of (4, 3) from each generation structure + more
# Actually, the SU(3)_gen has 3 generations, so the 3 in 12 = (4, 3)
# carries the generation index. The 3 copies of 12⊕12̄ correspond to
# the 3 rows of the 3-dimensional generation space.

# In other words: 12 = (4, 3) means 4 SU(4) states × 3 generation states
# = 12 states. And 3×(12⊕12̄) = 3 copies of both 12 and 12̄.

# 12 = (4, 3) = {state_α,i} where α=1..4 (SU(4)), i=1..3 (generation)
# 3 copies of 12 = 3 × 12 = 36
# 3 copies of 12̄ = 3 × 12̄ = 36
# Total = 72

# So the 36 = 3×12 states are:
# {state_α,i}^{(k)} where α=1..4, i=1..3, k=1..3 (copy index)
# Total: 4×3×3 = 36

# The SM fermions (48) are a subset of the 72, and the remaining 24 are VL.

# Now, 66 = Λ²(12) is a DIFFERENT representation entirely.
# Λ²(12) = antisymmetric product of two 12 fundamentals.
# This means: Λ²(12) = {state_a ∧ state_b | a,b=1..12}
# = 66 states.

# The 66 states are NOT contained in 3×(12⊕12̄) = 72.
# They are a separate representation.

# So what are they physically?
# If 12 = left-handed fermions (under SU(12) global symmetry),
# then Λ²(12) could represent:
# - Diquark-like composites (two-fermion bound states)
# - Gauge bosons of SO(12) ⊂ SU(12)
# - Scalar partners

# Actually, from the GUT perspective:
# In SU(12) GUT, the 66 = Λ²(12) is a Higgs representation
# that can break SU(12) → SO(12).
# The 66 VEV gives mass to the broken generators.

# But in IDCM, the 66 = 2×K_tree has a specific structural meaning:
# 66 = 2×33 = twice the tree structure depth.

# In the fermion context:
# 66 = 2×K_tree = 2×33
# 48 = SM fermions (from 3×(12⊕12̄))
# 66 - 48 = 18

# Or: 72 = 3×(12⊕12̄) = total fermion content
# 66 = Λ²(12) = different rep
# 72 + 66 = 138 total fermions in the theory?

# Or maybe 66 is NOT additional fermions, but rather the MASS MATRIX
# of the fermions? The Yukawa matrix lives in 12⊗12̄ = 1⊕143,
# and the antisymmetric part 66 is projected out.

# Let me check: 12 ⊗ 12̄ = 1 ⊕ 143
# 12 ⊗ 12 = 66 ⊕ 78
# The fermion bilinear ψ̄ψ transforms as 12 ⊗ 12̄ = 1 ⊕ 143
# The fermion mass matrix is in the adjoint of SU(12) (143).
# 66 = Λ²(12) = ψψ bilinear (not ψ̄ψ).

# So 66 corresponds to MAJORANA mass terms ψψ, not Dirac mass terms ψ̄ψ!

# This is the key insight: 66 = Λ²(12) carries the antisymmetric
# fermion-fermion bilinear, which could be:
# 1. Majorana mass terms for right-handed neutrinos
# 2. Diquark condensates
# 3. Lepton-number-violating processes

# In the SM, only the right-handed neutrino can have a Majorana mass
# (since it's SU(3)_c × SU(2)_L × U(1)_Y singlet).
# But in SU(12), the 66 could contain more Majorana mass terms.

# From the B-L charge analysis:
# 66 states have B-L = 2/3, -2/3, -2
# For a ψψ bilinear to have B-L, the constituent fermions must have
# appropriate charges.

# Actually, I think the most natural interpretation is:

# 66 = Λ²(12) = antisymmetric ψψ bilinear
# = 66 possible ψψ pairings
# = 2×K_tree = 2×33
# = The tree structure appears twice (left+right, or particle+antiparticle)

# The 66 states correspond to:
# 1. 48 = ψψ pairs that give SM fermion masses
# 2. 18 = extra pairings (possibly VL)

# But this still doesn't tell us the exact mapping.

# Let me approach this from a different angle:
# The 66 = 2×K_tree = 2×33
# 33 = K_tree = tree structure
# 66 = 2 copies of the tree

# In the 36 = h11 = K_tree + N_gen = 33+3 framework:
# 33 = K_tree modes (the "tree" of the W-field)
# 3 = N_gen generation indices

# 66 = 2×33 = 2×K_tree
# = 33 + 33
# = left-handed tree + right-handed tree?

# If we double the 33 tree modes (without the 3 generation indices),
# we get 66 = 2×33.

# The 66 = Λ²(12) under SU(4)×SU(3) gives:
# 66 = (6, 6) ⊕ (10, 3̄) = 36 + 30
# 36 = (6, 6) = h11 = K_tree + N_gen = 33 + 3
# 30 = (10, 3̄) = Nd - 2L₄ = 44 - 14

# So 36 = h11 = the 36-dimensional representation that matches
# the CY₃ Kähler moduli space. And 30 = extra structure.

# Under SM decomposition:
# 36 = (6, 6) = (3̄_{2/3} ⊕ 3_{-2/3}) ⊗ 6_gen
# 30 = (10, 3̄) = (6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}) ⊗ 3̄_gen

# Now, let me check if these 66 states can be matched to the
# SM fermion content from 3×(12⊕12̄):

# 12 ⊕ 12̄ per generation:
# (3, 3)_{1/3} ⊕ (1, 3)_{-1} ⊕ (3̄, 3̄)_{-1/3} ⊕ (1, 3̄)_{1}

# These live in SU(3)_c representations: 3, 1, 3̄, 1
# With B-L charges: 1/3, -1, -1/3, 1

# The 66 states live in SU(3)_c representations: 3̄, 3, 6, 1
# With B-L charges: 2/3, -2/3, -2

# There's NO direct overlap! The 66 states have different quantum numbers
# from the SM fermions.

# CONCLUSION: 66 = Λ²(12) does NOT contain the SM fermions.
# The SM fermions live in 3×(12⊕12̄) = 72.
# 66 = Λ²(12) is a different representation with different physical states.

# What IS 66 then?
# 1. 66 = adj(SO(12)) = gauge bosons of SO(12) subalgebra
# 2. 66 = ψψ bilinear (Majorana mass sector)
# 3. 66 = the "mirror" or "conjugate" structure of the 33 tree

# Given 66 = 2×K_tree = 2×33, and the SM fermions = 48,
# the 66 likely represents the COMPLETE mass matrix structure
# of the theory, including both left and right chiralities.

# The 66 = 2×33 = 2×K_tree = the tree structure of both
# chiral sectors (L and R).

# Under SU(4)×SU(3):
# 66 = (6, 6) ⊕ (10, 3̄)
# 36 = (6, 6) = h11 = 33+3 = K_tree + N_gen
# 30 = (10, 3̄) = 30 = Nd - 2L₄

# 36 = h11 = K_tree + N_gen = SU(12) fundamental content
# 30 = Nd - 2L₄ = extra structure from icosahedron

print("\n\n" + "=" * 70)
print("FINAL ANALYSIS")
print("=" * 70)

print("""
66 = Λ²(12) does NOT contain SM fermions directly.
SM fermions are in 3×(12⊕12̄) = 72.

66 = Λ²(12) has different quantum numbers:
  - B-L charges: 2/3, -2/3, -2 (vs SM: 1/3, -1, -1/3, 1)
  - Color reps: 3, 3̄, 6, 1 (vs SM: 3, 3̄, 1)

66 = 2×K_tree = 2×33 represents:
  1. adj(SO(12)) = SO(12) gauge bosons (P7 from O96)
  2. The ψψ bilinear sector (Majorana masses, diquarks)
  3. The complete L+R tree structure of the W-field

The 66 = 36 + 30 decomposition:
  36 = (6, 6) = h11 = K_tree + N_gen = 33+3
  30 = (10, 3̄) = Nd - 2L₄ = 44 - 14
""")

# Save results
results = {
    "problem": "O109",
    "title": "66 = Λ²(12) fermion correspondence",
    "status": "🟡 PARTIALLY CLOSED",
    "total_66_decomposition": {
        "Λ²(12)": {"dim": 66, "under_SU4xSU3": [
            {"rep": "(6,6)", "dim": 36, "idcm": "h11 = K_tree+N_gen = 33+3"},
            {"rep": "(10,3̄)", "dim": 30, "idcm": "Nd−2L₄ = 44−14"}
        ]}
    },
    "under_SM": {
        "(6,6)_36": {
            "6_SU4→SU3×U1": "3̄_{2/3} ⊕ 3_{-2/3}",
            "6_gen": "Sym²(3) = symmetric generation pairs",
            "total": "3̄_{2/3}⊗6_gen ⊕ 3_{-2/3}⊗6_gen = 18+18 = 36"
        },
        "(10,3̄)_30": {
            "10_SU4→SU3×U1": "6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}",
            "3̄_gen": "Λ²(3) = antisymmetric generation pairs",
            "total": "6_{2/3}⊗3̄_gen ⊕ 3_{-2/3}⊗3̄_gen ⊕ 1_{-2}⊗3̄_gen = 18+9+3 = 30"
        }
    },
    "key_finding": "66 = Λ²(12) does NOT contain SM fermions directly. SM fermions are in 3×(12⊕12̄)=72. 66 has different B-L charges (2/3, -2/3, -2 vs SM's 1/3, -1, -1/3, 1) and color reps (3, 3̄, 6, 1 vs SM's 3, 3̄, 1).",
    "physical_interpretation": [
        "66 = adj(SO(12)) = SO(12) gauge bosons under SU(12)→SO(12) breaking",
        "66 = 2×K_tree = 2×33 = complete L+R tree structure of W-field",
        "66 = ψψ bilinear sector (Majorana masses, not Dirac ψ̄ψ)"
    ]
}

with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o109_lambda2_fermion/data/01_decomposition_66.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Results saved to data/01_decomposition_66.json")