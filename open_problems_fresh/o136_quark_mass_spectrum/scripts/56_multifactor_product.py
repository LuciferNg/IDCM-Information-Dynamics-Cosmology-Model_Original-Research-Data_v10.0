#!/usr/bin/env python3
"""
O136 — Script 56: 多因子乘積結構攻堅 (質量 = Π f_i(n)^a_i ?)
================================================================
結構動機 (非猜測, 由既有定理強制):
  ★ docs/26 §一 定理: 單一模式函數 m ∝ γ^α 不可能 (α 跨度 42.6×)
  ★ 21 個已排除方向【全部】係單模式譜量 (γ_n, sin, |Δm|, Σc^{−k}, 本徵值, n...)
  ★ 用戶/Gemini 直覺: 跨度來自【乘積結構】P = Π p_i
  ⟹ 結構性空白: 【多因子乘積】從未測過

方法 (零事後擬合):
  模型: ln m_n = c + Σ_i a_i · ln f_i(n)
  配對: 由【重排不等式】決定 (z_n = Σ a_i ln f_i 排序後配對排序質量) — 唔係自由搜索
  度量: RMS 殘差 (形狀) — 範圍係紅鯡魚 (docs/30 §五)
  對照: 1 因子 (21 個已排除) vs 2 因子 vs 3 因子
  null: 置換質量 N=2000 → 顯著性

本 script:
  (A) 因子庫建立 (15 個 IDCM 譜量) + 相關矩陣
  (B) 2 因子全掃描 (C(15,2)=105 對) + (a,b) 網格
  (C) 3 因子掃描 (C(15,3)=455 三元組)
  (D) ★ null test (置換質量)
  (E) 裁決: 乘積結構成立嗎?
"""
import numpy as np, math, json, random, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = Path(__file__).parent.parent / "data"
ND = 44; M9 = [1,2,3,4,5,7,9,11,13]
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
LM = np.array([math.log(MASS[p]) for p in sorted(MASS, key=lambda p: MASS[p])])

# ═══ (A) 因子庫 ══════════════════════════════════════
g = lambda n: 4*math.sin(n*math.pi/88)**2
DM = {1:-4310.877431, 2:1275.174080, 3:756.841933, 4:460.723130, 5:303.463670,
      7:155.939172, 9:92.106867, 11:58.797781, 13:39.011703}

def cumprod_sin(n):
    p = 1.0
    for k in range(1, n+1): p *= math.sin(k*math.pi/88)
    return p

FAC = {}
for n in M9:
    FAC.setdefault("gamma", {})[n]     = g(n)
    FAC.setdefault("sin", {})[n]       = math.sin(n*math.pi/88)
    FAC.setdefault("n", {})[n]         = float(n)
    FAC.setdefault("absdm", {})[n]     = abs(DM[n])
    FAC.setdefault("cos", {})[n]       = math.cos(n*math.pi/88)
    FAC.setdefault("inv_gamma", {})[n] = 1.0/g(n)
    FAC.setdefault("sqrt_gamma", {})[n]= math.sqrt(g(n))
    FAC.setdefault("cumprod", {})[n]   = cumprod_sin(n)
    FAC.setdefault("n2", {})[n]        = float(n*n)
    FAC.setdefault("inv_cos", {})[n]   = 1.0/math.cos(n*math.pi/88)
    FAC.setdefault("sin2", {})[n]      = math.sin(n*math.pi/88)**2
    FAC.setdefault("dm_ratio", {})[n]  = abs(DM[n])/g(n)
    FAC.setdefault("sec2", {})[n]      = 1.0/math.cos(n*math.pi/88)**2
    FAC.setdefault("nd_minus_n", {})[n]= float(ND-n)
    FAC.setdefault("inv_ndn", {})[n]   = 1.0/(ND-n)

names = sorted(FAC)
print("=" * 96)
print("O136 Script 56: 多因子乘積結構攻堅")
print("=" * 96)
print(f"\n(A) 因子庫 ({len(names)} 個 IDCM 譜量): {', '.join(names)}")
print(f"\n  註: 單因子 RMS 已知 (docs/26-30): absdm^φ² = 0.5873 (最佳), sin = 0.8028,")
print(f"      gamma = 0.8028, n = 0.7819, 累積乘積 = 0.7106")

