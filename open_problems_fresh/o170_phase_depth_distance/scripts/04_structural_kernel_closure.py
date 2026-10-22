#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/04 — ★ 結構核閉合: M(ℓ) = 2cos(π/(m+1)), m = B (1+z<N_gen) / N_gen (1+z>N_gen)

★ 定義 (O167 scripts/12 一致):
    D_H(ℓ) = R_world·(dℓ/dz)·M(ℓ),  dℓ/dz = 4^{-ℓ}/ln4
    ⟺ M(ℓ) = D_H·(1+z)·ln4/R_world = D_H·(1+z)/(R_world/ln4)
    R_world = 4129.94 Mpc = c/H0_local  (世界半徑 = 哈勃半徑, O167/O169)
    M = 徑向載波阻抗 = 1/v_g(carrier) = 每單位相位深度嘅徑向步長 (R_world 單位)

★ 結構假設 (零參數):
    M(ℓ) = 2cos(π/(m+1)) = 1/v_g(carrier)
      m = B = 4   for 1+z < N_gen  → M = 2cos(π/5) = φ = 1.618034   (v_g = φ^{-1}, 黃金共軛 = beat ratio)
      m = N_gen = 3 for 1+z > N_gen → M = 2cos(π/4) = √2 = sec(π/4) (v_g(22) 中心模, O167 ✓)
    過渡 ℓ_t = log₄N_gen = 0.792481 (1+z = N_gen = 3)
    數據 bracketing: QSO ℓ=0.6563 (φ) < ℓ_t < Lyα ℓ=0.8678 (√2)
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1 + mp.sqrt(5)) / 2
R = mp.mpf("4129.94")
rd = mp.mpf("147.088")
B = 4
Ngen = 3
ell_t = mp.log(Ngen, 4)

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

def ell(z):
    return mp.log(1 + mp.mpf(str(z)), 4)

# ---------- 數據: DESI DR2 Table 6 ----------
# (name, z, D_M/rd, s_M, D_H/rd, s_H, rho, role)
DATA = [
    ('BGS',       0.295, None,   None,  None,  None,  None,  'DV-only'),
    ('LRG1',      0.510, 13.588, 0.167, 21.863, 0.425, -0.459, 'cosmo'),
    ('LRG2',      0.706, 17.351, 0.177, 19.455, 0.330, -0.404, 'cosmo'),
    ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416, 'cosmo'),
    ('ELG2',      1.321, 27.601, 0.318, 14.176, 0.221, -0.434, 'cosmo'),
    ('QSO',       1.484, 30.512, 0.760, 12.817, 0.516, -0.500, 'cosmo'),
    ('Lyalpha',   2.330, 38.988, 0.531,  8.632, 0.101, -0.431, 'cosmo'),
    ('LRG3',      0.922, 21.648, 0.178, 17.577, 0.213, -0.406, 'valid'),
    ('ELG1',      0.955, 21.707, 0.335, 17.803, 0.297, -0.462, 'valid'),
]
BGS_DV = (7.93, 0.15)   # z=0.295

print("=" * 108)
print("O170 scripts/04 — 結構核閉合: M(ℓ) = 2cos(π/(m+1)),  m = B | N_gen")
print("=" * 108)

# ---------- C1: 結構身份 ----------
print("\n--- C1: 2cos(π/(m+1)) 結構身份 ---")
chk("C1a 2cos(π/5) = φ (黃金比) — m = B = 4", abs(2*mp.cos(mp.pi/5) - phi) < mp.mpf("1e-30"))
chk("C1b 2cos(π/4) = √2 = sec(π/4) — m = N_gen = 3 (中心模 n=22)", abs(2*mp.cos(mp.pi/4) - mp.sqrt(2)) < mp.mpf("1e-30"))
chk("C1c 1/v_g(shallow) = φ ⟹ v_g = φ^{-1} = beat ratio (x²+x−1=0 根)", abs(1/phi - phi - (-1)) < mp.mpf("1e-30"))
chk("C1d v_g(deep) = 1/√2 = cos(π·22/88) = v_g(22) (O167 中心模)", abs(mp.cos(mp.pi*22/88) - 1/mp.sqrt(2)) < mp.mpf("1e-30"))
print(f"    φ = 2cos(36°) = {mp.nstr(phi, 10)}   √2 = 2cos(45°) = {mp.nstr(mp.sqrt(2), 10)}")
print(f"    ℓ_t = log₄N_gen = {mp.nstr(ell_t, 8)}  (1+z = {mp.nstr(4**ell_t, 8)} = N_gen)")

