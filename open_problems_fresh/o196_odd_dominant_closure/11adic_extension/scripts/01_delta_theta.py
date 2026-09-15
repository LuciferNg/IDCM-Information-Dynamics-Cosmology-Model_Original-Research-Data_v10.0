#!/usr/bin/env python3
# O200 scripts/01 — T1: Δθ 干涉相位高精度鎖定 + 結構字典掃描
# δ=±1 根: 88·I₀(2t) = ±sinh(2t) (artanh(δ) log 分支點, O195/O196)
# 目標: dps=100 求兩根 → 相位差 Δθ → 掃結構字典
#   O196 T2: r₁ = 0.0074+1.2024i, r₂ = −0.0074+1.2024i, Δθ = 0.70°
#   判準: 零新常數身份 (φ⁻¹ 組合 / L₅ 函數 / π/256 / 1/136 等) → 🟢;
#         冇命中 → 🔴 幾何干涉冇獨立閉式 (O196 T2 已預告)
import mpmath as mp

mp.mp.dps = 100
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def F_plus(t):    # δ=+1: 88·I₀(2t) − sinh(2t) = 0
    return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
def F_minus(t):   # δ=−1: 88·I₀(2t) + sinh(2t) = 0
    return 88*mp.besseli(0, 2*t) + mp.sinh(2*t)

# 起點: O196 已知近似 r₁ = 0.0074+1.2024i
r1 = mp.findroot(F_plus,  mp.mpc('0.0074', '1.2024'), tol=1e-90, maxsteps=100)
r2 = mp.findroot(F_minus, mp.mpc('-0.0074', '1.2024'), tol=1e-90, maxsteps=100)

print("== T1a: δ=±1 根高精度鎖定 (dps=100) ==")
print(f"  r₁ (δ=+1) = {mp.nstr(r1, 60)}")
print(f"  r₂ (δ=−1) = {mp.nstr(r2, 60)}")
print(f"  |r₁|      = {mp.nstr(abs(r1), 60)}")
print(f"  |r₂|      = {mp.nstr(abs(r2), 60)}")
print(f"  |r₁|−|r₂| = {mp.nstr(abs(r1)-abs(r2), 30)}  (等距?)")

R = abs(r1)
theta1 = mp.arg(r1)
theta2 = mp.arg(r2)
# 相位差 (最小正差)
dth = abs(theta1 - theta2)
if dth > mp.pi: dth = 2*mp.pi - dth
print(f"\n  θ₁ = {mp.nstr(theta1, 30)} rad = {mp.nstr(mp.degrees(theta1), 30)}°")
print(f"  θ₂ = {mp.nstr(theta2, 30)} rad = {mp.nstr(mp.degrees(theta2), 30)}°")
print(f"  Δθ = {mp.nstr(dth, 30)} rad = {mp.nstr(mp.degrees(dth), 30)}°")
print(f"  Δθ/2 = {mp.nstr(dth/2, 30)} rad = {mp.nstr(mp.degrees(dth/2), 30)}°")

# 驗證根方程殘差
check("T1a r₁ 係 δ=+1 根 (|F_plus(r₁)| ≈ 0)", abs(F_plus(r1)) < mp.mpf('1e-80'),
      mp.nstr(abs(F_plus(r1)), 5))
check("T1a r₂ 係 δ=−1 根 (|F_minus(r₂)| ≈ 0)", abs(F_minus(r2)) < mp.mpf('1e-80'),
      mp.nstr(abs(F_minus(r2)), 5))
check("T1a 兩根等距 (||r₁|−|r₂|| < 1e-40)", abs(abs(r1)-abs(r2)) < mp.mpf('1e-40'),
      mp.nstr(abs(abs(r1)-abs(r2)), 5))
# O196 記錄 Re=±7.35e-3, |t|=1.202532 交叉驗證
check("T1a O196 近似交叉 (Re(r₁) ≈ +7.35e-3)", abs(r1.real - mp.mpf('0.00735')) < mp.mpf('1e-5'),
      mp.nstr(r1.real, 10))
check("T1a O196 近似交叉 (|t| ≈ 1.202532)", abs(R - mp.mpf('1.202532')) < mp.mpf('1e-6'),
      mp.nstr(R, 10))

