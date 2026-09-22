#!/usr/bin/env python3
"""
O136 — Script 63: ★ 奇數 V 因子消滅定理 (精確定式) + 六階自能
================================================================
★ 由 scripts/61/62 發現:
   Δm^(2) ≠ 0 ✓    Δm^(4) ≡ 0 ✓    Δm^(6) ≠ 0 ✓

定理 (精確定式):
  設 V 為 Z₂-奇耦合: V_nm ≠ 0 僅當 parity(n) ≠ parity(m)
  則【任何含奇數個 V 因子之對角元 ≡ 0】
  證: 每個 V 因子要求 parity 反轉; 奇數次反轉 ⟹ 終 parity ≠ 始 parity
      ⟹ 對角元 (始=終) 必須為零
  ⟹ 自能階 2p 含 (p+1) 個 V 因子
  ⟹ 存活階 = {2p : p+1 偶} = {2p : p 奇} = {2, 6, 10, 14, ...}  (階 ≡ 2 mod 4)
  ⟹ 【4 階, 8 階, 12 階 全部恆等於零】

本 script:
  (A) 精確定式數值驗證: 階 2,4,6,8,10 之消滅/存活
  (B) 六階自能 Δm^(6) 分析
  (C) 二因子 (Δ2, Δ6) 測試 + λ 掃描
  (D) ★ null test
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

def dm(n, order):
    """Δm^(2p)_n = [V G V G ... V]_nn  (p 個 G, p+1 個 V)"""
    d = E[n-1] - E
    with np.errstate(divide='ignore', invalid='ignore'):
        g = np.where(np.abs(d) > 1e-12, 1.0/d, 0.0)
    G = np.diag(g)
    p = order // 2
    A = V.copy()
    for _ in range(p):
        A = A @ G @ V
    return float(A[n-1, n-1])

print("=" * 96)
print("O136 Script 63: ★ 奇數 V 因子消滅定理 (精確定式) + 六階自能")
print("=" * 96)

# ═══ (A) 精確定式驗證 ════════════════════════════════
print(f"\n{'─'*96}\n(A) 精確定式數值驗證 — 階 2,4,6,8,10\n{'─'*96}")
print(f"\n  預言: 階 2,6,10 存活 (p 奇);  階 4,8 消滅 (p 偶)")
print(f"\n  {'階 2p':>7} {'p':>4} {'V 因子數':>9} {'max|Δm| (n=1..44)':>20} {'預言':>8} {'實測':>8} {'判定':>8}")
print("  " + "-"*70)
D = {}
thm_ok = True
for order in [2,4,6,8,10]:
    p = order // 2
    vals = [abs(dm(n, order)) for n in range(1, 45)]
    mx = max(vals)
    pred = "存活" if p % 2 == 1 else "消滅"
    act = "存活" if mx > 1e-3*max(1.0, max(abs(dm(n,2)) for n in range(1,45))) else "消滅"
    ok = (pred == act)
    if not ok: thm_ok = False
    D[order] = {n: dm(n, order) for n in range(1, NC+1)}
    print(f"  {order:>7} {p:>4} {p+1:>9} {mx:>20.6e} {pred:>8} {act:>8} {'✅' if ok else '🔴':>8}")
print(f"\n  ⟹ 精確定式 {'✅ 全部確認' if thm_ok else '🔴 失敗'}")
print(f"     ⟹ 【4 階, 8 階, 12 階 全部恆等於零】— 呢個係 Z₂-奇耦合之精確代數後果")

# ═══ (B) 六階自能 ════════════════════════════════════
print(f"\n{'─'*96}\n(B) 六階自能 Δm^(6) (下一個存活階)\n{'─'*96}")
print(f"\n  {'n':>4} {'Δm^(2)':>18} {'Δm^(6)':>20} {'Δ6/Δ2':>14}")
print("  " + "-"*60)
for n in M9:
    print(f"  {n:>4} {D[2][n]:>18.6f} {D[6][n]:>20.4e} {D[6][n]/D[2][n]:>14.4e}")
print(f"\n  ★ Δm^(6) 範圍 (n=1..44): {max(abs(D[6][n]) for n in range(1,45))/min(abs(D[6][n]) for n in range(1,45)):.4g}×")
print(f"  ★ Δm^(2) 範圍 (n=1..44): {max(abs(D[2][n]) for n in range(1,45))/min(abs(D[2][n]) for n in range(1,45)):.4g}×")
r26 = float(np.corrcoef([math.log(abs(D[2][n])) for n in M9],
                        [math.log(abs(D[6][n])) for n in M9])[0,1])
print(f"  ★ corr(ln|Δ2|, ln|Δ6|) = {r26:.6f} ⟹ {'高度相關' if abs(r26)>0.9 else '相關中等' if abs(r26)>0.5 else '相關弱 (可提供新信息)'}")

# ═══ 評分 ════════════════════════════════════════════
def logscore(vals, LMv=None):
    y = LM if LMv is None else LMv
    v = np.abs(np.array(vals, dtype=float))
    if (v <= 0).any() or v.std() < 1e-14: return 9e9
    lv = np.log(v)
    if lv.std() < 1e-14: return 9e9
    o = np.argsort(lv); xs = lv[o]; ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0-r*r)))

# ═══ (C) 二因子 (Δ2, Δ6) ═════════════════════════════
print(f"\n{'─'*96}\n(C) 二因子 (Δ2, Δ6) + λ 掃描\n{'─'*96}")
cands = {
    "|Δm^(2)|": [abs(D[2][n]) for n in M9],
    "|Δm^(6)|": [abs(D[6][n]) for n in M9],
    "|Δ2+Δ6|":  [abs(D[2][n]+D[6][n]) for n in M9],
    "|Δ2·Δ6|":  [abs(D[2][n]*D[6][n]) for n in M9],
}
print(f"\n  {'候選':>12} {'RMS':>9} {'判定':>10}")
print("  " + "-"*34)
b1 = {}
for k, v in cands.items():
    r = logscore(v); b1[k] = r
    print(f"  {k:>12} {r:>9.4f} {'🟡 佳' if r < 0.60 else '🔴':>10}")

X2 = np.array([math.log(abs(D[2][n])) for n in M9]); X2 = (X2-X2.mean())/X2.std()
X6 = np.array([math.log(abs(D[6][n])) for n in M9]); X6 = (X6-X6.mean())/X6.std()
best = (9e9, 0, 0)
for a in np.linspace(-4, 4, 161):
    for b in np.linspace(-4, 4, 161):
        r = logscore(np.exp(a*X2 + b*X6))
        if r < best[0]: best = (r, a, b)
print(f"\n  ★ 二因子 (Δ2, Δ6) 最佳 (a,b) = ({best[1]:.3f}, {best[2]:.3f}), RMS = {best[0]:.4f}")
print(f"  ★ 改善 = {b1['|Δm^(2)|']/best[0]:.4f}×  ⟹ {'✅ 顯著' if best[0] < 0.40 else '🔴 有限'}")
print(f"\n  ★ λ 掃描 |Δ2 + λΔ6|:")
lam_best = (9e9, None)
for lam in np.linspace(-3, 3, 1201):
    r = logscore([abs(D[2][n] + lam*D[6][n]) for n in M9])
    if r < lam_best[0]: lam_best = (r, lam)
print(f"    最佳 λ = {lam_best[1]:.6f}, RMS = {lam_best[0]:.4f} (改善 {b1['|Δm^(2)|']/lam_best[0]:.4f}×)")
for v in [1.0, 1/45, 2.0, 3.0, 0.1]:
    print(f"    λ = {v:>8.5f}: RMS = {logscore([abs(D[2][n] + v*D[6][n]) for n in M9]):.4f}")

# ═══ (D) null test ═══════════════════════════════════
print(f"\n{'─'*96}\n(D) ★ null test: 隨機 9 模式集 (N=2000)\n{'─'*96}")
rng = random.Random(20260920)
obs = {"|Δm^(2)|": b1["|Δm^(2)|"], "|Δm^(6)|": b1["|Δm^(6)|"]}
nl = {k: [] for k in obs}
for _ in range(2000):
    md = rng.sample(range(1, NC+1), 9)
    nl["|Δm^(2)|"].append(logscore([abs(D[2][n]) for n in md]))
    nl["|Δm^(6)|"].append(logscore([abs(D[6][n]) for n in md]))
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
  ① ★ 奇數 V 因子消滅定理 (精確定式): {'✅ 全部確認' if thm_ok else '🔴'}
     存活階 = {{2, 6, 10, 14, ...}} (階 ≡ 2 mod 4)
     ⟹ 4 階, 8 階, 12 階【恆等於零】— 精確代數後果, 唔係數值巧合
  ② Δm^(2) = {b1['|Δm^(2)|']:.4f} (基線, docs/25/32)
  ③ Δm^(6) = {b1['|Δm^(6)|']:.4f}
  ④ corr(ln|Δ2|, ln|Δ6|) = {r26:.4f}
  ⑤ 二因子 (Δ2, Δ6) 最佳 = {best[0]:.4f}, 改善 {b1['|Δm^(2)|']/best[0]:.4f}×
  ⑥ λ 掃描最佳 = {lam_best[0]:.4f} (λ = {lam_best[1]:.6f})
  ⑦ null: Δ2 P = {nres['|Δm^(2)|']['p']:.4f};  Δ6 P = {nres['|Δm^(6)|']['p']:.4f}
  ⑧ 閉合需 < 0.05 ⟹ {'✅' if min(b1['|Δm^(2)|'], best[0], lam_best[0]) < 0.05 else '🔴 未閉合'}
""")

with open(OUT/"63_odd_v_factor_theorem.json", "w") as f:
    json.dump({
        "theorem": "Z₂-奇 V ⟹ 任何含奇數個 V 因子之對角元 ≡ 0 ⟹ 存活階 = {2,6,10,14,...}",
        "theorem_verified": bool(thm_ok),
        "order_survival": {str(o): {"max_abs": float(max(abs(D[o][n]) for n in range(1,45))),
                                    "predicted": "存活" if (o//2) % 2 == 1 else "消滅"}
                           for o in [2,4,6,8,10]},
        "dm2_M9": {str(n): D[2][n] for n in M9},
        "dm6_M9": {str(n): D[6][n] for n in M9},
        "corr_ln2_ln6": r26,
        "one_factor": b1,
        "two_factor_d2_d6": {"a": best[1], "b": best[2], "rms": best[0],
                             "improvement": b1['|Δm^(2)|']/best[0]},
        "lambda_scan": {"best_lambda": lam_best[1], "best_rms": lam_best[0]},
        "null_random_modeset": nres,
        "closure_threshold": 0.05,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/63_odd_v_factor_theorem.json")