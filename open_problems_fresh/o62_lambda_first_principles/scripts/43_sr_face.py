#!/usr/bin/env python3
"""
O62 九期 43: SR pairs 最終 — face-based 定義
=============================================
上次: sage 484 = 450 active-no-simplex + 25 anomaly
25 anomaly 有共同 4-simplex

hypothesis: SR pair = 冇共同 2-face (3點 face, edge 唔喺任何 2D face)
  或者冇共同 3-face (4點)

檢查 25 anomaly: 佢哋有共同 4-simplex, 但係咪冇共同 2-face?
  (1,3): 例 simplex [0,1,3,7,8] — (1,3) 喺呢個 simplex
  但係咪有 2-face 同時含 1 同 3? 即存在 k 令 {1,3,k} 係 face
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 43: SR face-based")
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
sr_set = set(tuple(sorted(p)) for p in sr_sage)

# 全部 faces (1D, 2D, 3D, 4D faces from all simplices)
faces_1d = set()  # edges (2 points)
faces_2d = set()  # triangles (3 points)
faces_3d = set()  # tetrahedra (4 points)
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
    for t in combinations(s, 3):
        faces_2d.add(tuple(sorted(t)))
    for q in combinations(s, 4):
        faces_3d.add(tuple(sorted(q)))
print(f"[1] faces: 1D={len(faces_1d)}, 2D={len(faces_2d)}, 3D={len(faces_3d)}")

# SR 定義 (正確): pair (i,j) 係 SR 如果 {i,j} 唔係任何 face
# 所有 1-face 都係「有共同 edge」→ 唔 SR
# 冇共同 edge → SR!
sr_1d = []
for i in range(48):
    for j in range(i+1, 48):
        if (i, j) not in faces_1d:
            sr_1d.append((i, j))
sr_1d_set = set(sr_1d)
print(f"\n[2] 冇共同 edge (1D face) pairs: {len(sr_1d)}")
print(f"  sage ∩ 1D: {len(sr_set & sr_1d_set)}")
print(f"  sage − 1D: {len(sr_set - sr_1d_set)}")
print(f"  1D − sage: {len(sr_1d_set - sr_set)}")

# 檢查 25 anomaly 係咪冇共同 edge
anomaly = sorted(sr_set - sr_1d_set)
print(f"\n[3] anomaly vs 1D: {len(anomaly)}")
for (i, j) in anomaly[:10]:
    has_edge = (i, j) in faces_1d
    print(f"  ({i},{j}): 有共同 edge? {has_edge}")

# ============ 1. 用 cytools 正確計 ============
print("\n[4] cytools 計 faces")
import cytools
from cytools import Polytope, config
config.enable_experimental_features()
canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
tri = P.triangulate(backend="qhull")
simps = tri.simplices()
# cytools simplices 同 sage 差 4 個 — 用 cytools 嘅
cyt_faces_1d = set()
for s in simps:
    for e in combinations(s, 2):
        cyt_faces_1d.add(tuple(sorted(e)))
print(f"  cytools 1D faces: {len(cyt_faces_1d)}")
cyt_sr = []
for i in range(48):
    for j in range(i+1, 48):
        if (i, j) not in cyt_faces_1d:
            cyt_sr.append((i, j))
cyt_sr_set = set(cyt_sr)
print(f"  cytools 冇共同 edge pairs: {len(cyt_sr)}")
print(f"  sage ∩ cyt: {len(sr_set & cyt_sr_set)}")
print(f"  sage − cyt: {len(sr_set - cyt_sr_set)}")
print(f"  cyt − sage: {len(cyt_sr_set - sr_set)}")

# ============ 2. 總結 ============
print("\n" + "=" * 72)
print("九期 43 總結:")
print("=" * 72)
print(f"""
  1D face 定義: {len(sr_1d)} pairs
  sage 484 = ?
  cytools 1D: {len(cyt_sr)}

  目標: 搵出 sage 484 嘅精確定義
""")
out = {
    "test": "O62 九期 43: SR face",
    "n_faces": {"1d": len(faces_1d), "2d": len(faces_2d), "3d": len(faces_3d)},
    "sr_1d": len(sr_1d),
    "sage_vs_1d": {"inter": len(sr_set & sr_1d_set), "sage_only": len(sr_set - sr_1d_set), "1d_only": len(sr_1d_set - sr_set)},
    "cytools_sr": len(cyt_sr),
    "sage_vs_cyt": {"inter": len(sr_set & cyt_sr_set), "sage_only": len(sr_set - cyt_sr_set), "cyt_only": len(cyt_sr_set - sr_set)},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "43_sr_face.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 43 完成!")
