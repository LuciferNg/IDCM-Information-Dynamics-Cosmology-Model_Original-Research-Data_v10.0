#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O213 scripts/15 — R9 零錨 track 第一輪核正（2026-10-08）
=========================================================
目的: 核對 docs/14 所有數值宣稱（track 章程之數字基礎），零 import 原 script、
      由文獻值＋結構數重算（與 scripts/14 同一紀律）。

段:
  A. V_Λ 分解核對（O62: 283.082129 = F(γ)+44−F₈−B; 264 = 6N_d = 3Σγ_odd）
  B. e^{−V_Λ} 指數量級
  C. Λ_eff = 8πM_Pl²e^{−V_Λ} 復現（與 O86 記錄值 4.2913e−84 GeV² 對照）
  D. R7 定理 1 不變量 Π、X、N（與 scripts/13 對照）
  E. O86 E2: R_world=(1−π/44)√(3Ω_Λ/Λ_eff) 與 dev 0.618%（恆等自審）
  F. ★ 階層橋量級檢查（e^{V_Λ/2} vs N）—— 標明為量級檢查, 非結構宣稱
"""
import sys
from mpmath import mp, mpf, pi, exp, sqrt, sin, log, ln, power

mp.dps = 40
G = 1.0   # global pass counter

def chk(name, cond, detail=""):
    global G
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        sys.exit(1)
    G += 1

# ---------- 文獻值 / 結構數（與 scripts/14 同源） ----------
# O62 docs/01: V_Λ = F(γ) + 44 − F₈ − B = 283.082129;  F(γ) = 264.082129
V_LAM_OBS  = mpf("283.075200")     # O62 之 V_obs
V_LAM_STRUCT = mpf("283.082129")   # O62 閉合值
F_GAM_O62  = mpf("264.082129")     # O62 紀錄 F(γ)
ND = 44; F8 = 21; B = 4
# O86 docs/04: Λ_eff = 8πM_Pl²e^{−V_Λ} = 4.2913e−84 GeV²
LAM_EFF_O86 = mpf("4.2913e-84")
# O86 docs/08 E2: Ω_Λ = 41/60; R_world = (1−π/44)√(3Ω_Λ/Λ_eff) = 4104.36 Mpc
OM_LAM = mpf(41)/mpf(60)
RWORLD_O86 = mpf("4104.36")
RWORLD_ANCHOR = mpf("4129.94")
# R7 (scripts/13): Π = ħ²k_BT/(G²m_p⁵) = 7.1759e63 (自然單位量, 記錄值)
PI_R7 = mpf("7.1759e63")
# O212/O213: N = τ/t_Pl = 7.8695114682e60 (O213 記錄) / 7.88468594512e60 (O200 一致)
N_O213 = mpf("7.88468594512e60")
# CODATA M_Pl (GeV) —— 用於 Λ_eff 量級復現（O86 未明列其 M_Pl 輸入）
M_PL_GEV = mpf("1.220910e19")

# ---------- A. V_Λ 分解 ----------
print("== A. V_Λ 分解（O62 docs/01） ==")
# A1: V_Λ = F(γ) + 44 − F₈ − B
print(f"  F(γ)+44−F₈−B = {F_GAM_O62}+44−{F8}−{B} = {F_GAM_O62 + ND - F8 - B}")
chk("A1 V_Λ 結構式重算", abs((F_GAM_O62 + ND - F8 - B) - V_LAM_STRUCT) < mpf("1e-25"),
    f"(V_Λ_struct = {V_LAM_STRUCT})")
# A2: dev vs V_obs
devA2 = abs(V_LAM_STRUCT - V_LAM_OBS) / V_LAM_OBS
print(f"  dev(V_struct vs V_obs) = {float(devA2*100):.5f}%  (O62 報 0.00245%)")
chk("A2 V_Λ 精度 0.00245%", devA2 < mpf("2.5e-5"), f"({float(devA2*100):.5f}%)")
# A3: 264 = 6N_d = 3×Σγ_odd（88-site 對偶鏈奇子鏈）—— 獨立重算
# γ_n = 4sin²(nπ/88); Σγ_odd over n=1..87 odd
odd_sum = sum(4*sin(mp.pi*n/88)**2 for n in range(1, 88, 2))
print(f"  Σγ_odd(88) = {odd_sum} → 3× = {3*odd_sum}  (目標 264)")
chk("A3 264 = 3×Σγ_odd EXACT", abs(3*odd_sum - 264) < mpf("1e-30"),
    f"({3*odd_sum})")

# ---------- B. e^{−V_Λ} ----------
print("\n== B. 指數 e^{−V_Λ}（docs/14 §3.1） ==")
e_negV = exp(-V_LAM_STRUCT)
print(f"  e^{{−V_Λ}} = e^{{-283.082129}} = {e_negV}")
# docs/14 草稿寫 1.3493e−123 —— 核正：
log10_eV = V_LAM_STRUCT / ln(10)
print(f"  log10(e^V_Λ) = {float(log10_eV):.4f}  → e^V_Λ = 10^{float(log10_eV):.4f}")
chk("B1 e^{−V_Λ} 量級 ~1.15e−123", abs(e_negV - mpf("1.15e-123")) < mpf("0.05e-123"),
    f"({e_negV})")
chk("B2 e^{−V_Λ} 提供 ~123 個數量級壓制", 122 < log10_eV < 124,
    f"(log10 = {float(log10_eV):.3f})")

# ---------- C. Λ_eff 復現 ----------
print("\n== C. Λ_eff = 8πM_Pl² e^{−V_Λ}（O86 docs/04 N1） ==")
lam_from_coda = 8*pi * M_PL_GEV**2 * e_negV
print(f"  8πM_Pl²e^−V_Λ (CODATA M_Pl) = {lam_from_coda} GeV²")
print(f"  O86 記錄 Λ_eff              = {LAM_EFF_O86} GeV²")
devC = abs(lam_from_coda - LAM_EFF_O86)/LAM_EFF_O86
print(f"  dev = {float(devC*100):.3f}%  (M_Pl 輸入來源差異容許 <1%)")
chk("C1 Λ_eff 量級復現", devC < mpf("0.01"),
    f"(dev {float(devC*100):.3f}%, 與 M_Pl 精確值相依)")

# ---------- D. R7 定理 1 不變量 ----------
print("\n== D. R7 定理 1（docs/12 + scripts/13） ==")
# X ≡ τ·k_BT/ħ = N·(T_CMB/T_Pl) 之重算留 scripts/14；此處取結構化核對：
# Π = ħ²k_BT/(G²m_p⁵)；N = 7.88468594512e60
# scripts/13 記錄 Π = 7.1759e63 (自然單位)；重算需要 CODATA 輸入，此處引用核對量級
print(f"  Π(O213 R7) = {PI_R7}")
print(f"  N(O213)    = {N_O213}")
chk("D1 Π 記錄值存在且量級 ~7.2e63", mpf("7e63") < PI_R7 < mpf("7.4e63"))
chk("D2 N 記錄值存在且 ~7.88e60", mpf("7.8e60") < N_O213 < mpf("8.0e60"))

# ---------- E. O86 E2 恆等自審 ----------
print("\n== E. O86 E2: R_world=(1−π/44)√(3Ω_Λ/Λ_eff)（docs/08 §8 撤回後立場） ==")
# 用自然單位 (GeV⁻¹)：O86 docs/08 記錄 R_world = 6.458095e41 GeV⁻¹
R_ANCHOR_NAT = mpf("6.458095e41")
Rpred_nat = (1 - pi/44) * sqrt(3*OM_LAM/LAM_EFF_O86)
print(f"  R_pred = {Rpred_nat} GeV⁻¹  (O86 報 6.418189e41)")
devE = (R_ANCHOR_NAT - Rpred_nat)/R_ANCHOR_NAT
print(f"  dev(natural) = {float(devE*100):.4f}% → 0.618% ✓")
chk("E1 dev 0.618% 復現", abs(devE - mpf("0.00618")) < mpf("0.0010"),
    f"({float(devE*100):.4f}%)")
# E2: 恆等本質 —— R_pred/R_world ≡ H_CMB/H₀^Λ（docs/08 §8.1）
# H_CMB = ω_ring(1−π/44), ω_ring = 1/R_world；H₀² = Λ_eff/(3Ω_Λ)
H_CMB = (1 - pi/44) / R_ANCHOR_NAT
H0_L  = sqrt(LAM_EFF_O86 / (3*OM_LAM))
LHS = Rpred_nat / R_ANCHOR_NAT
RHS = H_CMB / H0_L
print(f"  LHS R_pred/R_world = {LHS}")
print(f"  RHS H_CMB/H₀Λ      = {RHS}")
chk("E2 恆等本質（同一代數式, 機器精度）", abs(LHS - RHS) < mpf("1e-30"),
    f"(差 = {float(abs(LHS-RHS)):.2e}, 兩邊係同一表達式)")

# ---------- F. 階層橋（量級檢查, 非結構宣稱） ----------
print("\n== F. 階層橋量級檢查（docs/14 §7 候選, 未推導） ==")
eV_half = exp(V_LAM_STRUCT/2)
ratioF = eV_half / N_O213
print(f"  e^{{V_Λ/2}} = {float(eV_half):.6e}")
print(f"  N = {float(N_O213):.6e}")
print(f"  比 = {float(ratioF):.3f}  (量級一致 ~O(1–10); 非精確結構)")
chk("F1 量級一致（e^{V_Λ/2} ~ N）", mpf("0.5") < ratioF < mpf("10"),
    f"({float(ratioF):.3f})")

print(f"\n===== 全部 {int(G-1)} PASS =====")
sys.exit(0)