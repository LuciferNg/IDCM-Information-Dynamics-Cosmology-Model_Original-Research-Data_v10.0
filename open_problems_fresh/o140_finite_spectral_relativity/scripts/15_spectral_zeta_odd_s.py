#!/usr/bin/env python3
"""
O140 — spectral-zeta 奇 s 攻堅 v2 (2026-10-09)
==============================================
v1 發現: 奇 s 擬合 deg-4 FAIL (N=14 onward 偏差), 但原因係 deg 太低。
關鍵定理(csc 和, Euler/Bernoulli):
  Σ_{k=1}^N csc^{2m}(πk/2N) 係 N 嘅有理多項式, 次數 2m
  ζ_N(s) = Σ ε_k^{-s} = Σ csc^{2s}(πk/2N)/4^s
  ⟹ ζ_N(s) 係 N 嘅有理多項式, 次數 2s, 對所有 s (奇偶一樣!)
  ⟹ docs/08 「奇數 s 冇閉式」可能係錯判, 要 append-only 更正

v2: 用 deg=2s + 2s+1 個擬合點, 驗證 s=1..6 全部有閉式
"""
import math
from fractions import Fraction

def eps(k, Nv):
    return 4*math.sin(math.pi*k/(2*Nv))**2
def zeta_N(s, Nv):
    return sum(eps(k, Nv)**(-s) for k in range(1, Nv+1))

def fit_poly(vals_xy, deg):
    """Vandermonde + Fraction Gaussian elimination, 解 deg+1 個係數"""
    xs = [Fraction(x) for x, _ in vals_xy]
    ys = [Fraction(y).limit_denominator(10**14) for _, y in vals_xy]
    n = len(xs)
    A = [[xs[i]**j for j in range(n)] for i in range(n)]
    b = ys[:]
    for i in range(n):
        if A[i][i] == 0:
            for j in range(i+1, n):
                if A[j][i] != 0:
                    A[i], A[j] = A[j], A[i]
                    b[i], b[j] = b[j], b[i]
                    break
        piv = A[i][i]
        for j in range(i, n):
            A[i][j] /= piv
        b[i] /= piv
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i]
                for j in range(i, n):
                    A[r][j] -= f*A[i][j]
                b[r] -= f*b[i]
    return b

print("="*72)
print("1. 全 s=1..6: deg=2s 有理多項式擬合 + 樣本外驗證")
print("="*72)
results = {}
for s in range(1, 7):
    deg = 2*s
    pts = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28][:deg+1]
    vals = [(Nv, zeta_N(s, Nv)) for Nv in pts]
    coeffs = fit_poly(vals, deg)
    # 樣本外: 30, 36, 44
    ok = True
    detail = ""
    for Nt in [30, 36, 44]:
        pred = sum(float(c)*Nt**i for i, c in enumerate(coeffs))
        val = zeta_N(s, Nt)
        rel = abs(pred-val)/val
        if rel > 1e-6:
            ok = False
        detail += f" N={Nt}:rel={rel:.1e}"
    results[s] = (ok, coeffs)
    print(f"  s={s} (deg={deg}): {'✅ 閉式(樣本外吻合)' if ok else '❌ FAIL'}{detail}")
    if ok:
        # 簡化: 顯示前導係數 + 常數
        lead = coeffs[-1]
        const = coeffs[0]
        print(f"      前導 N^{deg} 係數 = {lead} = {float(lead):.6f}")
        print(f"      常數項       = {const} = {float(const):.6f}")

print("="*72)
print("2. 前導係數結構: 同 (N/π)^{2s} ζ_R(2s) 關係")
print("="*72)
for s in range(1, 7):
    if s not in results: continue
    ok, coeffs = results[s]
    if not ok: continue
    lead = float(coeffs[-1])
    zR = sum(1/m**(2*s) for m in range(1, 200000))
    pred_lead = zR/(math.pi**(2*s))
    print(f"  s={s}: 前導 = {lead:.8f},  ζ_R(2s)/π^(2s) = {pred_lead:.8f}, 比 = {lead/pred_lead:.8f}")

print("="*72)
print("3. 全 s 閉式總表 (s=1..6)")
print("="*72)
for s in range(1, 7):
    ok, coeffs = results[s]
    if not ok:
        print(f"  s={s}: ❌")
        continue
    # Fraction 字串 (簡化: 只列非零低度 0,1,2 同最高)
    cstr = []
    for i in range(len(coeffs)):
        c = coeffs[i]
        if c != 0:
            if c.denominator == 1:
                cstr.append(f"{c.numerator}N^{i}")
            else:
                cstr.append(f"({c.numerator}/{c.denominator})N^{i}")
    print(f"  ζ_N({s}) = " + " + ".join(cstr))
    print()

print("="*72)
print("4. 判決: docs/08『奇數 s 冇閉式』更正")
print("="*72)
s3_ok = results.get(3, (False,))[0]
s5_ok = results.get(5, (False,))[0]
s7_ok = results.get(7, (False,))[0]  # 唔喺 loop 入面 — 睇下面
print(f"  s=3 閉式: {'✅' if s3_ok else '❌'}")
print(f"  s=5 閉式: {'✅' if s5_ok else '❌'}")
print(f"  s=7: 需 deg=14, 用 15 點 —— 另行驗證")

# 特別驗證 s=7 (deg 14) — 需要 deg+1 = 15 點! 4..32 step 2 = 15 點
deg = 14
pts = list(range(4, 4+2*deg+1, 2))[:deg+1]   # 4,6,...,32
assert len(pts) == deg+1, f"need {deg+1} points, got {len(pts)}"
vals = [(Nv, zeta_N(7, Nv)) for Nv in pts]
coeffs7 = fit_poly(vals, deg)
ok7 = True
for Nt in [34, 40, 44]:
    pred = sum(float(c)*Nt**i for i, c in enumerate(coeffs7))
    val = zeta_N(7, Nt)
    rel = abs(pred-val)/val
    if rel > 1e-6:
        ok7 = False
        print(f"    s=7 N={Nt}: rel={rel:.2e} ✗")
    else:
        print(f"    s=7 N={Nt}: rel={rel:.2e} ✓")
print(f"  s=7 (deg 14): {'✅ 閉式存在' if ok7 else '❌ FAIL'}")

with open('data/spectral_zeta_odd_s.json', 'w') as f:
    import json
    json.dump({
        's1_closed': results[1][0], 's2_closed': results[2][0],
        's3_closed': s3_ok, 's5_closed': s5_ok, 's7_closed': ok7,
        'note': '奇s一樣有閉式 (csc偶冪和, Bernoulli結構) — docs/08判斷需更正',
    }, f, indent=2, ensure_ascii=False)
print("-> data/spectral_zeta_odd_s.json")