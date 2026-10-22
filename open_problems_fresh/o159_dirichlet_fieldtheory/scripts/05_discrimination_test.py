#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O159 scripts/05 (原 O205 scripts/02) — 判別測試: 176-Laplacian 投影 vs 阻挫度 k 選擇器
==================================================================
背景: 並行 O143 session (docs/02, 2026-09-19) 提出「阻挫度 k(i) = 節點 i 連接嘅
阻挫邊數」作為幅度選擇器 (corr(k, |T|) = −0.382, p = 0.0014)。

本 script 回答: 呢個 k-選擇係咪可以由本 O (原 O205) 導出嘅 176-Laplacian 投影解釋?
  - 若 k 同 cos(2Θ(â)) 對任何軸都唔相關 ⟹ 兩個結構獨立, 導出投影唔係 k 機制嘅來源
  - 若相關 ⟹ 導出投影可以承載 k 選擇

T1: 獨立重構 A₅ 網絡 + 2-著色 + 阻挫度 k (圖結構, 唔用溫度)
T2: 獨立核對 corr(k, |T|) = −0.382 + permutation p (核對 O143 docs/02)
T3: ★ 決定性測試 — k 係咪軸對稱? max_â |corr(k, cos2Θ(â))| + null
T4: |T| vs 導出折疊形式 |cos2Θ(â)|
T5: 偏相關 — 移除最佳軸對稱分量後, k-信號係咪仍然存在?
"""
import numpy as np, json, os
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O159 = os.path.join(BASE, "o159_dirichlet_fieldtheory")   # 2026-09-19 由 O205 併入
A5F = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
TEMPS = os.path.join(BASE, "o182_88grid_geometry/data/temps2_SMICA_4.17deg.json")
DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("=" * 76)
print("  O159 scripts/05 (原 O205 scripts/02) — 判別測試: 導出投影 vs 阻挫度 k")
print("=" * 76)

# ── 節點向量 + A₅ 網絡 ──
rd = np.loadtxt(A5F)
ra, dec = np.radians(rd[:, 0]), np.radians(rd[:, 1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
D = np.clip(V @ V.T, -1, 1)
ang = np.degrees(np.arccos(D))

THR = 28.0
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if ang[i, j] < THR]
adj = defaultdict(set)
for i, j in edges:
    adj[i].add(j); adj[j].add(i)
deg = np.array([len(adj[i]) for i in range(60)])
print(f"\n[T1] A₅ 網絡重構 (閾值 {THR}°): {len(edges)} 條邊, 度數分佈 {dict(zip(*np.unique(deg, return_counts=True)))}")
chk("T1a: 網絡 = 120 邊 (O7/O182 一致)", len(edges) == 120, f"({len(edges)})")
chk("T1b: 4-正則 (每節點 4 鄰)", bool(np.all(deg == 4)))

# 2-著色 (BFS, 唯一 up to global flip)
color = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]; q.append(v)
col = np.array([color[i] for i in range(60)])
frust = [(i, j) for i, j in edges if col[i] == col[j]]
kdeg = np.zeros(60, int)
for i, j in frust:
    kdeg[i] += 1; kdeg[j] += 1
n_by_k = dict(zip(*np.unique(kdeg, return_counts=True)))
print(f"  阻挫邊 {len(frust)} 條 (O182: 120−88 = 32); k 分佈 {n_by_k}")
chk("T1c: 阻挫邊 = 32 (120 − 88 透明)", len(frust) == 32, f"({len(frust)})")
chk("T1d: k 分佈 = 8 / 40 / 12 (k=0/1/2)", n_by_k.get(0) == 8 and n_by_k.get(1) == 40 and n_by_k.get(2) == 12)
chk("T1e: ★k=2 節點集 ≡ ΔE=0 節點集 (精確恆等式)",
    set(np.where(kdeg == 2)[0]) == DE0, f"(k=2: {sorted(np.where(kdeg==2)[0])})")

# ── 溫度 ──
T = np.array(json.load(open(TEMPS))["A5_60"][:60], float)
A = 134.2
rng = np.random.default_rng(20260919)

def corr(x, y):
    x = x - x.mean(); y = y - y.mean()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))

def perm_p(x, y, n=20000, two_sided=False):
    """置換檢定: 固定 x, 置換 y."""
    obs = corr(x, y)
    null = np.array([corr(x, rng.permutation(y)) for _ in range(n)])
    if two_sided:
        return obs, float(np.mean(np.abs(null) >= abs(obs)))
    return obs, float(np.mean(null <= obs))       # 單尾 (負相關)

# ── T2: 獨立核對 O143 docs/02 ──
print("\n[T2] 獨立核對 O143: corr(k, |T|)")
c_kT, p_kT = perm_p(kdeg.astype(float), np.abs(T))
print(f"  corr(k, |T|) = {c_kT:.4f}  (O143: −0.3819), 置換單尾 p = {p_kT:.4f}  (O143: 0.0014)")
chk("T2a: 重現 corr(k,|T|) = −0.382 (±0.01)", abs(c_kT + 0.3819) < 0.01, f"({c_kT:.4f})")
chk("T2b: 重現 p ≈ 0.0014 (±0.002)", abs(p_kT - 0.0014) < 0.002, f"({p_kT:.4f})")
# 各 k 組統計
for kk in (0, 1, 2):
    m = kdeg == kk
    print(f"  k={kk}: n={m.sum():2d}, σ(T)={T[m].std(ddof=1):5.1f} μK, mean|T|={np.abs(T[m]).mean():5.1f} μK")

# ── T3: ★ 決定性測試 — k 係咪軸對稱? ──
print("\n[T3] ★ 決定性測試: k 同導出形式 cos2Θ(â) 嘅最大相關")
def fib(M):
    i = np.arange(M) + 0.5
    phi = np.arccos(1 - 2*i/M); th = np.pi*(1+5**0.5)*i
    return np.column_stack([np.sin(phi)*np.cos(th), np.sin(phi)*np.sin(th), np.cos(phi)])
AX = fib(3072)
DD = V @ AX.T
S = 2 * DD**2 - 1                        # cos2Θ(â)
Ss = (S - S.mean(0)) / S.std(0)
kv = (kdeg - kdeg.mean()) / kdeg.std()
r_obs = np.abs(Ss.T @ kv / 60)
i_best = int(np.argmax(r_obs))
null = np.empty(2000)
for i0 in range(0, 2000, 200):
    blk = np.stack([rng.permutation(kdeg) for _ in range(200)]).astype(float)
    blk = (blk - blk.mean(1, keepdims=True)) / blk.std(1, keepdims=True)
    C = np.abs(Ss.T @ blk.T / 60)
    null[i0:i0+200] = C.max(0)
p_axis = float((1 + np.sum(null >= r_obs[i_best])) / (1 + 2000))
print(f"  max_â |corr(k, cos2Θ(â))| = {r_obs[i_best]:.4f}  (null 平均 {null.mean():.3f}, 95% {np.percentile(null,95):.3f})")
print(f"  p = {p_axis:.4f}")
chk("T3: 發現 — k **係**軸對稱 (p < 0.05) ⟹ 導出形式存在於圖結構 (但見 scripts/03 §A 環分析)",
    p_axis < 0.05, f"(p = {p_axis:.4f})")

# ── T4: |T| vs 導出折疊形式 ──
print("\n[T4] |T| vs 導出折疊形式 |cos2Θ(â)|")
Sf = np.abs(S)
Sfs = (Sf - Sf.mean(0)) / Sf.std(0)
ta = np.abs(T); ta = (ta - ta.mean()) / ta.std()
r_obs_T = np.abs(Sfs.T @ ta / 60)
i_T = int(np.argmax(r_obs_T))
null_T = np.empty(2000)
for i0 in range(0, 2000, 200):
    blk = np.stack([rng.permutation(np.abs(T)) for _ in range(200)])
    blk = (blk - blk.mean(1, keepdims=True)) / blk.std(1, keepdims=True)
    C = np.abs(Sfs.T @ blk.T / 60)
    null_T[i0:i0+200] = C.max(0)
p_T = float((1 + np.sum(null_T >= r_obs_T[i_T])) / (1 + 2000))
print(f"  max_â |corr(|T|, |cos2Θ|)| = {r_obs_T[i_T]:.4f}, p = {p_T:.4f}")
chk("T4: 折疊形式都唔顯著 (p > 0.05)", p_T > 0.05, f"(p = {p_T:.4f})")

# ── T5: 偏相關 — 移除最佳軸對稱分量後 k-信號係咪仍然存在 ──
print("\n[T5] 偏相關: |T| 移除最佳 cos2Θ 分量 → 同 k 嘅相關")
s_best = S[:, i_best]
beta = np.cov(np.abs(T), s_best)[0, 1] / np.var(s_best)
resid = np.abs(T) - beta * s_best
c_part, p_part = perm_p(kdeg.astype(float), resid)
print(f"  移除前 corr(k,|T|) = {c_kT:.4f} (p={p_kT:.4f})")
print(f"  移除後 corr(k, resid) = {c_part:.4f} (p={p_part:.4f})")
chk("T5: k-信號唔受導出分量影響 (殘餘仍負相關, p < 0.05)",
    c_part < 0 and p_part < 0.05, f"(Δ = {abs(c_part - c_kT):.4f})")

json.dump(dict(k_degree=kdeg.tolist(), n_frustrated_edges=len(frust),
               corr_k_absT=c_kT, p_k_absT=p_kT, p_k_axisym=p_axis,
               r_max_k_axisym=float(r_obs[i_best]),
               p_absT_folded=p_T, r_max_absT_folded=float(r_obs_T[i_T]),
               corr_k_resid=c_part, p_k_resid=p_part),
          open(os.path.join(O159, "data", "step2_discrimination.json"), "w"), indent=2, default=float)

print()
print("=" * 76)
print(f"RESULT: {ok}/{tot} PASS")
print("=" * 76)
exit(0 if ok == tot else 1)
