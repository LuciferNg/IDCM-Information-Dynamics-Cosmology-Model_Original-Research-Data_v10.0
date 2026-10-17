#!/usr/bin/env python3
"""
88_site88_core_arithmetic.py — 88-site Magic 核心算術必然對照 (2026-10-17)
===================================================================================
問題 (80-81 號之後): 44-site 有「3 算術必然」{22,33,20} (δ=44−d 唯一類)。
88-site (46 號對偶鏈域): 6 個輸出 [7,14,22,28,33,44] — 邊啲都有「算術必然」?

88-site 定義 (66/67 號審計確認):
  ω'_n = 2sin(πn/88), n=1..88; gcd 類 = gcd(|88−n|, 176)?
  (88-site gcd 類 gcl88(d) = gcd(|88−d|,176) — 88 係 HALF 軸)
  DATA88 = {11,13,17,19,21,25} ∩ [1,88] (相同 data 行)

檢查:
  A. 88-site gcd 類結構: 每個 gcd 類成員
  B. data-free 唯一代表: 邊啲 gcd 類 data-free 後得 1 個?
  C. ★對照 44-site 3 必然: 88-site 邊啲輸出係「算術必然」?
     44→這 88/2 (HALF); 28=? 33=? 22=? 14=? 7=?
  D. 跨 N 結論: 「3 算術必然」喺 88-site 變幾多個? 模式係咪 scale?
"""
from math import gcd
from itertools import combinations
import json

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

def gcl88(d):
    return gcd(abs(88 - d), 176)

def gcl44(d):
    return gcd(abs(44 - d), 176)

DATA = {11, 13, 17, 19, 21, 25}
M88 = [7, 14, 22, 28, 33, 44]   # 37 號 88-site R5 輸出
M44 = [7, 14, 20, 22, 33]       # 44-site magic

print("=" * 72)
print("A. 88-site gcd 類結構 (d=1..87, gcl88)")
print("=" * 72)
byg88 = {}
for d in range(1, 88):
    byg88.setdefault(gcl88(d), []).append(d)
for g in sorted(byg88):
    free = [d for d in byg88[g] if d not in DATA]
    flag = " ← R5 輸出!" if set(free) & set(M88) else ""
    print(f"    gcd{g:3d}: {len(byg88[g])} 個 → data-free {free}{flag}")

print()
print("=" * 72)
print("B. data-free 唯一代表 (88-site)")
print("=" * 72)
uniq88 = {}
for g in sorted(byg88):
    free = [d for d in byg88[g] if d not in DATA]
    uniq88[g] = free
    if len(free) == 1:
        print(f"    gcd{g}: 唯一 data-free = {free[0]}")
chk("B1_unique_classes", "88-site data-free 唯一類存在 (HALF 軸 88/2=44 等)",
    len({g: v for g, v in uniq88.items() if len(v) == 1}) >= 1)

print()
print("=" * 72)
print("C. ★R5 88-site 輸出 [7,14,22,28,33,44] 嘅算術必然性")
print("=" * 72)
for d in M88:
    g = gcl88(d)
    free = uniq88[g]
    is_uniq = len(free) == 1
    print(f"  d={d:2d}: gcd88={g:3d} 類 data-free={free}  → 唯一? {is_uniq}")
# 44 = 88/2? HALF
chk("C1_half44", "44 = 88/2 (HALF 鏡像軸) — 44-site 22 嘅 88-site 對應",
    gcl88(44) == 44 and len(uniq88[gcl88(44)]) == 1,
    f"gcd88(44)={gcl88(44)} 唯一類={uniq88.get(gcl88(44))}")
# 同 44-site 3 必然比較
print()
print("  44-site 3 必然: 22=44/2, 33=44−11, 20=4F₅(生成集唯一)")
print("  88-site 對照:")
pairs = {
    "22→44": (22, 44), "33→?": (33, 33), "20→28?": (20, 28),
    "11→22": (11, 22), "14→28?": (14, 28), "7→7": (7, 7),
}
for label, (d44, d88) in pairs.items():
    g44 = gcl44(d44)
    g88 = gcl88(d88)
    u44 = [x for x in range(1, 44) if gcl44(x) == g44 and x not in DATA]
    u88 = [x for x in range(1, 88) if gcl88(x) == g88 and x not in DATA]
    print(f"  {label}: d44={d44:2d} gcd44={g44:2d} 唯一? {len(u44)==1}  |  d88={d88:2d} gcd88={g88:3d} 唯一? {len(u88)==1}")

print()
print("=" * 72)
print("D. ★跨 N 結論")
print("=" * 72)
n44 = [d for d in M44 if len([x for x in range(1,44) if gcl44(x)==gcl44(d) and x not in DATA]) == 1]
n88 = [d for d in M88 if len([x for x in range(1,88) if gcl88(x)==gcl88(d) and x not in DATA]) == 1]
print(f"  44-site R5 輸出算術必然 (data-free 唯一類): {n44}")
print(f"  88-site R5 輸出算術必然 (data-free 唯一類): {n88}")
chk("D1_scale", f"跨 N: 44-site 必然 {n44} vs 88-site 必然 {n88}",
    set(n44) == {22, 33, 20} and len(n88) >= 3, f"{n44} vs {n88}")

# 7 嘅 88-site 角色
g7_44 = gcl44(7)
g7_88 = gcl88(7)
u7_88 = [x for x in range(1, 88) if gcl88(x) == g7_88 and x not in DATA]
print()
print(f"  7 喺 88-site: gcd88={g7_88} 類 data-free={u7_88} — Lucas 話系照舊?")
chk("E1_7_role", "7 → 88-site gcd 類唔唯一 (Lucas 話系層面照舊)",
    len(u7_88) > 1, f"{u7_88}")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "88_site88_core_arithmetic", "date": "2026-10-17",
    "gcd88_classes": {str(g): {"all": len(v), "datafree": v} for g, v in sorted(byg88.items())},
    "M44_necessary": n44, "M88_necessary": n88,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/88_site88_core_arithmetic.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/88_site88_core_arithmetic.json")