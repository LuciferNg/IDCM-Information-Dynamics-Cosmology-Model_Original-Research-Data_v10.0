#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/07 — 最終閉合驗證: 七 tracer 全表 + χ² 比較 + 誠實負結果

模型 (E = 伸長因子, D_A(ℓ) = R(1−4^{−ℓ})·E(ℓ)):
  OLD  : E = 1 + 2φ⁻¹ℓ                      (O76/O39 現行)
  OLD+δ: E = 1 + 2φ⁻¹ℓ + C(ℓ−1/2)(1−4^{−ℓ}), C = −0.1697  (O51/82)
  NEW  : E = ℓ + √5/2                        (本 O 結論, 零參數)

判準: D_M 六 tracer (DESI DR2 Table 6) 為主; BGS 用 D_V (需 D_H — 標明慣例)
      D_H 側唔用 dD_A/dz 判 (O117: D_H ≠ dD_A/dz, 屬 O117 範圍)
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2; inv = 1/phi; pi = mp.pi
R = mp.mpf('4129.94')
rd = pi*R/88*mp.mpf(420)/421

TR = [
    ('BGS',  mp.mpf('0.295'), None,              None,             None,             None,            None),
    ('LRG1', mp.mpf('0.510'), mp.mpf('13.588'),  mp.mpf('0.167'),  mp.mpf('21.863'), mp.mpf('0.425'), mp.mpf('-0.459')),
    ('LRG2', mp.mpf('0.706'), mp.mpf('17.351'),  mp.mpf('0.177'),  mp.mpf('19.455'), mp.mpf('0.330'), mp.mpf('-0.404')),
    ('LRG3', mp.mpf('0.934'), mp.mpf('21.576'),  mp.mpf('0.152'),  mp.mpf('17.641'), mp.mpf('0.193'), mp.mpf('-0.416')),
    ('ELG2', mp.mpf('1.321'), mp.mpf('27.601'),  mp.mpf('0.318'),  mp.mpf('14.176'), mp.mpf('0.221'), mp.mpf('-0.434')),
    ('QSO',  mp.mpf('1.484'), mp.mpf('30.512'),  mp.mpf('0.760'),  mp.mpf('12.817'), mp.mpf('0.516'), mp.mpf('-0.500')),
    ('Lya',  mp.mpf('2.330'), mp.mpf('38.988'),  mp.mpf('0.531'),  mp.mpf('8.632'),  mp.mpf('0.101'), mp.mpf('-0.431')),
]
BGS_DV, BGS_E = mp.mpf('7.942'), mp.mpf('0.075')

def Eof(l, tag):
    if tag == 'OLD':   return 1 + 2*inv*l
    if tag == 'OLDD':  return 1 + 2*inv*l - mp.mpf('0.1697')*(l-mp.mpf('0.5'))*(1-4**(-l))
    if tag == 'NEW':   return l + mp.sqrt(5)/2
    raise ValueError
def DA(z, tag): l = mp.log(1+z,4); return R*(1-4**(-l))*Eof(l, tag)
def DH(z, tag):
    h = mp.mpf('1e-9'); return (DA(z+h,tag)-DA(z-h,tag))/(2*h)

print("="*80)
print("O169/07 — 最終閉合驗證")
print("="*80)
print(f"R = {R} Mpc,  rd = {mp.nstr(rd,10)} Mpc")
print(f"OLD  E(ℓ) = 1 + 2φ⁻¹ℓ           (2φ⁻¹ = {mp.nstr(2*inv,8)})")
print(f"NEW  E(ℓ) = ℓ + √5/2            (√5/2 = {mp.nstr(mp.sqrt(5)/2,8)})")

# ---------- 表 1: D_M 殘餘 ----------
for tag, lab in [('OLD','V1 舊公式 (δ=0)'), ('OLDD','V2 舊公式+δ (C=−0.1697)'), ('NEW','★V3 新伸長定律')]:
    print(f"\n--- {lab} ---")
    print(f"{'tracer':<7}{'z':>7}{'ℓ':>8}{'D_M/rd':>9}{'obs':>8}{'σ_M':>8}")
    chi = mp.mpf(0); worst = (None, mp.mpf(0))
    for n, z, dm, em, dh, eh, rho in TR:
        l = mp.log(1+z,4)
        if dm is None: continue
        pm = DA(z, tag)/rd; s = (pm-dm)/em
        chi += s*s
        if abs(s) > abs(worst[1]): worst = (n, s)
        print(f"{n:<7}{float(z):>7.3f}{float(l):>8.4f}{float(pm):>9.3f}{float(dm):>8.3f}{float(s):>8.2f}")
    print(f"  χ²(D_M) = {mp.nstr(chi,6)}/5  最差 {worst[0]} {mp.nstr(worst[1],4)}σ")

