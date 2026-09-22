#!/usr/bin/env python3
"""
O136 — Script 42: 觀察者反作用 — 高階 + 自洽版本
================================================================
Script 41 結果:
  位置算子 = 精確 Z₂-奇耦合 (⟨n|x|m⟩ = 0 for |n−m| 偶) ✅
  二階自能 Δm_n = Σ|V_nm|²/(E_n−E_m): RMS = 0.5873 (比 sin 1.1178 好 1.9×)
  最佳配對反轉: t↔1, b↔2, τ↔3, c↔4, μ↔5, s↔7, d↔9, u↔11, e↔13

本 script 測試:
  (a) 高階自能 (3階, 4階, 全階 resummation)
  (b) Dyson 自洽: m² = m₀² + Σ(m²)
  (c) 指數形式: m ∝ exp(A·Δm)
  (d) 比值結構分析
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])

print("=" * 96)
print("O136 Script 42: 觀察者反作用 — 高階 + 自洽版本")
print("=" * 96)

# 重建幾何
Nc44 = 44
x44 = np.arange(1, Nc44+1, dtype=float)
Psi44 = np.zeros((Nc44, Nc44))
for n in range(1, Nc44+1):
    Psi44[:, n-1] = np.sin(n*math.pi*x44/(Nc44+1))
for n in range(Nc44):
    Psi44[:, n] /= np.linalg.norm(Psi44[:, n])
X44 = np.diag(x44 - x44.mean())
V44 = Psi44.T @ X44 @ Psi44
E44 = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])

print(f"\n{'─'*96}")
print("1. 高階自能 (n 階)")
print(f"{'─'*96}")

# 全階: 解 (E_n I - H_eff) 的本徵值, H_eff = diag(E) + 耦合
# 最簡單: 考慮 H = diag(E_n) + λ·V (位置算子), 求本徵值
print(f"\n{'λ':>8} " + " ".join(f"{'n='+str(n):>12}" for n in M9))
print("-" * (9 + 13*len(M9)))
res = {}
for lam in [0.001, 0.01, 0.05, 0.1, 0.5]:
    H = np.diag(E44) + lam*V44
    ev = np.sort(np.linalg.eigvalsh(H))
    # 取對應 n 的本徵值 (按原 n 的排序位置)
    order = np.argsort(E44)
    vals = []
    for n in M9:
        pos = int(np.where(order == n-1)[0][0])
        vals.append(ev[pos])
    res[lam] = vals
    print(f"{lam:>8.3f} " + " ".join(f"{v:>12.6f}" for v in vals))

# ═══ 2. 譜形檢驗 ════════════════════════════════════
print(f"\n{'─'*96}")
print("2. 譜形檢驗 (RMS)")
print(f"{'─'*96}")

def fit_rms(vals):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-15): return None
    X = np.log(v); order = np.argsort(X); Xp = X[order]
    A = np.vstack([np.ones(9), Xp]).T
    c,*_ = np.linalg.lstsq(A, LM, rcond=None)
    return float(np.sqrt(np.mean((A@c-LM)**2))), float(c[1])

def fit_rms_exp(vals):
    """m = exp(a + A·f) 線性擬合"""
    v = np.array(vals)
    A_ = np.vstack([np.ones(9), v]).T
    c,*_ = np.linalg.lstsq(A_, LM, rcond=None)
    return float(np.sqrt(np.mean((A_@c-LM)**2))), float(c[1])

print(f"\n{'候選':>22} {'冪律 RMS':>12} {'指數 RMS':>12} {'判定':>8}")
print("-" * 58)
cands = {"sin(nπ/88)": [math.sin(n*math.pi/88) for n in M9]}
for lam in [0.001, 0.01, 0.05, 0.1, 0.5]:
    cands[f"H(λ={lam}) 本徵值"] = res[lam]
# 二階自能
SE2 = []
for n in M9:
    tot = 0.0
    for m in range(44):
        if m == n-1 or (m-(n-1))%2==0: continue
        dE = E44[n-1]-E44[m]
        if abs(dE) < 1e-12: continue
        tot += V44[n-1,m]**2/dE
    SE2.append(tot)
cands["Δm 二階"] = SE2
# ★ 位置方差 (觀察者測量的不確定性)
varx, mom2, nn = [], [], []
for n in M9:
    psi = Psi44[:, n-1]
    xm = float(np.sum(psi**2 * x44))
    v = float(np.sum(psi**2 * x44**2) - xm**2)
    varx.append(v)
    mom2.append(float(np.sum(psi**2 * x44**2)))
    nn.append(abs(V44[n-1, n]))      # 對角 (mean position)
cands["Var(x) 位置方差"] = varx
cands["⟨x²⟩ 二階動差"] = mom2
cands["|⟨n|x|n⟩| 平均位置"] = nn
# ★ 測量率: 動量展寬 × 位置展寬的倒數
cands["1/Var(x)"] = [1/v for v in varx]
# ★ 動量動差 ⟨p²⟩ = n² (D-D 鏈)
cands["⟨p²⟩ = n²"] = [n**2 for n in M9]

results = []
for name, vals in cands.items():
    r1 = fit_rms(vals); r2 = fit_rms_exp(vals)
    s1 = f"{r1[0]:.4f}" if r1 else "n/a"
    s2 = f"{r2[0]:.4f}" if r2 else "n/a"
    best = min(x for x in [r1[0] if r1 else 9, r2[0] if r2 else 9])
    v = '🟢' if best<0.3 else ('🟡' if best<1.0 else '🔴')
    print(f"{name:>22} {s1:>12} {s2:>12} {v:>8}")
    results.append((best, name, r1, r2))
print(f"\n無解釋上限 = {LM.std():.4f}")
results.sort()
print(f"★ 最佳: {results[0][1]}, RMS = {results[0][0]:.4f}")

# ═══ 3. ★ 二階自能的比值結構 ════════════════════════
print(f"\n{'─'*96}")
print("3. ★ 二階自能的比值結構")
print(f"{'─'*96}")

print(f"\n{'n':>3} {'Δm':>14} {'Δm(n)/Δm(n+2)':>16} {'log_φ':>10}")
print("-" * 48)
phi = (1+math.sqrt(5))/2
for i, n in enumerate(M9[:-1]):
    if SE2[i+1] <= 0 or SE2[i] <= 0:
        print(f"{n:>3} {SE2[i]:>14.6f} {'n/a (負值)':>16} {'n/a':>10}")
        continue
    r = SE2[i]/SE2[i+1]
    print(f"{n:>3} {SE2[i]:>14.6f} {r:>16.6f} {math.log(r)/math.log(phi):>10.6f}")

pos_r = [SE2[i]/SE2[i+1] for i in range(8) if SE2[i] > 0 and SE2[i+1] > 0]
if pos_r:
    print(f"\n★ 比值範圍: [{min(pos_r):.4f}, {max(pos_r):.4f}]")
print(f"★ φ = {phi:.6f}, φ² = {phi**2:.6f}")

# ═══ 4. ★★ 全配對搜索 (各候選) ══════════════════════
print(f"\n{'─'*96}")
print("4. ★★ 全配對搜索")
print(f"{'─'*96}")

best_all = []
for name, vals in cands.items():
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-15): continue
    X = np.log(v)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c,*_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        best_all.append((rms, name, perm, c[1]))
best_all.sort(key=lambda z: z[0])
print(f"\n最佳 6 個:")
print(f"\n{'RMS':>9} {'候選':>20} {'配對 (模式→粒子)':>44}")
print("-" * 76)
for rms, name, perm, a in best_all[:6]:
    ps = " ".join(f"{p}:{M9[i]}" for p, i in zip(sp, perm))
    print(f"{rms:>9.4f} {name:>20} {ps:>44}")

# ═══ 5. 保存 ════════════════════════════════════════
with open(OUT/"42_observer_higher_order.json","w") as f:
    json.dump({
        "eigenvalue_spectra": {str(k): v for k, v in res.items()},
        "second_order": {str(n): SE2[i] for i, n in enumerate(M9)},
        "best": {"rms": best_all[0][0], "candidate": best_all[0][1],
                 "pairing": dict(zip(sp, [M9[i] for i in best_all[0][2]]))},
        "reference": {"sin": 1.1178, "2nd_order": 0.5873},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/42_observer_higher_order.json")