#!/usr/bin/env python3
"""
25_magic_rows_open.py — P9 續推: magic rows 未解項攻堅 (2026-10-17)
============================================================
賽局: 16_magic_rows_rule.md / 17_layer_magic_data.md 三個 🔴 未解項
  Q1: 點解 7 (gcd=1, deg40 高次數) 係 magic? 其他 gcd=1 端點 22 個點解唔揀?
  Q2: 點解缺 {4,16} 冇 magic (gcd 類別 7 個, magic 只覆蓋 5 個)?
  Q3: 低次數端點 24 個嘅 IDCM 身份 (24 = ?)

零 import 原推導; 第一原理: ω_n=2sin(πn/88), γ_n=4sin²(πn/88),
gcd(|44−n|,176) 分層, deg=φ(176/gcd)/2 (e≤2 → deg1 特判)
純整數/Fraction 運算; mpmath 只用於無理數屬類驗證 (唔做擬合)
"""
import json
from math import gcd
from fractions import Fraction

OUT = "data/25_magic_open.json"

# ---------- 0. 基本層 ----------
def deg_omega_n(n: int) -> int:
    """deg(ω_n) = φ(176/g) / 2, g=gcd(|44−n|,176); e≤2 → 1 (有理)"""
    g = gcd(abs(44 - n), 176)
    e = 176 // g
    # φ(e) 直接計
    phi = e
    p = 2
    while p * p <= e:
        if e % p == 0:
            while e % p == 0:
                e //= p
            phi -= phi // p
        p += 1
    if e > 1:
        phi -= phi // e
    if phi <= 2:  # e∈{1,2} → deg=1
        return 1
    return phi // 2

N = 44
deg_n = {n: deg_omega_n(n) for n in range(1, N + 1)}
g_n = {n: gcd(abs(44 - n), 176) for n in range(1, N + 1)}

MAGIC = [7, 14, 20, 22, 33]
DATA_ROWS = [11, 13, 17, 19, 21, 25]

result = {
    "Q0_deg_distribution": {str(d): sum(1 for n in range(1, 45) if deg_n[n] == d) for d in sorted(set(deg_n.values()))},
    "Q0_lowdeg_endpoints": {"count": sum(1 for n in range(1, 45) if deg_n[n] < 40),
                            "n_list": [n for n in range(1, 45) if deg_n[n] < 40]},
}

# ---------- 1. Q2: magic 覆蓋 gcd 類別 ----------
# gcd(|44−d|,176) 全部可能值 (d=1..43)
gcd_classes = sorted({gcd(abs(44 - d), 176) for d in range(1, 44)})
magic_gcd = {d: gcd(abs(44 - d), 176) for d in MAGIC}
covered = set(magic_gcd.values())
missing = [c for c in gcd_classes if c not in covered]
d_by_gcd = {c: [d for d in range(1, 44) if gcd(abs(44 - d), 176) == c] for c in gcd_classes}

result["Q2_gcd_classes"] = {"all": gcd_classes,
                            "magic_covered": sorted(covered),
                            "missing": missing,
                            "d_candidates_by_gcd": {str(c): d_by_gcd[c] for c in gcd_classes}}
result["Q2_magic_d_deg"] = {str(d): {"gcd": magic_gcd[d], "deg": deg_n[d]} for d in MAGIC}

# 缺 {4,16}: gcd=4 同 gcd=16 嘅 d 候選有咩共同點?
# d 值調 d=8,16,24,32,40 (gcd4) / d=4,12,20,28,36 (gcd16)? 檢查
for c in missing:
    dd = d_by_gcd[c]
    # 候選 d 有冇 Fibonacci/Lucas/2 次冪?
    fibs = {1,2,3,5,8,13,21,34}
    lucas = {2,1,3,4,7,11,18,29}
    result[f"Q2_missing_{c}"] = {"d_candidates": dd,
                                 "in_fib": [x for x in dd if x in fibs],
                                 "in_lucas": [x for x in dd if x in lucas],
                                 "even_parity": sum(1 for x in dd if x % 2 == 0)}

