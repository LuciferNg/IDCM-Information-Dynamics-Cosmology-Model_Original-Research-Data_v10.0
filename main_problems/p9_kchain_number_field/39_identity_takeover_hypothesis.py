#!/usr/bin/env python3
"""
39_identity_takeover_hypothesis.py — 身份接管統一假說 (2026-10-17)
==================================================================
38 號提出: 「缺類身份 = 另一算子層 (2B·N_gen 家族), 唔係冇身份」

今輪擴展成統一假說:
  H: magic 代表 = 啱好有 L/F 鏈身份 AND 冇被「更基礎身份」接管嘅數
     被接管(唔做魔法代表): 3=N_gen(B−1), 5=F₅(anchor), 11=data+anchor,
                           data 全體, 缺類端點 (24=2B·N_gen, 8=2B, 16=B²...)
     做代表 (magic): 7=L₄, 14=2L₄, 20=4F₅, 22=2L₅, 33=3L₅

測試:
  T1 44-site 全部非 magic R5 候選嘅身份接管表 (點解唔係 magic)
  T2 88-site 缺類 {8,16,32} 端點 = B-冪家族? (8=2B, 16=B², 24=2B·N_gen, 32=2B²)
  T3 7 vs 3 終極判準: 3=N_gen (結構參數本身) vs 7=L₄ (純鏈身份)
  T4 統一規則檢驗: 「magic = R5 生成 ∩ L/F鏈 ∩ ¬被接管」做唔做到 5/5?
  T5 88-site 用統一規則預測 (補盲測)

零 import; 純整數。
"""
import json
from math import gcd
from collections import defaultdict

def gc44(d): return gcd(abs(44 - d), 176)
def gc88(d): return gcd(abs(88 - d), 352)

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

# 身份字典 — 由已閉合 IDCM 結構 (RAG 查證)
IDENTITIES = {
    # 結構參數本身
    3: "N_gen = B−1 (世代數, O216) — 結構參數, 唔做操作代表",
    # 4 = B (色荷數)
    # anchor
    5: "F₅ = anchor (33/34/35 號) — 做生成器唔做代表",
    7: "L₄ — magic 代表 (唯一 Lucas 質數 index)",
    11: "L₅ = anchor + DATA row (m_W/m_Z) — data 樽",
    # data 全體
    13: "DATA row (n/p) — 數據面",
    17: "DATA row (m_μ/m_τ)",
    19: "DATA row (m_H/m_W)",
    21: "DATA row (m_s/m_d) — 36 號: 自動被 data-free 排除",
    25: "DATA row (m_c/m_b)",
    # 缺類端點
    8: "2B = 2×4 — B 家族",
    16: "B² = 4² — B 家族",
    24: "2B·N_gen = 2×4×3 (O142 v16) — B·N_gen 家族 ← 38 號閉合",
    28: "4L₄ = m=4 Lucas (TEST F 窗口外)",
    32: "2B² = 2×16 — B 家族",
    40: "8F₅ = 2³×5 (F 鏈) + 40=88−48?",
    12: "3L₂? 12=2L₆? m=2×L₆=36 唔係; 12 = 3×4 = 3L₃",
    36: "2L₆ = 2×18 — Lucas 鏈",
    20: "4F₅ — magic (Fib 鏈代表!)",
    14: "2L₄ — magic",
    22: "2L₅ — magic (HALF)",
    33: "3L₅ — magic (KTREE)",
}
ITS = {k: v.split(" — ")[0] for k, v in IDENTITIES.items()}

def is_lucas_chain(d):
    return any(d == m*luc(k) for m in (1,2,3,4) for k in range(2,8))
def is_fib_chain(d):
    return any(d == m*fib(k) for m in (1,2,3,4) for k in range(2,9))

MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}

print("=== T1: 44-site 非 magic R5 候選嘅身份接管 ===")
cand44 = sorted({m*a for a in (7,11,5) for m in (1,2,3,4) if 1 <= m*a <= 43})
for d in cand44:
    if d in MAGIC: continue
    print(f"  d={d:2d}: {IDENTITIES.get(d, '??')}")

print()
print("=== T2: 88-site 缺類端點身份 ===")
missing88 = [8, 16, 32]
end88 = {8: [16,32,48,64,80], 16: [8,40,72], 32: [24,56]}
for g in missing88:
    for d in end88[g]:
        extra = ""
        if d == 24: extra = " ← 38 號: 2B·N_gen (O142 v16) 閉合!"
        if d == 16: extra = " ← B² = 4²"
        if d == 8:  extra = " ← 2B = 2×4"
        if d == 32: extra = " ← 2B²"
        if d == 40: extra = " ← 8F₅"
        if d == 48: extra = " ← ?"
        if d == 56: extra = " ← ?"
        print(f"  gcd{g:2d} 端點 d={d:2d}: B/L/F 家族?{extra}")

print()
print("=== T3: 7 vs 3 終極判準 ===")
print("  3 = N_gen = B−1 (O216 已閉合: 色數 3=B−1=N_gen)")
print("  7 = L₄ (純 Lucas 鏈身份, 唯一索引)")
print("  判準: 3 係結構參數本身 (生成系數), 唔做操作代表; 7 係鏈成員")
print("  對應: 4 = B 都唔做代表 (R5 生成唔到 gcd4 — 37 號 T1 mod8 必然)")

print()
print("=== T4: 統一規則 = R5 生成 ∩ L/F 鏈 ∩ ¬被接管 ===")
def rule(d):
    if d not in cand44: return False
    if d in DATA: return False
    if d in IDENTITIES and IDENTITIES[d].startswith(("N_gen", "B 家族", "B·N_gen", "DATA", "anchor", "4L₄", "2L₆")): 
        # 被接管: 結構參數/B家族/data/anchor 本身
        return False
    return is_lucas_chain(d) or is_fib_chain(d)
pred = sorted(d for d in range(1, 44) if rule(d))
print(f"  統一規則預測 magic = {pred}")
print(f"  = magic? {set(pred) == set(MAGIC)}")

print()
print("=== T5: 88-site 統一規則 (冇 data label) ===")
cand88 = sorted({m*a for a in (7,11,5) for m in (1,2,3,4) if 1 <= m*a <= 87})
def rule88(d):
    if d not in cand88: return False
    if d in (3, 5, 11):  # anchor 本身/結構參數 — 同樣唔做代表
        return False
    return is_lucas_chain(d) or is_fib_chain(d)
pred88 = sorted(d for d in range(1, 88) if rule88(d))
print(f"  88-site 統一規則預測 = {pred88}")
print(f"  44-site 程序輸出 (37/38) = [7,11,14,22,28,44]")
print(f"  交集 = {sorted(set(pred88) & {7,14,20,22,33,28,44})}")

res = {
    "test": "39_identity_takeover_hypothesis",
    "T1_nonmagic_identity": {str(d): IDENTITIES.get(d) for d in cand44 if d not in MAGIC},
    "T2_missing88": end88,
    "T4_pred44": pred, "T4_match": set(pred) == set(MAGIC),
    "T5_pred88": pred88,
}
with open("data/39_identity_takeover.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/39_identity_takeover.json")