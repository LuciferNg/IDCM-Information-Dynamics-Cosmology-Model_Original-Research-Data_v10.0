#!/usr/bin/env python3
"""O149 script 02 — 先驗鎖定規則測試
====================================
測試候選先驗規則 (規則定義唔依賴目標值, 只用結構):
R0: 全空間基線 (946 beats → 831,713 ratios, O146 已做)
R1: v_g-ratio 家族 — mixing element = v_g(p)/v_g(q), p,q ∈ 特殊模式集 S₀
    (Z₂ 對偶: ω-ratio = v_g-ratio;  γ-ratio = v_g²-ratio)
R2: 相鄰對 ratio 家族 — beat(n,n+1)/beat(m,m+1) = v_g(n+½)/v_g(m+½)
R3: 結構 pair 類普查 — 每類 (d=1, Fib-d, Z₂-sum, 特殊mean) 命中 11 目標嘅統計
R4: 兩因子鎖定 — [sin(d₁π/176)/sin(d₂π/176)] × [v_g(m₁)/v_g(m₂)], d∈Fib, m∈特殊

統計: 每規則生成 M 個候選, 對 11 目標計 δ_min; 同全空間 δ_min 比較。
p 值: 候選在 [0,2] 均勻 → P(δ<ε) ≈ 2ε/2 · M 近似, 用精確 rank 分數。
"""
import math, json, os
from math import comb
import numpy as np

PI = math.pi
w  = lambda n: 2*math.sin(PI*n/88)
vg = lambda x: math.cos(PI*x/88)
beat = lambda a,b: abs(w(a)-w(b))

# 特殊模式集 S₀ (a priori: Fib F₅-F₉ ∪ Lucas L₅-L₇ ∪ 階梯 ∪ Z₂-dual ∪ 邊界)
S0 = [1,2,3,4,5,6,7,8,11,13,18,21,22,29,33,34,41,42,43,44]
# 特殊 mean 集 (整數 + 半整數, 由 S0 元素配對產生)
SPECIAL_MEANS = sorted(set((a+b)/2.0 for a in S0 for b in S0 if a < b) | set(S0))

# 11 個目標 (docs 觀測值, 只用作驗證, 唔用嚟定義規則)
targets = [
    ('CKM tanθ₁₂', 0.231604, (5,6),   (19,25)),
    ('CKM tanθ₂₃', 0.041563, (33,35), (3,22)),
    ('CKM sinθ₁₃', 0.003508, (42,43), (10,31)),
    ('CKM λ',      0.22500,  (25,35), (6,37)),
    ('CKM V_cb',   0.04182,  (13,14), (6,37)),
    ('CKM V_ub',   0.00369,  (41,42), (3,37)),
    ('CKM A',      0.830,    (16,35), (10,28)),
    ('PMNS tanθ₁₂',0.659629, (4,13),  (9,25)),
    ('PMNS tanθ₂₃',0.906745, (11,23), (12,26)),
    ('PMNS tanθ₂₃b',1.150368,(4,14),  (22,44)),
    ('PMNS sinθ₁₃',0.1485,   (25,29), (3,20)),
]
T = [t[1] for t in targets]

# ============ 全空間基線 (831,713 ratios) ============
pairs = [(i,j) for i in range(1,45) for j in range(i+1,45)]
B = np.array(sorted(beat(i,j) for i,j in pairs))
R_all = np.array([b1/b2 for b1 in B for b2 in B if b2 > 1e-6])
R_all = R_all[R_all < 10]; R_all.sort()

def delta_min(rule_values):
    """對每個目標: rule_values 集合中最近值嘅相對偏差"""
    out = []
    for t in T:
        if len(rule_values) == 0:
            out.append(float('inf')); continue
        rv = np.array(sorted(rule_values))
        idx = np.searchsorted(rv, t)
        best = float('inf')
        for i in (idx-1, idx, idx+1):
            if 0 <= i < len(rv):
                best = min(best, abs(rv[i]-t))
        out.append(best/t)
    return np.array(out)

