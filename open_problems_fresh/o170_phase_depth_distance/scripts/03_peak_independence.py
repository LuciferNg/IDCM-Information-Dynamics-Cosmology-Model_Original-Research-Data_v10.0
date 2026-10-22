#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/03 — 峰值獨立性 + 形狀診斷 (LRG3/ELG1 獨立測量)

★ 新數據: DESI DR2 Table 6 除咗宇宙學推論用嘅 6 bins, 仲有 LRG3 (z=0.922)
  同 ELG1 (z=0.955) 獨立測量 (arXiv 2503.14738 Table 6, 已對原表核實)。
  用途: 檢驗 ℓ≈0.48 嘅 M 峰值係咪「LRG3+ELG1 合併 tracer」假象。

C1: 擴展 M(ℓ) 表 (8 點 D_H) + BGS/QSO D_V 點
C2: 峰值獨立性 — LRG3 / ELG1 / 合併 三者 M 比較
C3: 形狀診斷 (2-3 參數平滑族, 只作形狀識別, 唔當結果)
C4: 結構候選再評 (含新點)
C5: 2D 聯合 χ² (含 ρ) — 徑向 vs 橫向解耦檢驗
"""
import mpmath as mp
import json
mp.mp.dps = 30

phi = (1+mp.sqrt(5))/2; phi_inv = 1/phi; phi3 = phi_inv**3
R = mp.mpf('4129.94'); rd = mp.pi*R/88*mp.mpf(420)/421
ln4 = mp.log(4); sq2 = mp.sqrt(2)
sig_phi = mp.log(phi)/(2*ln4)
ell_nyq = mp.log(18, 4); ell_cut = mp.mpf(17)/44*ell_nyq
mu2 = mp.mpf(2); N_gen = 3; B = 4; F_proj = 17; N_d = 44

def ell_of(z): return mp.log(1+z, 4)
def scale_of(z): return R/((1+z)*ln4)

# --- 8 點 D_H (6 宇宙學 bins + LRG3 + ELG1) ---
DH = [
    ('LRG1',      '0.510', '21.863', '0.425', 'cosmo'),
    ('LRG2',      '0.706', '19.455', '0.330', 'cosmo'),
    ('LRG3+ELG1', '0.934', '17.641', '0.193', 'cosmo'),
    ('ELG2',      '1.321', '14.176', '0.221', 'cosmo'),
    ('QSO',       '1.484', '12.817', '0.516', 'cosmo'),
    ('Lya',       '2.330', '8.632',  '0.101', 'cosmo'),
    ('LRG3',      '0.922', '17.577', '0.213', 'validation'),
    ('ELG1',      '0.955', '17.803', '0.297', 'validation'),
]
ROWS = []
print("="*96)
print("O170 scripts/03 — 峰值獨立性 + 形狀診斷")
print("="*96)
print(f"{'tracer':<11}{'z':>7}{'ell':>8}{'D_H/rd':>9}{'sig':>7}{'M':>9}{'sig_M':>8}{'M-ln4':>9}{'M-√2':>8}  role")
for nm, zs, dhs, shs, role in DH:
    z = mp.mpf(zs); dh = mp.mpf(dhs); sh = mp.mpf(shs); ell = ell_of(z); sc = scale_of(z)
    M = dh*rd/sc; sM = sh*rd/sc
    ROWS.append((nm, z, ell, dh, sh, M, sM, role))
    print(f"{nm:<11}{float(z):>7.3f}{float(ell):>8.4f}{float(dh):>9.3f}{float(sh):>7.3f}"
          f"{float(M):>9.4f}{float(sM):>8.4f}{float(M-ln4):>9.4f}{float(M-sq2):>8.4f}  {role}")

print("\n--- C2: 峰值獨立性 (ℓ≈0.47-0.48) ---")
sub = [r for r in ROWS if r[0] in ('LRG3','LRG3+ELG1','ELG1')]
for nm, z, ell, dh, sh, M, sM, role in sub:
    print(f"  {nm:<11} ℓ={float(ell):.4f}  M = {float(M):.4f} ± {float(sM):.4f}"
          f"   vs φ: {float((M-phi)/sM):+.2f}σ   vs ln4·(1+φ⁻³G[0.5,σ_φ]): ", end="")
    Mg = ln4*(1+phi3*mp.exp(-(ell-mp.mpf('0.5'))**2/(2*sig_phi**2)))
    print(f"{float((M-Mg)/sM):+.2f}σ")
lr, le = [r for r in sub if r[0]=='LRG3'][0], [r for r in sub if r[0]=='ELG1'][0]
print(f"  LRG3 vs ELG1 差: ΔM = {float(le[5]-lr[5]):+.4f} ± {float(mp.sqrt(le[6]**2+lr[6]**2)):.4f}"
      f" → {float((le[5]-lr[5])/mp.sqrt(le[6]**2+lr[6]**2)):+.2f}σ (兩獨立 tracer 一致)")
chk = abs(float((le[5]-lr[5])/mp.sqrt(le[6]**2+lr[6]**2))) < 2
print(f"  [{'PASS' if chk else 'FAIL'}] 峰值唔係合併 tracer 假象 (兩獨立 tracer 一致)")

# ---------- χ² ----------
def chi2(Mf, rows=ROWS):
    return sum(((Mf(ell)*R/((1+z)*ln4)/rd - dh)/sh)**2 for nm,z,ell,dh,sh,M,sM,role in rows)
def maxs(Mf, rows=ROWS):
    return max(float(abs((Mf(ell)-M)/sM)) for nm,z,ell,dh,sh,M,sM,role in rows)

print("\n--- C3: 形狀診斷 (平滑族; 只作形狀識別, 唔當結構結果) ---")
x = lambda e: 4**(-e)
# (a) 線性 in x
import itertools
def fit_poly(deg):
    best=None
    grid = [mp.mpf(str(v)) for v in [i*0.1 for i in range(-30, 61)]]
    if deg==1:
        for a in grid:
            for b in grid:
                c = chi2(lambda e, a=a, b=b: a+b*x(e))
                if best is None or c<best[0]: best=(c,a,b)
    else:
        for a in [mp.mpf(str(v)) for v in [i*0.2 for i in range(-15,31)]]:
            for b in grid:
                for c0 in grid:
                    c = chi2(lambda e, a=a, b=b, c0=c0: a+b*x(e)+c0*x(e)**2)
                    if best is None or c<best[0]: best=(c,a,b,c0)
    return best
b1 = fit_poly(1); print(f"  M = a+b·x        : χ²={float(b1[0]):.2f}/8  a={float(b1[1]):.3f} b={float(b1[2]):.3f}")
b2 = fit_poly(2); print(f"  M = a+b·x+c·x²   : χ²={float(b2[0]):.2f}/8  a={float(b2[1]):.3f} b={float(b2[2]):.3f} c={float(b2[3]):.3f}")

# (b) 高斯族 (A, ℓ0, σ) 最佳診斷
best=None
for i0 in range(26):
    l0 = mp.mpf('0.30')+i0*mp.mpf('0.02')
    for i1 in range(30):
        s = mp.mpf('0.08')+i1*mp.mpf('0.012')
        for i2 in range(36):
            A = mp.mpf('0.08')+i2*mp.mpf('0.01')
            c = chi2(lambda e,A=A,l0=l0,s=s: ln4*(1+A*mp.exp(-(e-l0)**2/(2*s*s))))
            if best is None or c<best[0]: best=(c,A,l0,s)
print(f"  高斯最佳診斷     : χ²={float(best[0]):.2f}/8  A={float(best[1]):.3f} ℓ₀={float(best[2]):.3f} σ={float(best[3]):.4f}")
print(f"    結構點對照: A=φ⁻³={float(phi3):.3f}, ℓ₀=0.5, σ=σ_φ={float(sig_phi):.4f}, 2/N_gen²={float(mp.mpf(2)/9):.3f}, log₄(4/3)={float(mp.log(mp.mpf(4)/3,4)):.4f}")

# (c) 餘弦 (φ-週期) 診斷
for Pnm, P in [('log₄φ', mp.log(phi,4)), ('2log₄φ', 2*mp.log(phi,4)), ('σ_φ', sig_phi), ('log₄2', mp.mpf('0.5'))]:
    best=None
    for i0 in range(41):
        ph0 = i0*mp.pi/20
        for i1 in range(31):
            A = mp.mpf('0.02')+i1*mp.mpf('0.01')
            for i2 in range(21):
                C = mp.mpf('0.0')+i2*mp.mpf('0.02')
                c = chi2(lambda e,A=A,ph0=ph0,C=C,P=P: ln4*(1+A*mp.cos(2*mp.pi*e/P+ph0)+C))
                if best is None or c<best[0]: best=(c,A,ph0,C)
    print(f"  餘弦 P={Pnm:<8}   : χ²={float(best[0]):.2f}/8  A={float(best[1]):.3f} φ₀={float(best[2]):.3f} C={float(best[3]):.3f}")

# (d) 冪律 x^p(1−x)^q
best=None
for i0 in range(1, 41):
    p = mp.mpf(i0)*mp.mpf('0.5')
    for i1 in range(1, 41):
        q = mp.mpf(i1)*mp.mpf('0.5')
        for i2 in range(1, 61):
            A = mp.mpf(i2)*mp.mpf('0.5')
            c = chi2(lambda e,A=A,p=p,q=q: ln4+A*x(e)**p*(1-x(e))**q)
            if best is None or c<best[0]: best=(c,A,p,q)
print(f"  冪律 x^p(1−x)^q  : χ²={float(best[0]):.2f}/8  A={float(best[1]):.3f} p={float(best[2]):.2f} q={float(best[3]):.2f}")

print("\n--- C4: 結構候選 (零參數) 對 8 點 ---")
CANDS = {
    'const φ': lambda e: phi,
    'const √2': lambda e: sq2,
    'const ln4': lambda e: ln4,
    'ln4(1+φ⁻³G[0.5,σ_φ])': lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2))),
    'ln4(1+2/9·G[0.5,σ_φ])': lambda e: ln4*(1+mp.mpf(2)/9*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2))),
    'ln4(1+φ⁻³G[0.5,log₄(4/3)])': lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*mp.log(mp.mpf(4)/3,4)**2))),
    'sec(π/4·(1+φ⁻³x))': lambda e: 1/mp.cos(mp.pi/4*(1+phi3*x(e))),
    'sec(π(22+22φ⁻³x)/88)': lambda e: 1/mp.cos(mp.pi*(22+22*phi3*x(e))/88),
    '2-regime ln4(1+δk0)|√2@0.806': lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2))) if e<ell_cut else sq2,
    '2-regime φ|√2@0.806': lambda e: phi if e<ell_cut else sq2,
    'O117 全式': None,
}
C_delay = mp.mpf(0)
g_ = [4*mp.sin(mp.pi*n/88)**2 for n in range(1,28)]
w_ = [1/mp.cos(mp.pi*n/88) for n in range(1,28)]
se = sum(w_[i]*g_[i] for i in range(0,27,2)); so = sum(w_[i]*g_[i] for i in range(1,27,2))
C_DH = (-(se-so)/(se+so))*2*phi_inv*mp.sqrt(5)*B/N_gen
CANDS['O117 全式'] = lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2)) + C_DH*(e-mp.mpf('0.5'))*(1-4**(-e)))
for nm, f in CANDS.items():
    print(f"  {nm:<32} χ²={float(chi2(f)):>7.2f}/8  max|σ|={maxs(f):>5.2f}  M(0.5)={float(f(mp.mpf('0.5'))):.4f}  M(∞)={float(f(mp.mpf('20'))):.4f}")

print("\n--- C5: 2D 聯合 χ² (含 ρ, 6 宇宙學 bins) — 徑向/橫向解耦 ---")
DM = [
    ('LRG1',  '0.510', '13.588', '0.167', '21.863', '0.425', '-0.459'),
    ('LRG2',  '0.706', '17.351', '0.177', '19.455', '0.330', '-0.404'),
    ('LRG3+ELG1','0.934','21.576','0.152', '17.641', '0.193', '-0.416'),
    ('ELG2',  '1.321', '27.601', '0.318', '14.176', '0.221', '-0.434'),
    ('QSO',   '1.484', '30.512', '0.760', '12.817', '0.516', '-0.500'),
    ('Lya',   '2.330', '38.988', '0.531', '8.632',  '0.101', '-0.431'),
]
def D_app(z, C=mp.mpf('-0.1697')):
    e = ell_of(z); d = C*(e-mp.mpf('0.5'))*(1-4**(-e))
    return R*(1-4**(-e))*(1+2*phi_inv*e+d)
def joint(Mf):
    c = mp.mpf(0)
    for nm, zs, dms, sms, dhs, shs, rhos in DM:
        z=mp.mpf(zs); dm=mp.mpf(dms); sm=mp.mpf(sms); dh=mp.mpf(dhs); sh=mp.mpf(shs); rho=mp.mpf(rhos)
        pm = D_app(z)/rd; ph = Mf(ell_of(z))*scale_of(z)/rd
        a=pm-dm; b=ph-dh; cov=sm*sh*rho; det=sm**2*sh**2-cov**2
        c += (a*a*sh**2+b*b*sm**2-2*cov*a*b)/det
    return c
def chi2_DM_only():
    return sum(((D_app(mp.mpf(zs))/rd-mp.mpf(dms))/mp.mpf(sms))**2 for nm,zs,dms,sms,dhs,shs,rhos in DM)
print(f"  橫向 D_app 單獨: χ²_DM = {float(chi2_DM_only()):.2f}/6")
for nm, f in CANDS.items():
    print(f"  {nm:<32} χ²_joint={float(joint(f)):>7.2f}/12")
print(f"  {'(舊) dD_A/dz 徑向':<32} χ²_joint={float(joint(lambda e: 0)):.2f} (參考: 已 FAIL)")

json.dump({'rows': [[r[0], float(r[2]), float(r[5]), float(r[6]), r[7]] for r in ROWS],
           'diag_gauss': [float(best[0]), float(best[1]), float(best[2]), float(best[3])]},
          open('/tmp/o170_shape.json','w'), indent=1)
print("\n→ /tmp/o170_shape.json")
