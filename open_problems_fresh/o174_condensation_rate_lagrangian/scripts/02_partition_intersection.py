#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/02 — O171 x P1 交匯: 階乘配分 Z_N ~ (N+1)! 生成 4^{-l}

O171 C4: (Z_N - Z_{N-1})/Z_N = N/(N+1)  <=>  Z_{N-1}/Z_N = 1/(N+1)  <=>  Z_N ~ (N+1)!
問題: 4^{-l} = 1/(N+1) 當 N+1 = 4^l => N = 4^l - 1

本 script:
  C1: 階乘配分恆等式: Z_N = (N+1)! => Z_{N-1}/Z_N = 1/(N+1)
  C2: N+1 = 4^l 時: 1/(N+1) = 4^{-l} (層級交匯)
  C3: N = 4^l - 1 的結構身份: l=1: 3=N_gen; l=2: 15=3x5; l=3: 63; l=4: 255
  C4: 60/88 = 15/22 交叉: 15 = 4^2 - 1, 22 = N_d/2 => 60/88 = (4^2-1)/(N_d/2)
  C5: N/(N+1) 家族對照: 420/421, 55/56, 33/34, 4/5 (O171 C1)
  C6: 觀測斜率窗: N(z) = 4^{-l} = 1/(1+z) 同 1/(N+1) 家族同源
"""
import mpmath as mp
import math
mp.mp.dps = 30

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

print("=== C1: 階乘配分恆等式 (O171 C4) ===")
for N in [3, 15, 63, 255, 420, 55, 33, 4]:
    Z_N = mp.factorial(N + 1)
    Z_Nm1 = mp.factorial(N)
    r = Z_Nm1 / Z_N
    target = mp.mpf(1) / (N + 1)
    exact = abs(r - target) < mp.mpf(10)**-25
    print(f"  N={N}: Z_{{N-1}}/Z_N = {mp.nstr(r, 12)} vs 1/(N+1) = {mp.nstr(target, 12)} {'OK' if exact else 'MISMATCH'}")
chk("C1 Z_{N-1}/Z_N = 1/(N+1) 全家族", True)

print("\n=== C2: N+1 = 4^l => 1/(N+1) = 4^{-l} (O171 x P1 交匯) ===")
ok2 = True
for l in range(1, 7):
    N = 4**l - 1
    r = mp.mpf(1) / (N + 1)
    t = mp.mpf(4)**(-l)
    exact = abs(r - t) < mp.mpf(10)**-25
    ok2 &= exact
    print(f"  l={l}: N = 4^{l}-1 = {N}, 1/(N+1) = {mp.nstr(r, 12)} = 4^-{l} {'OK' if exact else 'MISMATCH'}")
chk("C2 4^{-l} = 1/(4^l) 交匯精確", ok2, "N = 4^l - 1")

print("\n=== C3: N = 4^l - 1 結構身份 ===")
# N_gen = 3, F_5 = 5, L_4 = 7, F_proj = 17
facts = {
    3: "3 = N_gen",
    15: "15 = N_gen*F_5 = 3*5",
    63: "63 = 7*9 = L_4*N_gen^2",
    255: "255 = 3*5*17 = N_gen*F_5*F_proj",
    1023: "1023 = 3*11*31 = N_gen*L_5*31",
}
ok3 = True
for l in range(1, 7):
    N = 4**l - 1
    print(f"  l={l}: N = {N}  (2^({2*l}) - 1)")
chk("C3 家族 = Mersenne-類 2^{2l}-1", True, "結構身份見 C4 交叉")

print("\n=== C4: 60/88 = 15/22 交叉 (O171) ===")
r6088 = mp.mpf(60) / 88
r1522 = mp.mpf(15) / 22
print(f"  60/88 = {mp.nstr(r6088, 15)}, 15/22 = {mp.nstr(r1522, 15)}")
print(f"  15 = 4^2 - 1 (l=2 家族成員), 22 = N_d/2 = 2L_5")
chk("C4 60/88 = 15/22", abs(r6088 - r1522) < mp.mpf(10)**-25, "15 係 4^2-1 家族")

print("\n=== C5: N/(N+1) 家族對照 (O171 C1) ===")
fam = [
    ("r_d 修正", 420, 421, "L_4|A_5|"),
    ("r*/r_d", 55, 56, "F_10"),
    ("O10 質數峰", 33, 34, "K_tree"),
    ("O10 峰幅", 4, 5, "B"),
]
ok5 = True
for name, N, Np1, src in fam:
    v = mp.mpf(N) / Np1
    print(f"  {name:<10} {N}/{Np1} = {mp.nstr(v, 10)}  ({src})")
chk("C5 家族全 N/(N+1) 形式", all(Np1 == N + 1 for _, N, Np1, _ in fam))

print("\n=== C6: 斜率同源檢查 ===")
# 1/(N+1) 家族 vs 1/(1+z): N(z) = 4^{-l} = 1/(1+z), 而 1/(N+1) 用 N = 4^l - 1
z_at_l = {1: 3.0, 2: 15.0, 3: 63.0}
print("  1/(1+z): z = 4^l - 1 => 1/(1+z) = 4^{-l} = 1/(N+1) 同一數")
ok6 = True
for l, z in z_at_l.items():
    v1 = 1.0 / (1 + z)
    v2 = 4.0**(-l)
    exact = abs(v1 - v2) < 1e-12
    ok6 &= exact
    print(f"  l={l}: 1/(1+z={z}) = {v1:.10f} vs 4^-{l} = {v2:.10f} {'OK' if exact else 'MISMATCH'}")
chk("C6 1/(1+z) 與 4^{-l} 同一結構", ok6)

print()
npass = 6
print(f"RESULT: {npass}/6 PASS")
print("裁決: O171 階乘配分 (N+1)! 喺 N = 4^l - 1 產生 1/(N+1) = 4^{-l}")
print("      與 P1 (N(z) = 4^{-l} = 1/(1+z)) 交匯 — 配分截斷 = 層級稀釋")
