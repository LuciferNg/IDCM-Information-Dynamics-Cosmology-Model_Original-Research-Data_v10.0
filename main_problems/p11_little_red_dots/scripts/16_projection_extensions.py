#!/usr/bin/env python3
"""
投影審計延伸 — #17 D_app/N(z) 互補性 + #18 淨因子比值譜 + #16 物質 LH 鏈 (2026-09-09)
====================================================================================
Part A — D_app vs N(z): 兩條高→低律嘅互補關係
   D_app(ℓ)/R_H = (1-4^-ell)(1+2φ^-1·ell)   (O65, 0 params)
   N(z) ∝ 4^-ell                            (投影面積律)
   互補: 44·4^-ell = 未投影世界模, 44(1-4^-ell) = 已投影 → 同一投影兩個面
Part B — 物質/拓撲 HD 淨因子比值譜
   log_φ(1/η) × dβ/dℓ = 21 × 176/42 = 88 = 2N_d (代數: (N_d-μ²)/2 × 4N_d/(N_d-μ²))
   → 凝聚階梯 × 每層陡峭化 = 對偶鏈總譜
Part C — 物質低→高完整鏈 Lbol → M → E_strain + λ_Edd 身份
"""
import math, json
import numpy as np
from astropy.io import ascii

phi = (1+5**0.5)/2
N_d, B, L5, F9 = 44, 4, 11, 34
mu2 = 2.0
OUT = 'data/16_projection_extensions.json'
res = {}

print("="*78)
print("Part A: D_app vs N(z) 互補性 (#17)")
print("="*78)
print(f"{'ell':>5} {'4^-ell (N(z))':>14} {'(1-4^-ell)':>12} {'D_app/R_H':>12} {'和':>12} {'1+2φ^-1·ell·(1-4^-ell)':>24}")
for ell in [0.25, 0.5, 0.68, 1.0, 1.45, 2.0, 2.08]:
    nz = 4**(-ell)
    proj = 1 - 4**(-ell)
    dapp = (1-4**(-ell))*(1+2/phi*ell)
    s = dapp + nz
    rhs = 1 + 2/phi*ell*(1-4**(-ell))
    print(f"{ell:>5.2f} {nz:>14.6f} {proj:>12.6f} {dapp:>12.6f} {s:>12.6f} {rhs:>24.6f}")
print("互補: D_app/R_H + 4^-ell = 1 + 2φ^-1·ell·(1-4^-ell)")
print("  → 距離投影 (1-4^-ell) 同數密度投影 4^-ell 互補, 和 = 1 + 修正項")
print("  → 同一投影操作兩個面: 數密度睇「未投影」, 距離睇「已投影」🟢")
res['partA'] = {'relation': 'D_app/R_H + 4^-ell = 1 + 2/phi·ell·(1-4^-ell)',
                'interpretation': '投影互補: 44·4^-ell 未投影, 44(1-4^-ell) 已投影'}

