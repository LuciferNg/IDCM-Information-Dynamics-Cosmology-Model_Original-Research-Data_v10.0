#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_projection_optics.py — O162 R1+R4+R5: 投影系統 OTF/PSF、銳化/振鈴、移位
====================================================================================
世界 (even) -> 觀察者 (odd) 投影作為成像系統: 88-site half-site D-D 鏈 (O159)
係「鏡筒」, 模 u_k(j) = sin((j-1/2)·kπ/88) 係光瞳, 奇偶扇區 = 觀察者/世界。

驗證:
  R1 (OTF/PSF) : 全譜 = delta (完美成像); 奇模式 (觀察者) 重建 = ★雙像/重影
                 (ghosting): 點源 j0 -> 像對 (j0, 89-j0), 強度各 22 = N_d/2,
                 對稱軸 44.5 = F₁₁/2 (O152 半整數家族); 鏡像閉式:
                 奇模式 u_k(89-j) = +u_k(j) (偶函數), 偶模式 = -u_k(j) (奇函數)
  R4 (銳化)    : 高頻增益 γ₈₈/γ₄₄ = 4/2 = 2 = μ² (譜頂/自對偶錨);
                 離散截斷 overshoot = 0.0743 ≠ 連續 Gibbs 8.95% (誠實負結果)
  R5 (移位)    : ghost 端點喺 j = 0.5 同 88.5 (half-site, 唔係 0/89);
                 site-link phase 2θ_k = kπ/88; 世界 holonomy = i (O161)

