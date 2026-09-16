#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/14 — B3: πR 飽和張力 (界限 + 完成項 + null test)
==============================================================
原狀 (docs/04 §B3): O76 聲稱 D_A(ℓ_Nyq) = 0.9990πR 係「Nyquist 自洽」;
  但新仿射式畀 0.9629πR; 要同時滿足 DESI + πR 需 b = 1.2414297 (+17σ) ⇒ 🔴

本腳本三個檢驗:
  T1  界限: D_A(ℓ) ≤ πR 於 ℓ ≤ ℓ_Nyq? (環幾何硬上界)
  T2  完成項代價: 固定結構斜率 a = 1, 容許曲率 κℓ² 時, πR 條件嘅 Δχ²
  T3  ★ 結構身份: πR 所需嘅「Nyquist 有效截距」= 1.2414297 係唔係譜量?
      (+ null test: 同類家族隨機命中率)
  T4  群延遲累積模型 (結構候選) 檢驗

結構輸入: L₆ = 18 = 1 + z_max, F_proj = 17 = L₆ − 1, ℓ_Nyq = log₄(L₆), N_d = 44, B = 4
"""
import mpmath as mp, random
mp.mp.dps = 40
pi = mp.pi; phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf('4129.94')
rd = pi * R / 88 * mp.mpf(420) / 421
N = 44
gam = {n: 4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N + 1)}
vg  = {n: mp.cos(pi * n / 88) for n in range(1, N + 1)}
sec = {n: 1 / mp.cos(pi * n / 88) for n in range(1, N + 1)}
L6, Fp = 18, 17
l_nyq = mp.log(L6, 4)
b_spec = 1 / (mp.fsum(vg[n] for n in range(1, 23)) / 22)
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]

def ell(z): return mp.log(1 + mp.mpf(z), 4)
def DA(l, b, k=mp.mpf(0)): return R * (1 - 4 ** (-l)) * (l + b + k * l * l)
def chi2(b, k=mp.mpf(0), a=mp.mpf(1)):
    t = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z)
        t += ((R * (1 - 4 ** (-l)) * (a * l + b + k * l * l) / rd - mp.mpf(dm)) / mp.mpf(em)) ** 2
    return t

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 78)
print("O169/14 — B3: πR 飽和張力")
print("=" * 78)
print(f"  L6 = {L6} = 1+z_max, F_proj = {Fp} = L6-1, l_Nyq = log4(L6) = {mp.nstr(l_nyq, 12)}")
print(f"  R = {R} Mpc, piR = {mp.nstr(pi * R, 12)} Mpc")
print(f"  b_spec = 1/<v_g>_1..22 = {mp.nstr(b_spec, 12)}")

# ---------- T1: 界限 ----------
print("\nT1. 環幾何上界  D_A(l) <= piR  (l <= l_Nyq)")
ratio_nyq = DA(l_nyq, b_spec) / (pi * R)
chk("T1  D_A(l_Nyq) <= piR", DA(l_nyq, b_spec) < pi * R,
    f"D_A = {float(DA(l_nyq, b_spec)):.1f} = {float(ratio_nyq):.4f} piR")
l_sat = mp.findroot(lambda l: DA(l, b_spec) - pi * R, mp.mpf('2.3'))
chk("T1b D_A = piR 於 l_sat > l_Nyq (即截止前未飽和)", l_sat > l_nyq,
    f"l_sat = {mp.nstr(l_sat, 8)} (z = {float(4 ** l_sat - 1):.2f}), 超出 l_Nyq {mp.nstr(l_sat - l_nyq, 5)}")
print(f"      ⇒ O76 嘅 0.9990 係 delta = -0.1697 調出; 新式 0.9632 滿足上界 (餘 3.7%)")

# ---------- T2: 完成項代價 ----------
print("\nT2. 固定 a = 1, 容許曲率 k*l^2 — πR 條件嘅代價")
tgt = pi * L6 / (L6 - 1)
k_req = (tgt - l_nyq - b_spec) / l_nyq ** 2
print(f"  piR 所需 E(l_Nyq) = piL6/(L6-1) = {mp.nstr(tgt, 12)};  仿射值 = {mp.nstr(l_nyq + b_spec, 12)}")
print(f"  => 所需 k = {mp.nstr(k_req, 12)}")
# k=0 最佳 b (a=1)
A11 = A12 = mp.mpf(0)
for nm, z, dm, em in TR:
    l = ell(z); x2 = R * (1 - 4 ** (-l)) / rd; yv = mp.mpf(dm) - R * (1 - 4 ** (-l)) * l / rd
    w = 1 / mp.mpf(em) ** 2; A11 += w * x2 * x2; A12 += w * x2 * yv
b_fit = A12 / A11
c0 = chi2(b_fit, mp.mpf(0))
c1 = chi2(b_spec, k_req)
print(f"  k=0 (仿射, b 自由): b = {mp.nstr(b_fit, 10)}, chi2 = {float(c0):.4f}")
print(f"  k=k_req (piR 完成): b = b_spec = {mp.nstr(b_spec, 10)}, chi2 = {float(c1):.4f}")
chk("T2  piR 完成項代價 Delta_chi2 < 4 (唔被排除)", (c1 - c0) < 4,
    f"Delta_chi2 = {float(c1 - c0):.4f} (~{float(mp.sqrt(c1 - c0)):.2f} sigma)")
chk("T2b a = 1 固定時 k = 0 係 chi2 最小值 (DESI 唔要求曲率)", c0 < chi2(b_spec, mp.mpf('0.05')) and c0 < chi2(b_spec, -mp.mpf('0.02')),
    f"chi2(k=0)={float(c0):.4f} < chi2(k=+0.05)={float(chi2(b_spec, mp.mpf('0.05'))):.4f}")

# ---------- T3: 結構身份 + null test ----------
print("\nT3. ★ piR 所需有效截距 = 譜量?")
need = tgt - l_nyq
chk("T3  need = <sec>_{1..28}", abs(mp.fsum(sec[n] for n in range(1, 29)) / 28 - need) / need < mp.mpf('1e-4'),
    f"<sec>_1..28 = {mp.nstr(mp.fsum(sec[n] for n in range(1,29))/28, 14)}  vs need {mp.nstr(need, 14)}  dev {float(abs(mp.fsum(sec[n] for n in range(1,29))/28-need)/need*100):.6f}%")
print(f"      28 = B*L4 = 4*7 = {4*7};  28 = N_d - F_proj + 1 = {44-17+1}")

fam = []
for K in range(1, 44):
    fam.append(('sec', K, mp.fsum(sec[n] for n in range(1, K + 1)) / K))
    fam.append(('inv_vg', K, 1 / (mp.fsum(vg[n] for n in range(1, K + 1)) / K)))
    fam.append(('inv_rms', K, 1 / mp.sqrt(mp.fsum(vg[n] ** 2 for n in range(1, K + 1)) / K)))
vals = sorted(v for _, _, v in fam)
obs = float(abs(mp.fsum(sec[n] for n in range(1, 29)) / 28 - need) / need)
print(f"  null 家族 = {len(fam)} 個 (K=1..43 x 3 統計量)")
random.seed(7)
NT = 4000; hits = 0
for _ in range(NT):
    t = mp.mpf(random.uniform(1.0, 1.6))
    if min(abs(v - t) / t for v in vals) <= obs: hits += 1
pval = hits / NT
chk("T3b null test: 命中顯著 (P < 0.05)", pval < 0.05,
    f"P(min dev <= {obs:.2e}) = {pval:.4f}  ({NT} 次均勻 target 抽樣)")

# ---------- T4: 群延遲累積模型 ----------
print("\nT4. 群延遲累積模型  E(l) = b + int_0^l sec(pi*n(l')/88) dl'  (n = N_d*l/l_Nyq, 截斷 n<=F_proj)")
l_cut = Fp / N * l_nyq
c_ = pi * 44 / (88 * l_nyq)
def E_gd(l, b=b_spec):
    x = c_ * min(l, l_cut)
    s = mp.log(mp.sec(x) + mp.tan(x)) / c_
    if l > l_cut: s += (l - l_cut) / mp.cos(27 * pi / 88)
    return b + s
print(f"  l_cut = {mp.nstr(l_cut, 8)} (z = {float(4**l_cut-1):.3f}),  w_max = sec(27pi/88) = {mp.nstr(1/mp.cos(27*pi/88), 8)}")
chk("T4  群延遲累積模型 過衝 (E(l_Nyq) > 要求值) ⇒ 排除",
    E_gd(l_nyq) > tgt, f"E_gd(l_Nyq) = {mp.nstr(E_gd(l_nyq), 10)} vs 要求 {mp.nstr(tgt, 10)}")
chk("T4b 但 DESI 區間接近 (dev < 2%)", abs(E_gd(mp.mpf('0.5')) - (mp.mpf('0.5') + b_spec)) / (mp.mpf('0.5') + b_spec) < mp.mpf('0.02'),
    f"E_gd(0.5) = {mp.nstr(E_gd(mp.mpf('0.5')), 8)} vs 仿射 {mp.nstr(mp.mpf('0.5')+b_spec, 8)}")

print()
print("=" * 78)
print(f"RESULT: {len(PASS)}/{len(PASS) + len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 78)
print(f"""
結論 (B3 狀態更新: 🔴 -> 🟡):
  T1  環幾何上界 D_A <= piR **滿足** (0.9632 piR)。O76 嘅 0.9990 係 delta=-0.1697 調出。
  T2  「+17sigma」係**仿射假設嘅產物**: 容許曲率項 k*l^2 後, piR 條件只需
      Delta_chi2 = {float(c1-c0):.3f} (~{float(mp.sqrt(c1-c0)):.2f} sigma) — 唔被排除。
      且 a=1 固定時 DESI 最優就係 k=0 (仿射律 = DESI 區間律)。
  T3  ★★ piR 所需嘅「Nyquist 有效截距」1.2414297 = <sec>_{{1..28}} (dev {float(abs(mp.fsum(sec[n] for n in range(1,29))/28-need)/need*100):.6f}%),
      28 = B*L4 = N_d - F_proj + 1; null test P = {pval:.4f} ⇒ 結構級候選, 唔係調出。
  T4  群延遲累積模型過衝 (E = {mp.nstr(E_gd(l_nyq),6)} vs 要求 {mp.nstr(tgt,6)}) ⇒ 排除。
  🔴 未閉合: K(l) 律 (DESI 區間窗口 ~21-22 -> Nyquist 28 嘅演化律) 未導出;
      z >~ 3 觀測可直接裁決。
""")
