#!/usr/bin/env python3
"""
O62 十期 58: point 36 vs point 8 — L₇ divisor 身份
====================================================
point 8 = (1,1,0,0) = L₇ divisor (K=-232, 確認)
point 36 = (-1,-1,0,0) = -point 8? 反點!

檢查:
  1. point 36 = -point 8?
  2. point 36 喺 simplex 嘅角色 (star=8)
  3. point 36 對應嘅 kappa (如果 shift 到 kappa 36 度?)
  4. 25 anomaly 中涉及 point 36 嘅 pairs

關鍵: kappa 36×36 係咪其實包含 point 36 (index 36 被裁走)?
  或者 kappa 用嘅 36 個 divisor 唔係 0-35, 而係某種 mapping?
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 58: point 36 vs point 8")
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
pts = np.array(d["points"], dtype=float)
sr_sage = d["sr_ideal"]
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

print("[1] point 8 vs point 36")
print(f"  point 8:  {pts[8]}")
print(f"  point 36: {pts[36]}")
print(f"  point 36 = -point 8? {np.allclose(pts[36], -pts[8])}")
check("p36 = -p8", np.allclose(pts[36], -pts[8]), "")

print(f"\n[2] point 36 嘅 simplex 角色")
p36_simps = [s for s in simplices if 36 in set(s)]
print(f"  point 36 喺 {len(p36_simps)} simplices")
for s in p36_simps[:8]:
    print(f"    {s}")

# point 36 同邊啲點共 simplex?
p36_partners = set()
for s in p36_simps:
    for v in s:
        if v != 36:
            p36_partners.add(v)
print(f"  point 36 嘅 partners (共 simplex): {sorted(p36_partners)}")

# ============ 1. 25 anomaly 中涉 point 36 ============
print("\n[3] 25 anomaly 中涉 point 36")
# 正確 anomaly (kappa divisors 0-35)
faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge_36 = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge_36.add((i, j))
sr_set = set(tuple(sorted(p)) for p in sr_sage)
anomaly_36 = sorted(sr_set - no_edge_36)
print(f"  25 anomaly (kappa divisors): {len(anomaly_36)}")
print(f"  {anomaly_36}")

# ============ 2. kappa 對應 ============
print("\n[4] kappa index mapping")
# kappa 36 個 index 對應邊 36 個點?
# intersection_full 用 0-35? 定係 0-36 中刪一個?
# 如果 kappa[0,0,0] = -360 → index 0 = div0 = point 0 (0,0,0,0)
print(f"  kappa[0,0,0] = {kappa36[0,0,0]}")
print(f"  kappa[8,8,8] = {kappa36[8,8,8]}")
print(f"  kappa[35,35,35] = {kappa36[35,35,35]}")

# 檢查: kappa 有冇涉 index 36 嘅 entry (即 36×36 但其實係 0-35 + 36?)
print(f"\n[5] kappa 檔案完整度")
# intersection_full 有冇 n_points 記錄?
meta = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
if "n_points" in meta:
    print(f"  n_points: {meta['n_points']}")
if "points" in meta:
    print(f"  points count: {len(meta['points'])}")
print(f"  keys: {list(meta.keys())}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("十期 58 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 58: p36 vs p8",
    "p8": pts[8].tolist(), "p36": pts[36].tolist(),
    "neg": bool(np.allclose(pts[36], -pts[8])),
    "p36_partners": sorted(p36_partners),
    "anomaly36": anomaly_36,
    "kappa000": int(kappa36[0,0,0]), "kappa888": int(kappa36[8,8,8]),
    "keys": list(meta.keys()),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "58_p36_vs_p8.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 58 完成!")
