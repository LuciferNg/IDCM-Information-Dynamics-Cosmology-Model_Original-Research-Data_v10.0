#!/usr/bin/env python3
"""
36_anchor_chain_mapping.py — 鏈→類映射 + 衝突位鑑別特徵 (2026-10-17)
=================================================================
35 號殘留: gcd2 (14 vs 10) 同 gcd16 (28 出局) 未閉合 + Lucas>Fib 判準 FAIL。

目標: 搵一條規則 T (唔含 magic 結果) 同時:
  (a) gcd2 内選 14 (2L₄) 唔選 10 (2F₅)
  (b) gcd16 内 28 (4L₄) 出局
  且唔破壞已鎖 4 個 (gcd1=7, gcd8=20, gcd11=33, gcd22=22)

候選特徵:
  C1 前半/後半 (d<22 vs d>22): 20<22 前半, 28>22 後半; 14<22, 10<22 → 只解 (b)
  C2 d mod 16 (≡4 mod16 收, ≡12 mod16 唔收?): 20≡4 28≡12; 14≡14 10≡10 → 解 (b), 唔解 (a)
  C3 鏈類型: Lucas vs Fib → FAIL (35 號)
  C4 anchor 自身 gcd: L₄(7)→gcd1, F₅(5)→gcd1, L₅(11)→gcd11
  C5 m 同 anchor 嘅乘積 mod 16 / 2-adic 指紋
  C6 data 接觸 (32 號: data 格端點)
  C7 鏡像 44−d 去向 (30 號: gcd16 鏡像→gcd4 缺類; gcd8 鏡像→gcd4)

輸出: 每個候選 R5 成員嘅全特徵表 + 一刀切規則檢驗。
零 import; 純整數。
"""
import json
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}

def gcl(d):
    return gcd(abs(44 - d), 176)

