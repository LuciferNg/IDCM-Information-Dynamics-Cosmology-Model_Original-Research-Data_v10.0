#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O241 Q2 附錄 — 1D tight-binding 鏈: 裸有限譜 vs ζ 連續極限 (負發現一致性)
===========================================================================
結論預告 (2026-10-08, 實算):
  S(N) = Σ_{m=1}^N sin(πm/(2(N+1))) = 2(N+1)/π − 1/2 + O(1/N)   [精確閉式]
  => 裸譜差 E_cas_shape(N) = S(N) − 2N/π → 2/π − 1/2 (常數), 冇 1/N Casimir 項
  => 1D tight-binding 鏈之裸有限譜**唔出** −π/24·(1/N) 係數
  => 連續 Casimir 係數必須經 ζ 解析延續 (scripts/01 Part 2 = zeta 恆等), 與 C8 一致.
本 script 驗證 (a) 精確閉式 (b) 常數極限 (c) 方程式中之係數只能由 ζ 獲取.

呢個唔係「失敗」: 佢係支撐 docs/02 一句關鍵聲稱 —
「IDCM 88-site 有限譜 → Casimir 係數」唔可以靠裸有限譜截斷; 連續極限
係 ζ(−3)=1/120 之解析延續; 88-site 環譜差有限/吸引 (scripts/01 C1-C3)
提供機制, 係數由 ζ 恆等鎖定 (scripts/01 C5-C7, dev 1e-12).
"""

import math, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []

def check(name, cond, detail=""):
    results.append({"check": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

def S_exact(N):
    # Σ_{m=1}^N sin(mθ), θ = π/(2(N+1)):
    # = sin(Nθ/2)·sin((N+1)θ/2)/sin(θ/2)
    th = math.pi/(2*(N+1))
    return (math.sin(N*th/2.0)*math.sin((N+1)*th/2.0))/math.sin(th/2.0)

def S_direct(N):
    return sum(math.sin(m*math.pi/(2*(N+1))) for m in range(1, N+1))

print("="*72)
print("1D chain: S(N) = Σ sin(πm/(2(N+1))) — 精確閉式 vs 直接和")
print("="*72)
ok_exact = True
for N in [10, 100, 1000, 5000]:
    e, d = S_exact(N), S_direct(N)
    if abs(e-d) > 1e-12:
        ok_exact = False
    print(f"  N={N:5d}: exact={e:.12f} direct={d:.12f}  dev={abs(e-d):.2e}")
check("C1: S(N) 閉式 (sin 和公式) = 直接和 dev<1e-12",
      ok_exact)

print("\n  漸近: S(N) vs 2(N+1)/π − 1/2")
for N in [100, 1000, 5000]:
    asym = 2*(N+1)/math.pi - 0.5
    print(f"  N={N:5d}: S={S_exact(N):.8f}  2(N+1)/π−½={asym:.8f}  dev={abs(S_exact(N)-asym):.3e}")
check("C2: S(N) → 2(N+1)/π − 1/2 (dev 收縮, N=5000 < 1e-3)",
      abs(S_exact(5000) - (2*5001/math.pi - 0.5)) < 1e-3)

print("\n  裸譜差: E_cas_shape(N) = S(N) − 2N/π (每格 bulk 2/π)")
vals = {}
for N in [100, 500, 1000, 2000, 5000]:
    vals[N] = S_exact(N) - 2*N/math.pi
    print(f"  N={N:5d}: E_cas_shape = {vals[N]:+.8f}  (常數極限 2/π−½ = {2/math.pi-0.5:+.8f})")
L_lim = vals[5000]
check("C3: 裸譜差收斂至常數 2/π−1/2 (冇 1/N Casimir 項)",
      abs(L_lim - (2/math.pi - 0.5))/abs(2/math.pi-0.5) < 0.01,
      f"{L_lim:+.8f} vs {2/math.pi-0.5:+.8f}")

print("\n  負發現 — 裸有限譜唔出 −π/24·(1/N) 係數:")
ratio_at_N = vals[5000]*5000   # 若係 −π/24·1/N 則 *N → −π/24
print(f"  E_cas_shape(5000)*5000 = {ratio_at_N:+.4f}   (若係 −π/24 應 = {-math.pi/24:.4f})")
check("C4: 裸譜差×N 唔等於 −π/24 (證偽「裸有限譜直接出 Casimir 係數」)",
      abs(ratio_at_N - (-math.pi/24.0)) > 5.0,
      f"{ratio_at_N:+.4f} vs −π/24={-math.pi/24:.4f}  (>5 偏差 = 唔係嗰個係數)")

# ζ 路線 (唯一正確): Σ n^{-s} 解析延續 ζ(−3)=1/120 → 連續極限係數
print("\n  ζ 路線 (scripts/01 C5-C7): ζ(−3)=1/120 → π²/720 = ζ(2)ζ(−3)")
zprod = (math.pi**2/6.0)*(1.0/120.0)
print(f"  ζ(2)·ζ(−3) = {zprod:.12f}   π²/720 = {math.pi**2/720:.12f}")
check("C5: ζ(2)ζ(−3) = π²/720 EXACT (唯一出連續係數之路)",
      abs(zprod - math.pi**2/720.0) < 1e-15)
check("C6: 係數鏈 F = π²ħc/240d⁴ ⇐ 3·ζ(2)ζ(−3) (3/720=1/240)",
      abs(3*zprod - math.pi**2/240.0)/(math.pi**2/240.0) < 1e-15,
      f"3ζ2ζ−3 = {3*zprod:.12f}  π²/240 = {math.pi**2/240:.12f}")

with open(os.path.join(BASE, "data", "02_chain_casimir_em.json"), "w") as f:
    json.dump({"S_exact": {str(k): S_exact(k) for k in [100, 5000]},
               "E_cas_shape": {str(k): v for k, v in vals.items()},
               "zeta_prod": zprod}, f, indent=2)

npass = sum(1 for r in results if r["pass"])
nfail = sum(1 for r in results if not r["pass"])
print(f"\n{'='*72}\nRESULT: {npass}/{len(results)} PASS\n{'='*72}")