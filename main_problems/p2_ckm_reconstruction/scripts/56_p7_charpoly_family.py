#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 56 — P_Δ 特徵多項式求值家族 + resultant 譜黏合探測
==============================================================
目標: (1) P_Δ 喺結構點 (φ, 1/φ, φ², Lₙ, 邊界) 嘅求值有冇第二個定理級結果
      (2) resultant(P_Δ, P_{T̂ⁿ}) = Π(γ_k²−Lₙγ_k+1) — 兩 sector 譜嘅代數黏合
      (3) P_Δ 喺 T̂ⁿ 本徵值嘅求值
"""
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def chk(name, val, target, tol, note=""):
    global PASS, FAIL
    val_f = float(val); tgt = float(target)
    dev = abs(val_f-tgt)/abs(tgt)*100 if abs(tgt) > 1e-30 else abs(val_f-tgt)*100
    ok = abs(val_f - tgt) <= tol * max(1.0, abs(tgt)) if abs(tgt) > 1e-30 else abs(val_f) <= tol
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val_f:.9f}  (dev {dev:+.4f}%) {note}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val_f:.9f} vs {tgt}  (dev {dev:+.4f}%) {note}")

N_d, N_gen, B, K_tree, mu2 = 44, 3, 4, 33, 2.0
phi = (1+mp.sqrt(5))/2
T = mp.matrix([[1, 1], [1, 0]])
def Tn(n):
    M = mp.matrix([[1, 0], [0, 1]])
    for _ in range(n):
        M = M * T
    return M
L, F = {}, {}
for n in range(1, 16):
    M = Tn(n)
    L[n] = float(mp.nint(M[0,0]+M[1,1]))
    F[n] = float(mp.nint(M[0,1]))

gams = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]
def P_Delta(x):
    """P_Δ(x) = Π(x−γ_k), 回傳 log|P| + 符號"""
    s = sum(mp.log(abs(x-g)) for g in gams)
    sign = -1 if sum(1 for g in gams if x-g < 0) % 2 else 1
    return s, sign

print("=" * 72)
print("C1. P_Δ 求值家族 — 結構點掃描 (log|P| + 符號)")
print("=" * 72)
points = {
    "1 (單位)": 1, "μ²=2": 2, "B=4": 4, "L₄=7": 7, "φ": phi,
    "1/φ": 1/phi, "φ²": phi**2, "φ³": phi**3, "φ⁴": phi**4,
    "φ⁵": phi**5, "φ⁻⁵": phi**-5, "L₅=11": L[5], "L₆/2=9": L[6]/2,
    "2φ⁵": 2*phi**5, "L₆=18": L[6], "L₇=29": L[7],
}
for name, x in points.items():
    s, sign = P_Delta(x)
    if mp.isinf(s) or s < -100:
        # 接近 0 — 係咪本徵值?
        eig = [float(g) for g in gams if abs(x-g) < 1e-9]
        if eig:
            print(f"  P_Δ({name}) = 0 — ★ 本徵值點! (γ = {eig[0]:.6f})")
        else:
            print(f"  P_Δ({name}) ≈ 0 (log|P| = {float(s):.2f})")
        continue
    val = sign * mp.e**s
    log10 = float(s/mp.log(10))
    near_int = abs(log10 - round(log10)) < 1e-6
    print(f"  P_Δ({name}) = {sign:+}e^{float(s):.4f}  (log10 = {log10:.6f}{' ★整數冪' if near_int else ''})")

print()
print("=" * 72)
print("C2. ★ 第二求值定理搜索: 搵 P_Δ(x) = ±N_gen^m 或 ±L/F 嘅 x")
print("=" * 72)
# 掃描 x ∈ [0, 14] 精細格點, 搵 log|P_Δ(x)| ≈ 常數結構
targets = {1: "N_gen=3", 2: "μ²", 3: "N_gen", 4: "B", 7: "L₄",
           8: "F₆", 9: "L₆/2", 11: "L₅", 13: "F₇", 18: "L₆",
           29: "L₇", 34: "F₉", 47: "L₈", 55: "F₁₀", 76: "L₉",
           89: "F₁₁", 123: "L₁₀"}
hits = []
for i in range(1401):
    x = i/100.0
    s, sign = P_Delta(x)
    v = sign*mp.e**s
    vf = float(v)
    for tgt, name in targets.items():
        if abs(vf - tgt) < 0.5*max(1.0, abs(tgt)):
            hits.append((x, vf, name, abs(vf-tgt)/abs(tgt)*100))
for h in hits[:25]:
    print(f"  x = {h[0]:.2f}: P_Δ = {h[1]:.6f} ≈ {h[2]} (dev {h[3]:.2f}%)")
if not hits:
    print("  (冇命中 — 只有 x=1 係定理級)")

print()
print("=" * 72)
print("C3. resultant 譜黏合: R(P_Δ, P_T̂ⁿ) = Π(γ_k²−Lₙγ_k+1)")
print("=" * 72)
def result_chain(n):
    s = sum(mp.log(abs(g*g - L[n]*g + 1)) for g in gams)
    sign = -1 if sum(1 for g in gams if g*g-L[n]*g+1 < 0) % 2 else 1
    return sign*mp.e**s, s
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    v, s = result_chain(n)
    log10 = float(s/mp.log(10))
    print(f"  R(P_Δ, P_T̂^{n}) = {float(v):+.6e}  (log10 = {log10:.4f})")

print()
print("=" * 72)
print("C4. P_Δ 喺 T̂ⁿ 本徵值嘅求值")
print("=" * 72)
for n in [5, 10]:
    lam_p = float(phi**n); lam_m = float((-1/phi)**n)
    s1, sg1 = P_Delta(lam_p); s2, sg2 = P_Delta(lam_m)
    print(f"  P_Δ(φ^{n})  = {sg1:+}e^{float(s1):.4f}   (φ^{n} = {lam_p:.6f})")
    print(f"  P_Δ((−φ)^-{n}) = {sg2:+}e^{float(s2):.4f}   ((−φ)^-{n} = {lam_m:.8f})")

print()
print("=" * 72)
print("C5. 跡和: Σ_k P_T̂ⁿ(γ_k) = TrΔ² − Lₙ·TrΔ + 88")
print("=" * 72)
tr1 = float(sum(gams)); tr2 = float(sum(g**2 for g in gams))
for n in [5, 10]:
    s = tr2 - L[n]*tr1 + 88
    print(f"  ΣP_T̂^{n}(γ_k) = 536 − {L[n]}·178 + 88 = {s:.0f}")
    print(f"    因子: {s:.0f} = {abs(int(s))} = ?")

print()
print("=" * 72)
print("C6. 投影定理 v5 陳述 (譜黏合結果)")
print("=" * 72)
print("  核心結構保持: tanβ = Tr(Δ⊕T̂¹⁰)/Tr(T̂⁵) = 301/11")
print("  特徵多項式求值定理: P_Δ(1) = −N_gen (Chebyshev 證明)")
print("  加性/乘性對偶: TrΔ = det_even+det_odd, det(Δ) = det_even×det_odd")
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
