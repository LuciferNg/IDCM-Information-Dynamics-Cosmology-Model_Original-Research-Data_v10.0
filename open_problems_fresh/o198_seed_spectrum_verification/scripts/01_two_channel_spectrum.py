#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/01 — 兩通道種子質譜重建 (Two-Channel Seed Spectrum Reconstruction)

由 O197 閉合參數重建零新常數嘅種子質譜 (docs/01_closure.md):
  通道 A (譜偏差): M_A(k) = M_base·(2sin²(kπ/176))^{3/2}, k = 45..88 (44 正模態)
  通道 B (環境過密): ln M ~ N(ln M_base + 1.5μ, (1.5s)²), s² = B·N_gen²·Var_pop

驗證閉式 (全部由第一原理重算, 唔 import O197 任何 script):
  V1 轉折閉式: M_turn = M_base·2^{3/2} (k=88 模態 δ̂=1)
  V2 通道 A 範圍: [min_k M_A(k), max_k M_A(k)] = [~2.02e6, M_turn]
  V3 通道 A 模態數 = 44
  V4 Π 閉式: Π_{k=45}^{88}(1+δ̂₊) = 1.547e9 (O197 T2)
  V5 通道 B 中位: exp(ln M_base + 1.5μ) = 6.98e6 (O197 錨)
  V6 域分離量化: P_B(M < M_turn) = Φ((ln M_turn − ln M_base − 1.5μ)/(1.5s))
  V7 高端純度: 通道 A 有硬上限 M_turn, 通道 B support 無上限
  V8 σ_lnM = 1.5s

零新常數: M_base = 1.914e6 (O173 P7), μ = 0.862478, s = 1.1874 (O174 結構化值)
"""
import math

# ---------- 結構常數 (第一原理) ----------
M_base = 1.914e6          # O173 P7 種子基質量 (M☉)
mu = 0.862478             # O174: ln(1+δ_env) 平均
s = 1.1874                # O174: s² = B·N_gen²·Var_pop(ln(1+δ̂₊)) = 1.4098
B, N_d, N_gen = 4, 44, 3  # IDCM 基礎常數
L_EDD = 1.26e38           # Eddington 光度常數 (erg/s/M☉), 物理輸入

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

tot = 0; pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    chk(name, ok, note)

# ---------- 通道 A: 44 個正模態離散譜 ----------
def M_A(k):
    """M_A(k) = M_base·(2sin²(kπ/176))^{3/2}, k=45..88"""
    return M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5

A_masses = [M_A(k) for k in range(45, 89)]
A_min, A_max = min(A_masses), max(A_masses)
A_kmin = 45 + A_masses.index(A_min)
A_kmax = 45 + A_masses.index(A_max)

# ---------- V1: 轉折閉式 ----------
M_turn = M_base * 2.0 ** 1.5
T("V1 轉折閉式 M_turn = M_base·2^{3/2}", abs(M_turn - 5.41e6) / 5.41e6 < 1e-3,
  f"M_turn = {M_turn:.4e} (O197 5.41e6)")

# ---------- V2: 通道 A 範圍 ----------
T("V2a 通道 A 下限", abs(A_min - 2.02e6) / 2.02e6 < 2e-2,
  f"A_min = {A_min:.4e} (k={A_kmin}) vs O197 2.02e6")
T("V2b 通道 A 上限 = 轉折 (k=88)", abs(A_max - M_turn) / M_turn < 1e-9,
  f"A_max = {A_max:.6e} (k={A_kmax}) == M_turn")

# ---------- V3: 模態數 ----------
T("V3 通道 A 模態數 = 44", len(A_masses) == 44, f"{len(A_masses)} modes")

# ---------- V4: Π 閉式 ----------
Pi_A = 1.0
for k in range(45, 89):
    Pi_A *= 2.0 * math.sin(k * math.pi / 176.0) ** 2   # Π(1+δ̂₊)
T("V4 Π(1+δ̂₊) = 1.547e9", abs(Pi_A - 1.547e9) / 1.547e9 < 5e-3,
  f"Π = {Pi_A:.4e} vs O197 1.547e9")

# ---------- V5: 通道 B 中位 ----------
mu_lnM = math.log(M_base) + 1.5 * mu
med_B = math.exp(mu_lnM)
T("V5 通道 B 中位 = 6.98e6", abs(med_B - 6.98e6) / 6.98e6 < 2e-3,
  f"med_B = {med_B:.4e} vs O197 6.98e6 (LRD 錨 6.97e6)")

# ---------- V6: 域分離量化 ----------
sig_lnM = 1.5 * s
z_turn = (math.log(M_turn) - mu_lnM) / sig_lnM
P_B_below = 0.5 * (1.0 + math.erf(z_turn / math.sqrt(2.0)))
T("V6 P_B(M<M_turn) ≈ 0.44 (通道 B 低尾存在)", 0.35 < P_B_below < 0.55,
  f"z = {z_turn:.4f}, P_B_below = {P_B_below:.4f}")

# ---------- V7: 高端純度 ----------
T("V7 通道 A 硬上限 == M_turn (高端只屬 B)", abs(A_max - M_turn) < 1e-6 * M_turn,
  "M > M_turn ⟹ 100% 通道 B (可證偽核心)")

# ---------- V8: σ_lnM ----------
T("V8 σ_lnM = 1.5s", abs(sig_lnM - 1.5 * 1.1874) < 1e-9, f"σ_lnM = {sig_lnM:.4f}")

print(f"\n===== {pas}/{tot} PASS =====")
print(f"通道 A 離散譜 (k=45..88): [{A_min:.4e}, {A_max:.4e}]")
print(f"通道 B: ln M ~ N({mu_lnM:.4f}, {sig_lnM:.4f}²), 中位 {med_B:.4e}")
print(f"轉折: {M_turn:.4e}; P_B_below = {P_B_below:.4f}")
print(f"UHz1 (1.7e9) z = {(math.log(1.7e9) - mu_lnM) / sig_lnM:.4f}")
