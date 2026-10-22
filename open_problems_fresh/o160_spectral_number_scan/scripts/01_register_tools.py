#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/01 — R1: 工具註冊探測 (Tool Registry Probe)

4 套譜幾何工具 smoke test:
  csg  = CSG SpectralSpace (K_Chain 版)
  ktsg = KTreeSpectralGeometry (K_Tree 版雙矩陣)
  v2   = CSG-v2 v2core (T̂ 代數)
  fsr  = O140 FSR (有限譜相對論)

每 tool 一個 PASS/FAIL, 最後 RESULT: N/N PASS。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.registry import TOOLS, probe_all, probe, get_spectra, invariants

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


print("=" * 72)
print("O160 R1 — 工具註冊探測")
print("=" * 72)
for key in TOOLS:
    print(f"\n--- {key}: {TOOLS[key]['name']} ---")
    check(f"probe:{key}", probe(key, verbose=False),
          f"({TOOLS[key]['path']})")

print("\n--- 統一本徵值 (get_spectra) ---")
import numpy as np
S = get_spectra()
check("spectra:88", len(S["gamma"]) == 88 and len(S["omega"]) == 88)
check("spectra:33", len(S["lam"]) == 33)
check("spectra:Σγ=178", abs(S["gamma"].sum() - 178.0) < 1e-9,
      f"({S['gamma'].sum():.6f})")
check("spectra:Σγ_even=90", abs(S["gamma"][1::2].sum() - 90.0) < 1e-9,
      f"({S['gamma'][1::2].sum():.6f})")
check("spectra:Σγ_odd=88", abs(S["gamma"][0::2].sum() - 88.0) < 1e-9,
      f"({S['gamma'][0::2].sum():.6f})")
check("spectra:Σλ=66", abs(S["lam"].sum() - 66.0) < 1e-9,
      f"({S['lam'].sum():.6f})")
check("spectra:FSR恆等 γ_fsr=2/ω",
      np.allclose(S["gamma_fsr"], 2.0 / S["omega"], rtol=1e-12))
check("spectra:γ44 Σ=90", abs(S["gamma44"].sum() - 90.0) < 1e-9)
check("spectra:E−O=2", abs(S["gamma"][1::2].sum() - S["gamma"][0::2].sum() - 2.0) < 1e-9)

print("\n--- 單格不變量 (mpmath, 21,24,33) ---")
inv = invariants(21, 24, 33)
check("inv:13 families", len(inv) == 13, f"({len(inv)})")
check("inv:O88(21,24)=0.8813647", abs(inv["O88"] - 0.8813647) < 1e-6,
      f"= {inv['O88']} (O158 (21,24)@176 張力解)")
check("inv:R88=O88²", abs(inv["R88"] - inv["O88"] ** 2) < 1e-15,
      f"γ 比 = ω 比² (三角恆等)")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
sys.exit(0 if FAIL == 0 else 1)
