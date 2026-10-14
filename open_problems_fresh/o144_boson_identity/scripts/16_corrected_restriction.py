#!/usr/bin/env python3
"""
O144-16 — 修正限制: 對偶同家族 / 共享跨家族 (2026-09-17)
==========================================================
scripts/15 錯誤: 把「對偶必須跨家族」當限制 → 真網格被排除 (❌ 假陰性)。
真網格實際結構:
  共享對: e(L)↔s(D) 跨家族;  μ(L)↔u(U) 跨家族
  對偶:   τ(L)↔μ(L) 同家族;   b(D)↔d(D) 同家族
→ 修正限制: 共享跨家族 + 對偶同家族
判決: 此限制下唯一網格數 = ? 真網格是否唯一?
"""
import json, math, itertools, sys
from collections import defaultdict

M0 = 27.9009
Nd = 44
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

MODES = sorted({n for L in [4, 8, 11, 22, 44] for n in range(1, 45) if (n * L) % 88 == 44})
T_CONST = {"N_d": 44.0, "L4": 7.0, "L5": 11.0, "F7": 13.0, "F9": 34.0, "L6/F5": 3.6}
pool = {}
for k, v in T_CONST.items():
    pool[k] = v; pool[f"N_d-{k}"] = Nd - v; pool[f"(N_d-{k})/2"] = (Nd - v) / 2
pool = {k: v for k, v in pool.items() if 0 < v <= 200}

TRUE = {"e": (1, 3.6), "mu": (7, 15.5), "tau": (20, 37.0), "u": (1, 15.5),
        "d": (1, 33.0), "s": (14, 3.6), "c": (34, 13.0), "b": (33, 44.0)}
FAM = {"e": "L", "mu": "L", "tau": "L", "u": "U", "c": "U", "d": "D", "s": "D", "b": "D"}
TARGET = {"e": 0.5110, "mu": 105.66, "tau": 1776.86, "u": 2.16, "d": 4.67,
          "s": 93.0, "c": 1270.0, "b": 4180.0}
WINDOW = 0.025
pkeys = list(TRUE.keys())
sols = {}
for p, t in TARGET.items():
    seen, uniq = set(), []
    for n in MODES:
        for pk, pv in pool.items():
            if abs(M0 * gamma(n) * pv - t) / t < WINDOW and (n, round(pv, 4)) not in seen:
                seen.add((n, round(pv, 4))); uniq.append((n, round(pv, 4)))
    sols[p] = uniq

print("=" * 76)
print("O144-16 修正限制測試")
print("=" * 76)
all_assigns = [{p: combo[i] for i, p in enumerate(pkeys)}
               for combo in itertools.product(*[sols[p] for p in pkeys])]
print(f"解空間 |S| = {len(all_assigns)}")

def share_pattern(a):
    m = {}
    for p in pkeys: m.setdefault(round(a[p][1], 4), []).append(p)
    return tuple(sorted(tuple(sorted(v)) for v in m.values() if len(v) > 1))
def dual_set(a):
    hits = set()
    for p in pkeys:
        for q in pkeys:
            if p == q: continue
            if abs(a[p][1] - (Nd - a[q][0])) < 1e-9: hits.add((p, q, "Pf=Nd-n"))
            if abs(a[p][0] - a[q][1]) < 1e-9: hits.add((p, q, "n=Pf"))
    return frozenset(hits)

def ok_share(P):   # 跨家族, 每對恰 2 粒
    return (len(P) == 2 and all(len(pr) == 2 for pr in P)
            and all(FAM[pr[0]] != FAM[pr[1]] for pr in P))
def ok_dual(D):    # 同家族
    return len(D) == 2 and all(FAM[p] == FAM[q] for p, q, _ in D)

DERIVED = [28.5, 28.0, 44.0, 33.0]
R_cands = [(fam, f, t) for fam in ["L", "U", "D"] for f in ["n", "pf"] for t in DERIVED]

print(f"真網格 共享模式 = {[list(t) for t in share_pattern(TRUE)]} → 跨家族? {ok_share(share_pattern(TRUE))}")
print(f"真網格 對偶集 = {sorted(dual_set(TRUE))} → 同家族? {ok_dual(dual_set(TRUE))}")

buckets = defaultdict(list)
for a in all_assigns:
    P, D = share_pattern(a), dual_set(a)
    if ok_share(P) and ok_dual(D): buckets[(P, D)].append(a)
print(f"受限桶數 = {len(buckets)}")

def r_sat(a, R):
    fam, f, t = R
    mem = [p for p in pkeys if FAM[p] == fam]
    return abs(sum(a[p][0] if f == "n" else a[p][1] for p in mem) - t) < 1e-9

unique_triples = []
for (P, D), assigns in buckets.items():
    for R in R_cands:
        sat = [a for a in assigns if r_sat(a, R)]
        if len(sat) == 1: unique_triples.append((P, D, R, sat[0]))
print(f"唯一三元組數 = {len(unique_triples)}")

distinct = {}
for P, D, R, a in unique_triples:
    key = tuple(sorted((p, a[p][0], a[p][1]) for p in pkeys))
    distinct.setdefault(key, []).append(R)
print(f"不同網格數 = {len(distinct)}")
true_key = tuple(sorted((p, TRUE[p][0], TRUE[p][1]) for p in pkeys))
print(f"真網格在其中: {'✅' if true_key in distinct else '❌'}")
if true_key in distinct: print(f"  真網格由 R = {distinct[true_key]} 選出")

print(f"\n全部競爭網格:")
for i, (k, Rs) in enumerate(distinct.items()):
    a = {k[j][0]: (k[j][1], k[j][2]) for j in range(len(k))}
    diff = {p: a[p] for p in pkeys if a[p] != TRUE[p]}
    mark = "  ★ 真網格" if k == true_key else ""
    print(f"  [{i+1}] R={Rs[0]} 差異={diff}{mark}")

print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
print(f"解空間 6468 → 桶 {len(buckets)} → 唯一三元組 {len(unique_triples)} → 不同網格 {len(distinct)}")
print(f"真網格 = 1/{len(distinct)} → {'✅ 結構被迫' if len(distinct)==1 else '❌ 仍任意'}")
print(f"\n⚠️ 但限制 (共享跨家族 + 對偶同家族) 本身是從真網格讀出的 2 bits → 仍未 form-blind")

out = {"session": "2026-09-17 O144-16 corrected restriction",
       "solution_space": len(all_assigns), "buckets": len(buckets),
       "unique_triples": len(unique_triples), "distinct_grids": len(distinct),
       "true_grid_selected": true_key in distinct,
       "verdict": "forced" if len(distinct) == 1 else f"NOT forced: {len(distinct)} grids"}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/16_corrected_restriction.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/16_corrected_restriction.json 已寫入")
sys.exit(0)