def percentile_of(rule_values, t):
    """t 喺 rule_values 中嘅最近距離, 相對全空間最近距離 (percentile)"""
    if len(rule_values) == 0: return 1.0
    rv = np.array(sorted(rule_values))
    idx = np.searchsorted(rv, t)
    best = min(abs(rv[max(0,idx-1)]-t), abs(rv[min(len(rv)-1,idx)]-t))
    # 全空間: 任何隨機 ratio 嘅預期 δ 分佈
    return best

print("="*72)
print("R0 基線: 全空間 831,713 ratios 嘅 δ_min (O146 已審計)")
print("="*72)
d0 = delta_min(R_all)
print(f"  全空間對 11 目標 δ_min 中位數: {np.median(d0):.2e}  (O146: 4.60e-07)")
spacing = np.median(np.diff(R_all))
print(f"  全空間 median spacing: {spacing:.2e}")

# ============ R1: 純 v_g-ratio 家族 ============
print()
print("="*72)
print("R1: v_g(p)/v_g(q),  p,q ∈ S0 (特殊模式集)")
print("="*72)
r1_vals = []
for p in S0:
    for q in S0:
        if p != q and vg(q) > 1e-9:
            r = vg(p)/vg(q)
            if 0 < r < 10: r1_vals.append(r)
r1_vals = sorted(set(round(v,14) for v in r1_vals))
d1 = delta_min(r1_vals)
print(f"  候選數 M = {len(r1_vals)}")
for (name,t,(a,b),(c,d)),dd in zip(targets, d1):
    print(f"    {name:>13}: δ_min = {dd:.2e}  ({'<1%' if dd<0.01 else '✗'})")
print(f"  <1% 命中: {(d1<0.01).sum()}/11,  中位 δ: {np.median(d1):.2e}")

# ============ R2: 相鄰對 ratio = 半整數 v_g ratio ============
print()
print("="*72)
print("R2: beat(n,n+1)/beat(m,m+1) = v_g(n+½)/v_g(m+½)")
print("="*72)
r2_vals = []
for n in range(1,44):
    for m in range(1,44):
        if n != m:
            r = vg(n+0.5)/vg(m+0.5)
            if 0 < r < 10: r2_vals.append(r)
r2_vals = sorted(set(round(v,14) for v in r2_vals))
d2 = delta_min(r2_vals)
print(f"  候選數 M = {len(r2_vals)}")
for (name,t,(a,b),(c,d)),dd in zip(targets, d2):
    print(f"    {name:>13}: δ_min = {dd:.2e}  ({'<1%' if dd<0.01 else '✗'})")
print(f"  <1% 命中: {(d2<0.01).sum()}/11,  中位 δ: {np.median(d2):.2e}")

# ============ R3: 結構 pair 類 ============
print()
print("="*72)
print("R3: 結構 pair 類普查 — 每類對 11 目標嘅命中")
print("="*72)
fib_d = {1,2,3,5,8,13,21,34}
classes = {
    'C1 d=1 相鄰':        lambda a,b: abs(a-b)==1,
    'C2 Fib 分離':        lambda a,b: abs(a-b) in fib_d,
    'C3 Z₂ 對稱(sum=44)': lambda a,b: a+b==44,
    'C4 特殊mean(整數)':  lambda a,b: (a+b)/2 in set(S0),
    'C5 兩端點都特殊':     lambda a,b: a in S0 and b in S0,
}
for cname, cf in classes.items():
    cpairs = [(a,b) for a,b in pairs if cf(a,b)]
    cvals = sorted(set(round(beat(a,b)/beat(c,d),14)
                       for a,b in cpairs for c,d in cpairs if beat(c,d) > 1e-6))
    cvals = [v for v in cvals if 0 < v < 10]
    dc = delta_min(cvals)
    n_hit = int((dc < 0.01).sum())
    # 期望命中數 (隨機): 每個目標喺 [0,2] 均勻, 命中窗 = 2×t×0.01 → 密度 0.5
    exp = sum(2*t*0.01*len(cvals)/2 for t in T)
    print(f"  {cname:>20}: pairs={len(cpairs):4d}, ratios={len(cvals):6d}, "
          f"<1% 命中 {n_hit:2d}/11 (期望 {exp:.1f}), 中位δ {np.median(dc):.1e}")

