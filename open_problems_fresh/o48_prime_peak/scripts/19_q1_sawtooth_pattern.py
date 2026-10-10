#!/usr/bin/env python3
"""
O48 Q1.6: 鋸齒傳輸函數假說 — pattern 重複檢驗
=============================================================
調律者:「這個傳輸函數莫非又是鋸齒形嗎」

鋸齒形 = 峰/谷交替嘅「週期性圖案」而非單一平滑包絡。

18 script 發現: 高 ℓ 局部峰間距三重奏 [45,27,36] 喺兩區間重複:
  1013 →1058 →1085 →1121  (間距 45, 27, 36)
  1292 →1337 →1364 →1400  (間距 45, 27, 36)

本 script 檢驗:
  A. 兩區間形狀相似度 (correlation, 用 interpolate 對齊)
  B. pattern [45,27,36] 嘅統計顯著性 (隨機間距撞 pattern 概率)
  C. 鋸齒週期來源: 44 週期係「峰位模 44」嘅體現, 間距 45/27/36 嘅結構
     (45 = 44+1, 27 = 22+5??, 36 = 33+3??)
  D. 理論傳輸函數: T(ℓ) = 平滑包絡 × 鋸齒因子
     鋸齒因子候選: |sinc(π ℓ/44)| 或 Σ sin(2πℓ/44·k)/k 鋸齒波
"""
import math, sys
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

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
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

# ---------- A. 兩區間形狀相似度 ----------
print("="*72)
print("A. 兩區間 [1013..1121] vs [1292..1400] 形狀比較")
print("="*72)
def seg(lo, hi):
    pts = [(e, d) for e, d in planck_tt if lo <= e <= hi]
    ells = np.array([e for e, d in pts])
    Ds = np.array([d for e, d in pts])
    # 對齊到 45 格網
    return ells, Ds

e1, d1 = seg(1013, 1121)
e2, d2 = seg(1292, 1400)
# 兩段各 108 格 (45+27+36), 節點相同:
# 段1: 1013(0), 1058(45), 1085(72), 1121(108)
# 段2: 1292(0), 1337(45), 1364(72), 1400(108)
print(f"  段1 峰位: {[1013,1058,1085,1121]}")
print(f"  段2 峰位: {[1292,1337,1364,1400]}")
print(f"  段長: 108 = 45+27+36")

# interpolate 每段到 109 點 (0..108)
grid = np.arange(109)
D1i = np.interp(grid, e1-1013, d1)
D2i = np.interp(grid, e2-1292, d2)
# Pearson correlation
m1, m2 = D1i.mean(), D2i.mean()
cov = ((D1i-m1)*(D2i-m2)).sum()
s1, s2 = np.sqrt(((D1i-m1)**2).sum()), np.sqrt(((D2i-m2)**2).sum())
corr = cov/(s1*s2)
print(f"  兩段形狀 correlation = {corr:.4f}")
check("A1: 兩區間形狀相關 (corr>0.7)", corr > 0.7, f"corr={corr:.4f}")

# ---------- B. pattern 重複統計 ----------
print("\n" + "="*72)
print("B. [45,27,36] 重複嘅統計顯著性")
print("="*72)
# 高ℓ局部峰
pks = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if 900 < e0 < 2600 and d0 > planck_tt[i-1][1] and d0 > planck_tt[i+1][1]:
        pks.append(e0)
print(f"  高ℓ峰: {[int(e) for e in pks]}")
gaps = [int(pks[i+1]-pks[i]) for i in range(len(pks)-1)]
print(f"  間距: {gaps}")
# pattern 出現: 連續 3 間距 [45,27,36]
pat = (45, 27, 36)
cnt = sum(1 for i in range(len(gaps)-2) if tuple(gaps[i:i+3]) == pat)
print(f"  [45,27,36] 精確出現次數: {cnt}")
# 隨機 null: 平均間距 ~115, 44 週期間距 45/27/36 概率?
# 若間距獨立均勻 [20..400], P(g=45)=P(g=27)=P(g=36)=1/380 → P(pattern) ≈ 1/380³ ≈ 1.8e-8
# 但間距唔係均勻。近似: 密集段 (間距<100) 概率 P_dense ≈ 6/12 = 0.5
# 每個密集間距取 {45,27,36} 之一? 密集間距 [45,27,36,34,36] ...
dense = [g for g in gaps if g < 100]
print(f"  密集間距 (<100): {dense}")
from collections import Counter
cnt_dense = Counter(dense)
print(f"  密集間距分佈: {dict(cnt_dense)}")
# 45 出現 2 次, 27 出現 2 次, 36 出現 3 次
check("B1: pattern [45,27,36] 出現 ≥2 次", cnt >= 2, f"cnt={cnt}")

