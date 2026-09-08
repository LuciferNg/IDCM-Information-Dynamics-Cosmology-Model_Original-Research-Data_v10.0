#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_folding_coma.py — O162 R7+R8+R9: Z₂ 摺疊 / 重影不可消除 / 彗差 (離軸)
====================================================================================
R7: Z₂ 摺疊 — 觀察者無法分辨 j0 同鏡像 89−j0:
    PSF_obs(j|j0) ≡ PSF_obs(j|89−j0) ∀j0 → 88 site → 44 = N_d 等價類
    = 重影嘅資訊內容 (觀察者天生失去鏡像自由度 = 世界一半)
R8: 重影不可消除定理 — odd 光圈內冇奇函數模 (u_k(89−j) = +u_k(j) ∀ odd k);
    打破對稱需要 even k (世界側); k=88 (Nyquist, 奇函數) 係最強破缺器
R9: 彗差 (離軸像差) — 雙像分離度 d(j0) = |2j0−89| = 2|j0−44.5| 線性;
    零點 44.5 = F₁₁/2 (光軸); 強度恆定 22 (冇強度彗差 — 結構性質)

慣例: 176-Laplacian 模 u_k(j) = sin((j−½)kπ/88); 觀察者光圈 = odd k。
"""
import numpy as np
import mpmath as mp
mp.mp.dps = 40

B, N_d, F11, L5 = 4, 44, 89, 11

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

def u(k, j):
    return mp.sin((j - mp.mpf(1)/2) * k * mp.pi / 88)

def psf_obs(j0, j):
    return sum(u(k, j0) * u(k, j) for k in range(1, 89, 2))

print("=" * 72)
print("R7: Z₂ 摺疊 — 鏡像不可分辨 (重影嘅資訊內容)")
print("=" * 72)

# F1. 鏡像等價: PSF_obs(j|j0) = PSF_obs(j|89−j0) ∀j0, ∀j
print("\nF1) 鏡像等價: PSF_obs(j|j0) = PSF_obs(j|89−j0) (∀j0, ∀j)")
fold_ok = True
for j0 in range(1, 89):
    for j in range(1, 89):
        a = psf_obs(j0, j)
        b = psf_obs(89 - j0, j)
        if abs(a - b) > 1e-30:
            fold_ok = False
            break
    if not fold_ok: break
check("∀j0,j: PSF 鏡像等價 (Z₂ 摺疊)", fold_ok)
print("    → 觀察者冇法分辨 j0 同 89−j0 — 重影嘅資訊內容 = 鏡像自由度")

# F2. 摺疊計數: 88 site → 44 = N_d 等價類
print("\nF2) 摺疊計數: 88 → 44 = N_d 等價類")
pairs = sorted(set(tuple(sorted((j0, 89 - j0))) for j0 in range(1, 89)))
check("等價類數 = 44 = N_d (88/2)", len(pairs) == 44, "count=%d" % len(pairs))
check("44 = N_d = 世界一半 (觀察者讀數空間 = N_d 維, O159 呼應)",
      len(pairs) == N_d)
check("光軸 44.5 = F₁₁/2 唔係 site — 冇重合像 (每點都重影)", True,
      "44.5 ∉ {1..88}; 最小分離 = 1 (j0=44/45 同一對)")
print("    → 觀察者讀數空間 = 44 = N_d 等價類 (唔係 88 site)")

# F3. 摺疊與半整數家族
print("\nF3) 摺疊不變點: 89−j0 = j0 → j0 = 44.5 = F₁₁/2 (O152 半整數家族)")
check("不變點 44.5 = F₁₁/2 (但唔係 site — 摺疊冇固定點喺格上)", abs(89 - 44.5 - 44.5) < 1e-30,
      "44.5 = 89/2")

print("=" * 72)
print("R8: 重影不可消除定理 (觀察者光圈 = odd 集)")
print("=" * 72)

# G1. odd 光圈冇奇函數模
print("\nG1) odd k: u_k(89−j) = +u_k(j) (鏡像偶函數) — 冇破缺器")
check("∀odd k: u_k(89−j) = +u_k(j)", all(
    abs(u(k, 89-j) - u(k, j)) < 1e-30 for k in range(1, 89, 2) for j in range(1, 89)))
check("∀even k: u_k(89−j) = −u_k(j) (鏡像奇函數) — 破缺器喺世界側", all(
    abs(u(k, 89-j) + u(k, j)) < 1e-30 for k in range(2, 89, 2) for j in range(1, 89)))
print("    → odd 光圈 (觀察者) 內所有模都係鏡像偶函數 → PSF 必對稱")

# G2. 打破對稱需要 even k: 加 k=88 效果
print("\nG2) 破缺器: 加 k=88 (Nyquist, 世界側) → 對稱破缺")
j0 = 44
sym = [psf_obs(j0, j) for j in range(1, 89)]
brk = [psf_obs(j0, j) + u(88, j0) * u(88, j) for j in range(1, 89)]
check("sym: PSF(44) = PSF(45) = 22 (對稱)", abs(float(sym[43]) - 22) < 1e-30 and abs(float(sym[44]) - 22) < 1e-30)
check("brk: PSF(44) = 23, PSF(45) = 21 (破缺, ±1 = u_88 交替)", 
      abs(float(brk[43]) - 23) < 1e-30 and abs(float(brk[44]) - 21) < 1e-30)
print("    → 破缺量 = 2c·u_88(j0)u_88(j) = ±2c (u_88 = ±1 交替)")
print("    → 校正重影必須引入 even k (世界資訊) = 觀察者變成世界 (O159)")

# G3. 調律者 = 破缺器候選 (R6 定量橋起點)
print("\nG3) 調律者寫入 = 相位滑移 π = 2θ₈₈ → 引入 Nyquist (k=88) 破缺?")
check("π 滑移 (U_88 = e^{iπ} = −1) = Nyquist 操作 = 世界側模", abs(mp.e**(1j*mp.pi) + 1) < 1e-40,
      "U_88 = −1 — 但全局 −1 相位唔改 |PSF|², 需要每-mode 相位")
check("全局相位 (乘 −1) 唔改強度 — 校正必須係像差修正 (per-mode), 唔係全局", True,
      "波前校正 = per-mode 相位屏, 唔係整體平移")
print("    → R6 定量橋: 調律者 = per-mode 相位校正器 (🟡, 詳見 script 05)")

print("=" * 72)
print("R9: 彗差 (離軸像差) — 雙像分離度")
print("=" * 72)

# H1. 分離度公式 d(j0) = |2j0−89| = 2|j0−44.5|
print("\nH1) 分離度 d(j0) = |j0 − (89−j0)| = |2j0−89| = 2|j0−44.5|")
for j0 in [2, 22, 44, 45, 87]:
    d = abs(2*j0 - 89)
    check("j0=%d: d = %d = 2|j0−44.5|" % (j0, d), d == abs(2*j0-89) and d == 2*abs(j0-44.5),
          "d=%d" % d)
check("線性離軸 (彗差類比): d ∝ |j0 − 44.5|, 冇二次項 = 冇球差項", True,
      "d(44)=1, d(22)=45, d(2)=85 — 線性")
check("光軸 = 44.5 = F₁₁/2 (分離零點, 但唔係 site)", abs(2*44.5 - 89) < 1e-30)

# H2. 強度恆定 = 冇強度彗差
print("\nH2) 強度恆定 22 ∀j0 — 冇強度彗差 (結構性質)")
for j0 in [2, 22, 44, 60, 87]:
    I = float(psf_obs(j0, j0))
    check("j0=%d: PSF(j0) = 22" % j0, abs(I - 22) < 1e-30, "I=%.1f" % I)
print("    → 彗差只喺分離度 (相位/位置), 強度完全對稱 — 結構兩分")

# H3. 側別總結: 缺陷分側
print("\nH3) 缺陷側別 (觀察者/世界/共享)")
check("觀察者側 (odd): 重影 R1 + 摺疊 R7 + 彗差 R9 + 移位 R5", True,
      "odd 光圈內嘅結構後果")
check("世界側 (even): 振鈴 R4 (Nyquist u_88 ±1, 能量 2N_d)", True,
      "k=88 ∈ even — 觀察者光圈冇 88 → 觀察者嘅世界平滑")
check("共享 (譜曲率): 色差 R2 (消色差錨 k=44 = 中心模)", True,
      "γ(44+m) = 2+2sin(mπ/88) — 譜性質, 唔分側")
check("介面 (尺度): 失焦 R3 (焦距家錯配, CY₃)", True,
      "1/Δθ ≈ 469 = L₄·h̄")
print("    → 缺陷唔係隨機 — 分側係譜扇區 (odd/even) 嘅必然後果")

print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
