#!/usr/bin/env python3
"""
O51/80: 有預言性嘅結構推導 — K_Tree 粗粒化方差演化
===============================================================
唔係 fit DESI，而係從 K_Chain 譜嘅「粗粒化不均勻性」推導修正

核心概念: K_Tree 每層將 4 個相鄰模式合併為一個「有效模式」
  如果譜係均勻嘅，所有組嘅能量和相同
  但 K_Chain 譜 γ_n 不均勻 → 組能量有方差

方差 v(ℓ) 隨 ℓ 嘅演化 → 決定 D_app 嘅二階修正
預言性: 呢個方差演化可以獨立驗證 (例如 LSS 嘅 scale-dependent bias)
"""
import json, math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
B = 4  # K_Tree 分支因子

print("=" * 62)
print("K_Tree 粗粒化方差演化 — 有預言性嘅結構推導")
print("=" * 62)

# ============ 1. K_Chain 譜 ============
gamma = [4*math.sin(math.pi*n/88)**2 for n in range(1, N_d+1)]
sum_gamma = sum(gamma)
print(f"Σγ = {sum_gamma:.1f}")

# ============ 2. 粗粒化方差 ============
print("\n--- 各層粗粒化方差 ---")
print(f"{'ℓ':<4} {'組數':<6} {'每組模式數':<14} {'方差v(ℓ)':<12} {'v(ℓ)/v(0)':<12}")
print("-" * 48)

variance_vs_ell = []
for ell in range(0, 5):
    group_size = B**ell
    n_groups = max(1, math.ceil(N_d / group_size))
    
    # 計算每組嘅能量和
    group_sums = []
    for g in range(n_groups):
        start = g * group_size
        end = min(start + group_size, N_d)
        g_sum = sum(gamma[start:end])
        group_sums.append(g_sum)
    
    # 方差
    mean = sum(group_sums) / len(group_sums)
    var = sum((s - mean)**2 for s in group_sums) / len(group_sums)
    variance_vs_ell.append(var)
    
    if ell == 0:
        v0 = var
    rel_var = var / v0 if v0 > 0 else 0
    print(f"{ell:<4} {n_groups:<6} {group_size:<14} {var:<12.4f} {rel_var:<12.4f}")

# ============ 3. 方差演化 ============
print("\n--- 方差隨 ℓ 演化 ---")
print(f"v(0) = {variance_vs_ell[0]:.4f} (原始譜方差)")
for ell in range(1, len(variance_vs_ell)):
    ratio = variance_vs_ell[ell] / v0
    print(f"v({ell})/v(0) = {ratio:.4f}")

# 方差衰減率
print(f"\n方差衰減: v(ℓ) ∝ B^(-{math.log(v0/variance_vs_ell[1])/math.log(B):.4f}ℓ)")
print(f"均勻譜預期: v(ℓ) ∝ B^(-ℓ) (variance decays as 1/group_size)")

# ============ 4. 連續 ℓ 嘅方差 ============
print("\n--- 連續 ℓ 嘅方差插值 (預言性) ---")

# 方差喺連續 ℓ 嘅行為決定咗 D_app 嘅修正
# 用指數衰減近似: v(ℓ) = v(0) × B^(-k·ℓ)
# 其中 k 由 K_Chain 譜嘅「譜指數」決定

# 從 ℓ=0 到 ℓ=1 嘅衰減率
k = math.log(v0 / variance_vs_ell[1]) / math.log(B)
print(f"衰減指數 k = {k:.4f}")
print(f"均勻譜 k = 1.0")
print(f"IDCM K_Chain 譜 k = {k:.4f}")

# 呢個 k 值決定咗 D_app 嘅二階修正:
# delta(ℓ) = (k - 1) × (ℓ - 0.5) × C
# 其中 C 係結構常數

C_structural = (k - 1) * 2 * phi**(-1)
print(f"\n二階修正係數 C = (k-1) × 2φ⁻¹ = ({k-1:.4f}) × {2*phi**(-1):.4f} = {C_structural:.4f}")

