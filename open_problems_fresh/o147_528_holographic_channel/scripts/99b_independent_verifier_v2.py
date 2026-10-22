#!/usr/bin/env python3
"""
O147 — 99b_independent_verifier_v2: κ 可加性獨立核對（由原始定義重算）
========================================================================
唔 import o147 任何 scripts。由原始定義:
  γ_n = 4sin²(nπ/88), φ = (1+√5)/2, Lucas Lₙ, Fibonacci Fₙ
  5 種子結構數: κ(d)=0, κ(s)=L₆=18, κ(b)=Z₂=2, κ(e)=κ(μ)=L₄/2=3.5, κ(τ)=N_gen²=9
  2 生成規則: κ(U)=κ(D)−B², κ(μ)=κ(e)
重算 κ 表 + 驗證 21 個比 (grid × φ^(κ差/528) vs PDG)。
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

# ============ 原始定義 ============
N_d = 44
B = 4
N_gen = 3
phi = (1 + math.sqrt(5)) / 2
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
F = {5:5, 6:8, 7:13, 8:21, 9:34}

def gamma_n(n): return 4 * math.sin(n * math.pi / (2*N_d)) ** 2

# ============ κ 表由種子 + 規則生成 (唔 hardcode) ============
K = {}
K["d"] = 0.0                                  # 基準
K["s"] = float(L[6])                          # 種子 L₆ = 18
K["b"] = float(B//2)                          # 種子 Z₂ = 2  (= B/2)
K["e"] = float(L[4]) / 2                      # 種子 L₄/2 = 3.5
K["mu"] = K["e"]                              # 規則 κ(μ)=κ(e)
K["tau"] = float(N_gen**2)                    # 種子 N_gen² = 9
K["u"] = K["d"] - B*B                         # 規則 κ(U)=κ(D)−B²
K["c"] = K["s"] - B*B                         # 規則 κ(U)=κ(D)−B²
K["t"] = K["b"] - B*B                         # 規則 (gen3 預測)

print("=" * 100)
print("  O147 — 99b 獨立核對: κ 可加性由原始定義重算")
print("=" * 100)

print("\n─── κ 表生成 (種子 + 規則, 零 hardcode) ───")
expected = {"e":3.5, "mu":3.5, "tau":9.0, "d":0.0, "s":18.0, "b":2.0, "c":2.0, "u":-16.0, "t":-14.0}
for p in ["e","mu","tau","d","s","b","c","u","t"]:
    ok = abs(K[p] - expected[p]) < 1e-9
    check(f"κ({p}) = {K[p]:+5.1f}", ok)
    print(f"    κ({p}) = {K[p]:+5.1f}  {'✅' if ok else '🔴'}")

# ============ O143 grid ============
GRID = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "c":(34,13),
        "d":(1,33), "s":(14,3.6), "b":(33,44)}

# PDG (O143 target, 同 docs/07)
PDG = {
    "mu/e":  206.768, "tau/e": 3477.2, "tau/mu": 16.82,
    "s/d":   20.0,    "c/u":   587.96, "b/d":    895.0,
    "b/s":   44.75,   "c/s":   13.6,
    "c/d":   1270/4.67, "b/u": 4180/2.16, "mu/s": 105.66/93.4,
    "tau/d": 1776.86/4.67, "tau/s": 1776.86/93.4, "s/u": 93.4/2.16,
    "mu/d":  105.66/4.67, "mu/u": 105.66/2.16, "tau/c": 1776.86/1270,
    "tau/u": 1776.86/2.16, "b/c": 4180/1270, "c/e": 1270/0.511,
    "b/e":   4180/0.511,
}
pairs = [
    ("mu/e","mu","e"), ("tau/e","tau","e"), ("tau/mu","tau","mu"),
    ("s/d","s","d"), ("c/u","c","u"), ("b/d","b","d"),
    ("b/s","b","s"), ("c/s","c","s"),
    ("c/d","c","d"), ("b/u","b","u"), ("mu/s","mu","s"),
    ("tau/d","tau","d"), ("tau/s","tau","s"), ("s/u","s","u"),
    ("mu/d","mu","d"), ("mu/u","mu","u"), ("tau/c","tau","c"),
    ("tau/u","tau","u"), ("b/c","b","c"), ("c/e","c","e"),
    ("b/e","b","e"),
]

print("\n─── 21 比: grid × φ^(κ差/528) vs PDG (獨立重算) ───")
print(f"  {'比':>7} | {'修正後值':>11} | {'PDG':>10} | {'Δ%':>8} | 判定")
print(f"  {'─'*7}-+-{'─'*11}-+-{'─'*10}-+-{'─'*8}-+-{'─'*6}")
all_dev = []
for name, a, b in pairs:
    n1, p1 = GRID[a]; n2, p2 = GRID[b]
    grid_val = (gamma_n(n1)/gamma_n(n2)) * (p1/p2)
    corr = grid_val * phi**((K[a]-K[b])/528)
    dev = abs(corr - PDG[name])/PDG[name]*100
    all_dev.append(dev)
    hit = dev < 1.0
    print(f"  {name:>7} | {corr:11.4f} | {PDG[name]:10.2f} | {dev:7.3f}% | {'✅' if hit else '🔴'}")

avg = sum(all_dev)/len(all_dev)
print(f"\n  平均 Δ% = {avg:.4f}%, 最大 = {max(all_dev):.4f}%")
check("21 比全部 Δ% < 1%", max(all_dev) < 1.0, f"max={max(all_dev):.4f}%")
check("平均 Δ% < 0.1%", avg < 0.1, f"{avg:.4f}%")

# ============ 結構規則獨立驗證 ============
print("\n─── 結構規則 (由生成值驗證, 非 hardcode) ───")
check("行: κ(u)−κ(d) = −B²", K["u"]-K["d"] == -B*B)
check("行: κ(c)−κ(s) = −B²", K["c"]-K["s"] == -B*B)
check("行: κ(t)−κ(b) = −B²", K["t"]-K["b"] == -B*B)
check("列: κ(s)−κ(d) = L₆", K["s"]-K["d"] == L[6])
check("列: κ(c)−κ(u) = L₆", K["c"]-K["u"] == L[6])
check("列: κ(b)−κ(s) = −B²", K["b"]-K["s"] == -B*B)
check("列: κ(τ)−κ(μ) = L₅/2", abs(K["tau"]-K["mu"] - L[5]/2) < 1e-9)
check("跨行: κ(s) = 2κ(τ)", K["s"] == 2*K["tau"])
check("共享: κ(e)=κ(μ), κ(b)=κ(c)", K["e"]==K["mu"] and K["b"]==K["c"])

# ============ 階梯獨立驗證 ============
print("\n─── 階梯 N_d × {Z₂, N_gen, B·N_gen} (獨立驗證) ───")
check("88  = N_d × Z₂", 88 == N_d*B//2)
check("132 = N_d × N_gen", 132 == N_d*N_gen)
check("528 = N_d × B×N_gen", 528 == N_d*B*N_gen)
sum_gamma_odd = sum(gamma_n(k) for k in range(1, 88, 2))
check("Σγ_odd = 88 = 2N_d", abs(sum_gamma_odd - 88) < 1e-9)

# ============ 總結 ============
print("\n" + "=" * 100)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 100)
