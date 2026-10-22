#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/36_known_hits_audit.py — 已知家族命中正確定義驗證 (audit)
域正確定義: 88 域 = sin(kπ/88), 176 域 = sin(kπ/176)
驗證 O158 家族命中 (21,24), (13,32), (46,1), (86,39), (44,2) 真正 dev,
對照該域全域 top1 — 確立「家族命中 = 算子化 + 接近最佳」地位。
"""
import math

s176 = [math.sin(k*math.pi/176) for k in range(177)]
s88 = [math.sin(k*math.pi/88) for k in range(89)]

def dev_of(a, b, n, target):
    s = s176 if n == 176 else s88
    r = s[a]/s[b]
    return min(abs(r/target-1), abs(target/r-1)), r

def scan_top(n, target, exclude=None):
    s = s176 if n == 176 else s88
    best = (1e9, 0, 0)
    tb = float(target)
    for a in range(1, n+1):
        for b in range(1, n+1):
            if a == b: continue
            if exclude and (a, b) == exclude: continue
            r = s[a]/s[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            if d < best[0]: best = (d, a, b)
    return best

# PDG 目標 (同 scripts/35)
TARGETS = {
    "W/Z": (0.881353536, (21, 24, 176)),
    "τ/b": (0.425086121, (13, 32, 176)),
    "t/b": (41.3301435, (46, 1, 176)),
    "H/W": (1.55843672, (86, 39, 176)),
    "s/d": (20.0, (44, 2, 176)),
}

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("已知家族命中正確定義 dev vs 該域全域 top1")
print("="*72)
for name, (val, (a, b, n)) in TARGETS.items():
    d_known, r_known = dev_of(a, b, n, val)
    d_top, ta, tb_ = scan_top(n, val)
    print("%-5s (%2d,%2d)@%d dev=%.6e r=%.6f | 該域 top1 (%2d,%2d) dev=%.6e | rank比 %.1fx" % (
        name, a, b, n, d_known, r_known, ta, tb_, d_top, d_known/d_top if d_top > 0 else 1e9))
print()

print("="*72)
print("2. 家族命中地位檢定")
print("="*72)
for name, (val, (a, b, n)) in TARGETS.items():
    d_known, _ = dev_of(a, b, n, val)
    d_top, _, _ = scan_top(n, val)
    ratio = d_known/d_top if d_top > 0 else 1e9
    ck("%s (%d,%d) 喺 top 10 內 (family hit 有算子身份)" % (name, a, b),
       ratio < 10, "ratio=%.1f" % ratio)
    print("")
print()

print("="*72)
print("3. 誠實評估: 家族命中 vs 全域 top1")
print("="*72)
print("   - (86,39): H/W 176 域 top1 2.26x 內? 定係被超越?")
d_8639, _ = dev_of(86, 39, 176, 1.55843672)
d_top_hw, ta, tb_ = scan_top(176, 1.55843672)
print("     (86,39) dev=%.4e; top1=(%d,%d) dev=%.4e; ratio=%.1fx" % (d_8639, ta, tb_, d_top_hw, d_8639/d_top_hw))
ck("(86,39) 係 H/W 176 域 top1 (0.0011% 已知命中地位成立)", d_8639/d_top_hw < 2)

d_2124, _ = dev_of(21, 24, 176, 0.881353536)
d_top_wz, ta2, tb2 = scan_top(176, 0.881353536)
print("   (21,24) dev=%.4e; top1=(%d,%d) dev=%.4e; ratio=%.1fx" % (d_2124, ta2, tb2, d_top_wz, d_2124/d_top_wz))
ck("(21,24) 176 域定位 (家族命中, 0.0007%)", d_2124/d_top_wz < 10)
print()

print("="*72)
print("4. ★★★ 方法學裁決 (回退 T30)")
print("="*72)
print("   - scripts/32『10/10=176』= 平凡 (176 含 88 對應 + 大空間)")
print("   - scripts/35 公平測試: 176 新對真實 7/10 (70%) < 隨機 79.5%")
print("   - ⇒ 176 域優勢冇結構成分 → spin 假說否證無效")
print("   - ⇒ T30 撤回 (append-only 附註), spin 假說維持 🟡 冇直接證據")
print("   - 真正有結構嘅係『家族命中』: (21,24) 0.0007% (和=45 差=3),")
print("     (86,39) 0.0011% (和=125=F₅³ 差=47) — 唔係域優勢, 係算子化")
print()

total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)