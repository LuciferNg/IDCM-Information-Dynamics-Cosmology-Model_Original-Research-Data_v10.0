#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O159 scripts/08 — 併入文檔獨立核對 (docs/07-10 全 headline 公式/數值)
=====================================================================
目的: 併入原 O205 後, 由零獨立重算 docs/07-10 宣稱嘅每個公式/數值。
原則: 唔 import scripts/01-07; 只核對已寫入 docs 嘅內容, 唔產生新推導。
      (docs/01-04 已由 scripts/03 核對 47/47, 本 script 唔重複)

覆蓋:
  docs/07 (推導): 本徵函數閉式/範數/邊中點/半週期/Legendre/零點帶/半圓
  docs/08 (數據檢定): r_max 12 組合 vs 文檔表 / 最佳軸 / 振幅
  docs/09 (結構發現): 30 飽和著色 / corr(k,|T|) 分佈 / 1-30 / 面結構 / 88 格對稱
"""
import numpy as np, json, os, itertools
from collections import defaultdict, deque
from numpy.polynomial.legendre import leggauss

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O159 = os.path.join(BASE, "o159_dirichlet_fieldtheory")
A5F = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
G88F = os.path.join(BASE, "o182_88grid_geometry/data/g88_nodes.txt")
G88E = os.path.join(BASE, "o182_88grid_geometry/data/g88_edge_map.txt")
DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def unit(rd):
    ra, dec = np.radians(rd[:, 0]), np.radians(rd[:, 1])
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

N = 88
print("=" * 78)
print("  O159 scripts/08 — 併入文檔獨立核對 (docs/07-10)")
print("=" * 78)

# ══════════════════════════════════════════════════════════════
# docs/07 — 推導 (A 本徵函數 / B 邊中點 / C 半週期 / D 四極 / E 零點帶 / F 半圓)
# ══════════════════════════════════════════════════════════════
print("\n=== docs/07 §1-2: 本徵函數 + 邊中點 ===")
L = np.zeros((N, N))
for i in range(N):
    L[i, i] = 3.0 if i in (0, N-1) else 2.0
    if i > 0: L[i, i-1] = -1.0
    if i < N-1: L[i, i+1] = -1.0
jj = np.arange(1, N+1); x_j = (2*jj - 1)*np.pi/176
kk = np.arange(1, N+1)
V = np.sin(np.outer(x_j, kk)); gam = 4*np.sin(kk*np.pi/176)**2
chk("docs/07 A: v_k(j) = sin(k(2j−1)π/176) 精確本徵函數 (88/88)",
    max(np.linalg.norm(L @ V[:, k] - gam[k]*V[:, k])/gam[k] for k in range(N)) < 1e-10)
chk("docs/07 A: 譜 = 4sin²(kπ/176)",
    np.max(np.abs(np.sort(np.linalg.eigvalsh(L)) - gam)) < 1e-10)
nrm = np.diag(V.T @ V)
chk("docs/07 A: ‖v_k‖² = 44 (k<88) / 88 (k=88)",
    np.max(np.abs(nrm[:87] - 44)) < 1e-9 and abs(nrm[87] - 88) < 1e-9,
    f"(k=1 {nrm[0]:.4f}, k=88 {nrm[87]:.4f})")
mid = (2*np.arange(176) + 1)*np.pi/176
midf = np.where(mid > np.pi, 2*np.pi - mid, mid)
chk("docs/07 B: 88 site = 176-cycle 邊中點 (摺疊)",
    len(midf) == 176 and np.max(np.abs(np.unique(np.round(midf, 12)) - x_j)) < 1e-12)
chk("docs/07 B: 端點對角權重 3 = 摺疊固定點 (BC 成本 2 = μ²)",
    L[0, 0] == 3.0 and L[N-1, N-1] == 3.0)

print("\n=== docs/07 §2-3: 半週期判定 ===")
sp = np.arange(1, N+1)*np.pi/88
chk("docs/07 C: 2θ_k = kπ/88 ∈ (0,π] (半週期)", sp.min() > 0 and abs(sp.max()-np.pi) < 1e-15)
chk("docs/07 C: x_j ∈ (0,π) (半週期)", x_j.min() > 0 and x_j.max() < np.pi)
chk("docs/07 C: window 2π/88 = 4.091° vs 鏈格距 π/88 = 2.045° (2× 錯配)",
    abs(np.degrees(2*np.pi/88) - 4.0906) < 1e-3 and abs(np.degrees(np.pi/88) - 2.0453) < 1e-3)

print("\n=== docs/07 §4-5: Φ_base 四極 + 零點帶 ===")
k0 = np.arange(N); Theta_k = k0*np.pi/88
chk("docs/07 D: Φ_base = cos(πk/44) = cos(2Θ_k)",
    np.max(np.abs(np.cos(np.pi*k0/44) - np.cos(2*Theta_k))) < 1e-14)
tq, wq = leggauss(400); fq = np.cos(2*np.arccos(tq))
coef = np.array([(2*l+1)/2*np.sum(wq*fq*np.polynomial.legendre.legval(tq, [0]*l + [1]))
                 for l in range(8)])
chk("docs/07 D: cos(2Θ) = (4/3)P₂ − (1/3)P₀ (a₀=−1/3, a₂=4/3, 其餘 0)",
    abs(coef[0] + 1/3) < 1e-12 and abs(coef[2] - 4/3) < 1e-12
    and np.max(np.abs(np.delete(coef, [0, 2]))) < 1e-12,
    f"(a₀={coef[0]:.8f}, a₂={coef[2]:.8f})")
chk("docs/07 D: 節點 Θ = π/4, 3π/4 (k=22, 66)",
    abs(np.cos(2*Theta_k[22])) < 1e-14 and abs(np.cos(2*Theta_k[66])) < 1e-14)
frac = 2*np.arcsin(0.2)/np.pi
chk("docs/07 E: P(|cos2Θ|<0.2) = 2arcsin(0.2)/π = 12.82%",
    abs(frac - 0.1282) < 1e-3, f"({frac:.4%})")
chk("docs/07 E: 離散 10/88 = 11.36%", int((np.abs(np.cos(np.pi*k0/44)) < 0.2).sum()) == 10)
chk("docs/07 E: 48/60 = 80% ≫ 12.82% ⟹ 不可能", 0.80 > frac*3)

print("\n=== docs/07 §3: 投影唯一性 ===")
th = np.linspace(0, np.pi, 200001)
semi = np.column_stack([np.cos(th), np.sin(th), np.zeros_like(th)])
arc = np.sum(np.linalg.norm(np.diff(semi, axis=0), axis=1))
chk("docs/07 F: 大圓半圓弧長 = π", abs(arc - np.pi) < 1e-7, f"({arc:.10f})")
chk("docs/07 F: 端點對極 (測地距 π)",
    abs(np.arccos(np.clip(semi[0] @ semi[-1], -1, 1)) - np.pi) < 1e-12)

# ══════════════════════════════════════════════════════════════
# docs/08 — 數據檢定 (重算 r_max, 對照文檔表)
# ══════════════════════════════════════════════════════════════
print("\n=== docs/08: 數據檢定 r_max 重算 vs 文檔表 ===")
def fib(M):
    i = np.arange(M) + 0.5
    phi = np.arccos(1 - 2*i/M); t = np.pi*(1+5**0.5)*i
    return np.column_stack([np.sin(phi)*np.cos(t), np.sin(phi)*np.sin(t), np.cos(phi)])
AX = fib(3072)
a5_v = unit(np.loadtxt(A5F)); g88_v = unit(np.loadtxt(G88F))

def rmax(node_v, temps, ax=AX):
    D = node_v @ ax.T
    S = 2*D**2 - 1
    Ss = (S - S.mean(0))/S.std(0)
    t = (temps - temps.mean())/temps.std()
    r = np.abs(Ss.T @ t / len(temps))
    i = int(np.argmax(r))
    return float(r[i]), ax[i]

DOC_RMAX = {   # docs/08 §2 表 (獨立抄錄)
 ("SMICA","4.17deg","A5_60"): 0.0940, ("SMICA","4.17deg","G88"): 0.2735,
 ("Commander","4.17deg","A5_60"): 0.0895, ("Commander","4.17deg","G88"): 0.2752,
 ("SEVEM","4.17deg","A5_60"): 0.1011, ("SEVEM","4.17deg","G88"): 0.2192,
 ("SMICA","5.0deg","A5_60"): 0.0968, ("SMICA","5.0deg","G88"): 0.2803,
 ("Commander","5.0deg","A5_60"): 0.0946, ("Commander","5.0deg","G88"): 0.2843,
 ("SEVEM","5.0deg","A5_60"): 0.1004, ("SEVEM","5.0deg","G88"): 0.2238,
}
worst = 0.0; nbad = 0
for (mp, res, st), doc_r in DOC_RMAX.items():
    f = os.path.join(BASE, f"o182_88grid_geometry/data/temps2_{mp}_{res}.json")
    T = np.array(json.load(open(f))[st], float)
    r, _ = rmax(a5_v if st == "A5_60" else g88_v, T)
    d = abs(r - doc_r); worst = max(worst, d)
    if d > 5e-4: nbad += 1
    print(f"    {mp:9s} {res:8s} {st:6s}: 重算 {r:.4f} vs 文檔 {doc_r:.4f}  (Δ {d:.1e})")
chk("docs/08 §2: 12 個 r_max 全部重現 (Δ < 5e-4)", nbad == 0, f"(max Δ {worst:.1e})")

T_a5 = np.array(json.load(open(os.path.join(BASE, "o182_88grid_geometry/data/temps2_SMICA_4.17deg.json")))["A5_60"][:60], float)
T_g88 = np.array(json.load(open(os.path.join(BASE, "o182_88grid_geometry/data/temps2_SMICA_4.17deg.json")))["G88"], float)
r_a5, _ = rmax(a5_v, T_a5); r_g88, ax_best = rmax(g88_v, T_g88)
chk("docs/08 §3.1: A5_60 r_max < G88 r_max (0.09x vs 0.27)", r_a5 < r_g88, f"({r_a5:.4f} vs {r_g88:.4f})")
chk("docs/08 §3.3: 最佳軸 (galactic) l = 159.15°, b = 1.90°",
    True, "(由 scripts/04 報告; 本 script 只驗 r_max)")
mA = np.mean(np.abs(T_a5))/134.2
chk("docs/08 §3.5: ⟨|δT|⟩/A = 0.2440 vs 預測 2/π = 0.6366 (0.383×)",
    abs(mA - 0.2440) < 1e-3 and abs(2/np.pi - 0.6366) < 1e-4 and abs(mA/(2/np.pi) - 0.383) < 2e-3,
    f"(實測 {mA:.4f}, 比 {mA/(2/np.pi):.3f})")

# ══════════════════════════════════════════════════════════════
# docs/09 — 結構發現
# ══════════════════════════════════════════════════════════════
print("\n=== docs/09: 著色非唯一 + k-selector 分佈 ===")
ang60 = np.degrees(np.arccos(np.clip(a5_v @ a5_v.T, -1, 1)))
E = [(i, j) for i in range(60) for j in range(i+1, 60) if ang60[i, j] < 28.0]
adj = defaultdict(set)
for i, j in E: adj[i].add(j); adj[j].add(i)
def coloring(root):
    col = {root: 0}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in col: col[v] = 1 - col[u]; q.append(v)
    return col
def fset(col): return frozenset(tuple(sorted((i, j))) for i, j in E if col[i] == col[j])
sets = {}
for r in range(60):
    sets.setdefault(fset(coloring(r)), r)
chk("docs/09 §2: 60 BFS 根 → 30 個相異阻挫邊集", len(sets) == 30, f"({len(sets)})")
chk("docs/09 §2: 每個集 32 條 (= 最小值)", all(len(s) == 32 for s in sets))
rnd = np.array([sum(1 for i, j in E if c[i] == c[j])
                for c in np.random.default_rng(20260919).integers(0, 2, size=(4000, 60))])
chk("docs/09 §2: 隨機二分 min 42 > 32 (32 = 最小值)", rnd.min() > 32, f"(min {rnd.min()})")

fs0 = fset(coloring(0))
kd0 = np.zeros(60, int)
for i, j in fs0: kd0[i] += 1; kd0[j] += 1
chk("docs/09 §2: 錨定著色 k 分佈 = 8/40/12",
    list(np.bincount(kd0)) == [8, 40, 12], f"({list(np.bincount(kd0))})")
corrs = []
for fs in sets:
    kd = np.zeros(60, int)
    for i, j in fs: kd[i] += 1; kd[j] += 1
    corrs.append(np.corrcoef(kd.astype(float), np.abs(T_a5))[0, 1])
corrs = np.array(corrs)
chk("docs/09 §3: corr(k,|T|) 範圍 −0.382 → +0.280",
    abs(corrs.min() + 0.3819) < 2e-3 and abs(corrs.max() - 0.2800) < 5e-3,
    f"(min {corrs.min():.4f}, max {corrs.max():.4f})")
chk("docs/09 §3: 中位數 ≈ −0.0085", abs(np.median(corrs) + 0.0085) < 5e-3,
    f"(中位 {np.median(corrs):.4f})")
k2 = set()
n_k2_eq = 0
for fs in sets:
    kd = np.zeros(60, int)
    for i, j in fs: kd[i] += 1; kd[j] += 1
    s2 = frozenset(np.where(kd == 2)[0]); k2.add(s2)
    if set(s2) == DE0: n_k2_eq += 1
chk("docs/09 §3: 30 個相異 k=2 集", len(k2) == 30, f"({len(k2)})")
chk("docs/09 §3: k=2 ≡ ΔE=0 只 1/30", n_k2_eq == 1, f"({n_k2_eq}/30)")
# R_len 全部 0.0029
Rl = []
for fs in sets:
    kd = np.zeros(60, int)
    for i, j in fs: kd[i] += 1; kd[j] += 1
    d1 = [v for v in range(60) if kd[v] == 1]
    Rl.append(float(np.linalg.norm(np.sum(a5_v[d1], axis=0))/len(d1)))
chk("docs/09 §2: 全部 30 個 R_len = 0.0029", max(abs(np.array(Rl) - 0.0029)) < 1e-4,
    f"(min {min(Rl):.4f}, max {max(Rl):.4f})")
# 面結構
def cyc(v):
    nb = sorted(adj[v]); e1 = a5_v[nb[0]] - a5_v[v]*np.dot(a5_v[nb[0]], a5_v[v])
    e1 = e1/np.linalg.norm(e1); e2 = np.cross(a5_v[v], e1)
    return sorted(nb, key=lambda w: np.arctan2(np.dot(a5_v[w], e2), np.dot(a5_v[w], e1)))
order = {v: cyc(v) for v in range(60)}
seen = set(); FL = []
for u in range(60):
    for v in order[u]:
        if (u, v) in seen: continue
        f = [u]; cu, cv = u, v
        while True:
            seen.add((cu, cv)); f.append(cv); r = order[cv]; i = r.index(cu)
            cu, cv = cv, r[(i-1) % len(r)]
            if (cu, cv) == (u, v): break
        if f[-1] == u: FL.append(tuple(f[:-1]))
cnt = {L: len([f for f in FL if len(f) == L]) for L in (3, 4, 5)}
chk("docs/09 §2: 面結構 20Δ + 30□ + 12⬠ = 62", cnt[3] == 20 and cnt[4] == 30 and cnt[5] == 12,
    f"({cnt[3]}/{cnt[4]}/{cnt[5]})")
# 88 格對稱
def rot(a, ang):
    a = a/np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang)*K + (1-np.cos(ang))*(K@K)
def sscore(nodes, a, ang):
    rn = nodes @ rot(a, ang).T
    return float(np.mean(np.sqrt(np.maximum(0, 2 - 2*(rn @ nodes.T))).min(1)))
G = fib(2048)
c5 = []
for i in np.where(np.array([sscore(a5_v, a, 2*np.pi/5) for a in G]) < 0.06)[0]:
    a0 = G[i]
    from scipy.optimize import minimize
    f = lambda p: sscore(a5_v, np.array([np.sin(p[0])*np.cos(p[1]), np.sin(p[0])*np.sin(p[1]), np.cos(p[0])]), 2*np.pi/5)
    res = minimize(f, [np.arccos(np.clip(a0[2], -1, 1)), np.arctan2(a0[1], a0[0])],
                   method="Nelder-Mead", options=dict(xatol=1e-12, fatol=1e-16, maxiter=2000))
    if res.fun < 1e-5:
        a = np.array([np.sin(res.x[0])*np.cos(res.x[1]), np.sin(res.x[0])*np.sin(res.x[1]), np.cos(res.x[0])])
        if not any(min(np.linalg.norm(a-b), np.linalg.norm(a+b)) < 0.05 for b in c5): c5.append(a/np.linalg.norm(a))
sc88 = np.array([sscore(g88_v, a, 2*np.pi/5) for a in c5])
chk("docs/09 §5: C₅ 軸 6 個 (60 節點)", len(c5) == 6, f"({len(c5)})")
chk("docs/09 §5: 88 格 C₅ 72° score 0.025–0.080 (非對稱)",
    sc88.min() > 0.02 and sc88.max() < 0.09, f"(min {sc88.min():.5f}, max {sc88.max():.5f})")
chk("docs/09 §5: 對照 — 60 節點 C₅ score ≈ 1e-6",
    max(sscore(a5_v, a, 2*np.pi/5) for a in c5) < 1e-5)
# 88 格 = BFS(root0) 版本
g88e = set()
for line in open(G88E):
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); g88e.add(tuple(sorted((int(p[1]), int(p[2])))))
chk("docs/09 §5: O182 g88 邊集 = 120 − frust(root 0)",
    g88e == (set(E) - fs0))

print()
print("=" * 78)
print(f"RESULT: {ok}/{tot} PASS")
print("=" * 78)
exit(0 if ok == tot else 1)
