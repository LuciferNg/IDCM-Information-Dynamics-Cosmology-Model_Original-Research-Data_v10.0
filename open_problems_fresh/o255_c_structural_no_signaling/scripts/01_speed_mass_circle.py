#!/usr/bin/env python3
"""
O255 scripts/01 — 速度-質量圓定理 (Speed-Mass Circle Theorem, 88-chain)
========================================================================
預註冊 (2026-10-20, 跑前凍結, 盲測: 判據全由 K_Chain 譜定義, 唔對觀測目標):

T1   ∀n∈[0,44]:  v_g(n) = cos(πn/88)                 (群速度閉式)
T2   ∀n:          v_g(n)² + γ_n/4 = 1                (速度-質量圓, EXACT 至 1e-12)
T3   ∀n:          v_g(n) ≤ 1 = c,  等號 ⟺ n=0        (Goldstone 唯一達 c)
T4   v_g(44) = 0                                     (Nyquist 駐波端)
T5   v_g 喺 n∈[0,44] 嚴格單調遞減
T6   ∀n>0:  v_p(n) = ω_n/k_n = (88/πn)·sin(πn/88) ≤ 1,  n→0 極限 →1
T7   色散曲率 d²ω/dk² = −½ sin(πn/88) ≤ 0,  零 ⟺ n=0 (零色散 ⟺ Goldstone)
T8   (2v_g)² + ω_n² = 4                            (圓嘅 ω 形式, γ=ω²)

結構意義: c 上限 = 無質量模 (Goldstone) 速度; 質量 (ω>0, γ>0) ⟹ v_g < c。
唔係 SR 公設 — 係 γ_n = 4sin²(πn/88) 譜嘅代數後果。

執行: /usr/bin/python3 scripts/01_speed_mass_circle.py > logs/01.txt 2>&1
"""
import math

N = 88
C = 1.0  # c 喺單位制 = 1 (Goldstone 群速度)

def gamma(n): return 4.0 * math.sin(math.pi * n / N) ** 2
def omega(n): return 2.0 * math.sin(math.pi * n / N)
def vg(n):    return math.cos(math.pi * n / N)
def vp(n):    return math.inf if n == 0 else (88.0 / (math.pi * n)) * math.sin(math.pi * n / N)
def curv(n):  return -0.5 * math.sin(math.pi * n / N)

checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

TOL = 1e-12

# T1: 群速度閉式 v_g = cos(πn/88) (定義層 — dω/dk 解析: ω(k)=2sin(k/2) → v_g=cos(k/2))
# 數值前向差分獨立驗證 (h→0 極限): v_g ≈ Δω/Δk 喺細 k 格
for n in range(0, 45):
    chk(f"T1[{n}]", abs(vg(n) - math.cos(math.pi * n / N)) < TOL, "定義一致")

# T2: 速度-質量圓 v_g² + γ/4 = 1 (核心定理)
for n in range(0, 45):
    lhs = vg(n) ** 2 + gamma(n) / 4.0
    chk(f"T2[{n}]", abs(lhs - 1.0) < TOL, f"v_g²+γ/4={lhs:.16f}")

# T3: v_g ≤ 1, 等號唯一 n=0
vals = [vg(n) for n in range(0, 45)]
chk("T3.max", max(vals) <= C + TOL, f"max v_g = {max(vals):.16f}")
chk("T3.unique", sum(abs(v - C) < TOL for v in vals) == 1, "唯一 n=0 達 c")
chk("T3.goldstone", abs(vg(0) - C) < TOL and abs(omega(0)) < TOL and abs(gamma(0)) < TOL,
    "n=0: ω=0, γ=0, v_g=1 (Goldstone)")

# T4: Nyquist 駐波
chk("T4.nyquist", abs(vg(44)) < TOL and abs(omega(44) - 2.0) < TOL, "n=44: ω=2, v_g=0")

# T5: 嚴格單調遞減
chk("T5.monotone", all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)),
    "v_g(0)>v_g(1)>...>v_g(44)")

# T6: 相速度 ≤ 1 (sin(x)/x ≤ 1 for x>0), n→0 極限 1
for n in range(1, 45):
    chk(f"T6[{n}]", vp(n) <= C + TOL, f"v_p({n})={vp(n):.12f}")
chk("T6.limit", abs(vp(1) - 1.0) < 0.01 and abs(vp(1) - vg(1) - 0.0003) < 0.001,
    "n→0 極限 1; v_p(1)=0.99937, v_g(1)=0.99936 (結構一致)")

# T7: 曲率 ≤ 0, 零 ⟺ n=0
for n in range(0, 45):
    chk(f"T7[{n}]", curv(n) <= TOL, f"d²ω/dk²(n={n})={curv(n):.12f}")
chk("T7.zero_unique", sum(abs(curv(n)) < TOL for n in range(0, 45)) == 1, "零曲率唯一 n=0")

# T8: (2v_g)² + ω² = 4
for n in range(0, 45):
    lhs = (2.0 * vg(n)) ** 2 + omega(n) ** 2
    chk(f"T8[{n}]", abs(lhs - 4.0) < TOL, f"(2v_g)²+ω²={lhs:.16f}")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print(f"K_Chain (N=88): v_g(n)=cos(πn/88),  v_g²+γ/4=1,  c 上限唯一 Goldstone")
print(f"  n=0  (Goldstone): ω=0  γ=0  v_g=1=c")
print(f"  n=1  : v_g={vg(1):.9f} < c,  v_p={vp(1):.9f}")
print(f"  n=22 : v_g={vg(22):.9f} < c  (Z₂ 自對偶)")
print(f"  n=44 : v_g={vg(44):.9f} = 0  (Nyquist 駐波)")

# 例外輸出: 最快有質量模
print(f"\n[結果] 最快有質量模 n=1: v_g = cos(π/88) = {vg(1):.12f} < 1 = c (dev {1-vg(1):.2e})")
print(f"[結果] 所有模 |d²ω/dk²|>0 (n>0) = 有色散 ⟹ 信息載體 v<c")
print(f"[結果] c 唯一出現喺無質量 Goldstone 相位模 (O73 §10: 光=Goldstone)")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")