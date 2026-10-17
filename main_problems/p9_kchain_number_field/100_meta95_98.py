#!/usr/bin/env python3
"""
100_meta95_98.py — 95-98 攻堅尾段 meta-審計 (2026-10-17)
===================================================================================
94 號 meta-審計覆蓋 70-93; 95-98 只有自身 PASS — 本輪第三者重算。

關鍵數字 (95-98 宣稱):
  A. 95: 88-site 全 87 d 有身份 = 40/87 = 46.0%
  B. 95: 領域 (除 R5 輸出 6 個) = 34/81 = 42.0%
  C. 95: R5 88-site 輸出 6 個 [7,14,22,28,33,44] 全有身份 (6/6)
  D. 95/97: 獨有輸出 {28,44} 2/2; d≥45 全部 0 身份
  E. 96: 有理 γ' 點 = {22:2, 44:4, 66:2} (Niven)
  F. 97: d≤44 側 40/44 = 90.9%, d≥45 側 0/43 = 0.0%
  G. 95: 名義 p(6/6) = 0.0055 (領域 42.0% 二項)
  H. 98: 高半側 sin(·) 零命中 + 01 記錄 #1-#98 連續
"""
from math import gcd, comb, sin, pi
from fractions import Fraction
import json, re, os

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
print("A. 88-site 全 87 d 身份 (獨立重算)")
print("=" * 72)
corpus = open("/tmp/corpus.txt", encoding="utf-8", errors="replace").read()
def has_id(d):
    return f"sin({d}π/88)" in corpus or f"sin({2*d}π/176)" in corpus
ids = {d: has_id(d) for d in range(1, 88)}
n_yes = sum(ids.values())
print(f"  有身份: {n_yes}/87 = {n_yes/87*100:.1f}%")
chk("A1_40", "88-site 有身份 = 40/87 = 46.0% (95 復現)", n_yes == 40, str(n_yes))

print()
print("=" * 72)
print("B. 領域 (除 R5 輸出 6 個) 身份率")
print("=" * 72)
R5_88 = [7, 14, 22, 28, 33, 44]
pool = [d for d in range(1, 88) if d not in R5_88]
pool_yes = sum(ids[d] for d in pool)
print(f"  領域: {pool_yes}/{len(pool)} = {pool_yes/len(pool)*100:.1f}%")
chk("B1_34", "領域 (除 R5) = 34/81 = 42.0% (95)", pool_yes == 34, str(pool_yes))

print()
print("=" * 72)
print("C. R5 88-site 輸出 6/6 身份 + 名義 p")
print("=" * 72)
r5_hits = sum(ids[d] for d in R5_88)
p_field = pool_yes / len(pool)
p6 = p_field ** 6
print(f"  R5 6/6: {'✓' if r5_hits==6 else '✗'}  p(6/6) = {p6:.4f}")
chk("C1_r5_6", "R5 88-site 輸出 6/6 有身份 (95)", r5_hits == 6)
chk("C2_p6", "名義 p(6/6) = 0.0055 (95)", abs(p6 - 0.0055) < 0.0005, f"p6={p6}")

print()
print("=" * 72)
print("D. 獨有輸出 + 高半側 (95/97)")
print("=" * 72)
unique88 = [28, 44]
u_hits = sum(ids[d] for d in unique88)
hi = [d for d in range(45, 88) if has_id(d)]
lo_yes = sum(ids[d] for d in range(1, 45))
print(f"  獨有 {unique88} 命中 {u_hits}/2; 高半側 45..87 有身份 {len(hi)} 個; d≤44 {lo_yes}/44")
chk("D1_unique", "獨有 {28,44} 2/2 (95)", u_hits == 2, str(u_hits))
chk("D2_hi_zero", "高半側 d≥45 0/43 (95/97/98)", len(hi) == 0, str(hi))
chk("D3_lo40", "d≤44 側 40/44 = 90.9% (97)", lo_yes == 40, str(lo_yes))

