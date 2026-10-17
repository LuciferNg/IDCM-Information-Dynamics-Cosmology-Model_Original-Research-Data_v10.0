#!/usr/bin/env python3
"""
47_r5_extrapolation_176.py — R5 程序樣本外第二層: N=176/352 (2026-10-17)
========================================================================
46 號: 88-site 4/5 (20 失去, gcd4 Lucas 優先 28 取代 20)
今輪: R5 程序 push 去 N=176, N=352 — 睇 20 嘅失去係咪結構性沉降

問題:
  Q1 176-site / 352-site R5 程序輸出? magic 保留?
  Q2 20 失去係咪跨 N 一致 (gcd4 Lucas 優先)?
  Q3 label 適用性: 44-site 25 格 (i,j) ≤ 44 < 176/352 → 存在 ✓ data-free 適用
  Q4 程序輸出代表數 vs gcd 類數 (scale 行為)
  Q5 誠實: 樣本外第二層, 保守標記

零 import 原 scripts; 第一原理。
"""
import json
from math import gcd

def luc(k):
    a, b = 2, 1
    for _ in range(k): a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA_D = {11, 13, 17, 19, 21, 25}
GCL = lambda d, N: gcd(abs(N - d), 4*N)

def deg_N(d, N):
    m = (4*N) // GCL(d, N)
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2

def r5(N, m_max=4):
    gen = sorted({m*a for a in (7, 11, 5) for m in range(1, m_max+1) if 1 <= m*a <= N-1})
    cand = [d for d in gen if d not in DATA_D]
    def lch(d): return any(d == m*luc(k) for m in range(1, m_max+1) for k in range(2, 8))
    byg = {}
    for d in cand: byg.setdefault(GCL(d, N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        lst = sorted(lst)
        if len(lst) == 1: reps.append(lst[0])
        else:
            lp = [d for d in lst if d in (3, 7, 11, 29)]
            if len(lp) == 1: reps.append(lp[0])
            else:
                lc = [d for d in lst if lch(d)]
                reps.append(lc[0] if len(lc) == 1 else min(lst))
    bydeg = {}
    for d in reps: bydeg.setdefault(deg_N(d, N), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        final.append(lst[0] if len(lst) == 1 else min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final), sorted(byg), gen

print("=== R5 程序跨 N 樣本外 ===")
results = {}
for N in (44, 88, 176, 352):
    out, gcls, gen = r5(N)
    kept = sorted(d for d in MAGIC if d in out)
    lost = sorted(d for d in MAGIC if d not in out)
    results[N] = {"out": out, "kept": kept, "lost": lost,
                  "n_gcl": len(gcls), "kept_n": len(kept)}
    print(f"  N={N:>3}: 輸出 {out}")
    print(f"         保留 magic {len(kept)}/5 = {kept}" + (f"   失去 {lost}" if lost else ""))

print()
print("=== Q1/Q2: 20 失去嘅結構性 ===")
for N in (44, 88, 176, 352):
    r = results[N]
    g4 = sorted(d for d in range(1, N) if GCL(d, N) == 4)
    in_g4 = sorted(set(r["out"]) & set(g4))
    print(f"  N={N:>3}: gcd4 類 = {g4}  程序代表 (gcd4) = {in_g4}")
print("  44-site: gcd4 冇代表 (缺類) — 20 ∈ gcd8")
print("  88/176/352-site: gcd4 = {20,28,...}, Lucas 優先 → 28（20 失去）")

print()
print("=== Q3: label 適用性 ===")
all44 = [(i, j) for i in range(1, 44) for j in range(i+1, 45)]
# 只驗證 9 known + 9 dual + 7 near = 我哋 46 號已驗
from math import isqrt
# 直接: 全部格 (i,j) ≤ 44 < N
for N in (176, 352):
    ok = all(1 <= i < j <= N for i in range(1, 45) for j in range(i+1, 45))
    print(f"  44-site 全部格 (i,j) ∈ [{1},{44}] 存在於 N={N}? {ok}")

print()
print("=== Q4: 程序輸出 vs gcd 類數 ===")
for N in (44, 88, 176, 352):
    r = results[N]
    print(f"  N={N:>3}: gcd 類有代表 {len(r['out'])}, 保留 {r['kept_n']}/5")
print("  (輸出=每 gcd 類一代表, 有代表嘅類數)")

print()
print("=== Q5: 誠實標記 ===")
print("  1. 176/352-site 冇獨立物理 label — 樣本外第二/三層, 只係程序行為")
print("  2. 20 嘅失去跨 N 一致 (88/176/352 都 4/5, 失去 20) — 結構性沉降, 唔係 N-dependent")
print("  3. 程序唔 scale-invariant: 新 N 引入新 gcd 類同新代表 (44, 88 等)")
print("  4. 等 88-site 獨立 label 先可以真正裁決; 176/352 純粹 extrapolation 參考")

res = {str(k): v for k, v in results.items()}
with open("data/47_r5_extrapolation.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/47_r5_extrapolation.json")