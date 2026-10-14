#!/usr/bin/env python3
"""
O144-21 — 未測先驗攻堅: 「一代基本模」約束 (2026-09-17)
=========================================================
動機 (非後驗): CSG-v2 `docs/02_x_construction_rule.md` §3 的 16 約束集包含
  【約束 2】一代基本模 n_e = n_u = n_d = 1  (3 條)
該文檔日期 2026-09-04 — **早於** O144 的被迫性攻擊 (2026-09-17)。
O144 scripts/09-16 只用了 C2 (共享對) + C4 (對偶) + C5 (U 行和),
**從未使用約束 2**; CSG-v2 scripts/17 亦未測。
故本輪 = 測試唯一未測的上游預註冊先驗。

先驗內容 (零觀測質量輸入):
  P1  n(e) = n(u) = n(d) = 1
      理由: n=0 是零模 (Goldstone, 被 W/Z 吃掉 — O144 玻色子身份);
            故 n=1 = 鏈首個物理模 = 基本模; 第一代 = 最低激發。
  P2  n(s) = 2·n(μ)      (CSG-v2 docs/02 §4 LOOCV 表)
  P3  n(τ) = n(μ)+n(s)−1 (CSG-v2 docs/02 §4 LOOCV 表)

測試:
  §1 基準重現 (6468 / 439 桶 / 311 網格)
  §2 P1 過濾後 |S'| + 311 中有多少滿足 P1
  §3 **重跑被迫性 on S'** — 若 P1 是真先驗, 311 應崩塌
  §4 P1 + V10 組合 → 殘餘 n_charm
  §5 P2 / P3 測試
  §6 判決 + Bonferroni
"""
import json, math, itertools, sys
from collections import Counter, defaultdict

M0 = 27.9009; Nd = 44
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O144 = f'{BASE}/open_problems_fresh/o144_boson_identity'

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
FAMS = ["L", "U", "D"]
WINDOW = 0.025
pkeys = list(TRUE.keys())
tkey = tuple(sorted((p, TRUE[p][0], TRUE[p][1]) for p in pkeys))

def gkey(g): return tuple(sorted((p, g[p][0], g[p][1]) for p in pkeys))

# ================================================================
print("=" * 78); print("[§1] 基準重現"); print("=" * 78)
sols = {}
for p, t in TARGET.items():
    seen, uniq = set(), []
    for n in MODES:
        for pk, pv in pool.items():
            if abs(M0 * gamma(n) * pv - t) / t < WINDOW and (n, round(pv, 4)) not in seen:
                seen.add((n, round(pv, 4))); uniq.append((n, round(pv, 4)))
    sols[p] = uniq
print(f"|S| 每粒選項 = {dict(zip(pkeys, [len(sols[p]) for p in pkeys]))}")
ALL = [{p: combo[i] for i, p in enumerate(pkeys)} for combo in itertools.product(*[sols[p] for p in pkeys])]
print(f"解空間 |S| = {len(ALL)}")

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
struct_targets = [28.5, 28.0, 33.0, 44.0, 13.0, 7.0, 18.0, 34.0, 57.0, 90.0, 16.0, 51.0, 11.0, 37.0, 15.5, 3.6]
R_cands = [(f, fl, t) for f in FAMS for fl in ["n", "pf"] for t in struct_targets]
def r_sat(a, R):
    fam, field, t = R
    return abs(sum(a[p][0] if field == "n" else a[p][1] for p in pkeys if FAM[p] == fam) - t) < 1e-9

def forcedness(assigns, label):
    """在給定解空間上重跑完整被迫性枚舉 → (桶數, 唯一三元組數, 不同網格集)"""
    buckets = defaultdict(list)
    for a in assigns:
        buckets[(share_pattern(a), dual_set(a))].append(a)
    grids = set(); ntriples = 0
    for (P, D), asg in buckets.items():
        for R in R_cands:
            sat = [a for a in asg if r_sat(a, R)]
            if len(sat) == 1:
                ntriples += 1
                grids.add(gkey(sat[0]))
    print(f"  [{label}] |S|={len(assigns)} → 桶 {len(buckets)} → 唯一三元組 {ntriples} → 不同網格 {len(grids)}")
    return buckets, ntriples, grids

