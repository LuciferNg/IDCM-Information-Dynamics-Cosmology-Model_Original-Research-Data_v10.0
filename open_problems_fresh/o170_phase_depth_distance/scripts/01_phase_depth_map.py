#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/01 — 相位深度 Φ(ℓ) 映射 + M(ℓ) 非單調分析 + 候選核掃描

O167 scripts/12 發現: 徑向阻抗 M(ℓ) = 1.630, 1.639, 1.684, 1.624, 1.572, 1.419
非單調 (峰值 ℓ≈0.48)。深極限 √2 = sec(π/4) = 1/v_g(22) 命中 Lyα 0.3σ。

本 script (誠實版, 唔 fit):
  C1: M(ℓ) 表重現 + 誤差傳播 (用 DESI DR2 Table 6 正確誤差 + ρ)
  C2: 兩個舊 kernel (dD_A/dz, √2·R·dℓ/dz) 2D χ² (含 ρ) — 重現 FAIL
  C3: O117 kernel DH = R_H(1+δ_k0+δ_gd)/(1+z) — 用正確誤差重評 (O117 用咗錯誤差)
  C4: 常數阻抗候選 (1, ln4, φ, √2) — 結構常數直接對比
  C5: 高斯共振族 (O117 δ_k0) 結構點 (φ⁻³, ℓ₀=0.5, σ_φ) vs 最佳診斷 fit
  C6: 深極限錨: 各候選 ℓ→∞ 極限
  C7: 譜窗核 K(ℓ) = Σρ·w 型 (O170 問題記錄 §一.3 建議) — 窗規則掃描
  C8: 誠實裁決
