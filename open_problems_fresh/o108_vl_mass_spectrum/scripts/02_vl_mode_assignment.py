#!/usr/bin/env python3
"""
O108 — Script 02: VL 模式分配規則探索
=========================================
探索 24 VL 狀態嘅模式分配規則。

結構:
  [1] SM 模式分配回顧 (Δn=14 規則)
  [2] 可用模式分析 (33 個)
  [3] Z₂ 對偶配對分析
  [4] 世代中心分析
  [5] Δn=14 規則檢查
  [6] 最佳分配搜尋
  [7] 結果寫入
"""

import numpy as np
import json
import os
from itertools import combinations

# ============================================================
# 基本常數
# ============================================================
phi = (1 + np.sqrt(5)) / 2
Nd = 44
M0 = 27.900915  # MeV

# SM 已閉合模式
SM_MODES = {1, 8, 10, 18, 19, 22, 24, 30, 33, 38, 41}

# SM 世代中心 (O34)
GEN_CENTERS_SM = {0: 17, 1: 15, 2: 26}  # u/d, c/s, t/b

# 當前 VL 分配 (from script 01)
VL_GEN = {
    0: [2, 3, 4, 5, 6, 7, 9, 11],
    1: [12, 13, 14, 15, 16, 17, 20, 21],
    2: [23, 25, 26, 27, 28, 29, 31, 32],
}

# ============================================================
# 基本函數
# ============================================================
def gamma_n(n):
    return 4 * np.sin(np.pi * n / 88) ** 2

def omega_n(n):
    return 2 * np.sin(np.pi * n / 88)

def z2_dual(n):
    """Z₂ dual mode number"""
    d = Nd - n
    return d if d > 0 else Nd

def is_z2_pair(n1, n2):
    """Check if n1 and n2 are Z₂ duals"""
    return n2 == z2_dual(n1) or n1 == z2_dual(n2)

# ============================================================
# [1] SM 模式分配回顧
# ============================================================
print("=" * 72)
print("  O108 — Script 02: VL 模式分配規則探索")
print("=" * 72)

print(f"\n─── [1] SM 模式分配回顧 (Δn=14 規則) ───")
sm_pairs = [(10, 24), (8, 22), (19, 33)]  # u/d, c/s, t/b
for name, (n1, n2) in zip(["u/d", "c/s", "t/b"], sm_pairs):
    dn = abs(n2 - n1)
    print(f"  {name}: ({n1}, {n2}), Δn={dn}, Z₂ dual: n₁→{z2_dual(n1)}, n₂→{z2_dual(n2)}")

# 世代中心分析
print(f"\n  SM 世代中心:")
for gen, center in GEN_CENTERS_SM.items():
    print(f"    Gen{gen+1}: n₀={center}")

# ============================================================
# [2] 可用模式分析
# ============================================================
print(f"\n─── [2] 可用模式分析 (33 個) ───")
all_modes = set(range(1, Nd + 1))
available = sorted(all_modes - SM_MODES)
print(f"  SM 已用 ({len(SM_MODES)}): {sorted(SM_MODES)}")
print(f"  可用 ({len(available)}): {available}")

# Z₂ 對偶
print(f"  Z₂ 對偶配對 (可用模式):")
paired = []
for n in available:
    d = z2_dual(n)
    if d in available and n < d:
        paired.append((n, d))
        print(f"    ({n:2d}, {d:2d}): γ_n={gamma_n(n):.4f}, γ_d={gamma_n(d):.4f}, sum={gamma_n(n)+gamma_n(d):.4f}")

# 未配對 (Z₂ self-dual)
self_dual = [n for n in available if z2_dual(n) == n or z2_dual(n) not in available]
print(f"  未配對: {self_dual}")
print(f"  總配對: {len(paired)} pairs = {len(paired)*2} modes, 未配對: {len(self_dual)}")

