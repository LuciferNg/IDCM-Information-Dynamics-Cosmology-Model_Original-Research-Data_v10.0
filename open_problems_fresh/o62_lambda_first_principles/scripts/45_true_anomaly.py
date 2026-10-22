#!/usr/bin/env python3
"""
O62 九期 45: 真正 anomaly — 有共同 edge 但 sage 列 SR
=====================================================
正確 anomaly = (i,j) ∈ sage SR 且 (i,j) ∈ faces_1d (有共同 edge)
呢啲先係「定義衝突」!

如果 anomaly = 0 → sage 484 = 冇共同 edge pairs 中嘅 active 部分
  484 = {冇共同 edge} ∩ {active 點}?
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 45: 真正 anomaly")
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
pts = np.array(d["points"], dtype=float)
vertices = np.array(d["vertices"], dtype=float)

# faces_1d
faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))

# 冇共同 edge pairs
no_edge = set()
for i in range(48):
    for j in range(i+1, 48):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))

print(f"[1] 冇共同 edge pairs: {len(no_edge)}")
print(f"  sage ∩ no_edge: {len(sr_set & no_edge)}")
print(f"  sage − no_edge (有edge但SR!): {len(sr_set - no_edge)}")

# 真正 anomaly
anomaly = sorted(sr_set - no_edge)
print(f"\n[2] 真正 anomaly (有edge但SR): {len(anomaly)}")
for (i, j) in anomaly:
    print(f"  ({i:2d},{j:2d})")

# 如果 anomaly = 0:
print(f"\n[3] 分析")
print(f"  sage 484 = {len(sr_set & no_edge)} (冇edge) + {len(anomaly)} (anomaly)")

# 檢查: no_edge − sage (有邊啲冇edge但唔係SR)
no_edge_only = sorted(no_edge - sr_set)
print(f"\n[4] no_edge − sage: {len(no_edge_only)}")
# 呢啲係「冇共同edge」但 sage 唔列 SR — 點解?
if no_edge_only:
    print(f"  頭 10 個: {no_edge_only[:10]}")
    # 呢啲係咪涉 inactive 點?
    n_inactive = sum(1 for (i, j) in no_edge_only if i >= 37 or j >= 37)
    print(f"  涉 inactive (37-47): {n_inactive}/{len(no_edge_only)}")

# active 版本
star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1
active = [i for i in range(48) if star.get(i, 0) > 0]
active_set = set(active)
print(f"\n[5] Active-only no_edge")
no_edge_active = set((i, j) for (i, j) in no_edge if i in active_set and j in active_set)
print(f"  active-only no_edge: {len(no_edge_active)}")
print(f"  sage ∩ active-no_edge: {len(sr_set & no_edge_active)}")
print(f"  sage − active-no_edge: {len(sr_set - no_edge_active)}")
print(f"  active-no_edge − sage: {len(no_edge_active - sr_set)}")
# 冇edge但唔SR 嘅 active pairs
noedge_notsr = sorted(no_edge_active - sr_set)
print(f"\n  active 冇edge但唔SR: {len(noedge_notsr)}")
if noedge_notsr:
    print(f"    例: {noedge_notsr[:10]}")

# ============ 總結 ============
print("\n" + "=" * 72)
print("九期 45 總結:")
print("=" * 72)
out = {
    "test": "O62 九期 45: 真正 anomaly",
    "n_no_edge": len(no_edge),
    "sage_inter": len(sr_set & no_edge),
    "anomaly": [(i, j) for (i, j) in anomaly],
    "no_edge_only": [(i, j) for (i, j) in no_edge_only[:10]],
    "active_no_edge": len(no_edge_active),
    "active_noedge_notsr": [(i, j) for (i, j) in noedge_notsr[:10]],
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "45_true_anomaly.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 45 完成!")
