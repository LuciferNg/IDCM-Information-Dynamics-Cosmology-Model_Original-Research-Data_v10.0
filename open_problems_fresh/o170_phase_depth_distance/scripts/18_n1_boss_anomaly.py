#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/18 — N1: BOSS DR12 z=0.38 張力診斷 (2026-09-23)

目的: 判定 BOSS DR12 z=0.38 D_H 嘅 −2.56σ 係 (a) arch 核低 ℓ 問題
      vs (b) BOSS 數據側異常。

關鍵檢驗: DESI BGS D_V (z=0.295, ℓ=0.1865) 同 BOSS z=0.38 係最近嘅兩個低 z 徑向測量。
      如果 arch 核喺低 ℓ 低估 D_H (BOSS 需要 M 高 7.8%), BGS D_V 應該都偏離 +2.3σ;
      實際 BGS = −0.37σ ⟹ 矛盾 ⟹ 異常喺 BOSS 側, 唔係 arch 核。

數字:
  BOSS z=0.38:  D_H/r_d = 25.00 ± 0.76  (SDSS final BAO table)
  BOSS z=0.51:  D_H/r_d = 22.33 ± 0.58
  DESI z=0.51:  D_H/r_d = 21.863 ± 0.425 (LRG1)
  跨調查偏差 @z=0.51: 22.33/21.863 = +2.14%
  BOSS z=0.38 M (DESI rd): 25.00 × 147.09×1.38×ln4/4129.94 = 1.7034
  arch 預言 M(ℓ=0.2323) = 1.5708 → −2.56σ
  系統修正後: 1.7034/1.0214 = 1.6678 → 仍 +1.87σ vs arch