X = {f: np.array([math.log(abs(FAC[f][n])) for n in M9]) for f in names}
X = {f: (v - v.mean())/v.std() for f, v in X.items()}   # 標準化

def score(vals, LMv):
    """重排不等式配對 + 最小二乘 RMS 殘差
    ★ 修正 (docs/31): 舊版用固定斜率 std(y)/std(x) 而非 OLS 斜率
      ⟹ 對低相關候選系統性膨脹 (sin 得 1.1300 vs 已知 0.8028)
    ★ 正確: RMS = std(y)·sqrt(1−r²)  (等價於 OLS 殘差 RMS)"""
    o = np.argsort(vals); ys = np.sort(LMv); xs = vals[o]
    if xs.std() < 1e-14: return float(ys.std())
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0 - r*r)))

def best_ab(f1, f2, grid=np.linspace(-4, 4, 81)):
    best = (9e9, 0, 0)
    for a in grid:
        for b in grid:
            r = score(a*X[f1] + b*X[f2], LM)
            if r < best[0]: best = (r, a, b)
    return best

# 1 因子基線 (重排配對)
print(f"\n{'─'*96}\n(B) 1 因子基線 (重排配對) — 對照組\n{'─'*96}")
print(f"\n{'因子':>14} {'RMS':>9}")
print("-" * 26)
one = {}
for f in names:
    r = score(X[f], LM); one[f] = r
for f, r in sorted(one.items(), key=lambda kv: kv[1]):
    print(f"{f:>14} {r:>9.4f}")

# ═══ (B) 2 因子全掃描 ════════════════════════════════
print(f"\n{'─'*96}\n(B) 2 因子全掃描 (C({len(names)},2) = {len(names)*(len(names)-1)//2} 對)\n{'─'*96}")
pairs = []
for f1, f2 in itertools.combinations(names, 2):
    r, a, b = best_ab(f1, f2)
    pairs.append((r, f1, f2, a, b))
pairs.sort()
print(f"\n{'#':>3} {'因子 1':>14} {'因子 2':>14} {'RMS':>9} {'a':>8} {'b':>8} {'vs 最佳1因子':>12}")
print("-" * 76)
best1 = min(one.values())
for i, (r, f1, f2, a, b) in enumerate(pairs[:12], 1):
    print(f"{i:>3} {f1:>14} {f2:>14} {r:>9.4f} {a:>8.2f} {b:>8.2f} {r/best1:>12.4f}")
print(f"\n★ 1 因子最佳 = {best1:.4f} ({min(one, key=one.get)})")
print(f"★ 2 因子最佳 = {pairs[0][0]:.4f} ({pairs[0][1]} × {pairs[0][2]})")
print(f"★ 改善 = {best1/pairs[0][0]:.4f}×")
print(f"★★ 閉合所需 < 0.05 ⟹ {'✅ 閉合!' if pairs[0][0] < 0.05 else '🔴 未閉合'}")

# ═══ (C) 3 因子掃描 ══════════════════════════════════
print(f"\n{'─'*96}\n(C) 3 因子掃描 (C({len(names)},3) = {len(names)*(len(names)-1)*(len(names)-2)//6} 三元組)\n{'─'*96}")
trip = []
for f1, f2, f3 in itertools.combinations(names, 3):
    best = 9e9
    for a in np.linspace(-3, 3, 13):
        for b in np.linspace(-3, 3, 13):
            v = a*X[f1] + b*X[f2]
            for c in np.linspace(-3, 3, 13):
                r = score(v + c*X[f3], LM)
                if r < best: best = r
    trip.append((best, f1, f2, f3))
trip.sort()
print(f"\n{'#':>3} {'因子組合':>44} {'RMS':>9}")
print("-" * 60)
for i, (r, f1, f2, f3) in enumerate(trip[:8], 1):
    print(f"{i:>3} {f1+' × '+f2+' × '+f3:>44} {r:>9.4f}")
