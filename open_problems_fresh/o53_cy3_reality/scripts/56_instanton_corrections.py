#!/usr/bin/env python3
"""
O53 路徑一: Worldsheet Instanton 非微擾修正測試
==================================================
Y_ijk(tree) = κ_ijk
Y_ijk(inst) = κ_ijk + Σ_C n_C · e^(-2π∫_C J) / (1 − e^(-2π∫_C J))

問題:
  1. J* 嘅 10.1% 誤差 (φ^(-n) 模型) 可唔可以用 e^(-S) 修正?
  2. τ (5.4%) / u (7.0%) 質量殘餘可唔可以用 instanton 解釋?
  3. e^(-2πφ^(-k/3)) 形式嘅候選修正

方法 (quark 離線, 用有效測試):
  - J* 模型: J*_i = A·φ^(-n_i) · (1 + ε_i)
  - ε_i 有冇 e^(-2πm) 結構?
  - 質量模型: m = m44·e^(δ+c·lnφ) · (1 + ε_inst)
  - ε_inst 有冇 e^(-2πφ^(-k/3)) 結構?
"""
import os, json, math, sys
import numpy as np

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
print("O53 路徑一: Instanton 修正測試")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# --- [1] J* 模型誤差分解 ---
print("\n[1] J* vs φ^(-n) 模型誤差:")
lnJ = np.log(J0)
exps = lnJ / math.log(phi)
n_int = np.round(exps)
residual = exps - n_int  # 殘餘 φ 指數
print(f"    φ 指數殘餘 (exps − round):")
print(f"    {np.array2string(residual, precision=3)}")
print(f"    mean|res| = {np.abs(residual).mean():.3f}")
print(f"    max|res| = {np.abs(residual).max():.3f}")
print(f"    → 殘餘就係 10.1% 誤差來源")

# --- [2] 殘餘有冇 e^(-2πm) 結構? ---
print("\n[2] 殘餘 vs e^(-2π·k):")
# J*_i = A·φ^(-n_i)·e^(ε_i), ε_i = residual·lnφ
eps = residual * math.log(phi)
print(f"    ε = residual·lnφ:")
print(f"    {np.array2string(eps, precision=4)}")
# ε 有冇 = -2π·k 結構?
for k in [1, 2, 3, 4]:
    t = -2*math.pi/k  # 太大
print(f"    lnφ = {math.log(phi):.4f}")
print(f"    ε 範圍: {eps.min():.4f} 至 {eps.max():.4f}")
print(f"    -2π×0.01 = {-2*math.pi*0.01:.4f}")
print(f"    → ε 量級 0.01-0.1, 唔係 2π 量級")

# --- [3] 候選: J* 直接有 e^(-2πq) 結構? ---
print("\n[3] J* = A·e^(-2πq_i)?")
# ln(J*) = ln(A) - 2πq → q = -ln(J*)/(2π)
q = -lnJ / (2*math.pi)
print(f"    q 範圍: {q.min():.3f} 至 {q.max():.3f}")
print(f"    q 值:")
print(f"    {np.array2string(q, precision=3)}")
# q 近有理?
q_frac = q - np.round(q*12)/12
print(f"    q 離 1/12 格點: mean|Δ| = {np.abs(q_frac).mean():.4f}")
print(f"    q 離 1/6 格點: mean|Δ| = {np.abs(q - np.round(q*6)/6).mean():.4f}")

# --- [4] 質量殘餘 instanton ---
print("\n[4] τ/u 質量殘餘:")
M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
lnphi = math.log(phi)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
print(f"    {'粒子':5s} {'m_obs':>9s} {'m_pred':>9s} {'誤差%':>7s} {'Δln':>8s}")
for k, m in SM.items():
    d = 44 - math.log(M_Pl/m)
    n = round(d)
    c = round((d-n)/lnphi*3)/3
    m_pred = m44 * math.exp(n + c*lnphi)
    err = (m_pred - m)/m*100
    dln = math.log(m_pred/m)
    print(f"    {k:5s} {m:9.5f} {m_pred:9.5f} {err:+6.1f}% {dln:+8.4f}")

# τ, u 殘餘
dln_tau = math.log(m44*math.exp(1 + (-2/3)*lnphi) / 1.777)
dln_u = math.log(m44*math.exp(-6 + 0*lnphi) / 0.0022)
print(f"\n    τ 殘餘 Δln = {dln_tau:+.4f}")
print(f"    u 殘餘 Δln = {dln_u:+.4f}")
print(f"    e^(-2π/44) = {math.exp(-2*math.pi/44):.4f} (Δln = {-2*math.pi/44:.4f})")
print(f"    e^(-2π/88) = {math.exp(-2*math.pi/88):.4f} (Δln = {-2*math.pi/88:.4f})")
print(f"    ln(φ)/4 = {lnphi/4:.4f}")
print(f"    ln(φ)/6 = {lnphi/6:.4f}")
print(f"    → τ Δln ≈ ? u Δln ≈ ?")

# 候選: Δln = -2π/N?
print(f"\n[5] Δln = -2π/N 候選:")
for N in [44, 88, 33, 66, 22]:
    print(f"    -2π/{N} = {-2*math.pi/N:+.4f}")
print(f"    τ Δln = {dln_tau:+.4f} → N = {-2*math.pi/dln_tau:.1f}")
print(f"    u Δln = {dln_u:+.4f} → N = {-2*math.pi/dln_u:.1f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
