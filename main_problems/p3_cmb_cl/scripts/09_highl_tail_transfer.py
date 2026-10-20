#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — IDCM C_ℓ 高ℓ尾傳輸函數盲測 (2026-10-20)
=====================================================================
缺口 (O48 docs/02 §6 誠實保留): IDCM 對 C_ℓ 連續譜高 ℓ 尾 (ℓ>1409)
冇傳輸函數模型。O241 R10 FAIL 係類別錯誤: 9055 = 峰高殘差阻尼尺度 (層級1),
唔係 C_ℓ 譜 damp 尺度 (層級2)。O202 R6: IDCM 冇 C_ℓ 連續形式。

本 script 第一原理攻堅 (零 import 原推導 script, 獨立驗證):

已知結構 (全部已閉合):
  * 峰週期 P = 297 = 33×9 = M×9 (O48: mod-9 梳, 峰間距 306/288 交替)
  * 峰形 γ = P/6 = 49.5 (O48 Q1.45-47: CAMB γ=48.0, PR4 γ=47.5, 47.5-49.5 三源閉合)
  * 峰位: 真峰 m∈{1,2,3,5,7}: ℓ = 221, 527, 815, 1121, 1409
  * 峰高階梯: A(p_j) ∝ 1/F_j telescoping (m=7 得 1/3)
  * ℓ_sync = 44 = 2N_d

傳輸函數假說 H1 (結構延續):
  高ℓ尾 (ℓ>1409) = 最後真峰 Lorentz 尾 + 44-週期鋸齒包絡平均
  C_ℓ(tail) ∝ exp[-(ℓ-ℓ₇)/λ],  e-folding λ = ?
  候選 λ: (a) λ=297=峰週期 (b) λ=6γ=297 (同一個)
           (c) λ=44×6=264 (d) λ=88×3=264 (e) λ=33×9=297
  原則: 高ℓ尾 e-folding = 峰週期 297 = 33×9 = M×9 (與峰形 γ=P/6 同源)

假說 H2 (階梯延續):
  峰高階梯 telescoping 1/F_j 延續到 ℓ>1409 區 (j=5..): 1/F_5=1/5, 1/F_6=1/8
  ⟹ D(ℓ) ∝ 1/F_{j(ℓ)}, j 由 ℓ 位置決定

假說 H3 (ΛCDM 對照):
  Silk: exp[-(ℓ/1411)^1.24] — 文獻值, 非 IDCM 結構

測量:
  Planck TT 55 bins (ℓ 1418..2492), SPT-3G D1 TT_150x150 52 bins (有 cov),
  對比 log D vs ℓ 斜率 / e-folding
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
F  = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
P = 297          # 峰週期 = 33×9 = M×9
GAMMA = 49.5     # 峰形半寬 = P/6
L7 = 1409        # 最後真峰 (峰 7, N=32)

print("="*76)
print("P3/high-l-tail-transfer — 高ℓ尾傳輸函數盲測")
print("="*76)

