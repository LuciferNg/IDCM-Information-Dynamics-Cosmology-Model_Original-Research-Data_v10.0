#!/usr/bin/env python3
"""
★ s=33 列結構分析 — 15 個未 label pipeline 階段
==================================================
返回 structural 方向: s=33 列 16 格, 只有 (13,20) 有 label
其他 15 格嘅 beat 值係咪有代數關係?
(所有 beat 值 ∈ ℚ(ζ₈₈)⁺, 所以任何關係都係代數結構)
"""
from math import pi, sin
from collections import defaultdict
import csv

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# 讀 atlas
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'label': r['label'].strip()})
pairs = [r for r in rows if r['n'] < r['m']]

# s=33 列
s33 = [(i, 33-i) for i in range(1, 17)]
s33 = [(i,j) for i,j in s33 if i < j]

# 已知物理格
phys = {(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)}

print("="*72)
print("1. s=33 列 16 階段 — beat 值結構")
print("="*72)
print(f"{'d':>3s} | {'(i,j)':10s} | {'beat':12s} | {'差(d)':10s} | 二階差 | label")
print("-"*72)
beats = []
prev_b = None
prev_d = None
for i,j in sorted(s33, key=lambda x: x[0]):
    bv = beat(i,j)
    d = j-i
    beats.append(bv)
    label = ""
    for r in rows:
        if r['n']==i and r['m']==j and r['label']:
            label = r['label']
            break
    # 一階差
    if prev_b:
        diff1 = bv - prev_b
        # 二階差
        if prev_d is not None:
            diff2 = diff1 - prev_d
            print(f"{d:3d} | ({i:2d},{j:2d})  | {bv:.8f} | {diff1:+.8f} | {diff2:+.8f} | {label if label else '無'}")
        else:
            print(f"{d:3d} | ({i:2d},{j:2d})  | {bv:.8f} | {diff1:+.8f} |         | {label if label else '無'}")
        prev_d = diff1
    else:
        print(f"{d:3d} | ({i:2d},{j:2d})  | {bv:.8f} |         |         | {label if label else '無'}")
    prev_b = bv

print("\n" + "="*72)
print("2. ★ 二階差分析 — 係咪二次曲線?")
print("="*72)
# 二階差如果接近常數 → 二次曲線
# 如果二階差接近 0 → 線性
diffs2 = [beats[k+2]-2*beats[k+1]+beats[k] for k in range(len(beats)-2)]
print(f"二階差範圍: {min(diffs2):.8f} .. {max(diffs2):.8f}")
print(f"二階差平均: {sum(diffs2)/len(diffs2):.8f}")
print(f"二階差標準差: {__import__('statistics').stdev(diffs2):.8f}")
# 如果二階差接近常數, 係二次曲線
if max(diffs2)-min(diffs2) < 0.001:
    print("→ 二階差接近常數: beat(d) 係二次函數!")
else:
    print(f"→ 二階差變化 {max(diffs2)-min(diffs2):.6f}: 唔係純二次")

print("\n" + "="*72)
print("3. ★ s=33 列 beat 值嘅代數關係")
print("="*72)
# 檢查: beat 值之間嘅比例係咪簡單有理數?
print("beat 比例接近簡單有理數 (1/2, 2/3, 3/4, 4/5, 5/6):")
for a in range(len(s33)):
    for b in range(a+1, len(s33)):
        ra = beats[a]
        rb = beats[b]
        ratio = ra/rb if rb != 0 else 0
        targets = [(1,2),(2,3),(3,4),(4,5),(5,6),(2,1),(3,2),(4,3),(5,4),(6,5)]
        for p,q in targets:
            if abs(ratio - p/q) < 0.001:
                ia,ja = s33[a]
                ib,jb = s33[b]
                print(f"  beat({ia:2d},{ja:2d})/beat({ib:2d},{jb:2d}) = {ratio:.6f} ≈ {p}/{q}")

print("\n" + "="*72)
print("4. ★ s=33 列 vs 已知物理格 — 有冇 d 值對應?")
print("="*72)
# 已知物理格嘅 d 值: [11,13,14,14,14,17,19,21,25]
# s=33 列嘅 d 值: [1,3,5,...,31] (奇數)
# 檢查: 物理格嘅 d 值係咪某啲 s=33 階段?
phys_d = set(j-i for (i,j) in phys)
s33_d = set(j-i for (i,j) in s33)
print(f"物理格 d 值: {sorted(phys_d)}")
print(f"s=33 列 d 值: {sorted(s33_d)}")
overlap = phys_d & s33_d
print(f"交集: {sorted(overlap)}")
if overlap:
    for d in sorted(overlap):
        # 搵對應嘅 (i,j)
        for (i,j) in phys:
            if j-i == d:
                print(f"  d={d:2d}: 物理格 ({i:2d},{j:2d}) beat={beat(i,j):.8f}")
        for (i,j) in s33:
            if j-i == d:
                print(f"  d={d:2d}: s=33 格 ({i:2d},{j:2d}) beat={beat(i,j):.8f}")

print("\n" + "="*72)
print("5. ★ s=33 列 15 個未 label 格 — 結構候選")
print("="*72)
print("""
  s=33 列 (M-pipeline) 有 16 個階段, d=1..31 奇數:
  
  d=31 (1,32)  beat=1.74788  ← 最大
  d=29 (2,31)  beat=1.64577
  d=27 (3,30)  beat=1.54157
  ...
  d=7  (13,20) beat=0.41449  ← 唯一有 label (m7 anchor)
  ...
  d=1  (16,17) beat=0.05936  ← 最小
  
  beat 值隨 d 遞增而近乎線性增加
  → 16 個 pipeline 階段, 每個階段有特定嘅 beat 值!
  
  已知: d=7 (m7 anchor) 係 IDCM 結構常數
  其餘 15 個可能係 pipeline 其他階段嘅「錨點」
""")