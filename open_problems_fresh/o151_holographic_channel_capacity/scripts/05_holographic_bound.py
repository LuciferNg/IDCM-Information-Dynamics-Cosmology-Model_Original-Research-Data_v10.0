#!/usr/bin/env python3
"""
O151 — Script 05: 全息界限 (Holographic Bound)
================================================
1. S_dS = A/(4 l_P^2) 世界環熵上限重推導 (O121: 1.95e122)
2. 面積律 1/4 = 1/B 讀法 (O121 遺留)
3. log2(S_dS) vs 結構候選: C(29,2) = 406 -> 陷阱窗掃描 (預期巧合排除)
4. 2^88 (觀察者微態) vs S_dS: 信道容量 vs 熵容量 分層
5. Bekenstein 飽和: S = 2 pi R E/(hbar c) with E = R c^4/(2G) (dS Komar)
"""
import math

N_d = 44
B = 4

results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

print("=" * 74)
print("  O151 S05: 全息界限")
print("=" * 74)

# ---------------------------------------------------------------
# 1. 世界環熵上限 (O121 重推導)
# ---------------------------------------------------------------
print("\n--- 1. S_dS = A/(4 l_P^2) 重推導 ---")
c = 2.99792458e8        # m/s
omega_ring = 72.59      # (km/s)/Mpc (O73)
Mpc_m = 3.085677581e22  # m/Mpc
R_world_Mpc = 4129.94   # Mpc (src/kchain_wave_params.py)
R_world_m = R_world_Mpc * Mpc_m
lP = 1.616255e-35       # m (Planck length)
A = 4 * math.pi * R_world_m ** 2
S_dS = A / (4 * lP ** 2)
print(f"  R_world = {R_world_Mpc} Mpc = {R_world_m:.4e} m")
print(f"  A       = {A:.4e} m^2")
print(f"  S_dS    = A/(4 lP^2) = {S_dS:.4e}")
check("S_dS ~ 1.95e122 (O121 重現)", abs(S_dS - 1.95e122) / 1.95e122 < 0.01)

# R_world = c/omega_ring 一致性
R_from_w = c / (omega_ring * 1e3 / Mpc_m) / Mpc_m  # Mpc: omega in (km/s)/Mpc -> 1/s
print(f"  c/omega_ring = {R_from_w:.2f} Mpc (vs 4129.94, O73 閉合)")
check("R_world = c/omega_ring 一致", abs(R_from_w - R_world_Mpc) / R_world_Mpc < 0.02)

# ---------------------------------------------------------------
# 2. 面積律 1/4 = 1/B
# ---------------------------------------------------------------
print("\n--- 2. 面積律係數 1/4 = 1/B ---")
print(f"  1/4 = 1/B = {1/B} (K_Tree 分支因子)")
print("  (O121 遺留 🟡: 1/4 嘅 B 讀法係身份, 唔係推導)")
check("1/4 = 1/B (代數身份)", abs(0.25 - 1 / B) < 1e-12)

# ---------------------------------------------------------------
# 3. log2(S_dS) vs 結構候選
# ---------------------------------------------------------------
print("\n--- 3. log2(S_dS) vs 結構候選 (陷阱窗掃描) ---")
logS = math.log2(S_dS)
print(f"  log2(S_dS) = {logS:.6f} bits")
candidates = {
    "C(29,2) = 406":      406.0,
    "2^9 = 512":          512.0,
    "88*4.6":             88 * 4.6,
    "44*9.23":            44 * 9.233,
    "528*0.77":           528 * 0.7694,
}
for name, val in candidates.items():
    dev = abs(logS - val) / val
    in_trap = 1e-5 <= dev <= 1e-3
    flag = "  <== 陷阱窗! 🟡 巧合排除" if in_trap else ""
    print(f"  {name:14s}: dev = {dev:.3e}{flag}")
check("C(29,2) = 406 vs log2(S_dS) 落入陷阱窗 (0.06%) -> 排除",
      1e-5 <= abs(logS - 406.0) / 406.0 <= 1e-3)
print("  判決: log2(S_dS) ~ 406 bits 係巧合 (陷阱窗), 唔係結構閉合")

# ---------------------------------------------------------------
# 4. 信道容量 vs 熵容量: 分層
# ---------------------------------------------------------------
print("\n--- 4. 容量分層 ---")
micro_obs = 2 ** 88
print(f"  觀察者信道微態 2^88   = {micro_obs:.3e}")
print(f"  世界環熵上限 S_dS     = {S_dS:.3e}")
print(f"  比率 = {S_dS / micro_obs:.3e}")
check("2^88 << S_dS (9 個數量級以上)", S_dS / micro_obs > 1e9)
print("  解讀: 信道容量 88 bits = 每次掃描嘅資訊預算 (速率/預算層)")
print("        S_dS = 狀態計數熵上限 (存儲層) — 兩層唔同, 冇直接相等")
print("        觀察者係低熵信道: 88 bits << 406 bits 熵上限")

# ---------------------------------------------------------------
# 5. Bekenstein 飽和 (dS Komar 能量)
# ---------------------------------------------------------------
print("\n--- 5. Bekenstein 飽和 ---")
G = 6.67430e-11        # m^3 kg^-1 s^-2
hbar = 1.054571817e-34  # J s
# dS Komar 能量: E = R c^4/(2G) -> S_BeK = pi R^2 c^3/(hbar G) = A/(4 lP^2)
# 用精確 lP^2 = hbar G/c^3 (唔用四捨五入 lP) -> 數學恒等
lP2_exact = hbar * G / c ** 3
E_K = R_world_m * c ** 4 / (2 * G)
S_BeK = 2 * math.pi * R_world_m * E_K / (hbar * c)
S_dS_exact = A / (4 * lP2_exact)
print(f"  E_K = R c^4/(2G) = {E_K:.3e} J (dS Komar)")
print(f"  S_BeK = 2 pi R E_K/(hbar c) = {S_BeK:.4e}")
print(f"  S_dS (精確 lP^2) = {S_dS_exact:.4e}")
dev_bek = abs(S_BeK - S_dS_exact) / S_dS_exact
print(f"  dev = {dev_bek:.3e}")
check("Bekenstein 飽和: S_BeK = S_dS (dS 飽和不等式, 用 Komar 能量)",
      dev_bek < 1e-12)
print("  物理: dS 空間熵恰好飽和 Bekenstein 界限 (標準結果)")
print("        IDCM 世界環 = 最大黑洞 (O121) -> 熵上限 = 信道嘅存儲上界")

# ---------------------------------------------------------------
# 6. 面積律同信道嘅接駁 (誠實)
# ---------------------------------------------------------------
print("\n--- 6. 1/4 = 1/B 同信道容量接駁 (誠實標記) ---")
print("  候選: S_max = A/(4 lP^2) = A x (1/B) / lP^2")
print("        B = 4 = K_Tree 分支 = 每格 2 bits (log2 B)")
print("        -> 每 Planck 格 1/4 = 1/B 熵單位 = 每 4 格 1 bit")
print("        (呢個係統一讀法, 需要 O121 面積律機制先算閉合 -> 🟡)")
check("面積律 x 信道讀法標記為 🟡 (機制未閉合)", True)

print("\n" + "=" * 74)
print(f"  S05 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
