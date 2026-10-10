#!/usr/bin/env python3
"""
O48 Q1: ℓ_D = 9055 物理機制推導 (Silk 阻尼 / 傳輸函數模型)
=============================================================
⚠️ 探索 script: 本檔有**預期 FAIL 檢查**（記錄探索發現，非 regression）。
     「9055 唔係 4 峰/5 峰唯一擬合值」= Q1 起點發現。
     最終裁決見 scripts/14_q1_ruling.py (5/5 PASS)。
前提: O48 已閉合 ℓ_D = 88(Nd+M+2F7) - F4^2 = 9055 (零自由參數結構式)
O241 R10 記錄 FAIL: IDCM 9055 vs Planck Silk 1411 = 6.42x

本 script 目標:
A. 獨立重現 O10 擬合 (5 真峰幅度) → 確認 9055 由數據擬合得出
B. 測試假說 H1: 9055 ≠ Silk damping scale, 因為 Silk 達 Lamina
   喺仲苛早期傳輸函數嘅指數不是 3/2 而係 1.24
C. 測試假說 H2: Planck ℓ_D=1411 對應幾何平均 (9055/6.42?), 尋找結構比
D. 推導 9055 嘅「吸收長」(Silk 阻尼距離) 機制:
   D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}] 係擴散隨機遊走嘅結果 (三維),
   而 IDCM 用 88-site 對偶鏈嘅「離散步長」推導 ℓ_D
E. 檢驗: 高 ℓ 尾段 Planck 數據 vs IDCM 9055 vs ΛCDM 1411 vs 新推導
"""
import math, os, json, sys
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
L  = lambda n: int(round(phi**n + (-phi)**(-n)))
Nd, M = 44, 33

# ---------- A. 重現 O10 擬合 ----------
print("="*74)
print("A. O10 5-峰擬合重現 (真峰幅度)")
print("="*74)
A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

def geo(j):
    # 3eps * prod_{k=1}^{j-1} F_k/F_{k+1} 連乘坍縮 = 3eps/F_j
    return 3*eps/F(j)

# implied damping D = A/geo
print("\n  Implied damping (A/geo):")
Ds = {}
for m in [1,2,3,5,7]:
    D = A[m]/geo({1:1,2:1,3:2,5:3,7:4}[m])
    Ds[m] = D
    print(f"    m={m} ell={ell[m]}: A={A[m]:.4f} geo={geo({1:1,2:2,3:3,5:4,7:5}[m]):.4f} D={D:.4f}")

# 用 m=2,3,5,7 (m=1 基準) 擬合 ln D = -(ell/ellD)^1.5
ells = np.array([ell[m] for m in [2,3,5,7]], dtype=float)
dvals = np.array([Ds[m] for m in [2,3,5,7]], dtype=float)
lnD = np.log(dvals)
x = ells**1.5
coeff = np.polyfit(x, lnD, 1)
lD_fit = (-1/coeff[0])**(2/3)
print(f"\n  擬合: slope={coeff[0]:.6f}, intercept={coeff[1]:.4f}")
print(f"  ℓ_D(fit, 4 峰) = {lD_fit:.0f}")
check("A1: 4 峰擬合 ℓ_D ≈ 9055", abs(lD_fit - 9055) < 80, f"got {lD_fit:.0f}")

# 用全部 5 峰 (m=1 基準 D=1)
ells5 = np.array([ell[m] for m in [1,2,3,5,7]], dtype=float)
dvals5 = np.array([1.0] + [Ds[m] for m in [2,3,5,7]], dtype=float)
lnD5 = np.log(dvals5)
coef5 = np.polyfit(ells5**1.5, lnD5, 1)
lD5 = (-1/coef5[0])**(2/3)
print(f"  ℓ_D(fit, 5 峰) = {lD5:.0f}")
check("A2: 5 峰擬合 ℓ_D ≈ 9055", abs(lD5 - 9055) < 80, f"got {lD5:.0f}")

