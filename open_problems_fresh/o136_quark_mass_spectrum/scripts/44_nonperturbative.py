#!/usr/bin/env python3
"""
O136 — Script 44: 非微擾 Dyson 自洽 + 結構障礙定理
================================================================
Script 41-43 結果: 二階 PT 發散 (Δm=4310 ≫ 能階間距 0.8) → 微擾展開本身錯
→ 本 script 攻非微擾:

  (A) ★ 結構障礙: 質量比值 vs γ 比值的相關性 (單調函數可否?)
  (B) 精確對角化 H = diag(E_n) + λ·X, 結構 λ 值
  (C) Dyson 自洽 m² = E² + Σ(m²)
  (D) Gap 方程 m_n = g·Σ_m |V_nm|²·m_m/(E_m²+m_m²)
  (E) ★ 局域化 (Wannier-Stark) 體積 1/IPR
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2
mu2 = 2.0
mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])
MR = np.array([mass[sp[i+1]]/mass[sp[i]] for i in range(8)])

# 幾何
Nc = 44
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])
GR = np.array([E[M9[i+1]-1]/E[M9[i]-1] for i in range(8)])

print("=" * 94)
print("O136 Script 44: 非微擾 Dyson 自洽 + 結構障礙定理")
print("=" * 94)

# ═══ (A) ★ 結構障礙 ═════════════════════════════════
print(f"\n{'─'*94}")
print("(A) ★★ 結構障礙: 單調函數 m = f(n) 可否?")
print(f"{'─'*94}")

print(f"\n{'i':>2} {'n_i→n_j':>10} {'γ 比值':>10} {'質量比值':>10} {'ln(質量比值)':>14}")
print("-" * 52)
for i in range(8):
    print(f"{i+1:>2} {M9[i]:>4}→{M9[i+1]:<4} {GR[i]:>10.4f} {MR[i]:>10.4f} {math.log(MR[i]):>14.4f}")

r_gm = float(np.corrcoef(GR, MR)[0,1])
r_glm = float(np.corrcoef(GR, np.log(MR))[0,1])
r_lglm = float(np.corrcoef(np.log(GR), np.log(MR))[0,1])
print(f"\n相關係數:")
print(f"  corr(γ比值, 質量比值)      = {r_gm:>8.4f}")
print(f"  corr(γ比值, ln質量比值)    = {r_glm:>8.4f}")
print(f"  corr(lnγ比值, ln質量比值)  = {r_lglm:>8.4f}")

print(f"\n★ 單調函數 m=f(n) 的【充分條件】: ln(質量比值)/ln(γ比值) 為常數")
print(f"\n{'i':>2} {'ln(m比值)/ln(γ比值)':>22}")
print("-" * 26)
ratios_alpha = [math.log(MR[i])/math.log(GR[i]) for i in range(8)]
for i, a in enumerate(ratios_alpha):
    print(f"{i+1:>2} {a:>22.4f}")
print(f"\n  範圍 = [{min(ratios_alpha):.4f}, {max(ratios_alpha):.4f}]")
print(f"  標準差 = {np.std(ratios_alpha):.4f}")
print(f"  ★ 若 α 非常數 ⟹ 純冪律 m ∝ γ^α 不可能")
print(f"  ★ α 需為常數才可; 實測跨度 {max(ratios_alpha)/max(min(ratios_alpha),1e-9):.1f}×")

# ═══ (B) 精確對角化 ═════════════════════════════════
print(f"\n{'─'*94}")
print("(B) 精確對角化 H = diag(E_n) + λ·X, 結構 λ 值")
print(f"{'─'*94}")

def diag_spectrum(lam):
    H = np.diag(E) + lam*V
    ev, evec = np.linalg.eigh(H)
    return ev, evec

lam_struct = {"1/45 (g)": 1/45, "μ²/Σγ": 2/90, "1/88": 1/88, "μ²/44": 2/44,
              "1/11": 1/11, "φ⁻¹": 1/phi, "1/4": 0.25, "1": 1.0}
print(f"\n{'λ 名':>12} {'λ':>10} {'譜範圍':>22} {'比值範圍':>12}")
print("-" * 60)
lam_spectra = {}
for name, lam in lam_struct.items():
    ev, _ = diag_spectrum(lam)
    pos = ev[ev > 1e-9]
    rng = f"[{ev.min():.4f}, {ev.max():.4f}]"
    rr = f"{abs(ev.max()/ev.min()):.2f}×" if abs(ev.min())>1e-9 else "∞"
    print(f"{name:>12} {lam:>10.5f} {rng:>22} {rr:>12}")
    lam_spectra[name] = {"lam": lam, "ev": ev.tolist()}

# ═══ (C) Dyson 自洽 ═════════════════════════════════
print(f"\n{'─'*94}")
print("(C) Dyson 自洽 m_n² = E_n² + Σ_m |V_nm|²·E_m/(E_m² − m_n²)")
print(f"{'─'*94}")

def dyson(g, iters=2000, tol=1e-12):
    """自洽解: m² = E² + g²·Σ_m |V_nm|²·E_m/(E_m² − m²)"""
    m2 = E**2 + 1e-6
    for it in range(iters):
        new = np.zeros(Nc)
        for n in range(Nc):
            s = 0.0
            for m in range(Nc):
                if m == n: continue
                den = E[m]**2 - m2[n]
                if abs(den) < 1e-14: den = 1e-14
                s += V[n, m]**2 * E[m] / den
            new[n] = E[n]**2 + g**2 * s
        if np.max(np.abs(new - m2)) < tol: break
        m2 = 0.5*m2 + 0.5*np.maximum(new, 1e-12)
    return np.sqrt(np.maximum(m2, 0)), it

print(f"\n{'g':>10} {'收斂':>6} {'m_1':>14} {'m_13':>14} {'範圍':>12}")
print("-" * 60)
dyson_res = {}
for g in [1/45, 1/22, 0.1, 0.2, 0.5, 1.0]:
    m, it = dyson(g)
    vals = [m[n-1] for n in M9]
    rng = max(vals)/max(min(vals), 1e-12)
    print(f"{g:>10.5f} {it:>6} {vals[0]:>14.6f} {vals[-1]:>14.6f} {rng:>12.2f}×")
    dyson_res[str(g)] = vals

# ═══ (D) Gap 方程 ══════════════════════════════════
print(f"\n{'─'*94}")
print("(D) Gap 方程 m_n = g·Σ_m |V_nm|²·m_m/(E_m²+m_m²)  [冪法]")
print(f"{'─'*94}")

def gap_eq(g, iters=5000):
    """m = g·K(g)·m 形式 → 冪法求主本徵向量"""
    m = np.ones(Nc)
    for it in range(iters):
        new = np.zeros(Nc)
        for n in range(Nc):
            s = 0.0
            for mm in range(Nc):
                if mm == n: continue
                s += V[n, mm]**2 * m[mm] / (E[mm]**2 + m[mm]**2)
            new[n] = g * s
        nrm = np.max(np.abs(new))
        if nrm < 1e-300: return None, it
        new = new / nrm
        if np.max(np.abs(new - m)) < 1e-14:
            m = new; break
        m = new
    return m, it

print(f"\n{'g':>10} {'m 範圍':>24} {'比值範圍':>12}")
print("-" * 50)
gap_res = {}
for g in [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
    m, it = gap_eq(g)
    if m is None: continue
    vals = [abs(m[n-1]) for n in M9]
    rng = max(vals)/max(min(vals), 1e-300)
    print(f"{g:>10.2f} {f'[{min(vals):.6e}, {max(vals):.6e}]':>24} {rng:>12.3e}×")
    gap_res[str(g)] = vals

# ═══ (E) ★ 局域化體積 ═══════════════════════════════
print(f"\n{'─'*94}")
print("(E) ★ Wannier-Stark 局域化: 1/IPR (局域化體積)")
print(f"{'─'*94}")

print(f"\n{'λ 名':>12} " + " ".join(f"{'n='+str(n):>11}" for n in M9))
print("-" * (13 + 12*len(M9)))
ipr_res = {}
for name, lam in [("1/45", 1/45), ("1/11", 1/11), ("0.25", 0.25), ("1.0", 1.0)]:
    ev, evec = diag_spectrum(lam)
    vals = []
    for n in M9:
        # 取與 free mode n 最接近的本徵態
        psi = evec[:, n-1]
        ipr = float(np.sum(psi**4))
        vals.append(1.0/ipr)
    ipr_res[name] = vals
    print(f"{name:>12} " + " ".join(f"{v:>11.4f}" for v in vals))

# ═══ (F) 譜形檢驗 ══════════════════════════════════
print(f"\n{'─'*94}")
print("(F) 譜形檢驗 (RMS, 最佳配對)")
print(f"{'─'*94}")

def best_pairing(vals, topk=1):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v)
    best = []
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c,*_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        best.append((rms, perm))
    best.sort()
    return best[:topk]

cands = {"sin(nπ/88)": [math.sin(n*math.pi/88) for n in M9]}
for name, d in lam_spectra.items():
    cands[f"diag λ={name}"] = [d["ev"][n-1] for n in M9]
for g, vals in dyson_res.items():
    cands[f"Dyson g={g}"] = vals
for g, vals in gap_res.items():
    cands[f"Gap g={g}"] = vals
for name, vals in ipr_res.items():
    cands[f"1/IPR λ={name}"] = vals

print(f"\n{'候選':>20} {'最佳 RMS':>12} {'配對':>34}")
print("-" * 70)
allres = []
for name, vals in cands.items():
    b = best_pairing(vals)
    if b is None: continue
    rms, perm = b[0]
    allres.append((rms, name, perm))
    ps = " ".join(f"{sp[i][0]}:{M9[perm[i]]}" for i in range(9))
    print(f"{name:>20} {rms:>12.4f} {ps:>34}")
allres.sort()
print(f"\n無解釋上限 = {LM.std():.4f}")
print(f"★ 最佳: {allres[0][1]}, RMS = {allres[0][0]:.4f}")
print(f"★ 對照: 二階自能 0.5873 | sin 譜 1.1178")

# ═══ 保存 ═══════════════════════════════════════════
with open(OUT/"44_nonperturbative.json","w") as f:
    json.dump({
        "obstruction": {"gamma_ratios": GR.tolist(), "mass_ratios": MR.tolist(),
                        "alpha_per_pair": ratios_alpha,
                        "alpha_range": [min(ratios_alpha), max(ratios_alpha)],
                        "corr_gamma_mass": r_gm, "corr_lngamma_lnmass": r_lglm},
        "best": {"rms": allres[0][0], "candidate": allres[0][1],
                 "pairing": {sp[i]: M9[allres[0][2][i]] for i in range(9)}},
        "reference": {"2nd_order": 0.5873, "sin": 1.1178, "upper": float(LM.std())},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 寫入 data/44_nonperturbative.json")