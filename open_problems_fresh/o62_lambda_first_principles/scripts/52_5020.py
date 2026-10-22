#!/usr/bin/env python3
"""
O62 九期 52: all_36_98.poly 完整解析 + 對照
=============================================
PALP 格式: "n_vertices dim" 然後 n 行頂點座標
統計:
  1. 總 polytope 數
  2. 頂點數分佈
  3. 6 頂點 (canonical-like) 有幾多?
  4. 第一個 (canonical) vs 其他
"""
import sys, os, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 52: all_36_98.poly 解析")
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

with open(os.path.join(O53, "all_36_98.poly")) as f:
    lines = [l.strip() for l in f if l.strip()]

# parse
polytopes = []
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2:
        n_v, dim = int(parts[0]), int(parts[1])
        verts = []
        for j in range(n_v):
            i += 1
            verts.append([int(x) for x in lines[i].split()])
        polytopes.append({"n_v": n_v, "dim": dim, "vertices": verts})
    i += 1

print(f"[1] 解析結果")
print(f"  總 polytopes: {len(polytopes)}")
n_verts_dist = {}
for p in polytopes:
    n_verts_dist[p["n_v"]] = n_verts_dist.get(p["n_v"], 0) + 1
print(f"  頂點數分佈: {dict(sorted(n_verts_dist.items()))}")

# ============ 1. 6 頂點 polytopes ============
six_v = [p for p in polytopes if p["n_v"] == 6]
print(f"\n[2] 6 頂點 polytopes: {len(six_v)}")
check("有 6 頂點", len(six_v) > 0, f"({len(six_v)})")

# canonical = 第一個
canon = polytopes[0]
print(f"\n[3] 第一個 (canonical):")
print(f"  頂點數: {canon['n_v']}")
for v in canon["vertices"]:
    print(f"    {v}")

# 其他 6 頂點同 canonical 差幾多?
print(f"\n[4] 6 頂點對照")
for idx, p in enumerate(six_v[:5]):
    # 頂點數相同但座標可能唔同
    vset = set(tuple(v) for v in p["vertices"])
    cset = set(tuple(v) for v in canon["vertices"])
    print(f"  P{idx}: vertices={p['n_v']}, 同 canonical 相同? {vset == cset}")

# ============ 2. 用 cytools 檢查其他 polytope ============
print("\n[5] cytools 檢查非 canonical 6 頂點")
import cytools
from cytools import Polytope, config
config.enable_experimental_features()
for idx, p in enumerate(six_v[1:4]):
    try:
        P = Polytope(p["vertices"])
        print(f"  P{idx+1}: h11={P.h11()}, h12={P.h12()}, 點數={len(P.points())}, dual點數={len(P.polar_polytope().points())}")
    except Exception as e:
        print(f"  P{idx+1}: error {e}")

# canonical 對照
try:
    Pc = Polytope(canon["vertices"])
    print(f"\n  Canonical: h11={Pc.h11()}, h12={Pc.h12()}, 點數={len(Pc.points())}, dual點數={len(Pc.polar_polytope().points())}")
except Exception as e:
    print(f"  Canonical error: {e}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("九期 52 總結:")
print("=" * 72)
out = {
    "test": "O62 九期 52: 5020 對照",
    "n_polytopes": len(polytopes),
    "n_verts_dist": {str(k): v for k, v in sorted(n_verts_dist.items())},
    "n_six": len(six_v),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "52_5020.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 52 完成!")
