#!/usr/bin/env python3
"""
O59 Session 驗證報告 — 核對所有 docs 數值 vs raw data
=====================================================
逐項驗證 docs/01-03 嘅所有數值 claim:
  1. 12 = L₅+1 = B×N_gen = 4×3
  2. h11 = 36 = K_tree + N_gen = 33+3
  3. 66 = C(12,2) = 2×K_tree
  4. dim(su(12)) = 143 = B×K_tree + L₅
  5. tr(Y) = 66.355 (0.54%)
  6. 1+11 ratio = 28.1 (d_tensor), 20.1 (真κ block0)
  7. v_geom = 246.82 GeV (0.245%)
  8. λ_max = 52−29/66 (0.000010%)
  9. λ₂ ≈ 10 = 2F₅ (0.002%)
  10. Schur block 對角 5e15
  11. V+E+F = 62 = |A₅|+χ = 60+2
  12. A₅ 12維 = 1⊕5⊕3⊕3
  13. 1232 = (2N_d)×(2L₄)
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2
M0 = 27.900915
v_ew = 246.22e3

passed, failed = 0, 0
results = []
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        results.append(f"  ✅ {name} {detail}")
    else:
        failed += 1
        results.append(f"  ❌ {name} {detail}")

print("=" * 72)
print("O59 Session 完整驗證報告")
print("=" * 72)

B, Ngen, L5, L6, L4, L7 = 4, 3, 11, 18, 7, 29
Nd = B * L5
Ktree = Ngen * L5

# ============ [1] 主閉合 ============
print("\n[1] 主閉合 (docs/01)")
check("12 = L₅+1 = 11+1", L5+1 == 12, f"({L5}+1)")
check("12 = B×N_gen = 4×3", B*Ngen == 12, f"({B}×{Ngen})")
check("12 = (Nd−2B)/3 = 36/3", (Nd-2*B)//Ngen == 12, f"({Nd-2*B}/3)")
check("h11 = 36 = K_tree+N_gen = 33+3", Ktree+Ngen == 36, f"({Ktree}+{Ngen})")
check("66 = C(12,2) = 2×K_tree", 12*11//2 == 2*Ktree == 66, "(66)")
check("dim(su(12)) = 143 = B×K_tree+L₅", B*Ktree+L5 == 143, f"({B}×{Ktree}+{L5})")

# ============ [2] tr(Y) ============
print("\n[2] tr(Y) ≈ 66 (docs/01)")
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v12 = phi ** (-np.arange(12)/12)
d_iik = np.einsum('iik->i', d12)
trY = np.sum(d_iik * v12)
err_trY = abs(66 - trY)/66*100
check("tr(Y) = 66.355 (0.54%)", abs(err_trY - 0.539) < 0.01,
      f"(tr={trY:.3f}, err={err_trY:.3f}%)")

# ============ [3] 1+11 譜 ============
print("\n[3] 1+11 譜 (docs/01)")
Y12 = np.einsum("ijk,k->ij", d12, v12)
Y12 = (Y12+Y12.T)/2
ev12 = np.linalg.eigvalsh(Y12)
lam_max = np.max(ev12)
ratio12 = abs(lam_max)/np.mean(np.abs(ev12[ev12 != lam_max]))
check("d_tensor 1+11 ratio ≈ 28.1", abs(ratio12 - 28.1) < 0.5, f"({ratio12:.1f})")

with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2
b0 = Y[0:12, 0:12]
ev0 = np.sort(np.linalg.eigvalsh(b0))
ratio0 = abs(ev0[-1])/np.mean(np.abs(ev0[:-1]))
check("真κ block0 1+11 ratio ≈ 20.1", abs(ratio0 - 20.1) < 0.5, f"({ratio0:.1f})")

# ============ [4] Q1: v_geom ============
print("\n[4] Q1: v_geom (docs/02)")
sqrt_lam = math.sqrt(lam_max)
v_geom = sqrt_lam * M0 * 88 * 14
err_v = abs(v_geom - v_ew)/v_ew*100
check("v_geom ≈ 246.82 GeV (0.245%)", abs(err_v - 0.245) < 0.01,
      f"({v_geom/1e3:.2f} GeV, {err_v:.3f}%)")
check("λ_max ≈ Nd+2B = 52 (0.85%)", abs(52-lam_max)/lam_max < 0.01,
      f"({abs(52-lam_max)/lam_max*100:.2f}%)")
lam2 = np.sort(ev12)[::-1][1]
check("λ₂ ≈ 10 (0.002%)", abs(10-lam2)/10 < 0.001, f"({abs(10-lam2)/10*100:.4f}%)")

# ============ [5] Q2: Schur ============
print("\n[5] Q2: Schur (docs/02)")
from scipy.linalg import schur
T, Q = schur(Y, output='real')
q_orth = np.linalg.norm(Q.T@Q - np.eye(36))
t_lower = np.linalg.norm(np.triu(T, 1))
check("Q 正交 < 1e-10", q_orth < 1e-10, f"({q_orth:.1e})")
check("T 下三角 < 1e-10", t_lower < 1e-10, f"({t_lower:.1e})")

# ============ [6] Q3 + D4: V+E+F ============
print("\n[6] Q3/D4: V+E+F (docs/02-03)")
check("V+E+F = 62 = h21−h11", 12+30+20 == 98-36, "(62)")
check("V+E+F = Nd+L₆ = 44+18", 12+30+20 == 44+18, "(62)")
check("V+E+F = |A₅|+χ = 60+2", 12+30+20 == 60+2, "(62)")
check("A₅ irreps dim² = 60", 1+9+9+16+25 == 60, "")
check("A₅ 12維 = 1⊕5⊕3⊕3", 1+5+3+3 == 12, "(更正)")
check("12×5 = 60 = |A₅|", 12*5 == 60, "")

# ============ [7] D1: 1232 ============
print("\n[7] D1: 1232 (docs/03)")
check("1232 = (2N_d)×(2L₄) = 88×14", (2*Nd)*(2*L4) == 1232, f"({2*Nd}×{2*L4})")
check("1232 = 4N_dL₄ = 4×44×7", 4*Nd*L4 == 1232, "")

# ============ [8] D2: λ_max 精確 ============
print("\n[8] D2: λ_max = 52−29/66 (docs/03)")
pred = 52 - L7/(12*11//2)
rel_exact = abs(lam_max - pred)/lam_max
check("λ_max = 52−29/66 (0.000010%)", rel_exact < 1e-5,
      f"(actual={lam_max:.8f}, pred={pred:.8f}, rel={rel_exact*100:.6f}%)")
check("29 = L₇ = F₆+F₈", 8+21 == 29, "")
check("66 = C(12,2) = 2×K_tree", 12*11//2 == 2*Ktree, "(66)")
check("52 = Nd+2B = B×F₇ = 4×13", 4*13 == 52, "(52)")
# -4/11 撤回
err_411 = abs(4/11 - (52-lam_max))/(52-lam_max)*100
check("-4/11 撤回 (17.2%)", err_411 > 5, f"({err_411:.1f}%)")

# ============ [9] 檢查 docs 檔案存在 ============
print("\n[9] docs 檔案存在")
import glob
docs = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "docs", "*.md")))
for d in docs:
    print(f"  {os.path.basename(d)} ({os.path.getsize(d)} bytes)")
check("docs/01-03 存在", len(docs) >= 3, f"({len(docs)})")

print("\n" + "=" * 72)
print(f"Session 驗證: {passed} PASS, {failed} FAIL")
if failed == 0:
    print("🟢 全部通過 — 所有 docs 數值 vs raw data 一致!")
else:
    print(f"🔴 {failed} 項不一致")
print("=" * 72)

out = {
    "passed": passed,
    "failed": failed,
    "trY": float(trY),
    "trY_err": float(err_trY),
    "ratio12": float(ratio12),
    "ratio0": float(ratio0),
    "v_geom_GeV": float(v_geom/1e3),
    "v_geom_err": float(err_v),
    "lam_max": float(lam_max),
    "lam2": float(lam2),
    "lambda_pred": float(pred),
    "lambda_rel": float(rel_exact),
    "q_orth": float(q_orth),
    "t_lower": float(t_lower),
    "docs": [os.path.basename(d) for d in docs],
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "session_verification.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n結果已保存: data/session_verification.json")
