#!/usr/bin/env python3
"""
O48 Q1 v2: ℓ_D=9055 物理機制 — 咩係「9055」? (類別錯誤檢驗)
=============================================================
⚠️ 探索 script: 本檔有**預期 FAIL 檢查**（記錄探索發現，非 regression）。
     早期 geo 表錯誤已被 scripts/14_q1_ruling.py 修正 (5/5 PASS)。
     本檔保留探索歷史，最終裁決以 14 為準。
發現 (v1): 4 峰擬合根本 fit 出 9147, 唔係 9055! 9055 唔係唯一擬合值。
O241 R10: 「IDCM 9055 vs Planck Silk 1411 = 6.42× FAIL」

本 script 要分辨:
H1. 9055 係「峰值高度模型」嘅阻尼 (peak-height D), 而 Planck 1411
    係「C_ℓ 功率譜」嘅 damping — 兩者係**唔同量綱嘅對比 (類別錯誤)**
H2. 若 H1 成立: IDCM 峰高模型 (9055 + 33/34) 已 0.30% RMS 閉合
    Planck 峰高, 唔需要對齊 C_ℓ 譜嘅 1411
H3. C_ℓ 譜尾段真實 damping: 用 planck_tt 高 ℓ 測 exponent 同 scale
H4. IDCM C_ℓ 若存在 (cmb_cl 主題), 佢嘅阻尼點樣嚟?

執行:
A. 重現峰高模型: IDCM pred vs Planck 峰高 (5 峰) → RMS
B. 對比用相同峰位嘅 ΛCDM Silk D(peak) (1411, exponent 1.24)
C. 測 planck_tt 高 ℓ 尾: 有效 damping (envelope fit)
D. 9055 = 88×103−9 嘅「物理身份」: 峰值模型係「3/2 exponent」,
   Silk standard 係「1.24」— 睇 3/2 = 1.5 有冇結構來源 (K_Chain!
   玻色子扩散?) vs 1.24 (ΛCDM 觀測擬合)
"""
import math, os, sys
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

# ---------- A. 峰高模型重現 ----------
print("="*74)
print("A. IDCM 峰高模型 vs Planck 峰高 (RMS)")
print("="*74)
# 真峰: m=1,2,3,5,7; ℓ 同 A 由 planck_binned_peaks.json
import json
base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
pk = json.load(open(f"{base}/o10_peak_amplitudes/data/planck_binned_peaks.json"))
peaks = pk['peaks']  # keys '1'..'5' (真峰次序)
ms = [1, 2, 3, 5, 7]
A_obs = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell_m = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

# 幾何項: 3eps/F_j where j = 質數峰次序 (p: 1,2,3,5,7 -> j: 1,2,3,4,5? 唔)
# 睇 O10: j=1→p=2, j=2→p=3, j=3→p=5, j=4→p=7, 幾何 = 3ε, 3ε, 3ε/2, 3ε/3
geo_by_m = {1: 3*eps, 2: 3*eps, 3: 3*eps/2, 5: 3*eps/3, 7: 3*eps/5}
# j=5 → 3eps/5? F_5=5, 3ε×Π(F_k/F_{k+1}) up to j=5 = 3ε×1/2×2/3×3/5? 
# O10: Π_{k=1}^{j-1} F_k/F_{k+1}: j=4 (p=7): F1/F2·F2/F3·F3/F4 = 1/3 ✓ (3ε/3)

lD = 9055
print("\n  IDCM peak-height model: A = 3ε·(33/34)·Π(F_k/F_{k+1})·D(ℓ), ℓ_D=9055")
rows = []
for m in ms:
    j = {1:1, 2:1, 3:2, 5:3, 7:4}[m]
    geom = 3*eps/F(j) if j > 1 else 3*eps
    if j == 2: geom = 3*eps  # j=2: Π = F1/F2 = 1
    D = math.exp(-(ell_m[m]/lD)**1.5)
    pred = geom * D * (33/34)
    rows.append((m, geom, D, pred, A_obs[m]))
    dev = (A_obs[m]-pred)/pred*100
    print(f"    m={m} ℓ={ell_m[m]}: geom={geom:.4f} D={D:.4f} pred={pred:.4f} obs={A_obs[m]:.4f} dev={dev:+.2f}%")
