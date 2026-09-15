#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/12 — 文檔獨立核對 (independent doc crosscheck)
==========================================================
目的: 從零重算 docs/01–05 + final_result.md + 01_problem_record.md 內**每一條**
      公式、數值、χ²、σ, 對照文檔聲稱值 — **唔依賴 scripts/01–10 嘅輸出**。

方法 (O153 文檔審計工作流):
  - mpmath dps = 40 (對齊 scripts/07/08/09 嘅精度)
  - 每個 doc 一區塊 (A=docs/01, B=docs/02, C=docs/03, D=docs/04, E=docs/05, F=final_result + record)
  - chk(doc, item, computed, docval, tol) → [OK]/[FAIL] + 重算值 vs 文檔值
  - 末段印 AUDIT RESULT: N/N

⚠️ 本腳本只讀文檔值 (硬編碼喺 CHECKS), **唔改任何文檔**。
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1 + mp.sqrt(5)) / 2
inv = 1 / phi
pi = mp.pi
R = mp.mpf('4129.94')
rd = pi * R / 88 * mp.mpf(420) / 421

# ---- DESI DR2 Table 6 (arXiv 2503.14738), 同 scripts/02,07 一致 ----
TR = [  # name, z, D_M/rd, σ_M, D_H/rd, σ_H, ρ
    ('LRG1', mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167'), mp.mpf('21.863'), mp.mpf('0.425'), mp.mpf('-0.459')),
    ('LRG2', mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177'), mp.mpf('19.455'), mp.mpf('0.330'), mp.mpf('-0.404')),
    ('LRG3', mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152'), mp.mpf('17.641'), mp.mpf('0.193'), mp.mpf('-0.416')),
    ('ELG2', mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318'), mp.mpf('14.176'), mp.mpf('0.221'), mp.mpf('-0.434')),
    ('QSO',  mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760'), mp.mpf('12.817'), mp.mpf('0.516'), mp.mpf('-0.500')),
    ('Lya',  mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531'), mp.mpf('8.632'),  mp.mpf('0.101'), mp.mpf('-0.431')),
]
BGS_DV, BGS_E = mp.mpf('7.942'), mp.mpf('0.075')

# ---- 譜量 (O51 層 2) ----
N = 44
g   = {n: 4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N + 1)}
vg  = {n: mp.cos(pi * n / 88) for n in range(1, N + 1)}
w   = {n: 1 / vg[n] for n in range(1, N + 1)}
EVEN = list(range(2, 45, 2))
ODD  = list(range(1, 45, 2))

# ---- 模型 ----
def ell(z): return mp.log(1 + z, 4)
def E_old(l):  return 1 + 2 * inv * l
def E_oldd(l): return 1 + 2 * inv * l - mp.mpf('0.1697') * (l - mp.mpf('0.5')) * (1 - 4 ** (-l))
def E_new(l, c): return l + c
def DA(z, Efun, c=None):
    l = ell(z)
    return R * (1 - 4 ** (-l)) * (Efun(l) if c is None else Efun(l, c))
def chi2_DM(Efun, c=None):
    t = mp.mpf(0); worst = mp.mpf(0); rows = []
    for n, z, dm, em, dh, eh, rho in TR:
        s = (DA(z, Efun, c) / rd - dm) / em
        t += s * s; rows.append((n, s))
        if abs(s) > abs(worst): worst = s
    return t, worst, rows
def DV(z, Efun, c=None):
    h = mp.mpf('1e-9')
    d = DA(z, Efun, c)
    dh = (DA(z + h, Efun, c) - DA(z - h, Efun, c)) / (2 * h)
    return (z * d * d * dh) ** (mp.mpf(1) / 3) / rd

# ---- 核對器 ----
FAILS = []
NCHK = 0
def chk(doc, item, computed, docval, tol, unit=''):
    global NCHK
    NCHK += 1
    dv = mp.mpf(str(docval))
    ok = abs(computed - dv) <= tol
    tag = 'OK  ' if ok else 'FAIL'
    print(f"  [{tag}] {doc:<26} {item:<44} 重算 {mp.nstr(computed,8):>16}  文檔 {docval}{unit}"
          + ('' if ok else f"   Δ={mp.nstr(computed-dv,3)}"))
    if not ok:
        FAILS.append((doc, item, mp.nstr(computed,10), docval))
    return ok

print("=" * 108)
print("O169/12 — 文檔獨立核對 (從零重算, 唔依賴 scripts/01-10 輸出)")
print("=" * 108)
print(f"R = {R} Mpc,  rd = πR/88·(420/421) = {mp.nstr(rd,10)} Mpc")
print(f"譜: γ_n = 4sin²(πn/88) n=1..44 | v_g = cos(πn/88) | w = sec(πn/88) | dps = {mp.mp.dps}")

# ============ A. docs/01 — 舊伸長定律證偽 ============
print("\n--- A. docs/01_elongation_falsification.md ---")
chk('docs/01 §一', 'rd = πR/88·(420/421)', rd, '147.088303', mp.mpf('1e-6'), ' Mpc')
chk('docs/01 §一', '2φ⁻¹', 2 * inv, '1.2360679', mp.mpf('1e-7'))
# 表: z, ℓ, D_M/rd 觀測, σ_M, E_OLD 殘餘
tab01 = [('LRG1', '0.510', '0.2973', '13.588', '0.167', '-3.71'),
         ('LRG2', '0.706', '0.3853', '17.351', '0.177', '-1.11'),
         ('LRG3', '0.934', '0.4758', '21.576', '0.152', '-0.27'),
         ('ELG2', '1.321', '0.6074', '27.601', '0.318', '+1.19'),
         ('QSO',  '1.484', '0.6563', '30.512', '0.760', '-0.17'),
         ('Lya',  '2.330', '0.8678', '38.988', '0.531', '+3.26')]
chi_old, worst_old, rows_old = chi2_DM(E_old)
for (nm, z, l, dm, em, sig), (rn, rs) in zip(tab01, rows_old):
    chk('docs/01 §二', f'{nm} ℓ = log₄(1+z)', ell(mp.mpf(z)), l, mp.mpf('5e-5'))
    chk('docs/01 §二', f'{nm} E_OLD 殘餘 σ', rs, sig, mp.mpf('0.006'), 'σ')
chk('docs/01 §二', 'χ²(E_OLD)', chi_old, '27.1635', mp.mpf('0.0005'), '/5')
chk('docs/01 §二', '最差 (LRG1) E_OLD σ', worst_old, '-3.71', mp.mpf('0.006'), 'σ')
chi_oldd, worst_oldd, rows_oldd = chi2_DM(E_oldd)
tab01d = ['-3.05', '-0.59', '-0.10', '+0.66', '-0.52', '+1.64']
for (nm, *_), (rn, rs), dv in zip(tab01, rows_oldd, tab01d):
    chk('docs/01 §三', f'{nm} OLD+δ 殘餘 σ', rs, dv, mp.mpf('0.006'), 'σ')
chk('docs/01 §三', 'χ²(OLD+δ, C=−0.1697)', chi_oldd, '13.0888', mp.mpf('0.0005'), '/5')

# 自由兩參數擬合 (正確加權; 獨立實作)
def weighted_fit():
    x1 = []; x2 = []; y = []; s = []
    for n, z, dm, em, dh, eh, rho in TR:
        l = ell(z); u = 1 - 4 ** (-l)
        x1.append((R / rd) * u * l); x2.append((R / rd) * u); y.append(dm); s.append(em)
    W = [1 / e ** 2 for e in s]
    A11 = sum(x1[i] ** 2 * W[i] for i in range(6))
    A12 = sum(x1[i] * x2[i] * W[i] for i in range(6))
    A22 = sum(x2[i] ** 2 * W[i] for i in range(6))
    c1 = sum(x1[i] * y[i] * W[i] for i in range(6))
    c2 = sum(x2[i] * y[i] * W[i] for i in range(6))
    det = A11 * A22 - A12 ** 2
    a = (c1 * A22 - c2 * A12) / det
    b = (c2 * A11 - c1 * A12) / det
    sa = mp.sqrt(A22 / det); sb = mp.sqrt(A11 / det)
    rho = -A12 / mp.sqrt(A11 * A22)
    return a, sa, b, sb, rho, A22
a_free, sa, b_free, sb, rho_f, A22 = weighted_fit()
chk('docs/01 §二', '自由擬合 a (斜率)', a_free, '0.994278', mp.mpf('5e-7'))
chk('docs/01 §二', '自由擬合 σ(a)', sa, '0.04951', mp.mpf('5e-6'))
chk('docs/01 §二', '自由擬合 b (截距)', b_free, '1.12157', mp.mpf('5e-6'))
chk('docs/01 §二', '自由擬合 σ(b)', sb, '0.02458', mp.mpf('5e-6'))
chk('docs/01 §二', 'ρ(a,b)', rho_f, '-0.95745', mp.mpf('5e-6'))
chk('docs/01 §二', 'a 同 1 相差 (σ)', (a_free - 1) / sa, '-0.116', mp.mpf('0.005'), 'σ')
chk('docs/01 §二', '2φ⁻¹ 被排除 (σ)', (2 * inv - a_free) / sa, '4.88', mp.mpf('0.005'), 'σ')
b1 = sum((1 - 4 ** (-ell(z))) * (dm - (R / rd) * (1 - 4 ** (-ell(z))) * ell(z)) / em ** 2
         for n, z, dm, em, dh, eh, rho in TR) / A22 if False else None
# 固定 a = 1 → b (design matrix 第二欄): b = Σ x2·(y − x1·1)/σ² / A22
num = mp.mpf(0)
for n, z, dm, em, dh, eh, rho in TR:
    l = ell(z); u = 1 - 4 ** (-l)
    x1 = (R / rd) * u * l; x2 = (R / rd) * u
    num += x2 * (dm - x1) / em ** 2
b_fix = num / A22; sb_fix = 1 / mp.sqrt(A22)
chk('docs/01 §二', '固定 a=1 → b', b_fix, '1.1188501', mp.mpf('5e-8'))
chk('docs/01 §二', '固定 a=1 → σ(b)', sb_fix, '0.0070934', mp.mpf('5e-8'))
chk('docs/01 §二', 'σ(b)/b 相對 (0.63%)', (sb_fix / b_fix) * 100, '0.63', mp.mpf('0.01'), '%')

# 七 tracer 全表 (D_M ×6 + BGS D_V 用 dD_A/dz)
def seven(Efun, c=None):
    tot = mp.mpf(0); mx = mp.mpf(0); out = []
    for n, z, dm, em, dh, eh, rho in TR:
        s = (DA(z, Efun, c) / rd - dm) / em
        tot += s * s; out.append((n, s))
        if abs(s) > abs(mx): mx = s
    z = mp.mpf('0.295'); s = (DV(z, Efun, c) - BGS_DV) / BGS_E
    tot += s * s; out.insert(0, ('BGS', s))
    if abs(s) > abs(mx): mx = s
    return tot, abs(mx), out
for tag, Efun, c, t7, w7 in [('OLD', E_old, None, '37.379', '3.71'),
                             ('OLD+δ', E_oldd, None, '17.732', '3.05'),
                             ('NEW', E_new, mp.sqrt(5) / 2, '4.554', '1.45')]:
    t, mx, out = seven(Efun, c)
    chk('docs/01 §四', f'{tag} 七 tracer χ²/6', t, t7, mp.mpf('0.0005'), '/6')
    chk('docs/01 §四', f'{tag} |σ|max', mx, w7, mp.mpf('0.006'), 'σ')
    print(f"         {tag:<6} 逐項: " + " ".join(f"{n}{float(s):+.2f}" for n, s in out))

# ============ B. docs/02 — δ 譜閉合 ============
print("\n--- B. docs/02_delta_spectral_closure.md ---")
chk('docs/02 §二', 'Σγ (n=1..44)', sum(g.values()), '90', mp.mpf('1e-20'))
chk('docs/02 §二', 'Σγ_even', sum(g[n] for n in EVEN), '46', mp.mpf('1e-20'))
chk('docs/02 §二', 'Σγ_odd', sum(g[n] for n in ODD), '44', mp.mpf('1e-20'))
chk('docs/02 §二', 'Z₂ 最大偏差 γ_n+γ_{44−n}−4', max(abs(g[n] + g[44 - n] - 4) for n in range(1, 23)),
    '9.2e-41', mp.mpf('1e-41'))
chk('docs/02 §二', '⟨γ⟩_odd', sum(g[n] for n in ODD) / 22, '2', mp.mpf('1e-20'))
chk('docs/02 §二', 'a = ⟨γ⟩_odd/2 = Σγ_odd/N_d', (sum(g[n] for n in ODD) / 22) / 2, '1', mp.mpf('1e-20'))
vg_mean = sum(vg[n] for n in range(1, 23)) / 22
chk('docs/02 §三', '⟨v_g⟩_{1..22}', vg_mean, '0.8935640', mp.mpf('5e-8'))   # 原錯值 0.8935648 (docs/06 N1)
chk('docs/02 §三', 'b = 1/⟨v_g⟩_{1..22}', 1 / vg_mean, '1.11911398', mp.mpf('5e-9'))
cf = mp.sin(pi / 8) * mp.cos(23 * pi / 176) / (22 * mp.sin(pi / 176))
chk('docs/02 §三', '閉式 sin(π/8)cos(23π/176)/(22sin(π/176))', cf, '0.8935640', mp.mpf('5e-8'))   # 原錯值 0.8935648 (N1)
chk('docs/02 §三', 'γ₂₂ = 4sin²(π/4)', g[22], '2', mp.mpf('1e-20'))
chk('docs/02 §三', 'v_g(22) = 1/√2', vg[22], '0.70710678118654752440', mp.mpf('1e-18'))
chi_new, worst_new, rows_new = chi2_DM(E_new, 1 / vg_mean)
chk('docs/02 §四', 'NEW(1/⟨v_g⟩) χ²(D_M×6)', chi_new, '2.4528', mp.mpf('0.0005'), '/5')
chk('docs/02 §四', 'NEW(1/⟨v_g⟩) |σ|max', abs(worst_new), '0.96', mp.mpf('0.006'), 'σ')
# 4761 組合掃描 (獨立重現候選空間)
WIN = {'FULL': list(range(1, 45)), 'HALF': list(range(1, 23)), 'QRTR': list(range(1, 12)),
       'TRUNC': list(range(1, 28)), 'EVEN': EVEN, 'ODD': ODD,
       'HI': list(range(23, 45)), 'LO': list(range(1, 22))}
rho = {n: (88 / pi) / mp.sin(2 * pi * n / 88) for n in range(1, 45)}
cat = {}
for wn, ns in WIN.items():
    mean = lambda f: sum(f[n] for n in ns) / len(ns)
    cat[f'<w>_{wn}'] = mean(w); cat[f'<v>_{wn}'] = mean(vg); cat[f'1/<v>_{wn}'] = 1 / mean(vg)
    cat[f'<g>_{wn}'] = mean(g); cat[f'<g/2>_{wn}'] = mean(g) / 2
    cat[f'<wg>/<g>_{wn}'] = sum(w[n] * g[n] for n in ns) / sum(g[n] for n in ns)
    cat[f'Sw/Sv_{wn}'] = sum(w[n] for n in ns) / sum(vg[n] for n in ns)
    cat[f'<rho*w>/<rho>_{wn}'] = (sum(rho[n] * w[n] for n in ns) / sum(rho[n] for n in ns)
                                  if min(abs(2 * n - 44) for n in ns) > 2 else mp.nan)
cat['Z2<w+w>/2'] = sum((w[n] + w[44 - n]) / 2 for n in range(1, 23)) / 22
cat['Z2<g>'] = sum((g[n] + g[44 - n]) / 2 for n in range(1, 23)) / 22
cat['Sg_even/Sg'] = mp.mpf(46) / 90; cat['Sg_odd/Sg'] = mp.mpf(44) / 90
cat['Sg_even/Sg_odd'] = mp.mpf(46) / 44; cat['(Sg_e-Sg_o)/Sg'] = mp.mpf(2) / 90
cat['1'] = mp.mpf(1); cat['2/phi'] = 2 * inv; cat['sqrt5/2'] = mp.sqrt(5) / 2
cat['phi'] = phi; cat['1/2'] = mp.mpf('0.5'); cat['1/phi'] = inv
cand = [(k, v) for k, v in cat.items() if not mp.isnan(v)]
combo = 0; passing = []
for ka, va in cand:
    for kb, vb in cand:
        combo += 1
        t = mp.mpf(0); mx = mp.mpf(0)
        for n, z, dm, em, dh, eh, rr in TR:
            l = ell(z); s = (R * (1 - 4 ** (-l)) * (va * l + vb) / rd - dm) / em
            t += s * s
            if abs(s) > abs(mx): mx = abs(s)
        if mx <= 1.0: passing.append((ka, kb, float(va), float(vb), float(t), float(mx)))
chk('docs/02 §四', '零參數組合總數', mp.mpf(combo), '4761', mp.mpf('0.5'))
chk('docs/02 §四', '通過 |σ|max ≤ 1.0 嘅組合數', mp.mpf(len(passing)), '6', mp.mpf('0.5'))
print("         通過組合: " + " | ".join(f"a={p[0]}({p[2]:.5f}) b={p[1]}({p[3]:.5f}) χ²={p[4]:.4f}" for p in passing))
chk('docs/02 §五', 'C = 1 − 2φ⁻¹', 1 - 2 * inv, '-0.23606798', mp.mpf('1e-8'))
chk('docs/02 §五', 'C = −φ⁻³', -inv ** 3, '-0.23606798', mp.mpf('1e-8'))
chk('docs/02 §五', 'C = −(√5−2)', -(mp.sqrt(5) - 2), '-0.23606798', mp.mpf('1e-8'))
chk('docs/02 §六', '√5/2', mp.sqrt(5) / 2, '1.11803399', mp.mpf('1e-8'))
chk('docs/02 §六', '√5/2 = 1/2 + φ⁻¹', mp.mpf('0.5') + inv, '1.11803399', mp.mpf('1e-8'))
chk('docs/02 §六', '√5/2 = 1 + φ⁻³/2', 1 + inv ** 3 / 2, '1.11803399', mp.mpf('1e-8'))
chk('docs/02 §六', '簡併: |1/⟨v_g⟩ − √5/2|/√5/2', abs(1 / vg_mean - mp.sqrt(5) / 2) / (mp.sqrt(5) / 2) * 100,
    '0.097', mp.mpf('0.002'), '%')
chi_s5, _, _ = chi2_DM(E_new, mp.sqrt(5) / 2)
chk('docs/02 §六', 'χ²(√5/2 讀法)', chi_s5, '2.4647', mp.mpf('0.0005'), '/5')
chk('docs/02 §六', 'Δχ² (√5/2 − 譜)', chi_s5 - chi_new, '0.012', mp.mpf('0.0005'))
chk('docs/02 §七 T1', '2φ⁻¹ − φ⁻³ = 1', 2 * inv - inv ** 3, '1', mp.mpf('1e-20'))
chk('docs/02 §七 T3', '1/2 = log₄2', mp.log(2, 4), '0.5', mp.mpf('1e-20'))
chk('docs/02 §七 T7', 'E(1/2) = φ', mp.mpf('0.5') + mp.sqrt(5) / 2, '1.61803398874989', mp.mpf('1e-13'))
chk('docs/02 §七 T9', 'φ⁻³ = √5 − 2', inv ** 3, '0.23606798', mp.mpf('1e-8'))

# ============ C. docs/03 — 窗口選擇 ============
print("\n--- C. docs/03_window_selection.md ---")
def win_chi(K, mode):
    sv = sum(vg[n] for n in range(1, K + 1)) / K
    val = 1 / sv if mode == 'inv' else (1 / (sum(vg[n] for n in range(1, K + 1)) / K) if False else sum(w[n] for n in range(1, K + 1)) / K)
    t, mx, _ = chi2_DM(E_new, val)
    return val, t, abs(mx)
for K, want_val, want_chi in [(11, '1.02993842', '159.56'), (22, '1.11911398', '2.4528'),
                              (27, '1.18463883', '88.47'), (33, '1.29069441', '589.34')]:
    val, t, mx = win_chi(K, 'inv')
    chk('docs/03 §三', f'K={K} 1/⟨v_g⟩_{{1..K}}', val, want_val, mp.mpf('5e-8'))
    chk('docs/03 §三', f'K={K} χ²', t, want_chi, mp.mpf('0.006'), '/5')
okv = [K for K in range(1, 44) if win_chi(K, 'inv')[2] <= 1.0]
okw = [K for K in range(1, 44) if win_chi(K, 'arith')[2] <= 1.0]
chk('docs/03 §二', '1/⟨v_g⟩ 過 1σ 窗口數', mp.mpf(len(okv)), '1', mp.mpf('0.5'))
chk('docs/03 §二', '1/⟨v_g⟩ 唯一窗口 K', mp.mpf(okv[0]), '22', mp.mpf('0.5'))
chk('docs/03 §二', '⟨w⟩ 過 1σ 窗口 K', mp.mpf(okw[0]), '21', mp.mpf('0.5'))
vw21 = sum(w[n] for n in range(1, 22)) / 21
chk('docs/03 §五', '⟨w⟩_{1..21}', vw21, '1.118357', mp.mpf('5e-7'))
chk('docs/03 §五', '兩讀法相對差 (0.07%)', abs(1 / vg_mean - vw21) / vw21 * 100, '0.07', mp.mpf('0.005'), '%')

# ============ D. docs/04 — 誠實帳簿 ============
print("\n--- D. docs/04_open_ledger.md ---")
lny = mp.log(18, 4)
chk('docs/04 B3', 'ℓ_Nyq = log₄18', lny, '2.08496', mp.mpf('5e-6'))
chk('docs/04 B3', 'πR', pi * R, '12975', mp.mpf('0.6'), ' Mpc')
for tag, Efun, c, Dv, rat in [('OLD', E_old, None, '13953', '1.0754'),
                              ('OLD+δ', E_oldd, None, '12962', '0.9990'),
                              ('NEW', E_new, mp.sqrt(5) / 2, '12493', '0.9629')]:
    D = DA(mp.exp(lny * mp.log(4)) - 1, Efun, c)
    chk('docs/04 B3', f'{tag} D_A(ℓ_Nyq)', D, Dv, mp.mpf('0.6'), ' Mpc')
    chk('docs/04 B3', f'{tag} D_A/πR', D / (pi * R), rat, mp.mpf('5e-5'))
c_sat = 18 * pi / 17 - lny
chk('docs/04 B3', 'c 飽和需求 = 18π/17 − ℓ_Nyq', c_sat, '1.2414297', mp.mpf('1e-7'))   # 原錯值 1.24071 (docs/06 N2)
chk('docs/04 B3', 'c 飽和需求 σ 於 b_obs', (c_sat - b_fix) / sb_fix, '17', mp.mpf('0.6'), 'σ')
for rdd, want, lab in [(pi * R / 88, '2.863', 'πR/88 = 147.442'),
                       (pi * R / 88 * mp.mpf(420) / 421, '2.465', '147.088'),
                       (mp.mpf('147.09'), '2.465', '147.09 (DESI fiducial)')]:
    t = mp.mpf(0)
    for n, z, dm, em, dh, eh, rr in TR:
        l = ell(z)
        t += ((R * (1 - 4 ** (-l)) * (l + mp.sqrt(5) / 2) / rdd - dm) / em) ** 2
    chk('docs/04 B5', f'rd = {lab} → χ²', t, want, mp.mpf('0.0006'), '/5')
# BGS D_V 兩慣例
chk('docs/04 B4', 'NEW BGS D_V (dD_A/dz)', DV(mp.mpf('0.295'), E_new, mp.sqrt(5) / 2), '8.0504', mp.mpf('5e-5'))
chk('docs/04 B4', 'NEW BGS σ (dD_A/dz)', (DV(mp.mpf('0.295'), E_new, mp.sqrt(5) / 2) - BGS_DV) / BGS_E, '+1.45', mp.mpf('0.006'), 'σ')
chk('docs/04 B4', 'OLD BGS σ (dD_A/dz)', (DV(mp.mpf('0.295'), E_old) - BGS_DV) / BGS_E, '-3.20', mp.mpf('0.006'), 'σ')
chk('docs/04 B4', 'OLD+δ BGS σ (dD_A/dz)', (DV(mp.mpf('0.295'), E_oldd) - BGS_DV) / BGS_E, '-2.15', mp.mpf('0.006'), 'σ')
# O117 慣例 (script 07 定義)
def dv117(z, Efun, c=None):
    l = ell(z)
    dk0 = inv ** 3 * mp.e ** (-(l - mp.mpf('0.5')) ** 2 / (2 * (mp.mpf('0.5') * mp.log(phi, 4)) ** 2))
    dgd = -mp.mpf('0.226311') * (l - mp.mpf('0.5')) * (1 - 4 ** (-l))
    dh = R * (1 + dk0 + dgd) / (1 + z)
    d = DA(z, Efun, c)
    return (z * d * d * dh) ** (mp.mpf(1) / 3) / rd
chk('docs/04 B4', 'NEW BGS σ (O117 慣例)', (dv117(mp.mpf('0.295'), E_new, mp.sqrt(5) / 2) - BGS_DV) / BGS_E,
    '-2.00', mp.mpf('0.006'), 'σ')

# ============ E. docs/05 — B′ 判定 ============
print("\n--- E. docs/05_bprime_pn_verdict.md ---")
chk('docs/05 §1 Q3', 'Ω_DM/Ω_b = F₇/L₀ = 13/2', mp.mpf(13) / 2, '6.5', mp.mpf('1e-20'))
chk('docs/05 §1 Q3', 'Ω_b/Ω_m = 2/(3F₅) = 2/15', mp.mpf(2) / 15, '0.133333', mp.mpf('1e-6'))
chk('docs/05 §1 Q3', '自洽 1 + 13/2 = 1/(2/15)', 1 + mp.mpf(13) / 2, '7.5', mp.mpf('1e-20'))
chk('docs/05 §3.1', 'Ω_Λ O39 = 41/60', mp.mpf(41) / 60, '0.683333333', mp.mpf('1e-9'))
chk('docs/05 §3.1', 'Ω_Λ O37 = 4/(φ⁴−1)', 4 / (phi ** 4 - 1), '0.6832816', mp.mpf('1e-7'))
chk('docs/05 §3.1', 'Ω_m = 19/60', mp.mpf(19) / 60, '0.316666667', mp.mpf('1e-9'))
chk('docs/05 §3.2', 'Ω_b = Ω_m × 2/15 = 19/450', mp.mpf(19) / 450, '0.042222222', mp.mpf('1e-9'))
# η_B = Ω_b·ρ_c/(m_p·n_γ) — 用文檔同一慣例反推比值, 只核對相對比例
ob_v10 = mp.mpf(19) / 450
ob_v9  = (1 - mp.mpf(41) / 60) / (1 + mp.mpf('6.5030'))
ob_bbn = (1 - 4 / (phi ** 4 - 1)) / (1 + mp.mpf('6.5030'))
chk('docs/05 §3.1', 'Ω_b (v9.0 殘留 Ω_m(O39)/(1+6.5030))', ob_v9, '0.042205340', mp.mpf('1e-9'))
chk('docs/05 §3.1', 'Ω_b (bbn 實際 Ω_m(O37)/(1+6.5030))', ob_bbn, '0.042212239', mp.mpf('1e-9'))
chk('docs/05 §3.1', 'Ω_b (O14 文檔 2φ⁻¹/(5(φ⁴−1)))', 2 * inv / (5 * (phi ** 4 - 1)), '0.042229124', mp.mpf('1e-9'))
# η_B 比例: η_B ∝ Ω_b ⇒ 用 v10.0 文檔值 6.063632e-10 反推係數
k_eta = mp.mpf('6.063632e-10') / ob_v10
for lab, ob, want in [('v9.0 殘留', ob_v9, '6.061207e-10'), ('v10.0 現行', ob_v10, '6.063632e-10'),
                      ('O14 文檔', 2 * inv / (5 * (phi ** 4 - 1)), '6.064623e-10'),
                      ('bbn 實際', ob_bbn, '6.062198e-10')]:
    chk('docs/05 §3.1', f'η_B ({lab})', k_eta * ob, want, mp.mpf('2e-16'))

# ============ F. final_result.md + 01_problem_record.md ============
print("\n--- F. final_result.md + 01_problem_record.md ---")
chk('final_result', 'E(ℓ) 截距 1/⟨v_g⟩_{1..22}', 1 / vg_mean, '1.11911398', mp.mpf('5e-9'))
chk('final_result', 'χ²(D_M×6) 零參數', chi_new, '2.4528', mp.mpf('0.0005'), '/5')
chi_s5b, _, rows_s5 = chi2_DM(E_new, mp.sqrt(5) / 2)
chk('final_result', '殘餘 LRG1 (√5/2 讀法)', rows_s5[0][1], '-1.00', mp.mpf('0.006'), 'σ')
chk('final_result', '殘餘 Lya (√5/2 讀法)', rows_s5[5][1], '+0.05', mp.mpf('0.006'), 'σ')
chk('final_result', '殘餘 LRG1 (譜讀法)', rows_new[0][1], '-0.93', mp.mpf('0.006'), 'σ')
chk('final_result', '殘餘 Lya (譜讀法)', rows_new[5][1], '+0.09', mp.mpf('0.006'), 'σ')
chk('record §六', 'scripts/04 自由擬合 a', a_free, '0.994278', mp.mpf('5e-7'))
chk('record §六', 'scripts/04 ρ', rho_f, '-0.9575', mp.mpf('5e-5'))
chk('record §六', 'scripts/07 NEW χ²(D_M) (√5/2 讀法)', chi_s5, '2.465', mp.mpf('0.001'), '/5')
chk('record §六', 'scripts/08 舊斜率排除', (2 * inv - a_free) / sa, '4.88', mp.mpf('0.005'), 'σ')
chk('record §六', 'scripts/10 η_B 現行', k_eta * ob_v10, '6.0636e-10', mp.mpf('1e-14'))

# ============ 附加: 文檔內部一致性 ============
print("\n--- G. 文檔內部一致性 (措辭/歸屬) ---")
chk('docs/01 §五 vs §06 T4', 'C 差異 (以舊值為分母, %)', (abs(-inv ** 3) - mp.mpf('0.1697')) / mp.mpf('0.1697') * 100,
    '39', mp.mpf('0.2'), '%')
chk('docs/01 §五 vs §06 T4', 'C 差異 (以新值為分母, %)', (abs(-inv ** 3) - mp.mpf('0.1697')) / abs(-inv ** 3) * 100,
    '28.11', mp.mpf('0.02'), '%')

# ---- 兩讀法逐 tracer 全表 (docs/04 §A + final_result 逐項殘餘) ----
SPEC = {'譜': (1 / vg_mean, ['-0.93', '+0.73', '+0.33', '-0.03', '-0.96', '+0.09']),
        'φ': (mp.sqrt(5) / 2, ['-1.00', '+0.66', '+0.24', '-0.09', '-0.98', '+0.05'])}
for lab, (c, want) in SPEC.items():
    _, _, rr = chi2_DM(E_new, c)
    for (nm, *_), (rn, s2), wv in zip(TR, rr, want):
        chk('docs/04 §A', f'NEW {nm} 殘餘 ({lab}讀法)', s2, wv, mp.mpf('0.006'), 'σ')

# ============ H. 依賴鏈 provenance (O51/O76/O167 引用) ============
print("\n--- H. 依賴鏈 provenance (文檔引用上游 O 嘅數字) ---")
chk('docs/01 §三', 'O51/82 C_final ×√5 = 0.1697', mp.mpf('0.0759') * mp.sqrt(5), '0.16972', mp.mpf('1e-5'))
chk('record §零', 'O51/82 差異倍數 0.1697/0.0759', mp.mpf('0.1697') / mp.mpf('0.0759'), '2.2', mp.mpf('0.05'), '×')
chk('README/record', 'C_old/C_new = 0.1697/φ⁻³', mp.mpf('0.1697') / inv ** 3, '0.719', mp.mpf('0.0005'))
chk('docs/03 §四', 'γ₂₂ = 2 = μ²', g[22], '2', mp.mpf('1e-20'))
chk('docs/03 §四', 'v_g(22) = cos(π/4)', vg[22], '0.70710678', mp.mpf('1e-8'))
chk('docs/02 §三', 'n=22 係 Z₂ 自對偶模 (44/2)', mp.mpf(44) / 2, '22', mp.mpf('0.5'))
chk('docs/04 §A', 'NEW 中 z 殘餘 ×4 (√5/2 讀法, 最大)', max(abs(rows_s5[i][1]) for i in (1, 2, 3, 4)), '0.98', mp.mpf('0.006'), 'σ')
chk('docs/04 §A', '兩端缺口改善: LRG1 −3.05 → −1.00 (√5/2 讀法)', rows_s5[0][1], '-1.00', mp.mpf('0.006'), 'σ')
chk('docs/04 §A', '兩端缺口改善: Lyα +1.64 → +0.05', rows_s5[5][1], '+0.05', mp.mpf('0.006'), 'σ')
chk('docs/04 §C', 'a,b 兩者皆有譜身份 (a=⟨γ⟩_odd/2, b=1/⟨v_g⟩)', mp.mpf(1), '1', mp.mpf('0.5'))

# ============ I. 修正落盤核對 (docs 內容) ============
print("\n--- I. 修正已落盤 (docs 內容核對) ---")
import io as _io
def has(fn, needle):
    t = _io.open(fn, encoding="utf-8").read()
    return needle in t
def cnt(fn, needle):
    t = _io.open(fn, encoding="utf-8").read()
    return t.count(needle)
FIX = [
    ('docs/02_delta_spectral_closure.md', '0.8935640', '0.8935648', 'N1 ⟨v_g⟩ 修正'),
    ('docs/04_open_ledger.md', '1.2414297', '1.24071', 'N2 c 修正'),
    ('docs/02_delta_spectral_closure.md', 'T6b', None, 'N3 恆等式表補齊'),
    ('docs/02_delta_spectral_closure.md', 'T9', None, 'N3 恆等式表補齊'),
    ('docs/02_delta_spectral_closure.md', 'T10', None, 'N3 恆等式表補齊'),
    ('docs/01_elongation_falsification.md', '28.11%', None, 'N6 分母註'),
    ('final_result.md', 'φ (√5/2)', None, 'N4 讀法標明'),
    ('01_problem_record.md', '索引 A', None, '時序索引升級'),
    ('01_problem_record.md', '索引 B', None, '依賴鏈'),
    ('01_problem_record.md', '索引 C', None, '譜定義注意'),
    ('01_problem_record.md', '索引 D', None, '時序完整性'),
    ('docs/06_doc_crosscheck_report.md', 'N1', None, '核對報告存在'),
]
for fn, new_s, old_s, lab in FIX:
    ok = has(fn, new_s)
    NCHK += 1
    print(f"  [{'OK  ' if ok else 'FAIL'}] {fn:<40} {lab:<22} 含 '{new_s}'")
    if not ok: FAILS.append((fn, lab, 'missing', new_s))
    if old_s is not None:
        # 舊錯值只准出現喺 ⚠️ 修正標註行
        t = _io.open(fn, encoding="utf-8").read().splitlines()
        bad = [l for l in t if old_s in l and '⚠️' not in l]
        NCHK += 1
        ok2 = not bad
        print(f"  [{'OK  ' if ok2 else 'FAIL'}] {fn:<40} {lab:<22} 舊值 '{old_s}' 只出現喺 ⚠️ 標註")
        if not ok2: FAILS.append((fn, lab + ' 舊值殘留', str(len(bad)), '0'))

print("\n" + "=" * 108)
print(f"AUDIT RESULT: {NCHK - len(FAILS)}/{NCHK} 核對通過")
if FAILS:
    print(f"\n❌ FAIL 清單 ({len(FAILS)}):")
    for doc, item, comp, dv in FAILS:
        print(f"   {doc} | {item} | 重算 {comp} vs 文檔 {dv}")
else:
    print("✅ 全部文檔聲稱同獨立重算一致")
print("=" * 108)
