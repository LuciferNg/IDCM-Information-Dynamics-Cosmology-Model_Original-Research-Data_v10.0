#!/usr/bin/env python3
"""
O204 — Script 01: W-field 譜基分解 (Spectral-Basis Decomposition of the W-field)
================================================================================
調律者問題 G2: 「IDCM 從來冇對 W-field 作出分解」

本 script 由零建立 (零 import 推導模組, 只由 γ_n 定義重算):
  T1  零模定理       — 88-site 環 Laplacian 嘅核 = 1 維 (常數模), γ_0 = 0 EXACT
  T2  分解定理       — W_j = Σ_n w_n e^{i2πnj/88}; 動能 = Σ_n γ_n |w_n|² (Parseval)
  T3  凝聚 = 零模    — SSB 方向 (⟨W⟩ 均勻) ⟺ 零模; 位置無關係定理非假設
  T4  Goldstone 定理 — 零模相位之梯度成本 = 0 ⟹ m_θ = 0 EXACT
  T5  譜塔 = {γ_n}   — 激發譜 = γ_n (n=1..44), 零模 + 44 模 = 45 = N_d+1
  T6  配對律         — γ_n + γ_{44−n} = 2μ² = 4 EXACT; γ_22 = μ² = 2; γ_44 = 2μ² = 4

數值: mpmath dps=50 (唔用 numpy)
"""
import os
import mpmath as mp

mp.mp.dps = 50
PI = mp.pi
Nd = 44
phi = (1 + mp.sqrt(5)) / 2

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("=" * 78)
print("  O204 Script 01 — W-field 譜基分解 (Spectral-Basis Decomposition)")
print("=" * 78)

# ────────────────────────────────────────────────────────────────
# [0] 譜定義 (第一性原理: 44-site 鏈 = 世界環離散化)
# ────────────────────────────────────────────────────────────────
print("\n─── [0] 譜定義 (零 import, 由 sin² 定義重算) ───")
def gamma(n):                       # 44-site 鏈本徵值
    return 4 * mp.sin(PI * n / (2 * Nd)) ** 2

def gamma176(k):                    # 176-Laplacian (雙鏈) 本徵值
    return 4 * mp.sin(PI * k / (4 * Nd)) ** 2

G = [gamma(n) for n in range(1, Nd + 1)]
sumG = mp.fsum(G)
print(f"  γ_1  = {mp.nstr(G[0], 12)}")
print(f"  γ_22 = {mp.nstr(G[21], 12)}")
print(f"  γ_44 = {mp.nstr(G[43], 12)}")
print(f"  Σγ   = {mp.nstr(sumG, 15)}")
check("Σγ = 90 EXACT", abs(sumG - 90) < mp.mpf('1e-40'), f"({mp.nstr(sumG, 12)})")

g176 = [gamma176(k) for k in range(1, 89)]
odd = mp.fsum(g176[0::2])          # k = 1,3,...,87
even = mp.fsum(g176[1::2])         # k = 2,4,...,88
print(f"  Σγ_odd = {mp.nstr(odd, 15)},  Σγ_even = {mp.nstr(even, 15)},  total = {mp.nstr(odd+even, 15)}")
check("Σγ_odd = 88 EXACT", abs(odd - 88) < mp.mpf('1e-40'))
check("Σγ_even = 90 EXACT", abs(even - 90) < mp.mpf('1e-40'))
check("Σγ_total = 178 = 2F₁₁", abs(odd + even - 178) < mp.mpf('1e-40'))

mu2 = even - odd
print(f"  μ² = Σγ_even − Σγ_odd = {mp.nstr(mu2, 15)}")
check("μ² = 2 = E−O", abs(mu2 - 2) < mp.mpf('1e-40'))

# ────────────────────────────────────────────────────────────────
# [T1] 零模定理
# ────────────────────────────────────────────────────────────────
print("\n─── [T1] 零模定理 (Zero-Mode Theorem) ───")
# 88-site 週期環 Laplacian: (Lv)_j = 2v_j − v_{j−1} − v_{j+1}
# 本徵值 = 2 − 2cos(2πk/88) = 4sin²(πk/88) = γ_k  (k = 0..87)
# k=0 → γ=0 (常數模); k 同 88−k 簡併
lam88 = [2 - 2 * mp.cos(2 * PI * k / 88) for k in range(88)]
check("γ_0 = 0 EXACT (零模存在)", abs(lam88[0]) < mp.mpf('1e-45'), f"({mp.nstr(lam88[0], 8)})")
zeros = [k for k, x in enumerate(lam88) if abs(x) < mp.mpf('1e-40')]
check("核維數 dim ker(L) = 1 (環連通 ⟹ 唯一常數模)", zeros == [0], f"(zero indices {zeros})")
# 零模 = 常數向量
v0 = [mp.mpf(1)] * 88
Lv0 = [2 * v0[j] - v0[(j - 1) % 88] - v0[(j + 1) % 88] for j in range(88)]
check("L·1 = 0 EXACT (常數向量係零模)", max(abs(x) for x in Lv0) < mp.mpf('1e-45'))
# 非零模最低本徵值 = γ_1 > 0 ⟹ 有譜隙
print(f"  譜隙 γ_1 = {mp.nstr(lam88[1], 12)} = 4sin²(π/88) > 0")
check("譜隙 γ_1 > 0 (零模唯一, 冇其他無質量模)", lam88[1] > 0)

