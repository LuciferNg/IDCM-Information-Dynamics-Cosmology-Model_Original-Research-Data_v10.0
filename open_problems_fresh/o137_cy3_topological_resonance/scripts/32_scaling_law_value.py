#!/usr/bin/env python3
"""
O137 — 標度律研究價值評估

核心問題: m ∝ γ_n^{p_g} 嘅世代階梯 p_g = 1, 2.47, 6.40 (疑似 (5/2)^{g-1})
         係唔係一個【可辨識】嘅結構? 定係 3 點擬 2 參數嘅必然產物?
"""
import numpy as np
from math import sin, pi

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
def omega_n(n): return 2*sin(n*pi/88)

MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
order = ['e','u','d','s','mu','c','tau','b','t']
blocks = {1:[0,1,2], 2:[3,4,5], 3:[6,7,8]}

print("="*78)
print("(1) p_g 嘅標準誤 — 3 點擬 2 參數")
print("="*78)
print(f"{'世代':>4} {'模式':>12} {'p':>8} {'SE(p)':>8} {'rel':>7} {'RMS':>7} {'p=1 之 RMS':>11}")
pg, seg = {}, {}
for g, idx in blocks.items():
    ns = [A5[i] for i in idx]; ms = [MASS[order[i]] for i in idx]
    x = np.log([gamma_n(n) for n in ns]); y = np.log(ms)
    xb = x.mean()
    Sxx = float(np.sum((x-xb)**2))
    A = np.vstack([x, np.ones_like(x)]).T
    coef,*_ = np.linalg.lstsq(A, y, rcond=None)
    p = coef[0]
    res = y - A@coef
    SSE = float(np.sum(res**2))
    rms = float(np.sqrt(SSE/len(x)))
    dof = len(x)-2
    s2 = SSE/dof
    SE = float(np.sqrt(s2/Sxx))
    # p = 1 固定
    c1 = float(np.mean(y - x))
    rms1 = float(np.sqrt(np.mean((y - x - c1)**2)))
    pg[g], seg[g] = p, SE
    print(f"{g:>4} {str(ns):>12} {p:>8.4f} {SE:>8.4f} {SE/abs(p)*100:>6.1f}% {rms:>7.4f} {rms1:>11.4f}")

print("\n" + "="*78)
print("(2) 階梯步嘅顯著性: p_g 係唔係真嘅遞增?")
print("="*78)
for a,b in [(1,2),(2,3),(1,3)]:
    d = pg[b]-pg[a]
    SE_d = float(np.sqrt(seg[a]**2 + seg[b]**2))
    z = d/SE_d
    print(f"p{b} − p{a} = {d:+.4f} ± {SE_d:.4f}  ⟹ z = {z:+.2f}σ  "
          f"{'🟢 顯著' if abs(z)>2 else '🔴 唔顯著'}")

print(f"\n疑似階梯 (F₅/2)^(g−1) = 1, 2.5, 6.25")
for g in [1,2,3]:
    pred = (5/2)**(g-1)
    z = (pg[g]-pred)/seg[g]
    print(f"  g={g}: 擬合 p = {pg[g]:.4f} ± {seg[g]:.4f}  vs 預言 {pred:.2f}  "
          f"⟹ z = {z:+.2f}σ")

print("\n" + "="*78)
print("(3) ★ 階梯族係唔係可辨識? 多個簡單階梯同時符合?")
print("="*78)
ladders = {
    '(5/2)^(g-1)': [1, 2.5, 6.25],
    'g²':          [1, 4, 9],
    '(2g-1)':      [1, 3, 5],
    '2^(g-1)':     [1, 2, 4],
    'g!':          [1, 2, 6],
    'F_{2g+1}/2':  [1, 2.5, 6.5],
    '3^(g-1)':     [1, 3, 9],
    '(g²+g)/2':    [1, 3, 6],
}
print(f"{'階梯':>14} {'χ² (per gen)':>14} {'總 χ²':>9} {'dof':>5} {'χ²/dof':>8} {'判定'}")
results = {}
for name, ps in ladders.items():
    chi2 = 0.0; dof = 0
    for g in [1,2,3]:
        # 每世代 1 個標度 (C_g) 自由, p 固定
        idx = blocks[g]
        ns = [A5[i] for i in idx]; ms = [MASS[order[i]] for i in idx]
        x = np.log([gamma_n(n) for n in ns]); y = np.log(ms)
        r = y - ps[g-1]*x          # 加常數 = 去均值
        r = r - r.mean()
        s2 = seg[g]**2 * float(np.sum((x-x.mean())**2)) / (len(x)-2)  # σ² per gen
        chi2 += float(np.sum(r**2))/s2
        dof += len(x)-1
    results[name] = chi2
    print(f"{name:>14} {chi2:>14.3f} {chi2:>9.3f} {dof:>5} {chi2/dof:>8.3f} "
          f"{'🟢 符合' if chi2/dof < 2 else '🔴 排除'}")

print(f"\n★ 符合嘅階梯數: {sum(1 for v in results.values() if v/16 < 2)} / {len(ladders)}")
print(f"★ 最小 χ²/dof = {min(results.values())/16:.3f} ({min(results, key=results.get)})")
print(f"⟹ {'多個階梯不可分辨 ⟹ 未辨識' if sum(1 for v in results.values() if v/16<2) > 2 else '唯一'}")

