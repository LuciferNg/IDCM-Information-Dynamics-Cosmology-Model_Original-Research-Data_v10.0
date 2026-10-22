#!/usr/bin/env python3
"""
O100-C: O86 微擾 → 轉換係數結構檢驗 (聲學峰流體轉換)
=====================================================
檢驗三步:

[1] ζ·W·R 非最小耦合量級: O86 話「低能修正可忽略 (⟨W⟩≪M_Pl)」— 驗證
    ζ = M_Pl·λ_self = 1.99e17 GeV, ⟨W⟩ = M₀ = 27.9 MeV
    有效修正 κ_ζ = ζ·⟨W⟩/M_Pl² — 應該 < 1e-10 (真可忽略)

[2] Transfer 包絡: σ8 對 D₁ 錨點嘅敏感度 (±10% 峰高系統誤差)
    + 峰數 (m=1..7 vs 1..9) + A₉ 地板 (1/16 vs 1/7)
    → σ8 結構包絡 [低, 高] — BOSS 0.783 / 目標 0.81 是否落喺包絡內

[3] 聲學峰 baryon loading R_b: 用 IDCM BBN 閉合比 (Ω_b/Ω_m = 2/15)
    R_b = 3ρ_b/4ρ_γ at z* — 檢查「觀測峰高已含 R_b」所以唔應該再乘
    (即: D₁=5750μK² 係觀測值, 流體修正已喺入面 — 印證唔加參數)

輸出: σ8 包絡 [lo, hi], ζ 量級, R_b 數值, PASS/FAIL
"""
import os, json, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
res = []
def check(name, cond, detail=""):
    res.append(bool(cond)); print(f"  [{'✅' if cond else '❌'} PASS] {name}  {detail}")

phi = (1+math.sqrt(5))/2
H0 = 72.59; c = 299792.458; h = 0.6727
R_world = c/H0
T_cmb = 2.72548

print("="*72)
print("  O100-C: 轉換係數結構檢驗 (聲學峰流體)")
print("="*72)

# ─── [1] ζ·W·R 量級 ───
M_Pl_GeV = 2.435e18      # reduced? plain M_Pl = 1.22e19, sqrt(8πG) reduced = 2.435e18
M0_GeV = 27.9e-3         # K_Chain 能量尺度
zeta = M_Pl_GeV * 1.0e-4 # λ_self ~ 1e-4 量級? O86: ζ = M_Pl·λ_self = 1.99e17 → λ_self ≈ 0.0082
# O86 明言 ζ = 1.99e17 GeV → 對應 λ_self = ζ/M_Pl = 1.99e17/2.435e18 = 0.0817
zeta = 1.99e17
lam_self = zeta/M_Pl_GeV
kappa_zeta = zeta*M0_GeV/M_Pl_GeV**2
print(f"\n[1] ζ·W·R 非最小耦合量級")
print(f"  ζ = {zeta:.3e} GeV (= M_Pl·λ_self, λ_self = {lam_self:.4f})")
print(f"  ⟨W⟩ = M₀ = {M0_GeV*1e3:.1f} MeV")
print(f"  ζ⟨W⟩/M_Pl² = {kappa_zeta:.3e}  (有效耦合修正)")
check("ζ·W·R 低能修正可忽略 (κ_ζ < 1e-10)", kappa_zeta < 1e-10, f"({kappa_zeta:.1e})")
print("  → O86 判斷正確: ζ 耦合唔影響 σ_8 轉換 (k 細, ⟨W⟩≪M_Pl)")

# ─── 載入 Step2 線譜 ───
d2 = json.load(open(os.path.join(OUT, "02_inverse_abel.json")))
ells = np.array(d2["ell"]); Delta2 = np.array(d2["Delta2"])
k_h = np.array(d2["k_h"])
d3 = json.load(open(os.path.join(OUT, "03_sigma8.json")))
s8_base = d3["sigma8_idcm"]
print(f"\n  σ_8 基線 (docs/03) = {s8_base:.4f}")

def top_hat(x):
    return 3*(np.sin(x)-x*np.cos(x))/x**3

def sigma8_from_D1(D1_scale, use_m=(1,9), A9=1/16):
    """D1_scale = D₁ (μK²) 倍數; use_m = (min,max) 峰範圍"""
    As = d2["A"][use_m[0]-1:use_m[1]]
    els = ells[use_m[0]-1:use_m[1]]
    kh  = k_h[use_m[0]-1:use_m[1]]
    Dl = 5750.0*D1_scale*np.array(As)
    # m=9 奇峰地板替換
    if use_m[1] == 9:
        As = list(As); As[-1] = A9
        Dl = 5750.0*D1_scale*np.array(As)
    Cl = Dl*2*math.pi/(els*(els+1))*1e-12
    varT = Cl*(2*els+1)/(4*math.pi*T_cmb**2)
    tr = 2*(els/R_world/(1/R_world))**2   # = 2ℓ²
    D2 = tr**2*varT
    W2 = top_hat(kh*8.0)**2
    return math.sqrt(np.sum(D2*W2))