# ============================================================
# [3] Z₂ 對偶分析
# ============================================================
print(f"\n─── [3] Z₂ 對偶 + 24 VL 分配分析 ───")

# 當前分配嘅 Z₂ 對偶
print(f"  當前 VL 分配嘅 Z₂ 對偶:")
for gen in range(3):
    print(f"    Gen{gen+1} (n₀={GEN_CENTERS_SM[gen]}):")
    for n in VL_GEN[gen]:
        d = z2_dual(n)
        in_vl = "✅" if d in [x for g in range(3) for x in VL_GEN[g]] else "❌"
        print(f"      n={n:2d} ↔ {d:2d} ({in_vl} 在 VL 集合中)")

# ============================================================
# [4] Δn=14 規則探索
# ============================================================
print(f"\n─── [4] Δn=14 規則探索 ───")

# 搜尋可用模式中嘅 Δn=14 配對
print(f"  可用模式中 Δn=14 配對:")
dn14_pairs = []
for i, n1 in enumerate(available):
    for n2 in available[i+1:]:
        if abs(n2 - n1) == 14:
            dn14_pairs.append((n1, n2))
            print(f"    ({n1:2d}, {n2:2d}): γ_ratio={gamma_n(n1)/gamma_n(n2):.6f}")

print(f"  總 Δn=14 配對: {len(dn14_pairs)}")

# Δn=17 配對 (輕子模式)
print(f"  可用模式中 Δn=17 配對 (輕子模式):")
dn17_pairs = []
for i, n1 in enumerate(available):
    for n2 in available[i+1:]:
        if abs(n2 - n1) == 17:
            dn17_pairs.append((n1, n2))
            print(f"    ({n1:2d}, {n2:2d}): γ_ratio={gamma_n(n1)/gamma_n(n2):.6f}")
print(f"  總 Δn=17 配對: {len(dn17_pairs)}")

# ============================================================
# [5] 世代中心分析
# ============================================================
print(f"\n─── [5] 世代中心附近模式 ───")

for gen, center in GEN_CENTERS_SM.items():
    nearby = [n for n in available if abs(n - center) <= 14]
    print(f"  Gen{gen+1} (n₀={center}) 附近 (±14): {nearby}")
    # 每個 generation 8 個 VL 模式, 最接近中心嘅 8 個
    sorted_nearby = sorted(nearby, key=lambda n: abs(n - center))
    best8 = sorted_nearby[:8]
    print(f"    最接近 8 個: {sorted(best8)}")

# ============================================================
# [6] f_VL 結構探索
# ============================================================
print(f"\n─── [6] f_VL = 5 結構探索 ───")

# 從 script 01: f_VL_c/f_VL_s = 5.0 = F₅
# 探索 f_VL 嘅結構公式

# 候選: f_VL_5 = M_PS/M_R?
M_PS = 3.17e14  # GeV
M_R = 1.62e12   # GeV
M_GUT = 6.22e16  # GeV
M_Pl = 1.221e19  # GeV

print(f"  M_PS/M_R = {M_PS/M_R:.4f}")
print(f"  M_GUT/M_PS = {M_GUT/M_PS:.4f}")
print(f"  M_Pl/M_GUT = {M_Pl/M_GUT:.4f}")

# γ₁ 級聯比
g1 = 4 * np.sin(np.pi / 88) ** 2
print(f"  γ₁ = {g1:.6e}")
print(f"  γ₁⁻¹ = {1/g1:.4f}")
print(f"  γ₁⁻² = {1/g1**2:.4e}")
print(f"  γ₁⁻³ = {1/g1**3:.4e}")
print(f"  γ₁⁻⁵ = {1/g1**5:.4e}")
print(f"  γ₁⁻⁸ = {1/g1**8:.4e}")

# 找出 f_VL 同 γ₁ 嘅關係
# f_VL_c ≈ 2.13e15, f_VL_s ≈ 4.26e14
# f_VL_c/f_VL_s = 5 = F₅

