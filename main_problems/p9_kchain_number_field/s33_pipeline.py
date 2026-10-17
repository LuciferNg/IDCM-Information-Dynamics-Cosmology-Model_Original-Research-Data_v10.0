#!/usr/bin/env python3
"""
★ s=33 (M-pipeline) 列 — 16 個 pipeline 階段
==============================================
s=33 = M-pipeline 列, 16 格 (d=奇數 1..31)
只有 (13,20) d=7 有 label (Row m7 anchor)
其他 15 格可能係 pipeline 階段!

目標: 睇佢哋嘅 beat 值有冇形成「光譜」— 等差/等比/特殊間隔
"""
from math import pi, sin

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# s=33 列: (i,j) where i+j=33, i<j
s33 = [(i, 33-i) for i in range(1, 17)]  # i=1..16, j=32..17
s33 = [(i,j) for i,j in s33 if i < j]  # 保證 i<j

print("="*72)
print("★ s=33 (M-pipeline) 列 — 16 個階段")
print("="*72)
print(f"{'d':>3s} | {'(i,j)':10s} | {'beat':12s} | {'diff':12s} | {'ratio':12s} | label")
print("-"*72)
prev = None
for i,j in sorted(s33, key=lambda x: x[0]):
    bv = beat(i,j)
    d = j-i
    diff = bv - prev if prev else 0
    ratio = bv/prev if prev else 0
    # 檢查 atlas
    label = ""
    import csv
    with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if int(r['n'])==i and int(r['m'])==j and r['label'].strip():
                label = r['label'].strip()
    print(f"{d:3d} | ({i:2d},{j:2d})  | {bv:.8f} | {diff:+.8f} | {ratio:.6f} | {label if label else '無'}")
    prev = bv

print("\n" + "="*72)
print("2. ★ beat 值間隔分析 — 係咪等差?")
print("="*72)
beats = [beat(i,j) for i,j in sorted(s33, key=lambda x: x[0])]
diffs = [beats[k+1]-beats[k] for k in range(len(beats)-1)]
print(f"平均間隔: {sum(diffs)/len(diffs):.8f}")
print(f"間隔標準差: {(__import__('statistics').stdev(diffs)):.8f}")
print(f"最大間隔: {max(diffs):.8f}")
print(f"最小間隔: {min(diffs):.8f}")
print(f"變異係數: {__import__('statistics').stdev(diffs)/sum(diffs)*len(diffs)*100:.2f}%")
# 檢查係咪接近等差: 每個間隔同平均間隔嘅差
avg = sum(diffs)/len(diffs)
print(f"\n間隔 vs 平均 ({avg:.8f}) 偏差:")
for k, d in enumerate(diffs):
    print(f"  d={2*k+1:2d}→{2*k+3:2d}: {d:.8f}  (偏差 {d-avg:+.8f})")

print("\n" + "="*72)
print("3. ★ s=33 列 beat 值 vs 已知常數")
print("="*72)
constants = {
    "m_W/m_Z": 0.23318262, "γ_1": 0.00127396, "2−√2": 0.58578644,
    "√2": 1.41421356, "φ": 1.61803399, "π/4": 0.78539816,
    "π/2": 1.57079633, "1/√2": 0.70710678, "√3/2": 0.86602540,
    "m_μ/m_τ": 1.12717067, "m_s/m_d": 1.34282889, "n/p": 0.81510847,
    "c/s": 0.85074845, "m_c/m_b": 1.28429395, "u/d": 0.81257079,
    "t/b": 0.59282105, "m_H/m_W": 0.69935572
}
for i,j in sorted(s33, key=lambda x: x[0]):
    bv = beat(i,j)
    print(f"\n  ({i:2d},{j:2d}) d={j-i:2d} beat={bv:.8f}")
    for cname, cv in sorted(constants.items(), key=lambda x: abs(bv/x[1]-1)):
        if abs(bv-cv) < 0.01:
            print(f"    ≈ {cname:15s} = {cv:.8f}  (值差 {abs(bv-cv):.6f})")

print("\n" + "="*72)
print("4. ★ s=33 列 beat 值嘅『線性回歸』")
print("="*72)
# beat ≈ a + b×d?
ds = [j-i for i,j in sorted(s33, key=lambda x: x[0])]
n = len(ds)
sum_x = sum(ds)
sum_y = sum(beats)
sum_xy = sum(d*b for d,b in zip(ds, beats))
sum_xx = sum(d*d for d in ds)
b = (n*sum_xy - sum_x*sum_y)/(n*sum_xx - sum_x*sum_x)
a = (sum_y - b*sum_x)/n
print(f"beat ≈ {a:.6f} + {b:.6f} × d")
print(f"預測 vs 實際:")
for k, (i,j) in enumerate(sorted(s33, key=lambda x: x[0])):
    pred = a + b*ds[k]
    print(f"  d={ds[k]:2d}: 實際 {beats[k]:.8f}  預測 {pred:.8f}  偏差 {beats[k]-pred:+.8f}")