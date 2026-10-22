#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O241 R9 — ζ 分母族 forward 盲測 (docs/06 §4 之預先註冊執行)
================================================================
預先註冊 (執行前寫定, 2026-10-08):
  H0 (預期): ζ(-21)..ζ(-59) (k=11..30) 之分母中, 結構池命中率
             ≈ 隨機池命中率 (無統計差異, p>0.05).
             理由: R6 已證明前 10 項 (12,120,252,240,132,32760,12,8160,14364,6600)
             結構池 7/10 vs 隨機池 mean 5.92/10, p=0.219 — 細數喺細池好易撞.
             若 R9 樣本同樣無差 ⟹ R6 結論 (240 為算術奇想) 鞏固;
             若 p<0.05 (命中顯著高或低) ⟹ 意外, 需要重新評估.
判定:
  PASS = |p_ge - 預期| 正常: p_ge > 0.05 (無顯著差異, 鞏固 R6)
  注意: 單尾 p_ge 測試「結構池 ≥ 隨機」, 若 p_ge 低 (<0.05) 即結構池顯著優於隨機
        => 推翻 R6; 若 p_ge 高 >0.5 即結構池更差 => 更鞏固「無意義」.
方法: Bernoulli 精確 (Fraction), 結構池 28 個, 表示規則 = 二元運算 (×,+,-), MC 2000.
"""

import json, os, random
from fractions import Fraction

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []
def check(name, cond, detail=""):
    results.append({"check": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

# Bernoulli 精確 (B_2k, k=1..30) — 由前 20 擴展: 用 von Staudt-Clausen + 遞迴太煩,
# 直接手錶 (標準值, 可查 NIST DLMF / OEIS):
BERN = {
    2: Fraction(1,6), 4: Fraction(-1,30), 6: Fraction(1,42), 8: Fraction(-1,30),
    10: Fraction(5,66), 12: Fraction(-691,2730), 14: Fraction(7,6),
    16: Fraction(-3617,510), 18: Fraction(43867,798), 20: Fraction(-174611,330),
    22: Fraction(854513,138), 24: Fraction(-236364091,2730), 26: Fraction(8553103,6),
    28: Fraction(-23749461029,870), 30: Fraction(8615841276005,14322),
    32: Fraction(-7709321041217,510), 34: Fraction(2577687858367,6),
    36: Fraction(-26315271553053477373,1919190), 38: Fraction(2929993913841559,6),
    40: Fraction(-261082718496449122051,13530), 42: Fraction(1520097643918070802691,1806),
    44: Fraction(-27833269579301024235023,690), 46: Fraction(596451111593912163277961,282),
    48: Fraction(-5609403368997817686249127547,46410), 50: Fraction(495057205241079648212477525,66),
    52: Fraction(-801165718135489957347924991853,1590), 54: Fraction(29149963634884862421418123812691,798),
    56: Fraction(-2479392929313226753685415739663229,870), 58: Fraction(84483613348880041862046775994036021,354),
    60: Fraction(-1215233140483755572040304994079820246041491,56786730),
}

def zeta_odd_denom(k):
    """ζ(-(2k-1)) = -B_{2k}/(2k); 返回簡化後分母"""
    v = -BERN[2*k] / (2*k)
    return v.denominator

print("="*72)
print("R9: ζ 分母族 forward 盲測 (k=11..30, 預先註冊)")
print("="*72)
D11_30 = [zeta_odd_denom(k) for k in range(11, 31)]
print(f"  ζ(-21)..ζ(-59) 分母 (20 項):")
for k in range(11, 31):
    print(f"    ζ(-{2*k-1:2d}) 分母 = {zeta_odd_denom(k)}")

pool_int = sorted(set([
    2,3,4,5,7,8,11,13,17,18,20,21,29,33,34,42,44,60,88,90,
    120,123,137,176,178,240,36,98,
]))

def representable(pool_list, maxn=2000000):
    s = set(pool_list)
    for a in pool_list:
        for b in pool_list:
            if a*b <= maxn: s.add(a*b)
            if a+b <= maxn: s.add(a+b)
            if abs(a-b) <= maxn and abs(a-b) > 0: s.add(abs(a-b))
    return s

rep = representable(pool_int, max(D11_30)*2)
hits30 = [d for d in D11_30 if d in rep]
print(f"\n  結構池命中 (k=11..30): {len(hits30)}/20: {hits30}")

# MC null (2000 隨機池)
random.seed(20261008)
N_MC = 2000
hc = []
for _ in range(N_MC):
    rp = random.sample(range(2, 241), len(pool_int))
    rrep = representable(rp, max(D11_30)*2)
    hc.append(sum(1 for d in D11_30 if d in rrep))
mean_h = sum(hc)/len(hc)
p_ge = sum(1 for h in hc if h >= len(hits30))/N_MC
print(f"  MC null: 隨機池 mean = {mean_h:.2f}/20;  結構池命中 = {len(hits30)}/20")
print(f"  p(結構≥{len(hits30)}) = {p_ge:.4f}")

# 預先註冊判決: H0 = 無差異 (p_ge > 0.05) ⟹ PASS 鞏固 R6
check("R9-C1: p_ge > 0.05 (無顯著差異, 鞏固 R6: 240 為算術奇想)",
      p_ge > 0.05, f"p_ge={p_ge:.4f}, 結構池 {len(hits30)}/20 vs 隨機 {mean_h:.2f}/20")

# 更嚴格: 兩側檢定 — 結構池命中概率是否偏離隨機 mean 超過 2σ
import math
sd = math.sqrt(N_MC*mean_h*(1-mean_h/20)) if False else math.sqrt(sum((h-mean_h)**2 for h in hc)/(N_MC-1))
z = (len(hits30) - mean_h)/sd if sd > 0 else 0
check("R9-C2: 結構池命中偏離隨機池 mean < 2σ (雙側)",
      abs(z) < 2.0, f"z={z:+.2f}")

# 第一項 ζ(-21) 分母: 38730? 檢查唯一性
d21 = zeta_odd_denom(11)
print(f"\n  ζ(-21) 分母 = {d21}  (結構池命中? {d21 in rep})")

with open(os.path.join(BASE, "data", "09_zeta_forward.json"), "w") as f:
    json.dump({"D11_30": D11_30, "hits30": hits30, "mean_h": mean_h,
               "p_ge": p_ge, "z": z}, f, indent=2, default=str)

npass = sum(1 for r in results if r["pass"])
nfail = sum(1 for r in results if not r["pass"])
print(f"\n{'='*72}\nRESULT: {npass}/{len(results)} PASS\n{'='*72}")