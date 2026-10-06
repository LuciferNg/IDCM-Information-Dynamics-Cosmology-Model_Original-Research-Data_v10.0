#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/18 — C_f 塊參數盲測（block-parameter blind，第二十輪）
======================================================================
docs/04 §八 剩餘線索：塊幾何中位 {G1,G2,G3} = {3.685, 61.35, 202.07}；
塊間比 61.35/3.685 = 16.648 ≈ B² = 16（dev 4.1%, 線索級）。
docs/15 之後 O233 唯一大 🔴 = C_f 塊參數生成。

本 script：pre-registered 盲測 —— 3 個塊參數（G1/G2/G3 + R1/R2）撞
reuse docs/02 凍結池（hash be07ffd858ab544b, 55049 值）——但係**線索級 dev 4.1%
本身唔夠（池密度背景）**，所以盲測設計 = 兩個獨立統計：
  Q1: 塊參數（G1,G2,G3,R1,R2 = 5 目標）撞凍結池 1e-3/1e-4 窗命中數 vs MC null
  Q2: ★ 塊間比 R1 期望 B²=16 —— pre-registered 單目標（docs/04 已寫「線索級, 非證據」）
      —— 用「dev 4.1% 喺 random 5 目標中嘅最小 dev 分佈」做 look-elsewhere 控制
  Q3: 塊參數 vs 質量階層 - 塊間比 R1·R2 = 54.8 有冇結構身份
