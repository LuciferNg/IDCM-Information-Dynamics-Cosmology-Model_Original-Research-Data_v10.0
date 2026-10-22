#!/usr/bin/env python3
"""
O62 十期 61: SR = 冇共同 2D face? 最終定義測試
===============================================
試 3 個候選定義:
  A. 冇共同 edge (1D): 912 pairs
  B. 冇共同 2D face (3點): ?
  C. 冇共同 3D cone (4點): 912 (計過)

睇邊個 match sage 475 unique
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 61: SR 定義測試")
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

# 全部 faces
faces_1d, faces_2d, faces_3d = set(), set(), set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
    for t in combinations(s, 3):
        faces_2d.add(tuple(sorted(t)))
    for q in combinations(s, 4):
        faces_3d.add(tuple(sorted(q)))
print(f"[1] faces: 1D={len(faces_1d)}, 2D={len(faces_2d)}, 3D={len(faces_3d)}")

# 定義 A/B/C (active 0-36)
def sr_by_face(faces, dim):
    sr = set()
    for i in range(37):
        for j in range(i+1, 37):
            # pair (i,j) 喺 face 如果 ∃ face 同時含 i,j
            has = any(i in f and j in f for f in faces)
            if not has:
                sr.add((i, j))
    return sr

sr_A = sr_by_face(faces_1d, 1)
sr_B = sr_by_face(faces_2d, 2)
sr_C = sr_by_face(faces_3d, 3)

print(f"\n[2] 定義測試 (active 0-36)")
print(f"  A (冇共同 edge): {len(sr_A)}")
print(f"  B (冇共同 2D): {len(sr_B)}")
print(f"  C (冇共同 3D): {len(sr_C)}")
print(f"  sage unique: {len(sr_set)}")

for name, s in [("A", sr_A), ("B", sr_B), ("C", sr_C)]:
    inter = len(sr_set & s)
    only = len(s - sr_set)
    miss = len(sr_set - s)
    print(f"  {name}: sage∩={inter}, {name}−sage={only}, sage−{name}={miss}")

# ============ 1. 最佳定義 ============
print("\n[3] 對照")
scores = {}
for name, s in [("A", sr_A), ("B", sr_B), ("C", sr_C)]:
    inter = len(sr_set & s)
    only = len(s - sr_set)
    miss = len(sr_set - s)
    scores[name] = (inter, only, miss)
print(f"  分數 (inter, only, miss): {scores}")

# B 有冇可能 = sage?
# sage 有 25 個 anomaly = 有 edge 但列 SR
# B (冇共同 2D): 如果 anomaly pairs 有共同 edge 但冇共同 2D → 屬 B
# 檢查 anomaly 喺 B?
anomaly_pts = set(combinations(range(36), 2))
print(f"\n[4] 25 anomaly 喺邊個定義?")
# 25 anomaly = sr_set 中有 edge 嘅
for (i, j) in sorted(sr_set - sr_A):
    if i < 36 and j < 36:
        in_B = (i, j) in sr_B
        in_C = (i, j) in sr_C
        print(f"  ({i},{j}): 冇2D? {in_B}, 冇3D? {in_C}")

# ============ 2. 總結 ============
print("\n" + "=" * 72)
print("十期 61 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 61: SR 定義",
    "n_faces": {"1d": len(faces_1d), "2d": len(faces_2d), "3d": len(faces_3d)},
    "scores": {k: list(v) for k, v in scores.items()},
    "sage_n": len(sr_set),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "61_sr_def.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 61 完成!")