# ---------- 1. Planck TT 高ℓ尾數據 ----------
planck = []
with open(f"{BASE}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:, 0], planck[:, 1]
D_p = C_p * l_p*(l_p+1)/(2*math.pi)   # ★ 2026-10-20: txt 第二列係 C_ℓ, 轉 D_ℓ
mask_tail = l_p > 1409
l_t, D_t = l_p[mask_tail], D_p[mask_tail]
print(f"\nPlanck TT 高ℓ尾: {len(l_t)} bins, ℓ {l_t[0]:.0f}..{l_t[-1]:.0f}")
print(f"  D(1409)={D_p[np.abs(l_p-1409).argmin()]:.1f}  D(1418)={D_t[0]:.1f}  D(2492)={D_t[-1]:.1f}")
print(f"  (交叉驗證: SPT @1437 D=820.2, Planck @1418 D={D_t[0]:.1f})")

# ---------- 2. e-folding 測量 (ln D vs ℓ 線性擬合) ----------
logD = np.log(D_t)
A, B = np.polyfit(l_t, logD, 1)   # polyfit: 回傳 [slope, intercept]
slope, intercept = A, B
lam_obs = -1/slope
print(f"\nH1 測量: ln D = {intercept:.4f} {slope:.6f}·ℓ  ⟹  e-folding λ_obs = {lam_obs:.1f}")
print(f"  候選 λ: 297 (峰週期=33×9), 264 (=44×6=88×3), 294 (=44×6.7?)")
print(f"  λ_obs/297 = {lam_obs/297:.4f}  (dev {(lam_obs-297)/297*100:+.1f}%)")
print(f"  λ_obs/264 = {lam_obs/264:.4f}  (dev {(lam_obs-264)/264*100:+.1f}%)")

check("H1a: λ_obs ∈ 297±20%", 297*0.8 <= lam_obs <= 297*1.2,
      f"λ_obs={lam_obs:.1f} vs 297")
check("H1b: λ_obs 離 297 近過 264", abs(lam_obs-297) < abs(lam_obs-264),
      f"λ_obs={lam_obs:.1f} Δ297={abs(lam_obs-297):.1f} Δ264={abs(lam_obs-264):.1f}")

# ---------- 3. e-folding 分段穩定性 (尾段唔應該係單一指數?) ----------
print(f"\n分段 e-folding (每 5 bins):")
for i in range(0, len(l_t)-5, 5):
    seg_l, seg_D = l_t[i:i+5], D_t[i:i+5]
    sA, sB = np.polyfit(seg_l, np.log(seg_D), 1)
    print(f"  ℓ {seg_l[0]:.0f}..{seg_l[-1]:.0f}: λ={-1/sA:7.1f}")

# ---------- 4. 44-週期鋸齒: mod-44 殘差 ----------
res = logD - (intercept + slope*l_t)
print(f"\nH1c: mod-44 週期殘差檢查 (高ℓ尾):")
ranges = []
for r in range(44):
    m = (l_t.astype(int) % 44) == r
    if m.sum() >= 2:
        ranges.append((r, res[m].mean()))
r_arr = np.array([x[1] for x in ranges])
print(f"  {len(ranges)} 個 mod-44 類, mean 幅度 range = {r_arr.max()-r_arr.min():.4f}")
print(f"  殘差 std = {res.std():.4f} (相對 log 尺度)")
# O48 Q1.5 全譜測量 range 0.245; 呢度係高ℓ尾專用

# ---------- 5. 峰形 Lorentz 尾之預言 ----------
# 最後真峰 Lorentz: D(ℓ) = A·γ²/((ℓ-ℓ₇)²+γ²)
gamma2 = GAMMA**2
D1418_lorentz_frac = gamma2 / ((l_t[0]-L7)**2 + gamma2)
D2492_lorentz_frac = gamma2 / ((l_t[-1]-L7)**2 + gamma2)
print(f"\nLorentz 尾預言 (最後峰, γ={GAMMA}):")
print(f"  f(1418) = {D1418_lorentz_frac:.6f}  vs Planck 觀測比 D(1418)/D(1409~) ")
# 用 D(1409) bin 值當歸一
i1409 = np.abs(l_p-1409).argmin()
Dref = D_p[i1409]
ratio_obs_1418 = D_t[0]/Dref
ratio_obs_2492 = D_t[-1]/Dref
print(f"  實測 D(1418)/D(1409) = {ratio_obs_1418:.4f}  D(2492)/D(1409) = {ratio_obs_2492:.5f}")
print(f"  Lorentz 預言: 1418: {D1418_lorentz_frac:.6f} (實測 {ratio_obs_1418:.4f}) | 2492: {D2492_lorentz_frac:.7f} (實測 {ratio_obs_2492:.5f})")
check("H1d: 實測 1418 比 Lorentz 尾大 >> 10×", ratio_obs_1418 > 10*D1418_lorentz_frac,
      f"實測 {ratio_obs_1418:.4f} vs Lorentz {D1418_lorentz_frac:.6f}")

# ---------- 6. 峰高階梯延續 (H2) ----------
# 峰高階梯: A_m ∝ 1/F_{j(m)}, m=1,2,3,5,7 → j=1,2,3,4: 1/F: 1,1,1/2,1/3
# 高ℓ尾延續: j=5 → 1/5 = 0.2, j=6 → 1/8 = 0.125
# 位置: 峰間隔 Δℓ ≈ 306/288; j 對應 ℓ 步進 ~ 297
l_j5 = 1409 + 297   # ≈ 1706
l_j6 = 1409 + 2*297 # ≈ 2003
print(f"\nH2 階梯延續預言:")
for lq, j in [(l_j5, 5), (l_j6, 6)]:
    i = np.clip(np.abs(l_t-lq).argmin(), 0, len(l_t)-1)
    obs_ratio = D_t[i]/Dref
    pred = 1.0/F(j)
    print(f"  ℓ≈{lq}: 1/F_{j}={pred:.4f} vs 實測 D(ℓ)/D(1409)={obs_ratio:.4f}  (dev {(obs_ratio-pred)/pred*100:+.0f}%)")

# ---------- 7. 複合模型: Lorentz 尾 × 階梯 ----------
# C_ℓ(tail) = D_1409 · [γ²/((ℓ-ℓ₇)²+γ²)] · exp[-(ℓ-ℓ₇)/λ]
lam_297 = 297.0
for lam in [297.0, 264.0, 1411.0]:
    pred = Dref * gamma2/((l_t-L7)**2+gamma2) * np.exp(-(l_t-L7)/lam)
    devs = (D_t-pred)/pred
    rms = np.sqrt((devs**2).mean())
    print(f"\n複合模型 λ={lam:.0f}: RMS dev = {rms*100:.1f}%  (尾 {len(l_t)} bins)")
    if lam == 297.0:
        check("H7a: λ=297 複合 RMS < 60%", rms < 0.60, f"RMS={rms*100:.1f}%")

# ---------- 8. SPT-3G 盲測 ----------
print("\n" + "="*76)
print("SPT-3G D1 獨立盲測 (TT_150x150, 52 bins, 有 cov)")
print("="*76)
try:
    DATA = f"{BASE}/o214_energy_budget_definition/data/spt3g_d1"
    bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
    win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")
    # band centers
    centers = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
    spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
               ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
               ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
               ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
               ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
               ("EE_220x220",72)]
    off = 0
    for name, n in spectra:
        if name == "TT_150x150": break
        off += n
    tt150 = bdp[off:off+52]
    mask = tt150 > 0
    ells_s = centers[mask]; D_s = tt150[mask]
    print(f"  SPT bins: {len(ells_s)}, ℓ {ells_s.min():.0f}..{ells_s.max():.0f}")

    # 高ℓ段 (ℓ>1409)
    ms = ells_s > 1409
    ls, ds = ells_s[ms], D_s[ms]
    print(f"  SPT 高ℓ尾: {len(ls)} bins, ℓ {ls.min():.0f}..{ls.max():.0f}")
    if len(ls) >= 4:
        sA, sB = np.polyfit(ls, np.log(ds), 1)
        s_lam = -1/sA
        print(f"  SPT e-folding λ_obs = {s_lam:.1f}  (dev vs 297 {(s_lam-297)/297*100:+.1f}%)")
        check("H8a: SPT λ_obs ∈ 297±30%", 297*0.7 <= s_lam <= 297*1.3,
              f"λ={s_lam:.1f} vs 297")
        # SPT 對照 Planck: 兩個獨立實驗 e-folding 一致?
        check("H8b: SPT λ_obs ∈ [Planck λ×0.7, ×1.3]", 0.7*lam_obs <= s_lam <= 1.3*lam_obs,
              f"SPT {s_lam:.1f} vs Planck {lam_obs:.1f}")
except Exception as e:
    print(f"  SPT 數據讀取失敗: {e}")
    check("H8", False, str(e)[:80])

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)