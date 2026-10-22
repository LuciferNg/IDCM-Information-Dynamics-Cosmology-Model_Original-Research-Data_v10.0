#!/usr/bin/env python3
"""
O147 — 公式層 φ 修正必要性掃描（6 個質量比）
==============================================
問題: O143 grid 對質量比 0.03-1.7% off. 邊啲需要 φ 修正?
修正分子 k = log(target/grid)/logφ×528 係咪全部結構數?

如果 k 全部係結構數 → 公式層隱含 φ 修正, gap 係「grid 缺修正項」
如果 k 唔結構 → 修正係後驗擬合, gap 係框架內張力
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d = 44
phi = (1 + math.sqrt(5)) / 2
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 10:123}
F = {3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55}

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2

# O143 grid (CSG-v2)
GRID = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "c":(34,13),
        "d":(1,33), "s":(14,3.6), "b":(33,44)}

# PDG current mass 比 (O143 目標)
PDG = {
    "mu/e":  206.768, "tau/e": 3477.2, "tau/mu": 16.82,
    "s/d":   20.0,    "c/u":   587.96, "b/d":    895.0,
    "b/s":   44.75,   "c/s":   13.6,   "t/b":    41.33,
}

pairs = [
    ("mu/e",  "mu", "e"), ("tau/e", "tau", "e"), ("tau/mu", "tau", "mu"),
    ("s/d",   "s",  "d"), ("c/u",   "c",  "u"), ("b/d",    "b",  "d"),
    ("b/s",   "b",  "s"), ("c/s",   "c",  "s"),
]

print("=" * 90)
print("  O147 — 公式層 φ 修正必要性掃描")
print("=" * 90)
print(f"\n  {'比':>7} | {'grid 值':>10} | {'PDG':>9} | {'裸 Δ%':>7} | {'k 需要':>7} | {'k 最近結構':>12} | 命中 Δ%")
print(f"  {'─'*7}-+-{'─'*10}-+-{'─'*9}-+-{'─'*7}-+-{'─'*7}-+-{'─'*12}-+-{'─'*10}")

# 結構數集合 (含分數)
struct_vals = {}
for k, v in L.items(): struct_vals[f"L_{k}"] = v
for k, v in F.items(): struct_vals[f"F_{k}"] = v
struct_vals.update({"N_gen":3, "B":4, "N_d":44, "M":33, "B×N_gen":12, "L₅+1":12,
                    "2N_gen":6, "N_d−L₄":37, "2N_d":88, "3N_d":132, "12N_d":528,
                    "n_u":10, "2n_u":20, "L₆−L₄":11, "L₇−F₆":21, "F₈":21,
                    "−B²":-16, "−2F₆":-16, "−2N_gen":-6, "−L₆":-18})

results = []
for name, a, b in pairs:
    n1, p1 = GRID[a]
    n2, p2 = GRID[b]
    grid_val = (gamma_n(n1)/gamma_n(n2)) * (p1/p2)
    tgt = PDG[name]
    dev = abs(grid_val - tgt)/tgt*100
    k = math.log(tgt/grid_val)/math.log(phi)*528
    # 最近結構數
    best, best_k = None, None
    for sname, sv in struct_vals.items():
        if abs(k - sv) < 2.0:
            if best is None or abs(k-sv) < abs(k-best_k):
                best, best_k = sname, sv
    if best:
        hit = grid_val * phi**(best_k/528)
        hit_dev = abs(hit - tgt)/tgt*100
        status = f"{best}={best_k} → Δ{hit_dev:.3f}%"
    else:
        hit, hit_dev = None, None
        status = "— (k 唔近結構數)"
    results.append((name, grid_val, tgt, dev, k, best, best_k, hit, hit_dev, status))
    print(f"  {name:>7} | {grid_val:10.4f} | {tgt:9.2f} | {dev:6.2f}% | {k:7.2f} | {status}")

print()
# ============ 分析 ============
print("─── 分析 1: 需要修正嘅比 (裸 Δ > 0.5%) ───")
need_fix = [r for r in results if r[3] > 0.5]
ok_nofix = [r for r in results if r[3] <= 0.5]
print(f"    需要修正: {[r[0] for r in need_fix]}")
print(f"    唔需要修正 (裸 Δ≤0.5%): {[r[0] for r in ok_nofix]}")
check("1 b/d, b/s, tau/mu 裸 Δ≤0.5% 唔需要修正", all(r[3] <= 0.5 for r in ok_nofix))

print("\n─── 分析 2: 修正分子 k 係咪結構數? ───")
k_struct = [r for r in results if r[5] is not None]
k_not = [r for r in results if r[5] is None and r[3] > 0.5]
print(f"    k 有結構數匹配: {[(r[0], f'{r[5]}={r[6]}', f'Δ{r[8]:.3f}%') for r in k_struct]}")
print(f"    k 冇結構數匹配 (且需要修正): {[(r[0], f'k={r[4]:.1f}') for r in k_not]}")
check("2 需要修正嘅比都有結構 k 匹配 (除 c/s?)", len(k_not) <= 1, f"unmatched={k_not}")

print("\n─── 分析 3: 修正分子規律 ───")
for r in k_struct:
    if r[3] > 0.5:
        print(f"    {r[0]:>7}: n={GRID[r[0].split('/')[0]][0]}, k={r[6]} ({r[5]})")

# 分子同 n 關係
print("\n─── 分析 4: k vs n (分子粒子) ───")
for r in k_struct:
    if r[3] > 0.5:
        num_name = r[0].split("/")[0]
        n_num = GRID[num_name][0]
        print(f"    {r[0]:>7}: n_{num_name} = {n_num}, k = {r[6]}, 差 = {r[6]-n_num:+d}")

print("\n─── 分析 5: 全部修正分子統一寫做 k/528 ───")
all_k528 = []
for r in results:
    if r[6] is not None and r[3] > 0.5:
        all_k528.append((r[0], r[6]))
    elif r[3] <= 0.5:
        all_k528.append((r[0], 0))
print(f"    {all_k528}")
k528_s = [k for _, k in all_k528 if k > 0]
print(f"    非零 k 集合: {k528_s}")
check("5 非零 k 全部係結構數 (L/F/常數)", all(k in struct_vals.values() for k in k528_s))

# ============ 總結 ============
print("\n" + "=" * 90)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 90)