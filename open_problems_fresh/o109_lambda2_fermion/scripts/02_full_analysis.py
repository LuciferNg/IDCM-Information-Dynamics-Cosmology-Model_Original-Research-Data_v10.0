#!/usr/bin/env python3
"""
O109 — 66 = Λ²(12) fermion 對應: 完整結構分析
===========================================
Phase 1-4: Decompose 66, map to SM, analyze 2×K_tree, build mapping table.
"""

import json
import numpy as np

# ============================================================
# 1. Define the full decomposition chain
# ============================================================

# SU(12) → SU(4)_PS × SU(3)_gen (tensor embedding: 12 = 4 ⊗ 3)
# 66 = Λ²(12) = (Λ²(4), Sym²(3)) ⊕ (Sym²(4), Λ²(3))
#            = (6, 6) ⊕ (10, 3̄)
# dim: 6×6 + 10×3 = 36 + 30 = 66 ✓

# SU(4)_PS → SU(3)_c × U(1)_{B-L}
# 4 = 3_{1/3} ⊕ 1_{-1}
# 6 = Λ²(4) = 3̄_{2/3} ⊕ 3_{-2/3}
# 10 = Sym²(4) = 6_{2/3} ⊕ 3_{-2/3} ⊕ 1_{-2}

# SU(3)_gen → generation flavor
# 3 = fundamental (generation index)
# 6 = Sym²(3) = symmetric pairs: {11, 22, 33, 12, 13, 23}
# 3̄ = Λ²(3) = antisymmetric pairs: {[12], [13], [23]}

# ============================================================
# 2. Full SM decomposition of 66
# ============================================================

decomp = {
    "Λ²(12)": {
        "total": 66,
        "SU4xSU3": [
            {
                "rep": "(6, 6)",
                "dim": 36,
                "idcm_id": "h11 = K_tree + N_gen = 33+3",
                "SU3c_x_U1BL": {
                    "3̄_{2/3} ⊗ 6_gen": {"SU3c": "3̄", "U1_BL": "2/3", "gen_reps": "6", "dim": 18},
                    "3_{-2/3} ⊗ 6_gen": {"SU3c": "3", "U1_BL": "-2/3", "gen_reps": "6", "dim": 18},
                }
            },
            {
                "rep": "(10, 3̄)",
                "dim": 30,
                "idcm_id": "Nd−2L₄ = 44−14",
                "SU3c_x_U1BL": {
                    "6_{2/3} ⊗ 3̄_gen": {"SU3c": "6", "U1_BL": "2/3", "gen_reps": "3̄", "dim": 18},
                    "3_{-2/3} ⊗ 3̄_gen": {"SU3c": "3", "U1_BL": "-2/3", "gen_reps": "3̄", "dim": 9},
                    "1_{-2} ⊗ 3̄_gen": {"SU3c": "1", "U1_BL": "-2", "gen_reps": "3̄", "dim": 3},
                }
            }
        ]
    }
}

# ============================================================
# 3. SM fermion content (from 3×(12⊕12̄) = 72)
# ============================================================
# 12 = (4, 3) = (3, 3)_{1/3} ⊕ (1, 3)_{-1}
# 12̄ = (4̄, 3̄) = (3̄, 3̄)_{-1/3} ⊕ (1, 3̄)_{1}
# 3×(12⊕12̄) = 72 total

sm_fermions = {
    "per_generation": {
        "Q_L": {"rep": "(3,2)_{1/6}", "SU3c": "3", "SU2L": "2", "U1_Y": "1/6", "count": 6, "type": "left-handed quark doublet"},
        "u_R": {"rep": "(3,1)_{2/3}", "SU3c": "3", "SU2L": "1", "U1_Y": "2/3", "count": 3, "type": "right-handed up-quark"},
        "d_R": {"rep": "(3,1)_{-1/3}", "SU3c": "3", "SU2L": "1", "U1_Y": "-1/3", "count": 3, "type": "right-handed down-quark"},
        "L_L": {"rep": "(1,2)_{-1/2}", "SU3c": "1", "SU2L": "2", "U1_Y": "-1/2", "count": 2, "type": "left-handed lepton doublet"},
        "e_R": {"rep": "(1,1)_{-1}", "SU3c": "1", "SU2L": "1", "U1_Y": "-1", "count": 1, "type": "right-handed charged lepton"},
        "ν_R": {"rep": "(1,1)_0", "SU3c": "1", "SU2L": "1", "U1_Y": "0", "count": 1, "type": "right-handed neutrino"},
    },
    "total_per_gen": 16,
    "total_3_gen": 48,
    "from_3x12plus12bar": 72,
    "VL_extra": 24
}

