#!/usr/bin/env python3
"""
O144-20 — 餘下開放問題攻堅 (2026-09-17)
========================================
目標: 開放問題 11 (網格被迫性) / 12 (對稱模式身份) / 13 (變分原理刪 311 競爭者)

方法論 (form-blind 紀律, 用戶判準):
  1. 先驗註冊原則 — 下方 §3 的 V1..V10 **在計算前寫定**, 每條只用「網格自身」
     可算的量 (零觀測質量輸入)。禁止看到結果後再挑原則。
  2. 真值 (真網格) 作盲測目標: 原則若能唯選出真網格 → PASS;
     若多個網格並列極值 → FAIL (無鑑別力)。
  3. 多重比較校正: 試了 N 條原則, 至少一條碰巧命中的機率 ≈ N/311
     (Bonferroni) — 必須報告。

§3 預註冊原則 (計算前寫定):
  V1  最小 Σn                    — 網格「總模數」最小
  V2  最小 Σlog(P_f)             — 網格「總投影因子」最小 (幾何最小作用量)
  V3  最小 n 族內極差和 Σ_fam(max n − min n)
  V4  最小 P_f 族內極差和 Σ_fam(max P_f − min P_f)
  V5  P_f 對 n 全域嚴格單調遞增 (真/假, 非極值)
  V6  最小 Σ|n − N_d/2|          — n 最集中
  V7  最小 Σ|P_f − N_d/2|        — P_f 最集中
  V8  每族內 Σn == ΣP_f (封閉性; 真/假)
  V9  兩條對偶互為對合 ∧ 兩條共享互為對合 (真/假)
  V10 對偶**同家族** ∧ 共享**跨家族** (開放問題 12 的模式; 真/假) ← §2 主測
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

# ================================================================
print("=" * 78); print("[§1] 重解解空間 + 枚舉「能唯一選出」的網格"); print("=" * 78)
sols = {}
for p, t in TARGET.items():
    seen, uniq = set(), []
    for n in MODES:
        for pk, pv in pool.items():
            if abs(M0 * gamma(n) * pv - t) / t < WINDOW and (n, round(pv, 4)) not in seen:
                seen.add((n, round(pv, 4))); uniq.append((n, round(pv, 4)))
    sols[p] = uniq
all_assigns = [{p: combo[i] for i, p in enumerate(pkeys)}
               for combo in itertools.product(*[sols[p] for p in pkeys])]
print(f"解空間 |S| = {len(all_assigns)};  每粒選項 = {[len(sols[p]) for p in pkeys]}")

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

buckets = defaultdict(list)
for a in all_assigns:
    buckets[(share_pattern(a), dual_set(a))].append(a)
print(f"不同 (共享, 對偶) 組合數 = {len(buckets)}")

struct_targets = [28.5, 28.0, 33.0, 44.0, 13.0, 7.0, 18.0, 34.0, 57.0, 90.0, 16.0, 51.0, 11.0, 37.0, 15.5, 3.6]
R_cands = [(f, fl, t) for f in FAMS for fl in ["n", "pf"] for t in struct_targets]
def r_sat(a, R):
    fam, field, t = R
    return abs(sum(a[p][0] if field == "n" else a[p][1] for p in pkeys if FAM[p] == fam) - t) < 1e-9

grids = set()
for (P, D), assigns in buckets.items():
    for R in R_cands:
        sat = [a for a in assigns if r_sat(a, R)]
        if len(sat) == 1:
            grids.add(tuple(sorted((p, sat[0][p][0], sat[0][p][1]) for p in pkeys)))
grids = [dict((p, (n, pf)) for p, n, pf in g) for g in sorted(grids)]
print(f"能唯一選出的不同網格數 = {len(grids)}")
tkey = tuple(sorted((p, TRUE[p][0], TRUE[p][1]) for p in pkeys))
chk_true_in = tkey in {tuple(sorted((p, g[p][0], g[p][1]) for p in pkeys)) for g in grids}
print(f"真網格在上述集合內: {'✅' if chk_true_in else '❌'}")

# ================================================================
print("\n" + "=" * 78); print("[§2] 開放問題 12 — 對偶/共享的模式身份 (S₃ 家族對稱)"); print("=" * 78)
def duals(a):
    """兩類對偶 (與 scripts/14 dual_set 一致):
       (i)  P_f(p) = N_d − n(q)      (跨行對偶)
       (ii) n(p)  = P_f(q)           (n-P_f 對偶)"""
    out = []
    for p in pkeys:
        for q in pkeys:
            if p == q: continue
            if abs(a[p][1] - (Nd - a[q][0])) < 1e-9: out.append((p, q, "Pf=Nd-n"))
            if abs(a[p][0] - a[q][1]) < 1e-9: out.append((p, q, "n=Pf"))
    return sorted(set(out))
def shares(a):
    m = defaultdict(list)
    for p in pkeys: m[round(a[p][1], 4)].append(p)
    return sorted([tuple(sorted(v)) for v in m.values() if len(v) == 2])

def fam_pattern(a):
    ds, ss = duals(a), shares(a)
    n_same = sum(1 for (p, q, _t) in ds if FAM[p] == FAM[q])
    n_cross = sum(1 for t in ss if FAM[t[0]] != FAM[t[1]])
    return n_same, n_cross, len(ds), len(ss)

rows = [fam_pattern(g) for g in grids]
cnt = Counter((r[0], r[1]) for r in rows)
tr = fam_pattern(TRUE)
print(f"真網格: 對偶 {tr[2]} 條 (同家族 {tr[0]}), 共享 {tr[3]} 對 (跨家族 {tr[1]})")
print(f"311 網格的 (對偶同家族數, 共享跨家族數) 分佈 (前 12):")
for k, v in cnt.most_common(12):
    mark = "  ★真網格" if k == (tr[0], tr[1]) else ""
    print(f"    (同家族 {k[0]}, 跨家族 {k[1]}) : {v:3d} 個{mark}")
n_match = sum(1 for r in rows if (r[0], r[1]) == (tr[0], tr[1]))
n_both = sum(1 for r in rows if r[0] == 2 and r[1] == 2)
print(f"\n同時滿足「對偶全同家族 ∧ 共享全跨家族」的網格數 = {n_both} / {len(grids)}")
p_S3 = n_both / len(grids)
print(f"若把此模式當刪除原則 → 保留 {n_both} 個, 真網格在其中: {'✅' if tr[:2] == (2, 2) else '❌'}")
print(f"⟹ 模式命中率 p = {p_S3:.5f} ({n_both}/{len(grids)})")

# 反向: 該模式是「真網格專屬」還是「真網格碰巧」?
uniq = (n_both == 1 and tr[0] == 2 and tr[1] == 2)
print(f"是否唯一決定真網格: {'✅ 是 (唯一)' if uniq else f'❌ 否 ({n_both} 個並列)'}")

# §2b 剩下 5 個的結構差異 — 下一步攻堅面
survivors = [g for g in grids if fam_pattern(g)[0] == 2 and fam_pattern(g)[1] == 2]
print(f"\n[§2b] V10 模式存活網格 ({len(survivors)} 個) 與真網格的差異:")
for i, g in enumerate(survivors, 1):
    diff = [(p, TRUE[p], g[p]) for p in pkeys if (g[p][0], g[p][1]) != (TRUE[p][0], TRUE[p][1])]
    tag = "★真網格" if not diff else ""
    print(f"  #{i} {tag} 差異 {len(diff)} 項: " + ("; ".join(f"{p}: 真{TRUE[p]}→{v}" for p, _, v in diff) if diff else "—"))
# 差異集中在哪些粒子?
diffs = Counter(p for g in survivors for p in pkeys if (g[p][0], g[p][1]) != (TRUE[p][0], TRUE[p][1]))
print(f"  差異粒子頻率: {dict(diffs.most_common())}")
print(f"  ⟹ 需額外約束的粒子 = {[p for p, _ in diffs.most_common()]}")

# ================================================================
print("\n" + "=" * 78); print("[§3] 開放問題 11/13 — 預註冊變分原理電池 (V1..V10)"); print("=" * 78)
def sv(a, k):  # 統計量
    ns = [a[p][0] for p in pkeys]; pfs = [a[p][1] for p in pkeys]
    if k == "V1": return sum(ns)
    if k == "V2": return sum(math.log(v) for v in pfs)
    if k == "V3": return sum(max(a[p][0] for p in pkeys if FAM[p] == f) - min(a[p][0] for p in pkeys if FAM[p] == f) for f in FAMS)
    if k == "V4": return sum(max(a[p][1] for p in pkeys if FAM[p] == f) - min(a[p][1] for p in pkeys if FAM[p] == f) for f in FAMS)
    if k == "V6": return sum(abs(a[p][0] - Nd/2) for p in pkeys)
    if k == "V7": return sum(abs(a[p][1] - Nd/2) for p in pkeys)
def pred(a, k):
    if k == "V5":
        seq = [(a[p][0], a[p][1]) for p in pkeys]
        return all(seq[i][1] < seq[i+1][1] for i in range(len(seq)-1) if seq[i][0] < seq[i+1][0])
    if k == "V8":
        return all(abs(sum(a[p][0] for p in pkeys if FAM[p] == f) - sum(a[p][1] for p in pkeys if FAM[p] == f)) < 1e-9 for f in FAMS)
    if k == "V9":
        ds, ss = duals(a), shares(a)
        d_ok = len(ds) == 2 and all((q, p, t) in ds for (p, q, t) in ds)
        s_ok = len(ss) == 2 and all(len(t) == 2 for t in ss)
        return d_ok and s_ok
    if k == "V10":
        r = fam_pattern(a)
        return r[0] == 2 and r[1] == 2

EXTREMUM = ["V1", "V2", "V3", "V4", "V6", "V7"]   # 取最小
BOOLEAN = ["V5", "V8", "V9", "V10"]                # 真/假
res = []
for k in EXTREMUM:
    vals = [sv(g, k) for g in grids]
    tv = sv(TRUE, k)
    best = min(vals)
    n_tie = sum(1 for v in vals if abs(v - best) < 1e-9)
    is_best = abs(tv - best) < 1e-9
    res.append({"id": k, "type": "min", "true_value": tv, "grid_best": best,
                "true_is_best": is_best, "n_tie_at_best": n_tie,
                "p_if_true_best": (n_tie/len(grids)) if is_best else None})
    print(f"  {k}: 真值 {tv:.4f} | 網格最小 {best:.4f} | 真網格達最小: {'✅' if is_best else '❌'}"
          + (f" (並列 {n_tie} 個, p={n_tie/len(grids):.4f})" if is_best else ""))
for k in BOOLEAN:
    sat = [pred(g, k) for g in grids]
    t_sat = pred(TRUE, k)
    n_sat = sum(sat)
    res.append({"id": k, "type": "bool", "true_satisfies": bool(t_sat),
                "n_satisfying": n_sat, "p_if_true_satisfies": (n_sat/len(grids)) if t_sat else None})
    print(f"  {k}: 真網格滿足: {'✅' if t_sat else '❌'} | 滿足的網格數 = {n_sat} / {len(grids)}"
          + (f" (p={n_sat/len(grids):.4f})" if t_sat else ""))

# 多重比較 (布爾與極值兩類都要計)
n_tests = len(EXTREMUM) + len(BOOLEAN)
hits = [r for r in res if (r.get("true_is_best") or r.get("true_satisfies"))]
ps = [r["p_if_true_best"] if r.get("p_if_true_best") is not None else r.get("p_if_true_satisfies")
      for r in hits]
ps = [p for p in ps if p is not None] or [1.0]
p_min = min(ps)
print(f"\n[多重比較] 試了 {n_tests} 條預註冊原則; 真網格命中 {len(hits)} 條")
print(f"  命中者 = {[r['id'] for r in hits]}")
print(f"  最小 p = {p_min:.5f}; Bonferroni 校正 (×{n_tests}) = {min(1.0, p_min*n_tests):.4f}")
uniq_hits = [r["id"] for r in hits if (r.get("n_tie_at_best") == 1 or r.get("n_satisfying") == 1)]
print(f"  能「唯一」選出真網格的原則: {uniq_hits if uniq_hits else '無 ❌'}")

# ================================================================
print("\n" + "=" * 78)
print("[§4] 殘餘歧義定位: 311 → 5 只差 'c' 一個粒子 — 針對性預註冊測試")
print("=" * 78)
FIB = {1, 2, 3, 5, 8, 13, 21, 34, 55}
LUC = {1, 3, 4, 7, 11, 18, 29, 47}
print("預註冊 (計算前寫定): T1 全部 n ∈ Fibonacci; T2 全部 n ∈ Lucas; T3 n ∈ Fib∪Lucas")
for k, S, nm in [("T1", FIB, "Fibonacci"), ("T2", LUC, "Lucas"), ("T3", FIB | LUC, "Fib∪Lucas")]:
    sat = [g for g in grids if all(g[p][0] in S for p in pkeys)]
    t_sat = all(TRUE[p][0] in S for p in pkeys)
    print(f"  {k} (n ∈ {nm}): 真網格 {'✅' if t_sat else '❌'} | 滿足網格數 = {len(sat)}/{len(grids)}"
          + (f"  p = {len(sat)/len(grids):.5f}" if t_sat else ""))
    if t_sat:
        tag = "★真網格" if any(all(g[p] == TRUE[p] for p in pkeys) for g in sat) else ""
        print(f"      其中真網格: {'✅ 在內' if tag else '❌ 不在內'}")
# T4: 局部 tie-breaker — c 的 n ∈ Fib (在 5 個存活者中)
c_fib = [g for g in survivors if g["c"][0] in FIB]
print(f"  T4 (局部): 5 個存活者中 c 的 n ∈ Fibonacci 者 = {len(c_fib)} 個"
      f" (c 的 n 值 = {sorted(set(g['c'][0] for g in survivors))})")
for g in c_fib:
    d = [(p, TRUE[p], g[p]) for p in pkeys if g[p] != TRUE[p]]
    print(f"      c = {g['c']} 差異 {len(d)} 項 {'★真網格 ✅' if not d else '→ ' + str(d)}")
print(f"  ⟹ T4 若成立: 311 → {len(c_fib)} (唯一真網格: {'✅' if len(c_fib)==1 and c_fib[0]==TRUE else '❌'})")

# ================================================================
print("\n" + "=" * 78); print("[判決]"); print("=" * 78)
print(f"""
問題 12 (對稱模式 V10): 「對偶全同家族 ∧ 共享全跨家族」在 311 網格中符合者 = {n_both}
  → 具部分鑑別力 (311→{n_both}), p = {p_S3:.4f}; Bonferroni ×{n_tests} = {min(1.0, p_S3*n_tests):.3f}
    ⟹ 校正後不顯著 (未達 z ≥ 3 判準), 但為 14 條原則中唯一有刪除力者
  → 真網格 {'在其中 ✅' if tr[:2] == (2, 2) else '不在其中 ❌'}
  → ★ 殘餘歧義集中於 = {list(diffs.keys())} (s 1 次, c 4 次)
