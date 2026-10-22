#!/usr/bin/env python3
"""
O9-C1: 振幅級聯數字嘅 IDCM 結構分解
=====================================
對每個級聯數字 (分子/分母) 搵 IDCM 結構表達:
- N_d = 44 (K_chain)
- M = 33 (K_tree)
- Fib: F_n = 1,1,2,3,5,8,13,21,34...
- Lucas: L_n = 2,1,3,4,7,11,18,29,47...
- 組合: N_d−X, M−X, X±Y, a×b

級聯數字 (全部出現喺比率):
比率: 4/9, 1/1, 11/26, 15/13, 14/23, 23/21
歸一化: 1/1, 4/9, 18/41, 5/27, 3/14, 3/23, 1/7

獨特數字: 1, 3, 4, 5, 7, 9, 11, 13, 14, 15, 18, 21, 23, 26, 27, 41
"""
from fractions import Fraction

print("="*80)
print("O9-C1: 級聯數字 IDCM 結構分解")
print("="*80)

# Fib / Lucas
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
N_d, M = 44, 33

def fib_idx(x):
    for i, v in enumerate(F):
        if v == x: return i
    return None

def luc_idx(x):
    for i, v in enumerate(L):
        if v == x: return i
    return None

def describe(n):
    """搵最靚嘅 IDCM 結構表達"""
    out = []
    # 直接 Fib/Lucas
    fi = fib_idx(n)
    if fi is not None and fi >= 1:
        out.append(f"F_{fi}")
    li = luc_idx(n)
    if li is not None:
        out.append(f"L_{li}")
    # N_d − X
    for label, seq, name in [("F", F, "Fib"), ("L", L, "Lucas")]:
        for i, x in enumerate(seq):
            if x > 0 and N_d - x == n:
                out.append(f"N_d−{name}_{i}({x})")
            if x > 0 and M - x == n:
                out.append(f"M−{name}_{i}({x})")
            if x > 0 and x - n in (F[1:10] + L[1:10]):
                out.append(f"{name}_{i}({x})−{x-n}")
    # 乘積
    for a in F[2:9] + L[1:9]:
        for b in F[2:9] + L[1:9]:
            if a*b == n:
                out.append(f"{a}×{b}")
    # 平方
    for a in F[2:9] + L[1:9]:
        if a*a == n:
            out.append(f"{a}²")
    return out

numbers = [1, 3, 4, 5, 7, 9, 11, 13, 14, 15, 18, 21, 23, 26, 27, 41]
print("\n數字分解表:")
for n in numbers:
    descs = describe(n)
    # 過濾: 只留最靚 (優先 F/L 直接, 然後 N_d−X, M−X)
    print(f"   {n:>2}: {', '.join(descs) if descs else '—'}")

print("\n" + "-"*80)
print("重點檢查:")
print("-"*80)
# 23 嘅分解
print("23 出現 3 次 (14/23, 23/21, 3/23):")
for d in describe(23):
    print(f"   23 = {d}")
# 41
print("\n41 (18/41 分母):")
for d in describe(41):
    print(f"   41 = {d}")
# 26
print("\n26 (11/26 分母):")
for d in describe(26):
    print(f"   26 = {d}")
# 15
print("\n15 (15/13 分子):")
for d in describe(15):
    print(f"   15 = {d}")
# 14
print("\n14 (14/23 分子):")
for d in describe(14):
    print(f"   14 = {d}")

print("\n" + "="*80)
print("結構歸納:")
print("="*80)
print("""
已確認乾淨結構 (優先排序):
  21 = F₈ (F₈ = 21)
  13 = F₇
  18 = L₆
  11 = L₅
  7  = L₄
  4  = L₃
  3  = L₂ = F₄
  5  = F₅

  N_d−X 形式:
  26 = N_d−L₆ = 44−18
  23 = N_d−F₈ = 44−21
  15 = N_d−L₇ = 44−29
  41 = N_d−L₂ = 44−3

  有待解釋: 9 (4/9 分母), 27 (5/27 分母), 14 (14/23 分子)
  14 = L₆−L₃ = 18−4 ??
  9  = L₂² = 3² ?? 或者 N_d−F₅L₄ = 44−35 ??
  27 = L₂³ = 3³ ?? 或者 N_d−L₆+1 = 27 ??
""")