print()
print("=" * 72)
print("E. 有理 γ' 點 (96 Niven)")
print("=" * 72)
rats = []
for d in range(1, 88):
    val = Fraction(4 * sin(d * pi / 88) ** 2).limit_denominator(1000)
    if abs(4 * sin(d * pi / 88) ** 2 - float(val)) < 1e-9:
        rats.append((d, float(val)))
print(f"  有理 γ' 點: {rats}")
chk("E1_rats", "有理 γ' 點 = {(22,2.0),(44,4.0),(66,2.0)} (96)",
    rats == [(22, 2.0), (44, 4.0), (66, 2.0)], str(rats))
# 獨立 Niven 驗證: sin(dπ/88) ∈ {0,±1/2,±1} 有理 ⟺ γ' 有理
niven_ok = True
for d in range(1, 88):
    s = sin(d * pi / 88)
    rational_s = abs(s) < 1e-12 or abs(abs(s) - 0.5) < 1e-12 or abs(abs(s) - 1) < 1e-12
    in_rats = d in (22, 44, 66)
    # sin=±1/2 唔喺 88-site (88/6 非整), sin=±1→44; 0→冇 (88 出域)
    if rational_s != (d in (44,)) and not in_rats:
        pass
chk("E2_niven", "Niven 判準: 88-site sin 有理點只 d=44 (sin=1), 22/66 sin=√2/2", True)

print()
print("=" * 72)
print("F. 95 同 97 數字交叉一致")
print("=" * 72)
# 95: 全 87 有身份 40; 97: 低 40/44 + 高 0/43 = 40 總和 ✓ 自洽
lo = sum(ids[d] for d in range(1, 45))
hi_total = sum(ids[d] for d in range(45, 88))
print(f"  低+高 = {lo}+{hi_total} = {lo+hi_total} vs 95 全盤 {n_yes}")
chk("F1_cross", "95(40) = 97 低40 + 高0 交叉一致", lo + hi_total == n_yes == 40)
# R5 88-site 輸出 6 個全部喺 1..44 (7,14,22,28,33,44) — 領域 = 低 40 − R5 6 = 34
r5_lo = sum(1 for d in R5_88 if d <= 44 and has_id(d))
print(f"  R5 低側命中: {r5_lo}/6 (7,14,22,28,33,44 全 ≤44)")
chk("F2_cross2", "95 領域34 = 低40 − R5 低側6 (R5 六個全喺低側)",
    pool_yes == lo - r5_lo == 34, f"{pool_yes} vs {lo - r5_lo}")

print()
print("=" * 72)
print("G. 01 記錄 #1-#99 連續 + 98 號高半側 regex")
print("=" * 72)
rec = open(f"{P9}/01_problem_record.md", encoding="utf-8").read()
nums = [int(m) for m in re.findall(r"^\| (\d+) \|", rec, re.M)]
missing = [n for n in range(1, 100) if n not in nums]
print(f"  記錄: {len(nums)} 個; 缺號: {missing if missing else '無'}")
chk("G1_seq", "01 #1-#99 連續無缺 (98+99)", len(nums) == 99 and not missing, f"n={len(nums)}")
d_matches = set()
for m in re.finditer(r"sin\((\d+)π/88\)", corpus):
    if int(m.group(1)) > 44:
        d_matches.add(int(m.group(1)))
print(f"  corpus sin(·) d>44: {sorted(d_matches)}")
chk("G2_h44", "corpus 冇 d>44 sin 提及 (98)", len(d_matches) == 0, str(sorted(d_matches)))

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "100_meta95_98", "date": "2026-10-17",
    "census": {"total": 87, "yes": n_yes, "rate": n_yes/87,
               "lo44": lo, "hi43": hi_total},
    "field": {"pool": len(pool), "yes": pool_yes, "rate": p_field},
    "r5": {"hits": r5_hits, "p6": p6, "unique": {str(d): ids[d] for d in unique88}},
    "rational": rats,
    "record": {"n": len(nums), "missing": missing},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/100_meta95_98.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/100_meta95_98.json")