# ---------- C2: M(ℓ) 數據表 ----------
print("\n--- C2: M(ℓ) 表 (M = D_H·(1+z)·ln4/R_world) ---")
print(f"{'tracer':<11} {'z':<7} {'ℓ':<8} {'D_H/rd':<9} {'±':<7} {'M':<8} {'±M':<7} {'M−φ':<8} {'M−√2':<8} role")
rows = []
for name, z, dm, sm, dh, sh, rho, role in DATA:
    if dh is None:
        continue
    e = ell(z)
    M = mp.mpf(str(dh)) * rd * (1 + mp.mpf(str(z))) * mp.log(4) / R
    sM = mp.mpf(str(sh)) * rd * (1 + mp.mpf(str(z))) * mp.log(4) / R
    rows.append((name, z, e, dh, sh, M, sM, role))
    print(f"{name:<11} {z:<7.3f} {float(e):<8.4f} {dh:<9.3f} {sh:<7.3f} {float(M):<8.4f} {float(sM):<7.4f} "
          f"{float(M-phi):<+8.4f} {float(M-mp.sqrt(2)):<+8.4f} {role}")

# ---------- C3: 結構模型 χ² ----------
print("\n--- C3: 結構模型 M = φ (ℓ<ℓ_t) | √2 (ℓ>ℓ_t), ℓ_t = log₄3 = 0.792481 ---")
def M_model(e):
    return phi if e < ell_t else mp.sqrt(2)

def chi2_M(sel, model):
    chi = mp.mpf(0); out = []
    for name, z, e, dh, sh, M, sM, role in rows:
        if not sel(name, role):
            continue
        mp_ = model(e)
        r = (M - mp_) / sM
        chi += r**2
        out.append((name, float(M), float(mp_), float(r)))
    return chi, out

sel_cosmo = lambda n, r: r == 'cosmo'
sel_no934 = lambda n, r: (r == 'cosmo' and n != 'LRG3+ELG1')
sel_all8   = lambda n, r: True

chi_c, out_c = chi2_M(sel_cosmo, M_model)
chi_x, out_x = chi2_M(sel_no934, M_model)
chi_a, out_a = chi2_M(sel_all8, M_model)
print(f"  6 宇宙學 bins : χ² = {float(chi_c):.2f}/6  (χ²/dof = {float(chi_c)/6:.3f})")
for n, m, p, r in out_c:
    print(f"     {n:<11} M_obs = {m:.4f}  M_model = {p:.4f}  resid = {r:+.2f}σ")
print(f"  5 bins (排除 z=0.934): χ² = {float(chi_x):.2f}/5  (χ²/dof = {float(chi_x)/5:.3f})")
print(f"  8 點 (含 LRG3/ELG1 驗證): χ² = {float(chi_a):.2f}/8  (χ²/dof = {float(chi_a)/8:.3f})")

# ---------- C4: 淺極限加權平均 ----------
print("\n--- C4: 淺極限 (ℓ<ℓ_t) 加權平均 vs φ ---")
w = mp.mpf(0); sw = mp.mpf(0); w2 = mp.mpf(0); sw2 = mp.mpf(0)
for name, z, e, dh, sh, M, sM, role in rows:
    if e >= ell_t:
        continue
    ww = 1 / sM**2
    w += M * ww; sw += ww
    if name != 'LRG3+ELG1':
        w2 += M * ww; sw2 += ww
mean_all = w / sw; err_all = 1 / mp.sqrt(sw)
mean_no = w2 / sw2; err_no = 1 / mp.sqrt(sw2)
print(f"  全部 (含 z=0.934)   : ⟨M⟩ = {float(mean_all):.5f} ± {float(err_all):.5f}  vs φ: {float((mean_all-phi)/err_all):+.2f}σ")
print(f"  排除 z=0.934        : ⟨M⟩ = {float(mean_no):.5f} ± {float(err_no):.5f}  vs φ: {float((mean_no-phi)/err_no):+.2f}σ")

# ---------- C5: 過渡 ℓ_t 允許範圍 ----------
print("\n--- C5: ℓ_t 掃描 (χ²_M 6 bins) ---")
best = None
for i in range(1, 2000):
    lt = mp.mpf(i) / 1000
    if lt < mp.mpf("0.30") or lt > 1.0:
        continue
    def mm(e, lt=lt):
        return phi if e < lt else mp.sqrt(2)
    c = sum(((M - mm(e)) / sM)**2 for name, z, e, dh, sh, M, sM, role in rows if role == 'cosmo')
    if best is None or c < best[0]:
        best = (c, lt)
print(f"  最佳 ℓ_t = {float(best[1]):.3f} (χ² = {float(best[0]):.2f}/6);  結構值 log₄3 = {float(ell_t):.4f}")
lo = hi = None
for i in range(1, 2000):
    lt = mp.mpf(i) / 1000
    if lt < mp.mpf("0.30") or lt > 1.0:
        continue
    def mm(e, lt=lt):
        return phi if e < lt else mp.sqrt(2)
    c = sum(((M - mm(e)) / sM)**2 for name, z, e, dh, sh, M, sM, role in rows if role == 'cosmo')
    if c - best[0] <= 4:
        if lo is None: lo = lt
        hi = lt
