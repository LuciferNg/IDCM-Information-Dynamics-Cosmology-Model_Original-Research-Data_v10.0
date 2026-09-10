#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/01 — 缺口形狀提取 + δ 譜候選測試

問題: IDCM D_A(ℓ) 六 tracer 殘餘 (O167 scripts/17):
  BGS −2.16σ / LRG1 −3.05σ / 中 z <1σ / Lyα +1.64σ
δ(ℓ) = C(ℓ−0.5)(1−4^{−ℓ}) 係經驗式, C = −0.1697 冇身份。

本 script:
  C1: 缺口形狀提取 (六點, 單位 rd)
  C2: 缺口 = 投影因子 (1−π/44) 未補償部分? (IDCM 用 R_world, DESI 用 c/H₀^CMB)
  C3: 譜候選測試 — δ_spectral(ℓ) = ⟨γ·sec⟩ 譜平均形狀
  C4: 端點候選 — (1−4^{−ℓ}) 形狀 vs 缺口形狀
  C5: 誠實裁決 — δ 由譜結構出? 定要降級?
"""
import mpmath as mp
mp.mp.dps = 25

R = mp.mpf('4129.94')
C_delta = mp.mpf('-0.1697')
phi_inv = (mp.sqrt(5)-1)/2
c = mp.mpf('299792.458')
Om = mp.mpf('0.315'); OL = mp.mpf('1') - Om
H0_cmb = mp.mpf('67.407')
rd = mp.mpf('147.088')
pi44 = mp.pi/44

TRACERS = [
    ("LRG1", mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167')),
    ("LRG2", mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177')),
    ("LRG3", mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152')),
    ("ELG2", mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318')),
    ("QSO",  mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760')),
    ("Lya",  mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531')),
]

def ell_of(z): return mp.log(1+z)/mp.log(4)
def delta(ell, C=C_delta): return C*(ell - mp.mpf('0.5'))*(1 - mp.mpf('4')**(-ell))
def DA0(ell):  return R*(1 - mp.mpf('4')**(-ell))*(1 + 2*phi_inv*ell)
def DA_d(ell): return DA0(ell) + R*(1 - mp.mpf('4')**(-ell))*delta(ell)

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

# C1: 缺口 (δ 要解釋嘅) = DESI − IDCM(δ=0), 同埋 δ 已解釋部分
print("=== C1: 缺口分解 ===")
print(f"{'tracer':<7}{'ell':>7}{'gap(δ=0)':>10}{'δ已補':>8}{'剩缺口':>8}{'剩σ':>7}")
gaps = []
for name, z, dm, e in TRACERS:
    ell = ell_of(z)
    obs = dm*rd
    g0 = (obs - DA0(ell))/rd          # 缺口 (δ=0 時)
    gd = (DA_d(ell) - DA0(ell))/rd    # δ 已補
    gleft = (obs - DA_d(ell))/rd      # 剩缺口
    sleft = gleft/e
    gaps.append((ell, g0, gleft, sleft))
    print(f"{name:<7}{float(ell):>7.3f}{float(g0):>10.3f}{float(gd):>8.3f}{float(gleft):>8.3f}{float(sleft):>7.2f}")

# C2: 投影假設 — IDCM 全面細 ΛCDM(CMB) 因為用 R_world 標度
#     如果 D_A 應該用 c/H₀^CMB = R/(1−π/44) 標度, 缺口 = π/44 部分
print("\n=== C2: 投影標度修正 D_A^proj = D_A/(1−π/44) ===")
print(f"{'tracer':<7}{'IDCM0':>8}{'proj':>8}{'DESI':>8}{'proj σ':>8}")
for name, z, dm, e in TRACERS:
    ell = ell_of(z)
    d0 = DA0(ell)/rd
    dp = d0/(mp.mpf(1) - pi44)
    sp = (dp - dm)/e
    print(f"{name:<7}{float(d0):>8.3f}{float(dp):>8.3f}{float(dm):>8.3f}{float(sp):>8.2f}")

# C3: 譜候選 — δ_spectral(ell) 形狀: ⟨sec⟩ 加權窗
print("\n=== C3: 譜平均候選 (⟨γ^p·sec^q⟩ over n=1..n_max) ===")
# 群延遲權重嘅 ℓ 依賴: n_max(ℓ) = 22·ℓ (線性) — 試幾種
def spec_avg(p, q, n_max):
    s_num = mp.mpf(0); s_den = mp.mpf(0)
    for n in range(1, n_max+1):
        gam = 4*mp.sin(n*mp.pi/88)**2
        sec = 1/mp.cos(n*mp.pi/88)
        s_num += gam**p * sec**q
        s_den += gam**p
    return s_num/s_den if s_den != 0 else mp.mpf(0)

# 候選 δ: C_delay_form = A·(⟨sec⟩_w − 1), A 由譜定
# 用 n_max(ℓ) = 44·ℓ/2 = 22ℓ (ℓ=1 → n=22 深極限)
print(f"{'ell':>7}{'nmax':>6}{'⟨γsec⟩/⟨γ⟩':>12}{'⟨sec⟩':>9}")
for ell, g0, gl, sl in gaps:
    nm = max(1, int(round(float(22*ell))))
    a1 = spec_avg(1, 1, nm)
    a2 = spec_avg(0, 1, nm)
    print(f"{float(ell):>7.3f}{nm:>6}{float(a1):>12.5f}{float(a2):>9.5f}")

# C4: 缺口形狀 vs (1−4^{−ℓ}) 形狀 — 正規化比較
print("\n=== C4: 缺口形狀 (正規化到 Lyα=1) ===")
g_norm = [float(gl)/abs(float(gaps[-1][1])) for (e, g0, gl, sl) in gaps]
shape_14 = [float(1 - mp.mpf('4')**(-e)) for (e, g0, gl, sl) in gaps]
shape_g = [float(g0) for (e, g0, gl, sl) in gaps]
# 正規化 shape_g 到最後點
g0_last = abs(shape_g[-1])
shape_g_n = [g/g0_last for g in shape_g]
print(f"{'ell':>7}{'缺口(δ=0)norm':>15}{'(1−4^{−ℓ})norm':>15}")
for i, (e, g0, gl, sl) in enumerate(gaps):
    print(f"{float(e):>7.3f}{shape_g_n[i]:>15.4f}{shape_14[i]/shape_14[-1]:>15.4f}")

# C5: 誠實裁決
print()
print("裁決:")
print("  C1: δ 只補缺口 0.85/4.6 = 18% (LRG1) — 缺口大部分係投影+φ補償")
print("  C2: 投影標度 (1−π/44)⁻¹ 喺低 z 改善但 Lyα +7.6% 過頭 — 唔係純標度")
print("  C3/C4: 譜平均形狀同缺口形狀比較 → 見上表")
print()
print("RESULT: 見 C1-C4")
