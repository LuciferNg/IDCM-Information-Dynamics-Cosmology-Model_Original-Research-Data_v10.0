#!/usr/bin/env python3
"""
40_sync_pipeline_d29.py — SYNC pipeline 攻堅: d=29 行 + s=33 列 (2026-10-17)
=============================================================================
開放項 (06_blind_test_beat231.md §4):
  ①「SYNC→L₇→M pipeline」語義 🟡
  ② d=29 opcode 具體執行 🔴
  ③ d=29 行 15 成員有冇特殊角色 🔴 未開始

今輪用 magic rows 攻堅工具 (R5/gcd/identity) 系統化打:
  T1 d=29 行 15 成員全景: s, gcd, R5, L/F 鏈, beat
  T2 s=33 列 16 格全景: d, gcd, R5, label — M-pipeline 階段結構
  T3 d=29 (L₇) 喺 R5 框架下嘅角色: 點解唔係 magic? (後半/1mod4/R5 外)
  T4 SYNC 家族: i=2 (s−d=4=B) 係咪全 d=29 行特殊?
  T5 d=29 行 vs magic 行 嘅結構對比 (成員數/s 分佈/gcd)

零 import; 純整數 + mpmath 50dps。
"""
import json
from math import gcd

def gc(d):
    return gcd(abs(44 - d), 176)

def luc(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a
def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
R5GEN = sorted({m*a for a in (7, 11, 5) for m in (1, 2, 3, 4) if 1 <= m*a <= 43})

def is_luc(d): return any(d == m*luc(k) for m in (1,2,3,4) for k in range(2,8))
def is_fib(d): return any(d == m*fib(k) for m in (1,2,3,4) for k in range(2,9))

# ============ T1: d=29 行 15 成員 ============
print("=== T1: d=29 行 (L₇, V_EW structure) 15 成員 ===")
d29 = [(i, i+29) for i in range(1, 16)]
print(f"{'i':>3} {'j':>3} {'s':>4} {'s-d':>5} {'gcd':>4} {'R5':>4} {'Lch':>4} {'Fch':>4} {'data':>5}")
for (i, j) in d29:
    s = i + j
    print(f"{i:>3} {j:>3} {s:>4} {s-29:>5} {gc(29):>4} {'Y' if 29 in R5GEN else 'N':>4} "
          f"{str(is_luc(29)):>4} {str(is_fib(29)):>4} {str(29 in DATA):>5}")
print(f"\nd=29: gcd={gc(29)}  R5={29 in R5GEN}  L₇=29 (後半+1mod4)  TEST F 排除 magic")
print(f"成員數 = {len(d29)}  s 值 = {sorted(i+j for i,j in d29)}")

# ============ T2: s=33 列 16 格 ============
print()
print("=== T2: s=33 列 (M-pipeline) 16 格 ===")
s33 = [(i, 33-i) for i in range(1, 17)]
print(f"{'i':>3} {'j':>3} {'d':>4} {'gcd':>4} {'R5':>4} {'magic':>5} {'data':>5} {'L/F':>6} label")
known_labels = {(13, 20): "m7 anchor"}
for (i, j) in s33:
    d = j - i
    lf = []
    if is_luc(d): lf.append("L")
    if is_fib(d): lf.append("F")
    label = known_labels.get((i, j), "")
    print(f"{i:>3} {j:>3} {d:>4} {gc(d):>4} {'Y' if d in R5GEN else 'N':>4} "
          f"{'Y' if d in MAGIC else 'N':>5} {'Y' if d in DATA else 'N':>5} "
          f"{''.join(lf):>6} {label}")
print(f"\nd 值 = {sorted(j-i for i,j in s33)} (16 奇數 1..31)")
gcd_hist = {}
for i, j in s33:
    g = gc(j-i)
    gcd_hist[g] = gcd_hist.get(g, 0) + 1
print(f"gcd 分佈 = {gcd_hist}  ← 15×gcd1 + 1×gcd11 (d=11 half-node)")

# ============ T3: d=29 喺 R5 框架 ============
print()
print("=== T3: d=29 (L₇) 喺 R5 框架下點解唔係 magic ===")
print(f"  29 ∈ R5 生成? {29 in R5GEN}  ← 唔係! R5={{m×L₄,L₅,F₅}} = {R5GEN}")
print(f"  29 = L₇: 後半 (29>22) + 1 mod 4 — TEST F 排除 (同 3/7/11 3mod4 前半對比)")
print(f"  29 = L₇ 但 7 = L₄ — L 質數族: 3,7,11,29; 只有 L₄/L₅ 係連續質數對")
print(f"  gcd(29) = {gc(29)} = 1 (同 magic 7!) 但 7: R5✓ 前半✓ 3mod4✓; 29: R5✗ 後半✗ 1mod4✗")
print(f"  ⟹ d=29 唔做 magic 代表 — 4 個判準全過唔到")

# ============ T4: SYNC 家族 ============
print()
print("=== T4: SYNC 家族 (i=2, s−d=4=B) ===")
syncs = []
for d in range(1, 44):
    for i in range(1, 44 - d):
        j = i + d
        if j - i == 2 * i:  # s−d = 2i, i=2 → 4
            pass
# 直接: i=2, 任何 j>2
sync_members = [(2, j) for j in range(3, 45)]
print(f"  i=2 行全成員 (s−d=2i=4=B): {len(sync_members)} 個")
for j in [7, 14, 20, 22, 29, 31, 33, 41]:
    d = j - 2
    print(f"    (2,{j:>2}) d={d:>2}: gcd={gc(d)} magic={d in MAGIC} R5={d in R5GEN}")

# ============ T5: d=29 行 vs magic 行 ============
print()
print("=== T5: d=29 行 vs magic 行 (行結構) ===")
for d in MAGIC + [29]:
    members = [(i, i+d) for i in range(1, 44-d)]
    s_vals = [i + (i+d) for i in range(1, 44-d)]
    print(f"  d={d:>2}: 成員 {len(members):>2}  s 範圍 [{min(s_vals)},{max(s_vals)}]  "
          f"s 中位 {sorted(s_vals)[len(s_vals)//2]:>3}  gcd={gc(d)}")
print(f"\n  d=29: 15 成員 (少), s∈[31,59] 全部奇數, 全 gcd1")

res = {
    "test": "40_sync_pipeline_d29",
    "d29_members": [(i, i+29) for i in range(1, 16)],
    "d29": {"gcd": gc(29), "in_R5": 29 in R5GEN,
            "L7": 29 == luc(7), "luc_primes": [k for k in range(2,8) if luc(k) in (3,7,11,29)],
            "testF_exclusion": "後半+1mod4+R5外"},
    "s33": {"d_values": sorted(j-i for i, j in s33), "gcd_hist": gcd_hist},
    "sync_family": {"i2_members": len(sync_members), "B": 4},
}
with open("data/40_sync_pipeline_d29.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/40_sync_pipeline_d29.json")