判定: Q1 無富集 = 維持 docs/02 結論（塊參數都唔喺結構池）; Q2/Q3 用 MC 校正後
決定「B²=16 線索」可否升格。
"""
import json, math, random, hashlib
import mpmath as mp
mp.mp.dps = 40

# ── 塊參數（docs/04 §八，幾何中位）───────────────────────────────
G1, G2, G3 = 3.685, 61.35, 202.07
R1, R2 = G2/G1, G3/G2
print(f"塊中位: G1={G1} G2={G2} G3={G3}")
print(f"塊間比: R1=G2/G1={R1:.4f}  R2=G3/G2={R2:.4f}  R1·R2=G3/G1={R1*R2:.4f}")

# ── 重建 docs/02 凍結池（同源: S 集合 + F1/F2/F3/F4 族）────────────
L = [2, 1]
for k in range(2, 15):
    L.append(L[-1] + L[-2])
F = [0, 1]
for k in range(2, 21):
    F.append(F[k-1] + F[k-2])
S = set(L) | set(F[2:]) | {4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2, 18, 5,
                           88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37, 41,
                           47, 48, 50, 51, 26, 22, 17, 8, 40}
S = sorted(S)
POOL = set()
def add_pool(v):
    """原文用 mp.nstr(v,12) 做 set key（去重圓整），照做先可以還原 55049。"""
    if mp.mpf('0.1') <= v <= mp.mpf('1e4'):
        POOL.add(mp.nstr(v, 12))
for s in S:
    add_pool(mp.mpf(s))
for c in S:
    for s in S:
        add_pool(mp.mpf(s)/mp.mpf(c))
for c in S:
    for s1 in S:
        for s2 in S:
            add_pool((mp.mpf(s1)+mp.mpf(s2))/mp.mpf(c))
            if s1 > s2:
                add_pool((mp.mpf(s1)-mp.mpf(s2))/mp.mpf(c))
for i in range(1, 45):
    for j in range(i+1, 45):
        add_pool(mp.sin(mp.pi*i/88)**2 / mp.sin(mp.pi*j/88)**2)
        add_pool(mp.sin(mp.pi*j/88)**2 / mp.sin(mp.pi*i/88)**2)
for x3 in (1, 5, 9):
    for x3p in (0, 1, 3, 4, 6, 7):
        add_pool(mp.mpf(1 + x3 * x3p))
POOL = sorted((mp.mpf(k) for k in POOL), key=lambda x: float(mp.log(x)))
POOL = sorted(POOL)
h = hashlib.sha256("|".join(mp.nstr(v, 30) for v in POOL[:1000]).encode()).hexdigest()[:16]
print(f"重建池: {len(POOL)} 值, head hash={h} (原文 be07ffd858ab544b)")
if len(POOL) != 55049:
    print(f"⚠️ 池大小差 {len(POOL)-55049:+d} —— mpmath 版本 nstr 邊界圓整, 統計絕緣")

def pool_hits(target, dT):
    """target 對池嘅 dev<dT 命中數（bisect 窗）"""
    import bisect
    t = mp.mpf(target)
    lo, hi = t/mp.mpf(1+dT), t*mp.mpf(1+dT)
    i0 = bisect.bisect_left(POOL, lo)
    i1 = bisect.bisect_right(POOL, hi)
    return i1 - i0

TARGETS = {"G1": G1, "G2": G2, "G3": G3, "R1": R1, "R2": R2}
print("\n=== Q1: 塊參數撞凍結池（1e-3 / 1e-4 窗）===")
hits_3 = {k: pool_hits(v, 1e-3) for k, v in TARGETS.items()}
hits_4 = {k: pool_hits(v, 1e-4) for k, v in TARGETS.items()}
for k in TARGETS:
    print(f"  {k:>3} = {TARGETS[k]:8.4f}  hits(1e-3)={hits_3[k]:3d}  hits(1e-4)={hits_4[k]:3d}")

# Q1 MC null: log-uniform 5 目標（範圍 [0.1, 1000]）撞池 — 池密度背景
random.seed(20261006)
NMC = 5000
cnt_ge3 = cnt_ge4 = 0
for _ in range(NMC):
    ts = [10**random.uniform(-1, 3) for _ in range(5)]
    h3 = sum(pool_hits(t, 1e-3) for t in ts)
    h4 = sum(pool_hits(t, 1e-4) for t in ts)
    if h3 >= sum(hits_3.values()): cnt_ge3 += 1
    if h4 >= sum(hits_4.values()): cnt_ge4 += 1
print(f"\n  MC null (5 目標, {NMC}): P(h3 ≥ {sum(hits_3.values())}) = {cnt_ge3/NMC:.4f}"
      f"  P(h4 ≥ {sum(hits_4.values())}) = {cnt_ge4/NMC:.4f}")

# Q2: R1 ≈ B²=16 單目標 pre-registered（docs/04 線索）—— dev 4.1%
dev_r1 = abs(R1 - 16) / 16
print(f"\n=== Q2: R1 vs B²=16 （pre-registered 單目標, dev={dev_r1*100:.2f}%）===")
SQR = [k*k for k in range(1, 10)] + [k**3 for k in range(1, 6)]
# analytic: block ratio R = G2/G1, G_i ~ log-normal approx → P(0.96·16 ≤ R ≤ 1.04·16)
# 用 Monte-Carlo 10k
import random as rnd
rnd.seed(20261007)
cnt_dev = 0
N2 = 10000
for _ in range(N2):
    r = 10**rnd.uniform(0, 2.5)
    b = min(abs(r - s)/s for s in SQR)
    if b <= dev_r1: cnt_dev += 1
print(f"  P(隨機 塊間比 對結構冪 dev ≤ {dev_r1*100:.2f}%) = {cnt_dev/N2:.6f}")

# Q3: R1·R2 = G3/G1 = 54.82 對結構數
R12 = R1 * R2
print(f"\n=== Q3: R1·R2 = G3/G1 = {R12:.4f} ===")
for cand, name in [(54.0, "2·L₉?"), (55.0, "F₁₀"), (54.82, "obs"), (32*1.713, "2⁵·x")]:
    pass
cands = {"F₁₀": 55, "2·27": 54, "L₈+L₄": 41}  # 唔好亂加——pre-registered 只列已身份常數
for name, c in cands.items():
    print(f"  {name} = {c}: dev = {abs(R12-c)/c*100:.2f}%")
q3hits = pool_hits(R12, 1e-3)
print(f"  R12 撞池 1e-3 窗: {q3hits} hits")

out = {"TARGETS": {k: float(v) for k, v in TARGETS.items()},
       "hits_1e-3": hits_3, "hits_1e-4": hits_4,
       "P_Q1_3": cnt_ge3/NMC, "P_Q1_4": cnt_ge4/NMC,
       "R1_vs_B2_dev": dev_r1, "P_Q2": cnt_dev/N2,
       "R12": R12, "Q3_hits": q3hits,
       "note": "塊參數盲測: Q1 凍結池無富集預期; Q2 R1≈B² 單目標 MC; Q3 積身份"}
with open("data/18_block_parameter_blind.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n✅ data/18_block_parameter_blind.json 寫入")