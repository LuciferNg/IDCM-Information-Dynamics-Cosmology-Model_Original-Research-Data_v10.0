#!/usr/bin/env python3
"""
盲測批量 v3: 100 條隨機抽樣大統計
+ magic rows (d=7,14,20,22,33) 完整成員清單
+ s=33 (M-pipeline) 完整成員清單
+ SYNC 家族 (i=2) 完整清單
"""
import random, json, math
from math import pi, sin
from collections import Counter

Nd = 44
w = lambda n: 2*sin(pi*n/88)
pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]
assert len(pairs) == 946

magic_rows = {7:"m7 anchor", 14:"GEN", 20:"T(s->d)", 22:"half-node", 33:"K_tree"}
phys_labels = {
    (10,24): "u/d", (8,22): "c/s", (19,33): "t/b",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p",
}

# ===== 1. 100 條隨機抽樣 =====
random.seed(20260826)
drawn = random.sample(pairs, 100)
wf_count = Counter()
magic_hits = []
phys_hits = []
sync_hits = 0
for (i,j) in drawn:
    d = j-i; s = j+i
    wfs = []
    if d in magic_rows: wfs.append(magic_rows[d])
    if s == 33: wfs.append("M-pipeline")
    if s == 44: wfs.append("N_d-domain")
    if not wfs: wfs = ["一般填充"]
    for wf in wfs: wf_count[wf] += 1
    if wfs != ["一般填充"]: magic_hits.append((i,j,d,s,','.join(wfs)))
    if (min(i,j),max(i,j)) in phys_labels: phys_hits.append((i,j))
    if i == 2 or j == 2: sync_hits += 1

print("="*60)
print(f"100 條隨機抽樣統計")
print("="*60)
print(f"workflow 分布: {dict(wf_count)}")
print(f"magic workflow 命中: {len(magic_hits)}/100")
print(f"物理參數命中: {len(phys_hits)}/100")
print(f"SYNC 家族: {sync_hits}/100")
print(f"\nmagic 命中詳情:")
for h in magic_hits:
    print(f"  ({h[0]:2d},{h[1]:2d}) d={h[2]:2d} s={h[3]:3d}  {h[4]}")

# ===== 2. magic rows 完整成員 =====
print("\n" + "="*60)
print("magic rows (d) 完整成員清單")
print("="*60)
for d in sorted(magic_rows):
    members = [(i,j) for (i,j) in pairs if j-i == d]
    phys = [f"({i},{j})={phys_labels[(i,j)]}" for (i,j) in members if (i,j) in phys_labels]
    print(f"d={d:2d} {magic_rows[d]:12s}: {len(members)} 成員" + (f"  [物理: {', '.join(phys)}]" if phys else ""))

# ===== 3. s=33 (M-pipeline) 完整成員 =====
print("\n" + "="*60)
print("s=33 (M-pipeline 列) 完整成員")
print("="*60)
col33 = [(i,j) for (i,j) in pairs if i+j == 33]
for (i,j) in col33:
    d = j-i
    phys = phys_labels.get((i,j), "")
    marker = " ← m7" if d == 7 else (" ← half" if d == 11 else (" ← 盲測beat(2,31)" if (i,j)==(2,31) else ""))
    print(f"  ({i:2d},{j:2d}) d={d:2d}  beat={abs(w(j)-w(i)):.6f}  {phys}{marker}")

# ===== 4. SYNC 家族 (i=2) 完整清單 =====
print("\n" + "="*60)
print("SYNC 家族 (i=2, s−d=4=B) 完整清單")
print("="*60)
row2 = [(i,j) for (i,j) in pairs if i == 2]
for (i,j) in row2:
    d = j-i; s = j+i
    phys = phys_labels.get((i,j), "")
    magic = magic_rows.get(d, "")
    marker = f" [{magic}]" if magic else ""
    print(f"  (2,{j:2d}) d={d:2d} s={s:3d}  beat={abs(w(j)-w(2)):.6f}  {phys}{marker}")