# ============================================================
# 4. B-L charge comparison: 66 vs SM
# ============================================================

# SM fermion B-L charges (from 12 and 12̄):
# In Pati-Salam: 4 = 3_{1/3} ⊕ 1_{-1} under SU(3)_c × U(1)_{B-L}
# 12 = (4, 3): quarks B-L = 1/3, leptons B-L = -1
# 12̄ = (4̄, 3̄): antiquarks B-L = -1/3, antileptons B-L = 1

# 66 = Λ²(12) B-L charges:
# From 6 = Λ²(4): 3̄_{2/3} and 3_{-2/3}
# From 10 = Sym²(4): 6_{2/3}, 3_{-2/3}, 1_{-2}

bl_comparison = {
    "SM_from_12": {"quarks": "1/3", "leptons": "-1"},
    "SM_from_12bar": {"antiquarks": "-1/3", "antileptons": "1"},
    "66_from_Lambda2_12": {
        "3̄_{2/3}": "2/3",
        "3_{-2/3}": "-2/3",
        "6_{2/3}": "2/3",
        "1_{-2}": "-2"
    },
    "verdict": "66 = Λ²(12) has DIFFERENT B-L charges from SM fermions in 12/12̄. NO direct overlap."
}

# ============================================================
# 5. Physical interpretations of 66 = 2×K_tree
# ============================================================

interpretations = [
    {
        "name": "SO(12) gauge bosons (P7 from O96)",
        "description": "Under SU(12)→SO(12), adj(SU(12)) = 143 → 66⊕77. 66 = adj(SO(12)) = SO(12) gauge bosons.",
        "evidence": [
            "66 = dim(SO(12)) = adj(SO(12))",
            "66 = Λ²(12) = antisymmetric product = Lie algebra of SO(12)",
            "77 = coset = SU(12)/SO(12) = broken generators/Higgs",
            "O96 P7: 11/11 PASS for 66+77 decomposition"
        ],
        "status": "🟢 STRONG — well-established group theory"
    },
    {
        "name": "2×K_tree = complete L+R structure",
        "description": "66 = 2×33 = 2×K_tree represents the complete tree structure of the W-field, appearing twice (left + right chirality, or particle + antiparticle).",
        "evidence": [
            "36 = h11 = K_tree + N_gen = 33+3 = one chiral sector (3 generations)",
            "66 = 2×K_tree = 2×33 = both chiral sectors WITHOUT generation indices",
            "66 = 36 + 30 mirrors the 36 (L) + 36 (R) = 72 total fermion space, minus 6 N_gen-related terms",
            "72 - 6 = 66 = complete fermion mass spectrum structure"
        ],
        "status": "🟡 GOOD — structurally consistent with IDCM framework"
    },
    {
        "name": "ψψ bilinear (Majorana sector)",
        "description": "66 = Λ²(12) = antisymmetric ψψ product. Carries Majorana mass terms, NOT Dirac ψ̄ψ mass terms (which live in 12⊗12̄ = 1⊕143).",
        "evidence": [
            "12 ⊗ 12 = 66 ⊕ 78: 66 = antisymmetric, 78 = symmetric",
            "ψψ bilinear (fermion-fermion) vs ψ̄ψ (fermion-antifermion)",
            "Majorana masses for ν_R live in this sector",
            "B-L = -2 component (1_{-2}⊗3̄_gen) corresponds to ΔL=2 processes"
        ],
        "status": "🟡 GOOD — explains the different B-L charges"
    },
    {
        "name": "U(1)₆ extra gauge bosons",
        "description": "66 = 2×K_tree carries 6 extra U(1) gauge bosons from the rank difference (11 vs 5: SU(12) vs SM).",
        "evidence": [
            "SU(12) rank = 11, SM rank = 4+1 = 5",
            "6 extra U(1) factors: 11-5 = 6",
            "O96 §III, O90: 6 extra U(1) connected to V_Λ=283.0821",
            "66 = 6×11 = 6×L₅ = 6×rank(SU(12))"
        ],
        "status": "🟡 SPECULATIVE — needs more evidence"
    }
]

# ============================================================
# 6. Compute 66 in terms of IDCM numbers
# ============================================================

