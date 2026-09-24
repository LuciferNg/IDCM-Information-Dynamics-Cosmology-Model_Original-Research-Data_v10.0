#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-
"""
O73 scripts/27 — O5-1 判定: Ω_b 版本統一 (19/450 vs 3/60)
==========================================================
來源: O215 handback (2026-09-22) + O38 docs/02 + O163
      SESSION_START O73 L220+ (移交跟進 O215 閉合 + Ω_b 版本統一)

核心方法: 用 **同 h 無關** 嘅 Ω 比值判定 (Planck 直接測 Ω_b h², Ω_c h², Ω_m h²;
比值中 h² 相消 ⇒ 模型無關 + 零參數)。

版本:
  V-舊 (O14 φ-form 鏈):  Ω_b = 19/450 = 0.0422222;  Ω_DM = 247/900;  Ω_b/Ω_m = 2/15
                         結構比 Ω_DM/Ω_b = 13/2 = 6.5
  V-新 (O163/O215):      Ω_b = 3/60 = 1/20;  Ω_c = 16/60;  Ω_Λ = 41/60;  Ω_m = 19/60
                         家族 (3:16:41)/60;  結構比 Ω_c/Ω_b = 16/3
"""
import mpmath as mp
mp.mp.dps = 40

pi = mp.pi
G  = mp.mpf("6.67430e-11")          # m^3 kg^-1 s^-2
c  = mp.mpf("299792458")            # m/s
hbar = mp.mpf("1.054571817e-34")    # J s
kB   = mp.mpf("1.380649e-23")       # J/K
m_p  = mp.mpf("1.67262192369e-27")  # kg
Mpc  = mp.mpf("3.0856775814913673e22")
zeta3 = mp.zeta(3)
T_CMB = mp.mpf("2.7255")
KMS_MPC = mp.mpf("3.240779289e-20") # 1 km/s/Mpc in s^-1

# ---- Planck 2018 (TT,TE,EE+lowE+lensing) 直接測量 (互相獨立) ----
P = {
    "Obh2": (mp.mpf("0.02237"), mp.mpf("0.00015")),
    "Och2": (mp.mpf("0.1200"),  mp.mpf("0.0012")),
    "Omh2": (mp.mpf("0.1430"),  mp.mpf("0.0011")),
    "h":    (mp.mpf("0.6736"),  mp.mpf("0.0054")),
}
P_Ob   = P["Obh2"][0]/P["h"][0]**2
P_Oc   = P["Och2"][0]/P["h"][0]**2
P_Om   = P["Omh2"][0]/P["h"][0]**2
P_OL   = 1 - P_Om

# ---- IDCM 結構值 ----
h_cmb  = mp.mpf("0.674071")          # = (ω_ring/100)(1−π/44), O167
w_ring = mp.mpf("72.59")             # = c/R_world 結構
h_23   = mp.mpf(2)/3
R_world = mp.mpf("4129.94")

