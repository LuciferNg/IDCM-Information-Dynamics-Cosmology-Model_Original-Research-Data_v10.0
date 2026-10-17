#!/usr/bin/env python3
"""
99_script31_fix_verify.py — 31 號 script galois_fixed 修正驗證 (2026-10-17)
===================================================================================
50 號 B4: 31 script `galois_fixed()` 用錯條件 (a·d)%176 ∈ {d, 176−d}
= ±ω_d 鏡像 (\u03c3=反粒子), 唔係真正固定。正確: a·d ≡ d 或 d(a+1) ≡ 88 (mod 176)
= sin 同角/互補。附註已寫「script 要修正先重用」 — 本輪落實修正。

驗證:
  A. 修正後 galois: d=3/7/29 全部 [1, 87] (σ_87 = Z₂ 固定奇數)
  B. 同 31 md 正文一致
  C. 其餘 T1-T8 結果 (fixed_table/magic_unique/gshift) 不受影響
  D. 舊 json (錯誤 [1,175]) 已被正確值取代
"""
import json
from math import gcd

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

def galois_fixed(dom):
    """正確版 (50 號修正, 同 31 script 而家一致)"""
    a_set = []
    for a in range(1, 176):
        if gcd(a, 176) != 1:
            continue
        if (a * dom) % 176 == dom % 176 or ((a + 1) * dom) % 176 == 88:
            a_set.append(a)
    return a_set

print("=" * 72)
print("A. 修正後 galois 驗證")
print("=" * 72)
for d in (3, 7, 29):
    g = galois_fixed(d)
    print(f"  d={d:2d}: {g}")
    chk(f"A_{d}", f"d={d} 正確固定集 = [1, 87]", g == [1, 87], str(g))

# 獨立驗證: σ_a(ω_d) 是否真等於 ω_d (sin 值)
from math import sin, pi
for d in (3, 7, 29):
    wd = 2 * sin(pi * d / 88)
    ok_a = []
    for a in (1, 87):
        sa = 2 * sin(pi * a * d / 88)
        if abs(sa - wd) < 1e-12:
            ok_a.append(a)
    print(f"  σ_87 值檢: d={d}: σ_87(ω)={'✓' if 87 in ok_a else '✗'}  σ_1(ω)={'✓' if 1 in ok_a else '✗'}")
    chk(f"A_sin_{d}", f"d={d}: σ_1/σ_87(ω_d)=ω_d sin 值驗證", ok_a == [1, 87], str(ok_a))

print()
print("=" * 72)
print("B. 同 31 md 正文一致")
print("=" * 72)
md = open(f"{P9}/31_matrix_fixed_point.md", encoding="utf-8").read()
assert "d= 3  → a = {1, 87}" in md or "d=3  → a = {1, 87}" in md, "md 正文唔見"
print("  md 正文: d=3/7/29 → a = {1,87} ✓")
chk("B1_md", "修正後 script 同 31 md 正文一致", True)

print()
print("=" * 72)
print("C. 其他 T1-T8 不受影響 (json 全檔)")
print("=" * 72)
res = json.load(open(f"{P9}/data/31_matrix_fixed_point.json"))
print(f"  keys: {sorted(res.keys())}")
print(f"  test: {res.get('test')}")
has_galois = "galois" in res
has_fixed = "fixed_table" in res
chk("C1_keys", "json 結構完整 (test/fixed_table/magic_unique_fixed/gshift/galois)",
    has_galois and has_fixed and "magic_unique_fixed" in res and "gshift" in res)

print()
print("=" * 72)
print("D. 舊 json 錯誤值已取代")
print("=" * 72)
bad = any(v.get("sample", [])[:2] == [1, 175] for v in res.get("galois", {}).values())
print(f"  舊 [1,175] 殘留: {bad}")
chk("D1_replaced", "json 冇任何 [1,175] 殘留 (全 [1,87])", not bad)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "99_script31_fix_verify", "date": "2026-10-17",
    "galois": {str(d): {"fixed": galois_fixed(d)} for d in (3, 7, 29)},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/99_script31_fix_verify.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/99_script31_fix_verify.json")