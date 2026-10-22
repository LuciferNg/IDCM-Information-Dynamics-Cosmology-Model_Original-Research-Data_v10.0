#!/usr/bin/env python3
"""
O9-C2: N_d−X 母函數完整驗證
=============================
發現: 級聯數字全部係 N_d − Fib/Lucas 形式
23 = 44−21 = N_d−F₈
26 = 44−18 = N_d−L₆
15 = 44−29 = N_d−L₇
41 = 44−3  = N_d−L₂

檢查: 9, 27, 14 係咪都係 N_d−X 或者 3^k/Lucas 混合
同埋: 分子同分母之間有冇結構關係 (級聯)
"""
from fractions import Fraction
import numpy as np

print("="*80)
print("O9-C2: N_d−X 母函數驗證")
print("="*80)

F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
N_d = 44

# ---------- 1. 所有數字嘅 N_d−X 分解 ----------
print("\n1. 級聯數字 N_d−X 分解:")
nums = {'4': 'A2/A1 分子', '9': 'A2/A1 分母', '11': 'A4/A3 分子', '26': 'A4/A3 分母',
        '15': 'A5/A4 分子', '13': 'A5/A4 分母', '14': 'A6/A5 分子', '23': 'A6/A5 分母',
        '23b': 'A7/A6 分子', '21': 'A7/A6 分母', '18': 'A3/A1 分子', '41': 'A3/A1 分母',
        '5': 'A4/A1 分子', '27': 'A4/A1 分母', '3': 'A5/A1 分子', '14b': 'A6/A1 分子',
        '3b': 'A6/A1 分子', '7': 'A7/A1 分母'}
# 獨特數字 (非 Fib/Lucas 直接)
special = {'9': 'A2/A1 分母', '27': 'A4/A1 分母', '14': 'A6/A5 分子', '15': 'A5/A4 分子', '26': 'A4/A3 分母', '23': 'A6/A5 分母', '41': 'A3/A1 分母'}

for n_str, label in special.items():
    n = int(n_str.replace('b', ''))
    cands = []
    for i, f in enumerate(F):
        if f > 0 and N_d - f == n:
            cands.append(f"N_d−F_{i}")
    for i, l in enumerate(L):
        if l > 0 and N_d - l == n:
            cands.append(f"N_d−L_{i}")
    # 3^k
    for k in range(1, 5):
        if 3**k == n:
            cands.append(f"3^{k}")
    print(f"   {n} ({label}): {', '.join(cands) if cands else '—'}")

# ---------- 2. 比率結構 ----------
print("\n2. 所有比率嘅 N_d−X 表達:")
ratios = {
    'A2/A1': Fraction(4, 9), 'A3/A2': Fraction(1, 1), 'A4/A3': Fraction(11, 26),
    'A5/A4': Fraction(15, 13), 'A6/A5': Fraction(14, 23), 'A7/A6': Fraction(23, 21),
}
# 搵 X 值: 如果分子 = N_d−X₁, 分母 = N_d−X₂
for name, fr in ratios.items():
    n, d = fr.numerator, fr.denominator
    x1 = N_d - n
    x2 = N_d - d
    # X₁/X₂ 係咪 Fib/Lucas?
    def label(x):
        for i, f in enumerate(F):
            if f == x: return f"F_{i}"
        for i, l in enumerate(L):
            if l == x: return f"L_{i}"
        return None
    l1, l2 = label(x1), label(x2)
    print(f"   {name} = ({N_d}−{x1})/({N_d}−{x2}) = ({N_d}−{l1})/({N_d}−{l2})")

# ---------- 3. X 序列 ----------
print("\n3. 分子分母嘅 X 值 (N_d − X):")
X_vals = []
for name, fr in ratios.items():
    for pos, v in [('分子', fr.numerator), ('分母', fr.denominator)]:
        x = N_d - v
        X_vals.append(x)
        def label(x):
            for i, f in enumerate(F):
                if f == x: return f"F_{i}"
            for i, l in enumerate(L):
                if l == x: return f"L_{i}"
            return None
        print(f"   {name} {pos} = {v} → X = {x} ({label(x)})")

# ---------- 4. 連分數再檢查 ----------
print("\n4. 連分數結構 (級聯):")
for name, fr in ratios.items():
    cf = []
    x = fr.numerator/fr.denominator
    a = int(x)
    cf.append(a)
    for _ in range(6):
        if abs(x - a) < 1e-10: break
        x = 1/(x - a)
        a = int(x)
        cf.append(a)
    print(f"   {name} = {fr} → {cf}")

# ---------- 5. 關鍵: A2/A1 = 4/9 ----------
print("\n5. A2/A1 = 4/9 深層結構:")
print(f"   4 = L₃, 9 = ?")
print(f"   9 = L₂² = 3²")
print(f"   9 = N_d − X → X = 35 (唔係 Fib/Lucas)")
print(f"   但 4/9 = (2/3)²")
print(f"   2/3 = ?")
print(f"   2 = F₃, 3 = L₂ = F₄")
print(f"   4/9 = (F₃/L₂)² = (2/3)²")
print()
print(f"   ★ 4/9 = (F₃/F₄)² = (2/3)² — Fibonacci 比率平方!")
print(f"   2/3 = F₃/F₄ (相鄰 Fib 比)")
print(f"   而 F₃/F₄ = 2/3 ≈ 0.667, φ⁻¹ = 0.618")

# ---------- 6. 檢查其他比率係咪 Fib 比組合 ----------
print("\n6. 全部比率 Fib 比檢查:")
fib_ratios = {}
for i in range(2, 10):
    for j in range(2, 10):
        r = F[i]/F[j]
        fib_ratios[round(r, 4)] = f"F_{i}/F_{j}"
for name, fr in ratios.items():
    r = fr.numerator/fr.denominator
    closest = min(fib_ratios.keys(), key=lambda x: abs(x - r))
    dev = abs(closest - r)/r*100
    print(f"   {name} = {r:.4f} ≈ {fib_ratios[closest]} ({closest:.4f}) dev={dev:.1f}%")
