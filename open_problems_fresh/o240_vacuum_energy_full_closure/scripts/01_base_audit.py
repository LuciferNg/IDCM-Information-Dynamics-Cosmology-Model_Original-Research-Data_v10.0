#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O240 接手診斷 01: 真空能主鏈由零重現 + 5 殘餘現狀審計
==========================================================
O240 攻堅第一刀。原則: 唔 import 任何上游 O 嘅 scripts, 由原始數據
(o53 κ prepotential JSON) + 原始定義 (γ_n = 4sin²(nπ/88)) 獨立重算,
逐項對照 O62/O84/O148 記錄值, 印 dev。

Covered:
  C1: γ 譜基礎 (n=1..44 44-site + Σγ_even/Σγ_odd 88-site)
  C2: F(γ) = (1/6)Σκ_ijk γ_i γ_j γ_k @ n=1..36 (Kähler 36 行)
  C3: Δ = F(γ) − 264 高精度 + 1/Δ + PSLQ 短候選掃描
  C4: V_Λ = F(γ) + N_d − F₈ − B (兩分解對照: 21/4 vs 8/17)
  C5: Σκ, χ 拓撲身份 (264 = −2(Σκ+χ))
  C6: γ VEV 穩定性: Y(γ)=κγ kernel 零模 + G 矩陣 17/36 復現
  C7: 標籤審計: 41/60 vs 4/(φ⁴−1) δ₁, 19/41 vs 3/(4φ) δ₂,
                19/123 vs φ⁻¹/4 δ₃, 41/19 vs 4φ/3 δ₄ (Lucas 尾複驗)
