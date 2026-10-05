#!/usr/bin/env python3
"""38 — (c2) D6/S6/C6 生成原則: 配對結構 + null-control
測試:
T1: D6 配對 (1,2)/(6,9)/(19,21) — sums {3,15,40} = {N_gen, N_gen·F5, N_d−B}?
T2: S6 配對 (11,44)/(25,41)/(68,85) — sums {55,66,153}, diffs {33,16,17} = {F10, 2K_tree, N_gen²·F_proj} / {K_tree, B², F_proj}?
T3: null-control: 隨機 6-subset 有冇同樣配對性質? (1000 次)
T4: 41-hub: 41 同 S6 其他成員嘅差 {3,16,27,44,60} — 邊個結構?
T5: mod-5 分佈 + Z5 圈上位置
"""
import numpy as np, itertools, random
from fractions import Fraction

D6 = [1,2,6,9,19,21]
S6 = [11,25,41,44,68,85]
C6 = [3,11,20,25,41,44]

# 結構數字典 (IDCM 常量)
STRUCT = {1:"1",2:"2=log2B",3:"3=N_gen",4:"4=B",5:"5=F5",6:"6=2N_gen",7:"7=L4",
8:"8=F6",9:"9=K_tree",11:"11=L5",12:"12=L5+1=B·N_gen",13:"13=F7",16:"16=B²",17:"17=F_proj=L6−1",
18:"18=L6",19:"19=L6+1",20:"20=N_d−B",21:"21=F8",22:"22=γ22·?",25:"25=F5²",27:"27=3³",
29:"29=L7",32:"32=2B²",33:"33=K_tree",34:"34=F9",36:"36=(2N_gen)²",38:"38",40:"40=N_d−B",
41:"41=44−3",42:"42=N_d⁻",44:"44=N_d",47:"47=L8",55:"55=F10",64:"64=2^6",66:"66=2K_tree",
68:"68=44+24",76:"76=L9",77:"77=L4L5",85:"85=88−3",88:"88=Σγ_odd",90:"90=(N_d+1)log2B",
123:"123=L10",137:"137=α⁻¹(0)",143:"143=dim SU12",153:"153=9·17",176:"176",178:"178=2F11"}

def label(x):
    return STRUCT.get(x, f"{x}?")

# T1: D6 配對
print("=== T1: D6 pairs (adjacent in sorted order) ===")
for i in range(0, 6, 2):
    a, b = D6[i], D6[i+1]
    print(f"  ({a},{b}): sum={a+b} ({label(a+b)}), diff={b-a} ({label(b-a)})")
# 全部 15 對 D6 pairings 有冇 sum/diff 都結構嘅
print("  — 全部 D6 pairings 中 sum&diff 都結構:")
cnt = 0
for (a,b) in itertools.combinations(D6, 2):
    if a+b in STRUCT and (b-a) in STRUCT:
        cnt += 1
        print(f"    ({a},{b}): sum {a+b}={label(a+b)} diff {b-a}={label(b-a)}")
print(f"  → {cnt}/15 pairs 雙結構")

# T2: S6 配對
print("\n=== T2: S6 pairs ===")
for (a,b) in itertools.combinations(S6, 2):
    if (a+b in STRUCT) and (b-a in STRUCT):
        print(f"  ({a},{b}): sum {a+b}={label(a+b)} diff {b-a}={label(b-a)}")
print("  — 建議 pairing (11,44)/(25,41)/(68,85):")
for (a,b) in [(11,44),(25,41),(68,85)]:
    print(f"    ({a},{b}): sum {a+b}={label(a+b)}, diff {b-a}={label(b-a)}")

# T3: null-control — 隨機 6-subset 有幾大機會有「可配成 3 對全部 sum∈STRUCT 或 diff∈STRUCT」?
print("\n=== T3: null-control (1000 random 6-subsets of 1..87) ===")
def pairings_all_struct(S):
    """存在 pairing 使每對 sum∈STRUCT 且 diff∈STRUCT?"""
    S = list(S)
    for perm in itertools.permutations(S):
        ok = True
        for i in range(0, 6, 2):
            a, b = perm[i], perm[i+1]
            if a > b: a, b = b, a
            if not ((a+b in STRUCT) and (b-a in STRUCT)):
                ok = False; break
        if ok: return True
    return False

def any_pair_struct(S):
    """至少存在一對 sum&diff 都結構?"""
    for a, b in itertools.combinations(S, 2):
        if (a+b in STRUCT) and (b-a in STRUCT):
            return True
    return False

rng = random.Random(42)
n_all = n_any = 0
for _ in range(1000):
    S = rng.sample(range(1, 88), 6)
    if pairings_all_struct(S): n_all += 1
    if any_pair_struct(S): n_any += 1
print(f"  全配對(3對)都 sum&diff 結構: {n_all}/1000 = {n_all/10:.1f}%")
print(f"  至少一對 sum&diff 結構:      {n_any}/1000 = {n_any/10:.1f}%")
print(f"  D6 本身: 3/15 對雙結構; S6: 2/15 對雙結構")

# T4: 41-hub
print("\n=== T4: 41-hub ===")
for x in [11,25,44,68,85]:
    d = abs(41-x)
    print(f"  |41−{x}| = {d} ({label(d)}), 41+{x} = {41+x} ({label(41+x)})")

# T5: mod-5
print("\n=== T5: mod-5 分佈 ===")
for name, S in [("D6", D6), ("S6", S6), ("C6", C6), ("indices(all 16)", [2,3,5,6,8,10,17,19,22,23,25,31,33,35,42,43])]:
    mods = [x % 5 for x in S]
    from collections import Counter
    print(f"  {name}: {mods} → {dict(Counter(mods))}")

print("\nRESULT: (c2) 結構測試完成")