idcm_numbers = {
    "66": {
        "Λ²(12)": "C(12,2) = 66",
        "2×K_tree": "2×33 = 66",
        "adj(SO(12))": "dim(SO(12)) = 66",
        "|Φ⁺(SU(12))|": "positive roots of SU(12) = 66",
        "72 - 6": "total fermions (72) - 2×N_gen (6) = 66",
        "h11 + (Nd-2L₄)": "36 + 30 = 66",
        "B×K_tree + Nd - 2B": "4×33 + 44 - 8 = 132 + 36 = 168... NO",
        "B×K_tree - L₄": "4×33 - 7 = 132 - 7 = 125... NO",
        "K_tree + L₆ + Nd": "33 + 18 + 44 = 95... NO",
        "CORRECT: 66 = 2×K_tree": "2×33 = 66 ✓",
    },
    "36 = (6,6)": {
        "h11": "K_tree + N_gen = 33 + 3 = 36 ✓",
        "3×12": "3 generations of SU(12) fundamental = 36 ✓",
        "Λ²(4)×Sym²(3)": "6×6 = 36 ✓",
    },
    "30 = (10,3̄)": {
        "Nd - 2L₄": "44 - 14 = 30 ✓",
        "Sym²(4)×Λ²(3)": "10×3 = 30 ✓",
        "icosahedron_edges": "30 = icosahedron edge count",
    }
}

# ============================================================
# 7. Mapping table: 66 states vs SM fermion content
# ============================================================

# For each SU(3)_c × U(1)_{B-L} component of 66, compare with SM fermions

mapping_table = []

# (6, 6) components:
# 3̄_{2/3} ⊗ 6_gen: 18 states with B-L=2/3, color 3̄
# 3_{-2/3} ⊗ 6_gen: 18 states with B-L=-2/3, color 3

# SM fermions with similar color but different B-L:
# From 12: Q_L has B-L=1/3, u_R/d_R have B-L=1/3 (or -1/3 in some conventions)
# From 12̄: antiquarks have B-L=-1/3

# B-L convention check:
# In Pati-Salam: 4 = (3, 1)_{1/3} ⊕ (1, 1)_{-1}
# Quarks: B-L = 1/3, Leptons: B-L = -1
# In 12 = (4, 3): 3 quarks × 3 gen = 9 with B-L=1/3, 3 leptons with B-L=-1

# In Λ²(4): the antisymmetric product of two quarks gives B-L = 1/3+1/3 = 2/3
# In 6_{2/3} of Sym²(4): symmetric product of two quarks also gives B-L = 2/3
# In 3_{-2/3}: quark + lepton gives B-L = 1/3 + (-1) = -2/3
# In 1_{-2}: lepton + lepton gives B-L = (-1) + (-1) = -2

# This is consistent: the 66 = Λ²(12) represents two-fermion composites
# with B-L charges that are the SUM of two fundamental fermion charges.

# Generation structure:
# 6_gen = Sym²(3) = 6 symmetric pairs: 11, 22, 33, 12, 13, 23
# 3̄_gen = Λ²(3) = 3 antisymmetric pairs: [12], [13], [23]

# So the 66 carries NOT just one generation index (like 12), but TWO
# generation indices (symmetric or antisymmetric).

# This is the key: 66 = Λ²(12) = two-fermion states, each with its own generation index!
# Total: 12×11/2 = 66 states, each with two generation indices.

# Generation pairs in 66:
# 6_gen = 6 symmetric pairs: (11), (22), (33), (12), (13), (23)
# 3̄_gen = 3 antisymmetric pairs: [12], [13], [23]

# 48 SM fermions from 3×(12⊕12̄):
# Each SM fermion has ONE generation index (i=1,2,3)
# 66 states have TWO generation indices (i,j) with i≤j or i<j

# SO: the 66 states are NOT the SM fermions themselves,
# but rather the PAIRING STRUCTURE between fermions.
# They represent the possible fermion pairs in the theory.

# This naturally explains 66 = 2×K_tree:
# K_tree = 33 = tree structure = one generation structure
# 2×K_tree = 66 = TWO generation structures (pairing)

mapping = {
    "conclusion": "66 = Λ²(12) does NOT contain the 48 SM Weyl fermions directly. The SM fermions live in 3×(12⊕12̄)=72. The 66 is a DIFFERENT representation with different quantum numbers.",
    "what_66_represents": [
        "66 = adj(SO(12)) = SO(12) gauge bosons under SU(12)→SO(12) breaking",
        "66 = 2×K_tree = 2×33 = complete two-sector tree structure of the W-field",
        "66 = ψψ antisymmetric bilinear = Majorana/diquark sector (not Dirac ψ̄ψ)",
        "66 = the fermion PAIRING structure (two generation indices, not one)"
    ],
    "66_vs_48_SM": {
        "66": "Λ²(12) = antisymmetric product of two fundamentals",
        "48": "SM Weyl fermions from 3×(12⊕12̄) = 72",
        "66_contains_SM_fermions": False,
        "reason": "Different B-L charges (2/3, -2/3, -2 vs 1/3, -1, -1/3, 1). Different color reps (3, 3̄, 6, 1 vs 3, 3̄, 1).",
        "66_overlaps_with_72": "The 66 and 72 are different representations of SU(12); they intersect only at the identity.",
        "66_minus_48": "18 ≠ meaningful difference; they're different rep spaces."
    },
    "66_2xK_tree_meaning": {
        "K_tree": 33,
        "2xK_tree": 66,
        "interpretation": "66 = 2×33 = two copies of the W-field tree structure. Each copy represents one sector (e.g., left/right chirality, or particle/antiparticle, or generation pairing).",
        "comparison_with_36": "36 = h11 = K_tree + N_gen = 33+3 = one chiral sector with 3 generations. 66 = 2×K_tree = 2×33 = both sectors without explicit generation indices."
    },
    "status": "🟡 PARTIALLY CLOSED — 66 is NOT the SM fermion representation. It represents the SO(12) gauge boson sector / two-fermion pairing structure / mass matrix sector."
}

