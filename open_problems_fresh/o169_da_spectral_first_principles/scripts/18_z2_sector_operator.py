#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/18 — B1: Z₂ 扇區算子 (斜率 a = 1 嘅算子級推導)
=============================================================
docs/07 原狀: a = 1 已由 Z₂ 和律 (S2→S5) 解析導出, 但「輸運詮釋」🔴:
  點解每層增益 = 奇 (反週期) 扇區嘅譜重按鏈長歸一?

本腳本把 a = 1 推到**算子級**:
  T1  Z₂ 分裂: γ_n = μ² − 2cos(πn/44)  (常數部分 μ² + Z₂-奇波動部分)
  T2  奇扇區內波動部分**精確相消** ⇒ Σγ_odd = N_odd·μ² = N_d
  T3  算子身份: a = Tr(L_odd)/N_d = ⟨γ⟩_odd/μ² = 1
  T4  整數性/保護: 偶扇區含 Z₂ 不動點 (γ_22 = μ²) ⇒ 46/44 = 1.0455 非整數
      ⇒ 輸運量必須取奇 (反週期) 扇區, 增益先精確為 1
  T5  a = 1 嘅 9 個等價表達 (新增 2 個算子級)

結構輸入: N_d = 44 (偶), N_odd = N_even = 22, μ² = γ_22 = 2, B = 4, T̂ = [[0,1],[1,1]]
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi; phi = (1 + mp.sqrt(5))/2; inv = 1/phi
N, B = 44, 4
gam = {n: 4*mp.sin(pi*n/88)**2 for n in range(1, N+1)}
mu2 = gam[22]

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 80)
print("O169/18 — B1: Z₂ 扇區算子 (斜率 a = 1 嘅算子級推導)")
print("=" * 80)
print(f"  N_d = {N} (偶),  μ² = γ_22 = {mp.nstr(mu2,12)},  B = {B}")

# ---------- T1 ----------
print("\nT1. Z₂ 分裂: γ_n = μ² − 2cos(πn/44)")
ok = all(abs(gam[n] - 2 + 2*mp.cos(pi*n/44)) < mp.mpf('1e-38') for n in range(1, 44))
chk("T1  γ_n = 2 − 2cos(πn/44) 全部 43 個", ok)
ok2 = all(abs((gam[n]-2) + (gam[44-n]-2)) < mp.mpf('1e-38') for n in range(1, 44))
chk("T1b 波動部分 (γ_n − μ²) 係 Z₂-奇: (γ_n−2) + (γ_{44−n}−2) = 0", ok2,
    "43/43 對")
print(f"  ⇒ 譜 = Z₂-偶常數部分 μ² = {float(mu2):.6f} + Z₂-奇波動部分 −2cos(πn/44)")

# ---------- T2 ----------
print("\nT2. 奇扇區內波動部分精確相消")
S_odd = mp.fsum(gam[n] for n in range(1, 44, 2))
S_even = mp.fsum(gam[n] for n in range(2, 45, 2))
S_fluct_odd = mp.fsum(gam[n] - mu2 for n in range(1, 44, 2))
print(f"  Σ(γ_n − μ²) over odd = {mp.nstr(S_fluct_odd, 8)}  (精確 0)")
print(f"  Σγ_odd = N_odd·μ² = 22·2 = {mp.nstr(S_odd,12)} = N_d")
print(f"  Σγ_even = {mp.nstr(S_even,12)}  (含 Z₂ 不動點 γ_22 = μ² 同 γ_44 = B)")
chk("T2  奇扇區波動部分精確相消 (|Σ| < 1e-38)", abs(S_fluct_odd) < mp.mpf('1e-38'))
chk("T2b Σγ_odd = N_odd·μ² = N_d", abs(S_odd - N*mu2/2) < mp.mpf('1e-38'),
    f"{mp.nstr(S_odd,12)} = 22·2")
chk("T2c ⟨γ⟩_odd = μ² (奇扇區平均譜重 = 不動點權重)", abs(S_odd/22 - mu2) < mp.mpf('1e-38'))

