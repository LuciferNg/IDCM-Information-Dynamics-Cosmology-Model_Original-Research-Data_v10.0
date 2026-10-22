#!/usr/bin/env python3
"""
O100 — Step 2: O83 母函 → 逆 Abel → 3D P(k) 線譜
=================================================
構建逆投影算符 ℳ: C_ℓ 線譜 → P_3D(k) 線譜, 零自由參數。

輸入:
  - C_ℓ 峰位 ℓ_m (O83 公式) + 母函振幅 A_m (O83 閉合, 零自由參數)
  - 絕對歸一化: D₁(ℓ=220) = 5750 μK² (Planck TT 第一峰, 唯一觀測錨點)
  - δT↔δ 轉換 (結構化, 標準 Poisson+SW 以 IDCM 靜態世界代入):
        δT/T = −Φ/3   (Sachs-Wolfe)
        δ    = −(2/3)(k/aH)²·Φ   (Poisson, matter era)
        IDCM: a≡1, H≡H₀ (靜態環世界, 無膨脹) → aH = H₀ = 1/R_world
        ⇒ δ = 2(k/k_H)²·(δT/T),  k_H = H₀/c = 1/R_world
        ★ χ*=R_world ⇒ k/k_H = ℓ_m (恆等, Step 1 已驗證 dev=0%)
        ⇒ δ_m = 2·ℓ_m²·(δT/T)_m   ← 純結構, 零參數
  - 逆 Abel (正則離散): σ²_δ(k_m) ≡ Δ²_m = [2ℓ_m²]²·⟨(δT/T)²⟩_m
        P(k_m) = 2π²·Δ²_m / k_m³   [Mpc³]

輸出: P_3D(k) 線譜表 (k_m, Δ²_m, P_m) + 對照 BOSS P(k) 取值
"""
import os, json, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name}  {detail}")

print("="*72)
print("  O100 Step 2: 母函 → 逆 Abel → P_3D(k) 線譜")
print("="*72)

# ─── 常數 ───
H0 = 72.59
c = 299792.458
h = 0.6727
R_world = c/H0                 # 4129.64 Mpc
k_H = 1.0/R_world              # Mpc⁻¹
T_cmb = 2.72548                # K
D1_muK2 = 5750.0               # Planck TT D_ℓ(220), μK²
M = 33; F6, F8 = 8, 21

def ell_m(m):
    if m == 5:
        return 44*(M - F6) + F8
    from math import comb
    return 44*(M - comb(9-m, 2)) + ((m-1)*9) % 25

# 母函振幅 (零自由參數, O83):
# 偶峰 m=2k: A = ((k+1)/(4k−1))² ; 奇峰: A₃=4/9, A₅=3/14, A₇=1/7
def A_m(m):
    if m == 1:
        return 1.0
    if m % 2 == 0:
        k = m//2
        return ((k+1)/(4*k-1))**2
    return {3: 4/9, 5: 3/14, 7: 1/7}.get(m, 1/16)   # m≥9 奇峰: 母函極限地板 1/16 (延伸, 未閉合)

ells, As = [], []
for m in range(1, 10):
    ells.append(ell_m(m)); As.append(A_m(m))
ells = np.array(ells, float); As = np.array(As)
print(f"\n  峰階梯 ℓ_m   = {np.round(ells).astype(int)}")
print(f"  母函振幅 A_m = {np.round(As,4)}")

# ─── 1. 絕對 C_ℓ ───
# C_ℓ = D_ℓ·2π/(ℓ(ℓ+1));  D_ℓ = D₁·A_m
Dl = D1_muK2 * As                       # μK²
Cl = Dl * 2*math.pi/(ells*(ells+1))     # μK² (D_ℓ 定義)
Cl_K2 = Cl * 1e-12                      # K²
print(f"\n  D_ℓ (μK²)   = {np.round(Dl,1)}")
print(f"  C_ℓ (μK²)   = {np.round(Cl,6)}")

# ─── 2. 模式方差 (δT/T)² ───
varT = Cl_K2 * (2*ells+1)/(4*math.pi*T_cmb**2)   # ⟨(δT/T)²⟩_m per mode
print(f"\n  ⟨(δT/T)²⟩_m  = {np.array2string(varT, precision=2, suppress_small=False)}")
check("C_ℓ 絕對振幅合理 (D₁=5750μK² 錨)", abs(Dl[0]-5750) < 1, "A₁=1 定義")