# ============================================================
# 8. Save all results
# ============================================================

results = {
    "problem": "O109",
    "title": "66 = Λ²(12) fermion correspondence",
    "status": "🟡 PARTIALLY CLOSED",
    "decomposition": decomp,
    "sm_fermions": sm_fermions,
    "bl_comparison": bl_comparison,
    "interpretations": interpretations,
    "idcm_numbers": idcm_numbers,
    "mapping": mapping,
    "questions_answered": [
        {
            "q": "1. 66 個態點樣對應到 SM fermions？",
            "a": "66 = Λ²(12) 的 66 個態並未直接對應到 SM fermions。SM fermions 在 3×(12⊕12̄) = 72 中。66 有不同嘅 B-L 電荷 (2/3, -2/3, -2 vs SM 嘅 1/3, -1, -1/3, 1) 同色表示 (3, 3̄, 6, 1 vs SM 嘅 3, 3̄, 1)。66 代表 SO(12) 規範玻色子或雙費米子配對結構。",
            "status": "🟡 PARTIAL"
        },
        {
            "q": "2. 66 = 2×K_tree = 2×33 嘅物理意義？",
            "a": "66 = 2×33 = 兩份 K_tree 結構。一份對應一個手性 sector (左或右)，或者對應費米子-費米子配對嘅兩個世代指標。相比 36 = h11 = K_tree + N_gen = 33+3 係一個手性 sector 加三代，66 = 2×K_tree = 2×33 係兩個 sector 唔帶世代指標。",
            "status": "🟡 PARTIAL"
        },
        {
            "q": "3. 66 同 48 SM fermions 嘅關係？",
            "a": "66 同 48 係唔同嘅 SU(12) 表示 — 66 = Λ²(12) 而 SM fermions ⊂ 3×(12⊕12̄)。66-48=18 冇直接物理意義因為兩者屬於唔同表示空間。66 嘅 B-L 電荷係 2/3, -2/3, -2，而 SM fermions 嘅係 1/3, -1, -1/3, 1。",
            "status": "🟢 CLEAR"
        },
        {
            "q": "4. 66 中邊啲態對應到 observed particles？",
            "a": "66 中嘅態如果係 SO(12) 規範玻色子，則預言喺高能標度 (~M_GUT) 出現。如果係雙費米子配對，則對應到 Majorana 中微子質量項 (1_{-2}⊗3̄_gen, ΔL=2) 或 diquark 態。冇 66 嘅態喺低能可直接觀測。",
            "status": "🟢 CLEAR"
        }
    ]
}

# Save
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o109_lambda2_fermion/data/01_decomposition_66.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✅ Phase 1-4 complete: results saved to data/01_decomposition_66.json")
print(f"\nKey findings:")
print(f"  - 66 = Λ²(12) does NOT contain SM fermions directly")
print(f"  - SM fermions are in 3×(12⊕12̄) = 72")
print(f"  - 66 = 2×K_tree = 2×33 = two-sector tree structure")
print(f"  - 66 = adj(SO(12)) = SO(12) gauge bosons")
print(f"  - 66 = ψψ bilinear (Majorana sector, not Dirac)")
print(f"\n  B-L charge comparison:")
print(f"    SM from 12:  quarks=1/3, leptons=-1")
print(f"    SM from 12̄: antiquarks=-1/3, antileptons=1")
print(f"    66 from Λ²(12): 2/3, -2/3, -2")
print(f"    → DIFFERENT! No direct overlap.")
print(f"\n  Generation structure:")
print(f"    12 carries ONE generation index (i=1,2,3)")
print(f"    66 = Λ²(12) carries TWO generation indices (i,j)")
print(f"    6_gen = Sym²(3) = {6} symmetric pairs")
print(f"    3̄_gen = Λ²(3) = {3} antisymmetric pairs")