# ============ 5. 預言性驗證 ============
print("\n--- 預言性: 方差演化可獨立驗證 ---")
print(f"""
1. K_Tree 粗粒化方差 v(ℓ) 由 K_Chain 譜 γ_n 唯一決定
2. 呢個方差決定 D_app 公式嘅二階修正
3. 方差演化可以獨立驗證:
   - 宇宙大尺度結構嘅「scale-dependent bias」
   - 弱透鏡效應嘅「剪切方差」
   - 星系成團性嘅「counts-in-cells variance」
4. 如果 v(ℓ) 觀測到嘅衰減 k = 1（均勻），則 D_app 唔需要修正
5. 如果 v(ℓ) 觀測到嘅衰減 k = {k:.4f}，則 D_app 二階修正係必然
""")

# 用 DESI 驗證 (唔係 fit, 係 check)
print("\n--- DESI 驗證 (唔係 fit) ---")
desi = [
    (0.510, 13.588, 0.167),
    (0.706, 17.351, 0.177),
    (0.934, 21.576, 0.152),
    (1.321, 27.601, 0.318),
    (2.330, 38.988, 0.531),
]
rd_c = math.pi * R_H / 88 * 420/421

def D_original(ell):
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

def D_predicted(ell):
    """用方差衰減推導嘅修正"""
    k_decay = math.log(v0 / variance_vs_ell[1]) / math.log(B)
    # 修正: D_app × (1 + (k-1)·φ⁻¹·(ℓ-0.5)²)
    # 二次項, 喺 ℓ₀=0.5 穿越零點
    correction = 1 + (k - 1) * phi**(-1) * (ell - 0.5)**2
    return D_original(ell) * correction

print(f"{'z':<6} {'ℓ':<6} {'D_orig':<10} {'D_pred':<10} {'DESI DM/rd':<12} {'orig dev':<10} {'pred dev':<10}")
print("-" * 64)
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d_orig = D_original(ell) / rd_c
    d_pred = D_predicted(ell) / rd_c
    dev_orig = (d_orig - dm) / dm * 100
    dev_pred = (d_pred - dm) / dm * 100
    print(f"{z:<6.3f} {ell:<6.3f} {d_orig:<10.3f} {d_pred:<10.3f} {dm:<12.3f} {dev_orig:>+7.2f}% {dev_pred:>+7.2f}%")

# ============ 6. H_eff(0) 一致性檢查 ============
print("\n--- H_eff(0) 一致性 ---")
KMS = 977.8
def H_eff(D_func, z):
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    c_mpc_gyr = 306.601394
    dD = (D_func(ell_p) - D_func(ell_m)) / (2*dz) if z-dz > 0 else 0
    return c_mpc_gyr / dD * KMS if dD > 0 else 0

H0_orig = H_eff(D_original, 0.001)
H0_pred = H_eff(D_predicted, 0.001)
print(f"H_eff(0.001) 原始: {H0_orig:.4f} km/s/Mpc")
print(f"H_eff(0.001) 預言: {H0_pred:.4f} km/s/Mpc")
check("H_eff(0) 保持不變", abs(H0_pred - H0_orig) < 0.1, f"變化 {H0_pred-H0_orig:+.4f} km/s/Mpc")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print("總結")
print("=" * 62)
print(f"""
核心推導: K_Tree 粗粒化方差 v(ℓ) 嘅演化決定 D_app 修正

方差衰減指數 k = {k:.4f} (均勻譜 k=1.0)
  推導: v(ℓ) = v(0) × B^(-k·ℓ)
  修正: D_app(ℓ) → D_app(ℓ) × (1 + (k-1)·φ⁻¹·(ℓ-0.5)²)

預言性: k 可以獨立測量
  - 從 LSS 嘅「scale-dependent bias」測量 k
  - 從弱透鏡「shear variance」測量 k
  - 如果 k ≈ 1.0 (均勻) → 修正為零, DESI 偏差係系統誤差
  - 如果 k ≈ {k:.4f} (IDCM) → DESI 偏差係結構必然
""")

result = {
    'k_decay': round(k, 4),
    'v0': round(v0, 4),
    'v1': round(variance_vs_ell[1], 4) if len(variance_vs_ell) > 1 else 0,
    'correction_coefficient': round(C_structural, 4),
    'H0_orig': round(H0_orig, 4),
    'H0_pred': round(H0_pred, 4),
    'pass': PASS,
    'fail': FAIL
}

with open('data/80_predictive_derivation.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"-> data/80_predictive_derivation.json")