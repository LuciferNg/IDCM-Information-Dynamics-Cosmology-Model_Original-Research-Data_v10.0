#!/usr/bin/env python3
"""
O136 — Script 62: ★ 奇數階自能消滅定理 + 四階自能
================================================================
★★★ 由 scripts/61 發現: Δm^(3) ≡ 0 精確 (V³_nn = 0)

定理 (奇數階自能消滅):
  設 V 為 Z₂-奇耦合: V_nm ≠ 0 僅當 parity(n) ≠ parity(m)
  則 V^(2k+1)_nn ≡ 0 ∀k
  證: V_nm V_mk V_kn ≠ 0 需 p(n)≠p(m), p(m)≠p(k), p(k)≠p(n)
      但 p(n)≠p(m) ∧ p(m)≠p(k) ⟹ p(k)=p(n) 矛盾
  ⟹ 奇數階自能【恆等於零】; 只有偶數階存在

本 script:
  (A) 定理數值驗證: V^1,V^3,V^5,V^7 對角 ≡ 0; V^2,V^4,V^6 非零
  (B) 計算偶數階自能 Δm^(2), Δm^(4), Δm^(6) (resolvent 形式)
  (C) 單因子 + 二因子 (Δ2, Δ4) 測試
  (D) ★ null test (隨機 9 模式集)
  (E) 裁決
"""
import numpy as np, math, json, random
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
NC = 88
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
LM = np.array([math.log(MASS[p]) for p in sorted(MASS, key=lambda p: MASS[p])])

x = np.arange(1, NC+1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(NC+1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, NC+1)])

print("=" * 96)
print("O136 Script 62: ★ 奇數階自能消滅定理 + 四階自能")
print("=" * 96)

# ═══ (A) 定理驗證 ════════════════════════════════════
print(f"\n{'─'*96}\n(A) ★ 定理數值驗證: 奇數階 V^k 對角 ≡ 0?\n{'─'*96}")
print(f"\n  ★ 用【相對】閾值: 矩陣冪範數隨 k 增長, 絕對閾值不可用")
print(f"\n  {'k':>3} {'max|V^k_nn|':>15} {'||V^k||':>15} {'相對比值':>12} {'奇偶':>6} {'判定':>8}")
print("  " + "-"*68)
theorem_ok = True
for k in range(1, 9):
    Vk_ = np.linalg.matrix_power(V, k)
    dg = max(abs(Vk_[i, i]) for i in range(NC))
    nrm = float(np.linalg.norm(Vk_, 2))
    rel = dg/nrm
    par = "奇" if k % 2 == 1 else "偶"
    ok = (rel < 1e-10) if k % 2 == 1 else (rel > 1e-6)
    if not ok: theorem_ok = False
    print(f"  {k:>3} {dg:>15.3e} {nrm:>15.3e} {rel:>12.3e} {par:>6} {'✅' if ok else '🔴':>8}")
print(f"\n  ⟹ 奇數階消滅定理 {'✅ 數值確認' if theorem_ok else '🔴 失敗'}")
print(f"     (奇數階相對比值 ~1e−14 ≈ 機器精度 = 精確零 + 捨入; 偶數階 O(1))")

# ═══ (B) 偶數階自能 ══════════════════════════════════
print(f"\n{'─'*96}\n(B) 偶數階自能 Δm^(2), Δm^(4), Δm^(6)  (resolvent 形式)\n{'─'*96}")

def dm_ev(n, order):
    """Δm^(2p)_n = [V G V G ... V]_nn, G = diag(1/(E_n − E_m))"""
    d = E[n-1] - E
    with np.errstate(divide='ignore', invalid='ignore'):
        g = np.where(np.abs(d) > 1e-12, 1.0/d, 0.0)   # ★ 對角歸零 (V_nn = 0 故正確)
    G = np.diag(g)
    # ★ Δm^(2p)_n = [V G V G ... V]_nn  (p 個 G, p+1 個 V)
    #   ★ 修正: 舊版 A=V; A=A@(V@G) 得 [V²G]_nn ✗ (非對稱, 非自能)
    #           正確: A=V; A=A@G@V 得 [VGV]_nn ✓
    p = order // 2
    A = V.copy()
    for _ in range(p):
        A = A @ G @ V
    return float(A[n-1, n-1])

DM2 = {n: dm_ev(n, 2) for n in range(1, NC+1)}
DM4 = {n: dm_ev(n, 4) for n in range(1, NC+1)}
DM6 = {n: dm_ev(n, 6) for n in range(1, NC+1)}

print(f"\n  {'n':>4} {'Δm^(2)':>16} {'Δm^(4)':>16} {'Δm^(6)':>16} {'Δ4/Δ2':>11} {'Δ6/Δ4':>11}")
print("  " + "-"*80)
for n in M9:
    r42 = DM4[n]/DM2[n] if abs(DM2[n]) > 1e-12 else float('nan')
    r64 = DM6[n]/DM4[n] if abs(DM4[n]) > 1e-12 else float('nan')
    print(f"  {n:>4} {DM2[n]:>16.6f} {DM4[n]:>16.6f} {DM6[n]:>16.6f} "
          f"{r42:>11.6f} {r64:>11.6f}")
for lbl, D in [("Δ2", DM2), ("Δ4", DM4), ("Δ6", DM6)]:
    print(f"  ★ {lbl} 範圍 (n=1..44): {max(abs(D[n]) for n in range(1,45))/min(abs(D[n]) for n in range(1,45)):.4g}×")

r24 = float(np.corrcoef([math.log(abs(DM2[n])) for n in M9],
                        [math.log(abs(DM4[n])) for n in M9])[0,1])
r46 = float(np.corrcoef([math.log(abs(DM4[n])) for n in M9],
                        [math.log(abs(DM6[n])) for n in M9])[0,1])
