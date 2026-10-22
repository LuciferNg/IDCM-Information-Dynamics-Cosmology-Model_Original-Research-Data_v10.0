#!/usr/bin/env python3
"""
O62 九期 42: SR pairs 深入 — 25 anomaly + active 篩選
======================================================
上次發現:
  912 = 全部冇共同 simplex pairs (含 inactive 37-47)
  484 = sage (只涉 active?)
  我−sage 462 個全部涉 inactive 點
  sage−我 25 個: 有共同 simplex 但 sage 話 SR?!

深入:
  1. 如果只計 active 點 (0-36): 912 中涉 active-only 嘅 pairs?
  2. 25 個 anomaly: 檢查佢哋嘅 simplex 上下文
  3. sage 484 嘅精確定義
"""
import sys, os, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 42: SR pairs 深入")
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
pts = np.array(d["points"], dtype=float)

# star 計
star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1
active = [i for i in range(48) if star.get(i, 0) > 0]
inactive = [i for i in range(48) if star.get(i, 0) == 0]
print(f"[1] active: {len(active)} (0-36?), inactive: {inactive}")

# ============ 1. Active-only pairs ============
print("\n[2] Active-only 冇共同 simplex pairs")
simplex_sets = [set(s) for s in simplices]
my_pairs_active = []
for i in active:
    for j in active:
        if i < j and not any(i in ss and j in ss for ss in simplex_sets):
            my_pairs_active.append((i, j))
print(f"  active-only 冇共同 simplex pairs: {len(my_pairs_active)}")
my_active_set = set(my_pairs_active)
sr_set = set(tuple(sorted(p)) for p in sr_sage)
print(f"  sage ∩ active-only: {len(sr_set & my_active_set)}")
print(f"  sage − active-only: {len(sr_set - my_active_set)}")
print(f"  active-only − sage: {len(my_active_set - sr_set)}")

# ============ 2. 25 anomaly 深入 ============
print("\n[3] 25 個 anomaly (sage 有但我冇)")
anomaly = sorted(sr_set - my_active_set)
for (i, j) in anomaly:
    # 呢對有共同 simplex (因為唔喺 my_pairs)
    common_simps = [s for s in simplices if i in set(s) and j in set(s)]
    print(f"  ({i},{j}): 共同 simplex {len(common_simps)} 個, 例: {common_simps[0] if common_simps else '無'}")
    # 檢查呢啲 simplex 有冇包含佢哋嘅 3-face?
    # 可能: 佢哋喺同一 4-simplex 但唔係同一 3-face?

# 檢查: 呢啲 pairs 係咪「有共同 4-simplex 但冇共同 3-face」?
# SR ideal 嘅定義: {i,j} 唔係任何 face 嘅 subset
# face = 任何維度嘅面 (1-face, 2-face, 3-face, 4-face)
# 我計「有共同 simplex」= 有共同 4-simplex
# 但正確 SR: 有冇共同 3-face (cone)?

print("\n[4] 重新定義: SR = 冇共同 3D cone (4點 face)")
from itertools import combinations
cones = set()
for s in simplices:
    for f in combinations(s, 4):
        cones.add(tuple(sorted(f)))
print(f"  3D cones (4點): {len(cones)}")

# SR pair = 冇任何 cone 同時含 i,j
my_pairs_cone = []
for i in range(48):
    for j in range(i+1, 48):
        if not any(i in c and j in c for c in cones):
            my_pairs_cone.append((i, j))
print(f"  冇共同 cone pairs: {len(my_pairs_cone)}")
my_cone_set = set(my_pairs_cone)
print(f"  sage ∩ cone-def: {len(sr_set & my_cone_set)}")
print(f"  sage − cone-def: {len(sr_set - my_cone_set)}")
print(f"  cone-def − sage: {len(my_cone_set - sr_set)}")

# ============ 3. cytools 驗證 ============
print("\n[5] cytools 計 intersection")
import cytools
from cytools import Polytope, config
config.enable_experimental_features()
canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
tri = P.triangulate(backend="qhull")
simps = tri.simplices()
print(f"  cytools simplices: {len(simps)}")
# cytools 有冇 star / sr?
if hasattr(tri, "star"):
    print(f"  tri.star exists")
# 檢查 cytools 嘅 simplex 同 sage 一樣?
sage_sets = set(tuple(sorted(s)) for s in simplices)
cyt_sets = set(tuple(sorted(s)) for s in simps)
print(f"  sage simplex = cytools? {sage_sets == cyt_sets}")
print(f"  sage 有 cyt 冇: {len(sage_sets - cyt_sets)}")
print(f"  cyt 有 sage 冇: {len(cyt_sets - sage_sets)}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("九期 42 總結:")
print("=" * 72)
print(f"""
  active-only 冇共同 simplex: {len(my_pairs_active)}
  sage 484 = {len(sr_set & my_active_set)} ∩ + {len(sr_set - my_active_set)} 其他

  anomaly 25 個: 有共同 4-simplex 但可能冇共同 3-cone?
  cone 定義: {len(my_pairs_cone)} pairs
""")
out = {
    "test": "O62 九期 42: SR 深入",
    "n_active": len(active),
    "active_pairs": len(my_pairs_active),
    "anomaly": [(i, j) for (i, j) in anomaly],
    "cone_pairs": len(my_pairs_cone),
    "sage_vs_cone": {"inter": len(sr_set & my_cone_set), "sage_only": len(sr_set - my_cone_set), "cone_only": len(my_cone_set - sr_set)},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "42_sr_deep.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 42 完成!")
