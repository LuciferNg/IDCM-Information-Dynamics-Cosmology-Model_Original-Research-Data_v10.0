#!/usr/bin/env python3
"""
75_magic_role_diversity.py — Magic 角色多樣性 vs 37 替代 (2026-10-17)
===================================================================================
問題 (74 號之後最後維度): magic 5 個 cover 5 個唔同「物理角色」(49 號宇宙 5 支柱)。
其他 37 個過閘集合 cover 幾多個唔同角色/label d? — 若 magic 係唯一 cover 全部
5 支柱嘅, 「角色多樣性」先係真正嘅「支撐物理世界」證據。

定義:
  LABEL_D = 9 label 格 d 值 ∪ magic 5 個 (獨立, 來自 19 號週期表 + 49 號支柱)
          = {11,13,14,17,19,21,25} ∪ {7,14,20,22,33} = {7,11,13,14,17,19,20,21,22,25,33}
  PILLAR  = 5 支柱 (49 號): {7:ANCHOR/DM, 14:GEN, 20:TRANSFER, 22:HALF, 33:KTREE}

測試:
  T1 label cover: 37 集合每個 cover 幾多個 label d (11 個) — magic 排名
  T2 ★支柱 cover: 37 集合每個 cover 幾多個支柱 (5 個) — magic 係咪唯一 5/5
  T3 誠實: 冇支柱成員嘅集合 (cover 0) 有幾多 — R5 程序輸出嘅「空洞」佔比

方法: 重建 71 號 37 集合; 純集合計。
"""
import json
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
PILLAR = {
    7: "ANCHOR/DM", 14: "GEN", 20: "TRANSFER", 22: "HALF", 33: "KTREE",
}
LABEL_D = {11, 13, 14, 17, 19, 21, 25} | set(MAGIC)  # = 11 個
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

def G(anchors):
    return sorted({m * a for a in anchors for m in MULTS if 1 <= m * a <= 43})

print("=" * 72)
print("A. 重建 37 個過閘集合 (71 號方法) + 定義確認")
print("=" * 72)
chk("A0_label_def", f"LABEL_D = {sorted(LABEL_D)} ({len(LABEL_D)} 個)",
    len(LABEL_D) == 11, str(sorted(LABEL_D)))
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
print("B. T1 — Label cover (11 個) 對比")
print("=" * 72)
def label_cover(five):
    return len(set(five) & LABEL_D)

rows_l = sorted(((label_cover(f), f) for f in g1234), key=lambda kv: -kv[0])
mlc = label_cover(MAGIC)
lrank = next(i + 1 for i, (c, f) in enumerate(rows_l) if f == sorted(MAGIC))
print(f"magic label cover = {mlc}/{len(LABEL_D)}")
hist = {}
for c, f in rows_l:
    hist.setdefault(c, []).append(f)
for c in sorted(hist, reverse=True):
    star = " ★magic" if sorted(MAGIC) in hist[c] else ""
    print(f"  cover {c}: {len(hist[c])} 個{star}")
chk("B1_magic_label_rank", f"magic label cover 排名 = #{lrank}/37",
    lrank <= 3, f"rank={lrank} cover={mlc}")

print()
print("=" * 72)
print("C. ★T2 — 支柱 cover (5 個) 對比")
print("=" * 72)
def pillar_cover(five):
    return len(set(five) & set(PILLAR))

rows_p = sorted(((pillar_cover(f), f) for f in g1234), key=lambda kv: -kv[0])
mpc = pillar_cover(MAGIC)
prank = next(i + 1 for i, (c, f) in enumerate(rows_p) if f == sorted(MAGIC))
print(f"magic pillar cover = {mpc}/5")
phist = {}
for c, f in rows_p:
    phist.setdefault(c, []).append(f)
for c in sorted(phist, reverse=True):
    star = " ★magic" if sorted(MAGIC) in phist[c] else ""
    print(f"  cover {c} 支柱: {len(phist[c])} 個{star}")
chk("C1_magic_pillar_rank", f"magic 支柱 cover 排名 = #{prank}/37",
    prank == 1, f"rank={prank} cover={mpc}")
n_p5 = len(phist.get(5, []))
chk("C2_unique5", f"cover 全 5 支柱嘅集合數 = {n_p5} (magic 係咪唯一)",
    n_p5 == 1, f"若有其他集合都 5/5, magic 唔唯一")

print()
print("=" * 72)
print("D. ★T3 — R5 程序空洞率: 37 集合幾多個完全冇支柱?")
print("=" * 72)
n_0 = len(phist.get(0, []))
chk("D1_empty_rate", f"cover 0 支柱集合 = {n_0}/37 ({n_0/37*100:.0f}%) — ★程序保證至少 2 支柱 (22+33 結構強制)",
    n_0 == 0, f"{n_0} 個完全冇支柱 — 過閘集合全部含 22/33 (gcd 強制)")

print()
print("=" * 72)
print("E. 誠實判讀")
print("=" * 72)
print(f"""
  label cover: magic {mlc}/11, 排名 #{lrank}/37
  支柱 cover:   magic {mpc}/5,  排名 #{prank}/37 (cover 5 支柱集合數 = {n_p5})
  R5 空洞率:  {n_0}/37 個完全冇支柱 = {n_0/37*100:.0f}%
""")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "75_magic_role_diversity", "date": "2026-10-17",
    "magic": MAGIC, "n_g1234": len(g1234),
    "label_d": sorted(LABEL_D), "pillar": {str(k): v for k, v in PILLAR.items()},
    "label_cover_hist": {str(c): [list(x) for x in v] for c, v in hist.items()},
    "pillar_cover_hist": {str(c): [list(x) for x in v] for c, v in phist.items()},
    "magic_label_cover": mlc, "magic_label_rank": lrank,
    "magic_pillar_cover": mpc, "magic_pillar_rank": prank,
    "n_cover5": n_p5, "n_empty": n_0,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/75_magic_role_diversity.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/75_magic_role_diversity.json")