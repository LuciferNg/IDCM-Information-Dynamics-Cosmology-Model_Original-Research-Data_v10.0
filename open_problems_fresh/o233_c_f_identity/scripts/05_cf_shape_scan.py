#!/usr/bin/env python3
"""
O206 — 第十一輪 scripts/05_: C_f 作為「波幅形狀」測試（Shape Scan）
=========================================================================
調律者 reframe（2026-10-06）: C_f 唔係 8 個獨立數字，而係一個「波幅」——
例如形狀係「中間凹陷嘅二次方程」嘅連續函數喺合法模式上嘅採樣。

第十一輪 scripts/04_ 嘅盲點（承認）: U1..U10 全部係「單調 f(n)」族（γ_n 嚴格單調 ⟹
γ_n 嘅任意單調組合單調，連 2-參數 U11/U12 都係 log-log 直線/彎曲但整體單調）。
「凹陷二次」（非單調、有極值）從未測過。本 script 補測。

──────────────────────────────────────────────────────────────────────
PRE-REGISTERED 模型（ln C_f = y, LS fit）:
  M1  y = a + b·n + c·n²              [n 軸 global 凹陷二次]
  M2  y = a + b·γ + c·γ²              [γ 軸 global 凹陷二次]
  M3  y = a + b·lnγ + c·(lnγ)²        [log-log 彎曲 = U11 + 曲率]
  M4  Gaussian peak  y = lnA − (n−n₀)²/(2σ²)
  M5  塊 × 共享凹陷形狀: y = lnA_g + ln(1 + c·(x−1)²)
      x = 塊內順序 (gen1 0,1,2 / gen2 0,1,3 / gen3 0,2)；
      c>0 = U 形（中間凹陷）, c<0 = ∩ 形（中間凸起）; A_g = 塊波幅
      [4 參數 fit 8 點 = 4 dof — 唯一有真自由度嘅「形狀+塊階梯」模型]
  M6  塊常數基準: y = lnA_g  [3 參數, 對照]
判據: max|ln dev| < 0.01 = 形狀 match（PASS）; < 0.10 = 有前景; 否則負
──────────────────────────────────────────────────────────────────────
"""
import math, json, os
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

M0 = mp.mpf("27.900915")
gam = lambda n, N=88: 4 * mp.sin(mp.pi * n / N)**2
PDG = {"e":"0.51099895","u":"2.16","d":"4.67","s":"93.4","mu":"105.6583755",
       "c":"1270.0","tau":"1776.86","b":"4180.0"}
N5 = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
ORDER = ["e","u","d","s","mu","c","tau","b"]
nn = [N5[f] for f in ORDER]
Cf = [mp.mpf(PDG[f]) / (M0 * gam(N5[f])) for f in ORDER]
y = [float(mp.log(c)) for c in Cf]

def lsfit(xs, ys, terms):
    """least squares for y = Σ terms[j](x)·β_j"""
    n = len(xs); m = len(terms)
    A = [[0.0]*m for _ in range(m)]; b = [0.0]*m
    for i in range(n):
        row = [t(xs[i]) for t in terms]
        for j in range(m):
            b[j] += row[j]*ys[i]
            for k in range(m):
                A[j][k] += row[j]*row[k]
    # solve via simple elimination
    for j in range(m):
        p = j
        while p < m and abs(A[p][j]) < 1e-12: p += 1
        if p >= m: continue
        A[j], A[p] = A[p], A[j]; b[j], b[p] = b[p], b[j]
        for k in range(j+1, m):
            f_ = A[k][j]/A[j][j]
            for l in range(j, m): A[k][l] -= f_*A[j][l]
            b[k] -= f_*b[j]
    beta = [0.0]*m
    for j in range(m-1, -1, -1):
        s_ = b[j]
        for k in range(j+1, m): s_ -= A[j][k]*beta[k]
        if abs(A[j][j]) > 1e-12: beta[j] = s_/A[j][j]
    return beta

def report(name, xs, resid, npar):
    mx = max(abs(r) for r in resid)
    rms = math.sqrt(sum(r*r for r in resid)/len(resid))
    tag = "✅形狀" if mx < 0.01 else ("🟡有前景" if mx < 0.10 else "❌負")
    print("  %-4s %d參數  max|lndev|=%.4f  rms=%.4f  %s" % (name, npar, mx, rms, tag))
    return mx

print("=" * 78)
print("C_f 形狀 scan (y = ln C_f; 8 點: n=%s)" % nn)
print("=" * 78)

# M1: quadratic in n
b1 = lsfit(nn, y, [lambda x: 1.0, lambda x: x, lambda x: x*x])
r1 = [y[i] - (b1[0] + b1[1]*nn[i] + b1[2]*nn[i]**2) for i in range(8)]
m1 = report("M1", nn, r1, 3)
gs = [gamam := float(mp.log(4*mp.sin(mp.pi*nn[i]/88)**2)) for i in range(6)]  # unused placeholder

# M2: quadratic in γ
gn = [float(4*mp.sin(mp.pi*nn[i]/88)**2) for i in range(8)]
b2 = lsfit(gn, y, [lambda x: 1.0, lambda x: x, lambda x: x*x])
r2 = [y[i] - (b2[0] + b2[1]*gn[i] + b2[2]*gn[i]**2) for i in range(8)]
m2 = report("M2", gn, r2, 3)

