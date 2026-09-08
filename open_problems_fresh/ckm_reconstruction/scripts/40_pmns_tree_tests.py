#!/usr/bin/env python3
"""40 — PMNS tree-sector 測試: Q(√5) forms / rationals / δ_PMNS chain / C₅ anchors
T1: rational a/b (b≤100) 近似 + 結構因數檢查 (10/33, 41/91, 2/91 候選) + null-control
T2: δ_PMNS = 232°: tan(52°) 純 sine 類 + full beat 類命中
T3: C₅ anchors: sin²/cos²(kπ/5, kπ/10) vs PMNS sin²θ
T4: 232° 身份候選: 88+144, 4ΣD6, 360−128 核對
"""
import numpy as np, math
from fractions import Fraction

sin2 = {"θ₁₂": 0.303, "θ₂₃": 0.451, "θ₁₃": 0.02203}
STRUCT = {1,2,3,4,5,6,7,8,9,11,12,13,16,17,18,19,20,21,22,25,27,29,32,33,34,36,38,40,41,42,44,47,55,63,64,66,68,76,77,85,88,90,91,98}

def factored(x):
    """x 嘅質因數全部係結構數? (質因數 ∈ {2,3,5,7,11,13,17,19,41,47} ∪ 本身結構)"""
    n = x; facs = []
    p = 2
    while p*p <= n:
        while n % p == 0:
            facs.append(p); n //= p
        p += 1
    if n > 1: facs.append(n)
    return facs, all(f in {2,3,5,7,11,13,17,19,41,47} for f in facs)

print("=== T1: rational 近似 + 結構因數 ===")
for name, t in sin2.items():
    best = None
    cands = []
    for b in range(1, 101):
        for a in range(1, b+1):
            v = a/b
            if abs(v - t) < 1e-3:
                cands.append((abs(v-t), a, b))
    cands.sort()
    print(f"  {name} sin²={t}:")
    for err, a, b in cands[:6]:
        fa, ok_a = factored(a); fb, ok_b = factored(b)
        print(f"    {a}/{b} = {a/b:.6f} (Δ={err:.2e})  num{f'a' if ok_a else '✗'}{fa} den{f'b' if ok_b else '✗'}{fb}")

# null: 200 random targets 有幾多有 結構因數 rational within 1e-3
rng = np.random.default_rng(9)
n_hit = 0
for _ in range(200):
    t = rng.uniform(0.01, 0.7)
    ok = False
    for b in range(1, 101):
        a = int(round(t*b))
        if a < 1: continue
        if abs(a/b - t) < 1e-3:
            _, oa = factored(a); _, ob = factored(b)
            if oa and ob: ok = True; break
    n_hit += ok
print(f"  null-control: 200 random targets 有結構因數 rational (b≤100, Δ<1e-3): {n_hit}/200 = {n_hit/2:.0f}%")

print("\n=== T2: δ_PMNS = 232° (tan = tan 52° = 1.27994) ===")
t52 = math.tan(math.radians(52))
sinv = np.sin(np.arange(1, 88)*np.pi/176.0)
hits = []
for a in range(1, 88):
    for b in range(1, 88):
        if a == b: continue
        r = sinv[a-1]/sinv[b-1]
        if abs(r - t52) < 1e-4:
            hits.append((abs(r-t52), a, b))
hits.sort()
print(f"  純 sine 類 @1e-4: {len(hits)} hits {hits[:5]}")
hits6 = [h for h in hits if h[0] < 1e-6]
print(f"  @1e-6: {len(hits6)} hits")
# full beat 類 @1e-8
pairs = [(a,b) for a in range(1,88) for b in range(a+1,89)]
beats = np.array([4*np.sin((b-a)*np.pi/176.0)*np.cos((a+b)*np.pi/176.0) for a,b in pairs])
cnt = 0; first = None
for i in range(len(pairs)):
    m = np.abs(beats[i]/beats - t52) < 1e-8
    c = int(m.sum())
    cnt += c
    if c and first is None:
        j = int(np.argwhere(m).flatten()[0])
        first = (pairs[i], pairs[j])
print(f"  full beat 類 @1e-8: {cnt} hits (null mean 0.1) {first}")

print("\n=== T3: C₅ anchors vs PMNS ===")
anchors = {}
for k in range(1, 10):
    anchors[f"sin²(kπ/10) k={k}"] = math.sin(k*math.pi/10)**2
    anchors[f"cos²(kπ/10) k={k}"] = math.cos(k*math.pi/10)**2
for name, t in sin2.items():
    nearest = sorted(((abs(v-t), lbl) for lbl, v in anchors.items()))[:2]
    print(f"  {name} sin²={t}: 最近 anchors: {[(l, f'{a:.4f}') for a,l in nearest]}")

print("\n=== T4: 232° 身份候選 ===")
print(f"  88+144 = {88+144}, 4·ΣD6 = {4*58}, 360−128 = {360-128} — 全部 = 232?")
print(f"  α⁻¹(M_Z) = 128 (O142: 2·44+F₅F₆ = 88+40)")

print("\nRESULT: PMNS tree 測試完成")