print("\n" + "="*78)
print("Part B: 物質/拓撲 HD 淨因子比值譜 (#18)")
print("="*78)
log_eta_inv = 21  # log_φ(1/η) = (N_d-μ²)/2
dbdl = 176/42     # dβ/dℓ = 4N_d/(N_d-μ²)
prod = log_eta_inv * dbdl
print(f"log_φ(1/η) × dβ/dℓ = {log_eta_inv} × {dbdl:.6f} = {prod:.6f}")
print(f"  vs 2N_d = 88 → 偏差 {(prod-88)/88*100:.4f}%")
print(f"代數: (N_d-μ²)/2 × 4N_d/(N_d-μ²) = 2N_d = 88 — 精確, 非巧合 🟢🟢")
print(f"→ 凝聚階梯 (21 步) × 每層陡峭化 (176/42) = 對偶鏈總譜 (88)")
print(f"→ 反過嚟: 21 = 88/(176/42) — 凝聚階梯 = 總譜 ÷ 每層陡峭化")
# 其他淨因子組合
print()
C_id, Mhop = 4/11, 7/15
print(f"C × M₄/M₀ 鏈: C = {C_id:.6f} = B/L₅; M₄/M₀ = {Mhop:.6f} = (1-C)/(1+C)")
print(f"  C×(1+M₄/M₀) = {C_id*(1+Mhop):.6f} vs 2B/L₅·L₄... 檢查: (1-Mhop)/(1+Mhop) = {(1-Mhop)/(1+Mhop):.6f} = C ✓")
print(f"  即 M₄/M₀ = (1-C)/(1+C) ⇔ C = (1-M₄/M₀)/(1+M₄/M₀) — 干涉對比同質量比互逆 🟢")
print(f"  再: dβ/dℓ × M₄/M₀ = {dbdl*Mhop:.6f} vs 2N_d/L₅ = {2*N_d/L5:.4f}? ({(dbdl*Mhop)/(2*N_d/L5):.3f}x)")
print(f"  4.1905×0.4667 = 1.9556 ≈ 2 (0.9%) — 候選: dβ/dℓ × M₄/M₀ ≈ 2 = E-O (0.9% 巧合?)")
res['partB'] = {'log_eta_inv': log_eta_inv, 'dbdl': dbdl, 'product': float(prod),
                'identity': '21 × 176/42 = 88 = 2N_d (代數精確)',
                'C': C_id, 'Mhop': Mhop, 'C_from_Mhop': float((1-Mhop)/(1+Mhop)),
                'dbdl_times_Mhop': float(dbdl*Mhop)}

print("\n" + "="*78)
print("Part C: 物質低→高完整鏈 Lbol → M → E_strain (#16)")
print("="*78)
t = ascii.read('data/COSMOS-Web_LRDs.dat', format='ecsv')
Lbol = np.array(t['logLbol_med'], float)
z = np.array(t['z_qso_med'], float)
Lbol_med = np.median(Lbol)
M8 = 6.97e6  # M☉ (COSMOS node-8 median)
L_edd = 1.26e31 * M8  # W
Lbol_W = 10**Lbol_med * 1e-7  # erg/s → W (10^45.94 erg/s)
lam_Edd = Lbol_W / L_edd
print(f"Lbol_med = 10^{Lbol_med:.2f} erg/s = {Lbol_W:.2e} W")
print(f"M(8) = {M8:.2e} M☉ → L_Edd = {L_edd:.2e} W")
print(f"→ λ_Edd = {lam_Edd:.2f} (COSMOS LRDs 中位, 超 Eddington)")
# λ_Edd 結構身份候選
cand = {'L5-1': 10, 'Nd-F9': N_d-F9, '2*F5': 10, 'B+L4-1': 4+7-1}
for k, v in cand.items():
    print(f"  候選 {k} = {v} → 偏差 {abs(lam_Edd-v)/v*100:.1f}%")
# 完整 LH 鏈: Lbol → M → E_strain
eta = phi**(-21)
S8 = 0.047048509643483345; f4 = 1-0.3636
E_strain = M8 / (eta*S8*f4)  # M☉
print(f"\n完整 LH 鏈: Lbol →(÷λ_Edd·L_Edd/M)→ M →(÷η·S·f)→ E_strain")
print(f"  E_strain = M/(η·S·f) = {E_strain:.3e} M☉ vs 1.565e12 (record 04) → ratio {E_strain/1.565e12:.3f}")
print(f"  LH 投影因子: η⁻¹·S⁻¹·f⁻¹ = {1/(eta*S8*f4):.2e} (光度→應變能放大)")
print(f"  λ_Edd ≈ {lam_Edd:.1f} = 10? — 需要更多數據先可以定身份 🟡")
res['partC'] = {'Lbol_med': float(Lbol_med), 'lam_Edd': float(lam_Edd),
                'E_strain_infer': float(E_strain), 'ratio_vs_1565e12': float(E_strain/1.565e12),
                'LH_factor': float(1/(eta*S8*f4))}

json.dump(res, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")
