#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/08 — 譜量閉合掃描 (charter 判準 ①)

目標: E(ℓ) = a·ℓ + b 嘅 (a, b) 可否由譜量 {γ_n, w_n, ρ, Σγ, Z₂} 零參數給出?
      (唔准 φ-代數事後補齊; 只准譜和 / 譜平均 / Z₂ 配對)

譜結構 (O51 層 2):
  γ_n = 4sin²(πn/88)        n = 1..44      (K_Chain 譜)
  v_g(n) = cos(πn/88)                       (群速度)
  w_n = sec(πn/88)                          (群延遲權重)
  ρ(γ) = (88/π)/sin(2πn/88)                 (譜密度 dγ/dn 倒數)
  Σγ = 90, Σγ_even = 46, Σγ_odd = 44,  Z₂: γ_n+γ_{44−n} = 4

窗口 (全部有結構理由):
  FULL 1..44 (全鏈)   HALF 1..22 (Z₂ 自對偶半鏈, n=22=44/2)
  QRTR 1..11 (=L₅)    TRUNC 1..27 (F_proj=17 截斷, O54)
  EVEN / ODD / HI 23..44 / LO 1..21
"""
import mpmath as mp, itertools
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2; inv = 1/phi; pi = mp.pi
R = mp.mpf('4129.94'); rd = pi*R/88*mp.mpf(420)/421

TR = [('LRG1', mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167')),
      ('LRG2', mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177')),
      ('LRG3', mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152')),
      ('ELG2', mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318')),
      ('QSO',  mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760')),
      ('Lya',  mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531'))]

N = 44
g = {n: 4*mp.sin(pi*n/88)**2 for n in range(1, N+1)}
v = {n: mp.cos(pi*n/88)      for n in range(1, N+1)}
w = {n: 1/v[n]               for n in range(1, N+1)}
rho = {n: (88/pi)/mp.sin(2*pi*n/88) for n in range(1, N+1)}

WIN = {'FULL': list(range(1,45)), 'HALF': list(range(1,23)), 'QRTR': list(range(1,12)),
       'TRUNC': list(range(1,28)), 'EVEN': list(range(2,45,2)), 'ODD': list(range(1,45,2)),
       'HI': list(range(23,45)), 'LO': list(range(1,22))}

def mean(f, ns): return sum(f[n] for n in ns)/len(ns)

# ---------- 候選 catalogue ----------
cat = {}
for wn, ns in WIN.items():
    cat[f'<w>_{wn}']   = mean(w, ns)                       # 平均群延遲
    cat[f'<v>_{wn}']   = mean(v, ns)                       # 平均群速度
    cat[f'1/<v>_{wn}'] = 1/mean(v, ns)                     # 倒平均群速度
    cat[f'<g>_{wn}']   = mean(g, ns)                       # 平均譜
    cat[f'<g/2>_{wn}'] = mean(g, ns)/2
    cat[f'<wg>/<g>_{wn}'] = sum(w[n]*g[n] for n in ns)/sum(g[n] for n in ns)  # γ-權重延遲
    cat[f'Sw/Sv_{wn}'] = sum(w[n] for n in ns)/sum(v[n] for n in ns)          # 和比
    cat[f'<rho*w>/<rho>_{wn}'] = (sum(rho[n]*w[n] for n in ns)/sum(rho[n] for n in ns)
                                  if min(abs(2*n-44) for n in ns) > 2 else mp.mpf('nan'))
# Z₂ 配對量
cat['Z2<w+w>/2'] = mean({n: (w[n]+w[44-n])/2 for n in range(1,23)}, list(range(1,23)))
cat['Z2<g>']     = mean({n: (g[n]+g[44-n])/2 for n in range(1,23)}, list(range(1,23)))
# Σγ 組合 (charter 明列)
cat['Sg_even/Sg']  = mp.mpf(46)/90
cat['Sg_odd/Sg']   = mp.mpf(44)/90
cat['Sg_even/Sg_odd'] = mp.mpf(46)/44
cat['(Sg_e-Sg_o)/Sg'] = mp.mpf(2)/90
# φ-代數 (對照組, 非譜)
cat['1'] = mp.mpf(1); cat['2/phi'] = 2*inv; cat['sqrt5/2'] = mp.sqrt(5)/2
cat['phi'] = phi; cat['1/2'] = mp.mpf('0.5'); cat['1/phi'] = inv

def chi2(a, b):
    t = mp.mpf(0); worst = mp.mpf(0)
    for n, z, dm, em in TR:
        l = mp.log(1+z, 4); E = a*l + b
        mod = R*(1-4**(-l))*E/rd
        s = (mod-dm)/em
        t += s*s
        if abs(s) > abs(worst): worst = s
    return t, worst

print("="*84)
print("O169/08 — 譜量閉合掃描: E(ℓ) = a·ℓ + b,  (a,b) 只准由譜量取")
print("="*84)
print(f"rd = {mp.nstr(rd,10)} Mpc,  R = {R} Mpc")
print(f"\n譜量核對: Σγ = {mp.nstr(sum(g.values()),8)}  Σγ_even = {mp.nstr(sum(g[n] for n in WIN['EVEN']),8)}"
      f"  Σγ_odd = {mp.nstr(sum(g[n] for n in WIN['ODD']),8)}")
print(f"Z₂ 最大偏差: {mp.nstr(max(abs(g[n]+g[44-n]-4) for n in range(1,23)),3)}")
print(f"<w>_FULL = {mp.nstr(cat['<w>_FULL'],8)}   <w>_HALF = {mp.nstr(cat['<w>_HALF'],8)}"
      f"   1/<v>_HALF = {mp.nstr(cat['1/<v>_HALF'],8)}")

# ---------- 自由兩參數基準 (正確 design matrix: D_M = (R/rd)(1−4^{−l})(a·l+b)) ----------
def design(z):
    l = mp.log(1+z, 4); u = 1-4**(-l)
    return (R/rd)*u*l, (R/rd)*u          # x1 (乘 a), x2 (乘 b)
A11 = sum((design(z)[0]/em)**2 for _,z,_,em in TR)
A12 = sum(design(z)[0]*design(z)[1]/em**2 for _,z,_,em in TR)
A22 = sum((design(z)[1]/em)**2 for _,z,_,em in TR)
c1 = sum(design(z)[0]*dm/em**2 for _,z,dm,em in TR)
c2 = sum(design(z)[1]*dm/em**2 for _,z,dm,em in TR)
det = A11*A22-A12**2
a_free = (c1*A22-c2*A12)/det; b_free = (c2*A11-c1*A12)/det
sa = mp.sqrt(A22/det); sb = mp.sqrt(A11/det); rho = -A12/mp.sqrt(A11*A22)
print(f"\n自由兩參數擬合 (正確加權): E = a·ℓ + b")
print(f"  a (斜率) = {mp.nstr(a_free,6)} ± {mp.nstr(sa,4)}   → 同 1 相差 {mp.nstr((a_free-1)/sa,3)}σ")
print(f"  b (截距) = {mp.nstr(b_free,6)} ± {mp.nstr(sb,4)}")
print(f"  相關係數 ρ = {mp.nstr(rho,5)}")
print(f"  舊斜率 2φ⁻¹ = {mp.nstr(2*inv,6)}  → 被排除 {mp.nstr((2*inv-a_free)/sa,3)}σ ★")
# 固定 a = 1: 殘餘 dm − x2·ℓ, b = Σ x2·(dm−x2·ℓ)/σ² / A22
b1 = sum(design(z)[1]*(dm-design(z)[1]*mp.log(1+z,4))/em**2 for _,z,dm,em in TR)/A22
s1 = 1/mp.sqrt(A22)
print(f"  固定 a = 1 → b = {mp.nstr(b1,9)} ± {mp.nstr(s1,6)}  ({float((b1-1)*100):.3f}% 於 1)")
print(f"  舊形式 (a=2φ⁻¹, b=1) χ² = {mp.nstr(chi2(2*inv, mp.mpf(1))[0],6)}/5")

# ---------- 全 catalogue 配對掃描 ----------
res = []
for ka, a in cat.items():
    for kb, b in cat.items():
        if mp.isnan(a) or mp.isnan(b): continue
        t, worst = chi2(a, b)
        res.append((t, abs(worst), ka, kb, a, b))
res.sort(key=lambda r: r[1])
print(f"\n--- 零參數配對掃描: {len(res)} 組合, 依 |σ|max 排序 (前 14) ---")
print(f"{'a':<18}{'b':<18}{'a_val':>10}{'b_val':>10}{'χ²/5':>10}{'|σ|max':>9}")
for t, wm, ka, kb, a, b in res[:14]:
    print(f"{ka:<18}{kb:<18}{mp.nstr(a,6):>10}{mp.nstr(b,6):>10}{mp.nstr(t,5):>10}{mp.nstr(wm,3):>9}")

# ---------- 全 ≤1.0σ 組合 ----------
ok = [r for r in res if r[1] <= 1.0]
print(f"\n--- 全部通過 |σ|max ≤ 1.0 嘅組合: {len(ok)} 個 ---")
for t, wm, ka, kb, a, b in ok:
    print(f"  E = ({ka})·ℓ + ({kb})   χ² = {mp.nstr(t,5)}  |σ|max = {mp.nstr(wm,3)}")

# ---------- 最簡形式檢查 ----------
print("\n--- 重點候選逐一 (含 φ-代數對照) ---")
key = [('1','1/2'), ('1','1/phi'), ('1','sqrt5/2'), ('<w>_FULL','<w>_HALF'),
       ('<w>_FULL','1/<v>_HALF'), ('<w>_FULL','sqrt5/2'), ('<g/2>_FULL','<w>_HALF'),
       ('2/phi','1/2'), ('2/phi','1/phi'), ('Z2<w+w>/2','<w>_FULL')]
for ka, kb in key:
    if ka in cat and kb in cat:
        t, worst = chi2(cat[ka], cat[kb])
        print(f"  a={ka:<16} b={kb:<16} a={mp.nstr(cat[ka],7):>9} b={mp.nstr(cat[kb],7):>9}"
              f"  χ²/5={mp.nstr(t,5):>8}  |σ|max={mp.nstr(worst,3):>6}")

# ---------- 由譜量砌出 δ 嘅 C ----------
print("\n--- δ 係數 C (定義: E = 1+2φ⁻¹ℓ + C(ℓ−1/2) ⇒ C = a − 2φ⁻¹) ---")
for ka in ['1','<w>_FULL','<g/2>_FULL','Z2<w+w>/2','<wg>/<g>_FULL']:
    C = cat[ka]-2*inv
    print(f"  a = {ka:<16} = {mp.nstr(cat[ka],8):>10}  ⇒ C = {mp.nstr(C,8):>11}"
          f"   (C/φ⁻³ = {mp.nstr(C/(-inv**3),6)})")
print(f"  φ⁻³ = {mp.nstr(inv**3,8)}   −(2φ⁻¹−1) = {mp.nstr(-(2*inv-1),8)}   √5−2 = {mp.nstr(mp.sqrt(5)-2,8)}")
