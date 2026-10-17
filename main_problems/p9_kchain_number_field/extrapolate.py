#!/usr/bin/env python3
"""
★ 外推: 由已知元素找新元素候選
=================================
方法: 已知 9 個物理拍頻 + 5 個 magic rows
      在拍頻值空間找「近鄰」(值相近但未用)
      在 (d,s) 空間找「對稱位」(互補/對偶)
"""
from math import pi, sin

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

# 已知物理拍頻
phys = {
    (1,18): "m_μ/m_τ", (1,22): "m_s/m_d", (7,20): "n/p",
    (8,22): "c/s", (8,33): "m_c/m_b", (10,24): "u/d",
    (19,33): "t/b", (19,38): "m_H/m_W", (30,41): "m_W/m_Z"
}
phys_set = set(phys.keys())

print("="*72)
print("1. 外推 A: 值空間近鄰 — 離已知物理拍頻最近嘅『未用』拍頻")
print("="*72)
for (p_i,p_j), pname in sorted(phys.items(), key=lambda x: beat(x[0][0],x[0][1])):
    pv = beat(p_i,p_j)
    # 找最近嘅 5 個未用拍頻
    neighbors = []
    for (i,j) in pairs:
        if (i,j) in phys_set: continue
        bv = beat(i,j)
        diff = abs(bv-pv)
        neighbors.append((diff, i, j, bv))
    neighbors.sort()
    print(f"\n  {pname:20s} beat({p_i},{p_j}) = {pv:.8f}")
    for diff, i, j, bv in neighbors[:5]:
        print(f"    → beat({i:2d},{j:2d}) = {bv:.8f}  (差 {diff:.6f})")

print("\n" + "="*72)
print("2. 外推 B: (d,s) 空間對偶 — 每對已知物理拍頻嘅『對偶點』")
print("="*72)
# 對偶: (i,j) ↔ (44−j, 44−i) — 保持 d 不變, s 變 88−s
for (i,j), pname in sorted(phys.items(), key=lambda x: x[0][0]):
    di = 44-j
    dj = 44-i
    if di < dj:
        pv = beat(i,j)
        dv = beat(di, dj)
        print(f"  {pname:20s} ({i:2d},{j:2d}) d={j-i:2d} s={i+j:3d} beat={pv:.8f}")
        used = (di,dj) in phys_set
        print(f"    對偶 (44−j,44−i) = ({di:2d},{dj:2d}) d={dj-di:2d} s={di+dj:3d} beat={dv:.8f} {'[已知!]' if used else '[未用]'}")

print("\n" + "="*72)
print("3. 外推 C: s 列掃描 — 每條 s 列嘅『特殊密度』")
print("="*72)
from collections import Counter
s_phys = Counter(s for (i,j) in phys_set for s in [i+j])
s_magic = {}
for (i,j) in pairs:
    d = j-i
    if d in [7,14,20,22,33]:
        s_magic[j+i] = s_magic.get(j+i, 0) + 1
print("s 列物理格密度:")
for s in sorted(s_phys):
    cnt = s_phys[s]
    print(f"  s={s:3d}: {cnt} 個物理格")
print("\ns 列 magic row 密度 (top 10):")
for s, cnt in sorted(s_magic.items(), key=lambda x: -x[1])[:10]:
    print(f"  s={s:3d}: {cnt} 個 magic 成員")

print("\n" + "="*72)
print("4. 外推 D: 已知元素嘅 d 值週期")
print("="*72)
phys_d = sorted(set(j-i for (i,j) in phys_set))
print(f"物理格 d 值: {phys_d}")
print(f"d 值差分: {[phys_d[k+1]-phys_d[k] for k in range(len(phys_d)-1)]}")
print(f"平均間隔: {sum(phys_d[k+1]-phys_d[k] for k in range(len(phys_d)-1))/max(1,len(phys_d)-1):.2f}")
# 檢查 d 值模 2, 模 4
print(f"d mod 2: {[d%2 for d in phys_d]}")
print(f"d mod 4: {[d%4 for d in phys_d]}")
# 檢查 d 值在低次數端點集?
low_d = [d for d in range(1,44) if d%2==0 or d in [11,33]]
print(f"物理 d 在低次數端點集? {[d for d in phys_d if d in low_d]}")

print("\n" + "="*72)
print("5. 外推 E: s 值模分析")
print("="*72)
phys_s = sorted([i+j for (i,j) in phys_set])
print(f"物理格 s 值: {phys_s}")
print(f"s 值差分: {[phys_s[k+1]-phys_s[k] for k in range(len(phys_s)-1)]}")
print(f"s mod 4: {[s%4 for s in phys_s]}")
print(f"s mod 8: {[s%8 for s in phys_s]}")