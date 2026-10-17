#!/usr/bin/env python3
"""
★ 38 個未指派 opcode — 有冇隱藏結構?
========================================
方法: 對每個未指派 d, 睇佢同已指派 d 嘅 beat 值比例
      喺 s=44 (偶數) 同 s=33 (奇數) pipeline 入面
"""
from math import pi, sin

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# 已指派 magic d
magic = {7:"ANCHOR", 14:"GEN", 20:"TRANSFER", 22:"HALF", 33:"KTREE"}
# 已指派 data d
data = {11:"m_W/Z", 13:"n/p", 17:"m_μ/τ", 19:"m_H/W", 21:"m_s/d", 25:"m_c/b"}
# 所有已指派
assigned = set(magic) | set(data)

# Pipeline 函數
def s44_beat(d):
    """s=44 列, d 必須偶數"""
    i = (44-d)//2
    j = 44-i
    return beat(i,j)

def s33_beat(d):
    """s=33 列, d 必須奇數 ≤31"""
    i = (33-d)//2
    j = 33-i
    return beat(i,j)

print("="*72)
print("1. 偶數 pipeline (s=44) — 未指派 d 同已指派 d 嘅比例")
print("="*72)
# 已指派偶數 d: 14, 20, 22
assigned_even = [14, 20, 22]
unassigned_even = [d for d in range(2, 43, 2) if d not in assigned_even]
print(f"已指派偶數: {assigned_even}")
print(f"未指派偶數: {unassigned_even}")
print()
for d in unassigned_even:
    bv = s44_beat(d)
    for ad in assigned_even:
        av = s44_beat(ad)
        ratio = bv/av
        # 檢查接近簡單有理數?
        for p,q in [(1,2),(1,3),(2,3),(1,4),(3,4),(1,5),(2,5),(3,5),(4,5),
                     (1,6),(5,6),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),
                     (1,8),(3,8),(5,8),(7,8)]:
            if abs(ratio - p/q) < 0.005:
                print(f"  d={d:2d} beat={bv:.6f}  / d={ad:2d} beat={av:.6f} = {ratio:.6f} ≈ {p}/{q}")

print("\n" + "="*72)
print("2. 奇數 pipeline (s=33) — 未指派 d 同已指派 d 嘅比例")
print("="*72)
assigned_odd = [7]
unassigned_odd = [d for d in range(1, 32, 2) if d not in assigned_odd]
print(f"已指派奇數: {assigned_odd}")
print(f"未指派奇數: {unassigned_odd}")
print()
for d in unassigned_odd:
    bv = s33_beat(d)
    ad = 7
    av = s33_beat(ad)
    ratio = bv/av
    for p,q in [(1,2),(1,3),(2,3),(1,4),(3,4),(1,5),(2,5),(3,5),(4,5),
                 (1,6),(5,6),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),
                 (1,8),(3,8),(5,8),(7,8),(1,9),(2,9),(4,9),(5,9),(7,9),(8,9)]:
        if abs(ratio - p/q) < 0.005:
            print(f"  d={d:2d} beat={bv:.6f}  / d=7 beat={av:.6f} = {ratio:.6f} ≈ {p}/{q}")

print("\n" + "="*72)
print("3. ★ 所有 pipeline 未指派 d 嘅『最佳比例』")
print("="*72)
print("(只顯示 < 0.5% 誤差)")
for d in range(1, 44):
    if d in assigned: continue
    if d % 2 == 0:  # 偶數 — s=44
        bv = s44_beat(d)
        for ad in assigned_even:
            av = s44_beat(ad)
            ratio = bv/av
            for p,q in [(1,2),(1,3),(2,3),(1,4),(3,4),(1,5),(2,5),(3,5),(4,5),
                         (1,6),(5,6),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),
                         (1,8),(3,8),(5,8),(7,8)]:
                if abs(ratio - p/q) < 0.003:
                    print(f"  d={d:2d} (偶) / d={ad:2d}({magic.get(ad,'?'):8s}) = {ratio:.6f} ≈ {p}/{q}  err={abs(ratio-p/q)*100:.3f}%")
    else:  # 奇數 ≤31 — s=33
        if d > 31: continue
        bv = s33_beat(d)
        av = s33_beat(7)
        ratio = bv/av
        for p,q in [(1,2),(1,3),(2,3),(1,4),(3,4),(1,5),(2,5),(3,5),(4,5),
                     (1,6),(5,6),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),
                     (1,8),(3,8),(5,8),(7,8)]:
            if abs(ratio - p/q) < 0.003:
                print(f"  d={d:2d} (奇) / d=7(ANCHOR) = {ratio:.6f} ≈ {p}/{q}  err={abs(ratio-p/q)*100:.3f}%")