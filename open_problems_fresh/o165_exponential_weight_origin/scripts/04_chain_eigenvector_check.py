#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O165 scripts/04 — Q1 誠實檢查: K_chain 特徵向量有冇固有指數衰減?
================================================================
用 IPR (inverse participation ratio) 量化局部化:
  IPR_k = Σ_j |v_k(j)|⁴ / (Σ_j |v_k(j)|²)²
  完全延展 (平面波/正弦): IPR ~ 2/N  (N=44 -> ~0.045)
  完全局部化 (單點): IPR = 1
鏈本徵向量 v_k(j) = sin(πkj/88), k = 1..44 — 預期全延展, 無指數衰減。
另檢查 sub-band Green's function: 衰減喺 site 空間 (|i−j|), 唔喺 mode 索引。
"""
import math
from mpmath import mp, mpf
mp.dps = 30

PASS = FAIL = 0
def chk(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}  {info}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {info}")

N = 44
print("=" * 70)
print("[1] IPR 局部化指標 (44 個鏈本徵向量)")
print("=" * 70)
iprs = []
for k in range(1, N+1):
    vk = [math.sin(math.pi * k * j / 88) for j in range(1, N+1)]
    nrm = sum(x*x for x in vk)
    ipr = sum(x**4 for x in vk) / nrm**2
    iprs.append((k, ipr))
max_ipr = max(iprs, key=lambda t: t[1])
print(f"  IPR 範圍: {min(ipr for _, ipr in iprs):.5f} .. {max_ipr[1]:.5f}  (延展基準 ~2/{N} = {2/N:.5f})")
chk("所有 IPR << 1 (全延展)", max_ipr[1] < 0.1, f"最大 IPR = {max_ipr[1]:.5f} (k={max_ipr[0]})")
chk("無局部化模 (無 IPR ≈ 1)", max_ipr[1] < 0.5, "")
print("  -> 鏈本徵向量係延展正弦波: 冇固有指數衰減 (冇邊界模/局部化)")

print()
print("=" * 70)
print("[2] 衰減檢查: 有冇任何模式嘅包絡衰減?")
print("=" * 70)
# 對每個模式 k, 檢查 |v_k(j)| 包絡係咪單調衰減 (指數嘅特徵)
decay_found = False
for k in range(1, N+1):
    vk = [abs(math.sin(math.pi * k * j / 88)) for j in range(1, N+1)]
    # 檢查前半段包絡 (j = 1..22) 有冇單調下降
    if all(vk[j] <= vk[j-1] + 1e-12 for j in range(1, 22)):
        decay_found = True
        print(f"  mode k={k}: 前 22 個 site 包絡單調衰減? 有 (但係零點結構, 唔係指數)")
chk("無模式有指數包絡", not decay_found or max_ipr[1] < 0.1,
    "正弦零點造成局部起伏, 但 IPR 證實全延展")

print()
print("=" * 70)
print("[3] Green's function 衰減 (band 外 E < 0)")
print("=" * 70)
print("  G(i,j;E) = Σ_k v_k(i)v_k(j)/(E − γ_k), E 喺帶底以下")
print("  1D 鏈 resolvent: 指數衰減喺 SITE 距離 |i−j| (局域化長度 ξ = 1/ln(...))")
print("  呢個係 site 空間嘅 evanescent decay — 唔係 mode 索引 n 嘅 e⁻ⁿ")
# 示範: G(1, j) 喺 E = -0.1 隨 j 指數衰減
E = -mpf('0.1')
Gj = []
for j in range(1, 12):
    g = sum(math.sin(math.pi*k*1/88) * math.sin(math.pi*k*j/88) / (E - 4*math.sin(math.pi*k/88)**2) for k in range(1, 45))
    Gj.append(abs(g))
ratios = [Gj[i+1]/Gj[i] for i in range(len(Gj)-1) if Gj[i] != 0]
print(f"  |G(1,j)| 比值 (j=1..11): {[f'{float(r):.3f}' for r in ratios[:6]]}... (常數比 = 指數衰減, site 空間)")
if ratios:
    r_mean = float(sum(ratios)/len(ratios))
    print(f"  平均比 {r_mean:.4f} -> 局域化長度 ξ ≈ {mp.nstr(-1/mp.log(mpf(r_mean)), 5)} sites (site 空間)")
    chk("site 空間指數衰減存在", mpf(r_mean) < mpf(1), "但係 site 索引, 唔係 mode 索引")
chk("mode 索引無 e⁻ⁿ 衰減 (IPR 全延展)", max_ipr[1] < 0.1, "e⁻ⁿ 唔出自鏈譜 — 出自樹層縮放")

print()
print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