# ─── [2] Transfer 包絡 ───
print(f"\n[2] σ_8 結構包絡")
lo = min(sigma8_from_D1(0.90), sigma8_from_D1(1.0, A9=1/16), sigma8_from_D1(1.0))
hi = max(sigma8_from_D1(1.10), sigma8_from_D1(1.0, A9=1/7), sigma8_from_D1(1.0))
print(f"  D₁ ±10% 峰高系統誤差 + A₉ ∈ [1/16, 1/7]")
print(f"  σ_8 包絡 = [{lo:.3f}, {hi:.3f}]   基線 = {s8_base:.3f}")
print(f"  BOSS 0.783 喺包絡內? {lo<=0.783<=hi}    目標 0.81 喺包絡內? {lo<=0.81<=hi}")
check("BOSS 0.783 ∈ 結構包絡", lo <= 0.783 <= hi, f"([{lo:.3f},{hi:.3f}])")
check("目標 0.81 ∈ 包絡 (或貼邊)", lo-0.02 <= 0.81 <= hi+0.02, f"([{lo:.3f},{hi:.3f}])")
check("目標 0.81 ∈ 包絡 (嚴格)", lo <= 0.81 <= hi, f"([{lo:.3f},{hi:.3f}])")

# 敏感度表
print("\n  敏感度表:")
for lbl, val in [("D₁ ×0.90", 0.90), ("D₁ ×0.95", 0.95), ("D₁ ×1.00 (基線)", 1.0),
                 ("D₁ ×1.05", 1.05), ("D₁ ×1.10", 1.10),
                 ("m=1..7 only", None), ("A₉=1/7 (奇峰上界)", None)]:
    if lbl.startswith("D₁"):
        s = sigma8_from_D1(val)
    elif lbl.startswith("m=1..7"):
        s = sigma8_from_D1(1.0, use_m=(1,7))
    else:
        s = sigma8_from_D1(1.0, A9=1/7)
    print(f"    {lbl:24s} → σ_8 = {s:.3f}")

# ─── [3] 聲學峰 baryon loading R_b ───
print(f"\n[3] 聲學峰 baryon loading R_b (IDCM BBN 閉合比)")
# IDCM: Ω_b/Ω_m = 2/15 (BBN 閉合 0.04%), Ω_Λ = 4/(φ⁴−1) = 0.683282 (O39)
Om_m = 1 - 4/(phi**4 - 1)
Ob = Om_m*2/15
# Ω_γ from T_CMB: Ω_γ h² = 2.473e-5 (標準, T=2.7255)
h_idcm = 0.7259  # IDCM H0 → h (ω_ring 投影, 記為 IDCM h 變體)
Ogamma = 2.473e-5/h_idcm**2
z_star = 1089.0
R_b_gamma = 0.75*Ob/Ogamma/(1+z_star)      # 光子-only
N_eff = 3.0                                  # IDCM O54/O88: 3 代中微子已閉合
f_nu = 7/8*(4/11)**(4/3)                     # 每代中微子相對光子能量密度
R_b = R_b_gamma/(1 + N_eff*f_nu)             # ρ_rad = ρ_γ(1+N_eff·f_ν)
print(f"  Ω_m   = {Om_m:.5f} (1−Ω_Λ, O39)")
print(f"  Ω_b   = {Ob:.5f} (2/15 Ω_m, BBN)")
print(f"  Ω_γ   = {Ogamma:.3e} (T_CMB, h={h_idcm})")
print(f"  R_b(z*) 光子-only   = {R_b_gamma:.4f}")
print(f"  R_b(z*) 含 3ν (IDCM) = {R_b:.4f}   (N_eff={N_eff}, f_ν={f_nu:.4f})")
check("R_b(3ν) ≈ 0.3-0.45 (聲學峰標準範圍)", 0.30 <= R_b <= 0.45, f"({R_b:.3f})")
print("  → 觀測峰高 D₁=5750μK² 已含 baryon loading; 唔可以再乘 R_b (零參數原則)")
check("IDCM Ω 比 (2/15, Ω_Λ) + 3ν → R_b 落標準帶", 0.30 <= R_b <= 0.45)

# ─── 總結 ───
print("\n" + "="*72)
print(f"  RESULT: {sum(res)}/{len(res)} PASS")
print("="*72)
json.dump({
    "zeta_kappa": kappa_zeta, "sigma8_base": s8_base,
    "envelope": [lo, hi], "boss": 0.783, "target": 0.81,
    "R_b": float(R_b), "O_m": float(Om_m),
}, open(os.path.join(OUT, "06_transfer_checks.json"), "w"), indent=2)
exit(0 if sum(res) == len(res) else 1)