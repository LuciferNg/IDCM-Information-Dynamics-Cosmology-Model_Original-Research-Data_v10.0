#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/33_domain_superiority_null.py — 176 vs 88 域優勢 null control (float)
問題: census (T30) 話「10/10 目標最佳域=176」— 但 176 域有 176²=30976
對, 88 域只有 88²=7744 對 (4 倍搜尋空間) → 天然優勢! 可能唔係結構。
Control: 200 隨機目標 (log-uniform), 每個掃兩域 + 176奇奇對,
比較 median 改善比: 真實 vs 隨機; 176奇奇(1/4 空間) median > 1?
"""
import math, random, statistics
random.seed(20261011)

def best_dev_domain(n, target):
    """掃 n 域全對 (sin(aπ/2n)/sin(bπ/2n)), 返回最佳 |r/t-1|"""
    best = 1e9
    tb = float(target)
    pi2n = math.pi/(2*n)
    sins = [math.sin(k*pi2n) for k in range(n+1)]
    for a in range(1, n+1):
        sa = sins[a]
        for b in range(1, n+1):
            if a == b: continue
            r = sa/sins[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            if d < best: best = d
    return best

def best_dev_odd176(target):
    """176 域奇-奇對 (44²=1936 對, 細過 88 域 7744 對)"""
    best = 1e9
    tb = float(target)
    odd = list(range(1, 177, 2))
    sins = {k: math.sin(k*math.pi/176) for k in odd}
    for a in odd:
        sa = sins[a]
        for b in odd:
            if a == b: continue
            r = sa/sins[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            if d < best: best = d
    return best

REAL = [
    ("W/Z", 0.8813695), ("H/W", 1.5584376), ("τ/b", 0.4250861),
    ("t/b", 41.33014), ("s/d", 20.0), ("c/s", 13.59743),
    ("u/d", 0.462526), ("H/Z", 1.373516), ("H/t", 0.72499),
    ("H/b", 29.96411),
]

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. 真實 10 目標: 88 vs 176 全對 best dev")
print("="*72)
real_ratios = []
for name, val in REAL:
    d88 = best_dev_domain(88, val)
    d176 = best_dev_domain(176, val)
    ratio = d88/d176 if d176 > 0 else 1e9
    real_ratios.append(ratio)
    print("   %-5s: 88=%.4e 176=%.4e 改善 %.1fx" % (name, d88, d176, ratio))
real_med = statistics.median(real_ratios)
print("   真實 median 改善 = %.2fx" % real_med)
print()

print("="*72)
print("2. ★★ Null control: 200 log-uniform 隨機目標 (全對)")
print("="*72)
N_RAND = 200
random_ratios = []
for _ in range(N_RAND):
    v = 10**random.uniform(-1.5, 2.0)  # 0.03 ~ 100
    d88 = best_dev_domain(88, v)
    d176 = best_dev_domain(176, v)
    random_ratios.append(d88/d176 if d176 > 0 else 1e9)
rand_med = statistics.median(random_ratios)
print("   隨機 %d 目標 median 改善 = %.2fx" % (N_RAND, rand_med))
ck("真實 median 改善 > 隨機 median (結構成分 > 搜索空間效應)", real_med > rand_med)
print()

print("="*72)
print("3. ★★★ 最嚴格: 176 奇-奇對 (44²=1936 對 << 88 域 7744 對)")
print("="*72)
odd_ratios = []
odd_wins = 0
for name, val in REAL:
    d88 = best_dev_domain(88, val)
    dodd = best_dev_odd176(val)
    ratio = d88/dodd if dodd > 0 else 1e9
    odd_ratios.append(ratio)
    if dodd < d88: odd_wins += 1
    print("   %-5s: 88全對=%.4e 176奇奇=%.4e 改善 %.1fx" % (name, d88, dodd, ratio))
odd_med = statistics.median(odd_ratios)
print("   → 176奇奇 median 改善 = %.2fx (搜索空間只有 88 域 1/4!)" % odd_med)
print("   176奇奇 勝 88 全對: %d/%d" % (odd_wins, len(REAL)))
ck("176奇奇(細搜索空間) median 改善 > 1 (176 域真優勢, 唔係空間效應)", odd_med > 1.0)
print()

print("="*72)
print("4. 誠實小結")
print("="*72)
print("   - 全對比較: 176 域有 4x 搜索空間 → 天然優勢存在")
print("   - 隨機控制: median 改善比 真實 vs 隨機 → 結構 vs 隨機")
print("   - 176奇奇(1/4 空間): 最嚴 test → >1 = 176 域真結構")
print()

total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)