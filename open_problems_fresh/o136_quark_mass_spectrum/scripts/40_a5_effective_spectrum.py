#!/usr/bin/env python3
"""
O136 — Script 40: A₅ 有效作用量的完整譜 (非二階微擾)
================================================================
O80 結果: ΔE_n = −κ²ω_n ∝ sin(nπ/88)   ← 二階自能
O81 結果: m_eff_n²(ρ,θ) = 2κω_n ρ cos(θ−θ_n)  ← 高斯積分
          → m_eff_n ∝ sqrt(ω_n) ∝ sqrt(sin(nπ/88))  ★ 不同譜形!

本 script:
  1. 建立 A₅ Laplacian (60×60) + 譜
  2. 模式 n 投影 c_{i,n} 與 Laplacian 本徵模的重疊
  3. 高階自能候選 (Σ_k o_k²·f(λ_k))
  4. 檢驗譜形

關鍵: A₅ 譜係離散的結構譜 (λ_max = 4+φ², λ₂ = φ⁻²)
      模式與 Laplacian 模的重疊可能編碼質量
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"

phi = (1+math.sqrt(5))/2
mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])
pairs_idx = list(itertools.combinations(range(9),2))
lmd = np.array([LM[i]-LM[j] for i,j in pairs_idx])

print("=" * 96)
print("O136 Script 40: A₅ 有效作用量的完整譜")
print("=" * 96)

# ═══ 1. A₅ 圖 + Laplacian ═══════════════════════════
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
cold = U[0].copy()

col = {}
for line in (DATA/"anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])
dist = np.arccos(np.clip(U@U.T,-1,1))
edges = [(i,j) for i in range(60) for j in range(i+1,60) if dist[i,j] < np.radians(28.0)]

A = np.zeros((60,60))
for i,j in edges: A[i,j]=A[j,i]=1
Dg = np.diag(A.sum(axis=1))
Lap = Dg - A
ev, evec = np.linalg.eigh(Lap)

print(f"\n{'─'*96}")
print("1. A₅ Laplacian 譜")
print(f"{'─'*96}")
print(f"\n節點 60, 邊 {len(edges)}, 度分佈 {dict(zip(*np.unique(A.sum(axis=1).astype(int), return_counts=True)))}")
print(f"\nλ 範圍: [{ev.min():.8f}, {ev.max():.8f}]")
print(f"⟨λ⟩ = 2E/V = {2*len(edges)/60:.8f}")
print(f"λ_max = {ev.max():.8f}   4+φ² = {4+phi**2:.8f}  {'✅' if abs(ev.max()-(4+phi**2))<1e-8 else '🔴'}")
print(f"λ₂ = {ev[1]:.8f}   φ⁻² = {phi**-2:.8f}  {'✅' if abs(ev[1]-phi**-2)<1e-8 else '🔴'}")

# 譜簡併結構
print(f"\n前 12 個本徵值: {[round(float(x),6) for x in ev[:12]]}")
uniq, cnt = np.unique(np.round(ev, 6), return_counts=True)
print(f"\n相異能階數: {len(uniq)}")
print(f"相異能階: {[round(float(x),6) for x in uniq]}")
print(f"簡併度: {list(cnt.astype(int))}")

# ═══ 2. 模式投影 ═════════════════════════════════════
beta = np.arccos(np.clip(U@cold,-1,1))
def cvec(n): return np.cos(n*beta/2)**2

print(f"\n{'─'*96}")
print("2. 模式投影 c_{i,n} 與 Laplacian 本徵模的重疊")
print(f"{'─'*96}")

def overlaps(n):
    c = cvec(n)
    c0 = c - c.mean()          # 去常數部分
    o = np.array([float(np.dot(evec[:,k], c0)) for k in range(60)])
    return o

print(f"\n{'n':>3} {'⟨c⟩':>10} {'‖c−⟨c⟩‖':>12} {'最大 |o_k|':>12} {'主導 k':>8}")
print("-" * 50)
OV = {}
for n in M9:
    c = cvec(n); c0 = c - c.mean()
    o = overlaps(n)
    k = int(np.argmax(np.abs(o)))
    OV[n] = o
    print(f"{n:>3} {c.mean():>10.6f} {np.linalg.norm(c0):>12.6f} {np.abs(o).max():>12.6f} {k:>8}")

# ═══ 3. ★ 高階自能候選 ══════════════════════════════
print(f"\n{'─'*96}")
print("3. ★ 高階自能候選: Δm_n = Σ_k o_k²·f(λ_k)")
print(f"{'─'*96}")

def selfE(n, form):
    o = OV[n]
    lam = ev.copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        if form == "1/lambda": f = np.where(lam>1e-12, 1.0/np.maximum(lam,1e-12), 0.0)
        elif form == "1/sqrt": f = np.where(lam>1e-12, 1.0/np.sqrt(np.maximum(lam,1e-12)), 0.0)
        elif form == "log":    f = np.log(np.maximum(lam,1e-12))
        elif form == "1":      f = np.ones(60)
        elif form == "lambda": f = lam
        elif form == "1/(1+lambda)": f = 1.0/(1.0+lam)
        elif form == "exp(-lambda)": f = np.exp(-lam)
        elif form == "1/(m2+lambda)": f = 1.0/(2.0+lam)
    return float(np.sum(o**2 * f))

forms = ["1/lambda","1/sqrt","log","1","lambda","1/(1+lambda)","exp(-lambda)","1/(m2+lambda)"]
print(f"\n{'n':>3} " + " ".join(f"{f:>13}" for f in forms))
print("-" * (4+14*len(forms)))
SE = {}
for n in M9:
    SE[n] = {f: selfE(n,f) for f in forms}
    print(f"{n:>3} " + " ".join(f"{SE[n][f]:>13.6f}" for f in forms))

# ═══ 4. ★ 譜形檢驗 ══════════════════════════════════
print(f"\n{'─'*96}")
print("4. ★ 譜形檢驗 (RMS 殘差, 單調配對)")
print(f"{'─'*96}")

def fit_rms(vals):
    v = np.array(vals)
    if np.any(v <= 0): return None
    X = np.log(v); order = np.argsort(X); Xp = X[order]
    Amat = np.vstack([np.ones(9), Xp]).T
    c,*_ = np.linalg.lstsq(Amat, LM, rcond=None)
    return float(np.sqrt(np.mean((Amat@c-LM)**2))), float(c[1])

print(f"\n{'候選':>16} {'RMS':>10} {'α':>12} {'判定':>8}")
print("-" * 50)
cands = {"sin(nπ/88)": [math.sin(n*math.pi/88) for n in M9],
         "sqrt(sin)": [math.sqrt(math.sin(n*math.pi/88)) for n in M9]}
for f in forms:
    cands[f"selfE {f}"] = [SE[n][f] for n in M9]
for name, vals in cands.items():
    r = fit_rms(vals)
    if r is None: 
        print(f"{name:>16} {'非正':>10}"); continue
    rms, a = r
    v = '🟢' if rms<0.3 else ('🟡' if rms<1.0 else '🔴')
    print(f"{name:>16} {rms:>10.4f} {a:>12.5f} {v:>8}")
print(f"\n無解釋上限 (ln m 標準差) = {LM.std():.4f}")

# ═══ 5. 保存 ════════════════════════════════════════
with open(OUT/"40_a5_effective_spectrum.json","w") as f:
    json.dump({
        "laplacian_spectrum": [round(float(x),8) for x in ev],
        "n_distinct_levels": int(len(uniq)),
        "lambda_max": float(ev.max()), "lambda2": float(ev[1]),
        "self_energies": {str(n): SE[n] for n in M9},
        "overlaps_norm": {str(n): float(np.linalg.norm(OV[n])) for n in M9},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/40_a5_effective_spectrum.json")