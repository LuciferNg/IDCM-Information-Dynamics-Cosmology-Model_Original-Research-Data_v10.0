#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/20 — κ 張量非對角組合盲測（第二十二輪）
=====================================================
docs/04 §六 唯一未封死算子族 = κ 張量非對角組合。docs/16 §八 撤回「獨立錨」
後，κ 係 C_f 生成器個 hunt 唯一合法續路。

設計（pre-registered）：
  池 A：κ_ijk 全 entries（36 維 triple intersection, 整數 -232..85）
  池 B：K_ij = Σ_k κ_ijk（36×36 對稱矩陣）所有非對角元素
  池 C：K 本徵值譜（實數, mpmath 精確）
  池 D：K 本徵值比 λ_i/λ_j（i≠j）—— 無量綱比（同 C_f 量綱匹配）
目標：C_f 8 值（e,u,d,s,μ,c,τ,b,A_γ 授權序）
  C_e=3.5941 C_u=3.8029 C_d=3.6620 C_s=41.3207 C_μ=30.0309 C_c=186.0605
  C_τ=159.6437 C_b=255.7517
統計：8 目標撞四池 1e-3/1e-4 窗 vs MC null（log-uniform 8 目標）
判定：P(null) < 0.05 先有 κ 身份證據；否則 C_f 唔喺 κ 譜/元素/比池。
"""
import json, math, random, bisect
import mpmath as mp
mp.mp.dps = 40

# ── C_f 目標（A_γ 授權序 e→1,u→2,d→3,s→4,μ→5,c→7,τ→9,b→11）─────
CF_TARGETS = {"e": 3.5941, "u": 3.8029, "d": 3.6620, "s": 41.3207,
              "mu": 30.0309, "c": 186.0605, "tau": 159.6437, "b": 255.7517}

# ── 讀 O53 κ（CY₃(36,98) triple intersections）───────────────
KAPPA_PATH = ("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/"
              "open_problems_fresh/o53_cy3_reality/data/polytopes/kappa_36d_raw.json")
d = json.load(open(KAPPA_PATH, encoding="utf-8"))
kapp = d["kappa"]
N = 36

# 池 A：κ entries value
poolA = set()
for key, v in kapp.items():
    poolA.add(mp.mpf(abs(v)))      # C_f 全正，取 |κ|
    poolA.add(mp.mpf(v))           # 保負（若 C_f 某值負——唔會, 但照列）
poolA = sorted(poolA)
print(f"池 A: {len(poolA)} 值（κ entries |κ| 及 κ）")

# 池 B：K_ij = Σ_k κ_ijk 非對角元素
K = [[0]*N for _ in range(N)]
for key, v in kapp.items():
    a, b, c = map(int, key.split(","))
    # 對稱張量：所有置換等值。累計入 K[i][j] 每種 (i,j) 只一次（已對稱化）
    K[a][b] += v; K[b][a] += v
    K[a][c] += v; K[c][a] += v
    K[b][c] += v; K[c][b] += v
poolB = set()
for i in range(N):
    for j in range(N):
        if i != j:
            poolB.add(mp.mpf(K[i][j]))
poolB = sorted(poolB)
print(f"池 B: {len(poolB)} 值（K 非對角元素, 唯一化）")

# 池 C：K 本徵值譜
Kmf = mp.matrix(N, N)
for i in range(N):
    for j in range(N):
        Kmf[i, j] = mp.mpf(K[i][j])
ev_vals, _ = mp.eig(Kmf)          # (list of eigenvalues, eigenvectors matrix)
eigs = sorted([mp.mpf(x.real) for x in ev_vals], reverse=True)
poolC = sorted([mp.mpf(x.real) for x in eigs])
print(f"池 C: {len(poolC)} 值（K 譜, 實部）")
print("  譜頭5:", [mp.nstr(x, 6) for x in poolC[:5]])

# 池 D：本徵值比 λ_i/λ_j（無量綱, 同 C_f 量綱匹配）
poolD = set()
for i in range(N):
    for j in range(N):
        if i == j: continue
        if abs(eigs[j]) > mp.mpf('1e-30'):
            r = eigs[i]/eigs[j]
            if mp.mpf('1e-3') <= abs(r) <= mp.mpf('1e4'):
                poolD.add(abs(r))
poolD = sorted(poolD)
print(f"池 D: {len(poolD)} 值（λ 比, |r|∈[1e-3,1e4]）")

POOLS = {"A": poolA, "B": poolB, "C": poolC, "D": poolD}

def hits(pool, target, dT):
    t = mp.mpf(target)
    lo, hi = t/mp.mpf(1+dT), t*mp.mpf(1+dT)
    return bisect.bisect_right(pool, hi) - bisect.bisect_left(pool, lo)

# ── 盲測：8 目標撞四池 ──────────────────────────────────────
print("\n=== κ 池命中（C_f 8 目標 vs 池）===")
tot3 = tot4 = 0
for name, pool in POOLS.items():
    h3 = {k: hits(pool, v, 1e-3) for k, v in CF_TARGETS.items()}
    h4 = {k: hits(pool, v, 1e-4) for k, v in CF_TARGETS.items()}
    s3, s4 = sum(h3.values()), sum(h4.values())
    tot3 += s3; tot4 += s4
    hits3 = {k: v for k, v in h3.items() if v}
    hits4 = {k: v for k, v in h4.items() if v}
    print(f"  池 {name}: Σhits(1e-3)={s3} Σhits(1e-4)={s4}" +
          (f"  @1e-3: {hits3}" if hits3 else "") +
          (f"  @1e-4: {hits4}" if hits4 else ""))

# ── MC null：8 log-uniform 目標撞同池 ─────────────────────────
random.seed(20261010)
NMC = 8000
ge3 = ge4 = 0
LO, HI = 1e-2, 1e4   # C_f 範圍 3.59..255.75 畀大窗（嚴格）
for _ in range(NMC):
    s3 = s4 = 0
    for _ in range(8):
        t = 10**random.uniform(math.log10(LO), math.log10(HI))
        for pool in POOLS.values():
            s3 += hits(pool, t, 1e-3)
            s4 += hits(pool, t, 1e-4)
    if s3 >= tot3: ge3 += 1
    if s4 >= tot4: ge4 += 1
print(f"\nMC null (8 目標×4 池, {NMC}): P(Σhits ≥ {tot3} @1e-3) = {ge3/NMC:.4f}"
      f"  P(Σhits ≥ {tot4} @1e-4) = {ge4/NMC:.4f}")

out = {"CF_TARGETS": CF_TARGETS,
       "pool_sizes": {k: len(v) for k, v in POOLS.items()},
       "tot_hits_1e-3": tot3, "tot_hits_1e-4": tot4,
       "P_null_3": ge3/NMC, "P_null_4": ge4/NMC,
       "spectrum_head": [mp.nstr(x, 8) for x in poolC[:8]],
       "note": "O53 kappa(CY3-36d) 非對角組合盲測; 撤回獨立錨後唯一合法路線"}
with open("data/20_kappa_identity_blind.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n✅ data/20_kappa_identity_blind.json 寫入")