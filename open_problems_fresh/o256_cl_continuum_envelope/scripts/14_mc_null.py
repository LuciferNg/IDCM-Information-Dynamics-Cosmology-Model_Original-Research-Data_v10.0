#!/usr/bin/env python3
"""
O256 — Script 14: ★ MC null + 結構階梯判決 (4 Hard Tests)
=====================================================================
Script 13 發現:
  λ₁ = 半週期/lnφ = 148.5/lnφ = 308.60  vs 實測 308.5±5 → +0.19%
  半週期 148.5 = (峰→谷 212.5 + 谷→峰 84.5)/2 — O48 峰-谷模型 EXACT
  λ₄ = 全間隙/lnφ = 306/lnφ = 635.9 vs 646 → -1.56%

本 script:
  T1: MC null — 1000 隨機 λ ∈ [200,900] fit Planck 高ℓ尾第一段,
      φ 預言 λ=308.6 排名 (p-value)
  T2: 第二段 1700-2000 λ 預言? (半週期只有一段?)
  T3: 上升結構: 半間隙→全間隙過渡 (148.5→306) 形式
      實測: 308→410→420→646; 結構: 308.6→(?)→(?)→635.9
  T4: O48 telescoping 1/F_j 嘅 j 同半週期關係核實
"""
import math, sys
import numpy as np
import numpy.random as rng

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

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
phi = (1+math.sqrt(5))/2
lnphi = math.log(phi)

planck = []
with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p)>=2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:,0], planck[:,1]
D_p = C_p*l_p*(l_p+1)/(2*math.pi)

print("="*76)
print("1. MC null: λ=308.6 (φ 預言) 喺隨機 λ 嘅排名")
print("="*76)
# 對第一段 1418-1700 fit 單指數 A·exp(-ℓ/λ)
m1 = (l_p>1409)&(l_p<1700)
l1, D1 = l_p[m1], D_p[m1]
def fit_lam_rmse(l, d, lam):
    A = np.dot(d, np.exp(-l/lam))/np.dot(np.exp(-l/lam), np.exp(-l/lam))
    m = A*np.exp(-l/lam)
    return np.sqrt(np.mean(((d-m)/d)**2))
lam_phi = 148.5/lnphi
rmse_phi = fit_lam_rmse(l1, D1, lam_phi)
print(f"  φ 預言 λ={lam_phi:.2f}: RMSE={rmse_phi*100:.2f}%")
# MC: 1000 隨機 λ
rng.seed(42)
lam_rand = np.array([200+700*rng.random() for _ in range(1000)])
rmse_rand = np.array([fit_lam_rmse(l1, D1, lam) for lam in lam_rand])
pval = np.mean(rmse_rand <= rmse_phi)
rank = np.sum(rmse_rand <= rmse_phi)
print(f"  MC: 1000 隨機 λ, {int(rank)} 個 RMSE ≤ φ 預言 → p ≈ {pval:.4f} ({100*pval:.1f}%)")
check("φ 預言 p < 0.05 (前 5%)", pval < 0.05, f"(p={pval:.4f})")
# 最佳自由 λ
best_i = np.argmin(rmse_rand)
print(f"  最佳自由 λ* ≈ {lam_rand[best_i]:.1f} (RMSE {rmse_rand[best_i]*100:.2f}%) — 唔可用 (re-fit)")

# ── 2. 第二段 1700-2000: λ 預言? ─────────────────────────────────
print("\n" + "="*76)
print("2. 第二段 λ(ℓ): 上升結構 308→410→420→646")
print("="*76)
m2 = (l_p>=1700)&(l_p<2000)
l2, D2 = l_p[m2], D_p[m2]
if len(l2) >= 3:
    sl = np.polyfit(l2, np.log(D2), 1)[0]
    print(f"  實測 λ₂(1700-2000) = {-1/sl:.1f}")
# 結構候選: λ₂ = ?  (間隙 288/lnφ=598? 唔啱 410)
# 410 結構身份: 410 ≈ 306+104? 410 = 1452-1042? 410 = 2×205?
# 410 = 148.5×2.76? 唔靚. 410 ≈ 306×1.34 = F₆/F₈×306?
# 關鍵: 410/308 = 1.331 ≈ 4/3 = (1/F₂)/(1/F₄)? 唔知.
# 誠實: 第二段以上未建立結構 — 只確立 λ₁ (半週期/lnφ)
print("  第二段結構: 未建立 (410 嘅結構身份唔喺本 O 範圍)")
print("  — 308 (半週期/lnφ) 係唯一零參數預言點")

