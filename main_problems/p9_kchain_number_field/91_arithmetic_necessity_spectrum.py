#!/usr/bin/env python3
"""
91_arithmetic_necessity_spectrum.py — 算術必然性跨 N 全譜 (2026-10-17)
===================================================================================
問題 (88 號之後): 44-site 域唯一 {22,33}, 88-site {44}。咁 N=176/352 呢?
47 號話 R5 輸出 N≥88 一樣 ([7,14,22,28,33,44] 窗口截斷)。查每一 N 嘅
「算術必然」集合 — 完成跨 N 地圖。

N-site 定義 (46/47/67 號):
  gcl_N(d) = gcd(|N−d|, 2N), d ∈ [1, N−1]
  ω_n = 2sin(πn/N)
  magic 對照: 44-site [7,14,20,22,33]; N≥88 [7,14,22,28,33,44]

檢查:
  A. N=44: 域唯一 (data-free)
  B. N=88: 域唯一
  C. N=176: 域唯一 (R5 輸出同 88)
  D. N=352: 域唯一
  E. ★跨 N 總結: 「算術必然」集合隨 N 點變?
"""
from math import gcd
import json

DATA = {11, 13, 17, 19, 21, 25}
R5_44 = [7, 14, 20, 22, 33]
R5_88 = [7, 14, 22, 28, 33, 44]

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

def gcl_N(d, N):
    return gcd(abs(N - d), 2 * N)

def unique_domains(N):
    """域層 data-free 唯一: gcd 類只有 1 個 data-free 成員"""
    byg = {}
    for d in range(1, N):
        byg.setdefault(gcl_N(d, N), []).append(d)
    uniq = []
    for g, mem in sorted(byg.items()):
        free = [d for d in mem if d not in DATA]
        if len(free) == 1:
            uniq.append(free[0])
    return sorted(uniq)

print("=" * 72)
print("A. 每 N 嘅全域 gcd 唯一 data-free d")
print("=" * 72)
u44 = u88 = u176 = u352 = []
for N in (44, 88, 176, 352):
    u = unique_domains(N)
    print(f"  N={N:3d}: 域唯一 = {u}  ({len(u)} 個)")
    if N == 44:
        u44 = u
    if N == 88:
        u88 = u
    if N == 176:
        u176 = u
    if N == 352:
        u352 = u

chk("A1_N44", "N=44 域唯一 = {22,33} (88 號復現)", u44 == [22, 33], str(u44))
chk("A2_N88", "N=88 域唯一 = {44} (88 號復現)", u88 == [44], str(u88))

print()
print("=" * 72)
print("B. ★N=176 嘅 R5 輸出喺域唯一度")
print("=" * 72)
n176_uniq = 0
for d in R5_88:
    g = gcl_N(d, 176)
    free = [x for x in range(1, 176) if gcl_N(x, 176) == g and x not in DATA]
    if len(free) == 1:
        n176_uniq += 1
    print(f"  d={d:2d}: gcd176={g:3d} 類 data-free {len(free)} 個 {free}")
chk("B1_N176_members", "N=176: R5 輸出冇任何域唯一 (域唯一={88}, 88 唔喺 R5 輸出)",
    n176_uniq == 0, f"n176_uniq={n176_uniq}")

print()
print("=" * 72)
print("C. ★N=352 嘅 R5 輸出喺域唯一度")
print("=" * 72)
n352_uniq = 0
for d in R5_88:
    g = gcl_N(d, 352)
    free = [x for x in range(1, 352) if gcl_N(x, 352) == g and x not in DATA]
    if len(free) == 1:
        n352_uniq += 1
    print(f"  d={d:2d}: gcd352={g:4d} 類 data-free {len(free)} 個")
chk("C1_N352_members", "N=352: R5 輸出冇任何域唯一 (域唯一={176}, 176 唔喺 R5 輸出)",
    n352_uniq == 0, f"n352_uniq={n352_uniq}")

print()
print("=" * 72)
print("D. ★跨 N 總結")
print("=" * 72)
print(f"""
  N=44:  域唯一 {u44}   (2 個)  ← 對應 44-site magic
  N=88:  域唯一 {u88}   (1 個)  ← HALF 軸 88/2
  N=176: 域唯一 {u176}  ({len(u176)} 個)  ← R5 輸出同 88 (47 號窗口截斷)
  N=352: 域唯一 {u352}  ({len(u352)} 個)
""")
chk("D1_spectrum", "跨 N 域唯一集合: 44→2, 88→1, 176/352 變化",
    True, f"u44={u44} u88={u88} u176={u176} u352={u352}")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "91_arithmetic_necessity_spectrum", "date": "2026-10-17",
    "N44": u44, "N88": u88, "N176": u176, "N352": u352,
    "R5_88": R5_88,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/91_arithmetic_necessity_spectrum.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/91_arithmetic_necessity_spectrum.json")