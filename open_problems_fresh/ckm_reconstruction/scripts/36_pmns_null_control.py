#!/usr/bin/env python3
"""36 — PMNS beat 公式 null-control + D6/S6 成員資格
問題: pmns_beat_search_corrected 嘅「PMNS 4/4 ✅」係窮舉搜尋 (946² 對, err<1e-5 best-match)。
     搜尋到嘅 hit 係咪結構? 定係密度巧合? 對照: 隨機 target 有幾多都會搵到 err<1e-5 對?
同時: PMNS 對嘅 (d,s) 有幾多喺 D6/S6 (c2 跨驗證)?
"""
import math, random

N_d = 44
ω = [2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)]
def beat(i, j):
    return abs(ω[i-1] - ω[j-1])

# 預先計好所有 946 對 (i<j)
pairs = [(i, j) for i in range(1, N_d+1) for j in range(i+1, N_d+1)]
bvals = {p: beat(*p) for p in pairs}
bval_list = sorted(bvals.values())

print("=== 1) 重現 PMNS 搜尋結果 (驗證) ===")
pmns_targets = {
    "tan θ12 33.41": math.tan(math.radians(33.41)),
    "sin θ12 33.41": math.sin(math.radians(33.41)),
    "tan θ23 42.2 ": math.tan(math.radians(42.2)),
    "tan θ23 49.0 ": math.tan(math.radians(49.0)),
    "sin θ23 42.2 ": math.sin(math.radians(42.2)),
    "sin θ23 49.0 ": math.sin(math.radians(49.0)),
    "tan θ13 8.54": math.tan(math.radians(8.54)),
    "sin θ13 8.54": math.sin(math.radians(8.54)),
}
def best_ratio(target):
    best, be = None, float('inf')
    for p1, b1 in bvals.items():
        if b1 < 1e-12: continue
        for p2, b2 in bvals.items():
            if b2 < 1e-12: continue
            e = abs(b1/b2 - target)
            if e < be: be, best = e, (p1, p2, b1/b2)
    return best, be

for name, t in pmns_targets.items():
    (p1, p2, r), e = best_ratio(t)
    print(f"  {name}: beat{p1}/beat{p2} = {r:.10f} (err={e:.2e})")

print("\n=== 2) NULL-CONTROL: 隨機 target 都有 err<1e-5 hit? ===")
random.seed(42)
hit = 0
N = 100
for _ in range(N):
    t = random.uniform(0.1, 1.2)  # tan 範圍 (PMNS 目標所在區間)
    (p1, p2, r), e = best_ratio(t)
    if e < 1e-5:
        hit += 1
print(f"tan 區間 [0.1,1.2]: {hit}/{N} 隨機 target 搵到 err<1e-5 對 ({hit/N*100:.0f}%)")

hit = 0
for _ in range(N):
    t = random.uniform(0.14, 0.76)  # sin 範圍
    (p1, p2, r), e = best_ratio(t)
    if e < 1e-5:
        hit += 1
print(f"sin 區間 [0.14,0.76]: {hit}/{N} 隨機 target 搵到 err<1e-5 對 ({hit/N*100:.0f}%)")

# 特定 target 嘅 hit 多重度: 同一個 target 有幾多對喺 3.41e-6 內?
t = math.tan(math.radians(33.41))
cnt = sum(1 for b1 in bval_list for b2 in bval_list if b2 > 0 and abs(b1/b2 - t) < 3.41e-6)
print(f"\ntan θ12 嘅 err<3.41e-6 對數: {cnt} (PMNS 文件嗰對係咪唯一?)")

print("\n=== 3) PMNS 對嘅 (d,s) vs D6/S6 成員資格 ===")
D6 = {1, 2, 6, 9, 19, 21}
S6 = {11, 25, 41, 44, 68, 85}
pmns_pairs = [
    ("tan θ12", (4,13), (9,25)),
    ("sin θ12", (16,31), (8,33)),
    ("tan θ23 42.2", (11,23), (12,26)),
    ("tan θ23 49", (4,14), (22,44)),
    ("sin θ23 42.2", (13,24), (16,43)),
    ("sin θ23 49", (11,35), (7,42)),
    ("tan θ13", (28,30), (3,10)),
    ("sin θ13", (25,29), (3,20)),
]
inD6 = inS6 = tot = 0
for name, p1, p2 in pmns_pairs:
    for p in (p1, p2):
        d, s = abs(p[0]-p[1]), p[0]+p[1]
        tot += 1
        m1 = "D6✓" if d in D6 else ""
        m2 = "S6✓" if s in S6 else ""
        inD6 += d in D6; inS6 += s in S6
        print(f"  {name:>12} beat{p}: d={d:2d} {m1:4s} s={s:2d} {m2}")
print(f"\nD6 成員: {inD6}/{tot}, S6 成員: {inS6}/{tot}")

print("\n=== 4) CKM θ 家族控制對比 (同一搜尋, 已知結構對) ===")
ckm_targets = {
    "tan θ12 13.04": math.tan(math.radians(13.039994)),
    "tan θ23 2.38": math.tan(math.radians(2.379994)),
    "sin θ13 0.201": math.sin(math.radians(0.200961)),
    "tan δ 66.40": math.tan(math.radians(66.399960)),
}
for name, t in ckm_targets.items():
    (p1, p2, r), e = best_ratio(t)
    print(f"  {name}: beat{p1}/beat{p2} = {r:.10f} (err={e:.2e})")
    # 多重度
    cnt = sum(1 for b1 in bval_list for b2 in bval_list if b2 > 0 and abs(b1/b2 - t) < e + 1e-9)
    print(f"    err<{e:.1e} 對數: {cnt}")
