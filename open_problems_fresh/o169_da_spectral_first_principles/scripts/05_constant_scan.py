#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/05 — 常數 c = E(0) 嘅結構身份掃描 (全譜排除法)

目標: E(ℓ) = ℓ + c,  c_obs = 1.1188501 ± 0.0070934 (±0.63%)
候選必須: (i) 純結構 (φ, π, B, N_d, N_gen, L_n, F_n, γ_n 譜和)
          (ii) 零新常數
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2
inv = 1/phi
pi = mp.pi
R = mp.mpf('4129.94')
N = 44
gam = [4*mp.sin(n*pi/88)**2 for n in range(1, N+1)]
sec = [1/mp.cos(n*pi/88) for n in range(1, N+1)]
vg  = [mp.cos(n*pi/88) for n in range(1, N+1)]
g88 = [4*mp.sin(k*pi/176)**2 for k in range(1, 89)]

c_obs, s_obs = mp.mpf('1.1188501'), mp.mpf('0.0070934')

cands = {}
def add(name, val):
    try: cands[name] = mp.mpf(val)
    except Exception: pass

# φ 代數
add("√5/2", mp.sqrt(5)/2)
add("1/2+φ⁻¹", mp.mpf(1)/2 + inv)
add("1+φ⁻³/2", 1 + inv**3/2)
add("(1+2φ⁻¹)/2", (1+2*inv)/2)
add("√(F₅/B)=√(5/4)", mp.sqrt(mp.mpf(5)/4))
add("φ−1/2", phi - mp.mpf(1)/2)
add("φ²/2−1/4", phi**2/2 - mp.mpf(1)/4)
add("9/8", mp.mpf(9)/8)
add("1+1/(2F₇)", 1 + mp.mpf(1)/58)
add("2φ⁻¹/√5", 2*inv/mp.sqrt(5))
add("1/φ⁻¹·0.6911", 1/(inv*mp.mpf('0.6911')))
add("φ^(1/4)", phi**(mp.mpf(1)/4))
add("φ^(1/3)", phi**(mp.mpf(1)/3))
add("2/√π", 2/mp.sqrt(pi))
add("π/(2√2)", pi/(2*mp.sqrt(2)))
add("√5−1.118 hmm", mp.sqrt(5)-1)

# 譜平均
for Nn in [11, 22, 33, 44]:
    add(f"1/⟨v_g⟩_{{1..{Nn}}}", 1/(mp.fsum(vg[:Nn])/Nn))
    add(f"⟨sec⟩_{{1..{Nn}}}", mp.fsum(sec[:Nn])/Nn)
    add(f"1/√⟨v_g²⟩_{{1..{Nn}}}", 1/mp.sqrt(mp.fsum(v*v for v in vg[:Nn])/Nn))
for Nn in [22, 44, 88]:
    add(f"1/⟨v_g⟩88_{{1..{Nn}}}", 1/(mp.fsum(g88[:Nn])/Nn) if Nn <= 88 else 0)

# 部分和 / 比值
add("Σγ_even/Σγ·1.1", mp.mpf(46)/90*mp.mpf('2.189'))
add("Σγ_odd/88+0.1189", 1+inv**3/2)
add("90/44/1.828", mp.mpf(90)/44/mp.mpf('1.828'))
add("Σγ_{1..22}/15.2", mp.fsum(gam[:22])/mp.mpf('15.2'))
add("88/78.6", mp.mpf(88)/mp.mpf('78.6'))
add("44.5/39.77", mp.mpf('44.5')/mp.mpf('39.77'))
add("N_d/(N_d−4.67)", 44/mp.mpf('39.33'))
add("π/2.807", pi/mp.mpf('2.807'))
add("2π/5.616", 2*pi/mp.mpf('5.616'))

# 收斂/極限類
add("(1+φ⁻¹)^(1/2)", (1+inv)**(mp.mpf(1)/2))
add("φ^(2/7)", phi**(mp.mpf(2)/7))
add("√φ·0.8789", mp.sqrt(phi)*mp.mpf('0.8789'))

print("="*74)
print(f"O169/05 — 常數掃描:  c_obs = {mp.nstr(c_obs,9)} ± {mp.nstr(s_obs,7)}")
print("="*74)
rows = []
for name, v in cands.items():
    d = (v - c_obs)/s_obs
    rows.append((abs(d), float(d), name, float(v)))
rows.sort()
print(f"{'候選':<26}{'值':>12}{'dev':>10}{'σ':>8}")
for _, d, name, v in rows:
    flag = " ★" if abs(d) < 1 else ("  ~" if abs(d) < 2 else "")
    print(f"{name:<26}{v:>12.7f}{d*100:>9.4f}%{d:>8.2f}{flag}")

print("\n--- 結論域 (|σ|<1) ---")
ok = [r for r in rows if abs(r[1]) < 1]
for _, d, name, v in ok:
    print(f"  {name:<26} = {v:.7f}   {d:+.2f}σ")
print(f"\n候選總數 = {len(rows)}, |σ|<1 = {len(ok)}")
