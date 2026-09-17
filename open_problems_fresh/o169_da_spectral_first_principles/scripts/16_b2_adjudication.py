#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/16 — B2: 截距讀法裁決 (三族 vs 獨立 piR/Nyquist 條件)
====================================================================
docs/09 原狀: 三方簡併 (sec_1..21 / 1-vg_1..22 / sqrt5/2), Delta_chi2 = 0.0119
              => DESI 單獨完全不可分辨, 裁決需靠獨立條件。

本腳本用**獨立於 DESI 擬合**嘅條件裁決:
  環幾何對面條件: D_A(l_Nyq) = piR  <=>  (1-4^-l_Nyq)(l_Nyq + b_eff) = pi
  結構輸入: L6 = 18 = 1+z_max, F_proj = 17 = L6-1, l_Nyq = log4(L6)
  => 所需有效截距 need = pi*L6/(L6-1) - l_Nyq

T1  三族喺 need 嘅表現 (需整數窗 K)
T2  DESI chi2 (6 D_M) 三方對照 (確認簡併)
T3  雙錨點表: E(1/2) vs phi ; E(l_Nyq) vs pi*L6/(L6-1)
T4  phi 錨點係否恆等式 (tautology) + 佢依賴已證偽舊律
T5  sqrt5/2 唔屬 sec 家族 (最近 K 嘅 dev)

結構常數: L4 = 7, N_gen = 3, B = 4, N_d = 44
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi; phi = (1 + mp.sqrt(5))/2; inv = 1/phi
R = mp.mpf('4129.94'); rd = pi*R/88*mp.mpf(420)/421
N, L4, Ng, B, L6, Fp = 44, 7, 3, 4, 18, 17
l_nyq = mp.log(L6, 4)
tgt   = pi*L6/(L6-1)          # 3.3263922... 所需 E(l_Nyq)
need  = tgt - l_nyq           # 1.2414297... 所需有效截距
vg  = {n: mp.cos(pi*n/88) for n in range(1, N+1)}
sec = {n: 1/mp.cos(pi*n/88) for n in range(1, N+1)}
def bsec(K): return mp.fsum(sec[n] for n in range(1, K+1))/K
def binv(K): return 1/(mp.fsum(vg[n] for n in range(1, K+1))/K)
b_phi = inv + mp.mpf(1)/2     # sqrt5/2 = phi - 1/2
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]
def ell(z): return mp.log(1 + mp.mpf(z), 4)
def chi2DM(b):
    t = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z)
        t += ((R*(1 - 4**(-l))*(l + b)/rd - mp.mpf(dm))/mp.mpf(em))**2
    return t
def bfit():
    A = Bv = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z); x = R*(1 - 4**(-l))/rd
        y = mp.mpf(dm) - R*(1 - 4**(-l))*l/rd; w = 1/mp.mpf(em)**2
        A += w*x*x; Bv += w*x*y
    return Bv/A

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 80)
print("O169/16 — B2: 截距讀法裁決 (三族 vs 獨立 piR/Nyquist 條件)")
print("=" * 80)
print(f"  L6 = {L6} = 1+z_max, F_proj = {Fp}, l_Nyq = log4(L6) = {mp.nstr(l_nyq, 14)}")
print(f"  所需 E(l_Nyq) = piL6/(L6-1) = {mp.nstr(tgt, 14)}")
print(f"  所需有效截距 need = {mp.nstr(need, 14)}")
print(f"  三方候選: sec_1..21 = {mp.nstr(bsec(21),12)} | 1/vg_1..22 = {mp.nstr(binv(22),12)} | sqrt5/2 = {mp.nstr(b_phi,12)}")

# ---------- T1 ----------
print("\nT1. 三族喺 need 嘅表現 (整數窗 K = 1..43)")
dev_sec = min((abs(bsec(K) - need)/need, K) for K in range(1, 44))
dev_inv = min((abs(binv(K) - need)/need, K) for K in range(1, 44))
print(f"  sec   家族: 最佳 K = {dev_sec[1]}  dev = {float(dev_sec[0]*100):.7f}%   (K=28 dev = {float(abs(bsec(28)-need)/need*100):.7f}%)")
print(f"  inv_vg家族: 最佳 K = {dev_inv[1]}  dev = {float(dev_inv[0]*100):.5f}%   (無整數 K 命中)")
print(f"  phi   家族: 常數 {mp.nstr(b_phi,10)} — 無論如何達唔到 {mp.nstr(need,10)}")
chk("T1  sec 家族有整數窗命中 need (dev < 1e-4)", dev_sec[0] < mp.mpf('1e-4'),
    f"K = {dev_sec[1]}, dev = {float(dev_sec[0]*100):.7f}%")
chk("T1b inv_vg 家族冇整數窗命中 (dev > 1e-3)", dev_inv[0] > mp.mpf('1e-3'),
    f"最佳 dev = {float(dev_inv[0]*100):.5f}%")
chk("T1c phi 家族結構上不可能 (常數 vs 1.24)", abs(b_phi - need) > mp.mpf('0.1'),
    f"|sqrt5/2 - need| = {float(abs(b_phi-need)):.6f}")