# ============ R4: 兩因子鎖定 (Fib-d × 特殊mean) ============
print()
print("="*72)
print("R4: [sin(d₁π/176)/sin(d₂π/176)] × [v_g(m₁)/v_g(m₂)]")
print("     d₁,d₂ ∈ Fib {1,2,3,5,8,13,21,34};  m₁,m₂ ∈ 特殊 mean 集")
print("="*72)
fib_ds = sorted(fib_d)
r4_vals = []
for d1v in fib_ds:
    for d2v in fib_ds:
        s_ratio = math.sin(d1v*PI/176)/math.sin(d2v*PI/176)
        for m1 in SPECIAL_MEANS:
            for m2 in SPECIAL_MEANS:
                if abs(vg(m2)) < 1e-9: continue
                r = s_ratio * vg(m1)/vg(m2)
                if 0 < r < 10: r4_vals.append(r)
r4_vals = sorted(set(round(v,14) for v in r4_vals))
d4 = delta_min(r4_vals)
print(f"  候選數 M = {len(r4_vals)}")
for (name,t,(a,b),(c,d)),dd in zip(targets, d4):
    print(f"    {name:>13}: δ_min = {dd:.2e}  ({'<1%' if dd<0.01 else '✗'})")
print(f"  <1% 命中: {(d4<0.01).sum()}/11,  中位 δ: {np.median(d4):.2e}")

# ============ R5: 精簡兩因子 (d=1 分子 × v_g 鎖定) ============
print()
print("="*72)
print("R5: 精簡版 — 分子 d₁=1 (相鄰), 分母 d₂ ∈ Fib, mean ∈ 特殊")
print("     → 小角: sin(π/176)·v_g(m₁) / [sin(d₂π/176)·v_g(m₂)]")
print("="*72)
r5_vals = []
for m1 in SPECIAL_MEANS:
    for d2v in fib_ds:
        for m2 in SPECIAL_MEANS:
            if abs(vg(m2)) < 1e-9: continue
            r = math.sin(PI/176)*vg(m1)/(math.sin(d2v*PI/176)*vg(m2))
            if 0 < r < 10: r5_vals.append(r)
r5_vals = sorted(set(round(v,14) for v in r5_vals))
d5 = delta_min(r5_vals)
print(f"  候選數 M = {len(r5_vals)}")
for (name,t,(a,b),(c,d)),dd in zip(targets, d5):
    print(f"    {name:>13}: δ_min = {dd:.2e}  ({'<1%' if dd<0.01 else '✗'})")
print(f"  <1% 命中: {(d5<0.01).sum()}/11,  中位 δ: {np.median(d5):.2e}")

# ============ 儲存 ============
d1a = np.array(d1); d2a = np.array(d2); d4a = np.array(d4); d5a = np.array(d5)
res = {
    "R0_baseline": {"n_ratios": len(R_all), "median_spacing": float(spacing),
                    "dmin_median": float(np.median(d0))},
    "R1_vg_ratio": {"M": len(r1_vals), "hits_1pct": int((d1a<0.01).sum()),
                    "dmin_median": float(np.median(d1a)),
                    "per_target": {name: float(dd) for (name,*_),dd in zip(targets,d1)}},
    "R2_adjacent": {"M": len(r2_vals), "hits_1pct": int((d2a<0.01).sum()),
                    "dmin_median": float(np.median(d2a)),
                    "per_target": {name: float(dd) for (name,*_),dd in zip(targets,d2)}},
    "R4_two_factor": {"M": len(r4_vals), "hits_1pct": int((d4a<0.01).sum()),
                      "dmin_median": float(np.median(d4a))},
    "R5_reduced": {"M": len(r5_vals), "hits_1pct": int((d5a<0.01).sum()),
                   "dmin_median": float(np.median(d5a))},
}
out = os.path.join(os.path.dirname(__file__), "..", "data", "02_prior_locking.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
