#!/usr/bin/env python3
"""
O144-11 — 修正版刪除分析 + 殘餘解診斷 (2026-09-17)
====================================================
scripts/10 的 C4/C7 謂詞 bug:
  C4 錯寫 P_f(τ)=n(μ); 正確為 P_f(τ) = N_d − n(μ)  (跨行對偶)
  C7 只查 X 形式; 正確為 X 出現在 {X, N_d−X, (N_d−X)/2} 任一形式, 每家族恰好 2 次

目標: 修正後, 最小充分約束集能否唯一選出真網格?
      若否, 印出殘餘解 → 診斷殘餘自由度在哪
"""
import json, math, itertools, sys

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

sols = {}
for p, t in TARGET.items():
    seen, uniq = set(), []
    for n in MODES:
        for pk, pv in pool.items():
            if abs(M0 * gamma(n) * pv - t) / t < WINDOW and (n, round(pv, 4)) not in seen:
                seen.add((n, round(pv, 4))); uniq.append((n, round(pv, 4)))
    sols[p] = uniq
pkeys = list(sols.keys())
all_assigns = [{p: combo[i] for i, p in enumerate(pkeys)}
               for combo in itertools.product(*[sols[p] for p in pkeys])]

print("=" * 76)
print("O144-11 修正版刪除分析")
print("=" * 76)
print(f"基準 |S| = {len(all_assigns)}")

def C1(a):
    pr = list(a.values()); return len(set(pr)) == len(pr)
def C2(a):
    m = {}
    for p, (n, pv) in a.items(): m.setdefault(round(pv, 4), []).append(p)
    return sorted(tuple(sorted(v)) for v in m.values() if len(v) > 1) == sorted([("e","s"),("mu","u")])
def C3(a):
    for fam in ["L","U","D"]:
        mem = [p for p in a if FAM[p] == fam]
        if len(set(a[p][0] for p in mem)) != len(mem): return False
        if len(set(round(a[p][1],4) for p in mem)) != len(mem): return False
    return True
def C4(a):
    """跨行對偶: P_f(τ) = N_d − n(μ); n(b) = P_f(d) — 恰好這兩條"""
    hits = []
    for p in a:
        for q in a:
            if p == q: continue
            if abs(a[p][1] - (Nd - a[q][0])) < 1e-9: hits.append((p, q, "N_d-n"))
            if abs(a[p][0] - a[q][1]) < 1e-9: hits.append((p, q, "n=P_f"))
    return sorted(hits) == sorted([("tau","mu","N_d-n"), ("b","d","n=P_f")])
def C5(a): return abs(a["u"][1] + a["c"][1] - 28.5) < 1e-9
def C6(a): return abs(sum(a[p][0] for p in a if FAM[p]=="L") - 28) < 1e-9
def C7(a):
    """家族特徵常數 X 出現在 {X, N_d−X, (N_d−X)/2} 任一形式, 每家族恰好 2 次"""
    feats = {"L": 7.0, "U": 13.0, "D": 33.0}
    for fam, X in feats.items():
        mem = [p for p in a if FAM[p] == fam]
        cnt = 0
        for p in mem:
            for val in (a[p][0], a[p][1]):
                if abs(val - X) < 1e-9 or abs(val - (Nd - X)) < 1e-9 or abs(val - (Nd - X)/2) < 1e-9:
                    cnt += 1
        if cnt != 2: return False
    return True
def C8(a):
    for fam in ["L","U","D"]:
        mem = sorted([p for p in a if FAM[p]==fam], key=lambda p: GEN[p])
        ns = [a[p][0] for p in mem]
        if any(ns[i] >= ns[i+1] for i in range(len(ns)-1)): return False
    return True

CONSTRAINTS = [("C1 無重複對", C1), ("C2 P_f共享對", C2), ("C3 家族內互異", C3),
               ("C4 跨行對偶(修正)", C4), ("C5 U行和=28.5", C5), ("C6 L行n和=28", C6),
               ("C7 特徵常數×2(修正)", C7), ("C8 世代n遞增", C8)]
trueset = {p: TRUE[p] for p in pkeys}

print("\n[真網格檢驗]")
for name, fn in CONSTRAINTS:
    print(f"  {name:<22}: {'✅' if fn(trueset) else '❌'}")

print("\n[單條刪除力]")
for name, fn in CONSTRAINTS:
    n = sum(1 for a in all_assigns if fn(a))
    print(f"  {name:<22} 存活 {n:>6} (刪除率 {100*(1-n/len(all_assigns)):.2f}%)")

print("\n[最小充分子集搜尋]")
best = None
valid_c = [(nm, fn) for nm, fn in CONSTRAINTS if fn(trueset)]
for r in range(1, len(valid_c) + 1):
    found_any = False
    for subset in itertools.combinations(range(len(valid_c)), r):
        cnt = sum(1 for a in all_assigns if all(valid_c[i][1](a) for i in subset))
        if cnt == 0: continue
        found_any = True
        if best is None or cnt < best[0]:
            best = (cnt, [valid_c[i][0] for i in subset])
    print(f"  r={r}: 最小存活 {best[0] if best else '-'} ({best[1] if best else '-'})")
    if best and best[0] == 1:
        print(f"  ★ 找到唯一解: {best[1]}")
        break

# 殘餘解診斷
print("\n[殘餘解診斷]")
if best and best[0] <= 20:
    idxs = [i for i, (nm, fn) in enumerate(valid_c) if nm in best[1]]
    surv = [a for a in all_assigns if all(valid_c[i][1](a) for i in idxs)]
    print(f"  存活 {len(surv)} 個:")
    for a in surv[:12]:
        diff = {p: a[p] for p in pkeys if a[p] != TRUE[p]}
        print(f"    {diff}")

out = {"session": "2026-09-17 O144-11 corrected deletion",
       "baseline": len(all_assigns),
       "single_constraint_power": {nm: sum(1 for a in all_assigns if fn(a)) for nm, fn in CONSTRAINTS},
       "true_grid_passes": {nm: fn(trueset) for nm, fn in CONSTRAINTS},
       "min_sufficient": {"size": best[0] if best else None, "subset": best[1] if best else None},
       "verdict": "unique" if (best and best[0] == 1) else f"not unique (min {best[0] if best else '?'} survivors)"}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/11_corrected_deletion.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ data/11_corrected_deletion.json 已寫入")
sys.exit(0)
