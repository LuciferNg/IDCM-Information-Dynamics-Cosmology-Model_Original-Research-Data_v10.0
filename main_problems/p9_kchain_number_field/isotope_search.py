#!/usr/bin/env python3
"""
★ 外推: beat 值同位素 + s=44 列 + s=33 列
==============================================
1. 找 beat 值近乎相等嘅 (i,j) 對 (< 0.0001 diff)
2. s=44 列 3 個 magic 格嘅 beat 關係
3. s=33 列 15 個無 label 格 — 候選
"""
from math import pi, sin
import csv
from collections import defaultdict

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'label': r['label'].strip()})
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

phys_set = {(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)}

print("="*72)
print("1. ★ 同位素搜索: beat 值近乎相等 (< 0.00005)")
print("="*72)
# 對所有拍頻 pair 比較
found = []
for a in range(len(pairs)):
    (i,j) = pairs[a]
    bv = beat(i,j)
    for b in range(a+1, len(pairs)):
        (k,l) = pairs[b]
        if (i,j) == (k,l): continue
        ov = beat(k,l)
        diff = abs(bv-ov)
        if diff < 0.00005:
            found.append((diff, (i,j), (k,l), bv, ov))
found.sort()
# 去重: 只保留 (i,j) 同 (k,l) 唔係同一對
seen_pairs = set()
for diff, (i,j), (k,l), bv, ov in found:
    key = tuple(sorted([(i,j),(k,l)]))
    if key not in seen_pairs:
        seen_pairs.add(key)
        pi_def = "P" if (i,j) in phys_set else "N"
        pj_def = "P" if (k,l) in phys_set else "N"
        print(f"  差={diff:.8f}  beat({i:2d},{j:2d})={bv:.8f}[{pi_def}]  ≈  beat({k:2d},{l:2d})={ov:.8f}[{pj_def}]")

print("\n" + "="*72)
print("2. s=44 列 — 3 個 magic 格嘅 beat 關係")
print("="*72)
s44_magic = [(15,29,14,"GEN"), (12,32,20,"TRANSFER"), (11,33,22,"HALF")]
for i,j,d,name in s44_magic:
    bv = beat(i,j)
    print(f"  ({i:2d},{j:2d}) d={d:2d} {name:10s} beat={bv:.8f}")
print("\n  beat 比例:")
for a in range(len(s44_magic)):
    for b in range(a+1, len(s44_magic)):
        ra = beat(s44_magic[a][0], s44_magic[a][1])
        rb = beat(s44_magic[b][0], s44_magic[b][1])
        print(f"  {s44_magic[a][3]:10s}/{s44_magic[b][3]:10s} = {ra/rb:.6f}")

print("\n" + "="*72)
print("3. s=33 列 — 15 個無 label 格候選")
print("="*72)
s33 = [(i,33-i) for i in range(1,17)]
for i,j in s33:
    if i >= j: continue
    bv = beat(i,j)
    # 檢查 atlas
    label = ""
    for r in rows:
        if r['n'] == i and r['m'] == j and r['label']:
            label = r['label']
            break
    print(f"  ({i:2d},{j:2d}) d={j-i:2d} beat={bv:.8f}  label={label if label else '無'}")

print("\n" + "="*72)
print("4. ★ 所有 s=33 格嘅 beat 值 vs 物理常數")
print("="*72)
constants = {
    "m_μ/m_τ": 1.12717067, "m_s/m_d": 1.34282889, "n/p": 0.81510847,
    "c/s": 0.85074845, "m_c/m_b": 1.28429395, "u/d": 0.81257079,
    "t/b": 0.59282105, "m_H/m_W": 0.69935572, "m_W/m_Z": 0.23318262,
    "2−√2": 0.58578644, "√2": 1.41421356, "γ_1": 0.00127396
}
for i,j in s33:
    if i >= j: continue
    bv = beat(i,j)
    for cname, cv in constants.items():
        if abs(bv/cv - 1) < 0.01:
            print(f"  ({i:2d},{j:2d}) d={j-i:2d} beat={bv:.8f} ≈ {cname:15s} = {cv:.8f}  (差 {abs(bv/cv-1)*100:.3f}%)")