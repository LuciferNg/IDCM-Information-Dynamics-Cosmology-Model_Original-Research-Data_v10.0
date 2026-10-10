#!/usr/bin/env python3
"""
O48 Q1 v4: Planck Silk ℓ_D=1411 嘅 IDCM 結構身份
=============================================================
發現 (v3): 峰高模型 (m=2,3,5,7) 用 9055 → RMS 0.301% 閉合; 用 1411 → RMS 95% 爆。
         即 9055 係「峰高殘差阻尼尺度」, 唔係 C_ℓ 譜 Silk scale。

本 script 測試:
H1. Planck Silk ℓ_D=1411 有 IDCM 結構身份: 1411 = 44×32+3 = 44×F₂⁵+F₄
      而峰 7 位置 ℓ₇ = 1409 = 44×32+1 = 44×F₂⁵+F₂
      ⟹ 1411 = ℓ₇ + 2 = ℓ₇ + F₃  (Silk damping 起點 = 最後質數峰 + F₃)
H2. 分層裁決: 峰高模型用 9055 (O48), C_ℓ 譜 damping 用 1411
      (Planck) — 兩個唔同層級, O241 R10 比較錯對象
H3. 9055 嘅「殘差身份」: 9055 = Σγ_even×10² + F₁₀ = 90×100+55
      驗證 9055 亦 = 88×103−9 (原結構式) — 兩者一致?
      88×103−9 = 9064−9 = 9055;  90×100+55 = 9055 ✓ 但意義探索
H4. C_ℓ 譜尾段盲測: 用 ℓ_D=1411 (IDCM 結構身份) 對比 Planck 高ℓ尾段
"""
import math, os, sys, json
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

phi = (1 + 5**0.5)/2
eps = phi**-1/4
F  = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
F7 = F(7); F3 = F(3); F2 = F(2); F4 = F(4); F5 = F(5)

print("="*74)
print("H1. 1411 嘅結構身份")
print("="*74)
print(f"  峰 7: ℓ₇ = 1409 = 44×{1409//44} + {1409-44*32} = 44×F₂⁵ + F₂")
print(f"  Silk: 1411 = 44×{1411//44} + {1411-44*32} = 44×F₂⁵ + F₄")
print(f"  1411 − 1409 = {1411-1409} = F₃ = {F3}")
print(f"  dev = {(1411-1409)/1409*100:.3f}%")
check("H1a: 1411 = ℓ₇ + F₃", 1411 == 1409 + F3)
check("H1b: 1409 = 44×32+1  (峰7 N=32=F₂⁵, s=1)", 1409 == 44*32+1)
check("H1c: 1411 = 44×32+3  (F₄ 修正)", 1411 == 44*32+3)

print()
print("  詮釋候選: Silk damping 起點 = 最後質數峰位置 + F₃")
print("  (峰 7 = 最後可分辨聲學峰; damping 喺其後開始主導)")

# ---------- H2. 分層裁決 ----------
print("\n" + "="*74)
print("H2. 分層裁決: 兩個阻尼尺度, 兩個對象")
print("="*74)
print("""  層級 1 (峰高模型, O48): ℓ_D = 9055
    - 控制 5 個質數峰 (221..1409) 嘅相對高度
    - RMS 0.301% (v3 A 段已證)
    - 唔可以係 1411 (RMS 95% 爆表)

  層級 2 (C_ℓ 譜 damping, Planck): ℓ_D = 1411
    - 控制高 ℓ 連續譜嘅指數衰減 (Silk tail)
    - 結構身份: 1411 = ℓ₇ + F₃ = 44×F₂⁵+F₄

  O241 R10 錯誤: 用層級 1 嘅尺度 (9055) 判層級 2 嘅行為 (D(1733)/D(1121))
  → 類別錯誤 (comparing peak-height damping to spectral damping)""")
check("H2a: 1411 有結構身份", 1411 == 44*32+3 and 1411 == 1409+F3)

