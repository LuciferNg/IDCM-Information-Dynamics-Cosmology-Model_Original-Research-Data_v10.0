#!/usr/bin/env python3
"""
O62 九期 55: 最終 Audit — 四項目成果獨立重算
=============================================
獨立重算 41-54 關鍵發現:
  1. SR pairs: sage 484 = 450 active + 25 anomaly
  2. Dual: M=48, N=85, mirror h11/h12 互換
  3. Chow: 8436 = 904 + 7532, 非 co-simplex 全零
  4. 48/85 專屬: canonical only
  5. M+N=133
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 55: 最終 Audit")
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

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
simplices = d["simplices"]
sr_sage = d["sr_ideal"]
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

# ============ 項目 4: SR pairs ============
print("[項目 4] SR pairs")
star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1
active = [i for i in range(48) if star.get(i, 0) > 0]
active_set = set(active)
faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge_active = set((i, j) for i, j in combinations(active, 2) if (i, j) not in faces_1d)
sr_set = set(tuple(sorted(p)) for p in sr_sage)
check("active no_edge = 450", len(no_edge_active) == 450, f"({len(no_edge_active)})")
check("sage ∩ active = 450", len(sr_set & no_edge_active) == 450, f"({len(sr_set & no_edge_active)})")
check("active − sage = 0", len(no_edge_active - sr_set) == 0, f"({len(no_edge_active - sr_set)})")
check("sage unique 475 = 450 + 25", len(sr_set) == 475, f"({len(sr_set)})")
check("484 raw = 475 unique + 9 dup", len(sr_sage) == 484 and len(sr_set) == 475, f"({len(sr_sage)}/{len(sr_set)})")

# ============ 項目 2: Dual ============
print("\n[項目 2] Dual")
import cytools
from cytools import Polytope, config
config.enable_experimental_features()
canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
P_dual = P.polar_polytope()
M = len(P.points())
N = len(P_dual.points())
check("M = 48", M == 48, f"({M})")
check("N = 85", N == 85, f"({N})")
check("h11 = 36", P.h11() == 36, f"({P.h11()})")
check("h12 = 98", P.h12() == 98, f"({P.h12()})")
check("mirror h11* = 98", P_dual.h11() == 98, f"({P_dual.h11()})")
check("mirror h12* = 36", P_dual.h12() == 36, f"({P_dual.h12()})")
check("reflexive", P_dual.is_reflexive(), "")

# ============ 項目 1: Chow ============
print("\n[項目 1] Chow 消去")
cosimp = set()
for s in simplices:
    lst = sorted(v for v in s if v < 36)
    for i in range(len(lst)):
        for j in range(i, len(lst)):
            for k in range(j, len(lst)):
                cosimp.add((lst[i], lst[j], lst[k]))
all_triples = set()
for i in range(36):
    for j in range(i, 36):
        for k in range(j, 36):
            all_triples.add((i, j, k))
check("904 co-simplex", len(cosimp) == 904, f"({len(cosimp)})")
check("7532 非 co-simplex", len(all_triples) - len(cosimp) == 7532, f"({len(all_triples) - len(cosimp)})")
viol = sum(1 for t in all_triples - cosimp if kappa36[t] != 0)
check("非 co-simplex 全零", viol == 0, f"({viol})")
cosimp_zero = sum(1 for t in cosimp if kappa36[t] == 0)
cosimp_nnz = sum(1 for t in cosimp if kappa36[t] != 0)
check("554 + 350", cosimp_zero == 554 and cosimp_nnz == 350, f"({cosimp_zero}/{cosimp_nnz})")

# ============ 項目 3: 48/85 ============
print("\n[項目 3] 48/85 專屬")
with open(os.path.join(O53, "all_36_98.poly")) as f:
    lines = [l.strip() for l in f if l.strip()]
polytopes = []
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2:
        n_v = int(parts[0])
        verts = []
        for j in range(n_v):
            i += 1
            verts.append([int(x) for x in lines[i].split()])
        polytopes.append(verts)
    i += 1
n_48_85 = 0
n_6v = 0
for verts in polytopes:
    try:
        Pp = Polytope(verts)
        Mp, Np = len(Pp.points()), len(Pp.polar_polytope().points())
        if Mp == 48 and Np == 85:
            n_48_85 += 1
        if len(verts) == 6:
            n_6v += 1
    except Exception:
        pass
check("48/85 只 1 個", n_48_85 == 1, f"({n_48_85})")
check("6 頂點 2 個", n_6v == 2, f"({n_6v})")
check("48+85 = 133", M + N == 133, f"({M}+{N}={M+N})")

# ============ 總結 ============
print("\n" + "=" * 72)
print(f"九期 55 最終 Audit: Passed {passed}, Failed {failed}")
print("=" * 72)
out = {
    "test": "O62 九期 55: 最終 Audit",
    "t4": {"active_no_edge": len(no_edge_active), "sage_inter": len(sr_set & no_edge_active)},
    "t2": {"M": M, "N": N, "h11": int(P.h11()), "h12": int(P.h12()), "h11_dual": int(P_dual.h11()), "h12_dual": int(P_dual.h12())},
    "t1": {"cosimp": len(cosimp), "zero": cosimp_zero, "nnz": cosimp_nnz, "viol": viol},
    "t3": {"n_48_85": n_48_85, "n_6v": n_6v},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "55_final_audit.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 55 完成 — 四項目全部驗證一致!")
