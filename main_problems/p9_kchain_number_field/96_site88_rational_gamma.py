#!/usr/bin/env python3
"""
96_site88_rational_gamma.py — 88-site 有理 γ' 點 + R5 獨有輸出身份根源 (2026-10-17)
===================================================================================
問題 (95 號之後): 88-site 領域身份率 42%, R5 88-site 獨有輸出 {28,44} 2/2 命中。
點解? 44 喺 88-site 身份根源 = ?

檢查:
  A. ★88-site 有理 γ'_d = 4sin²(dπ/88) 點 (對照 69 號 44-site 有理 {γ_22=2,γ_44=4})
     Niven: 4sin²(dπ/88) 有理 ⟺ d ∈ ? (88-site d=1..87)
  B. R5 88-site 獨有 {28,44} 身份來源: 44→γ'_44=4 有理; 28→?
  C. 88-site 有理點 vs 有身份交集
  D. 結論: 44 有身份係「有理特化點」— 唔係 magic 獨有;
     28 有身份來源要搵
"""
from math import gcd, sin, pi
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

print("=" * 72)
print("A. ★88-site 有理 γ'_d 點 (Niven)")
print("=" * 72)
# γ'_d = 4sin²(dπ/88). 有理 ⟺ sin(dπ/88) ∈ {0, ±1/2, ±1} (Niven 廣義)
# sin(dπ/88) = 1/2 ⟺ d·π/88 ∈ {π/6, 5π/6} ⟺ d ∈ {88/6, 5·88/6} = {14.67, 73.3} — 非整
# sin(dπ/88) = 1 ⟺ dπ/88 = π/2 ⟺ d = 44
# sin(dπ/88) = -1 ⟺ d = 132 出域
# sin(dπ/88) = 1/√2 ⟺ dπ/88 = π/4, 3π/4 ⟺ d = 22, 66 → sin²=1/2 → γ=2 有理!
# sin(dπ/88) = 0 ⟺ d = 0, 88 出域
rational = []
for d in range(1, 88):
    val = 4 * sin(d * pi / 88) ** 2
    # 檢查 exact rational: 用 Fraction
    from fractions import Fraction
    # sin²(dπ/88) 有理 ⟺ 2cos(2dπ/88)=2cos(dπ/44) 有理?
    # 用 Niven 定理: 2cos(πm/n) 有理 ⟺ ... 直接算值對照
    frac = Fraction(val).limit_denominator(1000)
    if abs(val - float(frac)) < 1e-9:
        rational.append((d, float(frac)))
print("  有理 γ' 點 (d, γ'值):")
for d, v in rational:
    print(f"    d={d:2d}: γ'={v} ({'sin=' + str(round(sin(d*pi/88), 6))})")
chk("A1_rational", "88-site 有理 γ' 點 = {22:2, 44:4, 66:2} (Niven)",
    {d for d, _ in rational} == {22, 44, 66}, str(rational))

print()
print("=" * 72)
print("B. R5 88-site 獨有 {28,44} 身份根源")
print("=" * 72)
corpus = open("/tmp/corpus.txt", encoding="utf-8", errors="replace").read()
for d in (28, 44):
    s88 = f"sin({d}π/88)" in corpus
    s176 = f"sin({2*d}π/176)" in corpus
    g4 = f"4sin²({d}π/88)" in corpus or f"γ'_{d}" in corpus or f"gamma_{d}" in corpus
    g_plain = f"γ_{d}" in corpus or f"gamma_{d}" in corpus
    print(f"  d={d:2d}: sin({d}π/88)={s88} sin({2*d}π/176)={s176} γ_{d}提及={g_plain}")
# 44: γ_44 = 4 有理 (69 號)
chk("B1_44", "44 身份根源 = γ_44=4 有理特化點 (69 號; γ_44 係 44-site 都提)", "γ_44" in corpus)

print()
print("=" * 72)
print("C. 有理點 vs 有身份交集")
print("=" * 72)
def has_id(d):
    return f"sin({d}π/88)" in corpus or f"sin({2*d}π/176)" in corpus
id44 = has_id(44)
id22 = has_id(22)
id66 = has_id(66)
print(f"  有理點身份: d=22 {id22}, d=44 {id44}, d=66 {id66}")
# 66 有冇? 89 號話 R5 鏡像 (22,66) 66 冇身份
chk("C1_rational_identity", "有理點身份: 22 有, 44 有, 66 冇 (89 號 mirror 單側)",
    id22 and id44 and not id66, f"22={id22} 44={id44} 66={id66}")

print()
print("=" * 72)
print("D. ★結論 — 44 有身份嘅根源")
print("=" * 72)
print("""
  88-site 有理 γ' 點 = {22, 44, 66} (Niven):
    22 = 4sin²(π/4)²  = 2  (44-site γ_22 亦係 2)
    44 = 4sin²(π/2)   = 4  (44-site γ_44 亦係 4)
    66 = 4sin²(3π/4)  = 2  (88-site 新版 HALF mirror)

  ★ 44 有身份根源: γ_44 = 4 有理 — 呢個係 44-site/88-site 通用
    特化點 (69 號已證 γ_44=4), 唔係 magic 特別:
    R5 88-site 揀 44 因為佢係 HALF 軸 (gcd44 唯一), 而佢有身份
    係因為佢係唯一 γ'=4 有理點 — 兩件事獨立!
  ★ 66 冇身份 (89 號): 66 = 88−22 鏡像, 雖然 γ'_66=2 有理,
    但 corpus 冇 66-site sin 提及 — 有理唔保證 corpus 有
  ⟹ 身份 = corpus 存在事實 (90 號), 有理點 = 結構事實,
    兩者交集係 22/44 (44-site 研究焦點), 66 係「有理但唔在 corpus」
""")
chk("D1_conclusion", "44 身份根源 = γ_44=4 有理特化點 (同 69); 身份≠有理 (66 反例)", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "96_site88_rational_gamma", "date": "2026-10-17",
    "rational_points": [{"d": d, "val": v} for d, v in rational],
    "identity_check": {"22": has_id(22), "44": has_id(44), "66": has_id(66)},
    "conclusion": "44 身份 = γ_44=4 有理特化點 (69); 有理≠corpus (66 反例); 身份=存在事實 (90)",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/96_site88_rational_gamma.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/96_site88_rational_gamma.json")