# ---------- C. 間距結構 ----------
print("\n" + "="*72)
print("C. 間距嘅 44-結構")
print("="*72)
for g in sorted(set(dense)):
    print(f"  {g}: mod44 = {g%44:2d}, =? 44×(1,2,3)±delta")
print()
print("  45 = 44+1 = 44 + F₁")
print("  27 = ?  27 = 44−17?  17 = 峰6 相位 s=17 (被抑制!)")
print("  36 = 33+3 = M+F₄?")
print("  34 = F₉ = 34!")
print("  85 = 88−3 = 88−F₄")
# 45, 27, 36, 34, 85 對 Fib/Lucas:
Fseq = [1,2,3,5,8,13,21,34,55,89]
print(f"  27 = ? 27 唔係 Fib; 27 = 3³ = F₄³")
print(f"  45 = 5×9 = F₅×F₄²;  36 = 6²;  34=F₉;  85=5×17")
print("  → 間距多數唔係簡單 Fib — 鋸齒結構可能係相位週期嘅拍頻")
# 相位週期: s_o mod 44 步進 45/27/36 → ℓ 每步 44 增 1: 峰位公式 ℓ_m = 44N+s
# Δℓ = 44ΔN + Δs; Δs = 1, ?: 45 = 44×1+1: ΔN=1, Δs=1
# 27 = 44×1−17: ΔN=1, Δs=−17;  36 = 44×1−8? ΔN=1, Δs=−8
print()
print("  若 Δℓ = 44ΔN + Δs:")
print("    45 = 44×1 + 1   (ΔN=1, Δs=+1)")
print("    27 = 44×1 − 17  (ΔN=1, Δs=−17)")
print("    36 = 44×1 − 8   (ΔN=1, Δs=−8)")
print("  34 = 44×1 − 10  (ΔN=1, Δs=−10)")
print("  85 = 44×2 − 3   (ΔN=2, Δs=−3)")
check("C1: 所有密集間距 = 44k±δ (δ=Fib)", 
      all(g % 44 in [0,1,2,3,5,8,13,21,34] or (44-g%44) in [0,1,2,3,5,8,13,21,34] for g in dense),
      f"mods={[g%44 for g in dense]}")

# ---------- D. 理論: 鋸齒傳輸函數 ----------
print("\n" + "="*72)
print("D. 理論建模: 鋸齒傳輸函數")
print("="*72)
# IDCM C_ℓ = 聲學包絡 × T_saw(ℓ)
# T_saw 候選 1: |sinc(π(ℓ−ℓ₀)/44)| — 週期 44 嘅 sinc 疊加 = 鋸齒
# T_saw 候選 2: 鋸齒波 saw(ℓ) = 2/π Σ sin(k·2πℓ/44)/k — 鋸齒波 Fourier
# 測試 Planck 高ℓ殘差 (18 script detrend 後) 形狀
high = [(e, d) for e, d in planck_tt if 900 < e < 2600]
ells = np.array([e for e, d in high])
Ds = np.array([d for e, d in high])
logD = np.log(Ds)
coef = np.polyfit(ells, logD, 2)
res = Ds / np.exp(np.polyval(coef, ells))
print(f"  高ℓ detrend 殘差: min {res.min():.3f}, max {res.max():.3f}, std {res.std():.3f}")
# 殘差喺 ℓ mod 44 嘅平均 (鋸齒週期疊加)
res_by_r = {}
for e, r in zip(ells, res):
    r44 = int(e) % 44
    res_by_r.setdefault(r44, []).append(r)
print("  ⟨res⟩ 按 ℓ mod 44:")
mods_avg = []
for r44 in sorted(res_by_r):
    avg = np.mean(res_by_r[r44])
    mods_avg.append((r44, avg))
saw = [a for r, a in mods_avg]
if saw:
    print(f"  鋸齒幅度 (max−min): {max(saw)-min(saw):.3f}")
    print(f"  ⟨res⟩ 標準差: {np.std(saw):.4f} (全殘差 std {res.std():.3f})")
    # 如果 mod-44 平均變化大過全域, 就係 44 週期鋸齒
    print(f"  鋸齒信號/噪聲: mod-44 std / sampling std ≈ {np.std(saw)/(res.std()/math.sqrt(len(ells)/44)):.2f}")
    check("D1: mod-44 鋸齒結構存在 (周期均值變化>全域均值變化)",
          abs(max(saw)-min(saw)) > 0.1, f"range={max(saw)-min(saw):.3f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)