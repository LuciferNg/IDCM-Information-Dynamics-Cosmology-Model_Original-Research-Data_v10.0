#!/usr/bin/env python3
"""
O62 十期 65: cytools 權威 SR ideal 完整對照 ★★★
=================================================
cytools tri.sr_ideal() 有 pairs + triples (3-ary) generators!
  pairs: 450+ 個 (2-ary)
  triples: ~35 個 (3-ary)

對照 sage 475:
  1. cytools pairs (2-ary) vs sage pairs
  2. 25 anomaly 喺 cytools 嘅身份
  3. 3-ary generators 嘅角色 (co-simplex 消去!)
"""
import sys, os, json
import numpy as np
from itertools import combinations

print("=" * 72)
print("O62 十期 65: cytools SR 完整對照")
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
from cytools import Polytope, config
config.enable_experimental_features()

canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
tri = P.triangulate(backend="qhull")
sr = tri.sr_ideal()

# 分 pairs 同 triples
pairs = set()
triples = set()
for g in sr:
    if len(g) == 2:
        pairs.add(tuple(sorted(int(x) for x in g)))
    elif len(g) == 3:
        triples.add(tuple(sorted(int(x) for x in g)))
print(f"[1] cytools SR generators")
print(f"  2-ary (pairs): {len(pairs)}")
print(f"  3-ary (triples): {len(triples)}")
print(f"  總: {len(pairs) + len(triples)}")

# ============ 1. 對照 sage ============
d = json.load(open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json"))
sr_sage = set(tuple(sorted(p)) for p in d["sr_ideal"])
print(f"\n[2] sage vs cytools pairs")
print(f"  sage unique: {len(sr_sage)}")
print(f"  cytools pairs (0-47): {len(pairs)}")
sage_active = set((i, j) for (i, j) in sr_sage if i < 36 and j < 36)
print(f"  sage active-only: {len(sage_active)}")
print(f"  cytools pairs ∩ sage: {len(pairs & sr_sage)}")

# cytools pairs 中涉 >35 嘅
pairs_high = set((i, j) for (i, j) in pairs if i >= 36 or j >= 36)
print(f"  cytools pairs 涉 ≥36: {len(pairs_high)}")

# ============ 2. 25 anomaly 身份 ============
faces_1d = set()
for s in d["simplices"]:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))
anomaly = sorted((sr_sage - no_edge) & set(combinations(range(36), 2)))
print(f"\n[3] 25 anomaly 喺 cytools pairs?")
anom_in_cyt = [t for t in anomaly if t in pairs]
anom_not = [t for t in anomaly if t not in pairs]
print(f"  喺 cytools pairs: {len(anom_in_cyt)}")
print(f"  唔喺 cytools pairs: {len(anom_not)}")
if anom_not:
    print(f"    唔喺 pairs 嘅: {anom_not}")
    # 呢啲係咪喺 triples 嘅 subset?
    for t in anom_not:
        in_triple = any(set(t).issubset(set(tr)) for tr in triples)
        print(f"    {t}: 喺 3-ary generator? {in_triple}")

# ============ 3. 3-ary 同 co-simplex ============
print("\n[4] 3-ary generators vs co-simplex 消去")
# 3-ary: {i,j,k} 唔係 face → x_i x_j x_k = 0
# 呢啲對應「唔共 simplex」triples!
cosimp = set()
for s in d["simplices"]:
    lst = sorted(v for v in s if v < 36)
    for i in range(len(lst)):
        for j in range(i, len(lst)):
            for k in range(j, len(lst)):
                cosimp.add((lst[i], lst[j], lst[k]))
print(f"  co-simplex triples: {len(cosimp)}")
# 3-ary generators (active <36)
tri_active = set(t for t in triples if max(t) < 36)
print(f"  cytools 3-ary (active): {len(tri_active)}")
# 3-ary 係咪全部唔喺 co-simplex?
viol3 = sum(1 for t in tri_active if t in cosimp)
print(f"  3-ary 中 co-simplex (應 0): {viol3}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("十期 65 總結:")
print("=" * 72)
print(f"""
  cytools SR ideal: {len(pairs)} pairs + {len(triples)} triples
  sage 475 = 450 (no-edge) + 25 (anomaly)
  
  25 anomaly: {len(anom_in_cyt)} 喺 cytools pairs, {len(anom_not)} 唔喺
  
  → sage 同 cytools 嘅 SR 定義可能唔完全一致
  → 3-ary generators = co-simplex 消去嘅代數根源
""")
out = {
    "test": "O62 十期 65: cytools SR 對照",
    "n_pairs": len(pairs), "n_triples": len(triples),
    "sage_n": len(sr_sage),
    "anom_in_cyt": len(anom_in_cyt), "anom_not": anom_not,
    "tri_active": len(tri_active), "viol3": viol3,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "65_cytools_full.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 65 完成!")
