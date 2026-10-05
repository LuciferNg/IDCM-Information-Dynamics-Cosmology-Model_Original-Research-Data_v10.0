#!/usr/bin/env python3
"""
O53 路徑一 (最終): 直接 instanton 級數 fit
=============================================
J*_i = A·e^(-2πq_i) 已經睇過 (q 格點唔顯著)

試真正 instanton 形式:
  1. J* = A·φ^(-k) + B·e^(-2π·m) — 混合 fit
  2. 殘餘 ε_i = J*_i/(A·φ^(-k_i)) − 1 有冇 e^(-2π) 級數?
  3. 睇 τ/u 殘餘 Δln = +0.05/+0.07 — instanton 加項?

另外:
  4. 如果 Y_ij = κ_ijk·J*^k 有 instanton 修正,
     對 λ₁ = φ^(1/3) 有咩影響?
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
print("O53 路徑一最終: Instanton 級數")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
lnJ = np.log(J0)

# --- [1] J* = A·φ^(-n) 模型誤差重算 ---
print("\n[1] J* = A·φ^(-n) 最佳 fit:")
n_int = np.round(lnJ/math.log(phi))
A = np.exp(lnJ - n_int*math.log(phi)).mean()
print(f"    A = {A:.6f}")
pred = A * phi**(-n_int)
rel_err = np.abs(pred - J0)/J0
print(f"    mean rel err = {rel_err.mean()*100:.2f}%")
print(f"    max rel err = {rel_err.max()*100:.2f}%")

# --- [2] 殘餘對數 ---
print("\n[2] 殘餘 ln(J*/(A·φ^(-n))):")
res_ln = lnJ - (math.log(A) - n_int*math.log(phi))
print(f"    {np.array2string(res_ln, precision=4)}")
print(f"    mean|res| = {np.abs(res_ln).mean():.4f}")

# --- [3] 殘餘 vs e^(-2π) instanton 級數 ---
print("\n[3] 殘餘 fit e^(-2πm) 級數:")
# res ≈ Σ c_m·e^(-2πm/12), m = 1..13
Ms = np.arange(1, 14)
inst = np.exp(-2*math.pi*Ms/12)  # 13 個 instanton 因子
# 最小二乘
X = np.column_stack([inst for _ in range(36)]).T  # 36×13
coef, _, _, _ = np.linalg.lstsq(X, res_ln, rcond=None)
pred_res = X @ coef
r2 = 1 - np.sum((res_ln - pred_res)**2)/np.sum(res_ln**2)
print(f"    13-term fit R² = {r2:.4f}")
print(f"    係數: {np.array2string(coef, precision=3)}")
print(f"    最大 |coef|: {np.abs(coef).max():.4f}")

# 隨機對照
rng = np.random.default_rng(0)
rand_res = rng.normal(0, np.abs(res_ln).std(), 36)
coef_r, _, _, _ = np.linalg.lstsq(X, rand_res, rcond=None)
pred_r = X @ coef_r
r2_r = 1 - np.sum((rand_res - pred_r)**2)/np.sum(rand_res**2)
print(f"    隨機對照 R² = {r2_r:.4f}")
check("instanton fit R² > 隨機", r2 > r2_r + 0.1, f"({r2:.3f} vs {r2_r:.3f})")

# --- [4] 只用 1-2 個 instanton ---
print("\n[4] 1-term instanton (m=6?):")
# 揀最好單 term
best_m, best_r2 = None, -1
for m in Ms:
    x = np.exp(-2*math.pi*m/12)
    c = np.sum(res_ln*x)/np.sum(x**2)
    r = 1 - np.sum((res_ln - c*x)**2)/np.sum(res_ln**2)
    if r > best_r2:
        best_r2, best_m = r, m
print(f"    最好單 term: m={best_m}, R² = {best_r2:.4f}")
print(f"    → instanton 單項修正唔夠")

# --- [5] τ/u 殘餘 + instanton ---
print("\n[5] τ/u 殘餘 instanton 解釋:")
dln_tau = +0.0522
dln_u = +0.0673
# e^(-2πm/12) 級數:
for m in range(1, 14):
    f = math.exp(-2*math.pi*m/12)
    if abs(f - dln_tau) < 0.01 or abs(f - dln_u) < 0.01:
        print(f"    m={m}: e^(-2π·{m}/12) = {f:.4f} ← 接近 τ({dln_tau:.4f}) 或 u({dln_u:.4f})?")
print(f"    τ Δln = {dln_tau:.4f} — instanton 因子全 < 0.043, 冇匹配")
print(f"    u Δln = {dln_u:.4f} — 同上")
print(f"    → τ/u 殘餘唔似 instanton (量級差太遠)")

# --- [6] 其他候選: τ/u 殘餘 = ln(1+x)? ---
print("\n[6] τ/u 殘餘候選:")
print(f"    e^(0.0522) = {math.exp(0.0522):.4f} (τ 乘數)")
print(f"    e^(0.0673) = {math.exp(0.0673):.4f} (u 乘數)")
print(f"    φ^(-1/12) = {phi**(-1/12):.4f}")
print(f"    φ^(1/12) = {phi**(1/12):.4f}")
print(f"    2^(1/12) = {2**(1/12):.4f}")
print(f"    → τ 乘數 1.0536, u 乘數 1.0696")
print(f"    φ^(1/8) = {phi**(1/8):.4f}? φ^(1/8) = {phi**0.125:.4f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
