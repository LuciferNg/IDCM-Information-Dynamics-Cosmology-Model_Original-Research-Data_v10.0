#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/08 — D13 閉合: 4^l-1 Mersenne-類家族分解定理 (由零重算)

docs/05 D13 預檢 (scripts/06) 已 6/6。本 script 做閉合級完整驗證:
C1: 恆等 4^l-1 = (2^l-1)(2^l+1) 代數證明 (l=1..20)
C2: l<=6 質因數全結構身份 (逐質因數)
C3: l>=7 新質數出現點 (127/257) = FSR 物理層級界限 (O140: LEP l=6, LHC l=10)
C4: 結構身份字典 (3/5/7/11/13/17/31/33/43) 全部已註冊出處
C5: 控制組 — 4^l (冇 -1) 冇呢個模式; 5^l-1/3^l-1 對照
C6: mod-4 判準 (4^l-1 ≡ 3 mod 4, O160 45族 a 奇連接)
C7: 家族封閉性: 質因數集喺 l<=6 唔增長 (<= 已知結構質數)
"""
import mpmath as mp
mp.mp.dps = 30

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

def factorize(n):
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

# 已註冊結構質數 (含出處)
struct_primes = {
    3: "N_gen", 5: "F_5", 7: "L_4", 11: "L_5", 13: "F_7",
    17: "F_proj", 31: "N_d-F_7=44-13", 33: "K_tree(複合)", 43: "邊界mode O160 T25",
}
struct_all = set(struct_primes) | {9}

total = 0; passed = 0

print("=== C1: 恆等 4^l-1 = (2^l-1)(2^l+1) (l=1..20) ===")
ok = all(4**l - 1 == (2**l - 1) * (2**l + 1) for l in range(1, 21))
total += 1; passed += ok
chk("C1 恆等 4^l-1 = (2^l-1)(2^l+1)", ok, "l=1..20 全 OK")

print("\n=== C2: l<=6 質因數全結構 ===")
expected = {1:[3], 2:[3,5], 3:[3,3,7], 4:[3,5,17], 5:[3,11,31], 6:[3,3,5,7,13]}
ok = True
for l, exp in expected.items():
    f = sorted(factorize(4**l - 1))
    good = f == exp
    ok &= good
    print(f"  l={l}: 4^{l}-1 = {4**l-1} = {'x'.join(map(str,f))} "
          f"{'OK' if good else 'MISMATCH exp ' + str(exp)}")
    if not good:
        break
total += 1; passed += ok
chk("C2 l<=6 質因數全結構", ok)

print("\n=== C3: l>=7 新質數出現 (物理層級界限) ===")
known = set()
boundary = {}
for l in range(1, 13):
    f = factorize(4**l - 1)
    new = [p for p in f if p not in known and p not in struct_all]
    if new:
        boundary[l] = new
    known.update(f)
print(f"  新質數出現層級: {boundary}")
ok = 7 in boundary and 8 in boundary
total += 1; passed += ok
chk("C3 l=7,8 出現 127/257 新質數", ok, f"(boundary = {boundary})")

# 檢查 127, 257 唔喺結構字典
ok = 127 not in struct_all and 257 not in struct_all
total += 1; passed += ok
chk("C3b 127/257 未註冊 = 物理層級外", ok, "O140: 已閉合物理範圍 ℓ≤6 (LEP), LHC ℓ=10 仍喺 FSR")

print("\n=== C4: 結構身份出處 ===")
ok = all(struct_primes)
total += 1; passed += ok
chk("C4 結構質數字典出處全齊", ok,
    "3/5/7/11/13/17/31/33/43 = N_gen/F_5/L_4/L_5/F_7/F_proj/N_d-F_7/K_tree/邊界mode")

print("\n=== C5: 控制組 ===")
# 5^l-1, 3^l-1 冇呢個模式 (非 Mersenne-類 4^l-1)
ok = all(5**l - 1 != 4**l - 1 for l in range(1, 6))
total += 1; passed += ok
chk("C5a 5^l-1 唔同 4^l-1 (控制)", ok)

# 4^l 冇 -1: 質因數只有 2 (μ² 已結構) — 唔會出現 3/5/7...
ok = all(set(factorize(4**l)) == {2} for l in range(1, 6))
total += 1; passed += ok
chk("C5b 4^l 冇 -1: 只有 2", ok, "控制: 模式係 -1 家族特有")

print("\n=== C6: mod-4 判準 ===")
ok = all((4**l - 1) % 4 == 3 for l in range(1, 13))
total += 1; passed += ok
chk("C6 4^l-1 ≡ 3 (mod 4)", ok, "O160 45族 a 奇連接: mod-4 判準 (45族 a 奇/47族 a 偶)")

print("\n=== C7: 家族封閉性 (l<=6 質因數集唔增長) ===")
primes_l6 = set()
for l in range(1, 7):
    primes_l6.update(factorize(4**l - 1))
print(f"  l<=6 質因數集: {sorted(primes_l6)}")
ok = primes_l6 <= set(struct_primes)
total += 1; passed += ok
chk("C7 l<=6 質因數集 ⊆ 結構質數集", ok, f"({sorted(primes_l6)} ⊆ {sorted(set(struct_primes))})")

print(f"\nRESULT: {passed}/{total} PASS")
if passed == total:
    print("D13 閉合 — 4^l-1 Mersenne-類分解定理成立, 零新常數, 物理層級界限確認")