# ---------- T2 ----------
print("\nT2. DESI chi2 (6 D_M, a = 1 固定) — 確認簡併")
rows = [("sec_1..21", bsec(21)), ("1/vg_1..22", binv(22)), ("sqrt5/2", b_phi)]
c2s = []
for tag, b in rows:
    c = chi2DM(b); c2s.append(c)
    print(f"  {tag:<12} b = {mp.nstr(b,12)}  chi2 = {float(c):.6f}")
c_min, c_max = min(c2s), max(c2s)
print(f"  Delta_chi2(max-min) = {float(c_max-c_min):.6f}  ⇒ DESI 不可分辨")
chk("T2  DESI 三方簡併 (Delta_chi2 < 0.1)", (c_max - c_min) < mp.mpf('0.1'),
    f"Delta_chi2 = {float(c_max-c_min):.6f}")

# ---------- T3 ----------
print("\nT3. 雙錨點表 (常數截距律全部過唔到 Nyquist 錨點)")
print(f"  {'讀法':<16}{'E(1/2)':>14}{'vs phi':>11}{'E(l_Nyq)':>14}{'vs piL6/(L6-1)':>16}")
for tag, b in [("sec_1..21", bsec(21)), ("1/vg_1..22", binv(22)), ("sqrt5/2", b_phi),
               ("sec_1..28 (窗律)", bsec(28))]:
    E12 = mp.mpf(1)/2 + b; Eny = l_nyq + b
    print(f"  {tag:<16}{float(E12):>14.8f}{float(abs(E12-phi)/phi*100):>10.4f}%"
          f"{float(Eny):>14.8f}{float(abs(Eny-tgt)/tgt*100):>15.5f}%")
chk("T3  所有常數截距律都過唔到 Nyquist 錨點 (>1%)",
    all(abs(l_nyq + b - tgt)/tgt > mp.mpf('0.01') for _, b in rows))
chk("T3b 窗律 (K=28) 滿足 Nyquist 錨點 (dev < 1e-4)",
    abs(l_nyq + bsec(28) - tgt)/tgt < mp.mpf('1e-4'),
    f"dev = {float(abs(l_nyq+bsec(28)-tgt)/tgt*100):.6f}%")

# ---------- T4 ----------
print("\nT4. phi 錨點嘅地位")
E12_phi_from_b = mp.mpf(1)/2 + (phi - mp.mpf(1)/2)
chk("T4  E(1/2) = phi 對 phi 讀法係**恆等式** (b = phi - 1/2 ⇒ E(1/2) = phi)",
    abs(E12_phi_from_b - phi) < mp.mpf('1e-38'),
    f"E(1/2) = 1/2 + (phi-1/2) = {float(E12_phi_from_b):.12f} = phi (同義反覆)")
E_old_half = 1 + 2*inv*mp.mpf(1)/2
print(f"  該錨點嘅來源: 舊律 E_old(l) = 1 + 2phi^-1*l 於 l = 1/2 嘅值 = {float(E_old_half):.9f} = phi")
print(f"  但舊律已被 DESI D_M x6 排除 4.88 sigma ⇒ 錨點建基於已證偽式 (單點值)")
chk("T4b 舊律 l=1/2 值 = phi (錨點出處確認)", abs(E_old_half - phi) < mp.mpf('1e-38'))

# ---------- T5 ----------
print("\nT5. sqrt5/2 唔屬 sec 家族")
d5, K5 = min((abs(bsec(K) - b_phi)/b_phi, K) for K in range(1, 44))
print(f"  最近 K = {K5}, dev = {float(d5*100):.5f}%  (> 0.02% ⇒ 唔係家族成員)")
chk("T5  sqrt5/2 唔係任何 <sec>_K (最近 dev > 1e-4)", d5 > mp.mpf('1e-4'),
    f"最近 K = {K5}, dev = {float(d5*100):.5f}%")

print()
print("=" * 80)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 80)
print(f"""
結論 (B2 裁決):
  T1  **sec 家族唯一**可以喺整數窗下命中 πR/Nyquist 所需截距 {mp.nstr(need,10)}
      (K = 28, dev {float(dev_sec[0]*100):.7f}%); 1/vg 家族冇整數窗 (最佳 dev {float(dev_inv[0]*100):.5f}%);
      sqrt5/2 係常數, 結構上唔可能。
  T2  DESI 單獨三方簡併 (Delta_chi2 = {float(c_max-c_min):.6f}) — 與 docs/09 一致。
  T3  常數截距律全部過唔到 Nyquist 錨點 (差 3.7%); 只有窗律 (K 隨深度) 過得到。
  T4  phi 讀法嘅「E(1/2) = phi」係**參數化恆等式** (b = phi-1/2), 唔係獨立證據;
      而且佢建基於已證偽舊律嘅單點值。
  T5  sqrt5/2 唔屬 sec 家族 (最近 K dev {float(d5*100):.5f}%)。
  ⇒ **裁決: 譜 sec 家族 (窗律) 勝出** — 唯一同時滿足 DESI + πR/Nyquist 嘅讀法。
  🔴 殘餘: (i) πR/Nyquist 假設本身 (Nyquist 截止 = 環對面) 未由第一原理導出;
          (ii) E(1/2) 同 phi 嘅 0.02% 近簡併仍存在 (但屬湧現, 非構造)。
""")
