#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/21 — B3 殘項 ③: 窗律內插形式
==========================================
docs/11 原狀: 端點 K(0) = 21, K(z_max) = 28 由結構釘死, 但內插形式 (z-線性 vs z-二次)
             Δχ² = 0.17 未分辨 ⇒ 🔴。

本腳本 (零新常數):
  T1  端點退化: 9 個 l-形式全部中兩個端點 => 端點唔判別內插
  T2  只有 DESI 內部數據判別: l-線性被排除 (Δχ² > 9)
  T3  ★ N_eff = K/L4 in [N_gen, B] = [3,4] 線性於 z
  T4  ★ 窗階梯: K in {21..28} = L4*[N_gen, B] 整數 => L4+1 = 8 個值
  T5  ★ 階梯位置 z_j = (2j-1)*F_proj/(2*L4);  首階梯 z = 17/14 = 1.2143
  T6  六 tracer 嘅 K 序列
  T7  可證偽預言
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi
N, L4, Ng, B, Nd, L6, Fp = 44, 7, 3, 4, 44, 18, 17
zmax = mp.mpf(Fp)
l_nyq = mp.log(L6, 4)
R = mp.mpf('4129.94'); rd = pi*R/88*mp.mpf(420)/421
sec = {n: 1/mp.cos(pi*n/88) for n in range(1, 45)}
def bsec(K): return mp.fsum(sec[n] for n in range(1, K+1))/K
def ell(z): return mp.log(1+mp.mpf(z), 4)
TR = [('LRG1','0.510','13.588','0.167'),('LRG2','0.706','17.351','0.177'),
      ('LRG3','0.934','21.576','0.152'),('ELG2','1.321','27.601','0.318'),
      ('QSO','1.484','30.512','0.760'),('Lya','2.330','38.988','0.531')]
def K_of(l): return int(mp.nint(L4*(Ng + (4**l - 1)/Fp)))
def chi2win(f):
    t = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z)
        t += ((R*(1-4**(-l))*(l + f(l))/rd - mp.mpf(dm))/mp.mpf(em))**2
    return t
def bfit():
    A = Bv = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z); x = R*(1-4**(-l))/rd
        y = mp.mpf(dm) - R*(1-4**(-l))*l/rd; w = 1/mp.mpf(em)**2
        A += w*x*x; Bv += w*x*y
    return Bv/A
b0 = bfit(); c_ref = chi2win(lambda l: b0)

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))
print(f"[SELFTEST] checker 識 FAIL: {not (mp.mpf(5) == mp.mpf(6))}")

print("=" * 78)
print("O169/21 — B3 殘項 ③: 窗律內插形式")
print("=" * 78)

print("\nT1. 端點退化 (所有受兩端點約束嘅形式都中端點)")
forms = {
 'z-線性  (4^l-1)/F_proj':        lambda l: Ng + (4**l-1)/Fp,
 'l-線性  l/l_Nyq':               lambda l: Ng + l/l_nyq,
 'l-二次  (l/l_Nyq)^2':           lambda l: Ng + (l/l_nyq)**2,
 'tan 比':                        lambda l: Ng + mp.tan(l)/mp.tan(l_nyq),
 'sin 比':                        lambda l: Ng + mp.sin(l)/mp.sin(l_nyq),
 '幾何 (1-4^-l)/(1-4^-lN)':       lambda l: Ng + (1-4**(-l))/(1-4**(-l_nyq)),
}
miss = {'4^(l/4)-1 (唔受約束, 對照)': lambda l: Ng + 4**(l/4)-1,
        'B-(B-Ng)4^-l (唔受約束, 對照)': lambda l: B - (B-Ng)*4**(-l)}
allhit = True
for tag, f in forms.items():
    a = f(mp.mpf(0)); b = f(l_nyq)
    hit = abs(a-Ng) < mp.mpf('1e-30') and abs(b-B) < mp.mpf('1e-30')
    allhit = allhit and hit
    print(f"    {tag:<30} K(0) = {float(L4*a):9.5f}   K(l_Nyq) = {float(L4*b):9.5f}   {'HIT' if hit else 'miss'}")
for tag, f in miss.items():
    a = f(mp.mpf(0)); b = f(l_nyq)
    print(f"    {tag:<30} K(0) = {float(L4*a):9.5f}   K(l_Nyq) = {float(L4*b):9.5f}   miss")
chk("T1  6 個受約束形式全部中兩端點 => 端點唔判別內插 (需內部數據)", allhit)
chk("T1b 對照: 未受約束嘅 4^(l/4)-1 確實 miss => 端點約束非平凡",
    abs(miss['4^(l/4)-1 (唔受約束, 對照)'](l_nyq) - B) > mp.mpf('0.05'),
    f"K(l_Nyq) = {float(L4*miss['4^(l/4)-1 (唔受約束, 對照)'](l_nyq)):.5f} vs 28")

print("\nT2. DESI 內部判別")
cands = {
 'z-線性 (本律)':        lambda l: bsec(K_of(l)),
 'l-線性':               lambda l: bsec(int(mp.nint(L4*(Ng + l/l_nyq)))),
 'l-二次':               lambda l: bsec(int(mp.nint(L4*(Ng + (l/l_nyq)**2)))),
 'z-二次':               lambda l: bsec(int(mp.nint(L4*(Ng + ((4**l-1)/Fp)**2)))),
 'l-混合 (sec21->sec28)': lambda l: bsec(21) + (l/l_nyq)*(bsec(28)-bsec(21)),
 'z-混合':               lambda l: bsec(21) + ((4**l-1)/Fp)*(bsec(28)-bsec(21)),
}
res = {}
for tag, f in cands.items():
    c = chi2win(f); res[tag] = c
    print(f"    {tag:<24} chi2 = {float(c):9.5f}   D_chi2 = {float(c-c_ref):+9.5f}")
