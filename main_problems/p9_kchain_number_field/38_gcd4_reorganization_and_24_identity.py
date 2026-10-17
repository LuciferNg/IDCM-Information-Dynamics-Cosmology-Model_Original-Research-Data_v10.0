#!/usr/bin/env python3
"""
38_gcd4_reorganization_and_24_identity.py — 88-site 缺類重組 + 24 身份 (2026-10-17)
=====================================================================================
目標 (用戶: 1+2):
  ① 攻 88-site 缺類重組結構意義 — 44-site 7 類 → 88-site 9 類, 缺類點樣重組?
  ② 24 身份 — 用 O142 v16 已閉合結果 (24 = 2B·N_gen, ρ=3/11) 填空

已知 (O142 v16, RAG 確認閉合):
  24 = 2B·N_gen = 2×4×3 = 全世代替換模式
  ρ = m/88 = 24/88 = 3/11 = N_gen/L₅ (EXACT)
  γ₂₀ = 4sin²(20π/88) = 4cos²(3π/11) = 4cos²(ρπ) — mode 20 = N_d−m 補角 partner
  20↔24 = γ 補角對: γ₂₀+γ₂₄ = 4cos²(ρπ)+4sin²(ρπ) = 4 EXACT (A2 定理 m=2)

測試:
  T1 88-site gcd 類完整表 + 44→88 類重組映射
  T2 缺類重組: 44-site 缺 {4,16} → 88-site 缺邊啲? 20/28 喺 88-site 屬 gcd4 (變成有代表)
  T3 24 身份閉合: 24 ∈ gcd4(44), gcd32(88)? 2B·N_gen 引用 (跨 O note only)
  T4 20↔24 三層連接: γ 補角 + 鏡像 (44−24=20) + gcd 重組 (8→4(88→32))
  T5 對 R5 程序嘅 impact: 88-site 程序輸出 [7,11,14,22,28,44] 缺類 {8,16,32}?

零 import 原推導; 純整數 + mpmath 50dps。
"""
import json
from math import gcd
from collections import defaultdict

def gc44(d):
    return gcd(abs(44 - d), 176)

def gc88(d):
    return gcd(abs(88 - d), 352)

def phi(n):
    r = n; m = n; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r

def om_deg(g, N):
    return phi(4*N // g) // 2  # 44: 176/g; 88: 352/g

# ================= T1: 88-site 類完整表 =================
c88 = defaultdict(list)
for d in range(1, 88):
    c88[gc88(d)].append(d)
c44 = defaultdict(list)
for d in range(1, 44):
    c44[gc44(d)].append(d)

# ================= T2: 缺類重組 =================
# R5 生成 (anchor 5,7,11 × m 1..4) 喺 88-site
anchors = (7, 11, 5)
gen88 = sorted({m*a for a in anchors for m in (1,2,3,4) if 1 <= m*a <= 87})
print("=== T1/T2: 88-site gcd 類 vs 44-site ===")
print(f"{'gcd':>4} | {'44-site 類(43)':<32} {'88-site 類(87)':<70}")
print(f"{'44→88':>8}")
allg = sorted(set(list(c44) + list(c88)))
for g in allg:
    l44 = c44.get(g, [])
    l88 = c88.get(g, [])
    print(f"gcd={g:>3} | 44: {str(l44):<30} | 88: {str(l88):<66}")

# 88-site R5 生成集
print()
print(f"R5 生成集 88-site = {gen88}")
# magic 喺 88-site 嘅 gcd
print()
print("magic 移居 88-site:")
for d in [7, 14, 20, 22, 33, 24, 28]:
    print(f"  d={d:2d}: gcd44={gc44(d):2d}  gcd88={gc88(d):2d}")

# 缺類重組: 44-site 缺 {4,16} → 88-site R5 生成覆蓋?
cover88 = set()
for g, lst in defaultdict(list).items():
    pass
for d in gen88:
    cover88.add(gc88(d))
print()
print(f"88-site R5 生成覆蓋 gcd 類 = {sorted(cover88)}")
print(f"88-site 全部 gcd 類  = {sorted(c88)}")
print(f"88-site R5 未覆蓋 (缺) = {sorted(set(c88) - cover88)}  ← 缺類重組!")

# ================= T3: 24 身份 =================
print()
print("=== T3: 24 身份 (O142 v16 已閉合引用) ===")
print("  24 = 2B·N_gen = 2×4×3 (全世代替換模式)  [O142 v16 EXACT]")
print("  ρ = m/88 = 24/88 = 3/11 = N_gen/L₅  [O142 v16 EXACT]")
print("  γ₂₀ = 4cos²(ρπ) — mode 20 = N_d−m = 44−24 補角 partner")
print(f"  gcd44(24) = {gc44(24)}   gcd88(24) = {gc88(24)}")
print(f"  deg44(ω_24) = {om_deg(gc44(24), 44)}   deg88(ω_24) = {om_deg(gc88(24), 88)}")

# ================= T4: 20↔24 三層連接 =================
import mpmath as mp
mp.mp.dps = 50
g20 = 4*mp.sin(mp.mpf(20)*mp.pi/88)**2
g24 = 4*mp.sin(mp.mpf(24)*mp.pi/88)**2
print()
print("=== T4: 20↔24 三層連接 ===")
print(f"  γ₂₀+γ₂₄ = {mp.nstr(g20+g24, 20)}  (EXACT=4, A2 定理 m=2)") 
print(f"  γ₂₀ = 4cos²(3π/11) ? {mp.almosteq(g20, 4*mp.cos(mp.mpf(3)*mp.pi/11)**2, rel_eps=mp.mpf('1e-30'))}")
print(f"  γ₂₄ = 4sin²(3π/11) ? {mp.almosteq(g24, 4*mp.sin(mp.mpf(3)*mp.pi/11)**2, rel_eps=mp.mpf('1e-30'))}")
print("  層1 (γ 補角): γ₂₀+γ₂₄ = 4 (22±2 對稱, A2)")
print(f"  層2 (鏡像):  44−24 = {44-24} = 20 (30 號鏡像對)")
print(f"  層3 (gcd 重組): 20 gcd44={gc44(20)}→gcd88={gc88(20)};  24 gcd44={gc44(24)}→gcd88={gc88(24)}")

# ================= T5: R5 程序 88-site 缺類 =================
p88 = [7, 11, 14, 22, 28, 44]
pg88 = sorted(set(gc88(d) for d in p88))
print()
print("=== T5: 88-site R5 程序輸出缺類 ===")
print(f"  程序輸出 {p88} → 覆蓋 gcd {pg88}")
print(f"  缺 = {sorted(set(c88) - set(pg88))}")

res = {
    "test": "38_gcd4_reorganization_and_24_identity",
    "c88": {str(g): v for g, v in sorted(c88.items())},
    "c44": {str(g): v for g, v in sorted(c44.items())},
    "gen88": gen88, "cover88": sorted(cover88),
    "missing_88": sorted(set(c88) - cover88),
    "magic_gcd_migration": {str(d): {"gcd44": gc44(d), "gcd88": gc88(d)} for d in [7,14,20,22,24,28,33]},
    "g20_plus_g24": mp.nstr(g20 + g24, 30),
    "proc88": p88, "proc88_gcd": pg88,
}
with open("data/38_gcd4_reorganization_24.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/38_gcd4_reorganization_24.json")