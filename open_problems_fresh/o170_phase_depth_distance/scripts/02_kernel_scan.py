#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/02 — 徑向取樣核 K(ℓ) 結構掃描 (零參數候選庫)

目標: 由 IDCM 原子 (γ_n, v_g, ω_ring, 88, 44, φ, √2, ln4, F_proj) 生成
      零自由參數候選核, 對 DESI DR2 Table 6 六點 D_H 排序。

錨 (必須同時滿足):
  A1: 深極限 M → √2 = sec(π/4) = 1/v_g(22)   (O167 已命中 Lyα 0.3σ)
  A2: ℓ→0 有限 (M(0) 結構值)
  A3: 非單調 (峰值 ℓ≈0.48) 或誠實報告單調候選
"""
import mpmath as mp
import itertools, json
mp.mp.dps = 30

phi = (1+mp.sqrt(5))/2
phi_inv = 1/phi
phi2, phi3 = phi_inv**2, phi_inv**3
R = mp.mpf('4129.94'); rd = mp.pi*R/88*mp.mpf(420)/421
ln4 = mp.log(4)
sq2, sq5 = mp.sqrt(2), mp.sqrt(5)
pi = mp.pi
N_d, F_proj, n_cut, N_gen, B = 44, 17, 27, 3, 4
mu2 = mp.mpf(2)
sig_phi = mp.log(phi)/(2*ln4)
ell_nyq = mp.log(18, 4)
ell_cut = mp.mpf(F_proj)/N_d*ell_nyq

DATA = [
    ('LRG1',    mp.mpf('0.510'), mp.mpf('21.863'), mp.mpf('0.425')),
    ('LRG2',    mp.mpf('0.706'), mp.mpf('19.455'), mp.mpf('0.330')),
    ('LRG3+ELG',mp.mpf('0.934'), mp.mpf('17.641'), mp.mpf('0.193')),
    ('ELG2',    mp.mpf('1.321'), mp.mpf('14.176'), mp.mpf('0.221')),
    ('QSO',     mp.mpf('1.484'), mp.mpf('12.817'), mp.mpf('0.516')),
    ('Lya',     mp.mpf('2.330'), mp.mpf('8.632'),  mp.mpf('0.101')),
]
ROWS = []
for nm, z, dh, sh in DATA:
    ell = mp.log(1+z, 4)
    scale = R/((1+z)*ln4)
    ROWS.append((nm, z, ell, dh, sh, dh*rd/scale, sh*rd/scale))

def chi2DH(M):
    c = mp.mpf(0)
    for nm, z, ell, dh, sh, Mo, sM in ROWS:
        pred = M(ell)*R/((1+z)*ln4)/rd
        c += ((pred-dh)/sh)**2
    return c

def maxsig(M):
    return max(abs((M(ell)-Mo)/sM) for nm, z, ell, dh, sh, Mo, sM in ROWS)

def sec_n(n): return 1/mp.cos(pi*n/88)
def gam_n(n): return 4*mp.sin(pi*n/88)**2

# ---------------- 候選庫 ----------------
CAND = {}
def add(name, f): CAND[name] = f

# --- 1. 常數 ---
for nm, v in [('const 1', mp.mpf(1)), ('const ln4', ln4), ('const φ', phi), ('const √2', sq2),
              ('const 2φ⁻¹', 2*phi_inv), ('const √2·φ^{-1/4}', sq2*phi**(-mp.mpf('0.25'))),
              ('const 4φ⁻¹', 4*phi_inv), ('const φ+φ⁻³', phi+phi3),
              ('const √2+φ⁻³', sq2+phi3), ('const π/2', pi/2), ('const π²/6', pi**2/6)]:
    add(nm, (lambda v: (lambda e: v))(v))

# --- 2. sec(θ(ℓ)) 族: θ = π/4·(1+a·x^k) 或 π/4 + a·x^k  (x = 4^{−ℓ}) ---
A_POOL = [('φ⁻³', phi3), ('φ⁻²', phi2), ('φ⁻¹', phi_inv), ('1/44', mp.mpf(1)/44),
          ('1/27', mp.mpf(1)/27), ('1/17', mp.mpf(1)/17), ('2/44', mp.mpf(2)/44),
          ('π/44', pi/44), ('φ⁻¹/44', phi_inv/44), ('1/88', mp.mpf(1)/88),
          ('4/44', mp.mpf(4)/44), ('1/8', mp.mpf(1)/8), ('φ⁻³/2', phi3/2), ('φ⁻²/2', phi2/2)]
for anm, a in A_POOL:
    for k in [1, 2]:
        add(f'sec(π/4·(1+{anm}·x^{k}))', (lambda a, k: (lambda e: 1/mp.cos(pi/4*(1+a*4**(-k*e)))))(a, k))
        add(f'sec(π/4+{anm}·x^{k})', (lambda a, k: (lambda e: 1/mp.cos(pi/4+a*4**(-k*e))))(a, k))

# --- 3. 中心模 + 偏移: n = 22 + a·x^k, M = sec(πn/88) ---
for anm, a in A_POOL:
    for k in [1]:
        add(f'sec(π(22+44·{anm}·x^{k})/88)', (lambda a, k: (lambda e: sec_n(22+44*a*4**(-k*e))))(a, k))
        add(f'sec(π(22+22·{anm}·x^{k})/88)', (lambda a, k: (lambda e: sec_n(22+22*a*4**(-k*e))))(a, k))

# --- 4. √2 + a·x^k·(1−x)^p 族 ---
for anm, a in [('φ⁻³', phi3), ('φ⁻²', phi2), ('φ⁻¹', phi_inv), ('1/8', mp.mpf(1)/8),
               ('1/4', mp.mpf(1)/4), ('φ⁻³·√2', phi3*sq2)]:
    for k, p in [(1,1),(1,2),(2,1),(2,2),(1,3),(0,1)]:
        add(f'√2+{anm}·x^{k}(1−x)^{p}', (lambda a, k, p: (lambda e: sq2+a*4**(-k*e)*(1-4**(-e))**p))(a, k, p))

# --- 5. ln4·(1 + A·Gauss(ℓ; ℓ₀, σ)) 族 (O117 型) ---
L0_POOL = [('0.5', mp.mpf('0.5')), ('log₄φ', mp.log(phi,4)), ('1/2', mp.mpf(1)/2),
           ('log₄(μ²/√2)', mp.log(mu2/sq2,4)), ('0.45', mp.mpf('0.45'))]
S_POOL = [('σ_φ', sig_phi), ('log₄(4/3)', mp.log(mp.mpf(4)/3,4)), ('log₄φ', mp.log(phi,4)),
          ('1/4', mp.mpf(1)/4), ('1/(2√2)', 1/(2*sq2)), ('σ_φ·4/3', sig_phi*4/3)]
for anm, A in [('φ⁻³', phi3), ('φ⁻²', phi2), ('φ⁻¹', phi_inv), ('√2−1', sq2-1), ('1/4', mp.mpf(1)/4),
               ('φ⁻³·√2', phi3*sq2), ('φ⁻³/√2', phi3/sq2), ('2/9', mp.mpf(2)/9)]:
    for l0nm, l0 in L0_POOL:
        for snm, s in S_POOL:
            add(f'ln4(1+{anm}·G[{l0nm},{snm}])',
                (lambda A, l0, s: (lambda e: ln4*(1+A*mp.exp(-(e-l0)**2/(2*s*s)))))(A, l0, s))

# --- 6. 混合: φ·w + √2·(1−w), w = x^k ---
for k in [1, 2, 3]:
    add(f'φ·x^{k}+√2(1−x^{k})', (lambda k: (lambda e: phi*4**(-k*e)+sq2*(1-4**(-k*e))))(k))
for k in [1]:
    add(f'√2·x^{k}+φ(1−x^{k})', (lambda k: (lambda e: sq2*4**(-k*e)+phi*(1-4**(-k*e))))(k))

# --- 7. 譜窗加權平均 (窗規則 × 權重) ---
def wavg(nmax, numf, denf):
    ns = [n for n in range(1, int(nmax)+1)]
    if not ns: return mp.mpf(1)
    return sum(numf(n) for n in ns)/sum(denf(n) for n in ns)
WEIGHTS = {
    'sec':   (lambda n: sec_n(n), lambda n: mp.mpf(1)),
    'γsec':  (lambda n: gam_n(n)*sec_n(n), lambda n: gam_n(n)),
    'sec²':  (lambda n: sec_n(n)**2, lambda n: sec_n(n)),
    'γ²sec': (lambda n: gam_n(n)**2*sec_n(n), lambda n: gam_n(n)**2),
    'sec/γ': (lambda n: sec_n(n)/gam_n(n), lambda n: 1/gam_n(n)),
}
WINDOWS = {
    'n≤27':            (lambda e: 27),
    'n≤44·4^{−ℓ}':      (lambda e: 44*4**(-e)),
    'n≤44(1−4^{−ℓ})':   (lambda e: 44*(1-4**(-e))),
    '[22,27]':         (lambda e: 27),
    '[22,27] shrink':  (lambda e: 27),
}
for wnm, (nf, df) in WEIGHTS.items():
    for wdnm, wf in [('n≤27', lambda e: 27), ('n≤44·4^{−ℓ}', lambda e: 44*4**(-e)),
                     ('n≤44(1−4^{−ℓ})', lambda e: 44*(1-4**(-e)))]:
        add(f'⟨{wnm}⟩ win {wdnm}', (lambda nf, df, wf: (lambda e: wavg(min(wf(e), 27), nf, df)))(nf, df, wf))
# 窗 [22, n_hi] 收窄至 {22}
for hi in ['27', '26', '24']:
    add(f'⟨sec⟩ [22,{hi}]→22 linear', (lambda hi: (lambda e: wavg(27 if e < 0.5 else 22, lambda n: sec_n(n), lambda n: mp.mpf(1))))(hi))

# --- 8. 兩區制 (shallow 常數 → 深 √2) ---
for cnm, c in [('φ', phi), ('ln4(1+δk0)|0.5', None), ('1.63', mp.mpf('1.63'))]:
    for cutnm, cut in [('ℓ_cut=0.806', ell_cut), ('ℓ=0.75', mp.mpf('0.75')), ('ℓ=ℓ_nyq/2.5', ell_nyq/mp.mpf('2.5'))]:
        if c is None:
            f = (lambda cut: (lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2))) if e < cut else sq2))(cut)
            add(f'2-regime ln4(1+δk0) | √2 @ {cutnm}', f)
        else:
            f = (lambda c, cut: (lambda e: c if e < cut else sq2))(c, cut)
            add(f'2-regime {cnm} | √2 @ {cutnm}', f)

# ---------------- 排序 ----------------
res = []
for nm, f in CAND.items():
    try:
        c = chi2DH(f)
        if c == c and abs(c) < mp.mpf('1e12'):
            res.append((float(c), nm, float(maxsig(f)), float(f(mp.mpf('0.5'))), float(f(mp.mpf('20')))))
    except Exception as ex:
        pass
res.sort()
print("="*100)
print("O170 scripts/02 — 徑向取樣核 K(ℓ) 結構候選掃描 (零自由參數)")
print("="*100)
print(f"候選總數: {len(CAND)}")
print(f"\n{'rank':<5}{'χ²_DH':>9}{'max|σ|':>8}{'M(0.5)':>9}{'M(∞)':>9}  candidate")
print("-"*100)
for i, (c, nm, ms, m05, minf) in enumerate(res[:35]):
    print(f"{i+1:<5}{c:>9.2f}{ms:>8.2f}{m05:>9.4f}{minf:>9.4f}  {nm}")
print("\n--- 參考: 純結構點 ---")
print(f"{'':5}{float(chi2DH(lambda e: ln4*(1+phi3*mp.exp(-(e-mp.mpf('0.5'))**2/(2*sig_phi**2))))):>9.2f}"
      f"{'':8}{'':9}{'':9}  ln4(1+φ⁻³G[0.5,σ_φ])  (O117 純共振)")
print(f"{'':5}{float(chi2DH(lambda e: phi)):>9.2f}{'':8}{float(phi):>9.4f}{float(phi):>9.4f}  const φ")
print(f"{'':5}{float(chi2DH(lambda e: sq2)):>9.2f}{'':8}{float(sq2):>9.4f}{float(sq2):>9.4f}  const √2")

json.dump([{'chi2': c, 'name': nm, 'maxsig': ms, 'M05': m05, 'Minf': minf} for c, nm, ms, m05, minf in res[:60]],
          open('/tmp/o170_scan.json', 'w'), indent=1)
print(f"\n→ top 60 寫入 /tmp/o170_scan.json")
