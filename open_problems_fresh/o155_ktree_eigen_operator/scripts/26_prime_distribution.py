#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/26_prime_distribution.py — 點解質數極少見?
結構性回答: 閉合操作 (Z₂ 對和, FSR 加倍, 乘積, AP 和) 全部趨向合成數;
質數只生存喺不可約生成器層 + 加法閉合嘅特殊和 (137).
"""
import mpmath as mp
mp.mp.dps = 60

# O152 全庫整數常數 (numbers.yaml 實測抽取, 剔除 O-number 引用 74/75/148/149/151/152)
# 17 = F_proj 喺 operator_dict (O138), numbers.yaml 冇 — 補入
INV = [1,2,3,4,5,6,7,8,10,11,12,13,14,16,17,18,19,20,21,22,23,24,25,27,29,30,31,32,33,34,36,37,40,41,42,43,44,45,46,47,55,59,60,61,64,66,72,76,77,84,87,88,89,90,92,98,123,124,128,132,137,143,176,178,180,184,192,264,276,294,369,528,946]
INV = sorted(set(INV))

def isprime(n):
    if n < 2: return False
    for d in range(2, int(mp.sqrt(n))+1):
        if n % d == 0: return False
    return True

primes = [n for n in INV if isprime(n)]
composites = [n for n in INV if n > 1 and not isprime(n)]

# 命名質數: 結構生成器 (原子) — T̂/鏈算子層
ATOMS = {2:"μ²=γ₄₄ 自對偶", 3:"N_gen 世代", 5:"F₅ AP步/δ因子", 7:"L₄ Lucas",
         11:"L₅ Lucas", 13:"F₇ Fibonacci", 17:"F_proj=L₆−1 (O138)",
         19:"ε=19/123 分子 (O148)", 29:"L₇ Lucas", 41:"f_unproj (O148)",
         43:"邊界 mode k=43 (μ²括對)", 47:"L₈ Lucas", 89:"F₁₁ Fibonacci",
         137:"α⁻¹(0)=3N_d+F₅ (O142)"}
BIG = [n for n in INV if n > 99]

print("="*62)
print("1. 全庫質數分佈: %d 條整數常數中 %d 質數 (%.1f%%)" % (len(INV), len(primes), 100*len(primes)/len(INV)))
print("   對照: 1-1000 隨機整數質數密度 ≈ 16.8%")
print("   質數: %s" % primes)
print()
print("2. 細層 (≤50): 質數密集 — 所有細質數都係命名常數")
small_p = [p for p in range(2,51) if isprime(p)]
missing = [p for p in small_p if p not in INV]
print("   ≤50 質數 15 個, 庫中 %d 個, 缺 %d 個: %s (17=F_proj 喺 operator_dict)" % (len(small_p)-len(missing), len(missing), missing))
print()
print("3. 大層 (>99): 合成數壟斷 — %d 條中質數只 %d 條" % (len(BIG), sum(1 for n in BIG if isprime(n))))
for n in BIG:
    tag = "★ 質數!" if isprime(n) else ""
    print("   %4d  %s" % (n, tag))
print()
print("4. 四種合成數製造機 (全部有名字嘅閉合操作):")
print("   (a) Z₂ 對和: k 與 88−k 對和 = 4 = B → 偶數偏置 (88,90,92,176,178,180,360 全偶)")
print("   (b) FSR 加倍: ×2ⁿ → 偶數 (42→84, 44→88, 132→264, 264→528)")
print("   (c) 乘積閉合: 143=L₅×F₇, 176=L₅×B², 264=2N_gen×N_d, 369=3×123, 294=3×98")
print("   (d) AP 部分和: 33=6+11+16, 55=F₅×L₅")
print()
print("5. ★ 大層唯一質數 = 137 = α⁻¹ = 3N_d+F₅ — 加法閉合嘅和, 唔係乘積!")
print("   → 乘積操作保持因子 (合成); 加法先可以「碰彩」出質數")
print()
print("6. Fib/Lucas 質數模式 (質數只喺特定階):")
F = [0,1,1,2,3,5,8,13,21,34,55,89]
L = [2,1,3,4,7,11,18,29,47,76,123]
print("   F_n 質數: " + ", ".join("F%d=%d%s" % (i, F[i], "★" if isprime(F[i]) and i>2 else "") for i in range(2,12)))
print("   L_n 質數: " + ", ".join("L%d=%d%s" % (i, L[i], "★" if isprime(L[i]) else "") for i in range(0,10)))
print("   庫中用咗: F₅=5, F₇=13, F₁₁=89 (質數階 5,7,11); L₄=7, L₅=11, L₇=29, L₈=47")
print()
# 137 唯一性驗證
print("7. 驗證: 大層質數只 137")
big_p = [n for n in BIG if isprime(n)]
assert big_p == [137], big_p
print("   大層質數 = %s  ✔ (唯一)" % big_p)
# 所有 ≤50 質數都喺庫 (17 補入後)
assert all(p in INV for p in small_p), missing
print("   細層: 15/15 質數全數在庫  ✔")
print()
print("8. 結構結論:")
print("   質數 = 不可約生成器 (原子層); 合成數 = 閉合產物 (衍生層)")
print("   庫分兩層: 細層 (生成器, 質數密集) + 大層 (閉合, 合成數壟斷)")
print("   質數出現兩條路: (i) 作為原子生成器; (ii) 加法閉合嘅特殊和 (137)")
print("   → 137 係唯一大質數 = α⁻¹, 物理上最 fundamental 嘅常數 — 質數性 = 不可約性")
print("="*62)