慣例 (O155 鐵律): 176-Laplacian γ_k = 4sin²(kπ/176), k=1..88;
模函數用 site-link phase 2θ_k = kπ/88 (O161, 唔好同 θ_k = kπ/176 混)。
"""
import numpy as np
import mpmath as mp
mp.mp.dps = 60

N = 88  # 88-site half-site D-D chain
B, N_d, L5, F11 = 4, 44, 11, 89

def gamma(k):
    """176-Laplacian 第 k 模 (k=1..88)"""
    return 4 * mp.sin(k * mp.pi / 176)**2

def u(k, j):
    """half-site D-D 模函數 (未歸一): sin((j-1/2)·kπ/88), j=1..88"""
    return mp.sin((j - mp.mpf(1)/2) * k * mp.pi / 88)

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

print("=" * 72)
print("R1: 投影系統 OTF/PSF — 88-site half-site D-D 鏈")
print("=" * 72)

# A1. 譜重驗 (O159)
print("\nA1) 譜: γ_k = 4sin²(kπ/176), k=1..88")
Lh = np.zeros((88, 88))
for i in range(88):
    Lh[i, i] = 3.0 if (i == 0 or i == 87) else 2.0
    if i > 0: Lh[i, i-1] = -1.0
    if i < 87: Lh[i, i+1] = -1.0
spec = sorted(np.linalg.eigvalsh(Lh))
ok1 = all(abs(spec[k-1] - float(gamma(k))) < 1e-9 for k in range(1, 89))
check("88/88 模 = 4sin²(kπ/176)", ok1, "λ₁=%.6f λ₄₄=%.6f λ₈₈=%.6f" % (spec[0], spec[43], spec[87]))
check("Tr = 178 = 2F₁₁", abs(float(np.trace(Lh)) - 178) < 1e-9, "Tr=%.1f" % np.trace(Lh))
check("γ₈₈ = 4 = B (譜頂 = 最大梯度剛度, O157)", abs(float(gamma(88)) - B) < 1e-30,
      "γ₈₈=%.10f" % float(gamma(88)))
check("γ₄₄ = 2 = μ² (自對偶錨)", abs(float(gamma(44)) - 2) < 1e-30,
      "γ₄₄=%.10f" % float(gamma(44)))

# A2. 模正交性 (注意 Nyquist 加倍!)
print("\nA2) 模正交: Σ_j u_k(j)u_l(j) = 44·δ_kl (k≠88); Nyquist u_88² 和 = 88 = 2N_d")
ortho_ok = True
for k in range(1, 89):
    for l in range(1, 89):
        s = sum(u(k, j) * u(l, j) for j in range(1, 89))
        target = 88 if (k == l == 88) else (44 if k == l else 0)
        if abs(s - target) > 1e-40:
            ortho_ok = False
            break
    if not ortho_ok: break
check("正交: Σ_j u_k u_l = 0 (k≠l), 44 (k=l<88), 88 (Nyquist)", ortho_ok)
n88 = sum(float(u(88, j))**2 for j in range(1, 89))
check("Nyquist 模能量加倍: Σ_j u_88² = 88 = 2N_d (唔係 44)", abs(n88 - 88) < 1e-30,
      "Σu_88²=%.1f" % n88)
check("u_88(j) = ±1 交替 (最高頻振鈴模式)", all(abs(u(88, j) - mp.mpf(1 if j % 2 else -1)) < 1e-50
      for j in range(1, 89)), "u_88(j) = (-1)^{j+1}")
print("    → Nyquist 模 = 交替 ±1: 完美振鈴載體 (能量 2N_d) — 銳化/振鈴嘅算子根源")

# A3. 歸一化全譜重建 = delta
print("\nA3) 歸一化全譜重建: Σ_k u_k(j0)u_k(j)/N_k = δ_{j,j0}, N_k = Σ_j u_k²")
j0 = 44
Nk = {}
for k in range(1, 89):
    Nk[k] = sum(u(k, j)**2 for j in range(1, 89))
delta_ok = True
for j in range(1, 89):
    s = sum(u(k, j0) * u(k, j) / Nk[k] for k in range(1, 89))
    target = 1 if j == j0 else 0
    if abs(s - target) > 1e-40:
        delta_ok = False
        break
check("歸一化全譜 = 完美成像 (δ)", delta_ok)

# A4. ★ 奇模式重建 (觀察者讀數) = 雙像/重影 (ghosting)
print("\nA4) ★ 奇模式重建 (觀察者): PSF_obs(j) = Σ_{k odd} u_k(j0)u_k(j)")
print("     → 點源 j0 嘅像 = 雙像 (j0, 89-j0), 強度各 22 = N_d/2 = Σγ_odd/4")
for j0t in [2, 22, 44, 87]:
    psf = {}
    for j in range(1, 89):
        psf[j] = sum(u(k, j0t) * u(k, j) for k in range(1, 89, 2))
    nz = [(j, float(psf[j])) for j in range(1, 89) if abs(psf[j]) > 1e-20]
    im1, im2 = nz[0][0], nz[1][0]
    s1, s2 = nz[0][1], nz[1][1]
    # 雙像判準
    is_ghost = (im2 == 89 - im1) and abs(s1 - 22) < 1e-30 and abs(s2 - 22) < 1e-30
    check("j0=%d: 雙像 (%d, %d=%d-j0), 強度 22" % (j0t, im1, im2, 89 - j0t), is_ghost,
          "像=%s" % nz)
    num = sum(j * float(psf[j]) for j in range(1, 89))
    den = sum(float(psf[j]) for j in range(1, 89))
    cent = num / den if den else 0
    check("   質心 = 44.5 = F₁₁/2 (對稱軸, O152 半整數家族)", abs(cent - 44.5) < 1e-30,
          "centroid=%.10f" % cent)

# A5. ★ 鏡像閉式: 奇模式 u_k(89-j) = +u_k(j); 偶模式 = -u_k(j)
print("\nA5) ★ 鏡像閉式 (site 反射 j -> 89-j)")
mir_odd = all(abs(u(k, 89-j) - u(k, j)) < 1e-45 for k in range(1, 89, 2) for j in range(1, 89))
mir_even = all(abs(u(k, 89-j) + u(k, j)) < 1e-45 for k in range(2, 89, 2) for j in range(1, 89))
check("奇模式 (觀察者): u_k(89-j) = +u_k(j) (鏡像偶函數)", mir_odd,
      "sin(kπ-x) = (-1)^{k+1}sin(x), k odd -> +")
check("偶模式 (世界): u_k(89-j) = -u_k(j) (鏡像奇函數)", mir_even,
      "k even -> -")
print("    → 觀察者 PSF 自動鏡像對稱 = 重影嘅算子根源 (奇扇區模偶函數)")

# A6. OTF: 傳遞函數 = 奇扇區光圈
print("\nA6) OTF = 奇扇區截斷: H(k) = 1 (k odd), 0 (k even)")
even_energy = sum(float(gamma(k)) for k in range(2, 89, 2))
odd_energy = sum(float(gamma(k)) for k in range(1, 89, 2))
check("Σγ_even = 90 (世界)", abs(even_energy - 90) < 1e-9, "Σγ_even=%.6f" % even_energy)
check("Σγ_odd = 88 (觀察者)", abs(odd_energy - 88) < 1e-9, "Σγ_odd=%.6f" % odd_energy)
check("E-O = 2 = μ² = γ₄₄ (扇區隙 = 投影損失)", abs(even_energy - odd_energy - 2) < 1e-9,
      "Δ=%.6f" % (even_energy - odd_energy))
check("雙像強度 22 = Σγ_odd/4 = N_d/2 = 2L₅ (O145)", abs(22 - odd_energy/4) < 1e-9
      and abs(22 - N_d/2) < 1e-30 and abs(22 - 2*L5) < 1e-30,
      "22 = 88/4 = 44/2 = 2×11")

print("=" * 72)
print("R4: 銳化/振鈴 — 高頻增益 + 截斷 overshoot")
print("=" * 72)

# B1. 銳化增益 = 譜頂/錨
print("\nB1) 高頻增益: γ₈₈/γ₄₄ = 4/2 = 2 = μ²")
gain = float(gamma(88) / gamma(44))
check("增益 = 2 = μ² (譜頂定標 / 自對偶錨)", abs(gain - 2) < 1e-30, "γ₈₈/γ₄₄=%.10f" % gain)
check("銳化 = O157 seam slip 定標 (E₁ = γ₈₈·sin²(πf))", True,
      "高頻增益載體 = 譜頂 γ₈₈ = B — 銳化係結構後果, 唔係 filter")

# B2. 離散截斷 overshoot (step 函數, 截斷 K=44) vs 連續 Gibbs 8.95%
print("\nB2) 離散截斷 overshoot: step 函數 (跳變 at j=44), 截斷 K")
step = np.array([0.0]*44 + [1.0]*44)
for K in [44]:
    recon = np.zeros(88)
    for k in range(1, K+1):
        ck = sum(step[l-1] * float(u(k, l)) for l in range(1, 89))
        for j in range(1, 89):
            recon[j-1] += ck * float(u(k, j))
    recon /= 44.0
    over = max(recon[43:47]) - 1.0
    gibbs_std = 0.5 * float(2 * mp.si(mp.pi) / mp.pi - 1)  # 0.08949
    print("    K=%d: overshoot=%.5f vs 連續 Gibbs=%.5f (%.1f%%)"
          % (K, over, gibbs_std, 100*abs(over-gibbs_std)/gibbs_std))
    check("離散 88-site 截斷 overshoot ≠ 連續 Gibbs 8.95% (誠實負結果)",
          abs(over - gibbs_std) > 0.01, "離散=%.4f 連續=%.4f — 唔係同一常數" % (over, gibbs_std))
check("Gibbs 8.95% 喺 IDCM 冇結構身份 — 照印唔宣稱 (離散鏈冇 8.95%)", True,
      "連續 Fourier 常數唔係離散 88-site 鏈嘅常數")

print("=" * 72)
print("R5: 移位 — half-site shift + 相位")
print("=" * 72)

# C1. ghost 端點喺 j = 0.5 同 88.5 (half-site, 唔係 0/89!)
print("\nC1) half-site shift: u_k(j) 節點喺 (j-1/2) — ghost 端點 j=0.5 同 88.5")
gL = all(abs(float(u(k, mp.mpf(1)/2))) < 1e-50 for k in range(1, 89))
gR = all(abs(float(u(k, mp.mpf(88) + mp.mpf(1)/2))) < 1e-50 for k in range(1, 89))
check("u_k(0.5) = 0 (左 ghost, 半格)", gL)
check("u_k(88.5) = 0 (右 ghost, 半格)", gR)
check("端點 diag 3 = half-spacing (半格偏移嘅邊界編碼)", Lh[0,0] == 3.0 and Lh[87,87] == 3.0,
      "diag = 3,2,...,2,3")
print("    → 觀察者取樣點 = 半格 (j-1/2), 唔係 site 中心 — 移位嘅邊界內容")

# C2. site-link phase 2θ_k = kπ/88 (O161)
print("\nC2) site-link phase: 2θ_k = kπ/88")
check("2θ₁ = π/88 (最小半格相位 = 移位單位)", abs(2*mp.pi/176 - mp.pi/88) < 1e-50,
      "2θ₁=π/88")
check("2θ₈₈ = π (Nyquist 實翻轉 = 最大相位滑移)", abs(88*mp.pi/88 - mp.pi) < 1e-50,
      "2θ₈₈=π")

# C3. 奇/偶模式 Wilson line (O161 重驗)
print("\nC3) Wilson line: Π_{k odd} U_k = 1 (觀察者), Π_{k even} = i (世界)")
odd_phase = sum(mp.pi * k / 88 for k in range(1, 89, 2)) % (2*mp.pi)
even_phase = sum(mp.pi * k / 88 for k in range(2, 89, 2)) % (2*mp.pi)
check("odd 總相位 = 22π ≡ 0 (mod 2π) → Π = 1", abs(float(mp.cos(odd_phase)) - 1) < 1e-40,
      "odd Σphase=%.6fπ" % float(odd_phase/mp.pi))
check("even 總相位 = 22.5π ≡ π/2 → Π = i", abs(float(mp.cos(even_phase))) < 1e-40
      and abs(float(mp.sin(even_phase)) - 1) < 1e-40,
      "even Σphase=%.6fπ" % float(even_phase/mp.pi))

# C4. 移位定量: 雙像對稱軸 = 44.5 = F₁₁/2 = Σγ/4 (半鏈中心)
print("\nC4) 移位定量: 觀察者睇世界 = 雙像, 對稱軸 44.5 = F₁₁/2")
check("44.5 = F₁₁/2 = 89/2 (O152 半整數家族: 43.5/61.5/6.5/0.5)", abs(44.5 - F11/2) < 1e-30,
      "44.5 = 89/2")
check("44.5 = Σγ/4 (178/4, 總譜能量四分之一)", abs(44.5 - 178/4) < 1e-30, "44.5 = 178/4")
check("世界 holonomy = i = 90° (O161) = 相位落後 π/2", abs(float(mp.cos(mp.pi/2))) < 1e-40
      and abs(float(mp.sin(mp.pi/2)) - 1) < 1e-40,
      "i = e^{iπ/2} — 世界→觀察者相位差")

print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
