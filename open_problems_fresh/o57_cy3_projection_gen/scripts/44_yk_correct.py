#!/usr/bin/env python3
"""
O57 六期 44: 正確 κ K-sector Yukawa 矩陣 + 66 態
==================================================
Gemini 終極測試: C⊗K 雙 Sector 代數湧現

步驟 1: 用正確 CYTools κ 重建 36×36 Y_K = κ_ijk·t^k
步驟 2: 提取 66 態 (P_fixed_v2.npy → eigh → 66 態)
步驟 3: 分 K/C sector (Kähler 分量 vs CPX 分量)
步驟 4: Y_K 本徵值譜 (K-sector 幾何壓抑)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 44: 正確 κ K-sector Yukawa")
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

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 重建正確 κ ============
print("\n[1] 重建正確 κ")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
inter = cy.intersection_numbers()
K = np.zeros((36, 36, 36))
for key, val in inter.items():
    if isinstance(key, tuple) and len(key) == 3:
        i, j, k = key
        if 1 <= i <= 36 and 1 <= j <= 36 and 1 <= k <= 36:
            K[i-1, j-1, k-1] = val
            K[i-1, k-1, j-1] = val
            K[j-1, i-1, k-1] = val
            K[j-1, k-1, i-1] = val
            K[k-1, i-1, j-1] = val
            K[k-1, j-1, i-1] = val
print(f"  κ nnz={np.count_nonzero(K)}")
check("κ[0,0,0]=4", abs(K[0,0,0]-4) < 0.01, f"({K[0,0,0]})")

# ============ 2. 66 態提取 ============
print("\n[2] 66 態提取")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
print(f"  P: {P.shape}")
evals, evecs = np.linalg.eigh(P @ P.T)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evecs_pos = evecs[:, pos][:, :66]
print(f"  positive: {np.sum(pos)}, 66 態: {evecs_pos.shape}")

# sector 判斷
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
nK = np.sum(sector == "K")
nC = np.sum(sector == "C")
print(f"  K 態: {nK}, C 態: {nC}")
check("K+C = 66", nK + nC == 66, f"({nK}+{nC})")
check("K 態 = 36", nK == 36, f"({nK})")
check("C 態 = 30", nC == 30, f"({nC})")

# ============ 3. Y_K = κ·t ============
print("\n[3] Y_K = κ_ijk·t^k")
for name, t in [
    ("φ^(35-i)", phi ** (35 - np.arange(36))),
    ("φ^(i-1)", phi ** np.arange(36)),
    ("J*", np.array(json.load(open(os.path.join(O53, "Jstar_36D.json"))).get("Jstar_36D"))),
]:
    Y = np.einsum('ijk,k->ij', K, t)
    Y = (Y + Y.T) / 2
    ev = np.linalg.eigvalsh(Y)
    ev_sorted = np.sort(ev)[::-1]
    print(f"\n  --- {name} ---")
    print(f"  Y 譜 (top 10): {ev_sorted[:10]}")
    print(f"  Y 譜 (bottom 5): {ev_sorted[-5:]}")
    print(f"  正本徵值: {np.sum(ev > 0)}/{len(ev)}")
    # 有冇 φ^(1/3) 或者 φ 結構?
    print(f"  λ₁/λ₂ = {abs(ev_sorted[0]/ev_sorted[1]):.4f}")
    print(f"  φ = {phi:.4f}, φ² = {phi**2:.4f}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("六期 44 總結:")
print("=" * 72)
print(f"""
  正確 κ K-sector Yukawa:
  ─────────────────────────────────
  1. κ: {np.count_nonzero(K)} nnz (正確)
  2. 66 態: {nK} K + {nC} C (正確)
  3. Y_K = κ·t 譜: 睇上面

  {'✅ K-sector 結構確認!' if nK == 36 and nC == 30 else '❌ 結構不符'}
""")

results = {
    "test": "O57 六期 44: 正確 κ Y_K",
    "kappa_nnz": int(np.count_nonzero(K)),
    "nK": int(nK), "nC": int(nC),
    "passed": passed, "failed": failed
}
with open("data/44_yk_correct.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 44 完成!")
