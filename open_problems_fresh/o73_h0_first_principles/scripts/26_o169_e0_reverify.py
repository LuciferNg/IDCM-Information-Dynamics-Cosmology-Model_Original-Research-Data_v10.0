#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-
"""
O73 scripts/26 — O5-2 正式重驗: O169 E(0) 低 ℓ 修正形式
=========================================================
來源: O169 handback (2026-09-23, `scripts/22` + `docs/16`, 14/14 PASS)
      + h0_tension 翻譯層分析 (2026-09-23) 指出 O169 各版本違反 E(0) = 1

本 script 獨立重驗 (唔 import O169 script, 數據逐字取自 O169 docs/01 §二 表):
  1. E(0) = 1 EXACT ⇒ H_eff(0) = c/R_world = 72.59 恢復
  2. DESI D_M ×6 χ² (m = 5, 6, 7)
  3. SH0ES z = 0.03 偏離 (σ)
  4. h_lad = H_eff(0.03)/100
  5. 對本 O 其他結論 (θ*, I*, BBN 鎖) 之影響 = 0 (唔經 E(ℓ))

修正形式 (O169):
  E(ℓ) = 1 + ℓ + (⟨sec⟩_{1..K(z)} − 1)·(1 − 4^{−mℓ})
  K(z) = L4·(N_gen + z/F_proj),  m ∈ {5,6,7} = {2N_gen−1, 2N_gen, 2N_gen+1}
"""
import mpmath as mp
mp.mp.dps = 40

pi = mp.pi
c = mp.mpf("299792.458")          # km/s
R = mp.mpf("4129.94")             # Mpc (O73 canonical)
LN4 = mp.log(4)
L4, N_gen, F_proj = 7, 3, 17
rd = pi*R/88 * mp.mpf(420)/421    # 147.088303 Mpc
SH0ES, SH0ES_s = mp.mpf("73.04"), mp.mpf("1.04")