# ---------- H3. 9055 嘅兩種分解 ----------
print("\n" + "="*74)
print("H3. 9055 嘅結構身份 (兩種分解)")
print("="*74)
print(f"  (i)  88×103 − 9 = 9064 − 9 (O48 原結構式)")
print(f"  (ii) 90×100 + 55 = Σγ_even×10² + F₁₀")
print(f"  (iii) 9055 = 5×1811 (質因數; F₅×質數)")
print()
print("  有趣: 90×100+55 形式 — 90=Σγ_even, 55=F₁₀")
print("  而 88×103−9: 88=2Nd, 103=Nd+M+2F₇, 9=F₄²")
print("  兩個分解都需要確認係咪同一結構嘅不同投影")
print()
# 檢查: 103 vs 90: 103−90 = 13 = F₇!  88+? : 
# 88×103−9 vs 90×100+55:
# 88×103 = 9064;  90×100 = 9000; 差 64 = ?
print(f"  88×103 − 90×100 = {88*103 - 90*100} = 64 = 2^6? 或 F₂⁵+F₂⁵?")
print(f"  −9 − 55 = -64? 9+55 = 64! ... 64 = 2^6")
print(f"  所以: 88×103 − 9 = 90×100 + 55  ⟺ 88×103 − 90×100 = 9 + 55 = 64")
print(f"  ⟺ 88×103 − 90×100 = 64: 驗證 {88*103} - {90*100} = {88*103-90*100}")
check("H3a: 兩分解一致 (64=9+55)", 88*103 - 90*100 == 9 + 55)
print(f"  64 = F₂⁵+F₂⁵? 32+32;  64 = 2^6 = (Nd/44)? ...")
print("  64 = 8² = B² (B=8 = 44/5.5?), 更直接: 64 = 2F₂⁵×2F₂⁵/16?")
print("  留註: 兩種分解嘅「差」= 64 = 2⁶, 而 9+55=64 自我一致")

# ---------- H4. C_ℓ 譜尾段盲測 (ℓ_D=1411 結構身份) ----------
print("\n" + "="*74)
print("H4. 高 ℓ 尾段: 盲測用 1411 (結構身份)")
print("="*74)
base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
# Planck TT: ℓ, D (col 1, 2)
planck_tt = []
with open(f"{base}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                planck_tt.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
planck_tt = sorted(planck_tt)
print(f"  Planck bins: {len(planck_tt)} (ℓ {planck_tt[0][0]:.0f}..{planck_tt[-1][0]:.0f})")

# 睇 ℓ=1121 同 ℓ=1733 附近 (O241 R10 用)
def binD(et, w=40):
    c = [d for e, d in planck_tt if abs(e-et) <= w]
    return sum(c)/len(c) if c else None
D1121, D1733 = binD(1121), binD(1733)
if D1121 and D1733:
    ratio_obs = D1733/D1121
    # 模型: 假定雙層: C_ℓ = Acoustic × Silk; 高ℓ段 acoustic 由峰包絡
    # 用 1411 (IDCM 結構) vs 9055 (峰高) vs 用 Planck peak-anchor
    r_1411 = math.exp(-((1733/1411)**1.24 - (1121/1411)**1.24))
    r_1411_15 = math.exp(-((1733/1411)**1.5 - (1121/1411)**1.5))
    r_9055  = math.exp(-((1733/9055)**1.5 - (1121/9055)**1.5))
    print(f"  Planck 實測 (raw bins): D(1121)={D1121:.5f}, D(1733)={D1733:.5f}, ratio={ratio_obs:.4f}")
    print(f"  ※ raw bin ratio 唔係峰包絡 (O241 用 peak-top anchor 0.327)")
    print(f"  ΛCDM(1411, α=1.24) 預言 ratio = {r_1411:.3f}")
    print(f"  1411, α=1.5 預言 = {r_1411_15:.3f}")
    print(f"  IDCM(9055, α=1.5) 預言 = {r_9055:.3f}")

# 尾段完整衰減: ℓ > 1400 局部峰 (O241 概念: 峰包絡 anchor)
print("\n  高 ℓ 局部峰 (ℓ>1000):")
pks = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if 1000 < e0 < 2600 and d0 > planck_tt[i-1][1] and d0 > planck_tt[i+1][1]:
        pks.append((e0, d0))
for e, d in pks:
    print(f"    ℓ={e:.0f}: D={d:.4f}")
if len(pks) >= 3:
    # 峰包絡 fit: 用 3 個高ℓ峰 (raw bins 有局限, 但試)
    xs = np.array([e for e, d in pks], dtype=float)
    ys = np.log(np.array([d for e, d in pks], dtype=float))
    # 用 1411 結構: 期望 slope = -1/1411^1.24
    # fit α=1.24: 
    xa = xs**1.24
    coef = np.polyfit(xa, ys, 1)
    lD_fit = (-1/coef[0])**(1/1.24)
    print(f"  → 高ℓ峰包絡 fit (α=1.24): ℓ_D = {lD_fit:.0f}")
    print(f"  → 對比 Planck 1411: dev = {(lD_fit-1411)/1411*100:+.1f}%")

print("\n" + "="*74)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*74)
sys.exit(0 if FAIL == 0 else 1)