# ---------- B. Silk 指數之分 ----------
print("\n" + "="*74)
print("B. Silk 阻尼指數: 3/2 vs 1.24")
print("="*74)
# 文獻: Silk damping tail D(ell) ~ exp[-(ell/ell_D)^1.24] (ΛCDM CAMB)
# 但二維擴散投影 / 隨機遊走尾: exp[-(ell/ell_D)^(3/2)]?
# IDCM 用 3/2。 檢驗: 用 Planck 高 ℓ 尾 (data) 比較指數
# planck_tt.txt: ell D err
planck_tt = []
with open("../o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                planck_tt.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
planck_tt = sorted(planck_tt)
print(f"  Planck TT bins: {len(planck_tt)} (ell {planck_tt[0][0]:.0f}..{planck_tt[-1][0]:.0f})")

# 高 ℓ 尾: ell > 1400 攞尾段斜率, 睇 ln D vs ell^alpha
# 用 peak-normalized: 用 ℓ=1121 同 ℓ=1733 (O241 用)
D1121_obs = 0.327 / 0.961  # 唔, 直接用數據
# 抽附近 bins
def binned_D(ell_target, width=50):
    close = [(e, d) for e, d in planck_tt if abs(e-ell_target) <= width]
    if not close: return None
    return sum(d for e, d in close)/len(close)

D1121 = binned_D(1121); D1733 = binned_D(1733)
print(f"  D(1121)≈{D1121:.3f}, D(1733)≈{D1733:.3f}, ratio={D1733/D1121:.3f}" if D1121 and D1733 else "  bins missing")

# ---------- C. 9055 結構比 ----------
print("\n" + "="*74)
print("C. 9055 與 1411 嘅結構關係")
print("="*74)
# 9055 = 88*(44+33+2*13) - 9 = 9064-9
# 1411 = Planck ΛCDM Silk scale
r = 9055/1411
print(f"  9055/1411 = {r:.5f}")
print(f"  9055/(2π) = {9055/(2*math.pi):.2f}")
print(f"  9055/(2π) ≈ Planck 1411? dev = {(9055/(2*math.pi)-1411)/1411*100:+.2f}%")
print(f"  1411*2π = {1411*2*math.pi:.1f}")
print(f"  9055/(2π·√2) = {9055/(2*math.pi*math.sqrt(2)):.1f}")
# 結構: 1411 = ?
print(f"  1411 = 44×32+3? {44*32+3}")
print(f"  1411 = 88×16+3?  {88*16+3}")
print(f"  1411 = 1409+2 (峰7+2)")
print(f"  1411 = 33×42+25? {33*42+25}")

# 找出 1411 嘅 IDCM 分解候選
for a in [44, 88, 33, 103, 9055]:
    if a == 0: continue
    v = 9055/a
    if abs(v - round(v)) < 1e-6:
        print(f"  9055/{a} = {int(round(v))} (整數)")
check("C1: 1411 = 44*32+3 = 44*F2^5+3", 44*32+3 == 1411)

# ---------- D. 隨機遊走擴散推導 ----------
print("\n" + "="*74)
print("D. 隨機遊走 (Silk 阻尼) 機制")
print("="*74)
# Silk damping: 光子隨機遊走過 viscosity, 阻尼距離 r_D ~ sqrt(∫ η/(ρ) dt)
# 喺 CMB angular space: D(θ) ~ exp[-(θ/θ_D)^(3/2)], θ_D = 1/(k_D D_A)
# k_D = (2π)^(3/2) r_D ... 到底: ell_D = k_D D_A
# IDCM 把 ell_D 結構化: 9055 = 88*(Nd+M+2F7)-F4^2
# 睇 9055 嘅隨機遊走詮釋: 88 步, 每步 √103? 總平方位移 = 88*103 = 9064
# 9064-9 = 9055: 減去 F4^2 = 3^2 (最後一步修正)
print("  IDCM 詮釋: 88 步各 √103 位移 (無方向偏差隨機遊走)")
print(f"  ⟨Δ²⟩ = 88×103 = {88*103}")
print(f"  ⟨Δ²⟩-F₄² = {88*103 - 9}")
print("  10609 = 103²? ", 103**2)
print(f"  √9055 = {math.sqrt(9055):.4f}")
print(f"  √9064 = {math.sqrt(88*103):.4f}")
print(f"  103 = Nd+M+2F7 = {Nd+M+2*F(7)}")
# 隨機遊走: ℓ_D ~ √(N_steps) * step_size
# 如果 step = √103 ≈ 10.15, N=88: ℓ_D = 88*10.15 = 893? 唔啱
# 另一種: ℓ_D² = 9055² 對應 N² 步...
# 9055 = 88×103 - 9: 睇成 88 步, 每步 √103 (≈10.15), 總長 √(88·103) = √9064 ≈ 95.2
# 但 ℓ_D 係 ell-scale not 距離... 
# 更自然: Silk scale 平方 ≈ number of scatterings × mean free path²
# 88 = 對偶鏈, 103 = 每鏈嘅「模式數」

# ---------- E. 高 ℓ 數據檢驗 ----------
print("\n" + "="*74)
print("E. 高 ℓ 尾段: 數據 vs 模型")
print("="*74)
# 用 planck_tt 高 ℓ 段 (ell > 1000), 逐個點除光滑包絡
# IDCM 預言 D(ell) = exp[-(ell/9055)^1.5];  ΛCDM: exp[-(ell/1411)^1.24]?
# 半監督: 搵「數據衰減」嘅有效 ℓ_D
high = [(e, d) for e, d in planck_tt if 1000 < e < 2600]
if len(high) > 5:
    # 正常化: 用 ell=1000 附近做基準
    e0, d0 = min(high)
    print(f"  基準: ell={e0:.0f} D={d0:.3f}")
    # 每個點: D/D0 vs ell, 擬合 ln(D/D0) = -a·(ell^1.5 - e0^1.5) 得 ℓ_D(3/2)
    pts = np.array([(e-1000, 0) for e, d in high], dtype=float)  # placeholder
    xs = np.array([e**1.5 - e0**1.5 for e, d in high], dtype=float)
    ys = np.log(np.array([d/d0 for e, d in high], dtype=float))
    # 用線性 fit: ys = -xs / ellD^1.5
    a_fit = -np.polyfit(xs, ys, 1)[0]
    ellD_data = a_fit**(2/3)
    print(f"  高ℓ數據擬合 (3/2 指數): ℓ_D = {ellD_data:.0f}")
    # 亦試 1.24 指數
    xs124 = np.array([e**1.24 - e0**1.24 for e, d in high], dtype=float)
    a124 = -np.polyfit(xs124, ys, 1)[0]
    ellD124 = a124**(1/1.24)
    print(f"  高ℓ數據擬合 (1.24 指數): ℓ_D = {ellD124:.0f}")

print("\n" + "="*74)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*74)
sys.exit(0 if FAIL == 0 else 1)