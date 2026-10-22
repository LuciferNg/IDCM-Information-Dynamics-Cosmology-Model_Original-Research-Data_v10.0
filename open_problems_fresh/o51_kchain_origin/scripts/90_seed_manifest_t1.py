#!/usr/bin/env python3
"""
O51/90: 種子 manifest 微觀機制 — T1 疊代收斂深度探索
===============================================================
問題 (O51 §四 剩餘 🔴): 種子 (0,1)「幾時/點樣 manifest」成 44-site K_Chain 譜?

結構假設: 種子疊代收斂到結構閾值 = 譜量子化完成深度。
主遞歸 C_{n+1}=1/(1+C_n), C_0=1 → C_n = F_{n-1}/F_n (連分數收斂)
誤差 ε_n = |C_n − 1/φ| = 1/(φ^{n+1}·F_n) (sympy 精確)

閾值候選 (全零新常數):
  1/88  (譜分辨率 1/2N_d)
  1/90  (Σγ)
  γ₁    (最低模式能量 4sin²(π/88))
  1/L₅  (1/11)
  1/B   (1/4)
  1/44  (1/N_d)

目標: 搵 n_first(ε*) — 第一個 n 令 ε_n < ε* — 睇有冇結構命中 (22/33/44/88/11/4)
"""
import sympy as sp

phi = sp.Rational(1, 2) * (1 + sp.sqrt(5))
inv_phi = sp.simplify(1 / phi)

# 連分數收斂: F₁=F₂=1
F = [sp.Integer(1), sp.Integer(1)]
for n in range(2, 90):
    F.append(F[-1] + F[-2])

print("=== 種子 manifest T1: 疊代收斂深度 ===\n")
print("主遞歸 C_{n+1}=1/(1+C_n), C_0=1 → C_n = F_{n-1}/F_n")
print(f"極限 1/φ = {float(inv_phi.evalf(15)):.12f}\n")

# 閾值候選
targets = {
    "1/88 (譜分辨率)": sp.Rational(1, 88),
    "1/90 (Σγ)": sp.Rational(1, 90),
    "γ₁ (最低模式)": 4 * sp.sin(sp.pi / 88) ** 2,
    "1/L₅ (1/11)": sp.Rational(1, 11),
    "1/B (1/4)": sp.Rational(1, 4),
    "1/44 (1/N_d)": sp.Rational(1, 44),
}

# 誤差序列
print("--- 誤差 ε_n = 1/(φ^{n+1}·F_n) ---")
first_hit = {}
for n in range(1, 89):
    eps = sp.simplify(1 / (phi**(n+1) * F[n-1]))
    epsf = float(eps.evalf(20))
    for name, t in targets.items():
        tf = float(t.evalf(20))
        if name not in first_hit and epsf < tf:
            first_hit[name] = n
    if n <= 10 or n in (22, 33, 44, 88):
        cn = sp.simplify(F[n-1] / F[n])
        print(f"  n={n:2d}  ε={epsf:.3e}  C_n={float(cn.evalf(12)):.10f}  dev={(float(cn.evalf(20))-float(inv_phi.evalf(20))):.2e}")

print("\n--- 首次突破閾值 n_first(ε*) ---")
for name, n in first_hit.items():
    print(f"  {name:20s} → n_first = {n}")

# 結構命中檢查
print("\n--- 結構命中分析 ---")
hits = {n: [name for name, nf in first_hit.items() if nf == n] for n in set(first_hit.values())}
for n, names in sorted(hits.items()):
    print(f"  n={n}: {names}")

# 特別檢查: n_first 有冇 22/33/44/88/11/4/6?
special = {11: "L₅", 22: "N_d/2", 33: "K_tree", 44: "N_d", 88: "2N_d", 4: "B", 6: "2×N_gen"}
print("\n--- 特殊深度候選命中 ---")
for n, label in special.items():
    eps_n = float(sp.simplify(1/(phi**(n+1)*F[n-1])).evalf(20))
    print(f"  n={n:2d} ({label:6s}): ε={eps_n:.3e}")

# 驗證 C_n = F_{n-1}/F_n (sympy)
print("\n--- 驗證 C_n 閉式 ---")
ok = True
for n in range(1, 30):
    c_iter = sp.Integer(1)
    for _ in range(n):
        c_iter = sp.simplify(1 / (1 + c_iter))
    c_frac = sp.simplify(F[n-1] / F[n])
    if sp.simplify(c_iter - c_frac) != 0:
        ok = False
        print(f"  ❌ n={n}: 迭代 C={c_iter} ≠ 連分數 {c_frac}")
print(f"  {'✅ 全部一致 (C_n = F_{n-1}/F_n)' if ok else '❌ 不一致'}")
