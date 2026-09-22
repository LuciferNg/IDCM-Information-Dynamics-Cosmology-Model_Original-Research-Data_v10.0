#!/usr/bin/env python3
"""
O136 — Script 61: 三階自能 — |Δm| 殘餘之結構性延伸

⚠️⚠️ 【本 script 前提結構上不可能 — 已由 scripts/62 取代, 見 docs/33 §二】
    ★ 發現: Δm^(3) ≡ 0 精確 (V³_nn = 0)
    ★ 定理 (奇數階自能消滅): Z₂-奇 V ⟹ V^(2k+1)_nn ≡ 0 ∀k
      證: V_nm V_mk V_kn ≠ 0 需 p(n)≠p(m), p(m)≠p(k), p(k)≠p(n)
          但前兩式 ⟹ p(k)=p(n), 與第三式矛盾
    ⟹ 三階延伸【唔係失敗, 而係結構上不可能】; 只有偶數階存在
    ⚠️ 本 script 因 log(0) 崩潰 (D3 ≡ 0); 結論以 scripts/62 為準
================================================================
背景 (docs/32, scripts/60):
  ★ |Δm| 二階自能 = 0.5873, R² = 0.9768 — 結構雙重顯著 (P=0.0155/0.0080)
  ★ 殘餘 (典型 1.80×) 與 deg/v₂/世代/扇區/n/γ 【全部】無顯著相關 (scripts/60)
  ⟹ 殘餘無結構 ⟹ 需【結構性延伸】而非新因子

★ 自然延伸: 三階自能
   Δm^(3)_n = Σ_{m,k} V_nm V_mk V_kn / ((E_n−E_m)(E_n−E_k))
   (Z₂-奇 V: |n−m|,|m−k|,|k−n| 全奇 ⟹ 可能, V³_nn ≠ 0)

本 script:
  (A) 計算 Δm^(3) 與 Δm^(2); 檢驗兩者關係
  (B) 單因子: |Δm^(2)|, |Δm^(3)|, |Δm^(2)+Δm^(3)|, |Δm^(2)+λΔm^(3)| (λ 掃描)
  (C) 二因子: ln m ~ a·ln|Δm^(2)| + b·ln|Δm^(3)|
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
V2 = V @ V
V3 = V2 @ V

def logscore(vals, LMv=None):
    y = LM if LMv is None else LMv
    v = np.abs(np.array(vals, dtype=float))
    if (v <= 0).any() or v.std() < 1e-14: return 9e9
    lv = np.log(v)
    if lv.std() < 1e-14: return 9e9
    o = np.argsort(lv); xs = lv[o]; ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0-r*r)))

def dm2(n):
    idx = [m for m in range(NC) if m != n-1 and (m-(n-1)) % 2 == 1]
    return float((np.abs(V[n-1, idx])**2/(E[n-1]-E[idx])).sum())

def dm3(n):
    idx = [m for m in range(NC) if m != n-1 and (m-(n-1)) % 2 == 1]
    s = 0.0
    for m in idx:
        for k in idx:
            if (m-k) % 2 == 1:
                s += V[n-1, m]*V[m, k]*V[k, n-1]/((E[n-1]-E[m])*(E[n-1]-E[k]))
    return s

print("=" * 96)
print("O136 Script 61: 三階自能 — |Δm| 殘餘之結構性延伸")
print("=" * 96)

D2 = {n: dm2(n) for n in range(1, NC+1)}
D3 = {n: dm3(n) for n in range(1, NC+1)}

print(f"\n{'─'*96}\n(A) Δm^(2) vs Δm^(3)\n{'─'*96}")
print(f"\n  {'n':>4} {'Δm^(2)':>16} {'Δm^(3)':>16} {'比值 Δ3/Δ2':>13} {'V3nn':>14}")
print("  " + "-"*68)
for n in M9:
    print(f"  {n:>4} {D2[n]:>16.6f} {D3[n]:>16.6f} {D3[n]/D2[n]:>13.6f} {V3[n-1,n-1]:>14.6f}")
D3max = max(abs(D3[n]) for n in M9); D2max = max(abs(D2[n]) for n in M9)
THEOREM = (D3max/D2max < 1e-12)
r23 = None if THEOREM else float(np.corrcoef([math.log(abs(D2[n])) for n in M9],
                                             [math.log(abs(D3[n])) for n in M9])[0,1])
if THEOREM:
    print(f"\n  ★★★ 發現: Δm^(3) ≡ 0 精確! (max|Δ3|/max|Δ2| = {D3max/D2max:.3e})")
    print(f"      ⟹ 三階自能【結構上不存在】— 見 docs/33 §二 奇數 V 因子消滅定理")
    print(f"      ⟹ 後續分析 (B)-(D) 全部不適用; 結論以 scripts/62/63 為準")
else:
    print(f"  ★ corr(ln|Δm^(2)|, ln|Δm^(3)|) = {r23:.6f}")

# ═══ (B) 單因子 ══════════════════════════════════════
if THEOREM:
    with open(OUT/"61_third_order.json", "w") as f:
        json.dump({"discovery": "Δm^(3) ≡ 0 精確 (V³_nn = 0)",
                   "D3_max_over_D2_max": D3max/D2max,
                   "theorem": "Z₂-奇 V ⟹ V^(2k+1)_nn ≡ 0 ⟹ 奇數階自能恆零",
                   "dm2_M9": {str(n): D2[n] for n in M9},
                   "dm3_M9": {str(n): D3[n] for n in M9},
                   "note": "三階前提結構上不可能; 結論以 scripts/62/63 為準 (docs/33 §二)",
                   "closure_threshold": 0.05}, f, ensure_ascii=False, indent=2)
    print(f"✅ 寫入 data/61_third_order.json (記錄發現, 非失敗)")
    raise SystemExit(0)

print(f"\n{'─'*96}\n(B) 單因子掃描\n{'─'*96}")
cands = {
    "|Δm^(2)|": [abs(D2[n]) for n in M9],
    "|Δm^(3)|": [abs(D3[n]) for n in M9],
    "|Δ2+Δ3|":  [abs(D2[n]+D3[n]) for n in M9],
    "|Δ2−Δ3|":  [abs(D2[n]-D3[n]) for n in M9],
    "|V3nn|":   [abs(V3[n-1,n-1]) for n in M9],
    "|Δ2·Δ3|":  [abs(D2[n]*D3[n]) for n in M9],
}
print(f"\n  {'候選':>14} {'RMS':>9} {'判定':>10}")
print("  " + "-"*36)
b1 = {}
for k, v in cands.items():
    r = logscore(v); b1[k] = r
    print(f"  {k:>14} {r:>9.4f} {'🟡 佳' if r < 0.60 else '🔴':>10}")
print(f"\n  ★ 對照 |Δm^(2)| = {b1['|Δm^(2)|']:.4f} (docs/25/32 之 0.5873)")
print(f"  ★ 最佳 = {min(b1.items(), key=lambda kv: kv[1])}")

# λ 掃描
best_lam = (9e9, None)
for lam in np.linspace(-3, 3, 1201):
    v = [abs(D2[n] + lam*D3[n]) for n in M9]
    r = logscore(v)
    if r < best_lam[0]: best_lam = (r, lam)
print(f"\n  ★ λ 掃描 |Δ2 + λΔ3|: 最佳 λ = {best_lam[1]:.4f}, RMS = {best_lam[0]:.4f}")
print(f"    (λ = 0 即純二階 = {b1['|Δm^(2)|']:.4f}; 改善 = {b1['|Δm^(2)|']/best_lam[0]:.4f}×)")
print(f"    ★ 結構值 λ ∈ {{1, φ, 1/45, 2, 3}}: "
      + ", ".join(f"{v}: {logscore([abs(D2[n]+v*D3[n]) for n in M9]):.4f}"
                  for v in [1.0, (1+5**0.5)/2, 1/45, 2.0, 3.0]))

# ═══ (C) 二因子 ══════════════════════════════════════
print(f"\n{'─'*96}\n(C) 二因子: ln m ~ a·ln|Δm^(2)| + b·ln|Δm^(3)|\n{'─'*96}")
X2 = np.array([math.log(abs(D2[n])) for n in M9]); X2 = (X2-X2.mean())/X2.std()
X3 = np.array([math.log(abs(D3[n])) for n in M9]); X3 = (X3-X3.mean())/X3.std()
best = (9e9, 0, 0)
for a in np.linspace(-4, 4, 161):
    for b in np.linspace(-4, 4, 161):
        r = logscore(np.exp(a*X2 + b*X3))
        if r < best[0]: best = (r, a, b)
print(f"\n  ★ 最佳 (a,b) = ({best[1]:.3f}, {best[2]:.3f}), RMS = {best[0]:.4f}")
print(f"  ★ 對照: 1 因子 |Δ2| = {b1['|Δm^(2)|']:.4f};  3 因子乘積 = 0.4970;  閉合需 < 0.05")
print(f"  ★ 改善 = {b1['|Δm^(2)|']/best[0]:.4f}×  ⟹ {'✅ 顯著改善' if best[0] < 0.4 else '🔴 改善有限'}")

# ═══ (D) null test ═══════════════════════════════════
print(f"\n{'─'*96}\n(D) ★ null test: 隨機 9 模式集 (N=2000)\n{'─'*96}")
rng = random.Random(20260920)
obs2 = b1["|Δm^(2)|"]; obs3 = b1["|Δm^(3)|"]
n2l, n3l = [], []
for _ in range(2000):
    md = rng.sample(range(1, NC+1), 9)
    n2l.append(logscore([abs(D2[n]) for n in md]))
    n3l.append(logscore([abs(D3[n]) for n in md]))
print(f"\n  {'候選':>14} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("  " + "-"*70)
n1res = {}
for k, ob, nn in [("|Δm^(2)|", obs2, n2l), ("|Δm^(3)|", obs3, n3l)]:
    v = np.array(nn); p = float((v <= ob).mean())
    n1res[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"  {k:>14} {ob:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① |Δm^(2)| (二階) = {b1['|Δm^(2)|']:.4f} — 基線
  ② |Δm^(3)| (三階) = {b1['|Δm^(3)|']:.4f}
  ③ corr(ln|Δ2|, ln|Δ3|) = {r23:.4f} ⟹ {'高度相關, 無新信息' if abs(r23) > 0.9 else '相關中等'}
  ④ λ 掃描最佳 = {best_lam[0]:.4f} (λ = {best_lam[1]:.4f}), 改善 {b1['|Δm^(2)|']/best_lam[0]:.4f}×
  ⑤ 二因子最佳 = {best[0]:.4f}, 改善 {b1['|Δm^(2)|']/best[0]:.4f}×
  ⑥ null test (模式集): |Δ2| P = {n1res['|Δm^(2)|']['p']:.4f}; |Δ3| P = {n1res['|Δm^(3)|']['p']:.4f}
  ⑦ 閉合需 < 0.05 ⟹ {'✅' if min(b1['|Δm^(2)|'], best[0]) < 0.05 else '🔴 未閉合'}
""")

with open(OUT/"61_third_order.json", "w") as f:
    json.dump({
        "dm2": {str(n): D2[n] for n in M9},
        "dm3": {str(n): D3[n] for n in M9},
        "corr_ln_dm2_dm3": r23,
        "one_factor": b1,
        "lambda_scan": {"best_lambda": best_lam[1], "best_rms": best_lam[0],
                        "improvement": b1['|Δm^(2)|']/best_lam[0]},
        "two_factor": {"a": best[1], "b": best[2], "rms": best[0],
                       "improvement": b1['|Δm^(2)|']/best[0]},
        "null_random_modeset": n1res,
        "closure_threshold": 0.05,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/61_third_order.json")