#!/usr/bin/env python3
"""
P6 工具 #2: 譜積↔log10 身份搜尋器
========================================================
問題(#2): M_comp = M_pl·10^-(1/γ₆−1/76); 1/76 有冇譜積出處?
         點解 log10 尺度出現「−1/76」加法修正?

方法: 事前定義 operator 集合 (子譜積、Chebyshev 商、det ratios、對數)
     → 全掃描 → 睇有冇組合 = 1/γ₆−1/76 或者 = 1/76
     密度/唯一性判準: 唔准事後揀組合

用法: python3 scripts/07_spectral_log_identity_searcher.py
"""
import math
from itertools import combinations

# ── K_Chain 基礎 ──
def gamma(n, N=88):
    return 4 * math.sin(n * math.pi / N) ** 2

G = {n: gamma(n) for n in range(1, 89)}

# ── 事前定義子譜集合 (operator 自然子集) ──
def subset(name, nlist):
    return name, nlist

SUBSETS = [
    subset("1..44", list(range(1, 45))),
    subset("45..88", list(range(45, 89))),
    subset("odd1..87", list(range(1, 88, 2))),
    subset("even1..88", list(range(2, 89, 2))),
    subset("n≡1 mod3", [n for n in range(1, 89) if n % 3 == 1]),
    subset("n≡2 mod3", [n for n in range(1, 89) if n % 3 == 2]),
    subset("n≡0 mod3", [n for n in range(1, 89) if n % 3 == 0]),
    subset("n≡1 mod4", [n for n in range(1, 89) if n % 4 == 1]),
    subset("n≡2 mod4", [n for n in range(1, 89) if n % 4 == 2]),
    subset("n≡3 mod4", [n for n in range(1, 89) if n % 4 == 3]),
    subset("n≡0 mod4", [n for n in range(1, 89) if n % 4 == 0]),
    subset("1..11", list(range(1, 12))),
    subset("12..22", list(range(12, 23))),
    subset("23..33", list(range(23, 34))),
    subset("34..44", list(range(34, 45))),
    subset("45..55", list(range(45, 56))),
    subset("56..66", list(range(56, 67))),
    subset("67..77", list(range(67, 78))),
    subset("78..88", list(range(78, 89))),
    subset("Lucas mod", [n for n in range(1, 89) if n in (1,3,4,7,11,18,29,47,76)]),
    subset("Fib mod", [n for n in range(1, 89) if n in (1,2,3,5,8,13,21,34,55)]),
    subset("mode6&mirror", [6, 82]),
    subset("4,5,6", [4, 5, 6]),
    subset("Nfull", list(range(1, 89))),
]

def prod_of(nlist):
    p = 1.0
    for n in nlist:
        p *= G[n]
    return p

def ln_prod(nlist):
    return math.log(prod_of(nlist))

# 目標值
TARGET = 1/G[6] - 1/76      # 0.5199774... 實際: 1/γ₆−1/76
TARGET76 = 1/76

print("="*78)
print("【1】單子譜 log10 積 / ln 積 / 商 掃描")
print("="*78)
print(f"目標: 1/γ₆−1/76 = {TARGET:.10f}   1/76 = {TARGET76:.10f}")

# 候選量: ln 積, log10 積, 商, 半 ln, 兩倍 ln
hits = []
for name, ns in SUBSETS:
    p = prod_of(ns)
    lp = math.log(p)
    l10 = math.log10(p)
    cands = {
        "lnP": lp, "lnP/2": lp/2, "2lnP": 2*lp,
        "log10P": l10, "-log10P": -l10,
        "1/lnP": 1/abs(lp) if lp else 0,
        "lnP/ln88": lp/math.log(88),
        "lnP/ln(88²)": lp/math.log(7744),
    }
    for cname, cv in cands.items():
        if cv == 0: continue
        dev_t = abs(cv - TARGET)/TARGET*100
        dev_76 = abs(cv - TARGET76)/TARGET76*100
        if dev_t < 1.0 or dev_76 < 1.0:
            hits.append((name, cname, cv, dev_t, dev_76))

