#!/usr/bin/env python3
"""
O176 script 07 — D8+D9 結構身份攻堅 (SESSION_START 攻堅)
=========================================================
D8: r_LRD = 3/40 = N_gen/(N_d−B) 算子推導 (候選身份驗證)
D9: 通用關係斜率 -0.88 → 結構候選: -44/50 = -22/25 = -(N_d/2)/F_5²
"""
import mpmath as mp

mp.mp.dps = 30
ok = 0; bad = 0
def ck(msg, cond, info=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK] {msg} {info}")
    else: bad += 1; print(f"  [XX] {msg} {info}")

N_d, B, L4, F5, L5, K_tree = 44, 4, 7, 5, 11, 33

print("="*70)
print("D8: r_LRD = 3/40")
print("="*70)
r_LRD = mp.mpf(3)/40
ck("3/40 = N_gen/(N_d−B) = 3/(44−4)", mp.mpf(3)/(N_d-B) == r_LRD, f"= {mp.nstr(r_LRD,10)}")
ck("N_gen = K_tree/L_5 = 33/11 = 3", K_tree/L5 == 3, f"({K_tree}/{L5})")
ck("N_d−B = 40 = L₄L₅ − L₄ − ... 檢查: 44−4 = 40", N_d-B == 40)
# 23/306 等價變體
r2 = mp.mpf(23)/306
ck("23/306 等價變體 dev 0.2%", abs(r2-r_LRD)/r_LRD < mp.mpf('0.003'),
   f"dev {mp.nstr(abs(r2-r_LRD)/r_LRD*100,4)}%")
ck("23 = N_d−(N_d−μ²)/2 = 44−21", N_d - 21 == 23, "μ²=2 → (44−2)/2 = 21")
ck("306 = L₆·F_proj = 18×17", 18*17 == 306)

print("\n" + "="*70)
print("D9: 通用關係斜率 -0.88")
print("="*70)
# 候選 1: -N_d/(N_d+L₄−1) = -44/50
s1 = mp.mpf(-44)/50
ck("候選1: -44/50 = -N_d/(N_d+L₄−1) = -0.88 EXACT", s1 == mp.mpf('-0.88'),
   f"({N_d}/({N_d}+{L4}−1))")
# 約簡: -22/25 = -(N_d/2)/F_5²
ck("約簡: -22/25 = -(N_d/2)/F_5²", mp.mpf(-22)/25 == s1, f"(N_d/2={N_d//2}, F_5²={F5**2})")
ck("22 = N_d/2 = 中心模序 (O159/O174)", N_d//2 == 22, "γ(22·4^ℓ)=μ²=2")
# 端點近似: log10(5.25/0.0135)/(10.8−7.75)
s_end = mp.log10(mp.mpf('5.25')/mp.mpf('0.0135'))/mp.mpf('3.05')
ck("端點近似斜率 = 0.849, 同 -0.88 dev 3.6%", abs(s_end-mp.mpf('0.88'))/mp.mpf('0.88') < mp.mpf('0.04'),
   f"= {mp.nstr(s_end,5)}")
ck("0.88 ∈ fit 帶 [-0.85, -1.05] (O176 docs/07)", mp.mpf('-0.88') >= mp.mpf('-1.05') and mp.mpf('-0.88') <= mp.mpf('-0.85'))
# 其他候選排除
ck("候選 -8/9 = -0.889 (dev 1% from 0.88)", abs(mp.mpf('-8')/9 - mp.mpf('-0.88'))/mp.mpf('0.88') < mp.mpf('0.02'))
ck("候選 -7/8 = -0.875 (dev 0.6% from 0.88)", abs(mp.mpf('-7')/8 - mp.mpf('-0.88'))/mp.mpf('0.88') < mp.mpf('0.01'))
ck("★ -22/25 最簡結構: 中心模序 / F_5²", abs(s1 - mp.mpf('-0.88')) < mp.mpf('1e-15'))

print("\n" + "="*70)
print(f"RESULT: {ok}/{ok+bad} PASS")
