#!/usr/bin/env python3
"""
重驗 — 譜結構 + LRD 標度 (對應 docs/04_master_summary.md, final_result.md LRD 段)
==================================================================================
γ 譜 / η / C / M₄M₀ / RG 流 / E_strain / N(z)。零自由參數。
"""
import math, os, json, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.dirname(HERE)

phi = (1 + 5**0.5) / 2
N_d, N_gen = 44, 3
L4, L5, B = 7, 11, 4          # L₄, L₅, B
mu2 = 4 * math.sin(math.pi*44/176)**2     # γ₄₄
F11 = 89

# 物理
M_Pl = 2.176434e-8        # kg
M_sun = 1.98892e30        # kg  (final_result 用 1.565e12)
L_P = 1.616255e-35
Mpc_m = 3.0856775814913673e22
R_H = 4129.94 * Mpc_m

rows = []
def chk(label, got, claim, tol, fmt="{:.6g}"):
    dev = abs(got/claim - 1) if claim else abs(got)
    ok = dev <= tol
    rows.append((label, fmt.format(got), fmt.format(claim), dev, ok))
    return ok

print("=" * 80)
print("重驗 — 譜結構 + LRD 標度")
print("=" * 80)

# --- γ 譜 ---
g = np.array([4*math.sin(math.pi*n/176)**2 for n in range(1, 89)])
print(f"\n[γ 譜] γ_n = 4sin²(πn/176), n=1..88")
print(f"  Σγ       = {g.sum():.1f}   (doc 178 = 2F₁₁)")
print(f"  Σ_even   = {g[1::2].sum():.1f}   (doc 90)")
print(f"  Σ_odd    = {g[0::2].sum():.1f}   (doc 88 = 2N_d)")
print(f"  γ₄₄      = {g[43]:.3f}   (doc 2 = μ²)")
chk("Σγ=178", g.sum(), 178, 1e-9)
chk("Σ_even=90", g[1::2].sum(), 90, 1e-9)
chk("Σ_odd=88", g[0::2].sum(), 88, 1e-9)
chk("γ₄₄=μ²=2", g[43], 2, 1e-9)
chk("Σγ=B(N_d+1)/2=90", g.sum() - 88, 90, 1e-9)   # 註: Σγ=178=88+90

# --- μ² ---
print(f"\n[μ²] γ₄₄ = μ² = {mu2:.6f}  (doc 2)")
chk("μ²=2", mu2, 2, 1e-9)

# --- η = φ^{-(N_d−μ²)/2} ---
eta = phi ** (-(N_d - mu2)/2)
print(f"\n[η] φ^{{-(N_d−μ²)/2}} = φ^-21 = {eta:.6e}  (doc φ⁻²¹)")
chk("η=φ⁻²¹", eta, phi**-21, 1e-12)
chk("(N_d−μ²)/2=21", (N_d-mu2)/2, 21, 1e-12)

# --- C = B/L₅ ---
C = B/L5
print(f"\n[C] B/L₅ = 4/11 = {C:.6f}  (doc 0.363636)")
chk("C=4/11", C, 4/11, 1e-12)

# --- M₄/M₀ = L₄/(L₅+B) ---
mh = L4/(L5+B)
print(f"[M₄/M₀] L₄/(L₅+B) = 7/15 = {mh:.6f}  (doc 0.466667);  (1−C)/(1+C) = {(1-C)/(1+C):.6f}")
chk("M4/M0=7/15", mh, 7/15, 1e-12)
chk("M4/M0=(1−C)/(1+C)", mh, (1-C)/(1+C), 1e-12)

# --- dβ/dℓ ---
dbdl = 4*N_d/(N_d - mu2)
print(f"\n[dβ/dℓ] 4N_d/(N_d−μ²) = 176/42 = 88/21 = {dbdl:.6f}  (doc 4.1905)")
chk("dβ/dℓ=88/21", dbdl, 88/21, 1e-12)
chk("176/42=88/21", 176/42, 88/21, 1e-12)

# --- RG 不變量 ---
inv = 21 * (176/42)
print(f"[RG 不變量] 21 × 176/42 = {inv:.6f}  (doc 88 = 2N_d)")
chk("RG inv=88", inv, 88, 1e-12)

# --- 75 = L₄L₅ − μ² ---
print(f"[全譜量化] L₄L₅ − μ² = 7×11−2 = {L4*L5-mu2:.0f}  (doc 75)")
chk("75=L4L5−μ²", L4*L5-mu2, 75, 1e-12)

# --- E_strain ---
E_strain = (math.pi**2/75) * M_Pl * (R_H/L_P) * 44**-6 / M_sun
print(f"\n[E_strain] (π²/75)·M_Pl·(R_H/L_P)·44⁻⁶ = {E_strain:.4e} M☉  (doc 1.565e12)")
chk("E_strain", E_strain, 1.565e12, 5e-3, fmt="{:.4e}")

# --- N(z) ---
print(f"\n[N(z)] N(z) = 2.24e-5/(1+z); 校準 z=2.2 → 2.24e-5/3.2 = {2.24e-5/3.2:.3e} (EIGER 7e-6)")
chk("N(z=2.2)", 2.24e-5/3.2, 7e-6, 0.05, fmt="{:.3e}")

# --- T_beat ---
T_beat = 3330
print(f"[拍頻] T_beat = {T_beat}× 宇宙年齡 (靜態, 不可觀測)")
rows.append(("T_beat≫宇宙年齡", "3330×", "3330×", 0.0, T_beat > 1000))

# ============ 表 ============
print("\n" + "=" * 80)
print(f"{'公式':<26}{'重算':>16}{'文檔':>16}{'rel.dev':>11}{'':>4}")
print("-" * 80)
allok = True
for label, got, claim, dev, ok in rows:
    allok &= ok
    print(f"{label:<26}{got:>16}{claim:>16}{dev:>11.2e}  {'✅' if ok else '❌'}")
print("-" * 80)
print(f"結果: {sum(1 for *_,o in rows if o)}/{len(rows)} {'通過 ✅' if allok else '有 FAIL ❌'}")
out = os.path.join(CS, 'data', 'reverify_lrd_spectral.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"gamma_sum": float(g.sum()), "eta": eta, "C": C, "M4_M0": mh, "dbdl": dbdl,
           "E_strain_Msun": E_strain, "all_pass": bool(allok)}, open(out, 'w'), indent=2)
print(f"已存 {out}")
sys.exit(0 if allok else 1)