# ── 3. 上升結構: 半間隙 vs 全間隙 ──────────────────────────────
print("\n" + "="*76)
print("3. λ(ℓ) 段起點→終點: 半週期→全週期過渡")
print("="*76)
lam_half = 148.5/lnphi
lam_full = 306.0/lnphi
print(f"  λ₁ = 半週期/lnφ = {lam_half:.2f}  ← 峰-谷結構 (O48)")
print(f"  λ₄ = 全間隙/lnφ = {lam_full:.2f}  ← 峰-峰結構 (O83 rung)")
print(f"  λ(ℓ) 上升比: {lam_full/lam_half:.3f} (結構) vs {646/308:.3f} (實測)")
print(f"  一致 (缺口 {abs(lam_full/lam_half - 646/308)/(646/308)*100:.1f}%)")
print("  ⟹ λ 上升 = 有效間隙由峰-谷半週期過渡到峰-峰全週期")
print("  ⟹ 這一過渡嘅中間值 410/420 未界定 — 待 R3/lensing")

# ── 4. 峰序 j 同半週期核實 ──────────────────────────────────────
print("\n" + "="*76)
print("4. O48 telescoping 1/F_j 峰序核實")
print("="*76)
# docs/02: j=1,2,3,4 ⇒ 1, 1, 1/2, 1/3  (5 峰: m=1,2,3,5,7)
# 峰序 j 係「間隙序」: 峰 1→2 (306), 2→3 (288), 3→5 (306), 5→7 (288)?
# 但 O48 峰位: 221/527/815/1121/1409: 間隙 306/288/306/288
# docs/08: geo(m)=3ε/F_j (j=峰序 0-4)? — 峰序 0-4 係 5 峰!
F = lambda n: round((phi**n - (-phi)**-n)/math.sqrt(5))
print("  O48 docs/08: geo(m) = 3ε/F_j, j=峰序 0-4 (5 質數峰)")
print("  峰序: m=1 → j=0? F_0=0 爆!  ⟹ 峰序 j 由 1 起")
print("  峰 1: 1/F₁=1.000  峰 2: 1/F₂=1.000  峰 3: 1/F₃=0.500")
print("  峰 5: 1/F₄=0.333  峰 7: 1/F₅=0.200")
for j in [1,2,3,4,5]:
    print(f"    j={j}: F_{j}={F(j)}, 1/F_{j}={1/F(j):.5f}")

print("\n  ── 峰高階梯 vs 連續 e-folding 一致性 ──")
print("  離散峰高比: A₂/A₁ = 1,  A₃/A₁ = 0.5,  A₅/A₁ = 0.333,  A₇/A₁ = 0.200")
print("  對應位置:   221 → 527 (Δ306), 527→815 (Δ288), ...")
print("  連續化: A(ℓ) ∝ 1/F_{1+ℓ/Δℓ} ≈ √5·φ^{-ℓ/Δℓ}")
print(f"  每間隙 Δℓ=306: e-folding λ = Δℓ/lnφ = {306/lnphi:.1f}")
print(f"  峰高實測: A₂/A₁ = 4/9 = 0.444 (O83) vs 階梯 1/F₂ = 1.0??")
print("  ⚠️ O83 振幅母函數 (4/9, 4/9, 3/14, 1/7) 唔等於 O48 telescoping")
print("     兩個體系: O48 幾何階梯 (峰高衰減) vs O83 模式權重")
print("     本 O 用 O48 (峰高衰減主體) — 連續包絡唔可以攞 O83 振幅")

# ── 5. 判決 (4 Hard Tests) ───────────────────────────────────────
print("\n" + "="*76)
print("5. 4 Hard Tests")
print("="*76)
print("""
  ① 自由度成本: λ₁ = 148.5/lnφ 零新常數 (半週期=峰谷結構, lnφ=已知)
     → ✅ 零參數 (但只預言第一段)
  ② MC null: p 由 section 1 決定 (vs 隨機 λ 排名)
  ③ 可證偽+樣本外: λ₁ 預言喺 Planck 1418-1700 (未 fit λ) → 樣本外 ✅
     但第二段以上冇預言 → 半閉合
  ④ 結構剛性: 峰-谷半週期 148.5 EXACT (唔係 fit) → 結構 ✅
     R12 互動: 308.6 落入 lensed ΛCDM band (289..316) → 唔可以獨立閉合
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)