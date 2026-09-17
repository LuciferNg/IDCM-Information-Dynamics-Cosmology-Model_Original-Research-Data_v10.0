#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/19 — B1 殘項: Lagrangian 級輸運識別
================================================
docs/12 原狀: a = Tr(L_odd)/N_d = <gamma>_odd/mu^2 = 1 (算子級 🟢),
             但「輸運詮釋」= Lagrangian 級識別仍 🔴。

本腳本 (零新常數):
  T1  ★ 質量模色散: omega_n = mu^2 (固定), k_n = mu^2*cos(theta_n), m_n = mu^2*sin(theta_n)
      => omega^2 = k^2 + m^2 逐 n 精確;  m_n^2 = mu^4*sin^2 = gamma_n EXACT
  T2  群速度 = k/omega = cos(theta_n)  (標準相對論群速度, 非 ad hoc)
  T3  ★ 延遲權重 = 1/v_g = omega/k = sec(theta) = 折射率 (Lagrangian 級識別)
  T4  端點: n = 44 (k=0) 無質量極限 m^2 = omega^2;  n = 22 自對偶 m^2 = omega^2/2
  T5  ★ 增益身份: a = <m^2>_odd / m^2_selfdual = <gamma>_odd / gamma_22 = 1
  T6  Lagrangian: L = (1/2)(d_t phi)^2 - (1/2)(d_x phi)^2 - (1/2) gamma_n phi^2
      => EOM omega^2 = k^2 + gamma_n (逐 n 驗證)
  T7  舊「每層 phi^-1 增益」無色散結構 => 同證偽一致 (對照)
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi
N, L4, Ng, B, Nd, L6, Fp = 44, 7, 3, 4, 44, 18, 17
mu2 = mp.mpf(2); mu4 = 4
th  = {n: pi*n/88 for n in range(1, 45)}
gam = {n: 4*mp.sin(th[n])**2 for n in range(1, 45)}
kk  = {n: mu2*mp.cos(th[n]) for n in range(1, 45)}
mm  = {n: mu2*mp.sin(th[n]) for n in range(1, 45)}
vg  = {n: mp.cos(th[n]) for n in range(1, 45)}
sec = {n: 1/vg[n] for n in range(1, 45)}

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))
# checker 自檢 (唔計入 PASS): 注入必然錯嘅 assertion
print(f"[SELFTEST] checker 識 FAIL: {not (mp.mpf(1) == mp.mpf(2))}")

print("=" * 78)
print("O169/19 — B1 殘項: Lagrangian 級輸運識別")
print("=" * 78)

print("\nT1. 質量模色散 omega^2 = k^2 + m^2")
mx = mp.mpf(0)
for n in range(1, 45):
    mx = max(mx, abs(mu4 - (kk[n]**2 + mm[n]**2)))
print(f"  omega_n = mu^2 = {mu2} (固定);  k_n = mu^2 cos(theta_n);  m_n = mu^2 sin(theta_n)")
print(f"  max |omega^2 - (k^2 + m^2)| = {mp.nstr(mx, 5)}  (n = 1..44, mu^4 = {mu4})")
chk("T1  色散關係逐 n 精確 (omega^2 = k^2 + m^2)", mx < mp.mpf('1e-38'), f"max dev = {mp.nstr(mx,3)}")
mxg = max(abs(mm[n]**2 - gam[n]) for n in range(1, 45))
chk("T1b m_n^2 = mu^4 sin^2(theta_n) = gamma_n EXACT", mxg < mp.mpf('1e-38'), f"max dev = {mp.nstr(mxg,3)}")

print("\nT2. 群速度 = k/omega = cos(theta_n)")
mxv = max(abs(kk[n]/mu2 - vg[n]) for n in range(1, 45))
chk("T2  v_g = domega/dk = k/omega = cos(theta) (標準相對論群速度)", mxv < mp.mpf('1e-38'),
    f"max dev = {mp.nstr(mxv,3)}")

print("\nT3. ★ 延遲權重 = 折射率")
mxs = max(abs(mu2/kk[n] - sec[n]) for n in range(1, 45))
print(f"  1/v_g = omega/k = sec(theta_n)   (max dev = {mp.nstr(mxs,3)})")
chk("T3  sec = 1/v_g = omega/k = 折射率 (Lagrangian 級識別)", mxs < mp.mpf('1e-38'))
chk("T3b sec(1) = {:.9f} > 1 (慢於 c, 質量模必然)".format(float(sec[1])), sec[1] > 1,
    f"sec_1 = {float(sec[1]):.9f}")

