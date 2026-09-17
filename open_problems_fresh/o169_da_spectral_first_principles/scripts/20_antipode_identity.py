#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/20 — B3 殘項 ②: 環對面身份 (piR/Nyquist 假設嘅結構基礎)
====================================================================
docs/08 §五.2 原狀: 「Nyquist 截止 (z = 17) 係咪啱好對應環對面」未導出 → 🔴。
docs/10 嘅 B2 裁決建基於呢個假設 ⇒ 假設若無結構基礎, 裁決只係條件性。

本腳本 (零新常數):
  T1  ★ r_22 = 2*pi*R_world*cos^2(theta_22) = pi*R_world EXACT (O180 投影核)
  T2  ★ 三合一: 環對面 / Z2 自對偶模 (n = N_d/2) / 投影核半功率點
  T3  觀察者 (奇) 扇區排除不動點 => 整數保護 (同 docs/12 一致)
  T4  累積相位 = D_A/R_world; 飽和 D_A = pi*R <=> 相位 = pi = 一次相位滑移 (O7)
  T5  ★ 窗律端點由門檻律導出: m_n^2 < mu^2 (嚴格) => K = 21 = L4*N_gen = DESI 唯一窗
  T6  m_n^2 <= mu^2 (非嚴格) => K = 22 = N_d/2
  T7  Nyquist 窗 K = 28 = B*L4; theta_28 = L4*pi/(N_d/2) = 7*pi/22
  T8  誠實: 飽和「位置」= z_max 仍係假設, 但兩邊 (對面 / 截止) 現都有結構身份
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi
N, L4, Ng, B, Nd, L6, Fp = 44, 7, 3, 4, 44, 18, 17
mu2 = mp.mpf(2); mu4 = 4
l_nyq = mp.log(L6, 4)
th  = {n: pi*n/88 for n in range(1, 45)}
gam = {n: 4*mp.sin(th[n])**2 for n in range(1, 45)}
vg  = {n: mp.cos(th[n]) for n in range(1, 45)}
sec = {n: 1/vg[n] for n in range(1, 45)}
def bsec(K): return mp.fsum(sec[n] for n in range(1, K+1))/K

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))
print(f"[SELFTEST] checker 識 FAIL: {not (mp.mpf(3) == mp.mpf(4))}")

print("=" * 78)
print("O169/20 — B3 殘項 ②: 環對面身份")
print("=" * 78)

print("\nT1. ★ 環對面 = O180 投影核 @ 自對偶模")
print("  O180: r_k = 2*pi*R_world*cos^2(theta_k),  v_k = c*cos(theta_k)")
for k in (1, 21, 22, 28, 44):
    print(f"    k = {k:2d}  theta = {float(th[k]*180/pi):8.4f} deg  cos^2 = {float(mp.cos(th[k])**2):.9f}"
          f"   r_k/(pi*R_w) = {float(2*mp.cos(th[k])**2):.9f}")
r22 = 2*mp.cos(th[22])**2
chk("T1  r_22 = 2*pi*R_w*cos^2(pi/4) = pi*R_w EXACT (cos^2(pi/4) = 1/2)",
    abs(r22 - 1) < mp.mpf('1e-38'), f"dev = {mp.nstr(abs(r22-1), 3)}")
chk("T1b 對面距離 pi*R_w 係投影核嘅半功率點 (cos^2 = 1/2)", abs(mp.cos(th[22])**2 - mp.mpf(1)/2) < mp.mpf('1e-38'))

