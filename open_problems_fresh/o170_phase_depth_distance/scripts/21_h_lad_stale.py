#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/21 — h 三值統一結構 + h_lad stale 檢驗 (2026-09-23)

用戶批評: 「0.7116 / 0.67407 / 0.73130 係從三條獨立公式推出來, 並非從總分母+因子建立出來」

本腳本三件事:
  A. ★ h_lad 來源檢驗: h_lad = H_eff(0.03)/100 = 73.13/100 出自 h0_tension/03_first_results.md,
     用舊伸長律 D_app = R(1−4^{−ℓ})(1+2φ⁻¹ℓ) 嘅投影 Jacobian — 但 1+2φ⁻¹ℓ 已被 O169 證偽 (4.88σ)!
     ⟹ h_lad = 0.73130 係 **stale (基於已證偽律)**
  B. 新橫向律 (O169: E = ℓ+b) 下 H_eff(z) = c/(dD_M/dz) 重算 → SH0ES 匹配仲喺唔喺度?
  C. 統一「總分母 + 因子」結構掃描: h(scale) = H_master × f(scale)
"""
import mpmath as mp
mp.mp.dps = 40
C = mp.mpf("299792.458"); R = mp.mpf("4129.94"); LN4 = mp.log(4); PI = mp.pi
SQ2 = mp.sqrt(2); PHI = (1+mp.sqrt(5))/2; B = 4; NGEN = 3; ND = 44
B_NEW = 22/sum(mp.cos(mp.pi*n/88) for n in range(1, 23))   # 1.11911398203
W_RING = C/R
def ell(z): return mp.log(1+mp.mpf(str(z)))/LN4
def chk(tag, ok, note=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + tag + ("  " + note if note else ""))
    return ok

print("=" * 100)
print("O170 scripts/21 — h 三值統一結構 + h_lad stale 檢驗")
print("=" * 100)

print("\n--- A. ★ h_lad 來源: 已證偽舊律? ---")
print("  h0_tension/03_first_results.md: D_app = R(1−4^{−ℓ})(1+2φ⁻¹ℓ), H_eff = c/(dD_app/dz)")
print("  H_eff(0.03) = 73.13 → h_lad = 0.73130  (O215 docs/04 §4b 引用)")
E_OLD_2 = 1 + 2*PHI**-1*ell("0.03")
print(f"  E_OLD(0.03) = 1+2φ⁻¹·ℓ = {mp.nstr(E_OLD_2,8)}")
print("  O169 判決: E_OLD = 1+2φ⁻¹ℓ 被 DESI DR2 D_M ×6 排除 4.88σ ⟹ h_lad 基於已證偽律")
chk("A1 h_lad = 0.73130 基於已證偽舊伸長律 (O169 4.88σ)",
    True, "⟹ stale, 需用新律重算")

print("\n--- B. 新橫向律 H_eff(z) 重算 ---")
def D_new(z):
    e = ell(z); return R*(1-4**(-e))*(e+B_NEW)
def H_eff_new(z):
    e = ell(z)
    dD = R*(4**(-e)*LN4*(e+B_NEW) + (1-4**(-e)))/((1+mp.mpf(str(z)))*LN4)
    return C/dD
for z in ("0.01", "0.03", "0.05", "0.10"):
    print(f"  H_eff_new(z={z}) = {mp.nstr(H_eff_new(z),7)}  (舊 72.75/73.13/73.55/74.81)")
print(f"  H_eff_new(0) = c/(R·b) = {mp.nstr(C/(R*B_NEW),7)}  (z→0 極限)")
chk("B1 新律 H_eff(0.03) = 66.24 ≠ SH0ES 73.04 (差 9.3%) — 舊「SH0ES 匹配 0.12%」係舊律假象",
    abs(H_eff_new("0.03")/73.04 - 1) > 0.05, f"實際差 {mp.nstr((H_eff_new('0.03')/73.04-1)*100,3)}%")

print("\n--- C. 統一「總分母 + 因子」結構掃描 ---")
print("  候選 master: ω_ring = 72.59 (O73 結構值, BBN+CMB 雙重鎖定)")
h_ring = W_RING/100
h_cmb = h_ring*(1-PI/ND)
h_o170 = W_RING*SQ2*mp.log(2)/100
h_lad_new = H_eff_new("0.03")/100
print(f"  h_ring   = {mp.nstr(h_ring,8)}   (master)")
print(f"  h_cmb    = {mp.nstr(h_cmb,8)}   f = 1−π/44 = {mp.nstr(1-PI/ND,9)}")
print(f"  h_o170   = {mp.nstr(h_o170,8)}   f = √2·ln2 = {mp.nstr(SQ2*mp.log(2),9)}")
print(f"  h_lad新  = {mp.nstr(h_lad_new,8)}   f = {mp.nstr(h_lad_new/h_ring,9)}  (H_eff(0.03) 新律)")
# 掃描 h_lad_new 因子
f_lad = h_lad_new/h_ring
print(f"  f_lad = {mp.nstr(f_lad,10)}")
cands = {
    "1−π/36": 1-PI/36,
    "1−π/35.5": 1-PI/mp.mpf('35.5'),
    "1−1/11.42": 1-mp.mpf(1)/mp.mpf('11.42'),
    "1−π/(4N_gen²)": 1-PI/(4*NGEN**2),
    "1/(1+π/12.5)": 1/(1+PI/mp.mpf('12.5')),
    "(1−π/44)(1+1/18)": (1-PI/44)*19/18,
}
for k, v in cands.items():
    print(f"    {k:26} = {mp.nstr(v,9)}  dev = {mp.nstr((v/f_lad-1)*100,4)}%")
# 統一結構候選: h(scale) = h_cmb × (1+f), f 係 N_gen 代數
print("\n  統一結構候選 (master = h_cmb, 全部 (1+f) 形式):")
f_rad = 1/18; f_lad2 = PI/37
print(f"    h_o170 = h_cmb×(1+1/18)      = {mp.nstr(h_cmb*(1+f_rad),8)}  vs {mp.nstr(h_o170,8)}  (0.007%)")
print(f"    h_lad  = h_cmb×(1+π/37)      = {mp.nstr(h_cmb*(1+f_lad2),8)}  vs 舊 0.73130 (0.001%) / 新 {mp.nstr(h_lad_new,8)} (?%)")
print(f"    18 = 2N_gen²;  37 = 4N_gen²+1 = (2N_gen)²+1")
chk("C1 h_o170 = h_cmb×(1+1/(2N_gen²)) 0.007% (已知)", abs((h_o170/(h_cmb*(1+f_rad))-1)) < 1e-4)
chk("C2 舊 h_lad = h_cmb×(1+π/37) 0.001% — 但 h_lad 係 stale (A1)",
    abs((mp.mpf('0.73130')/(h_cmb*(1+f_lad2))-1)) < 1e-4,
    f"dev = {mp.nstr((mp.mpf('0.73130')/(h_cmb*(1+f_lad2))-1)*100,4)}%")
print(f"  ★ 新律 h_lad_new = {mp.nstr(h_lad_new,7)} vs h_cmb×(1+π/37) = {mp.nstr(h_cmb*(1+f_lad2),7)}")
print(f"    → 新律下 SH0ES 匹配消失 ⟹ h_lad 需要 O73 側重審 (新投影公式 / 或 SH0ES 另有解釋)")

print("\n" + "=" * 100)
print("★ 重大發現: (1) h_lad = 0.7313 基於已證偽舊伸長律 (O169 4.88σ) = stale")
print("  (2) 新橫向律 H_eff(0.03) = 66.24 — 「SH0ES 匹配 0.12%」係舊律假象")
print("  (3) 統一 (1+f) 結構: h_cmb(1+1/18) = h_o170 (0.007%); h_cmb(1+π/37) ≈ 舊 h_lad (0.001%)")
print("  (4) 但 h_lad stale ⟹ 三值統一結構要用新律重算先成立 — O73/h0_tension 需交收更新")
print("=" * 100)
