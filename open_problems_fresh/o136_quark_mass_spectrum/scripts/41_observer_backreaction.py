#!/usr/bin/env python3
"""
O136 — Script 41: 質量 = 觀察↔被觀察交互 (二階自能)
================================================================
用戶洞察: 「質量來自觀察和被觀察的交互」

IDCM 現成結構:
  88-site 對偶鏈 = 44 World (even modes) + 44 Observer (odd modes)
  Σγ_even = 46 (世界), Σγ_odd = 44 = N_d (觀察者), 差 = μ² = 2
  Z₂-奇耦合 (O203 §三 C2): L = g(φ_w∂φ_o − φ_o∂φ_w), g = 1/45

O203 判定: 質量譜對【一階】漂移結構性盲 (k=0 時耦合消失)
→ 但【二階】自能 (觀察者反作用) 未測試! ★ 本 script 攻此

模型:
  H = H_0 + V,  V = Z₂-奇算子 (連接奇偶模式)
  二階自能: Δm_n = Σ_{m: parity(m)≠parity(n)} |V_nm|²/(E_n − E_m)
"""
import numpy as np, math, json, itertools
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
OUT = Path(__file__).parent.parent / "data"

mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])
pairs_idx = list(itertools.combinations(range(9),2))
lmd = np.array([LM[i]-LM[j] for i,j in pairs_idx])

print("=" * 96)
print("O136 Script 41: 質量 = 觀察↔被觀察交互 (二階自能)")
print("=" * 96)

# ═══ 1. 對偶鏈結構 ═══════════════════════════════════
print(f"\n{'─'*96}")
print("1. 88-site 對偶鏈 + 世界/觀察者扇區")
print(f"{'─'*96}")

N = 88
# 176-鏈譜 (O34 權威): γ_k = 4sin²(πk/176), k=1..88
gamma176 = np.array([4*math.sin(math.pi*k/176)**2 for k in range(1, 89)])
even_sum = sum(gamma176[k] for k in range(88) if (k+1) % 2 == 0)   # k 偶
odd_sum  = sum(gamma176[k] for k in range(88) if (k+1) % 2 == 1)   # k 奇
print(f"\n176-鏈譜 γ_k = 4sin²(πk/176), k=1..88")
print(f"Σγ_even = {even_sum:.6f}  (世界扇區)")
print(f"Σγ_odd  = {odd_sum:.6f}  (觀察者扇區 = N_d)")
print(f"差 = {even_sum-odd_sum:.6f}  = μ² = 2  {'✅' if abs(even_sum-odd_sum-2)<1e-9 else '🔴'}")

# 44-鏈譜 (O136 慣例): γ_n = 4sin²(nπ/88)
gamma44 = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])
print(f"\n44-鏈譜 γ_n = 4sin²(nπ/88), n=1..44")
print(f"Σγ = {gamma44.sum():.6f} (= 90)")
print(f"Σγ_odd(n奇) = {sum(gamma44[n-1] for n in range(1,45) if n%2==1):.6f}")
print(f"Σγ_even(n偶) = {sum(gamma44[n-1] for n in range(1,45) if n%2==0):.6f}")

# ═══ 2. ★ 對偶鏈 Hamiltonian + Z₂-奇耦合 ═════════════
print(f"\n{'─'*96}")
print("2. ★ 對偶鏈 Hamiltonian: 位置算子作 Z₂-奇耦合")
print(f"{'─'*96}")

# D-D 鏈: ψ_n(i) = sin(nπi/(N+1)), i=1..N
Nc = 88
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
# 正交化歸一
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])

# 位置算子 (Z₂-奇: 連接 |n-m| 奇)
X = np.diag(x - x.mean())
Vnm = Psi.T @ X @ Psi     # ⟨n|x|m⟩
print(f"\n位置算子 ⟨n|x|m⟩ 的結構:")
print(f"  max |V_nm| (n≠m, |n−m| 偶) = {max(abs(Vnm[n,m]) for n in range(20) for m in range(20) if n!=m and (n-m)%2==0):.3e}  (應 ≈0)")
print(f"  max |V_nm| (n≠m, |n−m| 奇) = {max(abs(Vnm[n,m]) for n in range(20) for m in range(20) if (n-m)%2==1):.3e}")

# 能量 (176-鏈, 取前 88 或 44)
E176 = np.array([4*math.sin(math.pi*k/176)**2 for k in range(1, 89)])

# ═══ 3. ★★ 二階自能 ═════════════════════════════════
print(f"\n{'─'*96}")
print("3. ★★ 二階自能: Δm_n = Σ_m |V_nm|²/(E_n − E_m)")
print(f"{'─'*96}")

