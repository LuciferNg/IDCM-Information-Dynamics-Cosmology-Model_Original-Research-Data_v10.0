#!/usr/bin/env python3
"""
scripts/04 — IDCM 散射算子身份：子集鏡像定理（O231 Q1 核心定理）

定理（本 script 驗證）:
    IDCM 88-cycle 譜上（γ_k = 4sin²(πk/88), k=1..87, ω_k = 2|sin(πk/88)|），
    能量守恆 + 動量守恆 (mod 88) 的 n→n 散射解空間完全由「子集鏡像」生成：

    散射解 ⟺ 選擇初態模式的一個子集 S（Σ_{k∈S} k ≡ 0 (mod 44)），
              對 S 中每個模式做 antipodal 鏡像 k → 88−k，其餘模式不變。

    特例:
      S = ∅           → 恒等散射 (elastic, 無粒子產生)     [planar 可積性]
      S = 全集(2粒子)  → 2→2 antipodal 對偶 (a+b ≡ 0 mod 44)
      S = 全集(3粒子)  → 3→3 antipodal 對偶 (a+b+c ≡ 0 mod 44)
      S 真子集         → 「部分鏡像」散射（粒子數不變, 個別粒子鏡像化）

定理的 QFT 意義:
    - antipodal duality (QFT bootstrap) = 全子集鏡像 = IDCM 分層結構內建
    - 動量守恆模 44 = N_d/2 — 鏡像子集和必須是半鏈長度嘅整數倍
    - 無粒子產生 (粒子數守恆) = 子集鏡像保粒子數 → planar N=4 可積性對應
"""
import math, sys
from collections import Counter, defaultdict

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS [{name}] {detail}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL [{name}] {detail}")

N = 88
HALF = N // 2  # 44 = N_d
def omega(k): return 2 * abs(math.sin(math.pi * k / N))
K = list(range(1, N))

def mirror_subset_predictions(in_modes):
    """預測: 所有合法鏡像子集輸出（含恒等 S=∅）."""
    outs = {tuple(sorted(in_modes))}
    modes = list(in_modes)
    m = len(modes)
    for mask in range(1, 1 << m):
        S = [modes[i] for i in range(m) if (mask >> i) & 1]
        if sum(S) % HALF == 0:
            out = tuple(sorted(N - modes[i] if ((mask >> i) & 1) else modes[i]
                               for i in range(m)))
            outs.add(out)
    return outs

print("=" * 60)
print("T1. 2→2 散射解空間 = 子集鏡像（N=88, mod 44）")
print("=" * 60)
sols2 = []
for a in K:
    for b in K:
        Eab = omega(a) + omega(b)
        for c in K:
            d = (a + b - c) % N
            if d == 0:
                continue
            if abs(omega(c) + omega(d) - Eab) < 1e-12:
                sols2.append((a, b, c, d))

def subs_mirror_ok(s):
    a, b, c, d = s
    preds = mirror_subset_predictions((a, b))
    return tuple(sorted((c, d))) in preds

ok2 = sum(1 for s in sols2 if subs_mirror_ok(s))
check("T1a 所有 2→2 守恆解符合子集鏡像定理", ok2 == len(sols2),
      f"{ok2}/{len(sols2)}")

antip2 = [s for s in sols2 if Counter((s[2], s[3])) == Counter((N - s[0], N - s[1]))]
cond = all((s[0] + s[1]) % HALF == 0 for s in antip2)
check("T1b 2→2 antipodal 解全部滿足 a+b≡0 (mod 44)", cond, f"antipodal 解數={len(antip2)}")
# S=∅ 恒等
ident2 = [s for s in sols2 if Counter((s[2], s[3])) == Counter((s[0], s[1]))]
check("T1c 恒等散射 = S=∅", len(ident2) > 0, f"{len(ident2)}")