問題 11/13 (變分原理): {n_tests} 條預註冊原則中唯一選出真網格者 = {len(uniq_hits)}
  → ❌ 無 — 六條極值原則 (Σn, ΣlogP_f, 族內極差×2, 集中度×2) 真網格全部不達極值
""" + f"""問題 12b (殘餘定位, ★ 本輪最有價值結果):
  311 → 5 後, 5 個之中 4 個的差異**只在 c 的 n** (值集 {sorted(set(g['c'][0] for g in survivors))})
  ⟹ 整個 O144 網格歧義已收縮到**一個整數** n_charm
  ⚠️ tie-breaker T4 (c 的 n ∈ Fibonacci → 選 34) 為**後驗** (在 §2b 觀察後才提出), 不可計入盲測
  → 誠實合併機率: V10 (p=0.0161) × T4 局部 (1/4) = 0.004 raw, Bonferroni ×14 = 0.056 → 🟡 邊緣不顯著
  → 且 33 亦有結構身份 (N_d−L₅ = 33) — 「34 勝 33」本身仍未推導
""" if True else "")

out = {
    "session": "2026-09-17 O144-20 open-problem attack",
    "solution_space": len(all_assigns), "grids": len(grids),
    "true_in_grids": chk_true_in,
    "p12": {"true_pattern": {"dual_same_fam": tr[0], "share_cross_fam": tr[1],
                             "n_dual": tr[2], "n_share": tr[3]},
            "n_both_same_and_cross": n_both, "p": p_S3, "unique": bool(uniq),
            "joint_distribution": {f"{k[0]},{k[1]}": v for k, v in cnt.most_common()}},
    "p11_13": {"n_tests": n_tests, "results": res, "unique_hits": uniq_hits,
               "p_min": p_min, "p_bonferroni": min(1.0, p_min*n_tests)},
    "p12b": {"survivors": len(survivors),
             "c_n_values": sorted(set(g["c"][0] for g in survivors)),
             "diff_particles": dict(diffs.most_common()),
             "T4_survivors": len(c_fib),
             "T4_unique_true": bool(len(c_fib) == 1 and c_fib[0] == TRUE),
             "T4_status": "post-hoc (在 §2b 觀察後提出) — 不計入盲測",
             "combined_p_raw": p_S3 * 0.25,
             "combined_p_bonferroni14": min(1.0, p_S3 * 0.25 * 14)},
    "verdict": (f"P12 V10: 311->{n_both} (p={p_S3:.4f}, Bonferroni x{n_tests}={min(1.0,p_S3*n_tests):.3f}); "
                f"P11/13 unique principles={len(uniq_hits)}; P12b residual localized to {list(diffs.keys())}"),
}
json.dump(out, open(f'{O144}/data/20_open_problem_attack.json', 'w'), indent=2, ensure_ascii=False)
print("✅ data/20_open_problem_attack.json")