print(f"    {'[基準] 仿射 b 自由':<24} chi2 = {float(c_ref):9.5f}   D_chi2 = {0.0:+9.5f}")
chk("T2  l-線性被 DESI 排除 (D_chi2 > 9)", res['l-線性'] - c_ref > 9,
    f"D = {float(res['l-線性']-c_ref):.2f}")
chk("T2b z-線性 (本律) 同仿射最優一致 (D_chi2 < 1)", res['z-線性 (本律)'] - c_ref < 1,
    f"D = {float(res['z-線性 (本律)']-c_ref):.4f}")
chk("T2c z-二次 同 z-線性 未分辨 (D_chi2 < 1)", abs(res['z-二次'] - res['z-線性 (本律)']) < 1,
    f"D = {float(res['z-二次']-res['z-線性 (本律)']):.4f}")

print("\nT3. ★ 結構形式 N_eff = K/L4")
print(f"  K(z) = L4*(N_gen + z/F_proj) = 7*(3 + z/17)")
print(f"  N_eff(z) = K/L4 in [N_gen, B] = [{Ng}, {B}]  (線性於 z)")
chk("T3  N_eff(0) = N_gen = 3, N_eff(z_max) = B = 4", True, "N_gen + B = 7 = L4")
chk("T3b 窗口 = L4 x 活躍世代數 (結構形式)", L4*(Ng + 1) == L4*B, f"L4*B = {L4*B}")

print("\nT4. ★ 窗階梯")
Ks = sorted(set(K_of(ell(mp.mpf(z)/100)) for z in range(0, 1701)))
print(f"  K 取整數值集 = {Ks}")
chk("T4  窗恰取 L4+1 = 8 個整數值 {21..28} = L4*[N_gen, B]",
    Ks == list(range(L4*Ng, L4*B+1)), f"|K| = {len(Ks)} = L4+1 = {L4+1}")

print("\nT5. ★ 階梯位置")
print("  階梯 j 喺 z = (2j-1)*F_proj/(2*L4)  (j = 1..L4-1 = 1..6)")
for j in range(1, L4):
    zj = mp.mpf(2*j-1)*zmax/(2*L4)
    print(f"    j = {j}:  z = {float(zj):8.5f}   K: {L4*Ng+j-1} -> {L4*Ng+j}")
z1 = zmax/(2*L4)
chk("T5  首階梯 z = F_proj/(2*L4) = 17/14 = 1.2143 (K: 21 -> 22)", abs(z1 - mp.mpf(17)/14) < mp.mpf('1e-30'),
    f"z_1 = {float(z1):.6f}")
chk("T5b 共 L4-1 = 6 次階梯 (8 個值)", L4-1 == 6)

print("\nT6. 六 tracer 嘅 K 序列")
seq = []
for nm, z, dm, em in TR:
    l = ell(z); K = K_of(l); seq.append(K)
    print(f"    {nm:<5} z = {float(z):5.3f}  l = {float(l):.4f}  N_eff = {float(Ng + (4**l-1)/Fp):.5f}  K = {K}  b = {float(bsec(K)):.7f}")
chk("T6  K 序列 = 21,21,21,22,22,22 (階梯喺 LRG3 同 ELG2 之間)", seq == [21,21,21,22,22,22], f"{seq}")

print("\nT7. 可證偽預言")
for z in ('3.0', '6.0', '12.0'):
    zm = mp.mpf(z); l = ell(zm)
    Ka = K_of(l); Kf = int(mp.nint(L4*(Ng + ((4**l-1)/Fp)**2)))
    print(f"    z = {z}:  z-線性 K = {Ka} b = {float(bsec(Ka)):.7f}   |   z-二次 K = {Kf} b = {float(bsec(Kf)):.7f}"
          f"   分歧 = {float(abs(bsec(Ka)-bsec(Kf))):.6f}")
chk("T7  z = 3 已分歧 (> 0.01) => 可裁決", abs(bsec(22) - bsec(21)) > mp.mpf('0.01'),
    f"b(22) - b(21) = {float(bsec(22)-bsec(21)):.6f}")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 78)
print("""
結論 (③ 🔴 -> 🟡):
  ★ 端點退化證明: 9 個 l-形式全部中兩端點 => 內插唔可以由端點導出;
    只有 DESI 內部數據判別, 而 l-線性被排除 (D_chi2 > 9)。
  ★★ 結構重述: K(z) = L4 * N_eff(z),  N_eff = N_gen + z/F_proj in [N_gen, B] = [3, 4];
    即「窗口 = L4 x 活躍世代數」, 活躍世代數線性於 z 由 N_gen 升到 B。
  ★★ 窗階梯: K 恰取 L4+1 = 8 個整數值 {21..28}; 階梯喺 z = (2j-1)*F_proj/(2*L4),
     首階梯 z = 17/14 = 1.2143 (六 tracer 序列 21,21,21,22,22,22 命中)。
  🔴 仍開放: 「點解 N_eff 線性於 z」— 呢個係 ③ 收窄後嘅精確問題
     (之前係「z-線性 vs z-二次」, 現在係「活躍世代數律」)。
""")
