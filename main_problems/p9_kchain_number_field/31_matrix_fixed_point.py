#!/usr/bin/env python3
"""
31_matrix_fixed_point.py — 7 作為 2D 矩陣不動點測試 (2026-10-17)
================================================================
調律者指示: 「嘗試把7當成2D pattern 中的矩陣不動點測試」

框架:
  44×44 格平面, 行 d=|i−j| 嘅位置集 P_d = {(i,j): |i−j|=d}
  magic row 7 → 2D pattern P_7
  測試: 邊啲 operator O 令 O(P_7)=P_7? 對比其他 d — 7 有冇「獨特固定性」?

Operator 集 (全部作用喺格點座標):
  T1 transpose:         (i,j)→(j,i)               — 所有 d 都固定 (|j−i|=d) 預期 trivial
  T2 mirror44:          (i,j)→(44−i,44−j)        — |(44−i)−(44−j)|=|j−i|=d 預期 trivial
  T3 mirror88:          (i,j)→(88−i,88−j)        — 88 週期鏡像 (反粒子對稱投影)
  T4 neg44:             (i,j)→(44−i, j) 或 (i,44−j) — 單側鏡像
  T5 diag_shift1:       (i,j)→(i+1,j+1) mod 44    — 沿主對角線滑動
  T6 diag_shift2:       (i,j)→(i+2,j+2) mod 44
  T7 anti_diag_shift1:  (i,j)→(i+1,j−1) mod 44    — 沿反對角線滑動
  T8 gcd_shift:         d→d+k 保持 gcd(|44−d|,176) 類? (行層 operator)
  T9 Galois:            σ_a(ω_d)=ω_d 不動點 (ω 層)

判準: 若 O(P_7)=P_7 但 O(P_d)≠P_d (對 generic d), 則「7 = O 嘅獨特不動 point」
零 import 原推導; 純整數。
"""
import json
from math import gcd
from collections import Counter

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}

def gcl(d):
    return gcd(abs(44 - d), 176)

def P(d):
    """d 行位置集 (上三角唯象: i<j)"""
    return frozenset((i, j) for i in range(1, 45) for j in range(i + 1, 45) if j - i == d)

def norm(pair, mod=44):
    """格點歸一化 mod 44 (1..44 → 0..43 計算後還原)"""
    i, j = pair
    def red(x):
        x = x % mod
        return 44 if x == 0 else x
    return (red(i), red(j))

def apply_op(Pset, op, mod=44):
    out = set()
    for (i, j) in Pset:
        ni, nj = op(i, j)
        a, b = norm((ni, nj), mod)
        # 無向格 (i<j 正則化): (j,i) ≡ (i,j)
        out.add((min(a, b), max(a, b)))
    return frozenset(out)

ops = {
    "T1_transpose":    lambda i, j: (j, i),
    "T2_mirror44":     lambda i, j: (44 - i, 44 - j),
    "T3_mirror88":     lambda i, j: (88 - i, 88 - j),
    "T4_neg_left":     lambda i, j: (44 - i, j),
    "T4_neg_right":    lambda i, j: (i, 44 - j),
    "T5_diag_shift1":  lambda i, j: (i + 1, j + 1),
    "T6_diag_shift2":  lambda i, j: (i + 2, j + 2),
    "T7_antidiag_s1":  lambda i, j: (i + 1, j - 1),
}
mod = 44
fixed_table = {}
for name, op in ops.items():
    rows = {}
    for d in [7, 3, 14, 12, 20, 22, 29, 33]:
        Pd = P(d)
        oPd = apply_op(Pd, op, mod)
        is_fixed = (oPd == Pd)
        rows[d] = {"fixed": is_fixed, "image_size": len(oPd), "orig_size": len(Pd)}
    # 全域: 全部 43 行幾多固定
    all_fixed = [d for d in range(1, 44) if apply_op(P(d), op, mod) == P(d)]
    fixed_table[name] = {"rows": rows, "all_fixed_d": all_fixed}

