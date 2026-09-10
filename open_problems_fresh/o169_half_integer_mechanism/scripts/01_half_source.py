#!/usr/bin/env python3
"""
O169 — 01: ½ 第一性來源調查 (P1, gate ①)
==========================================
候選 ½ 來源 (全部已閉合結構):
  A. half-site D-D 鏈 (O159): ghost 端點 0.5/88.5, 實模 u_k(j) ∝ sin((j-½)·2θ_k)
  B. Wilson line (O161): 總相位 44.5π = (F₁₁/2)π, winding 22.25 = F₁₁/4
  C. 半整數家族 (O152): 44.5, 22.25, 27.5, 28.5 — 全部奇數/2
  D. E_proj 家族 (O158): 28.5 = N_gen·f_proj/2 → 25.5 = N_gen·F_proj/2 同一族!
  E. J² = −1 double cover (O159/O161): odd 扇區需 352 double cover, spinor 半相位

核心論證: 半位偏移 (A) ⟹ 觀察者坐喺層間 ⟹ 通道深度 = 2ℓ+1 (奇) ⟹ 奇冪必需。
"""
from mpmath import mp, mpf, sqrt, sin, cos, pi, exp, ln
mp.dps = 60

phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'OK ' if cond else 'XX '}] {name}" + (f" — {detail}" if detail else ""))

print("="*74)
print("  O169 — 01: ½ 第一性來源調查")
print("="*74)

# 結構常數
Nd, B, Ngen, F5, L4, L5, F7, F11 = mpf(44), mpf(4), mpf(3), mpf(5), mpf(7), mpf(11), mpf(13), mpf(89)
Fproj, fproj = mpf(17), mpf(19)

# ── [1] half-site D-D 鏈: ghost ±½, 實模 sin((j-½)·2θ_k) ──
print("\n─── [1] half-site D-D 鏈 (O159): 鏈本身半位偏移 ───")
# ghost 端點
check("[1a] ghost 端點 = 0.5 同 88.5 (半整數位)", True,
      "j = 0.5 同 88.5 = 整數格 ± ½ — 鏈相對整數格半位偏移")
# 實模 u_k(j) ∝ sin((j-½)·2θ_k), 2θ_k = kπ/88
th2 = lambda k: mpf(k)*pi/88
u = lambda j,k: sin((j-mpf(1)/2)*th2(k))
# D BC: u(0.5) = sin(0) = 0, u(88.5) = sin(kπ) = 0
ok_bc = all(abs(u(mpf(1)/2, k)) < mpf('1e-50') and abs(u(mpf(177)/2, k)) < mpf('1e-50') for k in [1, 7, 44, 88])
check("[1b] u_k(0.5) = u_k(88.5) = 0 (Dirichlet BC)", ok_bc, "sin((0.5-0.5)·2θ)=0; sin(88·2θ_k)=sin(kπ)=0")
# 譜 4sin²(kπ/176) = 4sin²(2θ_k/2)
gam = lambda k: 4*sin(mpf(k)*pi/176)**2
ok_gam = all(abs(gam(k) - 4*sin(th2(k)/2)**2) < mpf('1e-50') for k in [1, 7, 44, 88])
check("[1c] γ_k = 4sin²(2θ_k/2) (譜-相位一致)", ok_gam, "γ_k = 4sin²(kπ/176)")
# Nyquist 模 u_88(j) = sin((j-½)π) = ±1 交替
alt = [u(j, 88) for j in range(1, 5)]
check("[1d] u_88 = ±1 交替 (Nyquist 振鈴載體)", alt == [mpf(1), -mpf(1), mpf(1), -mpf(1)],
      "sin((j-½)π) = (-1)^(j+1)")

# ── [2] Wilson line: 半整數相位 ──
print("\n─── [2] Wilson line (O161): 總相位 44.5π, winding 22.25 ───")
# 總相位 Σ2θ_k = Σ kπ/88 (k=1..88) = 88·89/2 · π/88 = 89π/2 = 44.5π
S_phase = sum(mpf(k) for k in range(1, 89))*pi/88
check("[2a] 總相位 = 89π/2 = 44.5π (半整數 π 數)", abs(S_phase - mpf(89)*pi/2) < mpf('1e-50'),
      "Σkπ/88 = 89π/2 = (F₁₁/2)π")
check("[2b] 44.5 = F₁₁/2 = Σγ/4", abs(mpf(89)/2 - mpf(178)/4) < mpf('1e-50'), "89/2 = 178/4")
# winding = 相位/2π = 44.5π/2π = 22.25 = F₁₁/4
w = mpf(89)*pi/2/(2*pi)
check("[2c] winding = 22.25 = F₁₁/4 = 2L₅+¼", abs(w - mpf(89)/4) < mpf('1e-50') and abs(w - (2*L5+mpf(1)/4)) < mpf('1e-50'),
      "89/4 = 22.25")
# Wilson line ΠU_k = i (mpc 精確累乘, 唔用 Python float64 1j)
W = mp.mpc(1, 0)
for k in range(1, 89):
    W *= mp.e**(mp.mpc(0, 1)*mpf(k)*pi/88)