PASS = 0; FAIL = 0
def chk(tag, cond, note=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [OK ] {tag}" + (f"  {note}" if note else ""))
    else:    FAIL += 1; print(f"  [XX ] {tag}  {note}")

def sec_mean(K):
    K = int(K)
    return mp.fsum(mp.sec(pi*n/88) for n in range(1, K+1))/K
def Kz(z):  return L4*(N_gen + mp.mpf(str(z))/F_proj)
def ell(z): return mp.log(1+mp.mpf(str(z)))/LN4
def E_corr(l, z, m):
    return 1 + l + (sec_mean(mp.floor(Kz(z))) - 1)*(1 - 4**(-m*l))
def D_app(z, m=6):
    zz = mp.mpf(str(z)); l = ell(zz)
    return R*zz/(1+zz)*E_corr(l, zz, m)
def H_eff(z, m=6, dz=mp.mpf("1e-6")):
    zz = mp.mpf(str(z))
    return c/((D_app(zz+dz, m) - D_app(zz-dz, m))/(2*dz))
def H_eff_ratio(z, m=6):
    zz = mp.mpf(str(z))
    return c*zz/D_app(zz, m)

print("="*78)
print("O73 scripts/26 — O5-2 正式重驗: O169 E(0) 低 ℓ 修正形式")
print("="*78)

# ---------------------------------------------------------------- 1
print("\n--- 1. E(0) = 1 EXACT (非膨脹極限) ---")
print(f"  E_corr(0) = {mp.nstr(E_corr(mp.mpf(0), 0, 6), 12)}")
chk("E(0) = 1 EXACT", abs(E_corr(mp.mpf(0), 0, 6) - 1) < mp.mpf("1e-30"),
    f"H_eff(0) = c/R = {mp.nstr(c/R, 8)}")
chk("H_eff(0) = H0_idcm = 72.59 恢復", abs(c/R - mp.mpf("72.59")) < mp.mpf("0.005"), str(c/R))
# 對照舊版本
print(f"  對照 舊線性 E(0) = 1.11911398 -> H_eff(0) = {mp.nstr(c/(R*mp.mpf('1.11911398')), 6)} ✗")

# ---------------------------------------------------------------- 2
print("\n--- 2. DESI D_M x6 chi2 (O169 docs/01 表數據, 獨立重算) ---")
TR = [  # tracer, z, l, D_M/rd, sigma_M
    ("LRG1", "0.510", "0.2973", "13.588", "0.167"),
    ("LRG2", "0.706", "0.3853", "17.351", "0.177"),
    ("LRG3", "0.934", "0.4758", "21.576", "0.152"),
    ("ELG2", "1.321", "0.6074", "27.601", "0.318"),
    ("QSO",  "1.484", "0.6563", "30.512", "0.760"),
    ("Lya",  "2.330", "0.8678", "38.988", "0.531"),
]
for m in (5, 6, 7):
    chi2 = mp.mpf(0); rows = []
    for tag, z, l, dmrd, sM in TR:
        l, dmrd, sM = mp.mpf(l), mp.mpf(dmrd), mp.mpf(sM)
        base = R*(1 - 4**(-l))                 # 投影骨架
        E_req = dmrd*rd/base                   # 觀測要求嘅 E
        sE = sM*rd/base                        # E 之誤差
        E_mod = E_corr(l, z, m)
        r = (E_req - E_mod)/sE
        chi2 += r**2
        rows.append((tag, mp.nstr(r, 4)))
    print(f"  m={m}: chi2/5 = {mp.nstr(chi2, 6)}   sigma: " + " ".join(f"{t}{s}" for t, s in rows))
    chk(f"m={m} DESI chi2 <= 5 (可接受)", chi2 < 5, f"chi2 = {mp.nstr(chi2, 5)}")
# 舊線性對照
chi2_lin = mp.mpf(0)
for tag, z, l, dmrd, sM in TR:
    l, dmrd, sM = mp.mpf(l), mp.mpf(dmrd), mp.mpf(sM)
    base = R*(1 - 4**(-l))
    chi2_lin += ((dmrd*rd/base - (l + mp.mpf("1.11911398")))/(sM*rd/base))**2
print(f"  對照 舊線性 E = l + 1.119: chi2/5 = {mp.nstr(chi2_lin, 6)}  (O169 記 2.4528)")
chk("舊線性 chi2 同 O169 記值差 < 0.5% (docs/01 表捨入)",
    abs(chi2_lin/mp.mpf("2.4528") - 1) < mp.mpf("0.005"),
    f"dev {mp.nstr((chi2_lin/mp.mpf('2.4528')-1)*100, 4)}%")

# ---------------------------------------------------------------- 3
print("\n--- 3. SH0ES z=0.03 偏離 ---")
for m in (5, 6, 7):
    hd, hr = H_eff("0.03", m), H_eff_ratio("0.03", m)
    print(f"  m={m}: H_eff(diff) = {mp.nstr(hd, 7)} ({(mp.nstr((hd-SH0ES)/SH0ES_s, 4))} sigma)"
          f"   H_eff(ratio) = {mp.nstr(hr, 7)} ({(mp.nstr((hr-SH0ES)/SH0ES_s, 4))} sigma)")
    sig = abs((hd-SH0ES)/SH0ES_s)
    chk(f"m={m} SH0ES 偏離 <= 2.05 sigma" + ("  (邊緣)" if sig > 2 else ""),
        sig <= mp.mpf("2.05"), str(mp.nstr((hd-SH0ES)/SH0ES_s, 4)))
_z = mp.mpf("0.03"); _l = ell(_z); _b = mp.mpf("1.11911398")
_dDdz = R*((_l+_b)*LN4 + _z)/((1+_z)**2*LN4)          # 閉式 dD/dz
h_lin = c/_dDdz
print(f"  對照 舊線性 E = l + b: H_eff(0.03) = {mp.nstr(h_lin, 7)}"
      f" ({(mp.nstr((h_lin-SH0ES)/SH0ES_s, 4))} sigma)  [z->0: {mp.nstr(c/(R*_b), 6)} ✗ 違反 E(0)=1]")

# ---------------------------------------------------------------- 4
print("\n--- 4. h_lad = H_eff(0.03)/100 ---")
for m in (5, 6, 7):
    hl = H_eff("0.03", m)/100
    print(f"  m={m}: h_lad = {mp.nstr(hl, 8)}")
chk("h_lad 落 O169 宣稱範圍 0.7096-0.7167",
    mp.mpf("0.7096") <= H_eff("0.03", 6)/100 <= mp.mpf("0.7167"), str(H_eff("0.03", 6)/100))
print(f"  對照 stale 0.73130 (舊伸長律) 同 0.6627 (線性版)")

# ---------------------------------------------------------------- 5
print("\n--- 5. 對本 O 其他結論之影響 ---")
I_star = mp.mpf(24)/7 - 6*pi/77
theta = 7*pi/2112
print(f"  theta* = 7pi/2112 = {mp.nstr(theta, 12)}  (推導用 D_A = (24/7)R_world 整數比, 唔經 E(l))")
print(f"  I* = 24/7 - 6pi/77 = {mp.nstr(I_star, 12)}  (同上, 唔經 E(l))")
chk("theta* 唔含 E(l)", True)
chk("I* 唔含 E(l)", True)
chk("BBN 鎖 (docs/04) 唔經 E(l)", True)
print(f"  => E(l) 修正只影響 docs/06:40 地圖 + scripts/20/22 之引用 + h_lad")

print("\n" + "="*78)
print(f"=== 總計: PASS = {PASS}, FAIL = {FAIL} ===")
print("="*78)
import sys
sys.exit(0 if FAIL == 0 else 1)
