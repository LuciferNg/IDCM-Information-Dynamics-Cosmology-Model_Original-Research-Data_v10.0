#!/usr/bin/env python3
"""
O257 scripts/02 — log10 修正機制候選探索 (2026-10-21)
=====================================================
問題: 1/γ₆−1/76 嘅「−1/76 加法修正」(log10 尺度) operator 機制。

本 script 探索候選(非閉合 — 只係攞數值事實):
  A. 76 同 γ₆ 嘅交叉乘積: γ₆×76, 76/γ₆, 1/(γ₆·76), 76−γ₆
     → 76/γ₆ ≈ 420.5 = 29²/2? (L₇ 近命中 vs 巧合)
  B. 對偶 index 鏈: mode 6 →×2→ 12 (176-chain) →(N−n)→ 76 (88-chain mirror)
     → γ₆(88) = γ₁₂(176); 12 = hop_max; 76 = 88−12
     測試普適性: 對任意 n∈1..44, D(n)=88−2n 有冇 Lucas/結構身份?
  C. 76 = B×19 operator: 1/76 = 1/(B·(N_d−F₈−B)) = 1/(4×19)
  D. 譜和恆等: Σ_{k=1}^{87} 1/γ_k (176-chain) 等 有冇結構
  E. 1/γ_n − 1/(88−2n) 對 n=1..44 掃描 — 睇 L₉=76 是否唯一「結構身份」修正

判據 (預註冊):
  - 全部 mpmath 高精度; 近命中標記 ⚠(候選) 唔當閉合
  - 普適性測試: 對偶鏈形式若係真 operator, 應對其他 mode 出現結構身份
  - 密度: 76 喺 n=1..44 嘅 88−2n 池中只係其中一個值, 要睇「88−2n ∈ 結構池」密度
"""
import mpmath as mp
mp.mp.dps = 50

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B, Nd, N, Ngen = 4, 44, 88, 3
F8 = 21
L = {1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123, 11:199, 12:322}
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89, 12:144, 13:233}

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

def is_structure_num(x):
    """粗略結構池: |x−L_k|, |x−F_k|, |x−88k|, |x−44k|, |x−φ^k| < 1e-10"""
    for k, v in L.items():
        if abs(x - v) < 1e-9: return f"L{k}={v}"
    for k, v in F.items():
        if abs(x - v) < 1e-9: return f"F{k}={v}"
    for k in range(-20, 21):
        if abs(x - phi**k) < 1e-9: return f"φ^{k}"
    for k in range(1, 12):
        if abs(x - 88*k) < 1e-9: return f"88×{k}"
        if abs(x - 44*k) < 1e-9: return f"44×{k}"
    return None

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
print("O257 scripts/02 — log10 修正機制候選探索")
print("=" * 72)

g6 = gamma(6)
inv6 = 1/g6
tgt = inv6 - 1/mp.mpf(76)

# ── A. 交叉乘積 ──
print("\n[A] 76 同 γ₆ 交叉乘積")
print(f"  γ₆×76      = {mp.nstr(g6*76, 12)}")
print(f"  76/γ₆      = {mp.nstr(76/g6, 12)}   (420.5 = 29²/2? 差 {mp.nstr(abs(76/g6 - 841/2), 4)})")
print(f"  1/(γ₆·76)  = {mp.nstr(1/(g6*76), 12)}")
print(f"  76−γ₆      = {mp.nstr(mp.mpf(76)-g6, 12)}")
print(f"  1/γ₆×76    = {mp.nstr(inv6*76, 12)}")
ratio = 76/g6
for target_val, name in [(mp.mpf(841)/2, "29²/2"), (mp.mpf(420), "420"), (mp.mpf(421), "421")]:
    dev = abs(ratio - target_val)/target_val
    print(f"  76/γ₆ vs {name}: dev {mp.nstr(dev*100, 6)}%")
# γ₆ 喺結構池?? (γ₆ = 0.1807...)
print(f"  γ₆ 結構身份? {is_structure_num(g6) or '無'}")
print(f"  1/γ₆ 結構身份? {is_structure_num(inv6) or '無'}")

# ── B. 對偶 index 鏈 ──
print("\n[B] 對偶 index 鏈: 6 →×2→ 12 (176-chain) →(N−n)→ 76 (88 mirror)")
print("     γ₆(88) = γ₁₂(176);  12 = hop_max;  76 = 88−12")
ck("γ₆(88) = γ₁₂(176)", abs(gamma(12,176) - g6) < 1e-15)
ck("hop_max = 12 = 2×6 = B×N_gen", 2*6 == 12 == B*Ngen)
ck("76 = 88 − 12 = N − 2n₆", 88-12 == 76)
# γ₁₂(88) mirror = γ₇₆(88)
ck("γ₁₂(88) = γ₇₆(88) (mirror 恒等)", abs(gamma(12) - gamma(76)) < 1e-15)
print(f"  γ₁₂(88) = γ₇₆(88) = {mp.nstr(gamma(12), 10)} (1/γ₁₂ = {mp.nstr(1/gamma(12), 8)})")
# 普適性: D(n) = 88−2n 嘅結構身份密度
print("\n  D(n) = 88−2n, n=1..44 — 邊啲係結構數:")
hits = []
for n in range(1, 45):
    Dn = 88 - 2*n
    sid = is_structure_num(mp.mpf(Dn))
    if sid:
        hits.append((n, Dn, sid))
        print(f"    n={n:2d}: D={Dn:3d} → {sid}")
