#!/usr/bin/env python3
"""
★ 外推: 所有 magic rows 嘅「族」結構
========================================
GEN 行 (d=14) 有 6 格 quark 族
其他 magic rows 有冇類似嘅「族」?
"""
from math import pi, sin
import csv
from collections import defaultdict

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# 讀 atlas
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'deg_diff': int(r['deg_diff']),
                     'label': r['label'].strip()})
pairs = [r for r in rows if r['n'] < r['m']]

# 已知物理格
phys = {
    (1,18): "m_μ/m_τ", (1,22): "m_s/m_d", (7,20): "n/p",
    (8,22): "c/s", (8,33): "m_c/m_b", (10,24): "u/d",
    (19,33): "t/b", (19,38): "m_H/m_W", (30,41): "m_W/m_Z"
}
phys_set = set(phys.keys())

magic_rows = {7: "ANCHOR", 14: "GEN", 20: "TRANSFER", 22: "HALF", 33: "KTREE"}
special_cols = [33, 44, 22, 11, 88]

print("="*72)
print("1. 逐一檢視 magic rows 嘅「特殊格」")
print("="*72)
for d, name in magic_rows.items():
    members = [r for r in pairs if r['d'] == d]
    print(f"\n★ d={d:2d} ({name:10s}) — {len(members)} 成員")
    # 有 label 嘅格
    labeled = [r for r in members if r['label']]
    print(f"   有 label: {len(labeled)} 格")
    for r in labeled:
        print(f"     ({r['n']:2d},{r['m']:2d}) s={r['s']:3d} beat={beat(r['n'],r['m']):.8f}  {r['label']}")
    # 有特殊 s 值嘅格
    for col in special_cols:
        col_members = [r for r in members if r['s'] == col and not r['label']]
        if col_members:
            for r in col_members:
                print(f"    s={col:3d} col: ({r['n']:2d},{r['m']:2d}) beat={beat(r['n'],r['m']):.8f} [未label]")
    # 對偶檢查: 已知物理格嘅對偶係咪喺呢行?
    for (i,j), pname in phys.items():
        di, dj = 44-j, 44-i
        if di >= dj: continue
        if dj-di == d:
            print(f"    ★ 對偶: ({di:2d},{dj:2d}) s={di+dj:3d} beat={beat(di,dj):.8f}  dual({pname})")

print("\n" + "="*72)
print("2. s=33 (M-pipeline) 列 — 特殊列全面掃描")
print("="*72)
s33 = [(r['n'], r['m'], r['d'], r['s'], r['label']) for r in pairs if r['s'] == 33]
print(f"s=33 列: {len(s33)} 成員")
for n,m,d,s,lbl in sorted(s33, key=lambda x: x[2]):
    bv = beat(n,m)
    print(f"  ({n:2d},{m:2d}) d={d:2d} beat={bv:.8f}  label={lbl if lbl else '無'}")

print("\n" + "="*72)
print("3. s=44 (N_d) 列 — 特殊列全面掃描")
print("="*72)
s44 = [(r['n'], r['m'], r['d'], r['s'], r['label']) for r in pairs if r['s'] == 44]
print(f"s=44 列: {len(s44)} 成員")
for n,m,d,s,lbl in sorted(s44, key=lambda x: x[2]):
    bv = beat(n,m)
    print(f"  ({n:2d},{m:2d}) d={d:2d} beat={bv:.8f}  label={lbl if lbl else '無'}")

print("\n" + "="*72)
print("4. s=22 (half-sum) 列 — 特殊列全面掃描")
print("="*72)
s22 = [(r['n'], r['m'], r['d'], r['s'], r['label']) for r in pairs if r['s'] == 22]
print(f"s=22 列: {len(s22)} 成員")
for n,m,d,s,lbl in sorted(s22, key=lambda x: x[2]):
    bv = beat(n,m)
    print(f"  ({n:2d},{m:2d}) d={d:2d} beat={bv:.8f}  label={lbl if lbl else '無'}")

print("\n" + "="*72)
print("5. ★ 由 magic rows 找新族: 按 beat 值分組")
print("="*72)
# 每個 magic row 嘅 beat 值分佈
for d, name in magic_rows.items():
    members = [r for r in pairs if r['d'] == d]
    beats = sorted([beat(r['n'], r['m']) for r in members])
    print(f"\n★ d={d:2d} ({name:10s}) beat 值範圍: {beats[0]:.4f} .. {beats[-1]:.4f}")
    # 睇有冇 beat 值接近已知物理常數
    known_beats = [(1,18,1.12717067),(1,22,1.34282889),(7,20,0.81510847),
                   (8,22,0.85074845),(8,33,1.28429395),(10,24,0.81257079),
                   (19,33,0.59282105),(19,38,0.69935572),(30,41,0.23318262)]
    for (i,j), pname in phys.items():
        pv = beat(i,j)
        for r in members:
            bv = beat(r['n'], r['m'])
            if abs(bv-pv) < 0.01 and (r['n'],r['m']) not in phys_set:
                print(f"    近 {pname:15s}: ({r['n']:2d},{r['m']:2d}) beat={bv:.8f} 差 {abs(bv-pv):.6f}")