#!/usr/bin/env python3
"""
Self Loop 深度驗證: self loop = SYNC(ω_n), degree 一致性
==========================================================
問題: self loop (n,n) sum = 2ω_n = 4sin(nπ/88)
      lcm 定理話 beat degree = lcm(deg(ω_i), deg(ω_j))
      self loop 係咪 lcm(deg, deg) = deg? 定係直接 = deg(ω_n)?
"""
from math import gcd, lcm, pi, sin

def phi(n):
    r = n; p = 2
    while p*p <= n:
        if n % p == 0:
            while n % p == 0: n //= p
            r -= r // p
        p += 1
    if n > 1: r -= r // n
    return r

def omega_deg(n):
    if n == 44: return 1
    d = abs(44-n)
    g = gcd(d, 176)
    return phi(176//g)//2

def sum_deg(n):
    """4sin(nπ/88) = 4sin(2nπ/176) 嘅 degree"""
    def sin_deg(k):
        k = abs(k) % 176
        if k == 88: return 1
        m = (88-k) % 176
        g = gcd(352, m)
        return phi(352//g)//2
    return sin_deg(2*n)

print("="*70)
print("Self loop degree vs ω_n degree 對照")
print("="*70)
print(f"{'n':>3} {'deg(ω_n)':>9} {'deg(sum=4sin(nπ/88))':>22} {'一致?':>5}")
mismatch = []
for n in range(1,45):
    od = omega_deg(n)
    sd = sum_deg(n)
    ok = "✅" if od == sd else "❌"
    if od != sd: mismatch.append((n, od, sd))
    print(f"{n:>3} {od:>9} {sd:>22} {ok}")

print(f"\n一致: {44-len(mismatch)}/44")
if mismatch:
    print(f"不一致: {mismatch}")
else:
    print("✅ 全部一致 — self loop degree = deg(ω_n)")

print()
print("="*70)
print("結論: self loop (n,n) 嘅和頻次數 = deg(ω_n)")
print("="*70)
print("""
  sum(n,n) = 4sin(nπ/88) = 2ω_n
  deg = deg(ω_n) — 因為 2ω_n 係 ω_n 嘅有理倍數!
  
  ★ Self loop = SYNC(ω_n) = DUP+ADD
     — 唔係 lcm(deg,deg) = deg (trivial), 而係直接繼承端點次數
     — SYNC 唔增加代數複雜度 (有理倍數 2×)
     
  → 對比: 拍頻 (i,j) i≠j 嘅 degree = lcm(deg_i, deg_j) (可以提升)
  → self loop 嘅 degree = deg_n (冇提升, 冇組合)
  → 「拍頻 = 組合指令 (提升次數), self loop = 單一指令 (唔提升)」
""")

# 特殊值
print("="*70)
print("特殊 self loop (高對稱)")
print("="*70)
for n in [11, 22, 33, 44]:
    w = 2*sin(pi*n/88)
    print(f"  n={n:2d}: ω_n = {w:.10f}, SYNC → {2*w:.10f}, deg={omega_deg(n)}")
print(f"""
  n=11: 2√(2−√2) ≈ {2*(2-2**0.5)**0.5:.8f}  (γ_11 嘅 2×)
  n=22: 2√2 ≈ {2*2**0.5:.8f}  (半節點, v_g=c)
  n=33: 2√(2+√2) ≈ {2*(2+2**0.5)**0.5:.8f}
  n=44: 4 (Nyquist, 有理 — 唯一 deg=1 self loop)
""")