print(f"  命中 {len(hits)}/44 個 (全部偶數池密度)")
# 1/γ_n 修正形式: 1/γ_n − 1/D(n) 有冇對 n≠6 出現佢自己嘅「M_comp-like」?
print("\n  1/γ_n − 1/(88−2n) 掃描 (n=1..44):")
for n in range(1, 45):
    Dn = 88 - 2*n
    if Dn <= 0: continue
    v = 1/gamma(n) - 1/mp.mpf(Dn)
    if n in (6, 12, 22, 33, 44) or abs(v - tgt) < 1e-6:
        print(f"    n={n:2d}: 1/γ_n−1/({Dn:3d}) = {mp.nstr(v, 14)}")

# ── C. 76 = B×19 ──
print("\n[C] 76 = B×19 operator")
n19 = Nd - F8 - B
ck("19 = N_d−F₈−B", n19 == 19)
ck("76 = B×(N_d−F₈−B)", B*n19 == 76)
ck("1/76 = 1/(B×19)", 1/mp.mpf(B*n19) == 1/mp.mpf(76))
print(f"  O62 Λ V_Λ = F(γ)+19 — 同一 19 喺兩尺度 (O62-O66 統一)")

# ── D. 譜和恆等 ──
print("\n[D] 譜和恆等 (176-chain csc² 全譜)")
# Σ_{k=1}^{87} csc²(kπ/88) = (88²−1)/3 (標準恆等, N=88 odd)
sum_csc88 = sum(1/mp.sin(k*mp.pi/88)**2 for k in range(1, 88))
print("  Σ 1/sin²(kπ/88), k=1..87 = " + mp.nstr(sum_csc88, 10) + f"  (理論 (88²−1)/3 = {(88*88-1)//3})")
ck("csc² 全譜恆等 (88²−1)/3", abs(sum_csc88 - (88*88-1)/3) < 1e-8)
sum_inv_gamma_88 = sum(1/gamma(k) for k in range(1, 88))   # k=88 係 Nyquist γ=0, 剔除
print("  Σ 1/γ_k, k=1..87 = " + mp.nstr(sum_inv_gamma_88, 10))
sum_inv_gamma_176 = sum(1/gamma(k, 176) for k in range(1, 89))
print("  Σ 1/γ'_k(176), k=1..88 = " + mp.nstr(sum_inv_gamma_176, 10))
# 部分和: 1/γ₆ − 1/76 等於邊啲部分和嘅差? (k=88 剔除)
print("  部分和 1/γ 差:")
for a, b in [(1, 6), (6, 7), (6, 12), (5, 6), (12, 88), (6, 88)]:
    if b >= 88:
        sa = sum(1/gamma(k) for k in range(a, 88))
    else:
        sa = sum(1/gamma(k) for k in range(a, b+1))
    print(f"    Σ_{a}..{b} 1/γ = {mp.nstr(sa, 10)}  (vs tgt {mp.nstr(tgt, 10)})")

# ── E. 修正項 1/76 可否由 1/γ 子譜和 (唔含 log) 表示? ──
print("\n[E] 1/76 可否由 1/γ 子譜和 (唔含 log) 表示?")
# 1/γ_k 對大 k 細, 嘗試 odd/even/late 子譜 (k=88 剔除)
for name, ns in [
    ("k=44..87", range(44, 88)),
    ("k=66..87", range(66, 88)),
    ("k=76..87", range(76, 88)),
    ("k=1..87 even", range(2, 88, 2)),
    ("k=1..87 odd", range(1, 88, 2)),
]:
    s = sum(1/gamma(k) for k in ns)
    print(f"    Σ 1/γ ({name}) = {mp.nstr(s, 10)}")
# 1/76 = 0.0131579; 邊度有 0.013 級嘅值?
print("  1/γ_k ≈ 1/76 嘅 k (γ_k ≈ 76? 唔可能 γ≤4) — 修正項唔係單譜值")

# ── F. log10 尺度嘅「加法修正」=「乘 10^{1/76}」──
print("\n[F] 指數加法 = 乘因子")
f76 = mp.power(10, 1/mp.mpf(76))
print(f"  10^(1/76) = {mp.nstr(f76, 12)}")
print(f"  = e^(ln10/76) = e^{mp.nstr(mp.log(10)/76, 10)}")
# 100^(1/76)? 88^(1/76)?
print(f"  88^(1/76)  = {mp.nstr(mp.power(88, 1/mp.mpf(76)), 10)}")
print(f"  同 1+1/76 比較: {mp.nstr(1+1/mp.mpf(76), 10)}")

# ── G. ★ 關鍵: 1/γ₆−1/76 vs 76 嘅「加法定義」──
print("\n[G] 重寫: (76/γ₆ − 1)/76")
print(f"  76/γ₆ − 1 = {mp.nstr(76/g6 - 1, 12)}")
print(f"  (76/γ₆ − 1)/76 = {mp.nstr((76/g6 - 1)/76, 16)}")
ck("(76/γ₆−1)/76 = 1/γ₆−1/76 (代數恒等)", abs((76/g6-1)/76 - tgt) < 1e-30)
# 76/γ₆ − 1 有冇結構身份?
q = 76/g6 - 1
print(f"  76/γ₆ − 1 結構身份? {is_structure_num(q) or '無'}  (419.50...?)")
print(f"  419.5 = 29²/2? {mp.nstr(abs(q-841/2), 6)}")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")