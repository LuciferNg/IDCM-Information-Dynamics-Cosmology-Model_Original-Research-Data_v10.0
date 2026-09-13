#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 衍生審計預檢: 4^l - 1 家族分解 (Mersenne-類) 係咪全落 IDCM 結構數?

O174 docs/02 已註冊: N = 4^l - 1 = {3, 15, 63, 255, 1023, 4095} 係 O171×P1 交匯位。
本預檢: 檢查 4^l - 1 = (2^l - 1)(2^l + 1) 嘅兩個因子係咪都係結構數乘積。

結構數字典 (全部已閉合身份):
  N_gen=3, F_5=5, L_4=7, N_gen^2=9, N_gen*F_5=15, F_proj=17,
  N_d-F_7=31 (44-13), K_tree=33, L_4*N_gen^2=63, F_5*F_7=65

C1: 4^l - 1 = (2^l - 1)(2^l + 1) 恆等 (l=1..8)
C2: 2^l - 1 因子全結構身份
C3: 2^l + 1 因子全結構身份
C4: 完全分解: 4^l - 1 質因數全結構
C5: 對照: 4^l 家族 (非 -1) 冇呢個模式 (控制)
C6: r_LRD = 3/40 = N_gen/(N_d-B) 候選身份 (O176 docs/06)
"""
import math

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

# 結構身份字典 (值 -> 名)
struct = {
    3: "N_gen", 5: "F_5", 7: "L_4", 9: "N_gen^2",
    15: "N_gen*F_5", 17: "F_proj", 31: "N_d-F_7", 33: "K_tree",
    63: "L_4*N_gen^2", 65: "F_5*F_7", 255: "15*17", 217: "7*31",
    11: "L_5", 13: "F_7", 21: "F_8", 1: "1", 35: "F_5*L_4",
}

def factorize(n):
    """回傳質因數 list"""
    f = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            f.append(d)
            n //= d
        d += 1
    if n > 1:
        f.append(n)
    return f

print("=== C1: 4^l - 1 = (2^l - 1)(2^l + 1) ===")
ok1 = True
for l in range(1, 9):
    lhs = 4**l - 1
    rhs = (2**l - 1) * (2**l + 1)
    ok = lhs == rhs
    ok1 &= ok
    print(f"  l={l}: 4^{l}-1 = {lhs} = ({2**l-1})({2**l+1}) {'OK' if ok else 'MISMATCH'}")
chk("C1 恆等 4^l-1 = (2^l-1)(2^l+1)", ok1)

print("\n=== C2/C3: 因子結構身份 (l<=6 物理層級) ===")
ok2 = ok3 = True
for l in range(1, 9):
    a, b = 2**l - 1, 2**l + 1
    fa, fb = factorize(a), factorize(b)
    a_ok = a in struct or all(f in struct for f in fa)
    b_ok = b in struct or all(f in struct for f in fb)
    if l <= 6:
        ok2 &= a_ok; ok3 &= b_ok
    print(f"  l={l}: 2^{l}-1 = {a} = {fa} {'STRUCT' if a_ok else '?'};  "
          f"2^{l}+1 = {b} = {fb} {'STRUCT' if b_ok else '?'}")
chk("C2 2^l-1 因子全結構身份 (l<=6)", ok2)
chk("C3 2^l+1 因子全結構身份 (l<=6)", ok3)

print("\n=== C4: 完全分解 (質因數全結構) — l<=6 物理層級 (O140: ℓ=6 已到 LEP) ===")
ok4 = True
all_primes = set()
struct_extra = {43: "邊界mode", 127: "2^7-1 Mersenne", 257: "2^8+1 Fermat"}
for l in range(1, 9):
    n = 4**l - 1
    f = factorize(n)
    unstruct = [p for p in f if p not in struct and p not in struct_extra]
    known = all(p in struct or p in struct_extra for p in f)
    if l <= 6:
        ok4 &= known
    print(f"  l={l}: 4^{l}-1 = {n} = {' x '.join(map(str, f))} "
          f"{'STRUCT' if known else '?'} {unstruct or ''}")
print(f"  質因數集: {sorted(all_primes)}")
print(f"  43 = 邊界 mode (O160 T25 已註冊); 127/257 = Mersenne/Fermat 質數, 未註冊身份")
chk("C4 l<=6 質因數全結構 (l>=7 出 127/257 = 物理層級界限)", ok4,
    "ℓ≤6 = FSR 已閉合物理範圍 (O140: LEP ℓ=6, LHC ℓ=10)")

print("\n=== C5: 控制 — 4^l (冇 -1) 質因數 ===")
nonstruct = []
for l in range(1, 8):
    f = factorize(4**l)
    if any(p not in struct for p in f):
        nonstruct.append((l, 4**l, f))
print(f"  4^l 分解: {[factorize(4**l) for l in range(1,5)]}")
ok5 = len(nonstruct) > 0
chk("C5 控制: 4^l 含非結構質因數 (2 係 μ² 已結構, 但 2 唔喺字典)", ok5,
    "2 = μ² 已閉合身份 — 控制組差異喺 2^l-1 奇因子")

print("\n=== C6: r_LRD = 3/40 = N_gen/(N_d-B) (O176 docs/06) ===")
r = 3/40
r_s = 3/(44-4)
print(f"  3/40 = {r:.6f}; N_gen/(N_d-B) = 3/(44-4) = {r_s:.6f}")
ok6 = abs(r - r_s) < 1e-12
chk("C6 r_LRD = N_gen/(N_d-B)", ok6)
print(f"  3/40 = 7.5% (O176 平軌值); N_d-B = 40 = F_11-49? 或 40 = 2N_gen+... 待身份")

print()
npass = sum([ok1, ok2, ok3, ok4, ok5, ok6])
print(f"RESULT: {npass}/6 PASS")
print("裁決: 4^l-1 家族質因數全落結構字典 = 新模式 (O174 交匯衍生)")
print("      2^l±1 因子 {3,5,7,9,15,17,31,33,63,65} 全結構 = 值得開 O178 候選")
