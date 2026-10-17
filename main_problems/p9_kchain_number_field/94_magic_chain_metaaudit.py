#!/usr/bin/env python3
"""
94_magic_chain_metaaudit.py — Magic 攻堅統計鏈 meta-審計 (2026-10-17)
===================================================================================
目的: 70-93 核心數字獨立重算 — 審計嘅審計。零 Import 原推導, 第一原理。
（70-93 每個 script 有自身 PASS, 但跨 script 嘅數字冇被第三者重算）

重算清單 (全部 70-93 宣稱過嘅關鍵數字):
  A. 過閘集合數 = 37 (71)        窮舉 C(43,5)
  B. cover triples: M_L = 3 / M_F = 42 (70/82)
  C. 結構稀有: gcd+deg 全互斥 = 2.13% (70) — 窮舉精確
  D. 領域身份率 39/43 = 90.7%; 無身份 {21,32,36,39} (70/89)
  E. 跨 N 域唯一: N44={22,33} N88={44} N176={88} N352={176} (91)
  F. 程序級: 鎖4開2 = 4 組合 (92)
  G. 支柱 cover: magic 唯一 cover 5 (75/83); M_F 3/5
"""
from math import gcd
from itertools import combinations
import json, os

ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
DATA = {11, 13, 17, 19, 21, 25}
MAGIC = [7, 14, 20, 22, 33]
PARALLEL = [5, 10, 20, 22, 33]
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
    if d == 0:
        return 1
    g = gcl(d)
    m = 176 // g
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

def gcl_N(d, N):
    return gcd(abs(N - d), 2 * N)

def G(anchors, ms=(1, 2, 3, 4)):
    return sorted({m * a for a in anchors for m in ms if 1 <= m * a <= 43})

# ---- A. 過閘集合數 (71) ----
covers = [t for t in combinations(ALLD, 3) if set(MAGIC) <= set(G(t))]
g1234 = []
for five in combinations(ALLD, 5):
    f = sorted(five)
    if len({gcl(x) for x in f}) == 5 and len({om_deg(x) for x in f}) == 5 \
            and set(f).isdisjoint(DATA) \
            and any(set(f) <= set(G(t)) for t in covers):
        g1234.append(f)
n37 = len(g1234)
print(f"A. 過閘集合: {n37} 個 (71 宣稱 37)")
chk("A1_37", "過閘集合 = 37 (71 復現)", n37 == 37, str(n37))

# ---- B. cover triples M_L / M_F ----
covers_l = [t for t in combinations(ALLD, 3) if len(set(G(t)) & set(MAGIC)) == 5]
covers_f = [t for t in combinations(ALLD, 3) if len(set(G(t)) & set(PARALLEL)) == 5]
print(f"B. cover triples: M_L={len(covers_l)} M_F={len(covers_f)} (82 宣稱 3/42)")
chk("B1_3", "M_L cover triples = 3 (70/82)", len(covers_l) == 3, str(len(covers_l)))
chk("B2_42", "M_F cover triples = 42 (82)", len(covers_f) == 42, str(len(covers_f)))

# ---- C. 結構稀有 2.13% (70) ----
def rare_ok(five):
    return len({gcl(x) for x in five}) == 5 and len({om_deg(x) for x in five}) == 5
total = len(list(combinations(ALLD, 5)))
hit = 0
# 抽樣唔啱 — 窮舉全 962598 太慢但可 (76 號用過). 用相同窮舉.
hit = sum(1 for five in combinations(ALLD, 5) if rare_ok(five))
p = hit / total
print(f"C. 結構稀有: {hit}/{total} = {p*100:.4f}% (70 宣稱 2.13%)")
chk("C1_213pct", "gcd+deg 全互斥機率 = 2.13%±0.05 (70)", abs(p - 0.0213) < 0.0005, f"p={p}")

# ---- D. 領域身份 39/43 + 無身份 (70/89) ----
corpus = open("/tmp/corpus.txt", encoding="utf-8", errors="replace").read()
def has_id(d):
    return f"sin({d}π/88)" in corpus or f"sin({2*d}π/176)" in corpus
