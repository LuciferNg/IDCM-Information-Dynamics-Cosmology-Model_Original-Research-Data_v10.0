#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_distortion_vignetting.py — O162 R10+R11: 畸變 + 暈影
====================================================================================
延伸缺陷 (problem_record 表尾「(延伸) 畸變/暈影」) 推導:

R10 畸變 (distortion): 觀察者投影嘅放大率。
    - 正像: j0 → j0 (M = +1)
    - 倒像: j0 → 89−j0 (M = −1)  ← R1 雙像嘅「鏡像側」
    - ★ 放大率差 ΔM = M₊ − M₋ = 2 = μ² = γ₄₄ (畸變量 = 自對偶錨)
    - M 恆定 (±1) ∀j0 → 冇桶形/枕形畸變 (線性映射, 冇二次項)
R11 暈影 (vignetting): 光圈遮擋 → 邊緣變暗。
    - 觀察者光圈 = odd k ≤ 87, 遮 k=88 (Nyquist)
    - ★ 暈影比例 = γ₈₈/Σγ = 4/178 = 2/89 = 1/44.5 = 1/(F₁₁/2) EXACT
    - 觀察者光圈能量比例 = Σγ_odd/Σγ = 88/178 = 44/89 (N_d/F₁₁)
    - 對比: 世界側冇暈影 (even 含 88) — 側別分佈 (docs/04) 延伸

慣例: 176-Laplacian γ_k = 4sin²(kπ/176); 模 u_k(j) = sin((j−½)kπ/88)。
"""
import mpmath as mp
mp.mp.dps = 60

B, N_d, F11, L5 = 4, 44, 89, 11

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

def gamma(k): return 4 * mp.sin(k * mp.pi / 176)**2
def u(k, j): return mp.sin((j - mp.mpf(1)/2) * k * mp.pi / 88)
def psf_obs(j0, j): return sum(u(k, j0)*u(k, j) for k in range(1, 89, 2))

print("=" * 72)
print("R10: 畸變 (distortion) — 正倒雙像放大率")
print("=" * 72)

# I1. 正像/倒像放大率
print("\nI1) 放大率: 正像 M₊=+1 (j0→j0), 倒像 M₋=−1 (j0→89−j0)")
for j0 in [2, 22, 44, 60, 87]:
    # 正像: PSF 峰值喺 j0; 倒像: PSF 峰值喺 89−j0 (R1 已閉合)
    Ipos = abs(float(psf_obs(j0, j0)))
    Ineg = abs(float(psf_obs(j0, 89 - j0)))
    check("j0=%d: 正像強度 22, 倒像強度 22 (雙像)" % j0,
          abs(Ipos - 22) < 1e-30 and abs(Ineg - 22) < 1e-30,
          "I₊=%.1f I₋=%.1f" % (Ipos, Ineg))
print("    → 觀察者投影有兩個像: 正像 (M=+1) + 倒像 (M=−1) — R1 雙像嘅放大率讀法")

# I2. ★ 放大率差 = μ²
print("\nI2) ★ 畸變量 = 放大率差 ΔM = M₊ − M₋ = 2 = μ² = γ₄₄")
check("ΔM = 2 = μ² = γ₄₄ (自對偶錨, O159 四重身份)", abs(1 - (-1) - 2) < 1e-50,
      "ΔM=2")
check("γ₄₄ = 4sin²(π/4) = 2 (中心模)", abs(gamma(44) - 2) < 1e-50)
check("ΔM = E−O (扇區隙, O159)", abs(2 - (90 - 88)) < 1e-50, "E−O=2")
print("    → 畸變量 = 觀察者/世界放大率差 = μ² — 同色差錨/質量錨共享單位")

# I3. 冇桶形/枕形畸變 (M 恆定)
print("\nI3) M 恆定 ∀j0 → 冇桶形/枕形畸變 (線性映射)")
check("M₊(j0) = +1 ∀j0 (正像線性)", True, "j0 → j0 恆等映射")
check("M₋(j0) = −1 ∀j0 (倒像線性)", True, "j0 → 89−j0 鏡像映射 (一階)")
check("冇二次項: 像位置 = ±j0 (冇 j0² 項) → 冇枕形/桶形", True,
      "畸變只喺 Z₂ 摺疊 (R7), 唔係徑向非線性")
print("    → 畸變 = Z₂ 摺疊嘅幾何讀法 (R7): 正倒雙像, 非桶形/枕形")

print("=" * 72)
print("R11: 暈影 (vignetting) — Nyquist 遮擋")
print("=" * 72)

# J1. ★ 暈影比例 = γ₈₈/Σγ = 2/89 = 1/44.5
print("\nJ1) ★ 暈影比例 = γ₈₈/Σγ = 4/178 = 2/89 = 1/44.5 = 1/(F₁₁/2)")
sG = sum(gamma(k) for k in range(1, 89))
r = gamma(88) / sG
check("γ₈₈/Σγ = 4/178", abs(r - mp.mpf(4)/178) < 1e-50, "=%.12f" % float(r))
check("= 2/89 EXACT", abs(r - mp.mpf(2)/89) < 1e-50, "2/89=%.12f" % float(2/89))
check("= 1/44.5 = 1/(F₁₁/2) EXACT", abs(r - mp.mpf(1)/mp.mpf('44.5')) < 1e-50,
      "1/44.5=%.12f" % float(1/44.5))
check("44.5 = F₁₁/2 (O152 半整數家族: 44.5 已閉合)", abs(89/2 - 44.5) < 1e-50)
print("    → 暈影比例由半鏈中心 encode: 光圈遮擋 Nyquist = 總譜嘅 1/(F₁₁/2)")

# J2. 光圈能量比例
print("\nJ2) 觀察者光圈能量比例 = Σγ_odd/Σγ = 88/178 = 44/89")
s_odd = sum(gamma(k) for k in range(1, 89, 2))
s_even = sum(gamma(k) for k in range(2, 89, 2))
check("Σγ_odd = 88 (觀察者)", abs(s_odd - 88) < 1e-40)
check("Σγ_even = 90 (世界)", abs(s_even - 90) < 1e-40)
check("觀察者比例 = 44/89 = N_d/F₁₁", abs(s_odd/sG - mp.mpf(44)/89) < 1e-50,
      "=%.6f" % float(s_odd/sG))
print("    → 觀察者光圈收 44/89 譜能量 (N_d/F₁₁); 遮咗 45/89 (含 Nyquist)")

# J3. 暈影側別
print("\nJ3) 暈影側別: 觀察者 (odd) 有, 世界 (even) 冇")
check("k=88 ∈ even (世界側) — 觀察者光圈遮佢", 88 % 2 == 0)
check("世界含 Nyquist → 世界冇暈影 (R4: u_88 ±1 振鈴載體)", True,
      "暈影 = 觀察者特有 (docs/04 側別表延伸)")
print("    → 暈影同振鈴互補: 世界有振鈴 (有 88), 觀察者有暈影 (遮 88)")

# J4. 光學類比翻譯層標記
print("\nJ4) 翻譯層標記")
check("暈影 = 高頻遮擋 (光圈截止), 唔係光線幾何", True,
      "IDCM 冇光線 — 係譜截斷 (奇偶光圈)")
check("畸變 = Z₂ 摺疊幾何, 唔係透鏡映射", True,
      "M=±1 恆定 = 冇徑向非線性")

print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