# M3: quadratic in ln γ
lg = [math.log(g) for g in gn]
b3 = lsfit(lg, y, [lambda x: 1.0, lambda x: x, lambda x: x*x])
r3 = [y[i] - (b3[0] + b3[1]*lg[i] + b3[2]*lg[i]**2) for i in range(8)]
m3 = report("M3", lg, r3, 3)

# M4: Gaussian peak in n (grid + refine)
best = None
for n0 in [x/10 for x in range(10, 121, 2)]:      # 1.0..12.0
    for s in [x/10 for x in range(2, 61)]:          # 0.2..6.0
        A = math.log(sum(math.exp(y[i]) for i in range(8)) / sum(math.exp(-(nn[i]-n0)**2/(2*s*s)) for i in range(8)))  # LS scale in linear space? keep log-space:
        # log-space LS for lnA given (n0,s): d/d(lnA) Σ (y−lnA+..)² = 0 → lnA = mean(y + (n−n0)²/2s²)
        lnA = sum(y[i] + (nn[i]-n0)**2/(2*s*s) for i in range(8))/8
        mx = max(abs(y[i] - (lnA - (nn[i]-n0)**2/(2*s*s))) for i in range(8))
        if best is None or mx < best[0]:
            best = (mx, n0, s, lnA)
mx4, n0b, sb, lnAb = best
r4 = [y[i] - (lnAb - (nn[i]-n0b)**2/(2*sb*sb)) for i in range(8)]
m4 = report("M4", nn, r4, 3)
print("        n₀=%.1f σ=%.1f" % (n0b, sb))

# M6: block constant (baseline)
blocks = [["e","u","d"], ["s","mu","c"], ["tau","b"]]
blk_idx = {}
for g, blk in enumerate(blocks):
    for f in blk: blk_idx[f] = g
b6 = [sum(y[i] for i in range(8) if blk_idx[ORDER[i]] == g)/len(blocks[g]) for g in range(3)]
r6 = [y[i] - b6[blk_idx[ORDER[i]]] for i in range(8)]
m6 = report("M6", nn, r6, 3)

# M5: block amplitude × shared concave shape ln(1 + c(x−1)²)
xmap = {"e":0,"u":1,"d":2, "s":0,"mu":1,"c":3, "tau":0,"b":2}
best5 = None
for c in [k/200 for k in range(-199, 2001, 1)]:   # −0.995 .. 10.0
    if 1 + c*(3-1)**2 <= 0: continue               # 選 x=3 (c) 最大
    shape = [math.log(1 + c*(xmap[ORDER[i]]-1)**2) for i in range(8)]
    # LS for A_g: per block
    res = [0.0]*8
    ok = True
    for g, blk in enumerate(blocks):
        idxs = [i for i in range(8) if blk_idx[ORDER[i]] == g]
        if len(idxs) == 0: ok = False; break
        mu_ = sum((y[i] - shape[i]) for i in idxs)/len(idxs)
        for i in idxs: res[i] = y[i] - (mu_ + shape[i])
    if not ok: continue
    mx = max(abs(r) for r in res)
    if best5 is None or mx < best5[0]:
        best5 = (mx, c, [sum((y[i]-shape[i]) for i in range(8) if blk_idx[ORDER[i]] == gg)/len(blocks[gg])
                         for gg in range(3)])
mx5, c5, A5 = best5
r5 = [y[i] - (A5[blk_idx[ORDER[i]]] + math.log(1 + c5*(xmap[ORDER[i]]-1)**2)) for i in range(8)]
m5 = report("M5", nn, r5, 4)
print("        c=%.3f  A_g={gen1: %.4f, gen2: %.4f, gen3: %.4f}  (塊波幅, exp)"
      % (c5, math.exp(A5[0]), math.exp(A5[1]), math.exp(A5[2])))

print()
check("有形狀 match (max<1%)", min(m1,m2,m3,m4,m5) < 0.01)
check("有前景形狀 (max<10%)", min(m1,m2,m3,m4,m5) < 0.10,
      "best=%.4f" % min(m1,m2,m3,m4,m5))

# 局部極值位置觀察（明確標示: 未盲測, 只係觀察）
peaks = [nn[i] for i in range(8) if (i==0 or y[i]>y[i-1]) and (i==7 or y[i]>y[i+1])]
vals  = [nn[i] for i in range(8) if i>0 and i<7 and y[i]<y[i-1] and y[i]<y[i+1]]
print("\n觀察（唔係證據, 未盲測）: local max n=%s · local min n=%s" % (peaks, vals))
print("  max 集合 = {1,3,6,10}+1 (三角數+1)?  min 集合 = {2,4,8}+1 (2^k+1)?  — 需盲測, 大概率巧合")

out = {"models": {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6},
       "M5": {"c": c5, "block_amp": [math.exp(A5[0]), math.exp(A5[1]), math.exp(A5[2])]},
       "peak_positions": peaks, "valley_positions": vals}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "05_shape_scan.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL" % (PASS, FAIL))