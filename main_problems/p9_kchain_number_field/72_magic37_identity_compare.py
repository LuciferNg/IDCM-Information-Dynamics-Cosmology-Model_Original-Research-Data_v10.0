#!/usr/bin/env python3
"""
72_magic37_identity_compare.py — 37 替代集合 vs magic 身份完整性對比 (2026-10-17)
===================================================================================
問題 (71 號 gap): 37 個過閘 5-collection 入面, 除咗 magic, 有冇其他都含有
完整 O-series 身份? 領域 91% 預測幾乎全部都有 — 要實證。

轉換 (用戶 focus「獨特性」): magic 嘅「身份完整性」同其他 36 個有冇分別?
  - 若 magic 係唯一 5/5 有身份 → 獨特性返回
  - 若大部分 37 個都 5/5 → magic 冇任何優先性 (最後一擊)

配套測試 (label 格覆蓋):
  label 格 d 值 = {11,13,14,17,19,21,25} (9 DATA_CELLS)
  每個 5-collection 覆蓋幾多個 label d?
  magic ∩ = {14} 得 1 個 — 隨機期望 7/43×5 ≈ 0.81 — 正常範圍?
  37 個入面有冇 cover 更多 label d 嘅?

工具: corpus 一次掃描 (grep sin/he 全系); mpmath 唔需要; 純集合計。
"""
import subprocess
import json
import os
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}
LABEL_D = {11, 13, 14, 17, 19, 21, 25}  # 9 label 格嘅 d 值
ALLD = list(range(1, 44))
MULTS = (1, 2, 3, 4)
ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"

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
tot = 0
for five in combinations(ALLD, 5):
    tot += 1
    if len({gcl(x) for x in five}) == 5 and len({om_deg(x) for x in five}) == 5 \
            and set(five).isdisjoint(DATA) \
            and any(set(five) <= set(G(tri)) for tri in covers):
        g1234.append(sorted(five))
chk("A1_rebuild37", f"重建過閘集 = {len(g1234)} (71 號: 37)",
    len(g1234) == 37, f"count={len(g1234)} tot={tot}")

print()
print("=" * 72)
print("B. Corpus 掃描 — O-series 身份判準 (70 號同款)")
print("=" * 72)
allfiles = []
for rootdir in ("open_problems_fresh", "main_problems"):
    for pat in ("sin(", "γ_", "gamma_"):
        r = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                            "-e", pat, f"{ROOT}/{rootdir}"],
                           capture_output=True, text=True)
        allfiles += r.stdout.splitlines()
allfiles = sorted(set(f for f in allfiles if f))
corpus = ""
for f in allfiles:
    try:
        corpus += open(f, encoding="utf-8", errors="ignore").read() + "\n"
    except Exception:
        pass

def has_id(d):
    return f"sin({d}π/88)" in corpus or f"sin({2 * d}π/176)" in corpus

# 領域率 (70 號: 39/43)
dom_hits = {d: has_id(d) for d in ALLD}
n_dom = sum(dom_hits.values())
chk("B1_domain", f"領域身份率 = {n_dom}/43 = {n_dom/43*100:.1f}% (70 號: 90.7%)",
    n_dom == 39, f"count={n_dom}")

print()
print("=" * 72)
print("C. ★37 個集合身份完整度 — magic vs 其他 36")
print("=" * 72)
rows = []
for five in g1234:
    nh = sum(1 for d in five if has_id(d))
    rows.append((nh, five))
rows.sort(reverse=True, key=lambda r: r[0])
identity_histogram = {}
for nh, five in rows:
    identity_histogram.setdefault(nh, []).append(five)
print("身份完整度分佈:")
for nh in sorted(identity_histogram, reverse=True):
    fl = identity_histogram[nh]
    star = " ★magic" if sorted(MAGIC) in fl else ""
    print(f"  {nh}/5 有身份: {len(fl)} 個{star}{'%s' % ('' if sorted(MAGIC) not in fl else '')}")
# magic 位置
magic_row = [(nh, five) for nh, five in rows if five == sorted(MAGIC)]
chk("C1_magic_rank", f"magic 身份完整度: {magic_row[0][0]}/5 (37 個之中排名?)",
    True, str(magic_row[0][0]))
n5 = len(identity_histogram.get(5, []))
chk("C2_count5", f"37 個之中 5/5 全中 = {n5} 個", n5 >= 2,
     f"如果 >1, magic 唔係唯一 5/5")

print()
print("=" * 72)
print("D. Label 格覆蓋 — 每個集合 cover 幾多個 label d?")
print("=" * 72)
lrows = []
for five in g1234:
    cover = set(five) & LABEL_D
    lrows.append((len(cover), five))
lrows.sort(reverse=True)
mcover = set(MAGIC) & LABEL_D
chk("D1_magic_label", f"magic ∩ label d = {sorted(mcover)} (得 {len(mcover)} 個)",
    len(mcover) == 1, str(sorted(mcover)))
lhist = {}
for n, five in lrows:
    lhist.setdefault(n, []).append(five)
for n in sorted(lhist, reverse=True):
    print(f"  cover {n} label d: {len(lhist[n])} 個")
maxcov = max(n for n in lhist)
chk("D2_max_label", f"37 個最大 label cover = {maxcov} (magic 得 {len(mcover)})",
    maxcov <= len(mcover), f"magic {len(mcover)} vs max {maxcov}")

print()
print("=" * 72)
print("E. 判決")
print("=" * 72)
flag_magic_5 = sorted(MAGIC) in identity_histogram.get(5, [])
print(f"""
  身份完整度: magic {magic_row[0][0]}/5; 37 個之中 5/5 全中 = {n5} 個
  label 覆蓋: magic {len(mcover)}/{len(LABEL_D)}; 37 個最大 cover = {maxcov}
  領域身份率: {n_dom}/43 ({n_dom/43*100:.0f}%)
""")
# 判決
if n5 >= 2:
    print("  🔴 magic 唔係唯一 5/5 有身份 — 「magic 身份完整性」係領域常態")
elif n5 == 1:
    print("  ✅ magic 係唯一 5/5 有身份 — 獨特性返回 (身份層)")
else:
    print("  ⚠️ magic 唔係 5/5?! 檢查判準")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "72_magic37_identity_compare", "date": "2026-10-17",
    "magic": MAGIC,
    "n_g1234": len(g1234),
    "domain_rate": n_dom,
    "identity_hist": {str(k): [list(x) for x in v] for k, v in identity_histogram.items()},
    "magic_identity": magic_row[0][0],
    "n_5of5": n5,
    "label_cover_hist": {str(k): [list(x) for x in v] for k, v in lhist.items()},
    "magic_label_cover": len(mcover),
    "max_label_cover": maxcov,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/72_magic37_identity_compare.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/72_magic37_identity_compare.json")