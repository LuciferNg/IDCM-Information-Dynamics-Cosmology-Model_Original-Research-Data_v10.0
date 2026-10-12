#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 05 — 原子層連續過渡: 幻數離散骨架 + λ(x) 連續化 (判據預註冊)

調律者 2026-10-12: 「原子層不是複合投影就是單質投影，連續過渡公式應該在k-tree找」
scripts/04 已否決 K_Tree 池層面 (8/8) ⟹ 本 script 測兩樣未測:
  A. 原子層離散骨架 = 核幻數 {2,8,20,28,50,82,126} vs K_Tree 擴張結構池
     (幻數係「連續結合能曲線」嘅離散對立面 — 調律者「連續幻覺=離散骨架」框架)
  B. 連續過渡公式 = λ_k 譜連續化 λ(x) = 4sin²(πx/68): 對 E_bind(He4)/4 或
     E_bind/D2 位置掃描 — 「過渡」= 由 k (離散 level) 到 A (質量數連續)

判據 (預註冊, 凍結):
  G1 幻數池密度: magic = {2,8,20,28,50,82,126} 對 K_Tree 擴張池 (含 33,66,68,88,
     90,176,134,42,55,34,17,22,L_n,F_n,B 冪,φ 冪,λ_k,Σλ 部分和) 掃命中
     MC null: 隨機 7 數 (log-uniform) 計同池命中, N=20000, 窗口 5%
     pass: ≥5/7 命中 且 MC z≥5; 唔係就「幻數唔喺 K_Tree 結構池」
  G2 λ(x) 連續化: λ(x)=4sin²(πx/68), x 連續 — 對比 E_bind/A 曲線喺 A∈[1,33]
     (K_Tree level 範圍內): 只報 |λ(A)·M₀ − E_bind/A(A)| 偏差表, 唔預設命中
  G3 126 = 3×42 = N_gen×2F₈ 數字學閘: composite depth-2 命中率 (2-5 冪組合)
     隨機整數撞 3×42 形式嘅概率 — 防把普通組合當結構
  G4 ★ 過渡公式候選: E_bind(He4) = 28.2957 MeV 本身喺 K_Tree 池有冇身份:
     28.2957/M₀ = 1.0141; 對 68/66=1.0303, 68/67, 176/176... 最近候選報告

K_Tree 結構數 (O155/O157 正典):
  33 = K_tree, 66 = Σλ = 2K_tree, 68 = 2F₉ = B·F_proj, 176 = 66⊕68⊕42
  42 = 2F₈ = N_d⁻ (觀察者扇區), 134 = V_geom = 66+68, 88 = K_tree+F₁₀
  17 = F_proj, 22 = 2L₅, 34 = F₉, 55 = F₁₀
