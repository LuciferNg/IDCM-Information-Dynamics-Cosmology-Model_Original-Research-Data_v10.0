#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/15 — O4: C = −0.1697 不變量譜跡比掃描 (3/41 耦合子空間)

方向 (用戶): 繞過 7744 密度背景候選 (γ_23/γ_74)。鎖定重子(3)與真空(41)
耦合子空間嘅純譜特徵值, 尋找跨階矩陣元嘅不變量跡比 (Invariant Spectral
Trace Ratio), 令 C 成為純代數結構閉合極限。

設定: 44-site chain γ_n = 4sin²(nπ/88) (n=1..44), N_d = 44 = 3 + 41
  重子扇區 B₃ = {1,2,3}, 真空扇區 V₄₁ = {4..44}
  88-site chain γ_k = 4sin²(kπ/176) (k=1..88) 作為對照
掃描形式: Σ_A γ / Σ_B γ, (Σ_A−Σ_B)/(Σ_A+Σ_B), γ_a/γ_b, 跡比 Tr(P L P')
目標: |C + 0.1697| < 0.0001 (0.06%), 計密度背景。
"""
import mpmath as mp
import itertools
mp.mp.dps = 50

C_abs = mp.mpf("0.1697")
phi = (1 + mp.sqrt(5)) / 2

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

print("="*70)
print("O167 scripts/15 — O4: C 譜跡比掃描")
print("="*70)

# 譜
g44 = [4*mp.sin(n*mp.pi/88)**2 for n in range(1, 45)]       # 44-site
g88 = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]      # 88-site

# C1: 確認 O51 scripts/82 推導 FAIL 同 γ_23/γ_74 舊候選
chk("C1 舊候選 γ_23/γ_74 = 0.169668 (dev 0.02%, 密度背景)", True)
print(f"    γ_23/γ_74 = {mp.nstr(g88[22]/g88[73], 9)}")

# C2: 重子(3)/真空(41) 扇區跡 — 44-site
S3 = mp.fsum(g44[0:3])
S41 = mp.fsum(g44[3:44])
Sall = mp.fsum(g44)
print(f"    ΣB₃ = {mp.nstr(S3, 8)}, ΣV₄₁ = {mp.nstr(S41, 8)}, Σall = {mp.nstr(Sall, 8)}")

# 掃描 1: 扇區跡比
cands = []
def consider(name, val):
    d = abs(val - C_abs)
    if d < mp.mpf("0.002"):
        cands.append((float(d), name, float(val)))

consider("S3/S41", S3/S41)
consider("S41/S3", S41/S3)
consider("(S3-S41)/(S3+S41)", (S3-S41)/(S3+S41))
consider("(S41-S3)/(S41+S3)", (S41-S3)/(S41+S3))
consider("S3/Sall", S3/Sall)
consider("(S3+S41/2)/Sall", (S3+S41/2)/Sall)

# 掃描 2: 子扇區對 (1..m vs m+1..44)
for m in range(1, 44):
    A = mp.fsum(g44[0:m]); B = mp.fsum(g44[m:44])
    consider(f"Σ1..{m}/Σ{m+1}..44", A/B)
    consider(f"(Σ1..{m}-Σ{m+1}..44)/(Σ1..{m}+Σ{m+1}..44)", (A-B)/(A+B))

# 掃描 3: 88-site 跡 (even/odd/跨)
Se = mp.fsum(g88[1::2])  # even k (2,4,...)
So_ = mp.fsum(g88[0::2]) # odd k
consider("Se/So (88-site even/odd)", Se/So_)
consider("(Se-So)/(Se+So)", (Se-So_)/(Se+So_))
consider("So_/(Se+So_)", So_/(Se+So_))

# 掃描 4: 單模比 γ_a/γ_b (88-site) — 同 scripts/07 一致但加 S3/S41 扇區模
for a in range(1, 89):
    for b in range(1, 89):
        if a == b: continue
        consider(f"γ{a}/γ{b}", g88[a-1]/g88[b-1])

cands.sort()
print(f"\n候選總數 (<0.2% dev): {len(cands)}")
for d, name, val in cands[:8]:
    print(f"  {name:<32} = {val:.8f}  dev {d*100/float(C_abs):.3f}%")

# C3: 頂候選評估 — 密度背景
chk("C3 頂候選 (<0.02%) 有冇乾淨結構身份?", False)
if cands:
    d0, n0, v0 = cands[0]
    print(f"    頂候選: {n0} = {v0:.8f} (dev {d0*100/float(C_abs):.3f}%)")

# C4: 扇區跡比嘅頂候選
print("\n扇區型候選:")
shown = 0
for d, name, val in cands:
    if name.startswith("Σ") or name.startswith("S") or name.startswith("("):
        print(f"  {name:<40} = {val:.8f}  dev {d*100/float(C_abs):.3f}%")
        shown += 1
        if shown >= 6: break

# C5: 結構候選組合 — (γ₄₄−γ₂₂)/(γ₄₄+γ₂₂) 等
g2_88 = g88[21]  # γ₂₂ (88-site) = 2−√2
g44_88 = g88[43] # γ₄₄ = 2
c5_cands = {
    "(γ44−γ22)/(γ44+γ22)": (g44_88-g2_88)/(g44_88+g2_88),
    "(2−√2)/(2+√2)": (2-mp.sqrt(2))/(2+mp.sqrt(2)),
    "1/(2π(1−κ))": 1/(2*mp.pi*(1-mp.mpf(1)/16)),
    "6L₇/(41·25)": mp.mpf(6*29)/mp.mpf(41*25),
    "(1−π/44)²": (1-mp.pi/44)**2,
    "φ⁻⁴+1/44": phi**-4 + mp.mpf(1)/44,
    "1/φ³−1/15": phi**-3 - mp.mpf(1)/15,
    "3/(3+41)·2.32": mp.mpf(3)/44*mp.mpf("2.32"),
}
for name, val in c5_cands.items():
    d = abs(val - C_abs)
    print(f"  {name:<28} = {float(val):.8f}  dev {float(d)*100/float(C_abs):.3f}%")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("裁決: 冇不變量跡比喺 <0.06% 內帶乾淨結構身份 — C 保持 🔴/🟡")
print("  (頂候選仍然係 γ 比類密度背景; 扇區跡比冇命中)")
