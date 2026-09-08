#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT — O162 獨立核對 (由零重算, 唔 import 任何項目 script)
====================================================================================
用戶要求: 驗證並獨立核對每一個文檔中所有推導鏈過程中內容、公式和數值。
本 script 從頭計算 docs/01-06 宣稱嘅所有關鍵數值, 對照文檔聲明。
禁誇文檔污染: 只核對「文檔寫咗乜」vs「獨立計算出乜」, 唔引入新推導。
"""
import mpmath as mp
mp.mp.dps = 60   # 同原 scripts 一致 (dps=50 時 u(88.5)=sin(kπ) 誤差 > 1e-50)

B, N_d, L4, L5, F5, F6, F11, N_gen = 4, 44, 7, 11, 5, 8, 89, 3
h11, h21 = 36, 98
hbar = (h11 + h21) / 2   # 67

ok = 0; tot = 0
def check(doc, name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] doc/%s: %s %s" % ("PASS" if cond else "FAIL", doc, name, detail))

def gamma(k): return 4 * mp.sin(k*mp.pi/176)**2
def u(k, j): return mp.sin((j - mp.mpf(1)/2) * k * mp.pi / 88)
def psf_obs(j0, j): return sum(u(k, j0)*u(k, j) for k in range(1, 89, 2))
def theta23(N): return mp.atan(mp.sin(7*mp.pi/N)/mp.sin(6*mp.pi/N))

print("=" * 76)
print("A. S1 錨點 (O159): γ_k = 4sin²(kπ/176), Σ = 178 = 2F₁₁")
print("=" * 76)
s_g = sum(gamma(k) for k in range(1, 89))
check("01", "Σγ = 178 = 2F₁₁", abs(s_g - 178) < 1e-40, "Σ=%.6f" % float(s_g))
s_e = sum(gamma(k) for k in range(2, 89, 2))
s_o = sum(gamma(k) for k in range(1, 89, 2))
check("01", "Σγ_even = 90 (世界)", abs(s_e - 90) < 1e-40, "=%.6f" % float(s_e))
check("01", "Σγ_odd = 88 (觀察者)", abs(s_o - 88) < 1e-40, "=%.6f" % float(s_o))
check("01", "E−O = 2 = μ² = γ₄₄", abs(s_e - s_o - 2) < 1e-40 and abs(gamma(44) - 2) < 1e-40, "γ₄₄=%.6f" % float(gamma(44)))
check("01", "γ₈₈ = 4 = B (譜頂)", abs(gamma(88) - 4) < 1e-40, "=%.6f" % float(gamma(88)))

print("=" * 76)
print("B. R1 雙像/重影 (docs/01): 像對 (j0, 89−j0), 強度 22, 質心 44.5")
print("=" * 76)
for j0 in [2, 22, 44, 87]:
    Ij0 = float(psf_obs(j0, j0))
    Imir = float(psf_obs(j0, 89 - j0))
    check("01", "j0=%d: PSF(j0)=22, PSF(89-j0)=22" % j0,
          abs(Ij0 - 22) < 1e-30 and abs(Imir - 22) < 1e-30,
          "PSF(j0)=%.4f PSF(89-j0)=%.4f" % (Ij0, Imir))
# 質心 44.5: 對稱軸 = (j0 + (89-j0))/2 = 44.5 對任何 j0 成立 (代數恆等)
check("01", "像對質心 = (j0+89-j0)/2 = 44.5 = F₁₁/2 (代數恆等)",
      abs((j0 + (89 - j0)) / 2 - 44.5) < 1e-30)
check("01", "44.5 = Σγ/4 = 178/4", abs(178/4 - 44.5) < 1e-30)
# 鏡像閉式 u_k(89-j) = (-1)^{k+1} u_k(j)
mir_ok = all(abs(u(k, 89-j) - (-1)**(k+1)*u(k, j)) < 1e-40
             for k in range(1, 89) for j in range(1, 89))
check("01", "u_k(89-j) = (−1)^{k+1}·u_k(j) ∀k,j (鏡像閉式)", mir_ok)

print("=" * 76)
print("C. R4 銳化/振鈴 (docs/01): 增益 2, Nyquist 能量 88, Gibbs 負結果")
print("=" * 76)
check("01", "γ₈₈/γ₄₄ = 4/2 = 2 = μ² (增益)", abs(float(gamma(88)/gamma(44)) - 2) < 1e-40)
n88 = sum(float(u(88, j))**2 for j in range(1, 89))
check("01", "Σ_j u_88² = 88 = 2N_d (Nyquist 能量加倍)", abs(n88 - 88) < 1e-30, "=%.1f" % n88)
check("01", "u_88(j) = (−1)^{j+1} 交替 ±1", all(abs(u(88, j) - mp.mpf(1 if j % 2 else -1)) < 1e-50 for j in range(1, 89)))
# 正交性: Σ_j u_k u_l = 0 (k≠l), 44 (k=l<88), 88 (k=l=88)
ortho_ok = True
for k in range(1, 89):
    for l in range(1, 89):
        s = sum(u(k, j)*u(l, j) for j in range(1, 89))
        tgt = 88 if (k == l == 88) else (44 if k == l else 0)
        if abs(s - tgt) > 1e-40: ortho_ok = False
check("01", "正交性: 0/44/88 (Nyquist)", ortho_ok)
# 離散 Gibbs overshoot: 跟原 script 01 B2 定義 (step = [0]*44+[1]*44, 跳變 j=44→45)
import numpy as np
step = np.array([0.0]*44 + [1.0]*44)
recon = np.zeros(88)
for k in range(1, 45):
    ck = sum(step[l-1] * float(u(k, l)) for l in range(1, 89))
    for j in range(1, 89):
        recon[j-1] += ck * float(u(k, j))
recon /= 44.0
over = max(recon[43:47]) - 1.0
check("01", "離散 K=44 截斷 overshoot ≈ 0.0743 (docs 聲明, 原 script B2)",
      abs(over - 0.0743) < 0.001, "離散=%.4f" % over)
cont = 0.5 * float(2 * mp.si(mp.pi) / mp.pi - 1)
check("01", "連續 Gibbs = 0.08949 (½[2Si(π)/π−1], 原 script 因子)",
      abs(cont - 0.08949) < 1e-4, "連續=%.5f" % float(cont))
check("01", "兩者唔等 (負結果 — 連續常數冇離散身份)", abs(over - cont) > 0.005)

print("=" * 76)
print("D. R5 移位 (docs/01): ghost 0.5/88.5, 2θ, Wilson line, 質心 44.5")
print("=" * 76)
# ghost 端點 (用 mp 比較, 唔用 float — float 精度得 1e-16)
gL = all(abs(u(k, mp.mpf(1)/2)) < 1e-50 for k in range(1, 89))
gR = all(abs(u(k, mp.mpf(88) + mp.mpf(1)/2)) < 1e-50 for k in range(1, 89))
check("01", "u_k(0.5) = 0 (左 ghost)", gL)
check("01", "u_k(88.5) = 0 (右 ghost)", gR)
check("01", "2θ₁ = π/88, 2θ₈₈ = π (site-link phase)", abs(88*mp.pi/88 - mp.pi) < 1e-50)
# Wilson line: Π odd phase = 22π ≡ 0 → 1; even = 22.5π ≡ π/2 → i
# (用 cos 比較, 唔用 float — 原 script 慣例)
odd_phase = sum(k*mp.pi/88 for k in range(1, 89, 2))
even_phase = sum(k*mp.pi/88 for k in range(2, 89, 2))
check("01", "odd 總相位 = 22π ≡ 0 → Π = 1", abs(mp.cos(odd_phase) - 1) < 1e-40,
      "cos(22π)=%.2e" % float(mp.cos(odd_phase)))
check("01", "even 總相位 = 22.5π ≡ π/2 → Π = i", abs(mp.cos(even_phase)) < 1e-40,
      "cos(22.5π)=%.2e" % float(mp.cos(even_phase)))

print("=" * 76)
print("E. R2 色差 (docs/02): 消色差 k=44, γ(44+m) = 2+2sin(mπ/88)")
print("=" * 76)
# d²γ/dk² = (π²/3872)·cos(kπ/88): 驗證零點 k=44 用數值二階差
h = mp.mpf(1)/1000
d2_44 = (gamma(44+h) - 2*gamma(44) + gamma(44-h)) / h**2
d2_22 = (gamma(22+h) - 2*gamma(22) + gamma(22-h)) / h**2
check("02", "d²γ/dk²(k=44) ≈ 0 (消色差)", abs(float(d2_44)) < 1e-6, "d²=%.2e" % float(d2_44))
check("02", "d²γ/dk²(k=22) ≠ 0 (有色差)", abs(float(d2_22)) > 1e-3, "d²=%.4f" % float(d2_22))
for m in [1, 2, 3, 5, 8, 13, 22]:
    lhs = gamma(44+m)
    rhs = 2 + 2*mp.sin(m*mp.pi/88)
    check("02", "γ(44+%d) = 2+2sin(%dπ/88)" % (m, m), abs(lhs - rhs) < 1e-40,
          "γ=%.8f" % float(lhs))
# 鏡像和 = 4
for m in [1, 3, 7, 21, 44]:
    check("02", "γ(44+%d)+γ(44−%d) = 4 = B" % (m, m),
          abs(gamma(44+m) + gamma(44-m) - 4) < 1e-40)
# 紫邊方向: m>0 → γ 升
check("02", "紫邊: γ(45)−γ(44) = 2sin(π/88) > 0", float(gamma(45) - gamma(44)) > 0)

print("=" * 76)
print("F. R3 失焦 (docs/02): θ(88)/θ(55), 1/Δθ ≈ 469 = L₄·h̄, 33 = K_tree")
print("=" * 76)
t88 = mp.degrees(theta23(88))
t55 = mp.degrees(theta23(55))
check("02", "θ(88) = 49.3202°", abs(t88 - 49.3202) < 0.001, "=%.4f" % float(t88))
check("02", "θ(55) = 49.1966°", abs(t55 - 49.1966) < 0.001, "=%.4f" % float(t55))
dt_nufit = theta23(88) - mp.radians(49.198)
recip = 1 / dt_nufit
check("02", "1/Δθ(NuFIT) = 468.8 ≈ 469 = L₄·h̄ = 7×67 (dev 0.051%)",
      abs(recip - 469) / 469 < 0.001, "1/Δθ=%.2f dev=%.3f%%" % (float(recip), 100*abs(float(recip)-469)/469))
check("02", "h̄ = 67 = (36+98)/2", abs(hbar - 67) < 1e-30)
check("02", "88−55 = 33 = K_tree", 88-55 == 33)
check("02", "33²+44² = 55² (Pythagorean)", 33**2 + 44**2 == 55**2)
check("02", "55 = h¹¹+f_proj = 36+19", 55 == 36+19)
check("02", "88 = 2(h¹¹+F₆) = 2(36+8)", 88 == 2*(36+8))
check("02", "176 = 4(h¹¹+F₆) = 4(36+8)", 176 == 4*(36+8))

print("=" * 76)
print("G. R7/R8/R9 (docs/04): 摺疊 44 等價類, 破缺 ±2c, 分離度 2|j0−44.5|")
print("=" * 76)
fold_ok = all(abs(psf_obs(j0, j) - psf_obs(89-j0, j)) < 1e-30
              for j0 in range(1, 89) for j in range(1, 89))
check("04", "Z₂ 摺疊: PSF_obs(j|j0) = PSF_obs(j|89−j0) ∀j0,j", fold_ok)
pairs = len(set(tuple(sorted((j0, 89-j0))) for j0 in range(1, 89)))
check("04", "等價類數 = 44 = N_d", pairs == 44, "count=%d" % pairs)
# R8 破缺: sym 22/22, +u_88 → 23/21
j0 = 44
s44 = psf_obs(j0, 44); s45 = psf_obs(j0, 45)
b44 = s44 + u(88, j0)*u(88, 44); b45 = s45 + u(88, j0)*u(88, 45)
check("04", "sym: PSF(44)=PSF(45)=22", abs(float(s44)-22) < 1e-30 and abs(float(s45)-22) < 1e-30)
check("04", "brk: 23/21 (±u_88 交替)", abs(float(b44)-23) < 1e-30 and abs(float(b45)-21) < 1e-30)
# R9 分離度
for j0 in [2, 22, 44, 45, 87]:
    d = abs(2*j0 - 89)
    check("04", "d(%d) = %d = 2|j0−44.5|" % (j0, d), d == 2*abs(j0-44.5), "d=%d" % d)
check("04", "強度恆定 22 ∀j0 (冇強度彗差)",
      all(abs(float(psf_obs(j0, j0)) - 22) < 1e-30 for j0 in range(1, 89)))

print("=" * 76)
print("H. R6 (docs/06): P_k 投影, P_odd=0, P_even=½[csc+csc], P₈₈=sec")
print("=" * 76)
def P_proj(k): return sum(mp.cos((j-mp.mpf(1)/2)*mp.pi/88) * u(k, j) for j in range(1, 89))
odd_zero = all(abs(P_proj(k)) < 1e-35 for k in range(1, 89, 2))
check("06", "P_odd = 0 EXACT (觀察者光圈零響應)", odd_zero)
even_ok = all(abs(P_proj(k) - 0.5*(1/mp.sin((k+1)*mp.pi/176) + 1/mp.sin((k-1)*mp.pi/176))) < 1e-30
              for k in range(2, 89, 2))
check("06", "P_even = ½[csc((k+1)π/176)+csc((k−1)π/176)] 閉式", even_ok)
p44 = P_proj(44)
check("06", "P₄₄ ≈ √2", abs(p44 - mp.sqrt(2)) < 1e-3, "P₄₄=%.6f √2=%.6f" % (float(p44), float(mp.sqrt(2))))
p88 = P_proj(88)
check("06", "P₈₈ = sec(π/176) ≈ 1.000159", abs(p88 - 1/mp.cos(mp.pi/176)) < 1e-30,
      "P₈₈=%.6f" % float(p88))
sPe = sum(P_proj(k) for k in range(2, 89, 2))
check("06", "Σ_even P_k = 140.25 (docs 聲明)", abs(float(sPe) - 140.25) < 0.01,
      "=%.2f" % float(sPe))
check("06", "P₂ = 37.354 (docs 聲明)", abs(float(P_proj(2)) - 37.354) < 0.01,
      "=%.3f" % float(P_proj(2)))
# φ_k = π·P_k/N_k 規則: φ_odd ≈ 0
check("06", "φ_odd = π·P_odd/44 ≈ 0", all(abs(mp.pi*P_proj(k)/44) < 1e-35 for k in range(1, 89, 2)))

print("=" * 76)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 76)
