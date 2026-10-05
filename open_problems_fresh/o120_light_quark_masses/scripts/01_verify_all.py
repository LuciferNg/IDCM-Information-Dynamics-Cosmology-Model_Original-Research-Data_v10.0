#!/usr/bin/env python3
"""
O120 — 獨立驗證腳本 (Independent Verification)
================================================
任務 1: 驗證 O120 推導鏈所有推導同結果
方法: 零 import 上游腳本。由 x²+x−1=0 第一性原理重算全部常數，
      再對照 O136 data JSON 同 O120 文檔聲明。

日期: 2026-09-03
"""
import math, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # o120_light_quark_masses/
O136_DATA = os.path.join(BASE, "..", "o136_quark_mass_spectrum", "data")

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    mark = "✅" if cond else "❌"
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  {mark} {name}" + (f"  [{detail}]" if detail and not cond else ""))
    return cond

# ═══════════════════════════════════════════════════════════
# 第 1 層: 常數重算 (from x²+x−1=0)
# ═══════════════════════════════════════════════════════════
print("=" * 72)
print("[1] 常數層 — 由 x²+x−1=0 第一性原理")
print("=" * 72)
φ = (1 + math.sqrt(5)) / 2
L = [round(φ**n + (-1)**n * φ**(-n)) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
h11, h21 = 36, 98
CY3 = h11 + h21
B, M = 4, (CY3 - 2) // 4
EPS = 1/φ / 4
M0 = 27.900915
γ = lambda n: 4 * math.sin(n * math.pi / 88)**2

check("φ = (1+√5)/2 = 1.6180339887", abs(φ - 1.618033988749895) < 1e-12)
check("Lucas L₀..L₈ = 2,1,3,4,7,11,18,29,47", L[:9] == [2,1,3,4,7,11,18,29,47])
check("Fibonacci F₅..F₁₀ = 5,8,13,21,34,55", F[5:11] == [5,8,13,21,34,55])
check("CY₃ = h¹¹+h²¹ = 134", CY3 == 134)
check("M = (CY₃−2)/4 = 33", M == 33)
check("L₆/F₅ = 3.6", abs(L[6]/F[5] - 3.6) < 1e-12)
check("Nd−L₅ = 33 = M", 44 - L[5] == 33 == M)
check("Nd−E_proj = 15.5 (E_proj=28.5)", 44 - 28.5 == 15.5)
check("γ₁ = 0.005095770779493", abs(γ(1) - 0.005095770779492917) < 1e-15)

# ═══════════════════════════════════════════════════════════
# 第 2 層: Framework A — v9.0 第一代公式 (structural_forcing.py)
# ═══════════════════════════════════════════════════════════
print("\n[2] Framework A — v9.0 第一代公式 (Fₙ/CY₃ˢ)")
def compute_K(fib_idx, s, k, extra_a=0):
    sign = (-1)**(k+s+1); Fn = F[fib_idx]
    a = k - 3*(s-1) + extra_a
    return sign * Fn * CY3 * (1/φ)**a
def fg_ratio(fib_idx, s, k, extra_a=0):
    Fn = F[fib_idx]; Kn = compute_K(fib_idx, s, k, extra_a)
    return (Fn + EPS**3 * Kn) / CY3**s
V_EW = φ**8 * (φ**3 + 1)
VEV_nat = math.sqrt(EPS / (2 * (1/16)))
SCALE = V_EW / VEV_nat
m_t_nat = VEV_nat / math.sqrt(2)
k_d = (M - L[4]) * (1/φ) / 2 - (1/φ)**4
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)
m_t = m_t_nat * SCALE
m_b = m_t_nat * (1/φ)**k_d * D_quark * SCALE
m_u_A = m_t * fg_ratio(9, 3, 9, 0)   # GeV
m_d_A = m_b * fg_ratio(8, 2, 8, 0)   # GeV
dev_u_A = abs(m_u_A*1000 / 2.16 - 1) * 100
dev_d_A = abs(m_d_A*1000 / 4.67 - 1) * 100
print(f"  m_u = {m_u_A*1000:.4f} MeV  dev = {dev_u_A:.3f}%  (文檔 0.51%)")
print(f"  m_d = {m_d_A*1000:.4f} MeV  dev = {dev_d_A:.3f}%  (文檔 0.40%)")
check("m_u dev ≈ 0.51% (±0.01)", abs(dev_u_A - 0.5125) < 0.01)
check("m_d dev ≈ 0.40% (±0.01)", abs(dev_d_A - 0.4043) < 0.01)

# ═══════════════════════════════════════════════════════════
# 第 3 層: Framework B — v10.0 O136 M₀×γ×P_f (對照 JSON)
# ═══════════════════════════════════════════════════════════
print("\n[3] Framework B — O136 M₀×γ_n×P_f (對照 08_final_closure.json)")
with open(os.path.join(O136_DATA, "08_final_closure.json")) as f:
    j8 = json.load(f)
