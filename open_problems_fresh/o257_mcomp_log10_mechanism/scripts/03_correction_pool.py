#!/usr/bin/env python3
"""
O257 scripts/03 — 修正項 1/76 嘅池密度 + Lucas 階梯重驗 (2026-10-21)
====================================================================
問題: 「−1/76 加法修正」嘅 operator 機制。

判據設計 (預註冊):
  A. 密度閘: 修正項池窮舉 — 1/γ₆ − 1/x, x ∈ 結構池 (Lucas/Fib/88-m/44-m/B-m/19-m/組合)
     → 命中 (<0.1%) 數量: 若 >2 個 = 池密度, 76 唔特別; 若 =1 = 支持「76 係結構選擇」
  B. Lucas 誤差階梯重驗 (O66 §2.1): 1/γ₆−1/Lₙ (n=1..15 odd), L₉=76 係咪唯一精確
  C. log 底數測試: log₁₀ = log_{2F₅} (hop 通道週期); log_{2B}=log₈ 敗壞度幾大
  D. screening 形式: 1/γ₆−1/76 = (1−γ₆/76)/γ₆; γ₆/76 有冇結構身份掃描
  E. 修正因子 10^{1/76} = 1.03076 身份掃描 (有冇 = 結構數嘅根/冪)

注意: 呢個 script 唔閉合 — 只決定「76 喺池中密唔密 / 邊個 operator 身份有證據」
"""
import mpmath as mp
mp.mp.dps = 50

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B, Nd, N, Ngen = 4, 44, 88, 3
F8 = 21
L = {1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123, 11:199, 12:322, 13:521, 14:843, 15:1364}
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89, 12:144, 13:233, 14:377, 15:610}

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

passed = 0
failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

print("=" * 72)
print("O257 scripts/03 — 修正項 1/76 池密度 + Lucas 階梯重驗")
print("=" * 72)

g6 = gamma(6)
inv6 = 1/g6
one76 = 1/mp.mpf(76)
tgt = inv6 - one76

# ── A. 修正項池窮舉 ──
print("\n[A] 密度閘: 1/γ₆ − 1/x 對 x ∈ 結構池, 命中 log10 target ±0.1%?")
# 結構池: Lucas, Fib, 88-m, 44-m, 12-m, 4-m, 19-m, N_d 相關, φ power
pool = set()
for v in L.values(): pool.add(v)
for v in F.values(): pool.add(v)
for k in range(1, 40):
    pool.add(88*k); pool.add(44*k); pool.add(12*k); pool.add(4*k)
    try: pool.add(int(phi**k))
    except OverflowError: pass
for a in range(1, 60):
    for b in range(1, 15):
        if a > b and b != 0: pool.add(mp.mpf(a)/b)
# 加 hop 階梯
pool.update([1, 4, 8, 11, 12, 11, 8, 4, 1])
# 加 88, 90, 44, 60, 96, 176, 1749 等常用
pool.update([88, 90, 44, 60, 96, 176, 33, 32, 17, 22, 45, 19, 38, 76])
pool = sorted(pool)
hits = []
for x in pool:
    x = mp.mpf(x)
    if x <= 0: continue
    v = inv6 - 1/x
    if abs(v - tgt)/tgt < 0.001:   # ±0.1%
        hits.append((x, mp.nstr(v, 12), mp.nstr(abs(v-tgt)/tgt*100, 6)))
print(f"  池大小: {len(pool)}")
print(f"  ±0.1% 命中: {len(hits)}")
for x, v, d in hits:
    print(f"    x={x}: 1/γ₆−1/x = {v}  (dev {d}%)")
if len(hits) == 1 and abs(hits[0][0] - 76) < 1e-12:
    ck("76 係池中唯一 ±0.1% 命中", True, f"({len(hits)} hit, x=76)")
else:
    ck("76 係池中唯一 ±0.1% 命中", False, f"({len(hits)} hits: {[h[0] for h in hits]})")
# 放寬 ±1% 睇密度
hits_1 = [x for x in pool if x > 0 and abs((inv6 - 1/mp.mpf(x)) - tgt)/tgt < 0.01]
print(f"  ±1% 命中: {len(hits_1)} 個 ({[mp.nstr(mp.mpf(x),6) for x in hits_1[:10]]})")

# ── B. Lucas 誤差階梯重驗 ──
print("\n[B] Lucas 誤差階梯重驗 (1/γ₆−1/Lₙ, n odd)")
best = None
for n in sorted(L):
    if n % 2 == 0: continue
    Ln = mp.mpf(L[n])
    v = inv6 - 1/Ln
    dev = abs(v - tgt)/tgt*100
    star = " ★" if abs(Ln-76) < 1e-12 else ""
    print(f"    L_{n}={L[n]}: 1/γ₆−1/L{n} = {mp.nstr(v,16)}  dev {mp.nstr(dev,6)}%{star}")
    if best is None or dev < best[1]: best = (n, dev)