# ---------- 2. Q1: 7 嘅特殊身份 (gcd=1 唯一 magic) ----------
g1 = d_by_gcd[1]  # 22 個 gcd=1 d 值
fibs = {1,2,3,5,8,13,21,34}
lucas = {2,1,3,4,7,11,18,29}
# 22 個 gcd=1 d: 全部奇數非 11 倍? 檢查
r1 = {"d_list": g1, "count": len(g1),
      "odd": [x for x in g1 if x % 2 == 1],
      "in_lucas": [x for x in g1 if x in lucas],
      "in_fib": [x for x in g1 if x in fibs],
      "primitive_11": [x for x in g1 if x % 11 != 0],
      }
# 7 有咩獨有特徵?
r1["seven"] = {"lucas_index": "L4=7", "gamma": "γ7=4sin²(7π/88)"}
# 檢查: 係咪唯一 gcd=1 且 ≡3 mod 4? d∈{3,7,...}?
r1["three_mod4"] = [x for x in g1 if x % 4 == 3]
result["Q1_gcd1_rows"] = r1

# ---------- 3. Q3: 低次數端點 24 身份 ----------
low = [n for n in range(1, 45) if deg_n[n] < 40]
# 24 = ? 候選身份
cand = {
    "2^3*3": 24 == 2**3 * 3,
    "4!": 24 == 24,
    "88/44 對半": len(low) == 24,
    "偶數端點 22 + 奇數 2 (11,33)": (sum(1 for n in low if n % 2 == 0) == 22 and
                                      sorted([n for n in low if n % 2 == 1]) == [11, 33]),
    "φ(88)=": 0,  # φ(88)=40
    "C(8,2)+C(3,2)": 28 + 3,  # 31? no
}
result["Q3_lowdeg_24"] = {
    "endpoints": low,
    "even": [n for n in low if n % 2 == 0],
    "odd": [n for n in low if n % 2 == 1],
    "identity_candidates": {k: (v) for k, v in cand.items()},
}

# ---------- 4. Q1 深化: gcd=1 22 個端點嘅 magic 代表揀選規則 ----------
# 假說: 7 = 唯一同時滿足: 奇數 ∧ L_k ∧ 唔係 data row ∧ 唔係 filler 特殊?
# data rows {11,13,17,19,21,25} ∩ g1 = {13,17,19,21,25}? 11 ∉ g1 (11 有 gcd=11)
g1_set = set(g1)
data_in_g1 = [d for d in DATA_ROWS if d in g1_set]
r4 = {"data_rows_in_g1": data_in_g1,
      "g1_minus_data": sorted(g1_set - set(data_in_g1)),
      }
# g1 剩低: {1,3,5,7,9,23,27,29,31,35,37,39,41,43,...} 全部冇 data 角色
# → 揀 7 = L₄; 有冇其他 L 喺度? {1,3,4,7,11,18,29} ∩ g1 = {1,3,7,29}
r4["lucas_in_g1"] = [x for x in sorted(g1) if x in lucas]
result["Q1_selection_rule"] = r4

# ---------- 5. 額外: magic d 值本身嘅結構 ----------
# magic: 7,14,20,22,33 → gcd: 1,2,8,11,22
# 176 = 16×11; gcd 值 = {1,2,8,11,22} = 除 4,16 之外嘅「2^k 或 11×2^k」?
# 全部 176 因數: 1,2,4,8,11,16,22,44,88,176
f176 = [x for x in [1,2,4,8,11,16,22,44,88,176] if x <= 44]
r5 = {"factor_176_le44": f176,
      "covered_vs_factors": sorted(covered),
      "missing_vs_factors": missing,
      # 4=2², 16=2⁴ → 缺「2^even」但 2^0=1 有? → 唔係: 奇異點係 4/16 係 2^k, k 偶數 2,4 (k=0 亦有 magic gcd=1)
      "note": "缺 {4,16} = 2^2,2^4; 覆蓋 {1,2,8} = 2^0,2^1,2^3 → 缺 2^k with k∈{2,4}",
      }
