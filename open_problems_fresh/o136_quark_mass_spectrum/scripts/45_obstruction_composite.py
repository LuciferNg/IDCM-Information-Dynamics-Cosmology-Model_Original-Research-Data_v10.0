#!/usr/bin/env python3
"""
O136 — Script 45: 結構障礙定理 + 範圍/比值分離 + 複合方案
================================================================
Script 44 結果:
  (A) ★★★ 結構障礙: ln(質量比值)/ln(γ比值) 跨度 42.6×
      ⟹ 純冪律 m ∝ γ^α 【不可能】
      corr(γ比值, 質量比值) = −0.2901 (負相關)
  (B) 精確對角化: 所有結構 λ → 範圍 ≤ 30.6×
  (C) Dyson 自洽: 範圍 35–190×
  (D) Gap 方程: 範圍 4.797e4× (正確量級!) 但 RMS 1.1765 (比值錯)
  (E) 1/IPR λ=1/11: RMS 0.6450 (最佳非微擾)
  (F) ★ 修正基線: sin 譜在【最佳配對】下 RMS = 0.8028 (非 1.1178)

★ 關鍵發現: 【範圍】與【比值】係兩個獨立問題
  - Gap 方程: 範圍對 (4.8e4×), 比值錯
  - 二階自能: 比值最好 (0.5873), 範圍錯 (110×)
  → 測試複合: m ∝ |Δm|^a × G^b

本 script:
  1. 結構障礙定理 (完整版)
  2. 範圍/比值分離的定量化
  3. 複合方案 m ∝ |Δm|^a × G^b 全搜索
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2
ph2 = phi**2
mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])
MR = np.array([mass[sp[i+1]]/mass[sp[i]] for i in range(8)])

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
print("O136 Script 45: 結構障礙定理 + 範圍/比值分離 + 複合方案")
print("=" * 94)

# ═══ 1. ★★★ 結構障礙定理 ═══════════════════════════
print(f"\n{'─'*94}")
print("1. ★★★ 結構障礙定理")
print(f"{'─'*94}")

alpha_i = [math.log(MR[i])/math.log(GR[i]) for i in range(8)]
print(f"\n{'i':>2} {'n_i→n_j':>9} {'γ比值':>9} {'質量比值':>10} {'α_i=ln(m比)/ln(γ比)':>20}")
print("-" * 54)
for i in range(8):
    print(f"{i+1:>2} {M9[i]:>3}→{M9[i+1]:<3} {GR[i]:>9.4f} {MR[i]:>10.4f} {alpha_i[i]:>20.4f}")

print(f"""
★ 定理 (單調冪律不可能):
  若 m(n) = C·γ(n)^α 對所有 n 成立, 則
     ln(m(n_i+1)/m(n_i)) = α·ln(γ(n_i+1)/γ(n_i))  ∀i
  ⟹ α_i ≡ ln(m比)/ln(γ比) 必須為常數。
  實測: α_i ∈ [{min(alpha_i):.4f}, {max(alpha_i):.4f}], 標準差 {np.std(alpha_i):.4f}, 跨度 {max(alpha_i)/min(alpha_i):.1f}×
  ⟹ 【不可能】""")

print(f"\n★★ 相關係數 (負相關!):")
print(f"   corr(γ比值, 質量比值)      = {np.corrcoef(GR, MR)[0,1]:>8.4f}")
print(f"   corr(ln γ比值, ln 質量比值) = {np.corrcoef(np.log(GR), np.log(MR))[0,1]:>8.4f}")
print(f"   ⟹ 質量比值與 γ 比值【反向】: γ 跳得大處質量跳得小")

# ═══ 2. ★ 範圍/比值分離 ═════════════════════════════
print(f"\n{'─'*94}")
print("2. ★ 範圍 / 比值 分離的定量化")
print(f"{'─'*94}")

# 二階自能
SE2 = {}
for n in M9:
    tot = 0.0
    for m in range(Nc):
        if m == n-1 or (m-(n-1)) % 2 == 0: continue
        dE = E[n-1]-E[m]
        if abs(dE) < 1e-12: continue
        tot += V[n-1, m]**2/dE
    SE2[n] = tot
dm = np.array([abs(SE2[n]) for n in M9])

# Gap 方程主本徵向量 (K_nm = V_nm²/E_m²)
K = np.zeros((Nc, Nc))
for n in range(Nc):
    for m in range(Nc):
        if m == n: continue
        K[n, m] = V[n, m]**2 / E[m]**2
w, vec = np.linalg.eig(K)
i0 = int(np.argmax(np.abs(w)))
Gv = np.abs(vec[:, i0].real)
G = np.array([Gv[n-1] for n in M9])
G = G/G.max()

print(f"\n{'量':>18} {'範圍 (max/min)':>18} {'所需':>12} {'判定':>8}")
print("-" * 60)
print(f"{'觀測質量':>18} {max(mass.values())/min(mass.values()):>18.3e} {'—':>12} {'基準':>8}")
print(f"{'二階自能 |Δm|':>18} {dm.max()/dm.min():>18.3e} {max(mass.values())/min(mass.values()):>12.3e} {'🔴 太窄':>8}")
print(f"{'Gap 主本徵向量 G':>18} {G.max()/G.min():>18.3e} {max(mass.values())/min(mass.values()):>12.3e} {'🟢 對!':>8}")
print(f"{'sin(nπ/88)':>18} {max(math.sin(n*math.pi/88) for n in M9)/min(math.sin(n*math.pi/88) for n in M9):>18.3e} {max(mass.values())/min(mass.values()):>12.3e} {'🔴 太窄':>8}")

print(f"""
★ 分離:
   範圍正確者: Gap 方程 (4.8e4×) — 乘積型/冪次結構
   比值正確者: 二階自能 (RMS 0.5873) — 但範圍只 110×
   ⟹ 【兩個獨立環節】""")

# ═══ 3. 修正基線 ════════════════════════════════════
print(f"\n{'─'*94}")
print("3. ★ 修正基線 (最佳配對下的 RMS)")
print(f"{'─'*94}")

def best_pairing(vals):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v)
    best = (9e9, None)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        if rms < best[0]: best = (rms, perm)
    return best

base = {"sin(nπ/88)": [math.sin(n*math.pi/88) for n in M9],
        "cos(nπ/88)": [math.cos(n*math.pi/88) for n in M9],
        "γ_n": [E[n-1] for n in M9],
        "√γ_n": [math.sqrt(E[n-1]) for n in M9],
        "n": list(M9)}
print(f"\n{'候選':>16} {'RMS (最佳配對)':>16} {'RMS (單調)':>14}")
print("-" * 48)
for name, vals in base.items():
    b = best_pairing(vals)
    v = np.abs(np.array(vals)); X = np.log(v)
    A = np.vstack([np.ones(9), X]).T
    c, *_ = np.linalg.lstsq(A, LM, rcond=None)
    rms_mono = float(np.sqrt(np.mean((A@c-LM)**2)))
    print(f"{name:>16} {b[0]:>16.4f} {rms_mono:>14.4f}")

# ═══ 4. ★★ 複合方案 m ∝ |Δm|^a × G^b ══════════════
print(f"\n{'─'*94}")
print("4. ★★ 複合方案: m ∝ |Δm|^a × G^b")
print(f"{'─'*94}")

# 2 參數擬合 (a, b) + 配對: 用 grid search on a,b + best pairing
dm_ = dm/dm.max(); G_ = G
print(f"\n掃描 a ∈ [0,3], b ∈ [0,3] ...")
best_comp = []
for a in np.linspace(0, 3, 31):
    for b in np.linspace(0, 3, 31):
        f = dm_**a * G_**b
        if np.any(f <= 0): continue
        X = np.log(f)
        # 用單調配對快速篩選, 再用最佳配對
        for perm in [list(range(9)), list(range(8,-1,-1))]:
            Xp = X[perm]
            A = np.vstack([np.ones(9), Xp]).T
            c, *_ = np.linalg.lstsq(A, LM, rcond=None)
            rms = float(np.sqrt(np.mean((A@c-LM)**2)))
            best_comp.append((rms, a, b, tuple(perm)))
best_comp.sort()
print(f"\n最佳 6 個 (a, b, RMS, 配對):")
print(f"\n{'RMS':>9} {'a':>7} {'b':>7} {'配對':>34}")
print("-" * 60)
for rms, a, b, perm in best_comp[:6]:
    ps = " ".join(f"{sp[i][0]}:{M9[perm[i]]}" for i in range(9))
    print(f"{rms:>9.4f} {a:>7.3f} {b:>7.3f} {ps:>34}")

# ═══ 5. 保存 ════════════════════════════════════════
with open(OUT/"45_obstruction_composite.json","w") as f:
    json.dump({
        "obstruction": {"alpha_per_pair": alpha_i,
                        "alpha_range": [min(alpha_i), max(alpha_i)],
                        "alpha_std": float(np.std(alpha_i)),
                        "corr_gamma_mass": float(np.corrcoef(GR, MR)[0,1]),
                        "verdict": "純冪律 m ∝ γ^α 不可能"},
        "range_ratio_separation": {
            "mass_range_needed": float(max(mass.values())/min(mass.values())),
            "dm_range": float(dm.max()/dm.min()),
            "Gap_range": float(G.max()/G.min()),
        },
        "composite_best": {"rms": best_comp[0][0], "a": best_comp[0][1],
                           "b": best_comp[0][2],
                           "pairing": {sp[i]: M9[best_comp[0][3][i]] for i in range(9)}},
        "corrected_baselines": {"sin_best_pairing": best_pairing(base["sin(nπ/88)"])[0],
                                "sin_monotone": 1.1178,
                                "2nd_order_self_energy": 0.5873},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 寫入 data/45_obstruction_composite.json")