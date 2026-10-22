#!/usr/bin/env python3
# O195 scripts/06 — artanh(δ) 奇異點精確身份: δ=±1 根 vs I₀ 零點 (極點非奇異點)
# artanh(δ) = ½ln((1+δ)/(1−δ)): 奇異點只喺 δ=±1 (log 分支點)
# δ=1 ⟺ 88·I₀(2t) = sinh(2t); δ=−1 ⟺ 88·I₀(2t) = −sinh(2t)
# I₀ 零點 (δ 極點): artanh → ½ln(−1) = iπ/2 常數, 唔係奇異點 ← 關鍵修正
import mpmath as mp
mp.mp.dps = 50

def Fp(t):   # δ = 1
    return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
def Fm(t):   # δ = −1
    return 88*mp.besseli(0, 2*t) + mp.sinh(2*t)

# 精細掃描 log|F| 搵局部極小 → Newton 收斂
def find_nearest(F, rmax=3.0, step=0.05):
    best = None
    grid = mp.linspace(0, rmax, int(rmax/step)+1)
    for re_ in grid:
        for im_ in grid:
            t0 = mp.mpc(re_, im_)
            r = abs(t0)
            if r < 0.3 or r > rmax: continue
            try:
                root = mp.findroot(F, t0, tol=1e-30, maxsteps=80)
            except Exception:
                continue
            if abs(root) < 1e-10: continue
            if best is None or abs(root) < abs(best):
                best = root
    return best

r1 = find_nearest(Fp)
r1m = find_nearest(Fm)
print("== δ=1 根 (88I₀ = sinh) ==")
print(f"  t = {mp.nstr(r1, 16)},  |t| = {float(abs(r1)):.12f}")
print(f"  arg = {float(mp.arg(r1)):.6f} rad = {float(mp.arg(r1)*180/mp.pi):.4f}°")
print("== δ=−1 根 (88I₀ = −sinh) ==")
print(f"  t = {mp.nstr(r1m, 16)},  |t| = {float(abs(r1m)):.12f}")
print(f"  arg = {float(mp.arg(r1m)):.6f} rad = {float(mp.arg(r1m)*180/mp.pi):.4f}°")

j1 = mp.besseljzero(0, 1)
print(f"\n== 對比 ==")
print(f"  I₀ 首零點 t = i·j₁/2:  |t| = {float(j1/2):.12f}  (δ 極點 — 非奇異點!)")
print(f"  artanh 喺極點: artanh(δ→∞) → ½ln(−1) = iπ/2 常數 ⟹ 冇奇異點")
print(f"  δ=1 根 |t| = {float(abs(r1)):.12f}")
print(f"  δ=−1 根 |t| = {float(abs(r1m)):.12f}")

# δ=1 根嘅實部好細? 接近純虛?
print(f"\n  δ=1:  Re = {float(r1.real):.2e},  Im = {float(r1.imag):.8f}")
print(f"  δ=−1: Re = {float(r1m.real):.2e},  Im = {float(r1m.imag):.8f}")

# 實軸根: 88I₀(2x) = sinh(2x) 大實根
x = 130.0
for _ in range(60):
    f = 88*mp.besseli(0, 2*x) - mp.sinh(2*x)
    fp = 176*mp.besseli(1, 2*x) - 2*mp.cosh(2*x)
    x -= f/fp
print(f"\n  δ=1 實軸根: x = {mp.nstr(x, 12)}")

# 漸近論證: δ=1 根最近 ⟹ 衰減率 R⁻² = 1/|r1|²
R = abs(r1)
print(f"\n  R⁻² = {float(1/R**2):.10f}")
print(f"  4/j₁² = {float(4/j1**2):.10f}  (arcsine 尺度, O195 Thm4)")
print(f"  差異 = {float(abs(1/R**2 - 4/j1**2)):.2e}")