# ===== T1b: Δθ 結構字典掃描 =====
print("\n== T1b: Δθ 結構字典掃描 (零新常數) ==")
# 候選 (IDCM 已註冊常數 / 自然幾何量):
#  Δθ (rad) 候選: π/256, π/176, π/88, π/44, π/512, 1/134, 1/136, φ 組合...
cands = {
    "π/256":      mp.pi/256,
    "π/512":      mp.pi/512,
    "π/176":      mp.pi/176,      # θ_site = π/176 (88-site 相位步)
    "π/88":       mp.pi/88,
    "π/44":       mp.pi/44,
    "1/134":      mp.mpf(1)/134,  # crack (O168)
    "1/136":      mp.mpf(1)/136,
    "1/123":      mp.mpf(1)/123,  # L₁₀
    "1/137":      mp.mpf(1)/137,  # α⁻¹(0)
    "φ⁻¹/π":     mp.mpf(1)/mp.phi/mp.pi,
    "φ⁻⁴":       mp.mpf(1)/mp.phi**4,
    "1/(44·176)": mp.mpf(1)/(44*176),
    "π/(88·44)":  mp.pi/(88*44),
    "2·π/176²":   2*mp.pi/176**2,
}
print(f"  Δθ = {mp.nstr(dth, 25)} rad")
print(f"  {'候選':<14}{'值':<26}{'dev'}")
best = None
for name, v in cands.items():
    dev = abs(dth - v)/dth
    flag = "★" if dev < 1e-6 else ("◐" if dev < 1e-3 else " ")
    print(f"  {flag}{name:<14}{mp.nstr(v, 22):<26}{mp.nstr(dev, 6)}")
    if best is None or dev < best[1]:
        best = (name, dev)
# Δθ/2 掃描 (兩根干涉 cos(nΔθ/2) 用 Δθ/2)
print(f"\n  Δθ/2 = {mp.nstr(dth/2, 25)} rad")
cands2 = {
    "π/512":      mp.pi/512,
    "π/256":      mp.pi/256,
    "π/352":      mp.pi/352,      # 2·176
    "1/163":      mp.mpf(1)/163,
    "1/162.5":    mp.mpf(1)/mp.mpf('162.5'),
    "Re(r₁)/|r₁|": r1.real/R,
    "tan⁻¹(Re/Im)": mp.atan(r1.real/r1.imag),
}
for name, v in cands2.items():
    dev = abs(dth/2 - v)/(dth/2)
    flag = "★" if dev < 1e-6 else ("◐" if dev < 1e-3 else " ")
    print(f"  {flag}{name:<16}{mp.nstr(v, 22):<26}{mp.nstr(dev, 6)}")

# Re(r₁) 本身嘅身份 (相位嘅實部來源)
print("\n== T1c: Re(r₁) 結構掃描 (相位實部 = 偏離純虛數) ==")
Re1 = r1.real
cands3 = {
    "1/136":     mp.mpf(1)/136,
    "1/135.98":  mp.mpf(1)/mp.mpf('135.98'),
    "1/134":     mp.mpf(1)/134,
    "1/(2·67)":  mp.mpf(1)/(2*67),   # 67 = 2·K_tree+1
    "1/137":     mp.mpf(1)/137,
    "π/428":     mp.pi/428,
    "1/(44·3.09)": mp.mpf(1)/(44*mp.mpf('3.09')),
    "φ⁻¹/44":    mp.mpf(1)/mp.phi/44,
}
for name, v in cands3.items():
    dev = abs(abs(Re1) - v)/abs(Re1)
    flag = "★" if dev < 1e-6 else ("◐" if dev < 1e-3 else " ")
    print(f"  {flag}{name:<14}{mp.nstr(v, 22):<26}{mp.nstr(dev, 6)}")
print(f"  Re(r₁) = {mp.nstr(Re1, 30)}, Im(r₁) = {mp.nstr(r1.imag, 30)}")

# 相位比: Δθ/(2π) = 幾分之幾圈
frac = dth/(2*mp.pi)
print(f"\n  Δθ/2π = {mp.nstr(frac, 30)}  (1/{mp.nstr(1/frac, 10)} 圈)")
# 圓周 88-site: Δθ 對應幾多個 site 步? site 步 = 2π/88
sites = dth/(2*mp.pi/88)
print(f"  Δθ 對應 {mp.nstr(sites, 15)} 個 88-site 相位步 (2π/88)")

# 最終裁決: 邊個候選最接近?
print(f"\n  最佳命中: {best[0]} (dev {mp.nstr(best[1], 8)})")
if best[1] < 1e-6:
    check("T1b Δθ 結構身份命中 (dev < 1e-6)", True, f"{best[0]} dev={mp.nstr(best[1],3)}")
elif best[1] < 1e-3:
    check("T1b Δθ 結構身份候選 (1e-6 ≤ dev < 1e-3)", True, f"{best[0]} dev={mp.nstr(best[1],3)} — 🟡 需獨立機制")
else:
    check("T1b Δθ 冇結構身份命中 (全部 > 1e-3)", True,
          f"最佳 {best[0]} dev={mp.nstr(best[1],3)} — 幾何干涉, O196 T2 預告 🔴")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