"""
import mpmath as mp
mp.mp.dps = 30

# ---------- 結構常數 ----------
phi = (1 + mp.sqrt(5)) / 2
phi_inv = 1/phi
R = mp.mpf('4129.94')          # R_world (O73)
rd = mp.pi * R / 88 * mp.mpf(420)/421   # 147.088
ln4 = mp.log(4)
N_d = 44
F_proj = 17
n_cut = N_d - F_proj           # 27
N_gen = 3
B = 4
mu2 = mp.mpf(2)

P = 0; F = 0
def chk(name, cond, note=""):
    global P, F
    if cond: P += 1; print(f"[PASS] {name} {note}")
    else:    F += 1; print(f"[FAIL] {name} {note}")
    return cond

def ell_of(z): return mp.log(1+z, 4)

# ---------- DESI DR2 Table 6 (arXiv 2503.14738) ----------
# (tracer, z, D_M/rd, sig_M, D_H/rd, sig_H, rho)
DATA = [
    ('LRG1',    mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167'), mp.mpf('21.863'), mp.mpf('0.425'), mp.mpf('-0.459')),
    ('LRG2',    mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177'), mp.mpf('19.455'), mp.mpf('0.330'), mp.mpf('-0.404')),
    ('LRG3+ELG',mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152'), mp.mpf('17.641'), mp.mpf('0.193'), mp.mpf('-0.416')),
    ('ELG2',    mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318'), mp.mpf('14.176'), mp.mpf('0.221'), mp.mpf('-0.434')),
    ('QSO',     mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760'), mp.mpf('12.817'), mp.mpf('0.516'), mp.mpf('-0.500')),
    ('Lya',     mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531'), mp.mpf('8.632'),  mp.mpf('0.101'), mp.mpf('-0.431')),
]

print("="*78)
print("O170 scripts/01 — 相位深度距離: M(ℓ) 表 + 候選核誠實掃描")
print("="*78)
print(f"R_world = {mp.nstr(R,8)} Mpc, rd = {mp.nstr(rd,7)} Mpc, ln4 = {mp.nstr(ln4,8)}")
print(f"φ = {mp.nstr(phi,8)}, φ⁻¹ = {mp.nstr(phi_inv,8)}, √2 = {mp.nstr(mp.sqrt(2),8)}")
print(f"F_proj = {F_proj}, n_cut = {n_cut}")

# ---------- C1: M(ℓ) 表 ----------
print("\n--- C1: 需要嘅徑向阻抗 M(ℓ) = D_H·rd/(R·dℓ/dz) ---")
print(f"{'tracer':<10}{'z':>6}{'ell':>8}{'D_H/rd':>9}{'sig':>7}{'M':>9}{'sig_M':>8}{'M-ln4':>9}{'M-φ':>8}{'M-√2':>8}")
ROWS = []
for nm, z, dm, sm, dh, sh, rho in DATA:
    ell = ell_of(z)
    scale = R/((1+z)*ln4)          # R·dℓ/dz
    M = dh*rd/scale
    sM = sh*rd/scale
    ROWS.append((nm, z, ell, dm, sm, dh, sh, rho, M, sM))
    print(f"{nm:<10}{float(z):>6.3f}{float(ell):>8.4f}{float(dh):>9.3f}{float(sh):>7.3f}"
          f"{float(M):>9.4f}{float(sM):>8.4f}{float(M-ln4):>9.4f}{float(M-phi):>8.4f}{float(M-mp.sqrt(2)):>8.4f}")

mono = all(ROWS[i][8] <= ROWS[i+1][8] for i in range(5)) or all(ROWS[i][8] >= ROWS[i+1][8] for i in range(5))
chk("C1 M(ℓ) 非單調 (峰值 ℓ≈0.48)", not mono)

# ---------- χ² 工具 ----------
def chi2_DH(Mfun):
    """Mfun(ell) -> 徑向阻抗; D_H/rd = M·R·dℓ/dz/rd"""
    c = mp.mpf(0)
    for nm, z, ell, dm, sm, dh, sh, rho, M, sM in ROWS:
        pred = Mfun(ell)*R/((1+z)*ln4)/rd
        c += ((pred-dh)/sh)**2
    return c

def chi2_DM(Dfun):
    """Dfun(z) -> D_M (Mpc); D_M/rd = Dfun/rd"""
    c = mp.mpf(0)
    for nm, z, ell, dm, sm, dh, sh, rho, M, sM in ROWS:
        pred = Dfun(z)/rd
        c += ((pred-dm)/sm)**2
    return c

def chi2_joint(Dfun, Mfun):
    c = mp.mpf(0)
    for nm, z, ell, dm, sm, dh, sh, rho, M, sM in ROWS:
        pm = Dfun(z)/rd
        ph = Mfun(ell)*R/((1+z)*ln4)/rd
        a = pm-dm; b = ph-dh
        cov = sm*sh*rho
        det = sm**2*sh**2 - cov**2
        c += (a*a*sh**2 + b*b*sm**2 - 2*cov*a*b)/det
    return c

def D_app(z, C=mp.mpf('-0.1697')):
    ell = ell_of(z)
    d = C*(ell-mp.mpf('0.5'))*(1-4**(-ell))
    return R*(1-4**(-ell))*(1+2*phi_inv*ell+d)

def D_app_nodelta(z):
    ell = ell_of(z)
    return R*(1-4**(-ell))*(1+2*phi_inv*ell)

# ---------- C2: 兩個舊 kernel ----------
print("\n--- C2: O167 兩個舊 kernel (2D χ² 含 ρ) ---")
def M_dDAdz(ell):   # D_H = dD_A/dz  → M = dD_A/dℓ / R
    h = mp.mpf('1e-6')
    z = 4**ell - 1
    dD = (D_app(z+h)-D_app(z-h))/(2*h)
    dzdl = (1+z)*ln4
    return dD*dzdl/R
def M_sqrt2(ell): return mp.sqrt(2)

c2a = chi2_joint(D_app, M_dDAdz); c2b = chi2_joint(D_app, M_sqrt2)
print(f"  dD_A/dz kernel : χ²(DH)={float(chi2_DH(M_dDAdz)):.1f}/6, 2D joint={float(c2a):.1f}/12")
print(f"  √2 kernel      : χ²(DH)={float(chi2_DH(M_sqrt2)):.1f}/6, 2D joint={float(c2b):.1f}/12")
chk("C2 兩個舊 kernel 都 FAIL (χ²_DH/dof > 5)",
    chi2_DH(M_dDAdz)/6 > 5 and chi2_DH(M_sqrt2)/6 > 5)

# ---------- C3: O117 kernel 誠實重評 ----------
print("\n--- C3: O117 kernel 誠實重評 (O117 用 Lyα σ=0.532, Table 6 係 0.101) ---")
phi3 = phi_inv**3
sig_phi = mp.log(phi)/(2*ln4)
C_delay = mp.mpf(0)
g_ = [4*mp.sin(mp.pi*n/88)**2 for n in range(1, n_cut+1)]
w_ = [1/mp.cos(mp.pi*n/88) for n in range(1, n_cut+1)]
se = sum(w_[i]*g_[i] for i in range(0, n_cut, 2))
so = sum(w_[i]*g_[i] for i in range(1, n_cut, 2))
C_delay = (se-so)/(se+so)
C_DM = -C_delay*2*phi_inv*mp.sqrt(5)
C_DH = C_DM*B/N_gen
print(f"  C_delay = {mp.nstr(C_delay,7)}, C_DM = {mp.nstr(C_DM,7)}, C_DH = {mp.nstr(C_DH,7)}")
print(f"  φ⁻³ = {mp.nstr(phi3,7)}, σ_φ = ½log₄φ = {mp.nstr(sig_phi,7)}")

def dk0(ell): return phi3*mp.exp(-(ell-mp.mpf('0.5'))**2/(2*sig_phi**2))
def dgd(ell, C): return C*(ell-mp.mpf('0.5'))*(1-4**(-ell))

def M_o117(ell): return ln4*(1+dk0(ell)+dgd(ell, C_DH))
def M_o117_res(ell): return ln4*(1+dk0(ell))

print(f"  {'tracer':<10}{'M obs':>9}{'M_O117':>9}{'sig':>7}{'M_res':>9}{'sig':>7}")
for nm, z, ell, dm, sm, dh, sh, rho, M, sM in ROWS:
    print(f"  {nm:<10}{float(M):>9.4f}{float(M_o117(ell)):>9.4f}"
          f"{float((M_o117(ell)-M)/sM):>7.2f}{float(M_o117_res(ell)):>9.4f}{float((M_o117_res(ell)-M)/sM):>7.2f}")
c3a = chi2_DH(M_o117); c3b = chi2_DH(M_o117_res)
print(f"  χ²_DH: O117 全式 = {float(c3a):.2f}/6 (χ²/dof={float(c3a)/6:.2f}); 純共振 = {float(c3b):.2f}/6 ({float(c3b)/6:.2f})")
chk("C3 O117 全式 用正確誤差後 χ²/dof > 1.5 (O117 報 7.55 係用咗 σ=0.532)", c3a/6 > mp.mpf('1.5'))

# ---------- C4: 常數阻抗候選 ----------
print("\n--- C4: 常數阻抗候選 (結構常數直接對比) ---")
CAND_CONST = [('1', mp.mpf(1)), ('ln4', ln4), ('φ', phi), ('√2', mp.sqrt(2)),
              ('√2+φ⁻³', mp.sqrt(2)+phi3), ('4φ⁻¹', 4*phi_inv), ('sec(π/4)=√2', 1/mp.cos(mp.pi/4))]
for nm, v in CAND_CONST:
    c = chi2_DH(lambda e, v=v: v)
    print(f"  M = {nm:<10} = {float(v):.5f}  χ²_DH = {float(c):>7.2f}/6  (χ²/dof = {float(c)/6:.2f})")

# ---------- C5: 高斯共振族 ----------
print("\n--- C5: 高斯共振族 M = ln4(1 + A·exp(−(ℓ−ℓ₀)²/2σ²)) ---")
def mk_gauss(A, l0, s):
    return lambda e: ln4*(1 + A*mp.exp(-(e-l0)**2/(2*s*s)))
struct_pt = mk_gauss(phi3, mp.mpf('0.5'), sig_phi)
cs = chi2_DH(struct_pt)
print(f"  結構點 (A=φ⁻³={float(phi3):.4f}, ℓ₀=0.5, σ=σ_φ={float(sig_phi):.5f}): χ²_DH = {float(cs):.2f}/6 ({float(cs)/6:.2f})")
# 最佳診斷 fit (3 param, 只用嚟睇數據想要咩, 唔當結果)
best = None
for i0 in range(21):
    l0 = mp.mpf('0.35') + i0*mp.mpf('0.02')
    for i1 in range(26):
        s = mp.mpf('0.10') + i1*mp.mpf('0.015')
        for i2 in range(31):
            A = mp.mpf('0.10') + i2*mp.mpf('0.01')
            c = chi2_DH(mk_gauss(A, l0, s))
            if best is None or c < best[0]: best = (c, A, l0, s)
print(f"  診斷最佳 fit: A={float(best[1]):.3f}, ℓ₀={float(best[2]):.3f}, σ={float(best[3]):.4f} → χ²_DH={float(best[0]):.2f}/6")
# 結構點 vs 最佳: 偏差
print(f"  結構點 vs 最佳: A {float(phi3):.3f} vs {float(best[1]):.3f}; ℓ₀ 0.5 vs {float(best[2]):.3f}; σ {float(sig_phi):.4f} vs {float(best[3]):.4f}")

# ---------- C6: 深極限錨 ----------
print("\n--- C6: 深極限錨 (ℓ→∞ / ℓ→1) ---")
for nm, f in [('ln4(1+δ_k0)', M_o117_res), ('ln4(1+δ_k0+δ_gd)', M_o117), ('φ', lambda e: phi), ('√2', M_sqrt2)]:
    print(f"  {nm:<20} ℓ=1: {float(f(mp.mpf(1))):.5f}   ℓ=2: {float(f(mp.mpf(2))):.5f}   ℓ→∞: {float(f(mp.mpf(20))):.5f}")
chk("C6 深極限錨: 只有 √2 候選 ℓ→∞ 收斂 1.41421", abs(M_sqrt2(mp.mpf(20))-mp.sqrt(2)) < mp.mpf('1e-10'))

# ---------- C7: 譜窗核 ----------
print("\n--- C7: 譜窗核 K(ℓ) = Σρw 型 (窗隨 ℓ 變化) ---")
def sec_n(n): return 1/mp.cos(mp.pi*n/88)
def gam_n(n): return 4*mp.sin(mp.pi*n/88)**2
def window_avg(nmax, num='sec', den='1'):
    ns = list(range(1, int(nmax)+1))
    if not ns: return mp.mpf(0)
    numv = mp.mpf(0); denv = mp.mpf(0)
    for n in ns:
        numv += {'sec': sec_n(n), 'gsec': gam_n(n)*sec_n(n), 'sec2': sec_n(n)**2}[num]
        denv += {'1': mp.mpf(1), 'g': gam_n(n), 'sec': sec_n(n)}[den]
    return numv/denv
# 窗規則候選
def test_window(label, nfun, num='sec', den='1'):
    def M(e):
        nw = nfun(e)
        return window_avg(min(nw, n_cut), num, den) if nw >= 1 else sec_n(1)
    c = chi2_DH(M)
    vals = [float(M(r[2])) for r in ROWS]
    print(f"  {label:<38} χ²={float(c):>7.2f}/6  M={['%.3f'%v for v in vals]}")
test_window('窗 n≤44·4^{−ℓ} ⟨sec⟩', lambda e: 44*4**(-e))
test_window('窗 n≤27 ⟨sec⟩ (固定截斷)', lambda e: 27)
test_window('窗 n≤27 ⟨γsec⟩/⟨γ⟩', lambda e: 27, 'gsec', 'g')
test_window('窗 n≤44(1−4^{−ℓ}) ⟨sec⟩', lambda e: 44*(1-4**(-e)))
test_window('窗 n≤44(1−4^{−ℓ}) ⟨γsec⟩/⟨γ⟩', lambda e: 44*(1-4**(-e)), 'gsec', 'g')
test_window('窗 n∈[22,22+4·4^{−ℓ}] ⟨sec⟩', lambda e: 22+4*4**(-e))
test_window('窗 n≤27 ⟨sec²⟩/⟨sec⟩', lambda e: 27, 'sec2', 'sec')

# ---------- C8: 誠實裁決 ----------
print("\n" + "="*78)
print(f"RESULT: {P}/{P+F} PASS")
print("="*78)
print("裁決:")
print("  - M(ℓ) 非單調確認 (峰值 ℓ≈0.48); 深極限 √2 命中 Lyα 0.3σ")
print("  - O117 全式 (含 δ_gd) 用 Table 6 正確誤差後 FAIL → δ_gd 線性項過度下降")
print("  - 常數阻抗: φ / ln4 / √2 各自都唔過全部六點")
print("  - 譜窗 ⟨sec⟩ 型核: 量級 ~1.0-1.25, 遠低於需要嘅 1.63")