print(f"\n★ 3 因子最佳 = {trip[0][0]:.4f}")
print(f"★★ 閉合所需 < 0.05 ⟹ {'✅ 閉合!' if trip[0][0] < 0.05 else '🔴 未閉合'}")

# ═══ (D) null test ═══════════════════════════════════
print(f"\n{'─'*96}\n(D) ⚠️ null test — 【退化, 見 docs/31 §六 置換 null 退化定理】\n{'─'*96}")
print(f"  ★ 配對由重排不等式(排序)決定 ⟹ 統計量對質量置換【不變】")
print(f"  ★ 故 permutation null 恆退化 (觀測 = null 中位 = null min)")
print(f"  ★ 保留輸出作定理之實證; 有效 null 須用 9! 搜索配對 (如 scripts/47)")
rng = random.Random(20260920)
obs2 = pairs[0][0]; obs3 = trip[0][0]
n2, n3 = [], []
f1, f2 = pairs[0][1], pairs[0][2]
f1b, f2b, f3b = trip[0][1], trip[0][2], trip[0][3]
for _ in range(2000):
    perm = LM.copy().tolist(); rng.shuffle(perm)   # ★ 修 tolist 副本 bug (仍退化, 見 docs/31 §六)
    y = np.array(sorted(perm))
    def sc(v):
        o = np.argsort(v); vs = v[o]
        if vs.std() < 1e-14: return float(y.std())
        r = float(np.corrcoef(vs, y)[0, 1])
        return float(y.std()*math.sqrt(max(0.0, 1.0 - r*r)))
    bb = 9e9
    for a in np.linspace(-4, 4, 41):
        for b in np.linspace(-4, 4, 41):
            r = sc(a*X[f1] + b*X[f2])
            if r < bb: bb = r
    n2.append(bb)
    bb3 = 9e9
    for a in np.linspace(-3, 3, 9):
        for b in np.linspace(-3, 3, 9):
            v = a*X[f1b] + b*X[f2b]
            for c in np.linspace(-3, 3, 9):
                r = sc(v + c*X[f3b])
                if r < bb3: bb3 = r
    n3.append(bb3)
n2 = np.array(n2); n3 = np.array(n3)
print(f"\n{'模型':>10} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 66)
for lbl, ob, nn in [("2 因子", obs2, n2), ("3 因子", obs3, n3)]:
    p = float((nn <= ob).mean())
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{lbl:>10} {ob:>10.4f} {np.median(nn):>11.4f} {nn.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決: 乘積結構成立嗎?\n{'─'*96}")
print(f"""
  ① 1 因子最佳: {best1:.4f}
  ② 2 因子最佳: {obs2:.4f}  ({pairs[0][1]} × {pairs[0][2]})  改善 {best1/obs2:.3f}×
  ③ 3 因子最佳: {obs3:.4f}  改善 {best1/obs3:.3f}×
  ④ 閉合所需: < 0.05
  ⑤ null (2 因子): P = {float((n2<=obs2).mean()):.4f}
  ⑥ null (3 因子): P = {float((n3<=obs3).mean()):.4f}
""")

with open(OUT/"56_multifactor_product.json", "w") as f:
    json.dump({
        "library": names,
        "one_factor": {k: v for k, v in sorted(one.items(), key=lambda kv: kv[1])},
        "two_factor_top": [{"rms": r, "f1": a_, "f2": b_, "a": aa, "b": bb}
                           for r, a_, b_, aa, bb in pairs[:12]],
        "three_factor_top": [{"rms": r, "f1": a_, "f2": b_, "f3": c_} for r, a_, b_, c_ in trip[:8]],
        "null2": {"median": float(np.median(n2)), "min": float(n2.min()),
                  "p": float((n2<=obs2).mean())},
        "null3": {"median": float(np.median(n3)), "min": float(n3.min()),
                  "p": float((n3<=obs3).mean())},
        "closure_threshold": 0.05,
        "reference": {"absdm_phi2": 0.5873, "sin": 0.8028, "cumprod": 0.7106},
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/56_multifactor_product.json")