rms = math.sqrt(sum(((o-p)/p)**2 for m,p,o in [(r[0],r[3],r[4]) for r in rows])/len(rows))*100
print(f"  RMS = {rms:.2f}%")
check("A1: IDCM 峰高模型 RMS < 1%", rms < 1.0, f"RMS={rms:.2f}%")

# ---------- B. ΛCDM Silk 喺同啲峰位 ----------
print("\n" + "="*74)
print("B. ΛCDM Silk D(ℓ) (1411, 1.24) 喺 IDCM 峰位")
print("="*74)
lD_planck = 1411
for m in ms:
    D_planck_124 = math.exp(-(ell_m[m]/lD_planck)**1.24)
    D_planck_15 = math.exp(-(ell_m[m]/lD_planck)**1.5)
    D_idcm = math.exp(-(ell_m[m]/9055)**1.5)
    print(f"    ℓ={ell_m[m]:4d}: IDCM(9055,1.5) D={D_idcm:.4f} | ΛCDM(1411,1.24) D={D_planck_124:.4f} | ΛCDM(1411,1.5) D={D_planck_15:.4f}")

print("\n  → 兩者數學形式唔同 (3/2 vs 6/5), 直接比 ℓ_D 數值冇意義,")
print("    要睇各自模型對「峰高」嘅預言誤差。")

# ---------- C. Planck TT 高 ℓ 尾 damping ----------
print("\n" + "="*74)
print("C. Planck TT 高 ℓ 尾 damping (實測)")
print("="*74)
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
print(f"  bins: {len(planck_tt)} (ℓ {planck_tt[0][0]:.0f}..{planck_tt[-1][0]:.0f})")

# 搵峰位附近: broadband envelope。C_ℓ damping 應該睇「平滑包絡」
# 用 log-space smoothing 或者直接取 local maxima 高 ℓ 段
# 局部極大 (峰) 喺 ℓ>1000:
peaks_hi = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    e_prev, d_prev = planck_tt[i-1]
    e_nxt, d_nxt = planck_tt[i+1]
    if 1000 < e0 < 2600 and d0 > d_prev and d0 > d_nxt:
        peaks_hi.append((e0, d0))
print(f"  高ℓ局部峰: {[(int(e), round(d,3)) for e,d in peaks_hi]}")

# 用峰包絡擬合 D(ℓ) = C·exp[-(ℓ/ℓ_D)^α]: 試 α=1.24, 1.5, 2
if len(peaks_hi) >= 3:
    xs = np.array([e for e, d in peaks_hi], dtype=float)
    ys = np.log(np.array([d for e, d in peaks_hi], dtype=float))
    for alpha in [1.24, 1.5, 1.0, 2.0]:
        # ln C - (x/ℓD)^α: fit linear in x^α
        xa = xs**alpha
        coef = np.polyfit(xa, ys, 1)  # slope=-1/ℓD^α, intercept=ln C
        lD_env = (-1/coef[0])**(1/alpha)
        print(f"    α={alpha}: ℓ_D = {lD_env:.0f}, C = {math.exp(coef[1]):.4f}")
else:
    print("  (高ℓ峰不足, 試 bin 平均)")