buckets0, triples0, grids0 = forcedness(ALL, "基準")
print(f"真網格在內: {'✅' if tkey in grids0 else '❌'}")

# ================================================================
print("\n" + "=" * 78); print("[§2] P1: 一代基本模 n(e)=n(u)=n(d)=1"); print("=" * 78)
def gen1_ok(a): return a["e"][0] == 1 and a["u"][0] == 1 and a["d"][0] == 1
S1 = [a for a in ALL if gen1_ok(a)]
print(f"|S'| = {len(S1)}  (壓縮 {len(ALL)/max(1,len(S1)):.2f}×)")
print(f"真網格滿足 P1: {'✅' if gen1_ok(TRUE) else '❌'}")
g0 = [dict((p, (n, pf)) for p, n, pf in g) for g in grids0]
n_p1 = sum(1 for g in g0 if gen1_ok(g))
print(f"311 網格中滿足 P1 者 = {n_p1}  (p = {n_p1/max(1,len(grids0)):.4f})")
print(f"  ⟹ P1 對 311 的刪除力: {len(grids0)} → {n_p1}")
# u / d 在 S 中的 n 分佈
print(f"  u 的 n 值 = {sorted(set(a['u'][0] for a in ALL))}; d 的 n 值 = {sorted(set(a['d'][0] for a in ALL))}")

# ================================================================
print("\n" + "=" * 78); print("[§3] ★ 重跑被迫性 on S' (P1 作為基準先驗)"); print("=" * 78)
buckets1, triples1, grids1 = forcedness(S1, "P1")
print(f"真網格在內: {'✅' if tkey in grids1 else '❌'}")
red = len(grids0) / max(1, len(grids1))
print(f"\n★ 核心數字: 基準 311 → P1 後 {len(grids1)}  (壓縮 {red:.1f}×)")
if len(grids1) == 1 and tkey in grids1:
    print("  ⟹ ⟹ P1 令「唯一解」變成真網格專屬! ✅✅")
elif tkey in grids1:
    print(f"  ⟹ P1 大幅壓縮但未到唯一 ({len(grids1)} 個並列, 真網格在其中)")

# ================================================================
print("\n" + "=" * 78); print("[§4] P1 + V10 (對偶全同家族 ∧ 共享全跨家族)"); print("=" * 78)
def fam_pattern(a):
    ds = dual_set(a)
    n_same = sum(1 for (p, q, _t) in ds if FAM[p] == FAM[q])
    ss = [t for t in share_pattern(a) if len(t) == 2]
    n_cross = sum(1 for t in ss if FAM[t[0]] != FAM[t[1]])
    return n_same, n_cross, len(ds), len(ss)
G1 = [dict((p, (n, pf)) for p, n, pf in g) for g in grids1]
V10 = [g for g in G1 if fam_pattern(g)[0] == 2 and fam_pattern(g)[1] == 2]
print(f"P1 後網格 {len(G1)} → 滿足 V10 者 {len(V10)}")
print(f"真網格在內: {'✅' if any(gkey(g) == tkey for g in V10) else '❌'}")
if V10:
    cvals = sorted(set(g["c"][0] for g in V10))
    print(f"  n_charm 候選 = {cvals}   (基準時為 {{25,27,33,34}})")
    for i, g in enumerate(V10, 1):
        d = [(p, TRUE[p], g[p]) for p in pkeys if g[p] != TRUE[p]]
        print(f"    #{i} {'★真網格' if not d else f'差異 {len(d)}: ' + str(d)}")
# P1 + V10 對 311 的總壓縮
V10_on_311 = [g for g in g0 if fam_pattern(g)[0] == 2 and fam_pattern(g)[1] == 2]
P1V10_on_311 = [g for g in V10_on_311 if gen1_ok(g)]
print(f"\n在原始 311 上: V10 → {len(V10_on_311)}; V10 ∧ P1 → {len(P1V10_on_311)}")
print(f"  n_charm ∈ {sorted(set(g['c'][0] for g in P1V10_on_311)) if P1V10_on_311 else '—'}")

