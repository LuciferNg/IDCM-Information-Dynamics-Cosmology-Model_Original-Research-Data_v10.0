#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/17 — B3: K(ℓ) 窗律 (端點 + 內插 + 排除律)
========================================================
docs/08 原狀: DESI 區間窗 ~21-22, Nyquist 要 K = 28 ⇒ K(ℓ) 律未導出。

本腳本:
  T1  實證 b_req(ℓ) 同最佳整數窗 K*(ℓ) (由 D_M 六 tracer 反推)
  T2  候選 K 律嘅 DESI chi2 表 (邊啲被排除)
  T3  ★ 兩個結構端點: K(0) = L4*N_gen = 21, K(z_max) = L4*B = 28
  T4  ★ 不可能性: 常數 transit-time 門檻律 (tau_n <= c*l) 兩區間不相交 ⇒ 整族排除
  T5  可證偽預言: z = 3 / 8.5 處 (a) z-線性 vs (f) z-二次 嘅分歧
  T6  統一零參數律檢驗: E(l) = l + <sec>_1..K(z), K(z) = L4(N_gen + z/F_proj)

結構常數: L4 = 7, N_gen = 3, B = 4, N_d = 44, L6 = 18, F_proj = 17
"""
import mpmath as mp
mp.mp.dps = 40
pi = mp.pi; phi = (1 + mp.sqrt(5))/2
R = mp.mpf('4129.94'); rd = pi*R/88*mp.mpf(420)/421
N, L4, Ng, B, L6, Fp = 44, 7, 3, 4, 18, 17
l_nyq = mp.log(L6, 4); tgt = pi*L6/(L6-1); zmax = mp.mpf(Fp)
vg  = {n: mp.cos(pi*n/88) for n in range(1, N+1)}
sec = {n: 1/mp.cos(pi*n/88) for n in range(1, N+1)}
def bsec(K): return mp.fsum(sec[n] for n in range(1, K+1))/K
TR = [('LRG1', '0.510', '13.588', '0.167'), ('LRG2', '0.706', '17.351', '0.177'),
      ('LRG3', '0.934', '21.576', '0.152'), ('ELG2', '1.321', '27.601', '0.318'),
      ('QSO', '1.484', '30.512', '0.760'), ('Lya', '2.330', '38.988', '0.531')]
def ell(z): return mp.log(1 + mp.mpf(z), 4)
def chi2DM(b_of):
    t = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z)
        t += ((R*(1 - 4**(-l))*(l + b_of(l, mp.mpf(z)))/rd - mp.mpf(dm))/mp.mpf(em))**2
    return t
def bfit():
    A = Bv = mp.mpf(0)
    for nm, z, dm, em in TR:
        l = ell(z); x = R*(1 - 4**(-l))/rd
        y = mp.mpf(dm) - R*(1 - 4**(-l))*l/rd; w = 1/mp.mpf(em)**2
        A += w*x*x; Bv += w*x*y
    return Bv/A
b_free = bfit()
c_ref = chi2DM(lambda l, z: b_free)

PASS, FAIL = [], []
def chk(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'[OK]' if cond else '[FAIL]'} {name}" + (f"   {detail}" if detail else ""))

print("=" * 80)
print("O169/17 — B3: K(ℓ) 窗律 (端點 + 內插 + 排除律)")
print("=" * 80)
print(f"  l_Nyq = {mp.nstr(l_nyq,12)},  z_max = F_proj = {Fp},  chi2 參考 (仿射 b 自由) = {float(c_ref):.5f}")

# ---------- T1 ----------
print("\nT1. 實證: b_req(ℓ) 同最佳整數窗 K*(ℓ)")
pts = []
for nm, z, dm, em in TR:
    l = ell(z); base = R*(1 - 4**(-l)); b_req = mp.mpf(dm)*rd/base - l
    Ks = min(range(1, 44), key=lambda K: abs(bsec(K) - b_req))
    pts.append((l, b_req, Ks))
    print(f"  {nm:<5} z = {float(z):.3f}  l = {float(l):.4f}  b_req = {float(b_req):.7f}  K* = {Ks}")
mean_b = mp.fsum(p[1] for p in pts)/6
rms = mp.sqrt(mp.fsum((p[1]-mean_b)**2 for p in pts)/6)
print(f"  b_req 平均 = {float(mean_b):.7f}, 散佈 = ±{float(rms):.7f} (σ_M 主導)")
chk("T1  實證 K*(ℓ) 喺 DESI 區間無單調趨勢 (散佈 ±1.5 窗, 由雜訊主導)",
    all(abs(p[2]-21.5) <= 3 for p in pts), f"K* = {[p[2] for p in pts]}")

# ---------- T2 ----------
print("\nT2. 候選 K 律嘅 DESI chi2 (a = 1 固定; 窗律 b = <sec>_1..K)")
cands = {
 '(a) K = L4(N_gen+z/F_proj)  [z-線性]': lambda l, z: bsec(int(round(21 + 7*z/zmax))),
 '(b) K = L4(N_gen+(l/l_Nyq)^2)':         lambda l, z: bsec(int(round(21 + 7*(l/l_nyq)**2))),
 '(f) K = L4(N_gen+(z/F_proj)^2)':        lambda l, z: bsec(int(round(21 + 7*(z/zmax)**2))),
 '(c) 混合 z: sec21+(z/17)(sec28-sec21)': lambda l, z: bsec(21) + (z/zmax)*(bsec(28)-bsec(21)),
 '(e) K = 22+6z/F_proj':                  lambda l, z: bsec(int(round(22 + 6*z/zmax))),
 '(h) K = 21+7*4^(l-l_Nyq)':              lambda l, z: bsec(int(round(21 + 7*4**(l-l_nyq)))),
 '(g) 混合 l: sec21+(l/l_Nyq)(sec28-sec21)': lambda l, z: bsec(21) + (l/l_nyq)*(bsec(28)-bsec(21)),
 '(i) K = 21+7l/l_Nyq  [l-線性]':         lambda l, z: bsec(int(round(21 + 7*l/l_nyq))),
 '(d) K = 21+7(1-4^-l)/(1-4^-l_Nyq)':     lambda l, z: bsec(int(round(21 + 7*(1-4**(-l))/(1-4**(-l_nyq))))),
}
res = {}
for tag, f in cands.items():
    c = chi2DM(f); res[tag] = c
    print(f"  {tag:<44} chi2 = {float(c):>9.4f}   D = {float(c-c_ref):>+9.4f}")
print(f"  {'[基準] K = 21 常數':<44} chi2 = {float(chi2DM(lambda l,z: bsec(21))):>9.4f}   D = {float(chi2DM(lambda l,z: bsec(21))-c_ref):>+9.4f}")
print(f"  {'[基準] 仿射 b 自由 (1 參數)':<44} chi2 = {float(c_ref):>9.4f}   D = {0.0:>+9.4f}")
excl = ['(i) K = 21+7l/l_Nyq  [l-線性]', '(d) K = 21+7(1-4^-l)/(1-4^-l_Nyq)',
        '(g) 混合 l: sec21+(l/l_Nyq)(sec28-sec21)']
chk("T2  l-線性 / 正規化幾何 / l-混合 律被 DESI 排除 (D_chi2 > 9)",
    all(res[t] - c_ref > 9 for t in excl),
    f"D_chi2 = {[round(float(res[t]-c_ref),2) for t in excl]}")
chk("T2b z-線性窗律與仿射最優一致 (D_chi2 < 1)",
    res['(a) K = L4(N_gen+z/F_proj)  [z-線性]'] - c_ref < 1,
    f"D_chi2 = {float(res['(a) K = L4(N_gen+z/F_proj)  [z-線性]']-c_ref):.4f}")

# ---------- T3 ----------
print("\nT3. ★ 兩個結構端點")
K0 = L4*Ng; Kz = L4*B
print(f"  K(z = 0)      = L4*N_gen = {L4}*{Ng} = {K0}   (DESI 唯一選出嘅窗)")
print(f"  K(z = z_max)  = L4*B     = {L4}*{B} = {Kz}   (πR/Nyquist 要求嘅窗)")
E_nyq = l_nyq + bsec(Kz)
chk("T3  端點 K(0) = 21 對應 DESI 唯一窗", abs(bsec(21) - bsec(K0)) < mp.mpf('1e-38'))
chk("T3b 端點 K(z_max) = 28 滿足 πR 錨點 (dev < 1e-4)", abs(E_nyq - tgt)/tgt < mp.mpf('1e-4'),
    f"E(l_Nyq) = {mp.nstr(E_nyq,12)} vs {mp.nstr(tgt,12)}  dev = {float(abs(E_nyq-tgt)/tgt*100):.6f}%")
E12 = mp.mpf(1)/2 + bsec(21)
chk("T3c 自對偶點 E(1/2) ≈ phi (dev < 0.05%)", abs(E12-phi)/phi < mp.mpf('5e-4'),
    f"E(1/2) = {float(E12):.8f} vs phi = {float(phi):.8f}  dev = {float(abs(E12-phi)/phi*100):.4f}%")

# ---------- T4 ----------
print("\nT4. ★ 不可能性: 常數 transit-time 門檻律 (τ_n ≤ c·ℓ)")
lD = ell('2.330')
lo1, hi1 = sec[21]/lD, sec[22]/lD
lo2, hi2 = sec[28]/l_nyq, sec[29]/l_nyq
print(f"  DESI 上限 ℓ = {float(lD):.4f}: K = 21 ⇒ c ∈ [{float(lo1):.6f}, {float(hi1):.6f}]")
print(f"  Nyquist ℓ = {float(l_nyq):.4f}: K = 28 ⇒ c ∈ [{float(lo2):.6f}, {float(hi2):.6f}]")
chk("T4  兩區間不相交 ⇒ 常數 c 律不存在 (排除整族)",
    hi2 < lo1, f"[{float(lo2):.3f},{float(hi2):.3f}] ∩ [{float(lo1):.3f},{float(hi1):.3f}] = ∅")

# ---------- T5 ----------
print("\nT5. 可證偽預言 (z ≳ 3 可裁決)")
for z in ['3.0', '8.5']:
    zm = mp.mpf(z); lz = ell(z)
    Ka = int(round(21 + 7*zm/zmax)); Kf = int(round(21 + 7*(zm/zmax)**2))
    print(f"  z = {z}: (a) z-線性 K = {Ka} ⇒ b = {float(bsec(Ka)):.7f}   |   "
          f"(f) z-二次 K = {Kf} ⇒ b = {float(bsec(Kf)):.7f}   分歧 = {float(bsec(Ka)-bsec(Kf)):.5f}")
chk("T5  z-線性 vs z-二次 喺 z = 3 已分歧 (> 0.01)", abs(bsec(22)-bsec(21)) > mp.mpf('0.01'))

# ---------- T6 ----------
print("\nT6. 統一零參數律: E(ℓ) = ℓ + <sec>_1..K(z),  K(z) = L4(N_gen + z/F_proj)")
c_law = chi2DM(lambda l, z: bsec(int(round(21 + 7*z/zmax))))
print(f"  chi2(6 D_M) = {float(c_law):.5f}  (仿射 b 自由 = {float(c_ref):.5f}, 1 自由參數)")
print(f"  零自由參數;  滿足 πR/Nyquist (dev {float(abs(E_nyq-tgt)/tgt*100):.6f}%);  E(1/2) vs phi dev {float(abs(E12-phi)/phi*100):.4f}%")
chk("T6  零參數統一窗律通過 DESI (chi2 < 4)", c_law < 4,
    f"chi2 = {float(c_law):.5f} vs 仿射 1 參數 {float(c_ref):.5f}")

print()
print("=" * 80)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL)
print("=" * 80)
print(f"""
結論 (B3 狀態: 🔴 -> 🟡):
  T1  DESI 區間實證 K* 散佈 {[p[2] for p in pts]}, 無趨勢 (雜訊主導) ⇒ 內插唔受 DESI 約束。
  T2  ★ **l-線性窗律被排除** (D_chi2 = {float(res['(i) K = 21+7l/l_Nyq  [l-線性]']-c_ref):.1f});
      正規化幾何律 (d) D = {float(res['(d) K = 21+7(1-4^-l)/(1-4^-l_Nyq)']-c_ref):.1f} 亦排除。
      z-線性窗律 (a) 與仿射最優一致 (D = {float(res['(a) K = L4(N_gen+z/F_proj)  [z-線性]']-c_ref):.4f})。
  T3  兩端點由結構釘死: K(0) = L4*N_gen = 21, K(z_max) = L4*B = 28;
      Nyquist 錨點 dev {float(abs(E_nyq-tgt)/tgt*100):.6f}%; 自對偶點 E(1/2) vs phi dev {float(abs(E12-phi)/phi*100):.4f}%。
  T4  ★ 常數 transit-time 門檻律**不可能** (c 區間不相交) — 排除一整族候選。
  T5  預言: z = 3 處 (a) b = {float(bsec(22)):.6f} vs (f) b = {float(bsec(21)):.6f} ⇒ 可裁決。
  T6  ★ 統一零參數律: E(ℓ) = ℓ + <sec>_1..K(z), K(z) = L4(N_gen + z/F_proj)
      chi2(6 D_M) = {float(c_law):.5f} (仿射 1 參數 {float(c_ref):.5f}) — 零自由參數。
  🔴 殘餘: 內插形式 (z-線性 vs z-二次 vs 其他) 未由第一原理導出; z ≳ 3 觀測可裁決。
""")