# ---------- D. 9055 身份: 3/2 exponent 嘅結構 ----------
print("\n" + "="*74)
print("D. 9055 嘅物理身份 — 3/2 exponent 嘅結構來源")
print("="*74)
print("  文獻: Silk damping tail 喺 C_ℓ 通常寫 exp[-(ℓ/ℓ_D)^1.24] (ΛCDM)")
print("  IDCM 峰高模型用 exp[-(ℓ/9055)^{3/2}]")
print()
print("  3/2 = 1.5: 隨機遊走 (diffusion) 3D Gaussian 尾部?")
print("  exp[-(ℓ/ℓ_D)^2] (Gaussian, α=2): 相位隨機化 (亂相) 模型")
print("  exp[-(ℓ/ℓ_D)^{3/2}]: Fourier 域 Brownian? 或 Kolmogorov-Obukhov?")
print()
print("  關鍵: O10 擬合 5 峰時 使用 ℓ_D=9055 而唔係 1411,")
print("  因為 9055 係令 4 峰幅 RMS 最細嘅「代表衰減尺度」,")
print("  唔係 C_ℓ 卷積嘅 damping scale!")
print()
# 用 implied D 每個峰自己嘅 ℓ_D (per-point):
print("  逐峰 implied ℓ_D (冇擬合, 由 D(ℓ)=exp[-(ℓ/ℓD)^1.5] 反推):")
for m in ms:
    if m == 1: continue
    j = {1:1, 2:1, 3:2, 5:3, 7:4}[m]
    geom = 3*eps/F(j) if j > 1 else 3*eps
    if j == 2: geom = 3*eps
    D_impl = A_obs[m]/(geom*(33/34))
    lD_impl = ell_m[m]/(-math.log(D_impl))**(2/3)
    print(f"    m={m} ℓ={ell_m[m]}: D_impl={D_impl:.4f} → ℓ_D = {lD_impl:.0f}")
print()
print("  → 每個峰 implied ℓ_D 都唔同 (Silk 「唔係單一尺度」, O10 已記錄)")
print("  → 9055 係 O48 結構式 88×103−9, 但佢係「尾段位置」")

# ---------- E. 9055 結構式對應咩「ℓ 位置」 ----------
print("\n" + "="*74)
print("E. 9055 結構式嘅「幾何身份」")
print("="*74)
# 9055 = 88*(44+33+2*13)-9 = 88*103-9
# 睇: 88 = 2Nd (對偶鏈), 103 = Nd+M+2F7, 9 = F4^2
# 係咪 = 峰位公式嘅「第 m=?? 峰」?
# ℓ_m = 44*(33 - C(9-m,2)) + frac
# 邊個 m 嘅 ℓ 接近 9055? m 好大... C(9-m,2) 負數...
# 另一角度: 9055/44 = 205.8;  44×206 = 9064
# 44×206 - 9 = 9055: N=206, s=-9→35?
# 206 = ? 206 = 2×103 = 2(Nd+M+2F7)
print(f"  9055 = 44×205.80 = 88×102.90")
print(f"  9055 = 88×103 − 3² = 88(Nd+M+2F₇) − F₄²")
print(f"  N=205, s=35: ℓ=9055 → (9055-205×44) = 35")
print(f"  檢驗: 205 = ? 205 = 5×41 = F₅×(L₅×? )... 205 = 5×41, 41 = 44-3")
print(f"  而 103 = 44+33+26 = Nd+M+2F₇")

# 有趣 9055 同 peak chain 關係: 峰位 ell_m = 44N+s,
# N 值(5,11,18,25,32) 階梯; 9055 = 44×206 - 9
# 206 = 4×44+30? = 4Nd+30; 30 = N_6 (m=6 被抑制嘅 N)
# 9055 = 44×(4×44+30) − 9 = 44×(176+30) − 9 = 44×206 − 9 ✓
# 4×44 = 4Nd: 四層? 30 = 非Lucas 被抑制 N
print()
print("  9055 = 44×(4N_d + 30) − F₄², 其中 30 = N_6 (被抑制峰 m=6 嘅 N)")
print("  → 「9055 係 m=6 被抑制位置嘅 4 倍深度」 — 語義待定")

print("\n" + "="*74)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*74)
sys.exit(0 if FAIL == 0 else 1)