ids = {d: has_id(d) for d in range(1, 44)}
nid = sum(ids.values())
noid = [d for d in ids if not ids[d]]
print(f"D. 領域身份: {nid}/43 = {nid/43*100:.1f}% 無身份={noid} (70 宣稱 39/43, {21,32,36,39})")
chk("D1_field", "領域身份 = 39/43 = 90.7% (70)", nid == 39, str(nid))
chk("D2_noid", "無身份 = {21,32,36,39} (70/89)", set(noid) == {21, 32, 36, 39}, str(noid))

# ---- E. 跨 N 域唯一 (91) ----
def uniq_N(N):
    byg = {}
    for d in range(1, N):
        byg.setdefault(gcl_N(d, N), []).append(d)
    out = []
    for g, f in byg.items():
        free = [d for d in f if d not in DATA]
        if len(free) == 1:
            out.append(free[0])
    return sorted(out)
e_44, e_88 = uniq_N(44), uniq_N(88)
e_176, e_352 = uniq_N(176), uniq_N(352)
print(f"E. 域唯一: N44={e_44} N88={e_88} N176={e_176} N352={e_352} (91)")
chk("E1_N44", "N44 唯一 = {22,33}", e_44 == [22, 33], str(e_44))
chk("E2_N88", "N88 唯一 = {44}", e_88 == [44], str(e_88))
chk("E3_N176", "N176 唯一 = {88}", e_176 == [88], str(e_176))
chk("E4_N352", "N352 唯一 = {176}", e_352 == [176], str(e_352))

# ---- F. 程序級 4 組合 (92) ----
# S1-S5 鎖定: gcd1→7, gcd8→20, gcd11→33, gcd22→22; 開 gcd2 {10,14} gcd16 {20,28}
# 註: gcd16 20 唔喺 gcd16 — 20 係 gcd8. gcd16 候選 = {28} (28=4·7, gcd16)
# 程序開放 = gcd2 揀 14/10 (=2) × gcd16 揀 28/20? — 20 唔喺 gcd16!
# 92 號宣稱「4 組合」 — 重新驗證
byg16 = [d for d in G((7, 11, 5)) if gcl(d) == 16]
byg2 = [d for d in G((7, 11, 5)) if gcl(d) == 2]
print(f"F. 程序開放位: gcd2={byg2} (2 選 1) gcd16={byg16}")
print(f"   92 宣稱 4 組合 (gcd2×gcd16 = 2×2) — 但 gcd16 只有 {len(byg16)} 個候選")
chk("F1_open2", "gcd2 開放位 = {10,14}", set(byg2) == {10, 14}, str(byg2))
chk("F2_open16", "gcd16 候選 = {28} — 92 嘅『2 選 1 (28 vs 20)』有誤: 20 係 gcd8!", set(byg16) == {28}, str(byg16))

# ---- G. 支柱 cover ----
pillars = {7, 14, 20, 22, 33}
cov_l = len(set(MAGIC) & pillars)
cov_f = len(set(PARALLEL) & pillars)
print(f"G. 支柱 cover: M_L={cov_l} (5/5 唯一?) M_F={cov_f} (3/5)")
max_others = max((len(set(f) & set(pillars)) for f in g1234 if set(f) != set(MAGIC)), default=0)
print(f"   其他 37 集合最大 cover = {max_others}")
chk("G1_covL", "M_L cover 5/5", cov_l == 5, str(cov_l))
chk("G2_covF", "M_F cover 3/5", cov_f == 3, str(cov_f))
chk("G3_unique5", "magic 唯一 cover 全 5 (其他 ≤4)", max_others <= 4, str(max_others))

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "94_magic_chain_metaaudit", "date": "2026-10-17",
    "gates": n37, "covers_L": len(covers_l), "covers_F": len(covers_f),
    "rarity": {"hit": hit, "total": total, "p": p},
    "field": {"n": nid, "noid": noid},
    "N": {"44": e_44, "88": e_88, "176": e_176, "352": e_352},
    "program": {"gcd2": byg2, "gcd16": byg16},
    "pillars": {"L": cov_l, "F": cov_f, "max_others": max_others},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/94_magic_chain_metaaudit.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/94_magic_chain_metaaudit.json")