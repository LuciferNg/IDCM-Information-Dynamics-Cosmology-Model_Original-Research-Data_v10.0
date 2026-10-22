#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/22 — docs/10–12 獨立文檔核對 (2026-09-23)

scripts/15 只覆蓋 docs/01–07 + data/01。本腳本獨立重算 docs/10 (交收閉合)、
docs/11 (0.7116 判定)、docs/12 (h_lad stale + 統一結構) 全部宣稱值。

方法: 同 scripts/15 — 唔 import 任何 scripts/16-21 函數, 由定義重新實作。
"""
import mpmath as mp
mp.mp.dps = 40
C = mp.mpf("299792.458"); R = mp.mpf("4129.94"); LN4 = mp.log(4); LN2 = mp.log(2)
SQ2 = mp.sqrt(2); PI = mp.pi; PHI = (1+mp.sqrt(5))/2
NGEN = 3; ND = 44; B = 4
B_NEW = 22/sum(mp.cos(mp.pi*n/88) for n in range(1, 23))
W_RING = C/R; H_CMB = W_RING*(1-PI/ND); H_O170 = C*LN4/(R*SQ2)
ELL_T = mp.log(3)/LN4
def ell(z): return mp.log(1+mp.mpf(str(z)))/LN4
def chk(tag, ok, note=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + tag + ("  " + note if note else ""))
    return ok
L = []
def c2(tag, got, want, tol):
    ok = abs(mp.mpf(got)-mp.mpf(want)) <= mp.mpf(tol)
    L.append(ok)
    print(("  [OK] " if ok else "  [X ] ") + f"{tag}: 算 {mp.nstr(mp.mpf(got),8)}  doc {want}")

print("=" * 100)
print("O170 scripts/22 — docs/10–12 獨立核對")
print("=" * 100)

print("\n--- docs/10: 交收閉合 ---")
c2("N3a O214 h_best 0.6710 vs h_cmb dev 0.46%", (mp.mpf("0.6710")/(H_CMB/100)-1)*100, "-0.456", "0.01")
c2("N3b Ω_dm·h² h_cmb +0.84%", (mp.mpf(16)/60*(H_CMB/100)**2)/(mp.mpf("0.2645")*mp.mpf("0.674")**2)*100-100, "+0.84", "0.05")
c2("N3b Ω_dm·h² h_o170 +12.4%", (mp.mpf(16)/60*(H_O170/100)**2)/(mp.mpf("0.2645")*mp.mpf("0.674")**2)*100-100, "+12.4", "0.1")
c2("N2a 1.97% = 1−√2·ln2", (1-SQ2*LN2)*100, "1.9742", "0.01")
c2("N2b h_o170/h_cmb vs 19/18 (0.007%)", (H_O170/H_CMB)/(mp.mpf(19)/18)*100-100, "0.0070", "0.002")
c2("N2c √2·ln2 vs (1−π/44)(19/18) (0.007%)", (SQ2*LN2)/((1-PI/44)*19/18)*100-100, "0.0070", "0.002")
c2("H0P h_cmb vs Planck 67.4 (0.01%)", (H_CMB/67.4-1)*100, "0.0105", "0.005")
deep = SQ2*(mp.log(18)/LN4 - ELL_T)
c2("piR1 deep = √2·log₄6 精確", abs(deep - SQ2*mp.log(6)/LN4), "0", "1e-30")
def M_arch(e): return 1/mp.cos(mp.pi*(22+B*mp.sin(mp.pi*e))/88) if e < ELL_T else SQ2
shallow = mp.quad(lambda t: M_arch(t), [0, ELL_T])
tot19 = shallow + SQ2*(mp.log(19)/LN4 - ELL_T)
c2("piR2 ∫₀^{log₄19} = 3.143308 vs π (0.055%)", (tot19/PI-1)*100, "0.0546", "0.01")

print("\n--- docs/11: 0.7116 判定 ---")
c2("S4a h_o170 = h_cmb(1+1/18) 0.007%", (H_O170/(H_CMB*19/18)-1)*100, "0.0070", "0.002")
c2("S5a P3 SH0ES −1.84σ", (H_O170-73.0)/1.0, "-1.843", "0.02")
c2("S6 n_c(ln4) = 21.43 非整數", 88/PI*mp.acos(1/LN4), "21.43", "0.02")

print("\n--- docs/12: h_lad stale + 統一結構 ---")
def H_eff_new(z):
    e = ell(z)
    dD = R*(4**(-e)*LN4*(e+B_NEW) + (1-4**(-e)))/((1+mp.mpf(str(z)))*LN4)
    return C/dD
for z, want in (("0.01", "65.33"), ("0.03", "66.27"), ("0.05", "67.23"), ("0.10", "69.71")):
    c2(f"H_eff_new(z={z})", H_eff_new(z), want, "0.01")
c2("H_eff_new(0) = c/(R·b) = 64.86", C/(R*B_NEW), "64.86", "0.01")
c2("B1 新律 H_eff(0.03) vs SH0ES −9.3%", (H_eff_new("0.03")/73.04-1)*100, "-9.27", "0.1")
c2("統一 h_o170 = h_cmb(1+1/18) = 0.711520", H_CMB/100*19/18, "0.711520", "1e-5")
c2("統一 舊h_lad = h_cmb(1+π/37) = 0.731305", H_CMB/100*(1+PI/37), "0.731305", "1e-5")
c2("統一 舊h_lad 0.001%", (mp.mpf("0.73130")/(H_CMB/100*(1+PI/37))-1)*100, "-0.0007", "0.002")
c2("18 = 2N_gen²", 2*NGEN**2, "18", "1e-30")
c2("37 = 4N_gen²+1", 4*NGEN**2+1, "37", "1e-30")

print("\n" + "=" * 100)
print(f"DOCS 10-12 CROSSCHECK: {sum(L)}/{len(L)}")
print("=" * 100)
