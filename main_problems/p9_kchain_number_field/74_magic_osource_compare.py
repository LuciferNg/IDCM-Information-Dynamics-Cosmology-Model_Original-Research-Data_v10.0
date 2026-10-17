#!/usr/bin/env python3
"""
74_magic_osource_compare.py — Magic A 層閉合源頭數 vs 37 替代 (2026-10-17)
===================================================================================
問題 (73 號之後): magic 係咪喺「唔同 O-series 閉合項目數」(A 層 label 真實性)
上有優勢? 73 號數字面出現次數 (sin 深度); 74 號數「每 d 關聯幾多個唔同 O 編號」。

方法:
  - corpus = O-series 源頭 (排除 P9 自身 + 排除 data/ 目錄)
  - 對每個 d: 喺 corpus 中搵所有 O 編號 (O[0-9]+) 喺「含 sin(dπ/88) 或 γ_d
    或 sin(2dπ/176) 嘅行」出現 — 即「閉合同 d 相關嘅唔同 O 項目數」
  - 對比 magic 5 個 vs 37 個 5-collection 嘅「源頭數總和」— magic 排名

判決:
  magic 源頭數排名 top3 → A 層有量化優勢 (閉合項目數多)
  否則 → A 層同 37 集合並列, 「支撐」論證只靠個別閉合本身
"""
import subprocess
import json
import re
import os
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}
ALLD = list(range(1, 44))
MULTS = (1, 2, 3, 4)
ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
P9 = f"{ROOT}/main_problems/p9_kchain_number_field"

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

def G(anchors):
    return sorted({m * a for a in anchors for m in MULTS if 1 <= m * a <= 43})

print("=" * 72)
print("A. 重建 37 個過閘集合 (71 號方法)")
print("=" * 72)
covers = [t for t in combinations(ALLD, 3) if set(MAGIC) <= set(G(t))]
g1234 = []
for five in combinations(ALLD, 5):
    if len({gcl(x) for x in five}) == 5 and len({om_deg(x) for x in five}) == 5 \
            and set(five).isdisjoint(DATA) \
            and any(set(five) <= set(G(tri)) for tri in covers):
        g1234.append(sorted(five))
chk("A1_rebuild37", f"重建過閘集 = {len(g1234)} (71 號: 37)",
    len(g1234) == 37, f"count={len(g1234)}")

print()
print("=" * 72)
print("B. Corpus — O-series 源頭, 排除 P9 + data/")
print("=" * 72)
files = []
for rootdir in ("open_problems_fresh", "main_problems"):
    r = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                        "-e", "sin(", "-e", "γ_", "-e", "gamma_",
                        f"{ROOT}/{rootdir}"],
                       capture_output=True, text=True)
    for f in r.stdout.splitlines():
        if f.startswith(P9) or "/data/" in f:
            continue
        files.append(f)
files = sorted(set(f for f in files if f))
corpus = ""
for f in files:
    try:
        corpus += open(f, encoding="utf-8", errors="ignore").read() + "\n"
    except Exception:
        pass
chk("B1_corpus_size", f"源頭 corpus: {len(files)} 檔, {len(corpus)} chars",
    len(files) >= 30, f"files={len(files)}")

print()
print("=" * 72)
print("C. 每 d 嘅 O 閉合源頭數 (line-level)")
print("=" * 72)
lines = corpus.splitlines()
o_re = re.compile(r"\bO([0-9]{2,4})\b")
def o_sources(d):
    pats = [f"sin({d}π/88)", f"sin({2*d}π/176)", f"γ_{d}", f"gamma_{d}"]
    oset = set()
    for ln in lines:
        if any(p in ln for p in pats):
            for m in o_re.finditer(ln):
                oset.add(int(m.group(1)))
    return oset

src = {}
for d in range(1, 44):
    s = o_sources(d)
    src[d] = s
    print(f"  d={d:2d}: {len(s)} 個 O 源頭 {sorted(s)[:14]}{'...' if len(s)>14 else ''}")

print()
print("=" * 72)
print("D. ★Magic vs 37 集合 — O 源頭數對比")
print("=" * 72)
def o_sum(five):
    return sum(len(src[d]) for d in five)

magic_os = o_sum(MAGIC)
rows = sorted(((o_sum(f), f) for f in g1234), key=lambda kv: -kv[0])
print(f"magic O 源頭數 = {magic_os}")
print("37 集合 O 源頭數排名 (top 15):")
for i, (sd, five) in enumerate(rows[:15]):
    mark = " ★magic" if five == sorted(MAGIC) else ""
    print(f"  #{i+1:2d}: {sd:4d}  {five}{mark}")
rank = next(i + 1 for i, (sd, five) in enumerate(rows) if five == sorted(MAGIC))
chk("D1_magic_rank", f"magic O 源頭數排名 = #{rank}/37", rank <= 3, f"rank={rank}")
chk("D2_magic_top1", f"magic 係咪 O 源頭第一 = {magic_os == rows[0][0]}",
    magic_os == rows[0][0], f"top={rows[0][0]} magic={magic_os}")

print()
print("=" * 72)
print("E. Magic 5 個嘅 O 源頭明細 (A 層 label 真實性表)")
print("=" * 72)
for d in MAGIC:
    print(f"  {d}: {sorted(src[d])}")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "74_magic_osource_compare", "date": "2026-10-17",
    "magic": MAGIC, "n_g1234": len(g1234),
    "corpus_files": len(files),
    "o_sources": {str(d): sorted(v) for d, v in src.items()},
    "magic_o_sum": magic_os, "magic_o_rank": rank,
    "ranked": [[sd, list(f)] for sd, f in rows],
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/74_magic_osource_compare.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/74_magic_osource_compare.json")