hits.sort(key=lambda x: min(x[3], x[4]))
print(f"命中 (dev<1%): {len(hits)}")
for name, cname, cv, dt, d76 in hits[:20]:
    print(f"  {name:16s} {cname:8s} = {cv:.6f}  dev_T10 {dt:.4f}%  dev_76 {d76:.4f}%")

print()
print("="*78)
print("【2】雙子譜商 ln(P₁/P₂) 掃描")
print("="*78)
# 所有 (S₁,S₂) 對 → ln 商
pairs = []
names = [s[0] for s in SUBSETS]
prod = {s0: prod_of(s1) for s0, s1 in SUBSETS}
lnp = {s0: math.log(v) for s0, v in prod.items()}
hits2 = []
for i in range(len(names)):
    for j in range(len(names)):
        if i == j: continue
        a, b = names[i], names[j]
        L = lnp[a] - lnp[b]
        dev_t = abs(L - TARGET)/TARGET*100
        dev_76 = abs(L - TARGET76)/TARGET76*100
        if dev_t < 0.5 or dev_76 < 0.5:
            hits2.append((a, b, L, dev_t, dev_76))
hits2.sort(key=lambda x: min(x[3], x[4]))
print(f"命中 (dev<0.5%): {len(hits2)}")
for a, b, L, dt, d76 in hits2[:15]:
    print(f"  ln({a}/{b}) = {L:.6f}  dev_T10 {dt:.4f}%  dev_76 {d76:.4f}%")

print()
print("="*78)
print("【3】Chebyshev 身份驗證 + 擴展")
print("="*78)
# Π 2sin(πn/N) = N (n=1..N-1); γ = (2sin)²; Πγ = N²  (n=1..87)
prod_all = 1.0
for n in range(1, 88):
    prod_all *= 2*math.sin(n*math.pi/88)
print(f"Π 2sin(nπ/88), n=1..87 = {prod_all:.6f}  (理論 88)")
print(f"Π γₙ = {prod_all**2:.6f} (理論 7744)")
# 部分積: 移除 mode 6 pair
p_rem = prod_all**2 / (G[6]*G[82])
print(f"Π γₙ/(γ₆γ₈₂) = {p_rem:.6f}")
print(f"½ln(Π/Π_rem) = {math.log(prod_all**2/p_rem)/2:.8f}  (= ln(1/γ₆) 理論?)")
print(f"½ln(1/γ₆²)·log10 = {math.log10(1/G[6]**2)/2:.8f}")
print(f"1/γ₆−1/76 = {TARGET:.8f}")
print(f"log10(1/γ₆) = {math.log10(1/G[6]):.8f} (接近 0.7427)")
print(f"ln(1/γ₆) = {math.log(1/G[6]):.8f} (接近 1.7109)")

print()
print("="*78)
print("【4】Lucas/斐波那契係數 → 76 身份檢查")
print("="*78)
print(f"76 = L₉ (Lucas 9) = {76}")
print(f"76 = 88−12 = 88 − B·N_gen = 88 − 4×3")
print(f"76 = Σγ_odd − 12 = 88 − 12")
print(f"76 = Σγ(1..44) − 14 = 90 − 14 (14=2L₄)")
print(f"Σγ_odd(1..87) = {sum(G[n] for n in range(1,88,2)):.1f}  Σγ_even = {sum(G[n] for n in range(2,89,2)):.1f}")
print(f"Σγ(1..44) = {sum(G[n] for n in range(1,45)):.1f}  (=90, O212)")
print(f"Σγ(45..88) = {sum(G[n] for n in range(45,89)):.1f}")

print()
print("="*78)
print("【5】結論 (事前掃描判決)")
print("="*78)
print(f"""
  目標 1/γ₆−1/76 = {TARGET:.8f}
  掃描結果:
  - 單子譜 log/ln/商命中: {len(hits)} (全部列晒上面, 睇有冇真正 identity)
  - 雙子譜 ln 商命中: {len(hits2)}
  判準:
  - 如果命中部份係「Lucas/Fib mod 子譜」→ 可能有 operator 身份
  - 如果全部係 random 子譜 → 密度命中, 唔算閉合
""")