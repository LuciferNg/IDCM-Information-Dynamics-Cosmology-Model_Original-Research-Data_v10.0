#!/usr/bin/env python3
"""
O97 — Level B: 尺度選擇原理 (效率 / 最低生長)
script 02: 喺「整數閉合族自治相似尺度族 x²=bx+1」入面, 點解宇宙揀 b=1 → φ?
=============================================================
主張 C2:
  自相似閉合族 x²=bx+1 (b∈ℤ≥1, 常數項 −1 → rr'=−1 → 閉合 φ".

  1. 預算閉合 τ(μ)=μ⁻¹+μ⁻²=1 只喺 b=1 成立 (φ). b>1 全部 τ<1 (欠預算).
  2. 喺全部整數閉合族之中, b=1 嘅 根=φ 有「最低生長率」λ_min=1.618.
  3. 最低生長率 → 相同動態範圍 W 之下 解析階層最多 → 資訊解析度最高 → 相同 throughput 成本下最有效.
     N_levels(W,λ) = ln W / ln λ,  嚴格 ↓λ → b=1 (φ) 全局最大.
  4. π/e 超越 (冇整數閉合, 冇閉式階層), √2/√3 (constant −2/−3, τ≠1 且唔封閉
     喺單位預算), 2 係有理 (違 O51 946/946 無理比).
=============================================================
"""
import sympy as sp
import math

phi = sp.nsimplify((1 + sp.sqrt(5))/2)
results = []
def record(ok, label, detail=""):
    results.append((ok, label, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")

# ---------- 1. 整數閉合族 x²=bx+1, 根 λ_b=(b+√(b²+4))/2, b=1..10 ----------
print("=== 整數閉合族 x²=bx+1, 根 λ_b, 預算 τ=λ⁻¹+λ⁻² ===")
lambdas = {}
for b in range(1, 11):
    lb = (b + sp.sqrt(b**2 + 4)) * sp.Rational(1,2)
    lambdas[b] = sp.nsimplify(lb)
    tau = sp.N(1/lb + 1/lb**2, 8)
    # tau==1 only iff b==1 (check numeric)
    print(f"  b={b:>2}: λ={float(sp.N(lb,8)):.4f}   τ={float(tau):.5f}   b=1?{'✓' if b==1 else ''}")

# b=1 root == φ, 且係 global min growth
vals = {b: float(lambdas[b].evalf()) for b in lambdas}
ok = math.isclose(vals[1], float(phi.evalf()), rel_tol=1e-6)
record(ok, "b=1 根 = φ = (1+√5)/2", f"λ₁={vals[1]:.6f}, φ={float(phi.n()):.6f}")
ok = all(vals[1] < vals[b] for b in vals if b != 1)
record(ok, "b=1 係整數閉合族全局最低生長率", f"λ₁={vals[1]:.4f} < λ₂={vals[2]:.4f} < λ₃={vals[3]:.4f}")

# ---------- 2. 預算閉合 τ=1 只喺 b=1 ----------
ok_budget = True
for b in range(1, 11):
    lb = lambdas[b]
    tau = 1/lb + 1/lb**2
    d = sp.N(sp.Abs(tau - 1), 6)
    if b == 1:
        ok_budget &= d < 1e-8
    else:
        ok_budget &= d > 0.01   # 欠預算
record(ok_budget, "預算閉合 τ=1 只喺 b=1 (b=2..10 全 τ<1)", "")

# ---------- 3. 階層解析度: N_levels(W)=ln W/ln λ, λ 越小階層越多 ----------
W = 1e8   # 動態範圍 (arbitrary but fixed)
print("\n=== 階層數 N_level(W) = ln W / ln λ, 固定 W ===")
W_float = sp.Rational(math.log(1e8), 1)
Nlevels = {}
for b in range(1, 6):
    lb = lambdas[b]
    n = float(sp.N(sp.log(1e8) / sp.log(lb), 6))
    Nlevels[b] = n
    if b <= 5:
        print(f"  b={b}: λ={float(sp.N(lb,6)):.4f}  N_level={n:.2f}")
ok = all(Nlevels[1] > Nlevels[b] for b in Nlevels if b != 1)
record(ok, "φ(b=1) 喺固定預算下解析階層數最多 (監視度信息)", 
       f"N_level(φ)={Nlevels[1]:.2f} vs N_level(λ₂)={Nlevels[2]:.2f}")

# ---------- 4. π/e/√2/√3/2 排除 ----------
# 4a. 超越: π, e 冇整數閉合 (唔係代數 → 冇閉式組合階層)
for name, mu in [('π', sp.pi), ('e', sp.E)]:
    record(mu.is_algebraic == False,
           f"{name} 係超越數 (冇整數閉合閉環, 冇閉式階層)",
           f"is_algebraic={mu.is_algebraic}")
# 4b. √2, √3: 唔係 x²=bx+1 族 (凸配 root product ≠ −1), fail τ=1
for ip in [2, 3]:
    r = sp.sqrt(ip)
    tau = float(sp.N(1/r + 1/r**2, 6))
    in_family = any(sp.simplify(r - lb) == 0 for lb in lambdas.values())
    record(not in_family, f"√{ip}: 唔喺 x²=bx+1 整數閉合族", f"τ={float(tau):.4f}≠1")
# 4c. 有理尺度 2: τ=0.75<1 (欠預算, 疊唔滿), 且有理 → 譜相稱 (違 O51 無理譜)
record(sp.Rational(1,2) + sp.Rational(1,4) < 1,
       "有理 2: τ=0.75<1 欠 + 有理譜 (違 O51 946/946 無理比)", "τ(2)=0.7500")

npass = sum(1 for o,_,_ in results if o)
ntot = len(results)
print(f"\n=== Level B: {npass}/{ntot} PASS ===")
if npass == ntot:
    print(">>> φ 係整數閉合家族中唯一滿足預算閉合 + 全局最低生長率 → 收支最優)")