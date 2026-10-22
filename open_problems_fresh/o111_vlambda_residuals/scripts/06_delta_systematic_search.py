#!/usr/bin/env python3
"""
O111 攻堅 6: Δ 精確閉合形式 — 系統搜索
========================================
基於 script 01-05 嘅發現，進行更深入搜索
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O111 攻堅 6: Δ 精確閉合形式 — 系統搜索")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
phi = (1 + math.sqrt(5)) / 2

Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
delta = Fg - 264

print(f"\n  Δ = {delta:.15f}")
print(f"  1/Δ = {1/delta:.10f}")

# ═══════════════════════════════════════════
# 策略 1: Δ = γ_i/j - γ_k/l 形式
# ═══════════════════════════════════════════
print("\n[1] Δ = γ_i/a - γ_j/b 搜索")
best = []
for i in range(1, 45):
    for j in range(1, 45):
        for a in [36, 44, 88, 90, 134, 73, 61, 4, 8, 11, 18, 29, 33, 66, 98, 178, 264, 283]:
            for b in [36, 44, 88, 90, 134, 73, 61, 4, 8, 11, 18, 29, 33, 66, 98, 178, 264, 283]:
                val = gamma44[i-1]/a - gamma44[j-1]/b
                err = abs(val - delta)/delta
                if err < 1e-4 and val > 0:
                    best.append((err, f"γ_{i}/{a} - γ_{j}/{b}", val))
best.sort()
print("  Top 10 (err < 0.01%):")
for err, name, val in best[:10]:
    print(f"    {name:24s} = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 2: Δ = 1/(a + γ_i/b) 形式
# ═══════════════════════════════════════════
print("\n[2] Δ = 1/(a + γ_i/b) 搜索")
best2 = []
inv = 1/delta
for i in range(1, 45):
    for a in range(1, 20):
        for b in [1, 2, 4, 8, 11, 18, 29, 36, 44, 88, 90, 134, 946]:
            val = 1/(a + gamma44[i-1]/b)
            err = abs(val - delta)/delta
            if err < 0.001:
                best2.append((err, f"1/({a} + γ_{i}/{b})", val))
best2.sort()
print("  Top 10 (err < 0.1%):")
for err, name, val in best2[:10]:
    print(f"    {name:24s} = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 3: Δ = γ_i × (a - b)/c 形式  
# ═══════════════════════════════════════════
print("\n[3] Δ = γ_i × (a - γ_j)/c 搜索")
best3 = []
for i in range(1, 45):
    for j in range(1, 45):
        for a in range(1, 100):
            for c in [1, 2, 4, 8, 11, 18, 29, 36, 44, 88, 90, 134, 178, 264, 283]:
                val = gamma44[i-1] * (a - gamma44[j-1]) / c
                err = abs(val - delta)/delta
                if err < 0.001:
                    best3.append((err, f"γ_{i}×({a}-γ_{j})/{c}", val))
best3.sort()
print("  Top 10 (err < 0.1%):")
for err, name, val in best3[:10]:
    print(f"    {name:24s} = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 4: Δ = γ_29/36 - γ_1/N 搜索
# ═══════════════════════════════════════════
print("\n[4] Δ = γ_29/36 - γ_1/N 搜索")
g29_36 = gamma44[28]/36
for N in range(1, 200):
    val = g29_36 - gamma44[0]/N
    err = abs(val - delta)/delta
    if err < 0.001:
        print(f"    γ_29/36 - γ_1/{N:3d} = {val:.12f} (err {err*100:.4f}%)")

# 更一般: Δ = γ_i/a - γ_j/b + γ_k/c
print("\n[5] Δ = γ_i/a - γ_j/b + γ_k/c 搜索 (三項)")
best5 = []
for i in [29, 30, 28, 27, 31, 32, 33]:
    gi = gamma44[i-1]
    for j in [1, 2, 3, 4, 5, 6, 7, 8]:
        gj = gamma44[j-1]
        for k in [1, 2, 3, 4, 5, 44]:
            gk = gamma44[k-1]
            for a in [36, 44, 88, 90, 134, 73, 61, 18, 29, 33]:
                for b in [36, 44, 88, 90, 134, 73, 61, 18, 29]:
                    for c in [36, 44, 88, 90, 134, 73, 61, 18, 29, 33, 66, 98, 178, 264, 283]:
                        val = gi/a - gj/b + gk/c
                        err = abs(val - delta)/delta
                        if err < 1e-5:
                            best5.append((err, f"γ_{i}/{a} - γ_{j}/{b} + γ_{k}/{c}", val))
best5.sort()
print("  Top 10 (err < 0.001%):")
for err, name, val in best5[:10]:
    print(f"    {name:28s} = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 6: Δ = 1/(12 + γ_1/γ_29) 等
# ═══════════════════════════════════════════
print("\n[6] 1/(a + γ_i/γ_j) 搜索")
inv = 1/delta
for i in range(1, 45):
    for j in range(1, 45):
        if j == i:
            continue
        ratio = gamma44[i-1]/gamma44[j-1]
        for a in range(1, 20):
            val = 1/(a + ratio)
            err = abs(val - delta)/delta
            if err < 0.001:
                print(f"    1/({a} + γ_{i}/γ_{j}) = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 7: Δ = 1/(12 + 1/(5 + γ_i/γ_j)) 
# ═══════════════════════════════════════════
print("\n[7] 連分數: 1/(12 + 1/(5 + γ_i/γ_j))")
for i in range(1, 45):
    for j in range(1, 45):
        if j == i:
            continue
        ratio = gamma44[i-1]/gamma44[j-1]
        val = 1/(12 + 1/(5 + ratio))
        err = abs(val - delta)/delta
        if err < 0.001:
            print(f"    1/(12 + 1/(5 + γ_{i}/γ_{j})) = {val:.12f} (err {err*100:.4f}%)")

# 更高階
for i in range(1, 45):
    for j in range(1, 45):
        for a in [1, 2, 3, 6]:
            ratio = gamma44[i-1]/gamma44[j-1]
            val = 1/(12 + 1/(5 + 1/(a + ratio)))
            err = abs(val - delta)/delta
            if err < 0.0001:
                print(f"    1/(12+1/(5+1/({a}+γ_{i}/γ_{j}))) = {val:.12f} (err {err*100:.4f}%)")

# ═══════════════════════════════════════════
# 策略 8: Δ = κ 貢獻分解
# ═══════════════════════════════════════════
print("\n[8] κ 貢獻分解: 邊個 κ 出分數?")
# 每個 κ 三元組對 F(γ) 嘅貢獻
total = 0
frac_contrib = 0
for i in range(36):
    for j in range(i, 36):
        for k in range(j, 36):
            kk = kappa[i,j,k]
            if kk != 0:
                sym = 6 if i==j==k else (3 if i==j or j==k or i==k else 1)
                contrib = kk * gamma36[i] * gamma36[j] * gamma36[k] / (6 * sym/6)
                total += contrib
                # 睇分數部分
                if abs(contrib - round(contrib)) > 1e-10:
                    frac_contrib += contrib - round(contrib)
print(f"  F(γ) = {total:.10f}")
print(f"  分數貢獻總和 = {frac_contrib:.10f}")
print(f"  Δ = {delta:.10f}")

# 每個 κ 三元組嘅分數部分
print(f"\n  分數貢獻 > 0.01 嘅 κ 三元組:")
contribs = []
for i in range(36):
    for j in range(i, 36):
        for k in range(j, 36):
            kk = kappa[i,j,k]
            if kk != 0:
                sym = 6 if i==j==k else (3 if i==j or j==k or i==k else 1)
                contrib = kk * gamma36[i] * gamma36[j] * gamma36[k] / (6 * sym/6)
                frac = contrib - round(contrib)
                if abs(frac) > 0.001:
                    contribs.append((abs(frac), f"κ_{{{i},{j},{k}}}={kk}", float(contrib)))
contribs.sort(reverse=True)
for frac, name, contrib in contribs[:15]:
    print(f"    {name:20s} contrib={contrib:+.8f} (frac={frac:.6f})")

# ═══════════════════════════════════════════
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
print(f"""
  Δ = {delta:.15f}
  
  最佳候選 (兩項):
""")
for err, name, val in best[:5]:
    print(f"    {name:24s} = {val:.12f} (err {err*100:.4f}%)")

print(f"""
  最佳候選 (三項):
""")
for err, name, val in best5[:5]:
    print(f"    {name:28s} = {val:.12f} (err {err*100:.4f}%)")

print(f"""
  連分數: [0, 12, 5, 1, 2, 6, 12, 1, 2, 3, 3, 1, 1, 1, 25, 1195, ...]
  大項 1195 → Δ 極接近有理數 4235787/51574657
  
  Y(γ) signature: 18+ / 14- / 4 kernel
  G(γ) signature: 15+ / 17- / 4 kernel
  G_pos = Y_neg + 1, G_neg = Y_pos - 1 (正負交換定理)
""")