def luc(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

L = {k: luc(k) for k in range(1, 8)}   # {..: 1,2:3,3:4,4:7,5:11,6:18,7:29}
F = {k: fib(k) for k in range(1, 8)}   # {..: 1,2:1,3:2,4:3,5:5,6:8,7:13}

# R5 生成 (anchor 7,11,5) 完整分析
anchors = {7: ("L₄", 4), 11: ("L₅", 5), 5: ("F₅", 5)}
rows = []
for a in anchors:
    for m in (1, 2, 3, 4):
        d = m * a
        if d > 43:
            continue
        mir = 44 - d
        rows.append({
            "d": d, "anchor": a, "chain": anchors[a][0], "m": m,
            "rep": f"{m}×{anchors[a][0]}",
            "gcd": gcl(d),
            "mirror": mir, "mirror_gcd": gcl(mir),
            "d_mod16": d % 16, "d_mod8": d % 8,
            "half": "前" if d < 22 else ("軸" if d == 22 else "後"),
            "data": d in DATA, "magic": d in MAGIC,
            "is_lucas_chain": d in {m * L[k] for m in (1, 2, 3) for k in range(2, 7)},
            "is_fib_chain": d in {m * F[k] for m in (1, 2, 3, 4) for k in range(2, 8)},
        })

# 特徵對照: 每個衝突位
conf1 = [(r for r in rows if r["d"] in (10, 14))]
conf2 = [(r for r in rows if r["d"] in (20, 28))]

# 一刀切候選規則檢驗
def apply_rule(rows, key_fn, pick_fn):
    """key 分組, 每組揀 pick_fn — 回傳揀咗嘅 d 集"""
    picked = set()
    groups = {}
    for r in rows:
        groups.setdefault(key_fn(r), []).append(r)
    for k, grp in groups.items():
        chosen = pick_fn(grp)
        if chosen is not None:
            picked.add(chosen["d"])
    return picked

# C5: 2-adic — v2(d)
def v2(x):
    c = 0
    while x % 2 == 0:
        x //= 2; c += 1
    return c

rows2 = []
for r in rows:
    r2 = dict(r)
    r2["v2_d"] = v2(r2["d"])
    rows2.append(r2)
rows = rows2

print("=== R5 生成成員全特徵表 ===")
print(f"{'d':>3} {'rep':>8} {'gcd':>4} {'mir':>4} {'mirg':>4} {'m16':>4} {'v2':>3} {'half':>3} {'data':>5} {'Lch':>4} {'Fch':>4} {'magic':>5}")
for r in sorted(rows, key=lambda x: x["d"]):
    print(f"{r['d']:>3} {r['rep']:>8} {r['gcd']:>4} {r['mirror']:>4} {r['mirror_gcd']:>4} {r['d_mod16']:>4} {r['v2_d']:>3} {r['half']:>3} {str(r['data']):>5} {str(r['is_lucas_chain']):>4} {str(r['is_fib_chain']):>4} {str(r['magic']):>5}")

# 候選規則測試
print("\n=== 候選一刀切規則 ===")

def test(name, key_fn, pick_fn):
    picked = apply_rule(rows, key_fn, pick_fn)
    got_m = sorted(picked & set(MAGIC))
    got_nm = sorted(picked - set(MAGIC))
    good = (sorted(picked) == sorted(MAGIC))
    print(f"  {name}: 揀咗 {sorted(picked)}  magic={got_m} 非magic={got_nm}  完全=magic? {good}")
    return good

# 規則 A: 每 gcd 類 + 組内 L-chain 優先 (期望 gcd16 28 都係 L 鏈 → 衝突照舊)
test("A gcd類+L鏈優先", lambda r: r["gcd"], lambda grp: next((x for x in grp if x["is_lucas_chain"]), None))
# 規則 B: 每 gcd 類 + 組内最細 m
test("B gcd類+最細m", lambda r: r["gcd"], lambda grp: min(grp, key=lambda x: x["m"]))
# 規則 C: 每 gcd 類 + 組内最大 m
test("C gcd類+最大m", lambda r: r["gcd"], lambda grp: max(grp, key=lambda x: x["m"]))
# 規則 D: 每 gcd 類 + 組内 d mod8 = 4 (which are... 14≡6,10≡2,20≡4,28≡4 → 撞)
test("D gcd類+dmod8=4", lambda r: r["gcd"], lambda grp: next((x for x in grp if x["d_mod8"] == 4), None))
# 規則 E: 每 gcd 類 + 組内前半優先 (first then lucas)
test("E gcd類+前半優先", lambda r: r["gcd"], lambda grp: min(grp, key=lambda x: (x["half"] == "後", x["m"])))
# 規則 F: 每 gcd 類 + 組内 NOT data + 最細 m
# 注意 gcd11 組 = [11(data), 33]: 只有 33 非 data → 揀 33
def notdata_minm(grp):
    nd = [x for x in grp if not x["data"]]
    return min(nd, key=lambda x: x["m"]) if nd else None
test("F gcd類+非data+最細m", lambda r: r["gcd"], notdata_minm)

print("\n=== 逐衝突位分析 ===")
print("gcd2 (10 vs 14):")
for r in sorted([r for r in rows if r["gcd"] == 2], key=lambda x: x["d"]):
    print(f"  d={r['d']} {r['rep']}: L鏈={r['is_lucas_chain']} F鏈={r['is_fib_chain']} mod16={r['d_mod16']} v2={r['v2_d']} mirror={r['mirror']}(gcd{r['mirror_gcd']})")
print("gcd8 vs gcd16 (20 vs 28):")
for r in sorted([r for r in rows if r["gcd"] in (8, 16)], key=lambda x: x["d"]):
    print(f"  d={r['d']} {r['rep']}: gcd={r['gcd']} mod16={r['d_mod16']} v2={r['v2_d']} half={r['half']} mirror={r['mirror']}(gcd{r['mirror_gcd']})")

res = {"test": "36_anchor_chain_mapping", "rows": rows}
with open("data/36_anchor_chain_mapping.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/36_anchor_chain_mapping.json")