# ---------- T3 ----------
print("\nT3. 算子身份")
a_op = S_odd/N
print(f"  Tr(L_odd) = Σγ_odd = {mp.nstr(S_odd,12)} = N_d")
print(f"  a = Tr(L_odd)/N_d = {mp.nstr(a_op,12)}")
print(f"  a = ⟨γ⟩_odd/μ²     = {mp.nstr(S_odd/22/mu2,12)}")
print(f"  Tr(T̂) = φ + (−φ⁻¹) = {mp.nstr(phi - inv,12)},  det(T̂) = {mp.nstr(phi*(-inv),12)}")
chk("T3  a = Tr(L_odd)/N_d = 1 EXACT", abs(a_op - 1) < mp.mpf('1e-38'))
chk("T3b a = ⟨γ⟩_odd/μ² = 1 EXACT", abs(S_odd/22/mu2 - 1) < mp.mpf('1e-38'))
chk("T3c Tr(T̂) = 1, det(T̂) = −1 (Z₂ 對偶對 {φ, −φ⁻¹})",
    abs(phi-inv-1) < mp.mpf('1e-38') and abs(phi*(-inv)+1) < mp.mpf('1e-38'))

# ---------- T4 ----------
print("\nT4. 整數性/保護: 為何必須用奇 (反週期) 扇區")
a_even = S_even/N
print(f"  偶扇區: Σγ_even/N_d = {mp.nstr(a_even,12)} (非整數, 含不動點 γ_22 = μ²)")
print(f"  奇扇區: Σγ_odd/N_d  = {mp.nstr(a_op,12)} (精確整數 1)")
print(f"  結構理由: N_d = 44 偶 ⇒ 反射 n → 44−n 喺奇數集**冇不動點** ⇒ 反對稱相消零殘餘;")
print(f"            偶數集含不動點 n = 22 (γ_22 = μ² = 2) ⇒ 殘餘 2/44 = 0.0455")
chk("T4  偶扇區給非整數增益 (46/44 ≠ 1)", abs(a_even - 1) > mp.mpf('0.01'),
    f"{mp.nstr(a_even,10)}")
chk("T4b 奇扇區增益精確為整數 1", abs(a_op - 1) < mp.mpf('1e-38'))

# ---------- T5 ----------
print("\nT5. a = 1 嘅 9 個等價表達")
exprs = [("Σγ_odd/N_d", S_odd/N), ("⟨γ⟩_odd/2", S_odd/22/2), ("μ²/2", mu2/2),
         ("γ₂₂/2", gam[22]/2), ("(Σγe−Σγo)/2", (S_even-S_odd)/2), ("Σγ_odd/(2N_odd)", S_odd/44),
         ("B/4", mp.mpf(B)/4), ("★Tr(L_odd)/N_d", S_odd/N), ("★⟨γ⟩_odd/μ²", S_odd/22/mu2)]
for tag, v in exprs:
    print(f"  {tag:<18} = {mp.nstr(v,12)}   dev = {float(abs(v-1)):.1e}")
chk("T5  9 個表達全部 dev = 0", all(abs(v-1) < mp.mpf('1e-38') for _, v in exprs))

print()
print("=" * 80)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 80)
print(f"""
結論 (B1 狀態: 🟢 譜級完成 / 🔴 剩 Lagrangian 級):
  T1  γ_n = μ² − 2cos(πn/44): 譜 = Z₂-偶常數部分 μ² + Z₂-奇波動部分。
  T2  奇扇區內波動部分**精確相消** (Σ(γ_n−μ²) = 0) ⇒ Σγ_odd = N_odd·μ² = N_d = 44。
  T3  ★ 算子身份: **a = Tr(L_odd)/N_d = ⟨γ⟩_odd/μ² = 1** (L_odd = Z₂-奇扇區 Laplacian)。
  T4  ★ **整數性/保護**: N_d 偶 ⇒ 奇扇區冇 Z₂ 不動點 ⇒ 相消零殘餘 ⇒ 增益**精確整數**;
      偶扇區含不動點 γ_22 = μ² ⇒ 46/44 = {mp.nstr(a_even,8)} (非整數) — 故輸運量必須取奇扇區。
  T5  a = 1 有 9 個等價表達 (新增 2 個算子級: Tr(L_odd)/N_d, ⟨γ⟩_odd/μ²)。
  ⇒ B1 嘅**譜級**推導完成 (a = 1 = 奇扇區平均譜重 / 不動點權重)。
  🔴 殘餘 (真正未閉合): 「伸長 = 奇扇區輸運量」嘅 **Lagrangian 級**識別 —
     即邊個場論算子嘅期望值 = Tr(L_odd)/N_d。現有素材: O180 投影核 r_k = 2πR cos²θ_k。
""")