# 特別判準: 7 固定但其他 magic 唔固定?
magic_unique = {}
for name, op in ops.items():
    fd = set(fixed_table[name]["all_fixed_d"])
    uniq = [d for d in MAGIC if d in fd and all((d2 not in fd) for d2 in MAGIC if d2 != d)]
    magic_unique[name] = uniq

# T8: gcd_shift — d→d+k 保持 gcd 類 (行層)
gshift = {}
for k in range(1, 44):
    hits = []
    for d in range(1, 44):
        d2 = (d + k - 1) % 43 + 1
        if gcl(d2) == gcl(d):
            hits.append(d)
    if 7 in hits and gcl((7 + k - 1) % 43 + 1) == gcl(7):
        gshift[k] = {"gcd1_preserved": len([d for d in range(1,44) if gcl((d+k-1)%43+1)==gcl(d)])}
# 詳細: 邊啲 k 保住 gcd1 全部
gshift_detail = {}
for k in range(1, 44):
    pres = [d for d in range(1, 44) if gcl((d + k - 1) % 43 + 1) == gcl(d)]
    gshift_detail[k] = {"n": len(pres), "keeps_g1_full": all(gcl((d+k-1)%43+1)==1 for d in range(1,44) if gcl(d)==1)}

# T9: Galois 不動點 — σ_a(ω_d)=ω_d ⟺ a·d ≡ ±d (mod 176)? 但 ω_d 係 2sin(πd/88)...
# ω_n = 2sin(πn/88), n=1..44.  σ_a(ω_n) = 2sin(π·a·n/88)  (a 可逆 mod 176)
# 若 a·n ≡ n (mod 176) 或 a·n ≡ 176−n: σ fixed.  但真正固定要全部共軛...
# Galois fixed: ω_n 嘅 stabilizer size = deg(ω_n) 嘅 complement = φ(176)/2 / deg
# ∪: σ_a fixed ω_n ⟺ a ≡ ±1 (mod 176/gcd(n,176))  — 等我直接數
def galois_fixed(dom):
    """σ_a(ω_d)=ω_d 嘅 a 集合 (mod 176, a invertible)"""
    a_set = []
    for a in range(1, 176):
        if gcd(a, 176) != 1:
            continue
        # σ_a(ω_d) = 2sin(π·a·d/88)
        if (a * d) % 176 in (d % 176, (176 - d) % 176):
            a_set.append(a)
    return a_set
galois = {}
for d in [3, 7, 29]:
    g = galois_fixed(d)
    galois[d] = {"n_fixed_a": len(g), "sample": g[:6], "note": "σ_a(ω_d)=ω_d 嘅 a 數 (好細 = 幾乎冇固定)"}

res = {
    "test": "31_matrix_fixed_point",
    "fixed_table": fixed_table,
    "magic_unique_fixed": magic_unique,
    "gshift": gshift,
    "gshift_detail": gshift_detail,
    "galois": galois,
}

with open("data/31_matrix_fixed_point.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== 2D pattern 不動點測試 (P_d = |i−j|=d 位置集) ===")
for name, op in ops.items():
    t = fixed_table[name]
    m7 = t["rows"][7]["fixed"]
    print(f"{name:18s}: d=7 fixed={m7!s:5s} | magic 內唯一固定={magic_unique[name]!s:20s} | 全 43 行 fixed 數={len(t['all_fixed_d'])}")
print()
print("=== gcd_shift (d→d+k 保持 gcd 類) — 7 有冇特殊? ===")
g1_keepers = [k for k, v in gshift_detail.items() if v["keeps_g1_full"]]
print("保持 gcd1 全體嘅 k:", g1_keepers)
print()
print("=== Galois σ 不動點 (ω 層) ===")
for d, v in galois.items():
    print(f"d={d:2d}: σ_a 固定數 = {v['n_fixed_a']} (樣本 {v['sample']})")
print()
print("輸出: data/31_matrix_fixed_point.json")