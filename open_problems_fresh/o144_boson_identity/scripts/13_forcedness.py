#!/usr/bin/env python3
"""
O144-13 — 結構被迫性測試: 約束模式是數據強迫還是任意挑選? (2026-09-17)
========================================================================
scripts/11-12: 3 條結構約束 (2 共享對 + 2 對偶 + 1 行和) 唯一決定網格, LOOCV 8/8。
但約束模式是「看到網格後」選的。決定性問題:
  ★ 有多少種「同型」約束模式能容許一個符合 8 個質量的解?
  若極少 → 結構被數據強迫 (真結果)
  若很多 → 模式任意挑選 (後驗)

測試:
  [A] 共享對模式: 8 粒中選 2 個不相交對 (210 種) → 每種有多少解空間成員符合?
  [B] 對偶模式: 跨行對偶關係的模式 (P_f(p)=N_d−n(q) 或 n(p)=P_f(q)) → 容許解的模式數
  [C] 行和: 哪些 (家族, 和) 組合等於結構常數?
  [D] 判決
"""
import json, math, itertools, sys
from collections import Counter

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
GEN = {"e": 1, "mu": 2, "tau": 3, "u": 1, "c": 2, "d": 1, "s": 2, "b": 3}
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
print("O144-13 結構被迫性測試")
print("=" * 76)
all_assigns = [{p: combo[i] for i, p in enumerate(pkeys)}
               for combo in itertools.product(*[sols[p] for p in pkeys])]
print(f"解空間 |S| = {len(all_assigns)}")

# ================================================================
# [A] 共享對模式: 210 種, 每種有多少解符合?
# ================================================================
print("\n[A] 共享對模式 (2 個不相交 P_f 共享對) 的可容許性")
print("-" * 60)
pairs = list(itertools.combinations(pkeys, 2))
patterns = []
for i, p1 in enumerate(pairs):
    for p2 in pairs[i+1:]:
        if set(p1) & set(p2): continue
        patterns.append((tuple(sorted(p1)), tuple(sorted(p2))))
print(f"  總模式數 (2 不相交對) = {len(patterns)}")

def share_pattern(a):
    m = {}
    for p in pkeys: m.setdefault(round(a[p][1], 4), []).append(p)
    sh = sorted(tuple(sorted(v)) for v in m.values() if len(v) > 1)
    return tuple(sh)

pat_counter = Counter()
for a in all_assigns:
    pat_counter[share_pattern(a)] += 1
admissible = {k: v for k, v in pat_counter.items() if k}
print(f"  容許 (有解) 的共享模式數 = {len(admissible)}")
print(f"  真網格模式 = {share_pattern(TRUE)}")
print(f"  該模式解數 = {admissible.get(share_pattern(TRUE), 0)}")
top = sorted(admissible.items(), key=lambda kv: -kv[1])[:6]
print(f"  最常見模式:")
for k, v in top:
    mark = "  ← 真" if k == share_pattern(TRUE) else ""
    print(f"    {k}: {v} 解{mark}")

# ================================================================
# [B] 對偶模式
# ================================================================
print("\n[B] 跨行對偶模式 (P_f(p)=N_d−n(q) 或 n(p)=P_f(q))")
print("-" * 60)
def dual_set(a):
    hits = set()
    for p in pkeys:
        for q in pkeys:
            if p == q: continue
            if abs(a[p][1] - (Nd - a[q][0])) < 1e-9: hits.add((p, q, "Pf=Nd-n"))
            if abs(a[p][0] - a[q][1]) < 1e-9: hits.add((p, q, "n=Pf"))
    return frozenset(hits)
dual_counter = Counter()
for a in all_assigns:
    dual_counter[dual_set(a)] += 1
