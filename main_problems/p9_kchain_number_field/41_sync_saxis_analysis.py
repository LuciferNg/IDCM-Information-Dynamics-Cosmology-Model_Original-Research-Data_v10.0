#!/usr/bin/env python3
"""
41_sync_saxis_analysis.py — SYNC pipeline 攻堅 round2: s 軸全景 (2026-10-17)
=============================================================================
Round 1 (40 號) 發現:
  - (2,31): s=33 × d=29 唯一交叉 = i=2 SYNC 家族
  - s=33 列 d 對和 = 32 = 2B²
  - d=29 唔係 magic (R5 外 + TEST F) 已閉合

修正: 40 號 T5 member count off-by-one (range(1,44-d) 漏咗終點)
     正確: d=29 有 15 成員 (i=1..15, j=30..44); 06 文檔確認「d=7 37 個 vs d=29 15 個」

今輪 (s 軸 = workflow column):
  T1 修正: 全行 member count 正確表 (magic 行 + d=29)
  T2 s 軸全景: 每個 s∈[3,87] 有幾多 magic-d 格 / data-d 格 / R5-d 格?
     — 邊啲 s 係「重載 pipeline」(多 magic 格)?
  T3 s=33 (M-pipeline): 唯一 magic 格 = (13,20) d=7 — 驗證
  T4 SYNC 家族 (i=2 行): 42 格, 佢哋嘅 d/R5/magic 分佈 — 對比 i=4 (B) 行?
  T5 s=33 列 beat 值代數結構: mpmath 高精度探測 2cos/sqrt/已知常數
  T6 s 軸同 magic 關係: magic d 行嘅 s 值域 ∩ column s

零 import; 純整數 + mpmath 60dps。
"""
import json
from math import gcd
from collections import Counter, defaultdict

def gc(d):
    return gcd(abs(44 - d), 176)

