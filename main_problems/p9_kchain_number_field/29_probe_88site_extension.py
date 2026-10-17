#!/usr/bin/env python3
"""
29_probe_88site_extension.py — 88/176 擴展探針 (2026-10-17)
============================================================
問題: 44-site magic rows 嘅 L₄/L₅ anchor 對 (7,11) 點樣喺更大鏈做樣本外測試?

框架: N-site 鏈嘅數域推廣
  44-site: N=44,  ω_n=2sin(πn/88)  ∈ ℚ(ζ₁₇₆)⁺ (4N 分圓),  γ_n=4sin²(πn/88) ∈ ℚ(ζ₈₈)⁺ (2N 分圓)
  88-site: N=88,  ω_n=2sin(πn/176) ∈ ℚ(ζ₃₅₂)⁺ (4N),      γ_n=4sin²(πn/176)∈ ℚ(ζ₁₇₆)⁺ (2N)
  176-site: N=176, ω_n=2sin(πn/352) ∈ ℚ(ζ₇₀₄)⁺ (4N),      γ_n=4sin²(πn/352)∈ ℚ(ζ₃₅₂)⁺ (2N)
  deg(ω_n)=φ(4N/gcd(|N−n|,4N))/2;  deg(γ_n)=φ(2N/gcd(n,2N))/2

本探針重算: 88-site 數域結構 (gcd 類 / deg 分佈 / 七揀五推廣 / L 對地位)
零 import 原推導; 純整數/φ 第一原理。
"""
from math import gcd
from collections import Counter

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

def deg_omega(N, n):
    return phi(4 * N // gcd(abs(N - n), 4 * N)) // 2

def deg_gamma(N, n):
    return phi(2 * N // gcd(n, 2 * N)) // 2

def v2(x):
    c = 0
    while x % 2 == 0:
        c += 1; x //= 2
    return c

for N in (44, 88, 176):
    print(f"\n================ N={N} (=site 數) ================")
    # gcd 類: magic rows 喺 44-site 用 gcd(|44-d|,176); 推廣 = gcd(|N-d|, 4N)?!
    # 44-site: gcd(|44-d|,176) = gcd(|N-d|,4N) ✓ (176=4×44)
    classes = {}
    for d in range(1, N):
        g = gcd(abs(N - d), 4 * N)
        classes.setdefault(g, []).append(d)
    print(f"gcd 類 ({len(classes)}):", {g: len(v) for g, v in sorted(classes.items())})
    # ω deg 分佈 (n=1..N)
    do = Counter(deg_omega(N, n) for n in range(1, N + 1))
    print("ω deg 分佈:", dict(sorted(do.items())))
    # γ deg 分佈
    dg = Counter(deg_gamma(N, n) for n in range(1, N + 1))
    print("γ deg 分佈:", dict(sorted(dg.items())))
    # Lucas 質數喺呢個 N:
    L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76}
    Lp = [(k, v) for k, v in L.items() if v <= N and v != 18 and v != 76]  # 質數限定 (2,3,7,11,29,47)
    def isprime(x):
        if x < 2: return False
        for p in range(2, int(x**0.5) + 1):
            if x % p == 0: return False
        return True
    Lp = [(k, v) for k, v in L.items() if isprime(v) and v <= N]
    print("Lucas 質數 ≤N:", Lp)
    half = N // 2
    print(f"half-node = {half}")
    # 「gap = L₃ = 4」嘅連續質數對
    pairs4 = [(Lp[i], Lp[i+1]) for i in range(len(Lp)-1) if Lp[i+1][1] - Lp[i][1] == 4]
    print("gap=4=L₃ 連續質數對:", [(f"L{a[0]}={a[1]}", f"L{b[0]}={b[1]}") for a, b in pairs4])
    for ai, bi in pairs4:
        a, b = ai, bi
        both_front = b[1] <= half or a[1] <= half
        print(f"  對 ({a[1]},{b[1]}): 前半={both_front}, 唯一索引? L{a[0]}={a[1]} idx{a[0]}, L{b[0]}={b[1]} idx{b[0]}")
    # 檢查 7 同 11 喺 N 嘅 gcd 類 / deg
    for d in (7, 11, 29):
        g = gcd(abs(N - d), 4 * N)
        print(f"  d={d}: gcd=({g}) ω_deg={deg_omega(N, d)} γ_deg={deg_gamma(N, d)}")

print("\n== 結論要點 (由數據判斷) ==")
print("1. gcd 類數: 44-site 7 類 {1,2,4,8,11,16,22}; 88-site 應更大 (352=2⁵×11); 176-site 更大")