admissible_d = {k: v for k, v in dual_counter.items() if k}
print(f"  容許的對偶集數 = {len(admissible_d)}")
print(f"  真網格對偶集 = {sorted(dual_set(TRUE))}")
print(f"  該集解數 = {admissible_d.get(dual_set(TRUE), 0)}")
topd = sorted(admissible_d.items(), key=lambda kv: -kv[1])[:5]
print(f"  最常見對偶集 (前 5):")
for k, v in topd:
    print(f"    {sorted(k)}: {v} 解")

# ================================================================
# [C] 行和 vs 結構常數
# ================================================================
print("\n[C] 家族行和 = 結構常數?")
print("-" * 60)
struct_vals = {"E_proj=28.5": 28.5, "N_d=44": 44.0, "M=33": 33.0, "Σγ=90": 90.0,
               "N_φ12=28": 28.0, "2E_proj=57": 57.0, "F₇=13": 13.0, "L₄=7": 7.0,
               "B²=16": 16.0, "L₆=18": 18.0, "N_d+L₄=51": 51.0, "F₉=34": 34.0}
for fam in ["L", "U", "D"]:
    mem = [p for p in pkeys if FAM[p] == fam]
    nsum = sum(TRUE[p][0] for p in mem)
    pfsum = sum(TRUE[p][1] for p in mem)
    hits_n = [k for k, v in struct_vals.items() if abs(nsum - v) < 1e-9]
    hits_pf = [k for k, v in struct_vals.items() if abs(pfsum - v) < 1e-9]
    print(f"  {fam}: n 和 = {nsum} {hits_n or '∅'};  P_f 和 = {pfsum} {hits_pf or '∅'}")

# 每行和的候選數 (解空間中)
print("\n  行和的解空間分佈 (L 行 n 和):")
lc = Counter(sum(a[p][0] for p in pkeys if FAM[p] == "L") for a in all_assigns)
for k, v in sorted(lc.items())[:12]:
    print(f"    L n-和 = {k}: {v} 解")

# ================================================================
# [D] 判決
# ================================================================
print("\n" + "=" * 76)
print("[D] 判決: 結構被迫性")
print("=" * 76)
n_share_adm = len(admissible)
n_dual_adm = len(admissible_d)
print(f"""
[A] 共享對: 210 種模式中, {n_share_adm} 種容許解 → 真模式是 1/{n_share_adm}
[B] 對偶: {n_dual_adm} 種對偶集容許解
[C] 行和: L n-和 = 28 = N_φ12 (解空間中有 {lc.get(28,0)} 解)

判決:
  若 admissible 模式數少 (<< 210) → 結構被質量數據強迫 (真結果)
  若 admissible 模式數接近 210 → 模式任意 (後驗)

  ★ 關鍵: 共享對「e↔s, μ↔u」等價於質量比陳述
     m_s/m_e ≈ γ₁₄/γ₁ (純拍頻比, 無投影因子)
     m_μ/m_u ≈ γ₇/γ₁
     這些是可測量的事實, 不是自由選擇 — 但只在 2.5% 窗內成立
""")

out = {
    "session": "2026-09-17 O144-13 forcedness",
    "share_patterns_total": len(patterns),
    "share_patterns_admissible": n_share_adm,
    "true_share_pattern": [list(t) for t in share_pattern(TRUE)],
    "true_share_pattern_solutions": admissible.get(share_pattern(TRUE), 0),
    "dual_sets_admissible": n_dual_adm,
    "true_dual_set": [list(t) for t in sorted(dual_set(TRUE))],
    "true_dual_solutions": admissible_d.get(dual_set(TRUE), 0),
    "row_sums": {fam: {"n": sum(TRUE[p][0] for p in pkeys if FAM[p] == fam),
                       "pf": sum(TRUE[p][1] for p in pkeys if FAM[p] == fam)}
                 for fam in ["L", "U", "D"]},
    "verdict": f"share patterns admissible {n_share_adm}/210; dual sets admissible {n_dual_adm}",
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/13_forcedness.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/13_forcedness.json 已寫入")
sys.exit(0)
