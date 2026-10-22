#!/usr/bin/env python3
"""
O62 九期 41: SR pairs 484 vs 912 定義核對
===========================================
sage export: 484 SR pairs
我由 simplices 計: 912 pairs

hypothesis:
  - 912 = 所有「冇共同 simplex」嘅對 (pairs)
  - 484 = minimal generators? 定係有方向性?
  - 或者 sage 嘅 sr_ideal 用「minimal」定義 (冇 redundancy)

驗證:
  1. 912 對中, 邊啲係「minimal」(唔可以被其他 pair 推導)?
  2. 484 係咪 = minimal?
  3. SR ideal 生成元嘅正確定義
"""
import sys, os, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 41: SR pairs 484 vs 912")
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
sr_sage = d["sr_ideal"]  # 484 pairs

# 我自己計: 冇任何 simplex 同時包含 {i,j}
simplex_sets = [set(s) for s in simplices]
my_pairs = []
for i in range(48):
    for j in range(i+1, 48):
        if not any(i in ss and j in ss for ss in simplex_sets):
            my_pairs.append((i, j))
my_set = set(my_pairs)

print(f"[1] 數量")
print(f"  sage sr_ideal: {len(sr_sage)}")
print(f"  我計 (冇共同 simplex): {len(my_pairs)}")
print(f"  差: {len(my_pairs) - len(sr_sage)}")

sr_set = set(tuple(sorted(p)) for p in sr_sage)
print(f"\n[2] 集合比較")
print(f"  sage ∩ 我: {len(sr_set & my_set)}")
print(f"  sage − 我: {len(sr_set - my_set)}")
print(f"  我 − sage: {len(my_set - sr_set)}")

# sage 有但我冇嘅
only_sage = sorted(sr_set - my_set)
only_mine = sorted(my_set - sr_set)
if only_sage:
    print(f"\n  sage 有但我冇 ({len(only_sage)}): {only_sage[:10]}")
    # 呢啲對係咪真係有共同 simplex?
    for (i, j) in only_sage[:5]:
        has_common = any(i in ss and j in ss for ss in simplex_sets)
        print(f"    ({i},{j}): 有共同 simplex? {has_common}")
if only_mine:
    print(f"\n  我有但 sage 冇 ({len(only_mine)}): {only_mine[:10]}")
    for (i, j) in only_mine[:5]:
        has_common = any(i in ss and j in ss for ss in simplex_sets)
        print(f"    ({i},{j}): 有共同 simplex? {has_common}")

# ============ 1. Minimal generators ============
print("\n[3] Minimal generators 分析")
# SR ideal 生成元: monomial 唔可以被更細 monomial 整除
# pair (i,j) 係 minimal 如果冇其他 pair (i,k) or (k,j) 喺 ideal
# 即: 如果 (i,j) ∈ I 且 (i,k) ∈ I, 咁 (i,j,k) 自動 ∈ I (redundant)
# minimal pairs: 冇任何 proper subset 喺 I

# 對 pairs: (i,j) 嘅 proper subsets 係 {i}, {j} (單點永遠唔喺 I)
# 所以所有 pairs 都 minimal?? 唔係 — 要睇 monomial ideal 定義
# 正確: SR(I) = < x_{i1}...x_{ik} : {i1..ik} 唔係 face >
# minimal generators = 冇 proper sub-monomial 喺 ideal
# 即 pair (i,j) 係 minimal 如果 {i} 同 {j} 都係 face (一定係)
# → 所有 pairs 都 minimal!

# 咁 484 係咩? 可能係「co-plex 面」(face complement)?
# 或者 sage 用唔同嘅 simplex 集合 (只 count 某啲 faces)?

# 試另一定義: pairs (i,j) 喺唔同嘅 star?
print("\n[4] 另一假設: sage SR = face-based")
# sage 可能由 qhull triangulation 嘅 facets 計
# 我由 4-simplex 計 — 如果 sage 用嘅係「facets of polytope」而唔係「simplices of triangulation」?

# 檢查: 912 − 484 = 428 個 pairs — 有咩特徵?
diff_mine = only_mine
if diff_mine:
    # 呢啲 pairs 嘅 index 分佈
    from collections import Counter
    idx_count = Counter()
    for (i, j) in diff_mine:
        idx_count[i] += 1
        idx_count[j] += 1
    top = idx_count.most_common(10)
    print(f"  我−sage 嘅 pairs 最常出現 index: {top}")
    # 高 index (37-47 = star=0 點)?
    inactive = [i for i in range(37, 48)]
    n_inactive_pairs = sum(1 for (i,j) in diff_mine if i in inactive or j in inactive)
    print(f"  涉及 inactive 點 (37-47) 嘅 pairs: {n_inactive_pairs}/{len(diff_mine)}")

# sage 冇嘅 pairs 係咪全部涉及 inactive 點?
if diff_mine:
    n_inactive = sum(1 for (i,j) in diff_mine if max(i,j) >= 37)
    print(f"\n  my−sage 中涉及 index≥37: {n_inactive}/{len(diff_mine)}")

# ============ 2. 用 cytools 驗證 ============
print("\n[5] cytools SR ideal 對照")
try:
    import cytools
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    simps = tri.simplices()
    print(f"  cytools simplices: {len(simps)}")
    # cytools 有冇 SR ideal?
    if hasattr(P, "sr_ideal"):
        sr = P.sr_ideal()
        print(f"  cytools sr_ideal: {len(sr)}")
    else:
        print(f"  cytools 冇直接 sr_ideal method")
except Exception as e:
    print(f"  cytools error: {e}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("九期 41 總結:")
print("=" * 72)
print(f"""
  sage SR pairs: {len(sr_sage)} (484)
  我由 simplices 計: {len(my_pairs)} (912)

  假設:
  - sage 484 = 只計「triangulation 用到嘅點」(37 active)?
  - 912 − 484 = 428 = 涉及 star=0 點 (37-47) 嘅 pairs?

  需要: cytools 完整驗證
""")
out = {
    "test": "O62 九期 41: SR pairs",
    "n_sage": len(sr_sage), "n_mine": len(my_pairs),
    "inter": len(sr_set & my_set),
    "only_sage": len(sr_set - my_set), "only_mine": len(my_set - sr_set),
    "diff_inactive": n_inactive if diff_mine else None,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "41_sr_pairs.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 41 完成!")