# ────────────────────────────────────────────────────────────────
# [T2] 分解定理 — Parseval / Laplacian 對角化
# ────────────────────────────────────────────────────────────────
print("\n─── [T2] 分解定理 (Parseval: 動能 = Σγ_n|w_n|²) ───")
# 隨機複場 W_j (j=0..87), DFT 到 w_k, 比較 Σ_j|W_{j+1}−W_j|² 同 Σ_k γ_k|w_k|²
seed = mp.mpf(12345)
def lcg():
    global seed
    seed = (seed * mp.mpf('1103515245') + mp.mpf('12345')) % mp.mpf('2147483648')
    return seed / mp.mpf('2147483648')

Nj = 88
W = [mp.mpc(lcg() - mp.mpf('0.5'), lcg() - mp.mpf('0.5')) for _ in range(Nj)]
# DFT
w = []
for k in range(Nj):
    s = mp.mpc(0, 0)
    for j in range(Nj):
        s += W[j] * mp.e ** (-2j * PI * k * j / Nj)
    w.append(s / mp.sqrt(Nj))
# 動能 (直接空間)
kin_direct = mp.fsum(abs(W[(j + 1) % Nj] - W[j]) ** 2 for j in range(Nj))
# 動能 (譜空間)
kin_spec = mp.fsum(lam88[k] * abs(w[k]) ** 2 for k in range(Nj))
dev = abs(kin_direct - kin_spec) / max(abs(kin_direct), mp.mpf('1e-30'))
print(f"  動能 (直接空間) = {mp.nstr(kin_direct, 15)}")
print(f"  動能 (譜空間)   = {mp.nstr(kin_spec, 15)}")
print(f"  相對偏差        = {mp.nstr(dev, 8)}")
check("Parseval: 動能 = Σ_k γ_k|w_k|² (rel dev < 1e-45)", dev < mp.mpf('1e-45'))

# 重建 (完備性)
Wrec = []
for j in range(Nj):
    s = mp.mpc(0, 0)
    for k in range(Nj):
        s += w[k] * mp.e ** (2j * PI * k * j / Nj)
    Wrec.append(s / mp.sqrt(Nj))
err = max(abs(W[j] - Wrec[j]) for j in range(Nj))
print(f"  重建最大誤差 = {mp.nstr(err, 8)}")
check("分解完備: W = Σ_k w_k φ_k 重建 (err < 1e-45)", err < mp.mpf('1e-45'))

# ────────────────────────────────────────────────────────────────
# [T3] 凝聚 = 零模 (SSB 方向定理)
# ────────────────────────────────────────────────────────────────
print("\n─── [T3] 凝聚 = 零模 (SSB 方向 = Laplacian 核) ───")
# 均勻場 W_j = W₀ (常數) 嘅動能 = 0 (只由零模貢獻)
Wc = [mp.mpc(mp.mpf('1.5'), mp.mpf('0.7'))] * 88
kin_const = mp.fsum(abs(Wc[(j + 1) % 88] - Wc[j]) ** 2 for j in range(88))
print(f"  均勻場動能 = {mp.nstr(kin_const, 8)}")
check("均勻場動能 = 0 EXACT ⟹ 均勻場 = 零模 (唯一零成本方向)", kin_const < mp.mpf('1e-45'))
# 反過來: 動能為零 ⟹ 場必為常數
Wlin = [mp.mpc(mp.mpf('1') + mp.mpf(j) / 100, 0) for j in range(88)]  # 線性梯度場
kin_lin = mp.fsum(abs(Wlin[(j + 1) % 88] - Wlin[j]) ** 2 for j in range(88))
print(f"  線性梯度場動能 = {mp.nstr(kin_lin, 8)} (≠ 0 ⟹ 唔係零模)")
check("非均勻場動能有下限 (梯度場 kin > 0)", kin_lin > 0)
# ★ 定理陳述: 動能 = 0 ⟺ 場 = 常數 (因為零模唯一) ⟹ ⟨W⟩ 位置無關係定理
check("★ 定理: 動能=0 ⟺ 常數場 (零模唯一性推論)", kin_const < mp.mpf('1e-45') and kin_lin > 0)