def luc(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a
def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
R5GEN = sorted({m*a for a in (7, 11, 5) for m in (1, 2, 3, 4) if 1 <= m*a <= 43})
DATA_CELLS = {(30,41),(7,20),(8,22),(10,24),(19,33),(1,18),(19,38),(1,22),(8,33)}
DATA_CELL_DS = sorted({abs(i-j) for (i,j) in DATA_CELLS})

# ============ T1: 修正 member counts ============
print("=== T1: 行 member count 修正 (40 號 T5 off-by-one) ===")
print(f"{'d':>3} | {'正確成員數 (i=1..44−d)':>24} | mirror(44−d)")
for d in MAGIC + [29] + [11, 13, 17, 19, 21, 25]:
    n = 44 - d
    print(f"{d:>3} | {n:>24} | {44-d:>2}  {'(self)' if d==22 else ''}")
print("  ← 成員數 = 44−d = mirror partner (數數, 唔係發現)")

# ============ T2: s 軸全景 ============
print()
print("=== T2: s 軸 (workflow column) 全景 ===")
s_magic = defaultdict(list)
s_data = defaultdict(list)
s_r5 = defaultdict(list)
for i in range(1, 44):
    for j in range(i+1, 45):
        d = j - i
        s = i + j
        if d in MAGIC: s_magic[s].append((i, j, d))
        if d in DATA:  s_data[s].append((i, j, d))
        if d in R5GEN: s_r5[s].append((i, j, d))
print("s 嘅 magic 格數分佈:")
hist = Counter(len(v) for v in s_magic.values())
print(f"  {dict(sorted(hist.items()))}")
maxmagic = sorted(s_magic.items(), key=lambda kv: -len(kv[1]))[:6]
print("  magic 格最多嘅 s (重載 pipeline):")
for s, cells in maxmagic:
    ds = sorted({d for (_,_,d) in cells})
    print(f"    s={s:>2}: {len(cells)} magic 格  d={ds}")
print("  s=33 (M-pipeline):", [(i,j,d) for (i,j,d) in s_magic.get(33, [])])
print()
print("s 嘅 data 格數分佈:")
histd = Counter(len(v) for v in s_data.values())
print(f"  {dict(sorted(histd.items()))}")
print("  s=33 data 格:", [(i,j,d) for (i,j,d) in s_data.get(33, [])])
print()
print("s 嘅 R5 格數分佈:")
histr = Counter(len(v) for v in s_r5.values())
print(f"  {dict(sorted(histr.items()))}")
print("  s=33 R5 格:", [(i,j,d) for (i,j,d) in s_r5.get(33, [])])

# ============ T3: s=33 驗證 ============
print()
print("=== T3: s=33 列 16 格 ===")
s33 = [(i, 33-i) for i in range(1, 17)]
for (i, j) in sorted(s33):
    d = j - i
    tags = []
    if d in MAGIC: tags.append("MAGIC")
    if d in DATA: tags.append("data")
    if d in R5GEN: tags.append("R5")
    print(f"  ({i:>2},{j:>2}) d={d:>2} gcd={gc(d):>2} {' '.join(tags) or '—'}")

# ============ T4: SYNC 家族 (i=2) vs B 行 (i=4) ============
print()
print("=== T4: SYNC 家族 (i=2 行) vs B 行 (i=4 行) ===")
for ii in (1, 2, 3, 4):
    cells = [(ii, j) for j in range(ii+1, 45)]
    magic_hits = [d for (i, j) in cells if (d := j-i) in MAGIC]
    data_hits = [d for (i, j) in cells if (d := j-i) in DATA]
    r5_hits = [d for (i, j) in cells if (d := j-i) in R5GEN]
    print(f"  i={ii}: {len(cells)} 格  magic={sorted(magic_hits)} data={sorted(data_hits)} R5={sorted(r5_hits)}")

# ============ T5: s=33 beat 代數結構 ============
print()
print("=== T5: s=33 列 beat 值高精度 ===")
import mpmath as mp
mp.mp.dps = 60
w = lambda n: 2*mp.sin(mp.mpf(n)*mp.pi/88)
beats = {}
for (i, j) in sorted(s33):
    d = j - i
    bt = abs(w(j) - w(i))
    beats[d] = bt
    # 探測: 2cos(kπ/88)? sqrt(2+q)?
    best = None
    for k in range(1, 88):
        if mp.almosteq(bt, 2*mp.cos(mp.mpf(k)*mp.pi/88), rel_eps=mp.mpf('1e-40')):
            best = f"2cos({k}π/88)"
        if mp.almosteq(bt, 2*mp.sin(mp.mpf(k)*mp.pi/88), rel_eps=mp.mpf('1e-40')):
            best = f"2sin({k}π/88)"
    print(f"  d={d:>2} ({i:>2},{j:>2}): beat={mp.nstr(bt, 22)}  {best or ''}")

# 對數結構: 相鄰差
print()
ds_list = sorted(j-i for (i,j) in s33)
diff1 = [beats[ds_list[k+1]] - beats[ds_list[k]] for k in range(len(ds_list)-1)]
print("一階差:", [mp.nstr(x, 8) for x in diff1])

# ============ T6: magic d 行 s 值域 ∩ s ============
print()
print("=== T6: magic 行 s 值域 ===")
for d in MAGIC:
    s_vals = sorted({i + (i+d) for i in range(1, 44-d+1)})
    print(f"  d={d:>2}: s∈[{s_vals[0]},{s_vals[-1]}]  奇偶={'奇' if s_vals[0]%2 else '偶'}  個數={len(s_vals)}")
print("  s=33 (M): odd — 只有 odd-magic 行 (d=7,33) 可能相交")
print("  d=7: s∈[9,81] odd → 33 ∈ ✓ (13,20)!")
print("  d=33: s∈[35,53] odd → 33 ∉ (太細)")

res = {
    "test": "41_sync_saxis",
    "T1_fixed_member_counts": {str(d): 44-d for d in MAGIC + [29, 11, 13, 17, 19, 21, 25]},
    "T2_s_magic_hist": dict(sorted(hist.items())),
    "T2_top_s": [{"s": s, "cells": cells} for s, cells in maxmagic],
    "T3_s33": [{"i": i, "j": j, "d": j-i, "gcd": gc(j-i)} for (i, j) in sorted(s33)],
    "T5_beats_d": {str(d): mp.nstr(bt, 30) for d, bt in beats.items()},
}
with open("data/41_sync_saxis.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print()
print("輸出: data/41_sync_saxis.json")