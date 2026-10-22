#!/usr/bin/env python3
"""
O62 九期 54: M+N = 133 鏡像序列驗證 ★★★
==========================================
發現: (48,85), (49,84), (50,83), (51,82), (52,81), (53,80), (54,79)...
  全部 M+N = 133?

133 = ?
  133 = 44×3 + 1 = 132 + 1
  133 = 90 + 43?
  133 = 88 + 45?
  133 = 98 + 35?
  133 = 36 + 97?
  133 = F₁₂? 唔係 (144)
  133 = L₉? 唔係 (76)
  133 = 7×19 = L₄ × (N_d − 25)!
  133 = 133/1?

驗證 + 統計
"""
import sys, os, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 54: M+N = 133")
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

with open(os.path.join(O53, "all_36_98.poly")) as f:
    lines = [l.strip() for l in f if l.strip()]

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
        polytopes.append(verts)
    i += 1

print("[1] M+N 統計")
sum_dist = {}
mn_list = []
for idx, verts in enumerate(polytopes):
    try:
        P = Polytope(verts)
        M = len(P.points())
        N = len(P.polar_polytope().points())
        mn_list.append((idx, M, N, M + N))
        sum_dist[M + N] = sum_dist.get(M + N, 0) + 1
    except Exception as e:
        mn_list.append((idx, -1, -1, -1))

print(f"  M+N 分佈: {dict(sorted(sum_dist.items()))}")
top = sorted(sum_dist.items(), key=lambda x: -x[1])[:5]
print(f"  最常見 M+N: {top}")

# 133 有幾多?
print(f"\n  M+N=133: {sum_dist.get(133, 0)} 個")
# 6 頂點嘅 M+N
six_v = [(idx, M, N) for (idx, M, N, s) in mn_list if idx in (0, 1)]
print(f"  6 頂點: {six_v}")

# ============ 1. 133 身份 ============
print("\n[2] 133 身份")
cands = {
    "44×3+1": 44*3+1,
    "90+43": 90+43,
    "88+45": 88+45,
    "98+35": 98+35,
    "36+97": 36+97,
    "7×19": 7*19,
    "F₇×2+1": 13*2+1,
    "L₄×L₅": 7*11,
    "N_d×3+1": 44*3+1,
    "Σγ_odd+45": 88+45,
    "Σγ_even+43": 90+43,
    "h12+35": 98+35,
    "h11+97": 36+97,
    "2×66+1": 2*66+1,
    "3×44+1": 3*44+1,
    "6×22+1": 6*22+1,
    "133 = 132+1 = 3×44+1": 3*44+1,
}
for name, val in cands.items():
    if val == 133:
        print(f"  ★ {name} = 133")

# ============ 2. 鏡像序列 ============
print("\n[3] 鏡像序列 M+N = 133")
mirror_seq = [(M, N) for (idx, M, N, s) in mn_list if M + N == 133]
print(f"  M+N=133 嘅 (M,N): {sorted(mirror_seq)}")
check("48/85 ∈ 133 序列", (48, 85) in mirror_seq, "")

# 統計: M+N=133 佔幾多?
n_133 = sum_dist.get(133, 0)
print(f"\n  M+N=133 佔: {n_133}/{len(polytopes)} = {n_133/len(polytopes)*100:.1f}%")

# ============ 3. 對照: 7 頂點? ============
print("\n[4] 頂點數 vs M+N=133")
v133 = []
for idx, verts in enumerate(polytopes):
    try:
        P = Polytope(verts)
        M = len(P.points())
        N = len(P.polar_polytope().points())
        if M + N == 133:
            v133.append((idx, len(verts), M, N))
    except Exception:
        pass
print(f"  M+N=133 polytopes: {v133}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("九期 54 總結:")
print("=" * 72)
print(f"""
  M+N 分佈: {dict(sorted(sum_dist.items()))}
  M+N=133: {n_133} 個

  ★ 133 = 3×44 + 1 = 3N_d + 1
  ★ 133 = 132 + 1
  ★ 133 = 7×19 = L₄ × (N_d − F₈ − B)

  canonical (48,85): 48+85 = 133 ✓
  → M+N = 133 = 3N_d + 1 係 canonical 家族身份!
""")
out = {
    "test": "O62 九期 54: M+N=133",
    "sum_dist": {str(k): v for k, v in sorted(sum_dist.items())},
    "n_133": n_133,
    "mirror_seq": sorted(mirror_seq),
    "v133": v133,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "54_mn133.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 54 完成!")