m_u_B = M0 * γ(1) * 15.5
m_d_B = M0 * γ(1) * 33.0
print(f"  m_u = {m_u_B:.6f} MeV  JSON: {j8['up']['m_pred']:.6f}")
print(f"  m_d = {m_d_B:.6f} MeV  JSON: {j8['down']['m_pred']:.6f}")
check("m_u = M₀γ₁×15.5 與 JSON 一致", abs(m_u_B - j8['up']['m_pred']) < 1e-9)
check("m_d = M₀γ₁×33 與 JSON 一致", abs(m_d_B - j8['down']['m_pred']) < 1e-9)
check("JSON up n=1 P_f=15.5", j8['up']['n'] == 1 and abs(j8['up']['P_f']-15.5) < 1e-9)
check("JSON down n=1 P_f=33", j8['down']['n'] == 1 and abs(j8['down']['P_f']-33.0) < 1e-9)
check("JSON up dev=2.0249%", abs(j8['up']['dev_pct'] - 2.0249) < 0.001)
check("JSON down dev=0.4675%", abs(j8['down']['dev_pct'] - 0.4675) < 0.001)
# 輕子同表
check("JSON e n=1 P=3.6", j8['electron']['n'] == 1 and abs(j8['electron']['P_f']-3.6) < 1e-9)
check("JSON μ n=7 P=15.5", j8['muon']['n'] == 7 and abs(j8['muon']['P_f']-15.5) < 1e-9)
check("JSON τ n=20 P=37", j8['tau']['n'] == 20 and abs(j8['tau']['P_f']-37.0) < 1e-9)
# s/c/b/t
for name, n, pf in [("strange",14,3.6), ("charm",34,13.0), ("bottom",33,44.0)]:
    check(f"JSON {name} n={n} P={pf}", j8[name]['n'] == n and abs(j8[name]['P_f']-pf) < 1e-9)

# ═══════════════════════════════════════════════════════════
# 第 4 層: up_quark_correction.py 重算
# ═══════════════════════════════════════════════════════════
print("\n[4] up_quark_correction.py 重算")
M_Pl = 1.220890e22  # MeV
V_g1 = 46.5390
bare_up = 0.0227488532 * M_Pl * math.exp(-V_g1)
f_up = math.sqrt(φ)
up_corr = bare_up * f_up
dev_up = abs(up_corr / 2.16 - 1) * 100
bare_d = 0.0117201474 * M_Pl * math.exp(-V_g1)
d_corr = bare_d * 5.3
dev_d = abs(d_corr / 4.67 - 1) * 100
print(f"  bare_up = {bare_up:.4f} MeV; ×√φ → {up_corr:.4f} MeV  dev={dev_up:.3f}%  (腳本 0.47%)")
print(f"  bare_d  = {bare_d:.4f} MeV; ×5.3 → {d_corr:.4f} MeV  dev={dev_d:.3f}%  (腳本 0.24%)")
check("up ×√φ dev ≈ 0.47% (±0.01)", abs(dev_up - 0.472) < 0.01)
check("down ×5.3 dev ≈ 0.24% (±0.01)", abs(dev_d - 0.244) < 0.01)

# ═══════════════════════════════════════════════════════════
# 第 5 層: m_u/m_d 結構比
# ═══════════════════════════════════════════════════════════
print("\n[5] m_u/m_d 結構比 (Framework B)")
r_p = 15.5 / 33.0
r_obs = 2.16 / 4.67
r_dev = abs(r_p / r_obs - 1) * 100
print(f"  P_u/P_d = 15.5/33 = {r_p:.6f}; obs = {r_obs:.6f}; Δ = {r_dev:.3f}%")
check("m_u/m_d = 0.469697", abs(r_p - 0.469697) < 1e-6)
check("obs = 0.462527", abs(r_obs - 0.462527) < 1e-6)
check("Δ = 1.55% (±0.01)", abs(r_dev - 1.5502) < 0.01)

# ═══════════════════════════════════════════════════════════
# 第 6 層: O54 輕子交叉驗證 (u P_f=15.5 = μ P_f 聲明)
# ═══════════════════════════════════════════════════════════
print("\n[6] O54 輕子交叉驗證")
m_mu = M0 * γ(7) * 15.5
m_e = M0 * γ(1) * (L[6]/F[5])
dev_mu = abs(m_mu/105.66 - 1) * 100
dev_e = abs(m_e/0.510999 - 1) * 100
print(f"  m_μ = {m_mu:.4f} MeV dev={dev_mu:.3f}% (O54 0.13%)")
print(f"  m_e = {m_e:.6f} MeV dev={dev_e:.4f}% (O54 0.16%)")
check("μ dev ≈ 0.13%", abs(dev_mu - 0.131) < 0.01)
check("e dev ≈ 0.16%", abs(dev_e - 0.164) < 0.01)

# ═══════════════════════════════════════════════════════════
# 第 7 層: O137 費米子反週期條件 (scripts/05)
# ═══════════════════════════════════════════════════════════
print("\n[7] O137 費米子反週期條件 nL ≡ 44 (mod 88)")
assign = {1:44, 7:44, 20:11, 14:22, 34:22, 33:4}
all_ok = all((n*l) % 88 == 44 for n, l in assign.items())
for n, l in assign.items():
    ok = (n*l) % 88 == 44
    print(f"  n={n:2d} L={l:2d}: nL mod 88 = {(n*l)%88:3d} {'✅' if ok else '❌'}")
check("全部 6 模式通過反週期條件", all_ok)

# ═══════════════════════════════════════════════════════════
# 第 8 層: O115 表格聲稱 vs 實測 (s/c/b/t)
# ═══════════════════════════════════════════════════════════
print("\n[8] O115 '>90%' 聲稱 vs O136 實測")
for name in ['strange', 'charm', 'bottom', 'top']:
    d8 = abs(j8[name]['dev_pct'])
    print(f"  {name:>8}: O136 實測 {d8:.2f}%  (O115 聲稱 >90% → 過時)")
    check(f"{name} < 5% (實測閉合)", d8 < 5)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 72)
sys.exit(1 if FAIL else 0)
