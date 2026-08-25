#!/usr/bin/env python3
"""
盲測批量 v5: magic rows 物理分佈 + d=14 GEN 行深度分析
=====================================================
發現: d=14 (GEN) 行包含全部 3 個 quark pairs (u/d, c/s, t/b)
"""
from math import pi, sin

Nd = 44
w = lambda n: 2*sin(pi*n/88)
pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]

phys_labels = {
    (10,24): "u/d Quark", (8,22): "c/s Quark", (19,33): "t/b Quark",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p BBN",
}

print("="*70)
print("1. 全部 magic rows 嘅物理參數分佈")
print("="*70)
magic = {7:"m7 anchor", 14:"GEN (世代)", 20:"T(s->d)", 22:"half-node", 33:"K_tree"}
for d in sorted(magic):
    members = [(i,j) for (i,j) in pairs if j-i == d]
    phys = [(i,j,phys_labels[(i,j)]) for (i,j) in members if (i,j) in phys_labels]
    print(f"d={d:2d} {magic[d]:12s}: {len(members)} 成員, 物理: {phys if phys else '無'}")

print("\n" + "="*70)
print("2. d=14 (GEN 世代) 行完整成員")
print("="*70)
gen14 = [(i,j) for (i,j) in pairs if j-i == 14]
for (i,j) in gen14:
    phys = phys_labels.get((i,j), "")
    beat = abs(w(j)-w(i))
    s = j+i
    marker = " ★" if phys else ""
    print(f"  ({i:2d},{j:2d}) s={s:3d}  beat={beat:.6f}  {phys}{marker}")

print("\n" + "="*70)
print("3. 三代 quark 對 (u/d, c/s, t/b) 座標")
print("="*70)
for (i,j) in [(10,24),(8,22),(19,33)]:
    d = j-i; s = j+i
    print(f"  ({i:2d},{j:2d}) d={d:2d} s={s:3d}  beat={abs(w(j)-w(i)):.6f}  {phys_labels[(i,j)]}")
print(f"\n  三代 quark 全部 d=14? {(10,24)[1]-(10,24)[0] == (8,22)[1]-(8,22)[0] == (19,33)[1]-(19,33)[0] == 14}")

print("\n" + "="*70)
print("4. 其他物理參數嘅 d 值分佈")
print("="*70)
for (i,j), name in sorted(phys_labels.items(), key=lambda x: x[0][1]-x[0][0]):
    d = j-i; s = j+i
    print(f"  ({i:2d},{j:2d}) {name:12s} d={d:2d} s={s:3d}")