def selfE2(n_idx, E, V, w=None):
    """2nd-order self-energy for mode index n_idx (0-based)"""
    tot = 0.0
    for m in range(len(E)):
        if m == n_idx: continue
        if (m - n_idx) % 2 == 0: continue      # 只連接相反 parity
        dE = E[n_idx] - E[m]
        if abs(dE) < 1e-12: continue
        tot += V[n_idx, m]**2 / dE
    return tot

print(f"\n{'n':>3} {'γ_n (44鏈)':>12} {'Δm (176鏈)':>14} {'Δm (44鏈)':>14} {'Δm (γ²)':>14}")
print("-" * 62)

# 44-鏈版本
Nc44 = 44
x44 = np.arange(1, Nc44+1, dtype=float)
Psi44 = np.zeros((Nc44, Nc44))
for n in range(1, Nc44+1):
    Psi44[:, n-1] = np.sin(n*math.pi*x44/(Nc44+1))
for n in range(Nc44):
    Psi44[:, n] /= np.linalg.norm(Psi44[:, n])
X44 = np.diag(x44 - x44.mean())
V44 = Psi44.T @ X44 @ Psi44

SE = {}
for n in M9:
    d1 = selfE2(n-1, E176[:88], np.block([[Vnm, np.zeros((88,0))],[np.zeros((0,88)), np.zeros((0,0))]]) if False else Vnm)
    d2 = selfE2(n-1, gamma44, V44)
    d3 = selfE2(n-1, gamma44**2, V44)
    SE[n] = {"E176": d1, "E44": d2, "E44sq": d3}
    print(f"{n:>3} {gamma44[n-1]:>12.6f} {d1:>14.8f} {d2:>14.8f} {d3:>14.8f}")

# ═══ 4. ★ 譜形檢驗 ══════════════════════════════════
print(f"\n{'─'*96}")
print("4. ★ 譜形檢驗 (RMS 殘差)")
print(f"{'─'*96}")

def fit_rms(vals, absval=True):
    v = np.array([abs(x) for x in vals]) if absval else np.array(vals)
    if np.any(v <= 0): return None
    X = np.log(v); order = np.argsort(X); Xp = X[order]
    A = np.vstack([np.ones(9), Xp]).T
    c,*_ = np.linalg.lstsq(A, LM, rcond=None)
    return float(np.sqrt(np.mean((A@c-LM)**2))), float(c[1])

print(f"\n{'候選':>22} {'RMS':>10} {'α':>12} {'判定':>8}")
print("-" * 56)
cands = {"sin(nπ/88)": [math.sin(n*math.pi/88) for n in M9],
         "cos(nπ/88) (v_g)": [math.cos(n*math.pi/88) for n in M9]}
for k in ["E176","E44","E44sq"]:
    cands[f"Δm 2nd-order {k}"] = [SE[n][k] for n in M9]
for name, vals in cands.items():
    r = fit_rms(vals)
    if r is None:
        print(f"{name:>22} {'非正':>10}"); continue
    rms, a = r
    v = '🟢' if rms<0.3 else ('🟡' if rms<1.0 else '🔴')
    print(f"{name:>22} {rms:>10.4f} {a:>12.5f} {v:>8}")
print(f"\n無解釋上限 (ln m 標準差) = {LM.std():.4f}")

# ═══ 5. ★★ 全配對搜索 ═══════════════════════════════
print(f"\n{'─'*96}")
print("5. ★★ 全配對搜索 (最佳候選)")
print(f"{'─'*96}")

best = []
for name, vals in cands.items():
    v = np.array([abs(x) for x in vals])
    if np.any(v <= 0): continue
    X = np.log(v)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c,*_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        best.append((rms, name, perm, c[1]))
best.sort(key=lambda z: z[0])
print(f"\n最佳 5 個:")
print(f"\n{'RMS':>9} {'候選':>22} {'配對 (模式→粒子)':>40}")
print("-" * 74)
for rms, name, perm, a in best[:5]:
    ps = " ".join(f"{p}:{M9[i]}" for p, i in zip(sp, perm))
    print(f"{rms:>9.4f} {name:>22} {ps:>40}")
print(f"\n★ 最佳 RMS = {best[0][0]:.4f}  (對照 sin 譜 1.1178)")

# ═══ 6. 保存 ════════════════════════════════════════
with open(OUT/"41_observer_backreaction.json","w") as f:
    json.dump({
        "world_observer": {"sum_gamma_even": even_sum, "sum_gamma_odd": odd_sum,
                           "difference": even_sum-odd_sum},
        "self_energies": {str(n): SE[n] for n in M9},
        "best": {"rms": best[0][0], "candidate": best[0][1],
                 "pairing": dict(zip(sp, [M9[i] for i in best[0][2]]))},
        "reference": {"sin_monotone": 1.1178, "sin_best_pairing": 0.8028,
                      "upper_bound": float(LM.std())},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/41_observer_backreaction.json")