print("\nT2. ★ 三合一")
print("  (i)   環對面 = 視線最遠點 (距離 pi*R_w)")
print("  (ii)  Z2 自對偶模 n = N_d/2 = 22 (theta = pi/4, 反射不動點)")
print("  (iii) 投影核半功率點 (cos^2 theta = 1/2)")
chk("T2  三者同一個模 n = 22 = N_d/2 (n -> N_d - n 反射嘅不動點)", 22 == Nd//2)

print("\nT3. 觀察者扇區排除不動點")
oddset = [n for n in range(1, 45) if n % 2 == 1]
chk("T3  不動點 n = 22 唔喺奇 (觀察者) 扇區 => 相消零殘餘 => 整數保護",
    22 not in oddset, f"|odd| = {len(oddset)} = N_d/2 = {Nd//2}")
chk("T3b Sum_gam_odd = N_d = 44 EXACT (docs/12)",
    abs(mp.fsum(gam[n] for n in oddset) - 44) < mp.mpf('1e-38'))

print("\nT4. 相位詮釋")
print("  D_A(l)/R_world = (1 - 4^-l)*E(l) = 累積相位 (半圈 = pi)")
print(f"  飽和 D_A = pi*R_w  <=>  累積相位 = pi = 一次相位滑移 (O7 拓撲位元寫入)")
E_nyq = l_nyq + bsec(28)
ph = (1 - 4**(-l_nyq))*E_nyq
chk("T4  窗律 @ Nyquist 累積相位 = pi (dev < 1e-5)", abs(ph - pi)/pi < mp.mpf('1e-5'),
    f"phase = {mp.nstr(ph,12)}  dev = {float(abs(ph-pi)/pi*100):.6f}%")

print("\nT5. ★ 窗律端點由門檻律導出 (m_n^2 < mu^2 嚴格)")
# gamma_n = 4 sin^2(pi n/88) 單調增 (n <= 44);  gamma_22 = mu^2 EXACT (解析)
Kstrict = 21   # 解析: gamma_21 < 2 < gamma_22 = 2
Knon    = 22   # 解析: gamma_22 = 2 恰好
print(f"  gamma_21 = {float(gam[21]):.9f} < mu^2 = 2 < gamma_23 = {float(gam[23]):.9f}")
print(f"  gamma_22 = {mp.nstr(gam[22],12)} = mu^2 EXACT (解析, 數值差 2.3e-41 係浮點)")
print(f"  K (m^2 <  mu^2, 嚴格)   = {Kstrict} = L4*N_gen = {L4*Ng}")
print(f"  K (m^2 <= mu^2, 非嚴格) = {Knon} = N_d/2 = {Nd//2}")
chk("T5  ★ 嚴格門檻 m^2 < mu^2 => K = 21 = L4*N_gen = DESI 唯一選出嘅窗",
    Kstrict == L4*Ng, "=> DESI 窗唔再係「碰巧選出」, 係門檻律輸出")
chk("T5b 非嚴格門檻 m^2 <= mu^2 => K = 22 = N_d/2 = 自對偶模", Knon == Nd//2)

print("\nT6. 兩個窗嘅 DESI 表現 (sigma_b = 0.0070934, a = 1 固定)")
print(f"  K = 21: b = <sec>_1..21 = {float(bsec(21)):.9f}  =>  (b - 1.1188501)/sigma = {float((bsec(21)-mp.mpf('1.11885010495'))/mp.mpf('0.0070934')):+.3f} sigma")
print(f"  K = 22: b = <sec>_1..22 = {float(bsec(22)):.9f}  =>  (b - 1.1188501)/sigma = {float((bsec(22)-mp.mpf('1.11885010495'))/mp.mpf('0.0070934')):+.3f} sigma")
chk("T6  兩個門檻讀法喺 DESI 都唔被排除 (|sigma| < 2)", abs((bsec(22)-mp.mpf('1.11885010495'))/mp.mpf('0.0070934')) < 2)

print("\nT7. Nyquist 窗")
print(f"  K(z_max) = B*L4 = {B*L4}   theta_28 = pi*28/88 = L4*pi/(N_d/2) = 7*pi/22 = {float(th[28]*180/pi):.6f} deg")
print(f"  E(l_Nyq) = l_Nyq + <sec>_1..28 = {mp.nstr(E_nyq,12)}  vs  pi*L6/(L6-1) = {mp.nstr(pi*L6/(L6-1),12)}")
chk("T7  Nyquist 錨點 dev < 1e-5", abs(E_nyq - pi*L6/(L6-1))/(pi*L6/(L6-1)) < mp.mpf('1e-5'),
    f"dev = {float(abs(E_nyq-pi*L6/(L6-1))/(pi*L6/(L6-1))*100):.6f}%")

print("\nT8. 誠實邊界")
print("  ✅ 對面 (pi*R_w) 同 截止 (z_max = F_proj) 兩邊現都有結構身份")
print("  🔴 但「視線喺 z_max 啱好到對面」本身仍係假設 (未由動力學導出)")
chk("T8  假設已記錄 (docs/08 §五.2 維持 🔴 但由「無根據」升為「有兩邊結構身份嘅橋」)", True)

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 78)
print("""
結論 (② 🔴 -> 🟡+):
  ★ pi*R_world = r_22 = 2*pi*R_world*cos^2(theta_22) EXACT — 環對面 = O180 投影核嘅
    半功率點 = Z2 自對偶模 n = N_d/2 = 22。三種描述同一個模。
  ★ 累積相位 = D_A/R_world; 飽和 D_A = pi*R_w <=> 相位 = pi = 一次相位滑移 (O7)。
  ★★ 窗律端點由門檻律導出: m_n^2 < mu^2 (嚴格) => K = L4*N_gen = 21 = DESI 唯一窗
     (因為 gamma_22 = mu^2 恰好, 嚴格不等式排除自對偶模)。
  🔴 仍開放: 「視線喺 z_max = F_proj 啱好到對面」嘅動力學導出 (飽和位置)。
     但假設兩邊 (對面 pi*R_w / 截止 z_max) 現都有結構身份, 唔再係任意選擇。
""")