# ================================================================
print("\n" + "=" * 78); print("[§5] P2 / P3 (CSG-v2 docs/02 §4 的 n-關係)"); print("=" * 78)
P2 = lambda a: abs(a["s"][0] - 2 * a["mu"][0]) < 1e-9
P3 = lambda a: abs(a["tau"][0] - (a["mu"][0] + a["s"][0] - 1)) < 1e-9
for nm, fn, desc in [("P2", P2, "n(s) = 2·n(μ)"), ("P3", P3, "n(τ) = n(μ)+n(s)−1")]:
    t_ok = fn(TRUE)
    n_g0 = sum(1 for g in g0 if fn(g))
    n_g1 = sum(1 for g in G1 if fn(g))
    n_g1v = sum(1 for g in V10 if fn(g))
    print(f"  {nm} [{desc}]: 真網格 {'✅' if t_ok else '❌'} | 311 中 {n_g0} | P1 後 {n_g1} | P1+V10 後 {n_g1v}")
    if t_ok:
        print(f"      p(311) = {n_g0/len(g0):.4f}; p(P1) = {n_g1/max(1,len(G1)):.4f}")
# 組合 P1 ∧ P2 ∧ P3 ∧ V10
combo = [g for g in V10 if P2(g) and P3(g)]
print(f"\n  P1 ∧ V10 ∧ P2 ∧ P3 → {len(combo)} 個"
      + (f"; n_charm = {sorted(set(g['c'][0] for g in combo))}" if combo else ""))
print(f"  真網格在內: {'✅' if any(gkey(g) == tkey for g in combo) else '❌'}")

# ================================================================
print("\n" + "=" * 78); print("[判決 + Bonferroni]"); print("=" * 78)
# 預註冊先驗數 (P1, P2, P3) + V10 → 4 條
tests = 4
surv_final = combo if combo else V10
n_fin = len(surv_final)
p_raw = n_fin / len(grids0) if len(grids0) else 1.0
print(f"""
P1 (一代基本模)   : |S| {len(ALL)} → {len(S1)};  311 → {n_p1}
P1 重跑被迫性     : 311 → {len(grids1)}  (壓縮 {red:.1f}×)  {'★ 唯一真網格' if len(grids1)==1 else ''}
P1 + V10          : → {len(V10)} 個;  n_charm ∈ {sorted(set(g['c'][0] for g in V10)) if V10 else '—'}
P1+V10+P2+P3      : → {n_fin} 個;  n_charm ∈ {sorted(set(g['c'][0] for g in surv_final)) if surv_final else '—'}

合併刪除力: 311 → {n_fin}
raw p = {p_raw:.5f};  Bonferroni ×{tests} = {min(1.0, p_raw*tests):.4f}
""")
verdict = ("UNIQUE" if n_fin == 1 and any(gkey(g) == tkey for g in surv_final) else
           f"RESIDUAL_{n_fin}")
print(f"判決: {verdict}")

out = {
    "session": "2026-09-17 O144-21 gen1 fundamental mode prior",
    "base": {"S": len(ALL), "buckets": len(buckets0), "triples": triples0, "grids": len(grids0)},
    "P1": {"S_prime": len(S1), "grids_311_satisfying": n_p1,
           "grids_after_P1": len(grids1), "compression": red,
           "true_satisfies": bool(gen1_ok(TRUE))},
    "P1_V10": {"n": len(V10), "n_charm": sorted(set(g["c"][0] for g in V10)) if V10 else []},
    "P1_V10_P2_P3": {"n": n_fin, "n_charm": sorted(set(g["c"][0] for g in surv_final)) if surv_final else [],
                     "true_in": bool(any(gkey(g) == tkey for g in surv_final))},
    "p_raw": p_raw, "bonferroni_x4": min(1.0, p_raw * tests),
    "verdict": verdict,
}
json.dump(out, open(f'{O144}/data/21_gen1_fundamental_mode.json', 'w'), indent=2, ensure_ascii=False)
print("✅ data/21_gen1_fundamental_mode.json")
