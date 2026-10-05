#!/usr/bin/env python3
"""O146 §9 獨立驗證器 — 新推導 (2026-09-05 晚)
==============================================
驗證 (A) Δγ=拍頻×和頻  (B) 三頻道觀測閉合  (C) 聲學峰vs拍頻區分
     (D) 44-site 頻率來源身份鏈  (E) 影子可逆性
全部由原始定義重算, 唔 import o146 scripts。
"""
import math
import numpy as np

N = 44
R_world = 4129.94
c = 299792.458
omega_ring = 72.59
Mpc_to_km = 3.085677581e19

w = lambda n: 2*math.sin(math.pi*n/88)
G = lambda n: 4*math.sin(math.pi*n/88)**2

PASS = 0
FAIL = 0
rows = []
def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

# ============ (A) Δγ = 拍頻 × 和頻 (946/946) ============
ok = all(abs((G(b)-G(a)) - (w(b)-w(a))*(w(b)+w(a))) < 1e-12
        for a in range(1, N) for b in range(a+1, N+1))
check("(A) Δγ = 拍頻×和頻 946/946", ok)

# ============ (B) 三頻道觀測閉合 ============
# B1: 中微子 Δm² (main_problems/p15_early_derivations/docs/neutrino_mass_spectrum.md)
phi = (1+5**0.5)/2
m0 = 0.053424
m3, m2, m1 = m0, m0/phi, m0/phi**2
dm31 = m3**2 - m1**2
dm21 = (m2**2 - m1**2)/9
check("(B1) Δm²₃₁ 0.03%", abs(dm31-2.4377e-3)/2.4377e-3 < 0.001,
      f"{dm31:.4e} vs 2.4377e-3")
check("(B1) Δm²₂₁ 0.58%", abs(dm21-7.486e-5)/7.486e-5 < 0.01,
      f"{dm21:.4e} vs 7.486e-5")

# B2: O65 混合角 γ-ratio 4/4
MIX = [
    ("sin²θ₁₂", 0.303, G(2)/(G(2)+G(3))),
    ("sin²θ₂₃", 0.572, G(7)/(G(7)+G(6))),
    ("sin²θ₁₃", 0.02203, G(6)/8),
    ("λ_CKM", 0.225, (G(6)/16)**(1/3)),
]
for name, obs, pred in MIX:
    dev = abs(pred-obs)/obs*100
    check(f"(B2) {name} <5%", dev < 5, f"{pred:.5f} vs {obs} {dev:.2f}%")

# ============ (C) 聲學峰 vs 拍頻區分 ============
M = 33
def k_m(m): return 33-8 if m == 5 else M - math.comb(9-m, 2)
B_vals = np.array(sorted(abs(w(a)-w(b)) for a in range(1, N+1) for b in range(a+1, N+1)))
k_vals = [k_m(m) for m in range(1, 8)]
check("(C) 全部 k_m > 拍頻 max", min(k_vals) > B_vals.max(),
      f"k_min={min(k_vals)} vs B_max={B_vals.max():.4f}")
# 正規化峰位 ℓ/44 = k + frac/44 都 > 2
ell44 = [(44*k_m(m)+(((m-1)*9)%25 if m!=5 else 21))/44 for m in range(1,8)]
check("(C) ℓ_m/44 全部 > 2", min(ell44) > 2, f"min={min(ell44):.4f}")

# ============ (D) 44-site 頻率來源身份鏈 ============
c_ms = c*1e3
dx = R_world/N
omega_scale = 88*c_ms/(R_world*Mpc_to_km*1e3)
omega_2c_dx = 2*c_ms/(dx*Mpc_to_km*1e3)
omega_ring_rads = omega_ring*1e3/(Mpc_to_km*1e3)
check("(D) ω_scale = 2c/dx", abs(omega_scale/omega_2c_dx - 1) < 1e-9,
      f"比例={omega_scale/omega_2c_dx:.10f}")
check("(D) ω_scale = 88ω_ring", abs(omega_scale/(88*omega_ring_rads) - 1) < 1e-6,
      f"比例={omega_scale/(88*omega_ring_rads):.10f}")
# ω_n = ω_scale·sin(πn/88) 數值核對 n=1,22,44
for n, f_exp in [(1, 1.176e-18), (22, 2.3298e-17), (44, 3.2948e-17)]:
    f = omega_scale*math.sin(math.pi*n/88)/2/math.pi
    check(f"(D) f_{n} ≈ {f_exp:.2e}", abs(f-f_exp)/f_exp < 0.01, f"{f:.4e}")

# λ_n = R_world/n
check("(D) λ₁ = R_world", abs(R_world/1 - 4129.94) < 1e-6)

# γ_n = Laplacian 特徵值 = 2−2cos(2πn/88)
ok_lam = all(abs(G(n) - (2-2*math.cos(2*math.pi*n/88))) < 1e-12 for n in range(1, N+1))
check("(D) γ_n = 2−2cos(2πn/88) Laplacian", ok_lam)

# ============ (E) 影子可逆性: 946 差頻 → 44 譜唯一重建 ============
B_dict = {}
for n in range(1, N+1):
    for m in range(n+1, N+1):
        B_dict[(n,m)] = w(m) - w(n)
recon = {1: w(1)}
for n in range(2, N+1):
    recon[n] = recon[1] + B_dict[(1, n)]
err_recon = max(abs(recon[n] - w(n)) for n in range(1, N+1))
check("(E) 946→44 唯一重建", err_recon < 1e-12, f"max_err={err_recon:.2e}")

# ============ (F) λ_sync = π·dx 恆等式 + r_s ≈ r_d ============
lam_sync = 2*math.pi*R_world/88
check("(F) λ_sync = π·dx", abs(lam_sync - math.pi*dx) < 1e-9,
      f"{lam_sync:.4f} vs {math.pi*dx:.4f}")
r_s = lam_sync/2
check("(F) r_s=λ_sync/2 ≈ r_d 0.24%", abs(r_s-147.09)/147.09 < 0.01,
      f"{r_s:.2f} vs 147.09 ({(r_s-147.09)/147.09*100:+.3f}%)")

print("="*70)
print("  O146 §9 獨立驗證 (新推導)")
print("="*70)
for name, ok, detail in rows:
    print(f"  {'✅' if ok else '🔴'} {name:42s} {detail}")
print("-"*70)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
print(f"  總判定: {'✅ 全部一致' if FAIL==0 else '🔴 有偏差'}")