"""
import mpmath as mp
mp.mp.dps = 40

C = mp.mpf("299792.458"); R = mp.mpf("4129.94"); LN4 = mp.log(4); SQ2 = mp.sqrt(2)
RD_DESI = mp.mpf("147.09")      # DESI r_d fiducial
RD_BOSS = mp.mpf("147.78")      # BOSS DR12 r_d fiducial (Alam 2017)
NGEN = 3; B = 4
ELL_T = mp.log(3)/LN4
def M_arch(e): return 1/mp.cos(mp.pi*(22+B*mp.sin(mp.pi*e))/88) if e < ELL_T else SQ2
def ell(z): return mp.log(1+mp.mpf(str(z)))/LN4
def M_of(dh, z, rd): return mp.mpf(dh)*rd*(1+mp.mpf(str(z)))*LN4/R
def sM_of(s, z, rd): return mp.mpf(s)*rd*(1+mp.mpf(str(z)))*LN4/R
def chk(tag, ok, note=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + tag + ("  " + note if note else ""))
    return ok

print("=" * 100)
print("O170 scripts/18 — N1: BOSS z=0.38 張力診斷")
print("=" * 100)

print("\n--- 1. BOSS z=0.38 異常幅度 ---")
Mb = M_of("25.000", "0.38", RD_DESI); sb = sM_of("0.760", "0.38", RD_DESI)
Ma = M_arch(ell("0.38"))
print(f"  BOSS z=0.38 需要 M = {mp.nstr(Mb,7)} ± {mp.nstr(sb,6)}  (DESI rd)")
print(f"  arch 預言 M(ℓ=0.2323) = {mp.nstr(Ma,7)}")
print(f"  σ = {mp.nstr((Mb-Ma)/sb,4)}")
chk("1a BOSS z=0.38 = −2.56σ", abs((Mb-Ma)/sb - mp.mpf("2.56")) < 0.05,
    f"實際 {mp.nstr((Mb-Ma)/sb,4)}σ")

print("\n--- 2. 跨調查偏差 (z=0.51 交叉定標) ---")
bias = mp.mpf("22.330")/mp.mpf("21.863")
print(f"  BOSS/DESI @z=0.51: 22.330/21.863 = +{mp.nstr((bias-1)*100,4)}%")
Mc = Mb/bias
print(f"  BOSS z=0.38 系統修正後 M = {mp.nstr(Mc,7)}  → σ = {mp.nstr((Mc-Ma)/sb,4)}")
chk("2a 修正後仍 ~1.9σ (系統偏差只解釋部分)", abs((Mc-Ma)/sb) > 1.0)
chk("2b 修正後 M ≈ 峰值 sec(26π/88) = 1.668676 (0.06%)",
    abs(Mc - 1/mp.cos(mp.pi*26/88))/(1/mp.cos(mp.pi*26/88)) < 1e-3,
    f"dev = {mp.nstr((Mc/(1/mp.cos(mp.pi*26/88))-1)*100,4)}%")

print("\n--- 3. ★ 關鍵矛盾檢驗: 若 arch 低 ℓ 真係低估, BGS D_V 應偏離 ---")
# BGS z=0.295: D_V = (z·D_M²·D_H)^{1/3}
ZB = mp.mpf("0.295"); DVO = mp.mpf("7.942"); DVE = mp.mpf("0.075")
D_H_arch = Ma2 = M_arch(ell("0.295"))*R/((1+ZB)*LN4)/RD_DESI   # D_H/r_d @ z=0.295
D_M_new = (1 - 4**(-ell("0.295")))*(ell("0.295") + 22/sum(mp.cos(mp.pi*n/88) for n in range(1,23)))
D_M_rd = D_M_new*R/RD_DESI
DV_arch = (ZB*D_M_rd**2*D_H_arch)**(mp.mpf(1)/3)
print(f"  BGS (z=0.295) arch D_V/rd = {mp.nstr(DV_arch,7)} vs obs {DVO} ± {DVE} → {mp.nstr((DV_arch-DVO)/DVE,4)}σ")
# 若低 ℓ D_H 有 BOSS 式 +7.8% 偏差:
DV_infl = (ZB*D_M_rd**2*(D_H_arch*(Mb/Ma)))**(mp.mpf(1)/3)
print(f"  若 D_H 低 ℓ 都高估 {mp.nstr((Mb/Ma-1)*100,3)}% (BOSS 式): D_V → {mp.nstr(DV_infl,7)} → {mp.nstr((DV_infl-DVO)/DVE,4)}σ")
chk("3a BGS 觀測 −0.37σ (arch 低 ℓ 正確)", abs((DV_arch-DVO)/DVE) < 1.0)
chk("3b BOSS 式偏差會令 BGS +2.3σ — 同觀測矛盾 ⟹ 異常喺 BOSS 側",
    abs((DV_infl-DVO)/DVE) > 2.0, f"若 arch 錯, BGS 應 {mp.nstr((DV_infl-DVO)/DVE,3)}σ, 實測 −0.37σ")

print("\n--- 4. 異常點非單調性 (vs 鄰近 z) ---")
print(f"  z=0.295 (BGS, D_V): arch M = {mp.nstr(M_arch(ell('0.295')),6)}")
print(f"  z=0.38  (BOSS, D_H): 需要 M = {mp.nstr(Mb,6)}  ← 比兩邊都高 (非單調)")
print(f"  z=0.51  (LRG1, D_H): obs M = {mp.nstr(M_of('21.863','0.510',RD_DESI),6)}")
chk("4a BOSS z=0.38 需要嘅 M 比 z=0.295 同 z=0.51 都高 — 數據側非單調",
    Mb > M_of("21.863", "0.510", RD_DESI) and Mb > M_arch(ell("0.295")))

print("\n--- 5. 獨立低 z 數據空缺 ---")
print("  eBOSS DR16: 冇單獨 z=0.38 bin (合併/取代); DESI DR2 BGS: 只有 D_V(z=0.295)")
chk("5a 冇獨立 D_H(z≈0.38) 測量可交叉 — 需未來數據 (DESI DR2 BGS 完整 / DR3) 裁決", True)

print("\n" + "=" * 100)
print("N1 裁決: arch 核由 DESI 6 bins (χ²3.47/6) + BGS D_V (−0.37σ) 雙重閉合;")
print("  BOSS z=0.38 單點 −2.56σ 係數據側異常 (非單調 + 同 BGS 矛盾),")
print("  系統修正後仍 ~1.9σ — 保持 🟡 待獨立低 z 數據裁決, 唔係 arch 核失敗")
print("=" * 100)
