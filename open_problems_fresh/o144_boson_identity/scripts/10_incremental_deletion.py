#!/usr/bin/env python3
"""
O144-10 — 增量刪除分析: 哪條先驗約束把 369 → 1? (2026-09-17)
==============================================================
基準: scripts/09 的 6468 解空間 (窗 2.5%, 39 反週期模式 × 16 值嚴格池)
真網格: e(1,3.6) μ(7,15.5) τ(20,37) u(1,15.5) d(1,33) s(14,3.6) c(34,13) b(33,44)

約束 (逐條施加, 記錄存活數):
  C1 無重複對
  C2 P_f 共享對恰好 {(e,s),(μ,u)}
  C3 家族內 n 互異 + P_f 互異
  C4 跨行對偶恰好 {(τ,μ), (b,d)} (P_f(p)=n(q))
  C5 U 行和 P_f(u)+P_f(c) = E_proj = 28.5
  C6 L 行和 n = 28 = N_φ12 (新發現)
  C7 家族特徵常數出現恰好兩次 (S₃ 單射)
  C8 世代 n 遞增 (同家族 n 隨世代遞增)

判決: 全部施加後 = 1 (真網格) → 先驗約束集完整但需逐條先驗性審查
       > 1 → 仍不唯一
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
print("=" * 76)
print("O144-10 增量刪除分析")
print("=" * 76)
print(f"解空間: { {p: len(sols[p]) for p in pkeys} }")
base = 1
for p in pkeys:
    base *= len(sols[p])
print(f"基準 |S| = {base}")

# 全枚舉
all_assigns = []
for combo in itertools.product(*[sols[p] for p in pkeys]):
    all_assigns.append({p: combo[i] for i, p in enumerate(pkeys)})
print(f"枚舉: {len(all_assigns)}")

def C1(a):
    pr = list(a.values()); return len(set(pr)) == len(pr)
def C2(a):
    m = {}
    for p, (n, pv) in a.items(): m.setdefault(round(pv, 4), []).append(p)
    sh = sorted(tuple(sorted(v)) for v in m.values() if len(v) > 1)
    return sh == sorted([("e", "s"), ("mu", "u")])
def C3(a):
    for fam in ["L", "U", "D"]:
        mem = [p for p in a if FAM[p] == fam]
        if len(set(a[p][0] for p in mem)) != len(mem): return False
        if len(set(round(a[p][1], 4) for p in mem)) != len(mem): return False
    return True
def C4(a):
    pairs = sorted((p, q) for p in a for q in a if p != q and abs(a[p][1] - a[q][0]) < 1e-6)
    return pairs == sorted([("tau", "mu"), ("b", "d")])
def C5(a):
    return abs(a["u"][1] + a["c"][1] - 28.5) < 1e-9
def C6(a):
    return abs(sum(a[p][0] for p in a if FAM[p] == "L") - 28) < 1e-9
def C7(a):
    # 每家族特徵常數出現恰好兩次: L→7, U→13, D→33 (在 n 或 P_f 中)
    feats = {"L": 7.0, "U": 13.0, "D": 33.0}
    for fam, X in feats.items():
        mem = [p for p in a if FAM[p] == fam]
        cnt = sum(1 for p in mem if abs(a[p][0] - X) < 1e-9 or abs(a[p][1] - X) < 1e-9)
        if cnt != 2: return False
    return True
def C8(a):
    for fam in ["L", "U", "D"]:
        mem = sorted([p for p in a if FAM[p] == fam], key=lambda p: GEN[p])
        ns = [a[p][0] for p in mem]
        if any(ns[i] >= ns[i+1] for i in range(len(ns)-1)): return False
    return True

CONSTRAINTS = [("C1 無重複對", C1), ("C2 P_f共享對={(e,s),(μ,u)}", C2),
               ("C3 家族內互異", C3), ("C4 跨行對偶={(τ,μ),(b,d)}", C4),
               ("C5 U行和=28.5", C5), ("C6 L行n和=28", C6),
               ("C7 特徵常數×2", C7), ("C8 世代n遞增", C8)]

print("\n" + "=" * 76)
print("逐條施加 (累積)")
print("=" * 76)
cur = all_assigns
applied = []
for name, fn in CONSTRAINTS:
    nxt = [a for a in cur if fn(a)]
    trueset = {p: TRUE[p] for p in pkeys}
    ts = fn(trueset)
    print(f"  + {name:<26} → {len(nxt):>6} 存活  (真網格: {'✅' if ts else '❌'})")
    if ts:
        cur = nxt; applied.append(name)
    else:
        print(f"     ⚠️ 真網格不滿足 — 該約束與真網格衝突, 跳過")
print(f"\n累積後存活 = {len(cur)} (施加 {len(applied)} 條)")
trueset = {p: TRUE[p] for p in pkeys}
print(f"真網格在存活集內: {'✅' if trueset in cur else '❌'}")

# 哪些單條最有刪除力
print("\n" + "=" * 76)
print("單條刪除力排名")
print("=" * 76)
for name, fn in CONSTRAINTS:
    n = sum(1 for a in all_assigns if fn(a))
    print(f"  {name:<26} 存活 {n:>6} (刪除率 {100*(1-n/len(all_assigns)):.2f}%)")

# 最小充分集
print("\n" + "=" * 76)
print("最小充分子集搜尋 (真網格存活 + 存活數最少)")
print("=" * 76)
best = None
for r in range(1, len(CONSTRAINTS) + 1):
    for subset in itertools.combinations(range(len(CONSTRAINTS)), r):
        if any(not CONSTRAINTS[i][1](trueset) for i in subset):
            continue
        cnt = sum(1 for a in all_assigns if all(CONSTRAINTS[i][1](a) for i in subset))
        if best is None or cnt < best[0]:
            best = (cnt, [CONSTRAINTS[i][0] for i in subset])
    if best and best[0] == 1:
        break
if best:
    print(f"  最小存活 {best[0]} 由 {best[1]}")
else:
    print("  無子集能唯一選出真網格")

out = {"session": "2026-09-17 O144-10 incremental deletion",
       "baseline": base, "survivors_after_all": len(cur), "applied": applied,
       "true_grid_unique": best[0] == 1 if best else False,
       "min_sufficient": best[1] if best else None,
       "verdict": ("unique" if (best and best[0] == 1) else "not unique")}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/10_incremental_deletion.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ data/10_incremental_deletion.json 已寫入")
sys.exit(0)