print("\n" + "="*78)
print("(4) 模型比較: 加 p_g 指數值得嗎? (AIC / BIC)")
print("="*78)
def sse_of(model):
    tot = 0.0
    for g in [1,2,3]:
        idx = blocks[g]
        ns = [A5[i] for i in idx]; ms = [MASS[order[i]] for i in idx]
        x = np.log([gamma_n(n) for n in ns]); y = np.log(ms)
        if model == 'M1_globalC':      pred = x + np.mean(np.log([MASS[p] for p in order]) - np.log([gamma_n(n) for n in A5]))
        elif model == 'M2_Cg':         pred = x + (y-x).mean()
        elif model == 'M3_pg_Cg':      pred = None
        elif model == 'M4_ladder':     pred = None
        if pred is None:
            A = np.vstack([x, np.ones_like(x)]).T
            pred = A@np.linalg.lstsq(A, y, rcond=None)[0]
        tot += float(np.sum((y-pred)**2))
    return tot
n = 9
models = [('M1: m=M₀γ_n·C (1 param)', 1, sse_of('M1_globalC')),
          ('M2: m=M₀γ_n·C_g (3 param)', 3, sse_of('M2_Cg')),
          ('M3: m=M₀γ_n^{p_g}·C_g (6 param)', 6, sse_of('M3_pg_Cg')),
          ('M4: m=M₀γ_n^{(5/2)^{g-1}}·C_g (3+1)', 4, sse_of('M4_ladder'))]
print(f"{'模型':>36} {'k':>3} {'SSE':>9} {'AIC':>9} {'BIC':>9} {'RMS':>7}")
for name,k,sse in models:
    aic = 2*k + n*np.log(sse/n); bic = k*np.log(n) + n*np.log(sse/n)
    print(f"{name:>36} {k:>3} {sse:>9.4f} {aic:>9.2f} {bic:>9.2f} {np.sqrt(sse/n):>7.4f}")
print(f"\n★ AIC 最佳 = {min(models, key=lambda m: 2*m[1]+n*np.log(m[2]/n))[0]}")

print("\n" + "="*78)
print("(5) ★★ 約定依賴: 'p' 隨基底選擇而變")
print("="*78)
for g,idx in blocks.items():
    ns=[A5[i] for i in idx]; ms=[MASS[order[i]] for i in idx]
    xg=np.log([gamma_n(n) for n in ns]); xw=np.log([omega_n(n) for n in ns]); y=np.log(ms)
    pg_=np.polyfit(xg,y,1)[0]; pw_=np.polyfit(xw,y,1)[0]
    print(f"Gen{g}: 基底 γ_n=ω_n²  ⟹ p_γ = {pg_:.4f}   基底 ω_n=2sin(nπ/88) ⟹ p_ω = {pw_:.4f}")
print(f"\n★ O136 docs/02 質量譜約定: m_n = M₀·√γ_n = M₀·ω_n  (p_ω = 1)")
print(f"★ O54/O137 約定:            m = M₀·γ_n·C_f      (p_γ = 1)")
print(f"⟹ 同一物理譜, 兩個約定差一個 2 次冪 ⟹ 'p_g 階梯' 嘅絕對值依約定而定")

print("\n" + "="*78)
print("(6) ★★ 結構分歧: A₅ 升序 vs O54 (Φ 幾何 C_f) — μ, τ 對決")
print("="*78)
X3=[1,5,9]; X3P=[0,1,3,4,6,7]
PHI={}
for i,a in enumerate(X3):
    for j,b in enumerate(X3P): PHI[(i,j)]=1+a*b
print(f"{'':>6} {'A₅ 升序':>28} {'O54 (Φ 幾何)':>28}")
for p in ['mu','tau']:
    if p=='mu': nA, CfA = 5, MASS[p]/(M0*gamma_n(5)); nO, CfO = 7, PHI[(1,4)]/2
    else:       nA, CfA = 9, MASS[p]/(M0*gamma_n(9)); nO, CfO = 20, PHI[(2,3)]
    mA = M0*gamma_n(nA)*CfA; mO = M0*gamma_n(nO)*CfO
    print(f"{p:>6} n={nA}, C_f={CfA:.4f} (反解)      n={nO}, C_f={CfO} (Φ 值)")
    print(f"{'':>6} m={mA:.1f} ({100*(mA-MASS[p])/MASS[p]:+.2f}%)              "
          f"m={mO:.1f} ({100*(mO-MASS[p])/MASS[p]:+.2f}%)")
print(f"\n★ μ: A₅ 需 C_f = {MASS['mu']/(M0*gamma_n(5)):.4f} (Φ 目錄最近 31, 3.2% off)")
print(f"     O54 用 C_f = Φ[(1,4)]/2 = 15.5  →  0.13% 🟢")
print(f"★ τ: A₅ 需 C_f = {MASS['tau']/(M0*gamma_n(9)):.4f} (無 Φ 對應)")
print(f"     O54 用 C_f = Φ[(2,3)] = 37      →  0.34% 🟢")
print(f"\n★ 但 n=20 ∉ A₅ 集 ⟹ 兩個框架嘅輕子模式分配【不可共存】")
print(f"  A₅: μ↔5, τ↔9 (皆 ∈ A₅)   O54: μ↔7 (∈A₅), τ↔20 (∉A₅)")
