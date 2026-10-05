#!/usr/bin/env python3
"""
O53 剩餘問題 1: tr(Y²) ≈ 5 誤差 1.05% 來源分析
=================================================
發現: tr(Y²) = 4.9474 vs 5 = F₅ (誤差 1.05%)

分析:
  1. tr(Y²) = Σ_ijk κ_iab κ_jab J*^i J*^j (展開)
  2. 誤差來源: J* 唔精確? κ 有結構?
  3. 有冇「結構 J*」令 tr(Y²) 精確 = 5?
  4. 5 = F₅ 嘅幾何身份 (Penrose? 5-cell? B₂?)
"""
import os, json, math, sys
import numpy as np
from scipy.optimize import minimize

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 1: tr(Y²) ≈ 5 誤差分析")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])

def trY2(J):
    Y = np.einsum('ijk,k->ij', K, J)
    Y = (Y + Y.T) / 2
    return np.trace(Y @ Y)

# --- [1] 現狀 ---
print("\n[1] 現狀:")
t0 = trY2(J0)
print(f"    tr(Y²) = {t0:.6f} (誤差 {abs(t0-5)/5*100:.2f}%)")

# --- [2] tr(Y²) 分解 ---
print("\n[2] tr(Y²) 分解:")
# tr(Y²) = Σ_ij Y_ij Y_ji = Σ_ijk κ_iab κ_jab J_i J_j (sym)
# 定義 A_ij = κ_iab κ_jab (36×36 矩陣)
A = np.einsum('iab,jab->ij', K, K)
print(f"    A_ij = Σ_ab κ_iab κ_jab (36×36):")
evA = np.linalg.eigvalsh(A)
print(f"    A 本徵值 (前 10): {np.array2string(np.sort(evA)[::-1][:10], precision=3)}")
print(f"    tr(A) = {np.trace(A):.2f}")
print(f"    tr(Y²) = J·A·J = {J0 @ A @ J0:.4f}")

# --- [3] 誤差來源: J 嘅 scale? ---
print("\n[3] scale 掃描 (J → s·J):")
for s in np.linspace(0.9, 1.1, 9):
    t = trY2(s * J0)
    print(f"    s={s:.2f}: tr(Y²) = {t:.4f} ({abs(t-5)/5*100:.2f}%)")
# 最優 s
def f(s):
    return (trY2(s * J0) - 5)**2
res = minimize(f, 1.0)
s_opt = res.x[0]
print(f"    最優 s = {s_opt:.6f} (tr(Y²) = {trY2(s_opt*J0):.6f})")
check("scale 修正唔夠 (誤差唔係 scale)", abs(s_opt - 1.0) > 0.01, f"(s={s_opt:.4f})")

# --- [4] J 方向修正 ---
print("\n[4] 方向修正 (J → J0 + δ):")
# 允許 J 微擾令 tr(Y²) = 5
def loss(delta):
    J = J0 + delta
    return (trY2(J) - 5)**2 + 1e-3 * np.sum(delta**2)
res2 = minimize(loss, np.zeros(36), method='L-BFGS-B')
delta_opt = res2.x
J_opt = J0 + delta_opt
print(f"    修正後 tr(Y²) = {trY2(J_opt):.6f}")
print(f"    ||δ||/||J|| = {np.linalg.norm(delta_opt)/np.linalg.norm(J0)*100:.2f}%")
print(f"    → {'✅ 小修正可達 5 (J 方向問題)' if np.linalg.norm(delta_opt)/np.linalg.norm(J0) < 0.1 else '❌ 需要大修正'}")

# --- [5] 5 嘅幾何身份 ---
print("\n[5] 5 = F₅ 幾何身份:")
print(f"    5 = F₅ (Fibonacci)")
print(f"    5 = 5-cell (4-simplex) 面數 = C(5,2) = 10 /2")
print(f"    5 = 正八面體對頂點數? 6/2+2")
print(f"    5 = P⁴ 維度+1")
print(f"    5 = B 一維? (B=4)")
print(f"    5 = κ 非零行? 每行 mean 31.2 non-zero")

# --- [6] tr(Y²) 同 λ₁ 閉合一致性 ---
print("\n[6] 兩閉合一致性:")
ev = np.linalg.eigvalsh(np.einsum('ijk,k->ij', K, J_opt))
ev = (np.einsum('ijk,k->ij', K, J_opt) + np.einsum('ijk,k->ij', K, J_opt).T)/2
evals = np.linalg.eigvalsh(ev)
l1 = max(evals)
print(f"    J_opt 下: λ₁ = {l1:.6f}, 1/λ₁ = {1/l1:.6f}")
print(f"    φ^(-1/3) = {phi**(-1/3):.6f}")
print(f"    λ₁ 誤差: {abs(1/l1 - phi**(-1/3))/phi**(-1/3)*100:.3f}%")
print(f"    tr(Y²) = {trY2(J_opt):.6f}")

# 兩者同時最優?
print(f"\n    同時滿足 λ₁=φ^(1/3) 同 tr(Y²)=5 嘅 J:")
print(f"    λ₁ 需要 scale = {phi**(-1/3) * l1:.6f} (J→sJ)")
print(f"    但 tr(Y²) 需要 scale² → s² = 5/trY2(J0) → s = {math.sqrt(5/t0):.6f}")
s_l1 = phi**(-1/3)*l1  # J→sJ 令 λ₁ = φ^(1/3)
s_tr = math.sqrt(5/t0)
print(f"    s(λ₁) = {s_l1:.6f} vs s(tr) = {s_tr:.6f}")
check("兩閉合 scale 一致?", abs(s_l1 - s_tr) < 1e-3, f"({s_l1:.6f} vs {s_tr:.6f})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