PASS = 0; FAIL = 0
def chk(tag, cond, note=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [OK ] {tag}" + (f"  {note}" if note else ""))
    else:    FAIL += 1; print(f"  [XX ] {tag}  {note}")
def sig(model, obs, obs_s, rel_model=mp.mpf(0)):
    """model vs obs 之 σ 偏離 (obs_s 絕對誤差; rel_model 為 model 之相對不確定度)"""
    s = mp.sqrt(obs_s**2 + (obs*rel_model)**2)
    return (model - obs)/s

print("="*80)
print("O73 scripts/27 — O5-1 判定: Ω_b 版本統一 (19/450 vs 3/60)")
print("="*80)

# ================================================================ 0
print("\n--- 0. 物理常數自檢 (SI) ---")
n_g = 2*zeta3/pi**2 * (kB*T_CMB/(hbar*c))**3
rho_c_h2 = 3*(100*mp.mpf(1000)/Mpc)**2/(8*pi*G)
print(f"  n_γ = {mp.nstr(n_g, 8)} m^-3   (教科書 4.107e8)")
print(f"  ρ_crit/h² = {mp.nstr(rho_c_h2, 8)} kg/m³  (教科書 1.878e-26)")
chk("n_γ 合理", abs(n_g - mp.mpf("4.107e8"))/mp.mpf("4.107e8") < mp.mpf("0.01"))
chk("ρ_crit/h² 合理", abs(rho_c_h2 - mp.mpf("1.878e-26"))/mp.mpf("1.878e-26") < mp.mpf("0.01"))
CONV = rho_c_h2/(m_p*n_g)    # η_B = Ω_b h² × CONV  (Ω_b h² = η_B / CONV)
print(f"  η_B = Ω_b h² × {mp.nstr(CONV, 8)}   [⇒ Ω_b h² 同 η_B 一一對應, 同 h 無關]")
print(f"  自檢: 0.02237 × CONV = {mp.nstr(mp.mpf('0.02237')*CONV, 6)}  (Planck η_B ≈ 6.10e-10)")

# ================================================================ 1
print("\n--- 1. ★ Planck 觀測 (Ω h² 為直接測量量; 比值同 h 無關) ---")
print(f"  Ω_b h² = {P['Obh2'][0]} ± {P['Obh2'][1]}")
print(f"  Ω_c h² = {P['Och2'][0]} ± {P['Och2'][1]}")
print(f"  Ω_m h² = {P['Omh2'][0]} ± {P['Omh2'][1]}")
print(f"  h      = {P['h'][0]} ± {P['h'][1]}")
print(f"  ⇒ Ω_b = {mp.nstr(P_Ob,6)}, Ω_c = {mp.nstr(P_Oc,6)}, Ω_m = {mp.nstr(P_Om,6)}, Ω_Λ = {mp.nstr(P_OL,6)}")

# ================================================================ 2
print("\n--- 2. ★★ 判定核心: 結構比 vs Planck (同 h 完全無關) ---")
tests = [
    ("Ω_c/Ω_b  (DM/baryon)", mp.mpf(13)/2, mp.mpf(16)/3,
     P["Och2"][0]/P["Obh2"][0], P["Och2"], P["Obh2"]),
    ("Ω_b/Ω_m  (baryon 佔比)", mp.mpf(2)/15, mp.mpf(3)/19,
     P["Obh2"][0]/P["Omh2"][0], P["Obh2"], P["Omh2"]),
    ("Ω_c/Ω_m  (DM 佔比)", mp.mpf(13)/15, mp.mpf(16)/19,
     P["Och2"][0]/P["Omh2"][0], P["Och2"], P["Omh2"]),
]
for tag, v_old, v_new, obs, (val1, s1), (val2, s2) in tests:
    rel = mp.sqrt((s1/val1)**2 + (s2/val2)**2)   # 比值相對誤差 (兩量獨立)
    s_abs = obs*rel
    d_old = (v_old - obs)/s_abs
    d_new = (v_new - obs)/s_abs
    print(f"  {tag}: Planck = {mp.nstr(obs,7)} ± {mp.nstr(s_abs,3)}")
    print(f"     舊 13/2 家族 = {mp.nstr(v_old,7)}  dev {mp.nstr((v_old/obs-1)*100,4):>8}%  "
          f"= {mp.nstr(d_old,4)}σ")
    print(f"     新 16/3 家族 = {mp.nstr(v_new,7)}  dev {mp.nstr((v_new/obs-1)*100,4):>8}%  "
          f"= {mp.nstr(d_new,4)}σ")
    chk(f"{tag}: 新版本 < 2σ", abs(d_new) < 2, f"{mp.nstr(d_new,3)}σ")
    lim = 2 if "Ω_c/Ω_m" in tag else 5
    chk(f"{tag}: 舊版本被排除 (>{lim}σ)", abs(d_old) > lim, f"{mp.nstr(d_old,4)}σ")

# ================================================================ 3
print("\n--- 3. ★ 家族內部一致性 (純結構, 唔用數據) ---")
fam_b, fam_c, fam_L = mp.mpf(3)/60, mp.mpf(16)/60, mp.mpf(41)/60
print(f"  新: 3/60 + 16/60 + 41/60 = {mp.nstr(fam_b+fam_c+fam_L, 10)}  (扁平性 EXACT)")
chk("(3:16:41)/60 和 = 1 EXACT", abs(fam_b + fam_c + fam_L - 1) < mp.mpf("1e-35"))
chk("Ω_b + Ω_c = Ω_m = 19/60 EXACT", abs(fam_b + fam_c - mp.mpf(19)/60) < mp.mpf("1e-35"))
old_b, old_c = mp.mpf(19)/450, mp.mpf(247)/900
print(f"  舊: 19/450 + 247/900 = {mp.nstr(old_b+old_c,10)} = Ω_m ✓ (但 Ω_DM = 247/900 非結構: 分母 900)")
print(f"      舊 Ω_DM/Ω_b = 247/38 = 13/2 = 6.5  (對 Planck 5.364 偏 +21.2%)")
print(f"      舊家族同 (3:16:41)/60 不相容: Ω_b = 19/450 需 Ω_c = 19/60 − 19/450 = 1235/4500")
chk("舊版本 Ω_b 唔屬 (3:16:41)/60 家族",
    old_b != fam_b, f"19/450 = {mp.nstr(old_b,6)} vs 3/60 = {mp.nstr(fam_b,6)}")

# ================================================================ 4
print("\n--- 4. Ω_b h² (直接測量量) ---")
print(f"  Planck: {P['Obh2'][0]} ± {P['Obh2'][1]}  = {mp.nstr(P['Obh2'][0]*100,5)}%")
cands = [
    ("Ω_b = 3/60, h = h_cmb = 0.674071", fam_b*h_cmb**2),
    ("Ω_b = 3/60, h = 2/3",              fam_b*h_23**2),
    ("Ω_b = 19/450, h = ω_ring/100",     old_b*(w_ring/100)**2),
    ("Ω_b = 19/450, h = h_cmb",          old_b*h_cmb**2),
]
for tag, v in cands:
    d = sig(v, P["Obh2"][0], P["Obh2"][1])
    mark = "★" if abs(d) < 2 else "✗"
    print(f"  {mark} {tag:34s}: Ω_b h² = {mp.nstr(v,8)}  dev {mp.nstr((v/P['Obh2'][0]-1)*100,4):>8}%  "
          f"= {mp.nstr(d,4)}σ")
chk("Ω_b = 3/60 & h = 2/3 ⇒ Ω_b h² = 1/45 EXACT", abs(fam_b*h_23**2 - mp.mpf(1)/45) < mp.mpf("1e-35"))
print(f"  ★ 恆等: 3/60 × (2/3)² = {mp.nstr(fam_b*h_23**2,10)} = 1/45 = {mp.nstr(mp.mpf(1)/45,10)}"
      f"  (O199 強逼值 2.2222%)")
chk("Ω_b h² = 1/45 落 2σ", abs(sig(mp.mpf(1)/45, P["Obh2"][0], P["Obh2"][1])) < 2,
    f"{mp.nstr(sig(mp.mpf(1)/45, P['Obh2'][0], P['Obh2'][1]),3)}σ")
chk("Ω_b = 19/450 & h = h_cmb 被排除 (>5σ)",
    abs(sig(old_b*h_cmb**2, P["Obh2"][0], P["Obh2"][1])) > 5,
    f"{mp.nstr(sig(old_b*h_cmb**2, P['Obh2'][0], P['Obh2'][1]),4)}σ")

# ================================================================ 5
print("\n--- 5. Ω_c h² (第二直接測量量) ---")
for tag, v in (("新: 16/60 × h_cmb²", fam_c*h_cmb**2),
               ("舊: 247/900 × h_cmb²", old_c*h_cmb**2)):
    d = sig(v, P["Och2"][0], P["Och2"][1])
    print(f"  {tag:24s}: Ω_c h² = {mp.nstr(v,8)}  dev {mp.nstr((v/P['Och2'][0]-1)*100,4):>7}%  = {mp.nstr(d,4)}σ")
chk("新版本 Ω_c h² < 2σ", abs(sig(fam_c*h_cmb**2, P["Och2"][0], P["Och2"][1])) < 2)
chk("舊版本 Ω_c h² 偏離 > 2σ", abs(sig(old_c*h_cmb**2, P["Och2"][0], P["Och2"][1])) > 2,
    f"{mp.nstr(sig(old_c*h_cmb**2, P['Och2'][0], P['Och2'][1]),4)}σ")

# ================================================================ 6
print("\n--- 6. BBN 鎖 (docs/04): ω_ring = √(8πG η_B m_p n_γ/(3Ω_b)) ---")
def bbn_lock(eta, Ob):
    return mp.sqrt(8*pi*G*eta*m_p*n_g/(3*Ob))/KMS_MPC
print(f"  參考: 結構 ω_ring = c/R_world = {w_ring};  CMB 投影 h_cmb×100 = {mp.nstr(h_cmb*100,8)}")
print(f"        Planck h×100 = {mp.nstr(P['h'][0]*100,6)}")
eta_planck = P["Obh2"][0]*CONV
print(f"  Planck η_B (由 Ω_b h² 反推) = {mp.nstr(eta_planck,6)}")
for etag, eta in (("Planck 6.104e-10", eta_planck),
                  ("O73 舊 6.0636e-10", mp.mpf("6.0636e-10")),
                  ("O215 新 6.2145e-10", mp.mpf("6.2145e-10"))):
    for otag, Ob in (("19/450", old_b), ("3/60", fam_b)):
        v = bbn_lock(eta, Ob)
        d_cmb = (v - h_cmb*100)/(h_cmb*100)*100
        d_str = (v - w_ring)/w_ring*100
        print(f"  η_B = {etag:18s} Ω_b = {otag:7s} ⇒ ω_ring(BBN) = {mp.nstr(v,7)}"
              f"   vs h_cmb×100 {mp.nstr(d_cmb,6):>7}%   vs 結構 72.59 {mp.nstr(d_str,7):>7}%")
print("  ⇒ BBN 鎖給出嘅係 CMB-紀元 H₀ = ω_ring(1−π/44), 唔係裸 ω_ring (見 §7)")

# ================================================================ 7
print("\n--- 7. ★ 張力消解: BBN/CMB 兩通道 vs 裸結構 ω_ring ---")
hcmb_from_struct = w_ring*(1 - pi/44)
print(f"  ω_ring × (1−π/44) = {mp.nstr(w_ring,6)} × {mp.nstr(1-pi/44,10)} = {mp.nstr(hcmb_from_struct,8)}")
chk("ω_ring(1−π/44) = h_cmb×100 (0.001%)", abs(hcmb_from_struct/100 - h_cmb) < mp.mpf("1e-5"))
bbn_new = bbn_lock(eta_planck, fam_b)
print(f"  BBN(Ω_b = 3/60, η_B = Planck) = {mp.nstr(bbn_new,7)}  vs  h_cmb×100 = {mp.nstr(h_cmb*100,7)}"
      f"   dev {mp.nstr((bbn_new/(h_cmb*100)-1)*100,5)}%")
chk("BBN 新版本通道 ≈ CMB 投影 (<1%)", abs(bbn_new/(h_cmb*100) - 1) < mp.mpf("0.01"),
    f"{mp.nstr((bbn_new/(h_cmb*100)-1)*100,4)}%")
bbn_old = bbn_lock(eta_planck, old_b)
print(f"  BBN(Ω_b = 19/450, η_B = Planck) = {mp.nstr(bbn_old,7)}  vs  結構 72.59  dev"
      f" {mp.nstr((bbn_old/w_ring-1)*100,5)}%  (舊版本係「調到配結構值」)")
chk("舊版本 BBN 通道 ≈ 結構裸值", abs(bbn_old/w_ring - 1) < mp.mpf("0.01"),
    f"{mp.nstr((bbn_old/w_ring-1)*100,4)}%")
print("  ⇒ 舊 Ω_b = 19/450 令 BBN 鎖「配到」72.59 (看似成功); O163 用 CMB χ² 證偽")
print("  ⇒ 新 Ω_b = 3/60 令 BBN 通道落到 67 (CMB 側) ⇒ 同 O167 投影 67.407 一致")
print("  ⇒ 判讀: BBN 鎖 = CMB-紀元 H₀; 72.59 = 裸環頻率 (需 (1−π/44) 投影)")

# ================================================================ 8
print("\n--- 8. 對 O73 之影響 ---")
print(f"  docs/04 BBN 鎖: Ω_b 0.04221 → 1/20; ω_ring(BBN) 72.73 → {mp.nstr(bbn_new,6)} (CMB 側)")
print(f"  docs/06 連結規則 1 (ω_ring ↔ Ω_b): 數值更新; 規則本身成立")
print(f"  docs/06 結構比: Ω_b/Ω_m 2/15 → 3/19; Ω_DM/Ω_b 13/2 → 16/3")
print(f"  θ* / I* / c / R_world / E(ℓ): 零影響 (唔經 Ω_b)")
m7_old, w_old = mp.mpf("13.8002"), mp.mpf("72.59")
print(f"  m_7 敏感度: M₀ ∝ √H₀ ⇒ Δm_7/m_7 = ½ΔH₀/H₀")
for tag, hh in (("H₀ = 72.59 (裸結構)", w_ring), ("H₀ = 67.407 (CMB)", h_cmb*100),
                ("H₀ = 66.813 (BBN/Planck η_B)", bbn_new)):
    r = mp.sqrt(hh/w_ring)
    print(f"    {tag:30s}: m_7 = {mp.nstr(m7_old*r, 7)} MeV  ({mp.nstr((r-1)*100,5)}%)")
print("  ⚠️ m_7 錨定問題屬 O38/O34 範圍 — 本 O 只量化敏感度, 唔裁定")

print("\n" + "="*80)
print(f"=== 總計: PASS = {PASS}, FAIL = {FAIL} ===")
print("="*80)
import sys
sys.exit(0 if FAIL == 0 else 1)
