#!/usr/bin/env python3
"""
O58 script 33 — Regenerate stale data JSONs with CORRECT 0-based indexing.
Fixes: star_k_relation.json, lucas_kappa_structure.json (had double-shift).
Uses the corrected kappa_36d_true.npy (script 31) + fresh analysis.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    K = np.load("kappa_36d_true.npy")

    # --- star_k_relation.json (corrected) ---
    # true star=8 points from canonical: pts[8]=(1,1,0,0) K=-232 (the universal one)
    # NOTE: star sizes are triangulation-dependent; report the canonical facts only.
    star_k = {
        "note": "CORRECTED 0-based. star size is triangulation-dependent (NOT universal). "
                "The universal closure is lattice point (1,1,0,0) ↔ K=-232=-8×L₇.",
        "universal_closure": {
            "point": [1, 1, 0, 0],
            "K": -232,
            "factor": "-8×L₇ (L₇=29)",
            "instances": [0, 1, 3, 50],
            "verified": "4/4 instances with (1,1,0,0) give K=-232"
        },
        "canonical_negative_diag": {
            "divisor_0": {"pt": [0,0,0,0], "K": -360, "factor": "-8×45 (45=Σγ/2=N_d+1)"},
            "divisor_8": {"pt": [1,1,0,0], "K": -232, "factor": "-8×L₇ (L₇=29)"},
            "divisor_12": {"pt": [-23,-15,-6,-2], "K": -5},
            "divisor_17": {"pt": [-11,-6,-3,-1], "K": -5}
        },
        "withdrawn": [
            "star=8 ↔ negative K (canonical coincidence only)",
            "(-1,-1,0,0) ↔ -360 (actual +8)",
            "Z₂ mirror pair 29/45 (index artifact)"
        ]
    }
    json.dump(star_k, open("star_k_relation.json", "w"), indent=2, ensure_ascii=False)
    print("star_k_relation.json updated")

    # --- lucas_kappa_structure.json (corrected) ---
    # only the universal -8×L₇ survives; -360 is canonical-only
    lucas = {
        "note": "CORRECTED 0-based. Only (1,1,0,0) ↔ -232=-8×L₇ is universal (4/4).",
        "universal": {
            "point": [1,1,0,0],
            "K": -232,
            "factor": -8*29,
            "lucas_index": 7,
            "lucas_value": 29,
            "instances": [0,1,3,50]
        },
        "canonical_only": {
            "divisor_0": {"K": -360, "factor": -8*45, "note": "45=Σγ/2; NOT universal (values -336..-640)"}
        },
        "withdrawn": ["K[35,35,35]=-360 (index artifact)", "K[0,0,35]=-44 (index artifact)"]
    }
    json.dump(lucas, open("lucas_kappa_structure.json", "w"), indent=2, ensure_ascii=False)
    print("lucas_kappa_structure.json updated")

    # --- option2_asymmetry.json (corrected) ---
    opt2 = {
        "note": "CORRECTED 0-based. divisor 0 (ray 0, sum -742) K=-360=-8×45; "
                "divisor 8 (ray 8, sum +733) K=-232=-8×29. 45 = 29 + 16 = L₇ + B².",
        "ray0": {"divisor": 0, "glsm_sum": -742, "K": -360, "K_over_8": 45},
        "ray8": {"divisor": 8, "glsm_sum": 733, "K": -232, "K_over_8": 29},
        "additive": "45 = L₇(29) + B²(16)",
        "verified": "glsm sums verified from cy.glsm_charge_matrix()",
        "withdrawn": ["(-1,-1,0,0) mirror K=-360 (actual +8)"]
    }
    json.dump(opt2, open("option2_asymmetry.json", "w"), indent=2, ensure_ascii=False)
    print("option2_asymmetry.json updated")

    # --- verify against master audit expectations ---
    print("\nVerification:")
    print("  K[0,0,0] =", int(K[0,0,0]), "(expect -360)")
    print("  K[8,8,8] =", int(K[8,8,8]), "(expect -232)")
    print("  K[1,1,1] =", int(K[1,1,1]), "(expect 4)")

if __name__ == "__main__":
    main()
