#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/35_domain_advantage_fair.py — ★★★ 176 vs 88 域公平測試 (修正版)
scripts/32「10/10 最佳域=176」係平凡: 176 域含 88 域所有對應 (a,b)→(2a,2b)
scripts/33/34 域定義 bug (sin(iπ/2n) 錯尺度) → 作廢
正確問題: 176 域「真正新對」(至少一個 index 奇數) 有冇對真實目標提供
比 88 域全對更好嘅命中? 呢個先係「176 域額外預測力」。
正確定義: 88 域 = sin(kπ/88), 176 域 = sin(kπ/176)
"""
import math, random, statistics

def sins_domain(n):
    return [math.sin(k*math.pi/n) for k in range(n+1)]

def scan_all(n, target, sins):
    """全對掃 n 域, 返回 top5 [(dev, a, b)]"""
    hits = []
    tb = float(target)
    for a in range(1, n+1):
        sa = sins[a]
        for b in range(1, n+1):
            if a == b: continue
            r = sa/sins[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            hits.append((d, a, b))
    hits.sort(key=lambda x: x[0])
    return hits[:5]

def scan_odd_touch(n, target, sins):
    """176 域真正新對: 至少一個 index 奇數 (唔係 (2a,2b) 對應)"""
    hits = []
    tb = float(target)
    for a in range(1, n+1):
        sa = sins[a]
        for b in range(1, n+1):
            if a == b: continue
            if a % 2 == 0 and b % 2 == 0:
                continue  # 呢啲係 88 域對應,排除
            r = sa/sins[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            hits.append((d, a, b))
    hits.sort(key=lambda x: x[0])
    return hits[:5]

REAL = [
    ("W/Z", 0.88135354, 1), ("H/W", 1.55843672, 0), ("τ/b", 0.42508612, 0.5),
    ("t/b", 41.3301435, 0.5), ("s/d", 20.0, 0.5), ("c/s", 13.59743, 0.5),
    ("u/d", 0.4625257, 0.5), ("H/Z", 1.3735082, 0), ("H/t", 0.7250005, 0),
    ("H/b", 29.964115, 0),
]

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. 真實目標: 88 域全對 best vs 176 域『新對』(含奇) best")
print("="*72)
s88 = sins_domain(88)
s176 = sins_domain(176)
print("%-5s %-4s | %-24s | %-24s | 新對勝?" % ("tgt", "spin", "88域全對 top1", "176域新對 top1"))
improve_count = 0
for name, val, spin in REAL:
    h88 = scan_all(88, val, s88)[0]
    hnew = scan_odd_touch(176, val, s176)[0]
    ratio = h88[0]/hnew[0] if hnew[0] > 0 else float('inf')
    win = "✓" if hnew[0] < h88[0] else "✗"
    if hnew[0] < h88[0]: improve_count += 1
    print("%-5s %-4s | (%3d,%3d) dev %.2e | (%3d,%3d) dev %.2e | %s (%.1fx)" % (
        name, spin, h88[1], h88[2], h88[0], hnew[1], hnew[2], hnew[0], win, ratio if win else 0))
print()
print("   176 新對超越 88 全對: %d/%d" % (improve_count, len(REAL)))
print()

print("="*72)
print("2. ★★ 已知命中對位置: (21,24) 等等係咪仲係 top?")
print("="*72)
for name, val, spin in REAL:
    h88 = scan_all(88, val, s88)[0]
    print("   %-5s 88域 top1 = (%d,%d) dev=%.2e" % (name, h88[1], h88[2], h88[0]))
print()

print("="*72)
print("3. Null: 200 隨機目標, P(176新對勝過 88全對)")
print("="*72)
random.seed(20261011)
random_win = 0
N_RAND = 200
for _ in range(N_RAND):
    v = 10**random.uniform(-1.5, 2.0)
    h88 = scan_all(88, v, s88)[0]
    hnew = scan_odd_touch(176, v, s176)[0]
    if hnew[0] < h88[0]: random_win += 1
print("   隨機 %d 目標: 176新對勝 %d (%.1f%%)" % (N_RAND, random_win, 100*random_win/N_RAND))
ck("真實 176 新對勝率 > 隨機 176 新對勝率 (結構優勢)", improve_count/len(REAL) > random_win/N_RAND)
print()

print("="*72)
print("4. 誠實裁定")
print("="*72)
print("   - scripts/32 嘅『10/10 = 176』係平凡 (176 含 88 對應 + 4x 空間)")
print("   - 公平測試: 176 真正新對 (含奇 index) vs 88 全對")
print("   - 如果真實目標勝率高過隨機 → 176 域有真額外預測力")
print("   - 如果≈隨機 → 176 域優勢只係搜索空間, spin 假說否證無效")
print()

total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)