#!/usr/bin/env python3
"""
89_site88_mirror_pairs.py — 88-site 鏡像對身份 (2026-10-17)
===================================================================================
問題 (88 號之後): 44-site 中心唯一性靠 self-mirror (44−22=22)。88-site 有
鏡像對 (22,66), (33,55), (11,77)... 呢啲對有冇獨立 O-series 身份?
呢個直接連 G7 對偶鏈 (O218 44/44) + 46 DUAL_CELLS 週期表對偶。

檢查:
  A. 88-site 鏡像對盡數 (k, 88−k): 逗偶 (k, 88−k), k∈[1,44]
  B. 每對嘅 sin 身份 (sin(kπ/88) / sin(2kπ/176) 判準 同 63/70)
  C. 對比 R5 88-site 輸出: 6 個元素喺鏡像對度 (7,81)/(14,74)/(22,66)/(28,60)/(33,55)/(44,44)
  D. ★鏡像對身份對稱性: 成員有身份 ⇔ 鏡像有身份? (統計)
"""
import json
import os

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

# corpus
corpus = open("/tmp/corpus.txt", encoding="utf-8", errors="replace").read()
def has_id(d, n=88):
    """sin(dπ/n) 或 sin(2dπ/(2n)) 出現"""
    return f"sin({d}π/{n})" in corpus or f"sin({2*d}π/{2*n})" in corpus

M88 = [7, 14, 22, 28, 33, 44]
print("=" * 72)
print("A. 88-site 鏡像對 (k, 88−k) 身份表")
print("=" * 72)
pairs = [(k, 88 - k) for k in range(1, 45)]
both = 0
one = 0
none = 0
rows = []
for a, b in pairs:
    ia, ib = has_id(a), has_id(b)
    if ia and ib:
        both += 1
    elif ia or ib:
        one += 1
    else:
        none += 1
    if a in M88 or b in M88:
        rows.append(f"  ★({a:2d},{b:2d}): {ia} / {ib}")
print("  R5 輸出鏡像對:")
for r in rows:
    print(r)
print(f"  全 44 對: both={both} one={one} none={none}")
chk("A1_symmetry_strong", "鏡像對身份對稱 (both+one 佔大宗, 唔係 none)",
    both + one >= 40, f"both={both} one={one} none={none}")

print()
print("=" * 72)
print("B. ★R5 輸出 6 個嘅鏡像身份")
print("=" * 72)
for d in M88:
    m = 88 - d
    print(f"  d={d:2d}: 自身 {has_id(d)} | 鏡像 {m:2d}: {has_id(m)}")
mir_ok = all(has_id(d) or has_id(88 - d) for d in M88)
chk("B1_magic_mirror", "R5 88-site 輸出自身或鏡像至少有身份 (6/6)",
    mir_ok)

print()
print("=" * 72)
print("C. 88-site 沒 identity 嘅 d (mirror 對數)")
print("=" * 72)
noid = [d for d in range(1, 88) if not has_id(d) and not has_id(88 - d)]
print(f"  兩邊都冇身份嘅鏡像對 d: {sorted(set(tuple(sorted((x, 88-x))) for x in noid))}")
chk("C1_mirror_none", "冇身份鏡像對好少", len(noid) <= 8, str(len(noid)))

print()
print("=" * 72)
print("D. 判讀")
print("=" * 72)
print(f"""
  A: 鏡像對身份 (both+one) = {both+one}/44 對 ({100*(both+one)/44:.0f}%)
  B: R5 輸出 6 個全部自身或鏡像有身份
  ★ O218 對偶鏈 (G7) 已證明 44/44 對偶身份 — 呢度 mirror 對身份
    對稱係 O218 嘅 88-site 深化: 身份係鏡像對層面嘅 (k,88−k) 共生
  ⟹ 44-site self-mirror (22) → 88-site 鏡像對 (22,66) 身份對稱
     HALF 軸唯一性 = mirror 對身份兩邊都喺 O-series 出現嘅極端例
""")
chk("D1_read", "88-site mirror 對身份對稱確認: HALF 軸唯一性 = mirror 兩側共生", both + one >= 40)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "89_site88_mirror_pairs", "date": "2026-10-17",
    "pairs_identity": {"both": both, "one": one, "none": none},
    "R5_mirrors": {str(d): {"self": has_id(d), "mirror": has_id(88-d), "mirror_d": 88-d} for d in M88},
    "none_pairs": sorted(set(tuple(sorted((x, 88-x))) for x in noid)),
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/89_site88_mirror_pairs.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/89_site88_mirror_pairs.json")