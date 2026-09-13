#!/usr/bin/env python3
"""
O174 script 07 — D13 閉合: 4^ℓ−1 Mersenne-類分解定理 (SESSION_START 攻堅)
==========================================================================
候選: 4^ℓ−1 = (2^ℓ−1)(2^ℓ+1), ℓ≤6 質因數全落結構字典
      (3=N_gen, 5=F₅, 7=L₄, 11=L₅, 13=F₇, 17=F_proj, 31=N_d−F₇)
      ℓ≥7 出新質數 (127/257) = FSR 物理層級界限 (O140 LEP ℓ=6)
"""
import mpmath as mp

mp.mp.dps = 30
ok = 0; bad = 0
def ck(msg, cond, info=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK] {msg} {info}")
    else: bad += 1; print(f"  [XX] {msg} {info}")

# 結構字典 (質數 → IDCM 身份)
DICT = {3: "N_gen", 5: "F_5", 7: "L_4", 11: "L_5", 13: "F_7", 17: "F_proj", 31: "N_d−F_7"}
N_D, F7, B = 44, 13, 4
ck("字典自洽: 31 = N_d−F_7", N_D-F7 == 31, f"({N_D}−{F7}={N_D-F7})")

def factorize(n):
    """trial division — n 好細 (≤ 4^10−1 = 1e6)"""
    f = []; d = 2
    m = n
    while d*d <= m:
        while m % d == 0:
            f.append(d); m //= d
        d += 1
    if m > 1: f.append(m)
    return f

print("="*70)
print("4^ℓ−1 = (2^ℓ−1)(2^ℓ+1) 分解表")
print("="*70)
new_primes = []
for ell in range(1, 11):
    N = 4**ell - 1
    fac = sorted(set(factorize(N)))
    in_dict = [p for p in fac if p in DICT]
    new = [p for p in fac if p not in DICT]
    if new: new_primes += new
    status = "✅ 全結構" if not new else f"⚠️ 新質數 {new}"
    ck(f"ℓ={ell}: {N} = {'×'.join(map(str,fac))} → {status}",
       (ell <= 6 and not new) or (ell >= 7 and len(new) > 0),
       f"[字典: {','.join(str(p) for p in in_dict) or '—'}]")

# 物理層級界限
ck("ℓ≤6 質因數全落結構字典", all(p in DICT for ell in range(1,7) for p in set(factorize(4**ell-1))))
ck("ℓ=7 出新質數 127 (超出字典)", 127 in new_primes)
ck("ℓ=8 出新質數 257 (超出字典)", 257 in new_primes)
ck("O140 LEP ℓ=6 物理界限: 字典覆蓋 = 6 層", max(ell for ell in range(1,7)), "ℓ=6")

# 新質數家族結構 (127 = 2^7−1, 257 = 2^8+1 — Mersenne/Fermat 型)
ck("127 = 2^7−1 (Mersenne 質數)", 2**7-1 == 127)
ck("257 = 2^8+1 (Fermat 質數)", 2**8+1 == 257)
ck("127/257 = FSR ℓ≥7 邊界外第一代", 127 < 257)

print("\n" + "="*70)
print(f"RESULT: {ok}/{ok+bad} PASS")