"""
import math
import numpy as np

MAGIC = {2, 8, 20, 28, 50, 82, 126}
M0 = 27.900915
Eb_He4 = 28.2957
EB_CURVE = {1: 0.0, 2: 1.1123, 4: 7.0739, 12: 7.6801, 16: 7.9762,
            56: 8.7903, 100: 8.4700, 208: 7.8500, 238: 7.5700}

phi = (1 + math.sqrt(5)) / 2
lam = [4 * math.sin(k * math.pi / 68) ** 2 for k in range(1, 34)]

# K_Tree 擴張池 (凍結)
pool = set()
pool |= {33, 66, 68, 88, 90, 176, 134, 42, 55, 34, 17, 22, 4, 16, 36, 32, 44, 61.5, 123}
pool |= {2, 1, 3, 7, 11, 18, 29, 47, 76, 199, 322, 521, 843, 1364}          # Lucas
pool |= {1, 5, 8, 13, 21, 89, 144, 233, 377, 610, 987}                     # Fib
pool |= {4 ** p for p in range(-3, 6)}                                     # B 冪
pool |= {phi ** q for q in range(-8, 12)}
pool |= set(lam)
s = 0.0
for v in lam:
    s += v
    pool.add(s)                                                            # Σλ 部分和
pool |= {ki / 88 for ki in range(1, 89)}
pool.discard(0.0)
pool_arr = np.array(sorted(pool))

print("=" * 78)
print("G1  核幻數 {2,8,20,28,50,82,126} vs K_Tree 擴張池 (%d 候選, 5%% 窗)" % len(pool_arr))
print("=" * 78)
hits = []
for m in MAGIC:
    dev = np.abs(pool_arr / m - 1.0)
    j = int(np.argmin(dev))
    ok = dev[j] < 0.05
    hits.append(ok)
    print("  幻數 %3d: 最近 %-12g dev=%6.3f%%  %s" % (
        m, pool_arr[j], dev[j] * 100, "✔ 命中" if ok else "✗"))
rng = np.random.default_rng(20261012)
null_hits = np.zeros(20000)
for i in range(20000):
    r7 = np.exp(rng.uniform(math.log(1.0), math.log(400.0), size=7))
    c = 0
    for r in r7:
        if np.min(np.abs(pool_arr / r - 1.0)) < 0.05:
            c += 1
    null_hits[i] = c
n_hit = sum(hits)
z = (n_hit - null_hits.mean()) / null_hits.std()
print("  命中 %d/7   (MC null: mean=%.2f std=%.2f)  z=%.2f ⟹ %s" % (
    n_hit, null_hits.mean(), null_hits.std(), z,
    "PASS" if n_hit >= 5 and z >= 5 else "FAIL"))

print()
print("=" * 78)
print("G2  λ(x) 連續化 4sin²(πx/68)  對 E_bind/A 曲線 (A ∈ K_Tree 範圍 1..33)")
print("=" * 78)
print("  A | λ(A)     | λ(A)·M₀ (MeV) | E_bind/A (MeV) | dev")
for A in [1, 2, 3, 4, 5, 6, 8, 12, 16, 20, 28, 33]:
    lA = 4 * math.sin(math.pi * A / 68) ** 2
    pred = lA * M0
    if A in EB_CURVE and EB_CURVE[A] > 0:
        d = abs(pred / EB_CURVE[A] - 1.0) * 100
        print("  %3d | %8.5f | %12.3f | %14.4f | %7.2f%%" % (A, lA, pred, EB_CURVE[A], d))
    elif A in EB_CURVE:
        print("  %3d | %8.5f | %12.3f | %14s |   —(E_bind=0)" % (A, lA, pred, EB_CURVE[A]))
    else:
        print("  %3d | %8.5f | %12.3f | %14s |" % (A, lA, pred, "—"))

print()
print("=" * 78)
print("G3  126 = 3×42 = N_gen×2F₈ 數字學閘 (防普通組合當結構)")
print("=" * 78)
# depth-2: 隨機數 n, n 可分解嘅冪組合數目 vs 結構數 126
rng2 = np.random.default_rng(777)
cnt_126 = 0
cnt_rand = 0
N = 20000
for _ in range(N):
    n = rng2.integers(1, 200)
    hits_n = 0
    for a in range(1, 13):
        for b in range(1, 13):
            if a * b == n:
                hits_n += 1
    if n == 126:
        cnt_126 = hits_n
    elif hits_n >= cnt_126:
        cnt_rand += 1
print("126 嘅 depth-2 因數組合數 = %d" % cnt_126)
print("隨機 n∈[1,200] 有 ≥ 同量因數組合嘅比例 = %.4f" % (cnt_rand / N))
print("(126 = 3×42 冇更深結構; 126 只係多因數合成數 ⟹ 唔報結構)")

print()
print("=" * 78)
print("G4  E_bind(He4) = 28.2957 MeV 喺 K_Tree 擴張池嘅最近身份")
print("=" * 78)
r = Eb_He4 / M0
devs = np.abs(pool_arr / r - 1.0)
i = int(np.argmin(devs))
print("E_bind(He4)/M₀ = %.5f   最近候選 = %g   dev = %.3f%%%s" % (
    r, pool_arr[i], devs[i] * 100, "  <-- 5% 窗內" if devs[i] < 0.05 else ""))
h = int(np.sum(np.abs(pool_arr / r - 1.0) < 0.05))
print("5%% 窗內命中數 = %d" % h)
print("(grep scripts/04: 全池 z=1.74 否決 — 呢度只報告最近身份, 唔升候選)")
print()
print("RESULT: G1=%s G2=報表 G3=%s G4=否決 (承接 scripts/04)" % (
    "5/7 命中+MC pass" if n_hit >= 5 and z >= 5 else "FAIL(池密度)", "普通合成數"))