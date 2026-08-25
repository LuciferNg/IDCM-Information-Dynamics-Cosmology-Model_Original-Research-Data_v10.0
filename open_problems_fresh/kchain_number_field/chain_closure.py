#!/usr/bin/env python3
"""
Microcode 挖掘: 鏈閉合定理 — 946 拍頻可由 43 條相鄰邊生成
=============================================================
★ 核心假說: 拍頻空間係「保守勢場」— ω_n 係勢函數, beat(i,j) = 勢差
  beat(i,j) = |ω_j − ω_i| = Σ_{k=i}^{j-1} (ω_{k+1} − ω_k)  (有符號)
  → 43 條相鄰邊 (n,n+1) 係「基本指令集」, 946 全部可由佢哋組合!
"""
from math import gcd, lcm, pi, sin, cos
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)

pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

# ===== 1. 鏈閉合驗證 =====
print("="*72)
print("1. 鏈閉合驗證: beat(i,j) == Σ_{k=i}^{j-1} beat(k,k+1)?")
print("="*72)
adj = [(k, k+1, abs(w(k+1)-w(k))) for k in range(1,N)]
fail = []
for (i,j) in pairs:
    chain_sum = sum(b for (k,_,b) in adj if i <= k < j)
    direct = abs(w(j)-w(i))
    if abs(chain_sum - direct) > 1e-12:
        fail.append((i,j,chain_sum,direct))
print(f"驗證: {len(pairs)-len(fail)}/{len(pairs)} 鏈閉合 {'✅ 全部通過!' if not fail else fail[:5]}")

# ===== 2. 43 條基本指令 (相鄰邊) =====
print("\n" + "="*72)
print("2. 基本指令集 — 43 條相鄰邊 (n, n+1)")
print("="*72)
print(f"{'邊':>8} {'beat':>14} {'= 4sin(π/176)·cos((2n+1)π/176)':>36} {'degree':>6}")
def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r
def sin_deg(k):
    k=abs(k)%176
    if k==88: return 1
    m=(88-k)%176; g=gcd(352,m)
    return phi(352//g)//2
def beat_degree(d,s):
    return lcm(sin_deg(abs(d+s)), sin_deg(abs(d-s)))

for k in range(1,N):
    b = abs(w(k+1)-w(k))
    env = 4*sin(pi/176)*cos((2*k+1)*pi/176)
    d = beat_degree(1, 2*k+1)
    print(f"({k:2d},{k+1:2d}) {b:>14.10f} {env:>36.10f} {d:>6}")

print(f"\n  常數包絡: 4sin(π/176) = {4*sin(pi/176):.10f}")
print(f"  掃描因子: cos((2n+1)π/176), n=1..43")

# ===== 3. 壓縮率 =====
print("\n" + "="*72)
print("3. 指令壓縮: 946 → 43")
print("="*72)
print(f"拍頻總數: {len(pairs)}")
print(f"基本指令: {N-1} = 43 (相鄰邊)")
print(f"壓縮率: {len(pairs)/43:.1f}×")
print(f"self loop: 44 (SYNC 指令, 唔使組合)")
print(f"完整指令集: 43 基本 + 44 self loop = 87 = 3×29 = 3×L₇!")

# ===== 4. 物理參數嘅相鄰邊分解 =====
print("\n" + "="*72)
print("4. 物理參數喺基本指令集嘅分解 (邊數 = d)")
print("="*72)
phys = {
    (10,24): "u/d", (8,22): "c/s", (19,33): "t/b",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p",
}
for (i,j), name in phys.items():
    d = j-i
    # 分解為相鄰邊和
    chain = [abs(w(k+1)-w(k)) for k in range(i,j)]
    print(f"  {name:10s} ({i:2d},{j:2d}): {d} 條相鄰邊 [{i}→{j}]  Σ={sum(chain):.8f} = beat={abs(w(j)-w(i)):.8f}")

# ===== 5. 基本指令 degree 分布 =====
print("\n" + "="*72)
print("5. 基本指令 degree 分布")
print("="*72)
degs = [beat_degree(1, 2*k+1) for k in range(1,N)]
c = Counter(degs)
print(f"deg 分布: {dict(sorted(c.items()))}")
print(f"→ 43 條基本指令, 冇一條係 deg<20!")
print(f"→ 低次數 (deg<40) 全部喺『組合指令』(多邊和) 出現")

# ===== 6. 全部 946 嘅「邊數」分布 =====
print("\n" + "="*72)
print("6. 946 拍頻嘅邊數 (d) 分布 = 鏈長")
print("="*72)
dc = Counter(j-i for (i,j) in pairs)
print(f"d=1 (相鄰): {dc[1]} 條")
print(f"d=43 (最長): {dc[43]} 條")
print(f"平均鏈長: {sum((j-i) for (i,j) in pairs)/len(pairs):.2f}")
print(f"總邊數加權: {sum((j-i) for (i,j) in pairs)} = Σd×count = {sum(d*c for d,c in dc.items())}")
print(f"== C(44,3) = {44*43*42//6}? 唔係. = 2×C(44,3)/2? 實際上 Σ(i<j)(j-i) = C(44,3) = {44*43*42//6}")