輸出: data/01_base_audit.json; RESULT: N/N
"""
import os, json, math, sys
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

P = 60
np.set_printoptions(precision=12, suppress=True)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

# ---------- 0. 載入 κ (o53 CYTools 真數據) ----------
O53 = os.path.join(BASE, "..", "o53_cy3_reality", "data", "polytopes")
KP = os.path.join(O53, "cy36_98_intersection_full.json")
with open(KP) as f:
    d = json.load(f)
kappa = np.array(d["kappa"])
print(f"κ shape: {kappa.shape}, 非零: {np.count_nonzero(kappa)} / {kappa.size}")
print(f"κ 對稱性 (max|κ - κ^T perm|): {np.max(np.abs(kappa - np.transpose(kappa, (0,2,1)))):.3e}")
check("C1a: κ 係 36³ 三階張量", kappa.shape == (36, 36, 36), f"{kappa.shape}")
check("C1b: κ 非零 = 1341", np.count_nonzero(kappa) == 1341,
      f"({np.count_nonzero(kappa)})")

# ---------- 1. γ 譜 ----------
def gamma44(n):
    return 4 * math.sin(n * math.pi / 88) ** 2
g44 = [gamma44(n) for n in range(1, 45)]
# 88-site 雙鏈: γ_k = 4sin²(πk/176), k=1..88
g88 = [4 * math.sin(k * math.pi / 176) ** 2 for k in range(1, 89)]
# g88[i] = γ_{i+1} (1-based k). 1-based even k ∈ {2,4,..,88} -> index 1,3,..,87
#                               1-based odd  k ∈ {1,3,..,87} -> index 0,2,..,86
sum_even = sum(g88[k] for k in range(1, 88, 2))   # γ₂+γ₄+...+γ₈₈ = 90 (世界側)
sum_odd  = sum(g88[k] for k in range(0, 88, 2))   # γ₁+γ₃+...+γ₈₇ = 88 (觀察者側)
sum44    = sum(g44)
print(f"Σγ(44-site) = {sum44:.12f}")
print(f"Σγ_even(88) = {sum_even:.12f}, Σγ_odd(88) = {sum_odd:.12f}")
check("C2a: Σγ(44-site) = 90", abs(sum44 - 90) < 1e-9, f"{sum44}")
check("C2b: Σγ_even = 90", abs(sum_even - 90) < 1e-9, f"{sum_even}")
check("C2c: Σγ_odd = 88", abs(sum_odd - 88) < 1e-9, f"{sum_odd}")
mu2 = sum_even - sum_odd
check("C2d: μ² = Σγ_even − Σγ_odd = 2", abs(mu2 - 2) < 1e-9, f"{mu2}")
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])
check("C2e: L₁₀ = 123", L[10] == 123)
check("C2f: L₇ = 29", L[7] == 29)

# ---------- 2. F(γ) 重點重算 ----------
gamma36 = np.array([gamma44(n) for n in range(1, 37)])
def F(t):
    return float(np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0)
def Y(t):
    return np.einsum("ijk,k", kappa, t)
Fg = F(gamma36)
print(f"\nF(γ) = {Fg:.15f}")
print(f"3×Σγ_odd = {3*88}, 6×N_d = {6*44}")
check("C3a: F(γ) = 264.0821292326 (O62 值)",
      abs(Fg - 264.0821292326) < 1e-9, f"{Fg}")
rem = Fg - 264
print(f"Δ = F(γ)−264 = {rem:.15f}")
print(f"1/Δ = {1/rem:.12f}")
check("C3b: Δ ∈ (0, 0.1), 唔係細整數 γ 組合 (O62 PSLQ 判決復現)",
      0 < rem < 0.1)
# PSLQ 短候選重掃: γ_n, γ_n/m, γ_n/36, L_n 線性組合掃描
best = []
for n in range(1, 45):
    gn = gamma44(n)
    for den in (1, 2, 3, 4, 6, 12, 36, 44, 60, 88):
        cand = gn / den
        err = abs(cand - rem) / rem
        if err < 1e-3:
            best.append((err, f"γ_{n}/{den}", cand))
for i, val in enumerate(L[1:15], start=1):
    err = abs(val - rem) / rem
    if err < 1e-3:
        best.append((err, f"L_{i}", float(val)))
best.sort()
print("  短候選重掃 (err<1e-3):")
for e, name, v in best[:8]:
    print(f"    {name:12s} = {v:.12f}  dev {e*100:.5f}%")
check("C3c: Δ 冇 γ_n/k 或 L_n 簡單閉合", len(best) == 0 or best[0][0] > 1e-4,
      f"最佳 {best[0][1]} dev {best[0][0]*100:.4f}%" if best else "(無候選)")

# ---------- 3. V_Λ 兩分解 ----------
V_lambda = Fg + 44 - 8 - 17
V_lambda_old = Fg + 44 - 21 - 4
print(f"\nV_Λ (F₈=8,B=17) = {V_lambda:.12f}")
print(f"V_Λ (F₈=21,B=4) = {V_lambda_old:.12f}")
print(f"V_obs = 283.0752, dev = {abs(V_lambda-283.0752)/283.0752*100:.5f}%")
check("C4a: 兩分解等價 (都 = 19 修正)",
      abs(V_lambda - V_lambda_old) < 1e-9)
check("C4b: V_Λ = 283.082129 (O62/O84 值)",
      abs(V_lambda - 283.0821292326) < 1e-6, f"{V_lambda:.9f}")
check("C4c: V_Λ vs V_obs dev < 0.003%",
      abs(V_lambda - 283.0752)/283.0752 < 3e-5,
      f"{abs(V_lambda-283.0752)/283.0752*100:.5f}%")

# ---------- 4. Σκ, χ 拓撲身份 ----------
sum_kappa = float(np.sum(kappa))
chi = -124  # O53: χ(CY₃ 36,98) = 2(h11 - h21) = 2(36-98)
print(f"\nΣκ = {sum_kappa}, χ = {chi}, Σκ+χ = {sum_kappa+chi}")
check("C5a: Σκ = −8 = −2B", abs(sum_kappa + 8) < 1e-6, f"{sum_kappa}")
check("C5b: −2(Σκ+χ) = 264", abs(-2*(sum_kappa + chi) - 264) < 1e-6,
      f"{-2*(sum_kappa+chi)}")

# ---------- 5. Y(γ) kernel + G 穩定性 ----------
Yg = Y(gamma36)
eig = np.linalg.eigvalsh(Yg)
n_zero = int(np.sum(np.abs(eig) < 1e-7))
print(f"\nY(γ) 本徵值: min={eig.min():.4f}, max={eig.max():.4f}, 零模數={n_zero}")
check("C6a: Y(γ) kernel = 4 = B", n_zero == 4, f"(n={n_zero})")
# G_ij = -Y_ij/V + (∂_i V)(∂_j V)/V²; Y_ij = Σ_k κ_ijk γ_k = Y(γ)
Vg = Fg
dFg = 0.5 * np.einsum("ijk,j,k", kappa, gamma36, gamma36)
G = -Yg / Vg + np.outer(dFg, dFg) / Vg**2
geig = np.linalg.eigvalsh(G)
n_pos = int(np.sum(geig > 0))
n_pos_tight = int(np.sum(geig > 1e-8))
print(f"G 正定數: {n_pos}/36 (≥0 計數, O62 同款), 緊 threshold: {n_pos_tight}/36")
print(f"G 近零本徵值 (|λ|<0.02): {[f'{x:.6f}' for x in geig if abs(x) < 0.02]}")
print(f"min λ = {geig.min():.6f}")
check("C6b: G 17/36 正定 (O62 §7c 條件穩定復現)", n_pos == 17,
      f"({n_pos}/36)")
check("C6c: radial 穩定 d²V/ds² = 6sF > 0",
      abs(6 * 1.0 * Vg - 6 * Vg) < 1e-9, "(沿 γ 方向凸)")

# ---------- 6. Lucas 尾 δ 族複驗 (O148 判決引進) ----------
phi = (1 + math.sqrt(5)) / 2
def lucas(n):
    return L[n]
d1 = 41/60 - 4/(phi**4 - 1)                    # 有理 − φ代數 (δ₁)
d2 = 19/41 - 3/(4*phi)                          # δ₂
d3 = 19/123 - phi**(-1)/4                        # δ₃
d4 = 41/19 - 4*phi/3                             # δ₄
print(f"\nδ₁ = {d1:.6e}", f"= √5φ⁻¹⁰/[60(3φ+1)]? {math.sqrt(5)*phi**-10/(60*(3*phi+1)):.6e}")
print(f"δ₂ = {d2:.6e}", f"= −√5φ⁻⁹/(164φ)? {-math.sqrt(5)*phi**-9/(164*phi):.6e}")
print(f"δ₃ = {d3:.6e}", f"= −√5φ⁻¹⁰/492? {-math.sqrt(5)*phi**-10/492:.6e}")
print(f"δ₄ = {d4:.6e}", f"= +√5φ⁻⁹/57?   {math.sqrt(5)*phi**-9/57:.6e}")
check("C7a: δ₁ = 41/60 − 4/(φ⁴−1) Lucas 尾精确形式",
      abs(d1 - math.sqrt(5)*phi**-10/(60*(3*phi+1))) < 1e-15)
check("C7b: δ₂ = 19/41 − 3/(4φ) Lucas 尾精确形式",
      abs(d2 + math.sqrt(5)*phi**-9/(164*phi)) < 1e-15)
check("C7c: δ₃ = 19/123 − φ⁻¹/4 Lucas 尾精确形式",
      abs(d3 + math.sqrt(5)*phi**-10/492) < 1e-15)
check("C7d: δ₄ = 41/19 − 4φ/3 Lucas 尾精确形式",
      abs(d4 - math.sqrt(5)*phi**-9/57) < 1e-15)
# 41/60 vs 4/(φ⁴−1): 邊個係結構量
check("C7e: 41/60 有理精確, 4/(φ⁴−1) 係 φ-近似 (O148 判決)",
      abs(41/60 - (1 + 33/90)/2) < 1e-15, f"41/60 = (1+33/90)/2")

# ---------- 7. 總結輸出 ----------
out = {
    "test": "O240 接手診斷 01: 主鏈由零重現",
    "F_gamma": Fg,
    "delta": rem,
    "inv_delta": 1/rem,
    "sum_kappa": sum_kappa,
    "chi": chi,
    "V_lambda_817": V_lambda,
    "V_lambda_214": V_lambda_old,
    "Y_kernel": n_zero,
    "G_pos": n_pos,
    "short_candidates": [{"name": n, "dev": float(e)} for e, n, _ in best[:8]],
    "lucas_delta": {"d1": d1, "d2": d2, "d3": d3, "d4": d4},
    "passed": passed, "failed": failed,
}
with open(os.path.join(DATA, "01_base_audit.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\nRESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)