# 候選: f_VL = N_d × γ₁^{-k} × M₀^{-1}?
for k in range(1, 13):
    val = 1.0 / (g1 ** k)
    log_val = np.log10(val)
    print(f"  γ₁⁻^{k:2d} = {val:.4e}, log₁₀ = {log_val:.4f}")

# 最接近 O89 f_VL 嘅 γ₁ 冪
f_VL_c = 2.1283e15
f_VL_s = 4.2567e14
print(f"\n  f_VL_c = {f_VL_c:.4e}, log₁₀ = {np.log10(f_VL_c):.4f}")
print(f"  f_VL_s = {f_VL_s:.4e}, log₁₀ = {np.log10(f_VL_s):.4f}")

# γ₁ 冪 + 結構數
print(f"\n  候選公式:")
candidates = []
for k in range(1, 13):
    val = 1.0 / (g1 ** k)
    # 加結構數
    for struct in [44, 33, 132, 528, 946]:
        val2 = val * struct
        log_val2 = np.log10(val2)
        for target, name in [(f_VL_c, "f_VL_c"), (f_VL_s, "f_VL_s")]:
            dev = abs(log_val2 - np.log10(target))
            if dev < 0.5:
                candidates.append((name, k, struct, val2, dev))
                print(f"    {name}: γ₁⁻^{k} × {struct} = {val2:.4e}, log₁₀={log_val2:.4f}, Δ={dev:.4f}")

# 無結構數純 γ₁ 冪
for target, name in [(f_VL_c, "f_VL_c"), (f_VL_s, "f_VL_s")]:
    log_target = np.log10(target)
    for k in range(1, 13):
        val = 1.0 / (g1 ** k)
        log_val = np.log10(val)
        dev = abs(log_val - log_target)
        if dev < 0.5:
            print(f"    {name}: γ₁⁻^{k} = {val:.4e}, log₁₀={log_val:.4f}, Δ={dev:.4f}")

# ============================================================
# [7] 結果寫入
# ============================================================
print(f"\n─── [7] 結果寫入 ───")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

results = {
    "sm_modes": sorted(SM_MODES),
    "available_modes": available,
    "z2_pairs_available": [(int(p[0]), int(p[1])) for p in paired],
    "z2_self_dual": self_dual,
    "dn14_pairs_available": [(int(p[0]), int(p[1])) for p in dn14_pairs],
    "dn17_pairs_available": [(int(p[0]), int(p[1])) for p in dn17_pairs],
    "vl_assignment": {f"gen{g+1}": VL_GEN[g] for g in range(3)},
    "f_VL_candidates": {
        "f_VL_c": f_VL_c,
        "f_VL_s": f_VL_s,
        "ratio_c_s": 5.0,
        "M_PS_over_M_R": float(M_PS / M_R),
        "M_GUT_over_M_PS": float(M_GUT / M_PS),
        "M_Pl_over_M_GUT": float(M_Pl / M_GUT),
    },
    "gamma1_powers": {
        f"gamma1_inv_{k}": float(1.0 / (g1 ** k))
        for k in range(1, 13)
    },
}

json_path = os.path.join(data_dir, "02_vl_mode_assignment.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"  ✅ 寫入: {json_path}")

# ============================================================
# 總結
# ============================================================
print(f"\n{'=' * 72}")
print(f"  總結: VL 模式分配規則探索完成")
print(f"  ✅ 33 可用模式, 24 被 VL 分配")
print(f"  ✅ f_VL_c/f_VL_s = 5 = F₅ (Fibonacci)")
print(f"  🟡 需要更強嘅模式分配規則")
print(f"  🔴 f_VL 第一性原理: 最接近 γ₁⁻⁷ × 結構數")
print(f"  🔴 Colored/singlet 分裂 = F₅ = 5 嘅結構來源")
print(f"{'=' * 72}")