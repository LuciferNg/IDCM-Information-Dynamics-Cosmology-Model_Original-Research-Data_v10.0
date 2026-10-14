#!/usr/bin/env python3
"""
O144-14 — 聯合被迫性: 有多少三元組 (共享模式, 對偶集, 行和) 唯一決定解? (2026-09-17)
=====================================================================================
scripts/13 單條測試: 共享對 100/210 容許, 對偶集 42, 行和弱。
本測試: 枚舉所有 (P, D, R) 三元組, 數哪些能唯一決定一個解。
  - 若唯一三元組數 ≈ 1 → 結構被數據強迫 (真結果, 真網格是唯一自洽結構)
  - 若很多 → 框架的選擇是 1/N, 任意 (後驗)

R 候選: (家族, 欄位, 目標) — 欄位 ∈ {n 和, P_f 和}, 目標 ∈ 結構常數集
"""
import json, math, itertools, sys
from collections import Counter, defaultdict

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
print("O144-14 聯合被迫性測試")
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

# 桶: (share, dual) → assignments
buckets = defaultdict(list)
for a in all_assigns:
    buckets[(share_pattern(a), dual_set(a))].append(a)
print(f"不同 (共享, 對偶) 組合數 = {len(buckets)}")

# R 候選: (家族, 欄位, 目標)
struct_targets = [28.5, 28.0, 33.0, 44.0, 13.0, 7.0, 18.0, 34.0, 57.0, 90.0, 16.0, 51.0, 11.0, 37.0, 15.5, 3.6]
R_cands = []
for fam in ["L", "U", "D"]:
    for field in ["n", "pf"]:
        for t in struct_targets:
            R_cands.append((fam, field, t))
print(f"R 候選數 = {len(R_cands)}")

def r_sat(a, R):
    fam, field, t = R
    mem = [p for p in pkeys if FAM[p] == fam]
    s = sum(a[p][0] if field == "n" else a[p][1] for p in mem)
    return abs(s - t) < 1e-9

unique_triples = []
for (P, D), assigns in buckets.items():
    if not assigns: continue
    for R in R_cands:
        sat = [a for a in assigns if r_sat(a, R)]
        if len(sat) == 1:
            unique_triples.append((P, D, R, sat[0]))

print(f"\n能唯一決定解的三元組數 = {len(unique_triples)}")

# 真網格的三元組
true_P, true_D = share_pattern(TRUE), dual_set(TRUE)
true_triples = [(P, D, R, a) for (P, D, R, a) in unique_triples if P == true_P and D == true_D]
print(f"其中屬於真網格 (共享={[list(t) for t in true_P]}, 對偶={len(true_D)} 條) 的三元組數 = {len(true_triples)}")
for P, D, R, a in true_triples:
    same = (a == TRUE)
    print(f"  R = {R} → 解{'= 真網格 ✅' if same else ' ≠ 真網格 ❌'}")

# 有多少個不同的最終解被唯一選出?
distinct_solutions = set()
for P, D, R, a in unique_triples:
    distinct_solutions.add(tuple(sorted((p, a[p][0], a[p][1]) for p in pkeys)))
print(f"\n被唯一選出的不同解數 = {len(distinct_solutions)}")
print(f"真網格是否其中之一: {'✅' if tuple(sorted((p, TRUE[p][0], TRUE[p][1]) for p in pkeys)) in distinct_solutions else '❌'}")

# 判決
print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
print(f"""
解空間 6468 → 不同 (共享,對偶) 組合 {len(buckets)} → 唯一三元組 {len(unique_triples)}

真網格: 共享模式 = {[list(t) for t in true_P]}, 對偶集 = {len(true_D)} 條
  在真 (共享,對偶) 桶內, 有 {len(true_triples)} 個 R 能唯一決定 → 若 R = U行和=28.5 唯一 → 結構自洽

★ 判讀:
  唯一三元組數 = {len(unique_triples)}, 不同解 = {len(distinct_solutions)}
  若 不同解 少 (1-3) → 網格結構被數據強迫
  若 不同解 多 → 框架選擇任意 (1/N)
""")

out = {
    "session": "2026-09-17 O144-14 joint forcedness",
    "solution_space": len(all_assigns),
    "buckets": len(buckets),
    "unique_triples": len(unique_triples),
    "true_bucket_unique_R": [list(R) for _, _, R, _ in true_triples],
    "distinct_solutions_selected": len(distinct_solutions),
    "verdict": f"{len(distinct_solutions)} distinct grids uniquely selectable",
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/14_joint_forcedness.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/14_joint_forcedness.json 已寫入")
sys.exit(0)
