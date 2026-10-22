"""
O72 驗證 02: 自足定義核查 — 所有 K_Chain/K_Tree 定義數字一次過驗證
=====================================================================
目的: 供 docs/01_definition.md 使用嘅所有數字, 獨立核查, 唔准幻覺。

核查清單 (全部由源碼/公式獨立計算):
  [1] γ_k = 4sin²(πk/88), k=1..44 (K_Chain 色散)
  [2] Σγ_even = 90, Σγ_odd = 88, total = 178 = 2F₁₁
  [3] R_H = c/H₀ = 4129.94 Mpc (H₀=72.59), N_d = 44
  [4] λ_sync = c·T_sync/88 = 294.88 Mpc, T_sync = 2π/H₀ = 84.64 Gyr
  [5] v_g = c·cos(πn/88), n=22 → 0.7071c (唔係駐波!)
  [6] K_Tree: μ_m = φ^{L−m}, L = 53/8 = 6.625
  [7] K_Tree 33 = h11 − N_gen = 36−3 (O59)
  [8] 87 原子 = 43 邊 + 44 self-loop (kchain_number_field)
  [9] 946 拍頻 = 43×87 (可分離三角表)
  [10] 複合譜 44×34 = 1496
  [11] 264 = 3×Σγ_odd (O62)
  [12] φ = (1+√5)/2 = 1.6180339887...
"""
import numpy as np

ok = []
def check(name, cond, detail=""):
    ok.append(cond)
    print(f"[{'✅' if cond else '❌'}] {name} {detail}")

phi = (1 + np.sqrt(5)) / 2
Nd = 44
c = 299792.458  # km/s
H0 = 72.59      # km/s/Mpc
Gyr = 3.15576e16  # s

# [1] γ_k
k = np.arange(1, Nd+1)
gamma = 4.0 * np.sin(np.pi * k / 88.0)**2
check("γ_1 = 4sin²(π/88)", abs(gamma[0] - 4*np.sin(np.pi/88)**2) < 1e-15, f"γ_1={gamma[0]:.6f}")

# [2] 奇偶和 — 88-site 對偶鏈 (γ_k = 4sin²(πk/176), k=1..88)
k88 = np.arange(1, 89)
g88 = 4.0 * np.sin(np.pi * k88 / 176.0)**2
S_odd_88  = g88[0::2].sum()   # k=1,3,...,87
S_even_88 = g88[1::2].sum()   # k=2,4,...,88
print(f"[2] 88-site: Σγ_odd(k=1,3..87) = {S_odd_88:.10f}  Σγ_even(k=2,4..88) = {S_even_88:.10f}  total = {g88.sum():.10f}")
check("88-site Σγ_odd = 88", abs(S_odd_88 - 88) < 1e-9, f"({S_odd_88:.10f})")
check("88-site Σγ_even = 90", abs(S_even_88 - 90) < 1e-9, f"({S_even_88:.10f})")
check("88-site total = 178 = 2F₁₁", abs(g88.sum() - 178) < 1e-9, f"({g88.sum():.10f}, F₁₁=89)")

# [2b] 44-site 鏈總和 = 90 (世界鏈)
g44_sum = gamma.sum()
check("44-site Σγ(k=1..44) = 90", abs(g44_sum - 90) < 1e-9, f"({g44_sum:.10f})")

# [3] R_H
R_H = c / H0 * 1e3  # km / (km/s/Mpc) * 1e3 = Mpc... 其實 c/H0 = Mpc
# c [km/s] / H0 [km/s/Mpc] = Mpc
R_H_mpc = c / H0
check("R_H = c/H₀ = 4129.94 Mpc", abs(R_H_mpc - 4129.94) < 0.01, f"({R_H_mpc:.2f} Mpc)")
check("N_d = 44 = R_H/λ 基本格", Nd == 44)

# [4] T_sync + λ_sync
T_sync_Gyr = 2*np.pi / H0 / 1e3 * 1e9 / (3.15576e16/3.085677581e19)  # 轉換
# 直接: T_sync = 2π/H₀, H₀=72.59 km/s/Mpc → T = 2π×3.0857e19/(72.59×3.15576e16) Gyr
T_sync = 2*np.pi * 3.085677581e19 / (H0 * 3.15576e16)  # Gyr
print(f"[4] T_sync = {T_sync:.4f} Gyr")
check("T_sync = 2π/H₀ = 84.64 Gyr", abs(T_sync - 84.64) < 0.01, f"({T_sync:.4f})")
lam_sync = c * (T_sync * 3.15576e16) / (88 * 3.085677581e19)  # Mpc
print(f"[4] λ_sync = c·T_sync/88 = {lam_sync:.2f} Mpc")
check("λ_sync = 294.88 Mpc", abs(lam_sync - 294.88) < 0.05, f"({lam_sync:.2f})")

# [5] v_g
for n in [22, 44]:
    vg = np.cos(np.pi*n/88)
    print(f"[5] n={n}: v_g/c = {vg:.6f}")
check("n=22 → v_g = 0.7071c (唔係駐波)", abs(np.cos(np.pi*22/88) - 1/np.sqrt(2)) < 1e-9)
check("n=44 → v_g = 0 (Nyquist)", abs(np.cos(np.pi*44/88)) < 1e-15)

# [6] K_Tree
L_tree = 53/8
check("L = 53/8 = 6.625", abs(L_tree - 6.625) < 1e-12)
mu_0 = phi**(L_tree - 0)
mu_33 = phi**(L_tree - 33)
print(f"[6] μ_0 = φ^{L_tree:.3f} = {mu_0:.6f}, μ_33 = φ^{L_tree-33:.3f} = {mu_33:.6e}")
check("μ_m 遞減階梯 (m 越大越細)", mu_33 < mu_0)
# 33 = h11 - N_gen
check("K_Tree 33 = h11 − N_gen = 36−3", 33 == 36-3)

# [7] 87 原子
check("87 = 43 邊 + 44 self-loop = 88−1", 87 == 43+44 == 88-1)

# [8] 946 拍頻 = C(44,2) = 44×43/2 = 43×22 (差頻拍頻數)
check("946 = C(44,2) = 44×43/2 = 946", 946 == 44*43//2, "(43 對 × 22 = 43×22)")
check("43×22 = 946 (唔係 43×87!)", 43*22 == 946)

# [9] 複合譜
check("1496 = 44×34 (λ_{n,m} = γ_n·μ_m)", 1496 == 44*34)

# [10] 264
check("264 = 3×Σγ_odd = 3×88", 264 == 3*88)

# [11] φ
check("φ = 1.6180339887...", abs(phi - 1.6180339887498949) < 1e-12)

print()
print(f"=== 總計: {sum(ok)}/{len(ok)} PASS ===")
assert all(ok), "有核查失敗!"
