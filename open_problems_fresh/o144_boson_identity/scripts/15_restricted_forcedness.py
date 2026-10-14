#!/usr/bin/env python3
"""
O144-15 — 受限被迫性: 只用「衍生常數 + 跨家族模式」, 真網格還剩幾個競爭者? (2026-09-17)
=========================================================================================
scripts/14: 362 個三元組 → 311 個不同網格 (真網格 1/311)。
本測試加結構限制 (限制來自結構推理, 非從網格讀出):
  - 共享對: 必須跨家族 (e∈L & s∈D; μ∈L & u∈U) — 同家族共享被排除
  - 對偶: 必須跨家族
  - R 目標: 只用「有定理」的衍生常數 {E_proj=28.5, N_φ12=28, N_d=44, M=33}

判決: 若受限後唯一網格數 = 1 → 結構被迫 (真結果)
      > 1 → 仍任意, 框架無法選出真網格
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
print("O144-15 受限被迫性測試")
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

# 結構限制 1: 共享對必須跨家族
def cross_family_share(P):
    if len(P) != 2: return False
    for pair in P:
        if FAM[pair[0]] == FAM[pair[1]]: return False
    return True

# 結構限制 2: 對偶必須跨家族
def cross_family_dual(D):
    if len(D) != 2: return False
    for (p, q, _) in D:
        if FAM[p] == FAM[q]: return False
    return True

# 結構限制 3: R 目標 = 衍生常數
DERIVED = [28.5, 28.0, 44.0, 33.0]
R_cands = [(fam, field, t) for fam in ["L", "U", "D"] for field in ["n", "pf"] for t in DERIVED]

buckets = defaultdict(list)
for a in all_assigns:
    P, D = share_pattern(a), dual_set(a)
    if not (cross_family_share(P) and cross_family_dual(D)): continue
    buckets[(P, D)].append(a)
print(f"受限後 (共享,對偶) 桶數 = {len(buckets)}")
print(f"R 候選數 (衍生常數) = {len(R_cands)}")

def r_sat(a, R):
    fam, field, t = R
    mem = [p for p in pkeys if FAM[p] == fam]
    return abs(sum(a[p][0] if field == "n" else a[p][1] for p in mem) - t) < 1e-9

unique_triples = []
for (P, D), assigns in buckets.items():
    for R in R_cands:
        sat = [a for a in assigns if r_sat(a, R)]
        if len(sat) == 1:
            unique_triples.append((P, D, R, sat[0]))
print(f"\n唯一三元組數 = {len(unique_triples)}")

distinct = {}
for P, D, R, a in unique_triples:
    key = tuple(sorted((p, a[p][0], a[p][1]) for p in pkeys))
    distinct.setdefault(key, []).append(R)
print(f"被唯一選出的不同網格數 = {len(distinct)}")

true_key = tuple(sorted((p, TRUE[p][0], TRUE[p][1]) for p in pkeys))
print(f"真網格是否其中之一: {'✅' if true_key in distinct else '❌'}")
if true_key in distinct:
    print(f"  真網格由這些 R 選出: {distinct[true_key]}")

# 列出競爭者 (前 5)
print(f"\n競爭網格樣本 (前 5):")
for i, (k, Rs) in enumerate(list(distinct.items())[:5]):
    a = {p: (k[j][1], k[j][2]) for j, p in enumerate(pkeys)}
    diff = {p: a[p] for p in pkeys if a[p] != TRUE[p]}
    print(f"  [{i+1}] 由 {Rs[0]} 選出; 與真網格差異: {diff}")

print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
print(f"""
解空間 6468 → 受限桶 {len(buckets)} → 唯一三元組 {len(unique_triples)} → 不同網格 {len(distinct)}

真網格 = 1/{len(distinct)}
判決: {'✅ 結構被迫 (唯一)' if len(distinct) == 1 else f'❌ 仍任意 — {len(distinct)} 個網格同型自洽, 框架無法選出真網格'}
""")

out = {"session": "2026-09-17 O144-15 restricted forcedness",
       "solution_space": len(all_assigns), "restricted_buckets": len(buckets),
       "unique_triples": len(unique_triples), "distinct_grids": len(distinct),
       "true_grid_selected": true_key in distinct,
       "verdict": "forced (unique)" if len(distinct) == 1 else f"NOT forced: {len(distinct)} competing grids"}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/15_restricted_forcedness.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/15_restricted_forcedness.json 已寫入")
sys.exit(0)