print(f"  Δχ²≤4 允許範圍: ℓ_t ∈ [{float(lo):.3f}, {float(hi):.3f}]  → 1+z ∈ [{float(4**lo):.3f}, {float(4**hi):.3f}]")
chk("C5 結構值 ℓ_t = log₄3 落在允許範圍內", lo <= ell_t <= hi)

# ---------- C6: 對照模型 ----------
print("\n--- C6: 對照模型 (6 宇宙學 bins, D_H) ---")
def chi_of(model, sel=sel_cosmo):
    c = mp.mpf(0)
    for name, z, e, dh, sh, M, sM, role in rows:
        if not sel(name, role):
            continue
        c += ((M - model(e)) / sM)**2
    return float(c)

x_of = lambda e: 4**(-e)
G = lambda e, l0, s: mp.e**(-((e-l0)**2)/(2*s**2))
sig_phi = mp.log(phi, 4)/2
C_D = mp.mpf("-0.1697")
comp = [
    ("const φ", lambda e: phi, None),
    ("const √2", lambda e: mp.sqrt(2), None),
    ("const ln4", lambda e: mp.log(4), None),
    ("★2-regime φ|√2 @log₄3", None, None),
    ("2-regime φ|√2 @0.806 (掃描最佳)", None, None),
    ("ln4(1+φ⁻³G[0.5,σ_φ])", lambda e: mp.log(4)*(1 + phi**-3 * G(e, mp.mpf("0.5"), sig_phi)), None),
    ("ln4(1+2/9·G[0.5,σ_φ])", lambda e: mp.log(4)*(1 + mp.mpf(2)/9 * G(e, mp.mpf("0.5"), sig_phi)), None),
    ("sec(π/4·(1+φ⁻³x))", lambda e: mp.sec(mp.pi/4*(1 + phi**-3 * x_of(e))), None),
    ("O117 全式 (Gaussian δ)", lambda e: mp.log(4)*(1 + C_D*(e-mp.mpf("0.5"))*(1-x_of(e)) + phi**-3*G(e, mp.mpf("0.5"), sig_phi)), None),
]
for name, fn, _ in comp:
    if name.startswith("★"):
        v = chi_of(M_model); mx = max(abs((M - M_model(e))/sM) for n2, z, e, dh, sh, M, sM, r in rows if r == 'cosmo')
    elif name.startswith("2-regime φ|√2 @0.806"):
        v = chi_of(lambda e: phi if e < mp.mpf("0.806") else mp.sqrt(2))
        mx = max(abs((M - (phi if e < mp.mpf("0.806") else mp.sqrt(2)))/sM) for n2, z, e, dh, sh, M, sM, r in rows if r == 'cosmo')
    else:
        v = chi_of(fn)
        mx = max(abs((M - fn(e))/sM) for n2, z, e, dh, sh, M, sM, r in rows if r == 'cosmo')
    print(f"  {name:<36} χ² = {v:8.2f}/6   max|σ| = {float(mx):.2f}")

# ---------- C7: 2D 聯合 χ² (D_M 用 D_app + D_H 用結構核, 含 ρ) ----------
print("\n--- C7: 2D 聯合 χ² (含 ρ; 6 宇宙學 bins) ---")
def D_app(z):
    e = ell(z)
    return R * (1 - 4**(-e)) * (1 + 2*phi**-1*e + C_D*(e-mp.mpf("0.5"))*(1 - 4**(-e)))

def chi2_joint(M_fn):
    chi = mp.mpf(0)
    for name, z, dm, sm, dh, sh, rho, role in DATA:
        if role != 'cosmo' or dh is None:
            continue
        pm = D_app(z) / rd
        ph = M_fn(ell(z)) * R / ((1 + mp.mpf(str(z))) * mp.log(4)) / rd
        d1 = pm - mp.mpf(str(dm)); d2 = ph - mp.mpf(str(dh))
        e1 = mp.mpf(str(sm)); e2 = mp.mpf(str(sh)); r_ = mp.mpf(str(rho))
        cov = e1*e2*r_
        det = e1**2*e2**2 - cov**2
        chi += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/det
    return chi

chi_dm = mp.mpf(0)
for name, z, dm, sm, dh, sh, rho, role in DATA:
    if role != 'cosmo' or dh is None:
        continue
    chi_dm += ((D_app(z)/rd - mp.mpf(str(dm)))/mp.mpf(str(sm)))**2
