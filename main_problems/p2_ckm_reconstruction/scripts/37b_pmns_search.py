#!/usr/bin/env python3
"""37b — PMNS 結構重推: 1e-8/1e-9 精度唯一性測試
類別: (1) 純 sine-ratio sin(a)/sin(b) (2) full beat-ratio beat(a,b)/beat(c,d)
目標: 舊 search 嘅 PMNS 角 (從 data 檔 parse, fallback NuFIT 5.2 NO)
判準: 命中數 (multiplicity) + (d,s) 結構 + Z5 adjacency + D6/S6 membership
"""
import numpy as np, re, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
N = 88
n = np.arange(1, N+1, dtype=np.float64)  # 1..88
sinv = np.sin(n*np.pi/176.0)

# --- targets from old data file ---
targets = {}
try:
    txt = open("data/pmns_beat_search_corrected.txt").read()
    # 揾 "θ12 = 33.41" 之類模式
    for m in re.finditer(r"(theta|θ|s12|s23|s13)[ _]?(\d+)\s*=\s*([0-9.]+)°?", txt, re.I):
        key = f"θ{m.group(2)}"
        val = float(m.group(3))
        if key not in targets:
            targets[key] = val
except Exception as e:
    print("parse failed:", e)
if not targets:
    targets = {"θ12": 33.41, "θ23": 42.2, "θ13": 8.54}
print("targets:", targets)

D6 = {1,2,6,9,19,21}; S6 = {11,25,41,44,68,85}; C6 = {3,11,20,25,41,44}

def z5_adj(d, s):
    """Z5 cyclic distance: indices i=s±d 喺 mod-5 圈上差 1?"""
    a, b = (s-d)//2, (s+d)//2
    return abs((a % 5) - (b % 5)) == 1 or abs((a % 5) - (b % 5)) == 4

# --- class 1: pure sine ratio ---
print("\n=== C1: sin(a)/sin(b) === (87x87)")
for k, (tk, deg) in enumerate(targets.items()):
    t = np.tan(np.radians(deg))
    R = sinv[:,None] / sinv[None,:]   # 88x88
    for tol in (1e-8, 1e-9):
        hits = np.argwhere(np.abs(R - t) < tol)
        hits = [(int(a),int(b)) for a,b in hits if a != b]
        # distinct up to (a,b)<->(b,a) — 用 a<b
        hits = [(a,b) for a,b in hits if a < b]
        if hits:
            ds = [(b-a, a+b, (b-a) in D6 or (b-a) in S6 or (b-a) in C6,
                   z5_adj(b-a, a+b)) for a,b in hits[:5]]
            print(f"  {tk} tan={t:.8f} tol={tol:.0e}: {len(hits)} hits {hits[:3]} d,s={ds}")
        else:
            print(f"  {tk} tan={t:.8f} tol={tol:.0e}: 0 hits")

# --- class 2: full beat ratio ---
print("\n=== C2: beat(a,b)/beat(c,d) === (3828^2)")
# beats: |sqrt(gamma_a) - sqrt(gamma_b)| = 2|sin(aπ/176)-sin(bπ/176)|
pairs = [(a,b) for a in range(1,N) for b in range(a+1,N+1)]
beats = np.array([2*abs(sinv[a-1]-sinv[b-1]) for a,b in pairs])
# 全部 ratios (vectorized in chunks)
M = len(pairs)
d_pairs = np.array([(b-a, a+b) for a,b in pairs])  # (d, s)
for k, (tk, deg) in enumerate(targets.items()):
    t = np.tan(np.radians(deg))
    best = (1e30, None)
    cnt = 0
    hits_info = []
    for i in range(M):
        # vector: beats[i]/beats
        r = beats[i] / beats
        m = np.abs(r - t) < 1e-8
        cnt += int(m.sum())
        if m.any():
            idx = np.argwhere(m)[:3]
            for j in idx.flatten():
                (a,b),(c,d) = pairs[i], pairs[j]
                hits_info.append(((a,b),(c,d), (b-a,a+b),(d-c,c+d)))
        if len(hits_info) >= 10: break
    print(f"  {tk} tan={t:.8f}: hits(1e-8)={cnt} sample={hits_info[:4]}")

print("\nRESULT: PMNS 1e-8 唯一性測試完成")
