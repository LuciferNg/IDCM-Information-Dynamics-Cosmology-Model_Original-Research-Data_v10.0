#!/usr/bin/env python3
"""
O136 — Script 48: 集體激發 — 9×9 有效 Hamiltonian (Löwdin downfolding)
================================================================================
docs/26 §六 候選 #3: 「質量係集體激發 (非單模)」

具體化:
  44 模式經世界-觀察者耦合 V (位置算子, 精確 Z₂-奇) 連通
  A₅ 選出嘅 9 模式 = 慢子空間 (relevant); 其餘 35 = 快 (integrated out)
  ⟹ 9×9 有效 Hamiltonian H_eff 嘅本徵值 = 質量

  Löwdin downfolding (非微擾, 精確):
    H_eff(E) = E_sel + V_ss + V_sr (E − E_rr)^{-1} V_rs
    自洽: 解 H_eff(E) x = E x  (E 為本徵值) → 等價於完整 44×44 對角化嘅子空間投影

  亦測試: 完整 44×44 對角化, 取最接近 9 選模式嘅本徵值

比較基準: 二階自能 RMS 0.5873 (最佳); sin 最佳配對 0.8028; 上限 3.8588
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2; ph2 = phi**2
ND = 44

MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])
M9 = [1,2,3,4,5,7,9,11,13]

# ── 幾何 ──
Nc = 44
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])

sel = [n-1 for n in M9]                 # 0-based
rest = [i for i in range(Nc) if i not in sel]

print("=" * 96)
print("O136 Script 48: 集體激發 — 9×9 有效 Hamiltonian (Löwdin downfolding)")
print("=" * 96)

# ═══ 1. Löwdin downfolding ═══════════════════════════
print(f"\n{'─'*96}\n1. Löwdin downfolding: H_eff(E) = E_ss + λV_ss + λ²V_sr (E − E_rr)⁻¹ V_rs")
print(f"{'─'*96}")

def lowdin_eigs(lam, iters=500, tol=1e-13):
    """自洽解 9 個本徵值: 對每個試探 E 解廣義問題
    等價做法: 完整 44×44 對角化後, 取與 9 選模式重疊最大嘅 9 個本徵態"""
    H = np.diag(E) + lam*V
    w, u = np.linalg.eigh(H)
    # 用「與選定模式子空間嘅重疊」揀 9 個
    P = np.zeros(Nc)
    for i in sel:
        e = np.zeros(Nc); e[i] = 1.0
        # 投影到本徵基
        ov = np.array([abs(np.dot(u[:, k], e))**2 for k in range(Nc)])
        P += ov
    idx = np.argsort(-P)[:9]
    return np.sort(w[idx]), w, u

print(f"\n{'λ':>10} {'9 個有效本徵值':>56} {'範圍':>12}")
print("-" * 82)
collective = {}
for lam in [1/45, 1/22, 1/11, 1/4, 1.0, 2.0]:
    ev, w, u = lowdin_eigs(lam)
    collective[lam] = ev
    rng = (ev.max()-ev.min())/max(abs(ev.min()), 1e-12)
    print(f"{lam:>10.5f} " + " ".join(f"{v:>6.4f}" for v in ev) + f" {rng:>12.2f}")

# ═══ 2. 譜形檢驗 ════════════════════════════════════
print(f"\n{'─'*96}\n2. 譜形檢驗 (RMS, 最佳配對)\n{'─'*96}")

def best_pairing(vals, topk=3):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v)
    best = []
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        best.append((rms, perm, float(c[1])))
    best.sort()
    return best[:topk]

print(f"\n{'候選':>26} {'最佳 RMS':>11} {'α':>9} {'配對 (粒子→模式)':>38}")
print("-" * 88)
res = {}
for lam, ev in collective.items():
    b = best_pairing(ev)
    if b is None: continue
    rms, perm, a = b[0]
    res[f"集體 λ={lam:.5f}"] = (rms, perm, a)
    ps = " ".join(f"{SP[i][0]}:{M9[perm[i]]}" for i in range(9))
    print(f"{'集體 λ='+f'{lam:.5f}':>26} {rms:>11.4f} {a:>9.4f} {ps:>38}")

# 對照
for name, vals in [("sin(nπ/88)", [math.sin(n*math.pi/88) for n in M9]),
                   ("|Δm| 二階自能", None)]:
    if vals is None:
        SE = []
        for n in M9:
            t = 0.0
            for m in range(Nc):
                if m == n-1 or (m-(n-1)) % 2 == 0: continue
                dE = E[n-1]-E[m]
                if abs(dE) < 1e-12: continue
                t += V[n-1, m]**2/dE
            SE.append(abs(t))
        vals = SE
    b = best_pairing(vals)
    ps = " ".join(f"{SP[i][0]}:{M9[b[0][1][i]]}" for i in range(9))
    print(f"{name:>26} {b[0][0]:>11.4f} {b[0][2]:>9.4f} {ps:>38}")

print(f"\n★ 無解釋上限 = {LM.std():.4f}")

# ═══ 3. ★ 集體【乘積】形式 ═══════════════════════════
print(f"\n{'─'*96}\n3. ★ 集體乘積形式: m_p ∝ Π_{{k ∈ block_p}} f(k)\n{'─'*96}")

# 分塊: 代數次數層 (docs/16)
def deg(n):
    if n % 11 == 0: return {11:4,22:2,33:4,44:1}[n]
    v = 0; m = n
    while m % 2 == 0: m //= 2; v += 1
    return 40 // (2**min(v,3))
LAYERS = {}
for n in range(1,45): LAYERS.setdefault(deg(n), []).append(n)
print("  代數次數層:", {k: len(v) for k, v in sorted(LAYERS.items(), reverse=True)})
sel_deg = {n: deg(n) for n in M9}
print("  9 選模式之層:", {n: deg(n) for n in M9})

# 候選 1: m_p ∝ Π_{k ≤ n_p, 11∤k} sin(kπ/88)   (累積乘積)
c1 = []
for n in M9:
    p = 1.0
    for k in range(1, n+1):
        if k % 11: p *= math.sin(k*math.pi/88)
    c1.append(p)
# 候選 2: m_p ∝ Π_{k ∈ layer(n_p)} sin(kπ/88)
c2 = [float(np.prod([math.sin(k*math.pi/88) for k in LAYERS[deg(n)]])) for n in M9]
# 候選 3: m_p ∝ Π_{k: v₂(k)=v₂(n)} sin(kπ/88)
def v2(n):
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c
c3 = [float(np.prod([math.sin(k*math.pi/88) for k in range(1,45) if v2(k) == v2(n)])) for n in M9]

for name, vals in [("累積乘積 Π_{k≤n}", c1), ("層乘積 Π_{layer}", c2), ("v₂ 乘積", c3)]:
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): print(f"{name:>26} 含零 — 跳過"); continue
    b = best_pairing(vals)
    ps = " ".join(f"{SP[i][0]}:{M9[b[0][1][i]]}" for i in range(9))
    print(f"{name:>26} {b[0][0]:>11.4f} {b[0][2]:>9.4f} {ps:>38}")

# ═══ 4. 保存 ════════════════════════════════════════
best_all = sorted([(v[0], k) for k, v in res.items()])
with open(OUT/"48_collective_excitation.json", "w") as f:
    json.dump({
        "lowdin_spectra": {f"{k:.6f}": v.tolist() for k, v in collective.items()},
        "rms": {k: {"rms": v[0], "alpha": v[2],
                    "pairing": {SP[i]: M9[v[1][i]] for i in range(9)}} for k, v in res.items()},
        "best_collective": {"name": best_all[0][1], "rms": best_all[0][0]} if best_all else None,
        "reference": {"2nd_order": 0.5873, "sin": 0.8028, "upper": float(LM.std())},
    }, f, ensure_ascii=False, indent=2)
print(f"\n★ 集體方案最佳: {best_all[0][1]}  RMS = {best_all[0][0]:.4f}")
print(f"✅ 寫入 data/48_collective_excitation.json")