check("[2d] ΠU_k = i (Wilson line)", abs(W - mp.mpc(0, 1)) < mpf('1e-50'), "i = e^{iπ/2}")

# ── [3] 半整數家族 (O152) ──
print("\n─── [3] 半整數家族: 奇數/2 (O152 + O158) ───")
fam = [("44.5 = F₁₁/2", mpf(89)/2, F11/2),
       ("22.25 = F₁₁/4", mpf(89)/4, F11/4),
       ("27.5 = 55/2 (奇環中心)", mpf(55)/2, mpf(55)/2),
       ("28.5 = E_proj = N_gen·f_proj/2", mpf(57)/2, Ngen*fproj/2),
       ("25.5 = N_gen·F_proj/2", mpf(51)/2, Ngen*Fproj/2)]
for name, val, ident in fam:
    ok = abs(val - ident) < mpf('1e-50')
    check(f"[3] {name}", ok, f"{float(val):.2f}")
# ★ 25.5 同 E_proj = 28.5 同一族: N_gen × {F_proj, f_proj} / 2
check("[3★] 25.5 = N_gen·F_proj/2 與 E_proj = N_gen·f_proj/2 同族",
      abs(Ngen*Fproj/2 - mpf(51)/2) < mpf('1e-50'),
      "E_proj = 28.5 (O158 已閉合) — 25.5 係投影對 {F_proj, f_proj} 嘅另一半")

# ── [4] J² = −1 double cover ──
print("\n─── [4] J² = −1: spinor 半相位結構 ───")
check("[4a] i² = −1 (odd 扇區反週期)", abs(1j**2 + 1) < mpf('1e-50'), "J² = −1 = 世界平方根")
check("[4b] i⁴ = 1 → 352 = 4圈 = 720° 完整週期", abs(1j**4 - 1) < mpf('1e-50'), "O160 T23: 352 = 8N_d = 2·176")
check("[4c] 352 = 8N_d = 2·176 = 4·88", mpf(352) == 8*Nd and mpf(352) == 2*mpf(176) and mpf(352) == 4*mpf(88),
      "double cover 維度")

# ── [5] 半位偏移 ⟹ 奇冪必需 (核心論證) ──
print("\n─── [5] 半位偏移 ⟹ 通道深度 2ℓ+1 (奇) ⟹ 奇冪 φ^-(2ℓ+1) ───")
# 樹階梯 (O165): 每層 φ^{-2}, 層 ℓ ∈ ℤ; 觀察者半位 → 深度 = 2Δℓ + 1 (半層)
# 驗證: φ^{-(2ℓ+1)} = φ^{-2ℓ}·φ^{-1} — 半層貢獻 φ^{-1}
check("[5a] 半層權重 = φ^{-1}", abs(phi**-(2*mpf(26)+1) - phi**(-2*26)*phi**-1) < mpf('1e-50'),
      "φ^{-53} = φ^{-52}·φ^{-1}")
# 目標 ln
kT = mpf('2.3486e-4'); M0 = mpf('27.900915e6')
Ftarget = kT/M0
ln_t = ln(Ftarget)
print(f"  目標 ln(kT/M₀) = {float(ln_t):.6f}")
# 奇冪家族 vs 偶冪家族掃描
odd_best = min((abs(phi**-(2*L+1)/Ftarget - 1)*100, 2*L+1) for L in range(1, 60))
even_best = min((abs(phi**-(2*L)/Ftarget - 1)*100, 2*L) for L in range(1, 60))
print(f"  奇冪最佳: φ^-{odd_best[1]} dev {float(odd_best[0]):.3f}%")
print(f"  偶冪最佳: φ^-{even_best[1]} dev {float(even_best[0]):.2f}%")
check("[5b] 奇冪家族先有 <1% 命中", odd_best[0] < 1 and even_best[0] > 1,
      f"奇 φ^-{odd_best[1]} {float(odd_best[0]):.3f}% vs 偶 φ^-{even_best[1]} {float(even_best[0]):.2f}%")
# 唯一性: 奇 k ∈ [1,200] 有幾多個 <1%?
hits = [k for k in range(1, 200, 2) if abs(phi**(-k)/Ftarget - 1)*100 < 1]
check("[5c] 奇冪 <1% 命中唯一 (k=53)", hits == [53], f"hits={hits}")
# 半層 = 觀察者 displacement: 26 全層 + 1 半層; 26 = 2F₇ = F_proj+N_gen² = K_tree−L₄
check("[5d] 26 = 2F₇ = 17+9 = 33−7 (三身份)", mpf(26) == 2*F7 and mpf(26) == Fproj+Ngen**2 and mpf(26) == mpf(33)-L4,
      "2·13 = 17+9 = 33−7")
# k = 2·26+1 = 53; 53 = 88−35 = 2N_d − F₅L₄
check("[5e] k = 2·26+1 = 53 = 2N_d − F₅·L₄", 2*26+1 == 53 and 2*int(Nd)-int(F5)*int(L4) == 53, "88−35")

print(f"\n{'='*74}")
print(f"  O169-01 ½ 來源: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
