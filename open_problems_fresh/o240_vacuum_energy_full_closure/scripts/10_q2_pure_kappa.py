#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O240 攻堅 10: Q2 深化 — V_Λ 純κ譜形式 + 73=90−17 恆等探測
================================================================
承接 docs/07（19 = |Σκ_diag|/20 本O自證），Q2 兩個更深位:

C1 ★ V_Λ 純 κ 譜形式: V_Λ = F(γ) + |Σκ_diag|/(φ(88)/2) — 完全甩開 O57 P̂ 數據
  - V_Λ = 264.082... + 19 = 283.082... (O84 原式 = F+N_d−F₈−B)
  - 檢定: F(γ) + |Σκ_diag|/20 == 283.0821 EXACT; 同 O84 原式一致
C2 ★ 73 = 90−17: rank(CPX) = 73 可否由 Σγ_even=90 − G 負方向 17 重建?
  - 如果成立: 25 = 98−73 = 98−90+17 = 8+17 ⟹ O84「(8,17) 分解」有結構出處
  - 8 = |Σκ| = 2B; 17 = G 負方向數 (docs/03) 或 F_proj (O84)
C3: 25 = 98−90+17 vs O84 (F₈=8, B=17): 8 同 17 嘅身份對照
C4: 19 = 44−25 嘅第三讀法: 44−(98−90+17) = 44−25 — 檢定 O84 兩分解都出 19
輸出: data/10_q2_pure_kappa.json; RESULT: N/N
"""
import os, json, sys, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

O53 = os.path.join(BASE, "..", "o53_cy3_reality", "data", "polytopes")
with open(os.path.join(O53, "cy36_98_intersection_full.json")) as f:
    kappa = np.array(json.load(f)["kappa"])
g36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2

def F(t): return float(np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0)
Fg = F(g36)
d = Fg - 264
kd = sum(int(kappa[i, i, i]) for i in range(36))
phi88_2 = 20.0

# ============ C1: V_Λ 純κ譜形式 ============
print("=" * 60)
print("C1: ★ V_Λ = F(γ) + |Σκ_diag|/(φ(88)/2) 純κ譜閉合")
print("=" * 60)
V_lam_pure = Fg + abs(kd) / phi88_2
V_lam_o84 = Fg + 44 - 8 - 17
print(f"  F(γ)              = {Fg:.12f}")
print(f"  |Σκ_diag|/20      = {abs(kd)/phi88_2}")
print(f"  V_Λ (純κ譜)       = {V_lam_pure:.12f}")
print(f"  V_Λ (O84 原式)    = {V_lam_o84:.12f}")
check("C1a: V_Λ = F+|Σκ_diag|/20 (純κ譜) == O84 原式 F+N_d−F₈−B",
      abs(V_lam_pure - V_lam_o84) < 1e-9, f"({V_lam_pure:.6f} vs {V_lam_o84:.6f})")
check("C1b: V_Λ = 283.0821 命中", abs(V_lam_pure - 283.0821292326) < 1e-6,
      f"({V_lam_pure:.9f})")
# 機制意義: O84 需要 N_d−F₈−B = 19 (兩個人工數 F₈=8, B=17);
# 新形式只需要 κ 譜對角項總和同 88-site 度數 — 零外部輸入
print(f"  ⟹ O84 19 = N_d−F₈−B 由 κ 譜直接取代: 19 = |Σκ_diag|/20")
print(f"  ⟹ V_Λ 完全由 κ prepotential + 88-site 度數決定 (唔靠 O57 P̂)")
check("C1c: 19 純κ譜 = 44−F₈−B (兩讀收斂)", abs(kd)/phi88_2 == 19, f"({abs(kd)/phi88_2})")

# ============ C2: 73 = 90−17? ============
print("\n" + "=" * 60)
print("C2: ★ 73 = 90 − 17: rank(CPX) 可否由譜重建?")
print("=" * 60)
# 88-site 雙鏈: g88[k] = 4sin²(kπ/176), k=1..88; even index = γ₁..γ₄₄ = 世界側 90
g88 = [4 * math.sin(k * math.pi / 176) ** 2 for k in range(1, 89)]
S_even = sum(g88[k] for k in range(1, 88, 2))   # γ₂+γ₄+...+γ₈₈ = 90 (世界側)
S_odd = sum(g88[k] for k in range(0, 88, 2))    # γ₁+γ₃+...+γ₈₇ = 88 (觀察者側)
print(f"  Σγ_even(88-site 雙鏈) = {S_even:.9f} (90?)")
print(f"  Σγ_odd(88-site 雙鏈)  = {S_odd:.9f} (88?)")
# G 本徵負方向數
dFg = 0.5 * np.einsum("ijk,j,k", kappa, g36, g36)
Yg = np.einsum("ijk,k", kappa, g36)
G = -Yg/Fg + np.outer(dFg, dFg)/Fg**2
gv = np.linalg.eigvalsh(G)
n_neg = int(np.sum(gv < -1e-8))
print(f"  G 負方向數 = {n_neg}")
print(f"  Σγ_even − n_neg = {S_even - n_neg:.1f} (rank(CPX) = 73?)")
# O57 rank(CPX) = 73 (docs 引用)
check("C2a: Σγ_even − n_neg = 73 (rank CPX 譜重建候選)",
      abs(S_even - n_neg - 73) < 1e-6, f"({S_even - n_neg:.4f})")
print(f"  90 = Σγ_even (結構), 17 = G 負方向數 (docs/03) / F_proj (O84)")
# 但有 O57 官方 rank=73; 17 同時 = F_proj (O84 B 命名) — 需 O57 數據證實係 17 定 73 直接
# C2 係「譜重建候選」 — 標記為需要 O57 docs 對照

# ============ C3: 25 = 98−73 = 98−90+17 = 8+17 ============
print("\n" + "=" * 60)
print("C3: 25 嘅 (8,17) 結構出處")
print("=" * 60)
h21 = 98
r73 = 73
gap = h21 - r73
print(f"  25 = h²¹ − rank(CPX) = 98 − 73 = {gap}")
# 8 = |Σκ| 或 Σγ_even−Σγ_odd−2? 25 = 98−90+17: 98−90 = 8 = |Σκ_diag|/47.5? 唔, 8 = |Σκ|
sk_abs = abs(sum(int(kappa[i, j, k]) for (i, j, k) in np.argwhere(kappa != 0)))
print(f"  |Σκ| total = {sk_abs} (8?)")
print(f"  98 − 90 = {h21 - S_even:.1f} (h²¹ − Σγ_even = 8 ~ |Σk|?)")
check("C3a: h²¹ − Σγ_even = 8 = |Σκ| (候選身份)", abs(h21 - S_even - sk_abs) < 1e-6,
      f"({h21-S_even:.4f} vs {sk_abs})")
# 25 = 8 + 17 (O84 分解): 8 = |Σκ|, 17 = F_proj/G負方向
print(f"  25 = 8 + 17: 8 = |Σκ| = {sk_abs}, 17 = G負方向 = {n_neg}")
check("C3b: 25 = |Σκ| + 17 (O84 (8,17) 結構化)", sk_abs + n_neg == 25,
      f"({sk_abs}+{n_neg})")
# O84 另一分解 21+4: 21 = F₈, 4 = B; 而家 25 = 8+17 有結構出處
print(f"  ⟹ (8,17) 分解由 |Σκ| + G負方向 結構化; (21,4) 係 Fib/K_Tree 讀法")

# ============ C4: 19 第三讀法 ============
print("\n" + "=" * 60)
print("C4: 19 = 44 − 25 = 44 − (h²¹−Σγ_even+17)")
print("=" * 60)
r19_a = 44 - (h21 - S_even + n_neg)   # 44−(98−90+17)
r19_b = 44 - (h21 - 73)               # 44−25
r19_c = abs(kd) / phi88_2             # 380/20
print(f"  44−(98−90+17)  = {r19_a:.4f}")
print(f"  44−(98−73)     = {r19_b:.4f}")
print(f"  |Σκ_diag|/20   = {r19_c:.4f}")
check("C4a: 19 三讀收斂 (44−h²¹+Σγ_even−17 = 44−25 = |Σκ_diag|/20)",
      abs(r19_a - 19) < 1e-6 and abs(r19_c - 19) < 1e-6,
      f"({r19_a:.4f}, {r19_b:.4f}, {r19_c:.4f})")

with open(os.path.join(DATA, "10_q2_pure_kappa.json"), "w") as f:
    out = {
        "V_lambda_pure_kappa": V_lam_pure, "V_lambda_o84": V_lam_o84,
        "sum_kappa_diag_over_20": abs(kd)/phi88_2,
        "S_even": S_even, "S_odd": S_odd, "G_neg": n_neg,
        "rank_CPX_reconstructed": S_even - n_neg,
        "gap_from_spectra": h21 - S_even + n_neg,
        "passed": passed, "failed": failed,
    }
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)