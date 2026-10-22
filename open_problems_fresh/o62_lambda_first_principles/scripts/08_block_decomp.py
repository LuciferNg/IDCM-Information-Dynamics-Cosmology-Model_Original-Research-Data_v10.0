#!/usr/bin/env python3
"""
O62 三期 08: F(γ) block 分解 + 閉合形式
==========================================
目標: F(γ) = 264.0821 有冇精確代數形式?
  κ_ijk 有 3×12 block 結構 (O61):
    完全對角 (g1=g2=g3): 432 非零, mean 12.99
    兩維對角 (g1=g2≠g3): 807 非零, mean 2.10
    完全混合 (g1≠g2≠g3): 102 非零

  F(t) = (1/6)Σκ_ijk t_i t_j t_k
       = (1/6)[Σ_diag κ_iii t_i³ + 3Σ κ_iij t_i²t_j + 6Σ κ_ijk t_i t_j t_k]

分解:
  1. F_diag (完全對角)
  2. F_2idx (兩維對角)
  3. F_mix (完全混合)
  4. 每個 block 組合 (0/1/2 代)
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 三期 08: F(γ) block 分解")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 ============
print("\n[1] 載入")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2

def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

Fg = F(gamma36)
print(f"  F(γ) = {Fg:.10f}")

# ============ 2. 分類 κ 項 ============
print("\n[2] κ 項分類 (3×12 block)")
gidx = np.arange(36) // 12  # 0,1,2
F_diag = 0.0  # 完全對角 (i=j=k)
F_2idx = 0.0  # 兩維對角 (兩個相同)
F_mix = 0.0   # 完全混合
F_block = np.zeros((3, 3, 3))  # block 組合
for i in range(36):
    for j in range(36):
        for k in range(36):
            kk = kappa[i, j, k]
            if kk == 0:
                continue
            term = kk * gamma36[i] * gamma36[j] * gamma36[k] / 6.0
            gi, gj, gk = gidx[i], gidx[j], gidx[k]
            F_block[gi, gj, gk] += term
            if i == j == k:
                F_diag += term
            elif i == j or j == k or i == k:
                F_2idx += term
            else:
                F_mix += term

print(f"  F_diag (完全對角) = {F_diag:.8f}")
print(f"  F_2idx (兩維對角) = {F_2idx:.8f}")
print(f"  F_mix  (完全混合) = {F_mix:.8f}")
print(f"  總和 = {F_diag+F_2idx+F_mix:.8f}")
check("分解總和 = F(γ)", abs(F_diag+F_2idx+F_mix - Fg) < 1e-8)

print(f"\n  Block 分解 (3×3×3):")
print(f"  {'block':12s} {'F 貢獻':>14s}")
for gi in range(3):
    for gj in range(3):
        for gk in range(3):
            if abs(F_block[gi,gj,gk]) > 1e-6:
                print(f"  ({gi},{gj},{gk})     {F_block[gi,gj,gk]:14.6f}")

# ============ 3. 對角 block 分析 ============
print("\n[3] 對角 block (g,g,g)")
F_ggg = sum(F_block[g,g,g] for g in range(3))
print(f"  F(0,0,0)+F(1,1,1)+F(2,2,2) = {F_ggg:.8f}")
for g in range(3):
    print(f"  F({g},{g},{g}) = {F_block[g,g,g]:.8f}")
print(f"  3×44 = {3*44}, 264/3 = {264/3}")

# 每代 block 內 moduli 數 = 12
# γ_{12g+1}..γ_{12g+12}
print(f"\n  每代 γ 和:")
for g in range(3):
    sg = gamma36[12*g:12*g+12].sum()
    print(f"    gen {g}: Σγ = {sg:.6f}")

# ============ 4. F(γ) 閉合形式嘗試 ============
print("\n[4] F(γ) 閉合形式")
print(f"  F(γ) = {Fg:.10f}")
print(f"  264 = 6N_d = 88×3 = 2N_d×N_gen")
print(f"  F(γ) − 264 = {Fg-264:.10f}")

# 高精度: 剩餘 0.0821292326 有冇閉合形式?
rem = Fg - 264
print(f"\n  剩餘 rem = {rem:.12f}")
print(f"  γ_4 = {4*math.sin(4*math.pi/88)**2:.12f}")
print(f"  γ_4/1 = {rem/ (4*math.sin(4*math.pi/88)**2):.8f}")
print(f"  γ_29/36 = {4*math.sin(29*math.pi/88)**2/36:.12f}")
print(f"  rem/(γ_29/36) = {rem/(4*math.sin(29*math.pi/88)**2/36):.8f}")
print(f"  1/12.176 = {1/12.176:.8f}")
print(f"  γ_1×16.114 = {4*math.sin(math.pi/88)**2*16.114:.8f}")

# 更精確: rem 係咪 = γ_29/36 - γ_1/125?
print(f"\n  組合:")
combos = [
    ("γ_29/36", 4*math.sin(29*math.pi/88)**2/36),
    ("γ_4", 4*math.sin(4*math.pi/88)**2),
    ("γ_1×16", 4*math.sin(math.pi/88)**2*16),
    ("γ_6²×2.5", (4*math.sin(6*math.pi/88)**2)**2*2.5),
    ("(γ_1+γ_2)/10", (4*math.sin(math.pi/88)**2+4*math.sin(2*math.pi/88)**2)/10),
]
for name, val in combos:
    err = abs(val - rem)/rem*100
    print(f"  {name:16s} = {val:.10f} (誤差 {err:.4f}%)")

# ============ 5. 檢查 264 = 6N_d 嘅「來源」============
print("\n[5] 264 = 6N_d 來源分析")
# 如果 F(γ) = 6N_d + rem, 6N_d = 6×44
# 44 = N_d, 6 = ? 
# 6 = 2×3 = 2N_gen
# 6 = B + 2 = 4+2
# 6 = L₄ − 1 = 7−1
# 6 = F₅ + 1 = 5+1
# 264 = 4×66 = B × 66 態
# 264 = 88×3 = 2N_d × N_gen
print(f"  264 = 6N_d = 6×44")
print(f"  264 = 88×3 = 2N_d×N_gen (dual chain × generation!)")
print(f"  264 = 4×66 = B×66態")
print(f"  264 = 2×132 = 2×(L₁₀+9)")
print(f"  264 = 3×88 = 3×2N_d")

# 邊個最「第一性」?
print(f"\n  ★ 264 = 88×3: 88 = 2N_d (對偶鏈), 3 = N_gen")
print(f"  ★ 264 = 4×66: 66 = 66 態, 4 = B")
print(f"  ★ 264 = 6×44: 6 = 2N_gen, 44 = N_d")

# ============ 6. V_obs 閉合形式 ============
print("\n[6] V_obs = 283.0752 閉合形式")
V_obs = 283.0752
print(f"  V_obs = {V_obs:.6f}")
print(f"  7N_d − 25 = 308 − 25 = 283")
print(f"  7 = L₄, 25 = F₈+B = CPX gap")
print(f"  283.0000 vs {V_obs}: 誤差 {abs(283-V_obs)/V_obs*100:.4f}%")
print(f"  6N_d + 19 = 264 + 19 = 283")
print(f"  283.0821 (F(γ)+19) vs {V_obs}: 誤差 {abs(283.082129-V_obs)/V_obs*100:.4f}%")
print(f"  283.0752 vs 283.0821: 差 {283.082129-V_obs:.6f}")

# 283.0752 精確結構
print(f"\n  V_obs − 283 = {V_obs - 283:.6f}")
print(f"  0.0752 ≈ ?")
print(f"  0.0752 ≈ γ_4×0.928? {4*math.sin(4*math.pi/88)**2*0.928:.6f}")
print(f"  0.0752 ≈ γ_29/36 − γ_4/22? {(4*math.sin(29*math.pi/88)**2/36) - (4*math.sin(4*math.pi/88)**2/22):.6f}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("三期 08 總結:")
print("=" * 72)
print(f"""
  F(γ) block 分解:
    F_diag = {F_diag:.6f}
    F_2idx = {F_2idx:.6f}
    F_mix  = {F_mix:.6f}

  264 = 6N_d = 88×3 = 2N_d×N_gen = B×66

  V_obs 閉合形式:
    7N_d − 25 = 283.0000 ({abs(283-V_obs)/V_obs*100:.4f}%)
    F(γ) + 19 = 283.0821 ({abs(283.082129-V_obs)/V_obs*100:.4f}%)
""")
out = {
    "test": "O62 三期 08: F(γ) block 分解",
    "F_diag": float(F_diag), "F_2idx": float(F_2idx), "F_mix": float(F_mix),
    "F_block": [[[float(F_block[i,j,k]) for k in range(3)] for j in range(3)] for i in range(3)],
    "F_minus_264": float(Fg - 264),
    "V_obs_forms": {"7Nd_minus_25": 283.0, "F_gamma_plus_19": float(Fg+19)},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "08_block_decomp.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 08 完成!")