print(f"  橫向 D_app 單獨: χ²_DM = {float(chi_dm):.2f}/6")
for nm, fn in [("★ 2-regime φ|√2", M_model),
               ("const φ", lambda e: phi),
               ("const √2", lambda e: mp.sqrt(2)),
               ("ln4(1+φ⁻³G[0.5,σ_φ])", lambda e: mp.log(4)*(1 + phi**-3*G(e, mp.mpf("0.5"), sig_phi))),
               ("O117 全式", lambda e: mp.log(4)*(1 + C_D*(e-mp.mpf("0.5"))*(1-x_of(e)) + phi**-3*G(e, mp.mpf("0.5"), sig_phi)))]:
    v = chi2_joint(fn)
    print(f"  {nm:<28} χ²_joint = {float(v):8.2f}/12")

# ---------- C8: 深極限錨 ----------
print("\n--- C8: 深極限錨 (Lyα ℓ=0.8678) ---")
z_lya = mp.mpf("2.330"); e_lya = ell(z_lya)
M_lya = mp.mpf("8.632")*rd*(1+z_lya)*mp.log(4)/R
s_lya = mp.mpf("0.101")*rd*(1+z_lya)*mp.log(4)/R
for nm, val in [("√2 (結構)", mp.sqrt(2)), ("φ", phi), ("ln4", mp.log(4)), ("sec(25.5π/88) 半位點", mp.sec(mp.mpf("25.5")*mp.pi/88))]:
    zz = (M_lya - val) / s_lya
    print(f"  M = {nm:<18} = {float(val):.5f}  →  D_H/rd = {float(val*R/((1+z_lya)*mp.log(4))/rd):.4f}  vs 8.632±0.101  ({float(zz):+.2f}σ)")
chk("C8 深極限 M = √2 命中 Lyα (|z|<1σ)", abs((M_lya - mp.sqrt(2))/s_lya) < 1)
chk("C8b 深極限 φ 被 Lyα 排除 (>5σ)", abs((M_lya - phi)/s_lya) > 5)

# ---------- C9: 峰值獨立性 ----------
print("\n--- C9: 峰值獨立性 (z≈0.93) ---")
d = {n: (M, sM) for n, z, e, dh, sh, M, sM, r in rows}
m3, s3 = d['LRG3']; m1, s1 = d['ELG1']
print(f"  LRG3 M = {float(m3):.4f}±{float(s3):.4f} ({float((m3-phi)/s3):+.2f}σ vs φ);  ELG1 M = {float(m1):.4f}±{float(s1):.4f} ({float((m1-phi)/s1):+.2f}σ vs φ)")
chk("C9 LRG3 與 ELG1 一致 (兩獨立 tracer, 差 <2σ)", abs(m3-m1)/mp.sqrt(s3**2+s1**2) < 2)

# ---------- C10: ladder 外推 (推測, 標記) ---
print("\n--- C10: (推測) ladder m = B−k, 過渡 @1+z = N_gen^k ---")
tot = mp.mpf(0)
m_lad = 4; k = 0
while m_lad >= 1:
    Mv = 2*mp.cos(mp.pi/(m_lad+1))
    tot += Mv * ell_t
    print(f"  m={m_lad}: M = 2cos(π/{m_lad+1}) = {float(Mv):.5f}   1+z ∈ [{float(Ngen**k):.0f}, {float(Ngen**(k+1)):.0f})  Δℓ = {float(ell_t):.4f}")
    m_lad -= 1; k += 1
print(f"  徑向總延伸 ∫M dℓ = {float(tot):.5f} R_world = {float(tot*R):.1f} Mpc")
print(f"  橫向飽和 πR_world = {float(mp.pi*R):.1f} Mpc  (偏差 {float((tot*R-mp.pi*R)/(mp.pi*R)*100):+.2f}%)")
print(f"  (註: 純推測 — 只有 m=4→3 過渡有數據支持; m=2,1 未測)")

# ---------- C11: H0 含意 ----------
print("\n--- C11: H0 含意 (z→0 外推) ---")
c_km = mp.mpf("299792.458")
H0_trans = c_km / R
H0_rad = c_km / (R * phi / mp.log(4))
print(f"  H0^transverse = c/R_world = {float(H0_trans):.3f} km/s/Mpc   (SH0ES 73.0±1.0 → {float((H0_trans-73)/1):+.2f}σ)")
print(f"  H0^radial     = c·ln4/(φR_world) = {float(H0_rad):.3f} km/s/Mpc  (Planck 67.4 → {float((H0_rad-67.4)/0.5):+.2f}σ)")

print("\n" + "=" * 108)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("=" * 108)
print("裁決: M(ℓ) = 2cos(π/(m+1)) 兩區制 (m = B | N_gen) — 淺極限 φ (v_g = φ⁻¹), 深極限 √2 (v_g(22))")
print("      過渡 ℓ_t = log₄N_gen (1+z = N_gen = 3); χ²(6 bins) 14.41, 排除 z=0.934 後 1.38/5")