# ---------- 表 2: BGS D_V ----------
print("\n--- BGS D_V (需 D_H; 慣例 (a) dD_A/dz (O167) / (b) O117 公式) ---")
for tag in ['OLD','OLDD','NEW']:
    z = TR[0][1]; l = mp.log(1+z,4)
    dv = (z*DA(z,tag)**2*DH(z,tag))**(mp.mpf(1)/3)/rd
    dk0 = inv**3*mp.e**(-(l-mp.mpf('0.5'))**2/(2*(mp.mpf('0.5')*mp.log(phi,4))**2))
    dgd = -mp.mpf('0.226311')*(l-mp.mpf('0.5'))*(1-4**(-l))
    dh117 = R*(1+dk0+dgd)/(1+z)
    dv2 = (z*DA(z,tag)**2*dh117)**(mp.mpf(1)/3)/rd
    print(f"  {tag:<5} (a) D_V/rd = {float(dv):.4f} → {float((dv-BGS_DV)/BGS_E):+.2f}σ"
          f"   (b) D_V/rd = {float(dv2):.4f} → {float((dv2-BGS_DV)/BGS_E):+.2f}σ")

# ---------- 表 3: D_H 側 (誠實: 唔用 dD_A/dz 判) ----------
print("\n--- D_H 側殘餘 (dD_A/dz 慣例; ⚠️ O117 已證 D_H ≠ dD_A/dz — 只作記錄) ---")
for tag in ['OLD','OLDD','NEW']:
    r = []
    for n, z, dm, em, dh, eh, rho in TR:
        if dh is None: continue
        r.append(f"{n}{float(DH(z,tag)/rd-dh)/float(eh):+.1f}")
    print(f"  {tag:<5} σ_H: " + " ".join(r))

# ---------- 表 4: 全七 tracer 總結 (D_M + BGS D_V) ----------
print("\n--- ★ 全七 tracer 總結 (D_M ×6 + BGS D_V 用 dD_A/dz) ---")
for tag in ['OLD','OLDD','NEW']:
    sig = []
    chi = mp.mpf(0)
    for n, z, dm, em, dh, eh, rho in TR:
        if dm is None:
            dv = (z*DA(z,tag)**2*DH(z,tag))**(mp.mpf(1)/3)/rd
            s = (dv-BGS_DV)/BGS_E
        else:
            s = (DA(z,tag)/rd-dm)/em
        chi += s*s; sig.append((n,s))
    mx = max(abs(s) for _, s in sig)
    print(f"  {tag:<5} χ² = {float(chi):>7.3f}/6   |σ|max = {float(mx):.2f}   " +
          " ".join(f"{n}{float(s):+.2f}" for n, s in sig))

# ---------- 表 5: rd 敏感度 ----------
print("\n--- rd 敏感度 (NEW 形式 D_M χ²) ---")
for rdv, tag in [(pi*R/88, 'rd=πR/88=147.442'), (pi*R/88*mp.mpf(420)/421, 'rd=147.088'), (mp.mpf('147.09'), 'rd=147.09 (DESI fiducial)')]:
    chi = mp.mpf(0)
    for n, z, dm, em, dh, eh, rho in TR:
        if dm is None: continue
        l = mp.log(1+z,4)
        pm = R*(1-4**(-l))*Eof(l,'NEW')/rdv
        chi += ((pm-dm)/em)**2
    print(f"  {tag:<24} χ² = {float(chi):.3f}/5")

# ---------- 表 6: 外推 sanity ----------
print("\n--- 外推 sanity (ℓ_Nyq = log₄18 = 2.08496) ---")
lny = mp.log(18,4)
for tag in ['OLD','OLDD','NEW']:
    D = R*(1-4**(-lny))*Eof(lny,tag)
    print(f"  {tag:<5} D_A(ℓ_Nyq) = {float(D):8.0f} Mpc   πR = {float(pi*R):8.0f}   ratio = {float(D/(pi*R)):.4f}")
print(f"  ℓ→∞ 漸近: D → R·E = R(ℓ + c);  NEW 斜率 1 vs OLD 斜率 2φ⁻¹ = 1.2361")

# ---------- 表 7: 簡併 ----------
print("\n--- 常數簡併 (NEW 形式, 兩個結構讀法) ---")
c1 = mp.sqrt(5)/2
vg22 = mp.fsum([mp.cos(n*pi/88) for n in range(1,23)])/22
c2 = 1/vg22
for c, tag in [(c1,'√5/2 = 1/2+φ⁻¹'), (c2,'1/⟨v_g⟩_{1..22} (Z₂ 自對偶半鏈)')]:
    chi = mp.mpf(0)
    for n, z, dm, em, dh, eh, rho in TR:
        if dm is None: continue
        l = mp.log(1+z,4)
        chi += ((R*(1-4**(-l))*(l+c)/rd - dm)/em)**2
    print(f"  {tag:<30} c = {mp.nstr(c,9)}  χ² = {float(chi):.3f}/5  (Δχ² = {float(chi-mp.mpf('2.4648')):+.4f})")
print("  → 兩者只差一個常數偏移 0.0011 (E 的 0.1%), 任何仿射形式下不可分辨 🔴")

print("\nRESULT: NEW 零參數形式 χ²(D_M) = 2.46/5 (舊 27.16, 舊+δ 13.09)")
