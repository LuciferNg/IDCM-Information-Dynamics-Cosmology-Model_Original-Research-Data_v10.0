#!/usr/bin/env python3
"""
O9-C4: 母函數整合 — 奇偶分離 Fib/Lucas 級聯
==============================================
信號整合:
- A2/A1 = (F₃/F₄)² = (2/3)²          (0.23%)
- A4/A1 = (L₂/L₄)² = (3/7)²          (1.03%)
- A6/A1 = (L₃/L₅)² = (3/11)²         (1.48%)
- A7/A1 = L₁/L₄ = 1/7                (0.09%)
- A6/A5 = F₆/F₇ = 8/13               (1.19%)

奇數峰 (m=1,3,5,7): 1.000, 0.439, 0.214, 0.143
偶數峰 (m=2,4,6):   0.443, 0.186, 0.130

假設: 奇偶峰各自係 Fib/Lucas 平方級聯!
偶數峰: A_{2k}/A_1 = (X_k/Y_k)²
   k=1 (m=2): (2/3)² = (F₃/F₄)²
   k=2 (m=4): (3/7)² = (L₂/L₄)²
   k=3 (m=6): (3/11)² = (L₃/L₅)²

奇數峰: A_{2k+1}/A_1 = ?
   k=0 (m=1): 1
   k=1 (m=3): 0.439
   k=2 (m=5): 0.214
   k=3 (m=7): 0.143 = 1/7

檢查: (3/7)² = 0.184 vs 0.186 ✓
      (3/11)² = 0.074 vs 0.130 ✗! 錯!
"""
import numpy as np
from fractions import Fraction

print("="*80)
print("O9-C4: 母函數整合")
print("="*80)

F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]

A_obs = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
A1 = A_obs[1]
norm = {m: A_obs[m]/A1 for m in range(1, 8)}

# ---------- 1. 重新核對 ----------
print("\n1. 之前搜尋嘅候選 (全部再驗):")
cands = {
    2: [((F[3]/F[4])**2, "(F₃/F₄)²")],
    4: [((L[2]/L[4])**2, "(L₂/L₄)²"), ((F[3]/F[4])**2 * (L[2]/L[4])**2, "組合?")],
    6: [((L[3]/L[5])**2, "(L₃/L₅)²")],
    7: [(L[1]/L[4], "L₁/L₄")],
}
for m, cands_m in cands.items():
    print(f"   m={m} ({norm[m]:.4f}):")
    for val, label in cands_m:
        dev = abs(val - norm[m])/norm[m]*100
        print(f"      {label} = {val:.4f} dev={dev:.2f}%")

# ---------- 2. 偶數峰詳細搜尋 ----------
print("\n" + "-"*80)
print("2. 偶數峰 A_{2k}/A_1 系統搜尋 (Fib/Lucas 平方):")
print("-"*80)
even_targets = {2: norm[2], 4: norm[4], 6: norm[6]}
for m, target in even_targets.items():
    print(f"   m={m} (A{2}... target {target:.4f}):")
    best = []
    for i in range(1, 11):
        for j in range(1, 11):
            # Fib/Fib 平方
            if F[i] > 0 and F[j] > 0:
                r = (F[i]/F[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(F_{i}/F_{j})²={r:.4f}"))
            # Lucas/Lucas 平方
            if L[i] > 0 and L[j] > 0:
                r = (L[i]/L[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(L_{i}/L_{j})²={r:.4f}"))
            # Fib/Lucas 平方
            if F[i] > 0 and L[j] > 0:
                r = (F[i]/L[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(F_{i}/L_{j})²={r:.4f}"))
            if L[i] > 0 and F[j] > 0:
                r = (L[i]/F[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(L_{i}/F_{j})²={r:.4f}"))
    best.sort()
    for dev, s in best[:5]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 3. 奇數峰詳細搜尋 ----------
print("\n" + "-"*80)
print("3. 奇數峰 A_{2k+1}/A_1 系統搜尋:")
print("-"*80)
odd_targets = {3: norm[3], 5: norm[5], 7: norm[7]}
for m, target in odd_targets.items():
    print(f"   m={m} (target {target:.4f}):")
    best = []
    for i in range(1, 11):
        for j in range(1, 11):
            if F[i] > 0 and F[j] > 0:
                r = (F[i]/F[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(F_{i}/F_{j})²={r:.4f}"))
            if L[i] > 0 and L[j] > 0:
                r = (L[i]/L[j])**2
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"(L_{i}/L_{j})²={r:.4f}"))
            if F[i] > 0 and L[j] > 0:
                r = F[i]/L[j]
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"F_{i}/L_{j}={r:.4f}"))
            if L[i] > 0 and F[j] > 0:
                r = L[i]/F[j]
                dev = abs(r - target)/target*100
                if dev < 5: best.append((dev, f"L_{i}/F_{j}={r:.4f}"))
    best.sort()
    for dev, s in best[:5]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 4. 相鄰奇峰比 ----------
print("\n" + "-"*80)
print("4. 奇峰內部比 (A3/A1, A5/A3, A7/A5):")
print("-"*80)
r31 = norm[3]/norm[1]
r53 = norm[5]/norm[3]
r75 = norm[7]/norm[5]
print(f"   A3/A1 = {r31:.4f}")
print(f"   A5/A3 = {r53:.4f}")
print(f"   A7/A5 = {r75:.4f}")
for name, r in [("A3/A1", r31), ("A5/A3", r53), ("A7/A5", r75)]:
    best = []
    for i in range(1, 11):
        for j in range(1, 11):
            if F[i] > 0 and F[j] > 0:
                val = (F[i]/F[j])**2
                dev = abs(val - r)/r*100
                if dev < 5: best.append((dev, f"(F_{i}/F_{j})²={val:.4f}"))
            if L[i] > 0 and L[j] > 0:
                val = (L[i]/L[j])**2
                dev = abs(val - r)/r*100
                if dev < 5: best.append((dev, f"(L_{i}/L_{j})²={val:.4f}"))
    best.sort()
    print(f"   {name} ({r:.4f}):")
    for dev, s in best[:3]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 5. 偶峰內部比 ----------
print("\n" + "-"*80)
print("5. 偶峰內部比 (A4/A2, A6/A4):")
print("-"*80)
r42 = norm[4]/norm[2]
r64 = norm[6]/norm[4]
print(f"   A4/A2 = {r42:.4f}")
print(f"   A6/A4 = {r64:.4f}")
for name, r in [("A4/A2", r42), ("A6/A4", r64)]:
    best = []
    for i in range(1, 11):
        for j in range(1, 11):
            if F[i] > 0 and F[j] > 0:
                val = (F[i]/F[j])**2
                dev = abs(val - r)/r*100
                if dev < 5: best.append((dev, f"(F_{i}/F_{j})²={val:.4f}"))
            if L[i] > 0 and L[j] > 0:
                val = (L[i]/L[j])**2
                dev = abs(val - r)/r*100
                if dev < 5: best.append((dev, f"(L_{i}/L_{j})²={val:.4f}"))
    best.sort()
    print(f"   {name} ({r:.4f}):")
    for dev, s in best[:3]:
        print(f"      {s} dev={dev:.2f}%")