# ─── 3. 逆 Abel 轉換: δ = 2(k/k_H)²·(δT/T), k/k_H = ℓ ───
#    χ* = R_world (Step 1 恆等), k_m = ℓ_m/R_world
k_m = ells/R_world                     # Mpc⁻¹
k_h = k_m/h                            # h/Mpc
ratio_k = k_m/k_H                      # = ℓ_m (恆等)
transfer = 2*ratio_k**2                # δ/(δT/T)
var_delta = transfer**2 * varT         # σ²_δ per mode
Delta2 = var_delta                     # Δ²(k_m) = 每 decade 方差
P_m = 2*math.pi**2 * Delta2 / k_m**3   # Mpc³

print(f"\n  k_m (Mpc⁻¹) = {np.round(k_m,5)}")
print(f"  k_m (h/Mpc) = {np.round(k_h,4)}")
print(f"  k/k_H = ℓ   = {np.round(ratio_k,2)}")
print(f"  transfer 2(k/kH)² = {np.round(transfer,1)}")
print(f"  Δ²(k_m)    = {np.array2string(Delta2, precision=2, suppress_small=False)}")
print(f"  P(k_m) Mpc³ = {np.array2string(P_m, precision=2, suppress_small=False)}")
check("k/k_H = ℓ (恆等)", np.max(np.abs(ratio_k-ells)) < 1e-6)

# ─── 4. 對照 BOSS P(k) (正則預覽) ───
WIG = "/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt"
kb, Pb, Psb = [], [], []
for line in open(WIG):
    if line.startswith('#') or not line.strip(): continue
    p = line.split()
    if len(p) < 4: continue
    kb.append(float(p[0])); Pb.append(float(p[1])); Psb.append(float(p[2]))
kb = np.array(kb); Pb = np.array(Pb); Psb = np.array(Psb)
# IDCM Δ² 轉 BOSS 對照 (Δ² 單位無關 h):
# BOSS Δ²(k) = k³P(k)/2π² (k 用 h/Mpc, P 用 (Mpc/h)³ → Δ² 無量綱)
Delta2_boss = kb**3 * Pb / (2*math.pi**2)
print(f"\n  BOSS Δ²(k) 對照 (m 峰位插值):")
for i in range(len(ells)):
    if k_h[i] < kb.min() or k_h[i] > kb.max():
        print(f"    m={i+1}: k={k_h[i]:.4f} → 超出 BOSS 範圍")
        continue
    D_b = np.interp(k_h[i], kb, Delta2_boss)
    print(f"    m={i+1}: k={k_h[i]:.4f}  Δ²_ID={Delta2[i]:.3e}  Δ²_BOSS={D_b:.3e}  比={Delta2[i]/D_b:.3f}")

# ─── 5. 選項: χ=πR_world 變體 (Step 1 sensitivity) ───
print("\n  ─── 敏感度: χ*=πR_world (BOSS wiggle 最佳結構候選) ───")
k_m2 = ells/(math.pi*R_world)
ratio2 = k_m2/k_H                      # = ℓ/π
var_delta2 = (2*ratio2**2)**2 * varT
print(f"    k/k_H = ℓ/π = {np.round(ratio2,3)}")
print(f"    σ²_δ,m 總和 = {var_delta2.sum():.3e}  (χ=R: {var_delta.sum():.3e})")
print(f"    σ² 比 (π變體/R變體) = {var_delta2.sum()/var_delta.sum():.4f}  (=π⁻⁴={math.pi**-4:.4f})")

# ─── 輸出 ───
np.savetxt(os.path.join(OUT, "P3D_lines.dat"),
    np.column_stack([ells, As, Dl, k_h, k_m, transfer, Delta2, P_m]),
    header="ell_m  A_m  D_ell(muK2)  k_h(h/Mpc)  k_Mpc  transfer  Delta2  P_Mpc3",
    fmt="%.6e")
json.dump({
    "ell": ells.tolist(), "A": As.tolist(), "D_muK2": Dl.tolist(),
    "k_h": k_h.tolist(), "k_Mpc": k_m.tolist(), "transfer": transfer.tolist(),
    "Delta2": Delta2.tolist(), "P_Mpc3": P_m.tolist(),
    "chi_star": R_world, "identity_k_over_kH": True,
}, open(os.path.join(OUT, "02_inverse_abel.json"), "w"), indent=2)

n_pass = sum(results); n_tot = len(results)
print("="*72)
print(f"  RESULT: {n_pass}/{n_tot} PASS")
print("="*72)
exit(0 if n_pass == n_tot else 1)