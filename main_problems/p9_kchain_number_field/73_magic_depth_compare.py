#!/usr/bin/env python3
"""
73_magic_depth_compare.py — Magic 身份深度 vs 37 替代集合 (2026-10-17)
===================================================================================
問題 (72 號之後最後一個維度): magic 5 個嘅「身份深度」係咪深過其他 37 個集合?
  - 深度 = 喺 O-series 源頭文檔 (open_problems_fresh + main_problems 非 P9) 中,
    sin(dπ/88) / sin(2dπ/176) / γ_d 出現次數 (真正被物理閉合用過)
  - ★排除 P9 目錄自身: magic 喺 P9 被大量討論 (53/55/61 號等) — 若唔排除,
    會 bias (magic 係調查對象唔係源頭)
  - 控制 (γ 污染): γ_d 全譜普遍存在 (72 號見到 d=4 γ=458) —
    深度主結論用 sin 系列; γ 只做輔助

判決:
  magic avg depth vs 37 集合 avg depth — magic 排位
  top K 集合有冇 magic 之外嘅? — 若 magic 係深度 top, 「物理支撐」有量化證據
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
print("B. Corpus — O-series 源頭, 排除 P9")
print("=" * 72)
files = []
for rootdir in ("open_problems_fresh", "main_problems"):
    for pat in ("sin(", "γ_", "gamma_"):
        r = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                            "-e", pat, f"{ROOT}/{rootdir}"],
                           capture_output=True, text=True)
        for f in r.stdout.splitlines():
            if f.startswith(P9):
                continue
            files.append(f)
files = sorted(set(f for f in files if f))
corpus = ""
for f in files:
    try:
        corpus += open(f, encoding="utf-8", errors="ignore").read() + "\n"
    except Exception:
        pass
chk("B1_corpus_size", f"源頭 corpus: {len(files)} 檔, {len(corpus)} chars (排除 P9)",
    len(files) >= 30, f"files={len(files)}")

print()
print("=" * 72)
print("C. 深度計數 — sin 系列為主 (γ 輔助)")
print("=" * 72)
depth = {}
for d in range(1, 44):
    a = sum(len(re.findall(re.escape(p), corpus)) for p in [f"sin({d}π/88)", f"sin({2*d}π/176)"])
    c = len(re.findall(re.escape(f"γ_{d}"), corpus))
    depth[d] = {"sin": a, "gamma": c, "total": a + c}
    print(f"  d={d:2d}: sin ref={a:4d}  γ ref={c:4d}")

print()
print("=" * 72)
print("D. ★Magic vs 37 集合 — sin 深度對比")
print("=" * 72)
def s_depth(five):
    return sum(depth[d]["sin"] for d in five)

magic_sd = s_depth(MAGIC)
rows = sorted(((s_depth(f), f) for f in g1234), key=lambda kv: -kv[0])
print(f"magic sin 深度 = {magic_sd} (5 個 d 總和)")
print("37 集合 sin 深度排名 (top 12):")
for i, (sd, five) in enumerate(rows[:12]):
    mark = " ★magic" if five == sorted(MAGIC) else ""
    print(f"  #{i+1:2d}: {sd:4d}  {five}{mark}")
# magic 排名
rank = next(i + 1 for i, (sd, five) in enumerate(rows) if five == sorted(MAGIC))
chk("D1_magic_rank", f"magic sin 深度排名 = #{rank}/37", rank <= 3, f"rank={rank}")
chk("D2_magic_top1", f"magic 係咪深度第一 (sin) = {magic_sd == rows[0][0]}",
    magic_sd == rows[0][0], f"top={rows[0][0]} magic={magic_sd}")

print()
print("=" * 72)
print("E. γ 輔助深度對比")
print("=" * 72)
def g_depth(five):
    return sum(depth[d]["gamma"] for d in five)
mg = g_depth(MAGIC)
grows = sorted(((g_depth(f), f) for f in g1234), key=lambda kv: -kv[0])
grank = next(i + 1 for i, (gd, five) in enumerate(grows) if five == sorted(MAGIC))
print(f"magic γ 深度 = {mg}; 37 集合 γ 排名 = #{grank}/37")
chk("E1_gamma_rank", f"magic γ 深度排名 = #{grank}/37", grank <= 3, f"grank={grank}")

print()
print("=" * 72)
print("F. 裁決")
print("=" * 72)
print(f"""
  sin 深度: magic = {magic_sd}, 排名 #{rank}/37 (top = {rows[0][0]})
  γ 深度:   magic = {mg}, 排名 #{grank}/37
  決: magic 若雙榜 top3 → 身份深度維度有量化優勢; 否則同 37 集合並列
""")
sin_win = rank <= 3 and grank <= 3
chk("F1_depth_verdict", f"★Magic 身份深度優勢: {'✅ 有' if sin_win else '🔴 冇'} (雙榜 top3)",
    sin_win, f"sin#{rank} γ#{grank}")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "73_magic_depth_compare", "date": "2026-10-17",
    "magic": MAGIC, "n_g1234": len(g1234),
    "corpus_files": len(files),
    "depth": {str(d): v for d, v in depth.items()},
    "magic_sin_depth": magic_sd, "magic_sin_rank": rank,
    "magic_gamma_depth": mg, "magic_gamma_rank": grank,
    "ranked_sin": [[sd, list(f)] for sd, f in rows],
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/73_magic_depth_compare.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/73_magic_depth_compare.json")