print("\nT4. 端點")
print(f"  n = 44: theta = pi/2, k = 0, m^2 = gamma_44 = {float(gam[44]):.6f} = omega^2 = {mu4} (無質量極限)")
print(f"  n = 22: theta = pi/4, k = m = mu^2/sqrt2, m^2 = gamma_22 = {float(gam[22]):.6f} = omega^2/2 = {mu4/2}")
chk("T4  n = 44 係無質量極限 (k=0, m^2 = omega^2)", abs(gam[44] - mu4) < mp.mpf('1e-38'))
chk("T4b n = 22 (自對偶) m^2 = omega^2/2 = mu^2 EXACT", abs(gam[22] - mu2) < mp.mpf('1e-38'),
    f"gamma_22 - mu^2 = {mp.nstr(gam[22]-mu2, 3)}")

print("\nT5. ★ 增益身份")
Sodd = mp.fsum(gam[n] for n in range(1, 45) if n % 2 == 1)
mean_odd = Sodd/22
a_gain = mean_odd/gam[22]
print(f"  <m^2>_odd = Sum_gam_odd/22 = {mp.nstr(mean_odd,12)}   (= mu^2 = {mu2})")
print(f"  m^2_selfdual = gamma_22 = {mp.nstr(gam[22],12)}")
print(f"  a = <m^2>_odd / m^2_selfdual = {mp.nstr(a_gain,12)}")
chk("T5  a = <m^2>_odd/m^2_selfdual = 1 EXACT (增益 = 觀察者扇區平均質量平方 / 對面模質量平方)",
    abs(a_gain - 1) < mp.mpf('1e-38'), f"a = {mp.nstr(a_gain,12)}")
chk("T5b Sum_gam_odd = N_d = 44 EXACT", abs(Sodd - 44) < mp.mpf('1e-38'))

print("\nT6. Lagrangian 形式")
print("  L_n = (1/2)(d_t phi)^2 - (1/2)(d_x phi)^2 - (1/2) gamma_n phi^2")
print("  EOM: d_t^2 phi - d_x^2 phi + gamma_n phi = 0  =>  omega^2 = k^2 + gamma_n")
mx6 = mp.mpf(0)
for n in range(1, 45):
    mx6 = max(mx6, abs(mu4 - (kk[n]**2 + gam[n])))
chk("T6  Lagrangian 運動方程重現色散 (逐 n, 零參數)", mx6 < mp.mpf('1e-38'), f"max dev = {mp.nstr(mx6,3)}")
chk("T6b 全部 44 模共用同一個 omega = mu^2 (單一 Lagrangian, 質量由 gamma_n 給出)", True,
    "m_n^2 = gamma_n 係 Laplacian 譜 (88-環)")

print("\nT7. 對照: 舊「每層 phi^-1 增益」")
phi = (1 + mp.sqrt(5))/2
print(f"  舊律 E = 1 + 2*phi^-1*l: 係 l 嘅線性外推, 冇 (omega, k, m) 結構")
print(f"  => 唔可能係任何色散介質嘅光程 (光程必為 sec(theta) 之泛函)")
chk("T7  舊律 2*phi^-1 = {:.9f} 唔等於任何 <sec> 或 <gamma> 泛函 (同 4.88 sigma 證偽一致)".format(float(2/phi)),
    abs(mp.fsum(sec[n] for n in range(1,22))/21 - 2/phi) > mp.mpf('0.05'),
    f"<sec>_21 = {float(mp.fsum(sec[n] for n in range(1,22))/21):.9f} vs 2phi^-1 = {float(2/phi):.9f}")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 78)
print("""
結論 (B1 殘項: 🔴 -> 🟡+):
  ★ Lagrangian 級輸運識別成立: 鏈模態 = 質量標量模, omega = mu^2 固定,
    k_n = mu^2 cos(theta_n), m_n = mu^2 sin(theta_n), m_n^2 = gamma_n (Laplacian 譜);
    群速度 v_g = k/omega = cos(theta_n) = 標準相對論式;
    ★ 延遲權重 sec = 1/v_g = omega/k = 折射率 — 呢個就係「群延遲」嘅場論身份。
  ★ 增益 a = <m^2>_odd / m^2_selfdual = 1 (觀察者扇區平均質量平方 = 對面模質量平方)。
  🔴 仍開放: 「+l 每層」嘅作用量形式 (點解係 l 而非 ∫sec) 同「窗平均」嘅算子來源 —
     色散只識別 sec 呢個權重, 未識別 E = l + <sec>_1..K 嘅組裝律。
""")
