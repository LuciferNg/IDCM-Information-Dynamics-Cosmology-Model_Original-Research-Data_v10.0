#!/usr/bin/env python3
"""
O48 Q1.50: 谷距身份搜尋 — k=[10,11,9,7] 對應後峰 m={2,3,5,7}
================================================================
任務: 搵一條結構式 k(m) 同時命中 4 點:
  m=2 → k=10, m=3 → k=11, m=5 → k=9, m=7 → k=7
候選: 算子字典 {F_n, L_n, γ=297/6, 峰週期 297, 306, 288, N_d=44, 88,
  45=N_d+1, 90, 55=F₁₀, 個位…} 嘅簡單組合 (a op b, a±b, a×b 分數)。

判據: 同一式命中 4/4 = 唯一候選 (唔可以逐個配唔同式)。
另: 谷→後峰 [90,99,81,63] = 9×k 亦一齊列。
"""
import math, sys, itertools
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))

# ---------- 算子池 ----------
OPS = {}
for n in range(0, 13):
    OPS[f"F{n}"] = F(n); OPS[f"L{n}"] = L(n)
for name, v in [("Nd",44), ("2Nd",88), ("Nd1",45), ("B",4), ("Ngen",3),
                ("peak_period",297), ("gap306",306), ("gap288",288),
                ("gamma495",49.5), ("303",303), ("90",90), ("99",99),
                ("81",81), ("63",63), ("55",55), ("phi5",round(phi**5)),
                ("phi4",round(phi**4)), ("phi2",round(phi**2)), ("7",7),
                ("9",9), ("10",10), ("11",11), ("12",12), ("15",15),
                ("18",18), ("21",21), ("25",25), ("27",27), ("33",33),
                ("34",34), ("32",32), ("36",36), ("31",31)]:
    OPS[name] = v

# ---------- 簡單式生成 (a op b) ----------
def gen_expressions(targets, ops_pool, allow_div=True, allow_frac=False):
    names = sorted(ops_pool)
    res = {}
    for a in names:
        va = ops_pool[a]
        for b in names:
            vb = ops_pool[b]
            if a == b and abs(va) > 50: continue
            cands = []
            cands.append((va+vb, f"{a}+{b}"))
            cands.append((va-vb, f"{a}-{b}"))
            if va != 0 and vb != 0 and (allow_div or abs(va/vb - round(va/vb)) < 1e-9):
                cands.append((va/vb, f"{a}/{b}"))
            if allow_frac and vb != 0:
                cands.append((va/vb, f"{a}/{b}"))
            for v, expr in cands:
                if abs(v) < 1e-9: continue
                for t in targets:
                    if abs(v - t) < 1e-9:
                        res.setdefault(t, []).append(expr)
    return res

# ---------- 目標 ----------
k_targets = {2: 10, 3: 11, 5: 9, 7: 7}
g_targets = {2: 90, 3: 99, 5: 81, 7: 63}   # 谷→後峰直接距離

print("="*72)
print("A. 單步式 k(m) — 用 m 直接生成")
print("="*72)
# 先試簡單線性: k = round(a - m*b)?
for a in range(0, 40):
    for b in range(0, 8):
        ok = all(abs((a - m*b) - k) < 1e-9 for m, k in k_targets.items())
        if ok: print(f"  k = {a} − {b}·m  4/4 ✓")
for a in range(0, 40):
    for b in range(0, 8):
        ok = all(abs((a + m*b) - k) < 1e-9 for m, k in k_targets.items())
        if ok: print(f"  k = {a} + {b}·m  4/4 ✓")
# 比例: k = A/m?
for a in range(1, 120):
    ok = all(abs(a/m - k) < 1e-9 for m, k in k_targets.items())
    if ok: print(f"  k = {a}/m  4/4 ✓")

print("="*72)
print("B. 峰間隙分數: 谷→後峰/間隙")
print("="*72)
# 間隙: m=2 → 峰221-527 gap 306; m=3 → 527-815 gap 288; m=5 → 815-1121 gap 306; m=7 → 1121-1409 gap 288
gaps = {2: 306, 3: 288, 5: 306, 7: 288}
fracs = {m: g_targets[m]/gaps[m] for m in k_targets}
for m in k_targets:
    print(f"  m={m}: 谷→後峰 {g_targets[m]} / 間隙 {gaps[m]} = {fracs[m]:.4f}")
# 睇分數結構
for m in k_targets:
    fr = fracs[m]
    # 最接近 1/x
    cand = min(range(1, 30), key=lambda x: abs(fr - 1/x))
    if abs(fr - 1/cand) < 0.01:
        print(f"  m={m}: ≈ 1/{cand} (dev {fr-1/cand:+.4f})")

print("="*72)
print("C. k 值唔同式 (逐點, 只做診斷)")
print("="*72)
exp_10 = gen_expressions([10], OPS)
exp_11 = gen_expressions([11], OPS)
exp_9 = gen_expressions([9], OPS)
exp_7 = gen_expressions([7], OPS)
print("  10 候選:", exp_10.get(10, [])[:12])
print("  11 候選:", exp_11.get(11, [])[:12])
print("   9 候選:", exp_9.get(9, [])[:12])
print("   7 候選:", exp_7.get(7, [])[:12])

print("="*72)
print("D. 谷→後峰 [90,99,81,63] 嘅算子式")
print("="*72)
exp_90 = gen_expressions([90], OPS)
exp_99 = gen_expressions([99], OPS)
exp_81 = gen_expressions([81], OPS)
exp_63 = gen_expressions([63], OPS)
print("  90 候選:", exp_90.get(90, [])[:10])
print("  99 候選:", exp_99.get(99, [])[:10])
print("  81 候選:", exp_81.get(81, [])[:10])
print("  63 候選:", exp_63.get(63, [])[:10])

# 交叉: 同一表達式結構命中全部 4 個谷→後峰?
print("="*72)
print("E. 同一算子 pair 命中全部 4 個谷→後峰?")
print("="*72)
G4 = [90, 99, 81, 63]
names = sorted(OPS)
hits = []
for a in names:
    va = OPS[a]
    for b in names:
        vb = OPS[b]
        for expr, fun, label in [(va+vb, lambda x,y: x+y, "+"),
                                 (va-vb, lambda x,y: x-y, "-"),
                                 (va/vb if vb != 0 else None, lambda x,y: x/y, "/")]:
            if expr is None: continue
            if abs(expr) < 1e-9: continue
            if all(abs(expr - t) < 1e-9 for t in G4):
                hits.append(f"{a}{label}{b}={expr}")
print("  同時命中 90/99/81/63:", hits[:10] if hits else "無")
# 同埋谷距 [279,324,306]
print("  谷距 [279,324,306] 同時命中:")
G3 = [279, 324, 306]
hits3 = []
for a in names:
    va = OPS[a]
    for b in names:
        vb = OPS[b]
        for expr, label in [(va+vb, "+"), (va-vb, "-")]:
            if abs(expr) < 1e-9: continue
            if all(abs(expr - t) < 1e-9 for t in G3):
                hits3.append(f"{a}{label}{b}={expr}")
print("  ", hits3[:10] if hits3 else "無")

print("="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)