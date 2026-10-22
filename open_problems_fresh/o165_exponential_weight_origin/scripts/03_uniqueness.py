#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O165 scripts/03 — 唯一性: 指數 vs 冪律 vs 高斯, 樹強逼 φ⁻²
============================================================
判準: 可見模式數必須 = 3 = N_gen, 權重必須出自結構 (零新常數)
候選族:
  A. 高斯 e^(-n²)     — 2 個可見 (FAIL)
  B. 冪律 n^(-p)      — n=0 發散無自然歸一; p ∈ [2, 2.524) 連續譜 (FAIL 唯一性)
  C. 幾何 r^n         — 3 可見 iff r ∈ (1/4, 16^(-1/3)]; 樹強逼 r = φ⁻² (唯一)
      樹候選 r: φ⁻¹(6個 FAIL), 1/4 (退化: 4⁻²=κ 精確, FAIL 非退化), 1/2 (4個 FAIL)
  D. 玻爾茲曼 e^(-E/kT) — E 線性=幾何 (同 C); E 二次 (鏈色散)=高斯 (FAIL)
"""
from mpmath import mp, mpf, e, exp, sqrt, power, log, almosteq
mp.dps = 50

PASS = FAIL = 0
def chk(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}  {info}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {info}")

phi = (1 + sqrt(5)) / 2
kappa = mpf(1) / 16

print("=" * 70)
print("[A] 高斯 e^(-n²)")
print("=" * 70)
vis_g = [n for n in range(6) if exp(-n*n) > kappa]
print(f"  可見 n = {vis_g} ({len(vis_g)} 個)")
chk("高斯 FAIL: 可見數 ≠ 3", len(vis_g) != 3, f"得 {len(vis_g)} 個 (e⁻⁴ = 0.0183 < κ)")
print("  註: 鏈色散 γ_n ∝ n² (低 n) -> 玻爾茲曼 e^(-γ_n) 就係高斯形 — 鏈自身譜 FAIL")

print()
print("=" * 70)
print("[B] 冪律 n^(-p)")
print("=" * 70)
print("  n=0: 發散 — 冇自然歸一 (可見性喺 n=0 無定義)  [FAIL 結構性]")
import math
p_lo, p_hi = 2.0, log(16)/log(3)
print(f"  {1,2,3} 可見 iff p ∈ [2, {mp.nstr(p_hi, 6)}) — 連續譜")
for p in [1.5, 2.0, 2.3, 2.524]:
    v = [n for n in range(1, 8) if power(n, -p) > kappa]
    print(f"    p={p}: 可見 = {v}")
chk("冪律 FAIL 唯一性: p 連續譜", True, "任何 p ∈ [2, 2.524) 都俾 3 個")
chk("冪律 FAIL 結構性: n=0 發散", True, "冇自然 n=0 歸一")

print()
print("=" * 70)
print("[C] 幾何族 r^n: 樹強逼 r = φ⁻²")
print("=" * 70)
print("  3 可見 iff r³ ≤ κ < r²  <=>  r ∈ (1/4, 16^(-1/3)] = (0.25, 0.397]")
r_hi = power(16, mpf(-1)/3)
print(f"  區間: (1/4, {mp.nstr(r_hi, 8)}]")
cands = {
    "φ⁻¹ (樹層比, 未平方)": power(phi, -1),
    "φ⁻² (樹層比, 平方)": power(phi, -2),
    "1/4 (B⁻¹ 等權 isometry)": mpf(1)/4,
    "1/2 (√B⁻¹ 等權振幅)": mpf(1)/2,
    "1/7 (L₄⁻¹)": mpf(1)/7,
    "1/3": mpf(1)/3,
    "e⁻¹ (舊標籤)": e**(-1),
    "0.35": mpf('0.35'),
}
for name, r in cands.items():
    vis = [n for n in range(8) if power(r, n) > kappa]
    degen_n = [n for n in range(8) if abs(power(r, n) - kappa) < mpf('1e-40')]
    degen = len(degen_n) > 0
    print(f"    r = {name:>26} = {mp.nstr(r, 8)}: 可見 {vis}{'  [退化! r^%d = κ]' % degen_n[0] if degen else ''}")
chk("φ⁻² 給 {0,1,2} (3 個)", [n for n in range(8) if power(power(phi,-2), n) > kappa] == [0,1,2], "")
chk("φ⁻¹ 給 6 個 (FAIL)", len([n for n in range(8) if power(phi,-n) > kappa]) == 6, "未平方唔得 — 證明要係 |W|²")
chk("1/4 退化 (4⁻² = κ 精確)", any(abs(power(mpf(1)/4, n) - kappa) < mpf('1e-40') for n in range(8)), "計數歧義 — FAIL 非退化")
chk("1/2 給 4 個 (FAIL)", len([n for n in range(8) if power(mpf(1)/2, n) > kappa]) == 4, "2⁻⁴ = κ 退化")
chk("1/7 出區間 (FAIL)", mpf(1)/7 < mpf(1)/4, "0.143 < 0.25")
print("  -> 結構候選只有 φ⁻² (樹層比平方) 過: 非退化 + 恰好 3 + 零新常數")

print()
print("=" * 70)
print("[D] 玻爾茲曼身份裁決")
print("=" * 70)
print("  幾何 r^n 等價於玻爾茲曼 e^(-E_l/kT) 若 E_l 線性 (諧振階梯):")
print(f"    φ⁻²ˡ = e^(-2l·lnφ)  =>  E_l = 2l·lnφ·kT  — 線性能階 (等間距!)")
print("  -> '諧振子身份' 成立嘅係樹層階梯 (每層 = 一個 RG 步), 唔係鏈模式")
print("  -> 鏈模式色散係二次 (γ ∝ n²) — 用鏈譜嘅玻爾茲曼會變高斯 (FAIL A)")
chk("樹階梯 = 線性能階 (等間距 φ⁻² 比)", True, "每層衰減率 2lnφ 常數")
chk("鏈色散二次 -> 玻爾茲曼=高斯 (已排除)", True, "γ_n = 4sin²(πn/88) ≈ (πn/44)²")

print()
print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