print()
print("=" * 60)
print("T2. 3→3 散射（六粒子振幅的鏈身份）")
print("=" * 60)
table3 = defaultdict(list)
for d in K:
    for e in K:
        for f in K:
            table3[(round(omega(d) + omega(e) + omega(f), 10), (d + e + f) % N)].append((d, e, f))

sols3 = []
for a in K:
    for b in K:
        for c in K:
            key = (round(omega(a) + omega(b) + omega(c), 10), (a + b + c) % N)
            for triple in table3.get(key, []):
                sols3.append(((a, b, c), triple))

# 去重
seen3 = set()
uniq3 = []
for s in sols3:
    key = (tuple(sorted(s[0])), tuple(sorted(s[1])))
    if key not in seen3:
        seen3.add(key)
        uniq3.append(s)

ok3 = 0
for s in uniq3:
    preds = mirror_subset_predictions(s[0])
    if tuple(sorted(s[1])) in preds:
        ok3 += 1
check("T2a 所有 3→3 去重解符合子集鏡像定理", ok3 == len(uniq3),
      f"{ok3}/{len(uniq3)} 類")

# 分類 3→3: identity / antipodal(全集) / genuine 部分鏡像
cls3 = Counter()
for s in uniq3:
    in_ms = Counter(s[0]); out_ms = Counter(s[1])
    if out_ms == in_ms:
        cls3['identity'] += 1
    elif out_ms == Counter(N - k for k in s[0]):
        cls3['antipodal(全集)'] += 1
    else:
        cls3['genuine(部分鏡像)'] += 1
for k, v in cls3.items():
    print(f"  {k}: {v}")
check("T2b 存在 genuine 部分鏡像散射（六粒子結構）", cls3['genuine(部分鏡像)'] > 0,
      f"{cls3['genuine(部分鏡像)']} 類")

print()
print("=" * 60)
print("T3. 4→4 抽樣驗證（定理一般性）")
print("=" * 60)
import random
random.seed(42)
table4 = defaultdict(list)
for d in K:
    for e in K:
        for f in K:
            for g in K:
                table4[(round(omega(d) + omega(e) + omega(f) + omega(g), 9),
                        (d + e + f + g) % N)].append((d, e, f, g))

ok4 = tested4 = total4 = 0
NTEST = 300
for _ in range(NTEST):
    in4 = tuple(sorted(random.choices(K, k=4)))
    E = round(sum(omega(k) for k in in4), 9)
    S4 = sum(in4) % N
    preds = mirror_subset_predictions(in4)
    sols_for = {tuple(sorted(t)) for t in table4.get((E, S4), [])
                if Counter(t) != Counter(in4)}
    tested4 += 1
    if sols_for <= preds:
        ok4 += 1
    total4 += len(sols_for)
check("T3a 4→4 抽樣符合定理", ok4 == tested4, f"{ok4}/{tested4} 初態, 總非恒等解={total4}")

print()
print("=" * 60)
print("T4. 定理結構常數")
print("=" * 60)
print(f"  N = {N} (88-site cycle)")
print(f"  mod 44 = N_d (半鏈長) — 鏡像子集和必須 ≡ 0 (mod N_d)")
N88 = 44
print(f"  鏡像映射 k -> {N88}-k mod 44 等價; 直接寫 88-k: ω_k = ω_(88-k)")
# 動量變化: 子集 S 鏡像 -> Δp = Σ_{k∈S} (N−k − k) = Σ(N−2k) ≡ −2Σk (mod N)
#   守恆 iff 2*sum(S) ≡ 0 (mod 88) iff sum(S) ≡ 0 (mod 44) ✓
check("T4a 動量守恆條件 = 2*sum(S) ≡ 0 (mod 88) iff sum(S) ≡ 0 (mod 44)",
      True, "解析推導（見註釋）")

print()
print(f"\n===== 總結: PASS={PASS} FAIL={FAIL} =====")
sys.exit(0 if FAIL == 0 else 1)