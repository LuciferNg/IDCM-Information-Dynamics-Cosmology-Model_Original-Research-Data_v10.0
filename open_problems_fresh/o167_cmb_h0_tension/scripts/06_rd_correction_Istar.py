#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/06 — ★ r_d = λ_sync/2 × 420/421 修正身份 + I* 結構閉合

O51 scripts/75 發現: rd_corrected = (πR_H/88) × 420/421 = 147.0883
  vs Planck r_d = 147.090 → dev 0.0012% (0.008σ)
420 = 4·3·5·7 = B·N_gen·F₅·L₄ = 60·L₄ (球面正多邊形全集 × Lucas)
421 = 420+1 = F₁₄+N_d (F₁₄ = 377)

I* 結構 (O73 docs/12 🟡): I* = 24(1-π/44)/7 = 24/7 − 6π/77
  77 = L₄·L₅ = 7×11, 6 = 2N_gen → I* = 24/7 − 2N_gen·π/(L₄L₅) 全結構數
"""
import mpmath as mp
mp.mp.dps = 60

def eq(a, b, tol):
    return abs(a - b) < tol

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

print("="*70)
print("O167 scripts/06 — r_d 修正身份 + I* 結構")
print("="*70)

B = mp.mpf(4); N_gen = mp.mpf(3); L4 = mp.mpf(7); L5 = mp.mpf(11)
F5 = mp.mpf(5); F14 = mp.mpf(377)
R_H = mp.mpf("4129.94")
pi = mp.pi

# C1: rd_idcm = πR/88 = 147.439
rd_idcm = pi * R_H / 88
chk("C1 rd_idcm = πR_H/88 = 147.439", eq(rd_idcm, mp.mpf("147.439"), mp.mpf("0.001")))

# C2: 420 = B·N_gen·F₅·L₄ = 60·L₄
chk("C2 420 = B·N_gen·F₅·L₄ (4·3·5·7) = 60·L₄", B*N_gen*F5*L4 == 420 and 60*L4 == 420)

# C3: 421 = F₁₄+N_d = 420+1
chk("C3 421 = F₁₄+N_d (377+44)", F14 + mp.mpf(44) == 421)

# C4: rd_corrected = rd_idcm × 420/421 vs Planck r_d
rd_corr = rd_idcm * 420/421
dev_rd = (rd_corr - mp.mpf("147.090")) / mp.mpf("147.090")
chk("C4 rd_corr = 147.0883 vs Planck 147.090 (dev 0.0012%)", abs(dev_rd) < mp.mpf("0.00005"))
print(f"    rd_corr = {mp.nstr(rd_corr, 10)} Mpc, dev = {float(dev_rd)*100:.4f}%")

# C5: 冇修正 dev (0.24%) vs 有修正 (0.0012%) — 修正改善 200x
dev_raw = (rd_idcm - mp.mpf("147.090")) / mp.mpf("147.090")
chk("C5 修正改善 200× (0.237% → 0.0012%)", abs(dev_raw)/abs(dev_rd) > 100)
print(f"    raw dev = {float(dev_raw)*100:.3f}%")

# C6: I* = 24(1-π/44)/7 = 24/7 − 6π/77
I_star = 24*(1 - pi/44)/7
I_alt = mp.mpf(24)/7 - 6*pi/77
chk("C6 I* = 24/7 − 6π/77 (代數恒等)", eq(I_star, I_alt, mp.mpf("1e-50")))
print(f"    I* = {mp.nstr(I_star, 10)}")

# C7: 6 = 2N_gen, 77 = L₄·L₅ — 全結構數
chk("C7 I* = 24/7 − 2N_gen·π/(L₄L₅) (全結構數)", eq(mp.mpf(24)/7 - 2*N_gen*pi/(L4*L5), I_star, mp.mpf("1e-50")))

# C8: ΛCDM 鏈 H0 = c·θ*·I*/r_s(IDCM) 重構 = ω_ring(1-π/44) (IDCM 內部自洽)
c_km = mp.mpf("299792.458")
H0_from_IDCM = c_km * (7*pi/2112) * I_star / rd_idcm   # c·θ*·I/r_s
H0_cmb_pred = (c_km/R_H) * (1 - pi/44)
dev_h0 = (H0_from_IDCM - H0_cmb_pred)/H0_cmb_pred
chk("C8 H0 = c·θ*·I*/r_s(IDCM) == ω_ring(1-π/44) (ΛCDM 鏈收斂 IDCM 投影)",
    abs(dev_h0) < mp.mpf("1e-30"))
print(f"    H0(ΛCDM鏈) = {mp.nstr(H0_from_IDCM, 10)} vs ω_ring(1-π/44) = {mp.nstr(H0_cmb_pred, 10)} (dev {float(dev_h0):.1e})")

# C9: 用 rd_corr (420/421) 重構 — 誠實記錄偏離 (修正令 r_d 貼 Planck, 但 H0 鏈偏離 IDCM 投影)
H0_corr = c_km * (7*pi/2112) * I_star / rd_corr
dev_corr = (H0_corr - H0_cmb_pred)/H0_cmb_pred
chk("C9 記錄: rd_corr 版 H0 = 67.57 偏離 ω_ring(1-π/44) 0.24% (修正取捨, 誠實記錄)",
    abs(dev_corr) < mp.mpf("0.01"))
print(f"    H0(rd_corr) = {mp.nstr(H0_corr, 8)} vs 67.407 (dev {float(dev_corr)*100:.3f}%)")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("誠實標記: 420/421 修正有結構身份 (420=60·L₄, 421=F₁₄+N_d) 但機制未推導 🟡")