# 檢查: 176/4=44, 176/16=11 → 缺 4,16 = 176/44,176/11?
result["Q2_extra"] = r5

# ---------- 6. v₂ 階分析 (缺 {4,16} 假說) ----------
r6 = {}
for c in sorted(covered):
    v2 = 0; cc = c
    while cc % 2 == 0:
        v2 += 1; cc //= 2
    r6[f"gcd_{c}"] = {"v2": v2, "odd_part": cc}
for c in missing:
    v2 = 0; cc = c
    while cc % 2 == 0:
        v2 += 1; cc //= 2
    r6[f"gcd_{c}_MISSING"] = {"v2": v2, "odd_part": cc}
result["Q2_v2_analysis"] = r6
# 關鍵: 全部可能 gcd 值 v₂ 分佈 = {0,1,2,3,4} (2^0..2^4 各配 11^0)
# covered v₂ = {0,1,3} (1,2,8) + {0,1} with 11-part (11,22)
# missing v₂ = {2,4} → 缺 v₂ 偶數階 2,4 且 11-part=1

# ---------- 7. Magic rows 嘅幾何身份: d ∈ {7,14,20,22,33} 有咩實現 ----------
# 7 = 44-37? 14=44-30? 20=44-24? 22=44/2? 33=44-11?
r7 = {
    "d_as_44_minus": {str(d): 44 - d for d in MAGIC},
    "d_as_88_minus": {str(d): 88 - d for d in MAGIC},
    "d_ratio_44": {str(d): Fraction(d, 44) for d in MAGIC},
    "d_ratio_88": {str(d): Fraction(d, 88) for d in MAGIC},
}
result["Q_geometry"] = r7

with open(OUT, "w") as f:
    json.dump(result, f, indent=1, default=str)

print("=== Q0 基礎 ===")
print("deg 分佈:", result["Q0_deg_distribution"])
print("低次數端點 24:", result["Q0_lowdeg_endpoints"]["n_list"])
print()
print("=== Q2 gcd 類別 ===")
print("全部 gcd 值:", result["Q2_gcd_classes"]["all"])
print("magic 覆蓋:", result["Q2_gcd_classes"]["magic_covered"])
print("缺:", result["Q2_gcd_classes"]["missing"])
print("magic d 嘅 (gcd,deg):", {d: (result['Q2_magic_d_deg'][str(d)]['gcd'],
                                     result['Q2_magic_d_deg'][str(d)]['deg']) for d in MAGIC})
for c in result["Q2_gcd_classes"]["missing"]:
    print(f"  缺 gcd={c}: d 候選 {result[f'Q2_missing_{c}']['d_candidates']}, "
          f"Fib {result[f'Q2_missing_{c}']['in_fib']}, Lucas {result[f'Q2_missing_{c}']['in_lucas']}")
print()
print("=== Q1 gcd=1 22 個 ===")
print("全部:", r1["d_list"])
print("奇數:", r1["odd"])
print("Lucas 成員:", r1["in_lucas"])
print("Fib 成員:", r1["in_fib"])
print("≡3 mod4:", r1["three_mod4"])
print("gcd=1 內 data rows:", r4["data_rows_in_g1"], "→ 揀剩:", r4["g1_minus_data"])
print("gcd=1 內 Lucas:", r4["lucas_in_g1"])
print()
print("=== Q3 低次數端點 24 ===")
print("偶數 22 個 / 奇數:", result["Q3_lowdeg_24"]["odd"])
print()
print("=== Q2 v₂ 階 ===")
for k, v in result["Q2_v2_analysis"].items():
    tag = " 🔴MISSING" if "MISSING" in k else ""
    print(f"  {k}: v2={v['v2']}, odd_part={v['odd_part']}{tag}")
print()
print("=== Q 幾何 ===")
print("d=44−d:", r7["d_as_44_minus"])
print("d/44:", {k: str(v) for k, v in r7["d_ratio_44"].items()})
print()
print("輸出:", OUT)