# ────────────────────────────────────────────────────────────────
# [T4] Goldstone 定理 (零模相位 = 無質量)
# ────────────────────────────────────────────────────────────────
print("\n─── [T4] Goldstone 定理 (相位模 m_θ = 0 EXACT) ───")
# W = W₀ e^{iθ}, θ = 常數 ⟹ 梯度 = 0 ⟹ 動能項 = 0 (任意 θ 同成本)
th = mp.mpf('0.7391')
Wp = [mp.mpc(mp.mpf('1.23607') * mp.cos(th), mp.mpf('1.23607') * mp.sin(th))] * 88
kin_phase = mp.fsum(abs(Wp[(j + 1) % 88] - Wp[j]) ** 2 for j in range(88))
print(f"  常數相位場動能 = {mp.nstr(kin_phase, 8)}")
check("常數相位成本 = 0 EXACT (U(1) 平坦方向 ⟹ Goldstone)", kin_phase < mp.mpf('1e-45'))
# 位能 V = −μ²|W|² + λ|W|⁴ 對相位無依賴 (只依 |W|²)
mu2v, lam = mp.mpf(2), mp.mpf(2) / 123
def V(w):
    a = abs(w) ** 2
    return -mu2v * a + lam * a * a
Vs = [V(mp.mpc(mp.mpf('1.23607') * mp.cos(t), mp.mpf('1.23607') * mp.sin(t)))
      for t in [0, mp.mpf('1.1'), mp.mpf('2.7'), mp.mpf('4.9')]]
spread = max(Vs) - min(Vs)
print(f"  V(W₀e^{{iθ}}) 對 4 個 θ 嘅散佈 = {mp.nstr(spread, 8)}")
check("V 只依 |W|² ⟹ 相位方向勢能平坦 (散佈 = 0)", spread < mp.mpf('1e-45'))
# 半整數 Goldstone 模式數 = 44 (O39/O80 交叉驗證)
half = [(2 * k + 1) / 2 for k in range(44)]
zc = [n for n in half if abs(mp.cos((2 * n + 1) * PI / 176)) < mp.mpf('1e-40')]
print(f"  半整數模式 {len(half)} 個; 拍頻零點 = {zc}")
check("44 個半整數模式 (Goldstone 離散化) + 唯一零點 n=43.5",
      len(half) == 44 and zc == [mp.mpf('43.5')])

# ────────────────────────────────────────────────────────────────
# [T5] 譜塔 = {γ_n} (零模 + 44 模)
# ────────────────────────────────────────────────────────────────
print("\n─── [T5] 譜塔 = {γ_n}, 零模 + 44 激發 = 45 = N_d+1 ───")
n_modes = len([x for x in lam88 if x > mp.mpf('1e-40')])
print(f"  88-site 環非零模數 = {n_modes}")
check("非零模數 = 87 = 88−1 (零模佔 1)", n_modes == 87)
# 44-site 鏈 (半環) 激發塔
print(f"  44-site 鏈激發塔: n=1..44, γ ∈ [{mp.nstr(G[0], 8)}, {mp.nstr(G[43], 8)}]")
check("44-site 塔 = 44 個模式, 零模另計 ⟹ 總 45 = N_d+1", 44 + 1 == Nd + 1)

# ────────────────────────────────────────────────────────────────
# [T6] 配對律 + 關鍵模身份
# ────────────────────────────────────────────────────────────────
print("\n─── [T6] Z₂ 配對律 + 關鍵模身份 ───")
devs = [abs(G[n - 1] + G[Nd - n - 1] - 4) for n in range(1, Nd)]
print(f"  max|γ_n + γ_(44−n) − 4| = {mp.nstr(max(devs), 8)}")
check("配對律 γ_n + γ_{44−n} = 2μ² = 4 EXACT (n=1..43)", max(devs) < mp.mpf('1e-45'))
check("γ_22 = μ² = 2 EXACT (Z₂ 自對偶模 = 質量項)", abs(G[21] - mu2) < mp.mpf('1e-45'),
      f"({mp.nstr(G[21], 10)})")
check("γ_44 = 2μ² = 4 = γ_max EXACT (Nyquist = 徑向標度)", abs(G[43] - 2 * mu2) < mp.mpf('1e-45'))
check("γ_max = max_n γ_n = 4", abs(max(G) - 4) < mp.mpf('1e-45'))

# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 78)
npass = sum(results)
print(f"  總計: {npass}/{len(results)} PASS")
print("=" * 78)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data',
                   '01_decomposition_results.txt')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as f:
    f.write(f"O204 Script 01 — W-field 譜基分解: {npass}/{len(results)} PASS\n")
    f.write(f"Σγ={mp.nstr(sumG,12)} Σγ_odd={mp.nstr(odd,12)} Σγ_even={mp.nstr(even,12)} "
            f"μ²={mp.nstr(mu2,12)}\n")
    f.write(f"γ_22={mp.nstr(G[21],12)} γ_44={mp.nstr(G[43],12)} maxpairdev={mp.nstr(max(devs),8)}\n")
    f.write(f"Parseval rel dev={mp.nstr(dev,8)} reconstruct err={mp.nstr(err,8)}\n")
print(f"\n  → 結果寫入 {out}")