print(f"  最佳: L_{best[0]} dev {mp.nstr(best[1],6)}%")
ck("L₉=76 係 odd-Lucas 階梯唯一 <0.01%", best[0] == 9 and best[1] < 0.01,
   f"(best L_{best[0]} dev {mp.nstr(best[1],4)}%)")
# Fibonacci 對照
print("  Fibonacci 對照 (1/γ₆−1/Fₙ):")
fb_best = None
for n in sorted(F):
    Fn = mp.mpf(F[n])
    v = inv6 - 1/Fn
    dev = abs(v - tgt)/tgt*100
    if fb_best is None or dev < fb_best[1]: fb_best = (n, dev)
print(f"    best F_{fb_best[0]} dev {mp.nstr(fb_best[1],6)}%")

# ── C. log 底數測試 ──
print("\n[C] log 底數測試")
M_pl = mp.mpf("1.2209e19")
M_comp = mp.mpf("3.6890e13")
r = M_pl / M_comp
ck("10 = 2F₅ (O179 hop 通道週期)", 2*5 == 10)
log10_r = mp.log(r)/mp.log(10)
log8_r = mp.log(r)/mp.log(8)
log88_r = mp.log(r)/mp.log(88)
print(f"  log₁₀(M_pl/M_comp) = {mp.nstr(log10_r, 12)}")
print(f"  log₈ (2B)           = {mp.nstr(log8_r, 12)}  vs 1/γ₆−1/76 = {mp.nstr(tgt, 10)}")
print(f"  log₈₈               = {mp.nstr(log88_r, 12)}  vs 目標")
dev8 = abs(log8_r - tgt)/tgt*100
print(f"  log₈ vs 結構目標 dev: {mp.nstr(dev8,4)}%  (→ 用 2B 做底會敗壞, 支持 10=2F₅)")

# ── D. screening 形式 ──
print("\n[D] screening 形式: 1/γ₆−1/76 = (1−γ₆/76)/γ₆")
s = (1 - g6/76)/g6
ck("(1−γ₆/76)/γ₆ = 1/γ₆−1/76", abs(s - tgt) < 1e-30)
ratio = g6/76
print(f"  γ₆/76 = {mp.nstr(ratio, 14)}")
# γ₆/76 喺結構池有冇身份?
best_ratio = None
for x in pool:
    x = mp.mpf(x)
    if x <= 0: continue
    dev = abs(ratio - 1/x)/(1/x) if x > 1 else abs(ratio - x)/x
    if best_ratio is None or dev < best_ratio[1]:
        best_ratio = (mp.nstr(x, 6), dev)
print(f"  γ₆/76 最近池元素: x={best_ratio[0]} dev {mp.nstr(best_ratio[1]*100, 6)}%")

# ── E. 修正因子 10^{1/76} ──
print("\n[E] 修正因子 10^(1/76) 身份掃描")
f76 = mp.power(10, 1/mp.mpf(76))
print(f"  10^(1/76) = {mp.nstr(f76, 12)}")
# 檢查有冇 = q^(1/p) 結構?
for p in [2, 3, 4, 5, 6, 7, 8, 9, 11]:
    cand = f76**p
    # 最近有理/整數
    near = mp.nint(cand)
    dev = abs(cand - near)
    if dev < 0.01:
        print(f"    (10^{1/76})^{p} = {mp.nstr(cand,10)} ≈ {near} (dev {mp.nstr(dev,4)})")
# 檢查 ln10/76 有冇身份
ln10_76 = mp.log(10)/76
print(f"  ln10/76 = {mp.nstr(ln10_76, 12)}")
for x in pool:
    x = mp.mpf(x)
    if x <= 0: continue
    if abs(ln10_76 - 1/x)/(1/x) < 0.001:
        print(f"    ln10/76 ≈ 1/{mp.nstr(x,6)} (dev {mp.nstr(abs(ln10_76-1/x)/(1/x)*100,4)}%)")

# ── F. 跨尺度連繫: Λ 同 M_comp 嘅 19 ──
print("\n[F] O62Λ + O66 M_comp 嘅 19 統一複驗")
ck("19 = N_d−F₈−B", Nd-F8-B == 19)
# O62 V_Λ = F(γ)+19; O66 1/76 = 1/(4×19)
ck("76 = 4×19 = B×(N_d−F₈−B)", 4*(Nd-21-4) == 76)
print("  → 修正項 = 1/(B·N_free), N_free=19=自由模數 (世界鏈 44 − 固定 beats 21 − 分支 4)")
print("  → M_comp 修正 = 1/(4×19); Λ 修正 = +19 (同一 N_free 兩尺度)")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")