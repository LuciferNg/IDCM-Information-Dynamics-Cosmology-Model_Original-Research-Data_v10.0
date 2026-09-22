#!/usr/bin/env python3
"""
O136 — Script 52: B=4 四幀假設檢驗 (用戶提案)
================================================================================
用戶提案 (2026-09-20):
  「質量譜計算真的很困難，我懷疑計算 A 的質量是要求觀察者 B 的破缺去達成，
   不是普朗克時間內單幀完成賦予，是要觀察方 → 被觀察方 → 再加上 2 幀回溯自洽性檢查,
   4 幀 (B=4) 才能完成質量賦予」

★ 結構動機:
  B = 4 = A₅ 網之【頂點度數】(O182: 60 頂點 120 邊度 4)
  4 幀 = 觀察方 (1) → 被觀察方 (2) → 回溯自洽檢查 (3,4)

★ 零參數預言: 路徑長度 k = 4 (唔係 2 或 3)

⚠️ 已測: docs/23 / script 39 測過 k = 1,2,3,5,10 — 【從未測 k = 4】
   最佳 sumM2 = 0.9482 (2 步路徑和)

本 script:
  (A) k = 1..12 全掃描 — k=4 係唔係特別好?
  (B) 4 幀閉環讀法 (O→X→O 來回): m ∝ |⟨O|n⟩|^4
  (C) 4 幀自洽不動點: 解 m = g^4(m)
  (D) null test: k=4 嘅 RMS 喺 k 掃描中嘅排名 (隨機 k 對照)
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot" / "data"
O182 = ROOT / "o182_88grid_geometry" / "data"
OUT = Path(__file__).parent.parent / "data"

M9 = [1,2,3,4,5,7,9,11,13]
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])

print("=" * 96)
print("O136 Script 52: B=4 四幀假設檢驗")
print("=" * 96)

# ── 幾何 ──
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
cold = U[0].copy()

emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
transp_edges = [(u,v) for _,u,v in emap]

col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])
dist = np.arccos(np.clip(U @ U.T, -1, 1))
all_edges = [(i,j) for i in range(60) for j in range(i+1,60) if dist[i,j] < np.radians(28.0)]
frust_edges = [(i,j) for i,j in all_edges if color[i]==color[j]]
print(f"\n邊: 全 {len(all_edges)}, 透明 {len(transp_edges)}, 阻挫 {len(frust_edges)}")
print(f"★ B = 4 = A₅ 網頂點度數 (O182)")

beta_mid = {}
for u,v in all_edges:
    m = U[u]+U[v]; m /= np.linalg.norm(m)
    beta_mid[(u,v)] = math.acos(np.clip(float(m @ cold), -1, 1))

def build_M(n):
    M = np.zeros((60,60))
    for u,v in transp_edges:
        t = math.cos(n*beta_mid[(u,v)]/2)**2
        M[u,v] = t; M[v,u] = t
    return M

def rms_best(vals):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v); best = (9e9, None, None)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        r = float(np.sqrt(np.mean((A@c-LM)**2)))
        if r < best[0]: best = (r, perm, float(c[1]))
    return best

# ═══ (A) k = 1..12 全掃描 ═══════════════════════════
print(f"\n{'─'*96}\n(A) ★ k = 1..12 全掃描 — k=4 係唔係特別好?\n{'─'*96}")

KCAND = {}
for n in M9:
    Mx = build_M(n)
    Mk = np.eye(60)
    for k in range(1, 13):
        Mk = Mk @ Mx
        KCAND.setdefault(k, {})[n] = float(Mk.sum())

print(f"\n{'k':>4} {'sumM_k (n=1)':>16} {'sumM_k (n=13)':>16} {'最佳 RMS':>11} {'α':>10} {'判定':>8}")
print("-" * 72)
kres = {}
for k in range(1, 13):
    vals = [KCAND[k][n] for n in M9]
    b = rms_best(vals)
    if b is None: continue
    kres[k] = b[0]
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    mark = "  ★★ B=4!" if k == 4 else ""
    print(f"{k:>4} {KCAND[k][1]:>16.6e} {KCAND[k][13]:>16.6e} {b[0]:>11.4f} {b[2]:>10.4f} {flag:>8}{mark}")

bestk = min(kres.items(), key=lambda kv: kv[1])
print(f"\n★ 最佳 k = {bestk[0]} (RMS {bestk[1]:.4f})")
print(f"★ k = 4 之 RMS = {kres.get(4, float('nan')):.4f}, 排名 = {sorted(kres.values()).index(kres[4])+1 if 4 in kres else '—'}/{len(kres)}")
print(f"★ 對照: docs/23 報 sumM2 = 0.9482 (單調配對) | |Δm| 0.5873 | sin 0.8028 | 上限 3.8588")

# ═══ (B) 4 幀閉環讀法: m ∝ |⟨O|n⟩|^4 ═════════════════
print(f"\n{'─'*96}\n(B) 4 幀閉環讀法 (O→X→O 來回, 4 幀): m ∝ |⟨O|n⟩|^4\n{'─'*96}")
beta_n0 = np.arccos(np.clip(U @ cold, -1, 1))
C4 = {}
for n in M9:
    c = np.cos(n*beta_n0/2)**2
    C4[n] = c
cands_b = {
    "(b1) Σ_i c^4": [float((C4[n]**4).sum()) for n in M9],
    "(b2) Σ_i c^{−4}": [float((C4[n]**(-4)).sum()) for n in M9],
    "(b3) (Σ_i c)^4": [float(C4[n].sum()**4) for n in M9],
    "(b4) Σ_i c^2 (2幀)": [float((C4[n]**2).sum()) for n in M9],
    "(b5) Σ_i c^{−2} (2幀)": [float((C4[n]**(-2)).sum()) for n in M9],
}
print(f"\n{'候選':>22} {'最佳 RMS':>11} {'m 範圍':>12} {'判定':>8}")
print("-" * 58)
for name, vals in cands_b.items():
    vv = np.abs(np.array(vals))
    rng = vv.max()/vv.min() if vv.min() > 1e-300 else float('inf')
    b = rms_best(vals)
    if b is None: print(f"{name:>22} {'退化':>11} {rng:>12.3g} {'🔴':>8}"); continue
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    print(f"{name:>22} {b[0]:>11.4f} {rng:>12.3g} {flag:>8}")

# ═══ (C) 4 幀自洽不動點 ══════════════════════════════
print(f"\n{'─'*96}\n(C) 4 幀自洽不動點: 解 m = g^4(m)\n{'─'*96}")
# g(m) = λ·Σ_m' |V_nm'|²·m'/(E_m'² + m'²) 形式之 4 重迭代
Nc = 44
xx = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1): Psi[:, n-1] = np.sin(n*math.pi*xx/(Nc+1))
for n in range(Nc): Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(xx - xx.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])

def iterate4(lam, m0=None, iters=200):
    m = np.ones(Nc)*0.01 if m0 is None else m0.copy()
    for _ in range(iters):
        for _f in range(4):                      # ★ 4 幀
            new = np.zeros(Nc)
            for a in range(Nc):
                s = 0.0
                for b in range(Nc):
                    if b == a: continue
                    s += V[a,b]**2 * m[b]/(E[b]**2 + m[b]**2)
                new[a] = lam*s
            mx = np.max(np.abs(new))
            if mx < 1e-300: return None
            m = new/mx
    return m

print(f"\n{'λ':>10} {'4 幀迭代 m 範圍':>24} {'最佳 RMS':>11} {'判定':>8}")
print("-" * 58)
cres = {}
for lam in [0.5, 1.0, 2.0, 5.0, 10.0]:
    m = iterate4(lam)
    if m is None: continue
    vals = [abs(m[n-1]) for n in M9]
    b = rms_best(vals)
    rng = max(vals)/max(min(vals), 1e-300)
    if b is None: print(f"{lam:>10.2f} {rng:>24.3e} {'退化':>11} {'🔴':>8}"); continue
    cres[lam] = b[0]
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    print(f"{lam:>10.2f} {rng:>24.3e} {b[0]:>11.4f} {flag:>8}")

# ═══ 保存 ═══
with open(OUT/"52_b4_four_frame_test.json", "w") as f:
    json.dump({
        "k_scan": {str(k): {"rms": kres[k]} for k in kres},
        "k4_rms": kres.get(4),
        "best_k": bestk[0], "best_k_rms": bestk[1],
        "k4_rank": sorted(kres.values()).index(kres[4])+1 if 4 in kres else None,
        "n_k": len(kres),
        "closed_loop": {k: {"rms": (rms_best(v)[0] if rms_best(v) else None)} for k, v in cands_b.items()},
        "fixed_point_4frame": {str(k): v for k, v in cres.items()},
        "reference": {"sumM2_docs23": 0.9482, "2nd_order": 0.5873, "sin": 0.8028, "upper": float(LM.std())},
    }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/52_b4_four_frame_test.json")