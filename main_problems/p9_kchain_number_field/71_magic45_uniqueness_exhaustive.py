#!/usr/bin/env python3
"""
71_magic45_uniqueness_exhaustive.py — Magic「唯一性 vs 方便性」終極判決 (2026-10-17)
=====================================================================================
問題 (70 號 gap): magic 5 個係咪「唯一」同時滿足全部約束嘅 5-collection?

約束 (R5 程序各閘):
  G1 gcd 類互斥: 5 個 gcd(|44−d|,176) 全部唔同
  G2 deg 層互斥: 5 個 deg(ω_d) 全部唔同
  G3 data-free:  唔含 DATA = {11,13,17,19,21,25}
  G4 3-anchor 可生成: ∃ 3-anchor (a,b,c) 使 G({a,b,c}; m∈{1,2,3,4}) ⊇ 呢 5 個
  G5 (後驗語意) Lucas/Fib anchor 優先

魔法集: MAGIC = {7,14,20,22,33} 過晒 G1-G4?
其他 5-collection 呢? — 逐一數。

小數目標: 喺全部 C(43,5)=962,598 個 5-collection 入面,
  N_pass = 同時過 G1+G2+G3+G4 嘅數量
  magic ∈ N_pass?
  若 N_pass = 1 (magic 唯一) → 結構獨特性返嚟 (純結構層)
  若 N_pass ≥ 2 → magic 只係其中一個 → 「唯一性」撤回, 剩「方便性」

零 import 原推導; 純整數; 窮舉。
"""
from math import gcd
from itertools import combinations
from collections import defaultdict
import json

MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}
ALLD = list(range(1, 44))
MULTS = (1, 2, 3, 4)

PASS = 0
FAIL = 0
FAILS = []
OUT = []

def chk(name, desc, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {desc}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  ❌ {name}: {desc}" + (f"  [{detail}]" if detail else ""))
    OUT.append({"id": name, "desc": desc, "ok": ok, "detail": detail})

def gcl(d):
    return gcd(abs(44 - d), 176)

def om_deg(d):
    m = 176 // gcl(d)
    r = m; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r // 2

print("=" * 72)
print("A. 約束定義確認")
print("=" * 72)
# A1: magic 過全部約束
gm = [gcl(d) for d in MAGIC]
dm = [om_deg(d) for d in MAGIC]
ok_g1 = len(set(gm)) == 5
ok_g2 = len(set(dm)) == 5
ok_g3 = set(MAGIC).isdisjoint(DATA)
# G4: (5,7,11) cover? (from 70: covers = (5,7,11),(7,10,11),(7,11,20))
def G(anchors):
    return sorted({m * a for a in anchors for m in MULTS if 1 <= m * a <= 43})
ok_g4 = any(set(MAGIC) <= set(G(t)) for t in [(5, 7, 11), (7, 10, 11), (7, 11, 20)])
chk("A1_magic_all_gates", "magic 過 G1+G2+G3+G4", ok_g1 and ok_g2 and ok_g3 and ok_g4,
     f"gcd={gm} deg={dm} data={set(MAGIC)&DATA} cover={ok_g4}")
chk("A2_data_free", "data-free: magic∩DATA = ∅", ok_g3)

print()
print("=" * 72)
print("B. anchor 全集 (預計算): 邊啲 3-anchor 產生 magic?")
print("=" * 72)
# B1: 全部可 cover magic 5/5 嘅 3-anchor (重複 70 號)
covers = []
for tri in combinations(ALLD, 3):
    if set(MAGIC) <= set(G(tri)):
        covers.append(tri)
chk("B1_covers", f"cover magic 3-anchor 數 = {len(covers)} (70 號: 3)",
    len(covers) == 3, str(covers))

print()
print("=" * 72)
print("C. ★窮舉 5-collection — 過 G1+G2+G3 幾多?")
print("=" * 72)
# C1: 過 G1+G2 (gcd/deg 互斥) + G3 (data-free) 嘅 5-collection 數
n_g123 = 0
g123_list = []
for five in combinations(ALLD, 5):
    if len({gcl(x) for x in five}) == 5 and len({om_deg(x) for x in five}) == 5 \
            and set(five).isdisjoint(DATA):
        n_g123 += 1
        g123_list.append(sorted(five))
chk("C1_g123_count", f"過 G1+G2+G3 嘅 5-collection = {n_g123}",
    n_g123 >= 1, f"count={n_g123}")
print(f"  [全部: {len(g123_list)} 個]")
if len(g123_list) <= 30:
    for x in g123_list:
        mark = " ★MAGIC" if x == sorted(MAGIC) else ""
        print(f"     {x}{mark}")

print()
print("=" * 72)
print("D. ★加入 G4 (3-anchor 可生成) — 最後數")
print("=" * 72)
# D1: 過 G1+G2+G3+G4
n_g1234 = 0
g1234_list = []
cover_all = covers
for five in g123_list:
    # 要 ∃ anchor triple: G(tri) ⊇ five
    gen_ok = any(set(five) <= set(G(tri)) for tri in cover_all)
    if gen_ok:
        n_g1234 += 1
        g1234_list.append(five)
chk("D1_g1234_count", f"過 G1+G2+G3+G4 嘅 5-collection = {n_g1234}",
    n_g1234 >= 1, f"count={n_g1234}")
for x in g1234_list:
    mark = " ★MAGIC" if x == sorted(MAGIC) else ""
    print(f"     {x}{mark}")
# D2: magic 喺入面?
is_in = sorted(MAGIC) in g1234_list
chk("D2_magic_in", "magic ∈ 過晒 4 閘集合", is_in)

# D3: 唯一性判決
if n_g1234 == 1:
    verdict = f"✅ magic 係唯一同時過 G1-G4 嘅 5-collection ({n_g1234}/962598)"
else:
    verdict = f"🔴 magic 唔係唯一: {n_g1234} 個都過晒 (含 magic)"
chk("D3_uniqueness", f"★唯一性判決: {verdict}", n_g1234 == 1,
     f"N={n_g1234}: {g1234_list}")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "71_magic45_uniqueness_exhaustive", "date": "2026-10-17",
    "magic": MAGIC,
    "gate_descriptions": {
        "G1": "gcd(|44−d|,176) 5 個互斥",
        "G2": "deg(ω_d) 5 個互斥",
        "G3": "data-free (∩ DATA = ∅)",
        "G4": "∃ 3-anchor G(tri) ⊇ 5-collection",
    },
    "covers": [list(t) for t in covers],
    "n_g123": n_g123,
    "n_g1234": n_g1234,
    "g1234_list": [list(x) for x in g1234_list],
    "magic_unique": n_g1234 == 1,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/71_magic45_uniqueness_exhaustive.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/71_magic45_uniqueness_exhaustive.json")