print(f"\n  ★ corr(ln|Δ2|, ln|Δ4|) = {r24:.6f}")
print(f"  ★ corr(ln|Δ4|, ln|Δ6|) = {r46:.6f}")

# ═══ 評分函數 ════════════════════════════════════════
def logscore(vals, LMv=None):
    y = LM if LMv is None else LMv
    v = np.abs(np.array(vals, dtype=float))
    if (v <= 0).any() or v.std() < 1e-14: return 9e9
    lv = np.log(v)
    if lv.std() < 1e-14: return 9e9
    o = np.argsort(lv); xs = lv[o]; ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0-r*r)))

# ═══ (C) 單因子 + 二因子 ═════════════════════════════
print(f"\n{'─'*96}\n(C) 單因子 + 二因子測試\n{'─'*96}")
cands = {
    "|Δm^(2)|": [abs(DM2[n]) for n in M9],
    "|Δm^(4)|": [abs(DM4[n]) for n in M9],
    "|Δm^(6)|": [abs(DM6[n]) for n in M9],
    "|Δ2+Δ4|":  [abs(DM2[n]+DM4[n]) for n in M9],
    "|Δ2·Δ4|":  [abs(DM2[n]*DM4[n]) for n in M9],
}
print(f"\n  {'候選':>12} {'RMS':>9} {'判定':>10}")
print("  " + "-"*34)
b1 = {}
for k, v in cands.items():
    r = logscore(v); b1[k] = r
    print(f"  {k:>12} {r:>9.4f} {'🟡 佳' if r < 0.60 else '🔴':>10}")

X2 = np.array([math.log(abs(DM2[n])) for n in M9]); X2 = (X2-X2.mean())/X2.std()
X4 = np.array([math.log(abs(DM4[n])) for n in M9]); X4 = (X4-X4.mean())/X4.std()
best = (9e9, 0, 0)
for a in np.linspace(-4, 4, 161):
    for b in np.linspace(-4, 4, 161):
        r = logscore(np.exp(a*X2 + b*X4))
        if r < best[0]: best = (r, a, b)
print(f"\n  ★ 二因子 (Δ2, Δ4) 最佳 (a,b) = ({best[1]:.3f}, {best[2]:.3f}), RMS = {best[0]:.4f}")
print(f"  ★ 改善 = {b1['|Δm^(2)|']/best[0]:.4f}×  ⟹ {'✅ 顯著' if best[0] < 0.4 else '🔴 有限'}")
print(f"  ★ 對照: 3 因子乘積 = 0.4970;  閉合需 < 0.05")

# ═══ (D) null test ═══════════════════════════════════
print(f"\n{'─'*96}\n(D) ★ null test: 隨機 9 模式集 (N=2000)\n{'─'*96}")
rng = random.Random(20260920)
obs = {k: b1[k] for k in ["|Δm^(2)|", "|Δm^(4)|", "|Δm^(6)|"]}
nl = {k: [] for k in obs}
for _ in range(2000):
    md = rng.sample(range(1, NC+1), 9)
    nl["|Δm^(2)|"].append(logscore([abs(DM2[n]) for n in md]))
    nl["|Δm^(4)|"].append(logscore([abs(DM4[n]) for n in md]))
    nl["|Δm^(6)|"].append(logscore([abs(DM6[n]) for n in md]))
print(f"\n  {'候選':>12} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("  " + "-"*68)
nres = {}
for k in obs:
    v = np.array(nl[k]); p = float((v <= obs[k]).mean())
    nres[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"  {k:>12} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① ★ 奇數階消滅定理: {'✅ 數值確認 (V^1,3,5,7 對角 < 1e−8)' if theorem_ok else '🔴'}
     ⟹ 奇數階自能【恆等於零】— 三階延伸【結構上不可能】
  ② Δm^(2) = {b1['|Δm^(2)|']:.4f} (基線)
  ③ Δm^(4) = {b1['|Δm^(4)|']:.4f}
  ④ Δm^(6) = {b1['|Δm^(6)|']:.4f}
  ⑤ corr(ln|Δ2|, ln|Δ4|) = {r24:.4f} ⟹ {'高度相關' if abs(r24)>0.9 else '相關中等' if abs(r24)>0.5 else '相關弱'}
  ⑥ 二因子 (Δ2, Δ4) 最佳 = {best[0]:.4f}, 改善 {b1['|Δm^(2)|']/best[0]:.4f}×
  ⑦ null: Δ2 P = {nres['|Δm^(2)|']['p']:.4f};  Δ4 P = {nres['|Δm^(4)|']['p']:.4f}
  ⑧ 閉合需 < 0.05 ⟹ {'✅' if min(b1['|Δm^(2)|'], best[0]) < 0.05 else '🔴 未閉合'}
""")

with open(OUT/"62_odd_order_theorem.json", "w") as f:
    json.dump({
        "theorem": "Z₂-奇 V ⟹ V^(2k+1)_nn ≡ 0 ⟹ 奇數階自能恆零",
        "theorem_verified": bool(theorem_ok),
        "diag_powers": {str(k): float(max(abs((np.linalg.matrix_power(V, k))[i, i]) for i in range(NC)))
                        for k in range(1, 9)},
        "dm_even": {str(n): {"dm2": DM2[n], "dm4": DM4[n], "dm6": DM6[n]} for n in M9},
        "corr": {"ln2_ln4": r24, "ln4_ln6": r46},
        "one_factor": b1,
        "two_factor_d2_d4": {"a": best[1], "b": best[2], "rms": best[0],
                             "improvement": b1['|Δm^(2)|']/best[0]},
        "null_random_modeset": nres,
        "closure_threshold": 0.05,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/62_odd_order_theorem.json")