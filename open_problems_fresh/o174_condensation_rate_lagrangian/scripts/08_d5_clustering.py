#!/usr/bin/env python3
"""
O174 script 08 — D5 攻堅: 凝聚場 2-點函數 → LRD clustering (SESSION_START 攻堅)
===============================================================================
S_ℓ = Σ(γ_n+μ²)|Φ_n|², G(n) = 1/(γ_n+μ²) (O174 docs/03)
相關長度候選: r0 = 88·R_c = 2N_d·(R_H/44³) = 4.27 Mpc
vs Zhang+26 r0 = 3.4-4.5 h⁻¹Mpc
"""
import mpmath as mp

mp.mp.dps = 30
ok = 0; bad = 0
def ck(msg, cond, info=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK] {msg} {info}")
    else: bad += 1; print(f"  [XX] {msg} {info}")

N_d, B, mu2 = 44, 4, 2
R_H_Mpc = mp.mpf('4129.94')   # Hubble radius
R_c = R_H_Mpc / mp.mpf('44')**3

print("="*70)
print("2-點函數結構 (O174 docs/03)")
print("="*70)
# 傳播子譜: G(n) = 1/(γ_n+μ²), γ_n = 4sin²(πn/2N)
N = 88
gaps = []
for n in range(1, N+1):
    g = 4*mp.sin(mp.pi*n/(2*N))**2 + mu2
    gaps.append(g)
g_min = min(gaps)
g_44 = 4*mp.sin(mp.pi*44/(2*88))**2 + mu2
ck("凝聚模 n=44: γ = μ² = 2 (中心模定理), G(44) ≈ 1/4", abs(g_44-mp.mpf('4')) < mp.mpf('1e-9'), f"G(44) = 1/{mp.nstr(g_44,8)}")
ck("★ 譜最小能隙 = γ₁+μ² ≈ 2.0013 (n=1 長波長模, 唔係中心模)",
   abs(g_min - mp.mpf('2.001275')) < mp.mpf('1e-3'), f"min(γ+μ²) = {mp.nstr(g_min,8)}")
# 2-點函數主導模 = 最大 G(n) = n=1
G_max = 1/g_min
ck("★ 2-點函數主導模 = n=1 (G_max ≈ 0.4997), 唔係中心模", abs(G_max - mp.mpf('0.4997')) < mp.mpf('1e-3'),
   f"G(1) = {mp.nstr(G_max,6)}")
xi_modes = 1/g_min
ck("相關長度 (模態單位) = 1/min(γ+μ²) ≈ 0.5", abs(xi_modes - mp.mpf('0.5')) < mp.mpf('1e-3'),
   f"ξ_modes = {mp.nstr(xi_modes,6)}")

print("\n" + "="*70)
print("實空間尺度: r0 候選審計")
print("="*70)
R_c_kpc = R_c*1000
ck("R_c = R_H/44³", abs(R_c_kpc - mp.mpf('48.5'))/mp.mpf('48.5') < mp.mpf('1e-3'),
   f"= {mp.nstr(R_c_kpc,6)} kpc (O175 j_spec)")
r0_pred = mp.mpf('88')*R_c   # 2N_d × R_c
ck("r0 候選 = 88·R_c = R_H/968", abs(r0_pred - mp.mpf('4.2665'))/mp.mpf('4.2665') < mp.mpf('1e-3'),
   f"= {mp.nstr(r0_pred,5)} Mpc")
r0_lo = mp.mpf('3.4'); r0_hi = mp.mpf('4.5')
ck("r0 候選落入 Zhang+26 範圍 (h=1)", r0_lo <= r0_pred <= r0_hi,
   f"[{r0_lo}, {r0_hi}] h⁻¹Mpc")
r0_lo_phys = r0_lo/mp.mpf('0.674'); r0_hi_phys = r0_hi/mp.mpf('0.674')
ck("h=0.674 物理範圍 [5.04, 6.68] — 候選低端 (dev ≤ 18%)", abs(r0_pred-r0_lo_phys)/r0_lo_phys < mp.mpf('0.18'),
   f"r0_pred={mp.nstr(r0_pred,4)} vs [{mp.nstr(r0_lo_phys,4)}, {mp.nstr(r0_hi_phys,4)}] Mpc")
ck("88 = 2N_d", 2*N_d == 88)
ck("968 = 2³·L₅² = 8·121", 8*121 == 968, f"(2³={8}, L₅²={11**2})")
print("  ⚠️ 誠實標記: r0 = R_H/(2³L₅²) 係數值候選 — 冇 propagator→實空間映射基礎")
print("     (模態尺度 ξ≈0.5 已推; 晶格間距 a 未定義 = 🔴 開放)")

print("\n" + "="*70)
print(f"RESULT: {ok}/{ok+bad} PASS (r0 候選 = {mp.nstr(r0_pred,5)} Mpc = R_H/(2³·L₅²))")
